"""Quantum circuits built from open_gororoba Cayley-Dickson structure.

Left multiplication L_{e_m} by a basis unit is a signed permutation of the 2^k
basis states, so it is unitary and compiles to a diagonal sign layer plus X
gates on k qubits. Design A turns the octonion associator into a measurable
relative phase. Design B turns a sedenion zero divisor into perfect destructive
interference through a one-ancilla linear combination of unitaries; design D
sweeps the input's relative phase through the same circuit. Design C measures
the Walsh spectrum of the associator phase along the Cayley-Dickson ladder.
Running this module checks every circuit against the algebraic predictions of
predict.py, which no builder here imports, and raises on the first deviation.
"""

from __future__ import annotations

import math
from collections import defaultdict
from itertools import combinations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate, Parameter, ParameterExpression
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Operator, Statevector

import parallel
import predict
from boolean_anf import anf_coefficients, anf_degree_histogram
from cd_core import cd_sign, fano_completion, sedenion_zero_divisor_corpus, sedenion_zero_divisors
from select_lcu import (
    joint_select_signs,
    phase_oracle_from_truth_table,
    select_circuit,
    sparse_pair_prep,
)

SWEEP_PHASES = [k * math.pi / 4 for k in range(9)]
SPECTRUM_EXEMPLARS = ((8, 1, 4), (16, 1, 8), (32, 1, 16))
SIGN_HIERARCHY_EXEMPLARS = ((8, 4), (16, 8), (32, 16))


def left_mult_gate(dim: int, m: int, flip: int | None = None) -> Gate:
    """L_{e_m}: the sign diagonal D_m, then X on the bits of m.

    L_{e_m}|q> = cd_sign(dim,m,q)|m XOR q> factors into D_m followed by the
    basis permutation q -> m XOR q. flip negates the sign at input q = flip,
    giving the deliberately wrong operator a sign-mutation control needs.
    """
    nq = dim.bit_length() - 1
    signs = [float(cd_sign(dim, m, q)) * (-1.0 if q == flip else 1.0) for q in range(dim)]
    sub = QuantumCircuit(nq, name=f"Le{m}")
    sub.append(DiagonalGate(signs), range(nq))
    for b in range(nq):
        if (m >> b) & 1:
            sub.x(b)
    return sub.to_gate()


def left_mult_adjoint_gate(dim: int, m: int) -> Gate:
    """L_{e_m}^dagger = L_{e_m}^T = P_m D_m: X on the bits of m, then D_m.

    The transpose holds for every Cayley-Dickson dimension, with no appeal to
    L_{e_m}^2 = -I, which the octonions guarantee through alternativity.
    """
    nq = dim.bit_length() - 1
    sub = QuantumCircuit(nq, name=f"Le{m}_dg")
    for b in range(nq):
        if (m >> b) & 1:
            sub.x(b)
    sub.append(DiagonalGate([float(cd_sign(dim, m, q)) for q in range(dim)]), range(nq))
    return sub.to_gate()


def design_a_associator(i: int, j: int) -> tuple[QuantumCircuit, int, int, int]:
    """Octonion associator phase witness on 3 qubits, device-composed.

    W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j}, with L_{e_i e_j} = cd_sign(8,i,j)
    L_{e_{i^j}}, is diagonal +/-1 with the associator sign of (e_i, e_j, e_k).
    L_{e_m}^2 = -I on the octonions, so L_{e_{i^j}} = -cd_sign(8,i,j)
    L_{e_i e_j}^{-1} and the net operator L_{e_j}, L_{e_i}, L_{e_{i^j}} is W times
    a global sign, unobservable in this uncontrolled circuit. The three L gates
    are appended separately with barriers so the hardware performs the
    cancellation. A superposition of a line-completing k0 (associative) and a
    one-bit-away k1 (anti) picks up a relative sign, and a Hadamard on the
    differing qubit reads it as bit 1 for every pair.
    """
    k0 = fano_completion(i, j)
    if k0 is None:
        raise ValueError(f"({i},{j}) is not a pair of distinct octonion imaginary units")
    diff_bit = None
    k1 = None
    for b in range(3):
        cand = k0 ^ (1 << b)
        if cand in (0, i, j):
            continue
        lo = cd_sign(8, i, j) * cd_sign(8, i ^ j, cand)
        ro = cd_sign(8, j, cand) * cd_sign(8, i, j ^ cand)
        if lo != ro:
            k1, diff_bit = cand, b
            break
    if k1 is None or diff_bit is None:
        raise ValueError(f"no anti-associative neighbor of k0={k0} for ({i},{j})")

    qc = QuantumCircuit(3, 1)
    # H on |0> and then the X load of k0 give (|k0> + |k1>)/sqrt2 whatever bit
    # diff_bit of k0 is, because X swaps two equal-amplitude branches.
    qc.h(diff_bit)
    for b in range(3):
        if (k0 >> b) & 1:
            qc.x(b)
    for m in (j, i, i ^ j):
        qc.append(left_mult_gate(8, m), [0, 1, 2])
        qc.barrier()
    qc.h(diff_bit)
    qc.measure(diff_bit, 0)
    return qc, k0, k1, diff_bit


def lcu_witness(a_pair: tuple[int, int], b_pair: tuple[int, int], phase: float | ParameterExpression) -> QuantumCircuit:
    """(L_{e_i} + L_{e_j})/2 on (|e_k> + e^{i phase}|e_l>)/sqrt2, 4 data qubits + ancilla 4.

    Sparse pair preparation loads b, H on the ancilla splits the two branches,
    SELECT applies L_{e_i} on ancilla 0 and L_{e_j} on ancilla 1, and the final H
    recombines them: the ancilla-0 amplitude is the post-selected product.
    """
    (i, j), (k, el) = a_pair, b_pair
    qc = QuantumCircuit(5, 1)
    qc.compose(sparse_pair_prep(4, k, el, phase), [0, 1, 2, 3], inplace=True)
    qc.h(4)
    qc.compose(select_circuit(16, i, j), [0, 1, 2, 3, 4], inplace=True)
    qc.h(4)
    qc.measure(4, 0)
    return qc


def design_b_zero_divisor(a_pair: tuple[int, int], b_pair: tuple[int, int], s: int) -> QuantumCircuit:
    """Sedenion zero-divisor witness: b = (e_k + s e_l)/sqrt2, P(anc=0) = |a b|^2 / 8.

    For a true zero divisor a b = 0, so P(anc=0) = 0 by interference.
    """
    return lcu_witness(a_pair, b_pair, 0.0 if s > 0 else math.pi)


def design_d_phase_sweep(
    a_pair: tuple[int, int], b_pair: tuple[int, int], phase: float | ParameterExpression
) -> QuantumCircuit:
    """Design B's circuit on b = (e_k + e^{i phase} e_l)/sqrt2, one point of the fringe."""
    return lcu_witness(a_pair, b_pair, phase)


def design_c_associator_spectrum(
    dim: int, i: int, j: int, *, omit_adjoint: bool = False, flip: int | None = None
) -> QuantumCircuit:
    """Walsh spectrum of W = L_{e_i e_j}^dagger L_{e_i} L_{e_j} on log2(dim) qubits.

    H^n prepares |+>^n, the three multiplication blocks run separately between
    barriers so the device composes W, and H^n before measurement turns W's
    diagonal phase into a distribution over y. L_{e_i e_j}^dagger =
    cd_sign(dim,i,j) L_{e_{i^j}}^T, so the circuit carries cd_sign(dim,i,j) as
    a global phase and its unitary equals W exactly. omit_adjoint drops the last
    block and flip negates one sign of L_{e_i}; both are controls.
    """
    n = dim.bit_length() - 1
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.barrier()
    qc.append(left_mult_gate(dim, j), range(n))
    qc.barrier()
    qc.append(left_mult_gate(dim, i, flip=flip), range(n))
    qc.barrier()
    if not omit_adjoint:
        qc.append(left_mult_adjoint_gate(dim, i ^ j), range(n))
        if cd_sign(dim, i, j) < 0:
            qc.global_phase += math.pi
        qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def _unitary_part(qc: QuantumCircuit) -> QuantumCircuit:
    """The circuit between the first and last H layers: the composed blocks."""
    core = qc.remove_final_measurements(inplace=False)
    out = QuantumCircuit(core.num_qubits, global_phase=core.global_phase)
    layers = [idx for idx, inst in enumerate(core.data) if inst.operation.name == "barrier"]
    for inst in core.data[layers[0] + 1 : layers[-1]]:
        if inst.operation.name != "barrier":
            out.append(inst.operation, [core.find_bit(q).index for q in inst.qubits])
    return out


class DesignCheckFailed(RuntimeError):
    """A compiled circuit disagreed with its algebraic prediction."""


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise DesignCheckFailed(message)


def _check_design_a() -> None:
    for i, j in combinations(range(1, 8), 2):
        qc, k0, k1, diff = design_a_associator(i, j)
        probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([diff])
        _require(abs(probs[1] - 1.0) < 1e-9, f"design A ({i},{j}) k0={k0} k1={k1} reads P1={probs[1]:.6f}")
    print("design A: all 21 pairs read bit 1 with probability 1")


def _check_reed_muller_phase_oracles() -> None:
    expected_exemplar_operations = {
        8: {"z": 3, "cz": 1},
        16: {"z": 4, "cz": 3, "ccz": 1},
        32: {"z": 5, "cz": 6, "ccz": 4, "c3z": 1},
    }
    worst = 0.0
    constant_true = Operator(phase_oracle_from_truth_table([1, 1], name="constant_true")).data
    worst = max(worst, float(np.max(np.abs(constant_true + np.eye(2)))))
    checked_rows = 0
    for dim in (8, 16, 32):
        for unit_index in range(1, dim):
            truth_table = [0 if cd_sign(dim, unit_index, basis_index) > 0 else 1 for basis_index in range(dim)]
            circuit = phase_oracle_from_truth_table(truth_table, name=f"sign_{dim}_{unit_index}")
            got = Operator(circuit).data
            want = np.diag(np.array([1.0 if value == 0 else -1.0 for value in truth_table]))
            worst = max(worst, float(np.max(np.abs(got - want))))
            checked_rows += 1
    _require(worst < 1e-12, f"Reed-Muller phase oracle deviates by {worst:.2e}")

    for dim, unit_index in SIGN_HIERARCHY_EXEMPLARS:
        truth_table = [0 if cd_sign(dim, unit_index, basis_index) > 0 else 1 for basis_index in range(dim)]
        coefficients = anf_coefficients(truth_table)
        histogram = anf_degree_histogram(coefficients)
        expected_histogram = {
            degree: math.comb(dim.bit_length() - 2, degree) for degree in range(1, dim.bit_length() - 1)
        }
        expected_histogram[1] += 1
        _require(histogram == expected_histogram, f"dim {dim} L_e{unit_index} ANF histogram {histogram}")
        circuit = phase_oracle_from_truth_table(truth_table, name=f"sign_{dim}_{unit_index}")
        operations = {name: int(count) for name, count in circuit.count_ops().items()}
        _require(
            operations == expected_exemplar_operations[dim],
            f"dim {dim} L_e{unit_index} operations {operations}",
        )
    print(
        f"Reed-Muller signs: {checked_rows} row oracles exact within {worst:.1e}; "
        "high-bit ladder emits CZ, CCZ, then C3Z"
    )


def _check_select_and_prep() -> None:
    worst_diagonal = 0.0
    worst_reed_muller = 0.0
    diagonal_cz_savings: list[int] = []
    for i, j in combinations(range(1, 16), 2):
        want = predict.select_matrix(16, i, j)
        diagonal_circuit = select_circuit(16, i, j, "diagonal")
        reed_muller_circuit = select_circuit(16, i, j, "reed_muller")
        diagonal = Operator(diagonal_circuit).data
        reed_muller = Operator(reed_muller_circuit).data
        worst_diagonal = max(worst_diagonal, float(np.max(np.abs(diagonal - want))))
        worst_reed_muller = max(worst_reed_muller, float(np.max(np.abs(reed_muller - want))))
        g = [0 if s > 0 else 1 for s in joint_select_signs(16, i, j)]
        _require(predict.anf_degree(g) == 4, f"SELECT sign for ({i},{j}) has degree {predict.anf_degree(g)}")
        diagonal_isa = transpile(
            diagonal_circuit,
            basis_gates=["cz", "rz", "sx", "x"],
            optimization_level=3,
            seed_transpiler=20261010,
        )
        reed_muller_isa = transpile(
            reed_muller_circuit,
            basis_gates=["cz", "rz", "sx", "x"],
            optimization_level=3,
            seed_transpiler=20261010,
        )
        diagonal_cz_savings.append(
            int(reed_muller_isa.count_ops().get("cz", 0) - diagonal_isa.count_ops().get("cz", 0))
        )
    _require(worst_diagonal < 1e-12, f"diagonal SELECT operator deviates by {worst_diagonal:.2e}")
    _require(worst_reed_muller < 1e-12, f"Reed-Muller SELECT operator deviates by {worst_reed_muller:.2e}")
    _require(
        all(saving > 0 for saving in diagonal_cz_savings),
        f"diagonal SELECT does not win every pinned all-to-all compile: {diagonal_cz_savings}",
    )
    print(
        "SELECT: 105 diagonal and Reed-Muller operators equal the signed-permutation definition "
        f"within {max(worst_diagonal, worst_reed_muller):.1e}; diagonal saves "
        f"{min(diagonal_cz_savings)}..{max(diagonal_cz_savings)} CZ in the pinned all-to-all compile"
    )

    worst = 0.0
    for k, el in combinations(range(16), 2):
        for phase in SWEEP_PHASES:
            want = np.zeros(16, dtype=complex)
            want[k] = 1.0 / math.sqrt(2.0)
            want[el] = np.exp(1j * phase) / math.sqrt(2.0)
            circuit = sparse_pair_prep(4, k, el, phase)
            operations = circuit.count_ops()
            _require(operations.get("h", 0) == 1, f"sparse prep ({k},{el}) has {operations.get('h', 0)} H")
            _require(
                operations.get("cx", 0) == (k ^ el).bit_count() - 1,
                f"sparse prep ({k},{el}) has {operations.get('cx', 0)} CX",
            )
            _require(
                operations.get("p", 0) == int(phase != 0.0),
                f"sparse prep ({k},{el}) phase {phase} has {operations.get('p', 0)} P",
            )
            got = Statevector(circuit).data
            worst = max(worst, float(np.max(np.abs(got - want))))
    _require(worst < 1e-12, f"sparse prep deviates by {worst:.2e}")

    symbolic_phase = Parameter("phi")
    symbolic = sparse_pair_prep(4, 4, 15, symbolic_phase)
    bound_phase = math.pi / 3
    bound = symbolic.assign_parameters({symbolic_phase: bound_phase})
    symbolic_want = np.zeros(16, dtype=complex)
    symbolic_want[4] = 1.0 / math.sqrt(2.0)
    symbolic_want[15] = np.exp(1j * bound_phase) / math.sqrt(2.0)
    _require(
        float(np.max(np.abs(Statevector(bound).data - symbolic_want))) < 1e-12,
        "symbolic sparse-pair phase binding changes the prepared state",
    )

    invalid_preparations = ((0, 0, 1), (4, -1, 1), (4, 0, 16), (4, 3, 3))
    for qubit_count, first_index, second_index in invalid_preparations:
        try:
            sparse_pair_prep(qubit_count, first_index, second_index, 0.0)
        except ValueError:
            pass
        else:
            raise DesignCheckFailed(f"sparse prep accepted n={qubit_count}, indices ({first_index},{second_index})")
    print(
        f"sparse prep: 120 index pairs x {len(SWEEP_PHASES)} phases exact within {worst:.1e}; "
        "one H and popcount(k XOR l)-1 CX"
    )


def _check_design_b() -> None:
    worst = 0.0
    zds = sedenion_zero_divisors()
    for (i, j), (k, el), s in zds:
        # The bright control keeps a and flips s, so b leaves the annihilator.
        for sign, dark in ((s, True), (-s, False)):
            want = predict.zero_divisor_p0((i, j), (k, el), sign)
            _require(not dark or want < 1e-12, f"({i},{j})({k},{el},{s}) is not annihilating: {want}")
            qc = design_b_zero_divisor((i, j), (k, el), sign)
            p0 = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([4])[0]
            worst = max(worst, abs(p0 - want))
    _require(worst < 1e-9, f"design B deviates from |ab|^2/8 by {worst:.2e}")
    print(f"design B: {len(zds)} dark and {len(zds)} bright circuits match |ab|^2/8 within {worst:.1e}")


def _check_design_d() -> None:
    zds = sedenion_zero_divisors()
    for (i, j), (k, el), s in zds:
        for phase in SWEEP_PHASES:
            want = predict.phase_sweep_p0((i, j), (k, el), phase)
            _require(abs(want - (1.0 - s * math.cos(phase)) / 2.0) < 1e-12, f"fringe ({i},{j})({k},{el},{s}) {phase}")
        at_pi = predict.phase_sweep_p0((i, j), (k, el), math.pi)
        _require(
            abs(at_pi - predict.zero_divisor_p0((i, j), (k, el), -1)) < 1e-12,
            f"phi=pi vs cd_multiply ({i},{j})({k},{el})",
        )
    print(f"design D: P(anc=0) = (1 - s cos phi)/2 for all {len(zds)} zero divisors at {len(SWEEP_PHASES)} phases")

    (i, j), (k, el), s = zds[0]
    worst = 0.0
    for phase in SWEEP_PHASES:
        qc = design_d_phase_sweep((i, j), (k, el), phase)
        p0 = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([4])[0]
        worst = max(worst, abs(p0 - predict.phase_sweep_p0((i, j), (k, el), phase)))
    _require(worst < 1e-9, f"design D circuit deviates by {worst:.2e}")
    print(f"  ({i},{j})({k},{el}) sweep circuits match within {worst:.1e}")

    # Each a = e_i + t e_j annihilates a 4-dimensional space spanned by its
    # corpus partners, and (L_i + t L_j)/2 has Gram spectrum {0^4, (1/2)^8, 1^4}.
    partners: dict[tuple[int, int, int], list[np.ndarray]] = defaultdict(list)
    for ci, cj, t, ck, cl, cs in sedenion_zero_divisor_corpus():
        b = np.zeros(16)
        b[ck], b[cl] = 1.0, float(cs)
        partners[(ci, cj, t)].append(b)
    spectra = set()
    for (ci, cj, t), bs in partners.items():
        op = (predict.left_mult_matrix(16, ci) + t * predict.left_mult_matrix(16, cj)) / 2.0
        eig = np.linalg.eigvalsh(op.T @ op)
        spectra.add(tuple(np.round(eig, 9)))
        kernel_dim = int(np.sum(eig < 1e-9))
        _require(kernel_dim == 4, f"annihilator of ({ci},{cj},{t}) has dimension {kernel_dim}")
        _require(np.linalg.matrix_rank(np.array(bs)) == 4, f"partners of ({ci},{cj},{t}) span less than 4 dims")
    _require(len(spectra) == 1, f"Gram spectra differ across a: {spectra}")
    counts = {float(v): list(next(iter(spectra))).count(v) for v in sorted(set(next(iter(spectra))))}
    print(f"  {len(partners)} elements a: annihilator dim 4 spanned by partners; Gram spectrum {counts}")


def _design_c_pair_error(pair: tuple[int, int, int]) -> tuple[float, float]:
    """Largest operator and probability deviation of one Design C circuit from its prediction."""
    dim, i, j = pair
    qc = design_c_associator_spectrum(dim, i, j)
    omega = predict.associator_phase(dim, i, j)
    got = Operator(_unitary_part(qc)).data
    worst_op = float(np.max(np.abs(got - np.diag(np.array(omega, dtype=float)))))
    probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities()
    return worst_op, float(np.max(np.abs(probs - predict.walsh_distribution(omega))))


def _check_design_c() -> None:
    dims = (8, 16, 32)
    pairs_by_dim = {dim: [(dim, i, j) for i, j in combinations(range(1, dim), 2)] for dim in dims}
    errors = parallel.ordered_map(
        _design_c_pair_error, [pair for dim in dims for pair in pairs_by_dim[dim]], min_items=16
    )
    position = 0
    for dim in dims:
        dim_errors = errors[position : position + len(pairs_by_dim[dim])]
        position += len(pairs_by_dim[dim])
        worst_op = max(op for op, _ in dim_errors)
        worst_p = max(p for _, p in dim_errors)
        _require(worst_op < 1e-12 and worst_p < 1e-12, f"dim {dim}: operator {worst_op:.1e}, probs {worst_p:.1e}")
        pairs = (dim - 1) * (dim - 2) // 2
        print(f"design C dim {dim}: {pairs} pairs, W = diag(omega) within {worst_op:.1e}, spectra within {worst_p:.1e}")

    for dim, i, j in SPECTRUM_EXEMPLARS:
        n = dim.bit_length() - 1
        true = predict.walsh_distribution(predict.associator_phase(dim, i, j))
        flipped_phase = [w * (-1 if (j ^ x) == j else 1) for x, w in enumerate(predict.associator_phase(dim, i, j))]
        flipped = predict.walsh_distribution(flipped_phase)
        plus = np.full(dim, 1.0 / math.sqrt(dim))
        hn = np.array([[(-1) ** bin(x & y).count("1") for x in range(dim)] for y in range(dim)]) / math.sqrt(dim)
        omitted = np.abs(hn @ predict.left_mult_matrix(dim, i) @ predict.left_mult_matrix(dim, j) @ plus) ** 2
        for label, qc, want in (
            ("flip", design_c_associator_spectrum(dim, i, j, flip=j), flipped),
            ("omit", design_c_associator_spectrum(dim, i, j, omit_adjoint=True), omitted),
        ):
            probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities()
            _require(float(np.max(np.abs(probs - want))) < 1e-12, f"dim {dim} ({i},{j}) {label} control")
        tvd_flip = 0.5 * float(np.sum(np.abs(true - flipped)))
        tvd_omit = 0.5 * float(np.sum(np.abs(true - omitted)))
        _require(tvd_flip > 0.05 and tvd_omit > 0.05, f"dim {dim} ({i},{j}) controls indistinguishable")
        support = {y: round(float(p), 6) for y, p in enumerate(true) if p > 1e-12}
        print(f"  dim {dim} ({i},{j}) n={n}: P(y) {support}; TVD to flip {tvd_flip:.3f}, to omit {tvd_omit:.3f}")


def _verify() -> None:
    _check_design_a()
    _check_reed_muller_phase_oracles()
    _check_select_and_prep()
    _check_design_b()
    _check_design_d()
    _check_design_c()
    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    for name, qc in (
        ("design A (1,2)", design_a_associator(1, 2)[0]),
        (f"design B ({i},{j})({k},{el})", design_b_zero_divisor((i, j), (k, el), s)),
        *(
            (f"design C dim {d} ({ci},{cj})", design_c_associator_spectrum(d, ci, cj))
            for d, ci, cj in SPECTRUM_EXEMPLARS
        ),
    ):
        tqc = transpile(qc, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3, seed_transpiler=20261010)
        print(f"{name}: all-to-all depth={tqc.depth()} cz={tqc.count_ops().get('cz', 0)}")


if __name__ == "__main__":
    _verify()

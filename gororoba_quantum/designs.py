"""Quantum circuits built from open_gororoba Cayley-Dickson structure.

Left multiplication L_{e_m} by a basis unit is a signed permutation of the 2^k
basis states, so it is unitary and compiles to X plus diagonal-sign gates on k
qubits. Design A turns the octonion associator into a measurable relative phase;
design B turns a sedenion zero divisor into perfect destructive interference
through a one-ancilla linear combination of unitaries. Each circuit's ideal
outcome is predicted from cd_core and checked here by statevector.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate, UnitaryGate
from qiskit.quantum_info import Statevector

from cd_core import cd_multiply, cd_sign, fano_completion, sedenion_zero_divisors


def left_mult_matrix(dim: int, m: int) -> np.ndarray:
    """Matrix of L_{e_m}: |e_q> -> cd_sign(dim,m,q) |e_{m XOR q}>."""
    mat = np.zeros((dim, dim))
    for q in range(dim):
        mat[m ^ q, q] = cd_sign(dim, m, q)
    return mat


def left_mult_gate(dim: int, m: int):
    """Structured L_{e_m}: a +/-1 diagonal (the sign table) then X on the XOR bits.

    L_{e_m}|q> = cd_sign(dim,m,q)|m XOR q> factors into D_m (diagonal of signs,
    a real phase polynomial) followed by the basis permutation q -> m XOR q, one
    X per set bit of m. Used uncontrolled in design A, where the device composes
    three of them so the associator cancellation is physical, not precomputed.
    """
    nq = dim.bit_length() - 1
    signs = [float(cd_sign(dim, m, q)) for q in range(dim)]
    sub = QuantumCircuit(nq, name=f"Le{m}")
    sub.append(DiagonalGate(signs), range(nq))
    for b in range(nq):
        if (m >> b) & 1:
            sub.x(b)
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


def design_b_zero_divisor(
    a_pair: tuple[int, int],
    b_pair: tuple[int, int],
    s: int,
) -> QuantumCircuit:
    """Sedenion zero-divisor witness on 4 data qubits + 1 ancilla (LCU).

    a = e_i + e_j gives L_a = L_{e_i} + L_{e_j}. A one-ancilla linear combination
    applies (L_{e_i}+L_{e_j})/2 to |b> = (|e_k> + s|e_l>)/sqrt2 and post-selects
    ancilla=0. For a true zero divisor a*b=0, so P(anc=0)=0 by interference.
    """
    dim = 16
    i, j = a_pair
    k, el = b_pair
    anc = 4

    qc = QuantumCircuit(5, 1)
    # Prepare |b> = (|e_k> + s|e_l>)/sqrt2 on the 4 data qubits.
    prep = np.zeros(dim)
    prep[k] = 1.0 / np.sqrt(2.0)
    prep[el] = float(s) / np.sqrt(2.0)
    qc.append(UnitaryGate(_state_prep_unitary(prep), label="prep_b"), [0, 1, 2, 3])

    qc.h(anc)
    # Generic synthesis of the controlled signed permutation costs 141 CZ here,
    # fewer than the DiagonalGate-structured route (294 CZ, measured). A hand
    # phase-polynomial compile (CX for the XOR index, CZ/CCZ for the sign) is the
    # sub-100 path and is not yet implemented.
    gi = UnitaryGate(left_mult_matrix(dim, i), label="Lei").control(1, ctrl_state=0)
    gj = UnitaryGate(left_mult_matrix(dim, j), label="Lej").control(1, ctrl_state=1)
    qc.append(gi, [anc, 0, 1, 2, 3])
    qc.append(gj, [anc, 0, 1, 2, 3])
    qc.h(anc)
    qc.measure(anc, 0)
    return qc


def _state_prep_unitary(target: np.ndarray) -> np.ndarray:
    """A unitary whose first column is the target state (Householder)."""
    dim = len(target)
    e0 = np.zeros(dim)
    e0[0] = 1.0
    v = target - e0
    nv = np.linalg.norm(v)
    if nv < 1e-15:
        return np.eye(dim)
    v = v / nv
    return np.eye(dim) - 2.0 * np.outer(v, v)


def lcu_p0_prediction(a_pair: tuple[int, int], b_pair: tuple[int, int], s: int) -> float:
    """P(ancilla = 0) = |a b|^2 / 8 from cd_multiply, a = e_i + e_j, b = e_k + s e_l.

    The post-selected data state is (L_{e_i} + L_{e_j})/2 applied to b/sqrt2,
    whose squared norm is |a b|^2 / 8.
    """
    a = [0.0] * 16
    b = [0.0] * 16
    a[a_pair[0]] = a[a_pair[1]] = 1.0
    b[b_pair[0]] = 1.0
    b[b_pair[1]] = float(s)
    return sum(v * v for v in cd_multiply(16, a, b)) / 8.0


def _verify() -> None:
    """Statevector checks over every instance; raises on the first deviation."""
    print("== Design A: octonion associator phase witness ==")
    for i, j in combinations(range(1, 8), 2):
        qc, k0, k1, diff = design_a_associator(i, j)
        probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([diff])
        if abs(probs[1] - 1.0) > 1e-9:
            raise RuntimeError(f"design A ({i},{j}) k0={k0} k1={k1} reads P1={probs[1]:.6f}, expected 1")
    print("  all 21 pairs read bit 1 with probability 1")
    qc, k0, k1, diff = design_a_associator(1, 2)
    tqc = transpile(qc, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    print(
        f"  (1,2) k0={k0} k1={k1} diff_qubit={diff}; all-to-all depth={tqc.depth()} cz={tqc.count_ops().get('cz', 0)}"
    )

    print("== Design B: sedenion zero-divisor LCU witness ==")
    worst = 0.0
    zds = sedenion_zero_divisors()
    for (i, j), (k, el), s in zds:
        # The bright control keeps a and flips s, so b leaves the annihilator.
        for sign, ideal in ((s, 0.0), (-s, None)):
            qc = design_b_zero_divisor((i, j), (k, el), sign)
            p0 = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([4])[0]
            want = lcu_p0_prediction((i, j), (k, el), sign)
            if ideal is not None and abs(want - ideal) > 1e-12:
                raise RuntimeError(f"({i},{j})({k},{el},{s}) is not annihilating: |ab|^2/8 = {want}")
            worst = max(worst, abs(p0 - want))
            if abs(p0 - want) > 1e-9:
                raise RuntimeError(f"design B ({i},{j})({k},{el},{sign}) P0={p0:.9f}, cd_multiply gives {want:.9f}")
    print(f"  {len(zds)} dark and {len(zds)} bright circuits match |ab|^2/8 within {worst:.1e}")
    (i, j), (k, el), s = zds[0]
    qc_zd = design_b_zero_divisor((i, j), (k, el), s)
    bright = lcu_p0_prediction((i, j), (k, el), -s)
    sym, ctrl_sym = ("+", "-") if s > 0 else ("-", "+")
    print(f"  zero-divisor (e{i}+e{j})*(e{k}{sym}e{el})=0  P(anc=0)=0")
    print(f"  control      (e{i}+e{j})*(e{k}{ctrl_sym}e{el})    P(anc=0)={bright:.6f}")
    tqc = transpile(qc_zd, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    print(f"  all-to-all depth={tqc.depth()} cz={tqc.count_ops().get('cz', 0)}")


if __name__ == "__main__":
    _verify()

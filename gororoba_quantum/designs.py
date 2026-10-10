"""Quantum circuits built from open_gororoba Cayley-Dickson structure.

Left multiplication L_{e_m} by a basis unit is a signed permutation of the 2^k
basis states, so it is unitary and compiles to X plus diagonal-sign gates on k
qubits. Design A turns the octonion associator into a measurable relative phase;
design B turns a sedenion zero divisor into perfect destructive interference
through a one-ancilla linear combination of unitaries. Each circuit's ideal
outcome is predicted from cd_core and checked here by statevector.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import DiagonalGate, UnitaryGate
from qiskit.quantum_info import Statevector

from cd_core import cd_sign, fano_completion, sedenion_zero_divisors


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

    The net operator L_{e_j} then L_{e_i} then L_{e_{i^j}} equals W up to a global
    phase; W is diagonal +/-1 with the associator sign of (e_i, e_j, e_k). The
    three L gates are appended separately with barriers so the hardware performs
    the cancellation. A superposition of a line-completing k0 (associative) and a
    one-bit-away k1 (anti) picks up a relative sign, and a Hadamard on the
    differing qubit makes one measured bit deterministic.
    """
    k0 = fano_completion(i, j)
    assert k0 is not None
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
    assert k1 is not None and diff_bit is not None

    qc = QuantumCircuit(3, 1)
    for b in range(3):
        if (k0 >> b) & 1:
            qc.x(b)
    qc.h(diff_bit)  # (|k0> + |k1>)/sqrt2, since k1 = k0 ^ (1<<diff_bit)
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


def _verify() -> None:
    print("== Design A: octonion associator phase witness ==")
    qc, k0, k1, diff = design_a_associator(1, 2)
    probs = Statevector(qc.remove_final_measurements(inplace=False)).probabilities([diff])
    det = int(np.argmax(probs))
    print(f"  (i,j)=(1,2) k0={k0}(assoc) k1={k1}(anti) diff_qubit={diff}")
    print(f"  readout P0={probs[0]:.3f} P1={probs[1]:.3f} -> deterministic bit {det}")
    tqc = transpile(qc, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    print(f"  transpiled depth={tqc.depth()} 2q(cz)={tqc.count_ops().get('cz', 0)}")

    print("== Design B: sedenion zero-divisor LCU witness ==")
    zds = sedenion_zero_divisors()
    (i, j), (k, el), s = zds[0]
    qc_zd = design_b_zero_divisor((i, j), (k, el), s)
    p_zd = Statevector(qc_zd.remove_final_measurements(inplace=False)).probabilities([4])
    # Control: same a, but a non-annihilating b (flip sign s -> breaks the pair).
    qc_ct = design_b_zero_divisor((i, j), (k, el), -s)
    p_ct = Statevector(qc_ct.remove_final_measurements(inplace=False)).probabilities([4])
    sym = "+" if s > 0 else "-"
    ctrl_sym = "-" if s > 0 else "+"
    print(f"  zero-divisor (e{i}+e{j})*(e{k}{sym}e{el})=0  P(anc=0)={p_zd[0]:.6f}")
    print(f"  control      (e{i}+e{j})*(e{k}{ctrl_sym}e{el})    P(anc=0)={p_ct[0]:.6f}")
    tqc = transpile(qc_zd, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    print(f"  transpiled depth={tqc.depth()} 2q(cz)={tqc.count_ops().get('cz', 0)}")


if __name__ == "__main__":
    _verify()

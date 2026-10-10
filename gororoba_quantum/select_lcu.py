"""Ancilla-selected left multiplication and sparse pair-state preparation.

SELECT|a,x> = cd_sign(dim,m_a,x)|a, m_a ^ x>, with m_0 = i and m_1 = j, factors
into three layers: the diagonal (-1)^g(a,x) over data and ancilla, with
g = f_i(x) ^ a (f_i(x) ^ f_j(x)) and f_m(x) = [cd_sign(dim,m,x) = -1]; X on the
bits of i; and CX from the ancilla onto the bits of i ^ j. The sign layer is one
DiagonalGate on n+1 qubits, so the selected pair costs one diagonal synthesis
in place of two controlled dense unitaries. g has algebraic degree 4 for every
sedenion pair, so a per-monomial Z/CZ/CCZ/C3Z emission costs more than the
uniformly controlled Rz synthesis behind DiagonalGate (Shende, Bullock, and
Markov, quant-ph/0406176, Theorem 7).
"""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterExpression
from qiskit.circuit.library import DiagonalGate

from cd_core import cd_sign


def joint_select_signs(dim: int, i: int, j: int) -> list[float]:
    """Diagonal of (-1)^g(a,x) at index x + dim*a: cd_sign of the selected unit on x."""
    return [float(cd_sign(dim, j if z >= dim else i, z % dim)) for z in range(2 * dim)]


def select_circuit(dim: int, i: int, j: int) -> QuantumCircuit:
    """SELECT on qubits 0..n-1 (data) and n (ancilla); ancilla 0 picks L_{e_i}."""
    n = dim.bit_length() - 1
    qc = QuantumCircuit(n + 1, name=f"select_{i}_{j}")
    qc.append(DiagonalGate(joint_select_signs(dim, i, j)), range(n + 1))
    for b in range(n):
        if i >> b & 1:
            qc.x(b)
    for b in range(n):
        if (i ^ j) >> b & 1:
            qc.cx(n, b)
    return qc


def sparse_pair_prep(n: int, k: int, el: int, phase: float | ParameterExpression) -> QuantumCircuit:
    """(|k> + e^{i phase}|el>)/sqrt2 on n qubits from |0^n>.

    H on a pivot bit of k ^ el, the phase on its |1> branch, CX from the pivot
    to the other bits of k ^ el, then X on the bits of k. The X layer runs last,
    so it relabels |0> -> |k> and |k ^ el> -> |el> without touching the relative
    phase, whatever the pivot bit of k is. popcount(k ^ el) - 1 CX.
    """
    diff = k ^ el
    if diff == 0:
        raise ValueError(f"pair state needs distinct basis indices, got {k} twice")
    pivot = (diff & -diff).bit_length() - 1
    qc = QuantumCircuit(n, name=f"prep_{k}_{el}")
    qc.h(pivot)
    if phase != 0.0:
        qc.p(phase, pivot)
    for b in range(n):
        if b != pivot and diff >> b & 1:
            qc.cx(pivot, b)
    for b in range(n):
        if k >> b & 1:
            qc.x(b)
    return qc

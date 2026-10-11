"""Ancilla-selected left multiplication and sparse pair-state preparation.

SELECT|a,x> = cd_sign(dim,m_a,x)|a, m_a ^ x>, with m_0 = i and m_1 = j, factors
into three layers: the diagonal (-1)^g(a,x) over data and ancilla, with
g = f_i(x) ^ a (f_i(x) ^ f_j(x)) and f_m(x) = [cd_sign(dim,m,x) = -1]; X on the
bits of i; and CX from the ancilla onto the bits of i ^ j. The default sign
strategy uses one DiagonalGate on n+1 qubits, so the selected pair costs one
diagonal synthesis in place of two controlled dense unitaries. The alternate
Reed-Muller strategy emits one controlled-Z gate per ANF monomial and exposes
the exact gate-degree hierarchy. The joint sign has algebraic degree 4 for
every pair of distinct nonzero sedenion units, where the direct route costs
more than the uniformly controlled Rz synthesis behind DiagonalGate (Shende,
Bullock, and Markov, quant-ph/0406176, Theorem 7).
"""

from __future__ import annotations

import math
from typing import Literal

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterExpression
from qiskit.circuit.library import DiagonalGate, ZGate

from boolean_anf import anf_coefficients
from cd_core import cd_sign

SelectSignStrategy = Literal["diagonal", "reed_muller"]


def _validate_dimension_and_indices(dim: int, *indices: int) -> int:
    if dim <= 0 or dim & (dim - 1):
        raise ValueError(f"dimension must be a positive power of two, got {dim}")
    for index in indices:
        if not 0 <= index < dim:
            raise ValueError(f"basis index {index} lies outside dimension {dim}")
    return dim.bit_length() - 1


def phase_oracle_from_anf(
    variable_count: int, coefficients: tuple[int, ...], name: str = "reed_muller_phase"
) -> QuantumCircuit:
    """Build ``diag((-1)^f)`` from the ANF masks of a Boolean function.

    Degree-one and degree-two monomials emit Z and CZ. Higher monomials emit a
    controlled Z with one fewer control than its degree, so cubic and quartic
    masks appear explicitly as CCZ and C3Z gates.
    """
    if variable_count < 1:
        raise ValueError(f"phase oracle needs at least one variable, got {variable_count}")
    if len(set(coefficients)) != len(coefficients):
        raise ValueError("ANF coefficient masks must be unique")
    domain_size = 1 << variable_count
    circuit = QuantumCircuit(variable_count, name=name)
    for monomial_mask in coefficients:
        if not 0 <= monomial_mask < domain_size:
            raise ValueError(f"monomial mask {monomial_mask} lies outside {variable_count}-variable domain")
        monomial_qubits = [bit_index for bit_index in range(variable_count) if monomial_mask & (1 << bit_index)]
        if not monomial_qubits:
            circuit.global_phase += math.pi
        elif len(monomial_qubits) == 1:
            circuit.z(monomial_qubits[0])
        elif len(monomial_qubits) == 2:
            circuit.cz(monomial_qubits[0], monomial_qubits[1])
        elif len(monomial_qubits) == 3:
            circuit.ccz(*monomial_qubits)
        else:
            circuit.append(ZGate().control(len(monomial_qubits) - 1), monomial_qubits)
    return circuit


def phase_oracle_from_truth_table(truth_table: list[int], name: str = "reed_muller_phase") -> QuantumCircuit:
    """Build an exact Reed-Muller phase oracle from a Boolean truth table."""
    coefficients = anf_coefficients(truth_table)
    variable_count = len(truth_table).bit_length() - 1
    return phase_oracle_from_anf(variable_count, coefficients, name)


def joint_select_signs(dim: int, i: int, j: int) -> list[float]:
    """Diagonal of (-1)^g(a,x) at index x + dim*a: cd_sign of the selected unit on x."""
    _validate_dimension_and_indices(dim, i, j)
    return [float(cd_sign(dim, j if z >= dim else i, z % dim)) for z in range(2 * dim)]


def select_circuit(dim: int, i: int, j: int, sign_strategy: SelectSignStrategy = "diagonal") -> QuantumCircuit:
    """SELECT on data qubits 0..n-1 and ancilla n; ancilla zero picks L_ei.

    ``diagonal`` preserves the lower-CZ LCU implementation. ``reed_muller``
    emits the same sign function as explicit Z, CZ, CCZ, and higher controlled-Z
    gates so its maximum gate arity witnesses the Boolean degree.
    """
    n = _validate_dimension_and_indices(dim, i, j)
    signs = joint_select_signs(dim, i, j)
    qc = QuantumCircuit(n + 1, name=f"select_{i}_{j}")
    if sign_strategy == "diagonal":
        qc.append(DiagonalGate(signs), range(n + 1))
    elif sign_strategy == "reed_muller":
        truth_table = [0 if sign > 0 else 1 for sign in signs]
        qc.compose(
            phase_oracle_from_truth_table(truth_table, name=f"select_sign_{i}_{j}"),
            range(n + 1),
            inplace=True,
        )
    else:
        raise ValueError(f"unknown SELECT sign strategy {sign_strategy!r}")
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
    if n < 1:
        raise ValueError(f"pair-state register needs at least one qubit, got {n}")
    dimension = 1 << n
    for index in (k, el):
        if not 0 <= index < dimension:
            raise ValueError(f"basis index {index} lies outside {n}-qubit dimension {dimension}")
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

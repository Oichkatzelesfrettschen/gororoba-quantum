"""Explicit circuits for the three product bases in experiment_references.

Lemma 1.2 of docs/notes/papers/openai-2026-mub-dimension-six.md specifies
U_r = A_r tensor B_r. The encoding places (a,b) at 4*a+b, with labels 3 and
7 fixed. Generic unitary synthesis is unnecessary: the qutrit Fourier matrix
has the exact factorization F3 = A12 B01 C12 D, where the two-level blocks are
A = [[1,-1],[1,1]]/sqrt(2), B = [[1,-sqrt(2)],[sqrt(2),1]]/sqrt(3),
C = [[-1,-i],[-i,-1]]/sqrt(2), and D = diag(1,1,-i).

Circuit time order is D, C12, B01, A12. Each factor fixes qutrit label 3.
Controlled corrections restrict the qubit H and S factors to the three
active qutrit labels. Every builder retains the complete operator, including
the relative phases between the active and leakage subspaces.
"""

from __future__ import annotations

import math
from functools import cache

import sympy as sp
from qiskit import QuantumCircuit

from experiment_references import ACTIVE_INDICES, BASIS_NAMES


@cache
def _fourier_mixing_angle() -> float:
    """Round the exact analytic angle once from eighty decimal digits."""
    return float((2 * sp.atan(sp.sqrt(2))).evalf(80))


def _two_control_phase(circuit: QuantumCircuit, angle: float) -> None:
    """Apply phase exp(i*angle) only to label 7 using binary-control inclusion-exclusion."""
    circuit.cp(angle / 2, 1, 2)
    circuit.cx(0, 1)
    circuit.cp(-angle / 2, 1, 2)
    circuit.cx(0, 1)
    circuit.cp(angle / 2, 0, 2)


def _two_control_ry(circuit: QuantumCircuit, angle: float) -> None:
    """Rotate qubit 2 only when both low bits are one; the controls return to their input values."""
    circuit.cry(angle / 2, 1, 2)
    circuit.cx(0, 1)
    circuit.cry(-angle / 2, 1, 2)
    circuit.cx(0, 1)
    circuit.cry(angle / 2, 0, 2)


def _qutrit_fourier(circuit: QuantumCircuit) -> None:
    """Implement the source Fourier convention on low labels 0, 1, 2 and fix label 3."""
    # D gives only label 2 its phase; both values of the high bit share D.
    circuit.x(0)
    circuit.cp(-math.pi / 2, 0, 1)
    circuit.x(0)

    # CX sends ordered labels (1,2) to (3,2). The subspace minus sign in
    # C12 = -Rx(-pi/2) is relative to labels 0 and 3 and must remain explicit.
    circuit.cx(0, 1)
    circuit.p(math.pi, 1)
    circuit.crx(-math.pi / 2, 1, 0)
    circuit.cx(0, 1)

    # B01 is Ry(2 atan(sqrt(2))) conditioned on the other low bit being zero.
    circuit.x(1)
    circuit.cry(_fourier_mixing_angle(), 1, 0)
    circuit.x(1)

    # The coordinate change reverses the ordered pair, so A12 uses -pi/2.
    circuit.cx(0, 1)
    circuit.cry(-math.pi / 2, 1, 0)
    circuit.cx(0, 1)


def basis_circuit(name: str) -> QuantumCircuit:
    """Return U_r on the six active labels and identity on leakage labels 3 and 7."""
    if name not in BASIS_NAMES[:3]:
        raise ValueError(f"unsupported dimension-six product basis {name!r}")
    circuit = QuantumCircuit(3)
    if name == "computational":
        return circuit
    _qutrit_fourier(circuit)
    if name == "product_chirped":
        # diag(1,omega,omega,1) preserves the inactive low-bit label 3.
        circuit.p(2 * math.pi / 3, 0)
        circuit.p(2 * math.pi / 3, 1)
        circuit.cp(-4 * math.pi / 3, 0, 1)

    # H acts on every high-bit pair. The controlled H = Ry(pi/2) Z
    # cancels H on the leakage pair, where both low bits are one.
    circuit.h(2)
    _two_control_phase(circuit, math.pi)
    _two_control_ry(circuit, math.pi / 2)
    if name == "product_chirped":
        circuit.p(math.pi / 2, 2)
        _two_control_phase(circuit, -math.pi / 2)
    return circuit


def input_permutation_circuit(target: int) -> QuantumCircuit:
    """Swap labels zero and target in a three-qubit register, fixing all other labels."""
    if type(target) is not int or not 0 <= target < 8:
        raise ValueError("input permutation target must be an integer in [0,8)")
    circuit = QuantumCircuit(3)
    if target == 0:
        return circuit
    pivot = (target & -target).bit_length() - 1
    changed = [bit for bit in range(3) if bit != pivot and target & (1 << bit)]
    for bit in changed:
        circuit.cx(pivot, bit)
    controls = [bit for bit in range(3) if bit != pivot]
    circuit.x(controls)
    circuit.ccx(*controls, pivot)
    circuit.x(controls)
    for bit in reversed(changed):
        circuit.cx(pivot, bit)
    return circuit


def transition_circuit(preparation: str, measurement: str, column: int) -> QuantumCircuit:
    """Return U_measurement^dagger U_preparation times the exact input-label transposition."""
    if preparation not in BASIS_NAMES[:3] or measurement not in BASIS_NAMES[:3]:
        raise ValueError("transition requires two admitted dimension-six product bases")
    if type(column) is not int or not 0 <= column < len(ACTIVE_INDICES):
        raise ValueError("transition input column must be an integer in [0,6)")
    circuit = input_permutation_circuit(ACTIVE_INDICES[column])
    if preparation == measurement:
        return circuit
    circuit.compose(basis_circuit(preparation), inplace=True)
    circuit.compose(basis_circuit(measurement).inverse(), inplace=True)
    return circuit

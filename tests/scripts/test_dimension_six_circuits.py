"""Full-operator and exact-algebra checks for analytic dimension-six circuits."""

from __future__ import annotations

import numpy as np
import pytest
import sympy as sp
from qiskit.quantum_info import Operator

import dimension_six_circuits as circuits
import experiment_references as references


def test_fourier_factors_equal_the_exact_source_matrix() -> None:
    omega = (-1 + sp.I * sp.sqrt(3)) / 2
    fourier = sp.Matrix(3, 3, lambda row, column: sp.expand(omega ** ((row * column) % 3))) / sp.sqrt(3)
    first = sp.eye(3)
    first[1:3, 1:3] = sp.Matrix([[1, -1], [1, 1]]) / sp.sqrt(2)
    second = sp.eye(3)
    second[:2, :2] = sp.Matrix([[1, -sp.sqrt(2)], [sp.sqrt(2), 1]]) / sp.sqrt(3)
    third = sp.eye(3)
    third[1:3, 1:3] = sp.Matrix([[-1, -sp.I], [-sp.I, -1]]) / sp.sqrt(2)
    diagonal = sp.diag(1, 1, -sp.I)
    if (first * second * third * diagonal - fourier).applyfunc(sp.simplify) != sp.zeros(3):
        raise RuntimeError("the analytic factors differ from the source Fourier convention")
    if circuits._fourier_mixing_angle() != float((2 * sp.atan(sp.sqrt(2))).evalf(120)):
        raise RuntimeError("the high-precision Fourier angle did not stabilize at binary64 precision")


@pytest.mark.parametrize("name", references.BASIS_NAMES[:3])
def test_basis_operator_preserves_all_active_and_leakage_columns(name: str) -> None:
    circuit = circuits.basis_circuit(name)
    actual = np.asarray(Operator(circuit).data)
    np.testing.assert_allclose(actual, references.embedded_basis(name), atol=3e-15, rtol=0)
    np.testing.assert_allclose(
        actual[:, references.LEAKAGE_INDICES], np.eye(8)[:, references.LEAKAGE_INDICES], atol=2e-15, rtol=0
    )
    if float(circuit.global_phase) != 0:
        raise RuntimeError("the basis construction introduced an unaccounted global phase")


@pytest.mark.parametrize("target", range(8))
def test_input_permutation_swaps_only_its_two_labels(target: int) -> None:
    expected = np.eye(8, dtype=np.complex128)
    expected[:, [0, target]] = expected[:, [target, 0]]
    np.testing.assert_allclose(Operator(circuits.input_permutation_circuit(target)).data, expected, atol=1e-15, rtol=0)


@pytest.mark.parametrize("preparation", references.BASIS_NAMES[:3])
@pytest.mark.parametrize("measurement", references.BASIS_NAMES[:3])
@pytest.mark.parametrize("column", range(6))
def test_every_transition_matches_the_full_declared_operator(preparation: str, measurement: str, column: int) -> None:
    permutation = np.eye(8, dtype=np.complex128)
    target = references.ACTIVE_INDICES[column]
    permutation[:, [0, target]] = permutation[:, [target, 0]]
    expected = references.embedded_basis(measurement).conj().T @ references.embedded_basis(preparation) @ permutation
    circuit = circuits.transition_circuit(preparation, measurement, column)
    actual = np.asarray(Operator(circuit).data)
    np.testing.assert_allclose(actual, expected, atol=6e-15, rtol=0)
    np.testing.assert_allclose(
        actual[:, references.LEAKAGE_INDICES], np.eye(8)[:, references.LEAKAGE_INDICES], atol=3e-15, rtol=0
    )
    if float(circuit.global_phase) != 0:
        raise RuntimeError("transition comparison must include the source global phase")
    admitted_gates = {"x", "h", "p", "cx", "cp", "cry", "crx", "ccx"}
    if set(circuit.count_ops()) - admitted_gates:
        raise RuntimeError("the analytic circuit introduced a gate outside the explicit primitive construction")


@pytest.mark.parametrize("name", ["tao", "missing", ""])
def test_unadmitted_bases_are_rejected(name: str) -> None:
    with pytest.raises(ValueError, match="product basis"):
        circuits.basis_circuit(name)
    with pytest.raises(ValueError, match="product bases"):
        circuits.transition_circuit(name, "computational", 0)


@pytest.mark.parametrize("target", [-1, 8, True, 1.5])
def test_invalid_permutation_targets_are_rejected(target: int) -> None:
    with pytest.raises(ValueError, match="target"):
        circuits.input_permutation_circuit(target)


@pytest.mark.parametrize("column", [-1, 6, True, 1.5])
def test_invalid_transition_columns_are_rejected(column: int) -> None:
    with pytest.raises(ValueError, match="column"):
        circuits.transition_circuit("computational", "product_fourier", column)

"""Scalar native reconstruction retains phase, layout, metric and optical conventions."""

import json
import math
from typing import Any

import mpmath
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from operator_arithmetic import frobenius_residual, native_operator, photonic_template, probabilities


def circuit() -> Any:
    result = QuantumCircuit(3)
    result.rx(0.3, 0)
    result.ry(-0.7, 1)
    result.rz(2 * math.pi / 3, 2)
    result.cz(0, 2)
    result.barrier()
    result.rx(-0.2, 2)
    result.global_phase = 0.37
    return result


def test_scalar_operator_preserves_complete_layout_and_global_phase() -> None:
    source = circuit()
    order = [sum(((label >> bit) & 1) << (2 - bit) for bit in range(3)) for label in range(8)]
    actual = native_operator(source, order)
    np.testing.assert_allclose(actual, Operator(source).data[order], atol=1e-14, rtol=0)
    np.testing.assert_allclose(probabilities(actual), np.abs(Operator(source).data[order, 0]) ** 2, atol=1e-14)
    changed = source.copy()
    changed.rz(0.2, 0)
    if frobenius_residual(actual, native_operator(changed, order)) < 0.1:
        raise RuntimeError("a physical gate mutation vanished from the full-matrix residual")


def test_frobenius_metric_is_explicitly_distinct_from_spectral_norm() -> None:
    identity = np.eye(4, dtype=np.complex128)
    flipped = identity[::-1]
    value = frobenius_residual(identity, flipped)
    if abs(value - math.sqrt(8)) > 1e-14 or value <= np.linalg.norm(identity - flipped, ord=2):
        raise RuntimeError("the numerical diagnostic must retain the Frobenius metric")
    if frobenius_residual(identity, np.exp(0.4j) * identity) > 1e-14:
        raise RuntimeError("global phase must be removed before the Frobenius residual")


def test_arithmetic_isolated_from_ambient_mpmath_precision() -> None:
    previous = mpmath.mp.dps
    try:
        mpmath.mp.dps = 2
        low = native_operator(circuit(), list(range(8)))
        low_norm = frobenius_residual(np.eye(8, dtype=np.complex128), low)
        low_mesh = photonic_template(low)
        mpmath.mp.dps = 100
        high = native_operator(circuit(), list(range(8)))
        high_norm = frobenius_residual(np.eye(8, dtype=np.complex128), high)
        high_mesh = photonic_template(high)
    finally:
        mpmath.mp.dps = previous
    np.testing.assert_array_equal(low, high)
    if low_norm != high_norm or json.dumps(low_mesh) != json.dumps(high_mesh):
        raise RuntimeError("ambient precision changed retained scalar arithmetic")


def test_scalar_optical_mesh_reconstructs_the_complete_operator() -> None:
    import qd_platform
    from hypercomplex_cases import encoded

    matrix = native_operator(circuit(), list(range(8)))
    template, parameters = photonic_template(matrix)
    setting = {
        "name": "complete-operator",
        "circuit_params": parameters,
        "operator": encoded(matrix),
        "column": [[float(value.real), float(value.imag)] for value in matrix[:, 0]],
    }
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "job": "complete-operator",
        "iterations": 1,
        "min_detected_photons": 1,
        "settings": [setting],
    }
    qd_platform.template_experiment(manifest, template)


@pytest.mark.parametrize("malformation", ["layout", "gate", "angle", "global-phase"])
def test_scalar_operator_rejects_unsupported_or_nonfinite_inputs(malformation: str) -> None:
    source = QuantumCircuit(2)
    order = list(range(4))
    if malformation == "layout":
        order = [0, 1, 1, 3]
    elif malformation == "gate":
        source.h(0)
    elif malformation == "angle":
        source.rx(float("nan"), 0)
    else:
        source.global_phase = float("inf")
    with pytest.raises(ValueError):
        native_operator(source, order)


@pytest.mark.parametrize("operation", [probabilities, photonic_template])
def test_scalar_matrix_inputs_are_finite_and_square(operation: Any) -> None:
    with pytest.raises(ValueError, match="finite square"):
        operation(np.array([[complex("nan")]], dtype=np.complex128))
    with pytest.raises(ValueError, match="finite square"):
        operation(np.ones((2, 3), dtype=np.complex128))

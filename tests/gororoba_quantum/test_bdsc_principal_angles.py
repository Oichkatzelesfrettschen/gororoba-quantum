"""Principal angles retain analytic small rotations of rank-four subspaces."""

import math

import numpy as np
import pytest

from bdsc import max_principal_angle_deg


@pytest.mark.parametrize("angle", [0.0, 1e-10, 1e-8, 0.1, math.pi / 2 - 1e-10, math.pi / 2])
@pytest.mark.parametrize("complex_basis", [False, True])
def test_rank_four_rotation_has_analytic_largest_angle(angle: float, complex_basis: bool) -> None:
    basis = np.eye(24, dtype=complex)[:, :4]
    angles = angle / np.arange(1, 5)
    rotated = basis * np.cos(angles) + np.eye(24, dtype=complex)[:, 4:8] * np.sin(angles)
    if complex_basis:
        generator = np.random.default_rng(72)
        coordinates = generator.normal(size=(24, 24)) + 1j * generator.normal(size=(24, 24))
        unitary, _ = np.linalg.qr(coordinates)
        basis, rotated = unitary @ basis, unitary @ rotated
    first = basis @ basis.conj().T
    second = rotated @ rotated.conj().T
    np.testing.assert_allclose(max_principal_angle_deg(first, second), math.degrees(angle), atol=2e-12, rtol=1e-12)
    np.testing.assert_allclose(max_principal_angle_deg(second, first), math.degrees(angle), atol=2e-12, rtol=1e-12)


def test_equal_subspace_ignores_internal_basis_rotation() -> None:
    generator = np.random.default_rng(29)
    basis, _ = np.linalg.qr(generator.normal(size=(24, 4)) + 1j * generator.normal(size=(24, 4)))
    gauge, _ = np.linalg.qr(generator.normal(size=(4, 4)) + 1j * generator.normal(size=(4, 4)))
    equivalent = basis @ gauge
    np.testing.assert_allclose(
        max_principal_angle_deg(basis @ basis.conj().T, equivalent @ equivalent.conj().T),
        0.0,
        atol=2e-12,
    )

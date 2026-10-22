"""Behavioral boundaries for faithful hypercomplex operator experiments."""

import numpy as np
import pytest

from hypercomplex_operators import (
    algebra_certificate,
    grouped_probabilities,
    left_fourier,
    order_interferometer,
    periodic_generator,
    quaternion_matrix,
    right_fourier_real,
    split_evolve,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def test_quaternion_matrices_preserve_products() -> None:
    imaginary_i = quaternion_matrix([0, 1, 0, 0])
    imaginary_j = quaternion_matrix([0, 0, 1, 0])
    imaginary_k = quaternion_matrix([0, 0, 0, 1])
    require(np.array_equal(imaginary_i @ imaginary_j, imaginary_k), "ij must equal k")
    require(np.array_equal(imaginary_j @ imaginary_i, -imaginary_k), "ji must equal -k")


def test_order_signal_is_a_complex_encoding() -> None:
    matrix = order_interferometer(np.pi / 4, np.pi / 4)
    probabilities = grouped_probabilities(matrix[:, 0])
    np.testing.assert_allclose(probabilities, [0.75, 0.25], atol=1e-12)
    np.testing.assert_allclose(grouped_probabilities(matrix[:, 1]), probabilities, atol=1e-12)
    with pytest.raises(ValueError, match="normalized"):
        grouped_probabilities(2 * matrix[:, 0])


def test_resolved_periodic_generator_and_split_step() -> None:
    from scipy.linalg import expm

    generator = periodic_generator(16, 1)
    np.testing.assert_allclose(generator + generator.conj().T, 0, atol=1e-12)
    positions = 2 * np.pi * np.arange(16) / 16
    state = np.zeros((16, 2), dtype=complex)
    state[:, 0] = np.exp(np.cos(positions))
    state /= np.linalg.norm(state)
    reference = expm(generator) @ state.reshape(-1)
    coarse = split_evolve(state.reshape(-1), 1, 1, 8)
    fine = split_evolve(state.reshape(-1), 1, 1, 16)
    ratio = np.linalg.norm(coarse - reference) / np.linalg.norm(fine - reference)
    require(3.5 < ratio < 4.5, "Strang refinement must have second-order convergence")
    np.testing.assert_allclose(np.linalg.norm(fine), 1, atol=1e-12)
    with pytest.raises(ValueError):
        periodic_generator(3, 1)


def test_transforms_keep_their_linearity_boundary() -> None:
    left = left_fourier(4)
    right = right_fourier_real(4)
    np.testing.assert_allclose(left.conj().T @ left, np.eye(8), atol=1e-12)
    np.testing.assert_allclose(right.T @ right, np.eye(16), atol=1e-12)
    right_i = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]])
    structure = np.kron(np.eye(4), right_i)
    require(
        bool(np.linalg.norm(right @ structure - structure @ right) > 1), "right-j kernel must expose real linearity"
    )


def test_exact_algebra_certificate() -> None:
    certificate = algebra_certificate()
    require(certificate["g2_dimension"] == 14, "octonion derivations must have dimension 14")
    require(certificate["e7_stabilizer_dimension"] == 8, "the stabilizer must have dimension 8")
    require(certificate["aligned_commutators_failed"] == 0, "aligned color generators must commute")
    require(certificate["draft_commutators_failed"] == 6, "the draft convention mismatch must remain detectable")
    require(certificate["clifford_image_rank"] == 64, "the image must span M8(C)")
    require(certificate["occupation_dimensions"] == [1, 3, 3, 1], "the Fock multiplicities must hold")

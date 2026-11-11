"""Deterministic covariance, rank, model-degeneracy and finite-difference checks."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from measurement_identifiability import (
    fit_linear_amplitude,
    nuisance_geometry,
    ramsey_decay_design,
    simplex_contrasts,
)


def _close(actual: Any, expected: Any, tolerance: float = 1e-11) -> None:
    if not np.allclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"{actual} differs from {expected}")


def test_correlated_covariance_matches_schur_complement() -> None:
    covariance = np.array([[2.0, 0.3, 0.1], [0.3, 1.0, -0.2], [0.1, -0.2, 0.8]])
    target = np.array([1.0, 0.5, -1.0])
    nuisance = np.ones((3, 1))
    precision = np.linalg.inv(covariance)
    expected = (
        target @ precision @ target
        - (target @ precision @ nuisance).item() ** 2 / (nuisance.T @ precision @ nuisance).item()
    )
    result = nuisance_geometry(target, nuisance, covariance)
    _close(result.fisher_information, expected)
    fit = fit_linear_amplitude(2.5 * target + 4 * nuisance[:, 0], target, nuisance, covariance)
    _close(fit.amplitude, 2.5)
    _close(fit.standard_error, 1 / np.sqrt(expected))
    _close(fit.residual_sum_squares, 0)
    _close(fit.residual_degrees_of_freedom, 1)


def test_rank_deficiency_and_nuisance_unit_rescaling() -> None:
    target = np.array([1.0, -1, 2, -2])
    nuisance = np.column_stack((np.ones(4), np.ones(4) * 1e120, np.zeros(4)))
    result = nuisance_geometry(target, nuisance, np.eye(4))
    _close(result.nuisance_rank, 1)
    _close(result.fisher_information, 10)
    _close(result.identifiable_fraction, 1)


def test_observable_unit_transformation_preserves_information() -> None:
    target = np.array([1.0, 2, 3])
    nuisance = np.ones((3, 1))
    covariance = np.array([[2.0, 0.1, 0.0], [0.1, 3.0, 0.3], [0.0, 0.3, 1.0]])
    transform = np.diag([10.0, 0.1, 2.0])
    before = nuisance_geometry(target, nuisance, covariance)
    after = nuisance_geometry(transform @ target, transform @ nuisance, transform @ covariance @ transform.T)
    _close(after.fisher_information, before.fisher_information)
    _close(after.identifiable_fraction, before.identifiable_fraction)


def test_zero_target_is_not_a_nan_angle() -> None:
    result = nuisance_geometry(np.zeros(3), np.empty((3, 0)), np.eye(3))
    if result.identifiable_fraction is not None or result.principal_angle_degrees is not None:
        raise AssertionError("zero target has no defined angle")
    _close(result.fisher_information, 0)
    with pytest.raises(ValueError, match="unidentifiable"):
        fit_linear_amplitude(np.ones(3), np.zeros(3), np.empty((3, 0)), np.eye(3))


def test_no_nuisances_and_full_span() -> None:
    target = np.array([1.0, 2, 3])
    _close(nuisance_geometry(target, np.empty((3, 0)), np.eye(3)).fisher_information, 14)
    _close(nuisance_geometry(target, np.eye(3), np.eye(3)).fisher_information, 0)
    with pytest.raises(ValueError, match="unidentifiable"):
        fit_linear_amplitude(target, target, np.eye(3), np.eye(3))


def test_ramsey_cannot_separate_two_additive_decay_rates() -> None:
    mean, nuisance, target = ramsey_decay_design(
        np.array([0.0, 1e-6, 3e-6, 7e-6]), amplitude=0.9, phase=0.2, angular_frequency=2e5, decay_rate=3e4
    )
    result = nuisance_geometry(target, nuisance, np.eye(mean.size) * 0.01)
    if result.identifiable_fraction is None or result.identifiable_fraction > 1e-12:
        raise AssertionError("ordinary decay must exactly mimic extra exponential dephasing")
    with pytest.raises(ValueError, match="unidentifiable"):
        fit_linear_amplitude(mean, target, nuisance, np.eye(mean.size))


def test_ramsey_derivatives_against_centered_difference() -> None:
    times = np.array([0.0, 0.2, 0.5])
    parameters = dict(amplitude=0.8, phase=0.3, angular_frequency=1.2, decay_rate=0.4)
    _, nuisance, _ = ramsey_decay_design(times, **parameters)
    # Each perturbation is a fixed analytic fixture, not a randomized experiment.
    for column, name in enumerate(parameters):
        plus, minus = parameters.copy(), parameters.copy()
        plus[name] += 1e-5
        minus[name] -= 1e-5
        derivative = (ramsey_decay_design(times, **plus)[0] - ramsey_decay_design(times, **minus)[0]) / 2e-5
        _close(derivative, nuisance[:, column], 3e-11)


def test_simplex_projection_preserves_identifiable_multinomial_directions() -> None:
    probabilities = np.array([0.2, 0.3, 0.5])
    covariance = np.diag(probabilities) - np.outer(probabilities, probabilities)
    contrasts = simplex_contrasts(3)
    _close(contrasts @ np.ones(3), np.zeros(2))
    _close(contrasts @ contrasts.T, np.eye(2))
    target = np.array([1.0, -1, 0])
    result = nuisance_geometry(contrasts @ target, np.empty((2, 0)), contrasts @ covariance @ contrasts.T)
    _close(result.fisher_information, 1 / 0.2 + 1 / 0.3)


@pytest.mark.parametrize(
    "covariance",
    [np.zeros((2, 2)), [[1, 2], [2, 1]], [[1, 0.3], [0.1, 1]], [[1, 0], [0, np.nan]], np.eye(3)],
)
def test_invalid_covariance_is_refused(covariance: object) -> None:
    with pytest.raises(ValueError):
        nuisance_geometry(np.ones(2), np.empty((2, 0)), covariance)  # type: ignore[arg-type]


def test_complex_input_and_invalid_rank_cutoff_are_refused() -> None:
    with pytest.raises(ValueError, match="real"):
        nuisance_geometry(np.array([1j, 2]), np.empty((2, 0)), np.eye(2))
    with pytest.raises(ValueError, match="cutoff"):
        nuisance_geometry(np.ones(2), np.empty((2, 0)), np.eye(2), relative_cutoff=-1)


def test_singular_simplex_covariance_requires_explicit_contrasts() -> None:
    probabilities = np.array([0.2, 0.3, 0.5])
    covariance = np.diag(probabilities) - np.outer(probabilities, probabilities)
    with pytest.raises(ValueError, match="positive definite"):
        nuisance_geometry(np.array([1.0, -1.0, 0.0]), np.zeros((3, 0)), covariance)


def test_ramsey_overflow_is_a_validation_error() -> None:
    with pytest.raises(ValueError, match="representable"):
        ramsey_decay_design(np.array([1e300]), amplitude=1.0, phase=0.0, angular_frequency=1e300, decay_rate=0.0)

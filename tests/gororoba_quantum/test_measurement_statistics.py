"""Independent finite-outcome and affine-model oracles for measurement statistics."""

import math

import numpy as np
import pytest

from measurement_statistics import (
    MAX_EXACT_COUNT,
    QuadraticScore,
    StatisticsError,
    covariance_matrix,
    covariance_score,
    multinomial_scores,
    predictive_residual,
)


def finite_score(result: QuadraticScore) -> float:
    if result.value is None or not result.supported:
        raise AssertionError(f"expected a supported finite score: {result}")
    return result.value


def test_signed_score_keeps_zero_score_attempts() -> None:
    estimate = multinomial_scores([25, 25, 25, 25], [[1, 0, 0, -1]])
    np.testing.assert_allclose(estimate.means, [0], atol=1e-16)
    np.testing.assert_allclose(estimate.covariance_of_means, [[1 / 200]])
    if estimate.total_count != 100:
        raise AssertionError("zero-score attempts leave the denominator")


def test_shared_count_covariance_matches_indicator_oracle() -> None:
    # X = I0 - I2, Y = I1 + I2. E[XY] = -p2; Cov(X,Y) = -0.5 - (-0.3 * 0.8).
    estimate = multinomial_scores([2, 3, 5], [[1, 0, -1], [0, 1, 1]])
    np.testing.assert_allclose(estimate.means, [-0.3, 0.8])
    np.testing.assert_allclose(estimate.covariance_of_means, [[0.061, -0.026], [-0.026, 0.016]])
    unbiased = multinomial_scores([2, 3, 5], [[1, 0, -1], [0, 1, 1]], estimator="unbiased")
    np.testing.assert_allclose(unbiased.covariance_of_means, estimate.covariance_of_means * 10 / 9)


def test_permutation_affine_map_and_large_offset() -> None:
    counts = np.array([2, 3, 5])
    scores = np.array([[1.0, 0.0, -1.0], [0.0, 1.0, 1.0]])
    original = multinomial_scores(counts.tolist(), scores)
    permutation = [2, 0, 1]
    shuffled = multinomial_scores(counts[permutation].tolist(), scores[:, permutation])
    np.testing.assert_allclose(shuffled.means, original.means)
    np.testing.assert_allclose(shuffled.covariance_of_means, original.covariance_of_means)
    transform = np.array([[2.0, -3.0], [0.0, 0.5]])
    shift = np.array([2.0**40, -(2.0**40)])
    transformed = multinomial_scores(counts.tolist(), transform @ scores + shift[:, None])
    np.testing.assert_allclose(transformed.means, transform @ original.means + shift, rtol=0, atol=2**-12)
    np.testing.assert_allclose(transformed.covariance_of_means, transform @ original.covariance_of_means @ transform.T)


def test_deterministic_score_and_single_trial_do_not_create_significance() -> None:
    estimate = multinomial_scores([1, 0], [[7, -4]])
    np.testing.assert_array_equal(estimate.covariance_of_means, [[0]])
    result = covariance_score([1], estimate.covariance_of_means)
    if result.supported or result.value is not None or result.record()["reference_distribution"] is not None:
        raise AssertionError("an unsupported residual receives no finite score or p-value")


@pytest.mark.parametrize(
    ("counts", "scores", "estimator"),
    [
        ([], [[]], "plugin"),
        ([0, 0], [[0, 1]], "plugin"),
        ([True, 2], [[0, 1]], "plugin"),
        ([1.0, 2], [[0, 1]], "plugin"),
        ([-1, 2], [[0, 1]], "plugin"),
        ([MAX_EXACT_COUNT, 1], [[0, 1]], "plugin"),
        ([1, 0], [[0, 1]], "unbiased"),
        ([1, 1], [[0]], "plugin"),
        ([1, 0], [[0, math.nan]], "plugin"),
        ([1, 0], [[0, math.inf]], "plugin"),
        ([1, 1], [[1j, 0]], "plugin"),
        ([1, 1], [[True, False]], "plugin"),
        ([1, 1], [["1", "2"]], "plugin"),
        ([1, 1], [[0, 1]], "guess"),
        ([1, 1], [[-1e308, 1e308]], "plugin"),
        ([1, 1], [[0.0, 1e-200]], "plugin"),
    ],
)
def test_invalid_score_inputs_reject(counts, scores, estimator) -> None:
    with pytest.raises(StatisticsError):
        multinomial_scores(counts, scores, estimator=estimator)


@pytest.mark.parametrize(
    "matrix",
    [
        [[1, 2], [2, 1]],
        [[0, 1e-100], [1e-100, 1]],
        [[-1e-100, 0], [0, 1]],
        [[1e20, 0, 0], [0, 1e-20, 2e-20], [0, 2e-20, 1e-20]],
        [[1, 0.1], [0, 1]],
        [[math.nan]],
        [[1, 0]],
    ],
)
def test_covariance_admission_rejects_invalid_small_scale_blocks(matrix) -> None:
    with pytest.raises(StatisticsError):
        covariance_matrix(matrix)


def test_singular_covariance_support_and_unit_invariance() -> None:
    matrix = np.array([[1.0, 2.0], [2.0, 4.0]])
    supported = covariance_score([1, 2], matrix)
    if not supported.supported or supported.rank != 1:
        raise AssertionError(supported)
    np.testing.assert_allclose(finite_score(supported), 1.0)
    unsupported = covariance_score([1, -2], matrix)
    if unsupported.supported or unsupported.value is not None:
        raise AssertionError("a pseudoinverse hides a nonzero nullspace residual")
    units = np.diag([1e-80, 1e80])
    changed_units = covariance_score(units @ np.array([1.0, 2.0]), units @ matrix @ units)
    np.testing.assert_allclose(finite_score(changed_units), finite_score(supported))
    tiny = covariance_score([1e-100], [[1e-200]])
    np.testing.assert_allclose(finite_score(tiny), 1.0)


def test_independent_prediction_carries_shared_parameter_covariance() -> None:
    result = predictive_residual([1, 2], [0, 0], [[1, 0], [0, 1]], [[1], [2]], [[0.5]], dependence="independent")
    expected = np.array([[1.5, 1], [1, 3]])
    np.testing.assert_allclose(result.covariance, expected)
    np.testing.assert_allclose(finite_score(result.score), np.array([1, 2]) @ np.linalg.solve(expected, [1, 2]))
    if result.record()["score"]["reference_distribution"] is not None:
        raise AssertionError("predictive score supplies no automatic p-value")


def test_shared_data_subtracts_both_cross_terms() -> None:
    result = predictive_residual(
        [2], [1], [[4]], [[2]], [[1]], dependence="supplied_cross_covariance", cross_covariance=[[1]]
    )
    # Var(y - 2 theta) = 4 + 4 - 2*2*1 = 4.
    np.testing.assert_allclose(result.covariance, [[4]])
    np.testing.assert_allclose(finite_score(result.score), 0.25)


def test_reused_observation_can_cancel_exactly_but_not_hide_a_residual() -> None:
    exact = predictive_residual(
        [1], [1], [[1]], [[1]], [[1]], dependence="supplied_cross_covariance", cross_covariance=[[1]]
    )
    np.testing.assert_array_equal(exact.covariance, [[0]])
    if exact.score.value != 0 or not exact.score.supported:
        raise AssertionError(exact)
    inconsistent = predictive_residual(
        [1], [2], [[1]], [[1]], [[1]], dependence="supplied_cross_covariance", cross_covariance=[[1]]
    )
    if inconsistent.score.supported or inconsistent.score.value is not None:
        raise AssertionError("deterministic prediction disagreement must remain visible")


@pytest.mark.parametrize(
    "arguments",
    [
        {"dependence": "guess"},
        {"dependence": "independent", "cross_covariance": [[0]]},
        {"dependence": "supplied_cross_covariance"},
        {"dependence": "supplied_cross_covariance", "cross_covariance": [[-2]]},
        {"dependence": "supplied_cross_covariance", "cross_covariance": [[0, 0]]},
    ],
)
def test_prediction_rejects_unstated_or_impossible_joint_uncertainty(arguments) -> None:
    # Cross=-2 makes residual variance 6 positive but the JOINT covariance invalid.
    with pytest.raises(StatisticsError):
        predictive_residual([1], [0], [[1]], [[1]], [[1]], **arguments)


def test_missing_parameter_uncertainty_does_not_mean_zero() -> None:
    with pytest.raises(StatisticsError):
        predictive_residual([1], [0], [[1]], [[1]], None, dependence="independent")  # type: ignore[arg-type]


def test_subnormal_variance_is_not_erased_by_symmetrization() -> None:
    variance = np.nextafter(0.0, 1.0)
    np.testing.assert_array_equal(covariance_matrix([[variance]]), [[variance]])
    result = covariance_score([np.sqrt(variance)], [[variance]])
    if not result.supported or result.rank != 1:
        raise AssertionError(result)
    np.testing.assert_allclose(finite_score(result), 1.0)


def test_large_unsupported_residual_has_finite_relative_diagnostic() -> None:
    result = covariance_score([1.7e308, -1.7e308], [[1, 1], [1, 1]])
    if result.supported or result.unsupported_norm is None or not math.isfinite(result.unsupported_norm):
        raise AssertionError(result)


def test_deterministic_violation_keeps_the_same_numerical_rank() -> None:
    covariance: list[list[float]] = [[1, 1 - 2e-14, 0], [1 - 2e-14, 1, 0], [0, 0, 0]]
    supported = covariance_score([1, 1, 0], covariance)
    unsupported = covariance_score([0, 0, 1], covariance)
    if supported.rank != unsupported.rank or supported.tolerance != unsupported.tolerance:
        raise AssertionError("deterministic-violation branch changes the numerical rank convention")


def test_unrepresentable_prediction_variance_does_not_become_certainty() -> None:
    with pytest.raises(StatisticsError, match="underflows"):
        predictive_residual([0], [0], [[0]], [[1e-100]], [[1e-300]], dependence="independent")


def test_nearconstant_scores_keep_variance_below_mean_rounding() -> None:
    result = multinomial_scores([1, 1], [[1.0, np.nextafter(1.0, math.inf)]])
    np.testing.assert_allclose(result.covariance_of_means, [[2.0**-107]], rtol=2e-15, atol=0)

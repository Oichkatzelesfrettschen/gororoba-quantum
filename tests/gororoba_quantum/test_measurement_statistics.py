"""Independent finite-outcome and affine-model oracles for measurement statistics."""

import math
from typing import Any

import numpy as np
import pytest

from measurement_statistics import (
    MAX_EXACT_COUNT,
    QuadraticScore,
    StatisticsError,
    _snap_congruence,
    covariance_matrix,
    covariance_score,
    multinomial_scores,
    predictive_residual,
    reject_nonreal_elements,
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


@pytest.mark.parametrize("delta", [1e-2, 1e-3, 1e-5])
def test_small_residual_covariance_survives_cancellation_of_large_terms(delta: float) -> None:
    # S_y = J C J^T + delta I with cross covariance J C: the joint covariance is PSD by its Schur
    # complement and the exact residual covariance is delta I, a difference of terms near 30.
    jacobian = np.array([[3.0], [7.0]])
    parameter = np.array([[0.5]])
    observation = jacobian @ parameter @ jacobian.T + delta * np.eye(2)
    result = predictive_residual(
        [1, 2],
        [0, 0],
        observation,
        jacobian,
        parameter,
        dependence="supplied_cross_covariance",
        cross_covariance=jacobian @ parameter,
    )
    np.testing.assert_allclose(result.covariance, delta * np.eye(2), rtol=0, atol=1e-13)
    if result.covariance[0, 1] != 0 or result.covariance[1, 0] != 0:
        raise AssertionError("roundoff-sized covariance between the residuals is not snapped to zero")
    np.testing.assert_allclose(finite_score(result.score), 5 / delta, rtol=1e-6)


@pytest.mark.parametrize("parameter_variance", [0.1, 0.5])
@pytest.mark.parametrize("jacobian", [[[3.0], [7.0]], [[1.0], [1.0]], [[2.0], [-5.0]]])
def test_exact_reuse_with_a_cross_block_gives_zero_residual_covariance(
    parameter_variance: float, jacobian: list[list[float]]
) -> None:
    # delta = 0: the residual covariance is exactly zero, so the API admits it as the zero matrix
    # (the documented exact cancellation) and the score then tests residual support alone.
    gradient = np.array(jacobian)
    parameter = np.array([[parameter_variance]])
    arguments = {
        "dependence": "supplied_cross_covariance",
        "cross_covariance": gradient @ parameter,
    }
    observation = gradient @ parameter @ gradient.T
    consistent = predictive_residual([0, 0], [0, 0], observation, gradient, parameter, **arguments)
    np.testing.assert_array_equal(consistent.covariance, np.zeros((2, 2)))
    if consistent.score.value != 0 or not consistent.score.supported:
        raise AssertionError(consistent)
    disagreeing = predictive_residual([1, 2], [0, 0], observation, gradient, parameter, **arguments)
    if disagreeing.score.supported or disagreeing.score.value is not None:
        raise AssertionError("a deterministic disagreement must remain unsupported")


def test_indefinite_joint_covariance_is_rejected_although_the_residual_variance_is_positive() -> None:
    # Eigenvalue -0.8 of the joint matrix; both residual variances (0.2 and 3.8) are positive.
    with pytest.raises(StatisticsError, match="joint covariance: covariance must be positive semidefinite"):
        predictive_residual(
            [1, 2],
            [0, 0],
            [[1, 0.9], [0.9, 1]],
            [[1], [1]],
            [[1]],
            dependence="supplied_cross_covariance",
            cross_covariance=[[0.9], [-0.9]],
        )


def test_psd_check_rejects_an_indefinite_matrix_that_satisfies_cauchy_schwarz() -> None:
    indefinite = [[1, 0.9, 0.9], [0.9, 1, -0.9], [0.9, -0.9, 1]]
    if np.linalg.eigvalsh(indefinite)[0] > -0.5 or np.max(np.abs(indefinite)) > 1:
        raise AssertionError("the fixture must be indefinite with every correlation bounded by one")
    with pytest.raises(StatisticsError, match="positive semidefinite"):
        covariance_matrix(indefinite)
    with pytest.raises(StatisticsError, match="positive semidefinite"):
        covariance_score([1, 0, 0], indefinite)


def test_residual_on_a_zero_variance_coordinate_is_never_supported() -> None:
    covariance: list[list[float]] = [[1, 1 - 2e-14, 0], [1 - 2e-14, 1, 0], [0, 0, 0]]
    result = covariance_score([0, 0, 1], covariance)
    if result.supported or result.value is not None or result.unsupported_norm is not None:
        raise AssertionError(result)
    if not covariance_score([1, 1, 0], covariance).supported:
        raise AssertionError("a residual inside the support of a rank-deficient block stays supported")


@pytest.mark.parametrize("matrix", [[[1, 1e-11], [0, 1]], [[1, 1 + 1e-11], [1 + 1e-11, 1]], [[1, 1e-8], [-1e-8, 1]]])
def test_covariance_tolerance_is_machine_scale_not_nine_digits(matrix: list[list[float]]) -> None:
    with pytest.raises(StatisticsError):
        covariance_matrix(matrix)


def test_numerical_rank_and_support_thresholds_keep_small_directions() -> None:
    # Correlation eigenvalues 2 - 1e-11 and 1e-11 lie far above 64 eps * n yet below 1e-9.
    near = [[1, 1 - 1e-11], [1 - 1e-11, 1]]
    score = covariance_score([1, -1], near)
    if score.rank != 2 or not score.supported:
        raise AssertionError(score)
    np.testing.assert_allclose(finite_score(score), 2 / 1e-11, rtol=1e-3)
    # A relative discrepancy of 1e-6 outside the support of an exactly singular matrix is a violation.
    singular = covariance_score([1, 1 + 1e-6], [[1, 1], [1, 1]])
    if singular.supported or singular.value is not None or not 1e-7 < (singular.unsupported_norm or 0) < 1e-6:
        raise AssertionError(singular)


def test_count_bound_is_two_to_the_fifty_third() -> None:
    if MAX_EXACT_COUNT != 2**53:
        raise AssertionError("the exact integer bound of float64 changes")
    accepted = multinomial_scores([2**53], [[1.0]])
    if accepted.total_count != 2**53:
        raise AssertionError(accepted)
    with pytest.raises(StatisticsError, match="2"):
        multinomial_scores([2**53, 1], [[0.0, 1.0]])


def test_mean_offsets_use_exactly_rounded_sums() -> None:
    # Weighted offsets 2**54, 0.25 and -2**54 sum to 0.25 exactly; a naive left-to-right sum loses the 0.25.
    estimate = multinomial_scores([1, 1, 1, 1], [[0.0, 2.0**56, 1.0, -(2.0**56)]])
    if estimate.means[0] != 0.25:
        raise AssertionError(estimate.means)


def test_row_sums_go_to_the_pool_only_above_the_entry_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    import measurement_statistics as module

    seen: list[tuple[int, int]] = []
    real_map = module.parallel.ordered_map

    def spy(function, items, min_items=module.parallel.MIN_PARALLEL_ITEMS):
        seen.append((len(items), min_items))
        return real_map(function, items, min_items=min_items)

    monkeypatch.setattr(module.parallel, "ordered_map", spy)
    scores = np.sin(np.arange(80 * 5, dtype=float)).reshape(80, 5)
    counts = [1, 2, 3, 4, 5]
    small = multinomial_scores(counts, scores)
    monkeypatch.setattr(module, "POOLED_SUM_ENTRIES", 1)
    large = multinomial_scores(counts, scores)
    # One map per call carries both compensated reductions, so the offset sums never run in a second serial pass.
    if len(seen) != 2 or seen[0][1] <= seen[0][0] or seen[1][1] != module.parallel.MIN_PARALLEL_ITEMS:
        raise AssertionError(seen)
    if seen[1][0] < seen[1][1]:
        raise AssertionError(seen)
    np.testing.assert_array_equal(small.means, large.means)
    np.testing.assert_array_equal(small.covariance_of_means, large.covariance_of_means)


def test_congruence_roundoff_bound_snaps_noise_and_keeps_real_covariance() -> None:
    magnitude = np.ones((2, 2))
    snapped = _snap_congruence(np.array([[1.0, 1e-15], [-1e-15, 1.0]]), magnitude, 1)
    np.testing.assert_array_equal(snapped, np.eye(2))
    kept = _snap_congruence(np.array([[1.0, 1e-9], [1e-9, 1.0]]), magnitude, 1)
    np.testing.assert_array_equal(kept, [[1.0, 1e-9], [1e-9, 1.0]])
    deterministic = _snap_congruence(np.array([[1e-15, 1e-9], [1e-9, 1.0]]), magnitude, 1)
    np.testing.assert_array_equal(deterministic, [[0.0, 0.0], [0.0, 1.0]])
    with pytest.raises(StatisticsError, match="not symmetric"):
        _snap_congruence(np.array([[1.0, 0.5], [0.1, 1.0]]), magnitude, 1)
    with pytest.raises(StatisticsError, match="negative variance"):
        _snap_congruence(np.array([[-1e-3, 0.0], [0.0, 1.0]]), magnitude, 1)


def test_score_mean_keeps_a_small_term_beside_cancelling_ones_in_any_category_order() -> None:
    for row in ([1e16, 1.0, -1e16], [1.0, 1e16, -1e16], [-1e16, 1e16, 1.0]):
        means = multinomial_scores([1, 1, 1], [row]).means
        np.testing.assert_array_equal(means, [1 / 3])


def test_correlated_residual_survives_cancellation_of_shared_uncertainty() -> None:
    shared = 2.0**38
    residual = np.array([[1, 23 / 32, 23 / 32], [23 / 32, 1, 3 / 64], [23 / 32, 3 / 64, 1]])
    result = predictive_residual(
        np.zeros(3),
        np.zeros(3),
        np.full((3, 3), shared) + residual,
        np.ones((3, 1)),
        [[shared]],
        dependence="supplied_cross_covariance",
        cross_covariance=np.full((3, 1), shared),
    )
    np.testing.assert_allclose(result.covariance, residual, atol=1e-3)
    if np.linalg.eigvalsh(result.covariance)[0] <= 0:
        raise AssertionError("the residual covariance must stay positive definite")


def test_both_row_reductions_come_from_the_pool(monkeypatch: pytest.MonkeyPatch, forced_pool: Any) -> None:
    import measurement_statistics as module

    scores = np.sin(np.arange(80 * 5, dtype=float)).reshape(80, 5) * 1e8
    counts = [1, 2, 3, 4, 5]
    monkeypatch.setattr(module, "POOLED_SUM_ENTRIES", 1)

    def boom(parts: object) -> float:
        raise AssertionError("a compensated reduction ran in the parent process")

    # The spawned workers keep the real math.fsum, so a parent-side reduction beside the map fails here.
    with monkeypatch.context() as patch:
        patch.setattr(module.math, "fsum", boom)
        pooled = multinomial_scores(counts, scores)
    if forced_pool.maps != [("function", 80)] or forced_pool.pools != [2]:
        raise AssertionError((forced_pool.maps, forced_pool.pools))
    monkeypatch.setattr(module, "POOLED_SUM_ENTRIES", 2**22)
    monkeypatch.setattr(
        module.parallel, "ordered_map", lambda function, items, min_items=1: [function(i) for i in items]
    )
    serial = multinomial_scores(counts, scores)
    np.testing.assert_array_equal(pooled.means, serial.means)
    np.testing.assert_array_equal(pooled.covariance_of_means, serial.covariance_of_means)


@pytest.mark.parametrize(
    "scores",
    [
        [[True, 0.0]],
        [[0.0, np.bool_(True)]],
        [[1, "2"]],
        [[1.0, 1j]],
        [[1.0, b"2"]],
        [np.array([True, False])],
        np.array([[True, False]]),
    ],
)
def test_scores_reject_a_boolean_string_or_complex_entry_before_promotion(scores: object) -> None:
    with pytest.raises(StatisticsError, match="real integers or floats"):
        multinomial_scores([1, 1], scores)  # type: ignore[arg-type]


def test_admission_keeps_plain_numbers_and_numeric_arrays() -> None:
    for scores in (
        [[1, 2]],
        [[1.5, np.float32(2.0)]],
        [[np.int64(1), 2]],
        ((1.0, 2.0),),
        np.array([[1, 2]]),
        np.array([[1.0, 2.0]]),
    ):
        estimate = multinomial_scores([1, 1], scores)  # type: ignore[arg-type]
        if not np.isfinite(estimate.means).all():
            raise AssertionError(scores)
    reject_nonreal_elements(np.ones((1000, 1000)), name="array")
    with pytest.raises(StatisticsError, match="real integers or floats"):
        reject_nonreal_elements(np.ones((2, 2), dtype=complex), name="array")


def test_score_mean_scales_a_row_whose_products_overflow() -> None:
    estimate = multinomial_scores([10**9], [[1e300]])
    np.testing.assert_array_equal(estimate.means, [1e300])
    np.testing.assert_array_equal(estimate.covariance_of_means, [[0.0]])
    # Each product fits, their sum does not, and the mean is the common value.
    wide = multinomial_scores([1, 1], [[1.7e308, 1.7e308]])
    np.testing.assert_array_equal(wide.means, [1.7e308])
    # A cancelling pair keeps its exact small term through the scaling (the covariance of such a row overflows, so
    # the mean is read from the worker).
    from measurement_statistics import _weighted_mean

    mean = _weighted_mean(np.array([1e300, -1e300, 1.0]), np.array([1e9, 1e9, 3.0]), 2e9 + 3.0)
    if mean != 3 / (2e9 + 3.0):
        raise AssertionError(mean)
    # Score differences that exceed float64 still raise.
    with pytest.raises(StatisticsError, match="overflows"):
        multinomial_scores([1, 1], [[1.7e308, -1.7e308]])


def test_covariance_score_keeps_a_residual_direction_below_the_standardized_underflow() -> None:
    huge = [[1e308, 1e308], [1e308, 1e308]]
    # The residual lies in the nullspace of the rank-one covariance; its standardized entries are 1e-354.
    score = covariance_score([1e-200, -1e-200], huge)
    if score.supported or score.value is not None:
        raise AssertionError(score)
    if not 1.4 < (score.unsupported_norm or 0) < 1.5:
        raise AssertionError(score)
    # A supported direction whose score is below the subnormal range reports the correctly rounded zero.
    supported = covariance_score([1e-200, 1e-200], huge)
    if not supported.supported or supported.value != 0.0:
        raise AssertionError(supported)
    # A coordinate far below the largest one is not flushed silently.
    with pytest.raises(StatisticsError, match="underflows"):
        covariance_score([1e300, 1e-300], [[1.0, 0.0], [0.0, 1.0]])

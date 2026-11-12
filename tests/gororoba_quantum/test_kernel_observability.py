"""Independent exact-matrix and same-attempt oracles for kernel observability."""

from collections import Counter as Counts
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest

from cd_core import left_mult_matrix_exact
from kernel_observability import (
    DEFAULT_COEFFICIENT_ENTRY_BUDGET,
    certify_equal_weight_pair,
    completion_entries,
    exact_herald_moments,
    nested_herald_statistics,
    reconstruct_hermitian,
    tomography_completion,
    uniform_retention_nullity,
)
from provider_counters import Counter, Population, Status


def attempts(value: int) -> Counter:
    return Counter("executions", value, Population.CIRCUIT_EXECUTION, "fixture:0", Status.OBSERVED, "fixture ledger")


@pytest.mark.parametrize("dim,i,j,expected_nullity", [(8, 1, 2, 0), (16, 1, 10, 4), (32, 1, 10, 8)])
@pytest.mark.parametrize("sign", [-1, 1])
def test_normal_herald_moments_match_exact_kraus_words(
    dim: int, i: int, j: int, expected_nullity: int, sign: int
) -> None:
    certificate = certify_equal_weight_pair(dim, i, j, sign)
    if certificate.nullity != expected_nullity:
        raise AssertionError("the CD pair's exact nullity differs")
    vector = [0] * dim
    vector[i], vector[j] = 1, sign
    left = np.asarray(left_mult_matrix_exact(dim, vector), dtype=np.int64)
    predicted = exact_herald_moments(certificate, [0, 1, 2, 3, 4])
    # Actual repeated Kraus words supply an oracle independently of a
    # floating rank or a second evaluation of the spectral formula.
    words = np.stack([np.linalg.matrix_power(left, depth) for depth in range(5)])
    traces = np.sum(words * words, axis=(1, 2))
    actual = tuple(Fraction(int(trace), dim * 4**depth) for depth, trace in enumerate(traces))
    if predicted != actual:
        raise AssertionError(f"herald predictions {predicted} differ from {actual}")
    if predicted[0] != 1 or predicted[1] != Fraction(1, 2):
        raise AssertionError("depth-zero normalization or first herald moment differs")


def test_herald_depth_is_bounded_before_exponentiation() -> None:
    certificate = certify_equal_weight_pair(16, 1, 10, 1)
    if len(exact_herald_moments(certificate, [4096])) != 1:
        raise AssertionError("the largest admitted depth must return one value")
    with pytest.raises(ValueError, match="exact-denominator budget"):
        exact_herald_moments(certificate, [4097])
    with pytest.raises(ValueError, match="exact-denominator budget"):
        exact_herald_moments(certificate, [10**9])


@pytest.mark.parametrize("eta", [Fraction(1), Fraction(3, 4), Fraction(1, 1000)])
def test_uniform_retention_cancels_from_nullity_ratio(eta: Fraction) -> None:
    certificate = certify_equal_weight_pair(16, 1, 10)
    first, second, third = exact_herald_moments(certificate, [1, 2, 3], retention=eta)
    if uniform_retention_nullity(first, second, 16) != 4:
        raise AssertionError("uniform retention changes the exact nullity ratio")
    if eta**2 * first - 3 * eta * second + 2 * third:
        raise AssertionError("the retained moment recurrence fails")


def test_model_diagnostics_are_not_rounded_into_rank_claims() -> None:
    # Legal cumulative probabilities need not obey the ideal spectral model.
    inferred = uniform_retention_nullity(Fraction(1, 2), Fraction(1, 3), 16)
    if inferred != Fraction(8, 3):
        raise AssertionError("the model diagnostic loses its noninteger value")
    with pytest.raises(ValueError, match="positive"):
        uniform_retention_nullity(Fraction(0), Fraction(0), 16)
    with pytest.raises(ValueError, match="exact rational"):
        uniform_retention_nullity(0.5, Fraction(1, 3), 16)  # type: ignore[arg-type]


@pytest.mark.parametrize("arguments", [(True, 1, 2), (6, 1, 2), (16, 0, 1), (16, 1, 1), (16, 1, 16), (16, 1, 2, True)])
def test_bad_basis_pair_is_rejected(arguments: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        certify_equal_weight_pair(*arguments)


def test_bad_certificate_depth_and_retention_are_rejected() -> None:
    certificate = certify_equal_weight_pair(16, 1, 10)
    with pytest.raises(ValueError, match="cd_core"):
        exact_herald_moments(replace(certificate, nullity=0), [1, 2])
    with pytest.raises(ValueError, match="depth"):
        exact_herald_moments(certificate, [True])
    with pytest.raises(ValueError, match="depth"):
        exact_herald_moments(certificate, [-1])
    with pytest.raises(ValueError, match="retention"):
        exact_herald_moments(certificate, [1], retention=Fraction(3, 2))
    if exact_herald_moments(certificate, [0, 1, 2], retention=Fraction(0)) != (1, 0, 0):
        raise AssertionError("zero retention changes depth-zero normalization")


@pytest.mark.parametrize("nullity", [False, 4.0, -1])
def test_certificate_nullity_requires_an_integer(nullity: object) -> None:
    certificate = replace(certify_equal_weight_pair(16, 1, 10), nullity=nullity)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="certificate nullity"):
        exact_herald_moments(certificate, [1])


@pytest.mark.parametrize("estimator", ["plugin", "unbiased"])
def test_nested_covariance_matches_explicit_indicator_records(estimator: str) -> None:
    indicators = np.asarray([[0, 0, 0]] * 6 + [[1, 0, 0]] * 3 + [[1, 1, 0]] * 2 + [[1, 1, 1]])
    result = nested_herald_statistics(
        attempts(12),
        [6, 3, 1],
        sampling="fixed_independent_attempts",
        estimator=estimator,  # type: ignore[arg-type]
    )
    centered = indicators - indicators.mean(axis=0)
    denominator = 12 * (12 if estimator == "plugin" else 11)
    expected = centered.T @ centered / denominator
    np.testing.assert_allclose(result.probabilities, indicators.mean(axis=0), atol=1e-15, rtol=0)
    np.testing.assert_allclose(result.covariance_of_means, expected, atol=1e-15, rtol=0)
    weights = np.array([1, -3, 2])
    np.testing.assert_allclose(result.recurrence_residuals, [indicators.mean(axis=0) @ weights], atol=1e-15)
    np.testing.assert_allclose(result.recurrence_covariance, [[weights @ expected @ weights]], atol=1e-15)
    if result.attempt_counter.source != "fixture ledger" or result.covariance_of_means[0, 1] <= 0:
        raise AssertionError("attempt provenance or shared-attempt covariance disappears")


@pytest.mark.parametrize("count,successes,eta", [(64, [32, 24, 20, 18], 1.0), (512, [128, 48, 20, 9], 0.5)])
def test_exact_model_counts_have_zero_retained_recurrence(count: int, successes: list[int], eta: float) -> None:
    result = nested_herald_statistics(attempts(count), successes, sampling="fixed_independent_attempts", retention=eta)
    np.testing.assert_allclose(result.recurrence_residuals, 0, atol=1e-15, rtol=0)
    if result.recurrence_covariance.shape != (2, 2):
        raise AssertionError("the adjacent recurrence contrasts lose shared covariance")


def test_zero_successes_and_one_depth_remain_defined() -> None:
    result = nested_herald_statistics(attempts(10), [0], sampling="fixed_independent_attempts")
    np.testing.assert_array_equal(result.probabilities, [0.0])
    np.testing.assert_array_equal(result.covariance_of_means, [[0.0]])
    if result.recurrence_residuals.size or result.recurrence_covariance.shape != (0, 0):
        raise AssertionError("one depth cannot produce a three-depth contrast")


@pytest.mark.parametrize(
    "counter",
    [
        Counter("cap", 20, Population.REQUESTED_CAP, "fixture:0", Status.REQUESTED, "request"),
        Counter("accepted", 20, Population.LOGICAL_ACCEPTED, "fixture:0", Status.OBSERVED, "result"),
        Counter("detected", 20, Population.DETECTION_EVENT, "fixture:0", Status.OBSERVED, "result"),
        Counter("trials", None, Population.CIRCUIT_EXECUTION, "fixture:0", Status.UNAVAILABLE, "result"),
        replace(attempts(20), terminated_by="sample cap"),
        replace(attempts(20), source=""),
        replace(attempts(20), scope=""),
    ],
)
def test_requested_selected_missing_or_censored_denominator_is_rejected(counter: Counter) -> None:
    with pytest.raises(ValueError, match="observed"):
        nested_herald_statistics(counter, [10, 5], sampling="fixed_independent_attempts")


@pytest.mark.parametrize("successes", [[], [11], [4, 5], [True], [-1], [0.5]])
def test_invalid_nested_success_counts_are_rejected(successes: list[int]) -> None:
    with pytest.raises(ValueError):
        nested_herald_statistics(attempts(10), successes, sampling="fixed_independent_attempts")


def test_independent_depth_banks_and_invalid_retention_are_rejected() -> None:
    with pytest.raises(ValueError, match="same attempts"):
        nested_herald_statistics(attempts(10), [4, 2], sampling="independent_depths")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="retention"):
        nested_herald_statistics(attempts(10), [4, 2], sampling="fixed_independent_attempts", retention=float("nan"))
    with pytest.raises(ValueError, match="attempts"):
        nested_herald_statistics(attempts(0), [0], sampling="fixed_independent_attempts")


@pytest.mark.parametrize("half_dimension", [1, 2, 7])
def test_completion_is_exact_orthogonal_hermitian_cubic_basis(half_dimension: int) -> None:
    m = half_dimension
    basis = tomography_completion(m)
    a, b = basis.real, basis.imaginary
    expected = {"real_J_commutant": m * m, "real_J_anticommutant": m * (m + 1), "imaginary_skew": m * (2 * m - 1)}
    if Counts(basis.families) != expected or len(basis.names) != 4 * m * m:
        raise AssertionError("the Hermitian direct-sum dimensions differ")
    np.testing.assert_array_equal(a, a.swapaxes(1, 2))
    np.testing.assert_array_equal(b, -b.swapaxes(1, 2))
    flat = np.concatenate((a.reshape(len(a), -1), b.reshape(len(b), -1)), axis=1)
    np.testing.assert_array_equal(flat @ flat.T, np.diag(basis.hs_norm_squared))
    square_real, square_imaginary = a @ a - b @ b, a @ b + b @ a
    np.testing.assert_array_equal(square_real @ a - square_imaginary @ b, a)
    np.testing.assert_array_equal(square_real @ b + square_imaginary @ a, b)
    j = np.block(
        [[np.zeros((m, m), dtype=int), np.eye(m, dtype=int)], [-np.eye(m, dtype=int), np.zeros((m, m), dtype=int)]]
    )
    np.testing.assert_array_equal(a[: m * m] @ j, j @ a[: m * m])
    np.testing.assert_array_equal(a[m * m : m * (2 * m + 1)] @ j, -j @ a[m * m : m * (2 * m + 1)])


def test_completion_resolves_the_commutant_invisible_population_pair() -> None:
    basis = tomography_completion()
    np.testing.assert_array_equal(basis.real[:49, 0, 0], basis.real[:49, 7, 7])
    if basis.real[49, 0, 0] != 1 or basis.real[49, 7, 7] != -1:
        raise AssertionError("the added anticommutant observable fails to resolve e1 versus e9")


def test_complex_state_reconstruction_uses_actual_hilbert_schmidt_norms() -> None:
    # The squared Hilbert-Schmidt norms take the values 2 and 4, and this Hermitian matrix
    # carries weight on off-diagonal entries, so a reconstruction that assumes one common norm fails.
    m = 3
    basis = tomography_completion(m)
    if set(basis.hs_norm_squared.tolist()) != {2, 4}:
        raise AssertionError("the completion must have squared Hilbert-Schmidt norms 2 and 4 at m = 3")
    index = np.arange(2 * m)
    seed = np.sin(1 + index[:, None] * 2 + index[None, :]) + 1j * np.cos(1 + index[:, None] + 3 * index[None, :])
    hermitian = seed + seed.conj().T
    if np.max(np.abs(np.triu(hermitian, 1))) < 0.5 or np.max(np.abs(hermitian.imag)) < 0.5:
        raise AssertionError("the fixture needs off-diagonal and imaginary weight")
    operators = basis.real + 1j * basis.imaginary
    expectations = np.einsum("kij,ji->k", operators, hermitian).real
    np.testing.assert_allclose(reconstruct_hermitian(expectations, m), hermitian, atol=1e-14, rtol=0)


def test_linear_inversion_preserves_nonpositive_and_unnormalized_estimates() -> None:
    basis = tomography_completion(1)
    matrix = np.diag([2.0, -0.5])
    expectations = np.einsum("kij,ji->k", basis.real + 1j * basis.imaginary, matrix).real
    np.testing.assert_allclose(reconstruct_hermitian(expectations, 1), matrix, atol=1e-15, rtol=0)


@pytest.mark.parametrize("dimension", [0, -1, True, 2.5])
def test_invalid_completion_dimension_is_rejected(dimension: int) -> None:
    with pytest.raises(ValueError):
        tomography_completion(dimension)


@pytest.mark.parametrize("values", [[0, 0], [0, 0, 0, float("nan")], [0, 0, 0, 1j], [True] * 4, ["0"] * 4])
def test_invalid_reconstruction_coefficients_are_rejected(values: list[float]) -> None:
    with pytest.raises(ValueError):
        reconstruct_hermitian(values, 1)


@pytest.mark.parametrize(
    ("matrix", "message"),
    [
        ([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "not normal"),
        ([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "Gram spectrum"),
        ([[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], "Gram trace"),
    ],
)
def test_certificate_rejects_a_matrix_failing_each_exact_identity(
    matrix: list[list[int]], message: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Each fixture satisfies the checks before its own: the second is normal, the third has the
    # spectrum {0, 4}, so deleting a check lets the case through or surfaces another message.
    import kernel_observability as module

    monkeypatch.setattr(module, "left_mult_matrix_exact", lambda _dimension, _vector: matrix)
    with pytest.raises(ValueError, match=message):
        certify_equal_weight_pair(4, 1, 2)


def test_second_moment_above_first_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        uniform_retention_nullity(Fraction(1, 3), Fraction(1, 2), 16)
    if uniform_retention_nullity(Fraction(1, 2), Fraction(1, 2), 16) != 8:
        raise AssertionError("equal first and second moments give D/2 * (1/q - 1)")


@pytest.mark.parametrize("retention", [1.5, 2.0, -0.1])
def test_float_retention_outside_the_unit_interval_is_rejected(retention: float) -> None:
    with pytest.raises(ValueError, match="retention"):
        nested_herald_statistics(attempts(10), [4, 2], sampling="fixed_independent_attempts", retention=retention)


def test_completion_refuses_an_allocation_above_its_entry_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    import kernel_observability as module

    def forbidden(*_arguments: object, **_keywords: object) -> None:
        raise AssertionError("an over-budget request reaches the allocator")

    monkeypatch.setattr(module, "_units", forbidden)
    if completion_entries(7) != 32 * 7**4 or completion_entries(7) > DEFAULT_COEFFICIENT_ENTRY_BUDGET:
        raise AssertionError("the default completion must fit the default budget")
    with pytest.raises(ValueError, match="entry_budget"):
        tomography_completion(100)
    with pytest.raises(ValueError, match="entry_budget"):
        tomography_completion(2, entry_budget=completion_entries(2) - 1)
    for budget in (0, True, 1.5):
        with pytest.raises(ValueError, match="entry_budget"):
            tomography_completion(2, entry_budget=budget)  # type: ignore[arg-type]


def test_completion_entry_count_matches_the_allocated_coefficients() -> None:
    basis = tomography_completion(3)
    if basis.real.size + basis.imaginary.size != completion_entries(3):
        raise AssertionError("the budgeted entry count differs from the allocated coefficients")
    tomography_completion(2, entry_budget=completion_entries(2))


@pytest.mark.parametrize("head", [True, np.bool_(True), "1", 1j])
def test_reconstruction_rejects_a_boolean_string_or_complex_entry_before_promotion(head: object) -> None:
    count = tomography_completion(1).hs_norm_squared.shape[0]
    values: list[object] = [head] + [0] * (count - 1)
    with pytest.raises(ValueError, match="real integers or floats"):
        reconstruct_hermitian(values, 1)  # type: ignore[arg-type]
    reconstruct_hermitian([1, *([0.0] * (count - 1))], 1)
    reconstruct_hermitian(np.zeros(count), 1)


def test_herald_moments_keep_their_order_through_the_pool(forced_pool: None) -> None:
    certificate = certify_equal_weight_pair(16, 1, 10, 1)
    depths = list(range(40, -1, -1))
    pooled = exact_herald_moments(certificate, depths, retention=Fraction(3, 4))
    expected = [exact_herald_moments(certificate, [depth], retention=Fraction(3, 4))[0] for depth in depths]
    if list(pooled) != expected:
        raise AssertionError("mapped herald moments differ from the per-depth values")

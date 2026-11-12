"""Full covariance of outcome scores and linearized predictive residuals.

Counts describe one set of independent, fixed-number multinomial trials. Zero-score
outcomes remain in the denominator. This arithmetic does not establish attempt
provenance, a sampling design, model selection independence, or a physical noise
mechanism. Callers supply those contracts separately.

Prediction covariance uses the joint covariance of (observation, fitted parameter):
T = [I, -J], Cov(y - g(theta_hat)) = T Cov(y, theta_hat) T.T. Independence is a
required declaration, never the consequence of a missing cross-covariance. The
quadratic score reports covariance support and numerical rank; it supplies no
chi-squared reference distribution or p-value.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Integral
from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike

import parallel

MAX_EXACT_COUNT = 2**53
RELATIVE_TOLERANCE = 64 * np.finfo(float).eps
# Below this many entries a serial compensated sum finishes before the first pooled map has started
# its workers (measured on x86-64 with two workers: about 60 ns per entry against 0.1 to 0.3 s).
POOLED_SUM_ENTRIES = 2**22
Estimator = Literal["plugin", "unbiased"]
Dependence = Literal["independent", "supplied_cross_covariance"]


class StatisticsError(ValueError):
    """The supplied data do not define the requested finite statistic."""


_NONREAL_SCALARS = (bool, np.bool_, str, bytes, complex, np.complexfloating)


def reject_nonreal_elements(value: object, *, name: str) -> None:
    """Raise StatisticsError unless every element of a nested sequence is a real integer or float scalar.

    NumPy promotes a boolean beside a float to 1.0 and a numeric string beside a number to text, so the dtype of the
    converted array no longer shows what the caller supplied. A list or tuple is therefore judged element by element
    before conversion. An ndarray is judged by its dtype alone (integer, unsigned or float kind), which costs no
    per-element Python work; any other object reaches the dtype check of the caller after np.asarray.
    """
    if isinstance(value, np.ndarray):
        if value.dtype.kind not in "iuf":
            raise StatisticsError(f"{name}: entries must be real integers or floats, not {value.dtype}")
    elif isinstance(value, (list, tuple)):
        try:
            for item in value:
                reject_nonreal_elements(item, name=name)
        except RecursionError as error:
            raise StatisticsError(f"{name}: the nesting is too deep for a numerical array") from error
    elif isinstance(value, _NONREAL_SCALARS):
        raise StatisticsError(f"{name}: entries must be real integers or floats, not {type(value).__name__}")


def real_array(value: ArrayLike, *, ndim: int, name: str) -> np.ndarray:
    """Copy a finite real numerical array; reject coercions from strings/bools/complex."""
    reject_nonreal_elements(value, name=name)
    try:
        raw = np.asarray(value)
        if raw.dtype.kind not in "iuf" or raw.ndim != ndim or any(n == 0 for n in raw.shape):
            raise StatisticsError(f"{name}: a nonempty {ndim}-dimensional real numerical array is required")
        result = np.array(raw, dtype=float, copy=True)
    except (TypeError, OverflowError, ValueError) as error:
        raise StatisticsError(f"{name}: a finite real numerical array is required") from error
    if not np.isfinite(result).all():
        raise StatisticsError(f"{name}: all entries must be finite")
    return result


def _correlation(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    diagonal = np.diag(matrix)
    if np.any(diagonal < 0):
        raise StatisticsError("covariance: negative diagonal")
    active = diagonal > 0
    if np.any(matrix[~active, :] != 0) or np.any(matrix[:, ~active] != 0):
        raise StatisticsError("covariance: a zero-variance coordinate has nonzero covariance")
    scales = np.sqrt(diagonal[active])
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            correlation = (matrix[np.ix_(active, active)] / scales[:, None]) / scales[None, :]
        except FloatingPointError as error:
            raise StatisticsError("covariance: correlation scaling is not representable") from error
    return correlation, scales, active


def covariance_matrix(value: ArrayLike, *, dimension: int | None = None, name: str = "covariance") -> np.ndarray:
    """Admit a finite symmetric PSD covariance after dimensionless diagonal scaling.

    Symmetry and PSD tolerances apply to the correlation matrix, so a large-unit
    variable cannot hide an invalid small-unit block. Zero diagonal means an
    exactly deterministic coordinate and requires an exactly zero row/column.
    Roundoff-sized negative correlation eigenvalues are admitted within
    64 * eps * dimension * max(1, largest absolute eigenvalue).
    """
    matrix = real_array(value, ndim=2, name=name)
    if matrix.shape[0] != matrix.shape[1] or (dimension is not None and matrix.shape != (dimension, dimension)):
        raise StatisticsError(f"{name}: covariance dimensions disagree")
    correlation, _, _ = _correlation(matrix)
    if correlation.size:
        tolerance = RELATIVE_TOLERANCE * len(matrix)
        if np.any(np.abs(correlation) > 1 + tolerance):
            raise StatisticsError(f"{name}: covariance violates the Cauchy-Schwarz bound")
        if not np.allclose(correlation, correlation.T, rtol=0, atol=tolerance):
            raise StatisticsError(f"{name}: covariance must be symmetric")
        symmetric = correlation / 2 + correlation.T / 2
        eigenvalues = np.linalg.eigvalsh(symmetric)
        if eigenvalues[0] < -tolerance * max(1.0, float(np.max(np.abs(eigenvalues)))):
            raise StatisticsError(f"{name}: covariance must be positive semidefinite")
    # Admission above bounds the difference, so this midpoint neither overflows
    # on equal large entries nor erases equal smallest-subnormal variances.
    return matrix + (matrix.T - matrix) / 2


@dataclass(frozen=True)
class ScoreEstimate:
    total_count: int
    means: np.ndarray
    covariance_of_means: np.ndarray
    estimator: Estimator

    def record(self) -> dict[str, Any]:
        return {
            "total_count": self.total_count,
            "means": self.means.tolist(),
            "covariance_of_means": self.covariance_of_means.tolist(),
            "estimator": self.estimator,
            "sampling_assumption": "independent fixed-number multinomial trials",
        }


# A scaled product stays below 2**_SCALED_EXPONENT, and at most 2**53 products (the total count bound) sum to a value
# below 2**1013, inside float64.
_SCALED_EXPONENT = 960


def _exact_parts(row: list[float], counts: list[float], shift: int) -> list[float] | None:
    """Each product n_j s_j 2**shift as its rounded value and its fma remainder; None when a product overflows."""
    parts: list[float] = []
    for value, count in zip(row, counts, strict=True):
        scaled = math.ldexp(value, shift) if shift else value
        product = scaled * count
        if not math.isfinite(product):
            return None
        parts.append(product)
        parts.append(math.fma(scaled, count, -product))
    return parts


def _fsum(parts: list[float] | None) -> float | None:
    """The correctly rounded sum of the parts, or None when a part or the sum overflows float64."""
    if parts is None:
        return None
    try:
        return math.fsum(parts)
    except OverflowError:
        return None


def _weighted_mean(row: np.ndarray, occupied: np.ndarray, total: float) -> float:
    """sum_j n_j s_j / N with the sum exact: each product enters as its rounded value and its fma remainder.

    math.fsum then returns the correctly rounded sum of the exact products, so the mean does not depend on the
    order of the outcome categories and keeps a small term beside large cancelling ones. A row whose products or
    sum overflow is redone with every value scaled by one exact power of two that puts the largest product near
    2**_SCALED_EXPONENT; the scaling is exact except for terms that fall below the subnormal range of the scaled
    row. The mean is a convex combination of the scores, so it stays finite, and the scale is removed after the
    division by N.
    """
    values, counts = row.tolist(), occupied.tolist()
    exact = _fsum(_exact_parts(values, counts, 0))
    if exact is not None:
        return exact / total
    shift = _SCALED_EXPONENT - math.frexp(max(abs(value) for value in values))[1] - math.frexp(max(counts))[1]
    scaled = _fsum(_exact_parts(values, counts, shift))
    if scaled is None:
        raise OverflowError("score times count overflows float64")
    try:
        return math.ldexp(scaled, -shift) / total
    except OverflowError:
        # N times the mean exceeds float64 while the mean fits; dividing before removing the scale keeps it finite.
        return math.ldexp(scaled / total, -shift)


def _row_reductions(task: tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]) -> tuple[float, float]:
    """The two compensated reductions of one score row: its exact weighted mean and the sum of its weighted offsets.

    The offsets are the scores minus the anchor entry and the weights are the outcome probabilities, so the
    second value is the mean of the offsets that centering subtracts. Serial and pooled dispatch run this one
    function, which makes their results bit-identical.
    """
    row, occupied, total, offsets, weights = task
    return _weighted_mean(row, occupied, total), math.fsum((offsets * weights).tolist())


def multinomial_scores(counts: Sequence[int], scores: ArrayLike, *, estimator: Estimator = "plugin") -> ScoreEstimate:
    """Means and full covariance for score rows over mutually exclusive outcomes.

    For centered per-outcome vectors d_j and empirical probabilities p_j, the
    plug-in covariance is sum_j p_j d_j d_j.T / N. The unbiased version replaces
    N by N-1. Offset-centering precedes accumulation, and weighted square roots
    precede squaring. Totals above 2**53 are rejected instead of rounding counts.
    """
    if estimator not in ("plugin", "unbiased"):
        raise StatisticsError("estimator must be plugin or unbiased")
    if len(counts) == 0 or any(isinstance(n, bool) or not isinstance(n, Integral) or n < 0 for n in counts):
        raise StatisticsError("counts must be a nonempty sequence of nonnegative integers")
    total = sum(int(n) for n in counts)
    if total < 1 or total > MAX_EXACT_COUNT:
        raise StatisticsError("total count must lie in [1, 2**53]")
    if estimator == "unbiased" and total < 2:
        raise StatisticsError("unbiased covariance requires at least two trials")
    score = real_array(scores, ndim=2, name="scores")
    if score.shape[1] != len(counts):
        raise StatisticsError("score columns must match outcome counts")
    probabilities = np.asarray(counts, dtype=float) / total
    positive = probabilities > 0
    denominator = total if estimator == "plugin" else total - 1
    anchor = score[:, np.flatnonzero(positive)[0]]
    try:
        with np.errstate(over="raise", invalid="raise"):
            offsets = score[:, positive] - anchor[:, None]
            weights = probabilities[positive]
            occupied = np.asarray(counts, dtype=float)[positive]
            rows = [
                (row, occupied, float(total), offset, weights)
                for row, offset in zip(score[:, positive], offsets, strict=True)
            ]
            pooled = offsets.size >= POOLED_SUM_ENTRIES
            reductions = parallel.ordered_map(
                _row_reductions, rows, min_items=parallel.MIN_PARALLEL_ITEMS if pooled else len(rows) + 1
            )
            means = np.array([mean for mean, _ in reductions])
            # Centering uses the mean of the offsets, which keeps a spread far below the rounding of the mean.
            mean_offsets = np.array([offset_sum for _, offset_sum in reductions])
            centered = offsets - mean_offsets[:, None]
            weighted = centered * np.sqrt(weights / denominator)
            covariance = weighted @ weighted.T
    except (FloatingPointError, OverflowError) as error:
        raise StatisticsError("score arithmetic overflows float64") from error
    if not np.isfinite(means).all() or not np.isfinite(covariance).all():
        raise StatisticsError("score result is not finite")
    if np.any((np.diag(covariance) == 0) & np.any(centered != 0, axis=1)):
        raise StatisticsError("nonzero score variance underflows float64")
    return ScoreEstimate(total, means, covariance, estimator)


@dataclass(frozen=True)
class QuadraticScore:
    value: float | None
    rank: int
    supported: bool
    unsupported_norm: float | None
    tolerance: float

    def record(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "covariance_rank": self.rank,
            "supported": self.supported,
            "unsupported_relative_standardized_norm": self.unsupported_norm,
            "rank_tolerance": self.tolerance,
            "reference_distribution": None,
        }


def covariance_score(residual: ArrayLike, covariance: ArrayLike) -> QuadraticScore:
    """A covariance quadratic form that never discards a deterministic discrepancy.

    A pseudoinverse alone assigns zero weight to unsupported residual directions.
    This function first tests support in standardized coordinates, then evaluates
    the form only in the supported eigenspace. No fitted-model degrees of freedom
    are inferred from this numerical rank. unsupported_norm is the norm of the
    null projection divided by the largest absolute standardized coordinate;
    it is None when a nonzero residual has exactly zero coordinate variance.
    """
    vector = real_array(residual, ndim=1, name="residual")
    matrix = covariance_matrix(covariance, dimension=len(vector))
    correlation, scales, active = _correlation(matrix)
    if not correlation.size:
        if np.any(vector != 0):
            return QuadraticScore(None, 0, False, None, 0.0)
        return QuadraticScore(0.0, 0, True, 0.0, 0.0)
    eigenvalues, eigenvectors = np.linalg.eigh(correlation / 2 + correlation.T / 2)
    tolerance = RELATIVE_TOLERANCE * len(vector) * max(1.0, float(np.max(np.abs(eigenvalues))))
    positive = eigenvalues > tolerance
    rank = int(np.count_nonzero(positive))
    if np.any(vector[~active] != 0):
        return QuadraticScore(None, rank, False, None, tolerance)
    # The residual is scaled by the exact power of two 2**-exponent that brings its largest entry to [0.5, 1), so the
    # quotient by a large scale keeps its direction; the unscaled standardized residual is `standardized` * 2**exponent.
    exponent = int(np.frexp(np.max(np.abs(vector)))[1]) if np.any(vector != 0) else 0
    active_vector = vector[active]
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            standardized = np.ldexp(active_vector, -exponent) / scales
        except FloatingPointError as error:
            raise StatisticsError("standardized residual is not representable") from error
    if np.any((active_vector != 0) & (standardized == 0)):
        raise StatisticsError("a nonzero standardized residual coordinate underflows float64")
    scale = float(np.max(np.abs(standardized)))
    direction = standardized / scale if scale else standardized
    if np.any((standardized != 0) & (direction == 0)):
        raise StatisticsError("a nonzero standardized residual coordinate underflows float64")
    coordinates = eigenvectors.T @ direction
    unsupported = float(np.linalg.norm(coordinates[~positive]))
    supported = bool(unsupported <= RELATIVE_TOLERANCE * len(vector))
    value: float | None = None
    if supported:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            try:
                mantissa, scale_exponent = math.frexp(scale)
                whitened = (coordinates[positive] / np.sqrt(eigenvalues[positive])) * mantissa
                value = math.ldexp(float(whitened @ whitened), 2 * (exponent + scale_exponent))
            except (FloatingPointError, OverflowError) as error:
                raise StatisticsError("quadratic score is not representable") from error
        if not math.isfinite(value):
            raise StatisticsError("quadratic score is not finite")
    return QuadraticScore(value, rank, supported, unsupported, tolerance)


@dataclass(frozen=True)
class PredictiveResidual:
    residual: np.ndarray
    covariance: np.ndarray
    dependence: Dependence
    score: QuadraticScore

    def record(self) -> dict[str, Any]:
        return {
            "residual": self.residual.tolist(),
            "covariance": self.covariance.tolist(),
            "dependence": self.dependence,
            "approximation": "first-order delta method; exact for an affine predictor",
            "score": self.score.record(),
        }


def _snap_congruence(product: np.ndarray, magnitude: np.ndarray, terms: int) -> np.ndarray:
    """Admit a congruence product up to a roundoff tolerance and snap roundoff to zero.

    Each entry of S C S.T sums `terms` products twice, so its floating-point error
    scales with terms * eps * (|S| |C| |S|.T), the magnitude of the terms rather than
    of their sum. The tolerance is RELATIVE_TOLERANCE (64 eps, the margin of every
    other tolerance in this module) times that quantity. hypothesis: it dominates
    the roundoff of the two matrix products; no error analysis is retained, and the
    tests exercise it on residual scales from 1e-1 down to exact cancellation. A small residual covariance that is a
    difference of large terms therefore keeps its sign and symmetry tests at the
    scale of the cancellation. Entries within the bound become zero where that keeps the smallest eigenvalue, and a
    coordinate whose variance is within its bound is treated as deterministic, so
    an exactly cancelling shared-data prediction yields the zero covariance.
    """
    bound = RELATIVE_TOLERANCE * max(terms, 1) * (magnitude + (magnitude.T - magnitude) / 2)
    if np.any(np.abs(product - product.T) > bound + bound.T):
        raise StatisticsError("residual covariance: congruence is not symmetric beyond its roundoff bound")
    if np.any(np.diag(product) < -np.diag(bound)):
        raise StatisticsError("residual covariance: negative variance beyond the congruence roundoff bound")
    snapped = product + (product.T - product) / 2
    deterministic = np.diag(snapped) <= np.diag(bound)
    # Zeroing single entries can turn a positive-definite matrix indefinite, so the entrywise snap is kept only
    # when it does not lower the smallest eigenvalue; otherwise the entries keep their computed values.
    entrywise = np.where(np.abs(snapped) <= bound, 0.0, snapped)
    if np.linalg.eigvalsh(entrywise)[0] >= np.linalg.eigvalsh(snapped)[0]:
        snapped = entrywise
    snapped[deterministic, :] = 0.0
    snapped[:, deterministic] = 0.0
    return snapped


def predictive_residual(
    observed: ArrayLike,
    predicted: ArrayLike,
    observation_covariance: ArrayLike,
    jacobian: ArrayLike,
    parameter_covariance: ArrayLike,
    *,
    dependence: Dependence,
    cross_covariance: ArrayLike | None = None,
) -> PredictiveResidual:
    """Propagate observation, parameter and (when present) shared-data uncertainty.

    cross_covariance is Cov(y, theta_hat), shaped observations x parameters. The
    full joint covariance must be PSD: a cross block cannot be admitted merely
    because the final residual covariance happens to be positive. Missing fitted
    parameter covariance is an error. This API does not fit or select the model.

    The residual covariance is admitted to the roundoff of its congruence, a bound
    built from the magnitudes of the terms (see _snap_congruence), so a small
    residual covariance that is a difference of large terms is accepted. A coordinate
    whose variance lies within the bound becomes deterministic: exact reuse of an observation by the fit yields
    the zero covariance, and the score then reports whether the residual is
    supported. A rank-deficient nonzero residual covariance is still held to the
    correlation tolerance of covariance_matrix.
    """
    y = real_array(observed, ndim=1, name="observed")
    prediction = real_array(predicted, ndim=1, name="predicted")
    gradient = real_array(jacobian, ndim=2, name="jacobian")
    if prediction.shape != y.shape or gradient.shape[0] != len(y):
        raise StatisticsError("prediction and Jacobian observation dimensions disagree")
    observed_covariance = covariance_matrix(observation_covariance, dimension=len(y), name="observation covariance")
    fitted_covariance = covariance_matrix(
        parameter_covariance, dimension=gradient.shape[1], name="parameter covariance"
    )
    if dependence == "independent":
        if cross_covariance is not None:
            raise StatisticsError("independence and a supplied cross-covariance are mutually exclusive")
        cross = np.zeros_like(gradient)
    elif dependence == "supplied_cross_covariance":
        if cross_covariance is None:
            raise StatisticsError("shared-data prediction requires a supplied cross-covariance")
        cross = real_array(cross_covariance, ndim=2, name="cross-covariance")
        if cross.shape != gradient.shape:
            raise StatisticsError("cross-covariance must have observations x parameters shape")
    else:
        raise StatisticsError("dependence must be independent or supplied_cross_covariance")
    joint = covariance_matrix(
        np.block([[observed_covariance, cross], [cross.T, fitted_covariance]]), name="joint covariance"
    )
    correlation, scales, active = _correlation(joint)
    transform = np.concatenate((np.eye(len(y)), -gradient), axis=1)
    try:
        with np.errstate(over="raise", invalid="raise"):
            scaled_transform = transform[:, active] * scales
            if np.any((transform[:, active] != 0) & (scaled_transform == 0)):
                raise StatisticsError("nonzero predictive covariance factor underflows float64")
            # Form the small congruence directly. This preserves exact cancellation
            # for y == theta_hat with an identity predictor and exact covariance.
            projected_transform = scaled_transform @ correlation
            residual_covariance = projected_transform @ scaled_transform.T
            magnitude = np.abs(scaled_transform) @ np.abs(correlation) @ np.abs(scaled_transform).T
            if np.any((np.diag(magnitude) == 0) & np.any(projected_transform != 0, axis=1)):
                raise StatisticsError("nonzero predictive variance underflows float64")
            residual = y - prediction
    except FloatingPointError as error:
        raise StatisticsError("predictive covariance arithmetic overflows float64") from error
    residual_covariance = covariance_matrix(
        _snap_congruence(residual_covariance, magnitude, int(np.count_nonzero(active))),
        dimension=len(y),
        name="residual covariance",
    )
    return PredictiveResidual(
        residual, residual_covariance, dependence, covariance_score(residual, residual_covariance)
    )

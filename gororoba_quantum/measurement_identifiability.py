"""Local distinguishability of specified measurement models under covariance.

The caller supplies physically justified response derivatives and an
independently qualified covariance. A nuisance tangent span is not the set
of all conventional physics. The Gaussian linear fit is conditional on its
model; it does not turn dependent shots into independent interventions.
No provider data, inference threshold, calibration, or random seed is
chosen by this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Geometry:
    """Whitened local target geometry, with undefined zero-target angles kept absent."""

    nuisance_rank: int
    nuisance_singular_values: np.ndarray
    whitened_target: np.ndarray
    residual: np.ndarray
    fisher_information: float
    identifiable_fraction: float | None
    principal_angle_degrees: float | None


@dataclass(frozen=True)
class LinearFit:
    """Generalized least-squares amplitude and conditional Gaussian uncertainty."""

    amplitude: float
    standard_error: float
    residual_sum_squares: float
    residual_degrees_of_freedom: int
    geometry: Geometry


def _finite(value: np.ndarray, name: str, ndim: int) -> np.ndarray:
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise ValueError(f"{name} must be real, not silently projected from complex values")
    result = np.asarray(value, dtype=np.float64)
    if result.ndim != ndim or not np.isfinite(result).all():
        raise ValueError(f"{name} needs a finite {ndim}-dimensional array")
    return result


def _whiten(covariance: np.ndarray, *arrays: np.ndarray) -> tuple[np.ndarray, ...]:
    covariance = _finite(covariance, "covariance", 2)
    n = covariance.shape[0]
    if n == 0 or covariance.shape != (n, n) or any(a.shape[0] != n for a in arrays):
        raise ValueError("covariance and observation dimensions disagree")
    scale = float(np.max(np.abs(covariance)))
    if scale == 0 or not np.allclose(covariance / scale, covariance.T / scale, atol=1e-12, rtol=0):
        raise ValueError("covariance must be nonzero and symmetric")
    normalized = (covariance / scale + covariance.T / scale) / 2
    eigenvalues = np.linalg.eigvalsh(normalized)
    rank_floor = np.finfo(float).eps * n * float(eigenvalues[-1])
    if eigenvalues[0] <= max(0.0, rank_floor):
        raise ValueError("covariance must be numerically positive definite; project known constraints first")
    try:
        factor = np.linalg.cholesky(normalized)
    except np.linalg.LinAlgError as error:
        raise ValueError("covariance must be positive definite; project known constraints first") from error
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            whitened = tuple(np.linalg.solve(factor, array / math.sqrt(scale)) for array in arrays)
        except FloatingPointError as error:
            raise ValueError("whitened model is not representable in float64") from error
    if any(not np.isfinite(array).all() for array in whitened):
        raise ValueError("whitened model is not representable in float64")
    return whitened


def _nuisance_basis(nuisance: np.ndarray, relative_cutoff: float | None) -> tuple[np.ndarray, np.ndarray]:
    rows, columns = nuisance.shape
    if relative_cutoff is None:
        cutoff = np.finfo(float).eps * max(rows, columns, 1)
    else:
        if not math.isfinite(relative_cutoff) or not 0 <= relative_cutoff < 1:
            raise ValueError("relative singular cutoff must be in [0, 1)")
        cutoff = relative_cutoff
    if columns == 0:
        return np.zeros((rows, 0)), np.zeros(0)
    # Unit changes of nuisance coordinates must not decide numerical rank.
    scales = np.max(np.abs(nuisance), axis=0)
    active = scales > 0
    normalized = nuisance[:, active] / scales[active]
    if normalized.shape[1] == 0:
        return np.zeros((rows, 0)), np.zeros(0)
    normalized /= np.linalg.norm(normalized, axis=0)
    u, singular, _ = np.linalg.svd(normalized, full_matrices=False)
    rank = int(np.count_nonzero(singular > cutoff * singular[0]))
    return u[:, :rank], singular


def nuisance_geometry(
    target: np.ndarray,
    nuisance: np.ndarray,
    covariance: np.ndarray,
    *,
    relative_cutoff: float | None = None,
) -> Geometry:
    """Whiten first, then project the target off the nuisance column span.

    Rank-deficient or empty nuisance designs are valid. A zero target has
    zero information and no defined principal angle or identifiable fraction.
    A singular covariance is refused rather than silently discarding an
    exactly known observable. Use explicit contrasts for simplex data.
    """
    target = _finite(target, "target", 1)
    nuisance = _finite(nuisance, "nuisance", 2)
    t, n = _whiten(covariance, target, nuisance)
    basis, singular = _nuisance_basis(n, relative_cutoff)
    magnitude = float(np.max(np.abs(t)))
    if magnitude == 0:
        return Geometry(basis.shape[1], singular, t, t.copy(), 0.0, None, None)
    scaled = t / magnitude
    projected = scaled - basis @ (basis.T @ scaled)
    residual = projected * magnitude
    norm = float(np.linalg.norm(scaled))
    fraction = min(1.0, float(np.linalg.norm(projected)) / norm)
    with np.errstate(over="raise", invalid="raise"):
        try:
            information = float(np.dot(residual, residual))
        except FloatingPointError as error:
            raise ValueError("Fisher information is not representable in float64") from error
    if not math.isfinite(information) or (information == 0 and np.any(residual != 0)):
        raise ValueError("Fisher information is not representable in float64")
    return Geometry(
        basis.shape[1], singular, t, residual, information, fraction, math.degrees(math.asin(fraction))
    )


def fit_linear_amplitude(
    observed_minus_baseline: np.ndarray,
    target: np.ndarray,
    nuisance: np.ndarray,
    covariance: np.ndarray,
    *,
    relative_cutoff: float | None = None,
) -> LinearFit:
    """Profile unrestricted linear nuisances in a Gaussian model with known covariance.

    An amplitude indistinguishable from nuisance coordinates is refused.
    Returned uncertainty conditions on the supplied covariance and tangent
    model; it is not a calibrated test of a nonlinear or unknown instrument.
    """
    y = _finite(observed_minus_baseline, "observation", 1)
    target = _finite(target, "target", 1)
    nuisance = _finite(nuisance, "nuisance", 2)
    geometry = nuisance_geometry(target, nuisance, covariance, relative_cutoff=relative_cutoff)
    tolerance = np.finfo(float).eps * max(nuisance.shape[0], nuisance.shape[1], 1) * 8
    if geometry.identifiable_fraction is None or geometry.identifiable_fraction <= tolerance:
        raise ValueError("target is unidentifiable against the nuisance design")
    whitened_y, whitened_n = _whiten(covariance, y, nuisance)
    amplitude = float(np.dot(geometry.residual, whitened_y) / geometry.fisher_information)
    basis, _ = _nuisance_basis(whitened_n, relative_cutoff)
    remainder = whitened_y - amplitude * geometry.whitened_target
    remainder -= basis @ (basis.T @ remainder)
    squared = float(np.dot(remainder, remainder))
    standard_error = 1 / math.sqrt(geometry.fisher_information)
    if not all(math.isfinite(v) for v in (amplitude, squared, standard_error)):
        raise ValueError("linear fit is not representable in float64")
    return LinearFit(amplitude, standard_error, squared, y.size - basis.shape[1] - 1, geometry)


def simplex_contrasts(categories: int) -> np.ndarray:
    """Orthonormal Helmert rows removing only the known sum-to-one constraint."""
    if type(categories) is not int or categories < 2:
        raise ValueError("at least two categories are required")
    row = np.arange(1, categories, dtype=np.float64)[:, None]
    column = np.arange(categories)[None, :]
    return np.where(column < row, 1.0, np.where(column == row, -row, 0.0)) / np.sqrt(row * (row + 1))


def ramsey_decay_design(
    times_seconds: np.ndarray, *, amplitude: float, phase: float, angular_frequency: float, decay_rate: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return quadrature mean, ordinary nuisance derivatives and extra-dephasing derivative.

    Quadratures are interleaved Re(C), Im(C). Frequency is radians/second,
    decay rates are inverse seconds. Nuisance columns are amplitude, phase,
    angular frequency and ordinary decay. The last equals the proposed
    extra-dephasing target exactly: this design alone cannot identify two
    additive rates. No particular objective-collapse model is assumed.
    """
    times = _finite(times_seconds, "times", 1)
    if times.size == 0 or np.any(times < 0):
        raise ValueError("times must be nonempty and nonnegative")
    if not all(math.isfinite(v) for v in (amplitude, phase, angular_frequency, decay_rate)):
        raise ValueError("Ramsey parameters must be finite")
    if not 0 <= amplitude <= 1 or decay_rate < 0:
        raise ValueError("amplitude must be in [0, 1] and decay nonnegative")
    with np.errstate(over="raise", invalid="raise"):
        try:
            envelope = np.exp(-decay_rate * times)
            angle = angular_frequency * times + phase
        except FloatingPointError as error:
            raise ValueError("Ramsey evolution is not representable in float64") from error
    carrier = np.column_stack((np.cos(angle), np.sin(angle)))
    mean = amplitude * envelope[:, None] * carrier
    d_amplitude = envelope[:, None] * carrier
    d_phase = np.column_stack((-mean[:, 1], mean[:, 0]))
    d_frequency = times[:, None] * d_phase
    d_decay = -times[:, None] * mean
    nuisance = np.column_stack((d_amplitude.ravel(), d_phase.ravel(), d_frequency.ravel(), d_decay.ravel()))
    return mean.ravel(), nuisance, d_decay.ravel().copy()

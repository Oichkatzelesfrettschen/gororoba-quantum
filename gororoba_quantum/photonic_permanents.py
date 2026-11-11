"""Finite-photon references and bounded Gurvits/Aaronson-Hance estimation.

U[output_mode, input_mode] is the scattering convention. Exact methods mean
evaluation of an exact finite identity, not exact complex128 arithmetic.
Confidence disks bound sampling error under independent uniform draws;
floating-point roundoff and the numerical spectral norm are not certified.

The caller owns the Generator and its QRNG provenance. No function seeds an
RNG, contacts a provider, submits a job, or samples a full output distribution.
See docs/notes/topics/gurvits-computational-boundaries.md.
"""

from __future__ import annotations

import math
import operator
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

import parallel

ComplexMatrix = NDArray[np.complex128]
DEFAULT_EXACT_PHOTONS = 20
DEFAULT_MAX_ELEMENTS = 2_000_000


def integer(value: object, name: str, minimum: int = 0) -> int:
    """Reject booleans and non-integral values rather than truncating them."""
    if isinstance(value, bool | np.bool_):
        raise ValueError(f"{name} must be an integer, not a boolean")
    try:
        result = operator.index(value)  # type: ignore[arg-type]
    except TypeError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


def positive(value: float, name: str) -> float:
    """A finite positive scalar."""
    if isinstance(value, bool | np.bool_) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return float(value)


def failure_probability(delta: float) -> float:
    """A nontrivial failure probability."""
    value = positive(delta, "delta")
    if value >= 1:
        raise ValueError("delta must be less than one")
    return value


def matrix(value: ArrayLike, *, square: bool = True) -> ComplexMatrix:
    """Copy a finite matrix; the empty square matrix has shape (0, 0)."""
    result = np.array(value, dtype=np.complex128, copy=True)
    if result.ndim != 2 or (square and result.shape[0] != result.shape[1]):
        raise ValueError("matrix must be two-dimensional" + (" and square" if square else ""))
    if not np.isfinite(result).all():
        raise ValueError("matrix entries must be finite")
    return result


def occupation(values: Sequence[int], modes: int, name: str) -> tuple[int, ...]:
    """Validate an occupation vector without accepting rounded floats."""
    result = tuple(integer(value, name) for value in values)
    if len(result) != modes:
        raise ValueError(f"{name} must have {modes} entries")
    return result


def unitary(value: ArrayLike, atol: float = 1e-10) -> ComplexMatrix:
    """Require numerical unitarity within atol; no implicit postselection."""
    tolerance = positive(atol, "atol")
    result = matrix(value)
    if not np.allclose(result.conj().T @ result, np.eye(len(result)), atol=tolerance, rtol=0):
        raise ValueError("a lossless unitary is required; dilate lossy networks before use")
    return result


def finite_complex(value: complex) -> complex:
    """Reject an overflow rather than returning a nonfinite scientific value."""
    result = complex(value)
    if not (math.isfinite(result.real) and math.isfinite(result.imag)):
        raise ArithmeticError("complex128 overflow; rescale or use higher precision")
    return result


def complex_sum(values: Sequence[complex]) -> complex:
    """Compensated real and imaginary reductions in input order."""
    return finite_complex(complex(math.fsum(z.real for z in values), math.fsum(z.imag for z in values)))


def exp_scale(log_scale: float) -> float:
    """A nonzero finite scale, with no silent underflow to zero."""
    try:
        scale = math.exp(log_scale)
    except OverflowError as exc:
        raise ArithmeticError("scale overflows float64; rescale the matrix") from exc
    if not math.isfinite(scale) or scale == 0:
        raise ArithmeticError("scale is outside float64; rescale the matrix")
    return scale


def permanent_ryser(value: ArrayLike, *, max_photons: int = DEFAULT_EXACT_PHOTONS) -> complex:
    """Gray-code Ryser identity, O(n 2**n) arithmetic and O(n) scratch memory.

    The limit is checked before the exponential loop. Complex cancellation
    can lose precision; use this as a small-instance oracle, not a proof.
    """
    a = matrix(value)
    n = len(a)
    limit = integer(max_photons, "max_photons")
    if n > limit:
        raise ValueError(f"exact permanent has {n} photons, above max_photons={limit}")
    if n == 0:
        return 1 + 0j
    sums = np.zeros(n, dtype=np.complex128)
    total = 0j
    correction = 0j
    previous = 0
    # Gray-code row sums and compensated reduction depend on the previous step.
    with np.errstate(over="raise", invalid="raise"):
        for step in range(1, 1 << n):
            gray = step ^ (step >> 1)
            changed = gray ^ previous
            column = changed.bit_length() - 1
            sums += a[:, column] if gray & changed else -a[:, column]
            term = complex(np.prod(sums))
            if (n + gray.bit_count()) % 2:
                term = -term
            adjusted = term - correction
            following = total + adjusted
            correction = (following - total) - adjusted
            total = following
            previous = gray
    return finite_complex(total)


def fock_amplitude(
    value: ArrayLike,
    inputs: Sequence[int],
    outputs: Sequence[int],
    *,
    max_photons: int = DEFAULT_EXACT_PHOTONS,
    atol: float = 1e-10,
) -> complex:
    """<outputs|U|inputs>, including repeated rows AND columns and vacuum."""
    u = unitary(value, atol)
    t = occupation(inputs, len(u), "inputs")
    s = occupation(outputs, len(u), "outputs")
    limit = integer(max_photons, "max_photons")
    n = sum(t)
    if n != sum(s):
        return 0j
    if n > limit:
        raise ValueError(f"exact Fock amplitude has {n} photons, above max_photons={limit}")
    rows = np.repeat(np.arange(len(u)), s)
    columns = np.repeat(np.arange(len(u)), t)
    denominator = math.sqrt(math.prod(math.factorial(x) for x in (*t, *s)))
    return permanent_ryser(u[np.ix_(rows, columns)], max_photons=limit) / denominator


@dataclass(frozen=True)
class AdditiveEstimate:
    """A complex estimate and sampling-only disk, never a relative guarantee.

    `method` identifies exact structural shortcuts, bounded means, or
    median-of-means. Squaring the estimate is a plug-in statistic, not an
    unbiased probability estimator. No component certifies float roundoff.
    """

    value: complex
    radius: float
    delta: float
    samples: int
    method: str
    scale: float

    def __post_init__(self) -> None:
        finite_complex(self.value)
        failure_probability(self.delta)
        integer(self.samples, "samples")
        for name, value in (("radius", self.radius), ("scale", self.scale)):
            if isinstance(value, bool | np.bool_) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if not isinstance(self.method, str) or not self.method:
            raise ValueError("method must be a nonempty string")

    def probability_interval(self) -> tuple[float, float]:
        """Propagate the disk through |amplitude|**2, without assuming <= 1.

        This also works for unnormalised permanents. A physical amplitude's
        upper endpoint may separately be intersected with [0, 1].
        """
        lower = max(0.0, abs(self.value) - self.radius)
        upper = abs(self.value) + self.radius
        if upper > math.sqrt(np.finfo(float).max):
            raise ArithmeticError("squared interval overflows float64")
        squared_upper = upper * upper
        if upper > 0 and squared_upper == 0:
            raise ArithmeticError("squared interval underflows float64")
        return lower * lower, squared_upper


def hoeffding_radius(bound: float, samples: int, delta: float) -> float:
    """Complex disk: P(|mean-E[X]| > r) <= 4 exp(-N r**2/(4 B**2))."""
    n = integer(samples, "samples", 1)
    d = failure_probability(delta)
    if isinstance(bound, bool | np.bool_) or not math.isfinite(bound) or bound < 0:
        raise ValueError("bound must be finite and nonnegative")
    result = 2 * bound * math.sqrt((math.log(4) - math.log(d)) / n)
    if not math.isfinite(result) or (bound > 0 and result == 0):
        raise ArithmeticError("confidence radius is outside float64")
    return result


def sample_budget(epsilon: float, delta: float, *, max_samples: int = 1_000_000) -> int:
    """Samples for a disk of radius epsilon times the bounded-sample scale."""
    eps = positive(epsilon, "epsilon")
    d = failure_probability(delta)
    limit = integer(max_samples, "max_samples", 1)
    needed = 4 * (math.log(4) - math.log(d)) / eps / eps
    if not math.isfinite(needed) or needed > limit:
        raise ValueError("requested accuracy exceeds max_samples")
    return max(1, math.ceil(needed))


@dataclass(frozen=True)
class RootKernel:
    """Aaronson-Hance root-of-unity sample, evaluated on a normalised matrix."""

    normalised: ComplexMatrix
    counts: tuple[int, ...]

    def __call__(self, indices: NDArray[np.int64]) -> complex:
        counts = np.asarray(self.counts, dtype=np.int64)
        roots = np.exp((2j * math.pi) * indices / (counts + 1))
        # The ordinary +/-1 case keeps exact signs, rather than sin(pi) noise.
        roots = np.where(counts == 1, 1 - 2 * indices, roots)
        transformed = self.normalised @ (np.sqrt(counts) * roots)
        phase = complex(np.prod(np.conj(roots) ** counts))
        with np.errstate(over="raise", invalid="raise"):
            return finite_complex(phase * np.prod(transformed))


def repeated_kernel(
    value: ArrayLike,
    multiplicities: Sequence[int],
    *,
    axis: int = 1,
    log_normalisation: float = 0.0,
) -> tuple[RootKernel, float]:
    """Compact repeated-column/row kernel and its sample-modulus bound.

    axis=1 repeats columns of an n-by-k matrix; axis=0 repeats rows of a
    k-by-n matrix. Zero multiplicities remove unused columns/rows.
    The bound is prod(s! / s**(s/2)) * ||B||_2**n, divided by the supplied
    positive log normalisation. The norm is a numerical SVD, not interval arithmetic.
    """
    if isinstance(axis, bool | np.bool_) or axis not in (0, 1):
        raise ValueError("axis must be 0 or 1")
    b = matrix(value, square=False)
    if axis == 0:
        b = b.T.copy()
    counts = occupation(multiplicities, b.shape[1], "multiplicities")
    if sum(counts) != b.shape[0]:
        raise ValueError("multiplicities must sum to the number of un-repeated rows")
    if not math.isfinite(log_normalisation):
        raise ValueError("log_normalisation must be finite")
    keep = [i for i, count in enumerate(counts) if count]
    b = b[:, keep]
    counts = tuple(counts[i] for i in keep)
    n = b.shape[0]
    if n == 0:
        return RootKernel(b, counts), exp_scale(-log_normalisation)
    norm = float(np.linalg.norm(b, 2))
    if not math.isfinite(norm):
        raise ArithmeticError("spectral norm overflows float64")
    if norm == 0:
        return RootKernel(b, counts), 0.0
    log_bound = (
        n * math.log(norm) + math.fsum(math.lgamma(s + 1) - s * math.log(s) / 2 for s in counts) - log_normalisation
    )
    # Real-component division avoids forming the overflowing reciprocal
    # that complex division may use for a subnormal but nonzero norm.
    normalised = np.empty_like(b)
    normalised.real = b.real / norm
    normalised.imag = b.imag / norm
    return RootKernel(normalised, counts), exp_scale(log_bound)


def evaluate_roots(kernel: RootKernel, indices: ArrayLike) -> list[complex]:
    """Deterministic kernel evaluation; no confidence is assigned to supplied points."""
    points = np.asarray(indices)
    if points.ndim != 2 or points.shape[1] != len(kernel.counts) or points.dtype.kind not in "iu":
        raise ValueError("root indices must be a two-dimensional integer array of the right width")
    if np.any(points < 0) or np.any(points > np.asarray(kernel.counts)):
        raise ValueError("root index is outside its root-of-unity set")
    return parallel.ordered_map(kernel, list(points))


def _sample_kernel(
    kernel: RootKernel,
    scale: float,
    rng: np.random.Generator,
    samples: int,
    delta: float,
    max_elements: int,
) -> AdditiveEstimate:
    count = integer(samples, "samples", 1)
    d = failure_probability(delta)
    limit = integer(max_elements, "max_elements", 1)
    if kernel.normalised.size + count * max(1, len(kernel.counts)) > limit:
        raise ValueError("matrix and random draws exceed max_elements")
    if not kernel.counts or scale == 0:
        return AdditiveEstimate(complex(scale), 0.0, d, 0, "structural", scale)
    # Draw all shared-generator inputs before mapping; workers never own RNG state.
    indices = rng.integers(0, np.asarray(kernel.counts) + 1, size=(count, len(kernel.counts)))
    values = evaluate_roots(kernel, indices)
    mean = complex_sum(values) / count
    return AdditiveEstimate(
        finite_complex(mean * scale), hoeffding_radius(scale, count, d), d, count, "bounded-mean", scale
    )


def estimate_repeated_permanent(
    value: ArrayLike,
    multiplicities: Sequence[int],
    *,
    rng: np.random.Generator,
    samples: int,
    delta: float = 0.01,
    axis: int = 1,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
) -> AdditiveEstimate:
    """Additive Aaronson-Hance estimate; the caller supplies a provenance-bound RNG."""
    kernel, scale = repeated_kernel(value, multiplicities, axis=axis)
    return _sample_kernel(kernel, scale, rng, samples, delta, max_elements)


def estimate_permanent(
    value: ArrayLike,
    *,
    rng: np.random.Generator,
    samples: int,
    delta: float = 0.01,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
) -> AdditiveEstimate:
    """Gurvits's sign estimator with a complex Hoeffding disk."""
    a = matrix(value)
    return estimate_repeated_permanent(
        a, (1,) * len(a), rng=rng, samples=samples, delta=delta, max_elements=max_elements
    )


def estimate_fock_amplitude(
    value: ArrayLike,
    inputs: Sequence[int],
    outputs: Sequence[int],
    *,
    rng: np.random.Generator,
    samples: int,
    delta: float = 0.01,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
    atol: float = 1e-10,
) -> AdditiveEstimate:
    """Use the smaller deterministic row/column-repeat bound, then draw once.

    Repetition on both sides is allowed, but the resulting bound can be large.
    No polynomial-in-photon-number relative-error guarantee follows.
    """
    u = unitary(value, atol)
    t = occupation(inputs, len(u), "inputs")
    s = occupation(outputs, len(u), "outputs")
    count = integer(samples, "samples", 1)
    d = failure_probability(delta)
    limit = integer(max_elements, "max_elements", 1)
    if sum(t) != sum(s):
        return AdditiveEstimate(0j, 0.0, d, 0, "photon-number-selection", 0.0)
    n = sum(t)
    if n * max(1, len(u)) + count * max(1, len(u)) > limit:
        raise ValueError("expanded compact matrix and draws exceed max_elements")
    rows = np.repeat(np.arange(len(u)), s)
    columns = np.repeat(np.arange(len(u)), t)
    log_denominator = math.fsum(math.lgamma(x + 1) for x in (*t, *s)) / 2
    by_column = repeated_kernel(u[rows, :], t, log_normalisation=log_denominator)
    by_row = repeated_kernel(u[:, columns], s, axis=0, log_normalisation=log_denominator)
    kernel, scale = min((by_column, by_row), key=lambda item: item[1])
    return _sample_kernel(kernel, scale, rng, count, d, limit)

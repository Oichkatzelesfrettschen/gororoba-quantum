"""Hafnian references and product-Fock Husimi amplitude estimation.

The coherent-state estimator is the Fock specialization of Lim and Oh,
arXiv:2502.12882, Theorem 2 and supplement S4. Its second moment is at most
one for normalised input/output states and an exactly unitary transfer.
Median-of-means handles unbounded samples; a bounded-sample Hoeffding
interval does not. Exact pairings and pure Gaussian probabilities serve as
independent normalisation checks, not a Gaussian boson sampler.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache

import numpy as np
from numpy.typing import ArrayLike

import parallel
from photonic_permanents import (
    DEFAULT_EXACT_PHOTONS,
    DEFAULT_MAX_ELEMENTS,
    AdditiveEstimate,
    ComplexMatrix,
    complex_sum,
    exp_scale,
    failure_probability,
    finite_complex,
    integer,
    matrix,
    occupation,
    positive,
    unitary,
)


def hafnian(
    value: ArrayLike,
    *,
    loops: Sequence[complex] | None = None,
    max_photons: int = DEFAULT_EXACT_PHOTONS,
    atol: float = 1e-10,
) -> complex:
    """Pairing recurrence; optional singleton weights give the loop hafnian.

    The matrix diagonal is ignored. Supply singleton weights through `loops`;
    a Hermitian matrix is not necessarily symmetric. The empty hafnian is 1.
    Ordinary odd-dimensional hafnians are zero. Complexity is exponential.
    """
    a = matrix(value)
    n = len(a)
    limit = integer(max_photons, "max_photons")
    tolerance = positive(atol, "atol")
    if n > limit:
        raise ValueError("hafnian exceeds max_photons")
    if not np.allclose(a, a.T, atol=tolerance, rtol=0):
        raise ValueError("hafnian requires a complex symmetric matrix, not a Hermitian one")
    diagonal = None if loops is None else np.asarray(loops, dtype=np.complex128)
    if diagonal is not None and (diagonal.shape != (n,) or not np.isfinite(diagonal).all()):
        raise ValueError("loops must contain one finite singleton weight per vertex")
    if diagonal is None and n % 2:
        return 0j

    @cache
    def pairing(mask: int) -> complex:
        if mask == 0:
            return 1 + 0j
        first = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << first)
        terms = [] if diagonal is None else [complex(diagonal[first]) * pairing(rest)]
        bits = rest
        # Recursive subproblems share the memo table rather than independent pools.
        while bits:
            bit = bits & -bits
            j = bit.bit_length() - 1
            terms.append(complex(a[first, j]) * pairing(rest ^ bit))
            bits ^= bit
        return complex_sum(terms)

    return finite_complex(pairing((1 << n) - 1))


def pure_gaussian_probability(
    value: ArrayLike,
    outputs: Sequence[int],
    *,
    max_photons: int = DEFAULT_EXACT_PHOTONS,
    atol: float = 1e-10,
) -> float:
    """PNR probability of C exp(a^dagger B a^dagger / 2)|vacuum>.

    B must be complex symmetric with ||B||_2 < 1. C**2 =
    sqrt(det(I-B B^dagger)). No displacement, loss, mixed state, threshold
    detector, or adaptive feed-forward is included.
    """
    b = matrix(value)
    tolerance = positive(atol, "atol")
    if not np.allclose(b, b.T, atol=tolerance, rtol=0):
        raise ValueError("Gaussian B must be complex symmetric")
    s = occupation(outputs, len(b), "outputs")
    limit = integer(max_photons, "max_photons")
    n = sum(s)
    if n > limit:
        raise ValueError("Gaussian reference exceeds max_photons")
    singular = np.linalg.svd(b, compute_uv=False)
    if np.any(singular >= 1):
        raise ValueError("Gaussian B must be a strict contraction")
    log_vacuum = float(np.sum(np.log1p(-(singular * singular))) / 2)
    if n % 2:
        return 0.0
    repeated = np.repeat(np.arange(len(b)), s)
    h = hafnian(b[np.ix_(repeated, repeated)], max_photons=limit, atol=tolerance)
    if h == 0:
        return 0.0
    log_probability = log_vacuum + 2 * math.log(abs(h)) - math.fsum(math.lgamma(v + 1) for v in s)
    result = exp_scale(log_probability)
    if result > 1 + tolerance:
        raise ArithmeticError("Gaussian probability exceeds one; use higher precision")
    return result


@dataclass(frozen=True)
class FockHusimiKernel:
    """<s|U alpha>/<t|alpha>; Q_t samples have E|X|**2 <= 1."""

    transfer: ComplexMatrix
    inputs: tuple[int, ...]
    outputs: tuple[int, ...]

    def __call__(self, alpha: np.ndarray) -> complex:
        alpha = np.asarray(alpha, dtype=np.complex128)
        if alpha.shape != (len(self.transfer),) or not np.isfinite(alpha).all():
            raise ValueError("coherent point must be a finite vector of the right size")
        beta = self.transfer @ alpha
        log_size = math.fsum(math.lgamma(v + 1) for v in self.inputs) / 2
        log_size -= math.fsum(math.lgamma(v + 1) for v in self.outputs) / 2
        phase = 1 + 0j
        for z, count in zip(alpha, self.inputs, strict=True):
            if count:
                magnitude = abs(z)
                if magnitude == 0:
                    raise ValueError("coherent point lies at a zero of the sampling density")
                log_size -= count * math.log(magnitude)
                phase /= (z / magnitude) ** count
        for z, count in zip(beta, self.outputs, strict=True):
            if count:
                magnitude = abs(z)
                if magnitude == 0:
                    return 0j
                log_size += count * math.log(magnitude)
                phase *= (z / magnitude) ** count
        return finite_complex(exp_scale(log_size) * phase)


def block_mean(samples: Sequence[complex]) -> complex:
    """One independent, order-preserving compensated block mean."""
    if len(samples) == 0:
        raise ValueError("median-of-means blocks must be nonempty")
    return complex_sum(samples) / len(samples)


def median_of_means_plan(
    epsilon: float, delta: float, *, max_samples: int = 1_000_000
) -> tuple[int, int]:
    """Block size >= 8/epsilon**2, odd block count >= 8 log(2/delta).

    Chebyshev bounds either coordinate's bad-block probability by 1/4
    at coordinate error epsilon/sqrt(2). Hoeffding on independent blocks
    and a two-coordinate union bound give a complex disk of radius epsilon.
    """
    eps = positive(epsilon, "epsilon")
    d = failure_probability(delta)
    limit = integer(max_samples, "max_samples", 1)
    raw_size = 8 / eps / eps
    if not math.isfinite(raw_size) or raw_size > limit:
        raise ValueError("requested epsilon exceeds max_samples")
    block_size = max(1, math.ceil(raw_size))
    groups = max(1, math.ceil(8 * (math.log(2) - math.log(d))))
    groups += int(groups % 2 == 0)
    if block_size * groups > limit:
        raise ValueError("median-of-means plan exceeds max_samples")
    return block_size, groups


def estimate_fock_husimi(
    value: ArrayLike,
    inputs: Sequence[int],
    outputs: Sequence[int],
    *,
    rng: np.random.Generator,
    epsilon: float,
    delta: float = 0.01,
    max_samples: int = 1_000_000,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
    atol: float = 1e-10,
) -> AdditiveEstimate:
    """Additive physical amplitude estimate for arbitrary product-Fock occupations.

    |alpha_i|**2 ~ Gamma(t_i+1, 1), arg(alpha_i) ~ Uniform[0, 2pi).
    The probability guarantee presumes independent draws and exact arithmetic.
    A numerical unitary tolerance is not a bound on systematic error.
    """
    u = unitary(value, atol)
    t = occupation(inputs, len(u), "inputs")
    s = occupation(outputs, len(u), "outputs")
    block_size, groups = median_of_means_plan(epsilon, delta, max_samples=max_samples)
    limit = integer(max_elements, "max_elements", 1)
    if sum(t) != sum(s):
        return AdditiveEstimate(0j, 0.0, delta, 0, "photon-number-selection", 0.0)
    if sum(t) == 0:
        return AdditiveEstimate(1 + 0j, 0.0, delta, 0, "vacuum", 1.0)
    count = block_size * groups
    if 2 * count * max(1, len(u)) + u.size > limit:
        raise ValueError("Husimi draws exceed max_elements")
    # Parent draws every radius and phase before independent kernel evaluation.
    radii_squared = rng.gamma(np.asarray(t, dtype=float) + 1, 1, size=(count, len(u)))
    angles = rng.uniform(0, 2 * math.pi, size=(count, len(u)))
    alpha = np.sqrt(radii_squared) * np.exp(1j * angles)
    samples = parallel.ordered_map(FockHusimiKernel(u, t, s), list(alpha))
    blocks = [samples[start : start + block_size] for start in range(0, count, block_size)]
    means = np.asarray(parallel.ordered_map(block_mean, blocks))
    result = complex(float(np.median(means.real)), float(np.median(means.imag)))
    return AdditiveEstimate(result, float(epsilon), float(delta), count, "husimi-median-of-means", 1.0)

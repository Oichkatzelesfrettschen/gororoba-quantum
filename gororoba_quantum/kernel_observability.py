"""Repeated-herald statistics and a constructive Hermitian measurement completion.

The Cayley-Dickson basis convention comes from ``cd_core``. Algebraic
certificates describe the ideal linear encoding, not a native instruction or
a change to associative quantum mechanics. Count summaries assume declared,
observed attempts and nested outcomes from those same attempts. They neither
recover missing trials nor assign a physical cause to a residual.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

import numpy as np

from cd_core import left_mult_matrix_exact
from measurement_statistics import multinomial_scores
from provider_counters import Counter, Population, Status

# tomography_completion stores 32 * m**4 int64 coefficients; the default admits m up to 13 (0.9 million entries,
# 7 MB) and a caller that has checked its memory passes a larger entry_budget.
DEFAULT_COEFFICIENT_ENTRY_BUDGET = 1_000_000


@dataclass(frozen=True)
class EqualWeightPairCertificate:
    """Exact multiplicities of ``L.T L`` for ``L = L_ei + sign L_ej``.

    Eigenvalues 0, 2 and 4 have multiplicities ``nullity``,
    ``dimension - 2*nullity`` and ``nullity``. The heralded Kraus operator
    is ``L/2``. The certificate also checks normality, which is necessary
    before replacing repeated Kraus words by powers of ``L.T L``.
    """

    dimension: int
    i: int
    j: int
    sign: int
    nullity: int


def _integer(value: int, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return value


def certify_equal_weight_pair(dim: int, i: int, j: int, sign: int = 1) -> EqualWeightPairCertificate:
    """Check a CD basis pair by bounded-coefficient exact matrix identities.

    This does not assume that the left-multiplication map is an algebra
    homomorphism. All products here are ordinary compositions of its
    matrices. No floating-point rank threshold enters the certificate.
    """
    _integer(dim, "dimension", minimum=4)
    if dim & (dim - 1):
        raise ValueError("dimension must be a power of two")
    _integer(i, "i", minimum=1)
    _integer(j, "j", minimum=1)
    if i >= dim or j >= dim or i == j:
        raise ValueError("i and j must be distinct nonidentity basis indices")
    if isinstance(sign, bool) or not isinstance(sign, int) or sign not in {-1, 1}:
        raise ValueError("sign must be -1 or 1")
    vector = [0] * dim
    vector[i], vector[j] = 1, sign
    # cd_core returns Fraction coefficients; these basis-pair coefficients
    # are integers in {-1, 0, 1}, representable exactly in int64.
    left = np.asarray(left_mult_matrix_exact(dim, vector), dtype=np.int64)
    identity = np.eye(dim, dtype=np.int64)
    gram = left.T @ left
    square = gram @ gram
    if not np.array_equal(left @ left.T, gram):
        raise ValueError("the pair's left-multiplication matrix is not normal")
    if np.any(gram @ (gram - 2 * identity) @ (gram - 4 * identity)):
        raise ValueError("the Gram spectrum is not confined to 0, 2, 4")
    if int(np.trace(gram)) != 2 * dim:
        raise ValueError("the first Gram trace does not equal twice the dimension")
    nullity, remainder = divmod(int(np.trace(square)) - 4 * dim, 8)
    if remainder or not 0 <= 2 * nullity <= dim:
        raise ValueError("the spectral multiplicities are inconsistent")
    return EqualWeightPairCertificate(dim, i, j, sign, nullity)


def _exact_probability(value: Fraction, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise ValueError(f"{name} must be an exact rational probability")
    result = Fraction(value)
    if not 0 <= result <= 1:
        raise ValueError(f"{name} must lie in [0, 1]")
    return result


# The denominator of a depth-m survival probability is 2**m times the dimension, so the depth is the bit length
# of an exact result; no acquisition in this tree repeats a herald more than a few dozen times.
MAX_HERALD_DEPTH = 4096


def exact_herald_moments(
    certificate: EqualWeightPairCertificate,
    depths: Sequence[int],
    *,
    retention: Fraction = Fraction(1),
) -> tuple[Fraction, ...]:
    """Joint survival probabilities on the maximally mixed input.

    For positive depth m the ideal probability is
    ``z/D + (1 - 2*z/D)/2**m``; at depth zero it is one. A known,
    state-independent per-stage retention multiplies this by ``eta**m``.
    State-dependent loss and a nonmaximally mixed input do not obey this
    formula in general. This function is a model prediction, not a fit.
    """
    if not isinstance(certificate, EqualWeightPairCertificate):
        raise ValueError("an equal-weight pair certificate is required")
    dim, nullity = certificate.dimension, certificate.nullity
    _integer(nullity, "certificate nullity")
    if certificate != certify_equal_weight_pair(dim, certificate.i, certificate.j, certificate.sign):
        raise ValueError("the certificate does not match the cd_core pair")
    eta = _exact_probability(retention, "retention")
    checked = [_integer(depth, "depth") for depth in depths]
    if any(depth > MAX_HERALD_DEPTH for depth in checked):
        raise ValueError(f"depth exceeds the exact-denominator budget of {MAX_HERALD_DEPTH} bits")
    # Each value is one bounded exact coefficient, not a circuit simulation.
    return tuple(
        Fraction(1)
        if depth == 0
        else eta**depth * (Fraction(nullity, dim) + Fraction(dim - 2 * nullity, dim * 2**depth))
        for depth in checked
    )


def uniform_retention_nullity(first: Fraction, second: Fraction, dimension: int) -> Fraction:
    """Return D/2 * (q2/q1**2 - 1), conditional on the stated ideal model.

    The cancellation of an unknown uniform retention holds only for the
    maximally mixed, normal equal-weight pair model. A nonintegral or
    out-of-range value is retained as a model diagnostic, not rounded into
    an algebraic rank. This arithmetic supplies no sampling uncertainty.
    """
    _integer(dimension, "dimension", minimum=4)
    if dimension & (dimension - 1):
        raise ValueError("dimension must be a power of two")
    q1 = _exact_probability(first, "first moment")
    q2 = _exact_probability(second, "second moment")
    if not q1 or q2 > q1:
        raise ValueError("first moment must be positive and second must not exceed first")
    return Fraction(dimension, 2) * (q2 / q1**2 - 1)


@dataclass(frozen=True)
class NestedHeraldEstimate:
    """Cumulative same-attempt probabilities, covariance and recurrence residuals.

    ``recurrence_covariance`` propagates the full shared-attempt covariance.
    Retention is treated as fixed. A retention fitted from the same counts
    needs additional parameter and cross-covariance propagation. A zero
    empirical variance does not establish a zero population variance.
    """

    attempts: int
    attempt_counter: Counter
    successes: tuple[int, ...]
    probabilities: np.ndarray
    covariance_of_means: np.ndarray
    retention: float
    recurrence_residuals: np.ndarray
    recurrence_covariance: np.ndarray
    estimator: str


def nested_herald_statistics(
    attempt_counter: Counter,
    successes: Sequence[int],
    *,
    sampling: Literal["fixed_independent_attempts"],
    estimator: Literal["plugin", "unbiased"] = "plugin",
    retention: float = 1.0,
) -> NestedHeraldEstimate:
    """Analyze nested cumulative successes N1 >= ... >= Nm from N attempts.

    Requested shots, accepted-count caps and independently run depth banks
    do not supply this sampling contract. For independent attempts and
    nested indicators H_m, ``Cov(mean(H_i),mean(H_j))`` has plug-in value
    ``(p[max(i,j)] - p[i]*p[j])/N``. The exclusive failure-depth histogram
    passes through the shared multinomial-score implementation.

    For retained moments q_m=eta**m*p_m at m >= 1, the fixed-eta model contrast is
    ``eta**2*q_m - 3*eta*q_(m+1) + 2*q_(m+2)``. The return value contains
    descriptive residuals and covariance, not a chi-square significance.
    """
    if not isinstance(attempt_counter, Counter):
        raise ValueError("an observed attempt Counter is required")
    if (
        attempt_counter.status is not Status.OBSERVED
        or attempt_counter.population not in {Population.SOURCE_TRIGGER, Population.CIRCUIT_EXECUTION}
        or attempt_counter.terminated_by is not None
        or not isinstance(attempt_counter.scope, str)
        or not isinstance(attempt_counter.source, str)
        or not attempt_counter.scope.strip()
        or not attempt_counter.source.strip()
    ):
        raise ValueError(
            "uncensored observed source-trigger or circuit-execution attempts with provenance are required"
        )
    if not isinstance(attempt_counter.value, int):
        raise ValueError("attempt counter must contain an integer")
    attempts = _integer(attempt_counter.value, "attempts", minimum=1)
    if sampling != "fixed_independent_attempts":
        raise ValueError("fixed independent attempts and nested successes from those same attempts are required")
    counts = tuple(_integer(value, "success count") for value in successes)
    if not counts:
        raise ValueError("at least one depth is required")
    previous = (attempts, *counts[:-1])
    if any(current > prior for current, prior in zip(counts, previous, strict=True)):
        raise ValueError("success counts must be nested and no greater than attempts")
    if isinstance(retention, bool) or not isinstance(retention, (int, float)):
        raise ValueError("retention must be a finite number in [0, 1]")
    eta = float(retention)
    if not math.isfinite(eta) or not 0 <= eta <= 1:
        raise ValueError("retention must be a finite number in [0, 1]")
    exclusive = [prior - current for prior, current in zip(previous, counts, strict=True)] + [counts[-1]]
    depth = len(counts)
    scores = (np.arange(depth)[:, None] < np.arange(depth + 1)[None, :]).astype(float)
    estimate = multinomial_scores(exclusive, scores, estimator=estimator)
    contrasts = np.zeros((max(depth - 2, 0), depth))
    rows = np.arange(max(depth - 2, 0))
    contrasts[rows, rows] = eta * eta
    contrasts[rows, rows + 1] = -3 * eta
    contrasts[rows, rows + 2] = 2
    return NestedHeraldEstimate(
        attempts,
        attempt_counter,
        counts,
        estimate.means,
        estimate.covariance_of_means,
        eta,
        contrasts @ estimate.means,
        contrasts @ estimate.covariance_of_means @ contrasts.T,
        estimator,
    )


@dataclass(frozen=True)
class TomographyCompletion:
    """An exact, Hilbert-Schmidt orthogonal Hermitian basis on dimension 2m.

    ``real + 1j*imaginary`` gives each observable. The first m**2 rows
    commute with J=[[0,I],[-I,0]], the next m*(m+1) real rows anticommute,
    and the remaining m*(2*m-1) rows are imaginary skew matrices.
    The observables have operator norm one, but unequal Hilbert-Schmidt
    norms. Their binary effects are ``(I+T)/2`` and ``(I-T)/2``.
    """

    half_dimension: int
    names: tuple[str, ...]
    families: tuple[str, ...]
    real: np.ndarray
    imaginary: np.ndarray
    hs_norm_squared: np.ndarray


def _units(dim: int, *, skew: bool) -> tuple[list[tuple[int, int]], np.ndarray]:
    first, second = np.triu_indices(dim, k=1 if skew else 0)
    values = np.zeros((len(first), dim, dim), dtype=np.int64)
    rows = np.arange(len(first))
    values[rows, first, second] = 1
    values[rows, second, first] = -1 if skew else 1
    return list(zip(first.tolist(), second.tolist(), strict=True)), values


def _blocks(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> np.ndarray:
    return np.concatenate((np.concatenate((a, b), axis=2), np.concatenate((c, d), axis=2)), axis=1)


def completion_entries(half_dimension: int) -> int:
    """Integer coefficient entries of the completion on dimension 2m: 4m**2 observables of (2m)**2 entries, twice."""
    return 32 * half_dimension**4


def tomography_completion(
    half_dimension: int = 7, *, entry_budget: int = DEFAULT_COEFFICIENT_ENTRY_BUDGET
) -> TomographyCompletion:
    """Construct the completion without floating ranks or a census replay.

    At m=7 the direct-sum dimensions are 49+56+91=196 on the support
    ordered as e1..e7,e9..e15. This constructs the complement of the full
    real J commutant; it does not re-prove that a particular acquired bank
    spans that commutant or that the instrument implements these effects.
    The arrays hold ``completion_entries(m)`` = 32*m**4 int64 coefficients
    (m=100 needs about 25.6 GB), so a request above ``entry_budget`` raises
    before any allocation.
    """
    m = _integer(half_dimension, "half_dimension", minimum=1)
    budget = _integer(entry_budget, "entry_budget", minimum=1)
    if completion_entries(m) > budget:
        raise ValueError(
            f"the completion needs {completion_entries(m)} coefficient entries, above entry_budget={budget}"
        )
    symmetric_indices, symmetric = _units(m, skew=False)
    skew_indices, skew = _units(m, skew=True)
    full_indices, full_skew = _units(2 * m, skew=True)
    zero_s, zero_k = np.zeros_like(symmetric), np.zeros_like(skew)
    commutant = np.concatenate((_blocks(symmetric, zero_s, zero_s, symmetric), _blocks(zero_k, skew, -skew, zero_k)))
    anticommutant = np.concatenate(
        (_blocks(symmetric, zero_s, zero_s, -symmetric), _blocks(zero_s, symmetric, symmetric, zero_s))
    )
    real = np.concatenate((commutant, anticommutant, np.zeros_like(full_skew)))
    imaginary = np.concatenate((np.zeros_like(commutant), np.zeros_like(anticommutant), full_skew))
    names = tuple(
        [f"C_A_{i}_{j}" for i, j in symmetric_indices]
        + [f"C_B_{i}_{j}" for i, j in skew_indices]
        + [f"A_A_{i}_{j}" for i, j in symmetric_indices]
        + [f"A_B_{i}_{j}" for i, j in symmetric_indices]
        + [f"I_{i}_{j}" for i, j in full_indices]
    )
    families = tuple(
        ["real_J_commutant"] * len(commutant)
        + ["real_J_anticommutant"] * len(anticommutant)
        + ["imaginary_skew"] * len(full_skew)
    )
    norms = np.sum(real * real + imaginary * imaginary, axis=(1, 2))
    real.setflags(write=False)
    imaginary.setflags(write=False)
    norms.setflags(write=False)
    return TomographyCompletion(m, names, families, real, imaginary, norms)


def reconstruct_hermitian(expectations: Sequence[float], half_dimension: int = 7) -> np.ndarray:
    """Linear inversion in the completion basis, with its actual HS norms.

    This returns a Hermitian estimate; finite-shot expectations need not
    produce a positive or trace-one state. No positivity projection or
    renormalization silently changes the measured coefficients.
    """
    completion = tomography_completion(half_dimension)
    values = np.asarray(expectations)
    if values.dtype.kind not in {"i", "u", "f"} or values.shape != completion.hs_norm_squared.shape:
        raise ValueError("expectations must be one real coefficient per completion observable")
    try:
        with np.errstate(over="ignore", invalid="ignore"):
            values = values.astype(float)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError("expectations must contain finite real numbers") from error
    if not np.all(np.isfinite(values)):
        raise ValueError("expectations must contain finite real numbers")
    coefficients = values / completion.hs_norm_squared
    with np.errstate(over="ignore", invalid="ignore"):
        result = np.einsum("k,kij->ij", coefficients, completion.real + 1j * completion.imaginary)
    if not np.all(np.isfinite(result)):
        raise ValueError("reconstruction is not representable as a finite matrix")
    return result

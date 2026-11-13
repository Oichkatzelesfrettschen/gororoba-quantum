"""Exact-rational contrast statistics of the coin series' 32-outcome count vectors.

A count job of the coin series holds 32 integer counts over the outcome index y + 8 s + 16 c (bin y, selector s,
coin c). Its readout correction applies the inverse of the joint assignment matrix, the Kronecker product of one
2x2 matrix [[1 - e01, e10], [e01, 1 - e10]] per logical bit (row = measured, column = true, bit v of the index on
the v-th factor), and each rate e01 and e10 is a ratio of integer shot counts. The correction, the pile contrasts
c(y), the ratios c / V, V and N_hat, and their delta-method errors are therefore rational functions of integers,
and this module evaluates them in `Fraction` arithmetic with one rounding per reported float: the value is
`float(Fraction)`, which CPython rounds to nearest (an integer true division), and the standard error is the
correctly rounded square root of the exact variance (`correctly_rounded_root`). No BLAS, LAPACK, einsum or libm
call enters the result, so the floats are the same on every CPU, numpy build and worker count that reads the same
integers (docs/design/native-numeric-replay.md, contract item 7).

The error follows pathion_coset_analysis.contrast_statistics' definition for a coin job. The 32 counts are one
multinomial with covariance N (diag p - p p^T), and the Jacobian J of the 18 outputs is the central difference of
one count (the output at counts + e_i minus the output at counts - e_i, over 2), evaluated exactly. The variance
of output k is then the sum over i of n_i J_ki^2, minus (the sum over i of n_i J_ki)^2 over N, which equals
J cov J^T without forming the 32 x 32 covariance. The corrected counts follow from linearity: the readout inverse
G of a count vector n +- e_i is G n +- G e_i, so the 32 unit-vector solves give every perturbed vector.

Branches match qi_pathion_coset_coin_cases.coin_outputs: a pile whose total is zero leaves every output
undefined, a bin whose normalized weight does not exceed `zero` contributes 0 to its pile's conditional
probability (pathion_coset_block.output_contrast), and a zero V leaves c / V and N_hat undefined. An undefined
output, and the error of an output that has an undefined perturbed value, is None.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

OUTCOMES = 32
HALF = 16
BINS = 8
OUTPUTS = 2 * BINS + 2

# Per logical bit (e01, e10) of the joint assignment, in the order of the index bits (bit 0 first).
Readout = tuple[tuple[Fraction, Fraction], ...]


@dataclass(frozen=True)
class ContrastJob:
    """One coin job: integer `counts` over the 32 outcomes, the ideal sign (-1, 0 or 1) of each of the 8 bins,
    the `readout` assignment the counts are corrected with (None leaves them raw), and the `zero` weight
    threshold of pathion_coset_block.output_contrast."""

    counts: tuple[int, ...]
    sign: tuple[int, ...]
    readout: Readout | None
    zero: Fraction


@dataclass(frozen=True)
class ContrastResult:
    """The 18 outputs c (8), c / V (8), V and N_hat with their errors, rounded once; None marks an undefined one."""

    values: tuple[float | None, ...]
    errors: tuple[float | None, ...]


def integer_root(value: int, degree: int) -> int:
    """floor(value ** (1 / degree)) for an integer value >= 0, by bisection over integers."""
    if value < 0 or degree < 1:
        raise ValueError("integer_root needs a nonnegative value and a positive degree")
    low, high = 0, 1 << (-(-value.bit_length() // degree) + 1)
    while low < high:
        middle = (low + high + 1) // 2
        if middle**degree <= value:
            low = middle
        else:
            high = middle - 1
    return low


def correctly_rounded_root(value: Fraction, degree: int) -> float:
    """The float nearest to value ** (1 / degree) for a rational value >= 0.

    The integer root of value * 2^(degree k) carries at least 64 significant bits; an inexact root takes the odd
    neighbor of its floor (round to odd), so the final division by 2^k, which CPython rounds to nearest, rounds
    the true root once and correctly."""
    if value < 0:
        raise ValueError("a root of a negative value is undefined")
    if value == 0:
        return 0.0
    shift = 66 - (value.numerator.bit_length() - value.denominator.bit_length()) // degree
    scaled = value * Fraction(2) ** (degree * shift)
    floor = scaled.numerator // scaled.denominator
    root = integer_root(floor, degree)
    if scaled.denominator != 1 or root**degree != floor:
        root |= 1
    return float(Fraction(root) / Fraction(2) ** shift)


def scaled_inverse_readout(readout: Readout, vector: list[int]) -> list[int]:
    """The joint assignment matrix' inverse applied to an integer `vector`, scaled by the product of the factors'
    determinants so that every entry stays an integer.

    One bit's factor [[1 - e01, e10], [e01, 1 - e10]] has the inverse [[1 - e10, -e10], [-e01, 1 - e01]] / (1 -
    e01 - e10). With L the least common denominator of e01 and e10 the integer matrix [[L - E10, -E10], [-E01,
    L - E01]] (E = e L) equals the inverse times L (1 - e01 - e10), and the product of those scales divides out of
    every output of contrast_outputs, which is homogeneous of degree 0 in its piles."""
    scaled = list(vector)
    for bit, (e01, e10) in enumerate(readout):
        denominator = math.lcm(e01.denominator, e10.denominator)
        rate01, rate10 = int(e01 * denominator), int(e10 * denominator)
        if denominator - rate01 - rate10 == 0:
            raise ValueError(f"the assignment of bit {bit} is singular")
        stride = 1 << bit
        for index in range(len(scaled)):
            if index & stride:
                continue
            low, high = scaled[index], scaled[index + stride]
            scaled[index] = (denominator - rate10) * low - rate10 * high
            scaled[index + stride] = (denominator - rate01) * high - rate01 * low
    return scaled


def contrast_outputs(piles: list[int], sign: tuple[int, ...], zero: Fraction) -> list[Fraction | None]:
    """c(y), c / V, V and N_hat of 32 counts, the plus pile (coin = 1) the upper 16.

    The outputs depend on the counts only through ratios, so `piles` may carry any common nonzero scale."""
    minus, plus = piles[:HALF], piles[HALF:]
    plus_total, minus_total = sum(plus), sum(minus)
    if plus_total == 0 or minus_total == 0:
        return [None] * OUTPUTS
    contrast: list[Fraction] = []
    for y in range(BINS):
        value = Fraction(0)
        for pile, total, orientation in ((plus, plus_total, 1), (minus, minus_total, -1)):
            weight = pile[y] + pile[y + BINS]
            if Fraction(weight, total) > zero:
                value += orientation * Fraction(pile[y], weight)
        contrast.append(value)
    visibility = sum((c * s for c, s in zip(contrast, sign, strict=True)), Fraction(0)) / BINS
    outputs: list[Fraction | None] = [*contrast]
    if visibility == 0:
        return [*outputs, *([None] * BINS), visibility, None]
    outputs += [c / visibility for c in contrast]
    return [*outputs, visibility, sum(contrast, Fraction(0)) / 2 / visibility]


def check_job(job: ContrastJob) -> int:
    """The shot count of `job`, after refusing a malformed one."""
    if len(job.counts) != OUTCOMES or len(job.sign) != BINS:
        raise ValueError("a coin job holds 32 counts and 8 bin signs")
    if job.zero <= 0:
        raise ValueError("the zero-weight threshold must be positive")
    total = sum(job.counts)
    if total <= 0:
        raise ValueError("a coin job needs a positive shot count")
    return total


def corrected(job: ContrastJob, vector: list[int]) -> list[int]:
    """`vector` through the job's readout correction (a common scale of the result is irrelevant)."""
    return list(vector) if job.readout is None else scaled_inverse_readout(job.readout, vector)


def exact_values(job: ContrastJob) -> list[Fraction | None]:
    """The 18 outputs of `job` as exact rationals."""
    check_job(job)
    return contrast_outputs(corrected(job, list(job.counts)), job.sign, job.zero)


def exact_variances(job: ContrastJob) -> list[Fraction | None]:
    """The exact delta-method variance of each output; None where a perturbed value is undefined."""
    total = check_job(job)
    base = corrected(job, list(job.counts))
    jacobian: list[list[Fraction | None]] = [[] for _ in range(OUTPUTS)]
    for index in range(OUTCOMES):
        step = corrected(job, [int(i == index) for i in range(OUTCOMES)])
        up = contrast_outputs([b + s for b, s in zip(base, step, strict=True)], job.sign, job.zero)
        down = contrast_outputs([b - s for b, s in zip(base, step, strict=True)], job.sign, job.zero)
        for k in range(OUTPUTS):
            high, low = up[k], down[k]
            jacobian[k].append(None if high is None or low is None else (high - low) / 2)
    return [delta_variance(column, job.counts, total) for column in jacobian]


def delta_variance(column: list[Fraction | None], counts: tuple[int, ...], total: int) -> Fraction | None:
    """sum_i n_i J_i^2 - (sum_i n_i J_i)^2 / N for one Jacobian row, over one common denominator.

    Bringing the entries to the least common denominator turns the sums into integer products; a Fraction sum
    would reduce by a gcd of thousand-bit numbers after every addition."""
    entries = [entry for entry in column if entry is not None]
    if len(entries) != len(column):
        return None
    denominator = 1
    for entry in entries:
        denominator = denominator * entry.denominator // math.gcd(denominator, entry.denominator)
    numerators = [entry.numerator * (denominator // entry.denominator) for entry in entries]
    linear = sum(n * j for n, j in zip(counts, numerators, strict=True))
    square = sum(n * j * j for n, j in zip(counts, numerators, strict=True))
    variance = Fraction(total * square - linear * linear, total * denominator * denominator)
    if variance < 0:
        raise ValueError("a delta-method variance is negative in exact arithmetic")
    return variance


def contrast_statistics(job: ContrastJob) -> ContrastResult:
    """The 18 outputs and errors of `job`, each rounded once from its exact value."""
    values = exact_values(job)
    variances = exact_variances(job)
    return ContrastResult(
        values=tuple(None if v is None else float(v) for v in values),
        errors=tuple(
            None if v is None or q is None else correctly_rounded_root(q, 2)
            for v, q in zip(values, variances, strict=True)
        ),
    )

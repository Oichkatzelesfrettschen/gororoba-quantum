"""Contracts of the exact-rational contrast statistics: independent solves, branch rules, rounding, determinism.

Every fixture holds small integer counts and assignment rates k / 64, so each exact evaluation takes milliseconds;
the retained 19-batch regeneration is the on-demand gate core-pathion-one-cz-null-tuna-analysis-replay.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

import pytest

import exact_contrast_statistics as ecs
import parallel

SIGN = (1, -1, 1, 1, -1, 1, 1, 1)
ZERO = Fraction(1, 10**9)
RATES = ((3, 2), (1, 4), (5, 5), (2, 3), (4, 1))


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _readout(shift: int = 0, extra: Fraction = Fraction(0)) -> ecs.Readout:
    """Five (e01, e10) pairs of the form k / 64; `extra` moves the first e01 by an exact amount."""
    pairs = [(Fraction(a + shift % 3, 64), Fraction(b + shift % 2, 64)) for a, b in RATES]
    pairs[0] = (pairs[0][0] + extra, pairs[0][1])
    return tuple(pairs)


def _counts(shift: int = 0) -> tuple[int, ...]:
    return tuple(20 + (7 * i * i + 3 * i + 11 * shift) % 41 for i in range(ecs.OUTCOMES))


def _job(shift: int = 0, corrected: bool = True, extra: Fraction = Fraction(0)) -> ecs.ContrastJob:
    return ecs.ContrastJob(_counts(shift), SIGN, _readout(shift, extra) if corrected else None, ZERO)


def _generic_solve(readout: ecs.Readout, counts: tuple[int, ...]) -> list[Fraction]:
    """Gauss-Jordan elimination of the explicit 32 x 32 assignment matrix (row = measured, column = true)."""
    size = ecs.OUTCOMES
    matrix = [[Fraction(1)] * size for _ in range(size)]
    for measured in range(size):
        for true in range(size):
            for bit, (e01, e10) in enumerate(readout):
                cell = ((1 - e01, e10), (e01, 1 - e10))[measured >> bit & 1][true >> bit & 1]
                matrix[measured][true] *= cell
    rows = [[*matrix[r], Fraction(counts[r])] for r in range(size)]
    for column in range(size):
        pivot = next(r for r in range(column, size) if rows[r][column] != 0)
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [entry / scale for entry in rows[column]]
        for r in range(size):
            if r != column and rows[r][column] != 0:
                factor = rows[r][column]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[column], strict=True)]
    return [rows[r][size] for r in range(size)]


def _integer_scale(values: list[Fraction]) -> list[int]:
    scale = math.lcm(*(v.denominator for v in values))
    return [int(v * scale) for v in values]


def test_the_kronecker_inverse_equals_an_independent_gauss_jordan_solve() -> None:
    for shift in range(3):
        job = _job(shift)
        generic = _integer_scale(_generic_solve(_readout(shift), _counts(shift)))
        _expect(
            ecs.exact_values(job) == ecs.contrast_outputs(generic, SIGN, ZERO),
            f"shift {shift}: the bit-by-bit inverse and the explicit matrix solve disagree",
        )


def test_the_corrected_vector_keeps_the_shot_total_up_to_one_common_scale() -> None:
    readout = _readout()
    scaled = ecs.scaled_inverse_readout(readout, list(_counts()))
    exact = _generic_solve(readout, _counts())
    ratio = Fraction(scaled[0]) / exact[0]
    _expect(all(Fraction(s) == ratio * e for s, e in zip(scaled, exact, strict=True)), "scale is not common")
    _expect(sum(exact) == sum(_counts()), "a column-stochastic assignment matrix preserves the shot total")


def test_a_singular_assignment_is_refused() -> None:
    singular = ((Fraction(1, 2), Fraction(1, 2)),) * 5
    with pytest.raises(ValueError, match="singular"):
        ecs.exact_values(ecs.ContrastJob(_counts(), SIGN, singular, ZERO))


@pytest.mark.parametrize("degree", [2, 3, 21])
def test_the_root_is_the_float_nearest_to_the_true_root(degree: int) -> None:
    values = [Fraction(2), Fraction(1, 3), Fraction(10**30 + 7, 10**9), Fraction(5, 10**40), Fraction(7**21, 3**5)]
    for value in values:
        root = ecs.correctly_rounded_root(value, degree)
        below, above = math.nextafter(root, 0.0), math.nextafter(root, math.inf)
        low, high = (Fraction(root) + Fraction(below)) / 2, (Fraction(root) + Fraction(above)) / 2
        _expect(low**degree <= value <= high**degree, f"{value} ** (1 / {degree}) is not nearest to {root!r}")


def test_the_square_root_equals_the_correctly_rounded_math_sqrt_and_exact_roots_stay_exact() -> None:
    for x in (0.1, 2.0, 3.141592653589793, 1e-300, 123456.789):
        _expect(ecs.correctly_rounded_root(Fraction(x), 2) == math.sqrt(x), f"sqrt({x!r})")
    _expect(ecs.correctly_rounded_root(Fraction(1, 4), 2) == 0.5, "sqrt(1/4)")
    _expect(ecs.correctly_rounded_root(Fraction(27), 3) == 3.0, "cbrt(27)")
    _expect(ecs.correctly_rounded_root(Fraction(0), 5) == 0.0, "root of zero")
    with pytest.raises(ValueError, match="negative"):
        ecs.correctly_rounded_root(Fraction(-1), 2)


def test_an_empty_pile_leaves_every_output_and_error_undefined() -> None:
    counts = tuple([0] * ecs.HALF + [3] * ecs.HALF)
    result = ecs.contrast_statistics(ecs.ContrastJob(counts, SIGN, None, ZERO))
    _expect(all(v is None for v in result.values + result.errors), f"{result}")


def test_equal_piles_leave_the_ratios_and_nullity_undefined_but_keep_c_and_v() -> None:
    pile = [5, 9, 4, 7, 6, 8, 3, 10, 2, 6, 7, 5, 9, 4, 8, 3]
    result = ecs.contrast_statistics(ecs.ContrastJob(tuple(pile + pile), SIGN, None, ZERO))
    bins, ratios = result.values[: ecs.BINS], result.values[ecs.BINS : 2 * ecs.BINS]
    _expect(all(v == 0.0 for v in bins) and result.values[16] == 0.0, f"{result.values}")
    _expect(all(v is None for v in ratios) and result.values[17] is None, "ratio and N_hat are undefined at V = 0")
    _expect(all(e is None for e in result.errors[ecs.BINS : 2 * ecs.BINS]) and result.errors[17] is None, "errors")
    _expect(all(e is not None and e > 0.0 for e in result.errors[: ecs.BINS]), "c keeps its error at V = 0")


def test_a_bin_below_the_zero_weight_threshold_contributes_nothing() -> None:
    plus = [5, 1, 1, 1, 1, 1, 1, 1] + [95, 1, 1, 1, 1, 1, 1, 1]
    minus = [4, 1, 1, 1, 1, 1, 1, 1] + [4, 1, 1, 1, 1, 1, 1, 1]
    piles = [*minus, *plus]
    wide = ecs.contrast_outputs(piles, SIGN, Fraction(1, 10**9))
    narrow = ecs.contrast_outputs(piles, SIGN, Fraction(1, 2))
    _expect(wide[0] == Fraction(5, 100) - Fraction(4, 8), f"bin 0 reads its conditional probabilities: {wide[0]}")
    _expect(narrow[0] == Fraction(5, 100), "the minus pile's bin weight 8 / 18 sits below 1/2 and reads 0")


def test_a_malformed_job_is_refused() -> None:
    for job in (
        ecs.ContrastJob(_counts()[:31], SIGN, None, ZERO),
        ecs.ContrastJob(_counts(), SIGN[:7], None, ZERO),
        ecs.ContrastJob(_counts(), SIGN, None, Fraction(0)),
        ecs.ContrastJob((0,) * ecs.OUTCOMES, SIGN, None, ZERO),
    ):
        with pytest.raises(ValueError):
            ecs.contrast_statistics(job)


def _readout_with(pair_index: int, pair: tuple[Fraction, Fraction]) -> ecs.Readout:
    pairs = list(_readout())
    pairs[pair_index] = pair
    return tuple(pairs)


@pytest.mark.parametrize(
    ("job", "field"),
    [
        (ecs.ContrastJob((-1, *_counts()[1:]), SIGN, None, ZERO), "counts"),
        (ecs.ContrastJob((1.5, *_counts()[1:]), SIGN, None, ZERO), "counts"),  # type: ignore[arg-type]
        (ecs.ContrastJob(_counts(), (2, *SIGN[1:]), None, ZERO), "sign"),
        (ecs.ContrastJob(_counts(), SIGN, _readout()[:4], ZERO), "readout needs exactly 5"),
        (ecs.ContrastJob(_counts(), SIGN, _readout_with(2, (Fraction(-1, 64), Fraction(1, 64))), ZERO), "bit 2"),
        (ecs.ContrastJob(_counts(), SIGN, _readout_with(3, (Fraction(1, 64), Fraction(65, 64))), ZERO), "bit 3"),
        (ecs.ContrastJob(_counts(), SIGN, _readout_with(1, (Fraction(1, 4), Fraction(3, 4))), ZERO), "singular"),
    ],
)
def test_each_malformed_job_field_is_refused_with_its_name(job: ecs.ContrastJob, field: str) -> None:
    with pytest.raises(ValueError, match=field):
        ecs.contrast_statistics(job)


@pytest.mark.parametrize("degree", [0, -1])
def test_a_root_of_nonpositive_degree_is_refused(degree: int) -> None:
    with pytest.raises(ValueError, match="degree"):
        ecs.correctly_rounded_root(Fraction(2), degree)
    with pytest.raises(ValueError, match="degree"):
        ecs.integer_root(4, degree)


def test_the_floats_ignore_a_perturbation_far_below_one_ulp_and_follow_one_above_it() -> None:
    base = ecs.contrast_statistics(_job())
    below = ecs.contrast_statistics(_job(extra=Fraction(1, 10**40)))
    above = ecs.contrast_statistics(_job(extra=Fraction(1, 10**14)))
    _expect(below == base, "an exact rate perturbation of 1e-40 changed a rounded float")
    _expect(above.values != base.values, "an exact rate perturbation of 1e-14 left every value unchanged")


def test_one_more_shot_in_any_outcome_changes_the_result() -> None:
    base = ecs.contrast_statistics(_job())
    for index in (0, 7, 16, 31):
        counts = list(_counts())
        counts[index] += 1
        moved = ecs.contrast_statistics(ecs.ContrastJob(tuple(counts), SIGN, _readout(), ZERO))
        _expect(moved != base, f"a shot added to outcome {index} left the statistics unchanged")


def _perturbed_counts(job: ecs.ContrastJob, index: int, step: int) -> ecs.ContrastJob:
    counts = list(job.counts)
    counts[index] += step
    return ecs.ContrastJob(tuple(counts), job.sign, job.readout, job.zero)


def _multinomial_variances(job: ecs.ContrastJob) -> list[Fraction | None]:
    """J cov J^T with cov = N (diag p - p p^T) formed explicitly and J the central difference of exact_values at
    counts +- e_i (the readout correction applied to each perturbed integer vector, not through linearity)."""
    total = sum(job.counts)
    probability = [Fraction(n, total) for n in job.counts]
    covariance = [
        [
            total * ((probability[i] if i == j else Fraction(0)) - probability[i] * probability[j])
            for j in range(ecs.OUTCOMES)
        ]
        for i in range(ecs.OUTCOMES)
    ]
    ups = [ecs.exact_values(_perturbed_counts(job, i, 1)) for i in range(ecs.OUTCOMES)]
    downs = [ecs.exact_values(_perturbed_counts(job, i, -1)) for i in range(ecs.OUTCOMES)]
    variances: list[Fraction | None] = []
    for k in range(ecs.OUTPUTS):
        if any(up[k] is None or down[k] is None for up, down in zip(ups, downs, strict=True)):
            variances.append(None)
            continue
        jacobian = [(up[k] - down[k]) / 2 for up, down in zip(ups, downs, strict=True)]  # type: ignore[operator]
        covariance_times_j = [
            sum((c * j for c, j in zip(row, jacobian, strict=True)), Fraction(0)) for row in covariance
        ]
        variances.append(sum((j * w for j, w in zip(jacobian, covariance_times_j, strict=True)), Fraction(0)))
    return variances


@pytest.mark.parametrize("corrected", [True, False])
def test_the_exact_variances_equal_an_explicit_multinomial_covariance_sandwich(corrected: bool) -> None:
    job = _job(1, corrected=corrected)
    expected = _multinomial_variances(job)
    _expect(all(v is not None and v > 0 for v in expected), "every output of the fixture has a defined variance")
    _expect(ecs.exact_variances(job) == expected, "exact_variances differs from J cov J^T")


# Counts of the 32 outcomes as (minus pile first half, minus second half, plus first half, plus second half); bin y
# pairs outcome y with outcome y + 8 inside one pile. Conditional probabilities of the plus / minus piles:
# bin 0: 1/4, 3/4; 1: 3/4, 1/2; 2: 1/2, 1/2; 3: 3/4, 1/4; 4: 2/3, 1/3; 5: 1/4, 1/2; 6: 1/2, 1; 7: 3/4, 1/2.
HAND_COUNTS = (3, 1, 2, 1, 1, 3, 4, 1) + (1, 1, 2, 3, 2, 3, 0, 1) + (1, 3, 2, 3, 2, 1, 2, 3) + (3, 1, 2, 1, 1, 3, 2, 1)
HAND_CONTRAST = [Fraction(n, d) for n, d in ((-1, 2), (1, 4), (0, 1), (1, 2), (1, 3), (-1, 4), (-1, 2), (1, 4))]
HAND_SIGN = (1, -1, 1, 0, -1, 1, -1, 1)


def test_contrast_visibility_ratio_and_nullity_follow_the_hand_computed_fixture() -> None:
    # V = (1/8) sum c s = -7/96, c / V = c (-96/7), N_hat = (sum c) / 2 / V = (1/24) (-96/7) = -4/7.
    values = ecs.exact_values(ecs.ContrastJob(HAND_COUNTS, HAND_SIGN, None, ZERO))
    visibility = Fraction(-7, 96)
    _expect(values[:8] == HAND_CONTRAST, f"c(y) {values[:8]}")
    _expect(values[16] == visibility, f"V {values[16]}")
    _expect(values[8:16] == [c / visibility for c in HAND_CONTRAST], f"c / V {values[8:16]}")
    _expect(values[8] == Fraction(48, 7) and values[9] == Fraction(-24, 7) and values[10] == 0, "c / V of bins 0-2")
    _expect(values[17] == Fraction(-4, 7), f"N_hat {values[17]}")


def test_swapping_the_piles_negates_c_and_v_and_flipping_one_sign_moves_v_ratios_and_nullity() -> None:
    swapped = ecs.exact_values(ecs.ContrastJob(HAND_COUNTS[16:] + HAND_COUNTS[:16], HAND_SIGN, None, ZERO))
    _expect(swapped[:8] == [-c for c in HAND_CONTRAST], "swapped piles negate every c(y)")
    _expect(swapped[16] == Fraction(7, 96), "swapped piles negate V")
    _expect(swapped[8:16] == [c / Fraction(-7, 96) for c in HAND_CONTRAST] and swapped[17] == Fraction(-4, 7), "ratios")
    flipped_sign = (-1, *HAND_SIGN[1:])
    flipped = ecs.exact_values(ecs.ContrastJob(HAND_COUNTS, flipped_sign, None, ZERO))
    # c(0) = -1/2 changes sign in the sum: V = (-7/12 + 1) / 8 = 5/96 and N_hat = (1/24) / (5/96) = 4/5.
    _expect(flipped[:8] == HAND_CONTRAST and flipped[16] == Fraction(5, 96), f"V {flipped[16]}")
    _expect(flipped[8:16] == [c * Fraction(96, 5) for c in HAND_CONTRAST] and flipped[17] == Fraction(4, 5), "ratios")


def test_a_bin_weight_exactly_at_the_threshold_contributes_nothing_and_one_epsilon_below_it_contributes() -> None:
    # Every minus bin has weight 2 of 16 (1/8); plus bin 0 has weight 12 of 26, plus bins 1-7 weight 2 of 26.
    minus = [1] * ecs.HALF
    plus = [10, *([1] * 7), 2, *([1] * 7)]
    piles = [*minus, *plus]
    epsilon = Fraction(1, 10**9)
    at = ecs.contrast_outputs(piles, SIGN, Fraction(1, 8))
    below = ecs.contrast_outputs(piles, SIGN, Fraction(1, 8) - epsilon)
    above = ecs.contrast_outputs(piles, SIGN, Fraction(1, 8) + epsilon)
    _expect(at[0] == above[0] == Fraction(5, 6), f"a minus weight equal to the threshold reads 0: {at[0]}, {above[0]}")
    _expect(below[0] == Fraction(5, 6) - Fraction(1, 2), f"a minus weight just above the threshold counts: {below[0]}")
    _expect(at[1] == above[1] == 0 and below[1] == Fraction(-1, 2), "bin 1 follows the same strict comparison")


@pytest.mark.parametrize("degree", [2, 3])
@pytest.mark.parametrize("anchor", [1.0, math.nextafter(1.0, 2.0), 0.1, 123456.789, 3.0e-5])
def test_a_value_within_two_to_the_minus_200_of_a_halfway_point_rounds_toward_its_side(
    anchor: float, degree: int
) -> None:
    upper = math.nextafter(anchor, math.inf)
    halfway = (Fraction(anchor) + Fraction(upper)) / 2
    tilt = Fraction(1, 2**200)
    _expect(ecs.correctly_rounded_root(halfway**degree * (1 - tilt), degree) == anchor, f"{anchor!r} below halfway")
    _expect(ecs.correctly_rounded_root(halfway**degree * (1 + tilt), degree) == upper, f"{anchor!r} above halfway")


def _moved_job(job: ecs.ContrastJob, removed: int | None, added: int | None) -> ecs.ContrastJob:
    """`job` with one shot taken from outcome `removed` and one given to outcome `added` (None skips a side)."""
    counts = list(job.counts)
    if added is not None:
        counts[added] += 1
    if removed is not None:
        counts[removed] -= 1
    return ecs.ContrastJob(tuple(counts), job.sign, job.readout, job.zero)


def test_every_one_of_the_32_outcomes_enters_the_readout_corrected_values() -> None:
    job = _job(2)
    base = ecs.exact_values(job)
    for index in range(ecs.OUTCOMES):
        other = (index + 1) % ecs.OUTCOMES
        moved = ecs.exact_values(_moved_job(job, index, other))
        _expect(moved != base, f"moving a shot from {index} to {other} left the values unchanged")
        _expect(moved != ecs.exact_values(_moved_job(job, None, other)), f"outcome {index} does not enter the values")
        _expect(moved != ecs.exact_values(_moved_job(job, index, None)), f"outcome {other} does not enter the values")


def test_every_one_of_the_32_outcomes_enters_the_raw_values_and_errors() -> None:
    job = _job(2, corrected=False)
    base = ecs.contrast_statistics(job)
    for index in range(ecs.OUTCOMES):
        other = (index + 1) % ecs.OUTCOMES
        moved = ecs.contrast_statistics(_moved_job(job, index, other))
        added = ecs.contrast_statistics(_moved_job(job, None, other))
        removed = ecs.contrast_statistics(_moved_job(job, index, None))
        _expect(moved != base, f"moving a shot from {index} to {other} left the statistics unchanged")
        _expect(moved.values != added.values and moved.errors != added.errors, f"outcome {index} is ignored")
        _expect(moved.values != removed.values and moved.errors != removed.errors, f"outcome {other} is ignored")


def test_the_record_repeats_exactly_and_follows_the_worker_count(monkeypatch: pytest.MonkeyPatch) -> None:
    jobs = [_job(shift, corrected=shift % 4 != 3) for shift in range(8)]
    reference = [ecs.contrast_statistics(job) for job in jobs]
    _expect([ecs.contrast_statistics(job) for job in jobs] == reference, "a second serial run differs")
    for workers in ("1", "4"):
        monkeypatch.setenv("GOROROBA_WORKERS", workers)
        if parallel.workers() != int(workers):
            pytest.skip(f"fewer than {workers} CPUs available: the worker comparison would run serially")
        mapped: list[Any] = parallel.ordered_map(ecs.contrast_statistics, jobs, min_items=1)
        _expect(repr(mapped) == repr(reference), f"{workers} workers differ from the serial run")

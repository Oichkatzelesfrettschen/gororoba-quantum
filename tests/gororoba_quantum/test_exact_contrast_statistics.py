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

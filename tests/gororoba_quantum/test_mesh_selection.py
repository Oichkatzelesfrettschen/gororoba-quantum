"""Bounded fixtures for the mesh-selection estimators: shrinkage, directional sign selection, permutation and power."""

from __future__ import annotations

import itertools
import math
from typing import Any

import numpy as np
import pytest

from mesh_selection import (
    block_counts,
    contrast_shrinkage,
    exact_permutation_r,
    exact_upper_p,
    normal_cdf,
    persistence,
    persistence_reading,
    relabelings_of,
    replay_power,
    sign_flip_cross_product,
    slope_lower_p,
    slope_upper_bound,
)

LABELS = ("p", "q", "r", "s", "t", "u")
# docs/evidence/anu_qrng/draw-2026-10-31T193354Z.json: index 1 seeds the power simulation, indices 2 and 3 are
# fixture compilation seeds (ledger rows in docs/evidence/qrng_seeds/allocations.json).
POWER_SEED = 50187
FIXTURE_SEED = 54229
OTHER_FIXTURE_SEED = 19256
GRID = np.linspace(0.0, 0.25, 1001)


def counts_for(correct_a: list[int], correct_b: list[int], accepted: int = 2000) -> dict[str, Any]:
    return {
        label: {
            "A": {"correct": ca, "accepted": accepted, "samples": 10 * accepted},
            "B": {"correct": cb, "accepted": accepted, "samples": 10 * accepted},
        }
        for label, ca, cb in zip(LABELS, correct_a, correct_b, strict=True)
    }


def test_equal_blocks_shrink_every_difference_to_zero() -> None:
    record = contrast_shrinkage(counts_for([1600] * 6, [1600] * 6), LABELS, GRID, 0.10)
    if record["tau_mle"] != 0.0 or record["signs_determined"] != 0 or record["chi_square_on_6"] != 0.0:
        raise AssertionError(record)
    if any(row["expected_gap"] != 0.0 for row in record["inputs"].values()):
        raise AssertionError(record["inputs"])


def test_the_shrinkage_factor_equals_the_closed_form_at_a_fixed_tau() -> None:
    record = contrast_shrinkage(counts_for([1700, 1500] * 3, [1500, 1700] * 3), LABELS, np.asarray([0.05]), 0.10)
    s = math.sqrt(0.85 * 0.15 / 2000 + 0.75 * 0.25 / 2000)
    factor = 0.05**2 / (0.05**2 + s**2)
    for label in LABELS:
        row = record["inputs"][label]
        if abs(row["shrinkage_factor"] - factor) > 1e-12 or abs(row["expected_gap"] - 0.1 * factor) > 1e-12:
            raise AssertionError((label, row["shrinkage_factor"], factor))
        if row["z"] * row["difference"] <= 0 or abs(row["difference"]) != pytest.approx(0.1):
            raise AssertionError(row)


def test_directional_bh_selects_the_step_up_set() -> None:
    # z of 6, 4, 2.2, 1.9, 0.5 and 0 at s = 0.01: two-sided p of about 2e-9, 6e-5, 0.028, 0.057, 0.62 and 1, so the
    # step-up thresholds 0.10 k / 6 admit the first four (0.057 <= 0.067).
    differences = [0.06, -0.04, 0.022, 0.019, 0.005, 0.0]
    p_values = [2 * (1 - float(normal_cdf(abs(d) / 0.01))) for d in differences]
    expected = max((k + 1 for k, p in enumerate(sorted(p_values)) if p <= 0.10 * (k + 1) / 6), default=0)
    base = 0.5
    accepted = round(base * (1 - base) / 0.01**2 * 2)
    rows = {}
    for label, d in zip(LABELS, differences, strict=True):
        rows[label] = {
            "A": {"correct": round((base + d / 2) * accepted), "accepted": accepted},
            "B": {"correct": round((base - d / 2) * accepted), "accepted": accepted},
        }
    record = contrast_shrinkage(rows, LABELS, GRID, 0.10)
    if record["signs_determined"] != expected or expected != 4:
        raise AssertionError((record["signs_determined"], expected))
    chosen = {label for label, row in record["inputs"].items() if row["sign_determined_directional_bh"]}
    if chosen != {"p", "q", "r", "s"}:
        raise AssertionError(chosen)


def test_exact_permutation_counts_every_pairing() -> None:
    x = np.asarray([1.0, 2.0, 3.0, 4.0])
    r, p = exact_permutation_r(x, x.copy(), negative=False)
    if r != pytest.approx(1.0) or p != pytest.approx(1 / math.factorial(4)):
        raise AssertionError((r, p))
    r, p = exact_permutation_r(x, -x, negative=True)
    if r != pytest.approx(-1.0) or p != pytest.approx(1 / math.factorial(4)):
        raise AssertionError((r, p))


def test_sign_flip_cross_product_is_label_invariant_and_counts_every_flip() -> None:
    x = np.asarray([1.0, -2.0, 3.0, 0.5])
    y = np.asarray([-0.5, 2.0, -3.0, -1.5])
    total, p = sign_flip_cross_product(x, y, negative=True)
    if total != pytest.approx(-14.25) or p != pytest.approx(1 / 16):
        raise AssertionError((total, p))
    relabeled = np.asarray([-1.0, 1.0, 1.0, 1.0])
    if sign_flip_cross_product(x * relabeled, y * relabeled, negative=True) != (total, p):
        raise AssertionError("relabeling one input changed the statistic")
    if exact_permutation_r(x * relabeled, y * relabeled, negative=True)[0] == pytest.approx(
        exact_permutation_r(x, y, negative=True)[0]
    ):
        raise AssertionError("the centered r was expected to depend on the labels in this fixture")


def test_block_counts_pool_a_blocks_runs_and_refuse_a_second_seed() -> None:
    row = {
        "label": "p",
        "block_of_seed": "A",
        "compilation_seed": FIXTURE_SEED,
        "correct": 3,
        "accepted": 4,
        "samples": 10,
        "nb_shots_used": 100,
        "rejected": {"herald": 2},
    }
    pooled = block_counts([row, dict(row)], ["p"], ["herald"])
    if pooled["p"]["A"] != {
        "correct": 6,
        "accepted": 8,
        "samples": 20,
        "shots": 200,
        "seed": FIXTURE_SEED,
        "rejected_herald": 4,
    }:
        raise AssertionError(pooled)
    with pytest.raises(ValueError, match="mixes compilation seeds"):
        block_counts([row, {**row, "compilation_seed": OTHER_FIXTURE_SEED}], ["p"], ["herald"])


def test_replay_power_has_nominal_size_without_persistent_error_and_power_with_it() -> None:
    counts = counts_for([1700, 1500] * 3, [1500, 1700] * 3)
    shrink = contrast_shrinkage(counts, LABELS, GRID, 0.10)
    record = replay_power(
        counts,
        shrink,
        np.random.SeedSequence(POWER_SEED),
        labels=LABELS,
        tau_grid=GRID,
        trials=20_000,
        samples_per_iteration=1200,
        job_counts=(2,),
        dropouts=(0,),
        z_critical=1.6448536269514722,
    )
    by = {row["scenario"]: row["power"] for row in record["designs"]}
    if not 0.04 <= by["no persistent mesh error"] <= 0.06:
        raise AssertionError(by)
    if by["persistent mesh error"] < 0.9:
        raise AssertionError(by)


# docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json index 1 (ledger row in docs/evidence/qrng_seeds/allocations.json).
REALLOCATION_SEED = 36200


def test_two_row_chi_square_equals_the_pearson_statistic() -> None:
    from scipy.stats import chi2_contingency

    from mesh_selection import two_row_chi_square

    table = np.array([[12.0, 30.0, 7.0, 51.0], [20.0, 18.0, 15.0, 40.0]])
    expected = chi2_contingency(table, correction=False)[0]
    got = float(two_row_chi_square(table[0], table.sum(axis=0)))
    if not math.isclose(got, expected, rel_tol=1e-12):
        raise AssertionError((got, expected))


def test_a_two_by_two_adjusted_residual_squares_to_the_chi_square() -> None:
    from mesh_selection import adjusted_residuals, two_row_chi_square

    table = np.array([[30.0, 10.0], [20.0, 40.0]])
    residual = adjusted_residuals(table)
    chi_square = float(two_row_chi_square(table[0], table.sum(axis=0)))
    if not np.allclose(residual**2, chi_square) or not np.allclose(residual[0], -residual[1]):
        raise AssertionError((residual, chi_square))


def test_proportional_rows_never_reject_and_disjoint_rows_always_do() -> None:
    from mesh_selection import composition_test

    proportional = [np.array([[10, 20, 30], [20, 40, 60]]), np.array([[5, 5, 0], [15, 15, 0]])]
    record = composition_test(proportional, 500, REALLOCATION_SEED)
    if record["statistic"] != 0.0 or record["p"] != 1.0:
        raise AssertionError(record)
    disjoint = [np.array([[60, 0, 0], [0, 30, 30]])]
    record = composition_test(disjoint, 500, REALLOCATION_SEED)
    if record["p"] != 1 / 501:
        raise AssertionError(record)


def test_the_composition_test_replays_from_its_seed_and_refuses_bad_tables() -> None:
    from mesh_selection import composition_test

    tables = [np.array([[12, 30, 7, 51], [20, 18, 15, 40]]), np.array([[3, 9, 4], [6, 2, 8]])]
    first = composition_test(tables, 400, REALLOCATION_SEED)
    second = composition_test(tables, 400, np.random.SeedSequence(REALLOCATION_SEED))
    if first != second:
        raise AssertionError((first, second))
    for bad in (np.ones((3, 4), dtype=int), np.array([[0, 0, 0], [1, 2, 3]])):
        with pytest.raises(ValueError):
            composition_test([bad], 10, REALLOCATION_SEED)


# Thresholds of the Belenos mesh-persistence case, supplied explicitly as its script supplies them.
ALPHA = 0.05
USEFUL_SLOPE = 0.5


def test_exact_upper_p_equals_brute_force_enumeration() -> None:
    per_block = [np.array([0.3, -0.1, 0.2]), np.array([1.0, -1.0]), np.array([0.5, 0.0, -0.5, 0.25])]
    observed = 0.6
    brute = np.mean([sum(c) >= observed - 1e-12 for c in itertools.product(*per_block)])
    if exact_upper_p(per_block, observed) != pytest.approx(brute):
        raise AssertionError((exact_upper_p(per_block, observed), brute))


def test_exact_upper_p_counts_a_sum_equal_to_the_observed_value() -> None:
    # Every value is a binary fraction, so each sum is exact: 3 of the 6 sums reach 0.5 and 2 of those equal it.
    per_block = [np.array([1.0, -1.0]), np.array([0.5, 0.0, -0.5])]
    if exact_upper_p(per_block, 0.5) != pytest.approx(3 / 6):
        raise AssertionError(exact_upper_p(per_block, 0.5))
    if exact_upper_p(per_block, 0.75) != pytest.approx(2 / 6):
        raise AssertionError(exact_upper_p(per_block, 0.75))


def test_a_recurring_deviation_reads_persists_and_a_reversed_one_reads_redrawn() -> None:
    old = np.array(
        [
            [0.60, 0.52, 0.48, 0.40],
            [0.45, 0.55, 0.50, 0.58],
            [0.62, 0.50, 0.41, 0.47],
            [0.51, 0.44, 0.60, 0.53],
            [0.39, 0.47, 0.52, 0.58],
            [0.55, 0.61, 0.43, 0.49],
        ]
    )
    same = persistence(old, old + 0.03, ALPHA, USEFUL_SLOPE)
    if (
        same["slope"] != pytest.approx(1.0)
        or same["p_value"] > 0.01
        or same["slope_upper"] != pytest.approx(1.0, abs=1e-6)
        or persistence_reading(same, ALPHA, USEFUL_SLOPE) != "persists"
    ):
        raise AssertionError(same)
    mirrored = old.mean(axis=1, keepdims=True) - (old - old.mean(axis=1, keepdims=True))
    flipped = persistence(old, mirrored, ALPHA, USEFUL_SLOPE)
    if flipped["slope"] != pytest.approx(-1.0) or persistence_reading(flipped, ALPHA, USEFUL_SLOPE) != "redrawn":
        raise AssertionError(flipped)
    if flipped["slope_upper"] >= USEFUL_SLOPE or flipped["useful_slope_p"] >= ALPHA:
        raise AssertionError(flipped)


def test_persistence_p_value_equals_enumeration_of_the_whole_statistic() -> None:
    """Every within-block relabeling of two blocks of three meshes, with the statistic recomputed from the shares."""
    old = np.array([[0.60, 0.52, 0.41], [0.45, 0.55, 0.58]])
    new = np.array([[0.58, 0.50, 0.47], [0.49, 0.51, 0.60]])
    e_old = old - old.mean(axis=1, keepdims=True)
    e_new = new - new.mean(axis=1, keepdims=True)
    observed = float((e_old * e_new).sum())
    orders = [list(order) for order in itertools.permutations(range(3))]
    values = [
        float((e_old[0] * e_new[0][first]).sum() + (e_old[1] * e_new[1][second]).sum())
        for first in orders
        for second in orders
    ]
    # No relabeling other than the identity lies within 1e-6 of the observed value, so the count has no tie to break.
    if sum(abs(value - observed) < 1e-6 for value in values) != 1:
        raise AssertionError(sorted(values))
    brute = sum(value > observed - 1e-9 for value in values) / len(values)
    result = persistence(old, new, ALPHA, USEFUL_SLOPE)
    if result["statistic"] != pytest.approx(observed) or result["p_value"] != pytest.approx(brute):
        raise AssertionError((result, observed, brute))


def enumerated_lower_p(old: np.ndarray, new: np.ndarray, slope: float) -> float:
    """The share of within-block relabelings of the residuals new - slope old (both centered) whose cross product
    with the centered old shares lies at or below the observed one, over two blocks of three meshes."""
    e_old = old - old.mean(axis=1, keepdims=True)
    residual = new - new.mean(axis=1, keepdims=True) - slope * e_old
    observed = float((e_old * residual).sum())
    orders = [list(order) for order in itertools.permutations(range(3))]
    values = [
        float((e_old[0] * residual[0][first]).sum() + (e_old[1] * residual[1][second]).sum())
        for first in orders
        for second in orders
    ]
    return sum(value <= observed + 1e-12 for value in values) / len(values)


def test_the_slope_bound_inverts_the_enumerated_relabeling_test() -> None:
    old = np.array([[0.60, 0.52, 0.41], [0.45, 0.55, 0.58]])
    new = np.array([[0.58, 0.50, 0.47], [0.49, 0.51, 0.60]])
    e_old = old - old.mean(axis=1, keepdims=True)
    e_new = new - new.mean(axis=1, keepdims=True)
    slopes = (-1.0, 0.0, 0.3, 0.5, 0.9, 1.4, 3.0)
    exact = [slope_lower_p(e_old, e_new, slope) for slope in slopes]
    if exact != pytest.approx([enumerated_lower_p(old, new, slope) for slope in slopes]):
        raise AssertionError(exact)
    if any(later > earlier for earlier, later in itertools.pairwise(exact)):
        raise AssertionError(("the p-value rises with the slope", exact))
    # 36 relabelings: the identity alone gives 1/36, below alpha 0.05, so the bound is finite.
    result = persistence(old, new, ALPHA, USEFUL_SLOPE)
    upper = result["slope_upper"]
    if enumerated_lower_p(old, new, upper) < ALPHA or enumerated_lower_p(old, new, upper + 1e-6) >= ALPHA:
        raise AssertionError((upper, enumerated_lower_p(old, new, upper), enumerated_lower_p(old, new, upper + 1e-6)))
    if upper <= result["slope"] or result["useful_slope_p"] != pytest.approx(
        enumerated_lower_p(old, new, USEFUL_SLOPE)
    ):
        raise AssertionError(result)
    if slope_upper_bound(e_old, e_new, 0.20) >= upper:
        raise AssertionError("a larger alpha does not tighten the one-sided upper bound")
    if (result["useful_slope_p"] < ALPHA) != (upper < USEFUL_SLOPE):
        raise AssertionError("the p-value at the useful slope and the bound disagree on redrawn")
    if "slope_upper" in persistence(old, new, ALPHA, USEFUL_SLOPE, bound=False):
        raise AssertionError("bound=False still computes the bound")
    # Two tied retained deviations per block leave 4 of 36 relabelings unchanged at every slope: no finite bound.
    tied = np.array([[0.60, 0.60, 0.41], [0.45, 0.58, 0.58]])
    if slope_upper_bound(tied - tied.mean(axis=1, keepdims=True), e_new, ALPHA) != math.inf:
        raise AssertionError("tied retained deviations give a finite bound")


def test_the_slope_bound_is_finite_for_nearly_tied_retained_shares() -> None:
    new = np.array([[0.50, 0.58, 0.47], [0.49, 0.51, 0.60]])
    e_new = new - new.mean(axis=1, keepdims=True)
    # A gap of 1e-6 between two retained shares holds the swap of those meshes in the count up to a slope near
    # 8e4, far beyond a fixed number of steps from the estimate; the bound is that slope.
    old = np.array([[0.60, 0.600001, 0.41], [0.45, 0.55, 0.58]])
    e_old = old - old.mean(axis=1, keepdims=True)
    upper = slope_upper_bound(e_old, e_new, ALPHA)
    if not 200.0 < upper < 1e5:
        raise AssertionError(upper)
    # The enumeration forms the residuals at the slope itself and resolves this bound to about one part in 1e4.
    if enumerated_lower_p(old, new, upper * 0.99) < ALPHA or enumerated_lower_p(old, new, upper * 1.01) >= ALPHA:
        raise AssertionError((upper, enumerated_lower_p(old, new, upper * 0.99)))
    # At a gap of 1e-12 the bound exceeds 1e12, where adjacent floats lie further apart than the tolerance: the
    # bisection ends on adjacent floats with a finite value.
    old[0, 1] = 0.60 + 1e-12
    e_old = old - old.mean(axis=1, keepdims=True)
    upper = slope_upper_bound(e_old, e_new, ALPHA)
    if not 1e12 < upper < 2e12 or slope_lower_p(e_old, e_new, upper) < ALPHA:
        raise AssertionError(upper)
    if slope_lower_p(e_old, e_new, math.inf) != pytest.approx(1 / 36):
        raise AssertionError(slope_lower_p(e_old, e_new, math.inf))


def test_the_slope_bound_brackets_downward_and_holds_when_one_block_is_louder() -> None:
    old = np.array([[0.60, 0.52, 0.41], [0.45, 0.55, 0.58]])
    quiet = np.array([[0.58, 0.50, 0.47], [0.49, 0.51, 0.60]])
    loud = quiet.copy()
    loud[1] = 0.5 + 8.0 * (quiet[1] - quiet[1].mean())
    e_old = old - old.mean(axis=1, keepdims=True)
    for new in (quiet, loud):
        e_new = new - new.mean(axis=1, keepdims=True)
        # At alpha 0.9 the test already rejects the slope estimate, so the bound lies below it.
        for alpha in (ALPHA, 0.9):
            upper = slope_upper_bound(e_old, e_new, alpha)
            if enumerated_lower_p(old, new, upper) < alpha or enumerated_lower_p(old, new, upper + 1e-6) >= alpha:
                raise AssertionError((new, alpha, upper))
        estimate = float((e_old * e_new).sum() / (e_old**2).sum())
        if slope_lower_p(e_old, e_new, estimate) >= 0.9 or slope_upper_bound(e_old, e_new, 0.9) >= estimate:
            raise AssertionError("alpha 0.9 does not place the bound below the estimate")


def test_reading_thresholds_are_strict_and_supplied_by_the_caller() -> None:
    below = math.nextafter(ALPHA, 0.0)
    under = math.nextafter(USEFUL_SLOPE, 0.0)

    def reading(p_value: float, slope: float, useful_slope_p: float, alpha: float, useful: float) -> str:
        return persistence_reading(
            {"p_value": p_value, "slope": slope, "useful_slope_p": useful_slope_p}, alpha, useful
        )

    low = "recurs below the useful slope"
    readings = {
        "p below alpha, slope at the useful slope": (
            reading(below, USEFUL_SLOPE, 0.9, ALPHA, USEFUL_SLOPE),
            "persists",
        ),
        "p below alpha, slope under the useful slope, bound above it": (
            reading(below, under, ALPHA, ALPHA, USEFUL_SLOPE),
            "indeterminate",
        ),
        "p below alpha, bound under the useful slope": (reading(below, under, below, ALPHA, USEFUL_SLOPE), low),
        "a bound under the useful slope outranks the estimate": (reading(below, 0.9, below, ALPHA, USEFUL_SLOPE), low),
        "p at alpha, bound under the useful slope": (reading(ALPHA, 0.1, below, ALPHA, USEFUL_SLOPE), "redrawn"),
        "p at alpha, p at the useful slope at alpha": (
            reading(ALPHA, 0.1, ALPHA, ALPHA, USEFUL_SLOPE),
            "indeterminate",
        ),
        "p at alpha, slope above the useful slope": (reading(ALPHA, 0.9, 0.9, ALPHA, USEFUL_SLOPE), "indeterminate"),
        "alpha 0.10 admits p 0.07": (reading(0.07, 0.9, 0.9, 0.10, USEFUL_SLOPE), "persists"),
        "alpha 0.05 refuses p 0.07": (reading(0.07, 0.9, 0.9, ALPHA, USEFUL_SLOPE), "indeterminate"),
        "alpha 0.10 reads p 0.07 at the useful slope as redrawn": (
            reading(0.5, 0.1, 0.07, 0.10, USEFUL_SLOPE),
            "redrawn",
        ),
        "useful slope 0.3 admits slope 0.4": (reading(below, 0.4, 0.9, ALPHA, 0.3), "persists"),
        "useful slope 0.5 refuses slope 0.4": (reading(below, 0.4, 0.9, ALPHA, USEFUL_SLOPE), "indeterminate"),
    }
    wrong = {name: got for name, (got, want) in readings.items() if got != want}
    if wrong:
        raise AssertionError(wrong)


def test_a_full_sample_of_relabelings_reproduces_the_enumerated_reading() -> None:
    """Passing all m! relabelings with the identity first reproduces the enumerated p-values and slope bound, and a
    sample that is empty, non-integer, holds a row that is no permutation, or whose row 0 is not the identity is
    refused."""
    rng = np.random.default_rng(FIXTURE_SEED)
    old = rng.normal(size=(1, 5))
    new = 0.8 * old + 0.3 * rng.normal(size=(1, 5))
    every = np.array(list(itertools.permutations(range(5))))
    exact = persistence(old, new, 0.05, 0.5)
    sampled = persistence(old, new, 0.05, 0.5, relabelings=every)
    if exact != sampled:
        raise AssertionError(f"{exact} differs from {sampled}")
    with pytest.raises(ValueError, match="identity in row 0"):
        relabelings_of(5, every[::-1])
    with pytest.raises(ValueError, match="at least one row"):
        relabelings_of(5, every[:0])
    with pytest.raises(ValueError, match="integer labels"):
        relabelings_of(5, every[:3].astype(float))
    repeated = every[:3].copy()
    repeated[1] = [0, 1, 2, 4, 4]
    with pytest.raises(ValueError, match="permutation of range"):
        relabelings_of(5, repeated)


def test_a_partial_sample_of_relabelings_keeps_the_test_monotone_and_the_bound_inverted() -> None:
    """With a partial sample of relabelings (identity first) the useful-slope p-value never rises with the slope,
    the observed labeling keeps every p-value at or above 1 / (sample size), and the upper bound sits where the
    sampled test switches from accepting to rejecting."""
    rng = np.random.default_rng(FIXTURE_SEED)
    m = 40
    old = rng.normal(size=(1, m))
    new = 0.7 * old + 0.5 * rng.normal(size=(1, m))
    sample = np.vstack([np.arange(m)[None, :], rng.permuted(np.tile(np.arange(m), (999, 1)), axis=1)])
    values = [slope_lower_p(old - old.mean(), new - new.mean(), b, sample) for b in np.linspace(-1.0, 3.0, 41)]
    if any(later > earlier for earlier, later in itertools.pairwise(values)) or min(values) < 1 / 1000:
        raise AssertionError(f"sampled p-values {values}")
    e_old, e_new = old - old.mean(), new - new.mean()
    bound = slope_upper_bound(e_old, e_new, 0.05, relabelings=sample)
    if not (slope_lower_p(e_old, e_new, bound, sample) >= 0.05 > slope_lower_p(e_old, e_new, bound + 1e-6, sample)):
        raise AssertionError(f"bound {bound} does not invert the sampled test")

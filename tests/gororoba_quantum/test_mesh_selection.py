"""Bounded fixtures for the mesh-selection estimators: shrinkage, directional sign selection, permutation and power."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pytest

from mesh_selection import (
    block_counts,
    contrast_shrinkage,
    exact_permutation_r,
    normal_cdf,
    replay_power,
    sign_flip_cross_product,
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

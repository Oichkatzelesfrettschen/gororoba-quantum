import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts")]

import bdsc_drift_series as ds  # noqa: E402

LABELS = ["+", "-", "+i", "-i"] * 4 + ["f"] * 4 + ["g"] * 4


def run(values: list[float], start: float, dark: list[float] | None = None) -> dict[str, Any]:
    return {
        "start": start,
        "dark": dark or [0.0],
        "values": {i: {"label": LABELS[i], "p": p, "se": 0.0018} for i, p in enumerate(values)},
    }


def series(rng: np.random.Generator, step: float, n: int = 7) -> list[dict[str, Any]]:
    noise = rng.standard_normal((n, len(LABELS))) * 0.0018
    walk = np.cumsum(rng.standard_normal((n, len(LABELS))) * step, axis=0)
    x = 0.5 + noise + walk
    return [run(list(x[t]), 3600.0 * 2 * t) for t in range(n)]


def test_the_null_variance_matches_the_von_neumann_ratio_of_white_noise() -> None:
    rng = np.random.default_rng(20261024)
    ratios = [ds.von_neumann(list(rng.standard_normal(7))) for _ in range(20000)]
    if abs(np.mean(ratios) - 2) > 0.02 or abs(np.var(ratios) / ds.null_variance(7) - 1) > 0.05:
        raise AssertionError((np.mean(ratios), np.var(ratios)))


def test_white_jitter_reads_consistent_and_a_drift_reads_resolved() -> None:
    rng = np.random.default_rng(7)
    if ds.primary(series(rng, 0.0))["reading"] != "consistent":
        raise AssertionError("white noise did not read consistent")
    if ds.primary(series(rng, 0.004))["reading"] != "resolved":
        raise AssertionError("a random walk did not read resolved")


def test_jitter_shared_within_each_group_of_four_settings_keeps_the_size() -> None:
    rng = np.random.default_rng(5)
    resolved = 0
    for _ in range(200):
        shared = np.repeat(rng.standard_normal((4, 7)), ds.GROUP, axis=0) * 0.005
        own = rng.standard_normal((16, 7)) * 0.0005
        resolved += float(ds._synthetic_p(0.5 + shared + own)) < 0.01
    if resolved > 6:
        raise AssertionError(f"{resolved} of 200 group-correlated white series read resolved")


def test_the_identity_ordering_is_the_observed_statistic_and_reversal_ties() -> None:
    rng = np.random.default_rng(9)
    x = rng.standard_normal((16, 6))
    stats = ds.ordering_statistics(x)
    observed = np.mean([ds.von_neumann(list(row)) for row in x])
    if not math.isclose(stats[0], observed, rel_tol=1e-12) or len(stats) != 720:
        raise AssertionError((stats[0], observed))
    if float(ds.permutation_p(x)[1]) < 2 / 720:
        raise AssertionError("an ordering and its reverse did not tie")


def test_a_common_shift_of_the_class_does_not_enter_the_primary() -> None:
    rng = np.random.default_rng(11)
    white = series(rng, 0.0)
    shifted = [run([v["p"] + 0.01 * t for v in r["values"].values()], r["start"]) for t, r in enumerate(white)]
    a, b = ds.primary(white)["mean_ratio"], ds.primary(shifted)["mean_ratio"]
    if not math.isclose(a, b, rel_tol=1e-9):
        raise AssertionError((a, b))


def test_too_few_series_runs_leave_the_primary_not_run() -> None:
    rng = np.random.default_rng(3)
    if ds.primary(series(rng, 0.0, n=ds.MIN_POINTS - 1))["reading"] != "not run":
        raise AssertionError("a short series read")


def test_epochs_change_where_the_dark_vector_changes() -> None:
    runs = [run([0.5] * 24, t, dark) for t, dark in enumerate([[1.0], [1.0], [2.0], [2.0], [1.0]])]
    if ds.epochs(runs) != [0, 0, 1, 1, 2]:
        raise AssertionError(ds.epochs(runs))


def test_the_anchors_read_across_one_calibration() -> None:
    out = ds.readout([])
    if out["primary"]["reading"] != "not run" or [r["epoch"] for r in out["runs"]] != [0, 1]:
        raise AssertionError(out["runs"])
    (pair,) = out["pairs"]
    if not 0 < pair["lag_hours"] < 1 or pair["same_epoch"]:
        raise AssertionError(pair)


def test_a_directory_outside_the_series_is_refused() -> None:
    with pytest.raises(ValueError, match="not a series run"):
        ds.readout([ROOT / "results/quandela/runs" / ds.ANCHORS[1]])


@pytest.mark.parametrize("receipt", [None, {"run": "other", "outcome": "passed"}, {"outcome": "failed"}])
def test_a_series_run_without_its_passed_receipt_is_refused(tmp_path: Path, monkeypatch, receipt) -> None:
    run = tmp_path / "2026-10-24T120000Z-qpu_belenos-bdsc_drift_series-t1"
    monkeypatch.setattr(ds, "STATE_DIR", tmp_path / "state")
    if receipt is not None:
        (tmp_path / "state").mkdir()
        (tmp_path / "state/t1.receipt.json").write_text(json.dumps({"run": run.name, **receipt}))
    with pytest.raises(ValueError, match="receipt"):
        ds.require_passed_receipt(run)


def test_a_common_drift_with_binomial_errors_does_not_read_as_instance_drift() -> None:
    # Eight settings at 0.2 and eight at 0.6, all rising 0.005 per run, errors recomputed from each fraction.
    runs = []
    for t in range(7):
        values = [0.2 + 0.005 * t] * 8 + [0.6 + 0.005 * t] * 8 + [0.001] * 4 + [0.99] * 4
        record = run(values, 7200.0 * t)
        for value in record["values"].values():
            value["se"] = math.sqrt(value["p"] * (1 - value["p"]) / 100000)
        runs.append(record)
    jitter = np.random.default_rng(13).standard_normal((7, 16)) * 1e-4
    for record, row in zip(runs, jitter, strict=True):
        for i, value in enumerate(row):
            record["values"][i]["p"] += value
    if ds.primary(runs)["reading"] == "resolved":
        raise AssertionError("a common drift read as instance-specific drift")


def test_a_stack_of_series_returns_each_series_bit_for_bit() -> None:
    rng = np.random.default_rng(17)
    stack = [
        rng.standard_normal((16, 7)) * 0.0018,
        np.round(rng.standard_normal((16, 7)), 1),
        rng.standard_normal((16, 7)) * 1e-9 + 0.5,
        rng.standard_normal((16, 7)) * 1e3,
        np.tile(rng.standard_normal(7), (16, 1)) + rng.standard_normal((16, 7)) * 1e-12,
    ]
    together = ds._synthetic_p(np.array(stack))
    alone = np.array([ds._synthetic_p(x) for x in stack])
    if together.tobytes() != alone.tobytes():
        raise AssertionError((together, alone))
    stats = ds.ordering_statistics(np.array(stack))
    if any(ds.ordering_statistics(x).tobytes() != stats[k].tobytes() for k, x in enumerate(stack)):
        raise AssertionError("the batched statistics differ from the single-series ones")


def test_the_centered_counting_variance_is_the_mean_over_every_sign_pattern() -> None:
    se = [0.001 * (1 + k % 5) for k in range(16)]
    first = {"values": {k: {"label": LABELS[k], "p": 0.4, "se": 0.0} for k in range(16)}}
    signs = np.array(list(itertools.product((-1.0, 1.0), repeat=16)))
    changes = signs * np.array(se)
    centered = changes - changes.mean(axis=1, keepdims=True)
    second = {"values": {k: {"label": LABELS[k], "p": 0.4, "se": se[k]} for k in range(16)}}
    expected = ds.centered_counting_variances(first, second)
    observed = (centered**2).mean(axis=0)
    if not np.allclose(observed, [expected[k] for k in range(16)], rtol=1e-12, atol=0):
        raise AssertionError((observed, expected))


def test_a_fixed_linear_effect_obeys_both_sum_rules_in_every_group() -> None:
    bank = {"f": 0.1, "g": 0.9, "+": 0.6, "-": 0.4, "+i": 0.7, "-i": 0.3}
    values = {6 * g + k: {"label": label, "p": p} for g in (0, 1, 6) for k, (label, p) in enumerate(bank.items())}
    rules = ds.sum_rules(values)
    if [r["group"] for r in rules] != [0, 1, 6] or any(abs(r["delta_r"]) + abs(r["delta_i"]) > 1e-15 for r in rules):
        raise AssertionError(rules)


def test_an_excess_that_grows_with_lag_reaches_the_smallest_relabeling_p() -> None:
    runs = [
        run([0.4 + (-1) ** k * 0.001 * t for k in range(16)] + [0.001] * 4 + [0.99] * 4, 7200.0 * t) for t in range(7)
    ]
    for record in runs:
        for value in record["values"].values():
            value["se"] = 1e-9
    trend = ds.lag_trend(runs)
    if abs(trend["spearman"] - 1) > 1e-12 or abs(trend["p_value"] - 2 / 5040) > 1e-15:
        raise AssertionError(trend)

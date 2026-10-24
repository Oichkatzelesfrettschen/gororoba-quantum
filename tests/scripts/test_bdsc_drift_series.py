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
        resolved += ds._synthetic_p(0.5 + shared + own) < 0.01
    if resolved > 6:
        raise AssertionError(f"{resolved} of 200 group-correlated white series read resolved")


def test_the_identity_ordering_is_the_observed_statistic_and_reversal_ties() -> None:
    rng = np.random.default_rng(9)
    x = rng.standard_normal((16, 6))
    stats = ds.ordering_statistics(x)
    observed = np.mean([ds.von_neumann(list(row)) for row in x])
    if not math.isclose(stats[0], observed, rel_tol=1e-12) or len(stats) != 720:
        raise AssertionError((stats[0], observed))
    if ds.permutation_p(x)[1] < 2 / 720:
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

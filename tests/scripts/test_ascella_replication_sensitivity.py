"""The dependent-correlation tests of the replication sensitivity record reproduce the cocor worked example."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_replication_sensitivity as sensitivity  # noqa: E402


def test_the_tests_reproduce_the_printed_example() -> None:
    sensitivity.unit_check()
    example = sensitivity.COCOR_EXAMPLE
    if not sensitivity.williams(*example) < sensitivity.steiger(*example) < sensitivity.meng(*example) < 0:
        raise AssertionError("the example's Williams t, Steiger z and Meng z are negative and ordered as printed")


def test_equal_correlations_give_no_difference() -> None:
    for test in (sensitivity.williams, sensitivity.steiger, sensitivity.meng):
        if abs(test(0.3, 0.3, 0.5, 168)) > 1e-12:
            raise AssertionError(f"{test.__name__} must read zero for equal correlations")
    lower, upper = sensitivity.zou(0.3, 0.3, 0.5, 168)
    if not lower < 0 < upper:
        raise AssertionError("the Zou interval of a null difference spans zero")


def test_the_batched_paths_match_their_scalar_definitions() -> None:
    jobs = np.array(["a"] * 7 + ["b"] * 6)
    x = np.array([0.3, -1.2, 0.8, 2.1, -0.4, 0.0, 1.1, -0.7, 0.9, -1.5, 0.2, 1.3, -0.6])
    y = np.array([0.1, -0.9, 1.4, 1.7, -0.2, -0.5, 0.6, -1.1, 0.4, -0.8, 0.7, 0.9, -0.3])
    scalar = [
        sensitivity.correlation(
            sensitivity.base.centered(np.delete(x, i), np.delete(jobs, i)),
            sensitivity.base.centered(np.delete(y, i), np.delete(jobs, i)),
        )
        for i in range(len(y))
    ]
    if not np.allclose(sensitivity.leave_one_out(x, y, jobs), scalar, rtol=0, atol=1e-12):
        raise AssertionError("the batched leave-one-out r departs from the deletion-and-recentering definition")
    xc, yc = sensitivity.base.centered(x, jobs), sensitivity.base.centered(y, jobs)
    rolled = [
        xc[jobs == "a"] @ np.roll(yc[jobs == "a"], s_a) + xc[jobs == "b"] @ np.roll(yc[jobs == "b"], s_b)
        for s_a in range(7)
        for s_b in range(6)
    ]
    observed = sensitivity.correlation(xc, yc)
    scale = np.sqrt((xc @ xc) * (yc @ yc))
    expected = sum(value / scale >= observed - 1e-12 for value in rolled)
    null = sensitivity.shift_null(xc, yc, jobs, observed)
    if null["alignments"] != 42 or null["at_or_above"] != expected:
        raise AssertionError(f"the batched shift null departs from np.roll: {null}, expected {expected}")


def test_the_shift_null_counts_the_observed_alignment() -> None:
    jobs = np.array(["a"] * 4 + ["b"] * 4)
    x = np.array([1.0, -1.0, 2.0, -2.0, 0.5, -0.5, 1.5, -1.5])
    y = x.copy()
    observed = sensitivity.correlation(x, y)
    null = sensitivity.shift_null(x, y, jobs, observed)
    if null["alignments"] != 16 or null["at_or_above"] < 1:
        raise AssertionError(f"16 alignments, the observed one among them: {null}")

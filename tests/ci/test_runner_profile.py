"""Contract for ci/runner_profile.py: the speed factor never shrinks the per-test budget, scales it by the measured
slowdown, rejects a non-positive calibration, and a reduced profile reports the fields the job summary reads."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pytest
import runner_profile


def test_speed_factor_keeps_the_budget_without_a_calibration_or_on_a_fast_runner() -> None:
    factors = [runner_profile.speed_factor(None), runner_profile.speed_factor(""), runner_profile.speed_factor("0.4")]
    if factors != [1.0, 1.0, 1.0]:
        raise AssertionError(factors)


def test_speed_factor_scales_by_the_slowdown() -> None:
    if not math.isclose(runner_profile.speed_factor("1.1"), 2.0):
        raise AssertionError(runner_profile.speed_factor("1.1"))
    if not math.isclose(runner_profile.speed_factor("0.79", reference=0.5), 1.58):
        raise AssertionError(runner_profile.speed_factor("0.79", reference=0.5))


@pytest.mark.parametrize("bad", ["0", "-1", "nan"])
def test_speed_factor_rejects_non_positive_calibration(bad: str) -> None:
    with pytest.raises(ValueError, match="positive"):
        runner_profile.speed_factor(bad)


def test_thread_caps_match_the_suite_environment() -> None:
    """The calibration pins every pool ci/pr_checks.sh pins for the suite, VECLIB_MAXIMUM_THREADS included."""
    text = (Path(runner_profile.__file__).with_name("pr_checks.sh")).read_text(encoding="utf-8")
    pinned = {name for name in runner_profile.THREAD_CAPS if f"{name}=1" in text}
    if pinned != set(runner_profile.THREAD_CAPS) or "VECLIB_MAXIMUM_THREADS" not in pinned:
        raise AssertionError(sorted(set(runner_profile.THREAD_CAPS) - pinned))


def test_reduced_profile_reports_summary_fields_in_one_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    """A test process holds one slot, so the concurrent pass runs inline and starts no child process."""
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    result = runner_profile.profile(scale=0.01, repeats=2)
    missing = {"cpu", "calibration_median_wall", "concurrent_median_wall", "steal_fraction", "speed_factor"} - set(
        result
    )
    if missing or result["concurrent_copies"] != 1 or not float(str(result["calibration_median_wall"])) > 0:
        raise AssertionError((missing, result))


def test_concurrent_pass_maps_through_the_shared_worker_allocation(monkeypatch: pytest.MonkeyPatch) -> None:
    """The concurrent pass takes its copy count from parallel.workers() (affinity, cgroup quota, GOROROBA_WORKERS) and
    maps two workloads per slot through parallel.ordered_map; the stand-in map runs them inline."""
    calls: list[tuple[Callable[[Any], Any], int, int]] = []

    def ordered_map(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 64) -> list[Any]:
        calls.append((function, len(items), min_items))
        return [function(item) for item in items]

    monkeypatch.setattr(runner_profile.parallel, "workers", lambda: 3)
    monkeypatch.setattr(runner_profile.parallel, "ordered_map", ordered_map)
    result = runner_profile.profile(scale=0.001, repeats=1)
    if calls != [(runner_profile.workload, 6, 1)] or result["concurrent_copies"] != 3:
        raise AssertionError((calls, result))

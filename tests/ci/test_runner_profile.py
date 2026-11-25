"""Contract for ci/runner_profile.py: the speed factor never shrinks the per-test budget, scales it by the measured
slowdown, rejects a non-positive calibration, and a reduced profile reports the fields the job summary reads."""

from __future__ import annotations

import math

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


def test_reduced_profile_reports_summary_fields() -> None:
    result = runner_profile.profile(scale=0.01, repeats=2, copies=2)
    missing = {"cpu", "calibration_median_wall", "concurrent_median_wall", "steal_fraction", "speed_factor"} - set(
        result
    )
    if missing or not float(str(result["calibration_median_wall"])) > 0:
        raise AssertionError((missing, result))

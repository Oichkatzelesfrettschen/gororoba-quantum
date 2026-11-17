"""Level shifts of one circuit repeated in several batches, from binomial counts.

A circuit that appears byte for byte in three batches gives each qubit three counts of ones at three job times. Under
the null that the backend level does not move, the three fractions share one probability, and the Pearson statistic of
the three counts (2 degrees of freedom) tests that. The shift of the middle count against the linear time
interpolation of the first and last counts is the estimate of a level step between neighboring batches, with a
standard error from the pooled probability (the null variance, which stays finite when a count is 0 or the full shot
total). Ordering is by job finish time, so the middle level is the one that ran between the other two.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy import stats


@dataclass(frozen=True)
class Level:
    """Counts of ones out of shots for one job, with the job's finish time in seconds."""

    time_s: float
    ones: int
    shots: int


def pooled_probability(levels: list[Level]) -> float:
    return sum(level.ones for level in levels) / sum(level.shots for level in levels)


def homogeneity(levels: list[Level]) -> dict[str, float | int]:
    """Pearson chi-square of the levels against their pooled probability; zero when the pooled probability is 0 or 1."""
    pooled = pooled_probability(levels)
    freedom = len(levels) - 1
    if pooled in (0.0, 1.0):
        return {"chi_square": 0.0, "freedom": freedom, "p": 1.0}
    chi_square = sum(
        (level.ones - level.shots * pooled) ** 2 / (level.shots * pooled * (1.0 - pooled)) for level in levels
    )
    return {"chi_square": chi_square, "freedom": freedom, "p": float(stats.chi2.sf(chi_square, freedom))}


def probe_shift(levels: list[Level]) -> dict[str, float]:
    """Shift of the middle level against the time interpolation of the first and last, with its null standard error.

    levels holds exactly three entries; they are ordered by time here. The interpolation weight of the last level is
    (t_middle - t_first) / (t_last - t_first).
    """
    if len(levels) != 3:
        raise ValueError("probe_shift needs exactly three levels")
    first, probe, last = sorted(levels, key=lambda level: level.time_s)
    span = last.time_s - first.time_s
    if span <= 0.0:
        raise ValueError("the first and last levels share a finish time")
    weight = (probe.time_s - first.time_s) / span
    pooled = pooled_probability(levels)
    variance = pooled * (1.0 - pooled)
    p_first, p_probe, p_last = (level.ones / level.shots for level in (first, probe, last))
    interpolated = (1.0 - weight) * p_first + weight * p_last
    shift = p_probe - interpolated
    se = math.sqrt(variance * (1.0 / probe.shots + (1.0 - weight) ** 2 / first.shots + weight**2 / last.shots))
    return {
        "weight": weight,
        "level_first": p_first,
        "level_probe": p_probe,
        "level_last": p_last,
        "interpolated": interpolated,
        "shift": shift,
        "se": se,
        "z": shift / se if se > 0.0 else 0.0,
    }

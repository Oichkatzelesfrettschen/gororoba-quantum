"""The static df profile of scripts/n21_q143_beat_model.py: profile points fitted at the line-weight bound
a = 1 share one df-free likelihood, so they read as one minimum whatever the rounding of their NLLs.
"""

from __future__ import annotations

import n21_q143_beat_model as beat

WEIGHT = beat.names("static").index("a")


def row(df: float, value: float, weight: float) -> tuple[float, float, list[float]]:
    params = [0.0] * len(beat.names("static"))
    params[WEIGHT] = weight
    return df, value, params


def test_bound_weight_run_reads_as_one_minimum() -> None:
    top = beat.LINE_WEIGHT_MAX
    noise = (1e-9, -2e-9, 3e-9, 0.0, -1e-9)
    for sign in (1.0, -1.0):
        profile = [row(0.0, 5.0, 0.7), row(1.0, 4.0, 0.8)]
        profile += [row(2.0 + k, 2.0 + sign * e, top) for k, e in enumerate(noise)]
        profile += [row(7.0, 3.0, 0.6), row(8.0, 1.0, 0.6), row(9.0, 3.0, 0.6)]
        found = beat.local_minima(profile)
        if found != [8, 4]:
            raise AssertionError(f"the bound-weight run reads minima {found} under noise sign {sign}")


def test_interior_points_keep_their_own_minima() -> None:
    profile = [row(float(k), value, 0.75) for k, value in enumerate((3.0, 2.0, 2.5, 3.0, 1.0, 3.0))]
    if beat.local_minima(profile) != [4, 1]:
        raise AssertionError(f"interior points read minima {beat.local_minima(profile)}")
    if beat.local_minima([row(float(k), 1.0, beat.LINE_WEIGHT_MAX) for k in range(4)]) != [0]:
        raise AssertionError("a profile fitted at the bound everywhere reads more than one minimum")

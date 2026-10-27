"""state_prep_split's bound directions, clamp and replicate test."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts")]

import state_prep_split as split  # noqa: E402


def test_self_test_passes() -> None:
    split.self_test()


def test_interval_brackets_the_point_and_widens_with_fewer_shots() -> None:
    level = 0.01 / 8
    wide = split.interval([50, 1000, 0], [10, 1000, 0], 0.01, level)
    narrow = split.interval([500, 10000, 0], [100, 10000, 0], 0.01, level)
    point = split.history_dependent(0.05, 0.01, 0.01)
    if not (wide[0] < narrow[0] < point < narrow[1] < wide[1]):
        raise AssertionError((wide, narrow, point))

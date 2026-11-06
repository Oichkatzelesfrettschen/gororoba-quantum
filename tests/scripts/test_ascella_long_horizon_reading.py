"""Bounded fixtures for the long-horizon seed-repeat reading: the ceiling and the power replicate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_long_horizon_reading as long_horizon  # noqa: E402
import ascella_seed_repeat_reading as seed_repeat  # noqa: E402


def test_the_ceiling_at_job_02_and_job_03_samples_equals_the_seed_repeat_bound() -> None:
    """At 8,192 and 16,384 samples the generalized ceiling is the seed-repeat reading's halved-variance ceiling."""
    general = long_horizon.ceiling(8192, 16384, 56)
    fixed = seed_repeat.fixed_bound(56)
    if general["ceiling"] != pytest.approx(fixed["ceiling"], rel=1e-12):
        raise AssertionError(f"{general} differs from {fixed}")
    if general["bound"] != pytest.approx(fixed["bound"], rel=1e-12):
        raise AssertionError(f"{general} differs from {fixed}")


def test_a_power_replicate_depends_only_on_its_seed() -> None:
    """Two calls on one spawned seed read the same outcome; a fully persistent error reads persists."""
    value = json.loads((ROOT / long_horizon.LONG_REPEAT_ORDER_DRAW).read_text(encoding="utf-8"))["values"]
    seed = np.random.SeedSequence(int(value[long_horizon.POWER_INDEX])).spawn(1)[0]
    first = long_horizon.power_replicate((1.0, seed))
    if first != long_horizon.power_replicate((1.0, seed)) or first != "persists":
        raise AssertionError(f"replicate read {first}")

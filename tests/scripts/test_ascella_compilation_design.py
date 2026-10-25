"""The perturbed-compilation request's seed rule and the sizing helpers of its design record."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_coherence_request as request  # noqa: E402
import ascella_compilation_design as design  # noqa: E402


def test_compilation_job_anchors_seed_zero_and_draws_distinct_seeds() -> None:
    rows = request.entries(request.JOBS["job-02"])
    seeds, indices = request.compilation_seeds()
    if len(rows) != 64 or {row["block"] for row in rows} != {"theta2-x"} or {row["arm"] for row in rows} != {0}:
        raise AssertionError("job-02 is not 64 iterations of theta2-x-arm0")
    settings = [request.build_setting((index, row))[1] for index, row in enumerate(rows)]
    anchors = [s["compilation_seed"] for s, r in zip(settings, rows, strict=True) if "compilation_seed" not in r]
    perturbed = [r["compilation_seed"] for r in rows if "compilation_seed" in r]
    if anchors != [0] * 8 or perturbed != seeds or len(set(seeds)) != 56 or 0 in seeds:
        raise AssertionError("anchors must sit at seed 0 and the 56 perturbed seeds be distinct and nonzero")
    if [r["compilation_position"] for r in rows if "compilation_seed" not in r] != list(range(0, 64, 8)):
        raise AssertionError("the anchors leave the stride positions")
    if indices != sorted(indices):
        raise AssertionError("the draw's values are consumed in index order")


def test_retained_designs_keep_seed_zero() -> None:
    for name in ("job-00", "job-01"):
        if any("compilation_seed" in row for row in request.entries(request.JOBS[name])):
            raise AssertionError(f"{name} rows carry a compilation seed")


def test_starts_are_deterministic_points_of_the_torus() -> None:
    phases = np.zeros(126)
    first, second = design.starts(phases, 16), design.starts(phases, 16)
    if not np.array_equal(first, second) or first.min() < 0 or first.max() >= 2 * math.pi:
        raise AssertionError("starts must repeat and lie in [0, 2 pi)")
    if len({tuple(np.round(row, 9)) for row in first}) != 16:
        raise AssertionError("starts repeat a point")


@pytest.mark.parametrize("dof", [23, 55])
def test_detectable_noncentrality_reaches_the_power(dof: int) -> None:
    critical = float(stats.chi2.ppf(1 - design.ALPHA, dof))
    value = design.detectable_noncentrality(dof, critical)
    if abs(float(stats.ncx2.sf(critical, dof, value)) - design.POWER) > 1e-9:
        raise AssertionError("the bisection misses the power")


def row(family: str, perturbed: int, samples: int, power: float, ratio: float, credits: float) -> dict[str, Any]:
    return {
        "family": family,
        "perturbed": perturbed,
        "samples_per_iteration": samples,
        "r1_power": power,
        "r3_median_variance_ratio": {"x": ratio, "y": ratio},
        "credits": credits,
    }


def test_chosen_design_is_the_cheapest_that_meets_both_readings() -> None:
    rows = []
    for family in design.ORDER_ONE:
        rows.append(row(family, 24, 8192, 1.0, 2.0 if family.startswith("drive_harmonic") else 0.5, 1.016384))
        rows.append(row(family, 56, 8192, 1.0, 0.9, 1.016384))
        rows.append(row(family, 56, 16384, 1.0, 0.5, 1.032768))
    rows.append(row("static_heater_0.3", 24, 8192, 1.0, 5.0, 1.016384))
    rows.append(row("static_heater_0.3", 56, 8192, 1.0, 5.0, 1.016384))
    rows.append(row("static_heater_0.3", 56, 16384, 0.5, 5.0, 1.032768))
    chosen = design.chosen_design(rows)
    if (chosen["perturbed"], chosen["samples_per_iteration"]) != (56, 8192):
        raise AssertionError(f"chose {chosen}")
    with pytest.raises(ValueError, match="no design"):
        design.chosen_design([{**r, "r1_power": 0.0} for r in rows])

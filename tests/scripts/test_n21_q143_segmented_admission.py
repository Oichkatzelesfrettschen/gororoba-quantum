"""Admission of a returned segmented sweep in scripts/n21_q143_segmented_sweep.py: the stage reader parses a
returned Heron r2 scheduler table, a misplaced pre-idle, idle or pulse leaves its member differing, and the
herald evaluation reads every segment's reset herald through the undetected excitation it leaves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import n21_q143_segmented_sweep as sweep
import pytest

TIMING = json.loads((Path(__file__).parent / "data" / "n21_segmented_heron_timing.json").read_text())
SPECTATOR = TIMING["spectator"]
SEGMENTS = 6


def payload(timing: str) -> dict[str, Any]:
    return {"metadata": {"compilation": {"scheduler_timing": {"timing": timing}}}}


def schedule(member: str, timing: str | None = None) -> dict[str, Any]:
    stages = sweep.spectator_stages(payload(timing or TIMING["timing"][member]), SPECTATOR)
    return sweep.member_schedule(stages, SEGMENTS)


@pytest.mark.parametrize(
    ("member", "pre", "idle", "pulses"),
    [("xy_d0", 0, 0, 2), ("z_d693", 0, 693, 1), ("xy_d693_pre1250", 1250, 693, 2)],
)
def test_returned_table_reads_the_design(member: str, pre: int, idle: int, pulses: int) -> None:
    found = schedule(member)
    if found["pre_dt"] != [pre] * SEGMENTS or found["idle_dt"] != [idle] * SEGMENTS:
        raise AssertionError(found)
    if found["pulses"] != [pulses] * SEGMENTS or len(found["gaps_dt"]) != SEGMENTS - 1:
        raise AssertionError(found)


def test_neighbor_rows_stay_out_of_the_spectator() -> None:
    rows = TIMING["timing"]["z_d693"].splitlines()
    alone = "\n".join(row for row in rows if row.split(",")[2] == f"Qubit {SPECTATOR}")
    if schedule("z_d693") != schedule("z_d693", alone):
        raise AssertionError("a neighbor's rows changed the spectator's schedule")


def shifted(member: str, after: int, by: int) -> str:
    """The member's table with every spectator row at or after the time after moved by by dt."""
    rows = []
    for row in TIMING["timing"][member].splitlines():
        fields = row.split(",")
        if fields[2] == f"Qubit {SPECTATOR}" and int(fields[3]) >= after:
            fields[3] = str(int(fields[3]) + by)
        rows.append(",".join(fields))
    return "\n".join(rows)


def test_misplaced_pre_idle_is_found() -> None:
    # The pre-idle stage of segment 1 ends at the preparation's barrier, 3314 dt.
    found = schedule("xy_d693_pre1250", shifted("xy_d693_pre1250", 3314, 8))
    if found["pre_dt"][0] != 1258 or found["idle_dt"] != [693] * SEGMENTS:
        raise AssertionError(found)


def test_lengthened_idle_is_found() -> None:
    # The Ramsey idle of segment 1 ends at the basis change's barrier, 2766 dt.
    found = schedule("z_d693", shifted("z_d693", 2766, 4))
    if found["idle_dt"][0] != 697 or found["idle_dt"][1:] != [693] * (SEGMENTS - 1):
        raise AssertionError(found)


def test_missing_preparation_raises() -> None:
    timing = "\n".join(
        row
        for row in TIMING["timing"]["z_d693"].splitlines()
        if not (row.split(",")[2] == f"Qubit {SPECTATOR}" and row.split(",")[1].startswith("x_"))
    )
    with pytest.raises(ValueError, match="no preparation"):
        schedule("z_d693", timing)


def calibrations(members: list[str], p01: float = 0.01) -> dict[str, dict[str, Any]]:
    values = {str(q): {"prob_meas1_prep0": 0.002, "prob_meas0_prep1": p01} for q in (46, 47)}
    return {name: {"values": values, "source": "plan"} for name in members}


def counts(rates: dict[str, float], shots: int = 1200) -> dict[int, dict[str, Any]]:
    """Neighbor 46 and spectator 47 in segment 1, then the spectator's reset herald of segments 2 to 6."""
    flat = {name: (round(0.001 * shots), shots) for name in rates}
    found: dict[int, dict[str, Any]] = {
        0: {"qubit": 46, "segment": 1, "members": dict(flat)},
        1: {"qubit": SPECTATOR, "segment": 1, "members": dict(flat)},
    }
    for s in range(2, SEGMENTS + 1):
        members = {name: (round(rate * shots), shots) for name, rate in rates.items()}
        found[s] = {"qubit": SPECTATOR, "segment": s, "members": members}
    return found


def test_reset_heralds_admit_a_design_spread() -> None:
    # Z members hold the spectator near 1 before each reset, so their reset
    # leaves about twice the excitation of an X/Y member's.
    # At 20000 shots that excitation spread itself is resolved above the
    # bound; the p01 = 0.01 it passes undetected is not.
    rates = {"xy_a": 0.010, "xy_b": 0.011, "z_a": 0.020, "z_b": 0.021}
    herald = sweep.herald_evaluation(counts(rates, 20000), calibrations(list(rates)), 0.05 / len(sweep.TESTS))
    if not herald["evaluable"] or not herald["admissible"] or len(herald["bits"]) != SEGMENTS + 1:
        raise AssertionError(herald)
    reset = herald["bits"]["2"]
    if reset["spread_lower_limit"] <= herald["excitation_spread_bound"] * reset["readout_contrast"]:
        raise AssertionError(reset)


def test_undetected_spread_refuses() -> None:
    # p01 = 0.5 lets half of every excitation through its herald.
    rates = {"xy_a": 0.010, "z_a": 0.060}
    herald = sweep.herald_evaluation(counts(rates), calibrations(list(rates), 0.5), 0.05 / len(sweep.TESTS))
    if herald["admissible"] or herald["bits"]["2"]["status"] != "fail":
        raise AssertionError(herald)

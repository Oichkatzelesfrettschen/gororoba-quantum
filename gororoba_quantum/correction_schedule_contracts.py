"""Offline rejection contracts for the exposed correction schedule schema."""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from functools import partial
from typing import Any

from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeKingston

from correction_circuits import (
    CORRECTION_ARMS,
    bind_correction_template,
    correction_template,
    validate_correction_pair,
)
from correction_schedule import parse_timing, qualify_pair


def _reject(action: Callable[[], Any], label: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise RuntimeError(f"schedule validator accepted {label}")


def _fixture(report: dict[str, Any], *, else_present: bool = True) -> dict[str, Any]:
    """Make synthetic event metadata, without claiming native scheduling evidence."""
    first = report["measurement_writers"][0][1]
    terminal = report["measurement_writers"][1][1]
    rows = [
        f"main,sx_{first},Qubit {first},0,4,play",
        f"main,measure_{first},Qubit {first},10,4,play",
        f"main,measure_{first},AWGR1_{first},14,6,capture",
        "main,broadcast,Hub,14,8,broadcast",
        "main,receive,Receive,22,2,receive",
        f"main,reset_{first},Qubit {first},24,4,play",
        f"main,reset_{first},AWGR1_{first},28,6,capture",
        f"main,reset_{first},Qubit {first},34,2,play",
        f"main,sx_{first},Qubit {first},36,4,play",
        f"then,rz_{terminal},Qubit {terminal},40,0,shift_phase",
        f"main,sx_{terminal},Qubit {terminal},42,4,play",
        f"main,measure_{terminal},Qubit {terminal},46,4,play",
        f"main,measure_{terminal},AWGR1_{terminal},50,6,capture",
        f"main,barrier,Qubit {terminal},60,0,barrier",
    ]
    if else_present:
        rows.append(f"else,rz_{terminal},Qubit {terminal},40,0,shift_phase")
    return {"circuit_duration": 60, "timing": "\n".join(rows) + "\n"}


def verify() -> dict[str, Any]:
    """Exercise real circuit reports against synthetic table fixtures and mutations."""
    routed = transpile(
        correction_template(),
        backend=FakeKingston(),
        initial_layout=[95, 79, 93, 92, 94],
        optimization_level=3,
        seed_transpiler=20261010,
    )
    accepted = 0
    rejected = 0
    for label in (1, 3):
        arms = [bind_correction_template(routed, label, arm) for arm in CORRECTION_ARMS]
        report = validate_correction_pair(routed, arms[0], arms[1], label)
        feedback, independent = _fixture(report), _fixture(report)
        original = copy.deepcopy((feedback, independent, report))

        def qualify(
            feedback_value: dict[str, Any] | None = None,
            independent_value: dict[str, Any] | None = None,
            report_value: dict[str, Any] | None = None,
            dt: float = 4e-9,
            feedback: dict[str, Any] = feedback,
            independent: dict[str, Any] = independent,
            report: dict[str, Any] = report,
        ) -> dict[str, Any]:
            return qualify_pair(
                feedback if feedback_value is None else feedback_value,
                independent if independent_value is None else independent_value,
                dt_seconds=dt,
                circuit_pair_report=report if report_value is None else report_value,
            )

        success = qualify()
        if not success["qualified"] or success["feedback_zero_phase_else_elided"]:
            raise RuntimeError("equal explicit branch schedule failed")
        json.dumps(success, allow_nan=False)
        elided = qualify(feedback_value=_fixture(report, else_present=False))
        if not elided["feedback_zero_phase_else_elided"]:
            raise RuntimeError("declared zero-phase elision was lost")
        accepted += 2
        _reject(partial(qualify, independent_value=_fixture(report, else_present=False)), "missing U else")
        rejected += 1
        forbid_elision = dict(report, scheduler_zero_phase_else_elision_allowed=False)
        _reject(
            partial(qualify, feedback_value=_fixture(report, else_present=False), report_value=forbid_elision),
            "undeclared feedback else elision",
        )
        rejected += 1
        mutations = {
            "equal-duration internal timing": independent["timing"].replace(",42,4,play", ",43,4,play"),
            "changed correction slot": independent["timing"].replace(",40,0,shift_phase", ",41,0,shift_phase"),
            "duplicate dispatch": independent["timing"] + "main,broadcast,Hub,14,8,broadcast\n",
            "duplicate receive": independent["timing"] + "main,receive,Receive,22,2,receive\n",
            "missing reset": "\n".join(row for row in independent["timing"].splitlines() if ",reset_" not in row),
            "missing measurement": "\n".join(
                row for row in independent["timing"].splitlines() if ",measure_" not in row
            ),
            "missing then": "\n".join(row for row in independent["timing"].splitlines() if not row.startswith("then,")),
            "extra correction": independent["timing"] + independent["timing"].splitlines()[-1] + "\n",
            "changed measurement writer": independent["timing"].replace(",measure_", ",measure_999"),
            "changed reset writer": independent["timing"].replace(",reset_", ",reset_999"),
            "unknown branch": independent["timing"].replace("else,", "other,"),
            "unknown pulse": independent["timing"].replace("shift_phase", "unknown"),
            "negative start": independent["timing"].replace(",40,0,", ",-1,0,"),
            "fractional start": independent["timing"].replace(",40,0,", ",40.5,0,"),
            "positive phase duration": independent["timing"].replace(",40,0,", ",40,1,"),
            "extra CSV column": independent["timing"] + "main,x,Qubit 1,0,1,play,extra\n",
            "missing CSV column": "main,x,Qubit 1,0,1\n",
            "malformed CSV quoting": 'main,"unterminated\n',
            "empty timing": "",
        }
        for name, text in mutations.items():
            malformed = dict(independent, timing=text)
            _reject(partial(qualify, independent_value=malformed), name)
            rejected += 1
        for duration in (True, 60.0, "60", 0, -1, 39, 61):
            malformed = dict(independent, circuit_duration=duration)
            _reject(partial(qualify, independent_value=malformed), "invalid or mismatched duration")
            rejected += 1
        for dt in (0, -1, float("nan"), float("inf"), True):
            _reject(partial(qualify, dt=dt), "invalid dt")
            rejected += 1
        report_mutations = {
            "missing circuit validation": dict(report, validation="unverified"),
            "changed protected circuit": dict(report, protected_history_equal=False),
            "missing dispatch": dict(report, classical_dispatch_retained=False),
            "source phase operation": dict(report, correction_operation="p"),
            "wrong condition": dict(report, dispatch_condition={"classical_bit": 1, "equals": 1}),
            "missing digest": dict(report, feedback_history_sha256=None),
            "malformed writer": dict(report, measurement_writers=[[0, True, 0], [5, 1, 1]]),
            "missing elision policy": dict(report, scheduler_zero_phase_else_elision_allowed=None),
        }
        changed_angles = copy.deepcopy(report)
        changed_angles["correction_branch_angles"]["recorded_bit_independent"]["else"] = 0.0
        report_mutations["changed independent phase"] = changed_angles
        for name, malformed_report in report_mutations.items():
            _reject(partial(qualify, report_value=malformed_report), name)
            rejected += 1
        # Corrupt both arms identically so cross-arm equality cannot conceal missing required history.
        for text in (mutations["missing reset"], mutations["missing measurement"], mutations["duplicate dispatch"]):
            malformed = dict(independent, timing=text)
            _reject(partial(qualify, malformed, malformed), "matching but incomplete histories")
            rejected += 1
        _reject(partial(parse_timing, dict(independent, unknown=True)), "unknown scheduler schema")
        rejected += 1
        if (feedback, independent, report) != original:
            raise RuntimeError("schedule qualification mutated its inputs")
    return {
        "accepted_synthetic_cases": accepted,
        "rejected_mutations": rejected,
        "native_schedule_qualification": False,
        "scope": "offline validator behavior with real circuit reports and synthetic scheduler metadata",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

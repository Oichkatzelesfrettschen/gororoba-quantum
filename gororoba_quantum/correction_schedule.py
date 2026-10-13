"""Compare exposed native scheduler events for one folded-correction pair.

Runtime 0.50 returns ``{circuit_duration: int, timing: str}``, with CSV rows
``Branch,Instruction,Channel,T0,Duration,Pulse`` and integer times in backend
dt. The supported branches are main/then/else and the pilot has one dispatch.
The QPY-derived ``validate_correction_pair`` report supplies phase values,
classical operands, physical writers and protected circuit histories; the CSV
omits those phase values and classical operands. The caller must associate
the report and schedules with the same archived circuits and calibration.

Qualification covers the emitted event table and validated circuit artifacts.
It cannot establish undisclosed controller operations, pulse amplitudes,
per-shot timing, microscopic equality, or equality of physical noise.
Missing evidence and unrecognized schemas raise ValueError. The comparison
allows only the explicitly declared elision of the feedback arm's zero phase
else event, which has zero duration. Both independent-arm branches must remain.

Schema sources are qiskit_ibm_runtime.results.quantum_program.SchedulerTiming
and qiskit_ibm_runtime.visualization.circuit_schedule.CircuitSchedule.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, cast


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True, order=True)
class ScheduleEvent:
    branch: str
    instruction: str
    channel: str
    start: int
    duration: int
    pulse: str

    @property
    def end(self) -> int:
        return self.start + self.duration

    def row(self) -> tuple[str, str, str, int, int, str]:
        return (self.branch, self.instruction, self.channel, self.start, self.duration, self.pulse)


def parse_timing(timing: dict[str, Any]) -> tuple[int, tuple[ScheduleEvent, ...]]:
    """Read the unfiltered six-column native table, preserving repeated events."""
    _require(isinstance(timing, dict), "scheduler timing must be a dictionary")
    _require(set(timing) == {"circuit_duration", "timing"}, "unsupported scheduler timing fields")
    duration = timing["circuit_duration"]
    _require(type(duration) is int and duration > 0, "circuit duration must be a positive integer in dt")
    table = timing["timing"]
    _require(isinstance(table, str) and bool(table.strip()), "scheduler timing CSV is missing")
    events: list[ScheduleEvent] = []
    try:
        for row in csv.reader(io.StringIO(table), strict=True):
            _require(len(row) == 6, "scheduler CSV requires six columns per row")
            branch, instruction, channel, start_text, duration_text, pulse = row
            _require(branch in {"main", "then", "else"}, "unsupported scheduler branch")
            _require(bool(instruction) and bool(channel), "scheduler instruction and channel must be named")
            _require(
                re.fullmatch(r"[0-9]+", start_text) is not None and re.fullmatch(r"[0-9]+", duration_text) is not None,
                "scheduler event times must be nonnegative integers in dt",
            )
            _require(
                pulse in {"barrier", "play", "capture", "shift_phase", "broadcast", "receive"},
                "unsupported scheduler pulse kind",
            )
            event = ScheduleEvent(branch, instruction, channel, int(start_text), int(duration_text), pulse)
            _require(event.end <= duration, "scheduler event exceeds circuit duration")
            _require(
                (event.duration == 0) == (pulse in {"barrier", "shift_phase"}),
                "scheduler event has an invalid duration for its pulse kind",
            )
            events.append(event)
    except csv.Error as error:
        raise ValueError("malformed scheduler CSV") from error
    _require(bool(events), "scheduler timing CSV has zero events")
    return duration, tuple(events)


def _integer_rows(value: Any, lengths: list[int], label: str) -> list[list[int]]:
    _require(isinstance(value, list) and len(value) == len(lengths), f"invalid {label}")
    for row, length in zip(value, lengths, strict=True):
        _require(
            isinstance(row, list) and len(row) == length and all(type(item) is int and item >= 0 for item in row),
            f"invalid {label} row",
        )
    return value


def _pair_identity(report: dict[str, Any]) -> tuple[int, int, int, bool]:
    """Require the validated circuit report; raw QPY verification belongs to its producer."""
    _require(isinstance(report, dict), "circuit pair report must be a dictionary")
    _require(
        report.get("validation")
        in {
            "exact_common_template_history_and_ideal_law",
            "exact_bound_pair_history_and_ideal_law",
        },
        "circuit pair requires exact template or bound-pair validation",
    )
    _require(type(report.get("phase_label")) is int and report["phase_label"] in (1, 3), "unsupported eigenlabel")
    _require(report.get("protected_history_equal") is True, "protected circuit history is unqualified")
    _require(report.get("classical_dispatch_retained") is True, "classical dispatch is unqualified")
    writers = _integer_rows(report.get("measurement_writers"), [3, 3], "measurement writers")
    resets = _integer_rows(report.get("reset_instructions"), [2], "reset instructions")
    correction_index = report.get("correction_instruction_index")
    correction_qubit = report.get("correction_physical_qubit")
    _require(type(correction_index) is int and type(correction_qubit) is int, "invalid correction identity")
    correction_index = cast(int, correction_index)
    correction_qubit = cast(int, correction_qubit)
    _require(
        [entry[2] for entry in writers] == [0, 1]
        and writers[0][0] < resets[0][0] < correction_index < writers[1][0]
        and resets[0][1] == writers[0][1]
        and correction_qubit == writers[1][1],
        "circuit report changed measurement/reset/dispatch history",
    )
    _require(report.get("correction_operation") == "rz", "native correction must use the validated rz operation")
    condition = report.get("dispatch_condition")
    _require(
        isinstance(condition, dict)
        and set(condition) == {"classical_bit", "equals"}
        and type(condition["classical_bit"]) is int
        and condition["classical_bit"] == 0
        and type(condition["equals"]) is int
        and condition["equals"] == 1,
        "dispatch condition differs from first measured bit equaling one",
    )
    expected_angles = {
        "measured_feedback": {"then": -math.pi / 2, "else": 0.0},
        "recorded_bit_independent": {"then": -math.pi / 2, "else": -math.pi / 2},
    }
    angles = report.get("correction_branch_angles")
    _require(isinstance(angles, dict) and set(angles) == set(expected_angles), "correction angles are missing")
    angles = cast(dict[str, Any], angles)
    for arm, expected in expected_angles.items():
        actual = angles[arm]
        _require(isinstance(actual, dict) and set(actual) == set(expected), "correction branch angles are missing")
        for branch, expected_angle in expected.items():
            angle = actual[branch]
            _require(
                isinstance(angle, (int, float))
                and not isinstance(angle, bool)
                and math.isfinite(angle)
                and math.isclose(angle, expected_angle, rel_tol=0, abs_tol=1e-12),
                "correction phase differs from the finite odd-label contract",
            )
    for key in (
        "prefix_sha256",
        "suffix_sha256",
        "feedback_history_sha256",
        "independent_history_sha256",
    ):
        _require(
            isinstance(report.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", report[key]) is not None,
            f"missing circuit report digest: {key}",
        )
    elision = report.get("scheduler_zero_phase_else_elision_allowed")
    _require(type(elision) is bool, "feedback zero-phase elision policy must be explicit")
    return writers[0][1], writers[1][1], correction_qubit, cast(bool, elision)


def _branch_events(
    events: tuple[ScheduleEvent, ...], correction_qubit: int, *, independent: bool, allow_elision: bool
) -> tuple[ScheduleEvent, bool, dict[str, int | None]]:
    correction_events = [event for event in events if event.branch != "main"]
    counts = Counter(event.branch for event in correction_events)
    _require(counts["then"] == 1, "one explicit then correction event is required")
    if independent or not allow_elision:
        _require(counts["else"] == 1, "one explicit else correction event is required")
    else:
        _require(counts["else"] in (0, 1), "feedback else correction event is duplicated")
    for event in correction_events:
        _require(
            event.instruction == f"rz_{correction_qubit}"
            and event.channel == f"Qubit {correction_qubit}"
            and event.duration == 0
            and event.pulse == "shift_phase",
            "branch contains an unexpected correction event",
        )
    # shift_phase is a zero-duration frame update that takes effect at the next
    # pulse on its channel; the controller places the else update a few dt
    # after the then update, so the branches agree when no pulse on the
    # correction channel lies between them.
    first, last = min(event.start for event in correction_events), max(event.start for event in correction_events)
    channel = f"Qubit {correction_qubit}"
    _require(
        not any(
            event.branch == "main"
            and event.channel == channel
            and event.duration > 0
            and event.start < last
            and event.end > first
            for event in events
        ),
        "a pulse on the correction channel separates the then and else frame updates",
    )
    receives = [event for event in events if event.branch == "main" and event.instruction == "receive"]
    _require(bool(receives), "dispatch receive is missing")
    # Each branch's condition exists only after the receive completes.
    _require(
        all(event.start >= max(receive.end for receive in receives) for event in correction_events),
        "a branch frame update precedes dispatch completion",
    )
    starts: dict[str, int | None] = {
        branch: next((event.start for event in correction_events if event.branch == branch), None)
        for branch in ("then", "else")
    }
    return next(event for event in correction_events if event.branch == "then"), counts["else"] == 0, starts


def _event_history(events: tuple[ScheduleEvent, ...], first_writer: int, terminal_writer: int, correction: int) -> None:
    main = [event for event in events if event.branch == "main"]
    broadcasts = [event for event in main if event.instruction == "broadcast" or event.pulse == "broadcast"]
    receives = [event for event in main if event.instruction == "receive" or event.pulse == "receive"]
    _require(len(broadcasts) == len(receives) == 1, "one broadcast/receive dispatch is required")
    broadcast, receive = broadcasts[0], receives[0]
    _require(broadcast.instruction == broadcast.pulse == "broadcast", "invalid broadcast identity")
    _require(receive.instruction == receive.pulse == "receive", "invalid receive identity")
    _require(broadcast.end <= receive.start and receive.end <= correction, "invalid dispatch timing order")
    measures = [event for event in main if event.instruction.startswith("measure_")]
    _require(
        {event.instruction for event in measures} == {f"measure_{first_writer}", f"measure_{terminal_writer}"},
        "measurement writer history differs from the circuit report",
    )
    captures = sorted((event for event in measures if event.pulse == "capture"), key=lambda event: event.start)
    _require(len(captures) == 2, "exactly two measurement captures are required")
    first, terminal = captures
    _require(
        first.instruction == f"measure_{first_writer}" and terminal.instruction == f"measure_{terminal_writer}",
        "measurement captures changed their ordered writers",
    )
    _require(first.start <= broadcast.start and first.end <= receive.end, "dispatch precedes first measurement")
    _require(terminal.start >= correction, "terminal capture precedes correction")
    resets = [event for event in main if event.instruction.startswith("reset_")]
    _require(
        bool(resets) and {event.instruction for event in resets} == {f"reset_{first_writer}"},
        "reset event history differs from the first writer",
    )
    _require(any(event.pulse == "capture" for event in resets), "reset capture is missing")
    _require(any(event.pulse == "play" for event in resets), "reset drive history is missing")
    _require(
        first.end <= min(event.start for event in resets) and max(event.end for event in resets) <= correction,
        "reset history falls outside first measurement and correction",
    )
    _require(
        any(event.pulse == "play" and event.start < correction for event in measures),
        "first measurement drive history is missing",
    )
    _require(
        any(event.pulse == "play" and event.start >= correction for event in measures),
        "terminal measurement drive history is missing",
    )


def qualify_pair(
    feedback_timing: dict[str, Any],
    unconditional_timing: dict[str, Any],
    *,
    dt_seconds: float,
    circuit_pair_report: dict[str, Any],
) -> dict[str, Any]:
    """Qualify exposed F/U event equality for one independently validated odd label.

    The caller binds raw metadata and the circuit report to exact archived QPY,
    backend, calibration, options and PUB order. The returned digest identifies
    the complete report supplied by that caller. A successful synthetic test
    establishes the validator's behavior; it does not qualify a native run.
    """
    _require(
        isinstance(dt_seconds, (int, float))
        and not isinstance(dt_seconds, bool)
        and math.isfinite(dt_seconds)
        and dt_seconds > 0,
        "backend dt must be finite and positive",
    )
    first_writer, terminal_writer, correction_qubit, allow_elision = _pair_identity(circuit_pair_report)
    feedback_duration, feedback = parse_timing(feedback_timing)
    independent_duration, independent = parse_timing(unconditional_timing)
    feedback_correction, feedback_elided, feedback_starts = _branch_events(
        feedback, correction_qubit, independent=False, allow_elision=allow_elision
    )
    independent_correction, _, independent_starts = _branch_events(
        independent, correction_qubit, independent=True, allow_elision=False
    )
    _require(feedback_duration == independent_duration, "pair circuit durations differ")
    _require(feedback_correction == independent_correction, "pair then correction events differ")
    for events in (feedback, independent):
        _event_history(events, first_writer, terminal_writer, feedback_correction.start)
    protected_feedback = sorted(event for event in feedback if event.branch == "main")
    protected_independent = sorted(event for event in independent if event.branch == "main")
    _require(protected_feedback == protected_independent, "protected event histories or internal times differ")
    return {
        "schema": "folded-correction-exposed-schedule-pair-v2",
        "qualified": True,
        "evidence_scope": (
            "exposed native event CSV and validated circuit pair; undisclosed controller behavior excluded"
        ),
        "phase_label": circuit_pair_report["phase_label"],
        "circuit_pair_report_sha256": _sha256(circuit_pair_report),
        "feedback_timing_sha256": _sha256(feedback_timing),
        "independent_timing_sha256": _sha256(unconditional_timing),
        "protected_events_sha256": _sha256([event.row() for event in protected_feedback]),
        "protected_event_count": len(protected_feedback),
        "circuit_duration_dt": feedback_duration,
        "dt_seconds": float(dt_seconds),
        "circuit_duration_seconds": feedback_duration * dt_seconds,
        "correction_start_dt": feedback_correction.start,
        "correction_branch_start_dt": {"feedback": feedback_starts, "independent": independent_starts},
        "feedback_zero_phase_else_elided": feedback_elided,
        "phase_value_evidence": "validated circuit pair; scheduler CSV omits phase values",
        "per_shot_timing_certified": False,
        "undisclosed_controller_behavior_certified": False,
    }

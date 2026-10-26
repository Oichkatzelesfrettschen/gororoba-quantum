"""Contracts of the idle-penalty analyzer on synthetic records: role identity, collector refusals and decisions."""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any

import idle_penalty_report as report
import numpy as np
import pytest

import idle_penalty as ip

SKELETON_VIOLATIONS = report.skeleton_violations

DT = 4e-9
P1_GROUND, P1_EXCITED = 0.01, 0.98
# Replica 0 holds T on the lower qubit; replica 1 holds T on the higher qubit, which the sorted
# ownership list reverses.
LAYOUTS = [(10, 11), (21, 20), (40, 41)]
T1_US, T2_US = 200.0, 150.0


def _kappa(qubit: int) -> float:
    """The planted relaxation multiplier: 2 on every qubit behind clbit 0, 1 behind clbit 1."""
    return 2.0 if any(layout[0] == qubit for layout in LAYOUTS) else 1.0


def _law(p1: tuple[float, float]) -> list[float]:
    return [(1 - p1[0]) * (1 - p1[1]), p1[0] * (1 - p1[1]), (1 - p1[0]) * p1[1], p1[0] * p1[1]]


def _probe_p1(member: str, probe: int, qubit: int) -> float:
    """P1 of the probe in a Ramsey-type member: x reads (1 - c V) / 2, y reads 1 / 2, at zero phase."""
    contrast = 1 - P1_GROUND - (1 - P1_EXCITED)
    offset = (1 - P1_EXCITED) - P1_GROUND
    if member.split("_")[-1] == "y" or "_y_" in member:
        z = offset
    else:
        delay = next((d for d in ip.RAMSEY_DT if member.endswith(f"_{d}dt")), ip.MEAS_DT)
        if "meas_short" in member:
            delay = ip.SHORT_MEAS_DT
        z = contrast * math.exp(-delay * DT / (T2_US * 1e-6)) + offset
    return (1 - z) / 2


def _member_law(name: str, layout: tuple[int, int]) -> list[float]:
    if name == "idle_ground":
        return _law((P1_GROUND, P1_GROUND))
    if name in ("idle_excited", "idle_cz_kick"):
        return _law((P1_EXCITED, P1_EXCITED))
    if name.startswith("idle_relax_"):
        delay = int(name.removeprefix("idle_relax_").removesuffix("dt"))
        p1 = [P1_GROUND + (P1_EXCITED - P1_GROUND) * math.exp(-_kappa(q) * delay * DT / (T1_US * 1e-6)) for q in layout]
        return _law((p1[0], p1[1]))
    probe = ip.SPECTATOR if name.startswith("idle_s_") else ip.TARGET
    partner = P1_EXCITED if name.startswith("idle_zz_") else P1_GROUND
    p1 = [0.0, 0.0]
    p1[probe] = _probe_p1(name, probe, layout[probe])
    p1[1 - probe] = partner
    return _law((p1[0], p1[1]))


READ_DT, READ_GAP_DT = 300, 20


def _schedule(name: str, fault: str = "") -> str:
    """Service-schedule rows for one member on every replica; `fault` alters replica 1 only.

    Probed roles play an equator pulse, then one pulse after each planned idle, then the final read. A readout arm's
    reader plays its train inside the probe idle (during, short) or after the joint final read (after). Faults:
    "stretch" lengthens each probe idle by 16 dt, "drop" removes one train read, "shift" starts the train 100 dt
    before the probe's equator pulse ends (during, short) or moves the reader's joint read and train 600 dt ahead of
    the probe's final read (after).
    """
    planned = report.planned_idles(name)
    train = report.reader_train(name)
    probe = next(iter(planned), None)
    rows = []
    for k, layout in enumerate(LAYOUTS):
        fault_here = fault if k == 1 else ""
        gaps = [gap + (16 if fault_here == "stretch" else 0) for gap in max(planned.values(), default=[])]
        final = 108 + sum(gaps) + 8 * len(gaps) if gaps else 100
        for role, qubit in enumerate(layout):
            rows.append(f"main,reset_{qubit},Qubit {qubit},0,100,play")
            t = 100
            if role in planned:
                rows.append(f"main,sx_{qubit},Qubit {qubit},{t},8,play")
                for gap in gaps:
                    t += 8 + gap
                    rows.append(f"main,sx_{qubit},Qubit {qubit},{t},8,play")
            reads, offset = [], 0
            if train is not None and role != probe:
                count, inside = train
                offset = {"shift": -100 if inside else -600}.get(fault_here, 0)
                first = 118 if inside else final + READ_DT + READ_GAP_DT
                reads = [first + offset + j * (READ_DT + READ_GAP_DT) for j in range(count - (fault_here == "drop"))]
                offset = 0 if inside else offset
            for t0 in sorted([*reads, final + offset]):
                rows.append(f"main,measure_{qubit},Qubit {qubit},{t0},{READ_DT},play")
    return "\n".join(rows)


def _write_run(
    directory: Path, *, measured: bool, mutate: Any = None, calibration: str = "c1", fault: tuple[str, str] = ("", "")
) -> Path:
    names = [name for name, _, _ in ip.idle_penalty_circuits()]
    group: dict[str, Any] = {
        "group": "idle_penalty",
        "backend": "ibm_kingston",
        "calibration": calibration,
        "placed_qubit_calibration": {str(q): {"T1": T1_US, "T2": T2_US} for lay in LAYOUTS for q in lay},
        "replicas": [{"initial_layout": list(layout)} for layout in LAYOUTS],
        "members": [
            {
                "name": name,
                "reference": False,
                "replica_qubits": [sorted(layout) for layout in LAYOUTS],
                "replicas": [{"noisy": _member_law(name, layout)} for layout in LAYOUTS],
            }
            for name in names
        ],
    }
    record = {"experiment_digest": "e", "shots": 8192, "policy": {"rep_delay_seconds": 2e-5}, "groups": [group]}
    directory.mkdir(parents=True)
    (directory / "record.json").write_text(json.dumps(record))
    if measured:
        raw = directory / "raw" / "job"
        raw.mkdir(parents=True)
        for index, name in enumerate(names):
            timing = {"timing": _schedule(name, fault[1] if name == fault[0] else "")}
            payload = {"pub_name": f"pub_{name}", "metadata": {"compilation": {"scheduler_timing": timing}}}
            (raw / f"pub_{index:02d}.json").write_text(json.dumps(payload))
        executed = {
            name: {
                "pub": f"pub_{name}",
                "calibration": calibration,
                "calibration_changed_during_shots": False,
                "placed_qubit_calibration": group["placed_qubit_calibration"],
            }
            for name in names
        }
        measured_laws = {name: [_member_law(name, layout) for layout in LAYOUTS] for name in names}
        block: dict[str, Any] = {"group": "idle_penalty", "executed": executed, "measured": measured_laws}
        if mutate is not None:
            mutate(block)
        (directory / "collect.json").write_text(json.dumps([{"jobs": {}}, block]))
    return directory


@pytest.fixture(autouse=True)
def _no_compiled_circuits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Synthetic runs carry no isa.qpy; the compiled-instruction check has its own test below."""
    monkeypatch.setattr(report, "skeleton_violations", lambda run, record, names: [])


def test_roles_follow_the_initial_layout_not_the_sorted_ownership(tmp_path: Path) -> None:
    result = report.report(_write_run(tmp_path / "run", measured=True), predicted=False)
    for layout in LAYOUTS:
        target, spectator = (result["qubits"][str(q)] for q in layout)
        if target["role"] != "target" or spectator["role"] != "spectator":
            raise AssertionError(f"{layout}: roles {target['role']}, {spectator['role']}")
        if abs(target["kappa_1"] - 2.0) > 0.02 or abs(spectator["kappa_1"] - 1.0) > 0.02:
            raise AssertionError(f"{layout}: kappa_1 {target['kappa_1']}, {spectator['kappa_1']} misattributed")
        if abs(target["kappa_2star"] - 1.0) > 0.02:
            raise AssertionError(f"{layout}: kappa_2star {target['kappa_2star']}")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda b: b.__setitem__("comparisons_withheld", "split calibrations"),
        lambda b: b.__setitem__("summary_unavailable", "missing"),
        lambda b: b["executed"]["idle_ground"].__setitem__("calibration", None),
        lambda b: b["executed"]["idle_ground"].__setitem__("calibration_changed_during_shots", True),
        lambda b: b["executed"]["idle_ground"].__setitem__("calibration", "c2"),
        lambda b: b["measured"].pop("idle_echo_x_2500dt"),
    ],
    ids=["withheld", "unavailable", "unwindowed", "straddling", "split", "missing"],
)
def test_collected_comparisons_the_collector_withholds_are_refused(tmp_path: Path, mutation: Any) -> None:
    run = _write_run(tmp_path / "run", measured=True, mutate=mutation)
    with pytest.raises(report.RefusedAnalysis):
        report.report(run, predicted=False)


@pytest.mark.parametrize(
    ("member", "fault", "reason"),
    [
        ("idle_meas_during_x", "stretch", "idles"),
        ("idle_s_echo_y_10000dt", "stretch", "idles"),
        ("idle_relax_2500dt", "stretch", "idles"),
        ("idle_meas_during_y", "drop", "reader reads"),
        ("idle_s_meas_after_x", "drop", "reader reads"),
        ("idle_meas_short_x", "drop", "reader reads"),
        ("idle_s_meas_during_x", "shift", "leaves the probe idle"),
        ("idle_meas_short_y", "shift", "leaves the probe idle"),
        ("idle_meas_after_x", "shift", "before the probe's final read"),
    ],
)
def test_a_scheduled_exposure_off_plan_on_one_replica_is_refused(
    tmp_path: Path, member: str, fault: str, reason: str
) -> None:
    run = _write_run(tmp_path / "run", measured=True, fault=(member, fault))
    with pytest.raises(report.RefusedAnalysis, match=reason):
        report.report(run, predicted=False)


def test_compiled_instructions_must_match_the_scheduled_instances(tmp_path: Path) -> None:
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy

    register = ClassicalRegister(2, "g0_r0_c")
    fused = QuantumCircuit(QuantumRegister(2, "q"), register, name="pub_m")
    fused.reset([0, 1])
    fused.sx(0)
    fused.delay(100, 0, unit="dt")
    fused.sx(0)
    fused.measure([0, 1], [0, 1])
    rows = [
        "main,reset_0,Qubit 0,0,100,play",
        "main,reset_1,Qubit 1,0,100,play",
        "main,sx_0,Qubit 0,100,8,play",
        "main,sx_0,Qubit 0,208,8,play",
        "main,measure_0,Qubit 0,216,300,play",
        "main,measure_1,Qubit 1,216,300,play",
    ]
    record = {
        "groups": [{"group": "idle_penalty", "replicas": [{"physical_qubits": [0, 1]}]}],
        "execution_pubs": [
            {
                "name": "pub_m",
                "components": [
                    {"group": "idle_penalty", "member": "m", "reference": False, "registers_by_replica": [["g0_r0_c"]]}
                ],
            }
        ],
    }
    (tmp_path / "raw" / "job").mkdir(parents=True)
    with (tmp_path / "isa.qpy").open("wb") as stream:
        qpy.dump(fused, stream)
    for label, schedule in (("clean", rows), ("extra", [*rows, "main,measure_1,Qubit 1,600,300,play"])):
        payload = {
            "pub_name": "pub_m",
            "metadata": {"compilation": {"scheduler_timing": {"timing": "\n".join(schedule)}}},
        }
        (tmp_path / "raw" / "job" / "pub_00.json").write_text(json.dumps(payload))
        reasons = SKELETON_VIOLATIONS(tmp_path, record, ["m"])
        if (label == "clean") == bool(reasons):
            raise AssertionError(f"{label}: {reasons}")


def test_a_readout_arm_with_its_quiet_reference_schedule_passes_exposure(tmp_path: Path) -> None:
    result = report.report(_write_run(tmp_path / "run", measured=True), predicted=False)
    if not result["identity"]["exposure"].startswith(f"{len(ip.idle_penalty_circuits())} members"):
        raise AssertionError(result["identity"]["exposure"])
    if report.quiet_reference("idle_s_meas_short_y") != f"idle_s_ramsey_y_{ip.SHORT_MEAS_DT}dt":
        raise AssertionError("the short arm's quiet reference is not the short Ramsey arm")


def test_compare_refuses_predicted_and_same_calibration_reports(tmp_path: Path) -> None:
    measured = report.report(_write_run(tmp_path / "a", measured=True), predicted=False)
    predicted = report.report(_write_run(tmp_path / "b", measured=False), predicted=True)
    later = report.report(_write_run(tmp_path / "c", measured=True, calibration="c2"), predicted=False)
    for first, second in ((measured, measured), (measured, predicted)):
        with pytest.raises(report.RefusedAnalysis):
            report.compare(first, second)
    later["identity"]["collect_sha256"] = "other"
    verdicts = report.compare(measured, later)
    if verdicts["kappa_1"]["n"] != 2 * len(LAYOUTS):
        raise AssertionError(f"compare kept {verdicts['kappa_1']['n']} qubits")


def test_dephasing_needs_a_negative_mean_and_a_quiet_null() -> None:
    errors = [0.001] * 31
    gain = report._mean_decision([0.01] * 30 + [0.012], errors, 0.02, "negative")
    if gain["verdict"] == "present":
        raise AssertionError("a visibility gain read as dephasing")
    loss = report._mean_decision([-0.01] * 30 + [-0.012], errors, 0.02, "negative")
    if loss["verdict"] != "present":
        raise AssertionError("a uniform visibility loss read other than present")


def test_unwrap_recovers_a_shift_beyond_the_long_window_alias() -> None:
    true_khz = 31.0
    long_wrapped = math.remainder(2 * math.pi * true_khz * 1e3 * ip.MEAS_DT * DT, 2 * math.pi)
    long_khz = long_wrapped / (2 * math.pi * ip.MEAS_DT * DT) / 1e3
    if abs(report.unwrap_shift(long_khz, 30.2, DT) - true_khz) > 1e-9:
        raise AssertionError("the short-window value failed to unwrap the long-window phase")


def test_median_interval_widens_with_spread_and_holds_the_median() -> None:
    narrow = report.median_interval(list(np.linspace(0.99, 1.01, 31)))
    wide = report.median_interval(list(np.linspace(0.5, 1.5, 31)))
    if not (narrow["low"] <= narrow["median"] <= narrow["high"]):
        raise AssertionError(narrow)
    if wide["high"] - wide["low"] <= narrow["high"] - narrow["low"]:
        raise AssertionError("the interval failed to widen with spread")
    if copy.deepcopy(narrow) != narrow:
        raise AssertionError("interval not plain data")

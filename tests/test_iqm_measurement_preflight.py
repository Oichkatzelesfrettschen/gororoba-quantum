"""The pre-flight probe of the pinching case: byte-identical circuits, the stop rule and the retained build.

Tests that read the retained case or run carry `audit`; the unmarked tests build their input here."""

import json
import math
from pathlib import Path
from typing import Any

import iqm_measurement_preflight as probe
import pytest


@pytest.mark.audit
def test_self_test_holds() -> None:
    if "measurement preflight" not in probe.self_test():
        raise AssertionError("the self-test summary changed")


@pytest.mark.audit
def test_retained_probe_matches_the_main_case() -> None:
    probe.check(probe.ROOT / "results/iqm/cases" / probe.CASE)


@pytest.mark.audit
def test_analyze_reads_a_run_directory_and_stops_on_a_collapsed_qubit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    files = probe.build_files(probe.MAIN_CASE, probe.SHOTS)
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    prediction = json.loads(files["prediction.json"])
    excerpt = json.loads(files[probe.EXCERPT])
    circuits = [json.loads(files[f"circuits/{name}.json"]) for name in probe.NAMES]
    qubits = sorted(prediction["qubits"], key=lambda q: int(q[2:]))
    reading = {
        q: {name: probe.seq.raw_p0(probe.BAND_KEY[name], excerpt["qubits"][q], 0.03) for name in probe.NAMES}
        for q in qubits
    }
    (tmp_path / "raw").mkdir()
    (tmp_path / "submission.json").write_text(json.dumps({"qc": probe.QC, "job": probe.JOB}), encoding="utf-8")
    (tmp_path / "raw/job.json").write_text(
        json.dumps({"compilation": {"calibration_set_id": prediction["calibration_set"]}}), encoding="utf-8"
    )
    monkeypatch.setattr(probe, "run_facts", lambda run_dir: {"statuses": {"completed": 1}, "charge": 0.5})

    def run(values: dict[str, dict[str, float]]) -> dict[str, Any]:
        outcomes = probe.synthetic(circuits, prediction, probe.SHOTS, values)
        (tmp_path / "raw/measurements.json").write_text(json.dumps(outcomes), encoding="utf-8")
        return probe.analyze(tmp_path)

    quiet = run(reading)
    if quiet["proceed"] is not True or quiet["shots"] != probe.SHOTS:
        raise AssertionError(f"a model device stops the probe: {probe.table(quiet)}")
    reading[qubits[2]]["ro1"] = 0.52
    stopped = run(reading)
    flags = {q: row["passes"] for q, row in stopped["qubits"].items()}
    if stopped["proceed"] is not False or flags != {q: q != qubits[2] for q in qubits}:
        raise AssertionError(f"a collapsed qubit does not stop exactly its own verdict: {flags}")


def qb11_replay() -> dict[str, Any]:
    """The diagnostic's QB11 readings (ro0 0.906, ro1 0.522, pi/2-pair unitary 0.586; the measure reading is the
    model's) run through the probe's stop rule on the first qubit's circuits, against QB11's own calibrated bands."""
    files = probe.build_files(probe.MAIN_CASE, probe.SHOTS)
    prediction = json.loads(files["prediction.json"])
    excerpt = json.loads(files[probe.EXCERPT])
    circuits = [json.loads(files[f"circuits/{name}.json"]) for name in probe.NAMES]
    diag = probe.seq.load_json(probe.seq.DIAGNOSTIC_EXCERPT)["qubits"]["QB11"]
    host = sorted(prediction["qubits"], key=lambda q: int(q[2:]))[0]
    prediction["qubits"][host]["raw_band"] = probe.seq.raw_band(diag)
    reading = {
        q: {name: probe.seq.raw_p0(probe.BAND_KEY[name], excerpt["qubits"][q], 0.03) for name in probe.NAMES}
        for q in prediction["qubits"]
    }
    reading[host].update({"ro0": 0.906, "ro1": 0.522, "unitary-n16-s0p": 0.586})
    outcomes = probe.synthetic(circuits, prediction, probe.SHOTS, reading)
    result = probe.evaluate(circuits, outcomes, prediction, probe.SHOTS)
    result["host"] = host
    return result


@pytest.mark.audit
def test_qb11_diagnostic_readings_fail_the_stop_rule() -> None:
    result = qb11_replay()
    row = result["qubits"][result["host"]]
    if row["passes"] or row["contrast_passes"] or row["readings"]["ro1"]["passes"]:
        raise AssertionError(probe.table(result))
    if result["proceed"]:
        raise AssertionError("the probe proceeds with a collapsed qubit")


CAL = {"t1_s": 4.5e-5, "t2_s": 1.0e-5, "prx_p": 1.0e-3, "e01": 0.01, "e10": 0.02}
SHOTS = 1000


def synthetic_probe() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The four probe circuits on two qubits and a prediction holding their raw bands, built from CAL."""
    qubits = ["QB1", "QB2"]
    circuits = [
        probe.seq.ro_circuit("ro0", qubits),
        probe.seq.ro_circuit("ro1", qubits),
        probe.seq.circuit("unitary-n16-s0p", qubits, "unitary", 16, 1),
        probe.seq.circuit("measure-n16-s0p", qubits, "measure", 16, 1),
    ]
    return circuits, {"qubits": {q: {"raw_band": probe.seq.raw_band(CAL)} for q in qubits}}


def readings(p_init: float) -> dict[str, dict[str, float]]:
    return {
        q: {name: probe.seq.raw_p0(probe.BAND_KEY[name], CAL, p_init) for name in probe.NAMES} for q in ("QB1", "QB2")
    }


def test_judge_reads_distance_outside_a_band_at_the_nearest_edge() -> None:
    inside = probe.judge(0.5, [0.4, 0.6], SHOTS)
    edge = probe.judge(0.6 + 3 * math.sqrt(0.6 * 0.4 / SHOTS), [0.4, 0.6], SHOTS)
    if not inside["passes"] or inside["z"] != 0.0 or edge["passes"] or abs(edge["z"] - 3) > 1e-9:
        raise AssertionError(f"{inside} {edge}")


def test_stop_rule_passes_a_model_device_and_stops_a_collapsed_qubit() -> None:
    circuits, prediction = synthetic_probe()
    for p_init in probe.seq.RAW_EXCITATION_BAND:
        outcomes = probe.synthetic(circuits, prediction, SHOTS, readings(p_init))
        result = probe.evaluate(circuits, outcomes, prediction, SHOTS)
        if not result["proceed"]:
            raise AssertionError(probe.table(result))
    planted = readings(0.03)
    planted["QB1"].update({"ro0": 0.906, "ro1": 0.522, "unitary-n16-s0p": 0.586})
    result = probe.evaluate(circuits, probe.synthetic(circuits, prediction, SHOTS, planted), prediction, SHOTS)
    row = result["qubits"]["QB1"]
    if result["proceed"] or row["passes"] or row["contrast_passes"] or row["readings"]["ro1"]["passes"]:
        raise AssertionError(probe.table(result))
    if not result["qubits"]["QB2"]["passes"]:
        raise AssertionError("a collapsed qubit stops its neighbor")


def test_missing_final_key_stops_the_probe() -> None:
    circuits, prediction = synthetic_probe()
    outcomes = probe.synthetic(circuits, prediction, SHOTS, readings(0.03))
    del outcomes[3]["m7"]
    if probe.evaluate(circuits, outcomes, prediction, SHOTS)["proceed"]:
        raise AssertionError("a missing mid-circuit key passes")

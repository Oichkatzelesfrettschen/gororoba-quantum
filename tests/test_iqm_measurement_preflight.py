"""The pre-flight probe of the pinching case: byte-identical circuits, the stop rule and the retained build."""

import json
from pathlib import Path

import iqm_measurement_preflight as probe
import pytest


def test_self_test_holds() -> None:
    if "measurement preflight" not in probe.self_test():
        raise AssertionError("the self-test summary changed")


def test_retained_probe_matches_the_main_case() -> None:
    probe.check(probe.ROOT / "results/iqm/cases" / probe.CASE)


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

    def run(values: dict[str, dict[str, float]]) -> dict[str, object]:
        outcomes = probe.synthetic(circuits, prediction, probe.SHOTS, values)
        (tmp_path / "raw/measurements.json").write_text(json.dumps(outcomes), encoding="utf-8")
        return probe.analyze(tmp_path)

    quiet = run(reading)
    if quiet["proceed"] is not True or quiet["shots"] != probe.SHOTS:
        raise AssertionError(f"a model device stops the probe: {probe.table(quiet)}")
    reading[qubits[2]]["ro1"] = 0.52
    stopped = run(reading)
    flags = {q: row["passes"] for q, row in stopped["qubits"].items()}  # type: ignore[attr-defined]
    if stopped["proceed"] is not False or flags != {q: q != qubits[2] for q in qubits}:
        raise AssertionError(f"a collapsed qubit does not stop exactly its own verdict: {flags}")

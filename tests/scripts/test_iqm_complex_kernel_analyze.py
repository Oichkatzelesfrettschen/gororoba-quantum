"""The run reader of the A_5 complex kernel case on a synthetic run built from the case's own predicted laws."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import iqm_complex_kernel_analyze as reader
import pytest

import iqm_records

ROOT = Path(__file__).resolve().parents[2]
CASE_DIR = ROOT / "results/iqm/cases/a5-complex-kernel-garnet"
KEPT = 2000


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def rows_of(law: list[float], width: int) -> list[list[int]]:
    """Shot rows (bit c of the outcome at position c) holding each outcome in proportion to its law."""
    out: list[list[int]] = []
    for index, p in enumerate(law):
        out += [[(index >> c) & 1 for c in range(width)]] * round(p * KEPT)
    return out


def make_run(tmp_path: Path, *, qc: str = "garnet", mutate: Any = None, calibration: str | None = None) -> Path:
    run = tmp_path / "run"
    (run / "raw").mkdir(parents=True)
    shutil.copytree(CASE_DIR / "circuits", run / "circuits")
    for name in ("cases.json", "prediction.json"):
        shutil.copyfile(CASE_DIR / name, run / name)
    pred = json.loads((run / "prediction.json").read_text(encoding="utf-8"))
    case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    measurements = []
    for entry in case["jobs"][0]["circuits"]:
        operand, kind, orientation, _ = Path(entry["file"]).stem.split("-")
        width = pred["operands"][operand]["block"]["data_qubits"] + 1
        law = pred["operands"][operand]["kinds"][kind]["law"][orientation]
        measurements.append({"m": rows_of(law, width)})
    if mutate is not None:
        mutate(measurements)
    raw = {
        "job.json": {
            "id": "job-1",
            "status": "completed",
            "compilation": {"calibration_set_id": calibration or pred["calibration_set"]},
            "metrics": {"billed_seconds": 9, "runtime_seconds": 8.5},
        },
        "measurements.json": measurements,
        "measurement_counts.json": [],
    }
    digests = {}
    for name, value in raw.items():
        data = json.dumps(value).encode()
        (run / "raw" / name).write_bytes(data)
        digests[name] = iqm_records.sha256(data)
    (run / "results.json").write_text(
        json.dumps(
            {
                "schema": iqm_records.RESULTS_SCHEMA,
                "job_id": "job-1",
                "status": "completed",
                "raw_sha256": digests,
                "shots_per_circuit": [len(m["m"]) for m in measurements],
            }
        ),
        encoding="utf-8",
    )
    (run / "submission.json").write_text(
        json.dumps(
            {
                "schema": iqm_records.SUBMISSION_SCHEMA,
                "approval": "test",
                "cases_sha256": iqm_records.sha256((run / "cases.json").read_bytes()),
                "job": "kernel",
                "job_id": "job-1",
                "qc": qc,
                "submitted_at": "2026-11-28T00:00:00Z",
                "price_per_second": 0.5,
            }
        ),
        encoding="utf-8",
    )
    return run


def test_run_at_the_predicted_laws_reads_complex_strata(tmp_path: Path) -> None:
    result = reader.analyze_run(make_run(tmp_path))
    analysis = result["analysis"]
    require(analysis["verdict"] == "complex strata" and analysis["null_resolved"])
    for name, n_c in (("s016", 16.0), ("s412", 12.0), ("s124", 4.0)):
        require(abs(analysis["subtracted"][name]["n_c"] - n_c) < 0.5)
    require(result["billed_seconds"] == 9.0 and 0.0 < result["kept_fraction"] <= 1.0)
    require(all(abs(z) < 5 for z in result["half_to_half_z"].values()))


def test_run_that_swaps_the_real_and_complex_circuits_reads_real_strata(tmp_path: Path) -> None:
    def swap(measurements: list[dict[str, Any]]) -> None:
        names = [Path(e["file"]).stem for e in json.loads((CASE_DIR / "cases.json").read_text())["jobs"][0]["circuits"]]
        index = {n: i for i, n in enumerate(names)}
        for name in names:
            operand, kind, orientation, copy = name.split("-")
            if kind == "real":
                other = index[f"{operand}-cplx-{orientation}-{copy}"]
                measurements[index[name]], measurements[other] = measurements[other], measurements[index[name]]

    require(reader.analyze_run(make_run(tmp_path, mutate=swap))["analysis"]["verdict"] == "real strata")


def test_mock_run_is_refused(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, qc="garnet:mock"))


def test_run_compiled_against_another_calibration_set_is_refused(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(make_run(tmp_path, calibration="00000000-0000-0000-0000-000000000000"))


def test_run_with_a_changed_prediction_is_refused(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "prediction.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(iqm_records.RecordError):
        reader.analyze_run(run)

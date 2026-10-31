"""iqm_records reads a bounded synthetic IQM run from any location and refuses one whose facts disagree.

The archive-wide replay (every retained run through both reader paths) carries the audit marker."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import iqm_jobs
import iqm_platform
import pytest

import iqm_records

ROOT = Path(__file__).resolve().parents[2]
SHOTS = 4


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _text(value: Any) -> bytes:
    return (json.dumps(value, indent=1, sort_keys=True) + "\n").encode()


def make_run(root: Path, *, status: str = "completed", approval: str = "fixture approval") -> Path:
    """One job of two circuits; a completed job retains measurements of SHOTS shots per circuit."""
    run = root / "2026-01-01T000000Z-garnet-fixture-job"
    (run / "raw").mkdir(parents=True)
    circuits = []
    for name in ("x.json", "zero.json"):
        data = _text({"name": name, "instructions": []})
        (run / name).write_bytes(data)
        circuits.append({"file": name, "sha256": iqm_records.sha256(data)})
    case = {
        "schema": iqm_records.CASE_SCHEMA,
        "jobs": [{"job": "fixture", "shots": SHOTS, "options": {}, "circuits": circuits}],
    }
    case_bytes = _text(case)
    (run / "cases.json").write_bytes(case_bytes)
    job = {"id": "job-1", "status": status, "metrics": {"billed_seconds": 2.0}}
    measurements = [{"c": [[1]] * SHOTS}, {"c": [[0]] * SHOTS}]
    raw: dict[str, bytes] = {"job.json": _text(job)}
    if status == "completed":
        raw["measurements.json"] = _text(measurements)
        raw["measurement_counts.json"] = b"[]\n"
    for name, data in raw.items():
        (run / "raw" / name).write_bytes(data)
    (run / "submission.json").write_bytes(
        _text(
            {
                "schema": iqm_records.SUBMISSION_SCHEMA,
                "job_id": "job-1",
                "qc": "garnet",
                "job": "fixture",
                "cases_sha256": iqm_records.sha256(case_bytes),
                "approval": approval,
                "price_per_second": 0.5,
                "submitted_at": "2026-01-01T00:00:00Z",
            }
        )
    )
    (run / "results.json").write_bytes(
        _text(
            {
                "schema": iqm_records.RESULTS_SCHEMA,
                "job_id": "job-1",
                "status": status,
                "raw_sha256": {name: iqm_records.sha256(data) for name, data in raw.items()},
                "shots_per_circuit": [SHOTS, SHOTS] if status == "completed" else [],
            }
        )
    )
    return run


def test_platform_error_is_the_record_error() -> None:
    _check(iqm_platform.PlatformError is iqm_records.RecordError, "iqm_platform raises another class than the reader")
    _check(iqm_jobs.PlatformError is iqm_records.RecordError, "iqm_jobs raises another class than the reader")


def test_synthetic_run_yields_its_facts_and_run_facts_adds_only_the_charge(tmp_path: Path) -> None:
    run = iqm_records.read_run(make_run(tmp_path))
    _check(
        run.facts
        == {
            "created_at": "2026-01-01T00:00:00Z",
            "backends": ["garnet"],
            "jobs": 1,
            "circuits": 2,
            "statuses": {"completed": 1},
            "detail": "2 billed seconds",
        },
        f"facts {run.facts}",
    )
    _check(run.completed_measurements() == [{"c": [[1]] * SHOTS}, {"c": [[0]] * SHOTS}], "measurements differ")
    facts = iqm_jobs.run_facts(make_run(tmp_path / "again"))
    _check(facts == {**run.facts, "charge": 1.0}, f"run_facts adds other than the charge: {facts}")


def test_relocated_copy_reads_identically(tmp_path: Path) -> None:
    original = make_run(tmp_path / "here")
    moved = tmp_path / "elsewhere" / "renamed"
    shutil.copytree(original, moved)
    _check(iqm_records.read_run(moved) == iqm_records.read_run(original), "relocation changed the run")


def test_failed_job_is_an_acquisition_fact_without_measurements(tmp_path: Path) -> None:
    run = iqm_records.read_run(make_run(tmp_path, status="failed"))
    _check(run.facts["statuses"] == {"failed": 1} and run.measurements is None, f"{run.facts} {run.measurements}")
    with pytest.raises(iqm_records.RecordError, match="returned no measurements"):
        run.completed_measurements()


def test_altered_raw_bytes_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    raw = run / "raw/measurements.json"
    raw.write_bytes(raw.read_bytes() + b"\n")
    with pytest.raises(iqm_records.RecordError, match="differs from its recorded sha256"):
        iqm_records.read_run(run)


def test_altered_circuit_bytes_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "x.json").write_bytes(b"{}\n")
    with pytest.raises(iqm_records.RecordError, match="x.json differs from its recorded sha256"):
        iqm_records.read_run(run)


def test_wrong_job_identity_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    results = json.loads((run / "results.json").read_bytes())
    results["job_id"] = "another-job"
    (run / "results.json").write_bytes(_text(results))
    with pytest.raises(iqm_records.RecordError, match="names another job"):
        iqm_records.read_run(run)


def test_short_measurements_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    short = _text([{"c": [[1]] * (SHOTS - 1)}, {"c": [[0]] * SHOTS}])
    (run / "raw/measurements.json").write_bytes(short)
    results = json.loads((run / "results.json").read_bytes())
    results["raw_sha256"]["measurements.json"] = iqm_records.sha256(short)
    (run / "results.json").write_bytes(_text(results))
    with pytest.raises(iqm_records.RecordError, match="other shot counts"):
        iqm_records.read_run(run)


def test_unapproved_or_missing_receipt_rejected(tmp_path: Path) -> None:
    with pytest.raises(iqm_records.RecordError, match="not an approved"):
        iqm_records.read_run(make_run(tmp_path / "unapproved", approval=""))
    run = make_run(tmp_path / "receiptless")
    (run / "submission.json").unlink()
    records = iqm_records.load_run(run)
    _check(records.case is not None and records.submission is None, "load_run judged the directory")
    with pytest.raises(iqm_records.RecordError, match="submission.json is missing"):
        iqm_records.validate_run(records)


@pytest.mark.audit
def test_every_retained_run_reads_through_both_paths() -> None:
    """End-to-end replay of the archive: read_run and run_facts agree on every retained run apart from the charge."""
    runs = iqm_records.run_directories(ROOT / "results/iqm/runs")
    _check(len(runs) > 0, "no retained IQM runs")
    for directory in runs:
        run = iqm_records.read_run(directory)
        facts = iqm_jobs.run_facts(directory)
        _check({**run.facts, "charge": facts["charge"]} == facts, f"{directory.name}: facts differ beyond the charge")

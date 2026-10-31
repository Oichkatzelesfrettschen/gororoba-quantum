"""iqm_records reads a retained IQM run from any location; iqm_jobs delegates to it and adds only the charge."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import iqm_jobs
import iqm_platform
import pytest

import iqm_records

ROOT = Path(__file__).resolve().parents[2]


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _runs() -> list[Path]:
    return iqm_records.run_directories(ROOT / "results/iqm/runs")


def test_platform_error_is_the_record_error() -> None:
    _check(iqm_platform.PlatformError is iqm_records.RecordError, "iqm_platform raises another class than the reader")
    _check(iqm_jobs.PlatformError is iqm_records.RecordError, "iqm_jobs raises another class than the reader")


def test_every_retained_run_reads_and_run_facts_adds_only_the_charge() -> None:
    runs = _runs()
    _check(len(runs) > 0, "no retained IQM runs")
    for directory in runs:
        run = iqm_records.read_run(directory)
        facts = iqm_jobs.run_facts(directory)
        _check({**run.facts, "charge": facts["charge"]} == facts, f"{directory.name}: facts differ beyond the charge")
        _check(run.job["id"] == run.submission["job_id"], f"{directory.name}: job identity differs")
        _check((run.measurements is None) == (run.results["status"] != "completed"), f"{directory.name}: measurements")


def test_relocated_copy_reads_identically(tmp_path: Path) -> None:
    original = next(d for d in _runs() if iqm_records.read_run(d).measurements is not None)
    moved = tmp_path / "elsewhere" / "renamed"
    shutil.copytree(original, moved)
    _check(iqm_records.read_run(moved) == iqm_records.read_run(original), "relocation changed the run")


def test_altered_raw_and_wrong_job_and_missing_receipt_are_refused(tmp_path: Path) -> None:
    original = next(d for d in _runs() if iqm_records.read_run(d).measurements is not None)
    altered = tmp_path / "altered"
    shutil.copytree(original, altered)
    raw = altered / "raw/measurements.json"
    raw.write_bytes(raw.read_bytes() + b"\n")
    with pytest.raises(iqm_records.RecordError, match="differs from its recorded sha256"):
        iqm_records.read_run(altered)
    other = tmp_path / "other-job"
    shutil.copytree(original, other)
    results = json.loads((other / "results.json").read_bytes())
    results["job_id"] = "another-job"
    (other / "results.json").write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(iqm_records.RecordError, match="names another job"):
        iqm_records.read_run(other)
    receiptless = tmp_path / "receiptless"
    shutil.copytree(original, receiptless)
    (receiptless / "submission.json").unlink()
    records = iqm_records.load_run(receiptless)
    _check(records.case is not None and records.submission is None, "load_run judged the directory")
    with pytest.raises(iqm_records.RecordError, match="submission.json is missing"):
        iqm_records.validate_run(records)


def test_completed_measurements_refuses_a_job_without_them() -> None:
    run = iqm_records.read_run(_runs()[0])
    if run.measurements is None:
        with pytest.raises(iqm_records.RecordError, match="returned no measurements"):
            run.completed_measurements()
    else:
        _check(run.completed_measurements() is run.measurements, "completed job's measurements differ")

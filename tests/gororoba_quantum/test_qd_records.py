"""qd_records reads a retained Quandela run offline from any location; qd_platform delegates to it."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import qd_platform

import qd_records

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "results/quandela/runs"


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _retained_runs() -> list[Path]:
    return qd_records.run_directories(RUNS)


def test_platform_error_is_the_record_error() -> None:
    _check(
        qd_platform.PlatformError is qd_records.RecordError, "qd_platform raises another error class than the reader"
    )


def test_every_retained_run_reads_and_run_facts_adds_only_the_charge() -> None:
    runs = _retained_runs()
    _check(len(runs) > 0, "no retained Quandela runs")
    for directory in runs:
        run = qd_records.read_run(directory)
        facts = qd_platform.run_facts(directory)
        _check({**run.facts, "charge": facts["charge"]} == facts, f"{directory.name}: facts differ beyond the charge")
        _check(run.submission["job_id"] == run.collected["job_id"], f"{directory.name}: job identity differs")
        status = run.collected["status"]["status"]
        _check(run.facts["statuses"] == {status: 1}, f"{directory.name}: status fact differs")
        _check(
            (run.summary is None) == (status != "completed" and not (directory / "raw/result.json").exists()),
            "summary presence",
        )


def test_relocated_copy_reads_identically(tmp_path: Path) -> None:
    original = next(d for d in _retained_runs() if (d / "raw/result.json").is_file())
    moved = tmp_path / "elsewhere" / "renamed"
    shutil.copytree(original, moved)
    _check(qd_records.read_run(moved) == qd_records.read_run(original), "relocation changed the run")


def test_altered_raw_result_rejected(tmp_path: Path) -> None:
    original = next(d for d in _retained_runs() if (d / "raw/result.json").is_file())
    moved = tmp_path / "run"
    shutil.copytree(original, moved)
    raw = moved / "raw/result.json"
    raw.write_bytes(raw.read_bytes().replace(b"}", b" }", 1))
    with pytest.raises(qd_records.RecordError, match="raw/result.json differs from its recorded sha256"):
        qd_records.read_run(moved)


def test_wrong_job_identity_rejected(tmp_path: Path) -> None:
    original = next(d for d in _retained_runs() if (d / "raw/result.json").is_file())
    moved = tmp_path / "run"
    shutil.copytree(original, moved)
    path = moved / "results.json"
    value = json.loads(path.read_bytes())
    value["job_id"] = "another-job"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(qd_records.RecordError, match="names another job or schema"):
        qd_records.read_run(moved)


def test_altered_circuit_bytes_rejected(tmp_path: Path) -> None:
    original = next(d for d in _retained_runs() if (d / "raw/result.json").is_file())
    moved = tmp_path / "run"
    shutil.copytree(original, moved)
    circuit = moved / json.loads((moved / "cases.json").read_bytes())["circuit"]["file"]
    circuit.write_bytes(circuit.read_bytes() + b"\n")
    with pytest.raises(qd_records.RecordError, match="differs from its cases.json sha256"):
        qd_records.read_run(moved)


def test_uncollected_run_rejected(tmp_path: Path) -> None:
    original = _retained_runs()[0]
    moved = tmp_path / "run"
    shutil.copytree(original, moved)
    (moved / "results.json").unlink()
    with pytest.raises(qd_records.RecordError, match="results.json is missing"):
        qd_records.read_run(moved)


def test_run_carries_the_case_digest_and_the_sent_body() -> None:
    directory = _retained_runs()[0]
    run = qd_records.read_run(directory)
    _check(run.cases_sha256 == qd_records.sha256_bytes((directory / "cases.json").read_bytes()), "case digest differs")
    _check(
        qd_records.sha256_bytes(json.dumps(run.body, sort_keys=True).encode()) == run.submission["body_sha256"],
        "the carried body is not the body the receipt sent",
    )

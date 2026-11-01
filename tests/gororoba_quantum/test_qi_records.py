"""qi_records reads a retained Quantum Inspire run from any location and rejects records whose facts disagree."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

import qi_records

SHOTS = 8


def _text(value: Any) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def make_run(root: Path, *, v2: bool = True, failed: bool = False) -> Path:
    """Two circuits; the first completes with raw shots, the second completes too unless failed."""
    directory = root / "2026-01-01T000000Z-fixture"
    (directory / "raw").mkdir(parents=True)
    codes = {
        "a.cq": "version 3.0\nqubit[2] q\nbit[2] b\nX90 q[0]\nb = measure q\n",
        "b.cq": "version 3.0\nqubit[2] q\n",
    }
    rows = []
    for name, code in codes.items():
        (directory / name).write_text(code, encoding="utf-8")
        rows.append({"file": name, "sha256": qi_records.digest(code.encode()), "nqubits": 2})
    cases = {"backend": "QXsinglenodesimulator", "backend_type_id": 1, "shots": SHOTS, "circuits": rows}
    cases_text = _text(cases)
    (directory / "cases.json").write_text(cases_text, encoding="utf-8")
    jobs: list[dict[str, Any]] = [{"file": "a.cq", "job": 11}, {"file": "b.cq", "job": 12}]
    receipt: dict[str, Any] = {
        "schema": "qi-submission-v1",
        "approval": "fixture",
        "batch_job": 7,
        "backend": "QXsinglenodesimulator",
        "backend_type_id": 1,
        "shots": SHOTS,
        "jobs": jobs,
    }
    if v2:
        receipt.update(schema="qi-submission-v2", state="enqueued", cases_sha256=qi_records.digest(cases_text.encode()))
        for job, row in zip(jobs, rows, strict=True):
            job["sha256"] = row["sha256"]
    (directory / "submission.json").write_text(_text(receipt), encoding="utf-8")
    histograms: dict[str, dict[str, int]] = {"a.cq": {"01": 5, "11": 3}, "b.cq": {"00": SHOTS}}
    collected = []
    for index, job in enumerate(jobs):
        status = "failed" if failed and index == 1 else "completed"
        record = {
            "id": job["job"],
            "batch_job_id": 7,
            "created_on": f"2026-01-01T00:00:0{index}Z",
            "number_of_shots": SHOTS,
            "status": status,
            "raw_data_enabled": True,
        }
        results = []
        if status == "completed":
            histogram = histograms[str(job["file"])]
            results = [{"job_id": job["job"], "shots_requested": SHOTS, "shots_done": SHOTS, "results": histogram}]
            shots = [key for key, count in histogram.items() for _ in range(count)]
            (directory / "raw" / f"{job['file']}.json").write_text(_text(shots), encoding="utf-8")
        collected.append({"file": job["file"], "job": record, "results": results})
    (directory / "results.json").write_text(
        _text({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
    )
    return directory


def _rewrite(path: Path, edit: Any) -> None:
    value = json.loads(path.read_bytes())
    edit(value)
    path.write_text(_text(value), encoding="utf-8")


def test_valid_run_yields_its_facts(tmp_path: Path) -> None:
    acquisition = qi_records.read_run(make_run(tmp_path))
    _check(acquisition.schema == "qi-submission-v2", "receipt schema differs")
    _check(acquisition.statuses == {"completed": 2}, f"statuses {acquisition.statuses}")
    _check(acquisition.completed, "two completed jobs read as incomplete")
    _check([job.job_id for job in acquisition.jobs] == [11, 12], "job ids differ from the receipt")
    first = acquisition.jobs[0]
    _check(first.histogram == {"01": 5, "11": 3}, f"histogram {first.histogram}")
    _check(first.raw is not None and sorted(first.raw) == ["01"] * 5 + ["11"] * 3, "raw shots differ")
    _check(acquisition.created_at == "2026-01-01T00:00:00Z", "created_at is not the earliest job")


def test_relocated_copy_reads_identically(tmp_path: Path) -> None:
    original = make_run(tmp_path / "here")
    moved = tmp_path / "elsewhere" / "renamed"
    shutil.copytree(original, moved)
    _check(qi_records.read_run(moved) == qi_records.read_run(original), "relocation changed the acquisition")
    _check(
        qi_records.load_run(moved)["digests"] == qi_records.load_run(original)["digests"],
        "relocation changed the file digests",
    )


def test_record_digests_name_every_file_read(tmp_path: Path) -> None:
    digests = qi_records.load_run(make_run(tmp_path))["digests"]
    expected = {"cases.json", "submission.json", "results.json", "a.cq", "b.cq", "raw/a.cq.json", "raw/b.cq.json"}
    _check(set(digests) == expected, f"digest keys {sorted(digests)}")


def test_wrong_job_identity_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)

    def swap(collected: dict[str, Any]) -> None:
        collected["jobs"][0]["job"]["id"] = 99

    _rewrite(run / "results.json", swap)
    with pytest.raises(ValueError, match="results.json jobs differ from submission.json"):
        qi_records.read_run(run)


def test_altered_raw_bytes_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "raw/a.cq.json").write_text(_text(["01"] * 4 + ["11"] * 4), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the recorded outcome histogram"):
        qi_records.read_run(run)


def test_altered_circuit_bytes_rejected_by_receipt_and_manifest(tmp_path: Path) -> None:
    for v2, text in ((True, "bytes its receipt uploaded"), (False, "digest differs from cases.json")):
        run = make_run(tmp_path / str(v2), v2=v2)
        (run / "a.cq").write_text("version 3.0\nqubit[2] q\nbit[2] b\nmX90 q[0]\nb = measure q\n", encoding="utf-8")
        with pytest.raises(ValueError, match=text):
            qi_records.read_run(run)


def test_missing_raw_for_completed_job_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "raw/b.cq.json").unlink()
    with pytest.raises(ValueError, match="raw/ holds"):
        qi_records.read_run(run)


def test_uncollected_run_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path)
    (run / "results.json").unlink()
    with pytest.raises(ValueError, match="results.json is missing"):
        qi_records.read_run(run)


def test_failed_job_is_an_acquisition_fact(tmp_path: Path) -> None:
    acquisition = qi_records.read_run(make_run(tmp_path, failed=True))
    _check(acquisition.statuses == {"completed": 1, "failed": 1}, f"statuses {acquisition.statuses}")
    _check(not acquisition.completed, "a failed job read as completed")
    failed = acquisition.jobs[1]
    _check(failed.histogram is None and failed.raw is None and failed.shots_done == 0, "failed job holds results")


def test_failed_job_holding_raw_rejected(tmp_path: Path) -> None:
    run = make_run(tmp_path, failed=True)
    (run / "raw/b.cq.json").write_text(_text(["00"] * SHOTS), encoding="utf-8")
    with pytest.raises(ValueError, match="raw/ holds"):
        qi_records.read_run(run)

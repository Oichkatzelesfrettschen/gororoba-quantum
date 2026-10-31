"""Offline reader of a retained Quantum Inspire run directory.

A run directory holds cases.json (the circuit manifest), the cQASM files it
names, submission.json (the qi-submission-v1 or v2 receipt), results.json
(the qi-collection-v1 collection) and raw/<file>.json (the ordered shots of
every completed job). load_run reads those files into one record and
validate_run applies the rules every consumer shares: receipt binding,
circuit digests, job identities, one result per completed job and raw shots
agreeing with the recorded histogram. The record keeps every recorded job
status, so a failed or cancelled job validates as an acquisition fact; an
analyzer decides whether its experiment admits it.

Experiment criteria (expected shot count, backend, circuit roles, outcome
tests) belong to the analyzer that owns the design, and the account ledger
reconciliation belongs to scripts/research_state.py. The module reads files
and never writes, authenticates or reaches the provider.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUBMISSION_SCHEMAS = ("qi-submission-v1", "qi-submission-v2")
COLLECTION_SCHEMA = "qi-collection-v1"
RECORD_FILES = ("cases.json", "submission.json", "results.json")


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _optional_json(path: Path, key: str, digests: dict[str, str]) -> Any:
    if not path.is_file():
        return None
    data = path.read_bytes()
    digests[key] = digest(data)
    return json.loads(data)


def load_run(directory: Path) -> dict[str, Any]:
    """Read one run directory into a record; validate_run judges the record.

    The record holds the parsed receipt, manifest and collection, the sha256
    of every circuit file the manifest names (None for a missing file), the
    raw shot lists by file name, whether submission-state.json records an
    interrupted submit, and the sha256 of every file read.
    """
    digests: dict[str, str] = {}
    cases = _optional_json(directory / "cases.json", "cases.json", digests)
    circuits: dict[str, str | None] = {}
    for row in (cases or {}).get("circuits", []):
        path = directory / row["file"]
        if path.is_file():
            circuits[row["file"]] = digests[row["file"]] = digest(path.read_bytes())
        else:
            circuits[row["file"]] = None
    raw_dir = directory / "raw"
    raw: dict[str, Any] = {}
    if raw_dir.is_dir():
        for path in sorted(raw_dir.iterdir()):
            raw[path.name] = _optional_json(path, f"raw/{path.name}", digests)
    return {
        "submission": _optional_json(directory / "submission.json", "submission.json", digests),
        "interrupted": (directory / "submission-state.json").is_file(),
        "cases": cases,
        "cases_sha256": digests.get("cases.json"),
        "results": _optional_json(directory / "results.json", "results.json", digests),
        "circuits": circuits,
        "raw": raw,
        "digests": digests,
    }


@dataclass(frozen=True)
class Job:
    """One submitted circuit's recorded outcome; histogram and raw are None unless the job completed."""

    file: str
    job_id: Any
    batch_job: Any
    status: str
    number_of_shots: int
    shots_done: int
    histogram: dict[str, int] | None
    raw: tuple[str, ...] | None


@dataclass(frozen=True)
class Acquisition:
    """The validated facts of one run: what was submitted, to which backend, and what each job returned."""

    schema: str
    backend: str
    backend_type_id: Any
    shots: int
    batch_job: Any
    created_at: str
    jobs: tuple[Job, ...]

    @property
    def statuses(self) -> Counter[str]:
        return Counter(job.status for job in self.jobs)

    @property
    def completed(self) -> bool:
        return all(job.status == "completed" for job in self.jobs)


def validate_run(record: dict[str, Any], owner: str) -> Acquisition:
    """Apply the shared structural rules to a loaded record; every rejection names the owner."""
    submission = record["submission"]
    require(
        isinstance(submission, dict),
        f"{owner}: no submission.json"
        + (
            "; submission-state.json records an interrupted submit, run qi_platform.py reconcile"
            if record["interrupted"]
            else ""
        ),
    )
    require(submission.get("schema") in SUBMISSION_SCHEMAS, f"{owner}: submission.json schema differs")
    require(
        isinstance(submission.get("approval"), str) and submission["approval"].strip(),
        f"{owner}: submission.json records no approval",
    )
    cases = record["cases"]
    require(isinstance(cases, dict), f"{owner}: cases.json is missing")
    if submission["schema"] == "qi-submission-v2" or "cases_sha256" in submission:
        require(
            submission.get("cases_sha256") == record["cases_sha256"],
            f"{owner}: cases.json digest differs from submission.json",
        )
    if submission["schema"] == "qi-submission-v2":
        require(submission.get("state") == "enqueued", f"{owner}: v2 submission was not confirmed enqueued")
        for row in submission["jobs"]:
            require(
                row.get("sha256") == record["circuits"].get(row["file"]),
                f"{owner}: circuit {row['file']} differs from the bytes its receipt uploaded",
            )
    for field in ("backend", "backend_type_id", "shots"):
        require(cases.get(field) == submission[field], f"{owner}: cases.json and submission.json differ in {field}")
    files = [row["file"] for row in submission["jobs"]]
    require(len(set(files)) == len(files), f"{owner}: submitted circuit files repeat")
    submitted_ids = [row["job"] for row in submission["jobs"]]
    require(len(set(submitted_ids)) == len(submitted_ids), f"{owner}: submitted job ids repeat")
    require(files == [row["file"] for row in cases["circuits"]], f"{owner}: submitted files differ from cases.json")
    for row in cases["circuits"]:
        require(
            record["circuits"].get(row["file"]) == row["sha256"],
            f"{owner}: circuit {row['file']} digest differs from cases.json",
        )
    collected = record["results"]
    require(isinstance(collected, dict), f"{owner}: results.json is missing; collect the run")
    require(collected.get("schema") == COLLECTION_SCHEMA, f"{owner}: results.json schema differs")
    require(
        [(row["file"], row["job"]["id"]) for row in collected["jobs"]]
        == [(row["file"], row["job"]) for row in submission["jobs"]],
        f"{owner}: results.json jobs differ from submission.json",
    )
    jobs: list[Job] = []
    completed: dict[str, dict[str, Any]] = {}
    for row in collected["jobs"]:
        job = row["job"]
        require(
            job["batch_job_id"] == submission["batch_job"] and job["number_of_shots"] == submission["shots"],
            f"{owner}: job {job['id']} names another batch job or shot count",
        )
        histogram = None
        if job["status"] == "completed":
            results = row["results"]
            require(
                len(results) == 1
                and results[0]["job_id"] == job["id"]
                and results[0]["shots_requested"] == submission["shots"],
                f"{owner}: completed job {job['id']} holds one result of the submitted shots",
            )
            completed[f"{row['file']}.json"] = results[0]
            histogram = dict(results[0]["results"])
        else:
            require(not row["results"], f"{owner}: {job['status']} job {job['id']} holds results")
        done = sum(result["shots_done"] for result in row["results"])
        jobs.append(
            Job(
                file=row["file"],
                job_id=job["id"],
                batch_job=job["batch_job_id"],
                status=job["status"],
                number_of_shots=job["number_of_shots"],
                shots_done=done,
                histogram=histogram,
                raw=None,
            )
        )
    require(
        set(record["raw"]) == set(completed),
        f"{owner}: raw/ holds {sorted(record['raw'])}, the completed jobs need {sorted(completed)}",
    )
    for index, job in enumerate(jobs):
        if job.status != "completed":
            continue
        name = f"{job.file}.json"
        shots = record["raw"][name]
        result = completed[name]
        require(
            isinstance(shots, list) and len(shots) == result["shots_done"],
            f"{owner}: raw/{name} length differs from the {result['shots_done']} shots done",
        )
        require(
            all(isinstance(shot, str) for shot in shots), f"{owner}: raw/{name} holds a value other than a bitstring"
        )
        require(
            Counter(shots) == Counter(result["results"]),
            f"{owner}: raw/{name} differs from the recorded outcome histogram",
        )
        jobs[index] = Job(**{**job.__dict__, "raw": tuple(shots)})
    return Acquisition(
        schema=submission["schema"],
        backend=submission["backend"],
        backend_type_id=submission["backend_type_id"],
        shots=submission["shots"],
        batch_job=submission["batch_job"],
        created_at=min(row["job"]["created_on"] for row in collected["jobs"]),
        jobs=tuple(jobs),
    )


def read_run(directory: Path, owner: str | None = None) -> Acquisition:
    """Load and validate one run directory in one call."""
    return validate_run(load_run(directory), owner or f"Quantum Inspire run {directory.name}")

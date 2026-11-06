"""Offline reader of a retained IQM Resonance run directory.

A run directory holds cases.json (an iqm-circuit-case-v1 case naming its
jobs and circuit files), the circuit files, submission.json (the approved
receipt naming the job, the quantum computer and the cases.json digest),
results.json (the collection: job id, terminal status, shots per circuit and
the sha256 of every raw file) and raw/ (job.json, measurements.json,
measurement_counts.json and optional runtime_estimates.json). load_run reads
those files as written and names a missing one on access; validate_run
applies the rules every consumer shares: case schema and circuit digests,
receipt binding, the collection naming the same job with a terminal status,
every raw file keeping its recorded digest, raw/job.json agreeing with the
collection, and a completed job returning the case's shots for every
circuit. The credit charge is an account fact that scripts/iqm_jobs.py adds
to the facts, and that module re-exports every name here so its callers
keep working. The module reads files only and never reaches the service.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "results/iqm/runs"
CASE_SCHEMA = "iqm-circuit-case-v1"
SUBMISSION_SCHEMA = "iqm-submission-v1"
RESULTS_SCHEMA = "iqm-results-v1"
TERMINAL = ("completed", "failed", "cancelled")
ARTIFACTS = ("measurements", "measurement_counts")
# runtime_estimates is a Resonance artifact some jobs return and others do not.
OPTIONAL_ARTIFACTS = ("runtime_estimates",)


class RecordError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _optional_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


@dataclass(frozen=True)
class Records:
    """The files of one run directory as written; None marks a file the directory lacks."""

    directory: Path
    case_bytes: bytes | None
    submission_bytes: bytes | None
    results_bytes: bytes | None
    circuits: dict[str, bytes | None]
    raw: dict[str, bytes]

    def bytes_of(self, name: str) -> bytes:
        if name.startswith("raw/"):
            data = self.raw.get(name[len("raw/") :])
        else:
            data = {
                "cases.json": self.case_bytes,
                "submission.json": self.submission_bytes,
                "results.json": self.results_bytes,
            }.get(name, self.circuits.get(name))
        if data is None:
            raise RecordError(f"{self.directory}: {name} is missing")
        return data

    def json_of(self, name: str) -> Any:
        return json.loads(self.bytes_of(name))

    @property
    def case(self) -> Any:
        return None if self.case_bytes is None else json.loads(self.case_bytes)

    @property
    def submission(self) -> Any:
        return None if self.submission_bytes is None else json.loads(self.submission_bytes)

    @property
    def results(self) -> Any:
        return None if self.results_bytes is None else json.loads(self.results_bytes)


def load_run(directory: Path) -> Records:
    """Read a run (or case) directory's files without judging them: the case, receipt, collection, every circuit
    file a job names and every raw file."""
    case_bytes = _optional_bytes(directory / "cases.json")
    case = None if case_bytes is None else json.loads(case_bytes)
    circuits: dict[str, bytes | None] = {}
    if isinstance(case, dict):
        for row in case.get("jobs", []):
            for circuit in row.get("circuits", []):
                name = circuit.get("file")
                if isinstance(name, str) and name not in circuits:
                    circuits[name] = _optional_bytes(directory / name)
    raw_dir = directory / "raw"
    raw = (
        {path.name: path.read_bytes() for path in sorted(raw_dir.iterdir()) if path.is_file()}
        if raw_dir.is_dir()
        else {}
    )
    return Records(
        directory=directory,
        case_bytes=case_bytes,
        submission_bytes=_optional_bytes(directory / "submission.json"),
        results_bytes=_optional_bytes(directory / "results.json"),
        circuits=circuits,
        raw=raw,
    )


def validate_job(records: Records, job: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    """The case, the named job's row and the cases.json sha256; every circuit file keeps its recorded digest."""
    case_dir = records.directory
    raw = records.bytes_of("cases.json")
    case = json.loads(raw)
    if case.get("schema") != CASE_SCHEMA:
        raise RecordError(f"{case_dir}/cases.json is not {CASE_SCHEMA}")
    rows = [row for row in case["jobs"] if row["job"] == job]
    if len(rows) != 1:
        raise RecordError(f"{case_dir}: job {job} is not in the case")
    for circuit in rows[0]["circuits"]:
        data = records.circuits.get(circuit["file"])
        if data is None or sha256(data) != circuit["sha256"]:
            raise RecordError(f"{case_dir}/{circuit['file']} differs from its recorded sha256")
    return case, rows[0], sha256(raw)


def load_job(case_dir: Path, job: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    return validate_job(load_run(case_dir), job)


def shots_ok(returned: list[int], row: dict[str, Any]) -> bool:
    """Every circuit returned the case's shots, or at most that many under all-zeros heralding, which
    discards each shot whose pre-circuit measurement is not all zeros."""
    heralded = row["options"].get("heralding_mode") == "zeros"
    if len(returned) != len(row["circuits"]):
        return False
    return all(0 < n <= row["shots"] if heralded else n == row["shots"] for n in returned)


@dataclass(frozen=True)
class Run:
    """One validated run: its records, the service's job record, the measurements and the registry facts."""

    submission: dict[str, Any]
    case: dict[str, Any]
    row: dict[str, Any]
    cases_sha256: str
    results: dict[str, Any]
    job: dict[str, Any]
    measurements: list[Any] | None
    raw: dict[str, bytes]
    billed_seconds: float
    facts: dict[str, Any]

    def completed_measurements(self) -> list[Any]:
        """The measurements of a completed job; a job in another terminal state has none to analyze."""
        if self.measurements is None:
            raise RecordError(
                f"job {self.submission['job_id']} is {self.results['status']}; it returned no measurements"
            )
        return self.measurements


def validate_run(records: Records) -> Run:
    """The rules every consumer shares; every rejection names the run directory."""
    run_dir = records.directory
    submission = records.json_of("submission.json")
    if submission.get("schema") != SUBMISSION_SCHEMA or not submission.get("approval"):
        raise RecordError(f"{run_dir}: submission.json is not an approved {SUBMISSION_SCHEMA} receipt")
    case, row, cases_sha256 = validate_job(records, submission["job"])
    if cases_sha256 != submission["cases_sha256"]:
        raise RecordError(f"{run_dir}: cases.json differs from the submission receipt")
    results = records.json_of("results.json")
    if results.get("schema") != RESULTS_SCHEMA or results["job_id"] != submission["job_id"]:
        raise RecordError(f"{run_dir}: results.json names another job")
    if results["status"] not in TERMINAL:
        raise RecordError(f"{run_dir}: job status {results['status']} is not terminal")
    for name, digest in results["raw_sha256"].items():
        data = records.raw.get(name)
        if data is None or sha256(data) != digest:
            raise RecordError(f"{run_dir}/raw/{name} differs from its recorded sha256")
    record = records.json_of("raw/job.json")
    if record["id"] != submission["job_id"] or record["status"] != results["status"]:
        raise RecordError(f"{run_dir}: raw/job.json disagrees with results.json")
    measurements: list[Any] | None = None
    if results["status"] == "completed":
        expected = {"job.json", *(f"{artifact}.json" for artifact in ARTIFACTS)}
        optional = {f"{artifact}.json" for artifact in OPTIONAL_ARTIFACTS}
        if not expected <= set(results["raw_sha256"]) <= expected | optional:
            raise RecordError(
                f"{run_dir}: a completed run retains {sorted(results['raw_sha256'])}, not {sorted(expected)}"
            )
        # The shot counts come from the retained measurements, not from the summary that records them.
        measurements = records.json_of("raw/measurements.json")
        returned = [len(next(iter(circuit.values()))) for circuit in measurements]
        if returned != results["shots_per_circuit"]:
            raise RecordError(f"{run_dir}: results.json records other shot counts than raw/measurements.json")
        if not shots_ok(returned, row):
            raise RecordError(f"{run_dir}: a circuit returned other than {row['shots']} shots")
    billed = float((record.get("metrics") or {}).get("billed_seconds") or 0.0)
    facts = {
        "created_at": submission["submitted_at"],
        "backends": [submission["qc"]],
        "jobs": 1,
        "circuits": len(row["circuits"]),
        "statuses": {results["status"]: 1},
        "detail": f"{billed:g} billed seconds",
    }
    return Run(submission, case, row, cases_sha256, results, record, measurements, records.raw, billed, facts)


def read_run(directory: Path) -> Run:
    """load_run then validate_run: the one call a consumer of a retained run makes."""
    return validate_run(load_run(directory))


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []

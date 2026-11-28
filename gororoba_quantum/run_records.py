"""Read-only facade over the retained-run readers of four providers.

One RunEnvelope per retained run carries the facts every cross-provider check
needs: provider, backend, job identities, terminal status, approval, raw-file
digests, requested and executed shots, billed cost, calibration state, health
verdict and void reasons. The facade reads files only. The Quandela, IQM and
Quantum Inspire facts come through qd_records, iqm_records and qi_records, so
each provider's rules (receipt binding, digests, terminal status) stay in one
place; an IBM run directory has no light reader (live_run.py imports Qiskit),
so the facade reads record.json, collect.json and the raw index.json digests
directly. A reader rejection becomes a reader_errors entry, and validate()
returns every reason a run fails the cross-provider contract; an empty list
admits the run.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import iqm_records
import qd_records
import qi_records

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ("ibm", "quandela", "iqm", "qi")
RUN_ROOTS = {
    "ibm": ROOT / "results/live",
    "quandela": qd_records.RUNS,
    "iqm": iqm_records.RUNS,
    "qi": ROOT / "results/quantum_inspire/runs",
}
# Health verdicts. "unread" marks a run whose records predate the health field; the three void verdicts reject it.
VERDICTS = ("ok", "unread", "live-differ", "compiled-differ", "routing_collapsed")
VOID_VERDICTS = ("live-differ", "compiled-differ", "routing_collapsed")
READER_ERRORS = (RuntimeError, ValueError, KeyError, TypeError, OSError, AssertionError, IndexError)


@dataclass(frozen=True)
class Cost:
    """Billed cost in the provider's own unit (seconds of QPU time or credits); None when the records hold no charge."""

    unit: str
    value: float | None


@dataclass(frozen=True)
class RunEnvelope:
    """The provider-neutral facts of one retained run."""

    provider: str
    backend: str
    run_dir: str
    job_ids: tuple[str, ...]
    status: str
    started_utc: str | None
    approval_present: bool
    raw_sha256: dict[str, str]
    requested_shots: int | None
    executed_shots: int | None
    billed_cost: Cost
    calibration_state: str
    health_verdict: str
    void_reasons: tuple[str, ...] = ()
    reader_errors: tuple[str, ...] = field(default=())

    def to_json(self) -> str:
        """Byte-stable JSON: sorted keys, two-space indent, one trailing newline."""
        return json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"

    def validate(self) -> list[str]:
        """Every reason the run fails the cross-provider contract; an empty list admits it."""
        problems = [f"reader: {error}" for error in self.reader_errors]
        if self.provider not in PROVIDERS:
            problems.append(f"provider {self.provider!r} is not one of {PROVIDERS}")
        if not self.approval_present:
            problems.append("no approval is recorded")
        if not self.job_ids:
            problems.append("no job id is recorded")
        if not self.raw_sha256:
            problems.append("no raw file is retained")
        if self.health_verdict not in VERDICTS:
            problems.append(f"health verdict {self.health_verdict!r} is unknown")
        if self.health_verdict in VOID_VERDICTS:
            problems.append(f"health verdict {self.health_verdict} voids the run")
        problems.extend(f"void: {reason}" for reason in self.void_reasons)
        if (
            self.requested_shots is not None
            and self.executed_shots is not None
            and self.executed_shots > self.requested_shots
        ):
            problems.append(f"executed shots {self.executed_shots} exceed requested shots {self.requested_shots}")
        return problems


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    """The parsed JSON of a file, None when the file is absent."""
    return json.loads(path.read_bytes()) if path.is_file() else None


def display(directory: Path) -> str:
    """The run directory relative to the repository root, else its name."""
    try:
        return directory.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return directory.name


def raw_digests(directory: Path) -> dict[str, str]:
    """sha256 of every file under raw/ as observed on disk, keyed by its path below the run directory."""
    raw = directory / "raw"
    if not raw.is_dir():
        return {}
    return {
        path.relative_to(directory).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted(raw.rglob("*"))
        if path.is_file()
    }


def text_present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def approval_present(provider: str, directory: Path) -> bool:
    """Whether the run's records carry its approval: a quoted string in the receipt, or for IBM the consumed
    digest-bound approved record."""
    if provider == "ibm":
        record = read_json(directory / "record.json")
        return (
            isinstance(record, dict) and bool(record.get("approved_record")) and bool(record.get("approval_consumed"))
        )
    submission = read_json(directory / "submission.json")
    return isinstance(submission, dict) and text_present(submission.get("approval"))


def recovery_handle(provider: str, directory: Path) -> bool:
    """Whether the records name the handle that a recover or reconcile command resumes from: the job id of the
    receipt (or, for IBM, the collected job ids)."""
    if provider == "ibm":
        return bool(_ibm_job_ids(directory))
    submission = read_json(directory / "submission.json")
    if not isinstance(submission, dict):
        return False
    key = "batch_job" if provider == "qi" else "job_id"
    return submission.get(key) not in (None, "")


def _ibm_collections(directory: Path) -> list[dict[str, Any]]:
    data = read_json(directory / "collect.json")
    return [row for row in data if isinstance(row, dict)] if isinstance(data, list) else []


def _ibm_job_ids(directory: Path) -> tuple[str, ...]:
    ids: list[str] = []
    for row in _ibm_collections(directory):
        for job_id in row.get("jobs", {}):
            if job_id not in ids:
                ids.append(job_id)
    return tuple(ids)


def _ibm(directory: Path) -> RunEnvelope:
    errors: list[str] = []
    voids: list[str] = []
    record = read_json(directory / "record.json")
    if not isinstance(record, dict):
        record = {}
        errors.append(f"{directory.name}: record.json is missing")
    job_ids = _ibm_job_ids(directory)
    if not job_ids:
        errors.append(f"{directory.name}: collect.json names no job")
    digests = raw_digests(directory)
    for job_id in job_ids:
        index = read_json(directory / "raw" / job_id / "index.json")
        files = index.get("files") if isinstance(index, dict) else None
        if not isinstance(files, dict) or not files:
            errors.append(f"raw/{job_id}/index.json records no file digests")
            continue
        for name, recorded in sorted(files.items()):
            observed = digests.get(f"raw/{job_id}/{name}")
            if observed != recorded:
                errors.append(f"raw/{job_id}/{name} differs from its recorded sha256")
    planned = record.get("submission", {}).get("planned_jobs", [])
    mismatches = record.get("approved_record", {}).get("mismatches", [])
    verdict = "ok"
    if record.get("state") == "approval_required" or mismatches:
        verdict = "live-differ"
        voids.append("the live calibration differs from the approved record")
    elif record.get("compiled_ideal_validation", {}).get("all_candidates_passed") is False:
        verdict = "compiled-differ"
        voids.append("a compiled candidate differs from its ideal circuit")
    statuses = set()
    billed = 0.0
    executed = 0
    for row in _ibm_collections(directory):
        for job in row.get("jobs", {}).values():
            usage = job.get("usage", {})
            statuses.add(str(usage.get("job_status", "unknown")).lower())
            billed += float(usage.get("qpu_charge_time_seconds") or 0.0)
            executed += int(usage.get("submitted_pub_shots") or 0)
    requested = sum(int(job["shots"]) * len(job.get("pubs", [])) for job in planned) if planned else None
    status = "completed" if statuses == {"done"} else ",".join(sorted(statuses)) or "unknown"
    backends = record.get("submission", {}).get("planned_backends", [])
    return RunEnvelope(
        provider="ibm",
        backend=",".join(backends),
        run_dir=display(directory),
        job_ids=job_ids,
        status=status,
        started_utc=record.get("started"),
        approval_present=approval_present("ibm", directory),
        raw_sha256=digests,
        requested_shots=requested,
        executed_shots=executed if job_ids else None,
        billed_cost=Cost("seconds", billed if job_ids else None),
        calibration_state="plan-matches-approved" if not mismatches else "plan-differs",
        health_verdict=verdict,
        void_reasons=tuple(voids),
        reader_errors=tuple(errors),
    )


def _quandela(directory: Path) -> RunEnvelope:
    errors: list[str] = []
    voids: list[str] = []
    submission = read_json(directory / "submission.json") or {}
    collected = read_json(directory / "results.json") or {}
    shots: int | None = None
    try:
        run = qd_records.read_run(directory)
        shots = run.shots
    except READER_ERRORS as error:
        errors.append(str(error))
    live = collected.get("couplers_checked", "unread")
    compiled = collected.get("compiled_couplers_checked", "unread")
    analysis = read_json(directory / "analysis.json")
    collapsed = analysis.get("routing_collapsed_jobs") if isinstance(analysis, dict) else None
    verdict = "unread" if live == "unread" and compiled == "unread" else "ok"
    if live == "live-differ":
        verdict = "live-differ"
        voids.append("the live architecture differs from the retained one")
    elif compiled == "differ":
        verdict = "compiled-differ"
        voids.append("the compiled couplers differ from the planned ones")
    elif collapsed:
        verdict = "routing_collapsed"
        voids.append(f"routing collapsed in {collapsed}")
    status = collected.get("status", {}).get("status", "unknown") if isinstance(collected, dict) else "unknown"
    return RunEnvelope(
        provider="quandela",
        backend=str(submission.get("platform", "")),
        run_dir=display(directory),
        job_ids=(submission["job_id"],) if text_present(submission.get("job_id")) else (),
        status=str(status),
        started_utc=submission.get("submitted_utc"),
        approval_present=approval_present("quandela", directory),
        raw_sha256=raw_digests(directory),
        requested_shots=submission.get("estimated_shots"),
        executed_shots=shots,
        billed_cost=Cost("credits", None),
        calibration_state=f"couplers:{live}/compiled:{compiled}",
        health_verdict=verdict,
        void_reasons=tuple(voids),
        reader_errors=tuple(errors),
    )


def _iqm(directory: Path) -> RunEnvelope:
    errors: list[str] = []
    submission = read_json(directory / "submission.json") or {}
    results = read_json(directory / "results.json") or {}
    requested: int | None = None
    executed: int | None = None
    billed: float | None = None
    state = "unread"
    try:
        run = iqm_records.read_run(directory)
        requested = int(run.row["shots"]) * len(run.row["circuits"])
        executed = sum(int(n) for n in run.results["shots_per_circuit"])
        billed = float(run.results.get("credits_charged") or 0.0)
        state = f"calibration_set:{run.results.get('compilation', {}).get('calibration_set_id')}"
    except READER_ERRORS as error:
        errors.append(str(error))
    return RunEnvelope(
        provider="iqm",
        backend=str(submission.get("qc", "")),
        run_dir=display(directory),
        job_ids=(submission["job_id"],) if text_present(submission.get("job_id")) else (),
        status=str(results.get("status", "unknown")),
        started_utc=submission.get("submitted_at"),
        approval_present=approval_present("iqm", directory),
        raw_sha256=raw_digests(directory),
        requested_shots=requested,
        executed_shots=executed,
        billed_cost=Cost("credits", billed),
        calibration_state=state,
        health_verdict="unread",
        reader_errors=tuple(errors),
    )


def _qi(directory: Path) -> RunEnvelope:
    errors: list[str] = []
    submission = read_json(directory / "submission.json") or {}
    jobs: tuple[qi_records.Job, ...] = ()
    created: str | None = None
    backend = str(submission.get("backend", ""))
    requested: int | None = None
    try:
        acquisition = qi_records.read_run(directory)
        jobs = acquisition.jobs
        created = acquisition.created_at
        backend = acquisition.backend
        requested = acquisition.shots * len(jobs)
    except READER_ERRORS as error:
        errors.append(str(error))
    readouts = sum(1 for job in jobs if job.file.startswith("readout-"))
    statuses = sorted({job.status for job in jobs})
    return RunEnvelope(
        provider="qi",
        backend=backend,
        run_dir=display(directory),
        job_ids=tuple(str(job.job_id) for job in jobs),
        status=",".join(statuses) if statuses else "unknown",
        started_utc=submission.get("submitted_utc") or created,
        approval_present=approval_present("qi", directory),
        raw_sha256=raw_digests(directory),
        requested_shots=requested,
        executed_shots=sum(job.shots_done for job in jobs) if jobs else None,
        billed_cost=Cost("credits", None),
        calibration_state="batch-readout-pair" if readouts >= 2 else "no-readout-pair",
        health_verdict="unread",
        reader_errors=tuple(errors),
    )


def read_envelope(provider: str, directory: Path) -> RunEnvelope:
    """The envelope of one run directory; a record the reader rejects lands in reader_errors, never an exception."""
    builders = {"ibm": _ibm, "quandela": _quandela, "iqm": _iqm, "qi": _qi}
    if provider not in builders:
        raise ValueError(f"provider {provider!r} is not one of {PROVIDERS}")
    try:
        return builders[provider](directory)
    except READER_ERRORS as error:
        return RunEnvelope(
            provider=provider,
            backend="",
            run_dir=display(directory),
            job_ids=(),
            status="unreadable",
            started_utc=None,
            approval_present=False,
            raw_sha256={},
            requested_shots=None,
            executed_shots=None,
            billed_cost=Cost("unknown", None),
            calibration_state="unread",
            health_verdict="unread",
            reader_errors=(f"{type(error).__name__}: {error}",),
        )


def run_directories(provider: str, root: Path | None = None) -> list[Path]:
    """The retained run directories of a provider, sorted by name."""
    base = root if root is not None else RUN_ROOTS[provider]
    if not base.is_dir():
        return []
    marker = "record.json" if provider == "ibm" else "submission.json"
    return sorted(path for path in base.iterdir() if path.is_dir() and (path / marker).is_file())


def envelopes(provider: str, root: Path | None = None) -> list[RunEnvelope]:
    """One RunEnvelope per retained run of the provider."""
    return [read_envelope(provider, directory) for directory in run_directories(provider, root)]

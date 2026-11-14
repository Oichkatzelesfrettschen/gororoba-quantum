"""Wave submission of Quantum Inspire hardware batches: the policy table, the admission rule, and the submit and collect
routes of a case manifest that selects a policy.

scripts/qi_platform.py keeps its bytes, which retained run receipts, proposals and projector-geometry records pin by
sha256, and its `submit` admits one queued batch of at most three circuits (the legacy row below). This module is the
versioned successor for a case that needs more, and it calls the functions `qi_platform` exports without editing them.

Policy. A manifest selects a row of HARDWARE_POLICIES through its `hardware_policy` field; a manifest without the field
takes the `legacy` row. The FAQ allows three queued jobs per hardware backend and does not say whether a "job" is a
circuit or a batch (docs/notes/quantum_inspire/usage.md, "Queue rules"); the API counts its queue in batches.

- `legacy`: a batch of at most 3 circuits and 1 queued batch, which satisfies both readings of "job"; an unfinished job
  on any hardware backend type refuses, and the pause between jobs is the ladder step QI_HARDWARE_PAUSE_SECONDS selects
  (30 s by default).
- `wave-v1`: the batch-job reading (owner ruling 2026-11-14), a batch of at most 5 circuits and no more than 3 queued
  batches. A wave is 3 batches submitted back to back (fewer for the last wave of a series). Every batch of a wave
  finishes, then a pause of `pause_seconds` (60 s, a step of the ladder 30, 60, 90, 120) passes, and only then the next
  wave is queued. A higher ladder step from QI_HARDWARE_PAUSE_SECONDS raises the pause and never lowers it.

Both numbers of a row are capped by the backend record (`max_jobs_per_batch_job`, `batchjobs_per_queue_limit`).

Admission (`hardware_admission`). Under a wave policy the account's unfinished batches on the backend type to submit are
the earlier batches of the wave: they count as in flight, and their jobs set no pause. An unfinished job on another
hardware backend type refuses, every finished job keeps its pause, and a batch is refused once the batches in flight
reach the row's queued count. A batch the service lists as queued, reserved or running with no listed job refuses,
unless it is an earlier batch of the same backend type under a wave row. The pause clock is account-wide across every
`is_hardware` type. The checks read one snapshot of the account and the local SUBMIT_LOCK excludes only sessions on one
host, so the limit is not enforced across hosts, and the service owns the execution order of the queued batches (its
terms allow priority without regard to the queue order), so an estimator that needs an order reads the retained
`queued_at` times.

An unknown or non-string policy name is refused before any service read, and every refusal precedes the first remote
write.

Usage: "$QI_PYTHON" scripts/qi_platform_wave.py
       (submit CASE_DIR --backend-type-id N --approval TEXT | collect CASE_DIR [--poll S --timeout S]
        | series SERIES_DIR RUNS_DIR STAMP --backend-type-id N --approval TEXT [--sanity-command CMD])
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import qi_platform


class HardwarePolicy(NamedTuple):
    """One row of HARDWARE_POLICIES; `pause_seconds` is None for the ladder step QI_HARDWARE_PAUSE_SECONDS selects."""

    batch_circuits: int
    queued_batches: int
    pause_seconds: int | None


HARDWARE_POLICIES: dict[str, HardwarePolicy] = {
    "legacy": HardwarePolicy(batch_circuits=3, queued_batches=1, pause_seconds=None),
    "wave-v1": HardwarePolicy(batch_circuits=5, queued_batches=3, pause_seconds=60),
}
DEFAULT_HARDWARE_POLICY = "legacy"
# A batch the service lists as queued, reserved or running holds a queue slot even when the job read omits its jobs.
IN_FLIGHT_BATCH_STATUSES = {"queued", "reserved", "running"}
PAUSE_REFUSAL = re.compile(r"wait (\d+) more seconds")
for _name, _row in HARDWARE_POLICIES.items():
    if _row.pause_seconds is not None and _row.pause_seconds not in qi_platform.HARDWARE_PAUSE_LADDER:
        raise SystemExit(f"hardware policy {_name!r} pauses {_row.pause_seconds} s, not a step of the pause ladder")


class PauseRefused(SystemExit):
    """An admission refusal that names the seconds left in the pause; the series driver sleeps that long and retries."""

    def __init__(self, message: str, seconds: int) -> None:
        super().__init__(message)
        self.seconds = seconds


def hardware_policy(cases: dict[str, Any]) -> HardwarePolicy:
    """The row of HARDWARE_POLICIES a manifest selects by `hardware_policy`; a missing field selects the legacy row."""
    name = cases.get("hardware_policy", DEFAULT_HARDWARE_POLICY)
    if type(name) is not str or name not in HARDWARE_POLICIES:
        raise SystemExit(f"cases.json hardware_policy {name!r} is not one of {sorted(HARDWARE_POLICIES)}")
    return HARDWARE_POLICIES[name]


def hardware_limits(cases: dict[str, Any], backend_type: dict[str, Any]) -> HardwarePolicy:
    """The policy's circuits per batch and queued batches, each capped by the backend record; the pause is unchanged."""
    policy = hardware_policy(cases)
    return policy._replace(
        batch_circuits=min(policy.batch_circuits, backend_type["max_jobs_per_batch_job"]),
        queued_batches=min(policy.queued_batches, backend_type["batchjobs_per_queue_limit"]),
    )


def pause_seconds(policy: HardwarePolicy) -> int:
    """The pause between waves in seconds: the row's own, raised to the QI_HARDWARE_PAUSE_SECONDS ladder step."""
    ladder = qi_platform.HARDWARE_PAUSE_SECONDS
    return ladder if policy.pause_seconds is None else max(policy.pause_seconds, ladder)


def hardware_pause_state(
    client: qi_platform.Client, pause: int, wave_backend_type_id: int | None = None
) -> tuple[int, int]:
    """(seconds until every finished hardware job is `pause` seconds old, batches in flight).

    A job counts when its batch runs on a backend type with is_hardware set. An unfinished job refuses the batch, except
    in a batch that stayed un-enqueued for ABANDONED_PLANNING_SECONDS. `wave_backend_type_id` names the backend type of
    a wave policy's batch: its unfinished batches count as in flight and their jobs set no pause. Without it every
    unfinished hardware job refuses.
    """
    types = {row["id"] for row in client.pages("/backend_types/") if row["is_hardware"]}
    at = qi_platform.utc_now()
    batches: dict[int, int] = {}
    batch_status: dict[int, str] = {}
    for row in client.pages("/batch_jobs"):
        if row["backend_type_id"] not in types:
            continue
        if row["status"] == "planned":
            age = (at - datetime.datetime.fromisoformat(row["created_on"])).total_seconds()
            if age < qi_platform.ABANDONED_PLANNING_SECONDS:
                raise SystemExit(f"hardware batch {row['id']} is being planned; wait until it is enqueued")
            continue
        batches[row["id"]] = row["backend_type_id"]
        batch_status[row["id"]] = row["status"]
    jobs = [job for job in client.pages("/jobs") if job["batch_job_id"] in batches]
    listed = {job["batch_job_id"] for job in jobs}
    for batch_id, row_status in batch_status.items():
        own_type = wave_backend_type_id is not None and batches[batch_id] == wave_backend_type_id
        if row_status in IN_FLIGHT_BATCH_STATUSES and batch_id not in listed and not own_type:
            # The job read omits an active batch: its jobs cannot show it finishing, so it refuses as an unfinished job.
            raise SystemExit(
                f"hardware batch {batch_id} is {row_status} without a listed job; wait until the jobs finish"
            )
    in_flight: set[int] = set()
    if wave_backend_type_id is not None:
        in_flight = {
            job["batch_job_id"]
            for job in jobs
            if job["status"] not in qi_platform.TERMINAL and batches[job["batch_job_id"]] == wave_backend_type_id
        } | {
            batch_id
            for batch_id, row_status in batch_status.items()
            if row_status in IN_FLIGHT_BATCH_STATUSES and batches[batch_id] == wave_backend_type_id
        }
    left = 0.0
    for job in jobs:
        if job["batch_job_id"] in in_flight:
            continue
        if job["status"] not in qi_platform.TERMINAL:
            raise SystemExit(f"hardware job {job['id']} is {job['status']}; wait until the account's jobs finish")
        if job["finished_at"] is None:
            raise SystemExit(f"hardware job {job['id']} is {job['status']} without a finish time; its pause is unknown")
        elapsed = (at - datetime.datetime.fromisoformat(job["finished_at"])).total_seconds()
        left = max(left, pause - elapsed)
    return math.ceil(left), len(in_flight)


def hardware_admission(
    client: qi_platform.Client,
    cases: dict[str, Any],
    backend_type: dict[str, Any],
    backend_type_id: int,
    circuits: int,
    queue_limit: int,
) -> tuple[int, int]:
    """(queue limit, pause seconds left) of a batch of `circuits` circuits on a hardware backend type, or SystemExit.

    The batch holds at most the policy's circuits. Under the legacy row no account job on any hardware type may be
    unfinished. Under a wave row the account's earlier batches on this type may be unfinished, and the batch is
    refused once the batches in flight reach the row's queued count; a refusal for the pause is a PauseRefused.
    """
    limits = hardware_limits(cases, backend_type)
    if circuits > limits.batch_circuits:
        raise SystemExit(f"{circuits} circuits exceed the {limits.batch_circuits} a hardware batch may hold")
    queue_limit = min(queue_limit, limits.queued_batches)
    pause = pause_seconds(limits)
    wave = limits.queued_batches > 1
    left, in_flight = hardware_pause_state(client, pause, backend_type_id if wave else None)
    if in_flight + 1 > limits.queued_batches:
        raise SystemExit(
            f"the account has {in_flight} batches in flight; adding one exceeds the limit {limits.queued_batches}"
        )
    if left > 0:
        raise PauseRefused(
            f"the account's last hardware job finished less than {pause} s ago; "
            f"wait {left} more seconds so the platform can calibrate",
            left,
        )
    return queue_limit, left


def submit(
    case_dir: Path,
    backend_type_id: int,
    approval: str,
    *,
    expected_cases_sha256: str | None = None,
    execution_deadline: float | None = None,
) -> dict[str, Any]:
    """Submit one case batch under its manifest's hardware policy while holding the account submit lock.

    Every local process holds qi_platform.SUBMIT_LOCK from the admission checks until its batch is enqueued, so two
    sessions on this host cannot both pass the checks before either batch exists on the service.
    """
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        return _submit(
            case_dir,
            backend_type_id,
            approval,
            expected_cases_sha256=expected_cases_sha256,
            execution_deadline=execution_deadline,
        )


def _submit(
    case_dir: Path,
    backend_type_id: int,
    approval: str,
    *,
    expected_cases_sha256: str | None = None,
    execution_deadline: float | None = None,
) -> dict[str, Any]:
    """The submission of qi_platform._submit with hardware_admission in place of its fixed hardware limits: the same
    refusals before the first write, the same exclusive state file, receipts and enqueue order."""
    check = qi_platform._check_execution_deadline
    check(execution_deadline)
    if (case_dir / "preflight-refusal.json").exists():
        raise SystemExit("preflight-refusal.json exists; retain the refusal and prepare a separately approved case")
    if (case_dir / "submission.json").exists():
        raise SystemExit(f"{case_dir}/submission.json exists; this case was submitted")
    state_path = case_dir / "submission-state.json"
    if state_path.exists():
        raise SystemExit(f"{state_path} exists; run reconcile for read-only recovery, never repeat submit")
    if not approval.strip():
        raise SystemExit("a nonempty approval is required")
    cases_bytes = (case_dir / "cases.json").read_bytes()
    if expected_cases_sha256 is not None and hashlib.sha256(cases_bytes).hexdigest() != expected_cases_sha256:
        raise SystemExit("cases.json differs from the approved manifest digest; renewed case approval is required")
    cases = json.loads(cases_bytes)
    hardware_policy(cases)
    if cases["backend_type_id"] != backend_type_id:
        raise SystemExit(f"cases.json names backend type {cases['backend_type_id']}, not {backend_type_id}")
    if not isinstance(cases["shots"], int) or isinstance(cases["shots"], bool) or cases["shots"] < 1:
        raise SystemExit("shots must be a positive integer")
    sources = {}
    digests = {}
    for row in cases["circuits"]:
        source_bytes = (case_dir / row["file"]).read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != row["sha256"]:
            raise SystemExit(f"{row['file']} differs from its cases.json sha256")
        sources[row["file"]] = source_bytes.decode("utf-8")
        digests[row["file"]] = row["sha256"]
    if not sources or len(sources) != len(cases["circuits"]):
        raise SystemExit("cases.json needs at least one circuit and unique circuit filenames")
    widths = qi_platform._case_qubit_widths(cases, sources)
    client = qi_platform.Client()
    backend_type = client.get(f"/backend_types/{backend_type_id}")
    if backend_type["identifier"] != cases["backend"]:
        raise SystemExit(f"backend type {backend_type_id} is {backend_type['identifier']}, not {cases['backend']}")
    if backend_type["status"] == "offline":
        raise SystemExit(f"{backend_type['name']} is offline")
    capacity = backend_type.get("nqubits")
    if type(capacity) is not int or capacity < 1:
        raise qi_platform.PlatformError("backend nqubits capacity is not a positive integer")
    for file_name, width in widths.items():
        if width > capacity:
            raise SystemExit(f"{file_name}: declared width {width} exceeds backend nqubits {capacity}")
    if len(sources) > backend_type["max_jobs_per_batch_job"]:
        raise SystemExit(f"{len(sources)} circuits exceed max_jobs_per_batch_job")
    if cases["shots"] > backend_type["max_number_of_shots"]:
        raise SystemExit("shots exceed max_number_of_shots")
    queue = client.get(f"/backend_types/{backend_type_id}/queue", user_only=True)
    queue_limit = backend_type["batchjobs_per_queue_limit"]
    queued = queue["number_of_jobs_in_queue"]
    if type(queue_limit) is not int or queue_limit < 0 or type(queued) is not int or queued < 0:
        raise qi_platform.PlatformError("queue capacity or current-user queue count is invalid")
    if backend_type["is_hardware"]:
        queue_limit, _left = hardware_admission(client, cases, backend_type, backend_type_id, len(sources), queue_limit)
    if queued + 1 > queue_limit:
        raise SystemExit(f"current-user queue has {queued} batches; adding one exceeds the limit {queue_limit}")
    language = next(lang for lang in client.pages("/languages") if lang["name"] == "cQASM" and lang["version"] == "3.0")
    state: dict[str, Any] = {
        "schema": qi_platform.SUBMISSION_STATE_SCHEMA,
        "phase": "creating",
        "started_utc": qi_platform.now(),
        "approval": approval,
        "backend": cases["backend"],
        "backend_type_id": backend_type_id,
        "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
        "shots": cases["shots"],
        "jobs": [],
    }
    check(execution_deadline)
    try:
        qi_platform._write_json(state_path, state, exclusive=True)
    except FileExistsError:
        raise SystemExit(f"{state_path} exists; another submission owns this case") from None
    name = f"gororoba-{case_dir.name}"[:32]
    try:
        check(execution_deadline)
    except TimeoutError:
        state.update(phase="pre-dispatch-refused", resource_requests_dispatched=0)
        qi_platform._write_json(state_path, state)
        raise
    try:
        project = client.post(
            "/projects",
            {"owner_id": client.member_id, "name": name, "description": name, "starred": False},
            execution_deadline=execution_deadline,
        )
    except qi_platform.RequestNotDispatched:
        state.update(phase="pre-dispatch-refused", resource_requests_dispatched=0)
        qi_platform._write_json(state_path, state)
        raise
    except qi_platform.RequestRejectedBeforeRetry as error:
        if error.method == "POST" and error.path == "/projects":
            # RFC 9110 section 15.5.2: a received 401 means the request was not applied; the expired-signature 403
            # fails the same bearer check.
            state.update(
                phase="resource-request-rejected",
                resource_request_attempted=True,
                resource_requests_dispatched=1,
                resource_requests_applied=0,
                rejected_request=error.receipt(),
            )
            qi_platform._write_json(state_path, state)
        raise
    state["project"] = project["id"]
    qi_platform._write_json(state_path, state)
    batch = client.post("/batch_jobs", {"backend_type_id": backend_type_id})
    state["batch_job"] = batch["id"]
    qi_platform._write_json(state_path, state)
    jobs: list[dict[str, Any]] = state["jobs"]
    for file_name, text in sources.items():
        algorithm = client.post(
            "/algorithms", {"project_id": project["id"], "type": "quantum", "shared": "private", "name": file_name}
        )
        commit = client.post("/commits", {"description": name, "algorithm_id": algorithm["id"]})
        file = client.post(
            "/files",
            {
                "commit_id": commit["id"],
                "content": text,
                "language_id": language["id"],
                "compile_stage": "none",
                "compile_properties": {},
                "name": file_name,
            },
        )
        job = client.post(
            "/jobs",
            {
                "file_id": file["id"],
                "batch_job_id": batch["id"],
                "number_of_shots": cases["shots"],
                "raw_data_enabled": True,
            },
        )
        jobs.append({"file": file_name, "job": job["id"], "sha256": digests[file_name]})
        qi_platform._write_json(state_path, state)
    record = {
        "schema": qi_platform.SUBMISSION_SCHEMA,
        "state": "created",
        "created_utc": qi_platform.now(),
        "approval": approval,
        "backend": cases["backend"],
        "backend_type_id": backend_type_id,
        "cases_sha256": state["cases_sha256"],
        "backend_status_at_submit": backend_type["status"],
        "queue_at_submit": queue,
        "queue_user_only": True,
        "queue_limit_at_submit": queue_limit,
        "batch_job": batch["id"],
        "project": project["id"],
        "shots": cases["shots"],
        "jobs": jobs,
    }
    state["submission"] = record
    # Record uncertainty before sending: interruption or a lost response cannot leave an apparently unused case that a
    # second invocation can enqueue.
    state["phase"] = "enqueue_outcome_unknown"
    qi_platform._write_json(state_path, state)
    client.patch(f"/batch_jobs/{batch['id']}/enqueue")
    record.update(state="enqueued", submitted_utc=qi_platform.now())
    state["phase"] = "enqueued"
    state["confirmed_utc"] = record["submitted_utc"]
    qi_platform._write_json(state_path, state)
    qi_platform._retain_json(case_dir / "submission.json", record)
    return record


def collect(case_dir: Path, poll: float, timeout: float, *, execution_deadline: float | None = None) -> None:
    """Collect one submitted batch: the raw shots, results and charges of qi_platform.collect, which holds no
    hardware limit, so a wave batch collects as any other batch does."""
    qi_platform.collect(case_dir, poll, timeout, execution_deadline=execution_deadline)


def series_waves(series_dir: Path) -> list[list[str]]:
    """The submission waves a series' cases.json lists, each a list of batch directory names in submission order; every
    batch directory appears in exactly one wave."""
    index = json.loads((series_dir / "cases.json").read_text(encoding="utf-8"))
    waves = index["waves"]
    listed = [name for wave in waves for name in wave]
    held = sorted(path.name for path in series_dir.glob("batch-*") if path.is_dir())
    if sorted(listed) != held:
        raise SystemExit(f"{series_dir}/cases.json waves list {sorted(listed)}, the directory holds {held}")
    limit = hardware_policy(index).queued_batches
    if any(not 1 <= len(wave) <= limit for wave in waves):
        raise SystemExit(f"a wave holds more than the {limit} batches of the {index.get('hardware_policy')} policy")
    return [list(wave) for wave in waves]


def run_series(
    series_dir: Path,
    runs_dir: Path,
    stamp: str,
    backend_type_id: int,
    approval: str,
    *,
    poll: float = 15.0,
    timeout: float = 3600.0,
    sanity: Callable[[Path], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    max_pause_refusals: int = 10,
) -> list[Path]:
    """Submit and collect a series wave by wave: the batches of a wave are submitted back to back, every batch of the
    wave is collected in series order (`sanity` runs on each collected run directory), and the next wave is submitted
    only after that, when admission refuses a batch for the pause and this function sleeps the remainder plus one second
    and retries (at most `max_pause_refusals` times in a row). A refusal that names no pause, a failed collection and a
    failed sanity check stop the series. A run directory that exists is never resubmitted, and every destination is
    checked before the first submission.

    The driver resumes nothing: a stop leaves the batches it submitted queued on the service with their run directories,
    which `collect` (after `reconcile` for an uncertain enqueue) recovers one by one, and the batches it never
    submitted run from a fresh copy of the case."""
    series_dir = series_dir.resolve()
    waves = series_waves(series_dir)
    for wave in waves:
        for batch in wave:
            run = runs_dir / f"{stamp}-{series_dir.name}-{batch}"
            if run.exists():
                raise SystemExit(f"{run} exists; a submitted batch is never resubmitted")
    runs_dir.mkdir(parents=True, exist_ok=True)
    done: list[Path] = []
    for wave in waves:
        submitted: list[Path] = []
        for batch in wave:
            run = runs_dir / f"{stamp}-{series_dir.name}-{batch}"
            if run.exists():
                raise SystemExit(f"{run} exists; a submitted batch is never resubmitted")
            shutil.copytree(series_dir / batch, run)
            refusals = 0
            while True:
                try:
                    submit(run, backend_type_id, approval)
                    break
                except PauseRefused as refusal:
                    refusals += 1
                    if refusals >= max_pause_refusals:
                        raise
                    sleep(refusal.seconds + 1)
            submitted.append(run)
        for run in submitted:
            collect(run, poll, timeout)
            if sanity is not None:
                sanity(run)
            done.append(run)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("submit")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--backend-type-id", type=int, required=True)
    p.add_argument("--approval", required=True, help="the user's approval, quoted, recorded in submission.json")
    p = sub.add_parser("collect")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--poll", type=float, default=15.0)
    p.add_argument("--timeout", type=float, default=3600.0)
    p = sub.add_parser("series")
    p.add_argument("series_dir", type=Path)
    p.add_argument("runs_dir", type=Path)
    p.add_argument("stamp")
    p.add_argument("--backend-type-id", type=int, required=True)
    p.add_argument("--approval", required=True, help="the user's approval, quoted, recorded in every submission.json")
    p.add_argument("--poll", type=float, default=15.0)
    p.add_argument("--timeout", type=float, default=3600.0)
    p.add_argument("--sanity-command", help="a command that takes the collected run directory as its last argument")
    args = parser.parse_args()
    try:
        if args.command == "submit":
            record = submit(args.case_dir, args.backend_type_id, args.approval)
            print(f"batch {record['batch_job']}: jobs {[row['job'] for row in record['jobs']]}")
        elif args.command == "collect":
            collect(args.case_dir, args.poll, args.timeout)
        else:
            check: Callable[[Path], None] | None = None
            if args.sanity_command:
                words = shlex.split(args.sanity_command)

                def check(run: Path) -> None:
                    subprocess.run([*words, str(run)], check=True)

            run_series(
                args.series_dir,
                args.runs_dir,
                args.stamp,
                args.backend_type_id,
                args.approval,
                poll=args.poll,
                timeout=args.timeout,
                sanity=check,
            )
    except qi_platform.PlatformError as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    sys.exit(main())

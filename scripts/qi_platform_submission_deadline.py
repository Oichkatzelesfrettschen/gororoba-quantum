"""Submit with a deadline bound to every Quantum Inspire resource/API request.

The frozen platform module supplies validation, authentication, locks and durable
receipts. The successor client binds every inherited GET, page, POST and PATCH to
one finite monotonic deadline, including authenticated retries. An in-flight
request or SDK authentication exchange may finish after that deadline; the next
resource request still checks its initiation time. Authentication refresh keeps
the frozen SDK's token lock and rotation rules; its requests have a separate boundary.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

import qi_platform

AdmissionCheck = Callable[["Client", dict[str, Any], dict[str, Any], int], None]


def check_deadline(deadline: float) -> None:
    """Require a finite numeric monotonic deadline before initiating a request."""
    if type(deadline) not in (int, float) or not math.isfinite(deadline):
        raise ValueError("execution deadline must be a finite number excluding Boolean")
    qi_platform._check_execution_deadline(deadline)


class Client(qi_platform.Client):
    """Constrain every inherited request and authentication retry to one deadline."""

    def __init__(self, execution_deadline: float) -> None:
        check_deadline(execution_deadline)
        self.execution_deadline = execution_deadline
        super().__init__()

    def request(self, method: str, path: str, *, execution_deadline: float | None = None, **kwargs: Any) -> Any:
        deadline = self.execution_deadline
        if execution_deadline is not None:
            if type(execution_deadline) not in (int, float) or not math.isfinite(execution_deadline):
                raise ValueError("explicit execution deadline must be a finite number excluding Boolean")
            deadline = min(deadline, execution_deadline)
        try:
            check_deadline(deadline)
        except TimeoutError as error:
            raise qi_platform.RequestNotDispatched(str(error)) from error
        return super().request(method, path, execution_deadline=deadline, **kwargs)

    def patch(self, path: str, *, execution_deadline: float | None = None) -> Any:
        return self.request("PATCH", path, execution_deadline=execution_deadline)


def submit(
    case_dir: Path,
    backend_type_id: int,
    approval: str,
    *,
    expected_cases_sha256: str | None = None,
    execution_deadline: float,
    admission_check: AdmissionCheck | None = None,
) -> dict[str, Any]:
    """Submit one case batch while holding the account submit lock.

    Every local process holds qi_platform.SUBMIT_LOCK from the pause and queue checks
    until its batch is enqueued, so two sessions on this host cannot both pass
    the checks before either batch exists on the service.
    """
    with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
        return _submit(
            case_dir,
            backend_type_id,
            approval,
            expected_cases_sha256=expected_cases_sha256,
            execution_deadline=execution_deadline,
            admission_check=admission_check,
        )


def _submit(
    case_dir: Path,
    backend_type_id: int,
    approval: str,
    *,
    expected_cases_sha256: str | None = None,
    execution_deadline: float,
    admission_check: AdmissionCheck | None = None,
) -> dict[str, Any]:
    check_deadline(execution_deadline)
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
    client = Client(execution_deadline)
    backend_type = client.get(f"/backend_types/{backend_type_id}")
    if backend_type["identifier"] != cases["backend"]:
        raise SystemExit(f"backend type {backend_type_id} is {backend_type['identifier']}, not {cases['backend']}")
    if backend_type["status"] == "offline":
        raise SystemExit(f"{backend_type['name']} is offline")
    if backend_type.get("enabled") is not True:
        raise SystemExit("the backend type is disabled")
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
    # The API names '(batch) job queue statistics'. Both retained five-circuit
    # Tuna-17 receipts report queue count 2 before any child-job queued_at
    # timestamp. Treat it as batches; the separate circuit limit is above.
    queue_limit = backend_type["batchjobs_per_queue_limit"]
    queued = queue["number_of_jobs_in_queue"]
    if type(queue_limit) is not int or queue_limit < 0 or type(queued) is not int or queued < 0:
        raise qi_platform.PlatformError("queue capacity or current-user queue count is invalid")
    pause = 0
    if backend_type["is_hardware"]:
        if len(sources) > qi_platform.HARDWARE_BATCH_CIRCUITS:
            raise SystemExit(
                f"{len(sources)} circuits exceed the {qi_platform.HARDWARE_BATCH_CIRCUITS} a hardware batch may hold"
            )
        queue_limit = min(queue_limit, qi_platform.HARDWARE_QUEUED_BATCHES)
        pause = qi_platform.hardware_pause_left(client)
        if pause > 0:
            raise SystemExit(
                f"the account's last hardware job finished less than {qi_platform.HARDWARE_PAUSE_SECONDS} s ago; "
                f"wait {pause} more seconds so the platform can calibrate"
            )
    if queued + 1 > queue_limit:
        raise SystemExit(f"current-user queue has {queued} batches; adding one exceeds the limit {queue_limit}")
    if admission_check is not None:
        admission_check(client, backend_type, queue, pause)
    language = next(lang for lang in client.pages("/languages") if lang["name"] == "cQASM" and lang["version"] == "3.0")
    state: dict[str, Any] = {
        "schema": qi_platform.SUBMISSION_STATE_SCHEMA,
        "phase": "creating",
        "started_utc": qi_platform.utc_now().isoformat(),
        "approval": approval,
        "backend": cases["backend"],
        "backend_type_id": backend_type_id,
        "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
        "shots": cases["shots"],
        "jobs": [],
        "created_resources": [],
    }
    check_deadline(execution_deadline)
    try:
        qi_platform._write_json(state_path, state, exclusive=True)
    except FileExistsError:
        raise SystemExit(f"{state_path} exists; another submission owns this case") from None
    name = f"gororoba-{case_dir.name}"[:32]
    try:
        check_deadline(execution_deadline)
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
            # RFC 9110 section 15.5.2: a received 401 means the request was not
            # applied; the expired-signature 403 fails the same bearer check.
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
        resources: dict[str, Any] = {"circuit_file": file_name}
        state["created_resources"].append(resources)
        algorithm = client.post(
            "/algorithms", {"project_id": project["id"], "type": "quantum", "shared": "private", "name": file_name}
        )
        resources["algorithm"] = algorithm["id"]
        qi_platform._write_json(state_path, state)
        commit = client.post("/commits", {"description": name, "algorithm_id": algorithm["id"]})
        resources["commit"] = commit["id"]
        qi_platform._write_json(state_path, state)
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
        resources["file"] = file["id"]
        qi_platform._write_json(state_path, state)
        job = client.post(
            "/jobs",
            {
                "file_id": file["id"],
                "batch_job_id": batch["id"],
                "number_of_shots": cases["shots"],
                "raw_data_enabled": True,
            },
        )
        resources["job"] = job["id"]
        jobs.append({"file": file_name, "job": job["id"], "sha256": digests[file_name]})
        qi_platform._write_json(state_path, state)
    record = {
        "schema": qi_platform.SUBMISSION_SCHEMA,
        "state": "created",
        "created_utc": qi_platform.utc_now().isoformat(),
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
    # Record uncertainty before sending: interruption or a lost response cannot
    # leave an apparently unused case that a second invocation can enqueue.
    state["phase"] = "enqueue_outcome_unknown"
    qi_platform._write_json(state_path, state)
    try:
        client.patch(f"/batch_jobs/{batch['id']}/enqueue")
    except qi_platform.RequestNotDispatched:
        state["phase"] = "enqueue-refused-before-dispatch"
        qi_platform._write_json(state_path, state)
        raise
    record.update(state="enqueued", submitted_utc=qi_platform.utc_now().isoformat())
    state["phase"] = "enqueued"
    state["confirmed_utc"] = record["submitted_utc"]
    qi_platform._write_json(state_path, state)
    qi_platform._retain_json(case_dir / "submission.json", record)
    return record


def collect(case_dir: Path, poll: float, timeout: float, *, execution_deadline: float) -> None:
    """Initiate collection requests within the local window; server completion is unbounded."""
    check_deadline(execution_deadline)
    record = json.loads((case_dir / "submission.json").read_text(encoding="utf-8"))
    qi_platform._check_submission_manifest(case_dir, record, require_enqueued=True)
    deadline = time.monotonic() + timeout
    deadline = min(deadline, execution_deadline)
    client = Client(deadline)
    request_options = {"execution_deadline": deadline}
    while True:
        check_deadline(deadline)
        states = {row["job"]: client.get(f"/jobs/{row['job']}", **request_options) for row in record["jobs"]}
        if all(job["status"] in qi_platform.TERMINAL for job in states.values()):
            break
        if time.monotonic() > deadline:
            raise SystemExit(f"jobs still running: { {k: v['status'] for k, v in states.items()} }")
        time.sleep(min(poll, max(0.0, deadline - time.monotonic())))
    raw_dir = case_dir / "raw"
    raw: dict[str, list[str]] = {}
    rows = []
    for row in record["jobs"]:
        job = states[row["job"]]
        if job["id"] != row["job"] or job["batch_job_id"] != record["batch_job"]:
            raise qi_platform.PlatformError(f"job {row['job']} differs from submission.json")
        if job["number_of_shots"] != record["shots"]:
            raise qi_platform.PlatformError(f"job {row['job']} shot count differs from submission.json")
        results = client.get(f"/results/job/{row['job']}", **request_options, page=1, size=100)["items"]
        logs = None
        if job["status"] != "completed":
            logs = client.get(f"/jobs/{row['job']}/logs", **request_options)
            if results:
                raise qi_platform.PlatformError(f"{job['status']} job {row['job']} unexpectedly holds results")
        else:
            if len(results) != 1:
                raise qi_platform.PlatformError(f"completed job {row['job']} needs exactly one result")
            result = results[0]
            shots = result["raw_data"]
            if (
                result["job_id"] != row["job"]
                or result["shots_requested"] != record["shots"]
                or not isinstance(shots, list)
                or len(shots) != result["shots_done"]
                or not 0 <= result["shots_done"] <= record["shots"]
                or Counter(shots) != Counter(result["results"])
            ):
                raise qi_platform.PlatformError(f"job {row['job']} raw shots or result metadata disagree")
            raw[f"{row['file']}.json"] = shots
        rows.append(
            {
                "file": row["file"],
                "job": job,
                "results": [{k: v for k, v in r.items() if k != "raw_data"} for r in results],
                "logs": logs,
            }
        )
    job_ids = {row["job"] for row in record["jobs"]}
    charged = [
        {
            "id": t["id"],
            "timestamp": t["timestamp"],
            "domain": t["domain"],
            "change": t["change"],
            "job": t["job"],
        }
        for t in client.pages("/transactions/", **request_options)
        if t["job"] in job_ids
    ]
    collected = {
        "schema": "qi-collection-v1",
        "collected_utc": qi_platform.utc_now().isoformat(),
        "jobs": rows,
        "transactions": charged,
    }
    if raw_dir.exists() and {path.name for path in raw_dir.iterdir()} - set(raw):
        raise qi_platform.PlatformError("raw/ holds files outside the completed jobs; retained files were left intact")
    # Validate the entire recollection before publishing any new file. Ordered
    # list equality detects a permutation even when the histogram is unchanged.
    for name, shots in raw.items():
        qi_platform._retained_matches(raw_dir / name, shots)
    qi_platform._retained_matches(case_dir / "results.json", collected, ignore_collection_time=True)
    raw_dir.mkdir(exist_ok=True)
    for name, shots in raw.items():
        qi_platform._retain_json(raw_dir / name, shots)
    qi_platform._retain_json(case_dir / "results.json", collected, ignore_collection_time=True)
    for row in rows:
        print(row["file"], row["job"]["status"], [r["shots_done"] for r in row["results"]])

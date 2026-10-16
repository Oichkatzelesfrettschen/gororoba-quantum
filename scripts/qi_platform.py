"""Quantum Inspire account reads, batch submission and collection through the compute job manager REST API.

The quantuminspire SDK requires Python < 3.14 and qiskit-quantuminspire caps
Qiskit below 2.4, so this script runs under QI_PYTHON, the interpreter of the
pinned Quantum Inspire environment (docs/notes/quantum_inspire/setup.md), and
reads the OAuth tokens that `qi login` stores in ~/.quantuminspire/config.json.
Only --check runs under the repository's own $PYTHON; it imports nothing from
the Quantum Inspire stack.

Subcommands:

- snapshot --out DIR (network, read-only) writes catalogue.json (every
  backend type the account sees with its limits, topology and queue, every
  backend's status and heartbeat, the languages) and usage.json (the account's
  transaction ledger aggregated by domain, backend type and job, beside each
  job's shots and execution seconds). Team, member and user identifiers enter
  only as a 12-hex sha256; names, e-mail addresses and OIDC subjects never do.
- check DIR [--agents FILE] (offline) requires both files to carry their
  schema, the redacted identity form and a ledger whose aggregates equal the
  sum of its rows; with --agents it renders the structural backend table
  (facts_table) from catalogue.json and requires FILE to carry it verbatim
  between the quantum-inspire-facts markers, so a refreshed catalogue that
  changes a limit fails until AGENTS.md changes with it. Status, queue and
  heartbeat change minute to minute and stay out of the table.
- submit CASE_DIR --backend-type-id N --approval TEXT (network, spends quota)
  creates one project, one algorithm, commit and file per circuit, one batch
  job holding every circuit of cases.json, and enqueues it. It verifies each
  circuit's sha256 against cases.json first. An exclusive submission-state.json
  is retained before the first remote write; either it or submission.json
  prevents a repeat submission, including after an uncertain enqueue response.
- reconcile CASE_DIR (network, read-only) reads the recorded batch and jobs.
  Once the service confirms that the complete batch was enqueued, it recovers
  submission.json for collection. It never enqueues or creates resources.
- collect CASE_DIR (network, read-only) waits for the batch to finish and
  writes raw/<file>.json (the shot-ordered bit strings), results.json (shots
  requested and done, execution seconds, job timestamps and status) and the
  transactions charged to the batch's jobs. Existing raw shot order and bytes
  are preserved; a conflicting recollection is rejected before publication.

Usage: "$QI_PYTHON" scripts/qi_platform.py (snapshot --out DIR | submit CASE_DIR ... | collect CASE_DIR)
       "$PYTHON" scripts/qi_platform.py (check DIR [--agents AGENTS.md] | facts DIR)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib
import json
import os
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HOST = "https://api.quantum-inspire.com"
CATALOGUE_SCHEMA = "qi-catalogue-v1"
USAGE_SCHEMA = "qi-usage-v1"
SUBMISSION_STATE_SCHEMA = "qi-submission-state-v1"
SUBMISSION_SCHEMA = "qi-submission-v2"
# The FAQ allows three queued jobs per hardware backend, and the API counts
# its queue in batches. On hardware a batch holds at most three circuits and
# waits for the account's queue to be empty, so at most three jobs are queued
# under either reading of "job".
HARDWARE_BATCH_CIRCUITS = 3
HARDWARE_QUEUED_BATCHES = 1
REDACTED = ("email", "full_name", "oidc_sub")
TERMINAL = {"completed", "failed", "cancelled"}
ENQUEUED_BATCH_STATUSES = {"queued", "reserved", "running", "finished"}
REFRESH_MARGIN = 120.0


def digest(value: object) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


class PlatformError(RuntimeError):
    """A refused or failed platform request; carries the status and the service's message."""


class Client:
    """Bearer-token REST client over the quantuminspire SDK's stored OAuth tokens.

    An access token lives expires_in seconds (3600) from generated_at. Every
    request within REFRESH_MARGIN seconds of expiry calls the SDK's refresh,
    which exchanges the refresh token once the access token is within 5 s of
    expiry, so a long collect or a long-lived MCP server keeps a valid token.
    A request that still answers 401 refreshes once and is sent again; the
    service rejects a 401 request before creating anything, so the retry
    cannot duplicate a POST.
    """

    def __init__(self) -> None:
        # importlib keeps one typing outcome whether or not requests ships stubs.
        requests = importlib.import_module("requests")
        from quantuminspire.managers.auth_manager import AuthManager
        from quantuminspire.managers.config_manager import ConfigManager

        self.config = ConfigManager()
        self.host = self.config.get("default_host")
        if str(self.host).rstrip("/") != HOST:
            raise PlatformError(f"default_host is {self.host}, expected {HOST}")
        self.auth = AuthManager(user_settings=self.config.user_settings)
        if self.auth.login_required(self.host):
            raise PlatformError("no Quantum Inspire login; run `qi login` in the Quantum Inspire environment")
        self.member_id = self.config.user_settings.auths[self.host].team_member_id
        self.session = requests.Session()
        self.refresh()

    def refresh(self) -> None:
        self.auth.refresh_tokens(self.host)
        tokens = self.config.user_settings.auths[self.host].tokens
        self.expires = tokens.generated_at + tokens.expires_in
        self.session.headers["Authorization"] = f"Bearer {tokens.access_token}"

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if time.time() > self.expires - REFRESH_MARGIN:
            self.refresh()
        response = self.session.request(method, f"{HOST}{path}", timeout=60, **kwargs)
        if response.status_code == 401:
            self.refresh()
            response = self.session.request(method, f"{HOST}{path}", timeout=60, **kwargs)
        if response.status_code >= 400:
            raise PlatformError(f"{method} {path}: {response.status_code} {response.text[:500]}")
        # The compile endpoint answers 204 with no body.
        return response.json() if response.content else None

    def get(self, path: str, **params: Any) -> Any:
        return self.request("GET", path, params=params)

    def pages(self, path: str, **params: Any) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        page = 1
        while True:
            data = self.get(path, page=page, size=100, **params)
            rows += data["items"]
            if page >= data["pages"]:
                return rows
            page += 1

    def post(self, path: str, body: dict[str, Any]) -> Any:
        return self.request("POST", path, json=body)

    def patch(self, path: str) -> Any:
        return self.request("PATCH", path)


def ledger(client: Client) -> dict[str, Any]:
    jobs = {job["id"]: job for job in client.pages("/jobs")}
    batches = {batch["id"]: batch for batch in client.pages("/batch_jobs")}
    results: dict[int, list[dict[str, Any]]] = {}
    for job_id in jobs:
        results[job_id] = client.get(f"/results/job/{job_id}", page=1, size=100)["items"]
    rows = []
    for row in client.pages("/transactions/"):
        job = jobs.get(row["job"]) if row["job"] is not None else None
        batch = batches.get(job["batch_job_id"]) if job else None
        rows.append(
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "domain": row["domain"],
                "change": row["change"],
                "job": row["job"],
                "backend_type_id": batch["backend_type_id"] if batch else None,
                "team": digest(row["team_id"]),
                "member": digest(row["member_id"]) if row["member_id"] is not None else None,
            }
        )
    job_rows = []
    for job_id, job in sorted(jobs.items()):
        batch = batches.get(job["batch_job_id"], {})
        res = results[job_id]
        job_rows.append(
            {
                "job": job_id,
                "batch_job": job["batch_job_id"],
                "backend_type_id": batch.get("backend_type_id"),
                "status": job["status"],
                "created_on": job["created_on"],
                "queued_at": job["queued_at"],
                "finished_at": job["finished_at"],
                "number_of_shots": job["number_of_shots"],
                "shots_done": sum(r["shots_done"] or 0 for r in res),
                "execution_time_in_seconds": sum(r["execution_time_in_seconds"] for r in res),
                "charged": sum(r["change"] for r in rows if r["job"] == job_id),
            }
        )
    by: dict[str, dict[str, int]] = {"domain": defaultdict(int), "backend_type_id": defaultdict(int)}
    for row in rows:
        by["domain"][str(row["domain"])] += row["change"]
        by["backend_type_id"][str(row["backend_type_id"])] += row["change"]
    return {
        "schema": USAGE_SCHEMA,
        "retrieved_utc": now(),
        "transactions": rows,
        "jobs": job_rows,
        "totals": {
            "change": sum(r["change"] for r in rows),
            "by_domain": dict(sorted(by["domain"].items())),
            "by_backend_type_id": dict(sorted(by["backend_type_id"].items())),
            "execution_seconds": sum(j["execution_time_in_seconds"] for j in job_rows),
            "shots_done": sum(j["shots_done"] for j in job_rows),
        },
    }


def snapshot(out: Path) -> None:
    client = Client()
    backend_types = client.pages("/backend_types/")
    for backend_type in backend_types:
        backend_type["queue"] = client.get(f"/backend_types/{backend_type['id']}/queue")
    teams = client.pages("/teams/")
    members = client.pages("/members")
    catalogue = {
        "schema": CATALOGUE_SCHEMA,
        "retrieved_utc": now(),
        "host": HOST,
        "account": {
            "teams": [{"team": digest(t["id"]), "individual_user": t["individual_user"]} for t in teams],
            "members": [
                {
                    "member": digest(m["id"]),
                    "team": digest(m["team_id"]),
                    "role": m["role"],
                    "is_active": m["is_active"],
                }
                for m in members
            ],
            "projects": len(client.pages("/projects")),
            "reservations": len(client.pages("/reservations")),
        },
        "backend_types": sorted(backend_types, key=lambda b: b["id"]),
        "backends": sorted(client.pages("/backends"), key=lambda b: b["id"]),
        "languages": client.pages("/languages"),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "catalogue.json").write_text(json.dumps(catalogue, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out / "usage.json").write_text(json.dumps(ledger(client), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(backend_types)} backend types, {len(catalogue['backends'])} backends -> {out}")


def facts_table(catalogue: dict[str, Any]) -> str:
    """Markdown table of each backend type's structural limits and the backend instances behind them."""
    lines = [
        "| Backend type (id) | identifier | is_hardware | qubits | couplings | shots default / max "
        "| job limit (s) | jobs per batch | batch jobs queued |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for b in catalogue["backend_types"]:
        couplings = len({frozenset(edge) for edge in b["topology"]})
        lines.append(
            f"| {b['name']} ({b['id']}) | {b['identifier']} | {str(b['is_hardware']).lower()} | {b['nqubits']} "
            f"| {couplings} | {b['default_number_of_shots']} / {b['max_number_of_shots']} "
            f"| {b['job_execution_time_limit']:g} | {b['max_jobs_per_batch_job']} | {b['batchjobs_per_queue_limit']} |"
        )
    instances = ", ".join(f"{b['name']} ({b['location']})" for b in catalogue["backends"])
    return "\n".join(lines) + f"\n\nBackend instances: {instances}.\n"


def check_agents(catalogue: dict[str, Any], agents: Path) -> None:
    text = agents.read_text(encoding="utf-8")
    begin, end = "<!-- quantum-inspire-facts:begin -->\n", "<!-- quantum-inspire-facts:end -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise SystemExit(f"{agents}: needs one quantum-inspire-facts section")
    body = text[text.index(begin) + len(begin) : text.index(end)]
    if facts_table(catalogue) not in body:
        raise SystemExit(f"{agents}: the quantum-inspire-facts table differs from facts_table(catalogue.json)")


def check(directory: Path, agents: Path | None = None) -> None:
    catalogue = json.loads((directory / "catalogue.json").read_text(encoding="utf-8"))
    usage = json.loads((directory / "usage.json").read_text(encoding="utf-8"))
    if catalogue["schema"] != CATALOGUE_SCHEMA or usage["schema"] != USAGE_SCHEMA:
        raise SystemExit("unexpected schema")
    text = json.dumps(catalogue) + json.dumps(usage)
    for key in (*REDACTED, "access_token", "refresh_token", "team_id", "member_id", "user_id"):
        if f'"{key}"' in text:
            raise SystemExit(f"snapshot carries {key}")
    for field in (
        "nqubits",
        "topology",
        "gateset",
        "max_number_of_shots",
        "job_execution_time_limit",
        "max_jobs_per_batch_job",
        "batchjobs_per_queue_limit",
        "queue",
        "status",
    ):
        for backend_type in catalogue["backend_types"]:
            if field not in backend_type:
                raise SystemExit(f"backend type {backend_type['name']} lacks {field}")
    for edge in (e for b in catalogue["backend_types"] for e in b["topology"]):
        if len(edge) != 2:
            raise SystemExit(f"topology edge {edge}")
    rows = usage["transactions"]
    totals = usage["totals"]
    if totals["change"] != sum(r["change"] for r in rows):
        raise SystemExit("ledger total differs from its rows")
    for key, total in (("domain", totals["by_domain"]), ("backend_type_id", totals["by_backend_type_id"])):
        sums: dict[str, int] = defaultdict(int)
        for row in rows:
            sums[str(row[key])] += row["change"]
        if dict(sums) != total:
            raise SystemExit(f"ledger by_{key} differs from its rows")
    if totals["execution_seconds"] != sum(j["execution_time_in_seconds"] for j in usage["jobs"]):
        raise SystemExit("execution seconds differ from the job rows")
    if totals["shots_done"] != sum(j["shots_done"] for j in usage["jobs"]):
        raise SystemExit("completed shots differ from the job rows")
    if agents is not None:
        check_agents(catalogue, agents)
    print(f"qi snapshot: {len(catalogue['backend_types'])} backend types, {len(rows)} transactions consistent")


def _write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    """Publish a complete JSON file, optionally without replacing an existing one."""
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=1)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
        # A synced file is not enough: the directory entry must also survive
        # a crash before any remote resource creation or enqueue is attempted.
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _retained_matches(path: Path, value: object, *, ignore_collection_time: bool = False) -> None:
    """Compare JSON values without normalizing or rewriting any retained bytes."""
    if not path.exists():
        return
    retained = json.loads(path.read_text(encoding="utf-8"))
    if ignore_collection_time and isinstance(retained, dict) and isinstance(value, dict):
        retained = {key: item for key, item in retained.items() if key != "collected_utc"}
        value = {key: item for key, item in value.items() if key != "collected_utc"}
    if retained != value:
        raise PlatformError(f"{path.name}: recollection conflicts with retained data; no retained file was replaced")


def _retain_json(path: Path, value: object, *, ignore_collection_time: bool = False) -> None:
    try:
        _write_json(path, value, exclusive=True)
    except FileExistsError:
        _retained_matches(path, value, ignore_collection_time=ignore_collection_time)


def _check_submission_manifest(case_dir: Path, record: dict[str, Any], *, require_enqueued: bool = False) -> None:
    """Validate a v2 receipt's immutable manifest binding; keep v1 evidence readable."""
    if record.get("schema") not in {"qi-submission-v1", SUBMISSION_SCHEMA}:
        raise PlatformError("unexpected submission schema")
    if record["schema"] == "qi-submission-v1" and "cases_sha256" not in record:
        return
    cases_bytes = (case_dir / "cases.json").read_bytes()
    if record.get("cases_sha256") != hashlib.sha256(cases_bytes).hexdigest():
        raise PlatformError("cases.json differs from the submission receipt digest")
    cases = json.loads(cases_bytes)
    if any(cases[key] != record[key] for key in ("backend", "backend_type_id", "shots")):
        raise PlatformError("cases.json backend or shots differ from the submission receipt")
    if sorted(row["file"] for row in cases["circuits"]) != sorted(row["file"] for row in record["jobs"]):
        raise PlatformError("cases.json circuits differ from the submission receipt")
    for row in cases["circuits"]:
        if hashlib.sha256((case_dir / row["file"]).read_bytes()).hexdigest() != row["sha256"]:
            raise PlatformError(f"{row['file']} differs from its cases.json sha256")
    if record["schema"] == SUBMISSION_SCHEMA:
        digests = {row["file"]: row["sha256"] for row in cases["circuits"]}
        for row in record["jobs"]:
            if row.get("sha256") != digests[row["file"]]:
                raise PlatformError(f"{row['file']} differs from its submission receipt sha256")
        if record.get("state") not in {"created", "enqueued"}:
            raise PlatformError("unexpected submission receipt state")
        if require_enqueued and record["state"] != "enqueued":
            raise PlatformError("submission receipt is not enqueued; use read-only reconciliation")


def submit(case_dir: Path, backend_type_id: int, approval: str) -> dict[str, Any]:
    if (case_dir / "submission.json").exists():
        raise SystemExit(f"{case_dir}/submission.json exists; this case was submitted")
    state_path = case_dir / "submission-state.json"
    if state_path.exists():
        raise SystemExit(f"{state_path} exists; run reconcile for read-only recovery, never repeat submit")
    if not approval.strip():
        raise SystemExit("a nonempty approval is required")
    cases_bytes = (case_dir / "cases.json").read_bytes()
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
    client = Client()
    backend_type = client.get(f"/backend_types/{backend_type_id}")
    if backend_type["identifier"] != cases["backend"]:
        raise SystemExit(f"backend type {backend_type_id} is {backend_type['identifier']}, not {cases['backend']}")
    if backend_type["status"] == "offline":
        raise SystemExit(f"{backend_type['name']} is offline")
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
        raise PlatformError("queue capacity or current-user queue count is invalid")
    if backend_type["is_hardware"]:
        if len(sources) > HARDWARE_BATCH_CIRCUITS:
            raise SystemExit(f"{len(sources)} circuits exceed the {HARDWARE_BATCH_CIRCUITS} a hardware batch may hold")
        queue_limit = min(queue_limit, HARDWARE_QUEUED_BATCHES)
    if queued + 1 > queue_limit:
        raise SystemExit(f"current-user queue has {queued} batches; adding one exceeds the limit {queue_limit}")
    language = next(lang for lang in client.pages("/languages") if lang["name"] == "cQASM" and lang["version"] == "3.0")
    state: dict[str, Any] = {
        "schema": SUBMISSION_STATE_SCHEMA,
        "phase": "creating",
        "started_utc": now(),
        "approval": approval,
        "backend": cases["backend"],
        "backend_type_id": backend_type_id,
        "cases_sha256": hashlib.sha256(cases_bytes).hexdigest(),
        "shots": cases["shots"],
        "jobs": [],
    }
    try:
        _write_json(state_path, state, exclusive=True)
    except FileExistsError:
        raise SystemExit(f"{state_path} exists; another submission owns this case") from None
    name = f"gororoba-{case_dir.name}"[:32]
    project = client.post(
        "/projects", {"owner_id": client.member_id, "name": name, "description": name, "starred": False}
    )
    state["project"] = project["id"]
    _write_json(state_path, state)
    batch = client.post("/batch_jobs", {"backend_type_id": backend_type_id})
    state["batch_job"] = batch["id"]
    _write_json(state_path, state)
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
        _write_json(state_path, state)
    record = {
        "schema": SUBMISSION_SCHEMA,
        "state": "created",
        "created_utc": now(),
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
    _write_json(state_path, state)
    client.patch(f"/batch_jobs/{batch['id']}/enqueue")
    record.update(state="enqueued", submitted_utc=now())
    state["phase"] = "enqueued"
    state["confirmed_utc"] = record["submitted_utc"]
    _write_json(state_path, state)
    _retain_json(case_dir / "submission.json", record)
    return record


def reconcile(case_dir: Path) -> None:
    """Recover a receipt using only documented GET endpoints; never retry enqueue."""
    state_path = case_dir / "submission-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("schema") != SUBMISSION_STATE_SCHEMA:
        raise PlatformError("unexpected submission state schema")
    if state.get("cases_sha256") != hashlib.sha256((case_dir / "cases.json").read_bytes()).hexdigest():
        raise PlatformError("cases.json differs from the submission checkpoint")
    cases = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    for row in cases["circuits"]:
        if hashlib.sha256((case_dir / row["file"]).read_bytes()).hexdigest() != row["sha256"]:
            raise PlatformError(f"{row['file']} differs from its cases.json sha256")
    batch_id = state.get("batch_job")
    if batch_id is None:
        raise PlatformError("no batch id was retained; the remote creation outcome is unknown; submit remains blocked")
    record = state.get("submission")
    if record is not None:
        _check_submission_manifest(case_dir, record)
    client = Client()
    # The captured OpenAPI exposes GET /batch_jobs with an id filter, not
    # GET /batch_jobs/{id}. Keep the read confined to the checkpointed batch.
    batches = client.pages("/batch_jobs", id=batch_id)
    if len(batches) != 1 or batches[0]["id"] != batch_id:
        raise PlatformError("the service did not resolve exactly the recorded batch; submit remains blocked")
    batch = batches[0]
    if record is None:
        raise PlatformError(
            f"batch {batch_id} is {batch['status']}; resource creation was incomplete; submit remains blocked"
        )
    ids = [row["job"] for row in record["jobs"]]
    if batch["backend_type_id"] != record["backend_type_id"] or sorted(batch["job_ids"]) != sorted(ids):
        raise PlatformError("the service batch differs from the checkpointed backend or jobs")
    for job_id in ids:
        job = client.get(f"/jobs/{job_id}")
        if job["id"] != job_id or job["batch_job_id"] != batch_id or job["number_of_shots"] != record["shots"]:
            raise PlatformError(f"job {job_id} differs from the submission checkpoint")
    if batch["status"] not in ENQUEUED_BATCH_STATUSES:
        raise PlatformError(f"batch {batch_id} is {batch['status']}; enqueue is unconfirmed; submit remains blocked")
    record["state"] = "enqueued"
    # When an enqueue response was lost, this is the local confirmation time;
    # retained job timestamps remain the source for execution chronology.
    record.setdefault("submitted_utc", now())
    state["phase"] = "enqueued"
    state["reconciled_utc"] = now()
    _write_json(state_path, state)
    _retain_json(case_dir / "submission.json", record)
    print(f"batch {batch_id}: {batch['status']}; recovered submission.json through read-only reconciliation")


def collect(case_dir: Path, poll: float, timeout: float) -> None:
    record = json.loads((case_dir / "submission.json").read_text(encoding="utf-8"))
    _check_submission_manifest(case_dir, record, require_enqueued=True)
    client = Client()
    deadline = time.monotonic() + timeout
    while True:
        states = {row["job"]: client.get(f"/jobs/{row['job']}") for row in record["jobs"]}
        if all(job["status"] in TERMINAL for job in states.values()):
            break
        if time.monotonic() > deadline:
            raise SystemExit(f"jobs still running: { {k: v['status'] for k, v in states.items()} }")
        time.sleep(poll)
    raw_dir = case_dir / "raw"
    raw: dict[str, list[str]] = {}
    rows = []
    for row in record["jobs"]:
        job = states[row["job"]]
        if job["id"] != row["job"] or job["batch_job_id"] != record["batch_job"]:
            raise PlatformError(f"job {row['job']} differs from submission.json")
        if job["number_of_shots"] != record["shots"]:
            raise PlatformError(f"job {row['job']} shot count differs from submission.json")
        results = client.get(f"/results/job/{row['job']}", page=1, size=100)["items"]
        logs = None
        if job["status"] != "completed":
            logs = client.get(f"/jobs/{row['job']}/logs")
            if results:
                raise PlatformError(f"{job['status']} job {row['job']} unexpectedly holds results")
        else:
            if len(results) != 1:
                raise PlatformError(f"completed job {row['job']} needs exactly one result")
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
                raise PlatformError(f"job {row['job']} raw shots or result metadata disagree")
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
            "team": digest(t["team_id"]),
            "member": digest(t["member_id"]) if t["member_id"] is not None else None,
        }
        for t in client.pages("/transactions/")
        if t["job"] in job_ids
    ]
    collected = {"schema": "qi-collection-v1", "collected_utc": now(), "jobs": rows, "transactions": charged}
    if raw_dir.exists() and {path.name for path in raw_dir.iterdir()} - set(raw):
        raise PlatformError("raw/ holds files outside the completed jobs; retained files were left intact")
    # Validate the entire recollection before publishing any new file. Ordered
    # list equality detects a permutation even when the histogram is unchanged.
    for name, shots in raw.items():
        _retained_matches(raw_dir / name, shots)
    _retained_matches(case_dir / "results.json", collected, ignore_collection_time=True)
    raw_dir.mkdir(exist_ok=True)
    for name, shots in raw.items():
        _retain_json(raw_dir / name, shots)
    _retain_json(case_dir / "results.json", collected, ignore_collection_time=True)
    for row in rows:
        print(row["file"], row["job"]["status"], [r["shots_done"] for r in row["results"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    p.add_argument("--agents", type=Path)
    p = sub.add_parser("facts")
    p.add_argument("directory", type=Path)
    p = sub.add_parser("submit")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--backend-type-id", type=int, required=True)
    p.add_argument("--approval", required=True, help="the user's approval, quoted, recorded in submission.json")
    p = sub.add_parser("reconcile")
    p.add_argument("case_dir", type=Path)
    p = sub.add_parser("collect")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--poll", type=float, default=20.0)
    p.add_argument("--timeout", type=float, default=3600.0)
    args = parser.parse_args()
    try:
        return run(args)
    except PlatformError as error:
        raise SystemExit(str(error)) from None


def run(args: argparse.Namespace) -> int:
    if args.command == "snapshot":
        snapshot(args.out)
    elif args.command == "check":
        check(args.directory, args.agents)
    elif args.command == "facts":
        print(facts_table(json.loads((args.directory / "catalogue.json").read_text(encoding="utf-8"))), end="")
    elif args.command == "submit":
        record = submit(args.case_dir, args.backend_type_id, args.approval)
        print(f"batch {record['batch_job']}: jobs {[row['job'] for row in record['jobs']]}")
    elif args.command == "reconcile":
        reconcile(args.case_dir)
    else:
        collect(args.case_dir, args.poll, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
- check DIR (offline) requires both files to carry their schema, the redacted
  identity form and a ledger whose aggregates equal the sum of its rows.
- submit CASE_DIR --backend-type-id N --approval TEXT (network, spends quota)
  creates one project, one algorithm, commit and file per circuit, one batch
  job holding every circuit of cases.json, and enqueues it. It verifies each
  circuit's sha256 against cases.json first and writes submission.json; a case
  directory that already holds submission.json sends nothing.
- collect CASE_DIR (network, read-only) waits for the batch to finish and
  writes raw/<file>.json (the shot-ordered bit strings), results.json (shots
  requested and done, execution seconds, job timestamps and status) and the
  transactions charged to the batch's jobs.

Usage: "$QI_PYTHON" scripts/qi_platform.py (snapshot --out DIR | submit CASE_DIR ... | collect CASE_DIR)
       "$PYTHON" scripts/qi_platform.py check DIR
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

HOST = "https://api.quantum-inspire.com"
CATALOGUE_SCHEMA = "qi-catalogue-v1"
USAGE_SCHEMA = "qi-usage-v1"
REDACTED = ("email", "full_name", "oidc_sub")
TERMINAL = {"completed", "failed", "cancelled"}


def digest(value: object) -> str:
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


class PlatformError(RuntimeError):
    """A refused or failed platform request; carries the status and the service's message."""


class Client:
    """Bearer-token REST client; the token comes from the quantuminspire SDK's settings and is refreshed once."""

    def __init__(self) -> None:
        import requests
        from quantuminspire.managers.auth_manager import AuthManager
        from quantuminspire.managers.config_manager import ConfigManager

        config = ConfigManager()
        host = config.get("default_host")
        if str(host).rstrip("/") != HOST:
            raise PlatformError(f"default_host is {host}, expected {HOST}")
        auth = AuthManager(user_settings=config.user_settings)
        if auth.login_required(host):
            raise PlatformError("no Quantum Inspire login; run `qi login` in the Quantum Inspire environment")
        auth.refresh_tokens(host)
        settings = config.user_settings.auths[host]
        self.member_id = settings.team_member_id
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {settings.tokens.access_token}"

    def get(self, path: str, **params: Any) -> Any:
        response = self.session.get(f"{HOST}{path}", params=params, timeout=60)
        if response.status_code >= 400:
            raise PlatformError(f"GET {path}: {response.status_code} {response.text[:500]}")
        return response.json()

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
        response = self.session.post(f"{HOST}{path}", json=body, timeout=60)
        if response.status_code >= 400:
            raise PlatformError(f"POST {path}: {response.status_code} {response.text[:500]}")
        # The compile endpoint answers 204 with no body.
        return response.json() if response.content else None

    def patch(self, path: str) -> Any:
        response = self.session.patch(f"{HOST}{path}", timeout=60)
        if response.status_code >= 400:
            raise PlatformError(f"PATCH {path}: {response.status_code} {response.text[:500]}")
        return response.json()


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
                {"member": digest(m["id"]), "team": digest(m["team_id"]), "role": m["role"], "is_active": m["is_active"]}
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


def check(directory: Path) -> None:
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
    print(f"qi snapshot: {len(catalogue['backend_types'])} backend types, {len(rows)} transactions consistent")


def submit(case_dir: Path, backend_type_id: int, approval: str) -> None:
    if (case_dir / "submission.json").exists():
        raise SystemExit(f"{case_dir}/submission.json exists; this case was submitted")
    cases = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    if cases["backend_type_id"] != backend_type_id:
        raise SystemExit(f"cases.json names backend type {cases['backend_type_id']}, not {backend_type_id}")
    sources = {}
    for row in cases["circuits"]:
        text = (case_dir / row["file"]).read_text(encoding="utf-8")
        if hashlib.sha256(text.encode()).hexdigest() != row["sha256"]:
            raise SystemExit(f"{row['file']} differs from its cases.json sha256")
        sources[row["file"]] = text
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
    language = next(lang for lang in client.pages("/languages") if lang["name"] == "cQASM" and lang["version"] == "3.0")
    name = f"gororoba-{case_dir.name}"[:32]
    project = client.post(
        "/projects", {"owner_id": client.member_id, "name": name, "description": name, "starred": False}
    )
    batch = client.post("/batch_jobs", {"backend_type_id": backend_type_id})
    jobs = []
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
        jobs.append({"file": file_name, "job": job["id"]})
    client.patch(f"/batch_jobs/{batch['id']}/enqueue")
    record = {
        "schema": "qi-submission-v1",
        "submitted_utc": now(),
        "approval": approval,
        "backend": cases["backend"],
        "backend_type_id": backend_type_id,
        "backend_status_at_submit": backend_type["status"],
        "queue_at_submit": client.get(f"/backend_types/{backend_type_id}/queue"),
        "batch_job": batch["id"],
        "project": project["id"],
        "shots": cases["shots"],
        "jobs": jobs,
    }
    (case_dir / "submission.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(f"batch {batch['id']}: jobs {[j['job'] for j in jobs]}")


def collect(case_dir: Path, poll: float, timeout: float) -> None:
    record = json.loads((case_dir / "submission.json").read_text(encoding="utf-8"))
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
    raw_dir.mkdir(exist_ok=True)
    rows = []
    for row in record["jobs"]:
        job = states[row["job"]]
        results = client.get(f"/results/job/{row['job']}", page=1, size=100)["items"]
        logs = None
        if job["status"] != "completed":
            logs = client.get(f"/jobs/{row['job']}/logs")
        for result in results:
            (raw_dir / f"{row['file']}.json").write_text(json.dumps(result["raw_data"]) + "\n", encoding="utf-8")
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
    text = json.dumps(collected, indent=1, sort_keys=True)
    (case_dir / "results.json").write_text(text + "\n", encoding="utf-8")
    for row in rows:
        print(row["file"], row["job"]["status"], [r["shots_done"] for r in row["results"]])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    p = sub.add_parser("submit")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--backend-type-id", type=int, required=True)
    p.add_argument("--approval", required=True, help="the user's approval, quoted, recorded in submission.json")
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
        check(args.directory)
    elif args.command == "submit":
        submit(args.case_dir, args.backend_type_id, args.approval)
    else:
        collect(args.case_dir, args.poll, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())

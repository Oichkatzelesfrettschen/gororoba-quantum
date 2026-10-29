"""Read-only live admission for the frozen Tuna projector qualification.

Run with the Quantum Inspire interpreter. The receipt records API observations,
not a submission authorization. Inspect current public FAQ/free-use terms
separately and run the guarded qi_platform.submit immediately after admission;
its account lock rechecks queue and pause before any provider write.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import qi_platform
from qi_projector_compiler_admission import RECEIPT, check_retained

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-projector-geometry"
MANIFEST_SHA256 = "d9a41a677a2a4bff4e2d3f4e10c4db2017d41ba1ee910da67960333d151dcfb2"
REQUIRED_EDGES = ((1, 4), (4, 8), (13, 11), (11, 14), (3, 6), (6, 9))
REQUIRED_GATES = {"init", "X", "H", "Ry", "CZ", "barrier", "measure"}
STRUCTURAL_FIELDS = (
    "id",
    "identifier",
    "nqubits",
    "is_hardware",
    "supports_raw_data",
    "protocol_version",
    "job_execution_time_limit",
    "max_jobs_per_batch_job",
    "max_number_of_shots",
    "batchjobs_per_queue_limit",
    "default_compiler_config",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_digest(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def bound_inputs(case_dir: Path, written_case: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    check_retained(RECEIPT)
    manifest_bytes = (case_dir / "cases.json").read_bytes()
    if digest(manifest_bytes) != MANIFEST_SHA256:
        raise ValueError("manifest differs from the frozen qualification")
    manifest = json.loads(manifest_bytes)
    if digest((ROOT / manifest["producer"]["file"]).read_bytes()) != manifest["producer"]["sha256"]:
        raise ValueError("frozen circuit producer digest differs")
    snapshot_bytes = (case_dir / manifest["backend_snapshot"]["file"]).read_bytes()
    if digest(snapshot_bytes) != manifest["backend_snapshot"]["sha256"]:
        raise ValueError("backend snapshot digest differs")
    rows = []
    receipt = json.loads((PROPOSAL / "local-compiler-receipt.json").read_text())
    for circuit in manifest["circuits"]:
        source_digest = digest((case_dir / circuit["file"]).read_bytes())
        if source_digest != circuit["sha256"]:
            raise ValueError("source circuit digest differs")
        compiler_row = next(
            row for row in receipt["circuits"] if row["source"] == f"tuna-qualification/{circuit['file']}"
        )
        compiled = PROPOSAL / "local-compiled/tuna-qualification" / circuit["file"]
        if (
            compiler_row["source_sha256"] != source_digest
            or digest(compiled.read_bytes()) != compiler_row["compiled_sha256"]
        ):
            raise ValueError("compiled circuit binding differs")
        rows.append(
            {
                "file": circuit["file"],
                "source_sha256": source_digest,
                "compiled_sha256": compiler_row["compiled_sha256"],
            }
        )
    return json.loads(snapshot_bytes), {
        "compiler_replay_receipt_sha256": digest(RECEIPT.read_bytes()),
        "qualification_analyzer_sha256": digest((ROOT / "scripts/qi_tuna_qualification.py").read_bytes()),
        "public_terms_sha256": digest(
            (ROOT / "docs/evidence/tuna-projector-geometry/qualification-terms-observation.json").read_bytes()
        ),
        "manifest_sha256": MANIFEST_SHA256,
        "circuit_producer_sha256": manifest["producer"]["sha256"],
        "backend_snapshot_sha256": digest(snapshot_bytes),
        "written_case_sha256": digest(written_case.read_bytes()),
        "circuits": rows,
    }


def structural_check(
    frozen: dict[str, Any],
    live: dict[str, Any],
    instances: list[dict[str, Any]],
    queue: dict[str, Any],
    transactions: list[dict[str, Any]],
    pause_left: int,
    observed_at: datetime.datetime,
    max_heartbeat_age_seconds: int,
) -> dict[str, Any]:
    """Validate an observation without retaining account or transaction identities."""
    if type(max_heartbeat_age_seconds) is not int or max_heartbeat_age_seconds <= 0:
        raise ValueError("heartbeat freshness policy must be positive whole seconds")
    failures = []
    for field in STRUCTURAL_FIELDS:
        value = live.get(field)
        if field == "job_execution_time_limit":
            matches = (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                and value == frozen[field]
            )
        else:
            matches = field in live and type(value) is type(frozen[field]) and value == frozen[field]
        if not matches:
            failures.append(f"structural field differs: {field}")
    if live.get("enabled") is not True:
        failures.append("backend is disabled")
    if live.get("status") not in {"idle", "executing"}:
        failures.append("backend status is unavailable")
    edges = {tuple(edge) for edge in live.get("topology", [])}
    if edges != {tuple(edge) for edge in frozen["topology"]}:
        failures.append("topology differs")
    if any(edge not in edges and tuple(reversed(edge)) not in edges for edge in REQUIRED_EDGES):
        failures.append("required CZ edge missing")
    gates = set(live.get("gateset", []))
    if gates != set(frozen["gateset"]) or not REQUIRED_GATES <= gates:
        failures.append("gate set differs")
    if type(queue.get("number_of_jobs_in_queue")) is not int or queue["number_of_jobs_in_queue"] != 0:
        failures.append("account queue must be empty")
    if type(pause_left) is not int or pause_left != 0:
        failures.append("account hardware pause remains")
    heartbeat_rows = []
    if not instances:
        failures.append("hardware instance missing")
    for instance in instances:
        try:
            heartbeat = datetime.datetime.fromisoformat(instance["last_heartbeat"])
            if heartbeat.tzinfo is None:
                raise ValueError("heartbeat lacks timezone")
            age = (observed_at - heartbeat).total_seconds()
        except (KeyError, TypeError, ValueError):
            age = None
        if age is None or age < 0 or age > max_heartbeat_age_seconds:
            failures.append("hardware heartbeat violates freshness policy")
        if instance.get("backend_type_id") != 7 or instance.get("status") not in {"idle", "executing"}:
            failures.append("hardware instance unavailable")
        heartbeat_rows.append(
            {"status": instance.get("status"), "last_heartbeat": instance.get("last_heartbeat"), "age_seconds": age}
        )
    changes = [row.get("change") for row in transactions]
    if any(type(change) is not int or change != 0 for change in changes):
        failures.append("account ledger contains a nonzero or malformed transaction")
    return {
        "admitted": not failures,
        "failures": failures,
        "backend": {field: live.get(field) for field in STRUCTURAL_FIELDS},
        "enabled": live.get("enabled"),
        "status": live.get("status"),
        "topology": live.get("topology"),
        "gateset": live.get("gateset"),
        "compiler_config_sha256": json_digest(live.get("default_compiler_config")),
        "required_edges": REQUIRED_EDGES,
        "instances": heartbeat_rows,
        "heartbeat_max_age_seconds": max_heartbeat_age_seconds,
        "queue_user_only": True,
        "queued_batches": queue.get("number_of_jobs_in_queue"),
        "hardware_pause_left_seconds": pause_left,
        "account_transaction_rows": len(transactions),
        "all_transaction_changes_zero": all(type(v) is int and v == 0 for v in changes),
        "limits": {
            "batch_circuits": 3,
            "shots_per_circuit": 4096,
            "account_hardware_queued_batches": 1,
            "hardware_pause_seconds": qi_platform.HARDWARE_PAUSE_SECONDS,
        },
    }


def observe(case_dir: Path, written_case: Path, max_heartbeat_age_seconds: int) -> dict[str, Any]:
    frozen, inputs = bound_inputs(case_dir, written_case)
    started = qi_platform.now()
    client = qi_platform.Client()
    live = client.get("/backend_types/7")
    instances = [row for row in client.pages("/backends") if row["backend_type_id"] == 7]
    transactions = client.pages("/transactions/")
    pause_left = qi_platform.hardware_pause_left(client)
    queue = client.get("/backend_types/7/queue", user_only=True)
    observed_at = qi_platform.utc_now()
    record = structural_check(
        frozen, live, instances, queue, transactions, pause_left, observed_at, max_heartbeat_age_seconds
    )
    return {
        "schema": "qi-projector-live-admission-v1",
        "request_started_utc": started,
        "observed_utc": observed_at.isoformat(),
        "inputs": inputs,
        "producer_sha256": digest(Path(__file__).read_bytes()),
        "public_terms_review": "Required separately before guarded submission",
        "scope": "authenticated account reads; account identifiers omitted",
        **record,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--written-case", type=Path, required=True)
    parser.add_argument("--max-heartbeat-age-seconds", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("admission output already exists")
    record = observe(args.case_dir, args.written_case, args.max_heartbeat_age_seconds)
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"admitted": record["admitted"], "failures": record["failures"]}))
    return 0 if record["admitted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

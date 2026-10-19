"""Write a read-only completed-job inventory of the IBM Quantum account.

The observation calls service.jobs(limit=None), decodes each job's
QuantumProgram input for its PUB count and shots, and reads its finalized
metrics for the settled charge and execution timestamps, then records the
account's usage window. It submits nothing. Every job must have finished,
DONE or failed (ERROR or CANCELLED, which bill the lock time they consumed
and return no result), with complete usage and a positive charge, so a run
with any job still queued, running or settling refuses and is repeated later. scripts/reconcile_qpu_inventory.py --check
binds the written snapshot to every retained raw archive offline.

GOROROBA_IBM_ACCOUNT selects a saved account; an instance other than the one
--out records writes qpu-job-inventory.<instance_crn_hash>.json beside it.

Usage:
    "$PYTHON" scripts/observe_qpu_job_inventory.py --out results/live/qpu-job-inventory.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import ibm_account  # noqa: E402

SCHEMA = "completed-qpu-job-inventory-v1"
FINISHED_STATUSES = frozenset({"DONE", "ERROR", "CANCELLED"})
BOUNDARY = (
    "Read-only service.jobs(limit=None), decoded QuantumProgram inputs and finalized metrics. Physical jobs "
    "require a finished status (DONE, ERROR or CANCELLED) and positive settled charge; local simulations and "
    "mock results are separate evidence."
)


def job_row(job: Any) -> dict[str, Any]:
    inputs = job.inputs() if callable(job.inputs) else job.inputs
    program = inputs["quantum_program"]
    metrics = job.metrics()
    usage = metrics.get("usage") or {}
    return {
        "backend": job.backend().name,
        "created_at": job.creation_date.astimezone(UTC).isoformat(),
        "final_qpu_charge_seconds": usage.get("qpu_charge_time_seconds"),
        "input_schema_version": inputs.get("schema_version"),
        "job_id": job.job_id(),
        "pub_count": len(program.items),
        "shots_per_pub": program.shots,
        "status": str(job.status()),
        "timestamps": metrics["timestamps"],
        "usage_status": usage.get("status"),
    }


def observe(service: Any) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    from live_run import _instance_hash

    rows = sorted((job_row(job) for job in service.jobs(limit=None)), key=lambda row: row["created_at"])
    unsettled = [
        row["job_id"]
        for row in rows
        if row["status"] not in FINISHED_STATUSES
        or row["usage_status"] != "complete"
        or not isinstance(row["final_qpu_charge_seconds"], int | float)
        or row["final_qpu_charge_seconds"] <= 0
    ]
    if unsettled:
        raise RuntimeError(f"jobs without a settled positive charge: {unsettled}; observe again after they settle")
    usage = service.usage()
    return {
        "account_usage": {
            key: usage[key]
            for key in ("usage_consumed_seconds", "usage_limit_seconds", "usage_period", "usage_remaining_seconds")
        },
        "complete_service_inventory": True,
        "instance_crn_hash": _instance_hash(service),
        "jobs": rows,
        "new_qpu_submissions": 0,
        "observed_at": datetime.now(UTC).isoformat(),
        "retrieval_boundary": BOUNDARY,
        "schema": SCHEMA,
    }


def inventory_target(out: Path, instance: str) -> Path:
    """The file an instance's observation belongs in.

    --out names the default instance's inventory. An observation of another
    instance, or of a named account when --out does not exist yet, writes
    <stem>.<instance_crn_hash>.json beside it, and no file is overwritten
    when its recorded instance_crn_hash differs.
    """
    default_instance = json.loads(out.read_text())["instance_crn_hash"] if out.is_file() else None
    if default_instance == instance or (default_instance is None and not ibm_account.account_name()):
        target = out
    else:
        target = out.with_name(f"{out.stem}.{instance}{out.suffix}")
    if target.is_file():
        recorded = json.loads(target.read_text()).get("instance_crn_hash")
        if recorded != instance:
            raise RuntimeError(f"{target} records instance {recorded}, not {instance}; refusing to overwrite it")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, required=True, help="default instance's inventory JSON; other instances write beside it"
    )
    arguments = parser.parse_args()
    from qiskit_ibm_runtime import QiskitRuntimeService

    snapshot = observe(ibm_account.open_service(QiskitRuntimeService))
    target = inventory_target(arguments.out, snapshot["instance_crn_hash"])
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    charge = sum(row["final_qpu_charge_seconds"] for row in snapshot["jobs"])
    print(f"{len(snapshot['jobs'])} settled jobs, {charge} s charged; wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

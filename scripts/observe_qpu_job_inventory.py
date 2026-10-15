"""Write a read-only completed-job inventory of the IBM Quantum account.

The observation calls service.jobs(limit=None), decodes each job's
QuantumProgram input for its PUB count and shots, and reads its finalized
metrics for the settled charge and execution timestamps, then records the
account's usage window. It submits nothing. Every job must be DONE with
complete usage and a positive charge, so a run with any job still settling
refuses and is repeated later. scripts/reconcile_qpu_inventory.py --check
binds the written snapshot to every retained raw archive offline.

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
SCHEMA = "completed-qpu-job-inventory-v1"
BOUNDARY = (
    "Read-only service.jobs(limit=None), decoded QuantumProgram inputs and finalized metrics. Physical jobs "
    "require positive settled charge; local simulations and mock results are separate evidence."
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
        if row["status"] != "DONE"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="inventory JSON to write")
    arguments = parser.parse_args()
    from qiskit_ibm_runtime import QiskitRuntimeService

    snapshot = observe(QiskitRuntimeService())
    arguments.out.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    charge = sum(row["final_qpu_charge_seconds"] for row in snapshot["jobs"])
    print(f"{len(snapshot['jobs'])} settled jobs, {charge} s charged; wrote {arguments.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

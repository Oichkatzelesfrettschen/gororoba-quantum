"""Compare the circuits IBM received for every retained job with the run's retained circuits.

Each retained run keeps the ISA circuits it planned in isa.qpy (the
recovered wide-control job keeps submitted-circuits.qpy instead). The
service returns a job's submitted program through job.inputs: a
QuantumProgram whose CircuitItem entries hold the circuits the executor
ran. For every job of results/live/qpu-job-retention-audit.json this script
retrieves that program and records, per job, how many items it holds, their
item kinds, and how many items equal a retained circuit under
QuantumCircuit equality (same DAG: gates, operands, parameters, global
phase).

``--write`` needs the service and the account's credential store and writes
docs/evidence/submitted_circuits/comparison.json. ``--check`` needs no network:
it requires the file to name exactly the audit's jobs and runs, and every
item of every job to match a retained circuit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
OUT = ROOT / "docs/evidence/submitted_circuits/comparison.json"
RETAINED_NAMES = ("isa.qpy", "submitted-circuits.qpy")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def audit_jobs() -> list[dict[str, Any]]:
    return list(json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"])


def retained_file(run: str) -> Path:
    for name in RETAINED_NAMES:
        path = ROOT / run / name
        if path.is_file():
            return path
    raise SystemExit(f"{run} retains no circuit file")


def write() -> int:
    from qiskit import qpy
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    rows = []
    for job in audit_jobs():
        path = retained_file(job["run"])
        with path.open("rb") as stream:
            retained = qpy.load(stream)
        items = service.job(job["job_id"]).inputs["quantum_program"].items
        circuits = [getattr(item, "circuit", None) for item in items]
        matched = sum(c is not None and any(c == r for r in retained) for c in circuits)
        rows.append(
            {
                "job_id": job["job_id"],
                "run": job["run"],
                "retained_file": path.relative_to(ROOT).as_posix(),
                "retained_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "retained_circuits": len(retained),
                "items": len(items),
                "item_kinds": sorted({type(item).__name__ for item in items}),
                "matched_items": matched,
            }
        )
        print(json.dumps(rows[-1]), flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "submitted-circuit-comparison-v1", "jobs": rows}, indent=1) + "\n")
    return 0


def check() -> int:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    require(data.get("schema") == "submitted-circuit-comparison-v1", "unexpected schema")
    rows = data["jobs"]
    expected = {(job["job_id"], job["run"]) for job in audit_jobs()}
    require({(r["job_id"], r["run"]) for r in rows} == expected, "the comparison names other jobs than the audit")
    require(len(rows) == len(expected), "a job appears twice")
    for row in rows:
        path = ROOT / row["retained_file"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row["retained_sha256"], f"{path} changed")
        require(row["items"] > 0 and row["matched_items"] == row["items"], f"{row['job_id']}: unmatched items")
        require(row["item_kinds"] == ["CircuitItem"], f"{row['job_id']}: item kinds {row['item_kinds']}")
    items = sum(r["items"] for r in rows)
    print(f"submitted circuits: {len(rows)} jobs, {items} items, every item equals a retained circuit")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write() if args.write else check()


if __name__ == "__main__":
    sys.exit(main())

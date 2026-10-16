"""Compare the circuits IBM received for every retained job, position by position, with the run's record.

Each retained run keeps its ISA circuits in isa.qpy, one circuit per PUB and
named by the PUB, and its record.json lists, per submitted job, the ordered
PUBs that job carried (``submission.jobs[].pubs``). The recovered wide-control
job keeps no record; its submitted-circuits.qpy holds the job's circuits in
submission order. The service returns a job's submitted program through
job.inputs: a QuantumProgram whose CircuitItem entries are the circuits the
executor ran, in order.

For every job of results/live/qpu-job-retention-audit.json this script
builds the expected ordered circuit list (isa.qpy circuits by the job's PUB
names, or the retained submission order) and records, per job, the expected
PUB names, the number of items the service returned, their item kinds, and
how many items equal the expected circuit at the same position under
QuantumCircuit equality (same DAG: gates, operands, parameters, global
phase).

``--write`` needs the service and the account's credential store and writes
docs/evidence/submitted_circuits/comparison.json. ``--check`` needs no network:
it requires the file to name exactly the audit's jobs and runs, every
retained circuit file to keep its recorded digest, each job's item count to
equal both its expected PUB list and the audit's pub_count, and the QPY
sha256 that --write recorded for every submitted item to equal the QPY
sha256 of the expected circuit at the same position, recomputed from the
retained file. A circuit the service returns and the equal archived circuit
serialize to identical QPY bytes, so the gate re-derives the comparison
rather than trusting a recorded count.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
OUT = ROOT / "docs/evidence/submitted_circuits/comparison.json"
SCHEMA = "submitted-circuit-comparison-v3"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def audit_jobs() -> list[dict[str, Any]]:
    return list(json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"])


def expected_order(job: dict[str, Any]) -> tuple[Path, list[str] | None]:
    """The retained circuit file and, for a recorded run, the job's ordered PUB names."""
    run = ROOT / job["run"]
    record = run / "record.json"
    if (run / "isa.qpy").is_file() and record.is_file():
        submission = json.loads(record.read_text(encoding="utf-8")).get("submission") or {}
        for entry in submission.get("jobs", []):
            if entry.get("job_id") == job["job_id"]:
                return run / "isa.qpy", [pub["name"] for pub in entry["pubs"]]
        raise SystemExit(f"{job['job_id']}: record.json lists no such submitted job")
    path = run / "submitted-circuits.qpy"
    require(path.is_file(), f"{job['run']} retains no circuit file")
    return path, None


def qpy_digest(circuit: Any) -> str:
    """sha256 of a circuit's QPY serialization; equal service and archived circuits serialize identically."""
    from qiskit import qpy

    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def expected_circuits(row: dict[str, Any]) -> list[Any]:
    """The retained circuits a job's items must equal, in order, rebuilt from the retained file."""
    from qiskit import qpy

    with (ROOT / row["retained_file"]).open("rb") as stream:
        retained = list(qpy.load(stream))
    if row["order_source"] == "retained submission order":
        return retained
    by_name = {circuit.name: circuit for circuit in retained}
    return [by_name[name] for name in row["expected_pubs"]]


def write() -> int:
    from qiskit import qpy
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    rows = []
    for job in audit_jobs():
        path, names = expected_order(job)
        with path.open("rb") as stream:
            retained = qpy.load(stream)
        if names is None:
            expected = list(retained)
            names = [circuit.name for circuit in expected]
            source = "retained submission order"
        else:
            by_name = {circuit.name: circuit for circuit in retained}
            require(all(name in by_name for name in names), f"{job['job_id']}: a PUB name is missing from isa.qpy")
            expected = [by_name[name] for name in names]
            source = "record.json submission.jobs[].pubs"
        items = service.job(job["job_id"]).inputs["quantum_program"].items
        circuits = [getattr(item, "circuit", None) for item in items]
        submitted_digests = [qpy_digest(c) if c is not None else None for c in circuits]
        matched = sum(
            got is not None and index < len(expected) and got == expected[index] for index, got in enumerate(circuits)
        )
        rows.append(
            {
                "job_id": job["job_id"],
                "run": job["run"],
                "retained_file": path.relative_to(ROOT).as_posix(),
                "retained_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "order_source": source,
                "expected_pubs": names,
                "items": len(items),
                "item_kinds": sorted({type(item).__name__ for item in items}),
                "positional_matches": matched,
                "submitted_qpy_sha256": submitted_digests,
            }
        )
        print(json.dumps({k: v for k, v in rows[-1].items() if k != "expected_pubs"}), flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": SCHEMA, "jobs": rows}, indent=1) + "\n", encoding="utf-8")
    return 0


def check() -> int:
    data = json.loads(OUT.read_text(encoding="utf-8"))
    require(data.get("schema") == SCHEMA, "unexpected schema")
    rows = data["jobs"]
    audited = {job["job_id"]: job for job in audit_jobs()}
    require({(r["job_id"], r["run"]) for r in rows} == {(j, a["run"]) for j, a in audited.items()}, "jobs differ")
    require(len(rows) == len(audited), "a job appears twice")
    for row in rows:
        path = ROOT / row["retained_file"]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row["retained_sha256"], f"{path} changed")
        pub_count = audited[row["job_id"]]["pub_count"]
        counts_agree = row["items"] == pub_count == len(row["expected_pubs"])
        require(counts_agree, f"{row['job_id']}: item and PUB counts differ")
        expected = [qpy_digest(circuit) for circuit in expected_circuits(row)]
        require(len(row["submitted_qpy_sha256"]) == row["items"], f"{row['job_id']}: item digests are incomplete")
        mismatched = [
            k for k, (got, want) in enumerate(zip(row["submitted_qpy_sha256"], expected, strict=True)) if got != want
        ]
        require(not mismatched, f"{row['job_id']}: submitted items {mismatched} differ from the retained circuits")
        require(row["positional_matches"] == row["items"], f"{row['job_id']}: an item differs from its circuit")
        require(row["item_kinds"] == ["CircuitItem"], f"{row['job_id']}: item kinds {row['item_kinds']}")
    items = sum(r["items"] for r in rows)
    print(f"submitted circuits: {len(rows)} jobs, {items} items, each equal to its expected circuit in order")
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

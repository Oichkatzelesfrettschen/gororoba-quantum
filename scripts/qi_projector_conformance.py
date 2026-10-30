"""Replay the frozen QX projector screen using integer shot counts."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from qi_projector_geometry import analyze_case

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx"
APPROVED_MANIFEST = "bb52460648caed1a8fe2be39131f88efaaa7022f53614f386b48034027290554"


def screen(reports: dict[str, Any]) -> list[dict[str, Any]]:
    """The pre-acquisition tolerances are 1/20 for probabilities and 1/10 for signed means."""
    targets = {
        "geometry-z.cq": ("joint_zero_count", (1024, 768, 512), 20),
        "mutation-z.cq": ("joint_zero_count", (1024, 1024, 1024), 20),
        "geometry-x.cq": ("signed_joint_sum", (0, 512, 0), 10),
    }
    if set(reports) != set(targets):
        raise ValueError("the approved screen requires exactly the three named circuits")
    checks = []
    for filename, (metric, expected_counts, tolerance_denominator) in targets.items():
        replicas = reports[filename]["replicas"]
        if len(replicas) != 3:
            raise ValueError("the approved screen requires three replicas")
        for replica_index, (replica, expected_count) in enumerate(zip(replicas, expected_counts, strict=True)):
            for field, target, denominator in (
                ("herald_count", 1024, 20),
                (metric, expected_count, tolerance_denominator),
            ):
                observed = replica[field]
                if type(observed) is not int:
                    raise ValueError("screen inputs must be integer counts or signed sums")
                checks.append(
                    {
                        "file": filename,
                        "replica_index": replica_index,
                        "metric": field,
                        "observed_numerator": observed,
                        "expected_numerator": target,
                        "shots": 2048,
                        "tolerance": [1, denominator],
                        "passed": abs(observed - target) * denominator <= 2048,
                    }
                )
    return checks


def replay(run: Path = RUN) -> dict[str, Any]:
    manifest = run / "cases.json"
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != APPROVED_MANIFEST:
        raise ValueError("case differs from the approved manifest")
    reports = {
        name.removesuffix(".analysis.json"): json.loads(content)
        for name, content in analyze_case(run, run / "raw").items()
    }
    checks = screen(reports)
    collected = json.loads((run / "results.json").read_text())
    if any(row["job"]["status"] != "completed" for row in collected["jobs"]):
        raise ValueError("every job must be completed")
    execution = sum(
        (Decimal(str(result["execution_time_in_seconds"])) for row in collected["jobs"] for result in row["results"]),
        Decimal(0),
    )
    charge = sum(row["change"] for row in collected["transactions"])
    inputs = [
        manifest,
        run / "submission.json",
        run / "results.json",
        Path(__file__),
        ROOT / "scripts/qi_projector_geometry.py",
    ]
    inputs.extend(sorted((run / "raw").glob("*.json")))
    return {
        "schema": "qi-projector-conformance-v1",
        "run": run.relative_to(ROOT).as_posix(),
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
        "shots_total": 6144,
        "execution_seconds_decimal": str(execution),
        "transaction_change": charge,
        "zero_recorded_charge": charge == 0,
        "boundary": "Remote QX finite-shot conformance; hardware behavior and early-bit retention remain unmeasured.",
        "inputs": {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json.dumps(replay(), indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained QX conformance differs from raw replay")
        print("QX projector conformance: retained integer-count replay matches")
    else:
        with arguments.out.open("x") as destination:
            destination.write(content)


if __name__ == "__main__":
    main()

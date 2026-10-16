"""Calibration drift of ibm_fez, ibm_kingston and ibm_marrakesh from the medians the run records retain.

live_run records, for every backend it read (planned in ``backends`` or
withheld in ``skipped_backends``), the calibration identity (properties
last_update_date) and the medians of T1, T2, readout error and CZ error over
the qubits and couplers it admitted (live_run.BackendSnapshot.medians). The
admitted population is the device minus the quality exclusions
(faulty, missing calibration, T1 or T2 below the policy floor, readout or sx
error above the policy ceiling, CZ error above its ceiling) and minus any
``--exclude-qubits`` operator exclusion. One identity read by several
records therefore carries one device-wide median vector, and a record that
withheld qubits by operator exclusion carries the medians of its own subset.

The drift series keeps one row per (backend, identity), ordered by the
identity's timestamp, from the records without an operator exclusion; every
such record of one identity must carry the same medians, or the script
stops. Records with an operator exclusion are listed per identity with the
size of their admitted population and are kept out of the series, since
their medians describe a handful of chosen qubits.

The device-wide median still moves when the quality exclusions change. The
retained snapshots under docs/evidence/calibration/history separate the two:

- for every identity with both a snapshot and a device-wide record, the
  snapshot's T1, T2 and CZ errors over that record's admitted qubits and
  couplers reproduce its medians exactly; its readout entry is the mean
  assignment error (e01 + e10)/2, a different quantity from the service's
  readout_error, so that median is reported as a difference;
- between consecutive snapshots of a backend, the paired drift is the median
  relative change over the qubits (couplers) the policy admits in both, the
  population held fixed.

Consecutive identities often carry identical T1 and T2 medians, because a
properties update need not remeasure every quantity; the summary counts the
steps whose median changed and takes the median relative change over those.

The medians and snapshots carry no qubit frequency, so neither constrains a
frame detuning.

``--out FILE`` writes the result, naming every record and every snapshot
(docs/evidence/calibration/history/<backend>/*.json) read with its sha256.
``--check FILE`` recomputes from exactly the records and snapshots FILE
names, requires each to hold its recorded sha256, and requires the
recomputed result to equal FILE byte for byte, so records and snapshots
added later leave the check unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_calibrations  # noqa: E402
import numpy as np  # noqa: E402

SCHEMA = "calibration-median-drift-v1"
LIVE = ROOT / "results/live"
MEDIANS = ("t1_us", "t2_us", "readout_error", "cz_error")
THRESHOLDS = ("max_readout_error", "max_cz_error", "max_sx_error", "min_t1_us", "min_t2_us")
OPERATOR = "operator exclusion"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backend_entries(record: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    entries = [(name, entry) for name, entry in (record.get("backends") or {}).items() if isinstance(entry, dict)]
    entries += [
        (name, entry) for name, entry in (record.get("skipped_backends") or {}).items() if isinstance(entry, dict)
    ]
    return [(name, entry) for name, entry in entries if entry.get("medians") and entry.get("calibration")]


def snapshot_medians(
    snapshot: dict[str, Any], excluded_qubits: set[int], excluded_edges: set[tuple[int, int]], ceiling: float
) -> dict[str, float]:
    admitted = [q for q in range(snapshot["num_qubits"]) if q not in excluded_qubits]
    qubits = snapshot["qubits"]
    cz = [
        row["error"]
        for row in snapshot["instructions"]["cz"]
        if tuple(row["qargs"]) not in excluded_edges and row["error"] is not None and row["error"] <= ceiling
    ]
    return {
        "t1_us": float(np.median([qubits[q]["t1"] * 1e6 for q in admitted])),
        "t2_us": float(np.median([qubits[q]["t2"] * 1e6 for q in admitted])),
        "assignment_error": float(np.median([(qubits[q]["e01"] + qubits[q]["e10"]) / 2 for q in admitted])),
        "cz_error": float(np.median(cz)),
    }


def policy_admits(snapshot: dict[str, Any], thresholds: dict[str, float]) -> tuple[set[int], set[tuple[int, int]]]:
    """Qubits and couplers the policy thresholds admit from snapshot values alone."""
    sx = {row["qargs"][0]: row["error"] for row in snapshot["instructions"]["sx"]}
    qubits = {
        q
        for q, entry in enumerate(snapshot["qubits"])
        if entry["t1"] is not None
        and entry["t2"] is not None
        and entry["t1"] * 1e6 >= thresholds["min_t1_us"]
        and entry["t2"] * 1e6 >= thresholds["min_t2_us"]
        and (entry["e01"] + entry["e10"]) / 2 <= thresholds["max_readout_error"]
        and sx.get(q) is not None
        and sx[q] <= thresholds["max_sx_error"]
    }
    edges = {
        (row["qargs"][0], row["qargs"][1])
        for row in snapshot["instructions"]["cz"]
        if row["qargs"][0] < row["qargs"][1]
        and row["error"] is not None
        and row["error"] <= thresholds["max_cz_error"]
        and set(row["qargs"]) <= qubits
    }
    return qubits, edges


def qubit_values(snapshot: dict[str, Any], key: str, qubits: list[int]) -> list[float]:
    if key == "assignment_error":
        return [(snapshot["qubits"][q]["e01"] + snapshot["qubits"][q]["e10"]) / 2 for q in qubits]
    return [snapshot["qubits"][q][key] for q in qubits]


def relative_change(before: list[float], after: list[float]) -> float:
    return float(np.median([(b - a) / a for a, b in zip(before, after, strict=True)]))


def admitted(read: dict[str, Any]) -> int | None:
    """Admitted qubit count, when the record names the backend's size (capabilities.num_qubits)."""
    return read["num_qubits"] - len(read["excluded_qubits"]) if read["num_qubits"] else None


def compute(paths: list[Path], snapshot_paths: list[Path]) -> dict[str, Any]:
    reads: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    thresholds_seen = set()
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        thresholds_seen.add(tuple(record["policy"][key] for key in THRESHOLDS))
        for backend, entry in backend_entries(record):
            excluded = entry.get("excluded_qubits", {})
            reads[backend, entry["calibration"]].append(
                {
                    "record": path.parent.name,
                    "medians": entry["medians"],
                    "operator": sum(1 for reason in excluded.values() if reason == OPERATOR),
                    "excluded_qubits": {int(q) for q in excluded},
                    "excluded_edges": {tuple(int(v) for v in e.split("-")) for e in entry.get("excluded_edges", {})},
                    "num_qubits": entry.get("capabilities", {}).get("num_qubits"),
                }
            )
    require(len(thresholds_seen) == 1, f"records carry {len(thresholds_seen)} policy threshold sets")
    thresholds = dict(zip(THRESHOLDS, next(iter(thresholds_seen)), strict=True))
    snapshots: dict[tuple[str, str], dict[str, Any]] = {}
    for path in snapshot_paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        snapshots[data["backend"], data["calibration"]] = data | {"_file": path.relative_to(ROOT).as_posix()}
    backends: dict[str, Any] = {}
    for backend in sorted({b for b, _ in reads}):
        identities = sorted((c for b, c in reads if b == backend), key=datetime.fromisoformat)
        rows = []
        for calibration in identities:
            group = reads[backend, calibration]
            wide = [r for r in group if r["operator"] == 0]
            vectors = {json.dumps(r["medians"], sort_keys=True) for r in wide}
            require(len(vectors) <= 1, f"{backend} {calibration}: device-wide records disagree on the medians")
            row: dict[str, Any] = {
                "calibration": calibration,
                "device_wide_records": len(wide),
                "operator_scoped_records": [
                    {"record": r["record"], "admitted_qubits": admitted(r)} for r in group if r["operator"]
                ],
                "medians": wide[0]["medians"] if wide else None,
                "admitted_qubits": admitted(wide[0]) if wide else None,
            }
            snapshot = snapshots.get((backend, calibration))
            if snapshot is not None and wide:
                fresh = snapshot_medians(
                    snapshot, wide[0]["excluded_qubits"], wide[0]["excluded_edges"], thresholds["max_cz_error"]
                )
                for key in ("t1_us", "t2_us", "cz_error"):
                    require(
                        math.isclose(fresh[key], wide[0]["medians"][key], rel_tol=1e-12),
                        f"{backend} {calibration}: snapshot {key} median {fresh[key]} differs from the record",
                    )
                row["snapshot"] = snapshot["_file"]
                row["assignment_minus_readout_error"] = round(
                    fresh["assignment_error"] - wide[0]["medians"]["readout_error"], 9
                )
            rows.append(row)
        series = [row for row in rows if row["medians"] is not None]
        summary: dict[str, Any] = {}
        for key in MEDIANS:
            values = [row["medians"][key] for row in series]
            steps = [abs(b - a) / a for a, b in zip(values, values[1:], strict=False)]
            summary[key] = {
                "min": round(min(values), 9),
                "max": round(max(values), 9),
                "max_over_min": round(max(values) / min(values), 6),
                "steps": len(steps),
                "steps_with_change": sum(1 for step in steps if step > 0),
                "median_changed_step_relative_change": (
                    round(float(np.median([step for step in steps if step > 0])), 6) if any(steps) else None
                ),
                "largest_step_relative_change": round(max(steps), 6) if steps else None,
            }
        paired = []
        retained = sorted((c for b, c in snapshots if b == backend), key=datetime.fromisoformat)
        for before, after in zip(retained, retained[1:], strict=False):
            first, second = snapshots[backend, before], snapshots[backend, after]
            q1, e1 = policy_admits(first, thresholds)
            q2, e2 = policy_admits(second, thresholds)
            qubits, edges = sorted(q1 & q2), sorted(e1 & e2)
            cz1 = {tuple(r["qargs"]): r["error"] for r in first["instructions"]["cz"]}
            cz2 = {tuple(r["qargs"]): r["error"] for r in second["instructions"]["cz"]}

            paired.append(
                {
                    "before": before,
                    "after": after,
                    "hours": round(
                        (datetime.fromisoformat(after) - datetime.fromisoformat(before)).total_seconds() / 3600, 3
                    ),
                    "common_qubits": len(qubits),
                    "common_couplers": len(edges),
                    "median_relative_change": {
                        key: round(
                            relative_change(qubit_values(first, key, qubits), qubit_values(second, key, qubits)), 6
                        )
                        for key in ("t1", "t2", "assignment_error")
                    }
                    | {
                        "cz_error": round(relative_change([cz1[e] for e in edges], [cz2[e] for e in edges]), 6),
                    },
                }
            )
        backends[backend] = {"identities": rows, "series_summary": summary, "paired_snapshot_drift": paired}
    return {
        "schema": SCHEMA,
        "policy_thresholds": thresholds,
        "records": {path.parent.name: sha256(path) for path in paths},
        "snapshots": {path.relative_to(ROOT).as_posix(): sha256(path) for path in snapshot_paths},
        "backends": backends,
    }


def encode(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=1) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--out", type=Path)
    target.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        retained_text = args.check.read_text(encoding="utf-8")
        retained = json.loads(retained_text)
        require(retained.get("schema") == SCHEMA, f"{args.check}: schema {retained.get('schema')}, expected {SCHEMA}")
        paths = [LIVE / name / "record.json" for name in retained["records"]]
        for path, digest in zip(paths, retained["records"].values(), strict=True):
            require(path.is_file() and sha256(path) == digest, f"{path.relative_to(ROOT)}: sha256 differs")
        snapshot_paths = [ROOT / name for name in retained["snapshots"]]
        for path, digest in zip(snapshot_paths, retained["snapshots"].values(), strict=True):
            require(path.is_file() and sha256(path) == digest, f"{path.relative_to(ROOT)}: sha256 differs")
        require(encode(compute(paths, snapshot_paths)) == retained_text, f"{args.check}: recomputed result differs")
        print(f"{args.check}: {len(paths)} records and {len(snapshot_paths)} snapshots reproduce the drift result")
        return 0
    paths = sorted(LIVE.glob("*/record.json"))
    snapshot_paths = sorted(ghost_calibrations.HISTORY.glob("*/*.json"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(encode(compute(paths, snapshot_paths)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

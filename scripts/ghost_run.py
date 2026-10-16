"""Ghost runs: replay every retained IBM job's circuits in Aer under any retained calibration state.

A ghost run takes a submitted run's archived ISA circuits (isa.qpy), rebuilds
each logical member's replicas exactly as live_run.collect does
(packing.extract on the member's fused-PUB component, packing.split per
replica, from record.json's submission plan and group record), and samples
them under a calibration snapshot from docs/evidence/calibration/history/
(scripts/ghost_calibrations.py). It then compares each replica's ghost
distribution with the hardware distribution that collect.json retains
(``measured``) by total-variation distance.

Calibration states per run:

- ``execution``: the snapshot in force when the member's PUB began
  (index.json maps every job's execution start to it). Its TV distance to
  the hardware should match the record's own ``tvd_measured_to_replayed`` up
  to sampling noise, since both use live_run's noise model for that
  calibration; ``self_check`` reports the mean difference.
- ``current``: the backend's calibration at export time.
- every other retained snapshot of the same backend, earlier or later.

For each run and state the output gives the mean TV distance over members
and the per-member values, so a reader sees whether the hardware sits closest
to its own execution calibration, how far calibration drift alone moves the
prediction, and how large the floor no calibration explains is.

Members wider than MAX_QUBITS active qubits are skipped with that reason: a
density matrix beyond 14 qubits leaves a 15 GiB T4 (docs/notes/kaggle/
substrates.md). Runs whose record predates the fused-PUB submission plan are
skipped with the record's reason.

``--runs all`` ghosts every audited run; ``--runs RUN[,RUN]`` names run
directories. ``--states execution,current`` or ``all``. The entry reads
GOROROBA_AER_DEVICE (CPU by default). ``--check FILE`` reruns the
execution-state ghost of the runs FILE names (or of the ``--runs`` subset)
on the CPU and requires each mean TV distance to agree within five standard
errors.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402

import calibration_snapshot  # noqa: E402
import packing  # noqa: E402

AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
INDEX = ROOT / "docs/evidence/calibration/history/index.json"
MAX_QUBITS = 14
SEED = 20261016


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def distribution(counts: dict[str, int], clbits: int) -> np.ndarray:
    """live_run._distribution: outcome index from the joined bit string, clbit 0 least significant."""
    dist = np.zeros(2**clbits)
    for key, count in counts.items():
        dist[int(key.replace(" ", ""), 2)] += count
    return dist / dist.sum()


def measured_members(
    run: Path,
) -> tuple[dict[str, list[np.ndarray]], dict[str, dict[str, Any]], dict[str, list[float]]]:
    """Hardware distributions, execution windows and recorded replay distances from every collect pass."""
    data = json.loads((run / "collect.json").read_text(encoding="utf-8"))
    measured: dict[str, list[np.ndarray]] = {}
    executed: dict[str, dict[str, Any]] = {}
    recorded: dict[str, list[float]] = {}
    for collection in data if isinstance(data, list) else [data]:
        for name, replicas in (collection.get("measured") or {}).items():
            measured[name] = [np.asarray(r, dtype=float) for r in replicas]
        executed.update(collection.get("executed") or {})
        recorded.update(collection.get("tvd_measured_to_replayed") or {})
    return measured, executed, recorded


def member_replicas(
    record: dict[str, Any], isas: dict[str, QuantumCircuit]
) -> dict[str, tuple[str, list[QuantumCircuit]]]:
    """Each logical member's backend and replica circuits, rebuilt as live_run._archived_entries does."""
    planned = (record.get("submission") or {}).get("planned_jobs")
    if planned is None:
        raise SystemExit("record predates the fused-PUB submission plan")
    components: dict[str, tuple[str, str, dict[str, Any]]] = {}
    for job in planned:
        for pub in job["pubs"]:
            for component in pub["components"]:
                components[component["member"]] = (job["backend"], pub["name"], component)
    out: dict[str, tuple[str, list[QuantumCircuit]]] = {}
    for group in record["groups"]:
        for member in group["members"]:
            name = member["name"]
            if name not in components:
                continue
            backend, pub_name, component = components[name]
            qubits = sorted({q for replica in member["replica_qubits"] for q in replica})
            packed = packing.extract(isas[pub_name], component["register_prefix"], qubits, name)
            replicas = [
                packing.split(packed, component["register_prefix"] + prefix, replica_qubits, name)
                for prefix, replica_qubits in zip(member["replica_prefixes"], member["replica_qubits"], strict=True)
            ]
            out[name] = (backend, replicas)
    return out


def active_width(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(q).index for instruction in circuit.data for q in instruction.qubits})


def tv(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.abs(left - right).sum())


def ghost_run(run_name: str, states: str, device: str, index: dict[str, Any]) -> dict[str, Any]:
    run = ROOT / run_name
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    isas = {c.name: c for c in qpy.load(io.BytesIO((run / "isa.qpy").read_bytes()))}
    shots = int(record["shots"])
    try:
        replicas = member_replicas(record, isas)
    except SystemExit as reason:
        return {"run": run_name, "skipped": str(reason)}
    measured, executed, recorded = measured_members(run)
    starts = {w["start"]: w["snapshot"] for job in index["jobs"] if job["run"] == run_name for w in job["windows"]}
    backend = next(iter({b for b, _ in replicas.values()}))
    same_backend = sorted(f for f in index["files"] if f.startswith(f"docs/evidence/calibration/history/{backend}/"))
    plan: dict[str, list[str]] = {"execution": []}
    if states in ("current", "all", "execution,current"):
        plan["current"] = [index["current"][backend]]
    if states == "all":
        plan["other"] = [f for f in same_backend if f not in set(starts.values()) | {index["current"][backend]}]
    members = [
        name for name in replicas if name in measured and all(active_width(r) <= MAX_QUBITS for r in replicas[name][1])
    ]
    skipped = sorted(set(replicas) - set(members))
    results: dict[str, Any] = {}
    snapshots_used = {executed[m]["start"]: starts.get(executed[m]["start"]) for m in members if m in executed}
    execution_files = sorted({f for f in snapshots_used.values() if f})
    state_files = [("execution", f) for f in execution_files]
    state_files += [(kind, f) for kind in ("current", "other") for f in plan.get(kind, [])]
    for kind, relative in state_files:
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        simulator = calibration_snapshot.noise_simulator(snapshot, device=device)
        if kind == "execution":
            chosen = [m for m in members if starts.get(executed.get(m, {}).get("start", "")) == relative]
        else:
            chosen = members
        circuits = [replica for m in chosen for replica in replicas[m][1]]
        if not circuits:
            continue
        start = time.time()
        result = simulator.run(circuits, shots=shots, seed_simulator=SEED).result()
        position = 0
        distances: dict[str, list[float]] = {}
        for m in chosen:
            row = []
            for k, replica in enumerate(replicas[m][1]):
                ghost = distribution(result.get_counts(position), replica.num_clbits)
                row.append(round(tv(measured[m][k], ghost), 6))
                position += 1
            distances[m] = row
        entry = results.setdefault(relative, {"state": kind, "calibration": snapshot["calibration"], "tvd": {}})
        entry["tvd"].update(distances)
        entry["seconds"] = round(entry.get("seconds", 0) + time.time() - start, 2)
    summary = {}
    for relative, entry in results.items():
        values = [v for row in entry["tvd"].values() for v in row]
        summary[relative] = {
            "state": entry["state"],
            "calibration": entry["calibration"],
            "members": len(entry["tvd"]),
            "mean_tvd": round(float(np.mean(values)), 6),
        }
    deltas = [
        ghost - recorded_value
        for entry in results.values()
        if entry["state"] == "execution"
        for m, row in entry["tvd"].items()
        if m in recorded
        for ghost, recorded_value in zip(row, recorded[m], strict=False)
    ]
    self_check = {
        "pairs": len(deltas),
        "mean_ghost_minus_recorded_tvd": round(float(np.mean(deltas)), 6) if deltas else None,
        "sd": round(float(np.std(deltas)), 6) if deltas else None,
    }
    print(json.dumps({"run": run_name, "summary": summary, "self_check": self_check}), flush=True)
    return {
        "run": run_name,
        "backend": backend,
        "shots": shots,
        "members_ghosted": len(members),
        "members_skipped_width": skipped,
        "summary": summary,
        "self_check": self_check,
        "states": results,
    }


def audited_runs() -> list[str]:
    return sorted({job["run"] for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--states", default="all", choices=("execution", "execution,current", "current", "all"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        named = None if args.runs == "all" else set(args.runs.split(","))
        checked = 0
        for run in retained["runs"]:
            if "skipped" in run or (named is not None and run["run"] not in named):
                continue
            checked += 1
            fresh = ghost_run(run["run"], "execution", "CPU", index)
            for relative, summary in run["summary"].items():
                if summary["state"] != "execution":
                    continue
                old, new = summary["mean_tvd"], fresh["summary"][relative]["mean_tvd"]
                pairs = max(1, summary["members"])
                require(
                    abs(old - new) <= 5 * math.sqrt(2.0 / (pairs * run["shots"])) + 1e-3,
                    f"{run['run']}: {old} vs {new}",
                )
        require(checked > 0 and (named is None or checked == len(named)), "--runs names a run FILE lacks")
        print(f"{args.check}: execution-state ghosts of {checked} runs reproduced on the CPU")
        return 0
    require(args.out is not None, "--out is required")
    runs = audited_runs() if args.runs == "all" else args.runs.split(",")
    device = os.environ.get("GOROROBA_AER_DEVICE", "CPU")
    out = {
        "schema": "ghost-run-v1",
        "device": device,
        "max_qubits": MAX_QUBITS,
        "seed": SEED,
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "runs": [ghost_run(run, args.states, device, index) for run in runs],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

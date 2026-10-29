"""Paired exact-law test of local idle padding against the retained dynamic IBM runs.

For every replica of every member that ghost_run.py ghosts on a run holding a dynamic member, this script
computes two exact laws under the member's execution snapshot (docs/evidence/calibration/history/):

- unpadded: dynamic_density.probabilities on the replica restricted to its active qubits, as ghost_run.exact_law,
  with the circuit's own delays written in as relaxation channels (scheduled_idle_replay.relaxed);
- padded: the same replica after idle_padding.pad under the restricted snapshot's Target durations, with the
  noise model's delay relaxation written in as channels (scheduled_idle_replay.relaxed).

It reports d = TVD(measured, padded) - TVD(measured, unpadded) per replica and, per run, the mean d, its standard
error over replicas and the replica count. The decision rule (issue 526) passes when a strict majority of eligible
runs has a negative mean d and lists each run whose mean d lies more than two standard errors above zero. Exact
laws carry no shot noise, so the script draws no seed.

Usage:
    "$PYTHON" scripts/local_idle_falsifier.py --runs all --out docs/evidence/local_idle_padding/result.json
    "$PYTHON" scripts/local_idle_falsifier.py --runs results/live/2026-10-18T090603.530638Z --out OUT
    "$PYTHON" scripts/local_idle_falsifier.py --runs all --out OUT --parts DIR
    "$PYTHON" scripts/local_idle_falsifier.py --plan
    "$PYTHON" scripts/local_idle_falsifier.py --check docs/evidence/local_idle_padding/result.json --runs RUN[,RUN]

``--check FILE`` requires FILE to list every audited run exactly once, recomputes its decision from its runs, and
reruns each run named by ``--runs`` (``all`` reruns every one), requiring the fresh summary to equal the retained one
exactly.

``--parts DIR`` writes each run's full summary to DIR as soon as the run finishes and reuses a part whose
package versions and source digests (this script and the repository modules it evaluates with) match the
current ones, so a sweep that dies part way resumes at the first unfinished run. ``--parts-only`` assembles the
result from parts written elsewhere (the idle-falsifier workflow) and fails on a missing or mismatched part.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_run  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.dagcircuit.exceptions import DAGCircuitError  # noqa: E402
from scheduled_idle_replay import _without_delays, relaxed  # noqa: E402

import calibration_snapshot  # noqa: E402
import idle_padding  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

SCHEMA = "local-idle-padding-falsifier-v1"

Item = tuple[bytes, dict[str, Any], list[float]]

# The modules whose code decides a run's summary; a part is reused only when every one is byte-identical.
PART_SOURCES = (
    "scripts/local_idle_falsifier.py",
    "scripts/ghost_run.py",
    "scripts/scheduled_idle_replay.py",
    "gororoba_quantum/calibration_snapshot.py",
    "gororoba_quantum/dynamic_density.py",
    "gororoba_quantum/idle_padding.py",
    "gororoba_quantum/snapshot_laws.py",
)


def _serialized(circuit: QuantumCircuit) -> bytes:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


def replica_pair(item: Item) -> dict[str, Any]:
    """Unpadded and padded TV distances of one restricted replica to its measured law."""
    import dynamic_density

    payload, snapshot, measured = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    view, noise = calibration_snapshot.noise_model(snapshot)
    bare = dynamic_density.probabilities(relaxed(circuit, noise), noise)
    padded, inserted = idle_padding.pad(circuit, idle_padding.target_duration(view.target))
    law = dynamic_density.probabilities(relaxed(padded, noise), noise)
    hardware = np.asarray(measured)
    unpadded_tvd = ghost_run.tv(hardware, bare)
    padded_tvd = ghost_run.tv(hardware, law)
    return {
        "unpadded_tvd": round(unpadded_tvd, 9),
        "padded_tvd": round(padded_tvd, 9),
        "difference": round(padded_tvd - unpadded_tvd, 9),
        "inserted_dt": {str(q): v for q, v in sorted(inserted.items())},
        "unpadded_law": [round(float(v), 12) for v in bare],
        "padded_law": [round(float(v), 12) for v in law],
    }


def eligible_items(run_name: str, index: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, int]], list[Item]]:
    """The run's header, (member, replica) keys and replica items, or a header naming why the run is out."""
    prepared = ghost_run.prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "out": prepared["skipped"]}, [], []
    import dynamic_density

    replicas, execution = prepared["replicas"], prepared["execution"]
    members = [m for m in prepared["members"] if m in execution]
    if not any(ghost_run.is_dynamic(r) for m in members for r in replicas[m][1]):
        return {"run": run_name, "out": "no dynamic member"}, [], []
    snapshots: dict[str, dict[str, Any]] = {}
    keys: list[tuple[str, int]] = []
    items: list[Item] = []
    refused: dict[str, str] = {}
    exact: list[str] = []
    for m in members:
        # The relaxation pass turns every top-level delay into channels and both arms then drop the delays, so a
        # member's own delays leave it in the branch-resolved model.
        reasons = [dynamic_density.structural_refusal(_without_delays(r)) for r in replicas[m][1]]
        if any(reasons):
            refused[m] = next(str(r) for r in reasons if r)
            continue
        try:
            # A qubit that acts only inside a control-flow body is not an active wire of the top-level DAG, so
            # restrict_circuit cannot drop the other wires; ghost_run keeps such a member on Aer.
            reduced_pairs = [snapshot_laws.restrict_circuit(r) for r in replicas[m][1]]
        except DAGCircuitError as error:
            refused[m] = f"restrict_circuit: {str(error)[:80]}"
            continue
        relative = execution[m]
        if relative not in snapshots:
            snapshots[relative] = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        exact.append(m)
        for k, (reduced, qubits) in enumerate(reduced_pairs):
            restricted = snapshot_laws.restrict(snapshots[relative], qubits)
            keys.append((m, k))
            items.append((_serialized(reduced), restricted, prepared["measured"][m][k].tolist()))
    header = {
        "run": run_name,
        "backend": prepared["backend"],
        "members": len(exact),
        "members_refused": refused,
        "dynamic_members": sorted(m for m in exact if any(ghost_run.is_dynamic(r) for r in replicas[m][1])),
        "widths": sorted({ghost_run.active_width(r) for m in exact for r in replicas[m][1]}),
    }
    return header, keys, items


def run_summary(header: dict[str, Any], keys: list[tuple[str, int]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    differences = np.asarray([row["difference"] for row in rows])
    n = len(differences)
    mean = float(differences.mean())
    se = float(differences.std(ddof=1) / math.sqrt(n)) if n > 1 else math.nan
    dynamic = set(header["dynamic_members"])
    dynamic_d = [row["difference"] for (m, _), row in zip(keys, rows, strict=True) if m in dynamic]
    return {
        **header,
        "replicas": n,
        "mean_difference": round(mean, 9),
        "standard_error": round(se, 9) if n > 1 else None,
        "mean_unpadded_tvd": round(float(np.mean([row["unpadded_tvd"] for row in rows])), 9),
        "mean_padded_tvd": round(float(np.mean([row["padded_tvd"] for row in rows])), 9),
        "dynamic_replicas": len(dynamic_d),
        "dynamic_mean_difference": round(float(np.mean(dynamic_d)), 9) if dynamic_d else None,
        "per_replica": {
            m: [row for (member, _), row in zip(keys, rows, strict=True) if member == m]
            for m in dict.fromkeys(member for member, _ in keys)
        },
    }


def decision(runs: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [run for run in runs if "mean_difference" in run]
    lower = [run["run"] for run in scored if run["mean_difference"] < 0]
    worse = [
        run["run"]
        for run in scored
        if run["standard_error"] is not None and run["mean_difference"] > 2 * run["standard_error"]
    ]
    return {
        "eligible_runs": len(scored),
        "runs_lower": len(lower),
        "passes": 2 * len(lower) > len(scored),
        "runs_worse_by_two_se": worse,
    }


def evaluate(name: str, index: dict[str, Any], plan: bool = False) -> dict[str, Any]:
    """One run's summary, or its header naming why it is out (with its replica count under plan)."""
    header, keys, items = eligible_items(name, index)
    if not items:
        header.setdefault("out", "no member with an exact law")
        return header
    if plan:
        return {**header, "replicas": len(items)}
    # Each exact law takes seconds to minutes, so even a two-replica run fills the pool.
    return run_summary(header, keys, parallel.ordered_map(replica_pair, items, min_items=2))


def check(path: Path, runs: str, index: dict[str, Any]) -> None:
    retained = json.loads(path.read_text(encoding="utf-8"))
    listed = [run["run"] for run in retained["runs"]]
    if sorted(listed) != sorted(ghost_run.audited_runs()) or len(set(listed)) != len(listed):
        raise RuntimeError(f"{path}: runs are not each audited run exactly once")
    if retained.get("schema") != SCHEMA or retained.get("decision") != decision(retained["runs"]):
        raise RuntimeError(f"{path}: schema or decision differs from its runs")
    by_run = {run["run"]: run for run in retained["runs"]}
    names = listed if runs == "all" else runs.split(",")
    for name in names:
        if name not in by_run:
            raise RuntimeError(f"{path}: {name} is not a retained run")
        if evaluate(name, index) != by_run[name]:
            raise RuntimeError(f"{path}: {name} does not reproduce")
    print(json.dumps({"checked": names, "versions": versions()}))


def versions() -> dict[str, str]:
    import qiskit
    import qiskit_aer

    return {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__, "numpy": np.__version__}


def part_identity() -> dict[str, Any]:
    sources = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in PART_SOURCES}
    return {"versions": versions(), "sources": sources}


def evaluate_with_parts(
    name: str, index: dict[str, Any], parts: Path, identity: dict[str, Any], parts_only: bool = False
) -> dict[str, Any]:
    """The run's summary from a matching part in PARTS, or a fresh evaluation written there before returning."""
    part = parts / (Path(name).name + ".json")
    if part.exists():
        stored = json.loads(part.read_text(encoding="utf-8"))
        if stored.get("identity") == identity and stored.get("summary", {}).get("run") == name:
            return stored["summary"]
    if parts_only:
        raise RuntimeError(f"{part}: no part matching the current versions and sources")
    summary = evaluate(name, index)
    parts.mkdir(parents=True, exist_ok=True)
    staging = part.with_suffix(".tmp")
    staging.write_text(json.dumps({"identity": identity, "summary": summary}, sort_keys=True) + "\n", encoding="utf-8")
    staging.replace(part)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all", help="all, or comma-separated run directories")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--plan", action="store_true", help="print each run's eligibility, widths and replica count")
    parser.add_argument("--parts", type=Path, help="directory of per-run summaries to write and resume from")
    parser.add_argument("--parts-only", action="store_true", help="assemble from --parts and refuse to evaluate")
    parser.add_argument("--check", type=Path, help="rerun the --runs runs of a retained result and compare")
    args = parser.parse_args()
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.check:
        check(args.check, args.runs, index)
        return 0
    names = ghost_run.audited_runs() if args.runs == "all" else args.runs.split(",")
    if args.parts and args.plan:
        parser.error("--parts applies to an evaluation, not to --plan")
    if args.parts_only and not args.parts:
        parser.error("--parts-only needs --parts")
    identity = part_identity() if args.parts else None
    runs: list[dict[str, Any]] = []
    for name in names:
        if args.parts and identity is not None:
            summary = evaluate_with_parts(name, index, args.parts, identity, args.parts_only)
        else:
            summary = evaluate(name, index, args.plan)
        runs.append(summary)
        print(json.dumps({k: v for k, v in summary.items() if k != "per_replica"}), flush=True)
    if args.plan:
        return 0
    result = {"schema": SCHEMA, "versions": versions(), "runs": runs, "decision": decision(runs)}
    print(json.dumps(result["decision"]))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

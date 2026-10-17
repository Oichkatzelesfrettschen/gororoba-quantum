"""Ghost runs: replay every retained IBM job's circuits in Aer under any retained calibration state.

A ghost run takes a submitted run's archived ISA circuits (isa.qpy), rebuilds
each logical member's replicas exactly as live_run.collect does
(packing.extract on the member's fused-PUB component, packing.split per
replica, from record.json's submission plan and group record), and samples
them under a calibration snapshot from docs/evidence/calibration/history/
(scripts/ghost_calibrations.py). It then compares each replica's ghost
distribution with the hardware distribution that collect.json retains
(``measured``) by total-variation distance.

Each member is sampled at the shot count its job ran with (collect.json
``executed[m]["shots"]``, the pub_shots tier), as live_run.collect replays it.
With ``--states all`` every retained snapshot of the run's backend covers
every member; per member, the snapshot in force when its PUB began
(index.json maps every job's execution start to it) is its execution
snapshot. Under that snapshot the TV distance to the hardware should match
the record's own ``tvd_measured_to_replayed`` up to sampling noise, since
both use live_run's noise model for that calibration. ``self_check`` reports
the mean absolute and maximum difference, the signed mean as a bias
diagnostic, and the mean absolute difference between two independent ghost
draws, which is the scatter the first reaches when the models agree.

For each run and snapshot the output gives the mean TV distance over all
members and over the members that ran under it, so a reader sees whether the
hardware sits closest to its own execution calibration, how far calibration
drift alone moves the prediction, and how large the floor no calibration
explains is.

Members wider than MAX_QUBITS active qubits are skipped with that reason: a
density matrix beyond 14 qubits leaves a 15 GiB T4 (docs/notes/kaggle/
substrates.md). Runs whose record predates the fused-PUB submission plan are
skipped with the record's reason.

``--runs all`` ghosts every audited run; ``--runs RUN[,RUN]`` names run
directories. ``--states execution`` restricts each execution snapshot to the
members that ran under it; ``execution,current`` adds the export-time
snapshot over every member, and ``all`` (the default) every snapshot. The
entry reads GOROROBA_AER_DEVICE (CPU by default).

``--check FILE`` requires FILE to hold every audited run exactly once. It
rebuilds every run's skip reason, members, width exclusions, shots and
execution snapshots from the archived inputs and requires them, full
snapshot coverage, and the summaries and recorded-replay agreement
recomputed from the retained distances. It then reruns the execution-state
ghost of the runs FILE names (or of the ``--runs`` subset) on GOROROBA_AER_DEVICE and
requires each execution mean TV distance to agree within five standard
errors.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
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
# Seed blocks of the main draw and the independent resample never overlap.
SEED_STRIDE = 100_000
RESAMPLE_SEED = SEED + 50 * SEED_STRIDE


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


def sample(simulator: Any, circuits: list[QuantumCircuit], shots: list[int], seed: int) -> list[dict[str, int]]:
    """Counts of each circuit at its own shot count; one Aer call per shot tier, in input order.

    Aer seeds experiment k of a call with seed_simulator + k, so tier t starts
    at seed + t * SEED_STRIDE and no two circuits of one draw share a seed.
    """
    require(len(circuits) < SEED_STRIDE, f"{len(circuits)} circuits exceed the seed stride")
    counts: list[dict[str, int]] = [{} for _ in circuits]
    for offset, tier in enumerate(sorted(set(shots))):
        positions = [k for k, n in enumerate(shots) if n == tier]
        result = simulator.run(
            [circuits[k] for k in positions], shots=tier, seed_simulator=seed + offset * SEED_STRIDE
        ).result()
        for index, k in enumerate(positions):
            counts[k] = result.get_counts(index)
    return counts


def prepare(run_name: str, index: dict[str, Any]) -> dict[str, Any]:
    """Everything a ghost of the run derives from its archived inputs before simulating, or its skip reason."""
    run = ROOT / run_name
    missing = [name for name in ("record.json", "isa.qpy", "collect.json") if not (run / name).is_file()]
    if missing:
        # A recovered acquisition keeps its submitted circuits and raw counts
        # without a planning record, so its members cannot be rebuilt.
        return {"skipped": f"the run keeps no {', '.join(missing)}"}
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    isas = {c.name: c for c in qpy.load(io.BytesIO((run / "isa.qpy").read_bytes()))}
    try:
        replicas = member_replicas(record, isas)
    except SystemExit as reason:
        return {"skipped": str(reason)}
    measured, executed, recorded = measured_members(run)
    starts = {w["start"]: w["snapshot"] for job in index["jobs"] if job["run"] == run_name for w in job["windows"]}
    backends = {b for b, _ in replicas.values()}
    require(len(backends) == 1, f"{run_name}: members span backends {sorted(backends)}")
    members = [
        name for name in replicas if name in measured and all(active_width(r) <= MAX_QUBITS for r in replicas[name][1])
    ]
    # live_run.collect replays each job at its own shot count (pub_shots
    # tiers), which collect.json records per executed member.
    shots = {m: int(executed.get(m, {}).get("shots") or record["shots"]) for m in members}
    return {
        "backend": backends.pop(),
        "replicas": replicas,
        "measured": measured,
        "recorded": recorded,
        "members": members,
        "skipped_width": sorted(set(replicas) - set(members)),
        "shots": shots,
        "execution": {m: starts[executed[m]["start"]] for m in members if executed.get(m, {}).get("start") in starts},
    }


def summarize(results: dict[str, Any], execution: dict[str, str]) -> dict[str, Any]:
    """Per snapshot: mean TV distance over all members and over the members that ran under it."""
    summary = {}
    for relative, entry in results.items():
        own_values = [v for m, row in entry["tvd"].items() if execution.get(m) == relative for v in row]
        summary[relative] = {
            "calibration": entry["calibration"],
            "current": entry["current"],
            "members": len(entry["tvd"]),
            "mean_tvd": round(float(np.mean([v for row in entry["tvd"].values() for v in row])), 6),
            "execution_members": sum(execution.get(m) == relative for m in entry["tvd"]),
            "execution_mean_tvd": round(float(np.mean(own_values)), 6) if own_values else None,
        }
    return summary


def recorded_agreement(
    results: dict[str, Any], execution: dict[str, str], recorded: dict[str, list[float]]
) -> dict[str, Any]:
    """Ghost minus recorded replay distance, under each member's execution snapshot."""
    deltas = [
        g - r
        for m in sorted(recorded)
        if m in execution and execution[m] in results and m in results[execution[m]]["tvd"]
        for g, r in zip(results[execution[m]]["tvd"][m], recorded[m], strict=True)
    ]
    return {
        "pairs": len(deltas),
        "mean_abs_ghost_minus_recorded_tvd": round(float(np.mean(np.abs(deltas))), 6) if deltas else None,
        "max_abs_ghost_minus_recorded_tvd": round(float(np.max(np.abs(deltas))), 6) if deltas else None,
        "mean_ghost_minus_recorded_tvd": round(float(np.mean(deltas)), 6) if deltas else None,
        "sd": round(float(np.std(deltas)), 6) if deltas else None,
    }


def ghost_run(run_name: str, states: str, device: str, index: dict[str, Any]) -> dict[str, Any]:
    prepared = prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    backend, replicas, measured = prepared["backend"], prepared["replicas"], prepared["measured"]
    recorded, members, shots = prepared["recorded"], prepared["members"], prepared["shots"]
    execution = prepared["execution"]
    same_backend = sorted(f for f in index["files"] if f.startswith(f"docs/evidence/calibration/history/{backend}/"))
    current = index["current"][backend]
    # all: every snapshot over every member. execution: each execution
    # snapshot over the members that ran under it. current: the export-time
    # snapshot over every member. execution,current: both of the latter.
    plan = same_backend if states == "all" else []
    if states in ("execution", "execution,current"):
        plan = sorted(set(plan) | set(execution.values()))
    if states in ("current", "execution,current"):
        plan = sorted(set(plan) | {current})
    results: dict[str, Any] = {}
    resample: dict[str, list[float]] = {}
    for relative in plan:
        snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        simulator = calibration_snapshot.noise_simulator(snapshot, device=device)
        covers_all = states == "all" or (relative == current and states != "execution")
        chosen = [m for m in members if covers_all or execution.get(m) == relative]
        if not chosen:
            continue
        start = time.time()
        circuits = [replica for m in chosen for replica in replicas[m][1]]
        circuit_shots = [shots[m] for m in chosen for _ in replicas[m][1]]
        counts = iter(sample(simulator, circuits, circuit_shots, SEED))
        distances = {
            m: [
                round(tv(measured[m][k], distribution(next(counts), r.num_clbits)), 6)
                for k, r in enumerate(replicas[m][1])
            ]
            for m in chosen
        }
        # An independent second draw of the members with a recorded replay
        # distance gives the sampling scatter of |ghost - recorded| when the
        # two models agree.
        own = [m for m in chosen if execution.get(m) == relative and m in recorded]
        if own:
            circuits = [replica for m in own for replica in replicas[m][1]]
            circuit_shots = [shots[m] for m in own for _ in replicas[m][1]]
            counts = iter(sample(simulator, circuits, circuit_shots, RESAMPLE_SEED))
            for m in own:
                resample[m] = [
                    round(tv(measured[m][k], distribution(next(counts), r.num_clbits)), 6)
                    for k, r in enumerate(replicas[m][1])
                ]
        results[relative] = {
            "calibration": snapshot["calibration"],
            **calibration_snapshot.backend_identity(snapshot),
            "current": relative == current,
            "tvd": distances,
            "seconds": round(time.time() - start, 2),
        }
    summary = summarize(results, execution)
    scatter = [
        abs(g - h) for m, rows in resample.items() for g, h in zip(results[execution[m]]["tvd"][m], rows, strict=True)
    ]
    agreement = recorded_agreement(results, execution, recorded)
    self_check = {
        "pairs": agreement["pairs"],
        "mean_abs_ghost_minus_recorded_tvd": agreement["mean_abs_ghost_minus_recorded_tvd"],
        "max_abs_ghost_minus_recorded_tvd": agreement["max_abs_ghost_minus_recorded_tvd"],
        "mean_abs_ghost_minus_resampled_tvd": round(float(np.mean(scatter)), 6) if scatter else None,
        "mean_ghost_minus_recorded_tvd": agreement["mean_ghost_minus_recorded_tvd"],
        "sd": agreement["sd"],
    }
    print(json.dumps({"run": run_name, "summary": summary, "self_check": self_check}), flush=True)
    return {
        "run": run_name,
        "backend": backend,
        "shots": {str(n): sum(1 for m in members if shots[m] == n) for n in sorted(set(shots.values()))},
        "members_ghosted": len(members),
        "members_skipped_width": prepared["skipped_width"],
        "member_shots": shots,
        "execution_snapshot": execution,
        "summary": summary,
        "self_check": self_check,
        "snapshots": results,
    }


def validate(run: dict[str, Any], index: dict[str, Any]) -> None:
    """Require every field of a retained run that its archived inputs and its own TV distances determine.

    Only the simulated distances and the resampled scatter come from Aer;
    the skip reason, members, width exclusions, shots, execution snapshots,
    snapshot coverage, summaries and recorded-replay agreement are rebuilt
    here (prepare, summarize, recorded_agreement) and must match.
    """
    name = run["run"]
    prepared = prepare(name, index)
    if "skipped" in prepared:
        require(run.get("skipped") == prepared["skipped"], f"{name}: skip reason differs")
        return
    require("skipped" not in run, f"{name}: marked skipped although its inputs rebuild")
    members, shots, execution = prepared["members"], prepared["shots"], prepared["execution"]
    require(run["backend"] == prepared["backend"], f"{name}: backend differs")
    require(run["members_ghosted"] == len(members), f"{name}: member count differs")
    require(run["members_skipped_width"] == prepared["skipped_width"], f"{name}: width exclusions differ")
    require(run["member_shots"] == shots, f"{name}: member shots differ")
    require(run["execution_snapshot"] == execution, f"{name}: execution snapshots differ")
    tiers = {str(n): sum(1 for m in members if shots[m] == n) for n in sorted(set(shots.values()))}
    require(run["shots"] == tiers, f"{name}: shot tiers differ")
    prefix = f"docs/evidence/calibration/history/{prepared['backend']}/"
    expected = sorted(f for f in index["files"] if f.startswith(prefix))
    require(sorted(run["snapshots"]) == expected, f"{name}: snapshots differ from the index")
    current = index["current"][prepared["backend"]]
    for relative, entry in run["snapshots"].items():
        require(entry["calibration"] == index["files"][relative]["calibration"], f"{name}: {relative} identity")
        require(entry["current"] == (relative == current), f"{name}: {relative} current flag")
        require(set(entry["tvd"]) == set(members), f"{name}: {relative} lacks ghosted members")
        for m, row in entry["tvd"].items():
            require(len(row) == len(prepared["replicas"][m][1]), f"{name}: {relative} {m} replica count")
    require(run["summary"] == summarize(run["snapshots"], execution), f"{name}: summary differs from its distances")
    agreement = recorded_agreement(run["snapshots"], execution, prepared["recorded"])
    require(
        all(run["self_check"][key] == value for key, value in agreement.items()),
        f"{name}: recorded-replay agreement differs from its distances",
    )


def content_key(relative: str) -> str:
    """Digest of a snapshot's noise-relevant content; distinct calibration identities can share it."""
    snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    body = {key: snapshot[key] for key in ("num_qubits", "dt", "qubits", "instructions")}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]


def paired(run: dict[str, Any], relative: str) -> dict[str, Any] | None:
    """Per-replica TV distance under one snapshot minus under each member's execution snapshot.

    Members of one PUB share its shots, so the standard error is clustered by
    executed PUB: the deviations summed within each PUB enter as one term,
    with the G / (G - 1) small-sample factor; it is undefined below two PUBs.
    """
    snapshots, execution = run["snapshots"], run["execution_snapshot"]
    executed = measured_members(ROOT / run["run"])[1]
    other = snapshots[relative]["tvd"]
    pairs = [
        (executed[m]["pub"], b - a)
        for m, own in execution.items()
        if m in other and m in snapshots[own]["tvd"]
        for a, b in zip(snapshots[own]["tvd"][m], other[m], strict=True)
    ]
    if not pairs:
        return None
    deltas = np.array([d for _, d in pairs])
    mean = float(deltas.mean())
    sums: dict[str, float] = {}
    for pub, d in pairs:
        sums[pub] = sums.get(pub, 0.0) + d - mean
    clusters = len(sums)
    error = (
        math.sqrt(clusters / (clusters - 1) * sum(v * v for v in sums.values())) / len(pairs)
        if clusters > 1
        else math.nan
    )
    return {
        "replicas": len(pairs),
        "pubs": clusters,
        "mean_delta": round(mean, 6),
        "standard_error": round(error, 6) if clusters > 1 else None,
    }


def error_means(relative: str, qubits: set[int]) -> tuple[float, float]:
    """Mean CZ error over couplers inside qubits, and mean readout assignment error over qubits."""
    snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    cz = [e["error"] for e in snapshot["instructions"]["cz"] if set(e["qargs"]) <= qubits and e["error"] is not None]
    readout = [(snapshot["qubits"][q]["e01"] + snapshot["qubits"][q]["e10"]) / 2 for q in sorted(qubits)]
    return float(np.mean(cz)), float(np.mean(readout))


def calibration_change(run: dict[str, Any], current: str) -> dict[str, Any]:
    """Current minus execution mean CZ and readout error on the qubits the run's ghosted members used.

    A run whose members ran under several snapshots takes the one most of
    them ran under as its execution calibration.
    """
    record = json.loads((ROOT / run["run"] / "record.json").read_text(encoding="utf-8"))
    qubits = {
        q
        for group in record["groups"]
        for member in group["members"]
        if member["name"] in run["member_shots"]
        for replica in member["replica_qubits"]
        for q in replica
    }
    owners = sorted(run["execution_snapshot"].values())
    execution = max(sorted(set(owners)), key=owners.count)
    cz_before, readout_before = error_means(execution, qubits)
    cz_now, readout_now = error_means(current, qubits)
    return {
        "qubits": len(qubits),
        "execution_snapshot": execution,
        "cz_error_change": round(cz_now - cz_before, 9),
        "readout_error_change": round(readout_now - readout_before, 9),
    }


def report(path: Path) -> dict[str, Any]:
    """Per run: execution means, paired current-minus-execution difference, and every distinct state's mean."""
    retained = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for run in retained["runs"]:
        if "skipped" in run:
            rows.append({"run": run["run"], "skipped": run["skipped"]})
            continue
        summary = run["summary"]
        by_content: dict[str, list[str]] = {}
        for relative in summary:
            by_content.setdefault(content_key(relative), []).append(relative)
        means = {key: summary[sorted(group)[0]]["mean_tvd"] for key, group in sorted(by_content.items())}
        current = [relative for relative, entry in summary.items() if entry["current"]]
        rows.append(
            {
                "run": run["run"],
                "backend": run["backend"],
                "members": run["members_ghosted"],
                "shots": run["shots"],
                "execution_mean_tvd": [
                    v["execution_mean_tvd"] for _, v in sorted(summary.items()) if v["execution_members"]
                ],
                "current_minus_execution": paired(run, current[0]) if current else None,
                "distinct_states": len(means),
                "state_mean_tvd_range": [min(means.values()), max(means.values())],
                "self_check": run["self_check"],
                "calibration_change": calibration_change(run, current[0]) if current else None,
            }
        )
    changed = [r for r in rows if r.get("calibration_change") and r.get("current_minus_execution")]
    distance = [r["current_minus_execution"]["mean_delta"] for r in changed]
    correlations = {
        "runs": len(changed),
        "cz_error_higher_now": sum(r["calibration_change"]["cz_error_change"] > 0 for r in changed),
        "cz_error_change_vs_distance_change": round(
            float(np.corrcoef([r["calibration_change"]["cz_error_change"] for r in changed], distance)[0, 1]), 4
        ),
        "readout_error_change_vs_distance_change": round(
            float(np.corrcoef([r["calibration_change"]["readout_error_change"] for r in changed], distance)[0, 1]), 4
        ),
    }
    return {"schema": "ghost-run-report-v4", "source": path.as_posix(), "runs": rows, "correlations": correlations}


def audited_runs() -> list[str]:
    return sorted({job["run"] for job in json.loads(AUDIT.read_text(encoding="utf-8"))["jobs"]})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument("--states", default="all", choices=("execution", "execution,current", "current", "all"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--report", type=Path, help="print the paired summary of a retained result")
    args = parser.parse_args()
    if args.report:
        print(json.dumps(report(args.report), indent=1))
        return 0
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        listed = [run["run"] for run in retained["runs"]]
        require(
            sorted(listed) == audited_runs() and len(set(listed)) == len(listed),
            f"{args.check}: runs are not each audited run exactly once",
        )
        for run in retained["runs"]:
            validate(run, index)
        named = None if args.runs == "all" else set(args.runs.split(","))
        checked = 0
        for run in retained["runs"]:
            if "skipped" in run or (named is not None and run["run"] not in named):
                continue
            checked += 1
            fresh = ghost_run(run["run"], "execution", calibration_snapshot.aer_device(), index)
            for relative, summary in run["summary"].items():
                if not summary["execution_members"]:
                    continue
                old, new = summary["execution_mean_tvd"], fresh["summary"][relative]["execution_mean_tvd"]
                own = [m for m, snapshot in run["execution_snapshot"].items() if snapshot == relative]
                # The execution mean runs over every replica row of its members.
                rows = [run["member_shots"][m] for m in own for _ in run["snapshots"][relative]["tvd"][m]]
                inverse_shots = float(np.mean([1 / shots for shots in rows]))
                require(
                    abs(old - new) <= 5 * math.sqrt(2.0 * inverse_shots / len(rows)) + 1e-3,
                    f"{run['run']}: {old} vs {new}",
                )
        require(checked > 0 and (named is None or checked == len(named)), "--runs names a run FILE lacks")
        device = calibration_snapshot.aer_device()
        print(f"{args.check}: execution-state ghosts of {checked} runs reproduced on {device}")
        return 0
    require(args.out is not None, "--out is required")
    runs = audited_runs() if args.runs == "all" else args.runs.split(",")
    device = calibration_snapshot.aer_device()
    out: dict[str, Any] = {
        "schema": "ghost-run-v2",
        "device": device,
        "max_qubits": MAX_QUBITS,
        "seed": SEED,
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "runs": [],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for run in runs:
        # Written after every run, so a failure keeps every finished one.
        out["runs"].append(ghost_run(run, args.states, device, index))
        args.out.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

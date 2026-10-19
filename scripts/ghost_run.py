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

A dynamic member (mid-circuit measurement, reset or feed-forward) at
EXACT_MIN_SHOTS or more shots, which Aer's density-matrix method evolves
once per shot, draws its counts instead from its exact law: dynamic_density's
branch-resolved evolution under the same noise model, restricted to the
active qubits, then numpy's PCG64 multinomial at the seed Aer would give its
position. A replica dynamic_density.structural_refusal rejects (a delay,
nested or unsupported control flow, a measurement or reset inside a body)
keeps its member on Aer. Each record lists every member's law under
``member_law``; a record without it holds Aer-sampled members only.

``--merge RESULT`` ghosts only the (run, snapshot) pairs RESULT lacks under
the index (every snapshot of an audited run RESULT does not hold, and every
newly indexed snapshot of a retained run's backend), one pair per item of
parallel.ordered_map, and writes RESULT (or ``--out``) with every retained
entry unchanged; the header's ``merged`` list records each merge's device,
versions, added runs and added pairs. A retained run whose archived inputs
and index now give other execution windows, members, shots or laws (a newly
indexed job of that run) is ghosted again in full, and the record lists its
replaced entry's sha256. ``--provenance RESULT BASE`` requires RESULT without
those runs and pairs to be BASE byte for byte, less the replaced runs whose
recorded digests BASE matches, so a merged result still carries the bytes
the kernel that produced BASE wrote. ``--check --runs merged`` replays the
execution-snapshot ghost of every run a merge ghosted in full, bit for bit
on the merge's Aer device. The token ``pairs`` adds the replay of the
(run, snapshot) pairs a merge added to retained runs, bit for bit: the merge
ran on a CPU host and no kernel output holds those pairs, so no retained
shard bytes bind them. sampled_pairs() ranks the pairs of pair_cost() at most
PAIR_COST_CAP by a sha256 over every added pair's distances, and replay_pairs()
replays the first PAIR_SAMPLE. A hand-altered distance is caught only when
its pair is sampled. The token ``pairs-all`` replays every merge-added pair
through the process pool (replay_all_pairs), so a hand-altered distance in
any pair fails; gate core-597 runs it on the full tier.
``--self-test`` exercises the merge, its removal and the exact path's rule
and seeds on synthetic records.

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
from collections.abc import Callable
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
import parallel  # noqa: E402

AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
INDEX = ROOT / "docs/evidence/calibration/history/index.json"
MAX_QUBITS = 14
SEED = 20261016
# Seed blocks of the main draw and the independent resample never overlap.
SEED_STRIDE = 100_000
# Strided slices of the merge-added pairs ranked by pair_cost(): case k replays
# ranks k, k + PAIR_SLICES, ..., so the cases together replay every pair once
# and each holds about one costly pair (ci/gates.json case_registry).
PAIR_SLICES = 4
PAIR_CASES: dict[str, int] = {"slice0": 0, "slice1": 1, "slice2": 2, "slice3": 3}
RESAMPLE_SEED = SEED + 50 * SEED_STRIDE
# Aer seeds experiment k of one call with seed_simulator + 2113 k
# (controller_execute.hpp, the seed_shift loop of controller_execute).
AER_SEED_SHIFT = 2113
# Aer runs the experiments of one call on parallel threads (0: as many as
# its thread budget allows). Each experiment keeps the seed its position
# names, so the counts equal the serial call's.
PARALLEL_EXPERIMENTS = 0
AER_SAMPLED = "aer_sampled"
EXACT_MULTINOMIAL = "exact_multinomial"
# Aer's density-matrix method evolves a dynamic circuit (mid-circuit
# measurement, reset or feed-forward) once per shot, so its cost grows with the
# shots; dynamic_density gives the same law in one branch-resolved evolution.
# A dynamic member at this many shots or more is drawn from its exact law.
EXACT_MIN_SHOTS = 32768


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
    wanted = [member for group in record["groups"] for member in group["members"] if member["name"] in components]
    by_pub: dict[str, list[dict[str, Any]]] = {}
    for member in wanted:
        by_pub.setdefault(components[member["name"]][1], []).append(member)
    packed: dict[str, QuantumCircuit] = {}
    for pub_name, members in by_pub.items():
        specs = [
            (
                components[m["name"]][2]["register_prefix"],
                sorted({q for replica in m["replica_qubits"] for q in replica}),
                m["name"],
            )
            for m in members
        ]
        # One pass over the fused PUB places every member's instructions (packing.extract_many).
        for m, circuit in zip(members, packing.extract_many(isas[pub_name], specs), strict=True):
            packed[m["name"]] = circuit
    out: dict[str, tuple[str, list[QuantumCircuit]]] = {}
    for member in wanted:
        name = member["name"]
        backend, _, component = components[name]
        replicas = [
            packing.split(packed[name], component["register_prefix"] + prefix, replica_qubits, name)
            for prefix, replica_qubits in zip(member["replica_prefixes"], member["replica_qubits"], strict=True)
        ]
        out[name] = (backend, replicas)
    return out


def active_width(circuit: QuantumCircuit) -> int:
    return len({circuit.find_bit(q).index for instruction in circuit.data for q in instruction.qubits})


def tv(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.abs(left - right).sum())


def is_dynamic(circuit: QuantumCircuit) -> bool:
    """Whether Aer must evolve the circuit per shot: control flow, a reset, or an operation after a measurement."""
    measured: set[int] = set()
    for instruction in circuit.data:
        name = instruction.operation.name
        if name == "barrier":
            continue
        if name == "reset" or name in calibration_snapshot.CONTROL_FLOW:
            return True
        qubits = {circuit.find_bit(q).index for q in instruction.qubits}
        if qubits & measured:
            return True
        if name == "measure":
            measured |= qubits
    return False


def member_laws(replicas: dict[str, tuple[str, list[QuantumCircuit]]], shots: dict[str, int]) -> dict[str, str]:
    """Each member's sampling law, EXACT_MULTINOMIAL or AER_SAMPLED.

    A member draws from its exact law when it runs EXACT_MIN_SHOTS or more,
    a replica is dynamic, and dynamic_density.structural_refusal accepts
    every replica; any other member keeps Aer's sampler.
    """
    import dynamic_density

    def exact(m: str, n: int) -> bool:
        circuits = replicas[m][1]
        return (
            n >= EXACT_MIN_SHOTS
            and any(is_dynamic(r) for r in circuits)
            and all(dynamic_density.structural_refusal(r) is None for r in circuits)
        )

    return {m: EXACT_MULTINOMIAL if exact(m, n) else AER_SAMPLED for m, n in shots.items()}


def exact_law(snapshot: dict[str, Any], circuit: QuantumCircuit) -> np.ndarray:
    """The circuit's recorded distribution under the snapshot's noise model, clbit 0 least significant.

    dynamic_density evolves the active qubits only; the snapshot restricted
    to them (snapshot_laws.restrict, renumbered in ascending physical order as
    restrict_circuit renumbers the circuit) carries the same per-qubit and
    per-coupler channels and builds in a fraction of the full device's time.
    """
    import dynamic_density
    import snapshot_laws

    reduced, qubits = snapshot_laws.restrict_circuit(circuit)
    noise = calibration_snapshot.noise_model(snapshot_laws.restrict(snapshot, qubits))[1]
    return dynamic_density.probabilities(reduced, noise)


def multinomial_counts(law: np.ndarray, shots: int, seed: int, clbits: int) -> dict[str, int]:
    """Counts of shots draws from law under numpy's PCG64 at seed, keyed as Aer keys its counts."""
    drawn = np.random.Generator(np.random.PCG64(seed)).multinomial(shots, law)
    return {format(k, f"0{clbits}b"): int(c) for k, c in enumerate(drawn) if c}


def sample(
    simulator: Any,
    circuits: list[QuantumCircuit],
    shots: list[int],
    seed: int,
    exact: dict[int, np.ndarray] | None = None,
) -> list[dict[str, int]]:
    """Counts of each circuit at its own shot count; one Aer call per shot tier, in input order.

    Tier t starts at seed + t * SEED_STRIDE, and Aer seeds experiment k of
    the call with that seed plus AER_SEED_SHIFT k. exact maps a circuit
    position to its exact law; such a circuit leaves the Aer call and draws
    multinomially at the seed its position in the tier names, so the
    remaining Aer experiments keep consecutive positions.
    """
    require(len(circuits) < SEED_STRIDE, f"{len(circuits)} circuits exceed the seed stride")
    exact = exact or {}
    counts: list[dict[str, int]] = [{} for _ in circuits]
    for offset, tier in enumerate(sorted(set(shots))):
        positions = [k for k, n in enumerate(shots) if n == tier]
        base = seed + offset * SEED_STRIDE
        for index, k in enumerate(positions):
            if k in exact:
                counts[k] = multinomial_counts(exact[k], tier, base + AER_SEED_SHIFT * index, circuits[k].num_clbits)
        sampled = [k for k in positions if k not in exact]
        if not sampled:
            continue
        result = simulator.run([circuits[k] for k in sampled], shots=tier, seed_simulator=base).result()
        for index, k in enumerate(sampled):
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
        "laws": member_laws(replicas, shots),
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


def snapshot_entry(
    prepared: dict[str, Any], relative: str, current: str, device: str, chosen: list[str]
) -> tuple[dict[str, Any], dict[str, list[float]]]:
    """The chosen members' TV distances under one snapshot, and the resample of those that executed under it."""
    replicas, measured, shots = prepared["replicas"], prepared["measured"], prepared["shots"]
    execution, recorded, laws = prepared["execution"], prepared["recorded"], prepared["laws"]
    snapshot = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    simulator = (
        calibration_snapshot.noise_simulator(snapshot, device=device)
        if any(laws[m] == AER_SAMPLED for m in chosen)
        else None
    )
    if simulator is not None:
        simulator.set_options(max_parallel_experiments=PARALLEL_EXPERIMENTS)
    start = time.time()
    laws_of = {m: [exact_law(snapshot, r) for r in replicas[m][1]] for m in chosen if laws[m] == EXACT_MULTINOMIAL}

    def draw(members: list[str], seed: int) -> dict[str, list[float]]:
        circuits = [replica for m in members for replica in replicas[m][1]]
        circuit_shots = [shots[m] for m in members for _ in replicas[m][1]]
        exact = {}
        position = 0
        for m in members:
            for k in range(len(replicas[m][1])):
                if m in laws_of:
                    exact[position] = laws_of[m][k]
                position += 1
        counts = iter(sample(simulator, circuits, circuit_shots, seed, exact))
        return {
            m: [
                round(tv(measured[m][k], distribution(next(counts), r.num_clbits)), 6)
                for k, r in enumerate(replicas[m][1])
            ]
            for m in members
        }

    distances = draw(chosen, SEED)
    # An independent second draw of the members with a recorded replay
    # distance gives the sampling scatter of |ghost - recorded| when the
    # two models agree.
    own = [m for m in chosen if execution.get(m) == relative and m in recorded]
    resample = draw(own, RESAMPLE_SEED) if own else {}
    entry = {
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "current": relative == current,
        "tvd": distances,
        "seconds": round(time.time() - start, 2),
    }
    return entry, resample


def run_entry(
    run_name: str, prepared: dict[str, Any], results: dict[str, Any], resample: dict[str, list[float]]
) -> dict[str, Any]:
    """A ghosted run's record from its per-snapshot entries and the resample of its execution snapshots."""
    members, shots, execution = prepared["members"], prepared["shots"], prepared["execution"]
    summary = summarize(results, execution)
    scatter = [
        abs(g - h) for m, rows in resample.items() for g, h in zip(results[execution[m]]["tvd"][m], rows, strict=True)
    ]
    agreement = recorded_agreement(results, execution, prepared["recorded"])
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
        "backend": prepared["backend"],
        "shots": {str(n): sum(1 for m in members if shots[m] == n) for n in sorted(set(shots.values()))},
        "members_ghosted": len(members),
        "members_skipped_width": prepared["skipped_width"],
        "member_shots": shots,
        "member_law": {m: prepared["laws"][m] for m in members},
        "execution_snapshot": execution,
        "summary": summary,
        "self_check": self_check,
        "snapshots": results,
    }


def ghost_run(run_name: str, states: str, device: str, index: dict[str, Any]) -> dict[str, Any]:
    prepared = prepare(run_name, index)
    if "skipped" in prepared:
        return {"run": run_name, "skipped": prepared["skipped"]}
    backend, members, execution = prepared["backend"], prepared["members"], prepared["execution"]
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
        covers_all = states == "all" or (relative == current and states != "execution")
        chosen = [m for m in members if covers_all or execution.get(m) == relative]
        if not chosen:
            continue
        results[relative], own = snapshot_entry(prepared, relative, current, device, chosen)
        resample |= own
    return run_entry(run_name, prepared, results, resample)


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
    # A record without member_law predates the exact path, so every member
    # it holds must be one the rule samples with Aer.
    laws = {m: prepared["laws"][m] for m in members}
    require(
        run.get("member_law", dict.fromkeys(members, AER_SAMPLED)) == laws,
        f"{name}: member laws differ from the rule over its archived inputs",
    )
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


def serialize(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=1) + "\n"


class PairGhost:
    """snapshot_entry() of one (run, snapshot) pair over every ghosted member; picklable for the process pool."""

    def __init__(self, index: dict[str, Any], device: str) -> None:
        self.index = index
        self.device = device

    def __call__(self, pair: tuple[str, str]) -> tuple[dict[str, Any], dict[str, list[float]]]:
        run_name, relative = pair
        prepared = prepare(run_name, self.index)
        current = self.index["current"][prepared["backend"]]
        return snapshot_entry(prepared, relative, current, self.device, prepared["members"])


def entry_digest(run: dict[str, Any]) -> str:
    """sha256 of a run entry in ghost_run's serialization, which a merge records for each run it replaces."""
    return hashlib.sha256(json.dumps(run, indent=1).encode()).hexdigest()


def stale(run: dict[str, Any], prepared: dict[str, Any]) -> bool:
    """Whether the retained run differs from what its archived inputs and the index now determine.

    A newly indexed job of a retained run changes its execution windows, so
    its execution snapshots, summaries and self check no longer follow from
    the retained distances; such a run is ghosted again in full.
    """
    if "skipped" in run or "skipped" in prepared:
        return run.get("skipped") != prepared.get("skipped")
    members = prepared["members"]
    return (
        run["backend"] != prepared["backend"]
        or run["members_ghosted"] != len(members)
        or run["members_skipped_width"] != prepared["skipped_width"]
        or run["member_shots"] != prepared["shots"]
        or run["execution_snapshot"] != prepared["execution"]
        or run.get("member_law", dict.fromkeys(members, AER_SAMPLED)) != {m: prepared["laws"][m] for m in members}
    )


def missing_pairs(
    retained: dict[str, Any], index: dict[str, Any], runs: list[str]
) -> tuple[dict[str, dict[str, Any]], list[tuple[str, str]], dict[str, str]]:
    """The runs to ghost in full with their prepared inputs, every other pair coverage needs, and the replaced runs.

    A run retained lacks, or a retained run stale() finds changed, is ghosted
    under every indexed snapshot of its backend; the replaced map gives each
    such retained run's entry_digest. Any other retained run gains each
    indexed snapshot of its backend it lacks; such a snapshot executed none
    of its members, since its execution windows still map as retained, so
    the run's self check stays.
    """
    by_run = {run["run"]: run for run in retained["runs"]}
    added: dict[str, dict[str, Any]] = {}
    replaced: dict[str, str] = {}
    pairs: list[tuple[str, str]] = []
    for name in runs:
        run = by_run.get(name)
        prepared = prepare(name, index)
        if run is not None and stale(run, prepared):
            replaced[name] = entry_digest(run)
            run = None
        if run is not None and "skipped" in run:
            continue
        backend = run["backend"] if run is not None else None
        if run is None:
            added[name] = prepared
            if "skipped" in prepared:
                continue
            backend = prepared["backend"]
        expected = sorted(f for f in index["files"] if f.startswith(f"docs/evidence/calibration/history/{backend}/"))
        have = set(run["snapshots"]) if run is not None else set()
        require(have <= set(expected), f"{name}: retained snapshots outside the index")
        for relative in expected:
            if relative in have:
                continue
            require(
                run is None or relative not in run["execution_snapshot"].values(),
                f"{name}: {relative} is an execution snapshot the retained run lacks",
            )
            pairs.append((name, relative))
    return added, pairs, replaced


def merged_result(
    retained: dict[str, Any],
    added: dict[str, dict[str, Any]],
    pairs: list[tuple[str, str]],
    entries: list[tuple[dict[str, Any], dict[str, list[float]]]],
    provenance: dict[str, Any],
    replaced: dict[str, str] | None = None,
) -> dict[str, Any]:
    """retained with each added run and each pair's snapshot entry in place, every other retained entry unchanged.

    Runs stay in sorted name order and each run's snapshots and summary in
    sorted path order, the order ghost_run writes; a retained run's summary
    gains the new snapshots' rows and keeps every other row. The header
    records each merge under ``merged``: its device, versions, the runs it
    added and the pairs it added to retained runs, which unmerged() removes,
    and, when stale runs were ghosted again, each replaced run's
    entry_digest.
    """
    replaced = replaced or {}
    names = [run["run"] for run in retained["runs"]]
    require(names == sorted(names), "retained runs are not in sorted order")
    require(set(replaced) <= set(added), "a replaced run is not ghosted again")
    require(not (set(added) - set(replaced)) & set(names), "an added run is already retained")
    retained = dict(retained, runs=[run for run in retained["runs"] if run["run"] not in replaced])
    found: dict[str, dict[str, Any]] = {}
    resamples: dict[str, dict[str, list[float]]] = {}
    for (name, relative), (entry, resample) in zip(pairs, entries, strict=True):
        found.setdefault(name, {})[relative] = entry
        resamples.setdefault(name, {}).update(resample)
    runs = []
    for run in retained["runs"]:
        new = found.get(run["run"])
        if new:
            require(not resamples[run["run"]], f"{run['run']}: a merged snapshot resampled a retained member")
            snapshots = dict(sorted({**run["snapshots"], **new}.items()))
            run = dict(run, summary=summarize(snapshots, run["execution_snapshot"]), snapshots=snapshots)
        runs.append(run)
    for name, prepared in added.items():
        if "skipped" in prepared:
            runs.append({"run": name, "skipped": prepared["skipped"]})
            continue
        results = dict(sorted(found.get(name, {}).items()))
        runs.append(run_entry(name, prepared, results, resamples.get(name, {})))
    record = {
        **provenance,
        "runs": sorted(added),
        "pairs": [[name, relative] for name, relative in pairs if name not in added],
        **({"replaced": [{"run": n, "sha256": d} for n, d in sorted(replaced.items())]} if replaced else {}),
    }
    header = {key: value for key, value in retained.items() if key != "runs"}
    header["merged"] = [*retained.get("merged", []), record]
    return {**header, "runs": sorted(runs, key=lambda run: run["run"])}


def unmerged(result: dict[str, Any]) -> dict[str, Any]:
    """result without every run and (run, snapshot) pair its ``merged`` records name, and without that record."""
    merges = result.get("merged", [])
    added = {name for merge in merges for name in merge["runs"]}
    pairs: dict[str, set[str]] = {}
    for merge in merges:
        for name, relative in merge["pairs"]:
            pairs.setdefault(name, set()).add(relative)
    runs = []
    for run in result["runs"]:
        if run["run"] in added:
            continue
        drop = pairs.get(run["run"], set())
        if drop:
            run = dict(
                run,
                summary={k: v for k, v in run["summary"].items() if k not in drop},
                snapshots={k: v for k, v in run["snapshots"].items() if k not in drop},
            )
        runs.append(run)
    header = {key: value for key, value in result.items() if key not in ("merged", "runs")}
    return {**header, "runs": runs}


def pair_cost(prepared: dict[str, Any]) -> float:
    """Relative cost of one snapshot of a run: per-shot density-matrix evolutions for dynamic Aer members."""
    cost = 0.0
    for m in prepared["members"]:
        for circuit in prepared["replicas"][m][1]:
            width = active_width(circuit)
            if prepared["laws"][m] == EXACT_MULTINOMIAL:
                cost += 4.0**width
            elif is_dynamic(circuit):
                cost += prepared["shots"][m] * 4.0**width
            else:
                cost += 4.0**width
    return cost


def pool_order(costs: list[float]) -> list[int]:
    """Item order for ordered_map, whose chunks are contiguous: costliest first, each followed by a cheapest one."""
    ranked = sorted(range(len(costs)), key=lambda k: (-costs[k], k))
    order: list[int] = []
    low, high = 0, len(ranked) - 1
    while low <= high:
        order.append(ranked[low])
        if low != high:
            order.append(ranked[high])
        low, high = low + 1, high - 1
    return order


def merge(path: Path, out: Path, device: str, index: dict[str, Any]) -> None:
    """Ghost only the pairs path lacks, through the process pool, and write the merged result to out."""
    retained = json.loads(path.read_text(encoding="utf-8"))
    added, pairs, replaced = missing_pairs(retained, index, audited_runs())
    print(
        f"merge: {len(added)} runs in full ({len(replaced)} replace stale entries), {len(pairs)} (run, snapshot) pairs",
        flush=True,
    )
    costs = {name: pair_cost(added.get(name) or prepare(name, index)) for name in sorted({n for n, _ in pairs})}
    order = pool_order([costs[name] for name, _ in pairs])
    mapped = parallel.ordered_map(PairGhost(index, device), [pairs[k] for k in order], min_items=2)
    entries: list[Any] = [None] * len(pairs)
    for k, entry in zip(order, mapped, strict=True):
        entries[k] = entry
    provenance = {
        "device": device,
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__},
        "seed": SEED,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize(merged_result(retained, added, pairs, entries, provenance, replaced)), encoding="utf-8")


def base_without_replaced(result: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    """base without the runs a merge replaced, each of which must match the entry_digest the merge recorded.

    A run first added by an earlier merge and replaced later is absent from
    base, and its digest names the earlier merge's entry.
    """
    seen: set[str] = set()
    dropped: set[str] = set()
    by_run = {run["run"]: run for run in base["runs"]}
    for merge in result.get("merged", []):
        for item in merge.get("replaced", []):
            name = item["run"]
            if name not in seen and name not in dropped:
                require(name in by_run, f"{name}: a replaced run the base lacks")
                require(entry_digest(by_run[name]) == item["sha256"], f"{name}: replaced entry digest differs")
                dropped.add(name)
        seen |= set(merge["runs"])
    return dict(base, runs=[run for run in base["runs"] if run["run"] not in dropped])


def check_provenance(result_path: Path, base_path: Path) -> None:
    """Require result_path without its merges to be base_path byte for byte, less the runs merges replaced."""
    text = result_path.read_text(encoding="utf-8")
    result = json.loads(text)
    require(text == serialize(result), f"{result_path}: not in ghost_run's serialization")
    base_text = base_path.read_text(encoding="utf-8")
    base = json.loads(base_text)
    require(base_text == serialize(base), f"{base_path}: not in ghost_run's serialization")
    expected = serialize(base_without_replaced(result, base))
    require(serialize(unmerged(result)) == expected, f"{result_path}: without its merges differs from {base_path}")
    merges = result.get("merged", [])
    print(f"{result_path}: {base_path} plus {len(merges)} merges keeps every retained byte")


def merged_runs(result: dict[str, Any]) -> dict[str, str]:
    """Each run a merge ghosted in full, mapped to the device of the latest merge that ghosted it."""
    out: dict[str, str] = {}
    for merge in result.get("merged", []):
        for name in merge["runs"]:
            out[name] = merge["device"]
    return out


def replay_merged(run: dict[str, Any], index: dict[str, Any], device: str) -> None:
    """Require the merged run's execution-snapshot distances and resample scatter, recomputed, bit for bit.

    --merge draws every member under each snapshot in one batch
    (PairGhost), so the replay draws every member too and reproduces the
    seeds each retained row came from.
    """
    name = run["run"]
    prepared = prepare(name, index)
    current = index["current"][prepared["backend"]]
    resample: dict[str, list[float]] = {}
    for relative in sorted(set(prepared["execution"].values())):
        entry, own = snapshot_entry(prepared, relative, current, device, prepared["members"])
        require(entry["tvd"] == run["snapshots"][relative]["tvd"], f"{name}: {relative} distances differ")
        resample |= own
    fresh = run_entry(name, prepared, run["snapshots"], resample)["self_check"]
    require(fresh == run["self_check"], f"{name}: self check differs from the replayed resample")


PAIR_SAMPLE = 4
PAIR_COST_CAP = 1.0e6


def sampled_pairs(result: dict[str, Any], costs: dict[tuple[str, str], float]) -> list[tuple[str, str, str]]:
    """Up to PAIR_SAMPLE merge-added (run, snapshot, device) pairs of cost at most PAIR_COST_CAP, picked by a digest.

    Each pair ranks by sha256 over every added pair's retained distances and
    its own path, so a hand-altered distance reshuffles the ranking and the
    ranking cannot be read off the merge record. ``costs`` is pair_cost() per
    pair; a dearer pair is never sampled.
    """
    by_run = {run["run"]: run for run in result["runs"]}
    chosen: dict[tuple[str, str], str] = {}
    for merge in result.get("merged", []):
        for name, relative in merge["pairs"]:
            require(relative in by_run[name]["snapshots"], f"{name}: merged pair {relative} is not retained")
            chosen[name, relative] = merge["device"]
    salt = hashlib.sha256(
        json.dumps([[n, r, by_run[n]["snapshots"][r]["tvd"]] for n, r in sorted(chosen)]).encode()
    ).hexdigest()
    eligible = [pair for pair in chosen if costs[pair] <= PAIR_COST_CAP]
    ranked = sorted(eligible, key=lambda pair: hashlib.sha256(f"{salt}:{pair[0]}:{pair[1]}".encode()).hexdigest())
    return [(name, relative, chosen[name, relative]) for name, relative in ranked[:PAIR_SAMPLE]]


def pair_costs(result: dict[str, Any], index: dict[str, Any]) -> dict[tuple[str, str], float]:
    """pair_cost() of every (run, snapshot) pair a merge added to a retained run."""
    prepared: dict[str, dict[str, Any]] = {}
    out: dict[tuple[str, str], float] = {}
    for merge in result.get("merged", []):
        for name, relative in merge["pairs"]:
            if name not in prepared:
                prepared[name] = prepare(name, index)
            out[name, relative] = pair_cost(prepared[name])
    return out


def replay_pairs(
    result: dict[str, Any],
    index: dict[str, Any],
    device: str,
    costs: dict[tuple[str, str], float] | None = None,
    ghost: Callable[[str, str, str], dict[str, Any]] | None = None,
) -> int:
    """Require the sampled merge-added pairs' retained entries to equal snapshot_entry() recomputed, bit for bit.

    The sampled pairs are the ones sampled_pairs() ranks first. A pair whose
    merge ran on another Aer device than this host is skipped, since seeded
    counts differ across devices. A pair outside the sample (dearer than
    PAIR_COST_CAP, or ranked after PAIR_SAMPLE) keeps only validate() and
    --provenance, so a hand-altered distance in such a pair passes. Returns
    the number of pairs replayed.
    """
    by_run = {run["run"]: run for run in result["runs"]}
    if costs is None:
        costs = pair_costs(result, index)

    def simulate(name: str, relative: str, merge_device: str) -> dict[str, Any]:
        prepared = prepare(name, index)
        current = index["current"][prepared["backend"]]
        return snapshot_entry(prepared, relative, current, merge_device, prepared["members"])[0]

    replay = ghost or simulate
    done = 0
    for name, relative, merge_device in sampled_pairs(result, costs):
        if merge_device != device:
            continue
        retained = by_run[name]["snapshots"][relative]
        fresh = replay(name, relative, merge_device)
        for key in sorted(set(retained) | set(fresh)):
            if key != "seconds":
                require(
                    fresh.get(key) == retained.get(key), f"{name}: merged pair {relative} {key} differs from its replay"
                )
        done += 1
    return done


def replay_all_pairs(result: dict[str, Any], index: dict[str, Any], device: str, part: int | None = None) -> int:
    """Require every merge-added pair of this host's Aer device to equal snapshot_entry() recomputed, bit for bit.

    The pairs run through parallel.ordered_map in pool_order of pair_cost(),
    so a pass covers every added pair; pairs merged on another device are
    skipped, since seeded counts differ across devices. Returns the number
    of pairs replayed.
    """
    by_run = {run["run"]: run for run in result["runs"]}
    pairs = [
        (name, relative)
        for merge in result.get("merged", [])
        if merge["device"] == device
        for name, relative in merge["pairs"]
    ]
    costs = pair_costs(result, index)
    if part is not None:
        ranked = sorted(range(len(pairs)), key=lambda k: (-costs[pairs[k]], k))
        pairs = [pairs[k] for k in sorted(ranked[part::PAIR_SLICES])]
    order = pool_order([costs[pair] for pair in pairs])
    mapped = parallel.ordered_map(PairGhost(index, device), [pairs[k] for k in order], min_items=2)
    for k, (fresh, _distances) in zip(order, mapped, strict=True):
        name, relative = pairs[k]
        print(f"replayed merge-added pair {name} {relative}", flush=True)
        retained = by_run[name]["snapshots"][relative]
        for key in sorted(set(retained) | set(fresh)):
            if key != "seconds":
                require(
                    fresh.get(key) == retained.get(key), f"{name}: merged pair {relative} {key} differs from its replay"
                )
    return len(pairs)


def check(path: Path, runs: str, index: dict[str, Any], part: int | None = None) -> None:
    """Validate every run of path, rerun the --runs execution ghosts, and replay merged runs bit for bit.

    ``--runs`` names runs by path, ``all`` or the token ``merged``: each run
    a merge ghosted in full replays bit for bit when this host's Aer device
    is the one that merge used, and within five standard errors otherwise.
    """
    retained = json.loads(path.read_text(encoding="utf-8"))
    listed = [run["run"] for run in retained["runs"]]
    require(
        sorted(listed) == audited_runs() and len(set(listed)) == len(listed),
        f"{path}: runs are not each audited run exactly once",
    )
    for run in retained["runs"]:
        validate(run, index)
    device = calibration_snapshot.aer_device()
    tokens = None if runs == "all" else set(runs.split(","))
    merged = merged_runs(retained)
    exact = set()
    if tokens is not None and "merged" in tokens:
        tokens.discard("merged")
        exact = {n for n, d in merged.items() if d == device}
        tokens |= set(merged) - exact
    by_run = {run["run"]: run for run in retained["runs"]}
    replayed = 0
    for name in sorted(exact):
        if "skipped" in by_run[name]:
            continue
        replay_merged(by_run[name], index, device)
        replayed += 1
    pairs = replay_pairs(retained, index, device) if tokens is None or "pairs" in tokens else 0
    if tokens is not None and "pairs-all" in tokens:
        pairs += replay_all_pairs(retained, index, device, part)
    tokens = None if tokens is None else tokens - {"pairs", "pairs-all"}
    checked = 0
    for run in retained["runs"]:
        if "skipped" in run or (tokens is not None and run["run"] not in tokens):
            continue
        checked += 1
        fresh = ghost_run(run["run"], "execution", device, index)
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
    require(
        checked + replayed + pairs > 0 and (tokens is None or checked == len(tokens)),
        "--runs names a run FILE lacks",
    )
    print(
        f"{path}: execution-state ghosts of {checked} runs reproduced on {device}; "
        f"{replayed} merged runs and {pairs} sampled merge-added pairs replayed bit for bit"
    )


def self_test() -> None:
    """--merge on synthetic records, and the exact path's rule and seeded draws, without Aer."""
    entry = {"calibration": "c", "current": False, "tvd": {"m": [0.1]}, "seconds": 1.0}
    old = {
        "run": "results/live/a",
        "backend": "ibm_x",
        "execution_snapshot": {"m": "p0"},
        "summary": summarize({"p0": entry}, {"m": "p0"}),
        "self_check": {},
        "snapshots": {"p0": entry},
    }
    retained = {
        "schema": "ghost-run-v2",
        "device": "GPU",
        "runs": [old, {"run": "results/live/z", "skipped": "no record"}],
    }
    base = serialize(retained)
    new_entry = dict(entry, tvd={"m": [0.2]})
    added = {"results/live/b": {"skipped": "the run keeps no record.json"}}
    pairs = [("results/live/a", "p1")]
    merged = merged_result(retained, added, pairs, [(new_entry, {})], {"device": "CPU"})
    require(serialize(retained) == base, "self-test: merged_result mutated its input")
    require([run["run"] for run in merged["runs"]] == ["results/live/a", "results/live/b", "results/live/z"], "order")
    require(list(merged["runs"][0]["snapshots"]) == ["p0", "p1"], "self-test: snapshots not in path order")
    require(merged["runs"][0]["snapshots"]["p0"] == entry, "self-test: a retained entry changed")
    require(merged["runs"][0]["summary"]["p1"]["mean_tvd"] == 0.2, "self-test: summary lacks the merged row")
    require(serialize(unmerged(merged)) == base, "self-test: unmerged does not restore the retained bytes")
    again = merged_result(merged, {}, [("results/live/a", "p2")], [(new_entry, {})], {"device": "CPU"})
    require(len(again["merged"]) == 2 and serialize(unmerged(again)) == base, "self-test: a second merge")
    for action, fragment in (
        (lambda: merged_result(retained, {"results/live/a": {}}, [], [], {}), "already retained"),
        (lambda: merged_result(retained, {}, pairs, [(new_entry, {"m": [0.0]})], {}), "resampled a retained"),
        (lambda: merged_result(retained, {}, pairs, [], {}), "shorter"),
    ):
        try:
            action()
        except (SystemExit, ValueError) as reason:
            require(fragment in str(reason), f"self-test: {reason} lacks {fragment!r}")
            continue
        raise SystemExit(f"self-test: expected a failure naming {fragment!r}")
    # A newly indexed job that moves a retained run's execution windows makes
    # it stale; the merge ghosts it again in full and records its old digest.
    prepared = {
        "backend": "ibm_x",
        "members": ["m"],
        "shots": {"m": 100},
        "skipped_width": [],
        "execution": {"m": "p0"},
        "recorded": {},
        "laws": {"m": AER_SAMPLED},
    }
    current = dict(old, members_ghosted=1, members_skipped_width=[], member_shots={"m": 100})
    require(not stale(current, prepared), "self-test: an unchanged run reads stale")
    moved = dict(prepared, execution={"m": "p1"})
    require(stale(current, moved), "self-test: a moved execution window reads current")
    require(stale(current, {"skipped": "no record"}), "self-test: a run that lost its inputs reads current")
    base_runs = dict(retained, runs=[current, retained["runs"][1]])
    base_text = serialize(base_runs)
    fresh_entry = dict(entry, tvd={"m": [0.3]})
    regenerated = merged_result(
        base_runs,
        {"results/live/a": moved},
        [("results/live/a", "p0"), ("results/live/a", "p1")],
        [(fresh_entry, {}), (fresh_entry, {})],
        {"device": "CPU"},
        {"results/live/a": entry_digest(current)},
    )
    require(regenerated["runs"][0]["execution_snapshot"] == {"m": "p1"}, "self-test: the stale run kept its windows")
    require(regenerated["merged"][-1]["replaced"][0]["run"] == "results/live/a", "self-test: replacement unrecorded")
    stripped = serialize(unmerged(regenerated))
    require(stripped == serialize(base_without_replaced(regenerated, base_runs)), "self-test: replaced provenance")
    require(stripped != base_text, "self-test: unmerged kept the replaced run")
    forged = json.loads(serialize(regenerated))
    forged["merged"][-1]["replaced"][0]["sha256"] = "0" * 64
    try:
        base_without_replaced(forged, base_runs)
    except SystemExit as reason:
        require("digest differs" in str(reason), f"self-test: {reason}")
    else:
        raise SystemExit("self-test: a forged replaced digest passed")
    pair_result = merged_result(retained, {}, pairs, [(new_entry, {})], {"device": "CPU"})
    costs = {("results/live/a", "p1"): 1.0}
    truth = {"results/live/a": {"p1": new_entry}}

    def truthful(name: str, relative: str, _device: str) -> dict[str, Any]:
        return dict(truth[name][relative], seconds=9.0)

    require(replay_pairs(pair_result, {}, "CPU", costs, truthful) == 1, "self-test: pair not replayed")
    require(replay_pairs(pair_result, {}, "GPU", costs, truthful) == 0, "self-test: other device replayed")
    require(
        replay_pairs(pair_result, {}, "CPU", {("results/live/a", "p1"): 2 * PAIR_COST_CAP}, truthful) == 0, "cost cap"
    )
    forged_pair = json.loads(serialize(pair_result))
    forged_run = forged_pair["runs"][0]
    forged_run["snapshots"]["p1"]["tvd"]["m"] = [0.25]
    forged_run["summary"] = summarize(forged_run["snapshots"], forged_run["execution_snapshot"])
    try:
        replay_pairs(forged_pair, {}, "CPU", costs, truthful)
    except SystemExit as reason:
        require("differs from its replay" in str(reason), f"self-test: {reason}")
    else:
        raise SystemExit("self-test: a hand-altered merged pair passed")
    ranks = [
        sampled_pairs(pair_result, {("results/live/a", "p1"): 1.0}),
        sampled_pairs(pair_result, {("results/live/a", "p1"): 1.0}),
    ]
    require(ranks[0] == ranks[1] == [("results/live/a", "p1", "CPU")], "self-test: pair sample")
    order = pool_order([1.0, 9.0, 3.0, 7.0, 5.0])
    require(order == [1, 0, 3, 2, 4], f"self-test: pool order {order}")
    # The exact path: dynamic circuits at EXACT_MIN_SHOTS draw from their law
    # at the seed their tier position names, reproducibly.
    final = QuantumCircuit(1, 1)
    final.x(0)
    final.measure(0, 0)
    mid = QuantumCircuit(1, 2)
    mid.measure(0, 0)
    mid.x(0)
    mid.measure(0, 1)
    reset = QuantumCircuit(1, 1)
    reset.reset(0)
    reset.measure(0, 0)
    require(not is_dynamic(final) and is_dynamic(mid) and is_dynamic(reset), "self-test: dynamic rule")
    # dynamic_density refuses a delay, a measurement inside an if_else body
    # and nested control flow, so such members keep Aer's sampler.
    delayed = QuantumCircuit(1, 2)
    delayed.measure(0, 0)
    delayed.delay(100, 0, unit="dt")
    delayed.measure(0, 1)
    inner = QuantumCircuit(1, 2)
    inner.measure(0, 0)
    with inner.if_test((inner.clbits[0], 1)):
        inner.measure(0, 1)
    nested = QuantumCircuit(1, 2)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        with nested.if_test((nested.clbits[0], 1)):
            nested.x(0)
    nested.measure(0, 1)
    replicas = {
        "f": ("ibm_x", [final]),
        "d": ("ibm_x", [mid]),
        "low": ("ibm_x", [reset]),
        "delay": ("ibm_x", [delayed]),
        "body": ("ibm_x", [inner]),
        "nested": ("ibm_x", [nested]),
        "mixed": ("ibm_x", [mid, delayed]),
    }
    shots = dict.fromkeys(replicas, EXACT_MIN_SHOTS) | {"low": EXACT_MIN_SHOTS - 1}
    laws = member_laws(replicas, shots)
    expected = dict.fromkeys(replicas, AER_SAMPLED) | {"d": EXACT_MULTINOMIAL}
    require(laws == expected, f"self-test: laws {laws}")
    law = np.array([0.1, 0.2, 0.3, 0.4])
    counts = sample(None, [mid, mid], [100, 100], SEED, {0: law, 1: law})
    require(counts == sample(None, [mid, mid], [100, 100], SEED, {0: law, 1: law}), "self-test: draws repeat")
    require(counts[1] == multinomial_counts(law, 100, SEED + AER_SEED_SHIFT, 2), "self-test: position seed")
    require(counts[0] != counts[1] and sum(counts[0].values()) == 100, "self-test: positions share a seed")
    print("ghost run self-test: merges keep every retained byte and exact draws follow their positions' seeds")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="all")
    parser.add_argument(
        "--case", action="append", choices=tuple(PAIR_CASES), help="replay one strided slice of --runs pairs-all"
    )
    parser.add_argument("--states", default="all", choices=("execution", "execution,current", "current", "all"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--report", type=Path, help="print the paired summary of a retained result")
    parser.add_argument("--merge", type=Path, metavar="RESULT", help="ghost only the pairs RESULT lacks, into --out")
    parser.add_argument(
        "--provenance",
        type=Path,
        nargs=2,
        metavar=("RESULT", "BASE"),
        help="require RESULT without its merges to be BASE byte for byte",
    )
    parser.add_argument("--self-test", action="store_true", help="exercise --merge and the exact path")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.report:
        print(json.dumps(report(args.report), indent=1))
        return 0
    if args.provenance:
        check_provenance(*args.provenance)
        return 0
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    if args.merge:
        merge(args.merge, args.out or args.merge, calibration_snapshot.aer_device(), index)
        return 0
    if args.check:
        parts = [PAIR_CASES[name] for name in args.case or []]
        require(len(parts) <= 1, "--case names one pair slice")
        require(not parts or args.runs == "pairs-all", "--case slices --runs pairs-all")
        check(args.check, args.runs, index, parts[0] if parts else None)
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

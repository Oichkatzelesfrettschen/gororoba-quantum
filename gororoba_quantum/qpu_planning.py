"""Calibration-bound experiment design above the existing Runtime execution path.

The runtime adapter supplies compilation, packing, and simulation. Keeping those
operations in live_run preserves its hardware admission and archive contracts;
the optimizer receives explicit scientific quantities and accounting units.
"""

from __future__ import annotations

import copy
import json
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from typing import Any

import numpy as np
from qiskit.exceptions import QiskitError

import local_compute
import parallel
from diagnostic_experiments import (
    N21_FAMILIES,
    PATCH_FAMILIES,
    family_contracts,
    folded_group,
    n21_group,
    n21_orbit_rca_group,
)
from experiment_optimizer import (
    BudgetContract,
    CandidatePlan,
    CostScenario,
    JobCandidate,
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    PubPrediction,
    analyze_observations,
    optimize,
)
from packing import Replica
from qpe_diagnostics import ideal_compiled_probabilities


def settings(args: Any) -> dict[str, Any]:
    """Approval-bound design inputs, distinct from fluctuating quota readings."""
    return {
        name: getattr(args, name, default)
        for name, default in (
            ("family", None),
            ("optimize", False),
            ("objective", "minimum_charge"),
            ("cost_scenarios", []),
            ("shot_tiers", [2048, 4096, 8192, 16384]),
            ("shot_allocation", "uniform"),
            ("replica_tiers", [1, 2, 4]),
            ("optimizer_candidates", 6),
            ("model_shots", 32768),
            ("precision", 0.08),
            ("alpha", 0.05),
            ("power", 0.8),
            ("simulation_alpha", 0.01),
            ("job_overhead_seconds", 2.3),
            ("classical_latency_us", 20.0),
            ("reserve_seconds", 0.0),
            ("max_total_execution_seconds", None),
            ("patch_qubits", None),
        )
    }


def budget_plan(runtime: Any, choices: list[Any], args: Any, usage: dict[str, Any]) -> dict[str, Any]:
    """Reserve all ceilings before any job starts, including unsent batches."""
    ceiling = getattr(args, "max_execution_seconds", None)
    jobs = []
    pub_shots = getattr(args, "pub_shots", None)
    if pub_shots is not None:
        names = [pub.name for pub in runtime.execution_pubs(choices)]
        if (
            not isinstance(pub_shots, dict)
            or len(names) != len(set(names))
            or set(pub_shots) != set(names)
            or any(type(value) is not int or value <= 0 for value in pub_shots.values())
        ):
            raise runtime.LiveRunError("shot allocation must assign a positive integer to every execution PUB exactly")
    for backend in sorted({choice.snap.name for choice in choices}):
        selected = [choice for choice in choices if choice.snap.name == backend]
        backend_shots = (
            {pub.name: pub_shots[pub.name] for pub in runtime.execution_pubs(selected)}
            if pub_shots is not None
            else None
        )
        for kind in ("dynamic", "static"):
            batches = (
                runtime.submission_batches(selected, kind, args.shots, pub_shots=backend_shots)
                if backend_shots is not None
                else runtime.submission_batches(selected, kind, args.shots)
            )
            for index, batch in enumerate(batches, 1):
                jobs.append(
                    {
                        "backend": backend,
                        "kind": kind,
                        "batch_index": index,
                        "pubs": len(batch),
                        "ceiling_seconds": ceiling,
                        **(
                            {
                                "shots": runtime.batch_shots(batch, args.shots, backend_shots),
                                "pub_names": [pub.name for pub in batch],
                            }
                            if pub_shots is not None
                            else {}
                        ),
                    }
                )
    total = None if ceiling is None else float(ceiling) * len(jobs)
    reserve = float(getattr(args, "reserve_seconds", 0.0))
    cap = getattr(args, "max_total_execution_seconds", None)
    remaining = usage.get("usage_remaining_seconds")
    reasons = []
    if usage.get("usage_limit_reached"):
        reasons.append("the instance reports its usage limit reached")
    if total is not None:
        if cap is not None and total > cap:
            reasons.append(f"combined execution ceiling {total} s exceeds invocation cap {cap} s")
        if remaining is not None and total + reserve > float(remaining):
            reasons.append(
                f"combined execution ceiling {total} s plus reserve {reserve} s exceeds remaining {remaining} s"
            )
    return {
        "jobs": jobs,
        "combined_ceiling_seconds": total,
        "reserve_seconds": reserve,
        "max_total_execution_seconds": cap,
        "remaining_seconds": remaining,
        "admitted": not reasons,
        "reasons": reasons,
        "reservation_scope": "invocation-local ceilings; external submissions can change shared quota",
    }


def window_durations(runtime: Any, snapshot: Any, controls: list[int] | None = None) -> tuple[int, int, float]:
    """Readout length and echo half-window in dt from the routed control's measure and reset.

    controls names the physical qubits of the routed control's mid-circuit
    measure and reset; their slowest measure and reset set the window. With controls
    None the backend's slowest qubit sets it, which bounds the window of every
    placement before routing names the control. The delay arm idles one
    readout length. The echo halves together cover 1.2 times the measure plus
    reset, so the second X precedes the second round and no tail of the window
    stays unechoed.
    """
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    longest = {}
    for name in ("measure", "reset"):
        table = target[name] if name in target.operation_names else {}
        sites = table.values() if controls is None else [table.get((qubit,)) for qubit in controls]
        durations = [
            float(properties.duration)
            for properties in sites
            if properties is not None and properties.duration is not None
        ]
        if (
            not durations
            or (controls is not None and len(durations) != len(controls))
            or target.dt is None
            or target.dt <= 0
        ):
            raise runtime.LiveRunError(f"the N=21 window arms need a calibrated {name} duration and dt")
        longest[name] = max(durations) / float(target.dt)

    def rounded(value: float) -> int:
        return granularity * math.ceil(value / granularity)

    return rounded(longest["measure"]), rounded(0.6 * (longest["measure"] + longest["reset"])), float(target.dt)


def control_sites(runtime: Any, isas: list[Any]) -> list[tuple[tuple[str, int], ...]]:
    """Every measure and reset of each compiled window arm with its physical site, in instruction order.

    Only the QPE control is measured and reset. Routing can move the control
    between the rounds, so an arm's terminal readout can sit on another qubit
    than its mid-circuit measure and reset.
    """
    return [
        tuple((name, qubits[0]) for name, qubits in runtime._ops(isa) if name in ("measure", "reset")) for isa in isas
    ]


def window_controls(sites: list[tuple[tuple[str, int], ...]]) -> list[int]:
    """Physical qubits of the mid-circuit round: each arm's measures through its first reset.

    The window spans the round-1 readout and the reset that follows it, so
    the terminal readout's site stays out of the window durations.
    """
    window: set[int] = set()
    for arm in sites:
        names = [name for name, _ in arm]
        if "reset" not in names or names.index("reset") == 0:
            raise ValueError(f"a window arm lacks its mid-circuit measure and reset: {arm}")
        window.update(qubit for _, qubit in arm[: names.index("reset") + 1])
    return sorted(window)


def _control_windows(runtime: Any, candidate: Any, bound: tuple[int, int, float]) -> tuple[Any, dict[str, float]]:
    """Resize one routed window candidate to its control's own measure and reset durations.

    The candidate was routed with the backend-wide bound. The windows come
    from the sites of the mid-circuit measure and reset. When they give the
    same windows, the routed candidate stands; otherwise every arm rebuilds
    with them and recompiles on the same seed and initial layout, and each
    recompiled arm must keep its ordered measure and reset sites.
    """
    sites = control_sites(runtime, candidate.isas)
    controls = window_controls(sites)
    window_dt, half_dt, dt = window_durations(runtime, candidate.snap, controls)
    windows = {"window_delay_dt": window_dt, "echo_half_dt": half_dt, "dt_seconds": dt}
    if (window_dt, half_dt) == bound[:2]:
        return candidate, windows
    group = n21_orbit_rca_group(window_dt, half_dt)
    isas = [
        runtime._compile(member.circuit, candidate.snap, candidate.seed, candidate.layout) for member in group.members
    ]
    violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, candidate.snap)]
    if violations:
        raise runtime.LiveRunError(str(violations))
    moved = control_sites(runtime, isas)
    if moved != sites:
        raise runtime.LiveRunError(f"resized window arms moved the control from {sites} to {moved}")
    scores = [runtime.layout_score(isa, candidate.snap.backend.target) for isa in isas]
    if any(score <= 0 for score in scores):
        raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on layout {candidate.layout}")
    joint = math.exp(sum(math.log(score) for score in scores) / len(scores))
    resized = runtime.Choice(group, candidate.snap, candidate.seed, candidate.layout, isas, scores, joint)
    return resized, windows


def control_timing_dt(target: Any, control: int) -> tuple[float, float]:
    """Measure and reset durations of one physical qubit in units of the Target's dt."""
    durations = []
    for operation in ("measure", "reset"):
        properties = target[operation].get((control,)) if operation in target.operation_names else None
        duration = getattr(properties, "duration", None)
        if not target.dt or not duration or duration <= 0:
            raise ValueError(f"no Target {operation} duration or dt for control {control}")
        durations.append(float(duration) / float(target.dt))
    return durations[0], durations[1]


def coherence_readout_qubits(isas: list[Any]) -> dict[str, int]:
    """Physical qubit read into each coherence clbit, identical across every compiled circuit.

    Routing may move the logical work qubits during the round-1 prefix, so the
    pinned roles name the initial layout only. No two-qubit gate follows the
    prefix's closing barrier, so the qubit measured into a work clbit is the
    one that held that logical qubit through the window.
    """
    from coherence_window import B0, READ_A, READ_B, SECTOR

    labels = {B0: "b0", READ_A: "read_a", READ_B: "read_b", SECTOR: "sector"}
    found: dict[str, int] | None = None
    for isa in isas:
        barrier = next(i for i, inst in enumerate(isa.data) if inst.operation.name == "barrier")
        if any(inst.operation.num_qubits > 1 and inst.operation.name != "barrier" for inst in isa.data[barrier:]):
            raise ValueError(f"{isa.name}: a two-qubit gate follows the round-1 prefix")
        reads: dict[str, set[int]] = {}
        for inst in isa.data:
            if inst.operation.name == "measure":
                clbit = isa.find_bit(inst.clbits[0]).index
                reads.setdefault(labels[clbit], set()).add(isa.find_bit(inst.qubits[0]).index)
        if set(reads) != set(labels.values()) or any(len(qubits) != 1 for qubits in reads.values()):
            raise ValueError(f"{isa.name}: each coherence clbit must be read from one physical qubit")
        mapping = {label: next(iter(qubits)) for label, qubits in reads.items()}
        if found is not None and mapping != found:
            raise ValueError(f"{isa.name}: readout qubits {mapping} differ from {found}")
        found = mapping
    if found is None:
        raise ValueError("no compiled coherence circuit")
    return found


# Patch embeddings compiled in full per backend after the prefilter, and the
# declared idle over which the prefilter charges each qubit's T2 decay: the
# window the families place between the round and the readout is a control
# measure plus reset, about 4 to 5 us on Heron r2.
PATCH_PREFILTER = 16
PATCH_PREFILTER_IDLE_S = 5e-6


def patch_layouts(snapshot: Any, limit: int) -> tuple[list[tuple[list[int], float]], int]:
    """Patch embeddings on one backend's admitted CZ graph, best error product first.

    Every injective map of PATCH_ROLES onto physical qubits that carries each
    PATCH_EDGES pair onto a CZ coupler (rustworkx VF2, non-induced) is a
    candidate, excluding qubits and couplers the calibration excludes. The
    prefilter is the product of (1 - measure error), (1 - sx error) and
    exp(-PATCH_PREFILTER_IDLE_S / T2) over the six qubits and (1 - cz error)
    over the five couplers; a qubit without a positive T2 scores zero. Ties
    break on the layout tuple, so one calibration always yields the same
    ordered list. The second value is the number of embeddings found.
    """
    import rustworkx as rx

    from patch_characterization import PATCH_EDGES, PATCH_ROLES

    target = snapshot.backend.target
    if "cz" not in target.operation_names:
        return [], 0
    excluded = set(snapshot.excluded_qubits)
    blocked = {tuple(sorted(edge)) for edge in snapshot.excluded_edges}
    couplers = {
        tuple(sorted(pair)) for pair in target["cz"] if not set(pair) & excluded and tuple(sorted(pair)) not in blocked
    }
    graph = rx.PyGraph()
    nodes = graph.add_nodes_from(range(target.num_qubits))
    graph.add_edges_from_no_data([(nodes[a], nodes[b]) for a, b in sorted(couplers)])
    pattern = rx.PyGraph()
    pattern.add_nodes_from(range(len(PATCH_ROLES)))
    pattern.add_edges_from_no_data(list(PATCH_EDGES))

    def error(operation: str, qargs: tuple[int, ...]) -> float:
        properties = target[operation].get(qargs) or target[operation].get(qargs[::-1])
        value = getattr(properties, "error", None)
        return float(value) if value is not None else 1.0

    def decay(qubit: int) -> float:
        properties = target.qubit_properties[qubit] if target.qubit_properties else None
        t2 = getattr(properties, "t2", None)
        return math.exp(-PATCH_PREFILTER_IDLE_S / float(t2)) if t2 is not None and t2 > 0 else 0.0

    scored = []
    for mapping in rx.vf2_mapping(graph, pattern, subgraph=True, induced=False, id_order=True):
        layout = [0] * len(PATCH_ROLES)
        for physical, role in mapping.items():
            layout[role] = int(physical)
        product = math.prod((1.0 - error("measure", (q,))) * (1.0 - error("sx", (q,))) * decay(q) for q in layout)
        product *= math.prod(1.0 - error("cz", (layout[a], layout[b])) for a, b in PATCH_EDGES)
        scored.append((-product, tuple(layout)))
    scored.sort()
    return [(list(layout), -negative) for negative, layout in scored[:limit]], len(scored)


def _patch_candidate(
    runtime: Any, snapshot: Any, layout: list[int], args: Any, delays: list[int]
) -> tuple[list[Any], dict[str, Any]]:
    """Compile the characterization groups on one patch of one snapshot, or raise why it is refused."""
    from coherence_window import coherence_groups
    from patch_characterization import PATCH_EDGES, PATCH_ROLES, patch_groups

    excluded = sorted(set(layout) & set(snapshot.excluded_qubits))
    edges = [(layout[a], layout[b]) for a, b in PATCH_EDGES]
    blocked = [edge for edge in edges if edge in snapshot.excluded_edges or edge[::-1] in snapshot.excluded_edges]
    if excluded or blocked:
        raise runtime.LiveRunError(f"calibration excludes patch qubits {excluded} or couplers {blocked}")
    # Exchange circuits use no two-qubit gate, so the declared couplers
    # must exist in the Target for neighbors to be physical neighbors.
    couplers = set(snapshot.backend.target["cz"]) if "cz" in snapshot.backend.target.operation_names else set()
    missing = [edge for edge in edges if edge not in couplers and edge[::-1] not in couplers]
    if missing:
        raise runtime.LiveRunError(f"the backend has no coupler for patch edges {missing}")
    # The reset-only reference and echo halves follow the patch control's own
    # measure and reset durations.
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    try:
        control_measure, control_reset = control_timing_dt(target, layout[0])
    except ValueError as error:
        raise runtime.LiveRunError(str(error)) from error
    measure_dt = granularity * math.ceil(control_measure / granularity)
    half_dt = granularity * math.ceil(0.6 * (control_measure + control_reset) / granularity)
    # The matched idle spans the control's measure and reset, the window
    # the measure_reset context places between the round and the readout.
    window_dt = granularity * math.ceil((control_measure + control_reset) / granularity)
    dt = float(target.dt)
    choices = []
    groups = (
        coherence_groups(window_dt) if args.family == "coherence-window" else patch_groups(delays, measure_dt, half_dt)
    )
    for group in groups:
        isas = [runtime._compile(member.circuit, snapshot, runtime.SEED_TRANSPILER, layout) for member in group.members]
        violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, snapshot)]
        if violations:
            raise runtime.LiveRunError(str(violations))
        scores = [runtime.layout_score(isa, snapshot.backend.target) for isa in isas]
        if any(score <= 0 for score in scores):
            raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on patch {layout}")
        choices.append(
            runtime.Choice(
                group,
                snapshot,
                runtime.SEED_TRANSPILER,
                layout,
                isas,
                scores,
                math.exp(sum(math.log(score) for score in scores) / len(scores)),
            )
        )
    used = sorted({qubit for choice in choices for isa in choice.isas for qubit in runtime._physical(isa)})
    if set(used) - set(layout):
        raise runtime.LiveRunError(f"routing left the patch through qubits {sorted(set(used) - set(layout))}")
    readout: dict[str, int] = {}
    if args.family == "coherence-window":
        readout = coherence_readout_qubits([isa for choice in choices for isa in choice.isas])
    # The patch is reserved whole: an idle neighbor stays mapped so the
    # replica, the case and the collector name the same six qubits.
    pinned = sorted(set(used) | set(layout))
    replica = Replica(0, {qubit: qubit for qubit in pinned}, min(min(choice.member_scores) for choice in choices))
    for choice in choices:
        runtime._set_entries(choice, [replica], runtime.ReplicaPolicy(args.replica_floor, 1, False, True))
    runtime.execution_pubs(choices)
    timing: dict[str, Any] = (
        {
            "window_dt": window_dt,
            "control_measure_dt": round(control_measure),
            "control_reset_dt": round(control_reset),
            "readout_qubits": readout,
        }
        if args.family == "coherence-window"
        else {"delays_dt": delays, "measure_dt": measure_dt, "echo_half_dt": half_dt}
    )
    return choices, {
        "name": args.family,
        "patch_qubits": layout,
        "patch_roles": list(PATCH_ROLES),
        **timing,
        "dt_seconds": dt,
        "placement_contract": "one pinned patch; static and dynamic jobs",
    }


def patch_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Compile the characterization groups on a declared patch, or on the best calibrated patches of every backend.

    With --patch-qubits the patch is fixed, so a snapshot whose fresh
    calibration excludes a patch qubit or exercised coupler is refused rather
    than re-placed. Without it, each eligible snapshot contributes its
    PATCH_PREFILTER best embeddings (patch_layouts); every compiled patch is
    ranked by its joint score, fewer pending jobs breaking ties, and the
    best --optimizer-candidates go to admission. The trace keeps every scored
    and refused patch, so a dry run and a submit on one calibration choose the
    same patch.
    """
    from patch_characterization import PATCH_DELAYS_DT, PATCH_ROLES

    delays = list(PATCH_DELAYS_DT)
    declared = args.patch_qubits is not None
    if declared:
        fixed = [int(qubit) for qubit in args.patch_qubits]
        if len(fixed) != len(PATCH_ROLES) or len(set(fixed)) != len(fixed):
            raise runtime.LiveRunError(f"--patch-qubits names {len(PATCH_ROLES)} distinct qubits: {PATCH_ROLES}")
    scored: list[tuple[float, int, list[Any], dict[str, Any]]] = []
    search = trace.setdefault("patch_search", [])
    prefilter_trace = trace.setdefault("patch_prefilter", {})
    for snapshot in snapshots:
        if declared:
            layouts: list[tuple[list[int], float | None]] = [(fixed, None)]
        else:
            ranked, found = patch_layouts(snapshot, PATCH_PREFILTER)
            layouts = [(layout, score) for layout, score in ranked]
            prefilter_trace[snapshot.name] = {
                "embeddings": found,
                "compiled": len(ranked),
                "cutoff_prefilter": ranked[-1][1] if ranked else None,
            }
        for layout, prefilter in layouts:
            try:
                choices, configuration = _patch_candidate(runtime, snapshot, layout, args, delays)
            except (runtime.LiveRunError, QiskitError, ValueError) as error:
                trace.setdefault("family_rejections", []).append(
                    {"backend": snapshot.name, "patch_qubits": layout, "reason": str(error)}
                )
                continue
            joint = math.exp(sum(math.log(choice.joint_score) for choice in choices) / len(choices))
            configuration["patch_selection"] = "declared" if declared else "calibration"
            search.append(
                {"backend": snapshot.name, "patch_qubits": layout, "prefilter": prefilter, "joint_score": joint}
            )
            scored.append((joint, -snapshot.pending_jobs, choices, configuration))
    if declared:
        return [(choices, configuration) for _, _, choices, configuration in scored]
    scored.sort(key=lambda item: (item[0], item[1], [-q for q in item[3]["patch_qubits"]]), reverse=True)
    return [(choices, configuration) for _, _, choices, configuration in scored[: args.optimizer_candidates]]


def measurement_delay(runtime: Any, snapshot: Any, physical_qubit: int) -> int:
    """Round the actual measurement writer's fresh duration to timing granularity."""
    target = snapshot.backend.target
    duration = target["measure"][(physical_qubit,)].duration
    if duration is None or target.dt is None or duration <= 0 or target.dt <= 0:
        raise runtime.LiveRunError("the ladder needs a positive calibrated measurement duration and dt")
    granularity = max(1, int(target.granularity))
    return granularity * math.ceil(float(duration) / float(target.dt) / granularity)


def family_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Enumerate matched circuit sets; a folded family retains its exact physical mapping."""
    if args.family in ("ripple", "rank-sector"):
        import algebra_planning

        return algebra_planning.family_candidates(runtime, snapshots, args, trace)
    candidates: list[tuple[list[Any], dict[str, Any]]] = []
    if args.family in (*N21_FAMILIES, "n21-orbit-rca"):
        routed = []
        windows: dict[int, dict[str, float]] = {}
        if args.family == "n21-orbit-rca":
            # Window durations come from each backend's calibration, so each
            # snapshot routes its own group; per-snapshot traces merge by group.
            # A backend that lacks calibrated durations or rejects the group
            # leaves the others in the search; the trace records its reason.
            # Routing uses the backend-wide bound, and each routed candidate
            # then takes its control's own measure and reset durations.
            for snapshot in snapshots:
                local: dict[str, Any] = {}
                try:
                    bound = window_durations(runtime, snapshot)
                    group = n21_orbit_rca_group(bound[0], bound[1])
                    placed = runtime.select_candidates(group, [snapshot], args.seeds, local)
                except (runtime.LiveRunError, QiskitError, ValueError) as error:
                    trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
                    continue
                trace.setdefault(group.name, {}).update(local.get(group.name, {}))
                for placement in placed:
                    try:
                        choice, window = _control_windows(runtime, placement, bound)
                    except (runtime.LiveRunError, QiskitError, ValueError) as error:
                        trace.setdefault("family_rejections", []).append(
                            {
                                "backend": snapshot.name,
                                "seed": placement.seed,
                                "layout": placement.layout,
                                "reason": str(error),
                            }
                        )
                        continue
                    routed.append(choice)
                    windows[id(choice)] = window
            if not routed:
                raise runtime.LiveRunError(
                    f"no backend routes the N=21 window family: {trace.get('family_rejections')}"
                )
            routed.sort(key=lambda choice: -choice.joint_score)
        else:
            routed = runtime.select_candidates(
                n21_group(orbit=args.family == "n21-orbit-feedback", encoded=args.family == "n21-feedback-encoded"),
                snapshots,
                args.seeds,
                trace,
            )
        tiers = args.replica_tiers if args.optimize else [args.max_replicas or 1]
        if args.family == "n21-orbit-rca":
            # The window analysis reads one replica's schedule and wires.
            tiers = [1]
        if args.max_replicas is not None:
            tiers = [tier for tier in tiers if tier <= args.max_replicas]
        if not tiers:
            raise runtime.LiveRunError("replica tiers contain no placement within --max-replicas")
        for candidate in routed[: args.optimizer_candidates]:
            for cap in sorted(set(tiers)):
                trial = copy.copy(candidate)
                policy = runtime.ReplicaPolicy(args.replica_floor, cap, False, True)
                if runtime._prepare_individual_candidate(trial, trace, policy):
                    candidates.append(
                        ([trial], {"name": args.family, "replica_cap": cap, **windows.get(id(candidate), {})})
                    )
        return candidates
    if args.family in PATCH_FAMILIES:
        return patch_candidates(runtime, snapshots, args, trace)
    if args.family != "folded-qpe":
        raise runtime.LiveRunError(f"unknown family {args.family}")
    coherent = runtime.select_candidates(folded_group(("coherent",)), snapshots, args.seeds, trace)
    for candidate in coherent[: args.optimizer_candidates]:
        layout = candidate.layout[:5]
        try:
            archived = folded_group(("archived",))
            archived_isas = [
                runtime._compile(member.circuit, candidate.snap, candidate.seed, layout) for member in archived.members
            ]
            writers = {
                label: next(qubits[0] for name, qubits in runtime._ops(isa) if name == "measure")
                for label, isa in enumerate(archived_isas)
            }
            delay_dt = {label: measurement_delay(runtime, candidate.snap, writer) for label, writer in writers.items()}
            group = folded_group(("archived", "delay", "no_feed_forward"), delay_dt)
            isas = [
                *archived_isas,
                *(
                    runtime._compile(member.circuit, candidate.snap, candidate.seed, layout)
                    for member in group.members[4:]
                ),
            ]
            for label, isa in enumerate(isas[4:8]):
                delayed = [
                    isa.find_bit(instruction.qubits[0]).index
                    for instruction in isa.data
                    if instruction.operation.name == "delay"
                ]
                if delayed != [writers[label]]:
                    raise runtime.LiveRunError(
                        f"s{label}: delay route {delayed} differs from measurement wire {writers[label]}"
                    )
            violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, candidate.snap)]
            if violations:
                raise runtime.LiveRunError(str(violations))
            scores = [runtime.layout_score(isa, candidate.snap.backend.target) for isa in isas]
            if any(score <= 0 for score in scores):
                raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on patch {layout}")
            dynamic = runtime.Choice(
                group,
                candidate.snap,
                candidate.seed,
                layout,
                isas,
                scores,
                math.exp(sum(math.log(score) for score in scores) / len(scores)),
            )
            trial = [copy.copy(candidate), dynamic]
            # One fixed layout isolates the measured device patch. Re-embedding a
            # delay arm changes the measurement duration it replaces; the family
            # therefore searches layouts but does not pool independent placements.
            used = sorted({qubit for choice in trial for isa in choice.isas for qubit in runtime._physical(isa)})
            replica = Replica(0, {qubit: qubit for qubit in used}, min(scores))
            for choice in trial:
                runtime._set_entries(choice, [replica], runtime.ReplicaPolicy(args.replica_floor, 1, False, True))
            runtime.execution_pubs(trial)
        except (runtime.LiveRunError, ValueError) as error:
            trace.setdefault("family_rejections", []).append(
                {"backend": candidate.snap.name, "seed": candidate.seed, "reason": str(error)}
            )
            continue
        candidates.append(
            (
                trial,
                {
                    "name": args.family,
                    "measurement_delay_dt": {str(label): duration for label, duration in delay_dt.items()},
                    "replaced_measurement_qubits": {str(label): writer for label, writer in writers.items()},
                    "shared_initial_layout": layout,
                    "extra_control": candidate.layout[5],
                    "placement_contract": "one fixed shared work register; separate static/dynamic jobs",
                    "measurement_seconds": {
                        str(label): candidate.snap.backend.target["measure"][(writer,)].duration
                        for label, writer in writers.items()
                    },
                    "measurement_sites": {
                        member.name: [list(qubits) for name, qubits in runtime._ops(isa) if name == "measure"]
                        for choice in trial
                        for member, isa in zip(choice.group.members, choice.isas, strict=True)
                    },
                    "interpretation_boundary": (
                        "shared initial mapping; coherent routing and terminal readout sites can differ"
                    ),
                    "dt_seconds": candidate.snap.backend.target.dt,
                },
            )
        )
    return candidates


def repetition_delay(backend: Any) -> float:
    """Read seconds from the SDK attribute; configuration.to_dict uses wire microseconds."""
    configuration = backend.configuration()
    value = getattr(configuration, "default_rep_delay", None)
    interval = getattr(configuration, "rep_delay_range", None)
    if (
        not getattr(configuration, "dynamic_reprate_enabled", False)
        or value is None
        or not math.isfinite(value)
        or value < 0
        or interval is None
        or len(interval) != 2
        or not interval[0] <= value <= interval[1]
    ):
        raise ValueError("cost planning requires a valid backend default repetition delay in seconds")
    return float(value)


def execution_contract(choices: list[Any], record: dict[str, Any]) -> dict[str, Any]:
    """Bind submitted repetition settings and selected cost inputs to approval."""
    backends = {choice.snap.name: choice.snap.backend for choice in choices}
    optimization = record.get("optimization", {})
    selected: dict[str, Any] = next(
        (
            candidate
            for candidate in optimization.get("candidates", [])
            if candidate["name"] == optimization.get("selected")
        ),
        {},
    )
    return {
        "backends": [
            {
                "name": name,
                "repetition_delay_seconds": repetition_delay(backend)
                if getattr(backend.configuration(), "dynamic_reprate_enabled", False)
                else None,
            }
            for name, backend in sorted(backends.items())
        ],
        "selected_job_costs": json.loads(json.dumps(selected.get("jobs", []))),
        "selected_cost_scenarios": json.loads(json.dumps(selected.get("cost_scenarios", []))),
        "selected_worst_case_charge_seconds": selected.get("worst_case_charge_seconds"),
        **({"pub_shots": dict(record["pub_shots"])} if "pub_shots" in record else {}),
    }


def admitted_family_candidates(
    runtime: Any, candidates: list[tuple[list[Any], dict[str, Any]]], trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Drop every candidate holding a group that runtime.group_admission_violations rejects on its snapshot.

    Family builders construct Choices from direct compiles, outside
    select_candidates, so this applies the predicate the pre-submit refresh
    applies; each rejection names its backend, group and violations.
    """
    admitted = []
    for choices, configuration in candidates:
        rejected = [
            f"{choice.group.name}: {'; '.join(violations)}"
            for choice in choices
            if (violations := runtime.group_admission_violations(choice.group, choice.snap.capabilities))
        ]
        if rejected:
            backends = ",".join(sorted({choice.snap.name for choice in choices}))
            trace.setdefault("family_rejections", []).append({"backend": backends, "reason": " | ".join(rejected)})
            continue
        admitted.append((choices, configuration))
    return admitted


def prepare(
    runtime: Any, snapshots: list[Any], args: Any, usage: dict[str, Any], trace: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Compile and simulate the bounded candidate set before choosing a shot tier."""
    if args.family == "folded-correction":
        import correction_planning

        return correction_planning.prepare(runtime, snapshots, args, usage, trace)
    candidates = admitted_family_candidates(runtime, family_candidates(runtime, snapshots, args, trace), trace)
    if not candidates:
        diagnostic = runtime._scrub_instances(runtime._jsonable(trace))
        raise runtime.LiveRunError(
            "the experiment family has no admitted routed candidate; "
            f"family={args.family!r}; selection_trace={json.dumps(diagnostic, sort_keys=True)}"
        )
    contracts = family_contracts(args.family, args.precision, args.alpha, args.power)
    plans: list[CandidatePlan] = []
    ownership: dict[str, tuple[list[Any], dict[str, Any], int]] = {}
    simulators: dict[int, Any] = {}
    tiers = sorted(set(args.shot_tiers if args.optimize else [args.shots]))
    per_pub = getattr(args, "shot_allocation", "uniform") == "per-pub"
    if per_pub and (args.family not in ("ripple", "rank-sector", *PATCH_FAMILIES) or not args.optimize):
        raise runtime.LiveRunError("per-PUB shot allocation requires an optimized algebra or patch family")
    if not per_pub and hasattr(args, "pub_shots"):
        del args.pub_shots
    for choices, _configuration in candidates:
        for choice in choices:
            if id(choice.snap) not in simulators:
                simulators[id(choice.snap)] = runtime.noise_simulator(
                    choice.snap.name, choice.snap.backend.target, choice.snap.properties, local_compute.settings(args)
                )

    # Aer releases the GIL while it simulates, so independent choices run on
    # threads. Each simulator already uses the policy's thread count, so the
    # pool runs only as many simulators as fit in the available CPUs. Each task
    # owns a simulator built from the snapshot's cached noise model; its batch
    # evidence joins the snapshot simulator in serial order.
    def simulate_choice(choice: Any) -> tuple[Any, dict[str, Any]]:
        simulator = runtime.noise_simulator(
            choice.snap.name, choice.snap.backend.target, choice.snap.properties, local_compute.settings(args)
        )
        return simulator, runtime.simulate(choice, simulator, args.model_shots)

    ordered = [choice for choices, _configuration in candidates for choice in choices]
    concurrent = max(1, parallel.workers() // local_compute.settings(args)["threads"])
    with ThreadPoolExecutor(max_workers=concurrent) as pool:
        simulated = iter(list(pool.map(simulate_choice, ordered)))
    for candidate_index, (choices, configuration) in enumerate(candidates):
        predictions: dict[str, tuple[tuple[float, ...], ...]] = {}
        for choice in choices:
            for entry in choice.entries:
                for replica in entry.replicas:
                    actual = ideal_compiled_probabilities(replica)
                    if not np.allclose(actual, entry.ideal, rtol=0, atol=1e-10):
                        raise runtime.LiveRunError(
                            f"{entry.name}: compiled labeled ideal differs from its exact oracle"
                        )
            task_simulator, noisy = next(simulated)
            local_compute.merge_batches(simulators[id(choice.snap)], task_simulator)
            predictions.update(
                {name: tuple(tuple(map(float, dist)) for dist in replicas) for name, replicas in noisy.items()}
            )
        for shots in [max(tiers)] if per_pub else tiers:
            jobs = []
            for backend_name in sorted({choice.snap.name for choice in choices}):
                selected = [choice for choice in choices if choice.snap.name == backend_name]
                backend = selected[0].snap.backend
                for kind in ("dynamic", "static"):
                    for index, batch in enumerate(runtime.submission_batches(selected, kind, shots), 1):
                        pubs = []
                        for pub in batch:
                            manifest = pub.manifest()
                            pubs.append(
                                PubPrediction(
                                    name=pub.name,
                                    member_distributions={
                                        component.entry.name: predictions[component.entry.name]
                                        for component in pub.components
                                    },
                                    scheduled_seconds=runtime.duration_s(pub.circuit, backend.target),
                                    repetition_delay_seconds=repetition_delay(backend),
                                    classical_latency_seconds=manifest["sequential_stage_count"]
                                    * args.classical_latency_us
                                    * 1e-6,
                                    simulation_shots=args.model_shots,
                                    classical_stage_count=manifest["sequential_stage_count"],
                                    duration_assumption=(
                                        "Target duration includes reset; dynamic classical latency is a declared "
                                        "per-stage planning assumption"
                                    ),
                                )
                            )
                        jobs.append(
                            JobCandidate(
                                name=f"{backend_name}/{kind}/{index}",
                                pubs=tuple(pubs),
                                shots=shots,
                                overhead_seconds=args.job_overhead_seconds,
                                max_execution_seconds=args.max_execution_seconds,
                                overhead_assumption=(
                                    "declared overhead; 2.3 s default is the retained dynamic job's non-circuit "
                                    "charge, not a backend guarantee"
                                ),
                            )
                        )
            if args.family in ("ripple", "rank-sector") and len(jobs) != 1:
                raise runtime.LiveRunError(
                    f"{args.family}: {shots} shots require {len(jobs)} jobs; the static family requires one job"
                )
            name = f"candidate-{candidate_index:03d}-shots-{shots}"
            plans.append(
                CandidatePlan(
                    name=name,
                    jobs=tuple(jobs),
                    proxy_metadata={
                        "backend": choices[0].snap.name,
                        "seed": choices[0].seed,
                        "replicas": len(choices[0].replicas),
                        "shots": shots,
                        "proxy_score": sum(choice.joint_score for choice in choices) / len(choices),
                    },
                )
            )
            ownership[name] = choices, configuration, shots
    remaining = usage.get("usage_remaining_seconds")
    budget = BudgetContract(
        float(remaining) if remaining is not None else args.max_total_execution_seconds + args.reserve_seconds,
        args.reserve_seconds,
        args.max_total_execution_seconds,
    )
    policy = settings(args)
    scenarios = tuple(CostScenario(**scenario) for scenario in policy["cost_scenarios"])
    allocation_audits: dict[str, dict[str, Any]] = {}
    if per_pub:
        from pub_shot_allocation import allocate_plans

        couplings: dict[str, tuple[tuple[str, ...], ...]] = {}
        for candidate in plans:
            candidate_choices, configuration, _shots = ownership[candidate.name]
            row_pubs: dict[int, str] = {}
            metadata = configuration.get("members", {})
            for pub in runtime.execution_pubs(candidate_choices):
                for component in pub.components:
                    row = metadata.get(component.entry.name, {}).get("execution_row")
                    if row is not None:
                        if row in row_pubs and row_pubs[row] != pub.name:
                            raise runtime.LiveRunError("a declared execution row was split across PUBs")
                        row_pubs[row] = pub.name
            couplings[candidate.name] = tuple(
                tuple(row_pubs[row] for row in rows) for rows in configuration.get("matched_walk_rows", {}).values()
            )
        allocated, allocation_audits = allocate_plans(
            tuple(plans),
            contracts,
            tuple(tiers),
            budget,
            simulation_alpha=args.simulation_alpha,
            objective=policy["objective"],
            cost_scenarios=scenarios,
            coupled_pubs=couplings,
            unscored_tier="smallest" if args.family in PATCH_FAMILIES else "largest",
        )
        for original, allocated_plan in zip(plans, allocated, strict=True):
            selected_choices, selected_configuration, _shots = ownership[original.name]
            ownership[allocated_plan.name] = (
                selected_choices,
                selected_configuration,
                max(allocation_audits[allocated_plan.name]["pub_shots"].values()),
            )
        plans = list(allocated)
    result = optimize(
        tuple(plans),
        contracts,
        budget,
        simulation_alpha=args.simulation_alpha,
        objective=policy["objective"],
        cost_scenarios=scenarios,
    )
    # An infeasible dry run retains a concrete candidate and every rejection;
    # its state prevents that diagnostic archive from becoming a submission.
    retained = result.selected or plans[0].name
    choices, configuration, args.shots = ownership[retained]
    if per_pub:
        args.pub_shots = dict(allocation_audits[retained]["pub_shots"])
    metadata = {
        "family_configuration": configuration,
        "observable_contracts": json.loads(json.dumps([asdict(contract) for contract in contracts])),
        "optimization": result.as_dict()
        | {
            "retained_candidate": retained,
            "searched_routed_sets": len(candidates),
            "shot_tiers": tiers,
            "scope": (
                "bounded routed candidates with endpoint minima and costed whole-tier consolidation; "
                "global optimality is unclaimed"
                if per_pub
                else "bounded routed candidates and uniform shot tiers; global optimality is unclaimed"
            ),
        },
        "optimizer_settings": settings(args),
        **({"pub_shots": args.pub_shots, "shot_allocation": allocation_audits[retained]} if per_pub else {}),
        "optimization_budget": asdict(budget),
        "local_simulation_batches": (
            batches := [batch for simulator in simulators.values() for batch in local_compute.batches(simulator)]
        ),
        "compiled_ideal_validation": {
            "method": "branch-resolved statevector on active compiled replica wires",
            "absolute_tolerance": 1e-10,
            "noise_method": sorted({str(batch["method"]) for batch in batches}),
            "noise_policy": local_compute.settings(args)["method"],
            "all_candidates_passed": True,
        },
    }
    return choices, metadata


def measured_family(
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    runtime: Any,
    *,
    correction_evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Raw measured contrasts with simultaneous bounded-shot intervals across jobs."""
    if record.get("family_configuration", {}).get("name") == "folded-correction":
        import correction_collection

        return correction_collection.analyze(record, correction_evidence, executed, runtime)
    contracts = record.get("observable_contracts", [])
    if not contracts:
        return {}
    required = sorted({term["member"] for contract in contracts for term in contract["terms"]})
    missing = sorted(set(required) - distributions.keys())
    if missing:
        return {"withheld": f"missing measured members {missing}"}
    missing_execution = sorted(set(required) - executed.keys())
    if missing_execution:
        return {"withheld": f"missing execution evidence {missing_execution}"}
    reason = runtime._comparisons_withheld(required, executed)
    if reason:
        return {"withheld": reason}
    endpoints = tuple(
        ObservableContract(
            **{key: value for key, value in contract.items() if key != "terms"},
            terms=tuple(
                ObservableTerm(term["member"], tuple(term["values"]), term["sign"]) for term in contract["terms"]
            ),
        )
        for contract in contracts
    )
    by_pub: dict[str, dict[str, tuple[tuple[float, ...], ...]]] = {}
    for member in required:
        by_pub.setdefault(executed[member]["pub"], {})[member] = tuple(
            tuple(map(float, distribution)) for distribution in distributions[member]
        )
    try:
        if "pub_shots" in record:
            shot_map = record["pub_shots"]
            if not isinstance(shot_map, dict) or any(
                type(value) is not int or value <= 0 for value in shot_map.values()
            ):
                raise ValueError("record PUB shots must be positive integers")
            declared_pubs = {pub["name"] for pub in record.get("execution_pubs", [])}
            if set(shot_map) != declared_pubs:
                raise ValueError("record PUB shot map differs from the complete execution manifest")
            for member in required:
                execution = executed[member]
                actual_shots = execution.get("shots")
                if type(actual_shots) is not int or actual_shots != shot_map.get(execution["pub"]):
                    raise ValueError(f"{member}: validated measured shots differ from the approved PUB allocation")
            pubs = tuple(ObservedPub(name, members, shot_map[name]) for name, members in by_pub.items())
        else:
            pubs = tuple(ObservedPub(name, members, int(record["shots"])) for name, members in by_pub.items())
        return analyze_observations(pubs, endpoints).as_dict()
    except ValueError as error:
        return {"withheld": f"invalid measured family data: {error}"}

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
from diagnostic_experiments import N21_FAMILIES, family_contracts, folded_group, n21_group, n21_orbit_rca_group
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


def window_durations(runtime: Any, snapshot: Any) -> tuple[int, int, float]:
    """Readout length and echo half-window in dt from the backend's slowest measure and reset.

    The delay arm idles one readout length. The echo halves together cover
    1.2 times the longest measure plus reset, so the second X precedes the
    second round and no tail of the window stays unechoed.
    """
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    longest = {}
    for name in ("measure", "reset"):
        durations = [
            float(properties.duration)
            for properties in target[name].values()
            if properties is not None and properties.duration is not None
        ]
        if not durations or target.dt is None or target.dt <= 0:
            raise runtime.LiveRunError(f"the N=21 window arms need a calibrated {name} duration and dt")
        longest[name] = max(durations) / float(target.dt)

    def rounded(value: float) -> int:
        return granularity * math.ceil(value / granularity)

    return rounded(longest["measure"]), rounded(0.6 * (longest["measure"] + longest["reset"])), float(target.dt)


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
        windows: dict[str, dict[str, float]] = {}
        if args.family == "n21-orbit-rca":
            # Window durations come from each backend's calibration, so each
            # snapshot routes its own group; per-snapshot traces merge by group.
            # A backend that lacks calibrated durations or rejects the group
            # leaves the others in the search; the trace records its reason.
            for snapshot in snapshots:
                local: dict[str, Any] = {}
                try:
                    window_dt, half_dt, dt = window_durations(runtime, snapshot)
                    group = n21_orbit_rca_group(window_dt, half_dt)
                    routed += runtime.select_candidates(group, [snapshot], args.seeds, local)
                except (runtime.LiveRunError, QiskitError, ValueError) as error:
                    trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
                    continue
                windows[snapshot.name] = {"window_delay_dt": window_dt, "echo_half_dt": half_dt, "dt_seconds": dt}
                trace.setdefault(group.name, {}).update(local.get(group.name, {}))
            if not routed:
                raise runtime.LiveRunError(
                    f"no backend routes the N=21 window family: {trace.get('family_rejections')}"
                )
            routed.sort(key=lambda choice: -choice.joint_score)
        else:
            routed = runtime.select_candidates(
                n21_group(orbit=args.family == "n21-orbit-feedback"), snapshots, args.seeds, trace
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
                        ([trial], {"name": args.family, "replica_cap": cap, **windows.get(candidate.snap.name, {})})
                    )
        return candidates
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


def prepare(
    runtime: Any, snapshots: list[Any], args: Any, usage: dict[str, Any], trace: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Compile and simulate the bounded candidate set before choosing a shot tier."""
    if args.family == "folded-correction":
        import correction_planning

        return correction_planning.prepare(runtime, snapshots, args, usage, trace)
    candidates = family_candidates(runtime, snapshots, args, trace)
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
    if per_pub and (args.family not in ("ripple", "rank-sector") or not args.optimize):
        raise runtime.LiveRunError("per-PUB shot allocation requires an optimized static algebra family")
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
        "local_simulation_batches": [
            batch for simulator in simulators.values() for batch in local_compute.batches(simulator)
        ],
        "compiled_ideal_validation": {
            "method": "branch-resolved statevector on active compiled replica wires",
            "absolute_tolerance": 1e-10,
            "noise_method": local_compute.settings(args)["method"],
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

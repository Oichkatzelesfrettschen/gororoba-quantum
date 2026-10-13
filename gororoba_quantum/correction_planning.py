"""Choose the strongest calibrated correction witness across fresh device snapshots.

One symbolic template supplies four fixed-order, single-replica dynamic PUBs.
The planner searches every supplied fresh snapshot before selecting by its
worst-arm calibrated quality proxy. Exact-binomial hypothetical sensitivity
and finite-shot noise predictions retain separate evidence classes. Actual
returned schedules gate the matched scientific decision after execution.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from typing import Any

import numpy as np
from qiskit.exceptions import QiskitError

import correction_circuits
import correction_statistics
import local_compute
from experiment_optimizer import JobCost, PubCost
from experiments import Group, Member, tvd
from packing import Replica
from qpu_planning import repetition_delay, settings

FAMILY = "folded-correction"
LABELS = (1, 1, 3, 3)
ARMS = ("measured_feedback", "recorded_bit_independent", "recorded_bit_independent", "measured_feedback")


def correction_group() -> Group:
    """Keep each measured histogram in its own PUB and retain recorded bit zero."""
    template = correction_circuits.correction_template()
    members = []
    for name, label, arm in zip(correction_statistics.MEMBERS, LABELS, ARMS, strict=True):
        ideal = np.zeros(4)
        ideal[label] = 1.0
        weights = np.asarray([float(outcome >> 1 == label >> 1) for outcome in range(4)])
        members.append(
            Member(name, template, ideal, correction_circuits.correction_binding(label, arm), weights=weights)
        )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        summary = {}
        for member in members:
            distribution = distributions[member.name]
            summary[member.name + "_terminal_correct"] = float(distribution @ member.weights)
            summary[member.name + "_first_correct"] = float(distribution[1] + distribution[3])
            summary[member.name + "_tvd_to_ideal"] = tvd(distribution, member.ideal)
        for label in (1, 3):
            summary[f"correction_known_minus_measured_s{label}"] = (
                summary[f"correction_known_s{label}_terminal_correct"]
                - summary[f"correction_measured_s{label}_terminal_correct"]
            )
        return summary

    return Group(
        "folded_correction",
        tuple(members),
        summarize,
        rate_keys=frozenset(member.name + "_terminal_correct" for member in members),
        execution_rows=(0, 1, 2, 3),
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _positive_integer(value: Any, label: str) -> int:
    _require(type(value) is int and value > 0, f"{label} must be a positive integer")
    return int(value)


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    _require(type(value) in (int, float), f"{label} must be a finite real value")
    result = float(value)
    _require(math.isfinite(result) and (result > 0 if positive else result >= 0), f"invalid {label}")
    return result


def _priced_job(
    runtime: Any, choice: Any, shots: int, overhead: float, latency_us: float, ceiling: float
) -> dict[str, Any]:
    pubs = runtime.execution_pubs([choice])
    delay = repetition_delay(choice.snap.backend)
    costs = []
    for pub in pubs:
        stages = pub.manifest()["sequential_stage_count"]
        duration = _finite(
            runtime.duration_s(pub.circuit, choice.snap.backend.target), "Target duration", positive=True
        )
        latency = stages * latency_us * 1e-6
        costs.append(
            PubCost(
                pub.name,
                shots,
                duration,
                delay,
                0.0,
                latency,
                shots * (duration + delay + latency),
                "Target gate duration includes reset; added per-stage controller latency is a planning assumption",
                stages,
            )
        )
    charge = math.fsum([overhead, *(pub.estimated_execution_seconds for pub in costs)])
    job = asdict(
        JobCost(
            f"{choice.snap.name}/dynamic/1",
            tuple(costs),
            overhead,
            charge,
            ceiling,
            "declared overhead; retained historical charge supplies no backend guarantee",
        )
    )
    # Approval compares fresh metadata with JSON archives, which encode PUB sequences as lists.
    job["pubs"] = list(job["pubs"])
    return job


def _rank(row: dict[str, Any]) -> tuple[float, float, int, int, str]:
    proxy = row["proxy_metadata"]
    return (
        -proxy["worst_arm_quality"],
        proxy["charge_lower_scenario_seconds"],
        proxy["total_cz_count"],
        proxy["seed"],
        proxy["backend"],
    )


def prepare(
    runtime: Any, snapshots: list[Any], args: Any, usage: dict[str, Any], trace: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Search a finite fresh-calibration frontier without mock or physical execution."""
    _require(args.family == FAMILY, "correction planner received another family")
    shots = _positive_integer(args.shots, "shots")
    _require(shots == 8192, "the reviewed correction protocol requires exactly 8192 shots per PUB")
    _require(args.alpha == 0.05 and args.power == 0.8, "the correction protocol fixes alpha=0.05 and power=0.8")
    _require(args.max_replicas in (None, 1), "correction witnesses require one replica")
    if args.optimize:
        _require(args.shot_tiers == [8192], "correction optimization uses the declared single 8192-shot tier")
        _require(args.replica_tiers == [1], "correction optimization requires one replica")
    seed_count = min(_positive_integer(args.seeds, "seeds"), _positive_integer(args.optimizer_candidates, "candidates"))
    model_shots = _positive_integer(args.model_shots, "model_shots")
    overhead = _finite(args.job_overhead_seconds, "job overhead")
    latency_us = _finite(args.classical_latency_us, "controller latency")
    ceiling = _finite(args.max_execution_seconds, "per-job ceiling", positive=True)
    aggregate_cap = _finite(args.max_total_execution_seconds, "aggregate ceiling", positive=True)
    _require(ceiling == aggregate_cap == 30.0, "the correction protocol fixes both execution ceilings at 30 seconds")
    reserve = _finite(args.reserve_seconds, "reserve")
    remaining = usage.get("usage_remaining_seconds")
    remaining = aggregate_cap + reserve if remaining is None else _finite(remaining, "remaining quota")
    scenarios = list(args.cost_scenarios)
    _require(bool(scenarios), "the correction protocol requires an explicit controller-stress cost scenario")
    _require(len({item["name"] for item in scenarios}) == len(scenarios), "duplicate cost scenario names")
    for scenario in scenarios:
        _require(
            set(scenario) == {"name", "job_overhead_seconds", "classical_latency_us"}
            and isinstance(scenario["name"], str)
            and bool(scenario["name"].strip())
            and scenario["name"] != "nominal",
            "unsupported correction cost scenario",
        )
        scenario_overhead = _finite(scenario["job_overhead_seconds"], "scenario overhead")
        scenario_latency = _finite(scenario["classical_latency_us"], "scenario controller latency")
        _require(
            scenario_overhead >= overhead and scenario_latency >= latency_us,
            "every correction cost scenario must meet or exceed both nominal overhead and controller latency",
        )
    hypothetical = correction_statistics.planning_certificate(
        shots, alpha=args.alpha, minimum_gain=0.01, assumed_gain=0.04, required_joint_power=args.power
    )
    group = correction_group()
    requirements = runtime.group_requirements(group)
    frontier = []
    owners = {}
    backend_search = []
    _require(bool(snapshots), "correction planning requires fresh backend snapshots")
    _require(len({snapshot.name for snapshot in snapshots}) == len(snapshots), "duplicate backend snapshots")
    required_backends = {"ibm_fez", "ibm_kingston", "ibm_marrakesh"}
    supplied_backends = {snapshot.name for snapshot in snapshots}
    _require(
        supplied_backends == required_backends,
        "correction planning requires all three fresh QPU snapshots; "
        f"missing={sorted(required_backends - supplied_backends)}, "
        f"unexpected={sorted(supplied_backends - required_backends)}; "
        "inspect the live discovery skipped-backend inventory",
    )
    for snapshot in sorted(snapshots, key=lambda item: item.name):
        reason = snapshot.ineligible_reason(getattr(args, "max_pending", None))
        violations = runtime.capability_violations(requirements, snapshot.capabilities)
        if reason is None and violations:
            reason = "; ".join(violations)
        if reason is None:
            violations = runtime.routing_admission_violations(group, snapshot)
            if violations:
                reason = "; ".join(violations)
        backend_row = {
            "backend": snapshot.name,
            "calibration": snapshot.calibration,
            "eligible": reason is None,
            "rejection_reason": reason,
            "compiled_candidate_count": 0,
            "admitted_candidate_count": 0,
        }
        backend_search.append(backend_row)
        if reason is not None:
            continue
        for seed in range(runtime.SEED_TRANSPILER, runtime.SEED_TRANSPILER + seed_count):
            name = f"{snapshot.name}-seed-{seed}-shots-{shots}"
            backend_row["compiled_candidate_count"] += 1
            try:
                routed = runtime._compile(group.members[0].circuit, snapshot, seed)
                isas = [
                    correction_circuits.bind_correction_template(routed, label, arm)
                    for label, arm in zip(LABELS, ARMS, strict=True)
                ]
                for member, isa in zip(group.members, isas, strict=True):
                    isa.name = member.name
                    rejected = runtime.compiled_violations(isa, snapshot)
                    _require(not rejected, f"{member.name}: rejected native circuit: {rejected}")
                template_pairs = {
                    str(label): correction_circuits.validate_correction_pair(routed, isas[feedback], isas[known], label)
                    for label, feedback, known in ((1, 0, 1), (3, 3, 2))
                }
                scores = [
                    _finite(runtime.layout_score(isa, snapshot.backend.target), "calibrated quality", positive=True)
                    for isa in isas
                ]
                layout = routed.layout.initial_index_layout(filter_ancillas=True)
                choice = runtime.Choice(group, snapshot, seed, layout, isas, scores, min(scores))
                used = sorted({qubit for isa in isas for qubit in runtime._physical(isa)})
                replica = Replica(0, {qubit: qubit for qubit in used}, min(scores))
                runtime._set_entries(choice, [replica], runtime.ReplicaPolicy(args.replica_floor, 1, False, True))
                pubs = runtime.execution_pubs([choice])
                _require(
                    len(pubs) == 4
                    and all(pub.kind == "dynamic" and pub.backend == snapshot.name for pub in pubs)
                    and [component.entry.name for pub in pubs for component in pub.components]
                    == list(correction_statistics.MEMBERS),
                    "correction family changed its four isolated dynamic PUBs or order",
                )
                _require(
                    [len(batch) for batch in runtime.submission_batches([choice], "dynamic", shots)] == [4],
                    "correction family must fit in one dynamic job",
                )
                pairs = {
                    str(label): correction_circuits.validate_bound_correction_pair(
                        pubs[feedback].circuit, pubs[known].circuit, label
                    )
                    for label, feedback, known in ((1, 0, 1), (3, 3, 2))
                }
                job = _priced_job(runtime, choice, shots, overhead, latency_us, ceiling)
                lower_job = _priced_job(runtime, choice, shots, overhead, 0.0, ceiling)
                reasons = []
                if usage.get("usage_limit_reached"):
                    reasons.append("instance reports its usage limit reached")
                if ceiling > aggregate_cap or ceiling + reserve > remaining:
                    reasons.append("execution ceiling violates aggregate quota or retained reserve")
                if job["estimated_charge_seconds"] > ceiling:
                    reasons.append("nominal charge exceeds execution ceiling")
                scenario_rows = []
                for scenario in sorted(scenarios, key=lambda item: item["name"]):
                    scenario_job = _priced_job(
                        runtime,
                        choice,
                        shots,
                        scenario["job_overhead_seconds"],
                        scenario["classical_latency_us"],
                        ceiling,
                    )
                    scenario_reasons = []
                    if scenario_job["estimated_charge_seconds"] > ceiling:
                        scenario_reasons.append("scenario charge exceeds execution ceiling")
                        reasons.append(f"cost scenario {scenario['name']} exceeds execution ceiling")
                    scenario_rows.append(
                        {
                            "name": scenario["name"],
                            "feasible": not scenario_reasons,
                            "estimated_charge_seconds": scenario_job["estimated_charge_seconds"],
                            "jobs": [scenario_job],
                            "rejection_reasons": scenario_reasons,
                        }
                    )
                if not hypothetical["hypothetical_power_qualified"]:
                    reasons.extend(hypothetical["rejection_reasons"])
                total_cz = sum(operation == "cz" for isa in isas for operation, _ in runtime._ops(isa))
                row = {
                    "name": name,
                    "feasible": not reasons,
                    "estimated_charge_seconds": job["estimated_charge_seconds"],
                    "total_execution_ceiling_seconds": ceiling,
                    "jobs": [job],
                    "observables": [],
                    "rejection_reasons": reasons,
                    "proxy_metadata": {
                        "backend": snapshot.name,
                        "seed": seed,
                        "shots": shots,
                        "replicas": 1,
                        "worst_arm_quality": min(scores),
                        "member_scores": scores,
                        "charge_lower_scenario_seconds": lower_job["estimated_charge_seconds"],
                        "total_cz_count": total_cz,
                    },
                    "cost_scenarios": scenario_rows,
                    "worst_case_charge_seconds": max(
                        [job["estimated_charge_seconds"], *(item["estimated_charge_seconds"] for item in scenario_rows)]
                    ),
                    "normalized_precision_radius": None,
                }
                frontier.append(row)
                owners[name] = choice, template_pairs, pairs
                if row["feasible"]:
                    backend_row["admitted_candidate_count"] += 1
            except (QiskitError, ValueError, runtime.LiveRunError) as error:
                trace.setdefault("correction_candidate_rejections", []).append(
                    {"backend": snapshot.name, "seed": seed, "reason": str(error)}
                )
    trace["correction_backend_search"] = backend_search
    if not frontier:
        diagnostic = runtime._scrub_instances(runtime._jsonable(trace))
        raise runtime.LiveRunError(
            "correction family has no structurally valid routed candidate; "
            f"selection_trace={json.dumps(diagnostic, sort_keys=True)}"
        )
    admitted = sorted((row for row in frontier if row["feasible"]), key=_rank)
    retained = admitted[0] if admitted else min(frontier, key=_rank)
    choice, template_pairs, pairs = owners[retained["name"]]
    runtime.check_target_matches_properties(
        choice.isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name
    )
    simulator = runtime.noise_simulator(
        choice.snap.name, choice.snap.backend.target, choice.snap.properties, local_compute.settings(args)
    )
    noisy = runtime.simulate(choice, simulator, model_shots)
    modeled_members = {}
    for member in group.members:
        distributions = noisy[member.name]
        _require(len(distributions) == 1, "correction model changed replica count")
        probabilities = np.asarray(distributions[0], dtype=float)
        _require(
            probabilities.shape == (4,)
            and bool(np.isfinite(probabilities).all())
            and bool((probabilities >= 0).all())
            and bool(np.isclose(probabilities.sum(), 1, atol=1e-12, rtol=0)),
            "invalid correction noise-model distribution",
        )
        modeled_members[member.name] = {
            "probabilities": probabilities.tolist(),
            "terminal_success_probability": float(probabilities @ member.weights),
        }
    quality_policy = (
        "highest minimum across four arms of ESP times exp(-T*sum(1/T2)); "
        "ties use lower Target-plus-repetition charge scenario, total CZ, seed, backend name; "
        "calibration proxies establish neither measured fidelity nor global optimality"
    )
    configuration = {
        "name": FAMILY,
        "shots_per_pub": shots,
        "member_order": list(correction_statistics.MEMBERS),
        "replica_cap": 1,
        "execution_row_count": 4,
        "shared_initial_layout": choice.layout,
        "placement_contract": "one routed symbolic template, four isolated PUBs, one replica, one dynamic job",
        "circuit_pairs": pairs,
        "template_pairs": template_pairs,
        "backend_search": backend_search,
        "finite_candidate_frontier": frontier,
        "candidate_rejections": trace.get("correction_candidate_rejections", []),
        "calibration_quality_policy": quality_policy,
        "candidate_seeds_per_backend": seed_count,
        "hypothetical_power": hypothetical,
        "decision_contract": {
            "method": "four_one_sided_clopper_pearson_bounds",
            "family_alpha": args.alpha,
            "per_bound_tail": args.alpha / 4,
            "minimum_gain": 0.01,
            "require_both_labels": True,
            "count_semantics": "raw integer counts; y=first_bit+2*terminal_bit",
            "postexecution_schedule_gate": True,
        },
        "model_prediction": {
            "evidence_class": "finite-shot calibration noise simulation; controller/instrument errors incomplete",
            "shots_per_member": model_shots,
            "seed": runtime.SEED_SIMULATOR,
            "members": modeled_members,
            "gain_known_minus_measured": {
                str(label): modeled_members[f"correction_known_s{label}"]["terminal_success_probability"]
                - modeled_members[f"correction_measured_s{label}"]["terminal_success_probability"]
                for label in (1, 3)
            },
            "prediction_frozen_before_hardware": True,
        },
        "native_mock_required": False,
        "schedule_qualification": "actual returned scheduler metadata gates matched post-execution inference",
        "classical_dispatch_retained": True,
        "dispatch_removal_test": False,
        "dt_seconds": choice.snap.backend.dt,
    }
    metadata = {
        "family_configuration": configuration,
        "observable_contracts": [],
        "optimization": {
            "selected": retained["name"] if admitted else None,
            "retained_candidate": retained["name"],
            "candidates": frontier,
            "pareto_frontier": [],
            "rejection_reasons": []
            if admitted
            else ["every routed correction candidate failed cost or CP scenario admission"],
            "simulation_alpha": args.simulation_alpha,
            "simulation_comparisons": 0,
            "objective": "worst_arm_calibrated_quality_then_charge",
            "selected_objective_value": retained["proxy_metadata"]["worst_arm_quality"],
            "cost_scenarios": scenarios,
            "searched_routed_sets": len(frontier),
            "shot_tiers": [shots],
            "scope": "finite fresh-snapshot/seed frontier; exact-binomial planning remains hypothetical",
            "assumptions": [quality_policy, "actual schedule mismatch withholds the matched scientific decision"],
        },
        "optimizer_settings": settings(args),
        "optimization_budget": {
            "remaining_seconds": remaining,
            "reserve_seconds": reserve,
            "max_total_execution_seconds": aggregate_cap,
        },
        "local_simulation_batches": local_compute.batches(simulator),
        "compiled_ideal_validation": {
            "method": "branch-resolved statevector on native and final PUB wires",
            "absolute_tolerance": 1e-11,
            "noise_method": local_compute.settings(args)["method"],
            "all_candidates_passed": True,
        },
    }
    return [choice], metadata

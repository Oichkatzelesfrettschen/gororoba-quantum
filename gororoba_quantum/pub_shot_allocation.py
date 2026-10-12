"""Allocate complete PUB rows to declared shot tiers before hardware acquisition.

Every endpoint chooses a sufficient uniform tier using the search-wide model
allowance. Complete tier groups may then move upward to reduce job overhead
or improve precision. Every alternative retains the same model confidence
event and passes the existing bounded-shot evaluator and all job cost gates.
"""

from __future__ import annotations

import math
from dataclasses import asdict, replace
from itertools import product
from typing import Any

from experiment_optimizer import (
    BudgetContract,
    CandidatePlan,
    CandidateResult,
    CostScenario,
    ObservableContract,
    _simulation_comparisons,
    evaluate_candidate,
)

MAX_ALLOCATION_VARIANTS = 4096


def _tier_plan(plan: CandidatePlan, pub_shots: dict[str, int], name: str) -> CandidatePlan:
    """Rebuild complete homogeneous jobs while retaining original PUB order."""
    jobs = []
    job_indices: dict[str, int] = {}
    for job in plan.jobs:
        prefix = job.name.rpartition("/")[0] or job.name
        for tier in sorted({pub_shots[pub.name] for pub in job.pubs}):
            pubs = tuple(pub for pub in job.pubs if pub_shots[pub.name] == tier)
            job_indices[prefix] = job_indices.get(prefix, 0) + 1
            jobs.append(replace(job, name=f"{prefix}/{job_indices[prefix]}", pubs=pubs, shots=tier))
    return replace(
        plan, name=name, jobs=tuple(jobs), proxy_metadata=plan.proxy_metadata | {"shots": max(pub_shots.values())}
    )


def _rank(result: CandidateResult, objective: str) -> tuple[float, float, str]:
    """Use the optimizer's objective ordering on a shared-comparison evaluation."""
    charge = result.worst_case_charge_seconds
    score = charge if objective == "minimum_charge" else result.normalized_precision_radius
    if charge is None or score is None:
        raise ValueError(f"{result.name}: feasible allocation lacks its objective coordinates")
    return score, charge, result.name


def allocate_plans(
    plans: tuple[CandidatePlan, ...],
    contracts: tuple[ObservableContract, ...],
    tiers: tuple[int, ...],
    budget: BudgetContract,
    *,
    simulation_alpha: float,
    objective: str = "minimum_charge",
    cost_scenarios: tuple[CostScenario, ...] = (),
    coupled_pubs: dict[str, tuple[tuple[str, ...], ...]] | None = None,
) -> tuple[tuple[CandidatePlan, ...], dict[str, dict[str, Any]]]:
    """Preserve every member and use conservative endpoint-wise tier admission.

    Each routed plan retains its best feasible whole-tier upward assignment,
    including uniform allocations. Deterministic allocation alternatives reuse
    the original simulated marginals and simultaneous confidence event. Fresh
    hardware data never enters allocation. Endpoint-wise minimum tiers and
    whole-tier promotion define a bounded search, not a global PUB optimum.
    """
    if not tiers or any(type(tier) is not int or tier <= 0 for tier in tiers):
        raise ValueError("PUB shot tiers must be positive integers")
    if tuple(sorted(set(tiers))) != tiers:
        raise ValueError("PUB shot tiers must be unique and increasing")
    if objective not in ("minimum_charge", "precision_at_budget"):
        raise ValueError(f"unknown allocation objective {objective!r}")
    if objective == "precision_at_budget" and any(
        contract.precision_half_width is None or contract.minimum_effect is not None for contract in contracts
    ):
        raise ValueError("precision_at_budget requires precision-only contracts with positive precision_half_width")
    comparisons = _simulation_comparisons(plans, contracts)
    allocated = []
    audits = {}
    for plan in plans:
        member_pubs = {member: pub.name for job in plan.jobs for pub in job.pubs for member in pub.member_distributions}
        pub_names = [pub.name for job in plan.jobs for pub in job.pubs]
        if len(pub_names) != len(set(pub_names)):
            raise ValueError("PUB allocation requires unique PUB identities")
        endpoint_tiers: dict[str, int] = {}
        largest_rejections: dict[str, list[str]] = {}
        for tier in tiers:
            probe = replace(plan, jobs=tuple(replace(job, shots=tier) for job in plan.jobs))
            result = evaluate_candidate(
                probe,
                contracts,
                budget,
                simulation_alpha=simulation_alpha,
                simulation_comparisons=comparisons,
                cost_scenarios=cost_scenarios,
            )
            if len(result.observables) != len(contracts):
                raise ValueError(f"{plan.name}: invalid allocation probe: {result.rejection_reasons}")
            for observable in result.observables:
                if observable.feasible:
                    endpoint_tiers.setdefault(observable.name, tier)
                elif tier == tiers[-1]:
                    largest_rejections[observable.name] = list(observable.rejection_reasons)
        pub_shots = {name: tiers[0] for name in pub_names}
        scored_pubs: set[str] = set()
        for contract in contracts:
            tier = endpoint_tiers.setdefault(contract.name, tiers[-1])
            for term in contract.terms:
                if term.member not in member_pubs:
                    raise ValueError(f"{contract.name}: member {term.member} has no PUB")
                name = member_pubs[term.member]
                pub_shots[name] = max(pub_shots[name], tier)
                scored_pubs.add(name)
        unscored = sorted(set(pub_names) - scored_pubs)
        for name in unscored:
            pub_shots[name] = tiers[-1]
        couplings = (coupled_pubs or {}).get(plan.name, ())
        for coupling in couplings:
            if (
                len(coupling) < 2
                or len(coupling) != len(set(coupling))
                or any(name not in pub_shots for name in coupling)
            ):
                raise ValueError(f"{plan.name}: invalid matched PUB coupling")
            positions = [pub_names.index(name) for name in coupling]
            if sorted(positions) != list(range(min(positions), max(positions) + 1)):
                raise ValueError(f"{plan.name}: matched PUB rows must be adjacent before tier allocation")
        changed = True
        while changed:
            changed = False
            for coupling in couplings:
                tier = max(pub_shots[name] for name in coupling)
                for name in coupling:
                    if pub_shots[name] < tier:
                        pub_shots[name] = tier
                        changed = True
        minimum_pub_shots = dict(pub_shots)
        used_tiers = sorted(set(minimum_pub_shots.values()))
        domains = tuple(tuple(tier for tier in tiers if tier >= minimum) for minimum in used_tiers)
        variant_count = math.prod(len(domain) for domain in domains)
        if variant_count > MAX_ALLOCATION_VARIANTS:
            raise ValueError(
                f"{plan.name}: {variant_count} whole-tier upward allocations exceed the explicit "
                f"search limit {MAX_ALLOCATION_VARIANTS}; reduce the declared shot-tier domain"
            )
        variants = []
        for index, promoted in enumerate(product(*domains)):
            promotion = dict(zip(used_tiers, promoted, strict=True))
            mapping = {pub: promotion[minimum] for pub, minimum in minimum_pub_shots.items()}
            variant = _tier_plan(plan, mapping, f"{plan.name}-allocation-{index:04d}")
            evaluation = evaluate_candidate(
                variant,
                contracts,
                budget,
                simulation_alpha=simulation_alpha,
                simulation_comparisons=comparisons,
                cost_scenarios=cost_scenarios,
            )
            variants.append((variant, mapping, evaluation))
        feasible = [variant for variant in variants if variant[2].feasible]
        selected = min(feasible, key=lambda variant: _rank(variant[2], objective)) if feasible else variants[0]
        selected_plan, pub_shots, selected_result = selected
        name = plan.name + "-per-pub"
        allocated.append(replace(selected_plan, name=name))
        audits[name] = {
            "schema": "prespecified-pub-shot-allocation-v2",
            "method": "endpoint sufficient minima, matched coupling, and costed whole-tier upward assignments",
            "tiers": list(tiers),
            "simulation_comparisons": comparisons,
            "pub_shots": pub_shots,
            "minimum_pub_shots": minimum_pub_shots,
            "endpoint_tiers": endpoint_tiers,
            "infeasible_at_max_tier": largest_rejections,
            "unscored_pubs_at_max_tier": unscored,
            "coupled_pubs": [list(coupling) for coupling in couplings],
            "job_count": len(selected_plan.jobs),
            "objective": objective,
            "allocation_search": {
                "scope": "complete whole-tier upward assignments; global PUB allocation optimality is unclaimed",
                "variant_limit": MAX_ALLOCATION_VARIANTS,
                "variant_count": variant_count,
                "selected": selected_result.name if feasible else None,
                "retained": selected_result.name,
                "candidates": [asdict(result) | {"pub_shots": mapping} for _variant, mapping, result in variants],
            },
            "row_order": "ascending shot tier; original relative order retained inside each job",
            "sampling_boundary": "complete joint shot vectors within each PUB; different PUBs remain unpaired",
            "comparison_boundary": "tier jobs require stable comparison context and matching execution calibration",
        }
    if _simulation_comparisons(tuple(allocated), contracts) != comparisons:
        raise ValueError("PUB allocation changed the search-wide simulation comparison count")
    return tuple(allocated), audits

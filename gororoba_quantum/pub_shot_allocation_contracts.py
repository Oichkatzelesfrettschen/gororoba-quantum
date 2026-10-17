"""Check deterministic tier allocation, Runtime job costs, and measured denominators.

Credential-free fixtures retain every PUB and permit arbitrary dependence
inside each shot. Explicit failures remain active under optimized Python.
"""

from __future__ import annotations

import copy
import math
from dataclasses import replace
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np

import qpu_planning
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
    evaluate_candidate,
    optimize,
)
from pub_shot_allocation import MAX_ALLOCATION_VARIANTS, allocate_plans


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _fixture(repetition_seconds: float = 0.001) -> tuple[CandidatePlan, tuple[ObservableContract, ...], BudgetContract]:
    pubs = tuple(
        PubPrediction(
            name,
            {name + "_member": ((0.25, 0.75),)},
            repetition_seconds - 0.00025,
            0.00025,
            "fixture target duration",
            simulation_shots=32768,
            classical_stage_count=0,
        )
        for name in ("mean", "contrast_a", "contrast_b", "other_mean")
    )
    plan = CandidatePlan("fixture", (JobCandidate("backend/static/1", pubs, 4096, 2.3, 40.0, "fixed overhead"),))
    contracts = (
        ObservableContract("mean", (ObservableTerm("mean_member", (0.0, 1.0)),), precision_half_width=0.08, alpha=0.01),
        ObservableContract(
            "difference",
            (ObservableTerm("contrast_a_member", (0.0, 1.0)), ObservableTerm("contrast_b_member", (0.0, 1.0), -1)),
            precision_half_width=0.08,
            alpha=0.01,
        ),
        ObservableContract(
            "other_mean", (ObservableTerm("other_mean_member", (0.0, 1.0)),), precision_half_width=0.08, alpha=0.01
        ),
    )
    return plan, contracts, BudgetContract(200.0, 20.0, 80.0)


def _verify_allocation() -> dict[str, Any]:
    plan, contracts, budget = _fixture()
    scenarios = (CostScenario("stress", 4.6, 40.0),)
    plans, audits = allocate_plans(
        (plan,), contracts, (1024, 4096), budget, simulation_alpha=0.01, cost_scenarios=scenarios
    )
    allocated = plans[0]
    audit = audits[allocated.name]
    expected = {"mean": 1024, "contrast_a": 4096, "contrast_b": 4096, "other_mean": 1024}
    _require(audit["pub_shots"] == expected, "endpoint-wise allocation lost a hard comparison or overallocated a mean")
    _require(
        [job.name for job in allocated.jobs] == ["backend/static/1", "backend/static/2"],
        "tier jobs lost canonical batch identities",
    )
    _require(
        [[pub.name for pub in job.pubs] for job in allocated.jobs]
        == [["mean", "other_mean"], ["contrast_a", "contrast_b"]],
        "tier grouping changed relative row order",
    )
    _require(
        [pub for job in plan.jobs for pub in job.pubs]
        == sorted((pub for job in allocated.jobs for pub in job.pubs), key=lambda pub: list(expected).index(pub.name)),
        "allocation altered a PUB's predictions, membership, or circuit timing",
    )
    result = optimize(plans, contracts, budget, cost_scenarios=scenarios)
    _require(result.selected == allocated.name, "mixed-shot allocation failed final statistical admission")
    candidate = result.candidates[0]
    _require(
        math.isclose(candidate.estimated_charge_seconds or 0.0, 2 * 2.3 + 0.001 * (2 * 1024 + 2 * 4096)),
        "job overhead or PUB shots were mispriced",
    )
    _require(
        math.isclose(candidate.worst_case_charge_seconds or 0.0, 2 * 4.6 + 0.001 * (2 * 1024 + 2 * 4096)),
        "stress cost omitted a tier job's overhead",
    )
    _require(candidate.total_execution_ceiling_seconds == 80.0, "allocated job ceiling omitted a tier")
    observed = analyze_observations(
        tuple(ObservedPub(pub.name, pub.member_distributions, job.shots) for job in allocated.jobs for pub in job.pubs),
        contracts,
    )
    _require(
        [row.confidence_half_width for row in observed.observables]
        == [row.confidence_half_width for row in candidate.observables],
        "planned and measured per-PUB confidence bounds differ",
    )
    short = optimize(plans, contracts, replace(budget, max_total_execution_seconds=79.0))
    _require(short.selected is None, "one-second aggregate ceiling shortfall passed")
    coupled, coupled_audits = allocate_plans(
        (plan,),
        contracts,
        (1024, 4096),
        budget,
        simulation_alpha=0.01,
        coupled_pubs={plan.name: (("mean", "contrast_a"),)},
    )
    _require(
        coupled_audits[coupled[0].name]["pub_shots"]["mean"] == 4096,
        "matched companion was left in another shot-tier job",
    )
    _require(
        [pub.name for pub in coupled[0].jobs[-1].pubs][:2] == ["mean", "contrast_a"],
        "matched adjacent rows lost adjacency",
    )
    for bad_tiers in ((), (1024, 1024), (4096, 1024), (True, 4096), (-1, 4096)):
        try:
            allocate_plans((plan,), contracts, bad_tiers, budget, simulation_alpha=0.01)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"invalid shot tiers passed: {bad_tiers}")
    try:
        allocate_plans(
            (plan,),
            contracts,
            (1024, 4096),
            budget,
            simulation_alpha=0.01,
            coupled_pubs={plan.name: (("mean", "contrast_b"),)},
        )
    except ValueError:
        pass
    else:
        raise RuntimeError("nonadjacent matched rows passed")
    try:
        allocate_plans((plan,), contracts[:2], (1024, 4096), budget, simulation_alpha=0.01, unscored_tier="Largest")
    except ValueError:
        pass
    else:
        raise RuntimeError("an unknown unscored tier was accepted")
    unscored_plans, unscored_audits = allocate_plans(
        (plan,), contracts[:2], (1024, 4096), budget, simulation_alpha=0.01
    )
    unscored = unscored_audits[unscored_plans[0].name]
    _require(
        unscored["pub_shots"]["other_mean"] == 4096
        and unscored["unscored_pubs"] == ["other_mean"]
        and unscored["unscored_tier"] == "largest",
        "unscored control was silently dropped or downsampled",
    )
    impossible = tuple(replace(contract, precision_half_width=0.00001) for contract in contracts)
    rejected, rejected_audits = allocate_plans((plan,), impossible, (1024, 4096), budget, simulation_alpha=0.01)
    _require(
        len(rejected_audits[rejected[0].name]["infeasible_at_max_tier"]) == 3,
        "failed endpoints disappeared from allocation evidence",
    )
    _require(
        optimize(rejected, impossible, budget).selected is None, "insufficient maximum tier bypassed final admission"
    )
    alternatives = (plan, replace(plan, name="other_route"))
    routed, routed_audits = allocate_plans(alternatives, contracts, (1024, 4096), budget, simulation_alpha=0.01)
    routed_result = optimize(routed, contracts, budget)
    _require(
        routed_result.simulation_comparisons == 2 * audit["simulation_comparisons"],
        "routing alternatives escaped the simultaneous finite-model allowance",
    )
    _require(
        all(row["simulation_comparisons"] == routed_result.simulation_comparisons for row in routed_audits.values()),
        "allocation probes and routed final admission used different simulation allowances",
    )
    return audit


def _verify_consolidation() -> None:
    plan, contracts, budget = _fixture(0.00026)
    allocated, audits = allocate_plans((plan,), contracts, (1024, 4096), budget, simulation_alpha=0.01)
    audit = audits[allocated[0].name]
    search = audit["allocation_search"]
    mixed, uniform = search["candidates"]
    _require(math.isclose(mixed["estimated_charge_seconds"], 7.26240), "overhead counterexample changed")
    _require(math.isclose(uniform["estimated_charge_seconds"], 6.55984), "uniform comparison was mispriced")
    _require(search["selected"] == uniform["name"], "extra job overhead made the selected plan more expensive")
    _require(audit["pub_shots"] == dict.fromkeys(audit["pub_shots"], 4096), "uniform baseline lost complete coverage")
    _require(len(allocated[0].jobs) == 1, "uniform consolidation retained an empty tier job")
    _require(
        [pub.name for pub in allocated[0].jobs[0].pubs] == [pub.name for pub in plan.jobs[0].pubs],
        "uniform consolidation changed original PUB order",
    )
    expensive, _, _ = _fixture()
    mixed_plans, mixed_audits = allocate_plans((expensive,), contracts, (1024, 4096), budget, simulation_alpha=0.01)
    _require(len(mixed_plans[0].jobs) == 2, "shot-work savings were discarded when mixed allocation costs less")
    medium, _, _ = _fixture(0.0005)
    nominal, _audits = allocate_plans((medium,), contracts, (1024, 4096), budget, simulation_alpha=0.01)
    stress, stress_audits = allocate_plans(
        (medium,),
        contracts,
        (1024, 4096),
        budget,
        simulation_alpha=0.01,
        cost_scenarios=(CostScenario("stress", 4.6, 60.0),),
    )
    _require(len(nominal[0].jobs) == 2 and len(stress[0].jobs) == 1, "scenario overhead did not change consolidation")
    _require(
        all(row["cost_scenarios"] for row in stress_audits[stress[0].name]["allocation_search"]["candidates"]),
        "an allocation alternative skipped the stress scenario",
    )
    tight_job = replace(plan, jobs=(replace(plan.jobs[0], max_execution_seconds=6.0),))
    admitted, rejected = allocate_plans((tight_job,), contracts, (1024, 4096), budget, simulation_alpha=0.01)
    _require(len(admitted[0].jobs) == 2, "cheaper uniform workload exceeded a per-job ceiling")
    _require(
        rejected[admitted[0].name]["allocation_search"]["candidates"][1]["feasible"] is False,
        "uniform workload above its ceiling remained feasible",
    )
    tight_aggregate, _audits = allocate_plans(
        (expensive,),
        contracts,
        (1024, 4096),
        replace(budget, max_total_execution_seconds=40.0),
        simulation_alpha=0.01,
    )
    _require(len(tight_aggregate[0].jobs) == 1, "two job ceilings bypassed the aggregate cap")
    precision, precision_audits = allocate_plans(
        (expensive,),
        contracts,
        (1024, 4096, 8192),
        budget,
        simulation_alpha=0.01,
        objective="precision_at_budget",
    )
    precision_audit = precision_audits[precision[0].name]
    _require(
        precision_audit["pub_shots"] == {"mean": 4096, "contrast_a": 8192, "contrast_b": 8192, "other_mean": 4096},
        "precision objective failed to promote the worst endpoint before minimizing charge",
    )
    uniform_precision, uniform_audits = allocate_plans(
        (plan,), contracts, (1024, 4096, 8192), budget, simulation_alpha=0.01, objective="precision_at_budget"
    )
    _require(
        set(uniform_audits[uniform_precision[0].name]["pub_shots"].values()) == {8192},
        "precision ranking lost the cheaper uniform tier at the same worst endpoint radius",
    )
    _require(
        precision_audit["allocation_search"]["variant_count"] == 6,
        "whole-tier upward domain omitted declared promotions",
    )
    original_count = optimize((expensive,), contracts, budget).simulation_comparisons
    _require(
        precision_audit["simulation_comparisons"] == original_count
        and optimize(precision, contracts, budget, objective="precision_at_budget").simulation_comparisons
        == original_count,
        "deterministic allocation alternatives were counted as new model samples",
    )
    for candidate in precision_audit["allocation_search"]["candidates"]:
        _require(
            [row["simulation_error_radius"] for row in candidate["observables"]]
            == [
                row.simulation_error_radius
                for row in evaluate_candidate(
                    expensive, contracts, budget, simulation_comparisons=original_count
                ).observables
            ],
            "an upward allocation changed the original simultaneous model allowance",
        )
    for objective in ("minimum_charge", "precision_at_budget"):
        variants = []
        for candidate in precision_audit["allocation_search"]["candidates"]:
            mapping = candidate["pub_shots"]
            jobs = tuple(
                replace(
                    expensive.jobs[0],
                    name=f"backend/static/{index}",
                    pubs=tuple(pub for pub in expensive.jobs[0].pubs if mapping[pub.name] == tier),
                    shots=tier,
                )
                for index, tier in enumerate(sorted(set(mapping.values())), 1)
            )
            variants.append(replace(expensive, name=candidate["name"], jobs=jobs))
        selected, selected_audits = allocate_plans(
            (expensive,), contracts, (1024, 4096, 8192), budget, simulation_alpha=0.01, objective=objective
        )
        _require(
            selected_audits[selected[0].name]["allocation_search"]["selected"]
            == optimize(tuple(variants), contracts, budget, objective=objective).selected,
            "allocation ranking differs from the optimizer's declared objective order",
        )
    for objective in ("unknown", "precision_at_budget"):
        invalid_contracts = contracts if objective == "unknown" else (replace(contracts[0], minimum_effect=0.1),)
        try:
            allocate_plans((plan,), invalid_contracts, (1024, 4096), budget, simulation_alpha=0.01, objective=objective)
        except ValueError:
            pass
        else:
            raise RuntimeError("invalid allocation objective contract passed")
    with patch("pub_shot_allocation.MAX_ALLOCATION_VARIANTS", 1):
        try:
            allocate_plans((plan,), contracts, (1024, 4096), budget, simulation_alpha=0.01)
        except ValueError as error:
            _require("2 whole-tier upward allocations" in str(error), "search domain rejection hid its size")
        else:
            raise RuntimeError("excessive allocation domain was silently enumerated or truncated")
    _require(MAX_ALLOCATION_VARIANTS == 4096, "documented finite allocation bound changed")
    _require(
        mixed_audits[mixed_plans[0].name]["allocation_search"]["variant_count"] == 2,
        "actual two-tier domain grew unexpectedly",
    )


def _verify_measurement_denominators(audit: dict[str, Any]) -> None:
    plan, contracts, _budget = _fixture()
    from dataclasses import asdict

    pubs = plan.jobs[0].pubs
    record = {
        "observable_contracts": [asdict(contract) for contract in contracts],
        "pub_shots": audit["pub_shots"],
        "shots": 4096,
        "execution_pubs": [{"name": pub.name} for pub in pubs],
    }
    measured = {
        member: [np.asarray(distribution) for distribution in distributions]
        for pub in pubs
        for member, distributions in pub.member_distributions.items()
    }
    executed = {
        member: {"pub": pub.name, "shots": record["pub_shots"][pub.name]}
        for pub in pubs
        for member in pub.member_distributions
    }
    runtime = SimpleNamespace(_comparisons_withheld=lambda _required, _executed: None)
    result = qpu_planning.measured_family(record, measured, executed, runtime)
    _require("withheld" not in result, f"valid measured denominator rejected: {result}")
    reference = analyze_observations(
        tuple(ObservedPub(pub.name, pub.member_distributions, record["pub_shots"][pub.name]) for pub in pubs), contracts
    ).as_dict()
    _require(result == reference, "collection replaced actual per-PUB shots with the top-level maximum")
    for mutation in ("wrong_count", "missing_count", "missing_pub", "extra_pub", "boolean_count"):
        changed_record, changed_executed = copy.deepcopy(record), copy.deepcopy(executed)
        if mutation == "wrong_count":
            changed_executed["mean_member"]["shots"] = 4096
        elif mutation == "missing_count":
            del changed_executed["mean_member"]["shots"]
        elif mutation == "missing_pub":
            del changed_record["pub_shots"]["mean"]
        elif mutation == "extra_pub":
            changed_record["pub_shots"]["unsubmitted"] = 1024
        else:
            changed_record["pub_shots"]["mean"] = True
        rejected = qpu_planning.measured_family(changed_record, measured, changed_executed, runtime)
        _require("withheld" in rejected, f"invalid measured shot evidence passed: {mutation}")


def _verify_prepare() -> None:
    source, contracts, budget = _fixture()
    backend = SimpleNamespace(
        configuration=lambda: SimpleNamespace(
            dynamic_reprate_enabled=True, default_rep_delay=0.00025, rep_delay_range=[0.0, 0.001]
        ),
        target=object(),
    )
    snapshot = SimpleNamespace(name="backend", backend=backend, properties=object(), capabilities=object())
    entries = [
        SimpleNamespace(name=member, replicas=[object()], ideal=np.asarray(distributions[0]))
        for pub in source.jobs[0].pubs
        for member, distributions in pub.member_distributions.items()
    ]
    choice = SimpleNamespace(
        group=SimpleNamespace(name="rank_sector"),
        entries=entries,
        snap=snapshot,
        seed=6,
        replicas=[object()],
        joint_score=0.9,
    )
    pubs = [
        SimpleNamespace(
            name=pub.name,
            circuit=object(),
            components=(SimpleNamespace(entry=entry),),
            manifest=lambda: {"sequential_stage_count": 0},
        )
        for pub, entry in zip(source.jobs[0].pubs, entries, strict=True)
    ]

    def batches(_choices: list[Any], kind: str, shots: int, pub_shots: dict[str, int] | None = None) -> list[list[Any]]:
        if kind != "static":
            return []
        mapping = pub_shots or {pub.name: shots for pub in pubs}
        return [[pub for pub in pubs if mapping[pub.name] == tier] for tier in sorted(set(mapping.values()))]

    runtime = SimpleNamespace(
        LiveRunError=RuntimeError,
        group_admission_violations=lambda _group, _capabilities: [],
        noise_simulator=lambda *_args: SimpleNamespace(),
        simulate=lambda *_args: {entry.name: [entry.ideal] for entry in entries},
        submission_batches=batches,
        batch_shots=lambda batch, shots, pub_shots: pub_shots[batch[0].name] if pub_shots else shots,
        execution_pubs=lambda _choices: pubs,
        duration_s=lambda *_args: 0.00075,
    )
    args = SimpleNamespace(
        family="rank-sector",
        optimize=True,
        shot_allocation="per-pub",
        shot_tiers=[1024, 4096],
        model_shots=32768,
        max_execution_seconds=40.0,
        max_total_execution_seconds=80.0,
        reserve_seconds=20.0,
        job_overhead_seconds=2.3,
        classical_latency_us=20.0,
        precision=0.08,
        alpha=0.05,
        power=0.8,
        simulation_alpha=0.01,
        cost_scenarios=[],
    )
    with (
        patch.object(qpu_planning, "family_candidates", return_value=[([choice], {"name": "rank-sector"})]),
        patch.object(qpu_planning, "family_contracts", return_value=contracts),
        patch.object(qpu_planning, "ideal_compiled_probabilities", return_value=np.asarray([0.25, 0.75])),
    ):
        choices, metadata = qpu_planning.prepare(
            runtime, [snapshot], args, {"usage_remaining_seconds": budget.remaining_seconds}, {}
        )
    _require(choices == [choice], "tier allocation replaced the selected physical choices")
    _require(
        args.pub_shots == metadata["pub_shots"] and args.shots == 4096,
        "selected allocation differs between runtime arguments and retained record",
    )
    _require(metadata["optimization"]["selected"] is not None, "production preparation failed allocated admission")
    selected = next(
        candidate
        for candidate in metadata["optimization"]["candidates"]
        if candidate["name"] == metadata["optimization"]["selected"]
    )
    _require(
        len(selected["jobs"]) == 2 and selected["total_execution_ceiling_seconds"] == 80.0,
        "preparation silently retained the uniform one-job budget",
    )
    _require(
        metadata["shot_allocation"]["simulation_comparisons"] == metadata["optimization"]["simulation_comparisons"],
        "allocation used another simulation multiplicity than final optimization",
    )
    bound = qpu_planning.execution_contract(choices, metadata)
    _require(bound["pub_shots"] == args.pub_shots, "execution approval contract omitted the per-PUB denominator map")
    reservation = qpu_planning.budget_plan(runtime, choices, args, {"usage_remaining_seconds": 100.0})
    _require(
        reservation["admitted"] and reservation["combined_ceiling_seconds"] == 80.0,
        "tier budget lost one job's ceiling",
    )
    _require(
        [(job["shots"], job["pub_names"]) for job in reservation["jobs"]]
        == [(1024, ["mean", "other_mean"]), (4096, ["contrast_a", "contrast_b"])],
        "budget job membership differs from submitted shot-tier buckets",
    )
    _require(
        not qpu_planning.budget_plan(runtime, choices, args, {"usage_remaining_seconds": 99.0})["admitted"],
        "tier reservation spent one second of the retained quota reserve",
    )
    args.objective = "precision_at_budget"
    args.shot_tiers = [1024, 4096, 8192]
    with (
        patch.object(qpu_planning, "family_candidates", return_value=[([choice], {"name": "rank-sector"})]),
        patch.object(qpu_planning, "family_contracts", return_value=contracts),
        patch.object(qpu_planning, "ideal_compiled_probabilities", return_value=np.asarray([0.25, 0.75])),
    ):
        _choices, precise = qpu_planning.prepare(
            runtime, [snapshot], args, {"usage_remaining_seconds": budget.remaining_seconds}, {}
        )
    _require(
        precise["shot_allocation"]["objective"] == "precision_at_budget" and max(precise["pub_shots"].values()) == 8192,
        "production preparation failed to pass its precision objective into tier consolidation",
    )


def _verify_multibackend_reservation() -> None:
    choices = [SimpleNamespace(snap=SimpleNamespace(name=name)) for name in ("first", "second")]

    def pubs(selected: list[Any]) -> list[Any]:
        return [SimpleNamespace(name=choice.snap.name + "_pub") for choice in selected]

    def batches(
        selected: list[Any], kind: str, _shots: int, pub_shots: dict[str, int] | None = None
    ) -> list[list[Any]]:
        local_pubs = pubs(selected)
        _require(
            pub_shots is not None and set(pub_shots) == {pub.name for pub in local_pubs},
            "another backend's PUB allocation reached a local batch",
        )
        return [local_pubs] if kind == "static" else []

    runtime = SimpleNamespace(
        LiveRunError=RuntimeError,
        execution_pubs=pubs,
        submission_batches=batches,
        batch_shots=lambda batch, _shots, allocation: allocation[batch[0].name],
    )
    args = SimpleNamespace(
        shots=4096,
        pub_shots={"first_pub": 1024, "second_pub": 4096},
        max_execution_seconds=30.0,
        max_total_execution_seconds=60.0,
        reserve_seconds=20.0,
    )
    usage = {"usage_remaining_seconds": 80.0}
    result = qpu_planning.budget_plan(runtime, choices, args, usage)
    _require(
        result["admitted"] and [job["shots"] for job in result["jobs"]] == [1024, 4096],
        "backend-local allocation changed the complete reserved workload",
    )
    for mutation in ({"first_pub": 1024}, {"first_pub": 1024, "second_pub": 4096, "unknown": 1024}):
        changed = copy.copy(args)
        changed.pub_shots = mutation
        try:
            qpu_planning.budget_plan(runtime, choices, changed, usage)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("global allocation coverage was silently reduced to backend-local keys")


def _verify() -> None:
    audit = _verify_allocation()
    _verify_consolidation()
    _verify_measurement_denominators(audit)
    _verify_prepare()
    _verify_multibackend_reservation()
    print("PUB shot allocation contracts passed: endpoint bounds, paired rows, job ceilings, and measured counts")


if __name__ == "__main__":
    _verify()

"""Write an unapproved, artifact-bound case for an admitted diagnostic dry run.

The writer reads retained records and QPY circuits only. It constructs neither
an IBM service nor a primitive. The case separates model admission from future
hardware observations and carries the existing runner's approval command.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import re
import shlex
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qpy

CASE_FILENAME = "UNAPPROVED_CASE.md"
FAMILIES = {
    "folded-qpe",
    "folded-correction",
    "n21-feedback",
    "n21-orbit-feedback",
    "n21-orbit-rca",
    "patch-window",
    "coherence-window",
    "ripple",
    "rank-sector",
}
# Families that run on one pinned patch and carry its six physical qubits.
PATCH_FAMILIES = ("patch-window", "coherence-window")
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:+/-]*\Z")
_HEX_DIGEST = re.compile(r"[a-f0-9]{64}\Z")
_DESIGN_OPTIONS = (
    "shot_tiers",
    "replica_tiers",
    "optimizer_candidates",
    "model_shots",
    "precision",
    "alpha",
    "power",
    "simulation_alpha",
    "job_overhead_seconds",
    "classical_latency_us",
    "reserve_seconds",
    "max_total_execution_seconds",
)
_MAPPING_FIELDS = (
    "replica_cap",
    "measurement_delay_dt",
    "replaced_measurement_qubits",
    "shared_initial_layout",
    "extra_control",
    "measurement_seconds",
    "measurement_sites",
    "dt_seconds",
    "window_delay_dt",
    "echo_half_dt",
    "measure_dt",
    "window_dt",
    "readout_qubits",
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _identifier(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(_IDENTIFIER.fullmatch(value)), f"{label} needs a public identifier")
    _require(".." not in value.split("/"), f"{label} contains a parent path")
    return str(value)


def _number(value: Any, label: str, *, positive: bool = False) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be numeric")
    number = float(value)
    _require(math.isfinite(number), f"{label} must be finite")
    if positive:
        _require(number > 0, f"{label} must be positive")
    return number


def _count(value: Any, label: str) -> int:
    _require(type(value) is int and value > 0, f"{label} must be a positive integer")
    return int(value)


def _format_number(value: Any) -> str:
    return "n/a" if value is None else format(_number(value, "reported quantity"), ".12g")


def _portable_run_path(run_dir: Path) -> Path:
    """Use a checkout-relative destination when evidence comes from temporary storage."""
    repository = Path(__file__).resolve().parent.parent
    try:
        relative = run_dir.resolve().relative_to(repository)
    except ValueError:
        relative = Path("results/live") / run_dir.name
    _require(bool(relative.parts) and all(part not in (".", "..") for part in relative.parts), "invalid run location")
    for part in relative.parts:
        _identifier(part, "run path component")
    return relative


def _numeric_mapping(value: Any) -> Any:
    """Limit mapping output to public names and numeric calibration/placement data."""
    if isinstance(value, dict):
        return {_identifier(key, "mapping key"): _numeric_mapping(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_numeric_mapping(item) for item in value]
    if value is None:
        return None
    _number(value, "mapping value")
    return value


def _shot_allocation(record: dict[str, Any]) -> dict[str, int] | None:
    """Bind an opted-in allocation to every execution PUB and declared shot tier."""
    design = record["policy"]["design"]
    mode = design.get("shot_allocation", "uniform")
    _require(mode in ("uniform", "per-pub"), "unknown shot allocation mode")
    allocation = record.get("pub_shots")
    if mode == "uniform":
        _require(allocation is None, "uniform design carries a per-PUB shot allocation")
        return None
    _require(
        design["family"] == record["family_configuration"]["name"]
        and design["family"] in ("ripple", "rank-sector", *PATCH_FAMILIES)
        and design["optimize"] is True,
        "per-PUB allocation requires an optimized algebra or patch family",
    )
    names = [_identifier(pub["name"], "execution PUB") for pub in record["execution_pubs"]]
    _require(bool(names) and len(names) == len(set(names)), "execution PUB identities must be unique and complete")
    if not isinstance(allocation, dict):
        raise ValueError("per-PUB shot allocation must be a complete mapping")
    _require(
        set(allocation) == set(names),
        "per-PUB shot allocation differs from the complete execution-PUB manifest",
    )
    tiers = design["shot_tiers"]
    _require(isinstance(tiers, list) and bool(tiers), "shot tiers must contain positive counts")
    tiers = [_count(tier, "shot tier") for tier in tiers]
    _require(tiers == sorted(set(tiers)), "allocated shot tiers must be unique and increasing")
    result = {name: _count(allocation[name], "allocated PUB shots") for name in names}
    _require(set(result.values()) <= set(tiers), "allocated PUB shots exceed the declared tier domain")
    _require(
        _count(record["shots"], "recorded shots") == max(result.values()),
        "recorded shots differ from allocation maximum",
    )
    # The algebra families allocate static PUBs only; the patch families'
    # dynamic window PUBs take per-PUB tiers in their own jobs.
    _require(
        design["family"] in PATCH_FAMILIES or all(pub["kind"] == "static" for pub in record["execution_pubs"]),
        "per-PUB allocation requires static execution PUBs",
    )
    return result


def _reproduction_arguments(record: dict[str, Any], location: Path) -> list[str]:
    policy = record["policy"]
    design = policy["design"]
    family = _identifier(design["family"], "family")
    _require(family == record["family_configuration"]["name"], "policy and family configuration differ")
    _require(type(design["optimize"]) is bool, "optimize must be Boolean")
    _require(not policy["twirl"] and policy["dd"] is None, "matched families require the unmitigated policy")
    inventory = record["system_inventory"]
    _require(isinstance(inventory, dict) and bool(inventory), "the case needs the complete known backend inventory")
    backends = sorted(_identifier(name, "backend") for name in inventory)
    _require(
        {group["backend"] for group in record["groups"]} <= set(backends), "selected backend is absent from inventory"
    )
    _shot_allocation(record)
    arguments = ["--family", family]
    if "shot_allocation" in design:
        arguments.extend(["--shot-allocation", design["shot_allocation"]])
    objective = design.get("objective", "minimum_charge")
    _require(objective in ("minimum_charge", "precision_at_budget"), "unknown optimizer objective")
    if "objective" in design:
        arguments.extend(["--objective", objective])
    for scenario in design.get("cost_scenarios", []):
        scenario_name = _identifier(scenario["name"], "cost scenario")
        overhead = _number(scenario["job_overhead_seconds"], "scenario overhead")
        latency = _number(scenario["classical_latency_us"], "scenario latency")
        _require(overhead >= 0 and latency >= 0, "cost scenario values must be nonnegative")
        arguments.extend(["--cost-scenario", f"{scenario_name}:{overhead}:{latency}"])
    compute = policy.get("local_compute")
    if compute is not None:
        import local_compute

        local_compute.validate(compute)
        arguments.extend(
            [
                "--local-compute",
                compute["mode"],
                "--local-compute-method",
                compute["method"],
                "--simulation-threads",
                str(compute["threads"]),
                "--simulation-memory-mb",
                str(compute["memory_mb"]),
            ]
        )
    if design["optimize"]:
        arguments.append("--optimize")
    if design["family"] in PATCH_FAMILIES:
        declared = design.get("patch_qubits")
        _require(isinstance(declared, list), f"the {design['family']} family requires its patch qubits")
        patch = [qubit for qubit in declared if type(qubit) is int and qubit >= 0]
        _require(
            patch == declared and len(patch) == 6 and len(set(patch)) == 6,
            f"{design['family']} needs six distinct nonnegative qubits",
        )
        _require(
            patch == record["family_configuration"].get("patch_qubits"),
            "patch qubits differ between the design policy and the family configuration",
        )
        arguments.extend(["--patch-qubits", ",".join(str(qubit) for qubit in patch)])
    else:
        _require(design.get("patch_qubits") is None, "only the pinned-patch families carry patch qubits")
    arguments.extend(["--backends", ",".join(backends), "--shots", str(_count(record["shots"], "shots"))])
    for name in ("seeds", "max_pending", "min_remaining_seconds", "max_execution_seconds"):
        value = policy[name]
        _number(value, name)
        arguments.extend(["--" + name.replace("_", "-"), str(value)])
    for name in ("replica_floor", "max_replicas"):
        if policy[name] is not None:
            _number(policy[name], name, positive=True)
            arguments.extend(["--" + name.replace("_", "-"), str(policy[name])])
    for name in ("isolated_reference", "cross_group_buffer"):
        _require(type(policy[name]) is bool, f"{name} must be Boolean")
        arguments.append("--" + ("" if policy[name] else "no-") + name.replace("_", "-"))
    for name in _DESIGN_OPTIONS:
        value = design[name]
        if name in ("shot_tiers", "replica_tiers"):
            _require(isinstance(value, list) and bool(value), f"{name} must contain positive counts")
            argument = ",".join(str(_count(item, name)) for item in value)
        else:
            _number(value, name)
            argument = str(value)
        arguments.extend(["--" + name.replace("_", "-"), argument])
    arguments.extend(["--out", (Path("..") / location.parent).as_posix()])
    return arguments


def _command(arguments: list[str]) -> str:
    command = [
        "cd gororoba_quantum",
        'PYTHON="${PYTHON:-$(command -v python3)}"',
        '"$PYTHON" live_run.py \\',
    ]
    grouped: list[str] = []
    for token in arguments:
        if token.startswith("--"):
            grouped.append(shlex.quote(token))
        else:
            grouped[-1] += " " + shlex.quote(token)
    for index, option in enumerate(grouped):
        suffix = " \\" if index + 1 < len(grouped) else ""
        command.append("  " + option + suffix)
    return "\n".join(command)


def _validate_costs(candidate: dict[str, Any], record: dict[str, Any]) -> None:
    """Cross-check the selected cost ledger against its declared circuit workload."""
    policy = record["policy"]
    uniform_shots = _count(record["shots"], "recorded shots")
    allocation = _shot_allocation(record)
    pub_names: list[str] = []
    job_names: list[str] = []
    for job in candidate["jobs"]:
        job_names.append(_identifier(job["name"], "job"))
        _require(bool(job["pubs"]), "selected job has no PUBs")
        overhead = _number(job["overhead_seconds"], "job overhead")
        _require(overhead >= 0, "job overhead must be nonnegative")
        _require(overhead == policy["design"]["job_overhead_seconds"], "job overhead differs from the design policy")
        executions = []
        counts = set()
        for pub in job["pubs"]:
            name = _identifier(pub["name"], "PUB")
            pub_names.append(name)
            if allocation is not None:
                _require(name in allocation, "costed PUB is absent from the shot allocation")
            expected_shots = allocation[name] if allocation is not None else uniform_shots
            counts.add(_count(pub["shots"], "PUB shots"))
            if allocation is not None:
                stages = pub.get("classical_stage_count")
                # Only a dynamic job of a patch family carries dispatch stages.
                dynamic_allowed = policy["design"]["family"] in PATCH_FAMILIES and "/dynamic/" in job["name"]
                _require(
                    type(stages) is int and (stages == 0 or (dynamic_allowed and stages > 0)),
                    "static allocated PUB costs require zero classical stages",
                )
                _require(
                    pub["classical_latency_seconds"] == 0 or (dynamic_allowed and stages > 0),
                    "static allocated PUB cost includes classical latency",
                )
                _require(
                    math.isclose(
                        pub["classical_latency_seconds"],
                        stages * policy["design"]["classical_latency_us"] * 1e-6,
                        rel_tol=1e-12,
                        abs_tol=1e-15,
                    ),
                    "allocated PUB latency differs from its stages at the declared classical latency",
                )
            _require(_count(pub["shots"], "PUB shots") == expected_shots, "PUB shots differ from the saved plan")
            durations = [
                _number(pub[key], key)
                for key in (
                    "scheduled_seconds",
                    "repetition_delay_seconds",
                    "reset_seconds",
                    "classical_latency_seconds",
                )
            ]
            _require(all(value >= 0 for value in durations), "PUB duration components must be nonnegative")
            expected = expected_shots * math.fsum(durations)
            _require(expected > 0, "PUB repetition duration must be positive")
            _require(
                math.isclose(expected, _number(pub["estimated_execution_seconds"], "PUB charge"), rel_tol=1e-12),
                "PUB estimated execution disagrees with its shots and durations",
            )
            executions.append(expected)
        _require(len(counts) == 1, "each Runtime job must use one PUB shot count")
        charge = _number(job["estimated_charge_seconds"], "job charge", positive=True)
        _require(math.isclose(charge, math.fsum([overhead, *executions]), rel_tol=1e-12), "job charge sum disagrees")
        _require(charge <= job["max_execution_seconds"], "estimated job charge exceeds its service ceiling")
        _require(job["max_execution_seconds"] == policy["max_execution_seconds"], "job ceiling differs from policy")
    _require(len(job_names) == len(set(job_names)), "selected jobs must have distinct names")
    _require(len(pub_names) == len(set(pub_names)), "selected PUBs must have distinct names")
    _require(
        sorted(pub_names) == sorted(pub["name"] for pub in record["execution_pubs"]),
        "costed PUBs differ from the execution-PUB manifest",
    )
    _require(
        math.isclose(
            candidate["estimated_charge_seconds"],
            math.fsum(job["estimated_charge_seconds"] for job in candidate["jobs"]),
            rel_tol=1e-12,
        ),
        "candidate charge differs from its job sum",
    )


def _validate_allocated_jobs(candidate: dict[str, Any], record: dict[str, Any]) -> None:
    """Match every tier job to its reserved ceiling and ordered PUB membership."""
    budget_jobs = record["budget_plan"].get("jobs")
    _require(
        isinstance(budget_jobs, list) and len(budget_jobs) == len(candidate["jobs"]),
        "allocated budget must reserve every selected job",
    )
    manifests = {pub["name"]: pub for pub in record["execution_pubs"]}
    next_indices: dict[tuple[str, str], int] = {}
    previous_tiers: dict[tuple[str, str], int] = {}
    coordinates: list[tuple[str, str, int]] = []
    tier_rows: dict[tuple[str, str, int], list[str]] = {}
    selected_backends = {group["backend"] for group in record["groups"]}
    for reserved, job in zip(budget_jobs, candidate["jobs"], strict=True):
        backend = _identifier(reserved["backend"], "budget backend")
        kind = _identifier(reserved["kind"], "budget kind")
        index = _count(reserved["batch_index"], "budget batch index")
        key = (backend, kind)
        expected_index = next_indices.get(key, 1)
        _require(index == expected_index, "allocated budget job identity differs from the canonical batch sequence")
        next_indices[key] = expected_index + 1
        coordinates.append((backend, kind, index))
        _require(
            backend in selected_backends and backend in record["system_inventory"],
            "allocated budget backend is outside the selected groups or inventory",
        )
        _require(job["name"] == f"{backend}/{kind}/{index}", "allocated budget job identity differs from selection")
        names = [pub["name"] for pub in job["pubs"]]
        _require(reserved.get("pub_names") == names, "allocated budget PUB membership or order differs from selection")
        _require(_count(reserved["pubs"], "budget PUB count") == len(names), "allocated budget PUB count differs")
        _require(
            all(manifests[name]["backend"] == backend and manifests[name]["kind"] == kind for name in names),
            "allocated budget backend or kind differs from the execution manifest",
        )
        shots = _count(reserved["shots"], "reserved job shots")
        _require(shots == job["pubs"][0]["shots"], "allocated budget shots differ from selection")
        _require(shots >= previous_tiers.get(key, 0), "allocated jobs differ from ascending shot-tier order")
        previous_tiers[key] = shots
        tier_rows.setdefault((backend, kind, shots), []).extend(names)
        _require(
            _number(reserved["ceiling_seconds"], "reserved job ceiling", positive=True) == job["max_execution_seconds"],
            "allocated budget ceiling differs from selection",
        )
    _require(coordinates == sorted(coordinates), "allocated jobs differ from canonical backend order")
    for (backend, kind, shots), names in tier_rows.items():
        expected = [
            pub["name"]
            for pub in record["execution_pubs"]
            if pub["backend"] == backend and pub["kind"] == kind and record["pub_shots"][pub["name"]] == shots
        ]
        _require(names == expected, "allocated tier PUB order differs from the execution manifest")


def _validate_allocated_scenarios(candidate: dict[str, Any], record: dict[str, Any]) -> None:
    """Keep the complete allocated workload fixed under each cost assumption."""
    design = record["policy"]["design"]
    assumptions = design.get("cost_scenarios", [])
    scenarios = candidate.get("cost_scenarios", [])
    by_name = {_identifier(row["name"], "cost scenario"): row for row in assumptions}
    _require(
        len(by_name) == len(assumptions) == len(scenarios) and {row["name"] for row in scenarios} == set(by_name),
        "allocated cost scenarios differ from the declared policy",
    )
    charges = [candidate["estimated_charge_seconds"]]
    for scenario in scenarios:
        assumption = by_name[scenario["name"]]
        _require(scenario["feasible"] is True, "allocated cost scenario fails admission")
        _require(len(scenario["jobs"]) == len(candidate["jobs"]), "allocated cost scenario changed the job count")
        scenario_record = copy.deepcopy(record)
        scenario_record["policy"]["design"]["job_overhead_seconds"] = assumption["job_overhead_seconds"]
        scenario_candidate = dict(
            candidate, jobs=scenario["jobs"], estimated_charge_seconds=scenario["estimated_charge_seconds"]
        )
        _validate_costs(scenario_candidate, scenario_record)
        _validate_allocated_jobs(scenario_candidate, scenario_record)
        for nominal_job, scenario_job in zip(candidate["jobs"], scenario["jobs"], strict=True):
            _require(len(nominal_job["pubs"]) == len(scenario_job["pubs"]), "allocated scenario changed PUB membership")
            for nominal, modified in zip(nominal_job["pubs"], scenario_job["pubs"], strict=True):
                _require(
                    all(
                        nominal[key] == modified[key]
                        for key in (
                            "name",
                            "shots",
                            "scheduled_seconds",
                            "repetition_delay_seconds",
                            "reset_seconds",
                            "classical_stage_count",
                            "classical_latency_seconds",
                        )
                    ),
                    "allocated cost scenario changed the compiled workload",
                )
        charges.append(scenario["estimated_charge_seconds"])
    _require(
        math.isclose(_number(candidate["worst_case_charge_seconds"], "scenario envelope"), max(charges), rel_tol=1e-12),
        "allocated scenario envelope disagrees with its ledger",
    )


@cache
def _correction_power() -> dict[str, Any]:
    from correction_statistics import planning_certificate

    return planning_certificate(8192, alpha=0.05, minimum_gain=0.01, assumed_gain=0.04, required_joint_power=0.8)


def _correction_case_inputs(record: dict[str, Any], candidate: dict[str, Any], circuits: list[QuantumCircuit]) -> None:
    """Independently check the fixed pilot protocol and its archived physical pairs."""
    from correction_circuits import validate_bound_correction_pair
    from correction_statistics import MEMBERS

    configuration = record["family_configuration"]
    policy = record["policy"]
    design = policy["design"]
    _require(record["shots"] == configuration.get("shots_per_pub") == 8192, "correction case requires 8192 shots")
    _require(design["shot_tiers"] == [8192] and design["replica_tiers"] == [1], "correction tiers changed")
    _require(design["alpha"] == 0.05 and design["power"] == 0.8, "correction statistical policy changed")
    _require(configuration.get("member_order") == list(MEMBERS), "correction arm order changed")
    _require(configuration.get("replica_cap") == 1, "correction case requires one replica")
    _require(configuration.get("execution_row_count") == 4, "correction case requires four execution rows")
    _require(policy["max_replicas"] == 1 and policy["isolated_reference"] is False, "correction placement changed")
    _require(
        policy["max_execution_seconds"] == design["max_total_execution_seconds"] == 30,
        "correction pilot requires the reviewed 30-second execution ceiling and cap",
    )
    _require(policy["twirl"] is False and policy["dd"] is None, "correction case requires unmitigated execution")
    _require(
        configuration.get("native_mock_required") is False
        and configuration.get("classical_dispatch_retained") is True
        and configuration.get("dispatch_removal_test") is False,
        "correction schedule or dispatch boundary changed",
    )
    _require(
        configuration.get("decision_contract")
        == {
            "method": "four_one_sided_clopper_pearson_bounds",
            "family_alpha": 0.05,
            "per_bound_tail": 0.0125,
            "minimum_gain": 0.01,
            "require_both_labels": True,
            "count_semantics": "raw integer counts; y=first_bit+2*terminal_bit",
            "postexecution_schedule_gate": True,
        },
        "correction CP decision or post-execution schedule gate changed",
    )
    _require(record["observable_contracts"] == candidate["observables"] == [], "correction uses dedicated CP inference")
    _require(
        len(candidate["jobs"]) == 1 and len(candidate["jobs"][0]["pubs"]) == 4, "correction requires one four-PUB job"
    )
    _require(len(record["groups"]) == 1, "correction requires one matched group")
    group = record["groups"][0]
    _require(len(group["replicas"]) == 1, "correction group replica count changed")
    _require([member["name"] for member in group["members"]] == list(MEMBERS), "correction members changed")
    for member, phase_label in zip(group["members"], (1, 1, 3, 3), strict=True):
        _require(
            member["ideal"] == [float(outcome == phase_label) for outcome in range(4)], "correction ideal law changed"
        )
    pubs = record["execution_pubs"]
    _require(len(pubs) == len(circuits) == 4, "correction archive requires four PUBs")
    for pub, member in zip(pubs, MEMBERS, strict=True):
        _require(pub["kind"] == "dynamic" and pub["backend"] == group["backend"], "correction job kind/backend changed")
        _require(len(pub["components"]) == 1, "correction PUB contains extra components")
        component = pub["components"][0]
        _require(
            component["member"] == member
            and component["group"] == group["group"]
            and component["reference"] is False
            and len(component["registers_by_replica"]) == 1
            and bool(component["registers_by_replica"][0]),
            "correction PUB member, reference, or replica mapping changed",
        )
        _require(
            pub["feed_forward_operation_count"] == pub["sequential_stage_count"] == pub["parallel_stream_count"] == 1,
            "correction PUB must retain one classical dispatch",
        )
    actual_pairs = {
        "1": validate_bound_correction_pair(circuits[0], circuits[1], 1),
        "3": validate_bound_correction_pair(circuits[3], circuits[2], 3),
    }
    _require(
        configuration.get("circuit_pairs") == actual_pairs, "correction archive differs from validated pair reports"
    )
    templates = configuration.get("template_pairs")
    _require(isinstance(templates, dict) and set(templates) == {"1", "3"}, "common-template pair proofs are missing")
    for label in ("1", "3"):
        template = templates[label]
        _require(
            template.get("phase_label") == int(label)
            and template.get("validation") == "exact_common_template_history_and_ideal_law"
            and template.get("protected_history_equal") is True
            and template.get("classical_dispatch_retained") is True,
            "common-template pair proof is unqualified",
        )
        for key in ("prefix_sha256", "suffix_sha256", "feedback_history_sha256", "independent_history_sha256"):
            _require(
                isinstance(template.get(key), str) and bool(_HEX_DIGEST.fullmatch(template[key])),
                "common-template history digest is missing",
            )
    _require(configuration.get("hypothetical_power") == _correction_power(), "hypothetical power certificate changed")
    _require(_correction_power()["hypothetical_power_qualified"] is True, "hypothetical planning power failed")
    expected_backends = {"ibm_fez", "ibm_kingston", "ibm_marrakesh"}
    _require(set(record["system_inventory"]) == expected_backends, "correction search requires all three backends")
    search = configuration.get("backend_search")
    _require(isinstance(search, list) and len(search) == 3, "complete correction backend search is missing")
    _require({row["backend"] for row in search} == expected_backends, "correction search backend set changed")
    for row in search:
        name = row["backend"]
        snapshot = record["system_inventory"][name]
        _identifier(snapshot["fetched_at"], "backend refresh time")
        _require(row["calibration"] == snapshot["calibration"], "correction search calibration changed")
        _require(type(row["eligible"]) is bool, "backend eligibility must be Boolean")
        if row["eligible"]:
            _require(
                snapshot["eligibility"] == "eligible" and row["rejection_reason"] is None,
                "family eligibility requires an eligible backend snapshot",
            )
        else:
            _require(
                isinstance(row["rejection_reason"], str)
                and bool(row["rejection_reason"].strip())
                and row["admitted_candidate_count"] == 0,
                "excluded backend requires an explicit reason and zero admitted candidates",
            )
        for key in ("compiled_candidate_count", "admitted_candidate_count"):
            _require(type(row[key]) is int and row[key] >= 0, "backend candidate counts must be nonnegative integers")
        _require(row["admitted_candidate_count"] <= row["compiled_candidate_count"], "backend admission count changed")
        if name == group["backend"]:
            _require(
                row["eligible"] and row["admitted_candidate_count"] > 0, "selected backend lacks an admitted candidate"
            )
            _require(
                row["calibration"] == group["calibration"] == record["backends"][name]["calibration"],
                "selected backend calibration differs from its group",
            )
    _correction_model_inputs(record)
    _correction_cost_inputs(record, candidate)


def _correction_model_inputs(record: dict[str, Any]) -> None:
    from correction_statistics import MEMBERS

    prediction = record["family_configuration"]["model_prediction"]
    _require(
        prediction["evidence_class"]
        == "finite-shot calibration noise simulation; controller/instrument errors incomplete"
        and prediction["prediction_frozen_before_hardware"] is True,
        "correction noise-model evidence class or freeze changed",
    )
    _require(prediction["shots_per_member"] == record["policy"]["design"]["model_shots"], "model shot count changed")
    _count(prediction["shots_per_member"], "model shots")
    _require(prediction["seed"] == record["seed_simulator"], "model seed changed")
    _require(set(prediction["members"]) == set(MEMBERS), "model predictions require all four members")
    successes = {}
    for index, name in enumerate(MEMBERS):
        member = prediction["members"][name]
        values = member["probabilities"]
        _require(isinstance(values, list) and len(values) == 4, "model requires four labeled probabilities")
        probabilities = [_number(value, "model probability") for value in values]
        _require(
            all(0 <= value <= 1 for value in probabilities)
            and math.isclose(math.fsum(probabilities), 1.0, rel_tol=0, abs_tol=1e-12),
            "invalid model law",
        )
        success = math.fsum(probabilities[:2] if index < 2 else probabilities[2:])
        _require(
            math.isclose(
                success, _number(member["terminal_success_probability"], "model success"), rel_tol=0, abs_tol=1e-12
            ),
            "model terminal success disagrees with its labeled law",
        )
        successes[name] = success
    gains = prediction["gain_known_minus_measured"]
    _require(set(gains) == {"1", "3"}, "model gains require both labels")
    for label, known, measured in (("1", MEMBERS[1], MEMBERS[0]), ("3", MEMBERS[2], MEMBERS[3])):
        _require(
            math.isclose(
                _number(gains[label], "model gain"), successes[known] - successes[measured], rel_tol=0, abs_tol=1e-12
            ),
            "model gain disagrees with its member predictions",
        )


def _correction_cost_inputs(record: dict[str, Any], candidate: dict[str, Any]) -> None:
    """Require explicit sensitivity ledgers without interpreting assumptions as bounds."""
    design = record["policy"]["design"]
    assumptions = design.get("cost_scenarios", [])
    scenarios = candidate.get("cost_scenarios", [])
    _require(bool(assumptions) and len(assumptions) == len(scenarios), "correction cost scenarios are missing")
    by_name = {row["name"]: row for row in assumptions}
    _require(
        len(by_name) == len(assumptions) and {row["name"] for row in scenarios} == set(by_name),
        "correction cost scenarios differ from policy",
    )
    nominal = candidate["jobs"][0]["pubs"]
    for pub in nominal:
        _require(pub["classical_stage_count"] == 1, "correction cost lost its retained dispatch")
        _require(
            math.isclose(pub["classical_latency_seconds"], design["classical_latency_us"] * 1e-6, rel_tol=1e-12),
            "correction nominal latency differs from policy",
        )
    charges = [candidate["estimated_charge_seconds"]]
    for scenario in scenarios:
        assumption = by_name[scenario["name"]]
        _require(scenario["feasible"] is True and len(scenario["jobs"]) == 1, "correction cost scenario is unqualified")
        _require(
            assumption["job_overhead_seconds"] >= design["job_overhead_seconds"]
            and assumption["classical_latency_us"] >= design["classical_latency_us"],
            "correction scenarios must include conservative overhead and latency",
        )
        scenario_record = copy.deepcopy(record)
        scenario_record["policy"]["design"]["job_overhead_seconds"] = assumption["job_overhead_seconds"]
        scenario_candidate = dict(
            candidate, jobs=scenario["jobs"], estimated_charge_seconds=scenario["estimated_charge_seconds"]
        )
        _validate_costs(scenario_candidate, scenario_record)
        _require(len(scenario["jobs"][0]["pubs"]) == 4, "correction scenario requires four PUBs")
        for base, modified in zip(nominal, scenario["jobs"][0]["pubs"], strict=True):
            _require(
                all(
                    base[key] == modified[key]
                    for key in (
                        "name",
                        "shots",
                        "scheduled_seconds",
                        "repetition_delay_seconds",
                        "reset_seconds",
                        "classical_stage_count",
                    )
                ),
                "correction scenario changed the compiled workload",
            )
            _require(
                math.isclose(
                    modified["classical_latency_seconds"], assumption["classical_latency_us"] * 1e-6, rel_tol=1e-12
                ),
                "correction scenario latency differs from policy",
            )
        charges.append(scenario["estimated_charge_seconds"])
    _require(
        math.isclose(candidate["worst_case_charge_seconds"], max(charges), rel_tol=1e-12),
        "correction scenario envelope disagrees with its ledger",
    )


def _case_inputs(run_dir: Path, record: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    record_bytes = (run_dir / "record.json").read_bytes()
    retained = json.loads(record_bytes)
    _require(
        retained == json.loads(json.dumps(record, default=str)), "supplied record differs from retained record.json"
    )
    selected_name = record["optimization"]["selected"]
    candidates = [item for item in record["optimization"]["candidates"] if item["name"] == selected_name]
    _require(len(candidates) == 1 and candidates[0]["feasible"] is True, "selected candidate must be uniquely feasible")
    candidate = candidates[0]
    _identifier(selected_name, "selected candidate")
    _number(candidate["estimated_charge_seconds"], "estimated total charge", positive=True)
    ceiling = _number(candidate["total_execution_ceiling_seconds"], "summed execution ceilings", positive=True)
    _require(bool(candidate["jobs"]), "selected candidate has no jobs")
    _require(
        math.isclose(
            sum(_number(job["max_execution_seconds"], "job ceiling", positive=True) for job in candidate["jobs"]),
            ceiling,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        "selected job ceilings differ from their aggregate",
    )
    budget = record["budget_plan"]
    _require(
        math.isclose(ceiling, _number(budget["combined_ceiling_seconds"], "budget ceiling"), rel_tol=1e-12),
        "selected candidate and budget ledger disagree on summed ceilings",
    )
    _require(
        ceiling <= _number(budget["max_total_execution_seconds"], "invocation ceiling", positive=True),
        "summed ceilings exceed the invocation ceiling",
    )
    reserve = _number(budget["reserve_seconds"], "quota reserve")
    _require(reserve >= 0, "quota reserve must be nonnegative")
    for key in ("max_total_execution_seconds", "reserve_seconds"):
        _require(budget[key] == record["policy"]["design"][key], f"budget {key} differs from the design policy")
    if budget["remaining_seconds"] is not None:
        _require(
            ceiling + reserve <= _number(budget["remaining_seconds"], "remaining quota"),
            "summed ceilings consume the declared quota reserve",
        )
    _validate_costs(candidate, record)
    if _shot_allocation(record) is not None:
        _validate_allocated_jobs(candidate, record)
        _validate_allocated_scenarios(candidate, record)
    if record["family_configuration"]["name"] != "folded-correction":
        _require(
            bool(candidate["observables"]) and all(item["feasible"] is True for item in candidate["observables"]),
            "selected observables must all pass admission",
        )
    contract_names = [item["name"] for item in record["observable_contracts"]]
    _require(len(contract_names) == len(set(contract_names)), "endpoint contracts must have unique names")
    _require(
        contract_names == [item["name"] for item in candidate["observables"]],
        "endpoint contracts differ from selection",
    )
    archive_bytes = (run_dir / "isa.qpy").read_bytes()
    circuits = qpy.load(io.BytesIO(archive_bytes))
    _require(
        [circuit.name for circuit in circuits] == [pub["name"] for pub in record["execution_pubs"]],
        "QPY circuit names differ from the ordered execution-PUB manifest",
    )
    _require(bool(circuits), "the QPY archive has no execution circuits")
    if record["family_configuration"]["name"] == "folded-correction":
        _correction_case_inputs(record, candidate, list(circuits))
    return candidate, hashlib.sha256(record_bytes).hexdigest(), hashlib.sha256(archive_bytes).hexdigest()


def _correction_endpoints(record: dict[str, Any]) -> list[str]:
    """Keep exact-count inference separate from model predictions and planning power."""
    configuration = record["family_configuration"]
    certificate = configuration["hypothetical_power"]
    prediction = configuration["model_prediction"]
    lines = [
        "## Preregistered endpoints",
        "",
        "The primary estimand is unconditional terminal-bit success, using every raw shot. "
        "Outcome labels are y = first_bit + 2*terminal_bit. Success is terminal_bit=0 for s1 "
        "and terminal_bit=1 for s3. Each F and U arm must supply exactly 8192 integer-count "
        "observations; missing members or shots withhold the scientific decision.",
        "",
        "Four one-sided Clopper-Pearson bounds allocate family alpha=0.05 as 0.0125 per bound. "
        "Select U only when both labels satisfy `lower_U - upper_F > 0.01` and the post-execution "
        "circuit, schedule, count, and calibration checks qualify. Failure retains F and establishes "
        "neither equivalence nor a causal mechanism. Recorded B=0/B=1 strata remain descriptive; "
        "the decision uses zero conditional postselection.",
        "",
        "The observation bounds allow arbitrary dependence between PUBs through a union bound. "
        "Independent stationary Bernoulli repetitions within each PUB remain an assumption. "
        "Exact-binomial describes the interval construction; SciPy evaluates quantiles and tails "
        "in floating point without interval-certified rounding.",
        "",
        "### Hypothetical sensitivity scenario",
        "",
        "The fixed reference F rates are 6433/8192 for s1 and 6241/8192 for s3. "
        "A hypothetical U improvement of 0.04 gives the joint-power lower bound "
        f"{_format_number(certificate['joint_power_union_lower_bound'])} against the required 0.8. "
        "The finite-binomial sum adds independence between F and U counts within each label; "
        "the union bound across labels requires no independence between labels. The reference "
        "rates are scenario constants, with no stationarity or transfer claim to fresh calibration. "
        "Hypothetical power supplies neither a current model prediction nor measured advantage.",
        "",
        "### Frozen calibration-model predictions",
        "",
        f"The selected layout uses {_count(prediction['shots_per_member'], 'model shots')} finite "
        f"simulation shots per member and seed {_count(prediction['seed'], 'model seed')}. "
        "The four labeled distributions and gains are frozen before hardware acquisition. "
        "Controller and instrument errors remain incomplete in the model; sampling error and "
        "hardware-model discrepancy remain separate from the hypothetical sensitivity calculation.",
        "",
        "| Member | Labeled modeled probabilities | Terminal success |",
        "|---|---|---:|",
    ]
    for name in configuration["member_order"]:
        member = prediction["members"][name]
        lines.append(
            f"| {_identifier(name, 'model member')} | `{json.dumps(member['probabilities'])}` | "
            f"{_format_number(member['terminal_success_probability'])} |"
        )
    lines.extend(["", "| Label | Modeled U minus F |", "|---|---:|"])
    for label in ("1", "3"):
        lines.append(f"| s{label} | {_format_number(prediction['gain_known_minus_measured'][label])} |")
    lines.extend(
        ["", "The modeled gains may be small or negative; the hypothetical 0.04 gain stays separately labeled.", ""]
    )
    return lines


def _correction_selection(record: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    configuration = record["family_configuration"]
    _require(
        record["optimization"].get("objective") == "worst_arm_calibrated_quality_then_charge",
        "correction selection objective changed",
    )
    proxy = candidate["proxy_metadata"]
    quality = _number(proxy["worst_arm_quality"], "worst-arm calibration quality", positive=True)
    _require(
        quality == min(_number(score, "member calibration quality", positive=True) for score in proxy["member_scores"]),
        "worst-arm quality disagrees with its arm scores",
    )
    _require(len(proxy["member_scores"]) == 4, "correction selection requires four arm scores")
    lines = [
        "## Selection objective and sensitivity assumptions",
        "",
        "The dedicated correction objective maximizes the weakest of four calibrated arm scores "
        "(ESP times exp(-T*sum(1/T2))). Ties use lower Target-plus-repetition charge with zero "
        "added controller latency, then total CZ count, seed, and backend name. "
        "The generic objective flag remains recorded for CLI replay; the dedicated family ranker "
        "defines selection. Calibration proxies establish neither measured fidelity nor global optimality.",
        "",
        f"The selected candidate's worst-arm quality proxy is {quality:.12g}. "
        "The finite search includes fresh snapshots of Fez, Kingston, and Marrakesh; every "
        "recorded rejection stays in the retained search trace.",
        "",
        "| Backend | Calibration | Family eligible | Compiled candidates | Admitted candidates |",
        "|---|---|---|---:|---:|",
    ]
    for row in configuration["backend_search"]:
        lines.append(
            f"| {_identifier(row['backend'], 'backend')} | {_identifier(row['calibration'], 'calibration')} | "
            f"{str(row['eligible']).lower()} | {row['compiled_candidate_count']} | {row['admitted_candidate_count']} |"
        )
    lines.append("")
    return lines


def _endpoints(record: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    if record["family_configuration"]["name"] == "folded-correction":
        return _correction_endpoints(record)
    lines = [
        "## Preregistered endpoints",
        "",
        "Every endpoint uses raw measured outcomes, archived score coefficients, and the planner's "
        "PUB grouping. Two-sided intervals report measurement precision.",
        "",
    ]
    directional = any(endpoint["minimum_effect"] is not None for endpoint in candidate["observables"])
    lines.extend(
        [
            "Directional endpoints also use the planner's one-sided detection radius "
            "for the preregistered collection test."
            if directional
            else "The saved endpoints preregister precision intervals.",
            "",
        ]
    )
    contracts = {contract["name"]: contract for contract in record["observable_contracts"]}
    members = {member["name"]: member for group in record["groups"] for member in group["members"]}
    for endpoint in candidate["observables"]:
        name = _identifier(endpoint["name"], "endpoint")
        contract = contracts[name]
        lines.extend([f"### {name}", "", "Score terms (each member averages its recorded replicas):", ""])
        for term in contract["terms"]:
            member = _identifier(term["member"], "observable member")
            _require(member in members, "observable member is absent from the execution groups")
            _require(term["sign"] in (-1, 1), "observable sign must be -1 or +1")
            coefficients = [_number(value, "score coefficient") for value in term["values"]]
            _require(
                len(coefficients) == len(members[member]["ideal"]), "score labels differ from the member ideal law"
            )
            lines.append(f"- `{member}`: sign {term['sign']:+d}, labeled score vector `{json.dumps(coefficients)}`.")
        lines.extend(
            [
                "",
                f"The noise model predicts {_format_number(endpoint['predicted_value'])}; "
                "the simultaneous finite-simulation allowance is "
                f"+/-{_format_number(endpoint['simulation_error_radius'])}. "
                f"The lower modeled value is {_format_number(endpoint['modeled_value_lower_bound'])}.",
                "",
                f"At alpha {_format_number(endpoint['alpha'])}, the two-sided confidence half-width is "
                f"{_format_number(endpoint['confidence_half_width'])}; requested precision is "
                f"{_format_number(endpoint['precision_half_width'])}.",
            ]
        )
        if endpoint["minimum_effect"] is not None:
            threshold = _number(endpoint["null_value"], "null value") + _number(
                endpoint["detection_radius"], "detection radius"
            )
            lines.extend(
                [
                    "",
                    f"Reject the directional null only when the measured score exceeds {threshold:.12g} "
                    f"(null {_format_number(endpoint['null_value'])} plus one-sided radius "
                    f"{_format_number(endpoint['detection_radius'])}). The admitted alternative effect is "
                    f"{_format_number(endpoint['effect_used_for_power'])}, with conditional target power "
                    f"{_format_number(endpoint['power'])} and lower-tail radius "
                    f"{_format_number(endpoint['power_radius'])}. "
                    f"The requested minimum effect is {_format_number(endpoint['minimum_effect'])}.",
                ]
            )
            if endpoint["minimum_effect"] == 0:
                lines.extend(
                    [
                        "",
                        "Zero requested minimum effect selects the positive modeled contrast after the "
                        "simulation allowance. The power statement concerns that reported alternative, "
                        "rather than every arbitrarily small effect.",
                    ]
                )
        if endpoint.get("covariance_assumptions"):
            lines.extend(
                [
                    "",
                    "Additional covariance upper-bound assumptions appear in the selected endpoint's "
                    "`covariance_assumptions` in record.json and form part of the conditional guarantee.",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "The search-wide simulation error probability is "
            f"{_format_number(record['optimization']['simulation_alpha'])} "
            f"across {record['optimization']['simulation_comparisons']} scored finite-shot marginals. "
            "Hoeffding/union bounds allow arbitrary same-shot replica dependence. Independent stationary "
            "repetitions remain an assumption. Hardware-model discrepancy remains unquantified.",
            "",
        ]
    )
    if directional:
        lines.extend(
            [
                "Power admission is conditional on the supplied outcome model and reported alternative effect.",
                "",
            ]
        )
    return lines


def _scientific_case(family: str, record: dict[str, Any]) -> list[str]:
    if family == "folded-correction":
        return [
            "## Scientific question and interpretation",
            "",
            "The pilot compares measured-bit correction F with recorded-bit-independent correction U "
            "for the known odd eigenstate labels s1 and s3. One routed symbolic template produces "
            "four PUBs in order F1/U1/U3/F3, one replica, one dynamic job, and 8192 shots per PUB. "
            "Every arm retains the classical dispatch, first measurement, reset, physical history, "
            "and terminal readout. U applies -pi/2 in both dispatch branches; F applies -pi/2 only "
            "when the recorded first bit equals 1. The archived circuit pair proof permits only "
            "the false-branch phase and associated global-phase difference.",
            "",
            "The experiment tests dependence of the correction on the recorded first bit for "
            "supplied labels. Classical dispatch removal, general unknown-eigenstate QPE, "
            "and unique attribution to a controller or readout mechanism remain outside its scope. "
            "The fixed arm order can retain time and drift confounds.",
            "",
            "Fresh Target/properties supply placement and conditional noise predictions. "
            "A future hardware acquisition measures the terminal-success contrast and model residual. "
            "Raw shot order, all classical registers, actual returned schedules, calibration windows, "
            "and completed usage must be retained before the scientific decision.",
            "",
        ]
    if family in ("ripple", "rank-sector"):
        mechanism = (
            "The ripple family measures finite four-qubit associator prefixes and the complete signed "
            "sedenion box-kite phase atlas. The walk classes exchange two physical lanes under matched "
            "companion activity. Each edge's eight phases share one routed template; edge blocks rotate "
            "between atlas lanes. Isolated representative endpoints compare a fixed witness and mapping "
            "under changed neighboring activity. Computational-basis counts measure probabilities; "
            "long ideal recurrences and complex amplitudes remain outside the hardware claim."
            if family == "ripple"
            else "The rank-sector family measures the selector-success norm of each four-dimensional "
            "sector of the specified dimension-32 multiplication path. Two data and two selector qubits "
            "implement each sector with coefficient-dependent LCU normalization. Fixed probe and "
            "parameter bindings share one routed template per sector. Persistent-kernel, exceptional-point "
            "and bright probes test bounded norm predictions. A finite noisy frequency cannot certify "
            "an exact rank, an exact zero, or the topology of the full zero-divisor space."
        )
        return [
            "## Scientific question and interpretation",
            "",
            mechanism,
            "",
            "The family retains every declared scientific member and explicit packed/isolated row. "
            "Each lane has one physical placement, and simultaneous lanes share a shot index. "
            "The execution PUB manifests in record.json bind the exact condition, lane, registers, "
            "and neighboring workload. Comparisons across different physical patches retain patch "
            "and routing confounds unless a matched crossover is explicitly recorded.",
            "",
            "Calibration-based simulation supplies conditional gate/readout predictions and statistical "
            "admission. Physical crosstalk, common disturbances, initialization, drift and scheduler "
            "effects require the future hardware observations. The simultaneous intervals allow arbitrary "
            "within-shot dependence; independent stationary repetitions remain an assumption. "
            "Packing-control intervals measure the observed distortion for their stated representatives, "
            "rather than certifying every possible packed edge or condition.",
            "",
            "Raw outcomes and joint shot order, calibration windows, executed schedules, and final "
            "charged usage must be retained. Model residuals and uncertainty remain visible in measured "
            "visualizations. The family is independently admitted from the folded-QPE and N21 cases.",
            "",
        ]
    if family == "coherence-window":
        configuration = record["family_configuration"]
        roles = configuration["patch_roles"]
        patch = ", ".join(f"{role} {qubit}" for role, qubit in zip(roles, configuration["patch_qubits"], strict=True))
        backends = ", ".join(sorted({_identifier(group["backend"], "backend") for group in record["groups"]}))
        window = _count(configuration["window_dt"], "window_dt")
        dt_seconds = _number(configuration["dt_seconds"], "dt_seconds", positive=True)
        readout = configuration["readout_qubits"]
        _require(
            isinstance(readout, dict)
            and set(readout) == {"b0", "read_a", "read_b", "sector"}
            and all(type(qubit) is int and qubit >= 0 for qubit in readout.values()),
            "coherence-window needs the executed readout qubit of b0, read_a, read_b and sector",
        )
        reads = ", ".join(f"{label} from qubit {readout[label]}" for label in ("b0", "read_a", "read_b", "sector"))
        alias_khz = 1e-3 / (2 * window * dt_seconds)
        precision = _number(record["policy"]["design"]["precision"], "precision", positive=True)
        return [
            "## Scientific question and interpretation",
            "",
            f"The coherence-window family measures, on the pinned initial layout {patch} on {backends}, "
            "the work coherence the first N=21 orbit round leaves between work_a and work_b, signed by the "
            "control's first bit b0. In each branch the work pair holds |10> + (-1)^b0 e^{i phi} |01>, so "
            "rho_{01,10} = <01|rho|10> changes sign with b0, its branch-unsigned average is zero on an ideal "
            "device, and the terminal four-outcome orbit law cannot see it. Each shot is weighted by "
            "(-1)^b0, and C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 is the branch-signed rho_{01,10}, with "
            "arg C = phi and |C| = 1/2 ideally; a Z rotation by delta on work_b turns C by +delta, on work_a "
            "by -delta.",
            "",
            f"Routing moves the logical work qubits during the prefix, so the compiled circuits read {reads}; "
            "no two-qubit gate follows the prefix, so per-qubit attribution of a window phase uses this "
            "executed map, not the initial roles.",
            "",
            f"Three contexts follow the same round-1 prefix: immediate readout; a matched idle of {window} dt "
            "(the control's measure plus reset) with b0 read after it; and a mid-circuit measure and reset "
            "of the control before the work readout. A coherent window phase rotates C between contexts, "
            "dephasing or amplitude damping shrinks |C| without rotating it, and first-bit assignment error "
            "scales C by (1 - 2 epsilon), so rotation and shrinkage separate the explanations the terminal "
            "law left degenerate. The matched idle reads b0 after the window, so control relaxation there "
            "adds to epsilon and scales that context's C without rotating it. The branch-unsigned average is "
            "a negative control, the ZZ setting and the spectator readout give the work populations and the "
            "one-hot sector.",
            "",
            f"One idle length fixes a window phase only modulo 2 pi: a static detuning above {alias_khz:.0f} kHz "
            "aliases to a smaller rotation of the opposite sign, so a measured rotation converts to a "
            "frequency only below that bound. In the immediate and matched-idle contexts b0 and the work "
            "pair are read in one simultaneous layer, so correlated readout crosstalk enters C as a "
            "context-independent scale. The calibration noise model omits measurement-induced dephasing "
            "of the work pair, so it prices the measure-and-reset contracts optimistically; a smaller "
            "hardware |C| there widens the reported intervals and remains an allowed outcome.",
            "",
            "The immediate and matched-idle contexts run in the static job and the measure-and-reset "
            "context in the dynamic job; the idle-versus-immediate comparison shares one job, while drift "
            "between the jobs enters the measure-and-reset comparison as a rotation. The analysis reads "
            "each PUB's executed work exposure from the returned schedule and reports both jobs' execution "
            "times, so that comparison bounds a measurement-induced phase only together with them.",
            "",
            f"Five two-sided precision contracts admit the design, each with half-width {precision:g} on 4 C: "
            "Re C in the immediate context and the Re C and Im C differences between adjacent contexts. "
            f"That half-width resolves a rotation near {precision / 2:.2f} rad at |C| = 1/2 and "
            f"{precision / 1.72:.2f} rad at |C| = 0.43. They price resolution, not an effect; an "
            "unresolved rotation or a context-independent C remains an allowed outcome, and a phase is "
            "reported only where |C| supports it.",
            "",
        ]
    if family == "patch-window":
        configuration = record["family_configuration"]
        roles = configuration.get("patch_roles") or [
            "control",
            "work_a",
            "spectator",
            "work_b",
            "neighbor_a",
            "neighbor_b",
        ]
        patch = ", ".join(f"{role} {qubit}" for role, qubit in zip(roles, configuration["patch_qubits"], strict=True))
        backends = ", ".join(sorted({_identifier(group["backend"], "backend") for group in record["groups"]}))
        return [
            "## Scientific question and interpretation",
            "",
            f"The patch-window family characterizes the physical qubits {patch} on {backends}. It "
            "reproduces the window of the N=21 orbit runs only when this backend and these roles match the "
            "orbit record's layout; on other qubits it characterizes this patch alone. Paired and "
            "single-qubit Ramsey, plain and echoed, "
            "measure work-qubit phase and visibility against executed idle; measure-and-reset and reset-only "
            "windows separate the explicit measurement; exchange circuits with zero-delay, unexcited and "
            "all-one references bound population transfer; and nominal, barrier and barrier-plus-echo orbit "
            "pairs compare scheduling contexts in one acquisition.",
            "",
            "Ten two-sided precision contracts on member differences admit the design; the calibration noise "
            "model has no coherent window phase, so they price resolution, not an effect. The Y-only Ramsey "
            "endpoints resolve phase differences only at favorable orientation, the exchange and orbit "
            "endpoints are exploratory, and an unresolved or no-intervention outcome remains allowed. "
            "Physical detuning is withheld wherever executed timing, alias separation or visibility does "
            "not support it.",
            "",
        ]
    if family == "folded-qpe":
        return [
            "## Scientific question and interpretation",
            "",
            "The folded-QPE ladder measures terminal-bit contrasts for four supplied eigenstate labels. "
            "The archived arm, calibrated-delay arm, measurement-without-feedback arm, and coherent "
            "two-control arm expose distinct failures of the calibration-derived outcome model. "
            "The delay arm measures only its terminal bit; the supplied first-bit label is a preparation "
            "input. The other arms retain two measured bits with label index b0 + 2*b1.",
            "",
            "The delay replaces the compiled first measurement's duration, rounded to device granularity, "
            "retains reset, and uses the supplied eigenstate label for its unconditional correction. "
            "The intervention changes measurement and correction behavior together. Removing feedback "
            "changes some ideal laws. The coherent arm adds a control qubit and runs in a separate static "
            "job. Shared initial placement preserves the initial register assignment; coherent routing "
            "and terminal readout sites can differ. The archived mapping below records those confounds. "
            "A contrast therefore does not establish a unique gate-level cause.",
            "",
            "Noise simulation computes conditional predictions from Target/properties. The declared "
            "classical-latency allowance contributes to the cost estimate; scheduler-latency noise remains "
            "outside the Aer outcome model. Only future hardware observations measure scheduler residuals, "
            "correlated errors, readout disturbance, and drift omitted by that model. Raw outcomes, "
            "scheduler metadata, calibration windows, and charged usage support the comparison.",
            "",
        ]
    return [
        "## Scientific question and interpretation",
        "",
        "The N=21, base-4 family measures the change in the labeled two-phase-bit distribution when "
        "feed-forward is removed. Array labels are 00, 01, 10, 11 (index b0 + 2*b1). The preregistered "
        "score is P(01)-P(11) with feedback, minus the same score without feedback. Two phase bits "
        "provide a feedback diagnostic; they do not establish successful general order recovery, "
        "factoring advantage, or an asymptotic speedup.",
        "",
        *(
            [
                "The orbit families compile each controlled multiplier only on the orbit 1, 4, 16 of the "
                "work register, which supplies the order 3 to the circuit. They measure feed-forward in a "
                "two-round semiclassical QPE and perform no order finding or factoring (Smolin, Smith and "
                "Vargo, Nature 499, 163 (2013)). The window arms of n21-orbit-rca idle the control, read it "
                "a second time, or echo the work qubits during the first measurement and reset; the family "
                "configuration records their durations in dt.",
                "",
            ]
            if family in ("n21-orbit-feedback", "n21-orbit-rca")
            else []
        ),
        "Gate noise, measurement/reset disturbance, conditional-control latency, routing changes, "
        "replica correlations, and calibration drift can change the contrast. Calibration-based Aer "
        "simulation supplies a conditional model and power admission. Future hardware observations "
        "measure the actual contrast and model residual. A failed directional test leaves the stated "
        "hardware distinction unresolved; the case does not convert a simulated power calculation "
        "into a measured hardware guarantee.",
        "",
    ]


def _native_qualification(run_dir: Path, record_digest: str, qpy_digest: str, *, family: str = "") -> list[str]:
    """Report only mock evidence bound to the exact archived workload."""
    if family == "folded-correction":
        return [
            "## Post-execution schedule qualification",
            "",
            "The authorized preparation route skips unavailable native mock scheduling. "
            "Fresh Target timing and explicit overhead/controller-latency scenarios supply local "
            "planning estimates. The actual native schedule remains unknown before execution; "
            "the estimate supplies neither native timing proof nor a final-charge guarantee.",
            "",
            "Returned scheduler tables must qualify each archived F/U pair's exposed protected "
            "events, measurement/reset/dispatch history, correction slot, and timing. "
            "Circuit validation supplies phase and condition semantics omitted by the timing table. "
            "Missing or mismatched tables, incomplete counts, or ambiguous calibration withhold "
            "the CP scientific decision while retaining raw and descriptive results. "
            "Exposed schedule agreement leaves undisclosed controller behavior and per-shot timing uncertified.",
            "",
        ]
    lines = ["## Native server qualification", ""]
    reports = sorted((run_dir / "native-dry-run").glob("*/report.json"))
    matching = []
    for path in reports:
        report = json.loads(path.read_text())
        files = report.get("binding", {}).get("files", {})
        if files.get("record.json") == record_digest and files.get("isa.qpy") == qpy_digest:
            matching.append((path, report))
    if not matching:
        return lines + [
            "Native server timing remains unqualified for these archived bytes. "
            "The charge above is a local planning estimate.",
            "",
        ]
    path, report = matching[-1]
    relative = path.relative_to(run_dir).as_posix()
    _identifier(relative, "native report path")
    status = _identifier(report["status"], "native qualification status")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.extend([f"The [mock timing report]({relative}) reports `{status}`; SHA-256 `{digest}`.", ""])
    if report.get("qualified") is True and status == "complete" and report.get("dry_run") is True:
        estimate = _number(report["estimated_quantum_seconds"], "native server seconds", positive=True)
        lines.extend([f"The server estimates {estimate:.12g} quantum seconds for the archived workload.", ""])
    else:
        lines.extend(["The native attempt leaves server timing unqualified; its report retains the failure.", ""])
    return lines + [
        "Runtime mock execution validates a schedule without executing the QPU. Randomized mock "
        "outcomes are excluded from scientific analysis and visuals. Server estimates, schedule durations "
        "and future charged usage are distinct. Initialization and fixed overhead remain unseparated.",
        "",
    ]


def _render(
    record: dict[str, Any],
    candidate: dict[str, Any],
    location: Path,
    record_digest: str,
    qpy_digest: str,
    native_lines: list[str] | None = None,
) -> str:
    family = record["family_configuration"]["name"]
    source = record["code_commit"]
    head = source["head"]
    _require(isinstance(head, str) and bool(re.fullmatch(r"[a-f0-9]{40,64}", head)), "source commit is unavailable")
    _require(type(source["sources_modified"]) is bool, "source cleanliness is unavailable")
    _require(bool(_HEX_DIGEST.fullmatch(record["experiment_digest"])), "experiment digest is invalid")
    arguments = _reproduction_arguments(record, location)
    allocation = _shot_allocation(record)
    shot_description = f"at {_count(record['shots'], 'shots')} shots per PUB"
    if allocation is not None:
        tiers = ", ".join(map(str, sorted(set(allocation.values()))))
        shot_description = f"with per-PUB shot allocation (used tiers: {tiers}; {len(candidate['jobs'])} jobs)"
    lines = [
        f"# Unapproved QPU case: {family}",
        "",
        "Status: UNAPPROVED. The saved record describes a feasible "
        "submit-free dry run. Writing this case supplies zero authorization and submits zero QPU jobs.",
        "",
        f"The selected bounded-search candidate is `{_identifier(candidate['name'], 'candidate')}` "
        f"{shot_description}. Global optimality remains outside the claim.",
        "",
        "## Artifact and source binding",
        "",
        f"- Saved run: `{location.as_posix()}`.",
        f"- [record.json](record.json) SHA-256: `{record_digest}`.",
        f"- [isa.qpy](isa.qpy) SHA-256: `{qpy_digest}`.",
        f"- Experiment source digest: `{record['experiment_digest']}`.",
        f"- Source commit: `{head}`; sources_modified=`{str(source['sources_modified']).lower()}`.",
        f"- Simulator seed: `{_count(record['seed_simulator'], 'simulator seed')}`; "
        "the source digest binds the simulator implementation.",
        "",
    ]
    if source["sources_modified"]:
        lines.extend(
            [
                "The source flag records changes anywhere in the experiment directory, including "
                "documentation and unmanifested files. Reproduction requires verification of every "
                "declared source against the experiment digest; the broad flag alone does not establish "
                "which source bytes differ from the recorded commit. A separate source-closure audit "
                "can establish that comparison without altering the retained record.",
                "",
            ]
        )
    lines.extend(["Recorded dependency versions:", "", "| Dependency | Version |", "|---|---|"])
    for package, version in sorted(record["versions"].items()):
        lines.append(f"| {_identifier(package, 'package')} | {_identifier(version, 'version')} |")
    lines.append("")
    lines.extend(_scientific_case(family, record))
    lines.extend(
        [
            "## Archived ideal laws and placement",
            "",
            "The ideal arrays below come from the retained record. Their label order stays intact; "
            "sorting probabilities would discard the specified outcome labels.",
            "",
            "| Member | Labeled ideal probabilities |",
            "|---|---|",
        ]
    )
    for group in record["groups"]:
        for member in group["members"]:
            name = _identifier(member["name"], "member")
            ideal = [_number(value, "ideal probability") for value in member["ideal"]]
            _require(
                all(0 <= value <= 1 for value in ideal) and math.isclose(sum(ideal), 1.0, abs_tol=1e-9),
                "invalid ideal law",
            )
            lines.append(f"| {name} | `{json.dumps(ideal)}` |")
    # The transpiler routes a template layout; replica placement then maps each
    # replica onto the physical qubits that execute, which the last column names.
    lines.extend(
        [
            "",
            "| Group | Backend | Calibration | Transpiler seed | Template layout | Executed physical layouts |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for group in record["groups"]:
        calibration = _identifier(group["calibration"], "calibration")
        template = _numeric_mapping(group["initial_layout"])
        placed = [[replica["mapping"][str(qubit)] for qubit in template] for replica in group["replicas"]]
        lines.append(
            f"| {_identifier(group['group'], 'group')} | {_identifier(group['backend'], 'backend')} | "
            f"{calibration} | {_count(group['seed_transpiler'], 'transpiler seed')} | "
            f"`{json.dumps(_numeric_mapping(group['initial_layout']))}` | `{json.dumps(placed)}` |"
        )
    mappings = {
        key: _numeric_mapping(value) for key, value in record["family_configuration"].items() if key in _MAPPING_FIELDS
    }
    mappings["group_replica_mappings"] = {
        _identifier(group["group"], "group"): [_numeric_mapping(replica["mapping"]) for replica in group["replicas"]]
        for group in record["groups"]
    }
    lines.extend(
        ["", "Calibration-bound family and replica mapping:", "", "```json", json.dumps(mappings, indent=2), "```", ""]
    )
    lines.extend(_endpoints(record, candidate))
    if family == "folded-correction":
        lines.extend(_correction_selection(record, candidate))
    else:
        lines.extend(
            [
                "## Selection objective and sensitivity assumptions",
                "",
                f"The objective is `{record['policy']['design'].get('objective', 'minimum_charge')}`. "
                "Selection compares the declared finite candidate set after statistical and cost admission.",
                "",
            ]
        )
    if candidate.get("normalized_precision_radius") is not None:
        lines.extend(
            [
                "The worst confidence half-width divided by its declared target is "
                f"{_format_number(candidate['normalized_precision_radius'])}. "
                "Smaller sampling intervals quantify precision; physical-model bias remains a separate residual.",
                "",
            ]
        )
    scenarios = candidate.get("cost_scenarios", [])
    if scenarios:
        _require(all(scenario["feasible"] for scenario in scenarios), "selected cost sensitivity fails admission")
        lines.extend(
            [
                "Every listed cost scenario passes the same per-job and aggregate ceilings. "
                "Scenario values are explicit assumptions, with no claimed confidence coverage.",
                "",
                "| Scenario | Job overhead (s) | Classical latency per stage (us) | Total charge (s) |",
                "|---|---:|---:|---:|",
            ]
        )
        assumptions = {scenario["name"]: scenario for scenario in record["policy"]["design"]["cost_scenarios"]}
        for scenario in scenarios:
            assumption = assumptions[scenario["name"]]
            lines.append(
                f"| {_identifier(scenario['name'], 'cost scenario')} | "
                f"{_format_number(assumption['job_overhead_seconds'])} | "
                f"{_format_number(assumption['classical_latency_us'])} | "
                f"{_format_number(scenario['estimated_charge_seconds'])} |"
            )
        lines.extend(
            [
                "",
                "The largest nominal/scenario charge is "
                f"{_format_number(candidate['worst_case_charge_seconds'])} seconds. "
                "The complete scenario PUB ledgers remain in record.json.",
                "",
            ]
        )
    budget = record["budget_plan"]
    lines.extend(
        [
            "## Expected charge and service ceilings",
            "",
            "| Job | PUBs | Submitted PUB shots | Estimated charge (s) | Service ceiling (s) |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for job in candidate["jobs"]:
        pub_shots = sum(_count(pub["shots"], "PUB shots") for pub in job["pubs"])
        lines.append(
            f"| {_identifier(job['name'], 'job')} | {len(job['pubs'])} | {pub_shots} | "
            f"{_format_number(job['estimated_charge_seconds'])} | {_format_number(job['max_execution_seconds'])} |"
        )
    lines.extend(
        [
            "",
            f"The cost model predicts {_format_number(candidate['estimated_charge_seconds'])} seconds. "
            "The per-job service ceilings sum to "
            f"{_format_number(candidate['total_execution_ceiling_seconds'])} seconds "
            f"against an invocation cap of {_format_number(budget['max_total_execution_seconds'])} seconds. "
            f"The global reserve is {_format_number(budget['reserve_seconds'])} seconds; the saved quota "
            f"reports {_format_number(budget['remaining_seconds'])} seconds remaining.",
            "",
            "Every PUB cost includes its Target duration, explicit repetition delay, and "
            "declared reset/classical-latency additions. Each job also includes its declared fixed "
            "overhead. Those model assumptions estimate charge; the ceilings bound service execution "
            "instead. The ledger retains accepted and attempted jobs' reservations while their charges "
            "remain unsettled. External submissions can still change the shared quota. Dynamic Target "
            "duration omits classical scheduler latency; the declared addition remains a planning assumption. "
            "Explicit circuit resets contribute to Target duration. Runtime's implicit initialization cost "
            "remains unseparated unless a native server timing artifact qualifies that accounting boundary.",
            "",
        ]
    )
    for job in candidate["jobs"]:
        lines.extend(
            [
                "| PUB | Shots | Target duration (s) | Repetition delay (s) | "
                "Reset addition (s) | Classical latency addition (s) |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for pub in job["pubs"]:
            lines.append(
                f"| {_identifier(pub['name'], 'PUB')} | {_count(pub['shots'], 'PUB shots')} | "
                f"{_format_number(pub['scheduled_seconds'])} | {_format_number(pub['repetition_delay_seconds'])} | "
                f"{_format_number(pub['reset_seconds'])} | {_format_number(pub['classical_latency_seconds'])} |"
            )
        lines.extend(
            [
                "",
                f"Job `{_identifier(job['name'], 'job')}` adds "
                f"{_format_number(job['overhead_seconds'])} seconds of modeled overhead.",
                "",
            ]
        )
    lines.extend(native_lines or [])
    lines.extend(
        [
            "The [IBM timeout guide](https://quantum.cloud.ibm.com/docs/guides/max-execution-time) "
            "defines max_execution_time in QPU-usage seconds. Session/batch lifetime does not replace "
            "each job's execution ceiling. Actual charge comes from completed job usage.",
            "",
            "## Reproduce the dry run",
            "",
            "Run from the repository root with the recorded dependency versions and source digest. "
            "The command pins every backend in the saved discovery inventory, preserving the known "
            "candidate universe. The runner refreshes calibration and queue admission, so a changed "
            "backend can produce a different case. The transpiler seed count and simulator seed "
            "retain their recorded meanings.",
            "",
            "```sh",
            _command(arguments),
            "```",
            "",
            "## Approval-only submission template",
            "",
            "Execute the following command only after the owner explicitly approves this concrete "
            "case and its ceilings. Keep the complete saved run at the repository-relative location "
            "above; copying temporary evidence preserves record.json and isa.qpy byte-for-byte. "
            "The runner compares fresh source, dependency, policy, calibration, layout, and QPY evidence "
            "with the approved record, consumes its approval once, and stops for renewed approval when "
            "the comparison changes.",
            "",
            "```sh",
            _command(
                [
                    *arguments,
                    "--approved-record",
                    (Path("..") / location).as_posix(),
                    "--approved-record-sha256",
                    record_digest,
                    "--submit",
                ]
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_case(run_dir: Path, record: dict[str, Any]) -> Path | None:
    """Write an unapproved case only for an admitted family dry-run artifact pair."""
    family = record.get("family_configuration", {}).get("name")
    if family not in FAMILIES or record.get("state") != "planned":
        return None
    if (
        record.get("budget_plan", {}).get("admitted") is not True
        or record.get("optimization", {}).get("selected") is None
        or record.get("submission")
        or record.get("approval_consumed")
        or (run_dir / "approval-consumed.json").exists()
    ):
        return None
    candidate, record_digest, qpy_digest = _case_inputs(run_dir, record)
    text = _render(
        record,
        candidate,
        _portable_run_path(run_dir),
        record_digest,
        qpy_digest,
        _native_qualification(run_dir, record_digest, qpy_digest, family=family),
    )
    destination = run_dir / CASE_FILENAME
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=run_dir, prefix=".qpu-case-", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return destination


def _fixture() -> dict[str, Any]:
    """Minimal retained-record schema for artifact and command regression checks."""
    pub = dict(
        name="feedback_pub",
        shots=2048,
        scheduled_seconds=0.001,
        repetition_delay_seconds=0.00025,
        reset_seconds=0.0,
        classical_latency_seconds=0.00002,
        estimated_execution_seconds=2.60096,
    )
    endpoint = dict(
        name="feedback_contrast",
        feasible=True,
        predicted_value=0.25,
        simulation_error_radius=0.01,
        modeled_value_lower_bound=0.24,
        confidence_half_width=0.07,
        precision_half_width=None,
        minimum_effect=0.0,
        null_value=0.0,
        detection_radius=0.06,
        effect_used_for_power=0.24,
        power=0.8,
        power_radius=0.04,
        alpha=0.05,
        covariance_assumptions=[],
    )
    design = dict(
        family="n21-feedback",
        optimize=True,
        shot_tiers=[2048, 4096],
        replica_tiers=[1, 2],
        optimizer_candidates=3,
        model_shots=32768,
        precision=0.08,
        alpha=0.05,
        power=0.8,
        simulation_alpha=0.01,
        job_overhead_seconds=2.3,
        classical_latency_us=20.0,
        reserve_seconds=10.0,
        max_total_execution_seconds=90.0,
    )
    return dict(
        state="planned",
        family_configuration={"name": "n21-feedback", "replica_cap": 1},
        shots=2048,
        seed_simulator=7,
        experiment_digest="a" * 64,
        code_commit={"head": "b" * 40, "sources_modified": False},
        versions={"numpy": "2.5.4+local"},
        system_inventory={"ibm_fez": {}, "ibm_kingston": {}},
        policy=dict(
            design=design,
            twirl=False,
            dd=None,
            seeds=2,
            max_pending=25,
            min_remaining_seconds=60.0,
            max_execution_seconds=90,
            replica_floor=None,
            max_replicas=None,
            isolated_reference=True,
            cross_group_buffer=True,
        ),
        execution_pubs=[{"name": "feedback_pub"}],
        observable_contracts=[
            dict(name="feedback_contrast", terms=[dict(member="feedback", sign=1, values=[0.0, 1.0])])
        ],
        optimization=dict(
            selected="candidate-000-shots-2048",
            simulation_alpha=0.01,
            simulation_comparisons=4,
            candidates=[
                dict(
                    name="candidate-000-shots-2048",
                    feasible=True,
                    estimated_charge_seconds=4.90096,
                    total_execution_ceiling_seconds=90.0,
                    observables=[endpoint],
                    jobs=[
                        dict(
                            name="ibm_fez/dynamic/1",
                            pubs=[pub],
                            overhead_seconds=2.3,
                            estimated_charge_seconds=4.90096,
                            max_execution_seconds=90,
                        )
                    ],
                )
            ],
        ),
        budget_plan=dict(
            admitted=True,
            combined_ceiling_seconds=90.0,
            max_total_execution_seconds=90.0,
            reserve_seconds=10.0,
            remaining_seconds=591.0,
        ),
        groups=[
            dict(
                group="feedback_group",
                backend="ibm_fez",
                calibration="2026-10-11T12:00:00+00:00",
                seed_transpiler=7,
                initial_layout=[0],
                replicas=[{"mapping": {"0": 0}}],
                members=[dict(name="feedback", ideal=[0.5, 0.5])],
            )
        ],
    )


def _verify() -> None:
    record = _fixture()
    with tempfile.TemporaryDirectory(prefix="qpu-case-check-") as temporary:
        run_dir = Path(temporary) / "retained-run"
        run_dir.mkdir()
        circuit = QuantumCircuit(1, 1, name="feedback_pub")
        circuit.measure(0, 0)
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuit, handle)

        def retain(value: dict[str, Any]) -> None:
            (run_dir / "record.json").write_text(json.dumps(value, indent=2) + "\n")

        retain(record)
        originals = {name: (run_dir / name).read_bytes() for name in ("record.json", "isa.qpy")}
        destination = write_case(run_dir, record)
        assert destination is not None
        text = destination.read_text()
        assert "UNAPPROVED" in text and "--approved-record-sha256" in text
        assert hashlib.sha256(originals["record.json"]).hexdigest() in text
        assert hashlib.sha256(originals["isa.qpy"]).hexdigest() in text
        assert "--backends ibm_fez,ibm_kingston" in text
        assert "--shot-tiers 2048,4096" in text
        assert "2026-10-11T12:00:00+00:00" in text and "2.5.4+local" in text
        assert "exceeds 0.06" in text and "conditional target power 0.8" in text
        assert "one-sided detection radius" in text and "Power admission is conditional" in text
        assert str(run_dir) not in text and "crn:" not in text
        assert "--submit" not in text.split("## Approval-only submission template")[0]
        assert write_case(run_dir, record) == destination and destination.read_text() == text
        assert all((run_dir / name).read_bytes() == value for name, value in originals.items())
        for family, phrase in (("ripple", "box-kite phase atlas"), ("rank-sector", "coefficient-dependent LCU")):
            algebra = copy.deepcopy(record)
            algebra["policy"]["design"]["family"] = family
            algebra["family_configuration"]["name"] = family
            retain(algebra)
            assert write_case(run_dir, algebra) == destination
            assert (
                phrase in destination.read_text()
                and "Native server timing remains unqualified" in destination.read_text()
            )
        retain(record)
        assert write_case(run_dir, record) == destination and destination.read_text() == text
        native_run = Path(temporary) / "native-fixture"
        native_dir = native_run / "native-dry-run" / "fixture"
        native_dir.mkdir(parents=True)
        record_digest = hashlib.sha256(originals["record.json"]).hexdigest()
        qpy_digest = hashlib.sha256(originals["isa.qpy"]).hexdigest()
        native_report = {
            "binding": {"files": {"record.json": record_digest, "isa.qpy": qpy_digest}},
            "status": "complete",
            "qualified": True,
            "dry_run": True,
            "estimated_quantum_seconds": 7.5,
        }
        (native_dir / "report.json").write_text(json.dumps(native_report))
        assert "7.5 quantum seconds" in "\n".join(_native_qualification(native_run, record_digest, qpy_digest))
        assert "unqualified" in "\n".join(_native_qualification(native_run, "0" * 64, qpy_digest))
        native_report.update(status="unavailable", qualified=False)
        (native_dir / "report.json").write_text(json.dumps(native_report))
        assert "leaves server timing unqualified" in "\n".join(
            _native_qualification(native_run, record_digest, qpy_digest)
        )
        for state in ("design_infeasible", "budget_infeasible", "submitted", "approval_required"):
            changed = copy.deepcopy(record)
            changed["state"] = state
            assert write_case(run_dir, changed) is None
            assert destination.read_text() == text
        assert write_case(run_dir, {"state": "planned"}) is None
        for key in ("submission", "approval_consumed"):
            changed = copy.deepcopy(record)
            changed[key] = {"present": True}
            assert write_case(run_dir, changed) is None
        consumed = run_dir / "approval-consumed.json"
        consumed.write_text("{}\n")
        assert write_case(run_dir, record) is None
        consumed.unlink()
        folded = copy.deepcopy(record)
        folded["family_configuration"] = {
            "name": "folded-qpe",
            "measurement_delay_dt": {"1": 1600},
            "replaced_measurement_qubits": {"1": 3},
            "shared_initial_layout": [0, 1],
            "extra_control": 2,
            "measurement_seconds": {"1": 0.000004},
            "measurement_sites": {"feedback": [[3], [4]]},
            "dt_seconds": 2.5e-9,
        }
        folded["policy"]["design"]["family"] = "folded-qpe"
        folded_endpoint = folded["optimization"]["candidates"][0]["observables"][0]
        folded_endpoint.update(minimum_effect=None, precision_half_width=0.08)
        folded_candidate = folded["optimization"]["candidates"][0]
        static_job = copy.deepcopy(folded_candidate["jobs"][0])
        static_job["name"] = "ibm_fez/static/1"
        static_job["pubs"][0]["name"] = "coherent_pub"
        folded_candidate["jobs"].append(static_job)
        folded_candidate["estimated_charge_seconds"] *= 2
        folded_candidate["total_execution_ceiling_seconds"] *= 2
        folded["policy"]["design"]["max_total_execution_seconds"] = 180.0
        folded["budget_plan"].update(combined_ceiling_seconds=180.0, max_total_execution_seconds=180.0)
        folded["execution_pubs"].append({"name": "coherent_pub"})
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump([circuit, circuit.copy(name="coherent_pub")], handle)
        retain(folded)
        assert write_case(run_dir, folded) == destination
        folded_text = destination.read_text()
        assert "calibrated-delay arm" in folded_text and "measurement_sites" in folded_text
        assert "coherent routing and terminal readout sites can differ" in folded_text
        assert "--family folded-qpe" in folded_text and "requested precision is 0.08" in folded_text
        assert "Reject the directional null" not in folded_text
        assert "one-sided detection radius" not in folded_text and "Power admission" not in folded_text
        assert "preregister precision intervals" in folded_text
        assert "scheduler-latency noise remains outside the Aer outcome model" in folded_text
        cost_section = folded_text.split("## Expected charge and service ceilings", 1)[1]
        pub_tables = re.findall(r"(?:^\|[^\n]+\n)+", cost_section, flags=re.MULTILINE)
        assert len(pub_tables) == 3
        for table, job in zip(pub_tables[1:], folded_candidate["jobs"], strict=True):
            rows = table.splitlines()
            assert rows[0].startswith("| PUB | Shots |") and rows[1].startswith("|---|")
            assert len(rows) == len(job["pubs"]) + 2
            assert all(
                row.startswith("| " + pub["name"] + " |") for row, pub in zip(rows[2:], job["pubs"], strict=True)
            )
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuit, handle)
        changed = copy.deepcopy(record)
        changed["code_commit"]["sources_modified"] = True
        retain(changed)
        assert write_case(run_dir, changed) == destination
        assert "source flag records changes anywhere" in destination.read_text()
        retain(record)
        changed = copy.deepcopy(record)
        changed["shots"] = 4096
        try:
            write_case(run_dir, changed)
        except ValueError as error:
            assert "retained record.json" in str(error)
        else:
            raise AssertionError("case writer accepts mismatched in-memory record")
        changed = copy.deepcopy(record)
        changed["budget_plan"]["combined_ceiling_seconds"] = 180
        retain(changed)
        try:
            write_case(run_dir, changed)
        except ValueError as error:
            assert "budget ledger" in str(error)
        else:
            raise AssertionError("case writer accepts an inconsistent aggregate budget")
        for field, invalid_budget, expected_error in (
            ("remaining_seconds", 95.0, "quota reserve"),
            ("reserve_seconds", 9.0, "design policy"),
        ):
            changed = copy.deepcopy(record)
            changed["budget_plan"][field] = invalid_budget
            retain(changed)
            try:
                write_case(run_dir, changed)
            except ValueError as error:
                assert expected_error in str(error)
            else:
                raise AssertionError(f"case writer accepts inconsistent {field}")
        for field, invalid_pub, expected_error in (
            ("shots", 1024, "PUB shots"),
            ("name", "different_pub", "costed PUBs"),
            ("estimated_execution_seconds", 0.1, "estimated execution"),
        ):
            changed = copy.deepcopy(record)
            changed["optimization"]["candidates"][0]["jobs"][0]["pubs"][0][field] = invalid_pub
            retain(changed)
            try:
                write_case(run_dir, changed)
            except ValueError as error:
                assert expected_error in str(error)
            else:
                raise AssertionError(f"case writer accepts inconsistent PUB {field}")
        retain(record)
        circuit.name = "different_pub"
        with (run_dir / "isa.qpy").open("wb") as handle:
            qpy.dump(circuit, handle)
        try:
            write_case(run_dir, record)
        except ValueError as error:
            assert "ordered execution-PUB manifest" in str(error)
        else:
            raise AssertionError("case writer accepts a different QPY manifest")
    print("QPU cases: artifact and cost binding, both families, relative commands, and refusal checks pass")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true", help="run credential-free case-writer regression checks")
    args = parser.parse_args(argv)
    if args.check:
        _verify()
        return 0
    if args.run_dir is None:
        parser.error("supply a retained run directory or --check")
    record = json.loads((args.run_dir / "record.json").read_text())
    destination = write_case(args.run_dir, record)
    if destination is None:
        print("The saved record supplies no admitted family dry-run case.")
        return 0
    print(f"Written {destination.name}; status UNAPPROVED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

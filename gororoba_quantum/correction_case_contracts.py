"""Offline artifact and protocol rejection checks for the correction QPU case."""

from __future__ import annotations

import copy
import io
import json
import math
import tempfile
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qpy, transpile
from qiskit_ibm_runtime.fake_provider import FakeKingston

import correction_statistics
import qpu_cases
from correction_circuits import (
    CORRECTION_ARMS,
    bind_correction_template,
    correction_template,
    validate_bound_correction_pair,
    validate_correction_pair,
)


def _fixture() -> tuple[dict[str, Any], list[QuantumCircuit]]:
    """Build real common-template circuits with explicit synthetic planning evidence."""
    routed = transpile(
        correction_template(),
        backend=FakeKingston(),
        initial_layout=[95, 79, 93, 92, 94],
        optimization_level=3,
        seed_transpiler=20261010,
    )
    circuits = [
        bind_correction_template(routed, label, CORRECTION_ARMS[arm]) for label, arm in ((1, 0), (1, 1), (3, 1), (3, 0))
    ]
    for index, circuit in enumerate(circuits):
        circuit.name = f"correction_pub_{index}"
    pairs = {
        "1": validate_bound_correction_pair(circuits[0], circuits[1], 1),
        "3": validate_bound_correction_pair(circuits[3], circuits[2], 3),
    }
    template_pairs = {
        "1": validate_correction_pair(routed, circuits[0], circuits[1], 1),
        "3": validate_correction_pair(routed, circuits[3], circuits[2], 3),
    }
    members = correction_statistics.MEMBERS
    backend_names = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
    calibration = "2026-10-12T00:00:00+00:00"
    backend_states = {
        name: {"calibration": calibration, "fetched_at": "2026-10-12T01:00:00+00:00"} for name in backend_names
    }
    probabilities = ([0.2, 0.6, 0.1, 0.1], [0.18, 0.63, 0.1, 0.09], [0.1, 0.1, 0.15, 0.65], [0.12, 0.1, 0.16, 0.62])
    model_members: dict[str, Any] = {
        name: {
            "probabilities": list(values),
            "terminal_success_probability": sum(values[:2] if index < 2 else values[2:]),
        }
        for index, (name, values) in enumerate(zip(members, probabilities, strict=True))
    }
    record = qpu_cases._fixture()
    record.update(
        shots=8192,
        backends=backend_states,
        system_inventory={name: dict(state, eligibility="eligible") for name, state in backend_states.items()},
        observable_contracts=[],
        family_configuration={
            "name": "folded-correction",
            "shots_per_pub": 8192,
            "member_order": list(members),
            "replica_cap": 1,
            "execution_row_count": 4,
            "native_mock_required": False,
            "classical_dispatch_retained": True,
            "dispatch_removal_test": False,
            "decision_contract": {
                "method": "four_one_sided_clopper_pearson_bounds",
                "family_alpha": 0.05,
                "per_bound_tail": 0.0125,
                "minimum_gain": 0.01,
                "require_both_labels": True,
                "count_semantics": "raw integer counts; y=first_bit+2*terminal_bit",
                "postexecution_schedule_gate": True,
            },
            "circuit_pairs": pairs,
            "template_pairs": template_pairs,
            "hypothetical_power": correction_statistics.planning_certificate(8192),
            "backend_search": [
                {
                    "backend": name,
                    "calibration": calibration,
                    "eligible": True,
                    "rejection_reason": None,
                    "compiled_candidate_count": 1,
                    "admitted_candidate_count": int(name == "ibm_fez"),
                }
                for name in backend_names
            ],
            "model_prediction": {
                "evidence_class": "finite-shot calibration noise simulation; controller/instrument errors incomplete",
                "shots_per_member": 1000,
                "seed": record["seed_simulator"],
                "members": model_members,
                "gain_known_minus_measured": {
                    "1": model_members[members[1]]["terminal_success_probability"]
                    - model_members[members[0]]["terminal_success_probability"],
                    "3": model_members[members[2]]["terminal_success_probability"]
                    - model_members[members[3]]["terminal_success_probability"],
                },
                "prediction_frozen_before_hardware": True,
            },
        },
    )
    record["policy"].update(isolated_reference=False, max_replicas=1, max_execution_seconds=30)
    record["policy"]["design"].update(
        family="folded-correction",
        shot_tiers=[8192],
        replica_tiers=[1],
        model_shots=1000,
        max_total_execution_seconds=30,
        objective="minimum_charge",
        cost_scenarios=[{"name": "conservative", "job_overhead_seconds": 5.0, "classical_latency_us": 100.0}],
    )
    qubits = sorted(
        {
            index
            for circuit in circuits
            for instruction in circuit.data
            for index in (circuit.find_bit(qubit).index for qubit in instruction.qubits)
        }
    )
    record["groups"] = [
        {
            "group": "folded_correction",
            "backend": "ibm_fez",
            "calibration": calibration,
            "seed_transpiler": 20261010,
            "initial_layout": [95, 79, 93, 92, 94],
            "replicas": [{"mapping": {str(qubit): qubit for qubit in qubits}}],
            "members": [
                {"name": name, "ideal": [float(outcome == label) for outcome in range(4)]}
                for name, label in zip(members, (1, 1, 3, 3), strict=True)
            ],
        }
    ]
    record["execution_pubs"] = [
        {
            "name": circuit.name,
            "backend": "ibm_fez",
            "kind": "dynamic",
            "feed_forward_operation_count": 1,
            "sequential_stage_count": 1,
            "parallel_stream_count": 1,
            "components": [
                {
                    "group": "folded_correction",
                    "member": member,
                    "reference": False,
                    "physical_qubits": qubits,
                    "registers_by_replica": [["c"]],
                }
            ],
        }
        for circuit, member in zip(circuits, members, strict=True)
    ]
    job: dict[str, Any] = {
        "name": "ibm_fez/dynamic/1",
        "overhead_seconds": 2.3,
        "max_execution_seconds": 30,
        "pubs": [
            {
                "name": circuit.name,
                "shots": 8192,
                "scheduled_seconds": 1e-5,
                "repetition_delay_seconds": 0.00025,
                "reset_seconds": 0.0,
                "classical_latency_seconds": 20e-6,
                "classical_stage_count": 1,
                "estimated_execution_seconds": 8192 * (1e-5 + 0.00025 + 20e-6),
            }
            for circuit in circuits
        ],
    }
    job["estimated_charge_seconds"] = math.fsum(
        [job["overhead_seconds"], *[pub["estimated_execution_seconds"] for pub in job["pubs"]]]
    )
    scenario_job = copy.deepcopy(job)
    scenario_job["overhead_seconds"] = 5.0
    for pub in scenario_job["pubs"]:
        pub["classical_latency_seconds"] = 100e-6
        pub["estimated_execution_seconds"] = 8192 * (1e-5 + 0.00025 + 100e-6)
    scenario_job["estimated_charge_seconds"] = math.fsum(
        [5.0, *[pub["estimated_execution_seconds"] for pub in scenario_job["pubs"]]]
    )
    candidate = {
        "name": "correction-candidate",
        "backend": "ibm_fez",
        "feasible": True,
        "estimated_charge_seconds": job["estimated_charge_seconds"],
        "total_execution_ceiling_seconds": 30,
        "jobs": [job],
        "observables": [],
        "proxy_metadata": {"worst_arm_quality": 0.8, "member_scores": [0.8, 0.8, 0.8, 0.8]},
        "worst_case_charge_seconds": scenario_job["estimated_charge_seconds"],
        "cost_scenarios": [
            {
                "name": "conservative",
                "feasible": True,
                "estimated_charge_seconds": scenario_job["estimated_charge_seconds"],
                "jobs": [scenario_job],
            }
        ],
    }
    record["optimization"].update(
        selected=candidate["name"], candidates=[candidate], objective="worst_arm_calibrated_quality_then_charge"
    )
    record["budget_plan"].update(combined_ceiling_seconds=30, max_total_execution_seconds=30)
    return record, circuits


def verify() -> dict[str, Any]:
    record, circuits = _fixture()
    stream = io.BytesIO()
    qpy.dump(circuits, stream)
    archived = stream.getvalue()
    rejected = 0
    with tempfile.TemporaryDirectory(prefix="correction-case-contract-") as temporary:
        directory = Path(temporary) / "retained-run"
        directory.mkdir()
        (directory / "isa.qpy").write_bytes(archived)

        def retain(value: dict[str, Any]) -> None:
            (directory / "record.json").write_text(json.dumps(value, sort_keys=True, allow_nan=False))

        retain(record)
        original_record = (directory / "record.json").read_bytes()
        destination = qpu_cases.write_case(directory, record)
        if destination is None:
            raise RuntimeError("admitted correction case was omitted")
        text = destination.read_text()
        for expected in (
            "Clopper-Pearson",
            "0.0125",
            "lower_U - upper_F > 0.01",
            "both labels",
            "8192",
            "hypothetical",
            "post-execution",
            "raw",
            "--approved-record-sha256",
            "--backends ibm_fez,ibm_kingston,ibm_marrakesh",
        ):
            if expected not in text:
                raise RuntimeError(f"correction case omitted {expected}")
        if "one-sided detection radius" in text or "Reject the directional null" in text:
            raise RuntimeError("correction case inherited generic Hoeffding inference")
        if (directory / "record.json").read_bytes() != original_record or (
            directory / "isa.qpy"
        ).read_bytes() != archived:
            raise RuntimeError("case writer changed retained experiment inputs")
        excluded = copy.deepcopy(record)
        excluded["family_configuration"]["backend_search"][1].update(
            eligible=False, rejection_reason="synthetic missing routing capability", compiled_candidate_count=0
        )
        retain(excluded)
        if qpu_cases.write_case(directory, excluded) is None:
            raise RuntimeError("case writer conflated system eligibility with family capability admission")
        paths_and_values: list[tuple[tuple[Any, ...], Any]] = [
            (("shots",), 4096),
            (("family_configuration", "shots_per_pub"), 4096),
            (("family_configuration", "member_order"), list(reversed(correction_statistics.MEMBERS))),
            (("family_configuration", "replica_cap"), 2),
            (("family_configuration", "execution_row_count"), 5),
            (("family_configuration", "native_mock_required"), True),
            (("family_configuration", "classical_dispatch_retained"), False),
            (("family_configuration", "dispatch_removal_test"), True),
            (("family_configuration", "decision_contract", "method"), "hoeffding"),
            (("family_configuration", "decision_contract", "minimum_gain"), 0.0),
            (("family_configuration", "decision_contract", "family_alpha"), 0.1),
            (("family_configuration", "decision_contract", "per_bound_tail"), 0.05),
            (("family_configuration", "decision_contract", "require_both_labels"), False),
            (("family_configuration", "decision_contract", "postexecution_schedule_gate"), False),
            (("family_configuration", "circuit_pairs", "1", "prefix_sha256"), "f" * 64),
            (("family_configuration", "hypothetical_power", "assumed_gain"), 0.01),
            (("family_configuration", "hypothetical_power", "hypothetical_power_qualified"), False),
            (("family_configuration", "backend_search"), record["family_configuration"]["backend_search"][:2]),
            (("family_configuration", "backend_search", 0, "calibration"), "changed"),
            (("family_configuration", "backend_search", 0, "admitted_candidate_count"), 0),
            (("family_configuration", "backend_search", 1, "eligible"), False),
            (("family_configuration", "backend_search", 1, "rejection_reason"), "inconsistent eligibility"),
            (("system_inventory", "ibm_fez", "eligibility"), "ineligible"),
            (("family_configuration", "model_prediction", "prediction_frozen_before_hardware"), False),
            (("family_configuration", "model_prediction", "gain_known_minus_measured", "1"), 0.9),
            (
                (
                    "family_configuration",
                    "model_prediction",
                    "members",
                    correction_statistics.MEMBERS[0],
                    "terminal_success_probability",
                ),
                0.1,
            ),
            (("policy", "isolated_reference"), True),
            (("policy", "design", "alpha"), 0.1),
            (("policy", "design", "replica_tiers"), [1, 2]),
            (("policy", "design", "cost_scenarios"), []),
            (("optimization", "objective"), "minimum_charge"),
            (("optimization", "candidates", 0, "worst_case_charge_seconds"), 0.0),
            (("optimization", "candidates", 0, "proxy_metadata", "worst_arm_quality"), 0.9),
            (("execution_pubs", 0, "components", 0, "reference"), True),
            (("execution_pubs", 0, "kind"), "static"),
            (("execution_pubs", 0, "components", 0, "registers_by_replica"), [["a"], ["b"]]),
            (("execution_pubs", 0, "components", 0, "member"), "extra_member"),
        ]
        for path, value in paths_and_values:
            changed = copy.deepcopy(record)
            cursor = changed
            for key in path[:-1]:
                cursor = cursor[key]
            cursor[path[-1]] = value
            retain(changed)
            try:
                qpu_cases.write_case(directory, changed)
            except ValueError:
                rejected += 1
            else:
                raise RuntimeError(f"correction case accepted mutation {path}")
        retain(record)
        altered = [circuit.copy() for circuit in circuits]
        altered[0].x(0)
        with (directory / "isa.qpy").open("wb") as handle:
            qpy.dump(altered, handle)
        try:
            qpu_cases.write_case(directory, record)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("correction case accepted changed QPY operations")
    return {"rejected_mutations": rejected, "credential_free": True, "physical_submissions": 0}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

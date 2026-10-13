"""Exercise three-device correction planning without a service or quantum job."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
from dataclasses import replace
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import qpy
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston, FakeMarrakesh

import correction_planning
import live_run
import packing
import qpu_cases
from correction_circuits import validate_bound_correction_pair
from correction_statistics import MEMBERS
from diagnostic_experiments import FAMILY_NAMES, family_contracts, record_groups
from qpu_planning import execution_contract
from runtime_contracts import _fake_snapshot, _fixture_args


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _reject(action: Any, message: str) -> None:
    try:
        action()
    except (ValueError, live_run.LiveRunError):
        return
    raise RuntimeError(message)


def _archive(circuits: list[Any]) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuits, stream)
    return stream.getvalue()


def _args(**overrides: Any) -> Any:
    arguments = _fixture_args(
        family="folded-correction",
        optimize=False,
        shots=8192,
        seeds=1,
        optimizer_candidates=1,
        max_replicas=1,
        replica_tiers=[1],
        shot_tiers=[8192],
        isolated_reference=False,
        model_shots=256,
        alpha=0.05,
        power=0.8,
        precision=0.08,
        simulation_alpha=0.01,
        job_overhead_seconds=2.3,
        classical_latency_us=20.0,
        cost_scenarios=[{"name": "controller-stress", "job_overhead_seconds": 4.6, "classical_latency_us": 40.0}],
        reserve_seconds=10.0,
        max_total_execution_seconds=30.0,
        max_execution_seconds=30.0,
    )
    vars(arguments).update(overrides)
    return arguments


class _DiscoveryService:
    """Provide account reads for real local planning with synthetic snapshots."""

    def usage(self) -> dict[str, Any]:
        return {"usage_remaining_seconds": 100.0, "usage_limit_reached": False}

    def active_instance(self) -> str:
        return "fixture-correction-instance"


def _verify_complete_discovery_frontier(snapshots: list[live_run.Snapshot]) -> dict[str, Any]:
    """Exercise production planning and approval rejection with an excluded peer."""
    names = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]
    service: Any = _DiscoveryService()
    outcomes = []
    scenarios = (
        ("maintenance", "maintenance", 1, True, True),
        ("queue", "active", 26, True, True),
        ("inactive", "active", 0, False, True),
        ("missing-cz", "active", 0, True, False),
        ("healthy", "active", 0, True, True),
    )
    for scenario, status, pending, operational, native_cz in scenarios:
        fresh = {snapshot.name: copy.copy(snapshot) for snapshot in snapshots}
        fresh["ibm_marrakesh"].status_msg = status
        fresh["ibm_marrakesh"].pending_jobs = pending
        fresh["ibm_marrakesh"].operational = operational
        if not native_cz:
            capabilities = fresh["ibm_marrakesh"].capabilities
            fresh["ibm_marrakesh"].capabilities = replace(
                capabilities, operation_names=tuple(name for name in capabilities.operation_names if name != "cz")
            )
        eligible_names = names if scenario == "healthy" else names[:2]
        peer_eligibility = "eligible" if scenario == "healthy" else "ineligible"
        arguments = _args(backends=names, max_pending=25, local_compute="cpu")
        with patch.object(live_run, "take_snapshot", side_effect=lambda unused, name, current=fresh: current[name]):
            generic, skipped, inventory = live_run.discover_snapshots(service, names, 25)
            _require(
                [snapshot.name for snapshot in generic] == eligible_names,
                "generic discovery changed eligibility filtering",
            )
            _require(
                inventory["ibm_marrakesh"]["eligibility"] == peer_eligibility
                and ("ibm_marrakesh" in skipped) == (scenario != "healthy"),
                "generic discovery lost excluded-peer evidence",
            )
            choices, record = live_run.plan(service, arguments)
            search = {row["backend"]: row for row in record["family_configuration"]["backend_search"]}
            _require(set(search) == set(names), "production correction planning lost the complete backend search")
            excluded = search["ibm_marrakesh"]
            if scenario == "healthy":
                _require(
                    excluded["eligible"] is True
                    and excluded["compiled_candidate_count"] == 1
                    and excluded["rejection_reason"] is None,
                    "production correction planning dropped a healthy peer",
                )
            else:
                _require(
                    excluded["eligible"] is False
                    and excluded["compiled_candidate_count"] == 0
                    and excluded["admitted_candidate_count"] == 0
                    and bool(excluded["rejection_reason"]),
                    "production correction planning compiled or admitted the excluded peer",
                )
            _require(
                choices[0].snap.name in eligible_names, "production correction planning selected the excluded peer"
            )
            _require(
                record["system_inventory"]["ibm_marrakesh"]["eligibility"] == peer_eligibility
                and ("ibm_marrakesh" in record["skipped_backends"]) == (scenario != "healthy"),
                "correction planning lost exclusion evidence",
            )
            _require(
                {row["proxy_metadata"]["backend"] for row in record["optimization"]["candidates"]}
                == set(eligible_names),
                "correction planning truncated the eligible candidate frontier",
            )
            pubs = live_run.execution_pubs(choices)
            _require(len(pubs) == 4 and all(pub.backend == choices[0].snap.name for pub in pubs), "PUB owner changed")
            record["groups"] = [
                live_run._choice_record(
                    choice,
                    {entry.name: [entry.ideal] for entry in choice.entries},
                    choice.snap.calibration,
                    arguments.shots,
                )
                for choice in choices
            ]
            planned_record = copy.deepcopy(record)

            def archive_current_pubs(current_choices: list[Any] = choices) -> str:
                return hashlib.sha256(
                    _archive([pub.circuit for pub in live_run.execution_pubs(current_choices)])
                ).hexdigest()

            archive = _archive([pub.circuit for pub in pubs])
            with tempfile.TemporaryDirectory(prefix="correction-approval-") as temporary:
                directory = Path(temporary)
                valid_bytes = json.dumps(record, sort_keys=True).encode()
                (directory / "record.json").write_bytes(valid_bytes)
                (directory / "isa.qpy").write_bytes(archive)
                restored_record = json.loads(valid_bytes)
                written_case = qpu_cases.write_case(directory, restored_record)
                _require(
                    written_case is not None and written_case.is_file(),
                    "production excluded-peer record failed written-case admission",
                )
                _require(
                    (directory / "record.json").read_bytes() == valid_bytes
                    and (directory / "isa.qpy").read_bytes() == archive,
                    "written-case serialization changed the retained production inputs",
                )
                invalid = copy.deepcopy(record)
                invalid["experiment_digest"] = "0" * 64
                record_bytes = json.dumps(invalid, sort_keys=True).encode()
                (directory / "record.json").write_bytes(record_bytes)
                (directory / "isa.qpy").write_bytes(archive)
                arguments.approved_record = directory
                arguments.approved_record_sha256 = hashlib.sha256(record_bytes).hexdigest()
                with patch.object(live_run, "configure_sampler", side_effect=RuntimeError("primitive prohibited")):
                    try:
                        live_run.submit(
                            service,
                            choices,
                            arguments,
                            record,
                            archive_current_pubs,
                            lambda: None,
                        )
                    except live_run.LiveRunError:
                        _require(record["state"] == "approval_required", "submission failed before case comparison")
                        _require(
                            "experiment_digest differs" in record["approved_record"]["mismatches"],
                            "submission skipped the invalid source approval gate",
                        )
                    else:
                        raise RuntimeError("submission accepted an invalid source-bound case")
                _require(
                    set(record["revalidation"][0]["system_inventory"]) == set(names),
                    "submission revalidation lost the complete snapshot inventory",
                )
                _require("submission" not in record, "invalid case created a submission ledger")
                _require(not (directory / live_run.APPROVAL_CONSUMED_FILE).exists(), "invalid approval was consumed")
            outcomes.append(
                {"scenario": scenario, "peer_status": status, "peer_pending": pending, "selected": choices[0].snap.name}
            )
            if scenario == "maintenance":
                calibration_record = copy.deepcopy(planned_record)
                previous_calibration = fresh["ibm_marrakesh"].calibration
                fresh["ibm_marrakesh"].calibration = (
                    datetime.fromisoformat(previous_calibration) + timedelta(seconds=1)
                ).isoformat()
                selected_identity = choices[0].snap.name, choices[0].snap.calibration
                with patch.object(live_run, "configure_sampler", side_effect=RuntimeError("primitive prohibited")):
                    try:
                        live_run.submit(
                            service, choices, arguments, calibration_record, archive_current_pubs, lambda: None
                        )
                    except live_run.LiveRunError:
                        _require(
                            calibration_record["state"] == "approval_required", "peer calibration bypassed renewal"
                        )
                        _require(
                            "statistical_design" in calibration_record["revalidation"][0]["reselected_groups"],
                            "excluded peer calibration was omitted from the refreshed comparison",
                        )
                    else:
                        raise RuntimeError("changed excluded peer calibration retained the old approval")
                _require(
                    (choices[0].snap.name, choices[0].snap.calibration) == selected_identity,
                    "excluded-peer calibration fixture changed selected hardware",
                )
                _require(
                    "submission" not in calibration_record, "excluded-peer calibration created a submission ledger"
                )
                fresh["ibm_marrakesh"].calibration = previous_calibration
                fresh["ibm_marrakesh"].status_msg = "active"
                fresh["ibm_marrakesh"].pending_jobs = 0
                with patch.object(live_run, "configure_sampler", side_effect=RuntimeError("primitive prohibited")):
                    try:
                        live_run.submit(service, choices, arguments, planned_record, archive_current_pubs, lambda: None)
                    except live_run.LiveRunError:
                        _require(planned_record["state"] == "approval_required", "eligibility drift bypassed renewal")
                        _require(
                            "statistical_design" in planned_record["revalidation"][0]["reselected_groups"],
                            "newly eligible peer was omitted from the refreshed comparison",
                        )
                    else:
                        raise RuntimeError("changed peer eligibility retained the old approval")
                _require("submission" not in planned_record, "eligibility drift created a submission ledger")

    fresh = {snapshot.name: copy.copy(snapshot) for snapshot in snapshots}

    def failed_refresh(unused: Any, name: str) -> live_run.Snapshot:
        if name == "ibm_marrakesh":
            raise live_run.LiveRunError("fixture coherent snapshot refresh failed")
        return fresh[name]

    with (
        patch.object(live_run, "take_snapshot", side_effect=failed_refresh),
        patch.object(live_run, "_compile", side_effect=RuntimeError("incomplete frontier reached compilation")),
    ):
        refresh_record = copy.deepcopy(record)
        refresh_record["state"] = "planned"
        for action in (
            partial(live_run.plan, service, _args(backends=names, max_pending=25)),
            partial(live_run.submit, service, choices, arguments, refresh_record, lambda: "0" * 64, lambda: None),
        ):
            try:
                action()
            except ValueError as error:
                _require("missing=['ibm_marrakesh']" in str(error), "failed refresh lost exact inventory rejection")
            else:
                raise RuntimeError("failed peer refresh was accepted")
    for snapshot in fresh.values():
        snapshot.status_msg = "maintenance"
    with (
        patch.object(live_run, "take_snapshot", side_effect=lambda unused, name, current=fresh: current[name]),
        patch.object(live_run, "_compile", side_effect=RuntimeError("inactive frontier reached compilation")),
    ):
        _reject(partial(live_run.plan, service, _args(backends=names, max_pending=25)), "all-inactive plan accepted")
    return {
        "discovery_scenarios": outcomes,
        "failed_refresh_rejections": 2,
        "all_inactive_rejections": 1,
        "peer_eligibility_drift_rejections": 1,
        "excluded_peer_calibration_drift_rejections": 1,
        "serialized_production_cases": len(scenarios),
    }


def verify() -> dict[str, Any]:
    """Compile all three bundled Targets, retain one job, and reject protocol drift."""
    snapshots = []
    for name, backend_type in (("ibm_fez", FakeFez), ("ibm_kingston", FakeKingston), ("ibm_marrakesh", FakeMarrakesh)):
        snapshot = _fake_snapshot(backend_type())
        snapshot.name = name
        snapshots.append(snapshot)
    arguments = _args()
    usage = {"usage_remaining_seconds": 100.0, "usage_limit_reached": False}
    compiled_templates = {}
    compiler = live_run._compile

    def compile_once(circuit: Any, snapshot: Any, seed: int) -> Any:
        key = snapshot.name, seed
        _require(key not in compiled_templates, "planner recompiled a binding instead of sharing one routed template")
        result = compiler(circuit, snapshot, seed)
        compiled_templates[key] = result.copy()
        return result

    with (
        patch.object(live_run, "QiskitRuntimeService", side_effect=RuntimeError("network service prohibited")),
        patch.object(live_run, "_compile", side_effect=compile_once),
    ):
        choices, metadata = correction_planning.prepare(live_run, snapshots, arguments, usage, {})
    configuration = metadata["family_configuration"]
    _require(len(compiled_templates) == 3, "planner failed to compile every supplied fresh device")
    _require(len(choices) == 1 and len(choices[0].replicas) == 1, "planner changed the single-placement design")
    choice = choices[0]
    _require(
        all(member.circuit is choice.group.members[0].circuit for member in choice.group.members), "template split"
    )
    _require([member.name for member in choice.group.members] == list(MEMBERS), "member order changed")
    _require(all(not member.mirror for member in choice.group.members), "automatic mirrors entered the experiment")
    _require(all(not entry.reference for entry in choice.entries), "isolated references entered the experiment")
    _require(len(live_run.submission_batches(choices, "dynamic", 8192)) == 1, "dynamic family split into jobs")
    _require(live_run.submission_batches(choices, "static", 8192) == [], "static job entered correction design")
    pubs = live_run.execution_pubs(choices)
    _require(len(pubs) == 4, "correction design changed its PUB count")
    stream = io.BytesIO()
    qpy.dump([pub.circuit for pub in pubs], stream)
    archive = stream.getvalue()
    _require(
        all(_archive([pub.circuit for pub in live_run.execution_pubs(choices)]) == archive for _ in range(20)),
        "final execution-PUB QPY bytes changed across repeated reconstruction and serialization",
    )
    stream.seek(0)
    restored = qpy.load(stream)
    for label, measured, known in ((1, 0, 1), (3, 3, 2)):
        actual = validate_bound_correction_pair(restored[measured], restored[known], label)
        _require(actual == configuration["circuit_pairs"][str(label)], "final-PUB archive lost pair authority")
    reconstruction_record = {
        **metadata,
        "groups": [
            live_run._choice_record(
                choice,
                {entry.name: [entry.ideal] for entry in choice.entries},
                choice.snap.calibration,
                arguments.shots,
            )
        ],
        "submission": {
            "planned_jobs": [{"backend": choice.snap.name, "kind": "dynamic", "pubs": [pub.manifest() for pub in pubs]}]
        },
    }
    archived_entries = live_run._archived_entries(
        json.loads(json.dumps(reconstruction_record)), {circuit.name: circuit for circuit in restored}
    )[choice.group.name]
    _require([entry.name for entry in archived_entries] == list(MEMBERS), "collector lost final member order")
    for original, rebuilt_entry, pub in zip(choice.entries, archived_entries, pubs, strict=True):
        expected_replica = packing.relabel(
            original.replicas[0],
            {qubit: qubit for qubit in original.replica_qubits[0]},
            pub.manifest()["components"][0]["register_prefix"],
        )
        _require(
            len(rebuilt_entry.replicas) == 1
            and rebuilt_entry.replica_qubits == original.replica_qubits
            and np.array_equal(rebuilt_entry.ideal, original.ideal)
            and np.array_equal(rebuilt_entry.weights, original.weights)
            and rebuilt_entry.replicas[0] == expected_replica,
            "collector changed final replica circuit, physical wires, ideal law, or terminal weights",
        )
    frontier = metadata["optimization"]["candidates"]
    _require(len(frontier) == 3, "planner truncated the backend frontier before comparing all devices")
    ranked = min((candidate for candidate in frontier if candidate["feasible"]), key=correction_planning._rank)
    _require(metadata["optimization"]["selected"] == ranked["name"], "planner changed its declared ordering")
    _require(configuration["hypothetical_power"]["hypothetical_power_qualified"], "fixed CP scenario became infeasible")
    _require(metadata["observable_contracts"] == [], "Hoeffding contracts replaced the dedicated CP decision")
    _require(configuration["native_mock_required"] is False, "unavailable mock service became an acquisition gate")
    _require(configuration["decision_contract"]["postexecution_schedule_gate"] is True, "schedule decision gate lost")
    _require(configuration["classical_dispatch_retained"], "label-known arm claimed dispatch removal")
    _require(configuration["model_prediction"]["shots_per_member"] == 256, "model counts adopted acquisition shots")
    _require(len(configuration["model_prediction"]["members"]) == 4, "model prediction lost an arm")
    _require("folded-correction" in FAMILY_NAMES, "family CLI registration missing")
    _require(family_contracts("folded-correction", 0.08, 0.05, 0.8) == (), "generic inference claimed CP admission")
    rebuilt = record_groups(metadata)
    _require(
        len(rebuilt) == 1 and [member.name for member in rebuilt[0].members] == list(MEMBERS), "record reconstruction"
    )
    costs = execution_contract(choices, metadata)
    _require(len(costs["selected_job_costs"]) == 1, "execution contract lost the selected dynamic job")
    json.dumps(metadata, allow_nan=False)

    def cached_compile(circuit: Any, snapshot: Any, seed: int) -> Any:
        return compiled_templates[snapshot.name, seed].copy()

    with patch.object(live_run, "_compile", side_effect=cached_compile):
        repeated_choices, repeated = correction_planning.prepare(
            live_run, list(reversed(snapshots)), _args(), usage, {}
        )
        _require(repeated["family_configuration"] == configuration, "input inventory ordering changed frozen design")
        repeated_pubs = live_run.execution_pubs(repeated_choices)
        _require(
            _archive([pub.circuit for pub in repeated_pubs]) == archive, "fresh preparation changed final QPY bytes"
        )
        _require([pub.manifest() for pub in repeated_pubs] == [pub.manifest() for pub in pubs], "manifest drift")
        _, quota_rejected = correction_planning.prepare(
            live_run, snapshots, _args(), {**usage, "usage_remaining_seconds": 39.0}, {}
        )
        _require(quota_rejected["optimization"]["selected"] is None, "planner spent the retained reserve")
        _, ceiling_rejected = correction_planning.prepare(
            live_run,
            snapshots,
            _args(
                cost_scenarios=[
                    {"name": "ceiling-exceedance", "job_overhead_seconds": 31.0, "classical_latency_us": 40.0}
                ]
            ),
            usage,
            {},
        )
        _require(ceiling_rejected["optimization"]["selected"] is None, "planner admitted a scenario above its ceiling")
    changed_protocols = (
        _args(shots=4096),
        _args(alpha=0.1),
        _args(power=0.9),
        _args(max_replicas=2),
        _args(seeds=0),
        _args(model_shots=True),
        _args(classical_latency_us=float("nan")),
        _args(optimize=True, shot_tiers=[4096, 8192]),
        _args(optimize=True, replica_tiers=[1, 2]),
        _args(max_execution_seconds=1.0),
        _args(max_total_execution_seconds=60.0),
        _args(cost_scenarios=[]),
        _args(cost_scenarios=[{"name": "lower-overhead", "job_overhead_seconds": 1.0, "classical_latency_us": 40.0}]),
        _args(cost_scenarios=[{"name": "lower-latency", "job_overhead_seconds": 4.6, "classical_latency_us": 10.0}]),
    )
    with patch.object(live_run, "_compile", side_effect=RuntimeError("protocol guard reached compilation")):
        for changed in changed_protocols:
            _reject(
                partial(correction_planning.prepare, live_run, snapshots, changed, usage, {}), "protocol drift accepted"
            )
    _reject(
        partial(correction_planning.prepare, live_run, snapshots[:2], _args(), usage, {}), "missing backend accepted"
    )
    _reject(
        partial(correction_planning.prepare, live_run, [*snapshots, snapshots[0]], _args(), usage, {}),
        "duplicate backend accepted",
    )
    unexpected = copy.copy(snapshots[-1])
    unexpected.name = "ibm_unexpected"
    _reject(
        partial(correction_planning.prepare, live_run, [*snapshots[:2], unexpected], _args(), usage, {}),
        "unexpected backend accepted",
    )
    with patch.object(live_run, "_compile", side_effect=ValueError("fixture compile rejection")):
        try:
            correction_planning.prepare(live_run, snapshots, _args(), usage, {})
        except live_run.LiveRunError as error:
            _require(
                "ibm_fez" in str(error) and "fixture compile rejection" in str(error), "frontier error lost evidence"
            )
        else:
            raise RuntimeError("empty compile frontier was accepted")
    # The quality criterion precedes lower charge; complete ties use deterministic seed/name order.
    high_quality = copy.deepcopy(frontier[0])
    low_quality = copy.deepcopy(frontier[1])
    high_quality["proxy_metadata"].update(worst_arm_quality=0.8, charge_lower_scenario_seconds=20)
    low_quality["proxy_metadata"].update(worst_arm_quality=0.7, charge_lower_scenario_seconds=5)
    _require(
        correction_planning._rank(high_quality) < correction_planning._rank(low_quality), "charge displaced quality"
    )
    discovery_frontier = _verify_complete_discovery_frontier(snapshots)
    return {
        "production_discovery_frontier": discovery_frontier,
        "offline_backend_targets": 3,
        "routed_templates": len(compiled_templates),
        "archived_pair_roundtrips": 2,
        "isolated_pubs": len(pubs),
        "collector_reconstructed_members": len(archived_entries),
        "backend_search": configuration["backend_search"],
        "finite_candidate_frontier_size": len(frontier),
        "candidate_seeds_per_backend": configuration["candidate_seeds_per_backend"],
        "selected_fake_backend": choice.snap.name,
        "protocol_rejections": len(changed_protocols) + 3,
        "cost_rejections": 2,
        "fresh_inventory_permutation_invariant": True,
        "family_configuration_sha256": hashlib.sha256(
            json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "execution_qpy_sha256": hashlib.sha256(archive).hexdigest(),
        "execution_manifest_sha256": hashlib.sha256(
            json.dumps([pub.manifest() for pub in pubs], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "scope": "bundled calibration fixtures, local simulation, and archive validation only",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

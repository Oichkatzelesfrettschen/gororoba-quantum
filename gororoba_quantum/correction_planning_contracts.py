"""Exercise three-device correction planning without a service or quantum job."""

from __future__ import annotations

import copy
import hashlib
import io
import json
from functools import partial
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import qpy
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston, FakeMarrakesh

import correction_planning
import live_run
import packing
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
    return {
        "offline_backend_targets": 3,
        "routed_templates": len(compiled_templates),
        "archived_pair_roundtrips": 2,
        "isolated_pubs": len(pubs),
        "collector_reconstructed_members": len(archived_entries),
        "backend_search": configuration["backend_search"],
        "finite_candidate_frontier_size": len(frontier),
        "candidate_seeds_per_backend": configuration["candidate_seeds_per_backend"],
        "selected_fake_backend": choice.snap.name,
        "protocol_rejections": len(changed_protocols) + 1,
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

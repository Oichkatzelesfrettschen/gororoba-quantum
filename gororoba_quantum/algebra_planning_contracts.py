"""Local integration checks for sparse static algebra jobs and dry-run guards.

FakeFez supplies a historical Target for real compilation and disjoint placement.
Service constructors are failing sentinels. Core statevector checks validate
compiled, labeled distributions after physical remapping; every scientific
member and isolated reference must occur once in the declared sparse schedule.
The fixture establishes software conformance, independently of live admission.
"""

from __future__ import annotations

import copy
import io
import json
import math
from collections import Counter
from contextlib import redirect_stderr
from dataclasses import replace
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Measure
from qiskit.circuit.library import XGate
from qiskit.transpiler import InstructionProperties, QubitProperties, Target
from qiskit_ibm_runtime.fake_provider import FakeFez

import algebra_planning
import live_run
import parallel
import qpu_planning
from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member
from qpe_diagnostics import ideal_compiled_probabilities
from rank_sector_experiments import reference_probes
from runtime_contracts import _fake_snapshot, _fixture_args


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _writers(circuit: QuantumCircuit) -> tuple[int, ...]:
    return tuple(qubits[0] for name, qubits in live_run._ops(circuit) if name == "measure")


def _compiled_entry(entry: live_run.Entry) -> float:
    _require(len(entry.replicas) == 1, f"{entry.name}: one physical realization required")
    observed = np.asarray(ideal_compiled_probabilities(entry.replicas[0]))
    error = float(np.max(np.abs(observed - entry.ideal)))
    _require(error < 1e-10, f"{entry.name}: compiled labeled ideal error {error}")
    return error


def _rank_family(snapshot: live_run.Snapshot) -> tuple[list[live_run.Choice], dict[str, Any], dict[str, Any]]:
    args = _fixture_args(
        family="rank-sector",
        optimize=False,
        optimizer_candidates=1,
        replica_tiers=[1],
        max_replicas=1,
        isolated_reference=False,
        replica_floor=0.0,
        cross_group_buffer=True,
    )
    trace: dict[str, Any] = {}
    with patch.object(live_run, "_compile", wraps=live_run._compile) as compiler:
        candidates = algebra_planning.family_candidates(live_run, [snapshot], args, trace)
        compile_count = compiler.call_count
    _require(bool(candidates), f"FakeFez rejects the rank-sector integration fixture: {trace}")
    choices, configuration = candidates[0]
    _require(len(choices) == 8 and compile_count == 8, "rank family must compile one template per lane")
    occupied: set[int] = set()
    entries: list[live_run.Entry] = []
    for sector, choice in enumerate(choices):
        _require(len(choice.replicas) == 1, "rank family replicated a lane")
        physical = set(choice.replicas[0].qubits)
        _require(bool(physical) and not physical.intersection(occupied), "rank lane placements overlap")
        occupied.update(physical)
        _require(len(choice.entries) == len(choice.group.members) == 22, "rank lane lost a source or reference")
        source_writers = _writers(choice.isas[0])
        packed_writers = _writers(choice.entries[0].packed)
        _require(len(source_writers) == len(packed_writers) == 2, "rank selector readout arity")
        _require(
            tuple(choice.replicas[0].mapping[writer] for writer in source_writers) == packed_writers,
            "rank selector readout lost its physical remapping",
        )
        for member, isa, entry in zip(choice.group.members, choice.isas, choice.entries, strict=True):
            _require(member.circuit is choice.group.members[0].circuit, "rank members lost shared template identity")
            _require(
                isa.layout.initial_index_layout(filter_ancillas=True) == choice.layout,
                f"{member.name}: compiled initial layout differs",
            )
            _require(
                _writers(isa) == source_writers and _writers(entry.packed) == packed_writers,
                f"{member.name}: selector readout differs across bindings",
            )
            _require(not live_run.compiled_violations(entry.packed, snapshot), f"{member.name}: Target violation")
            _require(
                configuration["measurement_sites"][member.name] == [[writer] for writer in packed_writers],
                f"{member.name}: measurement-site metadata differs from final writers",
            )
        by_name = {entry.name: entry for entry in choice.entries}
        for probe in reference_probes(sector):
            source = by_name[f"rank_sector_{sector}_{probe}_t1d1"]
            reference = by_name[source.name + "_reference"]
            _require(
                source.packed == reference.packed and source.replica_qubits == reference.replica_qubits,
                f"{source.name}: isolated reference changes its compiled circuit or physical patch",
            )
        entries.extend(choice.entries)
    pubs = live_run.execution_pubs(choices)
    _require(len(pubs) == 36, "rank family must retain all thirty-six rows")
    _require([len(pub.components) for pub in pubs] == [8] * 20 + [1] * 16, "rank packed and isolated row occupancy")
    _require({(pub.backend, pub.kind) for pub in pubs} == {(snapshot.name, "static")}, "rank family job boundary")
    names = [component.entry.name for pub in pubs for component in pub.components]
    _require(Counter(names) == Counter(entry.name for entry in entries), "rank member execution multiplicity")
    _require(len(names) == len(set(names)) == 176, "rank member coverage")
    _require(
        [len(batch) for batch in live_run.submission_batches(choices, "static", args.shots)] == [36],
        "rank family split its static submission batch",
    )
    manifests = [pub.manifest() for pub in pubs]
    _require(sum(len(manifest["components"]) for manifest in manifests) == 176, "rank manifest coverage")
    errors = parallel.ordered_map(_compiled_entry, entries, min_items=16)
    return (
        choices,
        configuration,
        {
            "backend_fixture": snapshot.name,
            "compiled_templates": compile_count,
            "members": len(entries),
            "pubs": len(pubs),
            "occupied_physical_qubits": len(occupied),
            "maximum_compiled_ideal_error": max(errors),
            "quality_floor_scope": (
                "zero fixture floor tests routing and bookkeeping; live fidelity admission remains separate"
            ),
        },
    )


def _rejected(operation: Any, label: str) -> None:
    try:
        operation()
    except live_run.LiveRunError, ValueError:
        return
    raise RuntimeError(f"malformed algebra boundary accepted: {label}")


def _row_boundaries(choices: list[live_run.Choice], configuration: dict[str, Any]) -> int:
    group = choices[0].group
    for rows in (
        (0,) * len(group.members),
        (-1, *range(1, len(group.members))),
        (True, *range(1, len(group.members))),
        (0,),
    ):
        _rejected(lambda rows=rows: replace(group, execution_rows=rows), "invalid group row map")
    for invalid in (True, 36.5, "36", 0, -1, 35, 37):
        definition = {**configuration, "execution_row_count": invalid}
        _rejected(
            lambda definition=definition: algebra_planning._validate_rows(live_run, choices, definition),
            "invalid declared row count",
        )
    implicit = copy.copy(choices[0])
    implicit.group = replace(implicit.group, execution_rows=None)
    _rejected(
        lambda: algebra_planning._validate_rows(live_run, [implicit, *choices[1:]], configuration),
        "implicit lane in explicit schedule",
    )
    duplicated = copy.copy(choices[0])
    duplicated.entries = [choices[0].entries[0], *choices[0].entries[1:-1], choices[0].entries[0]]
    _rejected(
        lambda: algebra_planning._validate_rows(live_run, [duplicated, *choices[1:]], configuration),
        "duplicated or missing source entry",
    )
    return 13


def _readout_controls(snapshot: live_run.Snapshot) -> int:
    logical = QuantumCircuit(2, 1)
    logical.measure(0, 0)
    members = tuple(
        Member(name, logical, np.asarray((1.0, 0.0))) for name in ("atlas_source", "readout_zero", "readout_one")
    )
    group = Group("atlas_readout_fixture", members, lambda _: {})
    routed = QuantumCircuit(snapshot.backend.num_qubits, 1)
    routed.measure(7, 0)
    choices = SimpleNamespace(group=group, isas=[routed.copy() for _ in members], snap=snapshot)
    definition = {
        "members": {
            "readout_zero": {"readout_target": "atlas_source", "readout_value": 0},
            "readout_one": {"readout_target": "atlas_source", "readout_value": 1},
        }
    }
    algebra_planning._bind_readout_controls(live_run, choices, definition)
    _require(_writers(choices.isas[1]) == _writers(choices.isas[2]) == (7,), "atlas controls followed an initial wire")
    _require(list(live_run._ops(choices.isas[1])) == [("measure", (7,))], "zero readout control prepares extra gates")
    _require(
        list(live_run._ops(choices.isas[2])) == [("x", (7,)), ("measure", (7,))],
        "one readout control prepares the wrong physical writer",
    )
    for invalid in (True, -1, 2, "1"):
        malformed = {"members": {"readout_zero": {"readout_target": "atlas_source", "readout_value": invalid}}}
        _rejected(
            lambda malformed=malformed: algebra_planning._bind_readout_controls(live_run, choices, malformed),
            "invalid readout preparation",
        )
    foreign = {"members": {"readout_zero": {"readout_target": "foreign", "readout_value": 0}}}
    _rejected(lambda: algebra_planning._bind_readout_controls(live_run, choices, foreign), "foreign readout target")
    invalid_source = copy.copy(choices)
    invalid_source.isas = list(choices.isas)
    invalid_source.isas[0] = QuantumCircuit(snapshot.backend.num_qubits, 1)
    _rejected(lambda: algebra_planning._bind_readout_controls(live_run, invalid_source, definition), "unwritten target")
    doubled = routed.copy()
    doubled.measure(8, 0)
    invalid_source.isas[0] = doubled
    _rejected(
        lambda: algebra_planning._bind_readout_controls(live_run, invalid_source, definition), "multiple target writers"
    )
    return 7


def _readout_score_target(variant: str) -> Target:
    errors = [0.20, 0.01, 0.001, 0.40]
    coherence_times = [80e-6, 250e-6, 200e-6, 40e-6]
    x_errors = [0.02, 0.001, 0.001, 0.01]
    if variant == "refreshed":
        errors[:2] = [0.001, 0.30]
        coherence_times[:2] = [300e-6, 30e-6]
        x_errors[:2] = [0.0001, 0.20]
    elif variant == "equal":
        errors[1], coherence_times[1], x_errors[1] = errors[0], coherence_times[0], x_errors[0]
    target = Target(
        num_qubits=4,
        dt=1e-9,
        qubit_properties=[QubitProperties(t1=100e-6, t2=value) for value in coherence_times],
    )
    target.add_instruction(
        Measure(),
        {(qubit,): InstructionProperties(duration=800e-9, error=error) for qubit, error in enumerate(errors)},
    )
    target.add_instruction(
        XGate(),
        {
            (qubit,): InstructionProperties(duration=40e-9, error=error)
            for qubit, error in enumerate(x_errors)
            if variant != "unsupported_x" or qubit != 1
        },
    )
    return target


def _readout_score_proxy(choices: list[live_run.Choice], configuration: dict[str, Any]) -> None:
    """The real optimizer copies the final routed score into its candidate metadata."""
    args = _fixture_args(family="ripple", optimize=False, max_total_execution_seconds=60.0)
    vars(args).update(qpu_planning.settings(args))
    contracts = (ObservableContract("source", (ObservableTerm("atlas_source", (1.0, 0.0)),), precision_half_width=0.1),)
    predictions = {entry.name: [entry.ideal] for choice in choices for entry in choice.entries}
    with (
        patch.object(qpu_planning, "family_candidates", return_value=[(choices, configuration)]),
        patch.object(qpu_planning, "family_contracts", return_value=contracts),
        patch.object(live_run, "noise_simulator", return_value=SimpleNamespace()),
        patch.object(live_run, "simulate", return_value=predictions),
    ):
        selected, metadata = qpu_planning.prepare(
            live_run, [choices[0].snap], args, {"usage_remaining_seconds": 120.0}, {}
        )
    _require(selected == choices, "optimizer changed the bound candidate fixture")
    proxy = metadata["optimization"]["candidates"][0]["proxy_metadata"]["proxy_score"]
    _require(proxy == choices[0].joint_score, "optimizer proxy retained the pre-binding score")


def _readout_candidate_ranking(snapshot: live_run.Snapshot) -> dict[str, Any]:
    """Calibrated scores reverse after binding; identity placement isolates that decision.

    The fixture supplies routed ISAs and a fixed identity placement. Production
    scoring, fusion selection, entry packing, row checks and optimizer metadata
    run unchanged. The rank-family fixture separately covers real placement.
    """
    logical = QuantumCircuit(1, 1)
    logical.measure(0, 0)
    one = QuantumCircuit(1, 1)
    one.x(0)
    one.measure(0, 0)
    members = (
        Member("atlas_source", logical, np.asarray((1.0, 0.0))),
        Member("readout_zero", logical, np.asarray((1.0, 0.0))),
        Member("readout_one", one, np.asarray((0.0, 1.0))),
    )
    group = Group("atlas_ranking_fixture", members, lambda _: {}, execution_rows=(0, 1, 2))
    definition: dict[str, Any] = {
        "execution_row_count": 3,
        "members": {
            "readout_zero": {"readout_target": "atlas_source", "readout_value": 0},
            "readout_one": {"readout_target": "atlas_source", "readout_value": 1},
        },
    }
    cases = (
        ("original", 1, 13),
        ("original", 2, 13),
        ("refreshed", 1, 37),
        ("refreshed", 2, 37),
        ("unsupported_x", 1, 37),
        ("unsupported_x", 2, 37),
        ("equal", 1, 37),
        ("equal", 2, 37),
    )
    for variant, cap, expected_seed in cases:
        target = _readout_score_target(variant)
        backend = SimpleNamespace(
            target=target,
            num_qubits=4,
            configuration=lambda: SimpleNamespace(
                dynamic_reprate_enabled=True, default_rep_delay=250e-6, rep_delay_range=(0.0, 1e-3)
            ),
        )
        refreshed = replace(snapshot, name="readout_score_fixture", backend=backend)
        active_definition = definition if variant != "equal" else {**definition, "members": {}}
        routed: list[live_run.Choice] = []
        initial_scores: dict[int, float] = {}
        for writer, seed in enumerate((37, 13)):
            source = QuantumCircuit(4, 1)
            source.measure(writer, 0)
            control_writer = 2 if variant == "equal" else writer + 2
            zero = QuantumCircuit(4, 1)
            zero.measure(control_writer, 0)
            prepared_one = QuantumCircuit(4, 1)
            prepared_one.x(control_writer)
            prepared_one.measure(control_writer, 0)
            isas = [source, zero, prepared_one]
            scores = [live_run.layout_score(isa, target) for isa in isas]
            joint = math.exp(sum(math.log(score) for score in scores) / len(scores))
            initial_scores[seed] = joint
            routed.append(live_run.Choice(group, refreshed, seed, [control_writer], isas, scores, joint))
        _require(initial_scores[37] >= initial_scores[13], "fixture lost its original candidate ordering")

        def select_fixture(
            selected_group: Group,
            snapshots: list[live_run.Snapshot],
            seeds: int,
            trace: dict[str, Any],
            *,
            expected_snapshot: live_run.Snapshot = refreshed,
            compiled: list[live_run.Choice] = routed,
        ) -> list[live_run.Choice]:
            del seeds
            _require(selected_group is group and snapshots == [expected_snapshot], "fixture received another snapshot")
            trace[group.name] = {
                expected_snapshot.name: [
                    {"seed": choice.seed, "layout": choice.layout, "joint_score": choice.joint_score}
                    for choice in compiled
                ]
            }
            return compiled

        def identity_placement(
            choices: list[live_run.Choice], policy: live_run.ReplicaPolicy, cache: Any = None
        ) -> dict[str, Any]:
            del cache
            for choice in choices:
                used = sorted({qubit for isa in choice.isas for qubit in live_run._physical(isa)})
                replica = live_run.Replica(0, {qubit: qubit for qubit in used}, choice.member_scores[0])
                live_run._set_entries(choice, [replica], policy)
            return {"allocation": "identity scoring fixture"}

        args = _fixture_args(
            family="ripple", optimize=False, optimizer_candidates=cap, replica_tiers=[1], max_replicas=1
        )
        trace: dict[str, Any] = {}
        with (
            patch.object(algebra_planning, "family_definition", return_value=([group], active_definition)),
            patch.object(live_run, "select_candidates", side_effect=select_fixture),
            patch.object(live_run, "allocate_fusion_replicas", side_effect=identity_placement),
            patch.object(live_run, "select_fusion_choices", wraps=live_run.select_fusion_choices) as fusion,
        ):
            families = algebra_planning.family_candidates(live_run, [refreshed], args, trace)
        _require(len(families) == 1, f"bound candidate rejected a valid backend: {variant}, cap={cap}, {trace}")
        choices, configuration = families[0]
        choice = choices[0]
        _require(choice.seed == expected_seed, f"bound scores failed to rerank before cap/fusion: {variant}, cap={cap}")
        passed = fusion.call_args.args[0][0]
        _require(len(passed) == (1 if variant == "unsupported_x" else cap), "fusion received the wrong candidate cap")
        _require(passed[0].seed == expected_seed, "fusion received pre-binding candidate order")
        rows = trace["algebra_backends"][refreshed.name][group.name][refreshed.name]
        historical = [row for row in rows if "pre_readout_binding_joint_score" in row]
        final = [row for row in rows if row.get("stage") == "readout_bound_scoring"]
        _require(len(historical) == len(final) == 2, "candidate trace omitted a candidate before truncation")
        _require(
            all(row["pre_readout_binding_joint_score"] == initial_scores[row["seed"]] for row in historical),
            "candidate trace changed its original scoring evidence",
        )
        _require(all("joint_score" not in row for row in historical), "candidate trace mislabeled an old score")
        for candidate in routed:
            final_row = next(row for row in final if row["seed"] == candidate.seed)
            if variant == "unsupported_x" and candidate.seed == 13:
                _require("rejected" in final_row and "joint_score" not in final_row, "invalid bound X kept a score")
                continue
            expected_scores = [live_run.layout_score(isa, target) for isa in candidate.isas]
            expected_joint = math.exp(sum(math.log(score) for score in expected_scores) / len(expected_scores))
            _require(candidate.member_scores == final_row["member_scores"] == expected_scores, "stale member scores")
            _require(candidate.joint_score == final_row["joint_score"] == expected_joint, "stale joint candidate score")
            if variant != "equal":
                writer = _writers(candidate.isas[0])[0]
                _require(list(live_run._ops(candidate.isas[1])) == [("measure", (writer,))], "zero control writer")
                _require(
                    list(live_run._ops(candidate.isas[2])) == [("x", (writer,)), ("measure", (writer,))],
                    "one control writer",
                )
        if variant == "original":
            _require(routed[1].joint_score > routed[0].joint_score, "fixture lost its post-binding rank inversion")
        if variant == "equal":
            _require(routed[0].joint_score == routed[1].joint_score == initial_scores[37], "unbound scores changed")
        selection = configuration["placement"]["candidate_selection"]
        _require(selection["selected"][0]["joint_score"] == choice.joint_score, "fusion recorded stale scores")
        _require(
            selection["combined_log_score"] == math.log(choice.joint_score), "fusion priority retained stale score"
        )
        _require(
            [live_run.layout_score(entry.packed, target) for entry in choice.entries] == choice.member_scores,
            "execution entries differ from the scored identity-placement ISAs",
        )
        if variant == "original" and cap == 1:
            _readout_score_proxy(choices, configuration)
    return {"calibrated_ranking_cases": len(cases), "optimizer_proxy_checks": 1, "service_calls": 0}


def _cli_boundaries() -> int:
    base = [
        "--native-dry-run",
        "--family",
        "rank-sector",
        "--out",
        "unused-fixture-output",
        "--max-execution-seconds",
        "60",
        "--max-total-execution-seconds",
        "60",
    ]
    cases = [
        base + ["--submit"],
        base + ["--collect", "unused-record"],
        base + ["--preserve-raw", "unused-record"],
        ["--native-dry-run"],
        ["--native-dry-run", "--family", "rank-sector"],
        ["--native-dry-run", "--out", "unused-fixture-output"],
        ["--native-dry-run", "--family", "invalid", "--out", "unused-fixture-output"],
        base + ["--max-replicas", "2"],
        base + ["--optimize", "--replica-tiers", "1,2"],
    ]
    for arguments in cases:
        with redirect_stderr(io.StringIO()):
            try:
                live_run.main(arguments)
            except SystemExit as error:
                _require(error.code == 2, f"CLI arguments exited with a non-parser error: {arguments}")
            else:
                raise RuntimeError(f"native dry-run boundary accepted: {arguments}")
    return len(cases)


def audit_algebra_planning() -> dict[str, Any]:
    with patch.object(
        live_run, "QiskitRuntimeService", side_effect=RuntimeError("service constructor forbidden")
    ) as service:
        cli_rejections = _cli_boundaries()
        snapshot = _fake_snapshot(FakeFez())
        readout_rejections = _readout_controls(snapshot)
        readout_ranking = _readout_candidate_ranking(snapshot)
        choices, configuration, rank = _rank_family(snapshot)
        row_rejections = _row_boundaries(choices, configuration)
        _require(service.call_count == 0, "local algebra contract attempted a service constructor")
    return {
        "schema": "static-algebra-planning-contracts-v1",
        "qpu_executed": False,
        "service_constructor_calls": 0,
        "rank_family": rank,
        "readout_candidate_ranking": readout_ranking,
        "rejected_cli_invocations": cli_rejections,
        "rejected_readout_inputs": readout_rejections,
        "rejected_schedule_inputs": row_rejections,
    }


def main() -> int:
    print(json.dumps(audit_algebra_planning(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

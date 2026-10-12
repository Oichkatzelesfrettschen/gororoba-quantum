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
from collections import Counter
from contextlib import redirect_stderr
from dataclasses import replace
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime.fake_provider import FakeFez

import algebra_planning
import live_run
import parallel
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
    except (live_run.LiveRunError, ValueError):
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
        choices, configuration, rank = _rank_family(snapshot)
        row_rejections = _row_boundaries(choices, configuration)
        _require(service.call_count == 0, "local algebra contract attempted a service constructor")
    return {
        "schema": "static-algebra-planning-contracts-v1",
        "qpu_executed": False,
        "service_constructor_calls": 0,
        "rank_family": rank,
        "rejected_cli_invocations": cli_rejections,
        "rejected_readout_inputs": readout_rejections,
        "rejected_schedule_inputs": row_rejections,
    }


def main() -> int:
    print(json.dumps(audit_algebra_planning(), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

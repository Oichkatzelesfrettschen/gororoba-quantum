"""Preregister raw ripple observables and verify the static schedule locally.

The contracts retain arbitrary dependence among components of a single PUB
shot. Per-label precision includes every canonical atlas point and every
original Design C ladder outcome. Packing comparisons use the identical
template on the same lane, with an isolated workload as the second arm.
"""

from __future__ import annotations

import io
from collections import Counter, defaultdict
from copy import copy
from dataclasses import replace
from typing import Any
from unittest.mock import patch

import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Parameter
from qiskit.quantum_info import Operator, Statevector

from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member
from ripple_dynamics import PAIRS, walk_circuit
from ripple_experiments import _definitions


def _endpoints(
    groups: list[Group], configuration: dict[str, Any]
) -> list[tuple[str, tuple[ObservableTerm, ...], bool, bool]]:
    members = {member.name: member for group in groups for member in group.members}
    metadata = configuration["members"]
    endpoints: list[tuple[str, tuple[ObservableTerm, ...], bool, bool]] = []
    crossover = tuple(
        ObservableTerm(name, (0.5,) + (0.0,) * 15, 1 if item["pair"] == list(PAIRS[0]) else -1)
        for name, item in metadata.items()
        if item["kind"] == "walk" and item["role"] == "packed" and item["depth"] == 4
    )
    endpoints.append(("ripple_depth4_class_return_contrast", crossover, True, True))
    atlas: dict[tuple[int, int], dict[int, str]] = defaultdict(dict)
    for name, item in metadata.items():
        member = members[name]
        if item["role"] == "atlas":
            atlas[item["kite"], item["edge_index"]][item["phase_index"]] = name
            endpoints.append((name + "_p0", (ObservableTerm(name, (1.0, 0.0)),), False, True))
        if item["kind"] == "walk" and item["role"] == "packed":
            endpoints.append((name + "_return", (ObservableTerm(name, (1.0,) + (0.0,) * 15),), False, True))
        if item["role"] == "ladder":
            for outcome in range(len(member.ideal)):
                values = tuple(float(index == outcome) for index in range(len(member.ideal)))
                endpoints.append((name + f"_label{outcome}", (ObservableTerm(name, values),), False, True))
        if item["role"] == "isolated":
            packed_name = item["packed_member"]
            weights = (
                tuple(float(value) for value in member.ideal)
                if item["kind"] == "ladder"
                else (1.0,) + (0.0,) * (len(member.ideal) - 1)
            )
            endpoints.append(
                (
                    name + "_packed_difference",
                    (ObservableTerm(packed_name, weights), ObservableTerm(name, weights, -1)),
                    False,
                    True,
                )
            )
        if item["role"] == "readout":
            values = tuple(float(value) for value in member.ideal)
            endpoints.append((name + "_correct", (ObservableTerm(name, values),), False, True))
    for (kite, edge), phases in sorted(atlas.items()):
        sign = metadata[phases[0]]["sign"]
        dark, bright = (0, 4) if sign > 0 else (4, 0)
        endpoints.append(
            (
                f"ripple_kite{kite}_edge{edge}_bright_minus_dark",
                (ObservableTerm(phases[bright], (1.0, 0.0)), ObservableTerm(phases[dark], (1.0, 0.0), -1)),
                True,
                False,
            )
        )
    return endpoints


def ripple_contracts(precision: float, alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Simultaneous raw intervals, class contrast, and signed edge visibility."""
    groups, configuration = _definitions()
    endpoints = _endpoints(groups, configuration)
    return tuple(
        ObservableContract(
            name,
            terms,
            minimum_effect=0.0 if directional else None,
            precision_half_width=precision if interval else None,
            alpha=alpha / len(endpoints),
            power=power,
        )
        for name, terms, directional, interval in endpoints
    )


def _verify_sparse_runtime() -> None:
    """Exercise sparse fusion and shared-template compilation on a local fake Target."""
    import live_run
    from runtime_contracts import FakeFez, _fake_snapshot, _synthetic_fusion_choice

    snapshot = _fake_snapshot(FakeFez())
    source = QuantumCircuit(1, 1)
    source.measure(0, 0)
    ideal = np.array([1.0, 0.0])
    left = Group(
        "sparse_left",
        tuple(Member(f"left_{index}", source, ideal) for index in range(2)),
        lambda _: {},
        execution_rows=(0, 2),
    )
    right = Group(
        "sparse_right",
        tuple(Member(f"right_{index}", source, ideal) for index in range(2)),
        lambda _: {},
        execution_rows=(0, 1),
    )
    physical = sorted(set(range(snapshot.capabilities.num_qubits)) - snapshot.excluded_qubits.keys())
    choices = [
        _synthetic_fusion_choice(group, snapshot, physical[index], False) for index, group in enumerate((left, right))
    ]
    for choice in choices:
        choice.entries = [entry for entry in choice.entries if not entry.reference]
    pubs = live_run.execution_pubs(choices)
    observed = [[component.entry.name for component in pub.components] for pub in pubs]
    if observed != [["left_0", "right_0"], ["right_1"], ["left_1"]]:
        raise ValueError(f"sparse rows changed component membership: {observed}")
    for defect in ("reference", "implicit", "member-order"):
        changed = [copy(choice) for choice in choices]
        if defect == "reference":
            entry = copy(changed[0].entries[0])
            entry.reference = True
            changed[0].entries = [entry, *changed[0].entries[1:]]
        elif defect == "implicit":
            changed[0].group = replace(changed[0].group, execution_rows=None)
        else:
            changed[0].entries = list(reversed(changed[0].entries))
        try:
            live_run.execution_pubs(changed)
        except live_run.LiveRunError:
            continue
        raise ValueError(f"sparse fusion accepted {defect}")

    angle = Parameter("cache_angle")
    primary = QuantumCircuit(1, 1)
    primary.rx(angle, 0)
    primary.measure(0, 0)
    secondary = QuantumCircuit(1, 1)
    secondary.ry(angle, 0)
    secondary.measure(0, 0)
    group = Group(
        "shared_template",
        (
            Member("cache_primary", primary, ideal, {angle: 0.0}),
            Member("cache_second", secondary, ideal, {angle: 0.0}),
            Member("cache_third", secondary, ideal, {angle: 1.0}),
        ),
        lambda _: {},
    )
    with patch.object(live_run, "_compile", wraps=live_run._compile) as compiler:
        choices = live_run.select_candidates(group, [snapshot], 1, {})
    calls = Counter(id(call.args[0]) for call in compiler.call_args_list)
    if calls != Counter({id(primary): 1, id(secondary): 1}):
        raise ValueError(f"shared circuit templates compiled repeatedly: {calls}")
    for choice in choices:
        writers = [[qubits for name, qubits in live_run._ops(isa) if name == "measure"] for isa in choice.isas[1:]]
        if writers[0] != writers[1]:
            raise ValueError("shared template bindings changed their measured output sites")


def _verify_archived_weights() -> None:
    """Retain explicit scores through QPY replay and inherit automatic reference scores."""
    import live_run
    import variance
    from runtime_contracts import FakeFez, _fake_snapshot, _synthetic_fusion_choice

    snapshot = _fake_snapshot(FakeFez())
    physical = next(qubit for qubit in range(snapshot.capabilities.num_qubits) if qubit not in snapshot.excluded_qubits)
    source = QuantumCircuit(1, 1)
    source.measure(0, 0)
    ideal = np.array([1.0, 0.0])
    weighted_score = np.array([0.0, 1.0])
    explicit = Group(
        "archive_explicit",
        (
            Member("archive_base", source, ideal, weights=weighted_score),
            Member("archive_base_isolated", source, ideal),
            Member("archive_weighted_isolated", source, ideal, weights=weighted_score),
        ),
        lambda _: {},
        execution_rows=(0, 1, 2),
    )
    automatic = Group(
        "archive_automatic",
        (Member("archive_automatic_base", source, ideal, weights=weighted_score),),
        lambda _: {},
    )
    for group in (explicit, automatic):
        choice = _synthetic_fusion_choice(group, snapshot, physical, False)
        if group.execution_rows is not None:
            choice.entries = [entry for entry in choice.entries if not entry.reference]
        member_weights = {member.name: member.weights for member in group.members}
        for entry in choice.entries:
            entry.weights = group.members[0].weights if entry.reference else member_weights[entry.name]
        pubs = live_run.execution_pubs([choice])
        archive = io.BytesIO()
        qpy.dump([pub.circuit for pub in pubs], archive)
        archive.seek(0)
        circuits = {circuit.name: circuit for circuit in qpy.load(archive)}
        record = {
            "groups": [
                {
                    "group": group.name,
                    "members": [
                        {
                            "name": entry.name,
                            "reference": entry.reference,
                            "ideal": entry.ideal.tolist(),
                            "replica_prefixes": entry.prefixes,
                            "replica_qubits": entry.replica_qubits,
                        }
                        for entry in choice.entries
                    ],
                }
            ],
            "submission": {
                "planned_jobs": [{"backend": snapshot.name, "kind": "static", "pubs": [pub.manifest() for pub in pubs]}]
            },
        }
        with (
            patch.object(live_run, "experiment_groups", return_value=[]),
            patch.object(live_run, "record_groups", return_value=[group]),
        ):
            restored = live_run._archived_entries(record, circuits)[group.name]
        distribution = np.array([0.25, 0.75])
        for original, replayed in zip(choice.entries, restored, strict=True):
            if original.weights is None:
                if replayed.weights is not None:
                    raise ValueError(f"{original.name}: archive replaced an explicit default score")
            elif replayed.weights is None or not np.array_equal(original.weights, replayed.weights):
                raise ValueError(f"{original.name}: archive changed declared score weights")
            if variance.score(distribution, original.ideal, original.weights) != variance.score(
                distribution, replayed.ideal, replayed.weights
            ):
                raise ValueError(f"{original.name}: archive changed the score mean or variance")


def verify_ripple_family() -> dict[str, Any]:
    """Check every source circuit, exact matching pair, sparse row, and contract."""
    groups, configuration = _definitions()
    members = {member.name: member for group in groups for member in group.members}
    metadata = configuration["members"]
    if len(groups) != 12 or len(configuration["rows"]) != 146 or len(members) != 929:
        raise ValueError("ripple family must have 12 lanes, 146 rows, and 929 unique members")
    if set(members) != set(metadata):
        raise ValueError("ripple metadata and members differ")
    assignment = {}
    for group in groups:
        if group.execution_rows is None:
            raise ValueError("ripple groups require explicit execution rows")
        for member, row in zip(group.members, group.execution_rows, strict=True):
            assignment[member.name] = row
            if row != metadata[member.name]["execution_row"]:
                raise ValueError("member row differs from its retained metadata")
    for row in configuration["rows"]:
        if any(assignment[name] != row["row"] for name in row["members"]):
            raise ValueError("execution row contains a foreign member")
        if row["role"] == "isolated" and len(row["members"]) != 1:
            raise ValueError("isolated control has companion work")
    canonical = [item for item in metadata.values() if item["role"] == "atlas"]
    coverage = Counter((item["kite"], item["edge_index"], item["phase_index"]) for item in canonical)
    if len(coverage) != 672 or set(coverage.values()) != {1}:
        raise ValueError("atlas must cover all 84 edges at eight phases exactly once")
    for kite in range(1, 8):
        if {item["lane"] for item in canonical if item["kite"] == kite} != set(range(7)):
            raise ValueError("cyclic atlas assignment must visit every lane")
    for rows in configuration["matched_walk_rows"].values():
        if len(rows) != 2 or rows[1] != rows[0] + 1:
            raise ValueError("matched walk pair must remain adjacent")
        companions = []
        for row in rows:
            companions.append(
                sorted(
                    (metadata[name]["lane"], metadata[name]["template_key"], metadata[name]["phase_index"])
                    for name in configuration["rows"][row]["members"]
                    if metadata[name]["kind"] == "atlas"
                )
            )
        if companions[0] != companions[1] or len(companions[0]) != 7:
            raise ValueError("walk crossover changed its atlas companions")
        for lane in range(2):
            pairs = [
                item["pair"]
                for item in metadata.values()
                if item["kind"] == "walk"
                and item["role"] == "packed"
                and item["lane"] == lane
                and item["execution_row"] in rows
            ]
            if sorted(pairs) != sorted(map(list, PAIRS)):
                raise ValueError("walk crossover must place both classes on both patches")

    checked = 0
    maximum_error = 0.0
    seen: set[tuple[int, tuple[tuple[str, float], ...]]] = set()
    for name, member in members.items():
        binding = member.binding or {}
        key = id(member.circuit), tuple(sorted((str(parameter), value) for parameter, value in binding.items()))
        circuit = member.circuit.assign_parameters(binding) if binding else member.circuit
        item = metadata[name]
        if item["role"] == "isolated":
            packed = members[item["packed_member"]]
            if member.circuit is not packed.circuit or binding != (packed.binding or {}):
                raise ValueError("isolated reference differs from the packed source template or binding")
        if key in seen:
            continue
        seen.add(key)
        unmeasured = circuit.remove_final_measurements(inplace=False)
        state = Statevector(unmeasured)
        observed = state.probabilities([4]) if item["kind"] == "atlas" else state.probabilities()
        error = float(np.max(np.abs(observed - member.ideal)))
        maximum_error = max(maximum_error, error)
        if error > 1e-10:
            raise ValueError(f"{name}: source circuit differs from its independent ideal by {error}")
        if item["kind"] == "walk" and item["role"] == "packed":
            operator = Operator(unmeasured).data
            expected = Operator(walk_circuit(tuple(item["pair"]), item["depth"])).data
            if not np.allclose(operator, expected, atol=1e-10, rtol=0):
                raise ValueError(f"{name}: bound union template differs from the full walk operator")
        checked += 1
    endpoints = _endpoints(groups, configuration)
    if len({name for name, *_ in endpoints}) != len(endpoints):
        raise ValueError("observable endpoint names must be unique")
    crossover = endpoints[0][1]
    contrast = sum(term.sign * float(members[term.member].ideal @ np.asarray(term.values)) for term in crossover)
    if contrast != 5 / 16 or len(crossover) != 4:
        raise ValueError("balanced walk class contrast must equal 5/16")
    invalid_rows = [
        (-1,) * len(groups[0].members),
        (True,) * len(groups[0].members),
        (0,) * len(groups[0].members),
        (0,),
    ]
    for invalid in invalid_rows:
        try:
            replace(groups[0], execution_rows=invalid)
        except ValueError:
            continue
        raise ValueError("invalid explicit execution rows were accepted")
    mirrored = replace(groups[0].members[0], mirror=True)
    try:
        replace(groups[0], members=(mirrored, *groups[0].members[1:]))
    except ValueError:
        pass
    else:
        raise ValueError("explicit execution rows accepted an automatic mirror")
    _verify_sparse_runtime()
    _verify_archived_weights()
    return {
        "groups": len(groups),
        "rows": len(configuration["rows"]),
        "members": len(members),
        "distinct_source_circuits": checked,
        "observable_endpoints": len(endpoints),
        "maximum_source_probability_error": maximum_error,
        "depth4_contrast": contrast,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(verify_ripple_family(), sort_keys=True))

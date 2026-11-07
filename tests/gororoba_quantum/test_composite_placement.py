"""Contracts of the per-placement composite PUB: one fused PUB whose placements run different circuits.

A group with ``per_placement_laws`` lets each body of a patterned member keep its own ideal law, compiled body and
coupler subset. The contracts cover the group validation, the placement pattern that covers every body, the
refusals of a body that leaves its placement and of replicas that share a qubit or break the one-qubit buffer, the
per-replica ideal in scoring, records and archives, and the byte identity of the plans and records of every group
that does not opt in. The synthetic group takes three blocks of the 64-dimensional operands of pathion_wide_coset
on FakeFez.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import rustworkx as rx
from qiskit import QuantumCircuit, qpy
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston

import experiments
import idle_penalty as ip
import idle_readout as ir
import live_run
import packing
import pathion_coset_block as pcb
import pathion_wide_coset as pw
import qpu_planning
from diagnostic_controls import readout_delay_group
from experiments import Group, Member
from packing import Replica
from runtime_contracts import _fake_snapshot

ROOT = Path(__file__).resolve().parents[2]
BLOCKS = 3
PAIRS = 3
# sha256 prefixes of the offline plan of each group before per-placement laws existed (FakeFez, two seeds, three
# replicas): the digest covers choice_structure, every fused-PUB manifest and the archive bytes.
PLAN_DIGESTS = {
    "design_a": ("fd2b1ecfcc7badf4", "fe1fa93744567621"),
    "design_c_8_1_4": ("0842747b6e0275a1", "56a34676f8fd2ba5"),
    "readout_delay": ("40a929a918455daa", "03ec79e41df9514a"),
}
# The patterned synthetic group of test_idle_readout on its three pinned FakeKingston pairs.
IDLE_DIGEST = ("374c47952a5cf9b4", "13e8eae25de87a4c")


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _plan_digest(choice: live_run.Choice) -> tuple[str, str]:
    pubs = live_run.execution_pubs([choice])
    body = json.dumps(
        [live_run._json_value(live_run.choice_structure(choice)), [live_run._json_value(p.manifest()) for p in pubs]],
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(body.encode()).hexdigest()[:16], hashlib.sha256(live_run.archive_bytes([choice])).hexdigest()[
        :16
    ]


def _existing_group(name: str) -> Group:
    builders = {
        "design_a": experiments._design_a,
        "design_c_8_1_4": lambda: experiments._associator_spectrum(8, 1, 4),
        "readout_delay": readout_delay_group,
    }
    group = builders[name]()
    _expect(group.name == name, f"{name}: built {group.name}")
    return group


@pytest.mark.parametrize("name", sorted(PLAN_DIGESTS))
def test_groups_without_per_placement_laws_plan_byte_identically(name: str) -> None:
    group = _existing_group(name)
    _expect(not group.per_placement_laws and group.placed_summary is None and not group.body_bindings, name)
    candidates = live_run.select_candidates(group, [_fake_snapshot(FakeFez())], 2, {})
    choice = candidates[0]
    live_run.build_entries(choice, live_run.ReplicaPolicy(None, 3, True, True))
    _expect(_plan_digest(choice) == PLAN_DIGESTS[name], f"{name}: plan changed to {_plan_digest(choice)}")
    for entry in choice.entries:
        fields = live_run._member_fields(entry)
        _expect("replica_ideals" not in fields and "replica_cz" not in fields, f"{name}: new record fields")


def _pinned_paths() -> list[list[int]]:
    case = (ROOT / "results/live/IDLE_PENALTY_REPEAT_CASE.md").read_text()
    pin = next(line for line in case.splitlines() if line.startswith("ibm_kingston:"))
    return [[int(q) for q in path.split(",")] for path in pin.split(":", 1)[1].split("/")][:PAIRS]


def _idle_group() -> Group:
    circuits = {name: (circuit, ideal) for name, circuit, ideal in ip.idle_penalty_circuits()}
    quiet = {name: (circuit, ideal) for name, circuit, ideal in ir.readout_templates()}
    during, quiet_x = circuits["idle_meas_during_x"], quiet["idle_meas_quiet_x"]
    members = [Member("idle_cz_kick", *circuits["idle_cz_kick"]), Member("idle_meas_during_x", *during)]
    bodies = ("idle_meas_during_x",) + ("idle_meas_quiet_x",) * 2
    members.append(Member("reads_first", during[0], during[1], replica_bodies=bodies))
    bodies = ("idle_meas_quiet_x",) * 2 + ("idle_meas_during_x",)
    members.append(Member("reads_last", quiet_x[0], quiet_x[1], replica_bodies=bodies))
    return Group(
        "tiny_readout",
        tuple(members),
        lambda _: {},
        routed_violations=ir.routed_readout_violations,
        body_templates=(("idle_meas_quiet_x", quiet_x[0], quiet_x[1]),),
    )


def test_a_shared_law_patterned_group_plans_byte_identically() -> None:
    paths = _pinned_paths()
    group = _idle_group()
    log: dict[str, Any] = {}
    candidates = live_run.select_candidates(group, [_fake_snapshot(FakeKingston())], 1, log, paths[0])
    choices, _ = live_run.pinned_campaign_choices(
        [candidates], live_run.ReplicaPolicy(None, PAIRS, True, True), log, paths
    )
    _expect(_plan_digest(choices[0]) == IDLE_DIGEST, f"idle plan changed to {_plan_digest(choices[0])}")


# --- a three-block composite group -------------------------------------------------------------------------------


def _blocks() -> list[pcb.Block]:
    """Block k0 of the null operand n64 (routes over three couplers), its block k4 (two couplers) and block k4 of the
    target o64 (a different ideal law)."""
    null, target = pw.BY_KEY["n64"].blocks(), pw.BY_KEY["o64"].blocks()
    return [null[0], null[1], target[1]]


def _placed(placement: int, dist: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    est = pcb.output_contrast(dist["block_plus"], dist["block_minus"])
    reference = pcb.output_contrast(ideal["block_plus"], ideal["block_minus"])
    return {"placement": float(placement), "contrast": float(est.sum() / 2.0), "ideal": float(reference.sum() / 2.0)}


def _group(**changes: Any) -> Group:
    blocks = _blocks()
    templates, bindings, bodies = [], [], {"plus": [], "minus": []}
    for index, block in enumerate(blocks):
        template = pcb.block_template(block)
        template.name = f"syn_{index}"
        for arm, phase in (("minus", 0.0), ("plus", np.pi)):
            name = f"syn_{index}_{arm}"
            templates.append((name, template, pcb.block_law_closed_form(block, arm == "plus")))
            bindings.append((name, {pcb.ORIENTATION: phase}))
            bodies[arm].append(name)
    by_name = {name: (circuit, ideal) for name, circuit, ideal in templates}
    binding = dict(bindings)
    members = tuple(
        Member(
            f"block_{arm}",
            by_name[bodies[arm][0]][0],
            by_name[bodies[arm][0]][1],
            binding[bodies[arm][0]],
            replica_bodies=tuple(bodies[arm]),
        )
        for arm in ("minus", "plus")
    )
    fields: dict[str, Any] = {
        "body_templates": tuple(templates),
        "body_bindings": tuple(bindings),
        "per_placement_laws": True,
        "placed_summary": _placed,
    }
    members = changes.pop("members", members)
    return Group("synthetic_composite", members, lambda dist: {}, **(fields | changes))


@pytest.fixture(scope="module")
def planned() -> Iterator[live_run.Choice]:
    group = _group()
    candidates = live_run.select_candidates(group, [_fake_snapshot(FakeFez())], 1, {})
    choice = candidates[0]
    live_run.build_entries(choice, live_run.ReplicaPolicy(0.5, BLOCKS, True, True))
    yield choice


def test_group_validation_admits_per_placement_laws_and_refuses_each_inconsistency() -> None:
    group = _group()
    _expect(group.members[0].replica_bodies is not None, "the first member is patterned under the opt-in")
    plain = {"per_placement_laws": False, "placed_summary": None}
    with pytest.raises(ValueError, match="first member fixes the placement"):
        dataclasses.replace(group, **plain)
    lead = Member("lead", QuantumCircuit(4, 4), group.members[0].ideal)
    with pytest.raises(ValueError, match="differs in ideal law"):
        dataclasses.replace(group, members=(lead, *group.members), **plain)
    with pytest.raises(ValueError, match="placed summary needs per-placement laws"):
        dataclasses.replace(Group("g", (lead,), lambda d: {}), placed_summary=_placed)
    with pytest.raises(ValueError, match="at most once"):
        dataclasses.replace(group, body_bindings=(*group.body_bindings, group.body_bindings[0]))
    with pytest.raises(ValueError, match="at most once"):
        dataclasses.replace(group, body_bindings=(("absent", {}),))
    with pytest.raises(ValueError, match="need a patterned member"):
        Group("g", (lead,), lambda d: {}, per_placement_laws=True)
    arm = group.members[1]
    shorter = dataclasses.replace(arm, name="short", replica_bodies=(arm.replica_bodies or ())[:2])
    with pytest.raises(ValueError, match="one body per placement"):
        dataclasses.replace(group, members=(group.members[0], shorter))
    wrong = dataclasses.replace(arm, name="wrong", ideal=np.roll(arm.ideal, 1))
    with pytest.raises(ValueError, match="ideal differs from that of its first body"):
        dataclasses.replace(group, members=(group.members[0], wrong))


def test_the_placement_pattern_covers_every_body_and_each_body_keeps_its_own_couplers(planned: live_run.Choice) -> None:
    entry = planned.entries[0]
    bases = live_run._entry_bases(planned)
    union = packing.pattern(op for isa in live_run._pattern_isas(bases) for op in live_run._ops(isa))
    patterns = [
        packing.pattern(live_run._ops(body))
        for body in live_run._compiled_bodies(planned, entry.name, entry.replica_bodies or (), True)
    ]
    _expect(len({(tuple(q), tuple(sorted(e))) for q, e in patterns}) > 1, "the bodies share one coupler set")
    for qubits, edges in patterns:
        _expect(set(qubits) <= set(union[0]) and edges <= union[1], "a body leaves the placement pattern")
    with pytest.raises(live_run.LiveRunError, match="touches another qubit set or coupler"):
        live_run._compiled_bodies(planned, entry.name, entry.replica_bodies or (), False)


def test_each_placement_carries_its_own_body_ideal_digest_and_cz_count(planned: live_run.Choice) -> None:
    group = planned.group
    ideals = {name: ideal for name, _, ideal in group.body_templates}
    for entry in planned.entries:
        if entry.reference:
            fields = live_run._member_fields(entry)
            _expect("replica_ideals" not in fields and "replica_bodies" not in fields, "reference gained body fields")
            continue
        _expect(entry.replica_ideals is not None and len(entry.replica_ideals) == BLOCKS, f"{entry.name}: ideals")
        for k, body in enumerate(entry.replica_bodies or ()):
            _expect(np.array_equal(entry.ideal_at(k), ideals[body]), f"{entry.name}: replica {k} ideal")
        fields = live_run._member_fields(entry)
        _expect(len(fields["replica_ideals"]) == BLOCKS and len(fields["replica_cz"]) == BLOCKS, "record fields")
        _expect(fields["replica_cz"] == [r.count_ops().get("cz", 0) for r in entry.replicas], "cz per replica")
        _expect(len(set(entry.body_digests or ())) == BLOCKS, f"{entry.name}: bodies are not distinct")
        _expect(len({tuple(law) for law in entry.replica_ideals}) > 1, f"{entry.name}: every ideal is the same")
    minus, plus = (next(e for e in planned.entries if e.name == f"block_{arm}") for arm in ("minus", "plus"))
    _expect(
        [r.count_ops().get("cz", 0) for r in minus.replicas] == [r.count_ops().get("cz", 0) for r in plus.replicas],
        "the arms of a block route to different CZ counts",
    )


def test_every_compiled_replica_equals_the_ideal_of_its_own_body(planned: live_run.Choice) -> None:
    qpu_planning.check_compiled_ideals(live_run, [planned])
    swapped = copy.copy(planned)
    entry = planned.entries[0]
    ideals = (entry.replica_ideals or ())[::-1]
    swapped.entries = [live_run.Entry(**{**entry.__dict__, "replica_ideals": ideals}), *planned.entries[1:]]
    with pytest.raises(live_run.LiveRunError, match="compiled labeled ideal differs"):
        qpu_planning.check_compiled_ideals(live_run, [swapped])


def test_scoring_and_pooling_read_each_replicas_own_ideal(planned: live_run.Choice) -> None:
    runs = [e for e in planned.entries if not e.reference]
    dists = {e.name: [e.ideal_at(k) for k in range(BLOCKS)] for e in runs}
    pooled, per_replica = live_run._pooled_summaries(planned.group, runs, dists)
    _expect([row["placement"] for row in per_replica] == [0.0, 1.0, 2.0], "placement indices")
    _expect(all(abs(row["contrast"] - row["ideal"]) < 1e-12 for row in per_replica), "a placement read a foreign ideal")
    _expect(abs(pooled["contrast"] - float(np.mean([r["ideal"] for r in per_replica]))) < 1e-12, "pooled mean")
    stats = live_run.replica_statistics(
        planned.group,
        planned.entries,
        {**dists, **{e.name: [e.ideal_at(0)] for e in planned.entries if e.reference}},
        1000,
    )
    _expect("summary_interval" not in stats, "a spread over different blocks is no interval")
    scores = stats["variance"]["block_minus"]
    _expect(scores["shot_variance"] >= 0.0 if "shot_variance" in scores else True, "variance")


def test_sparse_placement_keys_pool_over_the_placements_that_report_them(planned: live_run.Choice) -> None:
    def sparse(placement: int, dist: dict, ideal: dict) -> dict[str, float]:
        return {"all": 1.0, **({"first": 5.0} if placement == 0 else {"rest": 2.0 * placement})}

    group = _group(placed_summary=sparse)
    runs = [e for e in planned.entries if not e.reference]
    dists = {e.name: [e.ideal_at(k) for k in range(BLOCKS)] for e in runs}
    pooled, per_replica = live_run._pooled_summaries(group, runs, dists)
    _expect(pooled == {"all": 1.0, "first": 5.0, "rest": 3.0}, f"{pooled}")
    _expect([sorted(row) for row in per_replica][0] == ["all", "first"], "per-placement key sets")


# --- isolation of the replicas ------------------------------------------------------------------------------------


def _line(count: int) -> Any:
    graph = rx.PyGraph()
    graph.add_nodes_from(range(count))
    graph.add_edges_from_no_data([(i, i + 1) for i in range(count - 1)])
    return graph


def _body(qubits: list[int], width: int = 12) -> QuantumCircuit:
    circuit = QuantumCircuit(width, 1)
    for a, b in zip(qubits, qubits[1:], strict=False):
        circuit.cz(a, b)
    return circuit


def test_replicas_that_share_a_qubit_or_break_the_buffer_are_refused() -> None:
    bodies = [_body([0, 1]), _body([0, 1])]
    far = [Replica(0, {0: 0, 1: 1}, 1.0), Replica(1, {0: 4, 1: 5}, 1.0)]
    live_run.check_replica_isolation("m", bodies, far, _line(12))
    shared = [Replica(0, {0: 0, 1: 1}, 1.0), Replica(1, {0: 1, 1: 2}, 1.0)]
    with pytest.raises(live_run.LiveRunError, match="share qubit 1"):
        live_run.check_replica_isolation("m", bodies, shared, None)
    adjacent = [Replica(0, {0: 0, 1: 1}, 1.0), Replica(1, {0: 2, 1: 3}, 1.0)]
    with pytest.raises(live_run.LiveRunError, match="within one coupler"):
        live_run.check_replica_isolation("m", bodies, adjacent, _line(12))
    live_run.check_replica_isolation("m", bodies, adjacent, None)


def test_a_body_that_acts_outside_its_placement_is_refused_by_the_entry() -> None:
    strays = [_body([0, 1]), _body([0, 1, 2])]
    replicas = [Replica(0, {0: 0, 1: 1}, 1.0), Replica(1, {0: 4, 1: 5}, 1.0)]
    with pytest.raises(live_run.LiveRunError, match="acts on qubits \\[2\\] outside its placement"):
        live_run._entry(
            "m", strays[0], np.array([1.0, 0.0]), replicas, None, ("a", "b"), tuple(strays), (np.ones(2),) * 2, None
        )


# --- records and archives ----------------------------------------------------------------------------------------


def _record(choice: live_run.Choice) -> tuple[dict[str, Any], dict[str, QuantumCircuit]]:
    pubs = live_run.execution_pubs([choice])
    planned_job = {
        "backend": pubs[0].backend,
        "kind": pubs[0].kind,
        "members": [component.entry.name for pub in pubs for component in pub.components],
        "pubs": [live_run._json_value(pub.manifest()) for pub in pubs],
    }
    record = {
        "groups": [live_run._json_value(live_run.choice_structure(choice))],
        "submission": {"planned_jobs": [planned_job]},
    }
    buffer = io.BytesIO()
    qpy.dump([pub.circuit for pub in pubs], buffer)
    buffer.seek(0)
    return record, {circuit.name: circuit for circuit in qpy.load(buffer)}


def test_archived_entries_restore_the_replica_ideals_and_refuse_a_changed_one(
    planned: live_run.Choice, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(live_run, "all_experiment_groups", lambda: [_group()])
    record, isas = _record(planned)
    restored = {e.name: e for e in live_run._archived_entries(record, isas)["synthetic_composite"]}
    for entry in planned.entries:
        if entry.reference:
            _expect(restored[entry.name].replica_ideals is None, "reference restored ideals")
            continue
        for k in range(BLOCKS):
            _expect(np.allclose(restored[entry.name].ideal_at(k), entry.ideal_at(k), atol=1e-9), f"{entry.name}: {k}")
    tampered = copy.deepcopy(record)
    member = next(m for m in tampered["groups"][0]["members"] if m["name"] == "block_minus")
    member["replica_ideals"] = member["replica_ideals"][::-1]
    with pytest.raises(live_run.LiveRunError, match="replica 0 ideal differs from its body"):
        live_run._archived_entries(tampered, isas)
    dropped = copy.deepcopy(record)
    for member in dropped["groups"][0]["members"]:
        member.pop("replica_ideals", None)
    with pytest.raises(live_run.LiveRunError, match="per-placement in code"):
        live_run._archived_entries(dropped, isas)

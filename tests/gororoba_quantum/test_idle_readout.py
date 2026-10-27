"""Contracts of patterned members: Group validation, per-replica packing, record fields and archived-body checks.

The synthetic group packs three pinned Kingston pairs on FakeKingston; the idle_readout checks read the
registered group's members, templates and ideal laws without compiling it.
"""

from __future__ import annotations

import copy
import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from qiskit import QuantumCircuit, QuantumRegister, qpy
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKingston

import idle_penalty as ip
import live_run
import packing
from experiments import Group, Member
from local_compute import is_dynamic
from packing import Replica
from runtime_contracts import _fake_snapshot

ROOT = Path(__file__).resolve().parents[2]
PAIRS = 3


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


# --- Group validation -------------------------------------------------------------------------


def _circuit(name: str, width: int = 2, clbits: int = 2, creg: str = "c") -> QuantumCircuit:
    circuit = QuantumCircuit(QuantumRegister(width, "q"), name=name)
    if clbits:
        from qiskit import ClassicalRegister

        circuit.add_register(ClassicalRegister(clbits, creg))
    circuit.x(0)
    circuit.measure(0, 0)
    return circuit


LAW = np.array([0.0, 1.0, 0.0, 0.0])


def _group(**changes: Any) -> Group:
    first = Member("primary", _circuit("primary"), LAW)
    plain = Member("plain", _circuit("plain"), LAW)
    quiet = ("quiet", _circuit("quiet"), LAW)
    members = changes.pop("members", None)
    templates = changes.pop("templates", (quiet,))
    if members is None:
        circuit = plain.circuit
        members = (first, plain, Member("patterned", circuit, LAW, replica_bodies=("plain", "quiet", "plain")))
    return Group("g", tuple(members), lambda _: {}, body_templates=tuple(templates), **changes)


def test_a_consistent_patterned_group_is_accepted() -> None:
    group = _group()
    _expect(group.members[2].replica_bodies == ("plain", "quiet", "plain"), "patterned member lost its bodies")


def _refused(match: str, **changes: Any) -> None:
    with pytest.raises(ValueError, match=match):
        _group(**changes)


def test_group_refuses_bodies_that_differ_or_name_nothing() -> None:
    plain = Member("plain", _circuit("plain"), LAW)
    first = Member("primary", _circuit("primary"), LAW)

    def patterned(bodies: tuple[str, ...], circuit: QuantumCircuit | None = None) -> tuple[Member, ...]:
        return (first, plain, Member("patterned", circuit or plain.circuit, LAW, replica_bodies=bodies))

    wide = _circuit("wide", width=3)
    extra = _circuit("extra", clbits=3)
    renamed = _circuit("renamed", creg="d")
    other_law = np.array([1.0, 0.0, 0.0, 0.0])
    _refused("differs in width", members=patterned(("plain", "wide")), templates=[("wide", wide, LAW)])
    _refused("differs in classical registers", members=patterned(("plain", "extra")), templates=[("extra", extra, LAW)])
    _refused(
        "differs in classical registers", members=patterned(("plain", "renamed")), templates=[("renamed", renamed, LAW)]
    )
    _refused(
        "differs in ideal law", members=patterned(("plain", "law")), templates=[("law", _circuit("law"), other_law)]
    )
    _refused("neither an unpatterned member nor a template", members=patterned(("plain", "missing")))
    _refused("neither an unpatterned member nor a template", members=patterned(("plain", "patterned")))
    _refused("nonempty tuple", members=patterned(()))


def test_group_refuses_misplaced_patterned_members_and_name_clashes() -> None:
    plain = Member("plain", _circuit("plain"), LAW)
    first = Member("primary", _circuit("primary"), LAW)
    quiet_template = ("quiet", _circuit("quiet"), LAW)
    lead = Member("lead", plain.circuit, LAW, replica_bodies=("plain",))
    _refused("first member fixes the placement", members=(lead, plain))
    mirrored = Member("mirrored", plain.circuit, LAW, mirror=True, replica_bodies=("plain",))
    _refused("mirror twin", members=(first, plain, mirrored))
    foreign = Member("foreign", _circuit("other"), LAW, replica_bodies=("plain",))
    _refused("first body plain as its circuit", members=(first, plain, foreign))
    _refused("differ from every member name", templates=[("plain", _circuit("plain"), LAW)])
    _refused("must be unique", templates=[quiet_template, quiet_template])
    with pytest.raises(ValueError, match="immutable tuple"):
        Group("g", (first,), lambda _: {}, body_templates=[quiet_template])  # type: ignore[arg-type]


# --- packing ----------------------------------------------------------------------------------


def _old_pack(isa: QuantumCircuit, replicas: list[Replica], name: str) -> QuantumCircuit:
    """The single-circuit pack as it stood before per-replica circuits, the byte-identity reference."""
    tail_start = packing._measurement_tail_start(isa)
    out = QuantumCircuit(*isa.qregs, name=name)
    moved = [packing.relabel(isa, replica.mapping, replica.prefix) for replica in replicas]
    for circuit in moved:
        out.global_phase += circuit.global_phase
        for register in circuit.cregs:
            out.add_register(register)
    for part in (slice(0, tail_start), slice(tail_start, None)):
        for circuit in moved:
            piece = circuit.copy_empty_like()
            piece.global_phase = 0
            for inst in circuit.data[part]:
                piece.append(inst)
            out.compose(piece, qubits=range(isa.num_qubits), clbits=circuit.clbits, inplace=True)
    return out


def _body(name: str, steps: int) -> QuantumCircuit:
    from qiskit import ClassicalRegister

    circuit = QuantumCircuit(QuantumRegister(4, "q"), ClassicalRegister(2, "c"), name=name)
    circuit.h(0)
    for _ in range(steps):
        circuit.delay(64, 1, unit="dt")
        circuit.x(1)
    circuit.barrier(0, 1)
    circuit.measure([0, 1], [0, 1])
    return circuit


def _qpy_bytes(circuit: QuantumCircuit) -> bytes:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


REPLICAS = [Replica(0, {0: 0, 1: 1}, 1.0), Replica(1, {0: 2, 1: 3}, 1.0)]


def test_pack_of_one_circuit_is_unchanged_and_a_list_of_it_is_identical() -> None:
    isa = _body("one", 1)
    expected = _qpy_bytes(_old_pack(isa, REPLICAS, "p"))
    _expect(_qpy_bytes(packing.pack(isa, REPLICAS, "p")) == expected, "pack of one circuit changed")
    _expect(_qpy_bytes(packing.pack([isa, isa], REPLICAS, "p")) == expected, "a list of one circuit differs")


def test_pack_relabels_and_slices_each_replicas_own_circuit() -> None:
    short, long = _body("short", 0), _body("long", 3)
    packed = packing.pack([short, long], REPLICAS, "p")
    for replica, body in zip(REPLICAS, (short, long), strict=True):
        own = packing.split(packed, replica.prefix, replica.qubits, "p")
        to_base = {physical: base for base, physical in replica.mapping.items()}
        _expect(
            packing.body_digest(own, to_base) == packing.body_digest(body, {q: q for q in replica.mapping}),
            f"replica {replica.index} does not run its own circuit",
        )
    names = [inst.operation.name for inst in packed.data]
    last_body = max(i for i, name in enumerate(names) if name not in ("measure", "barrier"))
    first_read = min(i for i, name in enumerate(names) if name == "measure")
    _expect(last_body < first_read, "a replica's tail started before another replica's body ended")
    _expect(not is_dynamic(packed), "packing per-replica circuits turned a static circuit dynamic")


def test_pack_refuses_mismatched_replica_circuits() -> None:
    with pytest.raises(ValueError, match="2 replica circuits for 3 replicas"):
        packing.pack([_body("a", 0)] * 2, [*REPLICAS, Replica(2, {0: 4, 1: 5}, 1.0)], "p")
    narrow = QuantumCircuit(3, 2, name="narrow")
    with pytest.raises(ValueError, match="differs from"):
        packing.pack([_body("a", 0), narrow], REPLICAS, "p")


def test_body_digest_ignores_relabeling_and_numeric_type_and_names_a_stray_qubit() -> None:
    body = _body("digest", 2)
    moved = packing.relabel(body, {0: 3, 1: 2}, "r_")
    _expect(
        packing.body_digest(moved, {3: 0, 2: 1}) == packing.body_digest(body, {0: 0, 1: 1}),
        "relabeling changed the digest",
    )
    as_int, as_float = QuantumCircuit(1), QuantumCircuit(1)
    as_int.delay(100, 0, unit="dt")
    as_float.delay(100.0, 0, unit="dt")
    _expect(packing.body_digest(as_int, {0: 0}) == packing.body_digest(as_float, {0: 0}), "numeric type moved it")
    longer = QuantumCircuit(1)
    longer.delay(101, 0, unit="dt")
    _expect(packing.body_digest(as_int, {0: 0}) != packing.body_digest(longer, {0: 0}), "a delay change kept it")
    with pytest.raises(ValueError, match="outside the placement"):
        packing.body_digest(body, {0: 0})


# --- registered idle_readout group -------------------------------------------------------------


def test_idle_readout_holds_55_members_over_31_replicas_and_8_templates() -> None:
    group = ip.idle_readout_group()
    patterned = [member for member in group.members if member.replica_bodies is not None]
    _expect(
        len(group.members) == 55 and len(patterned) == 32, f"{len(group.members)} members, {len(patterned)} patterned"
    )
    _expect(len(group.body_templates) == 8, f"{len(group.body_templates)} templates")
    _expect(group.members[0].name == "idle_cz_kick", "the placement anchor is not first")
    names = [member.name for member in group.members]
    _expect(len(set(names)) == 55, "member names repeat")
    expected = {
        ip.half_member(probe, partition, pattern, quadrature, short)
        for probe in (ip.TARGET, ip.SPECTATOR)
        for partition in ip.PARTITIONS
        for pattern in ip.PATTERNS
        for quadrature in ip.QUADRATURES
        for short in (False, True)
    }
    _expect({member.name for member in patterned} == expected, "patterned names differ from half_member")
    shared = {member.name for member in group.members if member.name in {n for n, _, _ in ip.idle_penalty_circuits()}}
    _expect(len(shared) == 23, f"{len(shared)} retained members")


def test_idle_readout_bodies_follow_the_class_strings_and_share_one_ideal_law() -> None:
    group = ip.idle_readout_group()
    bodies = {name: (circuit, ideal) for name, circuit, ideal in group.body_templates}
    bodies |= {member.name: (member.circuit, member.ideal) for member in group.members if member.replica_bodies is None}
    for member in group.members:
        if member.replica_bodies is None:
            continue
        _expect(len(member.replica_bodies) == 31, f"{member.name}: {len(member.replica_bodies)} bodies")
        partition, pattern = member.name.split("_half_")[1].split("_")[0][:2], member.name.split("_half_")[1][2]
        reading = ip.PATTERNS[pattern]
        short = "short" in member.name
        for index, (cls, body) in enumerate(zip(ip.PARTITIONS[partition], member.replica_bodies, strict=True)):
            quiet = "quiet" in body
            _expect(quiet == (cls != reading), f"{member.name} replica {index}: class {cls} runs {body}")
            _expect(("short" in body) == short, f"{member.name} replica {index}: window of {body}")
            circuit, ideal = bodies[body]
            _expect(np.allclose(ideal, member.ideal, atol=1e-12), f"{member.name} replica {index}: ideal law differs")
            law = Statevector(ip._unitary_part(circuit)).probabilities()
            _expect(np.allclose(law, member.ideal, atol=1e-12), f"{body}: statevector law differs from the member's")
            _expect(is_dynamic(circuit), f"{body} classifies static")
        _expect(member.circuit is bodies[member.replica_bodies[0]][0], f"{member.name}: first body is not its circuit")


def test_quiet_bodies_hold_the_probe_window_and_drop_only_the_reads() -> None:
    reads = {"meas_quiet": (ip.MEAS_DT, ip.MEAS_COUNT), "meas_short_quiet": (ip.SHORT_MEAS_DT, ip.SHORT_MEAS_COUNT)}
    circuits = {name: circuit for name, circuit, _ in ip.idle_penalty_circuits()}
    for name, quiet, _ in ip.readout_templates():
        kind = "meas_short_quiet" if "short_quiet" in name else "meas_quiet"
        idle, count = reads[kind]
        delays = sorted(int(i.operation.duration) for i in quiet.data if i.operation.name == "delay")
        _expect(delays == [count * (ip.MEASURE_DT + ip.MEAS_GAP_DT), idle], f"{name}: delays {delays}")
        _expect(quiet.count_ops().get("measure") == 2, f"{name}: the quiet body reads more than the final pair")
    during = circuits["idle_meas_during_x"].count_ops()
    quiet_ops = next(c for n, c, _ in ip.readout_templates() if n == "idle_meas_quiet_x").count_ops()
    _expect(
        during["measure"] - quiet_ops["measure"] == ip.MEAS_COUNT, "the reading body does not add the train's reads"
    )


def test_the_nominal_measure_duration_is_the_registered_kingston_duration() -> None:
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())["backends"]["ibm_kingston"]
    durations = {round(d / targets["dt"]) for d in targets["instructions"]["measure"]["duration"]}
    _expect(durations == {ip.MEASURE_DT}, f"registered measure durations {durations} dt against {ip.MEASURE_DT}")


def test_quiet_partner_idle_must_fit_the_probe_idle() -> None:
    target = FakeKingston().target
    pair = next(iter(target["cz"]))
    wide = QuantumCircuit(156, 2, name="idle_meas_quiet_x")
    wide.delay(ip.MEAS_DT, pair[0], unit="dt")
    wide.delay(ip.MEAS_DT, pair[1], unit="dt")
    wide.measure(list(pair), [0, 1])
    reasons = ip.routed_readout_violations([wide], target)
    _expect(any("does not fit" in reason for reason in reasons), f"an idle that fills the window passed: {reasons}")


# --- planned records and archived bodies --------------------------------------------------------


def _pinned_paths() -> list[list[int]]:
    case = (ROOT / "results/live/IDLE_PENALTY_REPEAT_CASE.md").read_text()
    pin = next(line for line in case.splitlines() if line.startswith("ibm_kingston:"))
    return [[int(q) for q in path.split(",")] for path in pin.split(":", 1)[1].split("/")][:PAIRS]


def _tiny_group() -> Group:
    circuits = {name: (circuit, ideal) for name, circuit, ideal in ip.idle_penalty_circuits()}
    quiet = {name: (circuit, ideal) for name, circuit, ideal in ip.readout_templates()}
    during, quiet_x = circuits["idle_meas_during_x"], quiet["idle_meas_quiet_x"]
    members = [Member("idle_cz_kick", *circuits["idle_cz_kick"]), Member("idle_meas_during_x", *during)]
    members.append(
        Member("reads_first", during[0], during[1], replica_bodies=("idle_meas_during_x",) + ("idle_meas_quiet_x",) * 2)
    )
    members.append(
        Member(
            "reads_last", quiet_x[0], quiet_x[1], replica_bodies=("idle_meas_quiet_x",) * 2 + ("idle_meas_during_x",)
        )
    )
    return Group(
        "tiny_readout",
        tuple(members),
        lambda _: {},
        routed_violations=ip.routed_readout_violations,
        body_templates=(("idle_meas_quiet_x", quiet_x[0], quiet_x[1]),),
    )


@pytest.fixture(scope="module")
def planned() -> Iterator[tuple[live_run.Choice, list[live_run.ExecutionPub]]]:
    snapshot = _fake_snapshot(FakeKingston())
    paths = _pinned_paths()
    group = _tiny_group()
    log: dict[str, Any] = {}
    candidates = live_run.select_candidates(group, [snapshot], 1, log, paths[0])
    policy = live_run.ReplicaPolicy(None, PAIRS, True, True)
    choices, _ = live_run.pinned_campaign_choices([candidates], policy, log, paths)
    yield choices[0], live_run.execution_pubs(choices)


def _record(choice: live_run.Choice, pubs: list[live_run.ExecutionPub]) -> tuple[dict[str, Any], dict[str, Any]]:
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


@pytest.fixture
def known(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(live_run, "all_experiment_groups", lambda: [_tiny_group()])


def test_patterned_entries_carry_their_bodies_and_digests_only_when_patterned(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]],
) -> None:
    choice, pubs = planned
    by_name = {entry.name: entry for entry in choice.entries}
    for name in ("idle_cz_kick", "idle_meas_during_x"):
        fields = live_run._member_fields(by_name[name])
        _expect("replica_bodies" not in fields and "replica_body_sha256" not in fields, f"{name} gained body fields")
    patterned = by_name["reads_first"]
    fields = live_run._member_fields(patterned)
    _expect(fields["replica_bodies"] == ["idle_meas_during_x", "idle_meas_quiet_x", "idle_meas_quiet_x"], "bodies")
    _expect(len(fields["replica_body_sha256"]) == PAIRS, "digest count")
    _expect(fields["replica_body_sha256"][1] == fields["replica_body_sha256"][2], "equal bodies, unequal digests")
    _expect(fields["replica_body_sha256"][0] != fields["replica_body_sha256"][1], "reader and quiet digests agree")
    for pub in pubs:
        for component in pub.components:
            manifest = component.manifest()
            has = "replica_bodies" in manifest and "replica_body_sha256" in manifest
            _expect(has == (component.entry.replica_bodies is not None), f"{component.entry.name}: manifest fields")
    template = choice.template_isas["idle_meas_quiet_x"]
    _expect(set(choice.template_isas) == {"idle_meas_quiet_x"} and is_dynamic(template), "template isa")
    _expect(not any(entry.name == "idle_meas_quiet_x" for entry in choice.entries), "a template became an entry")


def test_each_replica_runs_the_body_its_label_names(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]],
) -> None:
    choice, _ = planned
    entry = next(e for e in choice.entries if e.name == "reads_first")
    measures = [replica.count_ops().get("measure", 0) for replica in entry.replicas]
    _expect(measures == [2 + ip.MEAS_COUNT, 2, 2], f"replica measure counts {measures}")
    laws = live_run.simulate_entries(AerSimulator(), [entry], 64, live_run.SEED_SIMULATOR)["reads_first"]
    _expect(len(laws) == PAIRS and all(np.allclose(law, entry.ideal) for law in laws), "simulated laws differ")


def test_entry_refuses_a_replica_count_that_differs_from_the_bodies(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]],
) -> None:
    choice, _ = planned
    entry = next(e for e in choice.entries if e.name == "reads_first")
    bodies = live_run._compiled_bodies(choice, entry.name, entry.replica_bodies or ())
    with pytest.raises(live_run.LiveRunError, match="3 replicas for 2 replica bodies"):
        live_run._entry(
            entry.name, bodies[0], entry.ideal, choice.replicas, None, (entry.replica_bodies or ())[:2], bodies[:2]
        )


def test_archived_entries_restore_bodies_and_digests(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]], known: None
) -> None:
    choice, pubs = planned
    record, isas = _record(choice, pubs)
    restored = {e.name: e for e in live_run._archived_entries(record, isas)["tiny_readout"]}
    for entry in choice.entries:
        if entry.reference:
            continue
        _expect(restored[entry.name].replica_bodies == entry.replica_bodies, f"{entry.name}: bodies not restored")
        _expect(restored[entry.name].body_digests == entry.body_digests, f"{entry.name}: digests not restored")


def _swap_first_two(record: dict[str, Any], *, in_group: bool = True, in_component: bool = True) -> dict[str, Any]:
    swapped = copy.deepcopy(record)

    def swap(owner: dict[str, Any]) -> None:
        for key in ("replica_bodies", "replica_body_sha256"):
            owner[key][0], owner[key][1] = owner[key][1], owner[key][0]

    if in_group:
        swap(next(m for m in swapped["groups"][0]["members"] if m["name"] == "reads_first"))
    if in_component:
        for job in swapped["submission"]["planned_jobs"]:
            for pub in job["pubs"]:
                for component in pub["components"]:
                    if component["member"] == "reads_first":
                        swap(component)
    return swapped


def test_a_label_swap_with_digests_of_the_named_bodies_refuses_collection_naming_the_replica(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]], monkeypatch: pytest.MonkeyPatch
) -> None:
    choice, pubs = planned
    record, isas = _record(choice, pubs)
    # The code definition agrees with the swapped record, so only the archived circuits disagree.
    group = _tiny_group()
    members = list(group.members)
    members[2] = Member(
        "reads_first",
        group.body_templates[0][1],
        members[2].ideal,
        replica_bodies=("idle_meas_quiet_x", "idle_meas_during_x", "idle_meas_quiet_x"),
    )
    swapped_group = Group(group.name, tuple(members), group.summarize, body_templates=group.body_templates)
    monkeypatch.setattr(live_run, "all_experiment_groups", lambda: [swapped_group])
    with pytest.raises(live_run.LiveRunError, match=r"'reads_first' replica 0 \(r0_\).*'idle_meas_quiet_x'"):
        live_run._archived_entries(_swap_first_two(record), isas)


def test_a_record_that_disagrees_with_the_group_definition_or_the_pub_map_refuses_collection(
    planned: tuple[live_run.Choice, list[live_run.ExecutionPub]], known: None
) -> None:
    choice, pubs = planned
    record, isas = _record(choice, pubs)
    with pytest.raises(live_run.LiveRunError, match="differ from the group definition"):
        live_run._archived_entries(_swap_first_two(record), isas)
    with pytest.raises(live_run.LiveRunError, match="differ between group record and PUB map"):
        live_run._archived_entries(_swap_first_two(record, in_component=False), isas)
    stripped = copy.deepcopy(record)
    for member in stripped["groups"][0]["members"]:
        member.pop("replica_bodies", None)
        member.pop("replica_body_sha256", None)
    with pytest.raises(live_run.LiveRunError, match="replica body fields|patterned in code"):
        live_run._archived_entries(stripped, isas)


def test_idle_readout_runs_only_on_a_pin_that_names_one_path_per_body() -> None:
    from runtime_contracts import _fixture_args, _ProbeBackend, _ProbeService

    _expect(
        "idle_readout" in live_run.PIN_CAPABLE_CAMPAIGNS
        and "idle_readout" in live_run.PIN_REQUIRED_CAMPAIGNS
        and "idle_readout" not in live_run.PINNED_CAMPAIGNS,
        "idle_readout pin registration",
    )
    service = _ProbeService([_ProbeBackend("viable", FakeKingston())])
    one_path = {"backend": "viable", "qubits": _pinned_paths()[0]}
    for overrides, message in (
        ({"groups": ["idle_readout"]}, "runs on the paths --pin-layout names"),
        ({"groups": ["idle_readout"], "pin_layout": one_path, "max_replicas": 1}, r"one body to each of \[31\]"),
    ):
        with pytest.raises(live_run.LiveRunError, match=message):
            live_run.plan(service, _fixture_args(**overrides))


@pytest.mark.audit
def test_registered_group_plans_55_entries_and_8_templates_on_the_31_pinned_pairs() -> None:
    """The registered group on FakeKingston with every pinned pair: 55 executed entries, no template entry."""
    snapshot = _fake_snapshot(FakeKingston())
    case = (ROOT / "results/live/IDLE_PENALTY_REPEAT_CASE.md").read_text()
    pin = next(line for line in case.splitlines() if line.startswith("ibm_kingston:"))
    paths = [[int(q) for q in path.split(",")] for path in pin.split(":", 1)[1].split("/")]
    group = ip.idle_readout_group()
    log: dict[str, Any] = {}
    candidates = live_run.select_candidates(group, [snapshot], 1, log, paths[0])
    policy = live_run.ReplicaPolicy(None, len(paths), True, True)
    choices, _ = live_run.pinned_campaign_choices([candidates], policy, log, paths)
    choice = choices[0]
    executed = [entry for entry in choice.entries if not entry.reference]
    _expect(len(executed) == 55, f"{len(executed)} executed entries")
    _expect(len(choice.template_isas) == 8, f"{len(choice.template_isas)} routed templates")
    _expect(not {entry.name for entry in executed} & set(choice.template_isas), "a template became an entry")
    pubs = live_run.execution_pubs(choices)
    _expect(len(pubs) == 56, f"{len(pubs)} PUBs for 55 members and the replica-0 reference")
    for entry in executed:
        patterned = entry.replica_bodies is not None
        _expect(patterned == (entry.name in {m.name for m in group.members if m.replica_bodies}), entry.name)
        if patterned:
            _expect(len(entry.body_digests or ()) == len(paths), f"{entry.name}: digests")

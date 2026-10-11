"""Credential-free contracts for live admission, PUB fusion, approval, and Runtime helpers."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import tempfile
from contextlib import redirect_stdout
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit.circuit import Clbit
from qiskit.circuit.controlflow import IfElseOp
from qiskit.circuit.library import RZGate
from qiskit.primitives import StatevectorSampler
from qiskit.primitives.containers import BitArray, DataBin, PrimitiveResult, SamplerPubResult
from qiskit.transpiler import Target
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2

import hybrid_shor  # noqa: F401 - proves the digest ignores module load order
import live_run as live_run_module
import packing
from experiments import MIRROR_SUFFIX, Group, experiment_groups
from live_run import (
    RECORD_SCHEMA_CONTRACT,
    RECORD_SCHEMA_VERSION,
    BackendCapabilities,
    Choice,
    CircuitRequirements,
    Entry,
    LiveRunError,
    ReplicaPolicy,
    Snapshot,
    _archived_entries,
    _compile,
    _distribution,
    _is_dynamic,
    _ops,
    _physical,
    _pub_counts,
    _recovery_tags,
    build_admission_target,
    build_submission_plan,
    capability_violations,
    check_snapshot_matches_properties,
    choice_change_reasons,
    choice_reselection_reasons,
    collect,
    compiled_violations,
    component_execution_records,
    configure_sampler,
    discover_snapshots,
    execution_pubs,
    execution_requirements,
    experiment_digest,
    fusion_summary,
    group_requirements,
    pub_windows,
    reconcile_attempted_jobs,
    replica_floor,
    routing_admission_violations,
    select,
    select_candidates,
    select_fusion_choices,
    submission_batches,
    submission_gaps,
    target_violations,
    write_archive,
    write_json,
)
from order_finding import factor_order_finding

SINGLE_REPLICA_POLICY = ReplicaPolicy(max_replicas=1, isolated_reference=False)
PACKED_REPLICA_POLICY = ReplicaPolicy(floor=0.8, max_replicas=2, isolated_reference=True)


class _ProbeBackend:
    """Named fake backend that can fail one snapshot stage."""

    def __init__(
        self,
        name: str,
        backend: FakeFez,
        failure_stage: str | None = None,
    ):
        self.name = name
        self._backend = backend
        self._failure_stage = failure_stage
        self.property_refreshes = 0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._backend, name)

    def refresh(self) -> None:
        if self._failure_stage == "refresh":
            raise RuntimeError("fixture refresh failure")

    def properties(self, refresh: bool = False, **query: Any) -> Any:
        unexpected = set(query) - {"datetime"}
        if unexpected:
            raise RuntimeError(f"unexpected fixture property query {sorted(unexpected)}")
        if self._failure_stage == "properties":
            raise RuntimeError("fixture properties failure")
        if refresh:
            self.property_refreshes += 1
        return self._backend.properties(refresh=refresh)

    def target_history(self, **query: Any) -> Any:
        if set(query) != {"datetime"}:
            raise RuntimeError(f"unexpected fixture Target query {sorted(query)}")
        return self._backend.target

    def status(self) -> Any:
        if self._failure_stage == "status":
            raise RuntimeError("fixture status failure")
        return self._backend.status()

    def configuration(self) -> Any:
        if self._failure_stage == "capabilities":
            raise RuntimeError("fixture capability failure")
        configuration = copy.copy(self._backend.configuration())
        supported_features = list(getattr(configuration, "supported_features", []))
        if "dynamic_circuits" not in supported_features:
            supported_features.append("dynamic_circuits")
        configuration.supported_features = supported_features
        return configuration


class _ProbeService:
    """Minimal service surface for isolated discovery contracts."""

    def __init__(self, backends: list[_ProbeBackend], recovery_jobs: list[Any] | None = None):
        self._backends = {backend.name: backend for backend in backends}
        self.recovery_jobs = recovery_jobs or []
        self.recovery_queries: list[dict[str, Any]] = []

    def backends(self) -> list[_ProbeBackend]:
        return list(self._backends.values())

    def backend(self, name: str) -> _ProbeBackend:
        return self._backends[name]

    def usage(self) -> dict[str, Any]:
        return {"usage_limit_reached": False, "usage_remaining_seconds": None}

    def active_instance(self) -> str:
        return "fixture-instance"

    def instances(self) -> list[dict[str, str]]:
        return [{"crn": "fixture-instance", "plan": "fixture", "name": "fixture"}]

    def jobs(self, **query: Any) -> list[Any]:
        self.recovery_queries.append(query)
        return self.recovery_jobs


class _PinnedProbeService(_ProbeService):
    """Service whose direct backend lookup works while enumeration fails."""

    def backends(self) -> list[_ProbeBackend]:
        raise RuntimeError("fixture global discovery failure")


class _ProbeJob:
    def __init__(self, job_id: str):
        self._job_id = job_id

    def job_id(self) -> str:
        return self._job_id


class _ProbeExecutionSpan:
    def __init__(self, start: datetime, stop: datetime, pub_idxs: list[int]):
        self.start = start
        self.stop = stop
        self.pub_idxs = pub_idxs


class _ProbeResultJob:
    def __init__(self, result: PrimitiveResult[SamplerPubResult]):
        self._result = result

    def result(self) -> PrimitiveResult[SamplerPubResult]:
        return self._result

    def metrics(self) -> dict[str, Any]:
        return {"usage": {"quantum_seconds": 0.0}}


class _CollectionProbeService(_ProbeService):
    def __init__(self, backend: _ProbeBackend, jobs: dict[str, _ProbeResultJob]):
        super().__init__([backend])
        self._result_jobs = jobs

    def job(self, job_id: str) -> _ProbeResultJob:
        return self._result_jobs[job_id]


class _BoundedAngleTarget:
    """Target surface that proves bounded-angle systems stop at admission."""

    def has_angle_bounds(self) -> bool:
        return True


class _BoundedAngleBackend:
    """Backend surface used only before routing begins."""

    def __init__(self) -> None:
        self.target = _BoundedAngleTarget()


class _ProbeSamplerOptions:
    def __init__(self, kind: str, tags: list[str], shots: int):
        self._value = {"kind": kind, "environment": {"job_tags": tags}, "default_shots": shots}

    def model_dump(self, mode: str) -> dict[str, Any]:
        if mode != "json":
            raise RuntimeError(f"unexpected options serialization mode {mode}")
        return copy.deepcopy(self._value)


class _ProbeSampler:
    def __init__(
        self,
        kind: str,
        tags: list[str],
        shots: int,
        before_run: Any,
        after_run: Any = None,
    ):
        self.options = _ProbeSamplerOptions(kind, tags, shots)
        self._before_run = before_run
        self._after_run = after_run

    def run(self, circuits: list[QuantumCircuit]) -> _ProbeJob:
        self._before_run(circuits)
        if self._after_run is not None:
            self._after_run()
        return _ProbeJob("fixture-job-id")


def _verify_dynamic_classification() -> None:
    final_measurement = QuantumCircuit(2, 2)
    final_measurement.h(0)
    final_measurement.measure([0, 1], [0, 1])
    if _is_dynamic(final_measurement):
        raise RuntimeError("terminal measurements classify as dynamic")

    later_work = QuantumCircuit(2, 1)
    later_work.measure(0, 0)
    later_work.x(1)
    if not _is_dynamic(later_work):
        raise RuntimeError("measurement followed by work on another qubit classifies as static")


def _verify_nested_operations() -> None:
    nested = QuantumCircuit(2, 1)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.cz(0, 1)
    operations = _ops(nested)
    if operations != [("measure", (0,)), ("cz", (0, 1))]:
        raise RuntimeError(f"nested physical operations decode as {operations}")

    operation_names = ("cswap", "p", "measure", "reset")
    shor_operations = _ops(factor_order_finding(15, 2, 8))
    counts = {name: sum(operation == name for operation, _ in shor_operations) for name in operation_names}
    expected = {"cswap": 5, "p": 1, "measure": 2, "reset": 1}
    if counts != expected:
        raise RuntimeError(f"N=15 dynamic operation coefficients are {counts}")
    null_operations = _ops(factor_order_finding(15, 2, 8, identity=True))
    null_counts = {name: sum(operation == name for operation, _ in null_operations) for name in operation_names}
    expected_null = {"cswap": 0, "p": 1, "measure": 2, "reset": 1}
    if null_counts != expected_null:
        raise RuntimeError(f"N=15 identity-null operation coefficients are {null_counts}")


def _verify_result_register_order() -> None:
    qubits = QuantumRegister(2, "q")
    low = ClassicalRegister(1, "low")
    high = ClassicalRegister(1, "high")
    circuit = QuantumCircuit(qubits, low, high)
    circuit.x(qubits[0])
    circuit.measure(qubits[0], low[0])
    circuit.measure(qubits[1], high[0])
    pub = StatevectorSampler(seed=1).run([circuit], shots=8).result()[0]
    counts = _pub_counts(pub, [register.name for register in circuit.cregs], circuit.name)
    if counts != {"01": 8}:
        raise RuntimeError(f"multi-register counts decode as {counts}")
    distribution = _distribution(counts, circuit.num_clbits)
    if distribution[1] != 1.0:
        raise RuntimeError(f"multi-register distribution places probability at {distribution.argmax()}")


def _verify_packed_replica_split() -> None:
    """Packed replicas of a dynamic circuit split back into each replica's own counts.

    Replicas 0 and 2 start with their first qubit flipped and replica 1 does
    not, so the feed-forward circuit reads 11, 00, 11; a split that mixed
    registers or replicas would read another replica's outcome. The packed
    circuit runs through the client-side Sampler in local mode on FakeFez.
    """
    backend = FakeFez()
    graph = packing.coupling_graph(backend.target, backend.num_qubits)
    phase = ClassicalRegister(2, "phase")
    template = QuantumCircuit(QuantumRegister(2, "q"), phase)
    template.measure(0, phase[0])
    with template.if_test((phase[0], 1)):
        template.x(1)
    template.measure(1, phase[1])
    isa = transpile(template, backend=backend, optimization_level=0, initial_layout=[0, 1])
    used, edges = packing.pattern([("cz", (0, 1))])
    replicas = packing.place(used, edges, graph, lambda _: True, lambda m: 1.0 / (1 + min(m.values())), 1e-9, 3)
    if len(replicas) != 3 or len({q for r in replicas for q in r.qubits}) != 6:
        raise RuntimeError(f"placement returned overlapping or missing replicas: {replicas}")
    packed = packing.pack(isa, replicas, "packed")
    flips = QuantumCircuit(packed.num_qubits)
    flips.x([replicas[0].mapping[0], replicas[2].mapping[0]])
    packed = packed.compose(flips, front=True)
    if [r.name for r in packed.cregs] != [f"r{k}_phase" for k in range(3)]:
        raise RuntimeError(f"packed registers are {[r.name for r in packed.cregs]}")
    pub = Sampler(mode=backend).run([packed], shots=64).result()[0]
    for replica in replicas:
        single = packing.split(packed, replica.prefix, replica.qubits)
        if single.num_clbits != 2 or not _is_dynamic(single):
            raise RuntimeError(f"replica {replica.prefix} splits to {single.num_clbits} clbits")
        counts = _pub_counts(pub, packing.registers(packed, replica.prefix), replica.prefix)
        top = max(counts, key=lambda key: counts[key])
        if top != ("00" if replica.index == 1 else "11") or counts[top] < 48:
            raise RuntimeError(f"replica {replica.prefix} reads {counts}")

    left = packing.pack(isa, [packing.Replica(0, replicas[0].mapping, replicas[0].score)], "left")
    right = packing.pack(isa, [packing.Replica(0, replicas[2].mapping, replicas[2].score)], "right")
    fused = packing.fuse([left, right], ["g0_", "g1_"], "dynamic_fusion")
    flips = QuantumCircuit(fused.num_qubits)
    flips.x([replicas[0].mapping[0], replicas[2].mapping[0]])
    fused = fused.compose(flips, front=True)
    if not _is_dynamic(fused):
        raise RuntimeError("fused feed-forward components classify as static")
    fused_pub = Sampler(mode=backend).run([fused], shots=64).result()[0]
    for prefix in ("g0_r0_", "g1_r0_"):
        fused_counts = _pub_counts(fused_pub, packing.registers(fused, prefix), prefix)
        if fused_counts.get("11", 0) < 48:
            raise RuntimeError(f"fused dynamic component {prefix} reads {fused_counts}")


def _verify_packed_static_stays_static() -> None:
    """Packing replicas of a static circuit keeps every measurement after every gate.

    The static and dynamic Sampler jobs split on _is_dynamic, so a packed
    static circuit that read as dynamic would lose twirling and dynamical
    decoupling at submission.
    """
    backend = FakeFez()
    graph = packing.coupling_graph(backend.target, backend.num_qubits)
    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure([0, 1], [0, 1])
    isa = transpile(bell, backend=backend, optimization_level=1, initial_layout=[0, 1])
    used, edges = packing.pattern([("cz", (0, 1))])
    replicas = packing.place(used, edges, graph, lambda _: True, lambda m: 1.0 / (1 + min(m.values())), 1e-9, 4)
    packed = packing.pack(isa, replicas, "bell")
    if _is_dynamic(isa) or _is_dynamic(packed):
        raise RuntimeError("packing a static circuit produced a dynamic one")


def _verify_rate_keys() -> None:
    """Every declared per-shot rate names a value its group's summary produces.

    A misspelled rate key would silently drop the pooled-shot Wilson bound
    from that value's interval.
    """
    for group in experiment_groups():
        ideals: dict[str, np.ndarray] = {}
        for member in group.members:
            ideals[member.name] = member.ideal
            if member.mirror:
                zeros = np.zeros(len(member.ideal))
                zeros[0] = 1.0
                ideals[member.name + MIRROR_SUFFIX] = zeros
        unknown = set(group.rate_keys) - set(group.summarize(ideals))
        if unknown:
            raise RuntimeError(f"{group.name}: rate keys {sorted(unknown)} are not summary values")


def _verify_replica_floor_resolution() -> None:
    """Group floors apply by default, while an explicit CLI policy governs every group."""
    groups = experiment_groups()
    hybrid = next(group for group in groups if group.name == "hybrid_shor_mod15")
    ordinary = next(group for group in groups if group.replica_floor is None)
    default_policy = ReplicaPolicy()
    if replica_floor(hybrid, default_policy) != 0.8:
        raise RuntimeError("hybrid Shor fails to use its declared replica floor")
    if replica_floor(ordinary, default_policy) != 0.9:
        raise RuntimeError("a group without a declared replica floor fails to use the default")
    explicit_policy = ReplicaPolicy(floor=0.75)
    if replica_floor(hybrid, explicit_policy) != 0.75 or replica_floor(ordinary, explicit_policy) != 0.75:
        raise RuntimeError("an explicit replica floor fails to govern every group")


def _verify_twirling_shot_contract() -> None:
    sampler = configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=4096)
    if sampler.options.twirling.num_randomizations != 32:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.num_randomizations} randomizations")
    if sampler.options.twirling.shots_per_randomization != 128:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.shots_per_randomization} shots per randomization")
    try:
        configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=16)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("twirling accepted a shot count that Runtime 0.50 rounds upward")


def _verify_capability_admission() -> None:
    groups = {group.name: group for group in experiment_groups()}
    hybrid = group_requirements(groups["hybrid_shor_mod15"])
    expected_hybrid = {
        "qubits": 5,
        "classical_bits": 8,
        "static_circuits": 0,
        "dynamic_circuits": 2,
        "target_operations": ["if_else", "measure", "reset"],
        "control_flow": ["if_else"],
    }
    if hybrid.summary() != expected_hybrid:
        raise RuntimeError(f"hybrid-Shor capability requirements are {hybrid.summary()}")

    heron_like = BackendCapabilities(156, True, ("cz", "if_else", "measure", "reset"), ("if_else",))
    if capability_violations(hybrid, heron_like):
        raise RuntimeError("Heron-like capabilities reject the hybrid-Shor group")

    static_only = BackendCapabilities(156, False, ("cz", "measure"), ())
    static = group_requirements(groups["design_a"])
    if capability_violations(static, static_only):
        raise RuntimeError("static design A requires dynamic-circuit capabilities")
    hybrid_rejections = capability_violations(hybrid, static_only)
    if not any("dynamic-circuit" in reason for reason in hybrid_rejections):
        raise RuntimeError(f"static backend fails to reject dynamic hybrid Shor: {hybrid_rejections}")
    if not any("if_else" in reason and "reset" in reason for reason in hybrid_rejections):
        raise RuntimeError(f"missing dynamic operations are absent from rejection evidence: {hybrid_rejections}")

    narrow = BackendCapabilities(2, True, ("cz", "if_else", "measure", "reset"), ("if_else",))
    if not any("needs 5 qubits" in reason for reason in capability_violations(hybrid, narrow)):
        raise RuntimeError("backend quantum width fails to reject hybrid Shor")

    mixed = CircuitRequirements(2, 2, 1, 1, ("measure", "reset"), ())
    if not any("mixes static and dynamic" in reason for reason in capability_violations(mixed, heron_like)):
        raise RuntimeError("capability admission accepts a mixed static and dynamic result group")


def _verify_discovered_capabilities() -> None:
    backend = _ProbeBackend("viable", FakeFez())
    snapshots, skipped, inventory = discover_snapshots(_ProbeService([backend]), None, None)
    if skipped or len(snapshots) != 1:
        raise RuntimeError(f"viable capability discovery returned snapshots={snapshots} skipped={skipped}")
    if backend.property_refreshes:
        raise RuntimeError("snapshot discovery refreshes properties again after backend.refresh()")
    capabilities = snapshots[0].capabilities
    summary = capabilities.summary()
    expected_control_flow = ["for_loop", "if_else", "switch_case"]
    if summary["num_qubits"] != 156:
        raise RuntimeError(f"discovered backend dimensions are {summary}")
    if summary["dynamic_circuits"] is not True:
        raise RuntimeError(f"discovered dynamic-circuit support is {summary['dynamic_circuits']}")
    if not {"if_else", "measure", "reset"}.issubset(summary["operation_names"]):
        raise RuntimeError(f"discovered operations are {summary['operation_names']}")
    if summary["control_flow"] != expected_control_flow:
        raise RuntimeError(f"discovered control-flow operations are {summary['control_flow']}")
    if inventory["viable"]["capabilities"] != summary:
        raise RuntimeError("system inventory differs from discovered capabilities")

    hybrid = next(group for group in experiment_groups() if group.name == "hybrid_shor_mod15")
    violations = capability_violations(group_requirements(hybrid), capabilities)
    if violations:
        raise RuntimeError(f"discovered backend rejects hybrid Shor: {violations}")
    trace: dict[str, Any] = {}
    choice = select(hybrid, snapshots, 1, trace, SINGLE_REPLICA_POLICY)
    if choice.snap is not snapshots[0] or len(choice.entries) != 2:
        raise RuntimeError("discovered backend fails hybrid-Shor routing admission")

    pinned_backend = _ProbeBackend("pinned", FakeFez())
    pinned_snapshots, pinned_skipped, pinned_inventory = discover_snapshots(
        _PinnedProbeService([pinned_backend]), ["pinned"], None
    )
    if pinned_skipped or [snapshot.name for snapshot in pinned_snapshots] != ["pinned"]:
        raise RuntimeError("global discovery failure suppresses a directly reachable pinned backend")
    if pinned_inventory["pinned"]["eligibility"] != "eligible":
        raise RuntimeError("directly reachable pinned backend loses eligible inventory state")


def _fake_snapshot(backend: Any) -> Snapshot:
    properties = backend.properties()
    if properties is None:
        raise RuntimeError("FakeManilaV2 carries no properties")
    operations = tuple(sorted(backend.target.operation_names))
    capabilities = BackendCapabilities(
        backend.num_qubits,
        True,
        operations,
        tuple(name for name in operations if name in {"for_loop", "if_else", "switch_case"}),
    )
    return Snapshot(
        backend=backend,
        properties=properties,
        name=backend.name,
        operational=True,
        status_msg="active",
        pending_jobs=0,
        calibration=properties.last_update_date.isoformat(),
        fetched_at="fixture",
        capabilities=capabilities,
    )


def _verify_target_and_bad_qubit_status() -> None:
    backend = FakeManilaV2()
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    isa = transpile(circuit, backend=backend, optimization_level=1, seed_transpiler=7)
    if target_violations(isa, backend.target):
        raise RuntimeError(f"valid FakeManila ISA violates its Target: {target_violations(isa, backend.target)}")

    invalid = QuantumCircuit(backend.num_qubits)
    invalid.cx(0, 2)
    if target_violations(invalid, backend.target) != ["target lacks cx(0, 2)"]:
        raise RuntimeError(f"unsupported coupling status is {target_violations(invalid, backend.target)}")

    if "if_else" not in backend.target.operation_names:
        backend.target.add_instruction(IfElseOp, name="if_else")
    nested = QuantumCircuit(3, 1)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.cx(0, 2)
    nested_violations = target_violations(nested, backend.target)
    if "target lacks cx(0, 2)" not in nested_violations:
        raise RuntimeError(f"unsupported nested coupling status is {nested_violations}")

    fixed_angle_target = Target(num_qubits=1)
    fixed_angle_target.add_instruction(RZGate(math.pi / 2), {(0,): None})
    unsupported_angle = QuantumCircuit(1)
    unsupported_angle.rz(math.pi / 4, 0)
    angle_violations = target_violations(unsupported_angle, fixed_angle_target)
    if angle_violations != ["target lacks rz(0,)"]:
        raise RuntimeError(f"unsupported fixed-angle status is {angle_violations}")

    group = next(group for group in experiment_groups() if group.name == "design_a")
    bounded = _fake_snapshot(FakeFez())
    bounded.name = "bounded-angle"
    bounded.backend = _BoundedAngleBackend()
    bounded_rejections = routing_admission_violations(group, bounded)
    if bounded_rejections != ["bounded-angle Target cannot be filtered without widening its parameter bounds"]:
        raise RuntimeError(f"bounded-angle routing admission reports {bounded_rejections}")
    viable = _fake_snapshot(FakeFez())
    viable.name = "viable"
    trace: dict[str, Any] = {}
    selected = select(group, [bounded, viable], 1, trace, SINGLE_REPLICA_POLICY)
    if selected.snap is not viable:
        raise RuntimeError("bounded-angle admission prevents a later viable system from competing")
    if trace[group.name][bounded.name][1].get("rejected") != bounded_rejections:
        raise RuntimeError("bounded-angle system lacks explicit selection-trace evidence")

    snapshot = _fake_snapshot(backend)
    bad_qubit = _physical(isa)[0]
    snapshot.excluded_qubits[bad_qubit] = "fixture degradation"
    if f"qubit {bad_qubit}" not in compiled_violations(isa, snapshot):
        raise RuntimeError("fresh bad-qubit status fails to reject a routed circuit")

    filtered = _fake_snapshot(FakeFez())
    excluded_edge = next(iter(filtered.backend.target["cz"]))
    filtered.excluded_edges[excluded_edge] = "fixture degradation"
    filtered.admission_target = build_admission_target(filtered)
    if excluded_edge in filtered.admission_target["cz"]:
        raise RuntimeError(f"admission Target retains excluded CZ edge {excluded_edge}")
    reversed_edge = tuple(reversed(excluded_edge))
    if reversed_edge in filtered.admission_target["cz"]:
        raise RuntimeError(f"admission Target retains reverse of excluded CZ edge {excluded_edge}")
    routed_source = QuantumCircuit(2, 2)
    routed_source.h(0)
    routed_source.cz(0, 1)
    routed_source.measure([0, 1], [0, 1])
    for seed in range(4):
        routed = _compile(routed_source, filtered, seed)
        rejected = compiled_violations(routed, filtered)
        if rejected:
            raise RuntimeError(f"admission Target seed {seed} routed through excluded hardware: {rejected}")
        routed_edges = {qargs for operation, qargs in _ops(routed) if operation == "cz"}
        if excluded_edge in routed_edges or reversed_edge in routed_edges:
            raise RuntimeError(f"admission Target seed {seed} used excluded CZ edge {excluded_edge}")


def _verify_snapshot_and_fingerprint_coherence() -> None:
    backend = FakeFez()
    check_snapshot_matches_properties(backend.target, backend.properties(), backend.name)
    snapshot = _fake_snapshot(backend)
    hybrid = next(group for group in experiment_groups() if group.name == "hybrid_shor_mod15")
    choice = select(hybrid, [snapshot], 1, {}, PACKED_REPLICA_POLICY)
    fresh = _fake_snapshot(FakeFez())
    reset_qargs = next(qargs for operation, qargs in _ops(choice.entries[0].packed) if operation == "reset")
    reset_properties = fresh.backend.target["reset"][reset_qargs]
    if reset_properties is None or reset_properties.duration is None:
        raise RuntimeError(f"FakeFez reset{reset_qargs} lacks a duration fixture")
    reset_properties.duration *= 2
    reasons = choice_change_reasons(choice, fresh)
    if "calibration values changed on compiled instructions" not in reasons:
        raise RuntimeError(f"reset Target-property drift is absent from revalidation reasons: {reasons}")

    timing_changed = _fake_snapshot(FakeFez())
    timing_changed.backend.target.granularity += 1
    reasons = choice_change_reasons(choice, timing_changed)
    if "calibration values changed on compiled instructions" not in reasons:
        raise RuntimeError(f"Target timing-constraint drift is absent from revalidation reasons: {reasons}")


def _synthetic_entry(name: str, circuit: QuantumCircuit, ideal: np.ndarray) -> Entry:
    physical_qubits = _physical(circuit) or list(range(circuit.num_qubits))
    return Entry(
        name=name,
        base=circuit,
        ideal=ideal,
        packed=circuit,
        replicas=[circuit],
        prefixes=["r0_"],
        replica_qubits=[physical_qubits],
    )


def _source_entries(group: Group) -> list[Entry]:
    entries: list[Entry] = []
    for member in group.members:
        entries.append(_synthetic_entry(member.name, member.circuit, member.ideal))
        if member.mirror:
            entries.append(_synthetic_entry(member.name + MIRROR_SUFFIX, member.circuit, member.ideal))
    return entries


def _synthetic_fusion_choice(group: Group, snapshot: Snapshot, physical_qubit: int, dynamic: bool) -> Choice:
    """One-register logical entries on a group-specific physical qubit."""
    register = ClassicalRegister(1, "r0_result")
    circuit = QuantumCircuit(QuantumRegister(snapshot.capabilities.num_qubits, "q"), register)
    if dynamic:
        circuit.reset(physical_qubit)
    circuit.measure(physical_qubit, register[0])
    ideal = np.array([1.0, 0.0])
    entries = [
        Entry(
            name=source.name,
            base=circuit,
            ideal=ideal,
            packed=circuit,
            replicas=[circuit],
            prefixes=["r0_"],
            replica_qubits=[[physical_qubit]],
        )
        for source in _source_entries(group)
    ]
    reference = copy.copy(entries[0])
    reference.name = entries[0].name + "_isolated"
    reference.reference = True
    entries.append(reference)
    replica = packing.Replica(0, {physical_qubit: physical_qubit}, 1.0)
    return Choice(group, snapshot, 7, [], [], [], 1.0, entries, [replica])


def _verify_pub_fusion_contracts() -> None:
    snapshot = _fake_snapshot(FakeFez())
    groups = {group.name: group for group in experiment_groups()}
    static_names = ("design_a", "zero_divisor_fringe", "design_c_8_1_4", "design_c_16_1_8", "design_c_32_1_16")
    dynamic_names = ("folded_qpe_mod15", "hybrid_shor_mod15")
    static_choices = [
        _synthetic_fusion_choice(groups[name], snapshot, 2 * index, False) for index, name in enumerate(static_names)
    ]
    dynamic_choices = [
        _synthetic_fusion_choice(groups[name], snapshot, 30 + 2 * index, True)
        for index, name in enumerate(dynamic_names)
    ]
    choices = static_choices + dynamic_choices
    pubs = execution_pubs(choices)
    summary = fusion_summary(pubs)
    expected_summary = {
        "logical_entries": {"static": 29, "dynamic": 9},
        "execution_pubs": {"static": 14, "dynamic": 6},
        "reference_components": {"static": 5, "dynamic": 2},
    }
    for key, expected in expected_summary.items():
        if summary[key] != expected:
            raise RuntimeError(f"PUB fusion {key} is {summary[key]}, expected {expected}")

    no_reference_choices = copy.deepcopy(static_choices[:2])
    for choice in no_reference_choices:
        choice.entries = [entry for entry in choice.entries if not entry.reference]
    no_reference_summary = fusion_summary(execution_pubs(no_reference_choices))
    if (
        no_reference_summary["strategy"] != "aligned_members_without_reference"
        or no_reference_summary["reference_estimand"] is not None
        or no_reference_summary["reference_estimand_by_kind"] != {"static": None, "dynamic": None}
        or no_reference_summary["reference_components"] != {"static": 0, "dynamic": 0}
    ):
        raise RuntimeError(f"reference-free PUB fusion metadata is {no_reference_summary}")
    static_pubs = [pub for pub in pubs if pub.kind == "static"]
    dynamic_pubs = [pub for pub in pubs if pub.kind == "dynamic"]
    if any(_is_dynamic(pub.circuit) for pub in static_pubs):
        raise RuntimeError("static cross-group fusion produced a dynamic PUB")
    if any(not _is_dynamic(pub.circuit) for pub in dynamic_pubs):
        raise RuntimeError("dynamic cross-group fusion produced a static PUB")
    for pub in pubs:
        register_names = [register.name for register in pub.circuit.cregs]
        if len(register_names) != len(set(register_names)):
            raise RuntimeError(f"{pub.name}: fused classical-register namespaces collide")
        manifest_registers = [
            register_name
            for component in pub.manifest()["components"]
            for register_names in component["registers_by_replica"]
            for register_name in register_names
        ]
        if manifest_registers != register_names:
            raise RuntimeError(f"{pub.name}: manifest register order differs from the fused circuit")

    split_choices = [copy.copy(static_choices[0]), copy.copy(static_choices[1])]
    second_snapshot = copy.copy(snapshot)
    second_snapshot.name = "second_backend"
    split_choices[1].snap = second_snapshot
    archived_by_name = {pub.name: pub for pub in execution_pubs(split_choices)}
    for backend_name in (snapshot.name, second_snapshot.name):
        backend_choices = [choice for choice in split_choices if choice.snap.name == backend_name]
        for planned_pub in execution_pubs(backend_choices):
            archived_pub = archived_by_name[planned_pub.name]
            if planned_pub.manifest() != archived_pub.manifest() or planned_pub.circuit != archived_pub.circuit:
                raise RuntimeError(
                    f"{planned_pub.name}: backend partition changes its fused circuit or component manifest"
                )

    shared_pub = static_pubs[0].manifest()
    start = datetime(2026, 10, 10, tzinfo=UTC)
    executions = component_execution_records(
        shared_pub,
        start,
        start + timedelta(seconds=1),
        start - timedelta(minutes=5),
        False,
    )
    if set(executions) != {component["member"] for component in shared_pub["components"]}:
        raise RuntimeError("fused PUB execution window fails to fan out to every logical component")
    if len({json.dumps(evidence, sort_keys=True) for evidence in executions.values()}) != 1:
        raise RuntimeError("logical components of one fused PUB receive different execution windows")

    if len(submission_batches(static_choices, "static", 714_285)) != 1:
        raise RuntimeError("exact static execution bound splits the result-complete fusion cluster")
    if len(submission_batches(dynamic_choices, "dynamic", 1_666_666)) != 1:
        raise RuntimeError("exact dynamic execution bound splits the result-complete fusion cluster")
    for cluster, kind, shots in (
        (static_choices, "static", 714_286),
        (dynamic_choices, "dynamic", 1_666_667),
    ):
        try:
            submission_batches(cluster, kind, shots)
        except LiveRunError:
            pass
        else:
            raise RuntimeError(f"{kind} fusion exceeds the Sampler execution bound")

    submission, runtime_batches = build_submission_plan(choices, _fixture_args(), "0" * 64)
    planned_kinds = [planned_job["kind"] for planned_job in submission["planned_jobs"]]
    runtime_kinds = [kind for _, _, kind, _ in runtime_batches]
    if planned_kinds != ["dynamic", "static"] or runtime_kinds != planned_kinds:
        raise RuntimeError(
            f"submission order is planned={planned_kinds}, runtime={runtime_kinds}; dynamic must run first"
        )

    buffer = tempfile.SpooledTemporaryFile()
    qpy.dump([pub.circuit for pub in pubs], buffer)
    buffer.seek(0)
    round_trip = {circuit.name: circuit for circuit in qpy.load(buffer)}
    buffer.close()
    first_pub = pubs[0]
    first_component = first_pub.components[0]
    extracted = packing.extract(
        round_trip[first_pub.name],
        first_component.register_prefix,
        first_component.entry.replica_qubits[0],
        first_component.entry.name,
    )
    expected_registers = [
        first_component.register_prefix + register.name for register in first_component.entry.packed.cregs
    ]
    if [register.name for register in extracted.cregs] != expected_registers:
        raise RuntimeError("QPY round trip changes fused-component register identity")

    overlap = copy.deepcopy(static_choices[:2])
    overlap[1].entries = copy.deepcopy(overlap[1].entries)
    for entry in overlap[1].entries:
        entry.packed = static_choices[0].entries[0].packed
        entry.replicas = [entry.packed]
        entry.replica_qubits = [[0]]
    try:
        execution_pubs(overlap)
    except ValueError as error:
        if "overlaps fused qubits" not in str(error):
            raise RuntimeError(f"overlapping fusion reports {error}") from error
    else:
        raise RuntimeError("PUB fusion accepts overlapping physical layouts")

    narrow = QuantumCircuit(2, 1)
    wide = QuantumCircuit(3, 1)
    try:
        packing.fuse([narrow, wide], ["g0_", "g1_"], "width_mismatch")
    except ValueError as error:
        if "expected 2" not in str(error):
            raise RuntimeError(f"width mismatch reports {error}") from error
    else:
        raise RuntimeError("PUB fusion accepts components with different widths")

    for circuits, prefixes, failure in (
        ([], [], "empty component list"),
        ([narrow], [], "circuit/prefix count mismatch"),
        ([narrow, copy.copy(narrow)], ["same_", "same_"], "duplicate prefixes"),
        ([narrow], [""], "empty prefix"),
    ):
        try:
            packing.fuse(circuits, prefixes, "invalid_fusion")
        except ValueError:
            pass
        else:
            raise RuntimeError(f"PUB fusion accepts {failure}")

    unnamed_bits = QuantumCircuit(1)
    unnamed_bit = Clbit()
    unnamed_bits.add_bits([unnamed_bit])
    unnamed_bits.measure(0, unnamed_bit)
    try:
        packing.fuse([unnamed_bits], ["g0_"], "unnamed_bits")
    except ValueError as error:
        if "outside named registers" not in str(error):
            raise RuntimeError(f"unnamed classical bits report {error}") from error
    else:
        raise RuntimeError("PUB fusion accepts classical bits outside named registers")


def _zero_replica_distributions(entry: Entry) -> list[np.ndarray]:
    distributions: list[np.ndarray] = []
    for replica in entry.replicas:
        distribution = np.zeros(2**replica.num_clbits)
        distribution[0] = 1.0
        distributions.append(distribution)
    return distributions


def _verify_fused_collection() -> None:
    """Collect one complete mocked job through fused result decoding and execution-window fan-out."""
    backend = _ProbeBackend("viable", FakeFez())
    planning_service = _ProbeService([backend])
    args = _fixture_args(groups=["design_a", "zero_divisor_fringe"], shots=64)
    choices, record = live_run_module.plan(planning_service, args)
    pubs = execution_pubs(choices)
    fused_pub = next((pub for pub in pubs if len(pub.components) > 1), None)
    if fused_pub is None:
        raise RuntimeError("collection fixture produced no cross-group fused PUB")
    record["groups"] = [
        live_run_module._choice_record(
            choice,
            {entry.name: _zero_replica_distributions(entry) for entry in choice.entries},
            choice.snap.calibration,
            args.shots,
        )
        for choice in choices
    ]

    with tempfile.TemporaryDirectory(prefix="gororoba-fused-collection-") as directory:
        run_dir = Path(directory)
        archive_digest = write_archive(run_dir, choices)
        original_configure_sampler = live_run_module.configure_sampler

        def fake_configure_sampler(
            backend: Any,
            kind: str,
            twirl: bool,
            dd: str | None,
            tags: list[str],
            shots: int = 4096,
        ) -> Any:
            del backend, twirl, dd
            return _ProbeSampler(kind, tags, shots, lambda unused_circuits: None)

        live_run_module.configure_sampler = fake_configure_sampler
        try:
            submission, _ = build_submission_plan(choices, args, archive_digest)
        finally:
            live_run_module.configure_sampler = original_configure_sampler
        if len(submission["planned_jobs"]) != 1:
            raise RuntimeError(f"collection fixture planned {len(submission['planned_jobs'])} jobs")
        planned_job = submission["planned_jobs"][0]
        planned_job["budget_before"] = {"instance_sha256_12": "fixture"}
        planned_job["state"] = "submitted"
        job_id = "fused-collection-job"
        submission["jobs"].append(live_run_module._job_record(planned_job, job_id))
        submission["complete"] = True
        record["submission"] = submission
        record["state"] = "submitted"
        write_json(run_dir, record)

        with open(run_dir / "isa.qpy", "rb") as handle:
            archived = {circuit.name: circuit for circuit in qpy.load(handle)}
        pub_results: list[SamplerPubResult] = []
        for pub_manifest in planned_job["pubs"]:
            circuit = archived[pub_manifest["name"]]
            register_data = {
                register.name: BitArray.from_counts({"0" * register.size: args.shots}, num_bits=register.size)
                for register in circuit.cregs
            }
            pub_results.append(SamplerPubResult(DataBin(**register_data), metadata={}))

        base_time = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
        fused_index = next(
            index for index, pub_manifest in enumerate(planned_job["pubs"]) if pub_manifest["name"] == fused_pub.name
        )
        spans: list[_ProbeExecutionSpan] = []
        expected_fused_window = (
            base_time + timedelta(seconds=10 * fused_index),
            base_time + timedelta(seconds=10 * fused_index + 5),
        )
        for index in range(len(pub_results)):
            start = base_time + timedelta(seconds=10 * index)
            if index == fused_index:
                spans.extend(
                    [
                        _ProbeExecutionSpan(start + timedelta(seconds=2), start + timedelta(seconds=3), [index]),
                        _ProbeExecutionSpan(start, start + timedelta(seconds=5), [index]),
                    ]
                )
            else:
                spans.append(_ProbeExecutionSpan(start, start + timedelta(seconds=1), [index]))
        result = PrimitiveResult(pub_results, metadata={"execution": {"execution_spans": spans}})
        windows = pub_windows(result, len(pub_results))
        if len(windows) != len(planned_job["pubs"]) or windows[fused_index] != expected_fused_window:
            raise RuntimeError(f"fused PUB execution windows are {windows}")

        incomplete_spans = [span for span in spans if fused_index not in span.pub_idxs]
        incomplete_result = PrimitiveResult(
            pub_results,
            metadata={"execution": {"execution_spans": incomplete_spans}},
        )
        try:
            pub_windows(incomplete_result, len(pub_results))
        except LiveRunError as error:
            if f"no execution span covers PUB {fused_index}" not in str(error):
                raise RuntimeError(f"missing fused execution span reports {error}") from error
        else:
            raise RuntimeError("fused PUB result accepts a missing execution span")

        collection_service = _CollectionProbeService(backend, {job_id: _ProbeResultJob(result)})
        original_noise_simulator = live_run_module.noise_simulator
        original_run_replicas = live_run_module.run_replicas
        live_run_module.noise_simulator = lambda name, target, props: object()
        live_run_module.run_replicas = lambda noise, entry, shots, seed: _zero_replica_distributions(entry)
        try:
            with redirect_stdout(io.StringIO()):
                collect(collection_service, run_dir)
        finally:
            live_run_module.noise_simulator = original_noise_simulator
            live_run_module.run_replicas = original_run_replicas

        collected = json.loads((run_dir / "collect.json").read_text())
        executed = {
            name: evidence
            for group_record in collected[1:]
            for name, evidence in group_record.get("executed", {}).items()
        }
        fused_members = [component.entry.name for component in fused_pub.components]
        fused_evidence = [executed[name] for name in fused_members]
        if len({json.dumps(evidence, sort_keys=True) for evidence in fused_evidence}) != 1:
            raise RuntimeError("mocked collection gives fused components different execution evidence")
        expected_start, expected_stop = expected_fused_window
        if (
            fused_evidence[0]["pub"] != fused_pub.name
            or fused_evidence[0]["start"] != expected_start.isoformat()
            or fused_evidence[0]["stop"] != expected_stop.isoformat()
            or fused_evidence[0]["calibration_changed_during_shots"]
        ):
            raise RuntimeError(f"mocked fused execution evidence is {fused_evidence[0]}")


def _verify_joint_fusion_placement() -> None:
    snapshot = _fake_snapshot(FakeFez())
    groups = {group.name: group for group in experiment_groups()}
    candidate_sets = [select_candidates(groups[name], [snapshot], 1, {}) for name in ("design_a", "design_c_8_1_4")]
    choices, evidence = select_fusion_choices(candidate_sets, PACKED_REPLICA_POLICY)
    if not evidence["cross_group_disjoint"] or not evidence["within_group_one_hop_separated"]:
        raise RuntimeError(f"joint placement records incomplete separation evidence: {evidence}")
    if any(len(choice.replicas) != 2 for choice in choices):
        raise RuntimeError(
            f"joint placement violates the two-replica cap: {[len(choice.replicas) for choice in choices]}"
        )
    first_qubits = {qubit for replica in choices[0].replicas for qubit in replica.qubits}
    second_qubits = {qubit for replica in choices[1].replicas for qubit in replica.qubits}
    if first_qubits.intersection(second_qubits):
        raise RuntimeError("joint placement gives fused groups overlapping physical qubits")
    graph = packing.coupling_graph(snapshot.admission_target, snapshot.backend.num_qubits)
    for choice in choices:
        first, second = (set(replica.qubits) for replica in choice.replicas)
        if first.intersection(second) or any(graph.has_edge(a, b) for a in first for b in second):
            raise RuntimeError(f"{choice.group.name}: joint placement loses within-group one-hop separation")


def _verify_joint_fusion_candidate_backtracking() -> None:
    """The coupled selector retries after the independently best combination fails."""
    snapshot = _fake_snapshot(FakeFez())
    groups = {group.name: group for group in experiment_groups()}

    def candidate(group_name: str, seed: int, score: float) -> Choice:
        return Choice(groups[group_name], snapshot, seed, [], [], [], score)

    candidate_sets = [
        [candidate("design_a", 11, 0.99), candidate("design_a", 12, 0.80)],
        [candidate("design_c_8_1_4", 21, 0.98), candidate("design_c_8_1_4", 22, 0.90)],
    ]
    attempts: list[tuple[int, ...]] = []

    def forced_joint_placement(choices: list[Choice], policy: ReplicaPolicy) -> dict[str, Any]:
        del policy
        seeds = tuple(choice.seed for choice in choices)
        attempts.append(seeds)
        if seeds == (11, 21):
            raise LiveRunError("fixture rejects the independently best combination")
        return {
            "cross_group_disjoint": True,
            "within_group_one_hop_separated": True,
            "allocation": "fixture",
            "clusters": [],
        }

    original_allocate_fusion_replicas = live_run_module.allocate_fusion_replicas
    original_execution_pubs = live_run_module.execution_pubs
    live_run_module.allocate_fusion_replicas = forced_joint_placement
    live_run_module.execution_pubs = lambda choices: []
    try:
        selected, evidence = select_fusion_choices(candidate_sets, PACKED_REPLICA_POLICY)
    finally:
        live_run_module.allocate_fusion_replicas = original_allocate_fusion_replicas
        live_run_module.execution_pubs = original_execution_pubs

    if attempts != [(11, 21), (11, 22)]:
        raise RuntimeError(f"joint candidate backtracking attempts are {attempts}")
    if [choice.seed for choice in selected] != [11, 22]:
        raise RuntimeError(f"joint candidate backtracking selected {[choice.seed for choice in selected]}")
    selection = evidence.get("candidate_selection", {})
    if (
        selection.get("attempted_combinations") != 2
        or selection.get("rejected_combinations") != 1
        or [item["candidate_index"] for item in selection.get("selected", [])] != [0, 1]
    ):
        raise RuntimeError(f"joint candidate backtracking evidence is {selection}")


def _fixture_args(**overrides: Any) -> argparse.Namespace:
    values = {
        "backends": None,
        "groups": None,
        "max_pending": None,
        "seeds": 1,
        "started": "2026-10-10T00:00:00.000000+00:00",
        "shots": 4096,
        "twirl": False,
        "dd": None,
        "min_remaining_seconds": 0.0,
        "replica_floor": PACKED_REPLICA_POLICY.floor,
        "max_replicas": PACKED_REPLICA_POLICY.max_replicas,
        "isolated_reference": PACKED_REPLICA_POLICY.isolated_reference,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _verify_schema_lifecycle() -> None:
    backend = _ProbeBackend("viable", FakeFez())
    service = _ProbeService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    choices, record = live_run_module.plan(service, args)
    if (
        record["schema_version"] != RECORD_SCHEMA_VERSION
        or record["schema_contract"] != RECORD_SCHEMA_CONTRACT
        or record["state"] != "planned"
    ):
        raise RuntimeError("live planning fails to create a schema-5 fused-PUB planned record")
    for field_name in (
        "system_inventory",
        "backends",
        "circuit_requirements",
        "execution_requirements",
        "fusion_placement",
        "fusion_summary",
        "execution_pubs",
        "selection_trace",
    ):
        if field_name not in record:
            raise RuntimeError(f"schema-5 planning record lacks {field_name}")
    requirements = execution_requirements(choices[0])
    if requirements["entries"] != 3 or requirements["isolated_references"] != 1:
        raise RuntimeError(f"schema-5 execution requirements are {requirements}")
    exact_batches = submission_batches(choices, "dynamic")
    if len(exact_batches) != 1 or len(exact_batches[0]) != 3:
        raise RuntimeError("result-complete fusion cluster fails to retain the packed group")
    single_choice = select(
        choices[0].group,
        [choices[0].snap],
        1,
        {},
        SINGLE_REPLICA_POLICY,
    )
    if len(single_choice.entries) != 2 or execution_requirements(single_choice)["isolated_references"] != 0:
        raise RuntimeError("single-replica policy creates the wrong execution entry count")
    live_run_module.evaluate(choices, record)

    approval_choices = list(choices)
    approval_record = copy.deepcopy(record)
    revised_choice = copy.copy(choices[0])
    revised_choice.layout = list(reversed(revised_choice.layout))
    approval_checkpoints: list[dict[str, Any]] = []
    sampler_constructions = 0

    def approval_checkpoint() -> None:
        approval_checkpoints.append(copy.deepcopy(approval_record))

    def changed_select_candidates(
        group: Group,
        snaps: list[Snapshot],
        seeds: int,
        log: dict[str, Any],
    ) -> list[Choice]:
        del snaps, seeds
        log[group.name] = {"fixture": [{"stage": "renewed_approval_contract"}]}
        return [revised_choice]

    def forbidden_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
    ) -> Any:
        del backend, kind, twirl, dd, tags, shots
        nonlocal sampler_constructions
        sampler_constructions += 1
        raise RuntimeError("Sampler construction reached after approved circuits changed")

    original_select_candidates = live_run_module.select_candidates
    original_configure_sampler = live_run_module.configure_sampler
    with tempfile.TemporaryDirectory(prefix="gororoba-renewed-approval-") as directory:
        run_dir = Path(directory)
        live_run_module.select_candidates = changed_select_candidates
        live_run_module.configure_sampler = forbidden_configure_sampler
        try:
            try:
                live_run_module.submit(
                    service,
                    approval_choices,
                    args,
                    approval_record,
                    lambda: write_archive(run_dir, approval_choices),
                    approval_checkpoint,
                )
            except LiveRunError as error:
                if "renewed written submission case and user approval" not in str(error):
                    raise RuntimeError(f"changed approved plan reports {error}") from error
            else:
                raise RuntimeError("changed approved plan reaches submission")
        finally:
            live_run_module.select_candidates = original_select_candidates
            live_run_module.configure_sampler = original_configure_sampler
        if sampler_constructions:
            raise RuntimeError("changed approved plan constructs a Runtime Sampler")
        if approval_record["state"] != "approval_required" or "submission" in approval_record:
            raise RuntimeError("changed approved plan fails to retain a submit-free lifecycle state")
        if len(approval_checkpoints) != 1:
            raise RuntimeError(f"changed approved plan writes {len(approval_checkpoints)} approval checkpoints")
        renewed_approval = approval_record.get("renewed_approval", {})
        archive_digest = hashlib.sha256((run_dir / "isa.qpy").read_bytes()).hexdigest()
        if renewed_approval.get("qpy_archive_sha256") != archive_digest:
            raise RuntimeError("renewed approval evidence lacks the revised QPY identity")
        changed_groups = renewed_approval.get("changed_groups", {})
        if (
            choices[0].group.name not in changed_groups
            or "initial layout changed" not in changed_groups[choices[0].group.name]["reasons"]
        ):
            raise RuntimeError(f"renewed approval evidence loses the selection change: {changed_groups}")

    checkpoints: list[dict[str, Any]] = []
    run_observations: list[list[str]] = []

    def checkpoint() -> None:
        checkpoints.append(copy.deepcopy(record))

    def before_run(circuits: list[QuantumCircuit]) -> None:
        if not checkpoints:
            raise RuntimeError("mocked Sampler.run precedes every record checkpoint")
        submission = checkpoints[-1].get("submission", {})
        planned_jobs = submission.get("planned_jobs", [])
        if not planned_jobs or any("recovery_tags" not in entry for entry in planned_jobs):
            raise RuntimeError("mocked Sampler.run precedes the complete recovery ledger")
        if planned_jobs[0].get("state") != "attempted":
            raise RuntimeError("mocked Sampler.run precedes its attempted-state checkpoint")
        run_observations.append([circuit.name for circuit in circuits])

    original_configure_sampler = live_run_module.configure_sampler

    def fake_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
    ) -> Any:
        del backend, twirl, dd
        return _ProbeSampler(kind, tags, shots, before_run)

    with tempfile.TemporaryDirectory(prefix="gororoba-schema5-") as directory:
        run_dir = Path(directory)
        live_run_module.configure_sampler = fake_configure_sampler
        try:
            live_run_module.submit(
                service,
                choices,
                args,
                record,
                lambda: write_archive(run_dir, choices),
                checkpoint,
            )
        finally:
            live_run_module.configure_sampler = original_configure_sampler

        if not record.get("revalidation"):
            raise RuntimeError("submission record lacks a fresh revalidation entry")
        if record["state"] != "submitted" or not record["submission"]["complete"]:
            raise RuntimeError("mocked submission fails to reach the submitted lifecycle state")
        if len(run_observations) != 1:
            raise RuntimeError(f"mocked Sampler received {len(run_observations)} calls")
        missing, _, _ = submission_gaps(record["submission"])
        if missing:
            raise RuntimeError(f"complete mocked submission reports missing jobs: {missing}")
        duplicate_member_submission = copy.deepcopy(record["submission"])
        duplicate_member_submission["planned_jobs"][0]["members"].append(
            duplicate_member_submission["planned_jobs"][0]["members"][0]
        )
        try:
            submission_gaps(duplicate_member_submission)
        except LiveRunError as error:
            if "repeats a logical member" not in str(error):
                raise RuntimeError(f"duplicate planned member reports {error}") from error
        else:
            raise RuntimeError("submission ledger accepts a repeated logical member within one job")
        mismatched_pub_submission = copy.deepcopy(record["submission"])
        mismatched_job = mismatched_pub_submission["planned_jobs"][0]
        mismatched_job["pubs"][0]["backend"] = "different-backend"
        mismatched_job["recovery_tags"] = _recovery_tags(
            args.started,
            mismatched_job["backend"],
            mismatched_job["kind"],
            mismatched_job["batch_index"],
            mismatched_job["batch_count"],
            mismatched_job["pubs"],
            mismatched_job["qpy_archive_sha256"],
        )
        try:
            submission_gaps(mismatched_pub_submission)
        except LiveRunError as error:
            if "different backend or kind" not in str(error):
                raise RuntimeError(f"mismatched planned PUB ownership reports {error}") from error
        else:
            raise RuntimeError("submission ledger accepts a PUB owned by a different backend")
        planned_job = record["submission"]["planned_jobs"][0]
        alternate_tags = _recovery_tags(
            args.started,
            planned_job["backend"],
            planned_job["kind"],
            planned_job["batch_index"],
            planned_job["batch_count"],
            planned_job["pubs"],
            "1" * 64,
        )
        if alternate_tags == planned_job["recovery_tags"]:
            raise RuntimeError("packed QPY digest fails to change the recovery identity")

        write_json(run_dir, record)
        round_trip_record = json.loads((run_dir / "record.json").read_text())
        qpy_bytes = (run_dir / "isa.qpy").read_bytes()
        with open(run_dir / "isa.qpy", "rb") as handle:
            round_trip_circuits = {circuit.name: circuit for circuit in qpy.load(handle)}
        if (
            round_trip_record["schema_version"] != RECORD_SCHEMA_VERSION
            or round_trip_record["schema_contract"] != RECORD_SCHEMA_CONTRACT
        ):
            raise RuntimeError("schema-5 JSON round trip changes the record contract")
        if hashlib.sha256(qpy_bytes).hexdigest() != round_trip_record["submission"]["qpy_archive_sha256"]:
            raise RuntimeError("schema-5 QPY archive digest changes after its checkpoint")
        for planned_job in round_trip_record["submission"]["planned_jobs"]:
            for pub in planned_job["pubs"]:
                if pub["name"] not in round_trip_circuits:
                    raise RuntimeError(f"schema-5 QPY round trip loses fused PUB {pub['name']}")
        register_tampered = copy.deepcopy(round_trip_record)
        register_tampered["submission"]["planned_jobs"][0]["pubs"][0]["components"][0]["registers_by_replica"][0][0] = (
            "wrong_register"
        )
        try:
            _archived_entries(register_tampered, round_trip_circuits)
        except LiveRunError as error:
            if "register order differs from isa.qpy" not in str(error):
                raise RuntimeError(f"tampered fused register manifest reports {error}") from error
        else:
            raise RuntimeError("schema-5 archive reconstruction accepts a false register manifest")
        rebuilt = _archived_entries(round_trip_record, round_trip_circuits)
        archived_entries = rebuilt["hybrid_shor_mod15"]
        if [entry.name for entry in archived_entries] != [entry.name for entry in choices[0].entries]:
            raise RuntimeError("schema-5 archive reconstruction changes logical entry identity")
        if any(
            len(entry.prefixes) != len(entry.replicas) or len(entry.replica_qubits) != len(entry.replicas)
            for entry in archived_entries
        ):
            raise RuntimeError("schema-5 archive reconstruction changes replica metadata")

        incomplete_record = copy.deepcopy(round_trip_record)
        incomplete_record["state"] = "submission_started"
        incomplete_record["submission"]["jobs"] = []
        incomplete_record["submission"]["complete"] = False
        for planned_job in incomplete_record["submission"]["planned_jobs"]:
            planned_job["state"] = "planned"
        write_json(run_dir, incomplete_record)
        collect(service, run_dir)
        collection = json.loads((run_dir / "collect.json").read_text())
        if (
            collection[0]["members_without_recorded_job_id"]
            != incomplete_record["submission"]["planned_jobs"][0]["members"]
        ):
            raise RuntimeError(f"partial collection gap evidence is {collection[0]}")
        (run_dir / "isa.qpy").write_bytes(qpy_bytes + b"tampered")
        try:
            collect(service, run_dir)
        except LiveRunError as error:
            if "archive digest" not in str(error):
                raise RuntimeError(f"tampered QPY archive reports {error}") from error
        else:
            raise RuntimeError("collection accepts a QPY archive after byte tampering")

    recovery_submission = copy.deepcopy(record["submission"])
    recovery_submission["jobs"] = []
    recovery_submission["complete"] = False
    recovery_submission["planned_jobs"][0]["state"] = "attempted"
    recovery_service = _ProbeService([backend], [_ProbeJob("recovered-job-id")])
    if not reconcile_attempted_jobs(recovery_service, recovery_submission):
        raise RuntimeError("attempted-job reconciliation reports no record change")
    if recovery_submission["jobs"][0]["job_id"] != "recovered-job-id":
        raise RuntimeError("attempted-job reconciliation records the wrong job id")
    if recovery_service.recovery_queries[0]["job_tags"] != recovery_submission["planned_jobs"][0]["recovery_tags"]:
        raise RuntimeError("attempted-job reconciliation changes the recovery tags")
    if recovery_service.recovery_queries[0]["instance"] != "fixture-instance":
        raise RuntimeError("attempted-job reconciliation queries the wrong instance")
    if submission_gaps(recovery_submission)[0]:
        raise RuntimeError("recovered submission retains an unexplained ledger gap")

    for matches in ([], [_ProbeJob("first"), _ProbeJob("second")]):
        unresolved = copy.deepcopy(record["submission"])
        unresolved["jobs"] = []
        unresolved["complete"] = False
        unresolved["planned_jobs"][0]["state"] = "attempted"
        try:
            reconcile_attempted_jobs(_ProbeService([backend], matches), unresolved)
        except LiveRunError:
            pass
        else:
            raise RuntimeError(f"recovery accepted {len(matches)} matching jobs")

    partial = copy.deepcopy(record["submission"])
    partial["jobs"] = []
    partial["complete"] = False
    missing_jobs, missing_backends, missing_members = submission_gaps(partial)
    planned_job = partial["planned_jobs"][0]
    if missing_backends != [planned_job["backend"]] or missing_members != planned_job["members"]:
        raise RuntimeError(f"partial submission gaps are backends={missing_backends} members={missing_members}")
    if len(missing_jobs) != 1 or missing_jobs[0]["batch_index"] != planned_job["batch_index"]:
        raise RuntimeError(f"partial submission batch evidence is {missing_jobs}")
    partial["complete"] = True
    try:
        submission_gaps(partial)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("complete ledger accepts a missing submitted-job record")

    tampered_plan = copy.deepcopy(record["submission"])
    tampered_plan["planned_jobs"][0]["pubs"][0]["components"][0]["register_prefix"] = "tampered_"
    try:
        submission_gaps(tampered_plan)
    except LiveRunError as error:
        if "recovery tags" not in str(error):
            raise RuntimeError(f"planned fused-PUB manifest tampering reports {error}") from error
    else:
        raise RuntimeError("ledger accepts planned fused-PUB manifest tampering")

    tampered_job = copy.deepcopy(record["submission"])
    tampered_job["jobs"][0]["pubs"][0]["components"][0]["register_prefix"] = "tampered_"
    try:
        submission_gaps(tampered_job)
    except LiveRunError as error:
        if "differs from its plan in pubs" not in str(error):
            raise RuntimeError(f"submitted fused-PUB manifest tampering reports {error}") from error
    else:
        raise RuntimeError("ledger accepts submitted fused-PUB manifest tampering")


def _verify_schema_discrimination() -> None:
    """Incompatible historical schema-3 and schema-4 shapes fail before collection."""
    historical_records = (
        {"schema_version": 3, "system_inventory": {}, "code_commit": {"head": "capability-history"}},
        {"schema_version": 3, "groups": [{"replicas": []}], "code_commit": {"head": "replica-history"}},
        {
            "schema_version": 4,
            "schema_contract": "live-target-packed-replicas-v1",
            "experiment_digest": experiment_digest(),
            "code_commit": {"head": "packed-replica-history"},
        },
    )
    with tempfile.TemporaryDirectory(prefix="gororoba-schema-history-") as directory:
        run_dir = Path(directory)
        buffer = tempfile.SpooledTemporaryFile()
        qpy.dump([], buffer)
        buffer.seek(0)
        (run_dir / "isa.qpy").write_bytes(buffer.read())
        buffer.close()
        for historical_record in historical_records:
            (run_dir / "record.json").write_text(json.dumps(historical_record))
            try:
                collect(_ProbeService([]), run_dir)
            except LiveRunError as error:
                expected_schema = f"schema {historical_record['schema_version']}"
                if expected_schema not in str(error):
                    raise RuntimeError(f"historical {expected_schema} rejection reports {error}") from error
            else:
                raise RuntimeError(
                    f"schema-{RECORD_SCHEMA_VERSION} collection accepts a historical "
                    f"schema-{historical_record['schema_version']} record"
                )


def _verify_every_job_revalidates() -> None:
    backend = _ProbeBackend("viable", FakeFez())
    service = _ProbeService([backend])
    snapshots, _, _ = discover_snapshots(service, None, None)
    groups = {group.name: group for group in experiment_groups()}
    choices = [
        select(groups[name], snapshots, 1, {}, SINGLE_REPLICA_POLICY) for name in ("design_a", "hybrid_shor_mod15")
    ]
    args = _fixture_args(max_replicas=1, isolated_reference=False)
    record: dict[str, Any] = {"shots": args.shots}
    checkpoints: list[dict[str, Any]] = []
    run_count = 0

    def checkpoint() -> None:
        checkpoints.append(copy.deepcopy(record))

    def after_run() -> None:
        nonlocal run_count
        run_count += 1
        backend._failure_stage = "status"

    original_configure_sampler = live_run_module.configure_sampler

    def fake_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
    ) -> Any:
        del backend, twirl, dd
        return _ProbeSampler(kind, tags, shots, lambda unused_circuits: None, after_run)

    live_run_module.configure_sampler = fake_configure_sampler
    try:
        try:
            live_run_module.submit(service, choices, args, record, lambda: "0" * 64, checkpoint)
        except LiveRunError as error:
            if "status" not in str(error):
                raise RuntimeError(f"second-job refresh reports {error}") from error
        else:
            raise RuntimeError("second job submits after its status probe fails")
    finally:
        live_run_module.configure_sampler = original_configure_sampler
    if run_count != 1 or len(record["submission"]["jobs"]) != 1:
        raise RuntimeError("later-job failure changes the number of accepted mocked jobs")
    missing_jobs, _, missing_members = submission_gaps(record["submission"])
    if len(missing_jobs) != 1 or len(missing_members) != 2:
        raise RuntimeError(f"later-job failure loses unsent evidence: {missing_jobs}")


def _verify_live_reselection() -> None:
    backend = FakeFez()
    degraded = _fake_snapshot(backend)
    degraded.name = "degraded"
    degraded.excluded_qubits.update({qubit: "fixture degradation" for qubit in range(backend.num_qubits)})
    viable = _fake_snapshot(backend)
    viable.name = "viable"
    group = next(group for group in experiment_groups() if group.name == "design_a")
    trace: dict[str, Any] = {}
    choice = select(group, [degraded, viable], 1, trace, PACKED_REPLICA_POLICY)
    if choice.snap.name != "viable":
        raise RuntimeError(f"selector chose {choice.snap.name} instead of the viable system")
    if not any(entry.get("rejected") for entry in trace[group.name]["degraded"]):
        raise RuntimeError("degraded routed patch leaves no rejection evidence")

    fresh = _fake_snapshot(backend)
    fresh.name = "viable"
    if len(choice.replicas) < 2:
        raise RuntimeError("packed reselection fixture produces fewer than two replicas")
    used_qubit = choice.replicas[1].qubits[0]
    fresh.excluded_qubits[used_qubit] = "new fixture degradation"
    reasons = choice_change_reasons(choice, fresh)
    if not any(f"qubit {used_qubit}" in reason for reason in reasons):
        raise RuntimeError(f"pre-submit gate misses newly degraded qubit {used_qubit}: {reasons}")

    restricted = _fake_snapshot(FakeFez())
    restricted.name = "viable"
    restricted.excluded_qubits[choice.replicas[0].qubits[0]] = "temporary fixture degradation"
    restricted_choice = select(group, [restricted], 1, {}, PACKED_REPLICA_POLICY)
    recovered = _fake_snapshot(FakeFez())
    recovered.name = "viable"
    recovered_choice = select(group, [recovered], 1, {}, PACKED_REPLICA_POLICY)
    recovery_reasons = choice_reselection_reasons(restricted_choice, recovered_choice)
    if not any("replica placements changed" in reason for reason in recovery_reasons):
        raise RuntimeError(f"recovered hardware fails to trigger fresh placement: {recovery_reasons}")

    alternate = _fake_snapshot(FakeFez())
    alternate.name = "alternate"
    alternate_choice = select(group, [alternate], 1, {}, PACKED_REPLICA_POLICY)
    alternate_reasons = choice_reselection_reasons(recovered_choice, alternate_choice)
    if not any("backend changed" in reason for reason in alternate_reasons):
        raise RuntimeError(f"newly eligible alternate system leaves no reselection reason: {alternate_reasons}")


def _verify_discovery_failure_isolation() -> None:
    group = next(group for group in experiment_groups() if group.name == "design_a")
    for failure_stage in ("refresh", "properties", "status", "capabilities"):
        fake_backend = FakeFez()
        broken_name = f"broken_{failure_stage}"
        service = _ProbeService(
            [
                _ProbeBackend(broken_name, fake_backend, failure_stage),
                _ProbeBackend("viable", fake_backend),
            ]
        )
        snapshots, skipped, inventory = discover_snapshots(service, None, None)
        if [snapshot.name for snapshot in snapshots] != ["viable"]:
            raise RuntimeError(f"{failure_stage} failure suppresses viable discovery")
        reason = skipped.get(broken_name, {}).get("reason", "")
        if failure_stage not in reason:
            raise RuntimeError(f"{failure_stage} probe reports {reason!r}")
        if inventory[broken_name]["eligibility"] != "probe_failed":
            raise RuntimeError(f"{failure_stage} probe lacks probe_failed inventory state")
        if inventory["viable"]["eligibility"] != "eligible":
            raise RuntimeError(f"{failure_stage} probe changes viable inventory state")
        trace: dict[str, Any] = {}
        selected = select(group, snapshots, 1, trace, SINGLE_REPLICA_POLICY)
        if selected.snap.name != "viable":
            raise RuntimeError(f"{failure_stage} failure prevents viable selection")


def _verify() -> None:
    _verify_dynamic_classification()
    _verify_nested_operations()
    _verify_result_register_order()
    _verify_twirling_shot_contract()
    _verify_capability_admission()
    _verify_discovered_capabilities()
    _verify_target_and_bad_qubit_status()
    _verify_snapshot_and_fingerprint_coherence()
    _verify_pub_fusion_contracts()
    _verify_fused_collection()
    _verify_joint_fusion_placement()
    _verify_joint_fusion_candidate_backtracking()
    _verify_schema_lifecycle()
    _verify_schema_discrimination()
    _verify_every_job_revalidates()
    _verify_live_reselection()
    _verify_discovery_failure_isolation()
    _verify_packed_replica_split()
    _verify_packed_static_stays_static()
    _verify_rate_keys()
    _verify_replica_floor_resolution()
    first_digest = experiment_digest()
    second_digest = experiment_digest()
    if len(first_digest) != 64 or first_digest != second_digest:
        raise RuntimeError("experiment source manifest digest is unstable")
    print(
        "runtime contracts: discovery, direct pinned lookup, capability admission, "
        "bounded-angle isolation, coherent snapshots, Target routing, joint placement, "
        "cross-group PUB fusion, renewed approval, job revalidation, schema lifecycle, "
        "recovery, result order, rate keys, and digest pass"
    )


if __name__ == "__main__":
    _verify()

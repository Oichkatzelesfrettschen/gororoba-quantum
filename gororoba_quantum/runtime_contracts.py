"""Credential-free contracts for live admission, PUB fusion, approval, and Runtime helpers."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import io
import json
import math
import os
import shutil
import tempfile
from collections.abc import Callable, Collection
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
import rustworkx as rx
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit.circuit import Clbit, Measure, Parameter
from qiskit.circuit.controlflow import IfElseOp
from qiskit.circuit.library import CZGate, RZGate, SXGate
from qiskit.primitives import StatevectorSampler
from qiskit.primitives.containers import DataBin, PrimitiveResult, SamplerPubResult
from qiskit.quantum_info import Operator
from qiskit.transpiler import InstructionProperties, QubitProperties, Target
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2
from qiskit_ibm_runtime.fake_provider import local_service as runtime_local_service
from qiskit_ibm_runtime.results.quantum_program import (
    ChunkPart,
    ChunkSpan,
    ItemMetadata,
    Metadata,
    QuantumProgramItemResult,
    QuantumProgramResult,
    SchedulerTiming,
)

import hybrid_shor  # noqa: F401 - proves the digest ignores module load order
import live_run as live_run_module
import packing
import parallel
import variance
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
    _control_flow_count,
    _distribution,
    _feed_forward_stages,
    _has_feed_forward,
    _is_dynamic,
    _ops,
    _physical,
    _pub_counts,
    _recovery_tags,
    approved_backend_scope,
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
    corrected_summary,
    discover_snapshots,
    execution_pubs,
    execution_requirements,
    experiment_digest,
    fusion_summary,
    group_requirements,
    job_usage_record,
    mirror_isa,
    packing_schedule,
    pub_timing,
    pub_windows,
    reconcile_attempted_jobs,
    replica_floor,
    replica_statistics,
    routing_admission_violations,
    scheduled_duration,
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
from packing import Replica

SINGLE_REPLICA_POLICY = ReplicaPolicy(max_replicas=1, isolated_reference=False)
PACKED_REPLICA_POLICY = ReplicaPolicy(floor=0.8, max_replicas=2, isolated_reference=True)
# The path-graph backtracking fixture places two groups on adjacent sites,
# which the cross-group buffer forbids; it exercises the search alone.
ADJACENT_REPLICA_POLICY = ReplicaPolicy(floor=0.8, max_replicas=2, isolated_reference=True, cross_group_buffer=False)


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
    """The documented execution_spans shape: start, stop, and the PUB indices a span holds."""

    def __init__(self, start: datetime, stop: datetime, pub_idxs: list[int]):
        self.start = start
        self.stop = stop
        self.pub_idxs = pub_idxs


def _executor_result(
    backend: Any, circuits: list[QuantumCircuit], shots: int, chunks: list[ChunkSpan], durations: list[int]
) -> PrimitiveResult[SamplerPubResult]:
    """An all-zero Sampler result decoded by the executor Sampler's own post-processor.

    The local service's program runner is replaced by one that returns zero
    bits, the given chunk timing, and per-item scheduler durations, so the
    result metadata takes exactly the shape sampler_v2_post_processor_v0_1
    gives a hardware job.
    """

    def execute(backend: Any, program: Any, options: Any) -> QuantumProgramResult:
        del backend, options
        items = [
            QuantumProgramItemResult(
                {creg.name: np.zeros((program.shots, creg.size), dtype=bool) for creg in item.circuit.cregs},
                metadata=ItemMetadata(scheduler_timing=SchedulerTiming(timing="", circuit_duration=duration)),
            )
            for item, duration in zip(program.items, durations, strict=True)
        ]
        result = QuantumProgramResult(items, Metadata(chunk_timing=chunks), program.passthrough_data)
        result._semantic_role = program._semantic_role
        return result

    original = runtime_local_service.run_quantum_program
    runtime_local_service.run_quantum_program = execute
    try:
        sampler = Sampler(mode=backend)
        sampler.options.execution.scheduler_timing = True
        return sampler.run(circuits, shots=shots).result()
    finally:
        runtime_local_service.run_quantum_program = original


class _ProbeResultJob:
    """A finished job whose usage metadata and canonical charge the contract chooses."""

    def __init__(
        self,
        result: PrimitiveResult[SamplerPubResult],
        status: str = "DONE",
        usage: dict[str, Any] | None = None,
        charge: Any = None,
    ):
        self._result = result
        self._status = status
        self._usage = usage
        self._charge = charge

    def result(self) -> PrimitiveResult[SamplerPubResult]:
        return self._result

    def status(self) -> str:
        return self._status

    def metrics(self) -> dict[str, Any]:
        return {"usage": self._usage} if self._usage is not None else {}

    def usage(self, partial: bool = False) -> Any:
        del partial
        return self._charge


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
    def __init__(self, kind: str, tags: list[str], shots: int, max_execution_seconds: int | None = None):
        self._value: dict[str, Any] = {"kind": kind, "environment": {"job_tags": tags}, "default_shots": shots}
        if max_execution_seconds is not None:
            self._value["max_execution_time"] = int(max_execution_seconds)

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
        max_execution_seconds: int | None = None,
    ):
        self.options = _ProbeSamplerOptions(kind, tags, shots, max_execution_seconds)
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


def _verify_dynamic_mitigation_boundaries() -> None:
    """Feed-forward controls use identity nulls, never unitary mirrors or terminal readout inversion."""
    groups = {group.name: group for group in experiment_groups()}
    for group in groups.values():
        invalid = [member.name for member in group.members if member.mirror and _is_dynamic(member.circuit)]
        if invalid:
            raise RuntimeError(f"{group.name}: dynamic members request ODR mirrors: {invalid}")

    folded = groups["folded_qpe_mod15"]
    folded_primary = next(member.circuit for member in folded.members if member.name == "folded_qpe_s1")
    folded_null = next(member.circuit for member in folded.members if member.name == "folded_qpe_null")
    hybrid = groups["hybrid_shor_mod15"]
    hybrid_primary = next(member.circuit for member in hybrid.members if member.name == "hybrid_shor_N15_a2")
    hybrid_null = next(member.circuit for member in hybrid.members if member.name == "hybrid_shor_N15_a2_null")

    def dynamic_schedule(circuit: QuantumCircuit) -> list[str]:
        return [
            instruction.operation.name
            for instruction in circuit.data
            if isinstance(instruction.operation, IfElseOp) or instruction.operation.name in ("measure", "reset")
        ]

    for label, primary, null in (
        ("folded QPE", folded_primary, folded_null),
        ("hybrid Shor", hybrid_primary, hybrid_null),
    ):
        if dynamic_schedule(primary) != dynamic_schedule(null):
            raise RuntimeError(f"{label} identity null changes the dynamic-control schedule")
        try:
            mirror_isa(primary, FakeFez(), f"{label} mirror")
        except LiveRunError as error:
            if "unitary static circuit" not in str(error):
                raise RuntimeError(f"{label} ODR rejection reports {error}") from error
        else:
            raise RuntimeError(f"{label} dynamic circuit reaches ODR mirror construction")

    entries = [_synthetic_entry(member.name, member.circuit, member.ideal) for member in folded.members]
    skipped = corrected_summary(folded, entries, {}, None)
    expected = {"skipped": "feed-forward circuit: mid-circuit readout error changes later quantum evolution"}
    if skipped != expected:
        raise RuntimeError(f"feed-forward readout correction reports {skipped}")

    reset_only = QuantumCircuit(1, 1, name="reset_only")
    reset_only.reset(0)
    reset_only.measure(0, 0)
    reset_group = Group("reset_only", (), lambda distributions: {"p0": float(distributions["reset_only"][0])})
    reset_entry = _synthetic_entry("reset_only", reset_only, np.array([1.0, 0.0]))

    class ExactReadout:
        def qubit_property(self, qubit: int, name: str) -> tuple[float]:
            del qubit, name
            return (0.0,)

    reset_summary = corrected_summary(
        reset_group,
        [reset_entry],
        {"reset_only": [np.array([1.0, 0.0])]},
        ExactReadout(),
    )
    if reset_summary != {"p0": 1.0}:
        raise RuntimeError(f"reset-only terminal readout correction reports {reset_summary}")

    # A group that propagates covariance receives M p and M (diag(p) - p p^T) M^T.
    class AsymmetricReadout:
        def qubit_property(self, qubit: int, name: str) -> tuple[float]:
            del qubit
            return ({"prob_meas1_prep0": 0.1, "prob_meas0_prep1": 0.2}[name],)

    measured = QuantumCircuit(1, 1, name="measured")
    measured.measure(0, 0)
    raw = np.array([0.7, 0.3])
    inverse = np.linalg.inv(np.array([[0.9, 0.2], [0.1, 0.8]]))
    covariance_group = Group(
        "covariance_aware",
        (),
        lambda distributions: {"p0": float(distributions["measured"][0]), "variance": -1.0},
        summarize_with_covariance=lambda distributions, covariances: {
            "p0": float(distributions["measured"][0]),
            "variance": float(covariances["measured"][0, 0]),
        },
    )
    covariance_summary = corrected_summary(
        covariance_group,
        [_synthetic_entry("measured", measured, np.array([1.0, 0.0]))],
        {"measured": [raw]},
        AsymmetricReadout(),
    )
    expected_p0 = float((inverse @ raw)[0])
    expected_variance = float((inverse @ (np.diag(raw) - np.outer(raw, raw)) @ inverse.T)[0, 0])
    if not (
        math.isclose(covariance_summary["p0"], expected_p0, rel_tol=1e-12)
        and math.isclose(covariance_summary["variance"], expected_variance, rel_tol=1e-12)
        and expected_variance > expected_p0 * (1.0 - expected_p0)
    ):
        raise RuntimeError(f"readout-inverted covariance reaches the summary as {covariance_summary}")


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


def _verify_packing_global_phase() -> None:
    """Packing and fusion preserve full tensor-product operators, including phase."""
    identity = np.eye(2, dtype=complex)

    def fixture(
        active: int, phase: float, angle: float, gates: bool, measured: bool
    ) -> tuple[QuantumCircuit, np.ndarray]:
        circuit = QuantumCircuit(4, int(measured), global_phase=phase)
        local = QuantumCircuit(1, global_phase=phase)
        if gates:
            circuit.h(active)
            circuit.rz(angle, active)
            local.h(0)
            local.rz(angle, 0)
        if measured:
            circuit.measure(active, 0)
        return circuit, Operator(local).data

    def exact_operator(circuit: QuantumCircuit, expected: np.ndarray, label: str) -> None:
        actual = Operator(circuit.remove_final_measurements(inplace=False)).data
        if not np.allclose(actual, expected, rtol=0, atol=1e-12):
            error = float(np.max(np.abs(actual - expected)))
            raise RuntimeError(f"{label}: packed full operator differs by {error}")
        if _is_dynamic(circuit):
            raise RuntimeError(f"{label}: terminal measurements became dynamic")

    for phase in (0.3, -0.41, math.pi, 2 * math.pi + 0.19, -2 * math.pi - 0.29):
        for gates in (False, True):
            for measured in (False, True):
                first, first_operator = fixture(0, phase, 0.37, gates, measured)
                second, second_operator = fixture(2, -0.27, -0.21, gates, measured)
                originals = (first.copy(), second.copy())
                single = packing.pack(first, [Replica(0, {0: 0}, 1.0)], "single_phase")
                exact_operator(single, np.kron(np.eye(8), first_operator), "single replica")
                fused_single = packing.fuse([first], ["g0_"], "single_fused_phase")
                exact_operator(fused_single, np.kron(np.eye(8), first_operator), "single fusion component")
                fused_sources = packing.fuse([first, second], ["g0_", "g1_"], "source_phase_fusion")
                exact_operator(
                    fused_sources,
                    np.kron(np.kron(identity, second_operator), np.kron(identity, first_operator)),
                    "two source components",
                )
                packed_first = packing.pack(
                    first, [Replica(0, {0: 0}, 1.0), Replica(1, {0: 1}, 1.0)], "first_phase_replicas"
                )
                packed_second = packing.pack(
                    second, [Replica(0, {2: 2}, 1.0), Replica(1, {2: 3}, 1.0)], "second_phase_replicas"
                )
                first_pair = np.kron(first_operator, first_operator)
                second_pair = np.kron(second_operator, second_operator)
                exact_operator(packed_first, np.kron(np.eye(4), first_pair), "two first-source replicas")
                exact_operator(packed_second, np.kron(second_pair, np.eye(4)), "two second-source replicas")
                fused_packs = packing.fuse([packed_first, packed_second], ["g0_", "g1_"], "packed_phase_fusion")
                exact_operator(fused_packs, np.kron(second_pair, first_pair), "two packed components")
                exact_operator(packing.pack(first, [], "empty_phase_pack"), np.eye(16), "empty replica set")
                if first != originals[0] or second != originals[1]:
                    raise RuntimeError("phase-preserving composition mutated a source circuit")

    phase_parameter = Parameter("replica_global_phase")
    parameterized = QuantumCircuit(2, 1, global_phase=phase_parameter)
    parameterized.h(0)
    parameterized.measure(0, 0)
    packed = packing.pack(parameterized, [Replica(0, {0: 0}, 1.0), Replica(1, {0: 1}, 1.0)], "parameterized_phase_pack")
    fused = packing.fuse([packed], ["g0_"], "parameterized_phase_fusion")
    for value in (0.3, -0.41):
        local = QuantumCircuit(1, global_phase=value)
        local.h(0)
        expected = np.kron(Operator(local).data, Operator(local).data)
        exact_operator(packed.assign_parameters({phase_parameter: value}), expected, "bound packed phase")
        exact_operator(fused.assign_parameters({phase_parameter: value}), expected, "bound fused phase")


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
    for pub in pubs:
        streams = pub.manifest()["parallel_stream_count"]
        expected_streams = sum(
            len(c.entry.replicas)
            for c in pub.components
            if any(isinstance(instruction.operation, IfElseOp) for instruction in c.entry.replicas[0].data)
        )
        if streams != expected_streams:
            raise RuntimeError(f"{pub.name}: parallel_stream_count is {streams}, expected {expected_streams}")
    hybrid = next(choice for choice in dynamic_choices if choice.group.name == "hybrid_shor_mod15")
    primary = next(entry for entry in hybrid.entries if not entry.reference)
    reference = next(entry for entry in hybrid.entries if entry.reference)
    pub_of = {c.entry.name: pub.manifest() for pub in pubs for c in pub.components}
    executed: dict[str, dict[str, Any]] = {
        name: {"pub": pub_of[name]["name"]} for name in (primary.name, reference.name)
    }
    executed[primary.name].update({"calibration": "c1", "calibration_changed_during_shots": False})
    executed[reference.name].update({"calibration": "c1", "calibration_changed_during_shots": False})
    timing: dict[str, dict[str, Any]] = {
        pub_of[name]["name"]: {
            "scheduled_circuit_duration_dt": duration,
            "scheduler_residual_dt": residual,
            "timing_status": "complete",
            "parallel_stream_count": streams,
            "groups": ["folded_qpe_mod15", "hybrid_shor_mod15"],
        }
        for name, duration, residual, streams in ((primary.name, 5200, 900, 9), (reference.name, 4800, 500, 2))
    }
    schedule = packing_schedule(hybrid.entries, executed, timing)
    if (
        schedule is None
        or schedule["scope"] != "global"
        or schedule.get("residual_difference_dt") != 400
        or schedule["packed_parallel_stream_count"] != 9
        or not schedule["feed_forward"]
    ):
        raise RuntimeError(f"packing_schedule reports {schedule}")
    timing[pub_of[primary.name]["name"]]["groups"] = ["hybrid_shor_mod15"]
    if packing_schedule(hybrid.entries, executed, timing)["scope"] != "single_group":  # type: ignore[index]
        raise RuntimeError("a one-group packed PUB reports a global scope")
    executed[reference.name]["calibration"] = "c2"
    split = packing_schedule(hybrid.entries, executed, timing)
    withheld_split = str(split.get("unavailable")) if split else ""
    if split is None or "residual_difference_dt" in split or "one unchanged calibration" not in withheld_split:
        raise RuntimeError(f"packing_schedule across calibrations reports {split}")
    executed[reference.name]["calibration"] = "c1"
    timing[pub_of[reference.name]["name"]]["scheduler_residual_dt"] = None
    schedule = packing_schedule(hybrid.entries, executed, timing)
    if schedule is None or "residual_difference_dt" in schedule or "unavailable" not in schedule:
        raise RuntimeError(f"packing_schedule without reference residual reports {schedule}")
    timing[pub_of[reference.name]["name"]]["scheduler_residual_dt"] = -50
    timing[pub_of[reference.name]["name"]]["timing_status"] = "residual_below_target_bound"
    schedule = packing_schedule(hybrid.entries, executed, timing)
    withheld = str(schedule.get("unavailable")) if schedule else ""
    if schedule is None or "residual_difference_dt" in schedule or "not complete" not in withheld:
        raise RuntimeError(f"packing_schedule with an invalid residual reports {schedule}")
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
        (start, start + timedelta(seconds=1)),
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
    for pub in pubs:
        fused = round_trip[pub.name]
        specs = [
            (
                component.register_prefix,
                sorted({q for replica in component.entry.replica_qubits for q in replica}),
                component.entry.name,
            )
            for component in pub.components
        ]
        # Disjoint components take the one-pass path, and a repeated component
        # makes the qubit sets overlap, which takes extract() per component.
        for case in (specs, specs + specs[:1]):
            if packing.extract_many(fused, case) != [packing.extract(fused, *spec) for spec in case]:
                raise RuntimeError(f"{pub.name}: extract_many differs from extract")
        once = [(prefix, iter(qubits), name) for prefix, qubits, name in specs + specs[:1]]
        if packing.extract_many(fused, once) != [packing.extract(fused, *spec) for spec in specs + specs[:1]]:
            raise RuntimeError(f"{pub.name}: extract_many loses one-shot qubit iterables on the overlap path")

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


def _collect_with_zero_simulation(service: Any, run_dir: Path) -> None:
    """Collect fixture results with deterministic simulation and logical polling time."""
    original_noise_simulator = live_run_module.noise_simulator
    original_simulate_entries = live_run_module.simulate_entries
    original_wait_for_usage = live_run_module.wait_for_usage
    live_run_module.noise_simulator = lambda name, target, props, compute_policy=None: object()
    live_run_module.simulate_entries = lambda noise, entries, shots, seed: {
        entry.name: _zero_replica_distributions(entry) for entry in entries
    }
    live_run_module.wait_for_usage = partial(original_wait_for_usage, sleep=lambda seconds: None)
    try:
        collect(service, run_dir)
    finally:
        live_run_module.noise_simulator = original_noise_simulator
        live_run_module.simulate_entries = original_simulate_entries
        live_run_module.wait_for_usage = original_wait_for_usage


def _verify_worker_quota() -> None:
    """The default worker count honors the tightest CPU quota on the process's cgroup or any ancestor."""
    with tempfile.TemporaryDirectory(prefix="gororoba-cgroup-") as directory:
        root = Path(directory)
        proc = root / "proc_self_cgroup"
        v2 = root / "v2"
        leaf = v2 / "user.slice" / "session.scope"
        leaf.mkdir(parents=True)
        (v2 / "cpu.max").write_text("max 100000\n")
        (v2 / "user.slice" / "cpu.max").write_text("150000 100000\n")
        (leaf / "cpu.max").write_text("300000 100000\n")
        proc.write_text("0::/user.slice/session.scope\n")
        if parallel.cgroup_cpu_quota(proc, v2) != 1.5:
            raise RuntimeError("a tighter ancestor quota does not bind the nested cgroup")
        (v2 / "user.slice" / "cpu.max").write_text("garbage\n")
        if parallel.cgroup_cpu_quota(proc, v2) != 3.0:
            raise RuntimeError("a malformed ancestor file is not skipped")
        (leaf / "cpu.max").write_text("max 100000\n")
        if parallel.cgroup_cpu_quota(proc, v2) is not None:
            raise RuntimeError("an unlimited hierarchy reports a quota")
        v1 = root / "v1"
        cpu = v1 / "cpu,cpuacct" / "docker" / "abc"
        cpu.mkdir(parents=True)
        (cpu / "cpu.cfs_quota_us").write_text("200000\n")
        (cpu / "cpu.cfs_period_us").write_text("100000\n")
        (v1 / "cpu,cpuacct" / "cpu.cfs_quota_us").write_text("-1\n")
        (v1 / "cpu,cpuacct" / "cpu.cfs_period_us").write_text("100000\n")
        proc.write_text("12:cpu,cpuacct:/docker/abc\n3:memory:/docker/abc\n")
        if parallel.cgroup_cpu_quota(proc, v1) != 2.0:
            raise RuntimeError("the cgroup v1 cpu controller path is not resolved")
        if parallel.cgroup_cpu_quota(root / "absent", v1) is not None:
            raise RuntimeError("a missing /proc/self/cgroup reports a quota")
    original = parallel.cgroup_cpu_quota
    parallel.cgroup_cpu_quota = lambda *args: 1.5
    try:
        if parallel.available_cpus() != 2:
            raise RuntimeError(f"a 1.5-CPU quota counts {parallel.available_cpus()} CPUs")
        if os.environ.get("GOROROBA_WORKERS") is None and parallel.workers() != 2:
            raise RuntimeError(f"a 1.5-CPU quota sizes {parallel.workers()} workers")
    finally:
        parallel.cgroup_cpu_quota = original


def _verify_replay_seed_independence() -> None:
    """Replay batches under different calibrations never share a (seed, position) pair."""
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    packed = _synthetic_entry("packed", circuit, np.array([0.5, 0.5]))
    reference = _synthetic_entry("packed_isolated", circuit, np.array([0.5, 0.5]))
    first, second = datetime(2026, 10, 10, tzinfo=UTC), datetime(2026, 10, 11, tzinfo=UTC)
    calls: list[tuple[int, list[str]]] = []
    original = live_run_module.simulate_entries

    def recording(noise: Any, entries: list[Entry], shots: int, seed: int) -> dict[str, list[np.ndarray]]:
        del noise, shots
        calls.append((seed, [entry.name for entry in entries]))
        return {entry.name: _zero_replica_distributions(entry) for entry in entries}

    live_run_module.simulate_entries = recording
    try:
        replayed = live_run_module.replay_entries(
            {first: object(), second: object()}, {second: [reference], first: [packed]}, 64, 7
        )
    finally:
        live_run_module.simulate_entries = original
    if set(replayed) != {"packed", "packed_isolated"}:
        raise RuntimeError(f"replay loses entries: {sorted(replayed)}")
    if calls != [(7, ["packed"]), (8, ["packed_isolated"])]:
        raise RuntimeError(f"replay batches share seeds or run out of calibration order: {calls}")


def _verify_raw_scrubbing() -> None:
    """Raw files carry instances only as 12-hex CRN hashes, and metadata serializes losslessly enough to re-read."""
    scrubbed = live_run_module._scrub_instances(
        {"caller": "x", "instance": "crn:v1:bluemix:public:quantum-computing:us-east:a/abc:def::", "n": [1, "crn:z"]}
    )
    expected = (
        "crn-sha256-12:"
        + hashlib.sha256(b"crn:v1:bluemix:public:quantum-computing:us-east:a/abc:def::").hexdigest()[:12]
    )
    if scrubbed["instance"] != expected or scrubbed["n"][1][:14] != "crn-sha256-12:" or scrubbed["caller"] != "x":
        raise RuntimeError(f"CRN scrubbing reads {scrubbed}")
    moment = datetime(2026, 10, 11, 15, 31, 50, 399650, tzinfo=UTC)

    @dataclass
    class Span:
        start: datetime
        parts: list[int]

    serialized = live_run_module._jsonable({"chunk_timing": [Span(moment, [0, 1])], "other": object()})
    if serialized["chunk_timing"][0]["start"] != moment.isoformat() or serialized["chunk_timing"][0]["parts"] != [0, 1]:
        raise RuntimeError(f"metadata serialization reads {serialized}")
    if not isinstance(serialized["other"], str):
        raise RuntimeError("an unknown object does not serialize to text")


def _verify_fused_collection() -> None:
    """Collect one complete mocked job through fused result decoding and execution-window fan-out."""
    backend = _ProbeBackend("viable", FakeFez())
    planning_service = _ProbeService([backend])
    args = _fixture_args(groups=["design_a", "zero_divisor_fringe"], shots=64)
    choices, record = live_run_module.plan(planning_service, args)
    # Replicas of different groups on one backend share no CZ edge: the
    # cross-group buffer keeps them one hop apart.
    edges = {tuple(sorted(edge)) for edge in backend.coupling_map.get_edges()}
    by_group = {choice.group.name: {q for replica in choice.replicas for q in replica.qubits} for choice in choices}
    names = list(by_group)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            qa, qb = by_group[names[a]], by_group[names[b]]
            crossing = [e for e in edges if (e[0] in qa and e[1] in qb) or (e[0] in qb and e[1] in qa)]
            if crossing:
                raise RuntimeError(f"{names[a]} and {names[b]} share CZ edges {crossing}")
    if record["policy"].get("cross_group_buffer") is not True:
        raise RuntimeError("the plan's policy does not record the cross-group buffer")
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
            max_execution_seconds: int | None = None,
            *,
            rep_delay: float | None = None,
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
        circuits = [archived[pub_manifest["name"]] for pub_manifest in planned_job["pubs"]]

        base_time = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)
        fused_index = next(
            index for index, pub_manifest in enumerate(planned_job["pubs"]) if pub_manifest["name"] == fused_pub.name
        )
        chunks: list[ChunkSpan] = []
        expected_fused_window = (
            base_time + timedelta(seconds=10 * fused_index),
            base_time + timedelta(seconds=10 * fused_index + 5),
        )
        for index in range(len(circuits)):
            start = base_time + timedelta(seconds=10 * index)
            if index == fused_index:
                chunks.extend(
                    [
                        ChunkSpan(start + timedelta(seconds=2), start + timedelta(seconds=3), [ChunkPart(index, 1)]),
                        ChunkSpan(start, start + timedelta(seconds=5), [ChunkPart(index, 1)]),
                    ]
                )
            else:
                chunks.append(ChunkSpan(start, start + timedelta(seconds=1), [ChunkPart(index, 1)]))
        # Each fixture schedule exceeds its PUB's Target lower bound by 10 dt
        # times the index, so every residual is nonnegative and distinct.
        durations = [
            pub_manifest["target_gate_lower_bound_dt"] + 10 * index
            for index, pub_manifest in enumerate(planned_job["pubs"])
        ]
        result = _executor_result(FakeFez(), circuits, args.shots, chunks, durations)
        if sorted(result.metadata) != ["executor", "options", "shots"]:
            raise RuntimeError(f"executor Sampler result metadata keys are {sorted(result.metadata)}")
        spans = pub_windows(result, len(circuits))
        if (
            spans.source != "executor_chunk_timing"
            or len(spans.windows) != len(planned_job["pubs"])
            or spans.windows[fused_index] != expected_fused_window
        ):
            raise RuntimeError(f"fused PUB execution windows are {spans}")
        if [scheduled_duration(pub_result) for pub_result in result] != [(d, None) for d in durations]:
            raise RuntimeError("scheduler timing does not reach each PUB result")

        incomplete = _executor_result(
            FakeFez(),
            circuits,
            args.shots,
            [chunk for chunk in chunks if all(part.idx_item != fused_index for part in chunk.parts)],
            durations,
        )
        partial = pub_windows(incomplete, len(circuits))
        if partial.windows[fused_index] is not None or partial.reason is not None:
            raise RuntimeError(f"a PUB without a chunk reports {partial}")
        if any(window is None for index, window in enumerate(partial.windows) if index != fused_index):
            raise RuntimeError("a missing chunk for one PUB removes another PUB's window")

        usage = {"status": "completed", "qpu_charge_time_seconds": 12.5}
        probe_job = _ProbeResultJob(result, usage=usage, charge=12.5)
        collection_service = _CollectionProbeService(backend, {job_id: probe_job})
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)

        collected = json.loads((run_dir / "collect.json").read_text())
        executed = {
            name: evidence
            for group_record in collected[1:]
            for name, evidence in group_record.get("executed", {}).items()
        }
        fused_members = [component.entry.name for component in fused_pub.components]
        fused_evidence = [executed[name] for name in fused_members]
        # Each member's placed calibration is the PUB's restricted to its own qubits
        # (pub_calibration.split_pub_calibration); every other field is the PUB's and shared.
        per_member = ("placed_qubit_calibration", "placed_gate_calibration")
        shared = [
            {key: value for key, value in evidence.items() if key not in per_member} for evidence in fused_evidence
        ]
        if len({json.dumps(evidence, sort_keys=True) for evidence in shared}) != 1:
            raise RuntimeError("mocked collection gives fused components different execution evidence")
        for name, evidence, part in zip(
            fused_members, fused_evidence, planned_job["pubs"][fused_index]["components"], strict=True
        ):
            if set(evidence["placed_qubit_calibration"]) != {str(qubit) for qubit in part["physical_qubits"]}:
                raise RuntimeError(f"{name}'s placed calibration covers qubits other than its own")
        expected_start, expected_stop = expected_fused_window
        if (
            fused_evidence[0]["pub"] != fused_pub.name
            or fused_evidence[0]["start"] != expected_start.isoformat()
            or fused_evidence[0]["stop"] != expected_stop.isoformat()
            or fused_evidence[0]["calibration_changed_during_shots"]
            or "scheduled_circuit_duration_dt" in fused_evidence[0]
        ):
            raise RuntimeError(f"mocked fused execution evidence is {fused_evidence[0]}")
        job_out = collected[0]["jobs"][job_id]
        job_identity = job_out["backend_identity"]
        if (
            live_run_module.backend_identity_violations(job_identity)
            or job_identity["processor_type"] is None
            or job_identity["backend_version_at_execution"].get(expected_start.isoformat())
            != backend.properties().backend_version
        ):
            raise RuntimeError(f"collected job identity is {job_identity}")
        fused_timing = job_out["pub_timing"][fused_pub.name]
        lower = planned_job["pubs"][fused_index]["target_gate_lower_bound_dt"]
        if (
            fused_timing["timing_status"] != "complete"
            or fused_timing["timing_source"] != "executor_chunk_timing"
            or fused_timing["execution_window_start"] != expected_start.isoformat()
            or fused_timing["scheduled_circuit_duration_dt"] != durations[fused_index]
            or fused_timing["scheduler_residual_dt"] != durations[fused_index] - lower
            or fused_timing["planned_target_gate_lower_bound_dt"] != lower
            or fused_timing["parallel_stream_count"] != 0
            or fused_timing["timing_unavailable_reason"] is not None
        ):
            raise RuntimeError(f"fused PUB timing record is {fused_timing}")
        if any(group_record["job_id"] != job_id for group_record in collected[1:]):
            raise RuntimeError("group records do not reference their owning job")
        job_usage = job_out["usage"]
        expected_shots = len(planned_job["pubs"]) * args.shots
        if (
            job_usage["usage_status"] != "final"
            or job_usage["submitted_pub_shots"] != expected_shots
            or job_usage["qpu_charge_time_seconds"] != "12.5"
            or job_usage["pub_shots_per_qpu_second"]
            != str((Decimal(expected_shots) / Decimal("12.5")).quantize(Decimal("0.001")))
        ):
            raise RuntimeError(f"job usage record is {job_usage}")
        first = (run_dir / "collect.json").read_bytes()
        # The lossless result is on disk under raw/<job_id>/ with an index of
        # sha256s, every register as shot-ordered bit strings, and no CRN.
        raw_dir = run_dir / live_run_module.RAW_DIRECTORY / job_id
        raw_index = json.loads((raw_dir / "index.json").read_text())
        if job_out["raw"] != {"directory": f"{live_run_module.RAW_DIRECTORY}/{job_id}", "files": raw_index["files"]}:
            raise RuntimeError(f"collect.json raw index differs from raw/index.json: {job_out['raw']}")
        for name, digest in raw_index["files"].items():
            if hashlib.sha256((raw_dir / name).read_bytes()).hexdigest() != digest:
                raise RuntimeError(f"raw file {name} differs from its indexed sha256")
        raw_pubs = sorted(name for name in raw_index["files"] if name.startswith("pub_"))
        if len(raw_pubs) != len(planned_job["pubs"]):
            raise RuntimeError(f"raw preserved {len(raw_pubs)} PUBs for {len(planned_job['pubs'])} planned")
        first_pub = json.loads((raw_dir / raw_pubs[0]).read_text())
        if first_pub["pub_name"] != planned_job["pubs"][0]["name"]:
            raise RuntimeError("raw PUB 0 is not named after the planned PUB")
        for register in first_pub["registers"].values():
            if len(register["bitstrings"]) != args.shots or any(
                len(b) != register["num_bits"] for b in register["bitstrings"]
            ):
                raise RuntimeError("raw register bit strings are not one per shot at the register width")
        if "crn:" in (raw_dir / "job_metrics.json").read_text() + (raw_dir / "result_metadata.json").read_text():
            raise RuntimeError("a CRN reached the raw files")
        if "job_metrics.json" in raw_index["files"] or raw_index["metrics"] != ["job_metrics.json"]:
            raise RuntimeError(f"job metrics are not a single indexed snapshot: {raw_index}")
        first_metrics = (raw_dir / "job_metrics.json").read_bytes()
        raw_bytes = {name: (raw_dir / name).read_bytes() for name in raw_index["files"]}

        # Recollection after usage finalizes changes job and invocation usage.
        probe_job._usage = {"status": "pending"}
        probe_job._charge = None
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)
        pending = json.loads((run_dir / "collect.json").read_text())
        if pending[0]["jobs"][job_id]["usage"]["usage_status"] != "pending":
            raise RuntimeError("pending usage does not read pending")
        if (
            pending[0]["invocation_usage"]["total_charge_seconds"] is not None
            or pending[0]["invocation_usage"]["charge_complete"]
            or pending[0]["invocation_usage"]["workload_complete"]
        ):
            raise RuntimeError("pending job usage appears as complete invocation billing")
        probe_job._usage = usage
        probe_job._charge = 12.5
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)
        if (run_dir / "collect.json").read_bytes() != first:
            raise RuntimeError("recollection after usage finalizes changes bytes outside the usage block")
        if any((raw_dir / name).read_bytes() != content for name, content in raw_bytes.items()):
            raise RuntimeError("recollection rewrites the raw result files")
        # The pending-usage collection added a second metrics snapshot; the
        # final one matched the first and added none; the first is unchanged.
        snapshots = json.loads((raw_dir / "index.json").read_text())["metrics"]
        if (
            snapshots != ["job_metrics.json", "job_metrics.1.json"]
            or (raw_dir / "job_metrics.json").read_bytes() != first_metrics
        ):
            raise RuntimeError(f"metrics snapshots read {snapshots}")
        # Raw evidence is write-once: a file whose bytes differ from the
        # result the service returns stops the collection.
        tampered = raw_dir / raw_pubs[0]
        original_pub = tampered.read_bytes()
        tampered.write_bytes(original_pub.replace(b'"pub_index": 0', b'"pub_index": 9'))
        try:
            with redirect_stdout(io.StringIO()):
                _collect_with_zero_simulation(collection_service, run_dir)
        except LiveRunError as error:
            # The atomic publisher refuses differing bytes before the indexed sha256 check does.
            if "write-once" not in str(error) and "immutable acquisition snapshot" not in str(error):
                raise RuntimeError(f"tampered raw evidence reports {error}") from error
        else:
            raise RuntimeError("a collection over tampered raw evidence proceeds")
        finally:
            tampered.write_bytes(original_pub)
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)
        if (run_dir / "collect.json").read_bytes() != first:
            raise RuntimeError("recollection after restoring the raw evidence differs")
        pending[0]["jobs"][job_id]["usage"] = json.loads(first)[0]["jobs"][job_id]["usage"]
        final_invocation_usage = json.loads(first)[0]["invocation_usage"]
        if final_invocation_usage["total_charge_seconds"] != "12.5" or not final_invocation_usage["workload_complete"]:
            raise RuntimeError(f"final invocation usage reads {final_invocation_usage}")
        pending[0]["invocation_usage"] = final_invocation_usage
        if pending != json.loads(first):
            raise RuntimeError("pending and final collections differ outside job and invocation usage")

        # A job that ended in ERROR or CANCELLED keeps its usage, its reason
        # and its backend's configuration identity, with no execution start;
        # collection continues without its results.
        configured_identity = live_run_module.backend_identity(backend)
        for terminal in ("ERROR", "CANCELLED"):
            failed = _ProbeResultJob(result, status=terminal, usage=usage, charge=0.25)
            failed.result = lambda: (_ for _ in ()).throw(RuntimeError("job failed on the service"))  # type: ignore[method-assign]
            with redirect_stdout(io.StringIO()):
                _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: failed}), run_dir)
            errored = json.loads((run_dir / "collect.json").read_text())
            job_record = errored[0]["jobs"][job_id]
            if (
                job_record["usage"]["usage_status"] != "final"
                or job_record["usage"]["qpu_charge_time_seconds"] != "0.25"
                or job_record["usage"]["pub_shots_per_qpu_second"] is not None
                or "job failed on the service" not in job_record["result_unavailable"]
                or len(errored) != 1
                or (run_dir / "collect.partial.json").exists()
            ):
                raise RuntimeError(f"a job that ended in {terminal} collects as {job_record}")
            if job_record.get("backend_identity") != configured_identity | {"backend_version_at_execution": {}} or (
                configured_identity["processor_type"] is None
            ):
                raise RuntimeError(
                    f"a job that ended in {terminal} collects identity {job_record.get('backend_identity')}"
                )

        # A failed job on a backend the account no longer serves still
        # collects its usage, with an unread identity.
        class _RetiredBackendService(_CollectionProbeService):
            def backend(self, name: str) -> _ProbeBackend:
                raise RuntimeError(f"fixture backend {name} is not served")

        retired = _ProbeResultJob(result, status="CANCELLED", usage=usage, charge=0.25)
        retired.result = lambda: (_ for _ in ()).throw(RuntimeError("job failed on the service"))  # type: ignore[method-assign]
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_RetiredBackendService(backend, {job_id: retired}), run_dir)
        retired_record = json.loads((run_dir / "collect.json").read_text())[0]["jobs"][job_id]
        if retired_record["usage"]["qpu_charge_time_seconds"] != "0.25" or retired_record.get("backend_identity") != {
            "backend_version": None,
            "processor_type": None,
            "backend_version_at_execution": {},
        }:
            raise RuntimeError(f"a failed job on an unserved backend collects as {retired_record}")

        # A job still running at collection start that then fails keeps the
        # charge read after the failure.
        class _FailingRunningJob(_ProbeResultJob):
            def result(self) -> PrimitiveResult[SamplerPubResult]:
                self._status, self._usage, self._charge = "ERROR", usage, 0.75
                raise RuntimeError("job failed while collection waited")

        late = _FailingRunningJob(result, status="RUNNING", usage={"status": "pending"}, charge=None)
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: late}), run_dir)
        late_usage = json.loads((run_dir / "collect.json").read_text())[0]["jobs"][job_id]["usage"]
        if late_usage["usage_status"] != "final" or late_usage["qpu_charge_time_seconds"] != "0.75":
            raise RuntimeError(f"a job that failed while collection waited keeps {late_usage}")
        # A DONE job whose result retrieval raises propagates the failure and
        # leaves the complete earlier collect.json in place.
        flaky = _ProbeResultJob(result, status="DONE", usage=usage, charge=12.5)
        flaky.result = lambda: (_ for _ in ()).throw(RuntimeError("decoder failure"))  # type: ignore[method-assign]
        before = (run_dir / "collect.json").read_bytes()
        try:
            with redirect_stdout(io.StringIO()):
                _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: flaky}), run_dir)
        except RuntimeError as error:
            if "decoder failure" not in str(error):
                raise
        else:
            raise RuntimeError("a DONE job's retrieval failure passes for a failed job")
        if (run_dir / "collect.json").read_bytes() != before or not (run_dir / "collect.partial.json").exists():
            raise RuntimeError("a retrieval failure replaced the complete collection or left no partial checkpoint")
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)

        # A job still running at collection start reports pending usage
        # before result() and final usage after it.
        class _RunningJob(_ProbeResultJob):
            def result(self) -> PrimitiveResult[SamplerPubResult]:
                self._status, self._usage, self._charge = "DONE", usage, 12.5
                return self._result

        running = _RunningJob(result, status="RUNNING", usage={"status": "pending"}, charge=None)
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: running}), run_dir)
        if (run_dir / "collect.json").read_bytes() != first:
            raise RuntimeError("usage read before a running job's result is not refreshed after it")

        # Metrics still pending after result() finalize during the usage
        # wait; the raw index then points at the finalized snapshot.
        class _LateUsageJob(_ProbeResultJob):
            calls = 0

            def metrics(self) -> dict[str, Any]:
                self.calls += 1
                if self.calls >= 3:
                    self._usage, self._charge = usage, 12.5
                return super().metrics()

        late_job = _LateUsageJob(result, status="DONE", usage={"status": "pending"}, charge=None)
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: late_job}), run_dir)
        late_index = json.loads((raw_dir / "index.json").read_text())
        latest_metrics = json.loads((raw_dir / late_index["metrics_latest"]).read_text())
        if latest_metrics.get("usage") != usage:
            raise RuntimeError(f"raw metrics after the usage wait read {latest_metrics}")

        # A failure after the usage read leaves the usage checkpointed in
        # collect.json: a result with the wrong PUB count stops collection.
        # The fixture returns a different result for the same job id, which
        # the write-once raw evidence would refuse first, so the job's raw
        # directory is cleared around it.
        broken = _ProbeResultJob(PrimitiveResult([], metadata={}), usage=usage, charge=1.0)
        shutil.rmtree(raw_dir)
        try:
            with redirect_stdout(io.StringIO()):
                _collect_with_zero_simulation(_CollectionProbeService(backend, {job_id: broken}), run_dir)
        except LiveRunError as error:
            if "returned 0 PUB results" not in str(error):
                raise RuntimeError(f"a job with the wrong PUB count reports {error}") from error
        else:
            raise RuntimeError("a job with the wrong PUB count collects")
        finally:
            shutil.rmtree(raw_dir, ignore_errors=True)
        partial = json.loads((run_dir / "collect.partial.json").read_text())
        if partial[0]["jobs"][job_id]["usage"]["qpu_charge_time_seconds"] != "1.0" or len(partial) != 1:
            raise RuntimeError(f"the checkpoint after a failed collection lacks the usage: {partial[0]['jobs']}")
        with redirect_stdout(io.StringIO()):
            _collect_with_zero_simulation(collection_service, run_dir)
        if (run_dir / "collect.partial.json").exists() or (run_dir / "collect.json").read_bytes() != first:
            raise RuntimeError("a complete collection leaves the partial checkpoint or differs from the first")


def _verify_scheduler_timing_cases() -> None:
    """Window sources, scheduler durations, and residual classification over every documented shape."""
    backend = FakeFez()
    circuit = QuantumCircuit(1, 1)
    circuit.measure(0, 0)
    circuits = [transpile(circuit, backend, optimization_level=0, initial_layout=[k]) for k in range(3)]
    base = datetime(2026, 10, 10, 12, 0)  # naive: normalized to UTC
    for kind in ("static", "dynamic"):
        if configure_sampler(backend, kind, False, None, [], 4096).options.execution.scheduler_timing is not True:
            raise RuntimeError(f"{kind} job does not request scheduler timing")

    # One PUB in one chunk, one PUB across two chunks, two PUBs sharing one
    # chunk, and a duplicate part for one PUB in one chunk.
    chunks = [
        ChunkSpan(base, base + timedelta(seconds=1), [ChunkPart(0, 1), ChunkPart(0, 1)]),
        ChunkSpan(base + timedelta(seconds=2), base + timedelta(seconds=3), [ChunkPart(1, 1), ChunkPart(2, 1)]),
        ChunkSpan(base + timedelta(seconds=5), base + timedelta(seconds=6), [ChunkPart(1, 1)]),
    ]
    spans = pub_windows(_executor_result(backend, circuits, 8, chunks, [100, 100, 100]), 3)
    expected = [
        (base.replace(tzinfo=UTC), (base + timedelta(seconds=1)).replace(tzinfo=UTC)),
        ((base + timedelta(seconds=2)).replace(tzinfo=UTC), (base + timedelta(seconds=6)).replace(tzinfo=UTC)),
        ((base + timedelta(seconds=2)).replace(tzinfo=UTC), (base + timedelta(seconds=3)).replace(tzinfo=UTC)),
    ]
    if spans.source != "executor_chunk_timing" or spans.windows != expected or spans.reason is not None:
        raise RuntimeError(f"chunk windows are {spans}")

    legacy_spans = [
        _ProbeExecutionSpan(base, base + timedelta(seconds=1), [0, 1]),
        _ProbeExecutionSpan(base, base, [2]),
    ]
    legacy = PrimitiveResult([], metadata={"execution": {"execution_spans": legacy_spans}})
    spans = pub_windows(legacy, 3)
    if spans.source != "execution_spans" or spans.windows[0] != expected[0] or spans.windows[0] != spans.windows[1]:
        raise RuntimeError(f"legacy execution spans read {spans}")

    missing = pub_windows(_executor_result(backend, circuits, 8, chunks[:1], [100, 100, 100]), 3)
    if missing.windows[0] is None or missing.windows[1:] != [None, None] or missing.reason is not None:
        raise RuntimeError(f"PUBs without chunks read {missing}")
    beyond = [ChunkSpan(base, base, [ChunkPart(3, 1)])]
    outside = pub_windows(_executor_result(backend, circuits, 8, beyond, [1] * 3), 3)
    if outside.windows != [None] * 3 or "outside 0..2" not in str(outside.reason):
        raise RuntimeError(f"out-of-range chunk index reads {outside}")
    empty = pub_windows(PrimitiveResult([], metadata={"options": {}}), 2)
    if empty.windows != [None, None] or empty.source is not None or "no executor chunk timing" not in str(empty.reason):
        raise RuntimeError(f"result without timing reads {empty}")

    def pub_with(compilation: Any) -> SamplerPubResult:
        metadata = {"compilation": compilation} if compilation is not None else {}
        return SamplerPubResult(DataBin(), metadata=metadata)

    cases: list[tuple[Any, int | None, str | None]] = [
        ({"scheduler_timing": {"timing": "", "circuit_duration": 1200}}, 1200, None),
        (None, None, "no scheduler timing"),
        ({"stretch_values": []}, None, "no scheduler timing"),
        ({"scheduler_timing": {"circuit_duration": "1200"}}, None, "malformed"),
        ({"scheduler_timing": {"circuit_duration": 10.5}}, None, "malformed"),
        ({"scheduler_timing": {"circuit_duration": -1}}, None, "malformed"),
        ({"scheduler_timing": {"circuit_duration": True}}, None, "malformed"),
        ({"scheduler_timing": {"circuit_duration": float("nan")}}, None, "malformed"),
    ]
    for compilation, duration, fragment in cases:
        value, reason = scheduled_duration(pub_with(compilation))
        if value != duration or (fragment is None) != (reason is None) or (fragment and fragment not in str(reason)):
            raise RuntimeError(f"scheduler duration {compilation} reads {(value, reason)}")

    manifest = {"target_gate_lower_bound_dt": 1000, "parallel_stream_count": 2}
    window = expected[0]
    chunk = "executor_chunk_timing"
    statuses = [
        (pub_timing(manifest, window, None, 1200, None, chunk, 1000), "complete", 200),
        (pub_timing(manifest, window, None, 1200, None, chunk, 1100), "complete", 100),
        (pub_timing(manifest, None, "no chunk", 1200, None, chunk), "schedule_only", None),
        (pub_timing(manifest, window, None, None, "no timing", chunk, 1000), "windows_only", None),
        (pub_timing(manifest, None, "no chunk", None, "no scheduler timing", None), "unavailable", None),
        (pub_timing(manifest, window, None, 900, None, chunk, 1000), "residual_below_target_bound", -100),
    ]
    for record, status, residual in statuses:
        if record["timing_status"] != status or record["scheduler_residual_dt"] != residual:
            raise RuntimeError(f"timing record {record} is not {status}/{residual}")
        if status != "complete" and not record["timing_unavailable_reason"]:
            raise RuntimeError(f"{status} timing record carries no reason")
    if statuses[0][0]["timing_unavailable_reason"] is not None or statuses[2][0]["timing_source"] is not None:
        raise RuntimeError("complete timing carries a reason, or a windowless record names a source")
    if (
        statuses[1][0]["target_gate_lower_bound_dt"] != 1100
        or statuses[1][0]["planned_target_gate_lower_bound_dt"] != 1000
        or "residual withheld" not in str(statuses[2][0]["timing_unavailable_reason"])
    ):
        raise RuntimeError("the residual does not follow the execution-time Target bound")


def _verify_packing_equivalence() -> None:
    """The global packing comparison carries z, the difference interval, and the equivalence verdict."""
    group = Group(
        "probe", (), lambda distributions: {"p1": float(distributions["primary"][1])}, rate_keys=frozenset({"p1"})
    )
    ideal = np.array([0.0, 1.0])
    primary = _synthetic_entry("primary", QuantumCircuit(1, 1), ideal)
    reference = copy.copy(primary)
    reference.name = "primary_isolated"
    reference.reference = True
    entries = [primary, reference]
    cases: list[tuple[float, float, int, str, str]] = [
        (0.500, 0.495, 4096, "equivalent_within_0.03", "the run detected no difference"),
        (0.400, 0.500, 4096, "packed_degradation_detected", "more than three sigma below"),
        (0.480, 0.500, 1024, "difference_not_resolved", "the run detected no difference"),
        (0.000, 1.000, 8, "insufficient_shots", "unavailable"),
        (0.480, 0.500, 63, "insufficient_shots", "the run detected no difference"),
    ]
    for packed, alone, shots, verdict, resolution in cases:
        dists = {"primary": [np.array([1 - packed, packed])], "primary_isolated": [np.array([1 - alone, alone])]}
        scope = {"scope": "global", "groups": ["folded_qpe_mod15", "hybrid_shor_mod15"]}
        crosstalk = replica_statistics(group, entries, dists, shots, scope)["global_packing_crosstalk"]
        if (
            crosstalk["scope"] != "global"
            or crosstalk["method"] != "newcombe_wilson"
            or crosstalk["verdict"] != verdict
            or resolution not in crosstalk["resolution"]
            or abs(crosstalk["difference"] - (packed - alone)) > 1e-12
        ):
            raise RuntimeError(f"packing comparison at {packed} vs {alone} over {shots} shots reads {crosstalk}")
    weighted = _synthetic_entry("weighted", QuantumCircuit(1, 1), np.array([0.25, 0.75]))
    if live_run_module._bernoulli_score(weighted) or not live_run_module._bernoulli_score(primary):
        raise RuntimeError("Bernoulli score classification follows the per-shot weights")
    weighted_view = variance.equivalence(0.5, 0.25, 0.5, 0.25, 4096, live_run_module._bernoulli_score(weighted))
    bernoulli_view = variance.equivalence(0.5, 0.25, 0.5, 0.25, 4096, live_run_module._bernoulli_score(primary))
    if weighted_view["method"] != "hoeffding" or bernoulli_view["method"] != "newcombe_wilson":
        raise RuntimeError(f"score classification does not select the interval: {weighted_view} {bernoulli_view}")
    if "hoeffding_interval_90" not in crosstalk:
        raise RuntimeError("the packing comparison omits the Hoeffding view")
    degenerate = {"primary": [np.array([1.0, 0.0])], "primary_isolated": [np.array([0.0, 1.0])]}
    extreme = replica_statistics(group, entries, degenerate, 1024)["global_packing_crosstalk"]
    if extreme["z"] is not None or "unavailable" not in extreme["resolution"] or not extreme["below_zero_95"]:
        raise RuntimeError(f"zero-variance arms read {extreme}")
    if extreme["scope"] != "unknown":
        raise RuntimeError("a comparison without a PUB scope claims one")
    scoped = replica_statistics(group, entries, degenerate, 1024, {"scope": "single_group", "groups": ["probe"]})
    if scoped["global_packing_crosstalk"]["scope"] != "single_group":
        raise RuntimeError("a single-group PUB scope is not propagated")
    loss = {"below_zero_95": True, "above_zero_95": False, "within_margin": False}
    small_loss = {"below_zero_95": True, "above_zero_95": False, "within_margin": True}
    same = {"below_zero_95": False, "above_zero_95": False, "within_margin": True}
    open_question = {"below_zero_95": False, "above_zero_95": False, "within_margin": False}
    gain = {"below_zero_95": False, "above_zero_95": True, "within_margin": False}
    few = {"verdict": "insufficient_shots", "below_zero_95": False, "above_zero_95": False, "within_margin": False}
    readings: list[tuple[dict[str, Any], dict[str, Any], str]] = [
        ({"residual_difference_dt": 0, "feed_forward": True}, few, "below the equivalence floor"),
        (
            {"residual_difference_dt": 400, "feed_forward": True, "groups": ["hybrid_shor_mod15"]},
            loss,
            "within hybrid_shor_mod15 alone",
        ),
        ({"residual_difference_dt": 400, "feed_forward": True}, loss, "unattributed global packing scheduling cost"),
        ({"residual_difference_dt": 400, "feed_forward": False}, loss, "excludes feed-forward"),
        ({"residual_difference_dt": 0, "feed_forward": True}, loss, "readout crosstalk"),
        ({"residual_difference_dt": 0, "feed_forward": True}, small_loss, "loss inside the equivalence margin"),
        ({"residual_difference_dt": 0, "feed_forward": True}, same, "no packing cost"),
        ({"residual_difference_dt": 0, "feed_forward": True}, gain, "yield gain"),
        ({"residual_difference_dt": 0, "feed_forward": True}, open_question, "unresolved"),
        ({"unavailable": "x"}, open_question, "stands alone"),
    ]
    for schedule, crosstalk_view, fragment in readings:
        text = live_run_module.packing_interpretation(schedule, crosstalk_view)
        if text is None or fragment not in text:
            raise RuntimeError(f"packing interpretation of {schedule}, {crosstalk_view} reads {text}")
    if live_run_module.packing_interpretation(None, {"verdict": "x"}) is not None:
        raise RuntimeError("an absent schedule produces an interpretation")


def _verify_feed_forward_structure() -> None:
    """Operation count, stage depth, and feed-forward presence over static, reset, single, and nested shapes."""
    static = QuantumCircuit(1, 1)
    static.h(0)
    static.measure(0, 0)
    reset_only = QuantumCircuit(1, 1)
    reset_only.reset(0)
    reset_only.measure(0, 0)
    single = QuantumCircuit(1, 2)
    single.measure(0, 0)
    with single.if_test((single.clbits[0], 1)):
        single.x(0)
    single.measure(0, 1)
    nested = QuantumCircuit(1, 3)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.x(0)
        nested.measure(0, 1)
        with nested.if_test((nested.clbits[1], 1)):
            nested.x(0)
    nested.measure(0, 2)
    with nested.if_test((nested.clbits[2], 1)):
        nested.x(0)
    expected = {"static": (0, 0, False), "reset_only": (0, 0, False), "single": (1, 1, True), "nested": (3, 3, True)}
    for label, circuit in (("static", static), ("reset_only", reset_only), ("single", single), ("nested", nested)):
        observed = (_control_flow_count(circuit), _feed_forward_stages(circuit), _has_feed_forward(circuit))
        if observed != expected[label]:
            raise RuntimeError(f"{label} feed-forward structure reads {observed}, expected {expected[label]}")


def _verify_usage_wait() -> None:
    """Collection polls a finished job's usage until the service's calculation completes, within a bound."""
    result = PrimitiveResult([], metadata={})
    final = {"status": "completed", "qpu_charge_time_seconds": 3}

    class _LateUsageJob(_ProbeResultJob):
        def __init__(self, flips_after: int):
            super().__init__(result, status="DONE", usage={"status": "pending"}, charge=None)
            self.reads = 0
            self.flips_after = flips_after

        def metrics(self) -> dict[str, Any]:
            self.reads += 1
            if self.reads > self.flips_after:
                self._usage, self._charge = final, 3
            return super().metrics()

    naps: list[float] = []
    record = live_run_module.wait_for_usage(_LateUsageJob(2), 6, 4096, 120.0, 5.0, naps.append)
    if record["usage_status"] != "final" or record["pub_shots_per_qpu_second"] != "8192.000" or naps != [5.0, 5.0]:
        raise RuntimeError(f"usage that completes after two polls reads {record} with naps {naps}")
    naps.clear()
    stuck = live_run_module.wait_for_usage(_LateUsageJob(10**6), 6, 4096, 20.0, 5.0, naps.append)
    if (
        stuck["usage_status"] != "pending"
        or "still pending 20 s" not in str(stuck["throughput_unavailable_reason"])
        or len(naps) != 4
    ):
        raise RuntimeError(f"usage that stays pending reads {stuck} after {len(naps)} polls")
    running = live_run_module.wait_for_usage(
        _ProbeResultJob(result, status="RUNNING", usage={"status": "pending"}), 6, 4096, 20.0, 5.0, naps.append
    )
    if running["usage_status"] != "pending" or len(naps) != 4:
        raise RuntimeError("a job that has not ended is polled for usage")


def _verify_job_usage_cases() -> None:
    """Throughput derives only from a final job with final usage, over submitted PUB shots."""
    result = PrimitiveResult([], metadata={})
    final = {"status": "completed", "qpu_charge_time_seconds": 10}
    cases: list[tuple[_ProbeResultJob, str, str | None, str | None]] = [
        (_ProbeResultJob(result, status="RUNNING", usage=final, charge=10), "pending", None, "not final"),
        (_ProbeResultJob(result, status="DONE"), "missing", None, "no usage"),
        (_ProbeResultJob(result, status="DONE", usage={"status": "pending"}, charge=None), "pending", None, "pending"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=None), "missing", None, "no qpu_charge"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=0), "final", None, "zero QPU charge"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=10), "final", "2457.600", None),
        (_ProbeResultJob(result, status="ERROR", usage=final, charge=0.5), "final", None, "did not complete"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge="abc"), "malformed", None, "not a finite"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=float("inf")), "malformed", None, "not a finite"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=-1), "malformed", None, "not a finite"),
        (_ProbeResultJob(result, status="DONE", usage=final, charge=True), "malformed", None, "not a finite"),
    ]
    for job, status, rate, fragment in cases:
        record = job_usage_record(job, 6, 4096)
        if record["submitted_pub_shots"] != 24576:
            raise RuntimeError(f"six PUBs at 4096 shots submit {record['submitted_pub_shots']} PUB shots")
        if record["usage_status"] != status or record["pub_shots_per_qpu_second"] != rate:
            raise RuntimeError(f"usage case {job.status()}/{job.metrics()}/{job._charge!r} reads {record}")
        if (fragment is None) != (record["throughput_unavailable_reason"] is None) or (
            fragment and fragment not in record["throughput_unavailable_reason"]
        ):
            raise RuntimeError(f"usage case reason is {record['throughput_unavailable_reason']!r}")
    exact = job_usage_record(_ProbeResultJob(result, status="DONE", usage=final, charge=0.1), 6, 4096)
    if exact["qpu_charge_time_seconds"] != "0.1" or exact["pub_shots_per_qpu_second"] != "245760.000":
        raise RuntimeError(f"decimal charge text is {exact}")


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

    def forced_joint_placement(
        choices: list[Choice], policy: ReplicaPolicy, cache: dict[tuple[int, float], Any] | None = None
    ) -> dict[str, Any]:
        del policy, cache
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

    # A calibration that rejects every combination stops the search at the
    # attempt bound instead of walking the whole frontier.
    wide_sets = [
        [candidate("design_a", 100 + k, 0.99 - 0.001 * k) for k in range(20)],
        [candidate("design_c_8_1_4", 200 + k, 0.98 - 0.001 * k) for k in range(20)],
    ]
    rejections = 0

    def reject_everything(
        choices: list[Choice], policy: ReplicaPolicy, cache: dict[tuple[int, float], Any] | None = None
    ) -> dict[str, Any]:
        nonlocal rejections
        del choices, policy, cache
        rejections += 1
        raise LiveRunError("fixture rejects every combination")

    original_bound = live_run_module.FUSION_MAX_ATTEMPTS
    live_run_module.allocate_fusion_replicas = reject_everything
    live_run_module.execution_pubs = lambda choices: []
    live_run_module.FUSION_MAX_ATTEMPTS = 8
    try:
        select_fusion_choices(wide_sets, PACKED_REPLICA_POLICY)
    except LiveRunError as error:
        if "search stopped at FUSION_MAX_ATTEMPTS" not in str(error) or "attempted=8" not in str(error):
            raise RuntimeError(f"the exhausted search reports {error}") from error
    else:
        raise RuntimeError("a search that rejects every combination returns a selection")
    finally:
        live_run_module.allocate_fusion_replicas = original_allocate_fusion_replicas
        live_run_module.execution_pubs = original_execution_pubs
        live_run_module.FUSION_MAX_ATTEMPTS = original_bound
    if rejections != 8:
        raise RuntimeError(f"the attempt bound of 8 allowed {rejections} attempts")


def _verify_required_placement_backtracking() -> None:
    """A preferred path midpoint cannot hide the feasible two-endpoint replica set."""
    snapshot = _fake_snapshot(FakeFez())
    groups = {group.name: group for group in experiment_groups()}
    choices = [
        _synthetic_fusion_choice(groups["design_a"], snapshot, 0, False),
        _synthetic_fusion_choice(groups["design_c_8_1_4"], snapshot, 3, False),
    ]
    graph = rx.PyGraph()
    graph.add_nodes_from(range(snapshot.capabilities.num_qubits))
    graph.add_edges_from_no_data([(0, 1), (1, 2)])
    candidate_qubits = {0: [1, 0, 2], 3: [3, 4]}

    def path_candidates(
        snap: Snapshot, isas: list[QuantumCircuit], floor: float
    ) -> tuple[Any, list[packing.Replica], int]:
        del snap, floor
        source = _physical(isas[0])[0]
        return (
            graph,
            [
                packing.Replica(index, {source: qubit}, 1.0 - index * 0.01)
                for index, qubit in enumerate(candidate_qubits[source])
            ],
            1,
        )

    original_candidates = live_run_module._replica_candidates
    live_run_module._replica_candidates = path_candidates
    try:
        evidence = live_run_module.allocate_fusion_replicas(choices, ADJACENT_REPLICA_POLICY)
        placements = [[replica.qubits for replica in choice.replicas] for choice in choices]
        if placements != [[[0], [2]], [[3], [4]]]:
            raise RuntimeError(f"required replica-set backtracking selected {placements}")
        if evidence["clusters"][0]["required_rounds"] != 2:
            raise RuntimeError("required replica-set backtracking changes the reference requirement")
        if any(sum(entry.reference for entry in choice.entries) != 1 for choice in choices):
            raise RuntimeError("required replica-set backtracking loses a group's reference entry")
        execution_pubs(choices)

        candidate_calls = 0

        def counted_candidates(snap: Snapshot, isas: list[QuantumCircuit], floor: float) -> Any:
            nonlocal candidate_calls
            candidate_calls += 1
            return path_candidates(snap, isas, floor)

        live_run_module._replica_candidates = counted_candidates
        placement_cache: dict[tuple[int, float], Any] = {}
        for _ in range(2):
            live_run_module.allocate_fusion_replicas(choices, ADJACENT_REPLICA_POLICY, placement_cache)
        if candidate_calls != len(choices):
            raise RuntimeError(f"retried joint placement recomputed candidates {candidate_calls} times")
        live_run_module._replica_candidates = path_candidates

        candidate_qubits[0] = [1, 0]
        try:
            live_run_module.allocate_fusion_replicas(choices, ADJACENT_REPLICA_POLICY)
        except LiveRunError as error:
            if "cannot satisfy 2 required joint-placement rounds" not in str(error):
                raise RuntimeError(f"infeasible required replica set reports {error}") from error
        else:
            raise RuntimeError("required replica-set search accepts adjacent replicas")
    finally:
        live_run_module._replica_candidates = original_candidates


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
        "max_execution_seconds": 60,
        "approved_record_sha256": None,
        "replica_floor": PACKED_REPLICA_POLICY.floor,
        "max_replicas": PACKED_REPLICA_POLICY.max_replicas,
        "isolated_reference": PACKED_REPLICA_POLICY.isolated_reference,
        "cross_group_buffer": True,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def _verify_approved_record_gate() -> None:
    """--submit sends nothing unless the fresh plan matches the approved dry run byte for byte."""
    backend = _ProbeBackend("viable", FakeFez())
    service = _ProbeService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    choices, record = live_run_module.plan(service, args)
    live_run_module.evaluate(choices, record)
    original_configure_sampler = live_run_module.configure_sampler
    constructions = 0
    runs: list[int] = []

    def counting_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
    ) -> Any:
        # build_submission_plan constructs a Sampler to record its effective
        # options before any batch runs, so runs, not constructions, count
        # submissions.
        nonlocal constructions
        del backend, twirl, dd
        constructions += 1
        return _ProbeSampler(
            kind, tags, shots, lambda circuits: runs.append(len(circuits)), None, max_execution_seconds
        )

    with tempfile.TemporaryDirectory(prefix="gororoba-approved-record-") as directory:
        approved_dir = Path(directory) / "approved"
        approved_dir.mkdir()
        write_archive(approved_dir, choices)
        write_json(approved_dir, record)
        fresh_record = copy.deepcopy(record)
        fresh_qpy = hashlib.sha256((approved_dir / "isa.qpy").read_bytes()).hexdigest()
        if live_run_module.approved_record_mismatches(approved_dir, fresh_record, fresh_qpy):
            raise RuntimeError("an identical fresh plan mismatches its own approved record")
        record_sha256 = hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest()
        if live_run_module.approved_record_mismatches(approved_dir, fresh_record, fresh_qpy, record_sha256.upper()):
            raise RuntimeError("the approved record's own digest mismatches")
        wrong_digest = live_run_module.approved_record_mismatches(approved_dir, fresh_record, fresh_qpy, "0" * 64)
        if not any("approved-record-sha256" in m for m in wrong_digest):
            raise RuntimeError(f"a replaced approved record passes the digest check: {wrong_digest}")
        if record["policy"].get("max_execution_seconds") != 60:
            raise RuntimeError("the plan's policy does not record the execution ceiling")
        drifted = copy.deepcopy(record)
        drifted["groups"][0]["calibration"] = "2000-01-01T00:00:00+00:00"
        drifted["groups"][0]["calibration_fingerprint"]["target:dt"] = 0.0
        drifted["groups"][0]["initial_layout"] = list(reversed(drifted["groups"][0]["initial_layout"]))
        found = live_run_module.approved_record_mismatches(approved_dir, drifted, "0" * 64)
        if not any("calibration" in m for m in found) or not any("initial_layout" in m for m in found):
            raise RuntimeError(f"drifted plan mismatches read {found}")
        if not any("QPY archive" in m for m in found):
            raise RuntimeError("a changed QPY archive passes the approved-record gate")
        # The refreshed view carries the refreshed snapshot's calibration and
        # the refreshed PUB manifests, not the initial plan's copies.
        pubs = execution_pubs(choices)
        same_view = live_run_module.refreshed_plan_view(record, choices, pubs)
        if live_run_module.approved_record_mismatches(approved_dir, same_view, fresh_qpy):
            raise RuntimeError("the refreshed view of an unchanged plan mismatches the approved record")
        for label, mutate in (
            ("twirl", lambda r: r["policy"].__setitem__("twirl", not r["policy"].get("twirl", False))),
            ("min_remaining_seconds", lambda r: r["policy"].__setitem__("min_remaining_seconds", 999)),
            ("versions", lambda r: r["versions"].__setitem__("qiskit-ibm-runtime", "0.0.0")),
            ("instance_sha256_12", lambda r: r.__setitem__("instance_sha256_12", "000000000000")),
        ):
            changed = copy.deepcopy(record)
            mutate(changed)
            named = live_run_module.approved_record_mismatches(approved_dir, changed, fresh_qpy)
            field = "policy" if label in ("twirl", "min_remaining_seconds") else label
            if not any(field in m for m in named):
                raise RuntimeError(f"a changed {label} passes the approved-record gate")
        if "instance_sha256_12" not in record or len(record["instance_sha256_12"]) != 12:
            raise RuntimeError("the plan records no instance hash")
        submitted = json.loads((approved_dir / "record.json").read_text())
        submitted["submission"] = {}
        submitted["state"] = "submitted"
        (approved_dir / "record.json").write_text(json.dumps(submitted))
        rejected = live_run_module.approved_record_mismatches(approved_dir, fresh_record, fresh_qpy)
        if not any("not a submit-free plan" in m for m in rejected):
            raise RuntimeError("a submitted record passes as an approved dry run")
        write_json(approved_dir, record)
        # The submit path with a mismatching approved record stops before
        # the Sampler and leaves an approval_required record.
        run_dir = Path(directory) / "run"
        run_dir.mkdir()
        args.approved_record = approved_dir
        gated_record = copy.deepcopy(record)
        gated_record["shots"] = int(record["shots"]) + 1
        live_run_module.configure_sampler = counting_sampler
        try:
            try:
                live_run_module.submit(
                    service, list(choices), args, gated_record, lambda: write_archive(run_dir, choices), lambda: None
                )
            except LiveRunError as error:
                if "differs from the approved record" not in str(error):
                    raise RuntimeError(f"the approved-record gate reports {error}") from error
            else:
                raise RuntimeError("a plan that differs from the approved record reaches submission")
        finally:
            live_run_module.configure_sampler = original_configure_sampler
            args.approved_record = None
        mismatches = gated_record.get("renewed_approval", {}).get("mismatches", [])
        if constructions or gated_record["state"] != "approval_required" or "shots differs" not in mismatches:
            raise RuntimeError(f"the approved-record gate leaves {gated_record.get('state')} after {constructions}")
        if (approved_dir / live_run_module.APPROVAL_CONSUMED_FILE).exists():
            raise RuntimeError("a refused submission consumed the approval")
        # A matching plan consumes the authorization at its first batch, and
        # the Sampler carries the execution ceiling; a second matching
        # invocation finds the authorization spent and sends nothing.
        args.approved_record = approved_dir
        args.approved_record_sha256 = record_sha256
        live_run_module.configure_sampler = counting_sampler
        consumed_record = copy.deepcopy(record)
        try:
            live_run_module.submit(
                service, list(choices), args, consumed_record, lambda: write_archive(run_dir, choices), lambda: None
            )
        finally:
            live_run_module.configure_sampler = original_configure_sampler
            args.approved_record = None
            args.approved_record_sha256 = None
        marker = approved_dir / live_run_module.APPROVAL_CONSUMED_FILE
        if not runs or not marker.exists() or json.loads(marker.read_text())["run"] != args.started:
            raise RuntimeError("a matching plan did not consume the approval at its first batch")
        if consumed_record.get("approval_consumed", {}).get("run") != args.started:
            raise RuntimeError("the record does not carry the consumption")
        planned = consumed_record["submission"]["planned_jobs"][0]
        if planned["options"].get("max_execution_time") != 60:
            raise RuntimeError(f"the Sampler options carry no execution ceiling: {planned['options']}")
        real = configure_sampler(FakeFez(), "dynamic", False, None, [], 64, 60)
        if (
            real.options.max_execution_time != 60
            or real.options.model_dump(mode="json").get("max_execution_time") != 60
        ):
            raise RuntimeError("configure_sampler does not set max_execution_time on the client-side Sampler")
        runs.clear()
        args.approved_record = approved_dir
        args.approved_record_sha256 = record_sha256
        live_run_module.configure_sampler = counting_sampler
        second_record = copy.deepcopy(record)
        try:
            try:
                live_run_module.submit(
                    service, list(choices), args, second_record, lambda: write_archive(run_dir, choices), lambda: None
                )
            except LiveRunError as error:
                if "already consumed" not in str(error):
                    raise RuntimeError(f"a second attempt reports {error}") from error
            else:
                raise RuntimeError("a second attempt on a consumed approval reaches submission")
        finally:
            live_run_module.configure_sampler = original_configure_sampler
            args.approved_record = None
            args.approved_record_sha256 = None
        if runs or second_record["state"] != "approval_required":
            raise RuntimeError("a second attempt ran a Sampler or left the state unchanged")
        marker.unlink()


class _ShiftedReadout:
    """BackendProperties whose prob_meas1_prep0 on one qubit reads shifted: a republish that moved one value."""

    def __init__(self, properties: Any, qubit: int, shift: float = 0.01):
        self._properties = properties
        self._qubit = qubit
        self._shift = shift

    def __getattr__(self, name: str) -> Any:
        return getattr(self._properties, name)

    def qubit_property(self, qubit: int, name: str | None = None) -> Any:
        value = self._properties.qubit_property(qubit, name)
        if qubit == self._qubit and name == "prob_meas1_prep0":
            return (value[0] + self._shift, *value[1:])
        return value


def _legacy_approved(source: Path, destination: Path) -> Path:
    """A copy of an approved dry run whose groups carry no calibration values, as every earlier record."""
    destination.mkdir()
    shutil.copyfile(source / "isa.qpy", destination / "isa.qpy")
    legacy = json.loads((source / "record.json").read_text())
    for group in legacy["groups"]:
        group.pop("calibration_fingerprint")
        group.pop("calibration_fingerprint_sha256")
    write_json(destination, legacy)
    return destination


class _FiniteQuotaService(_ProbeService):
    """A service reporting a fixed finite quota, so a same-calibration refresh reuses the plan."""

    def usage(self) -> dict[str, Any]:
        return {"usage_limit_reached": False, "usage_remaining_seconds": 600.0}


def _verify_approval_calibration_values() -> None:
    """An approval binds the consumed calibration values: a timestamp-only republish passes, a moved value refuses.

    The dry run records each group's calibration_values; the refresh, the
    preflight before planning, and every batch compare fresh values with
    them. An approved record without values keeps the timestamp rule.
    """
    backend = _ProbeBackend("viable", FakeFez())
    service = _FiniteQuotaService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    with redirect_stdout(io.StringIO()):
        choices, record = live_run_module.plan(service, args)
        live_run_module.evaluate(choices, record)
    group = record["groups"][0]
    name = group["group"]
    values = group.get("calibration_fingerprint")
    if not isinstance(values, dict) or not values:
        raise RuntimeError("the dry-run group records no calibration values")
    if group["calibration_fingerprint_sha256"] != live_run_module.calibration_values_sha256(values):
        raise RuntimeError("the recorded calibration-value digest differs from its values")
    digest = group.get("noise_serialized_channels_sha256")
    if not (isinstance(digest, str) and len(digest) == 64):
        raise RuntimeError(f"the dry-run group records no noise-model digest: {digest!r}")
    measured = sorted(int(key.split(":")[1]) for key in values if key.startswith("e10:"))
    if not measured or "target:dt" not in values or not any(key.startswith("target:t1:") for key in values):
        raise RuntimeError(f"the calibration values omit readout, timing or coherence: {sorted(values)[:8]}")
    shifted_qubit = measured[0]
    same = live_run_module.same_calibration_instant
    if not same("2026-10-17T17:50:43-07:00", "2026-10-18T00:50:43+00:00") or same(
        "2026-10-17T17:50:43-07:00", "2026-10-18T00:50:44+00:00"
    ):
        raise RuntimeError("calibration stamps do not compare as instants")
    if same("unparsed", "other") or not same("unparsed", "unparsed"):
        raise RuntimeError("unparsed calibration stamps do not compare as text")
    republished = "2099-01-01T00:00:00+00:00"

    def moved_choice(shift: bool) -> Choice:
        moved = copy.copy(choices[0])
        moved.snap = copy.copy(choices[0].snap)
        moved.snap.calibration = republished
        if shift:
            moved.snap.properties = _ShiftedReadout(moved.snap.properties, shifted_qubit)
        return moved

    def rolled_snapshots(shift: bool, after: int) -> Any:
        original = live_run_module.take_snapshot
        calls = 0

        def rolled(service_: Any, backend_name: str, operator_excluded: Collection[int] = ()) -> Snapshot:
            nonlocal calls
            calls += 1
            snapshot = original(service_, backend_name, operator_excluded)
            if calls > after:
                snapshot.calibration = republished
                if shift:
                    snapshot.properties = _ShiftedReadout(snapshot.properties, shifted_qubit)
            return snapshot

        return patch.object(live_run_module, "take_snapshot", rolled)

    class PlanningStarted(RuntimeError):
        """Candidate selection began: the preflight let the plan proceed."""

    def refuse_planning(*_args: Any, **_kwargs: Any) -> Any:
        raise PlanningStarted("planning started")

    runs: list[int] = []

    def counting_sampler(
        backend_: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
    ) -> Any:
        del backend_, twirl, dd, rep_delay
        return _ProbeSampler(
            kind, tags, shots, lambda circuits: runs.append(len(circuits)), None, max_execution_seconds
        )

    with tempfile.TemporaryDirectory(prefix="gororoba-approval-values-") as directory:
        approved_dir = Path(directory) / "approved"
        approved_dir.mkdir()
        write_archive(approved_dir, choices)
        write_json(approved_dir, record)
        legacy_dir = _legacy_approved(approved_dir, Path(directory) / "legacy")
        qpy_digest = hashlib.sha256((approved_dir / "isa.qpy").read_bytes()).hexdigest()
        pubs = execution_pubs(choices)

        # The refresh comparison.
        binding: dict[str, Any] = {}
        view = live_run_module.refreshed_plan_view(record, [moved_choice(False)], pubs)
        found = live_run_module.approved_record_mismatches(approved_dir, view, qpy_digest, None, binding)
        accepted = binding.get("accepted_timestamp_changes", [])
        if found or len(accepted) != 1 or accepted[0]["fresh_calibration"] != republished:
            raise RuntimeError(f"a timestamp-only republish refuses or goes unrecorded: {found} {binding}")
        if binding.get("fingerprint_sha256") != {name: group["calibration_fingerprint_sha256"]}:
            raise RuntimeError(f"the refresh binds other digests than the approved values: {binding}")
        view = live_run_module.refreshed_plan_view(record, [moved_choice(True)], pubs)
        found = live_run_module.approved_record_mismatches(approved_dir, view, qpy_digest)
        if not any("calibration values changed" in m and f"e10:{shifted_qubit}" in m for m in found):
            raise RuntimeError(f"a moved readout value on a placed qubit passes the refresh: {found}")
        legacy_binding: dict[str, Any] = {}
        view = live_run_module.refreshed_plan_view(record, [moved_choice(False)], pubs)
        found = live_run_module.approved_record_mismatches(legacy_dir, view, qpy_digest, None, legacy_binding)
        if not any(f"{name}: calibration" in m for m in found) or legacy_binding:
            raise RuntimeError(f"a record without values accepts a moved timestamp: {found} {legacy_binding}")
        offset = copy.copy(choices[0])
        offset.snap = copy.copy(choices[0].snap)
        instant = datetime.fromisoformat(choices[0].snap.calibration)
        offset.snap.calibration = instant.astimezone(UTC).isoformat()
        if offset.snap.calibration == choices[0].snap.calibration:
            raise RuntimeError("the fixture calibration already reads UTC")
        view = live_run_module.refreshed_plan_view(record, [offset], pubs)
        found = live_run_module.approved_record_mismatches(legacy_dir, view, qpy_digest)
        if found:
            raise RuntimeError(f"one calibration instant under another UTC offset refuses: {found}")

        # The preflight at the first discovery, before any planning.
        def preflight_plan(approved: Path, shift: bool) -> Any:
            submit_args = _fixture_args(groups=["hybrid_shor_mod15"], submit=True, approved_record=approved)
            with (
                rolled_snapshots(shift, 0),
                patch.object(live_run_module, "select_candidates", refuse_planning),
                redirect_stdout(io.StringIO()),
            ):
                try:
                    live_run_module.plan(service, submit_args)
                except live_run_module.ApprovalPreflightRefused as error:
                    return error
                except PlanningStarted:
                    return None
            raise RuntimeError(f"the plan neither started nor stopped (shift={shift}, approved={approved.name})")

        refused = preflight_plan(approved_dir, True)
        if refused is None:
            raise RuntimeError("a moved readout value on a placed qubit lets planning start")
        refusal = refused.record
        if (
            refusal["state"] != "approval_required"
            or not any(f"e10:{shifted_qubit}" in m for m in refusal["renewed_approval"]["mismatches"])
            or refusal["approved_record"]["record_sha256"]
            != hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest()
        ):
            raise RuntimeError(f"the preflight refusal record is incomplete: {refusal}")
        legacy_refused = preflight_plan(legacy_dir, False)
        if legacy_refused is None or not any(
            "binds no calibration values" in m for m in legacy_refused.record["renewed_approval"]["mismatches"]
        ):
            raise RuntimeError("a record without values passes a moved timestamp at the preflight")
        if preflight_plan(approved_dir, False) is not None:
            raise RuntimeError("a timestamp-only republish stops at the preflight")
        with rolled_snapshots(False, 0), redirect_stdout(io.StringIO()):
            republished_snapshots, _skipped, _inventory = discover_snapshots(service, None, None)
        passed = live_run_module.approved_calibration_preflight(approved_dir, republished_snapshots)
        accepted = passed["accepted_timestamp_changes"]
        if passed["mismatches"] or [entry["fresh_calibration"] for entry in accepted] != [republished]:
            raise RuntimeError(f"the preflight records no accepted timestamp change: {passed}")
        # The CLI writes the refusal as an approval_required run record.
        out = Path(directory) / "out"
        argv = [
            "--groups",
            "hybrid_shor_mod15",
            "--backends",
            "viable",
            "--out",
            str(out),
            "--submit",
            "--approved-record",
            str(approved_dir),
            "--approved-record-sha256",
            hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest(),
            "--max-execution-seconds",
            "60",
            "--max-total-execution-seconds",
            "60",
        ]
        with (
            patch.object(live_run_module, "QiskitRuntimeService", lambda: service),
            rolled_snapshots(True, 0),
            patch.object(live_run_module, "select_candidates", refuse_planning),
            redirect_stdout(io.StringIO()),
            redirect_stderr(io.StringIO()),
        ):
            status = live_run_module.main(argv)
        written = [json.loads(path.read_text()) for path in out.glob("*/record.json")]
        if status != 1 or len(written) != 1 or written[0]["state"] != "approval_required":
            raise RuntimeError(f"the CLI preflight refusal exits {status} with records {written}")
        if (approved_dir / live_run_module.APPROVAL_CONSUMED_FILE).exists():
            raise RuntimeError("a preflight refusal consumed the approval")

        # A republish before the refresh is accepted there and again at the
        # batch; a value that moves after the refresh stops the batch for
        # renewed approval.
        run_dir = Path(directory) / "run"
        run_dir.mkdir()
        args.approved_record = approved_dir
        try:
            with (
                rolled_snapshots(False, 0),
                patch.object(live_run_module, "configure_sampler", counting_sampler),
                redirect_stdout(io.StringIO()),
            ):
                proceeded = copy.deepcopy(record)
                live_run_module.submit(
                    service, list(choices), args, proceeded, lambda: write_archive(run_dir, choices), lambda: None
                )
            revalidated = proceeded["submission"]["planned_jobs"][0]["pre_submit_revalidation"]
            refreshed = proceeded["approved_record"]["calibration_values"]
            if proceeded["approved_record"]["mismatches"] or [
                entry["fresh_calibration"] for entry in refreshed["accepted_timestamp_changes"]
            ] != [republished]:
                raise RuntimeError(f"the refresh records no accepted timestamp change: {refreshed}")
            if (
                not runs
                or proceeded["state"] != "submitted"
                or revalidated["calibration"] != republished
                or revalidated["calibration_fingerprint_sha256"] != {name: group["calibration_fingerprint_sha256"]}
            ):
                raise RuntimeError(f"a timestamp-only batch republish stops or goes unrecorded: {revalidated}")
            (approved_dir / live_run_module.APPROVAL_CONSUMED_FILE).unlink()
            runs.clear()
            for approved, shift, expected in (
                (approved_dir, True, "calibration values changed"),
                (legacy_dir, False, "calibration moved after the approved-record check"),
            ):
                args.approved_record = approved
                stopped = copy.deepcopy(record)
                with (
                    rolled_snapshots(shift, 1),
                    patch.object(live_run_module, "configure_sampler", counting_sampler),
                    redirect_stdout(io.StringIO()),
                ):
                    try:
                        live_run_module.submit(
                            service, list(choices), args, stopped, lambda: write_archive(run_dir, choices), lambda: None
                        )
                    except LiveRunError as error:
                        if expected not in str(error):
                            raise RuntimeError(f"a moved batch calibration reports {error}") from error
                    else:
                        raise RuntimeError(f"a moved batch calibration reaches submission ({approved.name})")
                if runs or stopped["state"] != "approval_required":
                    raise RuntimeError(f"a moved batch calibration ran a Sampler or left {stopped['state']}")
                if (approved / live_run_module.APPROVAL_CONSUMED_FILE).exists():
                    raise RuntimeError("a refused batch consumed the approval")
        finally:
            args.approved_record = None

    # With a batch already sent, the lifecycle stays with the submission.
    fresh = live_run_module.take_snapshot(service, backend.name)
    packed = [entry.packed for entry in choices[0].entries]
    unchanged = {name: live_run_module.calibration_values(packed, fresh.backend.target, fresh.properties)}
    shifted = {
        name: live_run_module.calibration_values(
            packed, fresh.backend.target, _ShiftedReadout(fresh.properties, shifted_qubit)
        )
    }
    bound = {name: group["calibration_fingerprint_sha256"]}
    for digests, fresh_values, reported in ((bound, unchanged, False), (bound, shifted, True), ({}, None, True)):
        sent = copy.deepcopy(record)
        sent["submission"] = {"jobs": [{"job_id": "sent-earlier"}]}
        sent["approved_record"] = {
            "calibrations": {backend.name: "approved"},
            "calibration_values": {"fingerprint_sha256": digests},
        }
        sent["state"] = "submitted"
        drift = live_run_module.approved_calibration_drift(sent, backend.name, republished, fresh_values)
        if (drift is not None) != reported:
            raise RuntimeError(f"batch drift with bound digests {bool(digests)} reports {drift!r}")
        if sent["state"] != "submitted" or ("renewed_approval_for_unsent_batches" in sent) != reported:
            raise RuntimeError("batch drift after a sent batch resets the lifecycle or goes unrecorded")

    # A batch whose groups are partly bound: the bound group's values decide
    # it whatever the timestamp, and only the unbound group falls to the
    # timestamp, so changed bound values never pass under an unchanged stamp.
    accepted = "2026-01-01T00:00:00+00:00"
    partly_bound: list[tuple[str, Any, str | None]] = [
        (accepted, unchanged[name], None),
        (accepted, shifted[name], f"calibration values changed for {name}"),
        (republished, unchanged[name], "the timestamp moved for unbound_group"),
        (republished, shifted[name], f"calibration values changed for {name}; the timestamp moved for unbound_group"),
    ]
    for calibration, bound_values, wanted in partly_bound:
        mixed = copy.deepcopy(record)
        mixed["approved_record"] = {
            "calibrations": {backend.name: accepted},
            "calibration_values": {"fingerprint_sha256": bound},
        }
        batch = {name: bound_values, "unbound_group": unchanged[name]}
        drift = live_run_module.approved_calibration_drift(mixed, backend.name, calibration, batch)
        if (drift is None) != (wanted is None) or (wanted is not None and wanted not in str(drift)):
            raise RuntimeError(f"a partly bound batch at {calibration} reports {drift!r}, wanted {wanted!r}")
        if mixed["state"] != ("approval_required" if wanted else record["state"]):
            raise RuntimeError(f"a partly bound batch leaves state {mixed['state']}")


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
        pinned: list[int] | None = None,
    ) -> list[Choice]:
        del snaps, seeds, pinned
        log[group.name] = {"fixture": [{"stage": "renewed_approval_contract"}]}
        return [revised_choice]

    def forbidden_configure_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
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
        # A planning inventory unlike the refresh takes the rebuild path this
        # fixture exercises.
        approval_record["system_inventory"] = {"planning-only-backend": {}}
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
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
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
    record: dict[str, Any] = {"state": "planned", "shots": args.shots}
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
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
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


def _verify_approved_backend_scope() -> None:
    """A submission plans only over the approved record's backends; a newly eligible one is never probed."""
    with tempfile.TemporaryDirectory() as temporary:
        approved_dir = Path(temporary)
        (approved_dir / "record.json").write_text(json.dumps({"backends": {"viable": {}, "approved": {}}}))
        if approved_backend_scope(approved_dir) != ["approved", "viable"]:
            raise RuntimeError("approved scope differs from the approved record's eligible backends")
        (approved_dir / "record.json").write_text(json.dumps({"backends": {}}))
        try:
            approved_backend_scope(approved_dir)
        except LiveRunError:
            pass
        else:
            raise RuntimeError("an approved record without eligible backends yields a scope")
    # The newcomer fails its first probe stage, so probing it would leave probe_failed.
    service = _ProbeService([_ProbeBackend("approved", FakeFez()), _ProbeBackend("newcomer", FakeFez(), "refresh")])
    snapshots, skipped, inventory = discover_snapshots(service, None, None, scope=["approved"])
    if [snapshot.name for snapshot in snapshots] != ["approved"]:
        raise RuntimeError("a backend outside the approved scope reached planning")
    if inventory["newcomer"]["eligibility"] != "outside_approved_scope":
        raise RuntimeError(f"out-of-scope backend was probed: {inventory['newcomer']}")
    if "approved record" not in skipped["newcomer"]["reason"]:
        raise RuntimeError(f"out-of-scope backend reports {skipped['newcomer']}")
    unscoped, _, unscoped_inventory = discover_snapshots(service, None, None)
    if [snapshot.name for snapshot in unscoped] != ["approved"] or unscoped_inventory["newcomer"]["eligibility"] != (
        "probe_failed"
    ):
        raise RuntimeError("a dry run without scope stops probing every discovered backend")


def _verify_operator_qubit_exclusion() -> None:
    """--exclude-qubits withholds named qubits from every snapshot and from placement, whatever their calibration."""
    if live_run_module._qubit_exclusion("ibm_kingston:0-4,16") != ("ibm_kingston", frozenset({0, 1, 2, 3, 4, 16})):
        raise RuntimeError("the qubit exclusion parser misreads a range list")
    for malformed in ("ibm_kingston", "ibm_kingston:", "ibm_kingston:4-1", "ibm_kingston:a"):
        try:
            live_run_module._qubit_exclusion(malformed)
        except argparse.ArgumentTypeError:
            pass
        else:
            raise RuntimeError(f"a malformed exclusion {malformed!r} parses")
    withheld = {0, 1, 2, 3, 4, 16}
    service = _ProbeService([_ProbeBackend("viable", FakeFez())])
    snapshot = live_run_module.take_snapshot(service, "viable", withheld)
    if not withheld <= set(snapshot.excluded_qubits):
        raise RuntimeError("an operator-excluded qubit stays available")
    plain = live_run_module.take_snapshot(service, "viable")
    if any(plain.excluded_qubits.get(q) == "operator exclusion" for q in withheld):
        raise RuntimeError("an exclusion leaks into a snapshot taken without it")
    snapshots, _, _ = discover_snapshots(service, None, None, operator_excluded={"viable": withheld})
    if not withheld <= set(snapshots[0].excluded_qubits):
        raise RuntimeError("discovery drops the operator exclusion")
    group = next(group for group in experiment_groups() if group.name == "design_a")
    choice = select(group, snapshots, 1, {}, SINGLE_REPLICA_POLICY)
    placed = {q for replica in choice.replicas for q in replica.qubits}
    if placed & withheld:
        raise RuntimeError(f"placement uses operator-excluded qubits {sorted(placed & withheld)}")
    # An edgeless six-qubit pattern searches only the placeable qubits, so a corner
    # left as the only placeable set is found at once and used whole.
    from qubit_baseline import qubit_baseline_group

    corner = {0, 1, 2, 3, 4, 16}
    only_corner, _, _ = discover_snapshots(service, None, None, operator_excluded={"viable": set(range(156)) - corner})
    baseline = select(qubit_baseline_group(), only_corner, 1, {}, SINGLE_REPLICA_POLICY)
    if [set(replica.qubits) for replica in baseline.replicas] != [corner]:
        raise RuntimeError("the qubit baseline does not occupy exactly the placeable corner")
    try:
        live_run_module.take_snapshot(service, "viable", {9999})
    except LiveRunError:
        pass
    else:
        raise RuntimeError("an exclusion outside the backend is accepted")


def _verify_fragmented_target_layout() -> None:
    """A group placed on a few operator-allowed tiles compiles from a layout seeded inside them."""
    service = _ProbeService([_ProbeBackend("viable", FakeFez())])
    tile = {0, 1, 2, 3, 4}
    snapshots, _, _ = discover_snapshots(service, None, None, operator_excluded={"viable": set(range(156)) - tile})
    layouts = live_run_module.component_layouts(snapshots[0], 3)
    if layouts != [[0, 1, 2]]:
        raise RuntimeError(f"component layouts on the 0-4 line read {layouts}")
    group = next(group for group in experiment_groups() if group.name == "design_a")
    choice = select(group, snapshots, 1, {}, SINGLE_REPLICA_POLICY)
    placed = {q for replica in choice.replicas for q in replica.qubits}
    if not placed or not placed <= tile:
        raise RuntimeError(f"design_a on the 0-4 tile placed {sorted(placed)}")
    # One placeable qubit leaves the admission target without any CZ coupler.
    from diagnostic_controls import readout_delay_group

    lone, _, _ = discover_snapshots(service, None, None, operator_excluded={"viable": set(range(156)) - {79}})
    single = select(readout_delay_group(), lone, 1, {}, SINGLE_REPLICA_POLICY)
    if [sorted(replica.qubits) for replica in single.replicas] != [[79]]:
        raise RuntimeError("the single-qubit readout campaign does not occupy the one placeable qubit")


def _verify_compile_panic_isolation() -> None:
    """A transpiler panic on one backend is one recorded compile failure, not a crashed plan."""

    class PanicException(BaseException):
        pass

    def panicking(*_: Any, **__: Any) -> QuantumCircuit:
        raise PanicException("capacity overflow")

    service = _ProbeService([_ProbeBackend("viable", FakeFez())])
    snapshots, _, _ = discover_snapshots(service, None, None)
    group = next(group for group in experiment_groups() if group.name == "design_a")
    with patch.object(live_run_module, "transpile", panicking):
        try:
            select_candidates(group, snapshots, 1, {})
        except LiveRunError as error:
            if "compile_error: CompilePanic" not in str(error):
                raise RuntimeError(f"a transpiler panic reports {error}") from error
        else:
            raise RuntimeError("a panicking compile produced a candidate")

    def interrupted(*_: Any, **__: Any) -> QuantumCircuit:
        raise KeyboardInterrupt

    with patch.object(live_run_module, "transpile", interrupted):
        try:
            select_candidates(group, snapshots, 1, {})
        except KeyboardInterrupt:
            pass
        else:
            raise RuntimeError("an interrupt during compilation is swallowed")


def _verify_experiment_source_manifest() -> None:
    """Every static local import in the declared run sources participates in replay identity."""
    source_root = Path(live_run_module.__file__).resolve().parent
    manifest = set(live_run_module.EXPERIMENT_SOURCE_MANIFEST)
    for relative_path in sorted(manifest):
        for node in ast.walk(ast.parse((source_root / relative_path).read_text())):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            for module in modules:
                dependency = module.split(".")[0] + ".py"
                if (source_root / dependency).is_file() and dependency not in manifest:
                    raise RuntimeError(f"experiment source manifest omits {relative_path}'s dependency {dependency}")
    first_digest = experiment_digest()
    second_digest = experiment_digest()
    if len(first_digest) != 64 or first_digest != second_digest:
        raise RuntimeError("experiment source manifest digest is unstable")


class _NoInstanceService(_ProbeService):
    def active_instance(self) -> str:
        return ""


class _LowBudgetService(_ProbeService):
    def usage(self) -> dict[str, Any]:
        return {"usage_limit_reached": False, "usage_remaining_seconds": 30.0}


def _verify_instance_and_ceiling() -> None:
    """A service without an instance is refused at planning; a ceiling above the remaining budget stops a batch."""
    backend = _ProbeBackend("viable", FakeFez())
    try:
        live_run_module.plan(_NoInstanceService([backend]), _fixture_args(groups=["hybrid_shor_mod15"]))
    except LiveRunError as error:
        if "no IBM Cloud instance" not in str(error):
            raise RuntimeError(f"an unresolved instance reports {error}") from error
    else:
        raise RuntimeError("an unresolved instance plans")
    service = _LowBudgetService([backend])
    args = _fixture_args(groups=["hybrid_shor_mod15"], max_execution_seconds=60)
    choices, record = live_run_module.plan(service, args)
    live_run_module.evaluate(choices, record)
    runs: list[int] = []
    original_configure_sampler = live_run_module.configure_sampler

    def ceiling_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
    ) -> Any:
        del backend, twirl, dd, max_execution_seconds
        return _ProbeSampler(kind, tags, shots, lambda circuits: runs.append(len(circuits)))

    live_run_module.configure_sampler = ceiling_sampler
    with tempfile.TemporaryDirectory(prefix="gororoba-ceiling-") as directory:
        run_dir = Path(directory)
        try:
            try:
                live_run_module.submit(
                    service, list(choices), args, record, lambda: write_archive(run_dir, choices), lambda: None
                )
            except LiveRunError as error:
                if "execution ceiling" not in str(error):
                    raise RuntimeError(f"a ceiling above the remaining budget reports {error}") from error
            else:
                raise RuntimeError("a ceiling above the remaining budget reaches submission")
        finally:
            live_run_module.configure_sampler = original_configure_sampler
    if runs:
        raise RuntimeError("a refused ceiling ran a Sampler")


def _verify_buffer_scope() -> None:
    """The cross-group buffer separates different groups only, across excluded couplers included.

    The admitted graph omits coupler 0-1 (excluded by quality policy); the
    physical graph keeps it. Two replicas of one group on qubits 0 and 1 are
    one hop apart only physically, so the within-group rule (admitted graph)
    allows them; two groups on 0 and 1 are physical neighbors, so the buffer
    forbids that pairing and allows it when off.
    """
    admitted = rx.PyGraph()
    admitted.add_nodes_from(range(6))
    admitted.add_edges_from_no_data([(2, 3), (4, 5)])
    physical = rx.PyGraph()
    physical.add_nodes_from(range(6))
    physical.add_edges_from_no_data([(0, 1), (2, 3), (4, 5)])

    def pool(candidates: list[int], index: int) -> Any:
        return live_run_module._FusionPlacementPool(
            None,  # type: ignore[arg-type]
            admitted,
            [Replica(k, {0: q}, 1.0 - 0.01 * k) for k, q in enumerate(candidates)],
            index,
            1,
            None,
            physical_graph=physical,
        )

    same_group = [pool([0, 1], 0)]
    if live_run_module._placement_assignment(same_group, set(), 2, True) is None:
        raise RuntimeError("the cross-group buffer blocks a group's own replica across an excluded coupler")
    two_groups = [pool([0], 0), pool([1], 1)]
    if live_run_module._placement_assignment(two_groups, set(), 1, True) is not None:
        raise RuntimeError("two groups on physically coupled qubits pass the cross-group buffer")
    if live_run_module._placement_assignment([pool([0], 0), pool([1], 1)], set(), 1, False) is None:
        raise RuntimeError("two disjoint groups fail with the buffer off")
    cluster = [pool([0], 0), pool([1, 4], 1)]
    live_run_module._commit_placement_assignment([(cluster[0], cluster[0].candidates[0])], set(), cluster)
    if cluster[1].foreign != {0, 1} or cluster[0].foreign:
        raise RuntimeError(f"committed footprints reach the wrong pools: {[p.foreign for p in cluster]}")


def _verify_placement_duplicate_branch_order() -> None:
    """Equivalent embeddings retain their multiplicity in the original pool heuristic."""
    graph = rx.PyGraph()
    graph.add_nodes_from(range(8))
    graph.add_edges_from_no_data([(0, 1), (2, 3), (4, 5), (6, 7)])

    def pool(index: int, mappings: list[tuple[int, int]]) -> Any:
        return live_run_module._FusionPlacementPool(
            None,  # type: ignore[arg-type]
            graph,
            [Replica(number, dict(enumerate(mapping)), 1.0 - number * 0.01) for number, mapping in enumerate(mappings)],
            index,
            2,
            physical_graph=graph,
        )

    pools = [pool(0, [(0, 1), (1, 0), (2, 3)]), pool(1, [(0, 1), (2, 3)])]
    result = live_run_module._placement_assignment(pools, set(), 1, False)
    observed = [(item.original_index, candidate.index, candidate.mapping) for item, candidate in result or []]
    expected = [(0, 2, {0: 2, 1: 3}), (1, 0, {0: 0, 1: 1})]
    if observed != expected:
        raise RuntimeError(f"equivalent-candidate pruning changed the first placement: {observed}")
    repeated = [pool(0, [(0, 1), (1, 0), (2, 3), (3, 2), (4, 5), (5, 4), (6, 7)])]
    occupied: set[int] = set()
    for required, expected_indices in ((2, [0, 2]), (1, [4]), (1, [6])):
        result = live_run_module._placement_assignment(repeated, occupied, required, True)
        if result is None or [candidate.index for _, candidate in result] != expected_indices:
            raise RuntimeError("equivalent-candidate pruning changed a required or surplus replica round")
        live_run_module._commit_placement_assignment(result, occupied, repeated)


def _verify_static_placement_judge() -> None:
    """Static check coalescing equals complete relabeling, including parameter bounds."""
    target = FakeFez().target
    sources = []
    for angle in (0.0, math.pi / 4, math.pi / 2, math.pi, -math.pi, 2 * math.pi, 0.0, math.pi):
        circuit = QuantumCircuit(target.num_qubits, 1)
        circuit.sx(0)
        circuit.rz(angle, 0)
        circuit.cz(0, 1)
        circuit.barrier(0, 1)
        circuit.measure(1, 0)
        sources.append(circuit)
    mappings = [dict(enumerate(edge)) for edge in list(target["cz"])[:16]]

    def compare(judge: live_run_module.PlacementJudge, mapping: dict[int, int]) -> float | None:
        reference = copy.copy(judge)
        object.__setattr__(reference, "static_checks", None)
        expected = reference(mapping)
        observed = judge(mapping)
        if observed != expected:
            raise RuntimeError(f"static placement validation changed an exact score: {expected} -> {observed}")
        return observed

    judge = live_run_module.PlacementJudge(tuple(sources), target, frozenset(), frozenset())
    if judge.static_checks is None or len(judge.static_checks) >= sum(len(circuit.data) for circuit in sources):
        raise RuntimeError("shared static instruction checks were not coalesced")
    for mapping in mappings:
        compare(judge, mapping)
        for excluded_qubits, excluded_edges in (
            (frozenset([mapping[0]]), frozenset()),
            (frozenset(), frozenset([tuple(mapping.values())])),
            (frozenset(), frozenset([tuple(reversed(tuple(mapping.values())))])),
        ):
            rejected = live_run_module.PlacementJudge(tuple(sources), target, excluded_qubits, excluded_edges)
            if compare(rejected, mapping) is not None:
                raise RuntimeError("static placement validation admitted an excluded qubit or coupler")
    with patch.object(packing, "relabel", wraps=packing.relabel) as relabel:
        if judge(mappings[0]) is None or relabel.call_count != 1:
            raise RuntimeError("static placement validation must relabel only the admitted primary for scoring")

    bounded = Target(num_qubits=4, qubit_properties=[QubitProperties(t1=100.0, t2=100.0)] * 4)
    singles = {(qubit,): InstructionProperties(duration=1.0, error=0.001) for qubit in range(4)}
    bounded.add_instruction(RZGate(Parameter("bounded_placement_angle")), singles, angle_bounds=[(0.0, 1.0)])
    bounded.add_instruction(SXGate(), singles)
    bounded.add_instruction(Measure(), singles)
    bounded.add_instruction(CZGate(), {(0, 1): InstructionProperties(duration=2.0, error=0.002)})
    valid = QuantumCircuit(4, 1)
    valid.rz(0.25, 0)
    valid.sx(0)
    valid.cz(0, 1)
    valid.measure(1, 0)
    invalid = valid.copy()
    invalid.data[0] = invalid.data[0].replace(operation=RZGate(1.25))
    for circuits, accepted in (((valid, valid.copy()), True), ((valid, invalid), False)):
        constrained = live_run_module.PlacementJudge(circuits, bounded, frozenset(), frozenset())
        if (compare(constrained, {0: 0, 1: 1}) is not None) != accepted:
            raise RuntimeError("static placement validation erased a distinct bounded-angle check")

    delayed = QuantumCircuit(target.num_qubits, 1)
    delayed.delay(256, target.num_qubits - 1, unit="dt")
    delayed.sx(0)
    delayed.measure(0, 0)
    delay_judge = live_run_module.PlacementJudge((delayed,), target, frozenset(), frozenset())
    compare(delay_judge, {0: target.num_qubits - 1})
    unsupported = QuantumCircuit(4, 1)
    unsupported.unitary(np.eye(2), 0)
    unsupported.measure(0, 0)
    dynamic = QuantumCircuit(target.num_qubits, 1)
    dynamic.measure(0, 0)
    with dynamic.if_test((dynamic.clbits[0], 1)):
        dynamic.x(1)
    dynamic.measure(1, 0)
    for circuit, checked_target in ((unsupported, bounded), (dynamic, target)):
        recursive = live_run_module.PlacementJudge((circuit,), checked_target, frozenset(), frozenset())
        if recursive.static_checks is not None:
            raise RuntimeError("non-scalar or dynamic placement bypassed complete relabeling")
        compare(recursive, {0: 0, 1: 1})


def _verify_unchanged_since_planning() -> None:
    """The pre-submit fast path reuses a plan only when every backend matches planning."""
    inventory = {
        "ibm_a": {"eligibility": "eligible", "calibration": "2026-01-01T00:00:00Z", "pending_jobs": 1},
        "ibm_b": {"eligibility": "eligible", "calibration": "2026-01-01T01:00:00Z", "pending_jobs": 4},
    }
    record: dict[str, Any] = {"system_inventory": copy.deepcopy(inventory), "budget_plan": {"remaining_seconds": 500}}
    if not live_run_module.unchanged_since_planning(record, copy.deepcopy(inventory), [], [], 500):
        raise RuntimeError("identical planning and refresh inventories rebuilt the plan")
    for name, field, value in (
        ("ibm_b", "calibration", "2026-01-01T02:00:00Z"),
        ("ibm_a", "eligibility", "maintenance"),
    ):
        changed = copy.deepcopy(inventory)
        changed[name][field] = value
        if live_run_module.unchanged_since_planning(record, changed, [], [], 500):
            raise RuntimeError(f"a changed {field} on {name} reused the plan")
    added = copy.deepcopy(inventory) | {"ibm_c": {"eligibility": "eligible", "calibration": "x"}}
    if live_run_module.unchanged_since_planning(record, added, [], [], 500):
        raise RuntimeError("a new backend in the refresh inventory reused the plan")
    gained = copy.deepcopy(inventory)
    for entry in (inventory["ibm_b"], record["system_inventory"]["ibm_b"]):
        entry["capabilities"] = {"dynamic_circuits": False}
    gained["ibm_b"]["capabilities"] = {"dynamic_circuits": True}
    if live_run_module.unchanged_since_planning(record, gained, [], [], 500):
        raise RuntimeError("an unselected backend's capability change reused the plan")
    del inventory["ibm_b"]["capabilities"], record["system_inventory"]["ibm_b"]["capabilities"]
    delayed = copy.deepcopy(inventory)
    delayed["ibm_b"]["repetition_delay"] = 1.0e-4
    if live_run_module.unchanged_since_planning(record, delayed, [], [], 500):
        raise RuntimeError("a changed repetition delay on an unselected backend reused the plan")
    if live_run_module.unchanged_since_planning(record, copy.deepcopy(inventory), [], [], 499):
        raise RuntimeError("a changed account quota reused the optimized plan")
    refetched = copy.deepcopy(inventory)
    refetched["ibm_a"]["fetched_at"] = "later"
    if not live_run_module.unchanged_since_planning(record, refetched, [], [], 500):
        raise RuntimeError("a fetch timestamp alone rebuilt the plan")
    queue_only = copy.deepcopy(inventory)
    queue_only["ibm_a"]["pending_jobs"] = 9
    if live_run_module.unchanged_since_planning(record, queue_only, [], [], 500):
        raise RuntimeError("a queue-length change, which breaks selection ties, reused the plan")
    upgraded = copy.deepcopy(inventory)
    upgraded["ibm_a"] |= {"backend_version": "9.9.9", "processor_type": {"family": "Heron", "revision": "3"}}
    if not live_run_module.unchanged_since_planning(record, upgraded, [], [], 500):
        raise RuntimeError("a backend version or processor type, which selection never reads, rebuilt the plan")


def _verify_backend_identity_records() -> None:
    """Every planned record carries each backend's version and processor type as data no gate compares."""
    backend = _ProbeBackend("viable", FakeFez())
    configuration = backend.configuration()
    expected = {
        "backend_version": str(configuration.backend_version),
        "processor_type": {str(k): str(v) for k, v in configuration.processor_type.items()},
    }
    if live_run_module.backend_identity(backend) != expected:
        raise RuntimeError(f"backend identity reads {live_run_module.backend_identity(backend)}, not {expected}")
    bare = _ProbeBackend("bare", FakeFez())
    bare_configuration = copy.copy(bare._backend.configuration())
    del bare_configuration.processor_type
    with patch.object(bare, "configuration", lambda: bare_configuration):
        if live_run_module.backend_identity(bare)["processor_type"] is not None:
            raise RuntimeError("a backend reporting no processor type records one")
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    choices, record = live_run_module.plan(_ProbeService([backend]), args)
    live_run_module.evaluate(choices, record)
    entries = [
        ("backends", record["backends"]["viable"]),
        ("system_inventory", record["system_inventory"]["viable"]),
        *((f"group {group['group']}", group) for group in record["groups"]),
    ]
    for label, entry in entries:
        faults = live_run_module.backend_identity_violations(entry)
        recorded = {key: entry.get(key) for key in live_run_module.BACKEND_IDENTITY_FIELDS}
        if faults or recorded != expected:
            raise RuntimeError(f"{label} records identity {recorded}: {faults}")
    for fault in (
        {"backend_version": ""},
        {"backend_version": 128},
        {"processor_type": {"family": "Heron"}},
        {"processor_type": {"family": "Heron", "revision": 2}},
    ):
        if not live_run_module.backend_identity_violations(fault):
            raise RuntimeError(f"malformed identity {fault} passes the shape check")
    if live_run_module.backend_identity_violations({"calibration": "older record"}):
        raise RuntimeError("a record without the identity fields fails the shape check")
    start = datetime(2026, 10, 10, tzinfo=UTC)
    unreported = live_run_module.execution_identity(object(), {start: object()})
    if unreported != {
        "backend_version": None,
        "processor_type": None,
        "backend_version_at_execution": {start.isoformat(): None},
    }:
        raise RuntimeError(f"a backend reporting no identity stops or fabricates collection identity: {unreported}")
    for name in live_run_module.APPROVED_RECORD_FIELDS:
        if any(key in json.dumps(record.get(name)) for key in live_run_module.BACKEND_IDENTITY_FIELDS):
            raise RuntimeError(f"approved-record field {name} carries backend identity")
    with tempfile.TemporaryDirectory(prefix="gororoba-backend-identity-") as directory:
        approved_dir = Path(directory)
        write_archive(approved_dir, choices)
        write_json(approved_dir, record)
        qpy_digest = hashlib.sha256((approved_dir / "isa.qpy").read_bytes()).hexdigest()
        upgraded = copy.deepcopy(record)
        for entry in (upgraded["backends"]["viable"], upgraded["system_inventory"]["viable"], *upgraded["groups"]):
            entry |= {"backend_version": "9.9.9", "processor_type": {"family": "Heron", "revision": "3"}}
        mismatches = live_run_module.approved_record_mismatches(approved_dir, upgraded, qpy_digest)
        if mismatches:
            raise RuntimeError(f"a backend version change refuses the approved record: {mismatches}")


class _VersionedProbeBackend(_ProbeBackend):
    """A probe backend whose configuration reports the backend_version the contract sets."""

    def __init__(self, name: str, backend: FakeFez, version: str):
        super().__init__(name, backend)
        self.version = version

    def configuration(self) -> Any:
        configuration = super().configuration()
        configuration.backend_version = self.version
        return configuration


class _QuotaProbeService(_ProbeService):
    """A probe service reporting a fixed remaining quota, which unchanged_since_planning compares."""

    def __init__(self, backends: list[_ProbeBackend], remaining_seconds: float | None):
        super().__init__(backends)
        self.remaining_seconds = remaining_seconds

    def usage(self) -> dict[str, Any]:
        return {"usage_limit_reached": False, "usage_remaining_seconds": self.remaining_seconds}


def _verify_submit_refreshes_backend_identity() -> None:
    """A backend_version bump between plan and approved submit lands in the submitted record's provenance.

    A fixed quota reuses the plan (unchanged_since_planning) and an unreported
    quota rebuilds it without reselection; on both paths the approval holds,
    the batch runs, and backends, system_inventory and every group carry the
    version the refresh read.
    """
    for remaining, rebuilt in ((500.0, False), (None, True)):
        _submit_after_version_bump(remaining, rebuilt)


def _submit_after_version_bump(remaining: float | None, rebuilt: bool) -> None:
    """Plan at backend_version 1.0.0, bump it to 9.9.9, and submit against the approved plan."""
    backend = _VersionedProbeBackend("viable", FakeFez(), "1.0.0")
    service = _QuotaProbeService([backend], remaining)
    args = _fixture_args(groups=["hybrid_shor_mod15"])
    choices, record = live_run_module.plan(service, args)
    live_run_module.evaluate(choices, record)
    planned_identity = live_run_module.backend_identity(backend)
    runs: list[int] = []

    def probe_sampler(
        backend: Any,
        kind: str,
        twirl: bool,
        dd: str | None,
        tags: list[str],
        shots: int = 4096,
        max_execution_seconds: int | None = None,
        *,
        rep_delay: float | None = None,
    ) -> Any:
        del backend, twirl, dd
        return _ProbeSampler(
            kind, tags, shots, lambda circuits: runs.append(len(circuits)), None, max_execution_seconds
        )

    with tempfile.TemporaryDirectory(prefix="gororoba-identity-refresh-") as directory:
        approved_dir, run_dir = Path(directory) / "approved", Path(directory) / "run"
        approved_dir.mkdir()
        run_dir.mkdir()
        write_archive(approved_dir, choices)
        write_json(approved_dir, record)
        args.approved_record = approved_dir
        args.approved_record_sha256 = hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest()
        backend.version = "9.9.9"
        submitted = copy.deepcopy(record)
        with patch.object(live_run_module, "configure_sampler", probe_sampler), redirect_stdout(io.StringIO()):
            live_run_module.submit(
                service, list(choices), args, submitted, lambda: write_archive(run_dir, choices), lambda: None
            )
    label = "rebuilt" if rebuilt else "reused"
    if (
        not runs
        or submitted["state"] == "approval_required"
        or submitted["revalidation"][-1]["rebuilt"] is not rebuilt
        or submitted["approved_record"]["mismatches"]
    ):
        raise RuntimeError(f"{label} plan: a backend version bump changes the submission: {submitted['state']}")
    if record["backends"]["viable"]["backend_version"] != "1.0.0":
        raise RuntimeError(f"{label} plan records {record['backends']['viable']['backend_version']} at planning")
    entries = [
        ("backends", submitted["backends"]["viable"]),
        ("system_inventory", submitted["system_inventory"]["viable"]),
        *((f"group {group['group']}", group) for group in submitted["groups"]),
    ]
    for name, entry in entries:
        recorded = {key: entry.get(key) for key in live_run_module.BACKEND_IDENTITY_FIELDS}
        if recorded != planned_identity | {"backend_version": "9.9.9"}:
            raise RuntimeError(f"{label} plan: submitted {name} keeps identity {recorded}")


CONTRACT_CASES: dict[str, Callable[[], None]] = {
    "dynamic_classification": _verify_dynamic_classification,
    "dynamic_mitigation_boundaries": _verify_dynamic_mitigation_boundaries,
    "scheduler_timing_cases": _verify_scheduler_timing_cases,
    "feed_forward_structure": _verify_feed_forward_structure,
    "job_usage_cases": _verify_job_usage_cases,
    "packing_equivalence": _verify_packing_equivalence,
    "usage_wait": _verify_usage_wait,
    "approved_record_gate": _verify_approved_record_gate,
    "approval_calibration_values": _verify_approval_calibration_values,
    "instance_and_ceiling": _verify_instance_and_ceiling,
    "raw_scrubbing": _verify_raw_scrubbing,
    "nested_operations": _verify_nested_operations,
    "result_register_order": _verify_result_register_order,
    "twirling_shot_contract": _verify_twirling_shot_contract,
    "capability_admission": _verify_capability_admission,
    "discovered_capabilities": _verify_discovered_capabilities,
    "target_and_bad_qubit_status": _verify_target_and_bad_qubit_status,
    "snapshot_and_fingerprint_coherence": _verify_snapshot_and_fingerprint_coherence,
    "pub_fusion_contracts": _verify_pub_fusion_contracts,
    "worker_quota": _verify_worker_quota,
    "unchanged_since_planning": _verify_unchanged_since_planning,
    "backend_identity_records": _verify_backend_identity_records,
    "submit_refreshes_backend_identity": _verify_submit_refreshes_backend_identity,
    "replay_seed_independence": _verify_replay_seed_independence,
    "fused_collection": _verify_fused_collection,
    "joint_fusion_placement": _verify_joint_fusion_placement,
    "joint_fusion_candidate_backtracking": _verify_joint_fusion_candidate_backtracking,
    "required_placement_backtracking": _verify_required_placement_backtracking,
    "buffer_scope": _verify_buffer_scope,
    "placement_duplicate_branch_order": _verify_placement_duplicate_branch_order,
    "static_placement_judge": _verify_static_placement_judge,
    "schema_lifecycle": _verify_schema_lifecycle,
    "schema_discrimination": _verify_schema_discrimination,
    "every_job_revalidates": _verify_every_job_revalidates,
    "live_reselection": _verify_live_reselection,
    "discovery_failure_isolation": _verify_discovery_failure_isolation,
    "approved_backend_scope": _verify_approved_backend_scope,
    "operator_qubit_exclusion": _verify_operator_qubit_exclusion,
    "compile_panic_isolation": _verify_compile_panic_isolation,
    "fragmented_target_layout": _verify_fragmented_target_layout,
    "packed_replica_split": _verify_packed_replica_split,
    "packing_global_phase": _verify_packing_global_phase,
    "packed_static_stays_static": _verify_packed_static_stays_static,
    "rate_keys": _verify_rate_keys,
    "replica_floor_resolution": _verify_replica_floor_resolution,
    "experiment_source_manifest": _verify_experiment_source_manifest,
}


def _run_contract_case(name: str) -> str:
    """Dispatch only registered contracts in an isolated process or the serial caller."""
    try:
        contract = CONTRACT_CASES[name]
    except KeyError as error:
        raise ValueError(f"unknown runtime contract case: {name!r}") from error
    # The outer case pool owns CPU concurrency; nested placement and replay
    # maps run serially inside each case to keep the total worker count bounded.
    with patch.dict(os.environ, {"GOROROBA_WORKERS": "1"}):
        contract()
    return name


def _verify(case_names: list[str] | None = None) -> None:
    names = list(CONTRACT_CASES) if case_names is None else case_names
    completed = parallel.ordered_map(_run_contract_case, names, min_items=2)
    if case_names is not None:
        for name in completed:
            print(f"runtime contract {name}: pass")
        return
    print(
        "runtime contracts: discovery, direct pinned lookup, capability admission, "
        "bounded-angle isolation, coherent snapshots, Target routing, joint placement, "
        "cross-group PUB fusion, renewed approval, approved backend scope, operator exclusion, job revalidation, "
        "schema lifecycle, "
        "recovery, result order, rate keys, scheduler timing, job usage, and digest pass"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--list-cases", action="store_true", help="print the ordered contract names as JSON")
    selection.add_argument(
        "--case", action="append", choices=tuple(CONTRACT_CASES), help="run a named contract; repeat to select more"
    )
    args = parser.parse_args()
    if args.list_cases:
        print(json.dumps(list(CONTRACT_CASES)))
        return
    _verify(args.case)


if __name__ == "__main__":
    main()

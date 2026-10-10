"""Discover live systems, adapt packed circuits, simulate, and submit safely.

Each plan refreshes every requested backend once, derives logical requirements
from the source circuits, removes degraded qubits and CZ couplers from the
routing Target, and validates every routed instruction against the original
fresh Target. Seeded candidates rank by gate, readout, duration, and coherence
calibration. The winner is placed as disjoint replicas; each packed member and
optional isolated crosstalk reference then receives final Target validation.

An explicit `--replica-floor` governs every group; otherwise each group's
declared floor applies, with 0.9 as the default. Before submission, the runner
repeats discovery and deterministic selection across all viable systems. Any
change to the approved backend, layout, replica placement, execution circuits,
capabilities, or used calibration values rewrites the submit-free plan and
stops for a renewed written case and user approval. An unchanged plan is
partitioned into whole static or dynamic client-side Sampler jobs under the
backend's client-reported compatibility bound. Every batch receives another
hardware refresh. The QPY digest, complete ledger, effective options, recovery
tags, attempt marker, and returned job identifier reach durable storage in that
order. Collection verifies the ledger and archive, recovers response-lost job
identifiers, and replays each replica under its execution-time calibration.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import ControlFlowOp
from qiskit.converters import circuit_to_dag
from qiskit.exceptions import QiskitError
from qiskit.providers import BackendV2, Options
from qiskit.transpiler import Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.executor_sampler import Sampler

import packing
import variance
from experiments import MIRROR_SUFFIX, Group, Member, experiment_groups, tvd
from packing import Replica

SHOTS = 4096
# Mirror rescaling divides two noisy <Z> estimates; at 4096 shots their
# attenuation difference is only about two standard deviations, so ODR values
# are reported only from runs of at least this many shots
# (literature/notes/2507.08088.md, action item 2).
ODR_MIN_SHOTS = 16384
TWIRLING_RANDOMIZATIONS = 32
TWIRLING_MIN_SHOTS_PER_RANDOMIZATION = 64
OPT_LEVEL = 3
SEED_TRANSPILER = 20261010
SEED_SIMULATOR = 20261011
JOINT_CANDIDATES = 3
DEFAULT_SEEDS = 8
DEFAULT_MAX_PENDING = 25
DEFAULT_MIN_REMAINING_S = 60.0
RECORD_SCHEMA_VERSION = 4
RECORD_SCHEMA_CONTRACT = "live-target-packed-replicas-v1"
CONTROL_FLOW_OPERATIONS = frozenset({"if_else", "while_loop", "for_loop", "switch_case", "break_loop", "continue_loop"})
DIRECT_TARGET_OPERATIONS = CONTROL_FLOW_OPERATIONS | {"delay", "measure", "reset", "store"}
# A replica is placed only while its layout score stays at least this fraction
# of the best placement's, so packing fills the device with near-best hardware.
DEFAULT_REPLICA_FLOOR = 0.9
# The unpacked copy of a group's primary member on replica 0's qubits; its
# difference from packed replica 0 measures crosstalk from the other replicas.
ISOLATED_SUFFIX = "_isolated"

EXPERIMENT_SOURCE_MANIFEST = (
    "boolean_anf.py",
    "cd_core.py",
    "designs.py",
    "experiments.py",
    "factoring.py",
    "live_run.py",
    "modular_arithmetic.py",
    "order_finding.py",
    "packing.py",
    "predict.py",
    "select_lcu.py",
    "variance.py",
)

# Exclusion policy: values outside these bounds mark degraded hardware that the
# backend may report without a faulty flag. Missing T1 or T2 also excludes.
QUALITY = {"max_readout_error": 0.08, "max_cz_error": 0.03, "max_sx_error": 0.01, "min_t1_us": 20.0, "min_t2_us": 20.0}


class LiveRunError(RuntimeError):
    """A live check failed: stale or mismatched calibration, policy, or budget."""


@dataclass(frozen=True)
class BackendCapabilities:
    """Submission-relevant capabilities read from one freshly refreshed backend."""

    num_qubits: int
    max_circuits: int | None
    dynamic_circuits: bool
    operation_names: tuple[str, ...]
    control_flow: tuple[str, ...]

    @property
    def native_cz(self) -> bool:
        return "cz" in self.operation_names

    def summary(self) -> dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
            "max_circuits": self.max_circuits,
            "dynamic_circuits": self.dynamic_circuits,
            "operation_names": list(self.operation_names),
            "control_flow": list(self.control_flow),
        }


@dataclass(frozen=True)
class CircuitRequirements:
    """Hardware capabilities needed by every source circuit in one experiment group."""

    qubits: int
    classical_bits: int
    static_circuits: int
    dynamic_circuits: int
    target_operations: tuple[str, ...]
    control_flow: tuple[str, ...]

    def summary(self) -> dict[str, Any]:
        return {
            "qubits": self.qubits,
            "classical_bits": self.classical_bits,
            "static_circuits": self.static_circuits,
            "dynamic_circuits": self.dynamic_circuits,
            "target_operations": list(self.target_operations),
            "control_flow": list(self.control_flow),
        }


@dataclass
class Snapshot:
    backend: Any
    properties: Any
    name: str
    operational: bool
    status_msg: str
    pending_jobs: int
    calibration: str
    fetched_at: str
    capabilities: BackendCapabilities
    excluded_qubits: dict[int, str] = field(default_factory=dict)
    excluded_edges: dict[tuple[int, int], str] = field(default_factory=dict)
    medians: dict[str, float | None] = field(default_factory=dict)
    admission_target: Target | None = field(default=None, repr=False)

    def ineligible_reason(self, max_pending: int | None) -> str | None:
        if not self.capabilities.native_cz:
            return "no native cz instruction; the exclusion policy and compiles assume CZ"
        if not self.operational or self.status_msg != "active":
            return f"status operational={self.operational} msg={self.status_msg!r}"
        if max_pending is not None and self.pending_jobs > max_pending:
            return f"{self.pending_jobs} pending jobs exceeds --max-pending {max_pending}"
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "operational": self.operational,
            "status_msg": self.status_msg,
            "pending_jobs": self.pending_jobs,
            "calibration": self.calibration,
            "fetched_at": self.fetched_at,
            "capabilities": self.capabilities.summary(),
            "medians": self.medians,
            "excluded_qubits": {str(q): r for q, r in sorted(self.excluded_qubits.items())},
            "excluded_edges": {f"{a}-{b}": r for (a, b), r in sorted(self.excluded_edges.items())},
        }


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _backend_capabilities(backend: Any) -> BackendCapabilities:
    operation_names = tuple(sorted(str(name) for name in backend.target.operation_names))
    supported_features = getattr(backend.configuration(), "supported_features", [])
    return BackendCapabilities(
        num_qubits=int(backend.num_qubits),
        max_circuits=int(backend.max_circuits) if backend.max_circuits is not None else None,
        dynamic_circuits="dynamic_circuits" in supported_features,
        operation_names=operation_names,
        control_flow=tuple(sorted(CONTROL_FLOW_OPERATIONS.intersection(operation_names))),
    )


def take_snapshot(service: QiskitRuntimeService, name: str) -> Snapshot:
    """Fresh status, Target, and properties for one backend, with the exclusion policy applied."""
    try:
        backend = service.backend(name)
    except Exception as error:
        raise LiveRunError(f"{name}: backend lookup failed ({type(error).__name__})") from error
    try:
        backend.refresh()
    except Exception as error:
        raise LiveRunError(f"{name}: backend refresh failed ({type(error).__name__})") from error
    try:
        # IBMBackend.refresh() refreshes properties and rebuilds the Target from
        # that same property object. A second refresh here can replace only the
        # cached properties and create a cross-calibration snapshot.
        props = backend.properties()
    except Exception as error:
        raise LiveRunError(f"{name}: backend properties failed ({type(error).__name__})") from error
    if props is None:
        raise LiveRunError(f"{name}: backend properties are unavailable")
    try:
        status = backend.status()
    except Exception as error:
        raise LiveRunError(f"{name}: backend status failed ({type(error).__name__})") from error
    try:
        capabilities = _backend_capabilities(backend)
    except Exception as error:
        raise LiveRunError(f"{name}: backend capability read failed ({type(error).__name__})") from error
    try:
        check_snapshot_matches_properties(backend.target, props, name)
    except LiveRunError:
        raise
    except Exception as error:
        raise LiveRunError(f"{name}: target/property coherence check failed ({type(error).__name__})") from error
    snap = Snapshot(
        backend=backend,
        properties=props,
        name=backend.name,
        operational=bool(status.operational),
        status_msg=str(status.status_msg),
        pending_jobs=int(status.pending_jobs),
        calibration=props.last_update_date.isoformat(),
        fetched_at=_now(),
        capabilities=capabilities,
    )
    if "cz" not in backend.target.operation_names:
        return snap
    faulty_q = set(props.faulty_qubits())
    faulty_edges = {tuple(g.qubits) for g in props.faulty_gates() if g.gate == "cz"}
    # A faulty single-qubit instruction (sx, x, measure) on an operational
    # qubit still makes that qubit unusable for these circuits.
    faulty_gate_q = {q: g.gate for g in props.faulty_gates() if g.gate != "cz" for q in g.qubits}
    t1s, t2s, ros, czs = [], [], [], []
    for q in range(backend.num_qubits):
        reason = f"faulty {faulty_gate_q[q]}" if q in faulty_gate_q else _qubit_reason(props, q, faulty_q)
        if reason:
            snap.excluded_qubits[q] = reason
        else:
            t1s.append(props.t1(q) * 1e6)
            t2s.append(props.t2(q) * 1e6)
            ros.append(props.readout_error(q))
    for qargs, inst in backend.target["cz"].items():
        err = inst.error if inst is not None else None
        edge = (qargs[0], qargs[1])
        if edge in faulty_edges or tuple(reversed(edge)) in faulty_edges:
            snap.excluded_edges[edge] = "faulty"
        elif err is None or err > QUALITY["max_cz_error"]:
            snap.excluded_edges[edge] = f"cz error {err}"
        else:
            czs.append(err)
    snap.medians = {
        "t1_us": float(np.median(t1s)) if t1s else None,
        "t2_us": float(np.median(t2s)) if t2s else None,
        "readout_error": float(np.median(ros)) if ros else None,
        "cz_error": float(np.median(czs)) if czs else None,
    }
    return snap


def _qubit_reason(props: Any, q: int, faulty: set[int]) -> str | None:
    if q in faulty:
        return "faulty"
    if not props.is_qubit_operational(q):
        return "not operational"
    try:
        t1, t2, ro = props.t1(q) * 1e6, props.t2(q) * 1e6, props.readout_error(q)
        sx = props.gate_error("sx", q)
    except Exception as exc:  # BackendPropertyError for a missing parameter
        return f"missing calibration: {exc}"
    if t1 < QUALITY["min_t1_us"] or t2 < QUALITY["min_t2_us"]:
        return f"T1={t1:.1f}us T2={t2:.1f}us"
    if ro > QUALITY["max_readout_error"]:
        return f"readout error {ro:.3f}"
    if sx > QUALITY["max_sx_error"]:
        return f"sx error {sx:.4f}"
    return None


def _qargs(circuit: QuantumCircuit, instruction: Any) -> tuple[int, ...]:
    return tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)


def _ops(isa: QuantumCircuit) -> list[tuple[str, tuple[int, ...]]]:
    """Return every possible physical operation, including nested control-flow blocks."""
    operations: list[tuple[str, tuple[int, ...]]] = []

    def walk(circuit: QuantumCircuit, physical_qubits: tuple[int, ...]) -> None:
        for instruction in circuit.data:
            local_indices = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
            mapped = tuple(physical_qubits[index] for index in local_indices)
            if isinstance(instruction.operation, ControlFlowOp):
                for block in instruction.operation.blocks:
                    if block.num_qubits != len(mapped):
                        raise LiveRunError(
                            f"{isa.name}: control-flow block has {block.num_qubits} qubits, expected {len(mapped)}"
                        )
                    walk(block, mapped)
            elif instruction.operation.name not in ("barrier", "delay"):
                operations.append((instruction.operation.name, mapped))

    walk(isa, tuple(range(isa.num_qubits)))
    return operations


def _source_operation_names(circuit: QuantumCircuit) -> set[str]:
    """Operation names in a logical circuit and every nested control-flow block."""
    names: set[str] = set()

    def walk(current: QuantumCircuit) -> None:
        for instruction in current.data:
            names.add(instruction.operation.name)
            if isinstance(instruction.operation, ControlFlowOp):
                for block in instruction.operation.blocks:
                    walk(block)

    walk(circuit)
    return names


def group_requirements(group: Group) -> CircuitRequirements:
    """Derive the backend-facing requirements from circuits built for this run."""
    qubits = max(member.circuit.num_qubits for member in group.members)
    classical_bits = max(member.circuit.num_clbits for member in group.members)
    operation_names: set[str] = set()
    static_circuits = 0
    dynamic_circuits = 0
    for member in group.members:
        operation_names.update(_source_operation_names(member.circuit))
        circuit_count = 1 + int(member.mirror)
        if _is_dynamic(member.circuit):
            dynamic_circuits += circuit_count
        else:
            static_circuits += circuit_count
    direct = tuple(sorted(operation_names.intersection(DIRECT_TARGET_OPERATIONS)))
    control_flow = tuple(sorted(operation_names.intersection(CONTROL_FLOW_OPERATIONS)))
    return CircuitRequirements(qubits, classical_bits, static_circuits, dynamic_circuits, direct, control_flow)


def _interaction_width(circuit: QuantumCircuit) -> int:
    """Largest connected logical component induced by multi-qubit operations."""
    neighbors: list[set[int]] = [set() for _ in range(circuit.num_qubits)]

    def walk(current: QuantumCircuit, parent_qubits: tuple[int, ...]) -> None:
        for instruction in current.data:
            local_indices = tuple(current.find_bit(qubit).index for qubit in instruction.qubits)
            mapped = tuple(parent_qubits[index] for index in local_indices)
            if isinstance(instruction.operation, ControlFlowOp):
                for block in instruction.operation.blocks:
                    walk(block, mapped)
            elif len(mapped) > 1:
                root = mapped[0]
                for other in mapped[1:]:
                    neighbors[root].add(other)
                    neighbors[other].add(root)

    walk(circuit, tuple(range(circuit.num_qubits)))
    largest = 0
    unseen = set(range(circuit.num_qubits))
    while unseen:
        pending = [unseen.pop()]
        size = 0
        while pending:
            qubit = pending.pop()
            size += 1
            adjacent = neighbors[qubit].intersection(unseen)
            unseen.difference_update(adjacent)
            pending.extend(adjacent)
        largest = max(largest, size)
    return largest


def _healthy_cz_width(snapshot: Snapshot) -> tuple[int, int]:
    """Count admitted qubits and the largest connected admitted CZ component."""
    healthy = set(range(snapshot.capabilities.num_qubits)) - set(snapshot.excluded_qubits)
    neighbors: dict[int, set[int]] = {qubit: set() for qubit in healthy}
    if "cz" in snapshot.backend.target.operation_names:
        for qargs in snapshot.backend.target["cz"]:
            if any(qubit not in healthy for qubit in qargs):
                continue
            if qargs in snapshot.excluded_edges or tuple(reversed(qargs)) in snapshot.excluded_edges:
                continue
            first, second = qargs
            neighbors[first].add(second)
            neighbors[second].add(first)
    largest = 0
    unseen = set(healthy)
    while unseen:
        pending = [unseen.pop()]
        size = 0
        while pending:
            qubit = pending.pop()
            size += 1
            adjacent = neighbors[qubit].intersection(unseen)
            unseen.difference_update(adjacent)
            pending.extend(adjacent)
        largest = max(largest, size)
    return len(healthy), largest


def routing_admission_violations(group: Group, snapshot: Snapshot) -> list[str]:
    """Reject a snapshot whose admitted hardware cannot host a group's interaction graph."""
    if snapshot.backend.target.has_angle_bounds():
        return ["bounded-angle Target cannot be filtered without widening its parameter bounds"]
    healthy_qubits, healthy_cz_width = _healthy_cz_width(snapshot)
    requirements = group_requirements(group)
    violations = []
    if requirements.qubits > healthy_qubits:
        violations.append(f"needs {requirements.qubits} qubits; quality policy admits {healthy_qubits}")
    interaction_width = max(_interaction_width(member.circuit) for member in group.members)
    if interaction_width > healthy_cz_width:
        violations.append(
            f"needs a connected {interaction_width}-qubit interaction region; "
            f"quality policy admits at most {healthy_cz_width}"
        )
    return violations


def capability_violations(requirements: CircuitRequirements, capabilities: BackendCapabilities) -> list[str]:
    """Return explicit reasons a backend cannot host one source-circuit group."""
    violations = []
    if requirements.static_circuits and requirements.dynamic_circuits:
        violations.append("one result group mixes static and dynamic circuits")
    if requirements.qubits > capabilities.num_qubits:
        violations.append(f"needs {requirements.qubits} qubits; backend has {capabilities.num_qubits}")
    missing = sorted(set(requirements.target_operations) - set(capabilities.operation_names))
    if missing:
        violations.append(f"missing target operations {missing}")
    if requirements.dynamic_circuits and not capabilities.dynamic_circuits:
        violations.append("service dynamic-circuit filter rejects backend")
    largest_batch = max(requirements.static_circuits, requirements.dynamic_circuits)
    if capabilities.max_circuits is not None and largest_batch > capabilities.max_circuits:
        violations.append(
            f"group needs at least {largest_batch} circuits in one result-complete batch; "
            "client-reported max_circuits compatibility bound is "
            f"{capabilities.max_circuits}"
        )
    return violations


def target_violations(isa: QuantumCircuit, target: Any) -> list[str]:
    """Return ISA instructions that the refreshed Target does not support on their physical qubits."""
    violations: list[str] = []

    def walk(circuit: QuantumCircuit, physical_qubits: tuple[int, ...]) -> None:
        for instruction in circuit.data:
            operation = instruction.operation
            local_indices = tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits)
            mapped = tuple(physical_qubits[index] for index in local_indices)
            if operation.name != "barrier" and not target.instruction_supported(
                operation_name=operation.name, qargs=mapped, parameters=operation.params
            ):
                violations.append(f"target lacks {operation.name}{mapped}")
            if isinstance(operation, ControlFlowOp):
                for block in operation.blocks:
                    if block.num_qubits != len(mapped):
                        violations.append(
                            f"{operation.name}{mapped} block has {block.num_qubits} qubits, expected {len(mapped)}"
                        )
                    else:
                        walk(block, mapped)

    walk(isa, tuple(range(isa.num_qubits)))
    return sorted(set(violations))


def esp(isa: QuantumCircuit, target: Any) -> float:
    """Product of (1 - error) over every gate and measurement of isa, from target."""
    log_p = 0.0
    for name, qargs in _ops(isa):
        props = target[name].get(qargs) if name in target.operation_names else None
        err = props.error if props is not None and props.error is not None else 0.0
        log_p += math.log1p(-min(err, 1.0 - 1e-15))
    return math.exp(log_p)


def _violations(isa: QuantumCircuit, snap: Snapshot) -> list[str]:
    bad = []
    for name, qargs in _ops(isa):
        bad += [f"qubit {q}" for q in qargs if q in snap.excluded_qubits]
        if name == "cz" and (qargs in snap.excluded_edges or tuple(reversed(qargs)) in snap.excluded_edges):
            bad.append(f"edge {qargs}")
    return sorted(set(bad))


def compiled_violations(isa: QuantumCircuit, snap: Snapshot) -> list[str]:
    """Threshold, fault, and exact Target violations for one transpiled circuit."""
    return sorted(set(_violations(isa, snap) + target_violations(isa, snap.backend.target)))


CALIBRATED = ("cz", "sx", "x", "measure")


def _property_values(name: str, qargs: tuple[int, ...], props: Any) -> dict[str, float]:
    """Error and duration of one calibrated instruction, read from the properties."""
    if name == "measure":
        return {"error": props.readout_error(qargs[0]), "duration": props.readout_length(qargs[0])}
    gate_qubits: Any = list(qargs) if len(qargs) > 1 else qargs[0]
    return {"error": props.gate_error(name, gate_qubits), "duration": props.gate_length(name, gate_qubits)}


def fingerprint(isas: list[QuantumCircuit], target: Any, props: Any) -> dict[str, Any]:
    """Calibration values the plan depends on for every routed instruction.

    The layout score and noise model read Target instruction properties and
    qubit coherence. The readout correction reads asymmetric fields from
    BackendProperties. A change to any consumed value moves the plan, including
    reset and identity properties that BackendProperties may not expose.
    """
    concurrent_measurements = target.concurrent_measurements
    out: dict[str, Any] = {
        "target:dt": target.dt,
        "target:granularity": target.granularity,
        "target:min_length": target.min_length,
        "target:pulse_alignment": target.pulse_alignment,
        "target:acquire_alignment": target.acquire_alignment,
        "target:concurrent_measurements": (
            tuple(tuple(group) for group in concurrent_measurements) if concurrent_measurements is not None else None
        ),
    }
    for isa in isas:
        for name, qargs in _ops(isa):
            for q in qargs:
                qubit_properties = target.qubit_properties[q]
                out[f"target:t1:{q}"] = qubit_properties.t1
                out[f"target:t2:{q}"] = qubit_properties.t2
            instruction_properties = target[name].get(qargs) if name in target.operation_names else None
            out[f"target:{name}{qargs}:error"] = (
                instruction_properties.error if instruction_properties is not None else None
            )
            out[f"target:{name}{qargs}:duration"] = (
                instruction_properties.duration if instruction_properties is not None else None
            )
            if name == "measure":
                # readout_corrected reads the asymmetric channel, which can move
                # while the aggregate readout_error holds.
                e10, e01 = readout_flips(props, qargs[0])
                out[f"e10:{qargs[0]}"], out[f"e01:{qargs[0]}"] = e10, e01
    return out


def _same_optional_float(first: Any, second: Any) -> bool:
    if first is None or second is None:
        return first is second
    return math.isclose(float(first), float(second), rel_tol=1e-9, abs_tol=1e-15)


def check_snapshot_matches_properties(target: Any, props: Any, label: str) -> None:
    """Prove that a refreshed Target and its cached properties describe one calibration."""
    for qubit, target_qubit in enumerate(target.qubit_properties):
        available = {parameter.name for parameter in props.qubits[qubit]}
        for field_name, target_value, property_value in (
            ("t1", target_qubit.t1, props.t1(qubit) if "T1" in available else None),
            ("t2", target_qubit.t2, props.t2(qubit) if "T2" in available else None),
        ):
            if not _same_optional_float(target_value, property_value):
                raise LiveRunError(
                    f"{label} qubit {qubit} {field_name}: target {target_value} vs properties {property_value}"
                )

    property_gates = {
        (gate.gate, tuple(gate.qubits)): {parameter.name: parameter.value for parameter in gate.parameters}
        for gate in props.gates
    }
    for operation_name in target.operation_names:
        for qargs, instruction_properties in target[operation_name].items():
            if qargs is None or instruction_properties is None:
                continue
            if operation_name == "measure":
                available = {parameter.name for parameter in props.qubits[qargs[0]]}
                values = {
                    "error": props.readout_error(qargs[0]) if "readout_error" in available else None,
                    "duration": props.readout_length(qargs[0]) if "readout_length" in available else None,
                }
            else:
                gate_values = property_gates.get((operation_name, qargs), {})
                gate_qubits: Any = list(qargs) if len(qargs) > 1 else qargs[0]
                values = {}
                if "gate_error" in gate_values:
                    values["error"] = props.gate_error(operation_name, gate_qubits)
                if "gate_length" in gate_values:
                    values["duration"] = props.gate_length(operation_name, gate_qubits)
            for field_name, property_value in values.items():
                target_value = getattr(instruction_properties, field_name)
                if not _same_optional_float(target_value, property_value):
                    raise LiveRunError(
                        f"{label} {operation_name}{qargs} {field_name}: "
                        f"target {target_value} vs properties {property_value}"
                    )


def readout_flips(props: Any, q: int) -> tuple[float, float]:
    """(e10, e01) = (prob_meas1_prep0, prob_meas0_prep1) of qubit q, or readout_error for both.

    The noise model, the readout correction, and the fingerprint all read the
    channel here, so a backend that omits the asymmetric fields gets the same
    symmetric fallback in each.
    """
    try:
        return props.qubit_property(q, "prob_meas1_prep0")[0], props.qubit_property(q, "prob_meas0_prep1")[0]
    except Exception:  # BackendPropertyError: asymmetric fields absent for this qubit
        error = props.readout_error(q)
        return error, error


def check_target_matches_properties(isas: list[QuantumCircuit], target: Any, props: Any, label: str) -> None:
    """The Target that scores and noise read and the properties agree on every qubit and edge of isas.

    Errors and durations of every CZ, sx, x, and measurement, and T1 and T2 of
    every touched qubit, must match, which proves both views come from one
    calibration fetch: the ESP ranking reads errors, and the noise model reads
    errors, durations, and T1/T2 from the Target.
    """
    for isa in isas:
        for name, qargs in _ops(isa):
            pairs: list[tuple[str, Any, float]] = []
            if name in CALIBRATED:
                inst = target[name][qargs]
                values = _property_values(name, qargs, props)
                pairs += [("error", inst.error, values["error"]), ("duration", inst.duration, values["duration"])]
            for q in qargs:
                qp = target.qubit_properties[q]
                pairs += [("t1", qp.t1, props.t1(q)), ("t2", qp.t2, props.t2(q))]
            for field_name, t_val, p_val in pairs:
                if t_val is None or not math.isclose(t_val, p_val, rel_tol=1e-9, abs_tol=1e-15):
                    raise LiveRunError(f"{label} {name}{qargs} {field_name}: target {t_val} vs properties {p_val}")


@dataclass
class Entry:
    """One PUB: the single-copy compiled base, its ideal, the packed circuit that runs, and its replicas.

    replicas holds the single-replica circuits split from packed, in replica
    order, each carrying only its own registers; simulation, readout
    correction, and replay run on them, never on the packed width.
    """

    name: str
    base: QuantumCircuit
    ideal: np.ndarray
    packed: QuantumCircuit
    replicas: list[QuantumCircuit]
    prefixes: list[str]
    replica_qubits: list[list[int]]
    reference: bool = False
    weights: np.ndarray | None = None


@dataclass(frozen=True)
class ReplicaPolicy:
    floor: float | None = None
    max_replicas: int | None = None
    isolated_reference: bool = True


@dataclass
class Choice:
    """The winning compile of a group, its replica placements, and its PUB entries."""

    group: Group
    snap: Snapshot
    seed: int
    layout: list[int]
    isas: list[QuantumCircuit]
    member_scores: list[float]
    joint_score: float
    entries: list[Entry] = field(default_factory=list)
    replicas: list[Replica] = field(default_factory=list)
    replica_floor: float = DEFAULT_REPLICA_FLOOR


def build_admission_target(snapshot: Snapshot) -> Target:
    """Copy the fresh Target while removing every excluded qubit and coupler.

    The transpiler sees the same instruction properties used for scoring, but
    its layout and routing passes cannot place work on hardware rejected by the
    live quality policy. Global control-flow instructions remain global.
    """
    source = snapshot.backend.target
    if source.has_angle_bounds():
        raise LiveRunError(f"{snapshot.name}: bounded-angle Target cannot be filtered without widening its bounds")
    concurrent_measurements = source.concurrent_measurements
    if concurrent_measurements is not None:
        concurrent_measurements = [
            [qubit for qubit in group if qubit not in snapshot.excluded_qubits] for group in concurrent_measurements
        ]
        concurrent_measurements = [group for group in concurrent_measurements if group]
    admitted = Target(
        description=source.description,
        num_qubits=source.num_qubits,
        dt=source.dt,
        granularity=source.granularity,
        min_length=source.min_length,
        pulse_alignment=source.pulse_alignment,
        acquire_alignment=source.acquire_alignment,
        qubit_properties=source.qubit_properties,
        concurrent_measurements=concurrent_measurements,
    )
    for operation_name in source.operation_names:
        operation = source.operation_from_name(operation_name)
        properties = source[operation_name]
        if None in properties:
            admitted.add_instruction(operation, name=operation_name)
            continue
        allowed = {
            qargs: instruction_properties
            for qargs, instruction_properties in properties.items()
            if not any(qubit in snapshot.excluded_qubits for qubit in qargs)
            and not (
                operation_name == "cz"
                and (qargs in snapshot.excluded_edges or tuple(reversed(qargs)) in snapshot.excluded_edges)
            )
        }
        if allowed:
            admitted.add_instruction(operation, allowed, name=operation_name)
    return admitted


def _compile(qc: QuantumCircuit, snap: Snapshot, seed: int, layout: list[int] | None = None) -> QuantumCircuit:
    if snap.admission_target is None:
        snap.admission_target = build_admission_target(snap)
    return transpile(
        qc,
        backend=snap.backend,
        target=snap.admission_target,
        optimization_level=OPT_LEVEL,
        seed_transpiler=seed,
        initial_layout=layout,
    )


def _bind(isa: QuantumCircuit, member: Member) -> QuantumCircuit:
    return isa.assign_parameters(member.binding) if member.binding else isa


def _gate_time_view(isa: QuantumCircuit) -> QuantumCircuit:
    """isa with each control-flow op replaced by its first block's gates.

    estimate_duration rejects control flow; the view keeps every gate the true
    branch can run and drops the classical feed-forward latency, which the
    Target does not report, so its duration is a lower bound for dynamic
    circuits.
    """
    out = isa.copy_empty_like()
    for inst in isa.data:
        if isinstance(inst.operation, ControlFlowOp):
            body = inst.operation.blocks[0]
            for sub in body.data:
                if sub.clbits:
                    raise LiveRunError(f"{isa.name}: classical operation inside a control-flow block")
                out.append(sub.operation, [inst.qubits[body.find_bit(q).index] for q in sub.qubits])
        else:
            out.append(inst)
    return out


def duration_s(isa: QuantumCircuit, target: Any) -> float:
    return float(_gate_time_view(isa).estimate_duration(target, unit="s"))


def coherence(isa: QuantumCircuit, target: Any) -> float:
    """exp(-T sum_q 1/T2_q) over the qubits isa touches, T its estimated duration.

    ESP counts gate and readout error; this factor charges idle dephasing on the
    chosen qubits for the length of the circuit (literature/notes/2509.18259.md).
    """
    duration = duration_s(isa, target)
    rate = sum(1.0 / target.qubit_properties[q].t2 for q in _physical(isa))
    return math.exp(-duration * rate)


def layout_score(isa: QuantumCircuit, target: Any) -> float:
    return esp(isa, target) * coherence(isa, target)


def mirror_isa(isa: QuantumCircuit, backend: Any, name: str) -> QuantumCircuit:
    """A prefix of isa's dependency layers, a barrier, its inverse, measured as isa measures.

    The cut is the layer near the depth midpoint whose twin best matches the
    witness in both scheduled depth and CZ count, the idle and two-qubit
    exposures whose attenuation the twin measures. The twin runs on isa's
    physical qubits and ideally returns all zeros, so its measured <Z> is the
    attenuation a witness's <Z> is divided by (literature/notes/2507.08088.md,
    Sec. IV A 3). The forward half keeps isa's gates unchanged on the trivial
    layout, and the barrier keeps the halves from cancelling.
    """
    dag = circuit_to_dag(isa.remove_final_measurements(inplace=False))
    layers = [[node for node in layer["graph"].op_nodes() if node.op.name != "barrier"] for layer in dag.layers()]
    total_cz = sum(node.op.name == "cz" for layer in layers for node in layer)
    trivial = list(range(isa.num_qubits))

    def build(cut: int) -> QuantumCircuit:
        half = QuantumCircuit(isa.num_qubits)
        for layer in layers[:cut]:
            for node in layer:
                half.append(node.op, [dag.find_bit(q).index for q in node.qargs])
        # The inverse half is translated with single-qubit merging, so sx
        # inverses do not each expand into a longer chain than the forward half.
        undo = transpile(half.inverse(), backend=backend, optimization_level=1, initial_layout=trivial)
        out = QuantumCircuit(isa.num_qubits, isa.num_clbits, name=name)
        out.compose(half, inplace=True)
        # The barrier spans only the qubits the twin uses, so the untouched
        # qubits of the full-width ISA stay idle from initialization.
        out.barrier(_physical(isa))
        out.compose(undo, inplace=True)
        for inst in isa.data:
            if inst.operation.name == "measure":
                out.measure(isa.find_bit(inst.qubits[0]).index, isa.find_bit(inst.clbits[0]).index)
        return transpile(out, backend=backend, optimization_level=0, initial_layout=trivial)

    def mismatch(twin: QuantumCircuit) -> float:
        depth_err = abs(twin.depth() - isa.depth()) / max(isa.depth(), 1)
        cz_err = abs(twin.count_ops().get("cz", 0) - total_cz) / max(total_cz, 1)
        return max(depth_err, cz_err)

    mid = len(layers) // 2
    candidates = [build(cut) for cut in range(max(mid - 6, 1), min(mid + 7, len(layers)))]
    return min(candidates, key=mismatch)


def replica_floor(group: Group, policy: ReplicaPolicy) -> float:
    """An explicit --replica-floor for every group, else the group's declared floor, else DEFAULT_REPLICA_FLOOR."""
    if policy.floor is not None:
        return policy.floor
    return DEFAULT_REPLICA_FLOOR if group.replica_floor is None else group.replica_floor


def place_replicas(snap: Snapshot, isas: list[QuantumCircuit], floor: float, policy: ReplicaPolicy) -> list[Replica]:
    """Disjoint placements of the group's compiled pattern on snap, best layout score first.

    The pattern is every qubit and CZ edge the group's circuits touch, mirror
    twins included, so one mapping moves every member consistently. A
    placement is admissible when every moved operation exists in the Target
    and avoids excluded qubits and edges; the score is the layout score of the
    moved primary circuit, so ranking reads the same calibration as selection.
    """
    target = snap.backend.target
    if snap.admission_target is None:
        snap.admission_target = build_admission_target(snap)
    base_ops = {op for isa in isas for op in _ops(isa)}
    used, edges = packing.pattern(base_ops)
    graph = packing.coupling_graph(snap.admission_target, snap.backend.num_qubits)

    def admissible(mapping: dict[int, int]) -> bool:
        moved = [packing.relabel(isa, mapping, "") for isa in isas]
        return all(not compiled_violations(isa, snap) for isa in moved)

    def score(mapping: dict[int, int]) -> float:
        return layout_score(packing.relabel(isas[0], mapping, ""), target)

    replicas = packing.place(used, edges, graph, admissible, score, floor, policy.max_replicas)
    if not replicas:
        raise LiveRunError(f"{snap.name}: no admissible placement of the compiled pattern")
    return replicas


def _entry(
    name: str, base: QuantumCircuit, ideal: np.ndarray, replicas: list[Replica], weights: np.ndarray | None = None
) -> Entry:
    packed = packing.pack(base, replicas, name)
    return Entry(
        weights=weights,
        name=name,
        base=base,
        ideal=ideal,
        packed=packed,
        replicas=[packing.split(packed, r.prefix, r.qubits, name) for r in replicas],
        prefixes=[r.prefix for r in replicas],
        replica_qubits=[r.qubits for r in replicas],
    )


def build_entries(choice: Choice, policy: ReplicaPolicy) -> Choice:
    """Entries: each member packed over the replicas, followed directly by its packed mirror twin.

    A twin is cut from the member's single-copy ISA and packed with the same
    placements, so replica k of a witness and of its twin occupy the same
    qubits; adjacent in the job, the pair stays inside one calibration
    whenever the job allows. With more than one replica, the primary member
    also runs alone on replica 0's qubits as the crosstalk reference.
    """
    bases: list[tuple[str, QuantumCircuit, np.ndarray, np.ndarray | None]] = []
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        bases.append((member.name, isa, member.ideal, member.weights))
        if member.mirror:
            name = member.name + MIRROR_SUFFIX
            zeros = np.zeros(2**member.circuit.num_clbits)
            zeros[0] = 1.0
            bases.append((name, mirror_isa(isa, choice.snap.backend, name), zeros, None))
    choice.replica_floor = replica_floor(choice.group, policy)
    choice.replicas = place_replicas(choice.snap, [base[1] for base in bases], choice.replica_floor, policy)
    choice.entries = [_entry(name, isa, ideal, choice.replicas, w) for name, isa, ideal, w in bases]
    if policy.isolated_reference and len(choice.replicas) > 1:
        primary = choice.entries[0]
        alone = primary.replicas[0].copy(name=primary.name + ISOLATED_SUFFIX)
        choice.entries.append(
            Entry(
                name=alone.name,
                base=primary.base,
                ideal=primary.ideal,
                packed=alone,
                replicas=[alone],
                prefixes=primary.prefixes[:1],
                replica_qubits=primary.replica_qubits[:1],
                reference=True,
                weights=primary.weights,
            )
        )
    return choice


def execution_requirements(choice: Choice) -> dict[str, Any]:
    """Requirements derived from the exact packed circuits written to QPY."""
    static_entries = [entry for entry in choice.entries if not _is_dynamic(entry.packed)]
    dynamic_entries = [entry for entry in choice.entries if _is_dynamic(entry.packed)]
    operation_names = sorted({name for entry in choice.entries for name, _ in _ops(entry.packed)})
    return {
        "entries": len(choice.entries),
        "entry_names": [entry.name for entry in choice.entries],
        "static_circuits": len(static_entries),
        "dynamic_circuits": len(dynamic_entries),
        "max_classical_bits": max(entry.packed.num_clbits for entry in choice.entries),
        "physical_qubits": sorted({qubit for entry in choice.entries for qubit in _physical(entry.packed)}),
        "operation_names": operation_names,
        "replicas": len(choice.replicas),
        "isolated_references": sum(entry.reference for entry in choice.entries),
        "target_validated": True,
    }


def _trace_failure_summary(trace_by_backend: dict[str, list[dict[str, Any]]]) -> dict[str, list[str]]:
    """Compact selection failures for a terminal CLI diagnostic."""
    summary: dict[str, list[str]] = {}
    for backend_name, entries in trace_by_backend.items():
        reasons: set[str] = set()
        for entry in entries:
            stage = str(entry.get("stage", "routing"))
            reasons.update(f"{stage}: {reason}" for reason in entry.get("rejected", []))
            for field_name in ("compile_error", "member_compile_error", "entry_build_error"):
                if field_name in entry:
                    reasons.add(f"{field_name}: {entry[field_name]}")
            for field_name in ("member_rejections", "execution_rejections"):
                for member_name, rejected in entry.get(field_name, {}).items():
                    reasons.update(f"{member_name}: {reason}" for reason in rejected)
        summary[backend_name] = sorted(reasons) or ["no candidate reached final validation"]
    return summary


def select(group: Group, snaps: list[Snapshot], seeds: int, log: dict[str, Any], policy: ReplicaPolicy) -> Choice:
    """Best (backend, seed, layout) for the group by geometric-mean layout score over its members."""
    requirements = group_requirements(group)
    candidates: list[Choice] = []
    log[group.name] = {}
    for snap in snaps:
        trace: list[dict[str, Any]] = []
        log[group.name][snap.name] = trace
        capability_rejections = capability_violations(requirements, snap.capabilities)
        trace.append(
            {
                "stage": "capability_admission",
                "requirements": requirements.summary(),
                "rejected": capability_rejections,
            }
        )
        if capability_rejections:
            continue
        routing_rejections = routing_admission_violations(group, snap)
        trace.append({"stage": "routing_admission", "rejected": routing_rejections})
        if routing_rejections:
            continue
        primaries = []
        primary = group.members[0]
        for seed in range(SEED_TRANSPILER, SEED_TRANSPILER + seeds):
            try:
                isa = _compile(primary.circuit, snap, seed)
            except (QiskitError, ValueError) as error:
                trace.append({"seed": seed, "compile_error": type(error).__name__})
                continue
            bad = compiled_violations(isa, snap)
            trace.append({"seed": seed, "cz": isa.count_ops().get("cz", 0), "rejected": bad})
            if bad:
                continue
            # Scoring follows rejection: coherence() divides by T2, which an
            # excluded qubit may lack, so a rejected layout is never scored.
            score = layout_score(isa, snap.backend.target)
            trace[-1]["primary_score"] = score
            primaries.append((score, seed, isa))
        primaries.sort(key=lambda item: -item[0])
        for _, seed, isa in primaries[:JOINT_CANDIDATES]:
            layout = isa.layout.initial_index_layout(filter_ancillas=True)
            # Members that share the primary's parametrized circuit reuse its ISA
            # with their own parameter values: one routing, one readout qubit.
            try:
                isas = [_bind(isa, primary)] + [
                    _bind(
                        isa if member.circuit is primary.circuit else _compile(member.circuit, snap, seed, layout),
                        member,
                    )
                    for member in group.members[1:]
                ]
            except (QiskitError, ValueError) as error:
                trace.append({"seed": seed, "layout": layout, "member_compile_error": type(error).__name__})
                continue
            member_rejections = {
                member.name: rejected
                for member, member_isa in zip(group.members, isas, strict=True)
                if (rejected := compiled_violations(member_isa, snap))
            }
            if member_rejections:
                trace.append({"seed": seed, "layout": layout, "member_rejections": member_rejections})
                continue
            scores = [layout_score(c, snap.backend.target) for c in isas]
            joint = math.exp(sum(math.log(s) for s in scores) / len(scores))
            trace.append({"seed": seed, "joint_score": joint, "layout": layout})
            candidates.append(Choice(group, snap, seed, layout, isas, scores, joint))
    candidates.sort(key=lambda choice: (choice.joint_score, -choice.snap.pending_jobs), reverse=True)
    for candidate in candidates:
        trace = log[group.name][candidate.snap.name]
        try:
            build_entries(candidate, policy)
        except (LiveRunError, QiskitError, ValueError) as error:
            trace.append(
                {
                    "seed": candidate.seed,
                    "layout": candidate.layout,
                    "entry_build_error": f"{type(error).__name__}: {error}",
                }
            )
            continue
        execution_rejections = {
            entry.name: rejected
            for entry in candidate.entries
            if (rejected := compiled_violations(entry.packed, candidate.snap))
        }
        if execution_rejections:
            trace.append(
                {
                    "seed": candidate.seed,
                    "layout": candidate.layout,
                    "execution_rejections": execution_rejections,
                }
            )
            continue
        execution_kinds = {"dynamic" if _is_dynamic(entry.packed) else "static" for entry in candidate.entries}
        if len(execution_kinds) != 1:
            trace.append(
                {
                    "seed": candidate.seed,
                    "layout": candidate.layout,
                    "execution_rejections": {"group": ["packed execution set mixes static and dynamic circuits"]},
                }
            )
            continue
        compatibility_bound = candidate.snap.capabilities.max_circuits
        if compatibility_bound is not None and len(candidate.entries) > compatibility_bound:
            trace.append(
                {
                    "seed": candidate.seed,
                    "layout": candidate.layout,
                    "execution_rejections": {
                        "group": [
                            f"{len(candidate.entries)} packed entries exceed client-reported "
                            f"max_circuits compatibility bound {compatibility_bound}"
                        ]
                    },
                }
            )
            continue
        return candidate
    failure_summary = _trace_failure_summary(log[group.name])
    raise LiveRunError(
        f"{group.name}: no valid routed and packed candidate; failures={json.dumps(failure_summary, sort_keys=True)}"
    )


def _distribution(counts: dict[str, int], clbits: int) -> np.ndarray:
    dist = np.zeros(2**clbits)
    for key, c in counts.items():
        dist[int(key.replace(" ", ""), 2)] += c
    return np.asarray(dist / dist.sum())


def _pub_counts(pub: Any, register_names: list[str], label: str) -> dict[str, int]:
    """Join the named classical registers, in the given order, into one bit string per shot.

    Passing one replica's registers in circuit order yields that replica's
    counts in its own clbit order.
    """
    if not register_names:
        raise LiveRunError(f"{label}: result decoder needs at least one classical register")
    joined = pub.join_data(register_names)
    if not hasattr(joined, "get_counts"):
        raise LiveRunError(f"{label}: joined result data does not provide bit counts")
    return dict(joined.get_counts())


class TargetView(BackendV2):
    """A BackendV2 whose only content is a Target, for building Aer noise from it.

    AerSimulator.from_backend reads gate errors, durations, and T1/T2 from
    backend.target, so the view turns a live or historical Target into a noise
    model without a second calibration source.
    """

    def __init__(self, name: str, target: Any) -> None:
        super().__init__(name=name)
        self._view_target = target

    @property
    def target(self) -> Any:
        return self._view_target

    @property
    def max_circuits(self) -> None:
        return None

    @classmethod
    def _default_options(cls) -> Options:
        return Options()

    def run(self, run_input: Any, **options: Any) -> Any:
        raise NotImplementedError("TargetView carries a Target for noise modeling only")


def noise_simulator(name: str, target: Any, props: Any) -> AerSimulator:
    """AerSimulator with gate and coherence noise from this Target and readout from props.

    The Target's measure entries carry only the aggregate readout_error, from
    which Aer builds a symmetric channel. The noise model takes each qubit's
    asymmetric channel [[1 - e10, e10], [e01, 1 - e01]] (e10 =
    prob_meas1_prep0, e01 = prob_meas0_prep1) from the properties instead, the
    same channel readout_corrected inverts, so a corrected prediction removes
    exactly the readout error the simulation applied. A qubit without the two
    fields gets the symmetric readout_error channel from readout_flips, as the
    correction does. Planning and --collect both use it.
    """
    view = TargetView(name, target)
    noise = NoiseModel.from_backend(view, readout_error=False)
    for q in range(target.num_qubits):
        try:
            e10, e01 = readout_flips(props, q)
        except Exception:  # BackendPropertyError: no readout calibration at all
            continue
        noise.add_readout_error(ReadoutError([[1.0 - e10, e10], [e01, 1.0 - e01]]), [q])
    return AerSimulator.from_backend(view, noise_model=noise)


def simulate(choice: Choice, noise: Any, shots: int = SHOTS) -> dict[str, list[np.ndarray]]:
    """Noisy distribution of every entry's every replica, each simulated as its own single-replica circuit.

    The noise model carries no crosstalk between replicas, so a replica alone
    and a replica inside the packed circuit simulate identically.
    """
    return {entry.name: run_replicas(noise, entry, shots, SEED_SIMULATOR) for entry in choice.entries}


def run_replicas(noise: Any, entry: Entry, shots: int, seed: int) -> list[np.ndarray]:
    """Noisy distributions of entry's replicas from one batched run, in replica order.

    Aer derives each experiment's seed from seed_simulator and the
    experiment's position in the batch, so planning and --collect, which both
    batch an entry's replicas in replica order under the record's seed,
    replay identical noise draws.
    """
    result = noise.run(entry.replicas, shots=shots, seed_simulator=seed, max_parallel_experiments=0).result()
    return [_distribution(result.get_counts(k), rep.num_clbits) for k, rep in enumerate(entry.replicas)]


def readout_corrected(dist: np.ndarray, isa: QuantumCircuit, props: Any, symmetric: bool = False) -> np.ndarray:
    """dist with each classical bit's readout channel inverted, unclipped.

    A raw P(0) carries prob_meas0_prep1 of its readout qubit as an additive
    floor, so even a perfect zero divisor reads a nonzero dark probability.
    Each clbit's 2x2 channel [[1 - e10, e01], [e10, 1 - e01]] comes from the
    physical qubit that last wrote it (e10 = prob_meas1_prep0, e01 =
    prob_meas0_prep1), and their Kronecker product is inverted with clbit 0 as
    the least significant index bit. Aer's noise model applies the symmetric
    readout_error by default; noise_simulator replaces it with the same
    asymmetric channel, so in simulation and on hardware the inversion matches
    the channel applied.

    symmetric replaces both flip probabilities with their mean: measurement
    twirling randomizes the measured bit and reverses it classically, so a
    twirled job's effective channel is the symmetric average.
    """
    writer: dict[int, int] = {}
    for inst in isa.data:
        if inst.operation.name == "measure":
            writer[isa.find_bit(inst.clbits[0]).index] = isa.find_bit(inst.qubits[0]).index
    inverse = np.ones((1, 1))
    for clbit in reversed(range(isa.num_clbits)):
        e10, e01 = readout_flips(props, writer[clbit])
        if symmetric:
            e10 = e01 = (e10 + e01) / 2.0
        inverse = np.kron(inverse, np.linalg.inv(np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])))
    return np.asarray(inverse @ dist)


def corrected_summary(
    group: Group, entries: list[Entry], dists: dict[str, list[np.ndarray]], props: Any, symmetric: bool = False
) -> Any:
    """The pooled group summary on readout-inverted replica distributions, or why it is skipped.

    readout_corrected assumes each classical bit passes through its own
    output-only channel. In a feed-forward circuit a misread mid-circuit bit
    also steers the conditional gate, so the second bit's distribution depends
    on the first readout error and the separable inversion is biased; such
    groups report the reason instead of a corrected summary. Each replica is
    inverted with the channels of its own readout qubits before the replicas
    are averaged. props is one properties object, or a per-circuit mapping
    when circuits ran under different calibrations.
    """
    runs = [e for e in entries if not e.reference]
    if any(_is_dynamic(e.replicas[0]) for e in runs):
        return {"skipped": "feed-forward circuits: readout error steers the conditional branch"}
    corrected = {}
    for e in runs:
        own = props[e.name] if isinstance(props, dict) else props
        corrected[e.name] = [
            readout_corrected(d, rep, own, symmetric) for d, rep in zip(dists[e.name], e.replicas, strict=True)
        ]
    return _pooled_summaries(group, runs, corrected)[0]


def _pooled_summaries(
    group: Group, runs: list[Entry], dists: dict[str, list[np.ndarray]]
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """The pooled summary and the per-replica summaries of runs' replica distributions.

    Every pooled value is the mean over replicas of that value computed on
    each replica alone, the estimand summary_interval spans. For a ratio, a
    fringe fit, or a TVD this differs from the statistic of averaged
    distributions, and for a mirror-rescaled value it divides each replica's
    witness by that replica's own twin.
    """
    count = len(runs[0].replicas)
    per_replica = [group.summarize({e.name: dists[e.name][k] for e in runs}) for k in range(count)]
    pooled = {key: float(np.mean([r[key] for r in per_replica])) for key in per_replica[0]}
    return pooled, per_replica


def replica_statistics(
    group: Group, entries: list[Entry], dists: dict[str, list[np.ndarray]], shots: int
) -> dict[str, Any]:
    """Pooled, per-replica, interval, variance, crosstalk, and admission views of one group's replicas.

    The pooled summary averages each summary value over the replicas
    (_pooled_summaries), and summary_interval spans it; a value the group
    declares a per-shot rate (Group.rate_keys) also carries its pooled-shot
    Wilson bound. variance decomposes every entry's ideal-weighted score into shot
    and layout variance, and instance_variance adds the instance axis over the
    group's declared instances. crosstalk compares the primary's isolated
    reference with packed replica 0 on the same qubits.
    """
    runs = [e for e in entries if not e.reference]
    count = len(runs[0].replicas)
    pooled, per_replica = _pooled_summaries(group, runs, dists)
    out: dict[str, Any] = {"summary": pooled, "summary_per_replica": per_replica}
    # A declared rate has a Wilson interval from one replica's shots; any
    # other value needs two replicas for a spread.
    intervals = {
        key: variance.interval([r[key] for r in per_replica], shots, bernoulli=key in group.rate_keys)
        for key in pooled
        if (count >= 2 or key in group.rate_keys) and all(math.isfinite(r[key]) for r in per_replica)
    }
    if intervals:
        out["summary_interval"] = intervals
    scores = {e.name: [variance.score(d, e.ideal, e.weights) for d in dists[e.name]] for e in runs}
    out["variance"] = {
        name: variance.decompose([m for m, _ in pairs], [v for _, v in pairs], shots) for name, pairs in scores.items()
    }
    if group.instances and count >= 2:
        table = np.array([[m for m, _ in scores[n]] for n in group.instances])
        spread = np.array([[v for _, v in scores[n]] for n in group.instances])
        out["instance_variance"] = variance.instance_layout(table, spread, shots)
    for e in entries:
        if e.reference:
            iso, iso_var = variance.score(dists[e.name][0], e.ideal, e.weights)
            packed, packed_var = scores[runs[0].name][0]
            sd = math.sqrt((iso_var + packed_var) / shots)
            out["crosstalk"] = {
                "isolated_score": iso,
                "packed_replica0_score": packed,
                "difference": packed - iso,
                "z": (packed - iso) / sd if sd > 0 else None,
                "tvd": tvd(dists[e.name][0], dists[runs[0].name][0]),
            }
    if group.admission is not None:
        out["admission"] = group.admission(per_replica, shots)
    return out


def experiment_digest() -> str:
    """Return sha256 over the declared source closure that defines a run.

    Group membership, circuits, ideals, and summaries live in the experiment
    modules, and live_run.py itself holds the distribution, readout-correction,
    and replay code that turns counts into summaries, so collection under a
    different digest would reinterpret a run's measurements.
    """
    here = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for relative_path in EXPERIMENT_SOURCE_MANIFEST:
        path = here / relative_path
        if not path.is_file():
            raise LiveRunError(f"experiment source manifest entry is missing: {path}")
        digest.update(relative_path.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _code_commit() -> dict[str, Any]:
    """HEAD of the checkout and whether its gororoba_quantum sources differ from it."""
    here = Path(__file__).resolve().parent
    try:
        head = subprocess.run(["git", "-C", str(here), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        dirty = subprocess.run(
            ["git", "-C", str(here), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or f"exit {error.returncode}"
        raise LiveRunError(f"cannot establish Git provenance: {detail}") from error
    return {"head": head.stdout.strip() or None, "sources_modified": bool(dirty.stdout.strip())}


def _physical(isa: QuantumCircuit) -> list[int]:
    return sorted({q for _, qargs in _ops(isa) for q in qargs})


def _choice_record(
    choice: Choice, noisy: dict[str, list[np.ndarray]], noise_calibration: str, shots: int
) -> dict[str, Any]:
    target = choice.snap.backend.target
    members = []
    for entry in choice.entries:
        dynamic = _is_dynamic(entry.base)
        members.append(
            {
                "name": entry.name,
                "reference": entry.reference,
                "cz": entry.base.count_ops().get("cz", 0),
                "depth": entry.base.depth(),
                "duration_bound": "lower_without_classical_latency" if dynamic else "scheduled",
                "dynamic": dynamic,
                "feed_forward": any(isinstance(i.operation, ControlFlowOp) for i in entry.base.data),
                "replica_prefixes": entry.prefixes,
                "replica_qubits": entry.replica_qubits,
                "ideal": [round(float(p), 12) for p in entry.ideal],
                "replicas": [
                    {
                        "physical_qubits": _physical(rep),
                        "duration_s": duration_s(rep, target),
                        "esp": esp(rep, target),
                        "coherence": coherence(rep, target),
                        "noisy": [round(float(p), 6) for p in dist],
                        "tvd_noisy_to_ideal": tvd(dist, entry.ideal),
                    }
                    for rep, dist in zip(entry.replicas, noisy[entry.name], strict=True)
                ],
            }
        )
    return {
        "group": choice.group.name,
        "backend": choice.snap.name,
        "calibration": choice.snap.calibration,
        "noise_model_calibration": noise_calibration,
        "seed_transpiler": choice.seed,
        "initial_layout": choice.layout,
        "joint_score": choice.joint_score,
        "replica_floor": choice.replica_floor,
        "replicas": [
            {
                "index": r.index,
                "prefix": r.prefix,
                "score": r.score,
                "physical_qubits": r.qubits,
                "initial_layout": [r.mapping.get(q) for q in choice.layout],
                "mapping": {str(k): v for k, v in sorted(r.mapping.items())},
            }
            for r in choice.replicas
        ],
        **replica_statistics(choice.group, choice.entries, noisy, shots),
        "summary_readout_corrected": corrected_summary(choice.group, choice.entries, noisy, choice.snap.properties),
        "members": members,
    }


def discover_snapshots(
    service: QiskitRuntimeService, pinned_names: list[str] | None, max_pending: int | None
) -> tuple[list[Snapshot], dict[str, Any], dict[str, Any]]:
    """Return eligible snapshots, skipped evidence, and the requested-system inventory."""
    try:
        discovered = service.backends()
    except Exception as error:
        raise LiveRunError(f"backend discovery failed ({type(error).__name__})") from error
    names = list(dict.fromkeys(pinned_names or sorted(backend.name for backend in discovered)))
    snapshots: list[Snapshot] = []
    skipped: dict[str, Any] = {}
    inventory: dict[str, Any] = {}
    for name in names:
        try:
            snapshot = take_snapshot(service, name)
        except Exception as error:
            reason = (
                str(error) if isinstance(error, LiveRunError) else f"snapshot refresh failed ({type(error).__name__})"
            )
            skipped[name] = {"reason": reason}
            inventory[name] = {"eligibility": "probe_failed", "reason": reason}
            print(f"{name}: skipped: {reason}")
            continue
        ineligible = snapshot.ineligible_reason(max_pending)
        state = snapshot.summary()
        inventory[name] = (
            {"eligibility": "ineligible", "reason": ineligible} | state
            if ineligible
            else {"eligibility": "eligible"} | state
        )
        rounded_medians = {
            key: round(value, 5) if value is not None else None for key, value in snapshot.medians.items()
        }
        print(
            f"{snapshot.name}: {snapshot.status_msg} pending={snapshot.pending_jobs} "
            f"calibration={snapshot.calibration} capabilities={snapshot.capabilities.summary()} "
            f"medians={rounded_medians} "
            f"excluded qubits={len(snapshot.excluded_qubits)} edges={len(snapshot.excluded_edges)}"
            + (f" -> skipped: {ineligible}" if ineligible else "")
        )
        if ineligible:
            skipped[name] = {"reason": ineligible} | state
        else:
            snapshots.append(snapshot)
    return snapshots, skipped, inventory


def plan(service: QiskitRuntimeService, args: argparse.Namespace) -> tuple[list[Choice], dict[str, Any]]:
    available_groups = experiment_groups()
    known = {group.name for group in available_groups}
    unknown = sorted(set(args.groups or []) - known)
    if unknown:
        raise LiveRunError(f"unknown experiment groups {unknown}; known: {sorted(known)}")
    snaps, skipped, inventory = discover_snapshots(service, args.backends, args.max_pending)
    if not snaps:
        raise LiveRunError("no eligible backend")
    groups = [group for group in available_groups if not args.groups or group.name in args.groups]
    trace: dict[str, Any] = {}
    choices = [select(group, snaps, args.seeds, trace, _policy(args)) for group in groups]
    record = {
        "schema_version": RECORD_SCHEMA_VERSION,
        "schema_contract": RECORD_SCHEMA_CONTRACT,
        "state": "planned",
        "started": args.started,
        "versions": {pkg: version(pkg) for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
        "policy": QUALITY
        | {
            "max_pending": args.max_pending,
            "seeds": args.seeds,
            "joint_candidates": JOINT_CANDIDATES,
            "replica_floor": args.replica_floor,
            "max_replicas": args.max_replicas,
            "isolated_reference": args.isolated_reference,
        },
        "shots": args.shots,
        "seed_simulator": SEED_SIMULATOR,
        "experiment_digest": experiment_digest(),
        "code_commit": _code_commit(),
        "system_inventory": inventory,
        "backends": {s.name: s.summary() for s in snaps},
        "skipped_backends": skipped,
        "circuit_requirements": {group.name: group_requirements(group).summary() for group in groups},
        "execution_requirements": {choice.group.name: execution_requirements(choice) for choice in choices},
        "selection_trace": trace,
    }
    return choices, record


def _policy(args: argparse.Namespace) -> ReplicaPolicy:
    return ReplicaPolicy(args.replica_floor, args.max_replicas, args.isolated_reference)


def evaluate(choices: list[Choice], record: dict[str, Any]) -> None:
    """Noise-simulate each choice under its backend's live properties, after proving they match the Target."""
    # One simulator per snapshot: a group recompiled on a fresh snapshot of a
    # backend is simulated with that snapshot's Target, not an earlier one.
    sims: dict[int, tuple[AerSimulator, str]] = {}
    record["groups"] = []
    record["execution_requirements"] = {choice.group.name: execution_requirements(choice) for choice in choices}
    for choice in choices:
        isas = [entry.packed for entry in choice.entries]
        check_target_matches_properties(isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name)
        key = id(choice.snap)
        if key not in sims:
            sims[key] = (
                noise_simulator(choice.snap.name, choice.snap.backend.target, choice.snap.properties),
                choice.snap.calibration,
            )
        sim, cal = sims[key]
        noisy = simulate(choice, sim, int(record["shots"]))
        entry = _choice_record(choice, noisy, cal, int(record["shots"]))
        record["groups"].append(entry)
        cz = [m["cz"] for m in entry["members"]]
        summary = {k: round(v, 4) for k, v in entry["summary"].items()}
        scores = [round(r.score, 4) for r in choice.replicas]
        print(
            f"{choice.group.name}: {choice.snap.name} seed={choice.seed} layout={choice.layout} "
            f"joint_score={choice.joint_score:.4f} replicas={len(choice.replicas)} scores={scores} "
            f"cz={cz} summary={summary}"
        )


def check_budget(name: str, usage: dict[str, Any], minimum: float) -> None:
    """Reject an exhausted or below-minimum finite quota; an instance with no limit passes.

    usage() can omit usage_remaining_seconds or report None for an instance
    without a configured limit; usage_limit_reached still marks exhaustion.
    """
    if usage.get("usage_limit_reached"):
        raise LiveRunError(f"{name}: the instance reports its usage limit reached")
    remaining = usage.get("usage_remaining_seconds")
    if remaining is not None and float(remaining) < minimum:
        raise LiveRunError(f"{name}: {remaining} s of QPU time remaining, below --min-remaining-seconds")


def _qpy_digest(circuits: list[QuantumCircuit]) -> str:
    """Stable in-process identity for an ordered execution-circuit set."""
    buffer = io.BytesIO()
    qpy.dump(circuits, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def choice_change_reasons(choice: Choice, fresh: Snapshot) -> list[str]:
    """Reasons an existing compile needs rebuilding against a fresh snapshot."""
    reasons = capability_violations(group_requirements(choice.group), fresh.capabilities)
    if choice.snap.capabilities != fresh.capabilities:
        reasons.append("backend capabilities changed")
    isas = [entry.packed for entry in choice.entries]
    for entry in choice.entries:
        reasons.extend(f"{entry.name}: {reason}" for reason in compiled_violations(entry.packed, fresh))
    compatibility_bound = fresh.capabilities.max_circuits
    if compatibility_bound is not None and len(choice.entries) > compatibility_bound:
        reasons.append(
            f"{len(choice.entries)} packed entries exceed client-reported "
            f"max_circuits compatibility bound {compatibility_bound}"
        )
    try:
        if fingerprint(isas, fresh.backend.target, fresh.properties) != fingerprint(
            isas, choice.snap.backend.target, choice.snap.properties
        ):
            reasons.append("calibration values changed on compiled instructions")
    except Exception as error:
        reasons.append(f"calibration fingerprint failed ({type(error).__name__})")
    return sorted(set(reasons))


def choice_reselection_reasons(current: Choice, fresh: Choice) -> list[str]:
    """Reasons full fresh selection changes an existing executable choice."""
    reasons = choice_change_reasons(current, fresh.snap)
    if current.snap.name != fresh.snap.name:
        reasons.append(f"backend changed from {current.snap.name} to {fresh.snap.name}")
    if current.layout != fresh.layout:
        reasons.append("initial layout changed")
    current_replicas = [tuple(sorted(replica.mapping.items())) for replica in current.replicas]
    fresh_replicas = [tuple(sorted(replica.mapping.items())) for replica in fresh.replicas]
    if current_replicas != fresh_replicas:
        reasons.append("replica placements changed")
    current_names = [entry.name for entry in current.entries]
    fresh_names = [entry.name for entry in fresh.entries]
    if current_names != fresh_names:
        reasons.append("execution entry identities changed")
    if _qpy_digest([entry.packed for entry in current.entries]) != _qpy_digest(
        [entry.packed for entry in fresh.entries]
    ):
        reasons.append("packed execution circuits changed")
    return sorted(set(reasons))


def submission_batches(
    choices: list[Choice], kind: str, max_circuits: int | None
) -> list[list[tuple[str, QuantumCircuit, Choice]]]:
    """Partition whole result-complete groups into deterministic first-fit-decreasing jobs."""
    groups: list[tuple[int, list[tuple[str, QuantumCircuit, Choice]]]] = []
    for group_index, choice in enumerate(choices):
        classified = [
            (
                entry.name,
                entry.packed,
                choice,
                "dynamic" if _is_dynamic(entry.packed) else "static",
            )
            for entry in choice.entries
        ]
        choice_kinds = {entry_kind for _, _, _, entry_kind in classified}
        if len(choice_kinds) != 1:
            raise LiveRunError(f"{choice.group.name}: one result group mixes static and dynamic circuits")
        if kind not in choice_kinds:
            continue
        entries = [(name, isa, owner) for name, isa, owner, _ in classified]
        if max_circuits is not None and len(entries) > max_circuits:
            raise LiveRunError(
                f"{choice.group.name}: {len(entries)} circuits exceed client-reported "
                f"max_circuits compatibility bound {max_circuits}"
            )
        groups.append((group_index, entries))
    if not groups:
        return []
    if max_circuits is None:
        return [[entry for _, entries in groups for entry in entries]]
    batches: list[list[tuple[str, QuantumCircuit, Choice]]] = []
    for _, entries in sorted(groups, key=lambda item: (-len(item[1]), item[0])):
        for batch in batches:
            if len(batch) + len(entries) <= max_circuits:
                batch.extend(entries)
                break
        else:
            batches.append(list(entries))
    return batches


def _submission_key(entry: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(entry["backend"]),
        str(entry["kind"]),
        int(entry["batch_index"]),
        int(entry["batch_count"]),
    )


def _recovery_tags(
    started: str,
    backend: str,
    kind: str,
    batch_index: int,
    batch_count: int,
    members: list[str],
    qpy_archive_sha256: str,
) -> list[str]:
    """Tags that identify exactly one planned Runtime job after response loss."""
    run_digest = hashlib.sha256(started.encode()).hexdigest()[:20]
    batch_identity = json.dumps(
        {
            "started": started,
            "backend": backend,
            "kind": kind,
            "batch_index": batch_index,
            "batch_count": batch_count,
            "members": members,
            "qpy_archive_sha256": qpy_archive_sha256,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    batch_digest = hashlib.sha256(batch_identity.encode()).hexdigest()[:24]
    return ["gororoba-quantum", f"gororoba-run-{run_digest}", f"gororoba-batch-{batch_digest}"]


def build_submission_plan(
    choices: list[Choice], args: argparse.Namespace, qpy_archive_sha256: str
) -> tuple[dict[str, Any], list[tuple[int, str, str, list[tuple[str, QuantumCircuit, Choice]]]]]:
    """Materialize the complete immutable batch identity before any job call."""
    planned_backends = sorted({choice.snap.name for choice in choices})
    by_backend: dict[str, list[Choice]] = {}
    for choice in choices:
        by_backend.setdefault(choice.snap.name, []).append(choice)
    runtime_batches: list[tuple[int, str, str, list[tuple[str, QuantumCircuit, Choice]]]] = []
    planned_jobs: list[dict[str, Any]] = []
    for name, group_choices in by_backend.items():
        backend = group_choices[0].snap.backend
        if any(choice.snap.backend is not backend for choice in group_choices):
            raise LiveRunError(f"{name}: final groups do not share one refreshed backend snapshot")
        for kind in ("static", "dynamic"):
            max_circuits = group_choices[0].snap.capabilities.max_circuits
            batches = submission_batches(group_choices, kind, max_circuits)
            for batch_index, batch in enumerate(batches, start=1):
                members = [member_name for member_name, _, _ in batch]
                batch_count = len(batches)
                recovery_tags = _recovery_tags(
                    args.started,
                    name,
                    kind,
                    batch_index,
                    batch_count,
                    members,
                    qpy_archive_sha256,
                )
                sampler = configure_sampler(
                    backend,
                    kind,
                    args.twirl,
                    args.dd,
                    recovery_tags,
                    args.shots,
                )
                plan_index = len(planned_jobs)
                planned_jobs.append(
                    {
                        "backend": name,
                        "kind": kind,
                        "batch_index": batch_index,
                        "batch_count": batch_count,
                        "members": members,
                        "qpy_archive_sha256": qpy_archive_sha256,
                        "calibrations": sorted({choice.snap.calibration for _, _, choice in batch}),
                        "recovery_tags": recovery_tags,
                        "options": sampler.options.model_dump(mode="json"),
                        "state": "planned",
                    }
                )
                runtime_batches.append((plan_index, name, kind, batch))
    return {
        "planned_backends": planned_backends,
        "qpy_archive_sha256": qpy_archive_sha256,
        "planned_jobs": planned_jobs,
        "jobs": [],
        "complete": False,
    }, runtime_batches


def _job_record(plan_entry: dict[str, Any], job_id: str, recovered: bool = False) -> dict[str, Any]:
    record = {
        "backend": plan_entry["backend"],
        "kind": plan_entry["kind"],
        "batch_index": plan_entry["batch_index"],
        "batch_count": plan_entry["batch_count"],
        "job_id": job_id,
        "members": plan_entry["members"],
        "qpy_archive_sha256": plan_entry["qpy_archive_sha256"],
        "calibrations": plan_entry["calibrations"],
        "recovery_tags": plan_entry["recovery_tags"],
        "budget_before": plan_entry["budget_before"],
        "options": plan_entry["options"],
    }
    if recovered:
        record["job_id_recovered"] = True
    return record


def submission_gaps(submission: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Validate the planned/submitted ledger and return batches without a job id."""
    planned_jobs = submission.get("planned_jobs")
    if planned_jobs is None:
        sent_backends = {job["backend"] for job in submission["jobs"]}
        backends = [name for name in submission.get("planned_backends", []) if name not in sent_backends]
        return [], backends, []

    archive_digest = submission.get("qpy_archive_sha256")
    if not isinstance(archive_digest, str) or len(archive_digest) != 64:
        raise LiveRunError("submission plan has no valid QPY archive SHA-256")
    planned_by_key: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    planned_members: set[str] = set()
    for planned_job in planned_jobs:
        key = _submission_key(planned_job)
        if key in planned_by_key:
            raise LiveRunError(f"duplicate planned job identity {key}")
        if planned_job.get("qpy_archive_sha256") != archive_digest:
            raise LiveRunError(f"planned job {key} differs from the submission QPY archive digest")
        duplicate_members = planned_members.intersection(planned_job["members"])
        if duplicate_members:
            raise LiveRunError(f"planned circuits appear in more than one job: {sorted(duplicate_members)}")
        planned_members.update(planned_job["members"])
        planned_by_key[key] = planned_job

    submitted_by_key: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    submitted_job_ids: set[str] = set()
    for submitted_job in submission["jobs"]:
        key = _submission_key(submitted_job)
        if key in submitted_by_key:
            raise LiveRunError(f"duplicate submitted job identity {key}")
        if key not in planned_by_key:
            raise LiveRunError(f"submitted job {key} has no planned ledger entry")
        job_id = submitted_job.get("job_id")
        if not job_id:
            raise LiveRunError(f"submitted job {key} has no job id")
        if job_id in submitted_job_ids:
            raise LiveRunError(f"submitted job id {job_id!r} appears more than once")
        submitted_job_ids.add(job_id)
        planned_job = planned_by_key[key]
        for field_name in ("members", "qpy_archive_sha256", "calibrations", "recovery_tags", "options"):
            if submitted_job.get(field_name) != planned_job.get(field_name):
                raise LiveRunError(f"submitted job {key} differs from its plan in {field_name}")
        submitted_by_key[key] = submitted_job

    missing = [
        {
            "backend": entry["backend"],
            "kind": entry["kind"],
            "batch_index": entry["batch_index"],
            "batch_count": entry["batch_count"],
            "members": entry["members"],
            "attempt_state": entry.get("state", "planned"),
        }
        for key, entry in planned_by_key.items()
        if key not in submitted_by_key
    ]
    if submission.get("complete", False) and missing:
        raise LiveRunError("submission is marked complete but planned jobs lack recorded job ids")
    return (
        missing,
        sorted({entry["backend"] for entry in missing}),
        [member for entry in missing for member in entry["members"]],
    )


def reconcile_attempted_jobs(service: QiskitRuntimeService, submission: dict[str, Any]) -> bool:
    """Recover a response-lost job id from its unique pre-recorded Runtime tags."""
    planned_jobs = submission.get("planned_jobs")
    if planned_jobs is None:
        return False
    submitted_keys = {_submission_key(job) for job in submission["jobs"]}
    changed = False
    for plan_entry in planned_jobs:
        key = _submission_key(plan_entry)
        if key in submitted_keys or plan_entry.get("state") != "attempted":
            continue
        instance_hash = plan_entry.get("budget_before", {}).get("instance_sha256_12")
        try:
            instances = service.instances()
        except Exception as error:
            raise LiveRunError(f"planned job {key} instance discovery failed ({type(error).__name__})") from error
        matching_instances = [
            instance["crn"]
            for instance in instances
            if hashlib.sha256(str(instance["crn"]).encode()).hexdigest()[:12] == instance_hash
        ]
        if len(matching_instances) != 1:
            raise LiveRunError(
                f"planned job {key} maps to {len(matching_instances)} accessible instances; "
                "submission identity remains unresolved"
            )
        try:
            matches = service.jobs(
                limit=2,
                backend_name=plan_entry["backend"],
                instance=matching_instances[0],
                job_tags=plan_entry["recovery_tags"],
            )
        except Exception as error:
            raise LiveRunError(f"planned job {key} recovery query failed ({type(error).__name__})") from error
        plan_entry["recovery"] = {"checked_at": _now(), "match_count": len(matches)}
        changed = True
        if len(matches) != 1:
            raise LiveRunError(
                f"planned job {key} has {len(matches)} recovery-tag matches; submission identity remains unresolved"
            )
        recovered_id = matches[0].job_id()
        submission["jobs"].append(_job_record(plan_entry, recovered_id, recovered=True))
        plan_entry["state"] = "recovered"
        submitted_keys.add(key)
    missing, _, _ = submission_gaps(submission)
    if not missing:
        submission["complete"] = True
    return changed


def submit(
    service: QiskitRuntimeService,
    choices: list[Choice],
    args: argparse.Namespace,
    record: dict[str, Any],
    archive: Callable[[], str],
    checkpoint: Callable[[], None],
) -> None:
    """Re-gate the approved plan once, stop on change, then archive and submit.

    A changed selection receives fresh predictions and QPY evidence, but the
    process sends no Runtime job because the written case approved different
    execution circuits or hardware. An unchanged selection reaches isa.qpy
    before the first job is sent. The exact archive digest and recovery tags
    are checkpointed before each attempt, and each returned job id is
    checkpointed before the next batch.
    """
    fresh_snapshots, skipped, inventory = discover_snapshots(service, args.backends, args.max_pending)
    if not fresh_snapshots:
        raise LiveRunError("no eligible backend remains before submission")
    attempt_trace: dict[str, Any] = {}
    reselected: dict[str, Any] = {}
    for idx, choice in enumerate(choices):
        previous_backend = choice.snap.name
        fresh_choice = select(
            choice.group,
            fresh_snapshots,
            args.seeds,
            attempt_trace,
            _policy(args),
        )
        reasons = choice_reselection_reasons(choice, fresh_choice)
        choices[idx] = fresh_choice
        if reasons:
            print(f"{choice.group.name}: live configuration changed; preparing a revised submit-free plan")
            reselected[choice.group.name] = {
                "previous_backend": previous_backend,
                "selected_backend": fresh_choice.snap.name,
                "reasons": reasons,
            }
    record.setdefault("revalidation", []).append(
        {
            "attempt": 1,
            "system_inventory": inventory,
            "skipped_backends": skipped,
            "reselected_groups": reselected,
            "selection_trace": attempt_trace,
        }
    )
    if reselected:
        record["system_inventory"] = inventory
        record["backends"] = {snapshot.name: snapshot.summary() for snapshot in fresh_snapshots}
        record["skipped_backends"] = skipped
        record["selection_trace"] = attempt_trace
        evaluate(choices, record)
        record["reevaluated_before_submit"] = 1
        record["state"] = "approval_required"
        qpy_archive_sha256 = archive()
        record["renewed_approval"] = {
            "required_at": _now(),
            "reason": "live configuration changed after the written submission case was approved",
            "changed_groups": reselected,
            "qpy_archive_sha256": qpy_archive_sha256,
        }
        checkpoint()
        raise LiveRunError(
            "live configuration changed after approval; the revised record and isa.qpy require "
            "a renewed written submission case and user approval; no Runtime job was submitted"
        )
    qpy_archive_sha256 = archive()
    submission, runtime_batches = build_submission_plan(choices, args, qpy_archive_sha256)
    # The complete batch ledger reaches disk before the first job starts. A
    # partial submission can therefore name every unsent circuit, including a
    # later batch on a backend that already accepted an earlier one.
    record["submission"] = submission
    record["state"] = "submission_started"
    checkpoint()
    for plan_index, name, kind, batch in runtime_batches:
        plan_entry = record["submission"]["planned_jobs"][plan_index]
        batch_index = int(plan_entry["batch_index"])
        batch_count = int(plan_entry["batch_count"])
        batch_tag = f"{kind}-{batch_index}-of-{batch_count}"
        fresh = take_snapshot(service, name)
        ineligible = fresh.ineligible_reason(args.max_pending)
        if ineligible:
            raise LiveRunError(f"{name}: {batch_tag} left the eligibility gate ({ineligible})")
        owner_reasons: dict[str, list[str]] = {}
        seen_owners: set[int] = set()
        for _, _, owner in batch:
            if id(owner) in seen_owners:
                continue
            seen_owners.add(id(owner))
            reasons = choice_change_reasons(owner, fresh)
            if reasons:
                owner_reasons[owner.group.name] = reasons
        if owner_reasons:
            raise LiveRunError(
                f"{name}: {batch_tag} hardware moved after batch planning; "
                f"no circuit in this batch was submitted ({owner_reasons})"
            )
        usage = service.usage()
        check_budget(name, usage, args.min_remaining_seconds)
        sampler = configure_sampler(
            fresh.backend,
            kind,
            args.twirl,
            args.dd,
            plan_entry["recovery_tags"],
            args.shots,
        )
        effective_options = sampler.options.model_dump(mode="json")
        if effective_options != plan_entry["options"]:
            raise LiveRunError(f"{name}: {batch_tag} effective Sampler options moved after planning")
        plan_entry["pre_submit_revalidation"] = {
            "fetched_at": fresh.fetched_at,
            "calibration": fresh.calibration,
            "capabilities": fresh.capabilities.summary(),
            "excluded_qubits": len(fresh.excluded_qubits),
            "excluded_edges": len(fresh.excluded_edges),
        }
        plan_entry["budget_before"] = _budget(service, usage)
        plan_entry["state"] = "attempted"
        # The recovery identity and attempt marker reach disk before the remote
        # call, so collection can resolve a response-lost accepted job exactly.
        checkpoint()
        job = sampler.run([isa for _, isa, _ in batch])
        job_id = job.job_id()
        record["submission"]["jobs"].append(_job_record(plan_entry, job_id))
        plan_entry["state"] = "accepted"
        # The job id is the only handle on QPU time already spent; it reaches
        # disk before the next job is sent.
        record["state"] = "partially_submitted"
        checkpoint()
        print(f"submitted {len(batch)} {batch_tag} circuits to {name}: job {job_id}")
    record["submission"]["complete"] = True
    record["state"] = "submitted"
    checkpoint()


def configure_sampler(
    backend: Any, kind: str, twirl: bool, dd: str | None, tags: list[str], shots: int = SHOTS
) -> Sampler:
    """The client-side Sampler for one job: twirling and DD apply to static jobs only.

    IBM's Sampler rejects dynamical decoupling on dynamic circuits, and the 0.50
    client-side Sampler's twirling boxes circuits through samplomatic, which
    rejects if_else. With DD on, idle qubits still in their initial state get no
    pulses: a 3- to 5-qubit experiment on a 156-qubit ISA would otherwise drive
    the unused qubits too.
    """
    if kind not in ("static", "dynamic"):
        raise LiveRunError(f"unknown Sampler job kind {kind!r}")
    if shots < 1:
        raise LiveRunError(f"Sampler shots must be positive, got {shots}")
    if twirl and kind == "static":
        shots_per_randomization, remainder = divmod(shots, TWIRLING_RANDOMIZATIONS)
        if remainder or shots_per_randomization < TWIRLING_MIN_SHOTS_PER_RANDOMIZATION:
            minimum = TWIRLING_RANDOMIZATIONS * TWIRLING_MIN_SHOTS_PER_RANDOMIZATION
            raise LiveRunError(
                f"twirled static jobs need at least {minimum} shots divisible by {TWIRLING_RANDOMIZATIONS}; got {shots}"
            )
    sampler = Sampler(mode=backend)
    sampler.options.default_shots = shots
    sampler.options.environment.job_tags = tags
    if twirl and kind == "static":
        sampler.options.twirling.enable_gates = True
        sampler.options.twirling.enable_measure = True
        sampler.options.twirling.num_randomizations = TWIRLING_RANDOMIZATIONS
        sampler.options.twirling.shots_per_randomization = shots_per_randomization
    if dd and kind == "static":
        sampler.options.dynamical_decoupling.enable = True
        sampler.options.dynamical_decoupling.sequence_type = dd
        sampler.options.dynamical_decoupling.skip_reset_qubits = True
    return sampler


def _is_dynamic(isa: QuantumCircuit) -> bool:
    """Control flow, reset, or any measurement followed by later quantum work."""
    measurement_seen = False
    for inst in isa.data:
        name = inst.operation.name
        if isinstance(inst.operation, ControlFlowOp) or name == "reset":
            return True
        if measurement_seen and name not in ("measure", "barrier", "delay"):
            return True
        if name == "measure":
            measurement_seen = True
    return False


def _budget(service: QiskitRuntimeService, usage: dict[str, Any]) -> dict[str, Any]:
    """usage() seconds and window, with the instance identified only by a hash of its CRN."""
    instance = str(service.active_instance() or "")
    return {
        "instance_sha256_12": hashlib.sha256(instance.encode()).hexdigest()[:12],
        "usage_period": usage.get("usage_period"),
        "usage_limit_seconds": usage.get("usage_limit_seconds"),
        "usage_consumed_seconds": usage.get("usage_consumed_seconds"),
        "usage_remaining_seconds": usage.get("usage_remaining_seconds"),
    }


def pub_windows(result: Any, count: int) -> list[tuple[datetime, datetime]]:
    """Start and stop of the execution spans that hold each PUB's shots.

    The Sampler result carries them at result.metadata["execution"]
    ["execution_spans"] (IBM's Sampler input/output guide, "View execution
    spans"); the job-level running timestamp can precede the shots by
    server-side preparation, across a calibration update. Naive span times are
    UTC.
    """
    execution = result.metadata.get("execution") or {}
    spans = execution.get("execution_spans")
    if spans is None or len(spans) == 0:
        raise LiveRunError(f"result metadata carries no execution spans (keys {sorted(result.metadata)})")
    windows = []
    for idx in range(count):
        # ExecutionSpans.filter_by_pub keeps every span and empties those
        # without the PUB, so the PUB's own window comes from the spans whose
        # pub_idxs include it.
        own = [span for span in spans if idx in span.pub_idxs]
        if not own:
            raise LiveRunError(f"no execution span covers PUB {idx}")
        start, stop = min(span.start for span in own), max(span.stop for span in own)
        windows.append(
            (
                start if start.tzinfo else start.replace(tzinfo=UTC),
                stop if stop.tzinfo else stop.replace(tzinfo=UTC),
            )
        )
    return windows


def _odr_withheld(
    names: list[str], executed: dict[str, dict[str, Any]], shots: int, replicas: int
) -> tuple[str | None, str | None]:
    """Why the pooled and the per-replica mirror-rescaled values are not valid, or None for each that is.

    Rescaling divides a witness's <Z> by its twin's attenuation, a correction
    only when both ran under one calibration. A replica's own quotient needs
    ODR_MIN_SHOTS shots. The pooled value averages the replicas' own
    quotients, whose mean over R replicas carries the statistical error of one
    quotient at R times the shots, so it needs ODR_MIN_SHOTS shots over all
    replicas together; replicas whose attenuations differ still each divide
    by their own.
    """
    if not any(name.endswith(MIRROR_SUFFIX) for name in names):
        return None, None
    ran = [executed[n] for n in names if n in executed]
    if any(e["calibration_changed_during_shots"] for e in ran) or len({e["calibration"] for e in ran}) > 1:
        reason = "witnesses and mirror twins did not all run under one calibration"
        return reason, reason
    per_replica = f"{shots} shots per replica; ODR needs at least {ODR_MIN_SHOTS}" if shots < ODR_MIN_SHOTS else None
    pooled = (
        f"{shots} shots on each of {replicas} replicas; pooled ODR needs {ODR_MIN_SHOTS} in total"
        if shots * replicas < ODR_MIN_SHOTS
        else None
    )
    return pooled, per_replica


def _without_odr(summary: dict[str, Any], withheld: str | None) -> dict[str, Any]:
    """summary minus its mirror-rescaled and twin fields when withheld names a reason."""
    if withheld is None:
        return summary
    return {k: v for k, v in summary.items() if "odr" not in k and not k.startswith("mirror_z")}


def _gate_odr(stats: dict[str, Any], pooled: str | None, per_replica: str | None) -> dict[str, Any]:
    """stats with ODR values removed from the pooled and the per-replica views each gate withholds.

    summary_interval spans the replicas' quotients around their mean, the
    pooled value, so it follows the pooled gate.
    """
    stats["summary"] = _without_odr(stats["summary"], pooled)
    stats["summary_per_replica"] = [_without_odr(r, per_replica) for r in stats["summary_per_replica"]]
    if "summary_interval" in stats:
        stats["summary_interval"] = _without_odr(stats["summary_interval"], pooled)
    return stats


def _comparisons_withheld(names: list[str], executed: dict[str, dict[str, Any]]) -> str | None:
    """Why statistics that combine separate PUBs of a group are not valid, or None when they are.

    Each member, twin, and isolated reference runs as its own PUB, and every
    group summary combines them: a dark/bright ratio, a fringe fit, a margin
    over a null, crosstalk, and admission. A calibration update between PUBs
    would read as the experiment's signal, so these need every PUB of the
    group under one calibration with no update inside any PUB's shots.
    """
    ran = [executed[n] for n in names if n in executed]
    if any(e["calibration_changed_during_shots"] for e in ran) or len({e["calibration"] for e in ran}) > 1:
        return "the group's PUBs did not all run under one calibration"
    return None


def _single_pub_views(stats: dict[str, Any]) -> dict[str, Any]:
    """The views of stats computed within one PUB each: every entry's replica variance."""
    return {"variance": stats["variance"]}


def _archived_entries(record: dict[str, Any], isas: dict[str, QuantumCircuit]) -> dict[str, list[Entry]]:
    """Each group's entries rebuilt from the archived packed circuits and the record's replica layout."""
    weights = {m.name: m.weights for g in experiment_groups() for m in g.members}
    out: dict[str, list[Entry]] = {}
    for group in record["groups"]:
        entries = out.setdefault(group["group"], [])
        for member in group["members"]:
            packed = isas[member["name"]]
            replicas = [
                packing.split(packed, prefix, qubits, member["name"])
                for prefix, qubits in zip(member["replica_prefixes"], member["replica_qubits"], strict=True)
            ]
            entries.append(
                Entry(
                    name=member["name"],
                    base=replicas[0],
                    ideal=np.asarray(member["ideal"]),
                    packed=packed,
                    replicas=replicas,
                    prefixes=member["replica_prefixes"],
                    replica_qubits=member["replica_qubits"],
                    reference=member["reference"],
                    weights=weights.get(member["name"].removesuffix(ISOLATED_SUFFIX)),
                )
            )
    return out


def collect(service: QiskitRuntimeService, run_dir: Path) -> None:
    """Measured replica distributions against the noise model of the calibration in force at execution."""
    record = json.loads((run_dir / "record.json").read_text())
    qpy_bytes = (run_dir / "isa.qpy").read_bytes()
    groups = {g.name: g for g in experiment_groups()}
    if (
        record.get("experiment_digest") != experiment_digest()
        or record.get("schema_version") != RECORD_SCHEMA_VERSION
        or record.get("schema_contract") != RECORD_SCHEMA_CONTRACT
    ):
        commit = record.get("code_commit", {}).get("head")
        raise LiveRunError(
            "experiment definitions or record contract differ from the run's "
            f"(digest {record.get('experiment_digest')}, schema {record.get('schema_version')}, "
            f"contract {record.get('schema_contract')!r}); collect from commit "
            f"{commit}, where groups, ideals, summaries, and replica decoding match the archived circuits"
        )
    if "submission" not in record:
        raise LiveRunError(f"{run_dir} is a dry-run record with no submitted jobs to collect")
    submission = record["submission"]
    planned_jobs = submission.get("planned_jobs")
    if planned_jobs is not None:
        actual_archive_sha256 = hashlib.sha256(qpy_bytes).hexdigest()
        if actual_archive_sha256 != submission.get("qpy_archive_sha256"):
            raise LiveRunError("isa.qpy differs from the archive digest checkpointed before submission")
    isas = {c.name: c for c in qpy.load(io.BytesIO(qpy_bytes))}
    if planned_jobs is not None:
        planned_members = [member for planned_job in planned_jobs for member in planned_job["members"]]
        if len(planned_members) != len(set(planned_members)):
            raise LiveRunError("submission plan assigns one packed circuit to multiple jobs")
        missing_from_plan = sorted(set(isas) - set(planned_members))
        missing_from_archive = sorted(set(planned_members) - set(isas))
        if missing_from_plan or missing_from_archive:
            raise LiveRunError(
                "submission plan and QPY archive differ: "
                f"archive-only={missing_from_plan}, plan-only={missing_from_archive}"
            )
        for planned_job in planned_jobs:
            for member_name in planned_job["members"]:
                if member_name not in isas:
                    raise LiveRunError(f"planned circuit {member_name!r} is absent from isa.qpy")
        try:
            reconciled = reconcile_attempted_jobs(service, submission)
        finally:
            # Recovery evidence and recovered ids retain their own atomic
            # checkpoint even when a zero-match or ambiguous query stops.
            write_json(run_dir, record)
        if reconciled and submission.get("complete", False):
            record["state"] = "submitted"
            write_json(run_dir, record)
    jobs_without_id, backends_without_id, members_without_id = submission_gaps(submission)
    if not submission.get("complete", False):
        if planned_jobs is None:
            detail = f"backends without a recorded job id: {backends_without_id}"
        else:
            detail = f"{len(jobs_without_id)} jobs and {len(members_without_id)} circuits lack recorded job ids"
        print(f"incomplete submission: {detail}; collecting {len(submission['jobs'])} recorded jobs", file=sys.stderr)
    shots, seed = int(record["shots"]), int(record["seed_simulator"])
    by_group = _archived_entries(record, isas)
    by_name = {e.name: e for entries in by_group.values() for e in entries}
    out: list[dict[str, Any]] = [
        {
            "submission_complete": bool(submission.get("complete", False)),
            "backends_without_recorded_job_id": backends_without_id,
            "members_without_recorded_job_id": members_without_id,
            "jobs_without_recorded_id": jobs_without_id,
        }
    ]
    for job_entry in record["submission"]["jobs"]:
        job = service.job(job_entry["job_id"])
        result = job.result()
        metrics = job.metrics()
        members = job_entry["members"]
        windows = pub_windows(result, len(members))
        twirled_readout = bool(job_entry.get("options", {}).get("twirling", {}).get("enable_measure"))
        backend = service.backend(job_entry["backend"])
        # One calibration fetch per distinct execution start: a PUB is replayed
        # under the Target and properties in force when its shots began.
        at: dict[datetime, tuple[Any, Any]] = {}
        for start, _ in windows:
            if start not in at:
                props_then = backend.properties(datetime=start)
                target_then = backend.target_history(datetime=start)
                at[start] = (
                    props_then,
                    noise_simulator(f"{backend.name}@{start.isoformat()}", target_then, props_then),
                )
                starting = [isas[n] for (st, _), n in zip(windows, members, strict=True) if st == start]
                check_target_matches_properties(starting, target_then, props_then, f"{backend.name}@{start}")
        measured: dict[str, list[np.ndarray]] = {}
        props_by_name: dict[str, Any] = {}
        replayed: dict[str, list[np.ndarray]] = {}
        executed: dict[str, dict[str, Any]] = {}
        for idx, (name, pub) in enumerate(zip(members, result, strict=True)):
            entry = by_name[name]
            start, stop = windows[idx]
            props_then, sim_then = at[start]
            measured[name] = [
                _distribution(_pub_counts(pub, packing.registers(entry.packed, prefix), name), rep.num_clbits)
                for prefix, rep in zip(entry.prefixes, entry.replicas, strict=True)
            ]
            props_by_name[name] = props_then
            replayed[name] = run_replicas(sim_then, entry, shots, seed)
            stop_calibration = backend.properties(datetime=stop).last_update_date
            executed[name] = {
                "start": start.isoformat(),
                "stop": stop.isoformat(),
                "calibration": props_then.last_update_date.isoformat(),
                "calibration_changed_during_shots": stop_calibration != props_then.last_update_date,
            }
        for gname, entries in by_group.items():
            required = [e.name for e in entries]
            if not any(n in measured for n in required):
                continue
            group = groups[gname]
            # A summary needs every entry of the group; a job that lacks some
            # still reports the distributions it has.
            missing = [n for n in required if n not in measured]
            out_entry: dict[str, Any] = {
                "group": gname,
                "backend": job_entry["backend"],
                "executed": {n: executed[n] for n in required if n in executed},
                "job_usage": metrics.get("usage"),
                "measured": {
                    n: [[round(float(p), 6) for p in dist] for dist in measured[n]] for n in required if n in measured
                },
            }
            # A circuit whose shots straddle a calibration update has no single
            # calibration to correct or replay against; its group keeps the raw
            # measurement and states why the rest is absent.
            straddling = [n for n in required if n in executed and executed[n]["calibration_changed_during_shots"]]
            if missing:
                out_entry["summary_unavailable"] = f"missing {missing}"
                out.append(out_entry)
                continue
            stats = replica_statistics(group, entries, measured, shots)
            comparison_reason = _comparisons_withheld(required, executed)
            if comparison_reason:
                # Every summary combines members that ran as separate PUBs, so
                # under split calibrations only each entry's own replica
                # variance stands; the raw distributions above stay for
                # reanalysis.
                out_entry["comparisons_withheld"] = comparison_reason
                out_entry["measured_statistics"] = _single_pub_views(stats)
                if straddling:
                    out_entry["calibration_dependent_summaries_unavailable"] = (
                        f"calibration changed during the shots of {straddling}"
                    )
                else:
                    out_entry["replayed_statistics"] = _single_pub_views(
                        replica_statistics(group, entries, replayed, shots)
                    )
                    out_entry["tvd_measured_to_replayed"] = {
                        n: [tvd(m, r) for m, r in zip(measured[n], replayed[n], strict=True)] for n in required
                    }
                out.append(out_entry)
                continue
            # A failed ODR gate removes the mirror-rescaled values from every
            # view the entry publishes, measured, readout-corrected, and
            # replayed alike.
            pooled_reason, replica_reason = _odr_withheld(required, executed, shots, len(entries[0].replicas))
            if pooled_reason or replica_reason:
                out_entry["odr_withheld"] = {"pooled": pooled_reason, "per_replica": replica_reason}
            out_entry["measured_statistics"] = _gate_odr(stats, pooled_reason, replica_reason)
            out_entry["measured_summary_readout_corrected"] = _without_odr(
                corrected_summary(group, entries, measured, props_by_name, symmetric=twirled_readout),
                pooled_reason,
            )
            out_entry["replayed_statistics"] = _gate_odr(
                replica_statistics(group, entries, replayed, shots), pooled_reason, replica_reason
            )
            out_entry["tvd_measured_to_replayed"] = {
                n: [tvd(m, r) for m, r in zip(measured[n], replayed[n], strict=True)] for n in required
            }
            out.append(out_entry)
    text = json.dumps(out, indent=2) + "\n"
    _replace_atomically(run_dir / "collect.json", lambda handle: handle.write(text), "w")
    print(json.dumps(out, indent=2))


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"needs a positive count, got {value}")
    return value


def _fraction(text: str) -> float:
    value = float(text)
    if not 0.0 < value <= 1.0:
        raise argparse.ArgumentTypeError(f"needs a fraction in (0, 1], got {value}")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backends", type=lambda s: s.split(","), help="comma-separated pin; default all accessible")
    parser.add_argument("--groups", type=lambda s: s.split(","), help="comma-separated experiment groups")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS, help="transpiler seeds per group and backend")
    parser.add_argument("--max-pending", type=int, default=DEFAULT_MAX_PENDING)
    parser.add_argument("--out", type=Path, help="directory under which the run's audit record is written")
    parser.add_argument("--submit", action="store_true", help="submit the chosen circuits (spends QPU time)")
    parser.add_argument("--min-remaining-seconds", type=float, default=DEFAULT_MIN_REMAINING_S)
    parser.add_argument(
        "--shots",
        type=_positive_int,
        default=SHOTS,
        help=(
            f"shots per circuit; ODR needs at least {ODR_MIN_SHOTS}; "
            f"--twirl submission needs at least {TWIRLING_RANDOMIZATIONS * TWIRLING_MIN_SHOTS_PER_RANDOMIZATION} "
            f"and a multiple of {TWIRLING_RANDOMIZATIONS}"
        ),
    )
    parser.add_argument(
        "--replica-floor",
        type=_fraction,
        help=(
            "place a disjoint replica only while its layout score is at least this fraction of the best, for every "
            f"group; default each group's declared floor, else {DEFAULT_REPLICA_FLOOR}"
        ),
    )
    parser.add_argument(
        "--max-replicas", type=_positive_int, help="cap on disjoint replicas per group; default fills the device"
    )
    parser.add_argument(
        "--isolated-reference",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="run each replicated group's primary alone on replica 0 as the crosstalk reference",
    )
    parser.add_argument(
        "--twirl",
        action="store_true",
        help="Pauli-twirl gates and measurements on static submission batches; dynamic batches remain disabled",
    )
    parser.add_argument(
        "--dd",
        choices=("XX", "XpXm", "XY4"),
        help="apply dynamical decoupling to static submission batches; dynamic batches remain disabled",
    )
    parser.add_argument("--collect", type=Path, help="run directory whose submitted jobs to collect")
    args = parser.parse_args(argv)
    if args.submit and not args.out:
        parser.error("--submit needs --out so the job ids land in an audit record")
    service = QiskitRuntimeService()
    try:
        if args.collect:
            collect(service, args.collect)
            return 0
        now = datetime.now(UTC)
        args.started = now.isoformat(timespec="microseconds")
        # Microsecond names and exclusive creation keep concurrent runs from
        # sharing a directory.
        run_dir = args.out / now.strftime("%Y-%m-%dT%H%M%S.%fZ") if args.out else None
        choices, record = plan(service, args)
        evaluate(choices, record)
        if run_dir:
            run_dir.mkdir(parents=True, exist_ok=False)
            write_archive(run_dir, choices)
            write_json(run_dir, record)
        if args.submit and run_dir:
            try:
                submit(
                    service,
                    choices,
                    args,
                    record,
                    lambda: write_archive(run_dir, choices),
                    lambda: write_json(run_dir, record),
                )
            finally:
                write_json(run_dir, record)
    except LiveRunError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


def _replace_atomically(target: Path, write: Callable[[Any], None], mode: str) -> None:
    """Write beside target, fsync, and os.replace over it: an interruption leaves the old file whole."""
    tmp = target.with_name(target.name + ".tmp")
    with open(tmp, mode) as handle:
        write(handle)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)
    directory_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def write_archive(run_dir: Path, choices: list[Choice]) -> str:
    """Write the packed execution circuits and return the exact QPY-file digest."""
    archived = []
    for choice in choices:
        for entry in choice.entries:
            named = copy.copy(entry.packed)
            named.name = entry.name
            archived.append(named)
    buffer = io.BytesIO()
    qpy.dump(archived, buffer)
    qpy_bytes = buffer.getvalue()
    _replace_atomically(run_dir / "isa.qpy", lambda handle: handle.write(qpy_bytes), "wb")
    return hashlib.sha256(qpy_bytes).hexdigest()


def write_json(run_dir: Path, record: dict[str, Any]) -> None:
    """The run's JSON record."""
    text = json.dumps(record, indent=2, default=str) + "\n"
    _replace_atomically(run_dir / "record.json", lambda handle: handle.write(text), "w")
    print(f"audit record: {run_dir}")


if __name__ == "__main__":
    sys.exit(main())

"""Discover live systems, adapt packed circuits, simulate, and submit safely.

Each plan refreshes every requested backend once, derives logical requirements
from the source circuits, removes degraded qubits and CZ couplers from the
routing Target, and validates every routed instruction against the original
fresh Target. Seeded candidates rank by gate, readout, duration, and coherence
calibration. The winners that share a backend and execution kind draw replicas
from one placement pool, so corresponding members can share a Runtime PUB on
disjoint hardware. Each packed member and optional group-isolated reference
component then receives final Target validation.

An explicit `--replica-floor` governs every group; otherwise each group's
declared floor applies, with 0.9 as the default. Before submission, the runner
repeats discovery and deterministic selection across all viable systems. Any
change to the approved backend, layout, replica placement, execution circuits,
capabilities, or used calibration values rewrites the submit-free plan and
stops for a renewed written case and user approval. An unchanged plan is
fused by member index into static or dynamic client-side Sampler jobs under the
documented 10-million-execution job bound. Every job receives another hardware
refresh. The QPY digest, complete PUB manifest, effective options,
recovery tags, attempt marker, and returned job identifier reach durable
storage in that order. Collection verifies the ledger and archive, recovers
response-lost job identifiers, and replays each logical component under its
fused PUB's execution-time calibration.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import heapq
import io
import json
import math
import os
import subprocess
import sys
import time
from collections import OrderedDict
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import rustworkx as rx
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import ControlFlowOp, ParameterExpression
from qiskit.converters import circuit_to_dag
from qiskit.exceptions import QiskitError
from qiskit.providers import BackendV2, Options
from qiskit.transpiler import Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime.executor_sampler import Sampler

import correction_collection
import local_compute
import packing
import parallel
import placement_feasibility
import qpu_planning
import variance
from coherence_window import COHERENCE_PRECISION
from diagnostic_experiments import FAMILY_NAMES, N21_FAMILIES, PATCH_FAMILIES, record_groups
from experiments import (
    MIRROR_SUFFIX,
    Group,
    Member,
    all_experiment_groups,
    experiment_groups,
    standalone_campaign_groups,
    tvd,
)
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
MAX_JOB_EXECUTIONS = 10_000_000
RECORD_SCHEMA_VERSION = 7
RECORD_SCHEMA_CONTRACT = "live-target-statistical-design-invocation-budget-v1"
CONTROL_FLOW_OPERATIONS = frozenset({"if_else", "while_loop", "for_loop", "switch_case", "break_loop", "continue_loop"})
DIRECT_TARGET_OPERATIONS = CONTROL_FLOW_OPERATIONS | {"delay", "measure", "reset", "store"}
# A replica is placed only while its layout score stays at least this fraction
# of the best placement's, so packing fills the device with near-best hardware.
DEFAULT_REPLICA_FLOOR = 0.9
# The unpacked copy of a group's primary member on replica 0's qubits. All
# groups' copies share one reference PUB, so the comparison is between the
# global packed and global replica-0 workloads.
ISOLATED_SUFFIX = "_isolated"
# Combinations of routed candidates the joint-placement search tries before
# it stops: each attempt packs every group's entries, and a calibration that
# rejects the best combinations would otherwise walk a frontier of hundreds
# of thousands for hours.
FUSION_MAX_ATTEMPTS = 256

EXPERIMENT_SOURCE_MANIFEST = (
    "aer_identity.py",
    "aer_resources.py",
    "algebra_planning.py",
    "affine_residual.py",
    "boolean_anf.py",
    "cd_core.py",
    "correction_circuits.py",
    "correction_collection.py",
    "correction_planning.py",
    "correction_schedule.py",
    "correction_statistics.py",
    "designs.py",
    "diagnostic_experiments.py",
    "dynamic_density.py",
    "experiment_optimizer.py",
    "experiments.py",
    "factoring.py",
    "hybrid_shor.py",
    "integral_homology.py",
    "jax_bridge.py",
    "live_run.py",
    "local_compute.py",
    "maximal_experiments.py",
    "modular_arithmetic.py",
    "n21_exact_planning.py",
    "native_preflight.py",
    "order_finding.py",
    "packing.py",
    "parallel.py",
    "placement_feasibility.py",
    "predict.py",
    "pub_shot_allocation.py",
    "qpe_diagnostics.py",
    "patch_characterization.py",
    "coherence_window.py",
    "conditional_ramsey.py",
    "crossed_tile_template.py",
    "diagnostic_controls.py",
    "qpu_cases.py",
    "qpu_planning.py",
    "qubit_baseline.py",
    "rank_attachments.py",
    "rank_charts.py",
    "rank_polynomials.py",
    "rank_path_topology.py",
    "rank_sector_contracts.py",
    "rank_sector_experiments.py",
    "ripple_contracts.py",
    "ripple_dynamics.py",
    "ripple_experiments.py",
    "runtime_contracts.py",
    "select_lcu.py",
    "star_ramsey.py",
    "target_flip.py",
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
    dynamic_circuits: bool
    operation_names: tuple[str, ...]
    control_flow: tuple[str, ...]

    @property
    def native_cz(self) -> bool:
        return "cz" in self.operation_names

    def summary(self) -> dict[str, Any]:
        return {
            "num_qubits": self.num_qubits,
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
    identity: dict[str, Any] = field(default_factory=dict)

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
            **self.identity,
            "capabilities": self.capabilities.summary(),
            "repetition_delay": _optional_repetition_delay(self.backend),
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
        dynamic_circuits="dynamic_circuits" in supported_features,
        operation_names=operation_names,
        control_flow=tuple(sorted(CONTROL_FLOW_OPERATIONS.intersection(operation_names))),
    )


# Provenance fields of a backend summary: recorded data that neither selection
# reuse (unchanged_since_planning) nor the approved-record comparison reads.
BACKEND_IDENTITY_FIELDS = ("backend_version", "processor_type")


def backend_identity(backend: Any) -> dict[str, Any]:
    """The backend's reported version and processor type, as its configuration carries them.

    IBMBackend.refresh() replaces the configuration but leaves the
    BackendV2.backend_version read at construction, so both values come from
    backend.configuration(). processor_type is the configuration's
    {"family", "revision"[, "segment"]} dictionary, or None when the backend
    reports none.
    """
    configuration = backend.configuration()
    processor = getattr(configuration, "processor_type", None)
    return {
        "backend_version": str(configuration.backend_version),
        "processor_type": {str(k): str(v) for k, v in processor.items()} if isinstance(processor, Mapping) else None,
    }


def reported_identity(backend: Any) -> dict[str, Any]:
    """backend_identity, with None for each field a backend object does not report.

    Identity is provenance: a backend without it stays eligible in a snapshot
    and a collection proceeds.
    """
    try:
        return backend_identity(backend)
    except AttributeError:
        return dict.fromkeys(BACKEND_IDENTITY_FIELDS)


def execution_identity(backend: Any, properties_at: Mapping[datetime, Any]) -> dict[str, Any]:
    """A collected job's backend identity: the configuration now and the properties at each execution start.

    The properties in force when a PUB's shots began report the
    backend_version that ran them; the configuration read at collection names
    the processor type and the current version; a property set without a
    version records None.
    """
    identity = reported_identity(backend)
    at_execution = {}
    for start, properties in sorted(properties_at.items()):
        version = getattr(properties, "backend_version", None)
        at_execution[start.isoformat()] = None if version is None else str(version)
    return identity | {"backend_version_at_execution": at_execution}


def backend_identity_violations(entry: Mapping[str, Any]) -> list[str]:
    """Shape faults of the identity fields one record entry carries; an absent field is no fault.

    backend_version is None or a nonempty string; processor_type is None or a
    string-valued dictionary naming at least the family and the revision.
    """
    faults = []
    version = entry.get("backend_version")
    if version is not None and not (isinstance(version, str) and version):
        faults.append(f"backend_version {entry['backend_version']!r} is not a nonempty string")
    processor = entry.get("processor_type")
    if processor is not None and not (
        isinstance(processor, Mapping)
        and {"family", "revision"} <= set(processor)
        and all(isinstance(key, str) and isinstance(value, str) for key, value in processor.items())
    ):
        faults.append(f"processor_type {processor!r} is not a string dictionary with family and revision")
    return faults


def _qubit_exclusion(text: str) -> tuple[str, frozenset[int]]:
    """Parse BACKEND:Q[,Q|A-B...] into the backend name and its excluded physical qubits."""
    backend_name, separator, spec = text.partition(":")
    if not separator or not backend_name or not spec:
        raise argparse.ArgumentTypeError(f"expected BACKEND:Q[,Q|A-B...], got {text!r}")
    qubits: set[int] = set()
    try:
        for part in spec.split(","):
            low, dash, high = part.partition("-")
            first, last = int(low), int(high) if dash else int(low)
            if first < 0 or last < first:
                raise ValueError(part)
            qubits.update(range(first, last + 1))
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid qubit list {spec!r}") from error
    return backend_name, frozenset(qubits)


def take_snapshot(service: QiskitRuntimeService, name: str, operator_excluded: Collection[int] = ()) -> Snapshot:
    """Fresh status, Target, and properties for one backend, with the exclusion policy applied.

    operator_excluded names qubits the operator withholds from placement whatever
    their reported calibration (--exclude-qubits), recorded as "operator
    exclusion" beside the calibration exclusions.
    """
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
    identity = reported_identity(backend)
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
        identity=identity,
    )
    if "cz" not in backend.target.operation_names:
        return snap
    faulty_q = set(props.faulty_qubits())
    faulty_edges = {tuple(g.qubits) for g in props.faulty_gates() if g.gate == "cz"}
    # A faulty single-qubit instruction (sx, x, measure) on an operational
    # qubit still makes that qubit unusable for these circuits.
    faulty_gate_q = {q: g.gate for g in props.faulty_gates() if g.gate != "cz" for q in g.qubits}
    t1s, t2s, ros, czs = [], [], [], []
    unknown = sorted(q for q in operator_excluded if not 0 <= q < backend.num_qubits)
    if unknown:
        raise LiveRunError(f"{name}: --exclude-qubits names qubits {unknown} outside 0..{backend.num_qubits - 1}")
    for q in range(backend.num_qubits):
        reason = f"faulty {faulty_gate_q[q]}" if q in faulty_gate_q else _qubit_reason(props, q, faulty_q)
        if reason is None and q in operator_excluded:
            reason = "operator exclusion"
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
    return violations


def group_admission_violations(group: Group, capabilities: BackendCapabilities) -> list[str]:
    """Capability violations of one source-circuit group, naming the members of a mixed group's minority kind.

    select_candidates, qpu_planning.prepare and the pre-submit refresh
    (choice_change_reasons) apply this one predicate to the source members, so
    a group the refresh rejects never reaches a planned record. Routing can
    serialize independent operations in another order, so a routed ISA can
    classify static where its source circuit classifies dynamic.
    """
    violations = capability_violations(group_requirements(group), capabilities)
    kinds: dict[str, list[str]] = {"dynamic": [], "static": []}
    for member in group.members:
        kinds["dynamic" if _is_dynamic(member.circuit) else "static"].append(member.name)
    if kinds["dynamic"] and kinds["static"]:
        minority = "dynamic" if len(kinds["dynamic"]) <= len(kinds["static"]) else "static"
        violations.append(f"{minority} members {kinds[minority]}")
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
    return _excluded_operations(isa, snap.excluded_qubits, snap.excluded_edges)


def _excluded_operations(isa: QuantumCircuit, excluded_qubits: Any, excluded_edges: Any) -> list[str]:
    """Every excluded qubit and CZ edge isa touches."""
    bad = []
    for name, qargs in _ops(isa):
        bad += [f"qubit {q}" for q in qargs if q in excluded_qubits]
        if name == "cz" and (qargs in excluded_edges or tuple(reversed(qargs)) in excluded_edges):
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
    """One logical result entry and the packed replicas that become a fused-PUB component.

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
    # Different groups keep one CZ hop between their replicas, the
    # one-hop crosstalk window of multi-programming placement
    # (literature/notes/2102.05321.md); off, groups are only disjoint.
    cross_group_buffer: bool = True


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
    fusion_index: int | None = None


@dataclass(frozen=True)
class PubComponent:
    """One logical entry inside a fused Runtime PUB."""

    choice: Choice
    entry: Entry
    register_prefix: str

    def manifest(self) -> dict[str, Any]:
        registers_by_replica = [
            [self.register_prefix + name for name in packing.registers(self.entry.packed, replica_prefix)]
            for replica_prefix in self.entry.prefixes
        ]
        if any(not register_names for register_names in registers_by_replica):
            raise LiveRunError(f"{self.entry.name}: fused component has a replica without result registers")
        return {
            "group": self.choice.group.name,
            "member": self.entry.name,
            "reference": self.entry.reference,
            "register_prefix": self.register_prefix,
            "physical_qubits": sorted({qubit for replica in self.entry.replica_qubits for qubit in replica}),
            "registers_by_replica": registers_by_replica,
        }


@dataclass(frozen=True)
class ExecutionPub:
    """One submitted PUB and the logical entries decoded from its namespaced registers."""

    name: str
    backend: str
    kind: str
    circuit: QuantumCircuit
    components: tuple[PubComponent, ...]

    def manifest(self) -> dict[str, Any]:
        target = self.components[0].choice.snap.backend.target
        streams = [replica for component in self.components for replica in component.entry.replicas]
        return {
            "name": self.name,
            "backend": self.backend,
            "kind": self.kind,
            "target_gate_lower_bound_dt": target_duration_dt(self.circuit, target),
            "feed_forward_operation_count": _control_flow_count(self.circuit),
            "sequential_stage_count": max((_feed_forward_stages(replica) for replica in streams), default=0),
            "parallel_stream_count": sum(
                len(component.entry.replicas)
                for component in self.components
                if _has_feed_forward(component.entry.replicas[0])
            ),
            "components": [component.manifest() for component in self.components],
        }


@dataclass
class _FusionPlacementPool:
    """Candidate embeddings and selected replicas for one group in a shared device pool."""

    choice: Choice
    graph: Any
    candidates: list[Replica]
    original_index: int
    pattern_width: int
    bases: list[tuple[str, QuantumCircuit, np.ndarray, np.ndarray | None]] | None = None
    selected: list[Replica] = field(default_factory=list)
    blocked: set[int] = field(default_factory=set)
    physical_graph: Any = None
    # Qubits other groups' placed replicas forbid to this group: their
    # physical CZ footprints when the cross-group buffer is on.
    foreign: set[int] = field(default_factory=set)


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


class CompilePanic(ValueError):
    """A Rust panic inside the transpiler, reported as one compile failure of one backend and seed."""


def _compile(qc: QuantumCircuit, snap: Snapshot, seed: int, layout: list[int] | None = None) -> QuantumCircuit:
    """Transpile qc onto the snapshot's admission Target.

    Qiskit's Rust passes raise pyo3's PanicException, a BaseException, on some
    fragmented admission Targets (a backend whose calibration excludes most
    qubits); it becomes CompilePanic, a ValueError, so candidate selection
    records it for that backend and seed and goes on with the others.
    """
    if snap.admission_target is None:
        snap.admission_target = build_admission_target(snap)
    try:
        return transpile(
            qc,
            backend=snap.backend,
            target=snap.admission_target,
            optimization_level=OPT_LEVEL,
            seed_transpiler=seed,
            initial_layout=layout,
        )
    except BaseException as error:
        if type(error).__name__ != "PanicException":
            raise
        raise CompilePanic(f"{snap.name}: transpiler panic ({error})") from None


def component_layouts(snap: Snapshot, width: int) -> list[list[int]]:
    """Connected initial layouts, one inside each placeable component that holds width qubits.

    Sabre layout panics (petgraph capacity overflow) on an admission Target
    whose placeable qubits form small islands, as an operator exclusion that
    leaves a few tiles does, while routing from a fixed layout inside one
    connected component stays within it. Each component contributes its
    first width qubits in breadth-first order from its lowest index, with
    neighbours visited in ascending order, so the layout is connected and
    deterministic; node indices are physical qubits.
    """
    if snap.admission_target is None:
        snap.admission_target = build_admission_target(snap)
    placeable = packing.coupling_graph(snap.admission_target, snap.backend.num_qubits)
    placeable.remove_nodes_from(sorted(snap.excluded_qubits))
    layouts = []
    for component in sorted(rx.connected_components(placeable), key=min):
        if len(component) < width:
            continue
        order, frontier = [min(component)], [min(component)]
        while frontier and len(order) < width:
            node = frontier.pop(0)
            for neighbour in sorted(placeable.neighbors(node)):
                if neighbour not in order:
                    order.append(neighbour)
                    frontier.append(neighbour)
        layouts.append(order[:width])
    return layouts


def _compile_primary(qc: QuantumCircuit, snap: Snapshot, seed: int) -> QuantumCircuit:
    """_compile with Sabre's own layout, or from component_layouts when that layout panics."""
    try:
        return _compile(qc, snap, seed)
    except CompilePanic:
        for layout in component_layouts(snap, qc.num_qubits):
            try:
                return _compile(qc, snap, seed, layout)
            except (QiskitError, ValueError):
                continue
        raise


def _bind(isa: QuantumCircuit, member: Member) -> QuantumCircuit:
    """Bind the shared ISA while preserving its exact compiled global phase.

    Qiskit circuit substitution can expand a compiled multi-parameter global
    phase during successive assignments. Binding that expression simultaneously
    avoids the expansion and retains the phase required by operator checks.
    """
    binding = member.binding
    if not binding:
        return isa
    phase = isa.global_phase
    if not isinstance(phase, ParameterExpression) or not phase.parameters.intersection(binding):
        return isa.assign_parameters(binding)
    if any(not isa.has_parameter(parameter) for parameter in binding):
        # Preserve Qiskit's strict rejection of parameters absent from the ISA.
        return isa.assign_parameters(binding)
    bound = isa.copy()
    bound_phase = phase.bind(binding, allow_unknown_parameters=True)
    bound.global_phase = bound_phase if bound_phase.parameters else float(bound_phase)
    gate_binding = {parameter: value for parameter, value in binding.items() if bound.has_parameter(parameter)}
    if gate_binding:
        bound.assign_parameters(gate_binding, inplace=True)
    return bound


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


def target_duration_dt(isa: QuantumCircuit, target: Any) -> int:
    """The Target-derived critical-path duration in dt, the gate-time lower bound for one execution.

    The backend scheduler's circuit_duration for the same PUB adds what the
    Target omits. Their difference, the scheduler residual, collects
    feed-forward, alignment, measurement, reset, and controller time on a
    dynamic PUB. Static and dynamic circuits run in separate jobs and no
    static PUB is a schedule-matched copy of a dynamic one, so a static
    residual from the same submission bounds the scheduler's alignment on a
    different circuit and attributes nothing; attribution waits for a matched
    dynamic/control pair in one job.
    """
    return int(_gate_time_view(isa).estimate_duration(target, unit="dt"))


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

    ODR requires a unitary forward half. A reset, control-flow branch, or
    mid-circuit measurement makes the circuit non-unitary, so dynamic circuits
    use an explicit schedule-matched null instead of a mirror twin.

    The cut is the layer near the depth midpoint whose twin best matches the
    witness in both scheduled depth and CZ count, the idle and two-qubit
    exposures whose attenuation the twin measures. The twin runs on isa's
    physical qubits and ideally returns all zeros, so its measured <Z> is the
    attenuation a witness's <Z> is divided by (literature/notes/2507.08088.md,
    Sec. IV A 3). The forward half keeps isa's gates unchanged on the trivial
    layout, and the barrier keeps the halves from cancelling.
    """
    if _is_dynamic(isa):
        raise LiveRunError(
            f"{name}: ODR mirror requires a unitary static circuit; "
            "control flow, reset, or mid-circuit measurement has no circuit inverse"
        )
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


def _replica_candidates(snap: Snapshot, isas: list[QuantumCircuit], floor: float) -> tuple[Any, list[Replica], int]:
    """Return the admitted graph and every floor-qualified embedding of one group's pattern.

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

    matched_x: tuple[int, int] | None = None
    if any(isa.name.startswith("spectator_wavefront_") for isa in isas):
        from maximal_experiments import core_x_duration_dt

        act_isa = next(isa for isa in isas if isa.name == "spectator_wavefront_active")
        driven = [act_isa.find_bit(inst.qubits[0]).index for inst in act_isa.data if inst.operation.name == "x"]
        if not driven:
            raise LiveRunError("the spectator active arm compiled without an X on its core")
        matched_x = (driven[0], core_x_duration_dt(target, driven[0]))

    judge = PlacementJudge(
        tuple(isas),
        target,
        frozenset(snap.excluded_qubits),
        frozenset(snap.excluded_edges),
        matched_x_duration=matched_x,
    )
    # Embeddings that touch an excluded qubit fail the judge, so the search runs on
    # the placeable qubits only; node indices stay physical. An edgeless pattern
    # otherwise enumerates every ordered tuple of the whole device.
    placeable = graph.copy()
    placeable.remove_nodes_from(sorted(snap.excluded_qubits))
    candidates = packing.candidate_replicas(used, edges, placeable, judge, floor, parallel.ordered_map)
    return graph, candidates, len(used)


@dataclass(frozen=True)
class PlacementJudge:
    """Admissibility and layout score of one embedding, picklable for parallel placement.

    An embedding is admissible when every moved circuit avoids excluded qubits
    and edges and passes the exact Target check (compiled_violations); its
    score is the layout score of the moved primary circuit.
    """

    isas: tuple[QuantumCircuit, ...]
    target: Any
    excluded_qubits: frozenset[int]
    excluded_edges: frozenset[tuple[int, int]]
    matched_x_duration: tuple[int, int] | None = None
    static_checks: tuple[tuple[str, tuple[int, ...], tuple[Any, ...]], ...] | None = field(
        default=None, init=False, repr=False
    )
    static_operations: tuple[tuple[str, tuple[int, ...]], ...] = field(default=(), init=False, repr=False)

    def __post_init__(self) -> None:
        """Retain exact scalar parameter checks once across shared static templates."""
        if not self.isas or len({isa.num_qubits for isa in self.isas}) != 1:
            return
        checks: list[tuple[str, tuple[int, ...], tuple[Any, ...]]] = []
        seen: set[tuple[Any, ...]] = set()
        for isa in self.isas:
            if _is_dynamic(isa):
                return
            for instruction in isa.data:
                operation = instruction.operation
                if operation.name == "barrier":
                    continue
                parameters = tuple(operation.params)
                if any(
                    type(parameter) not in (bool, int, float, str)
                    or isinstance(parameter, float)
                    and not math.isfinite(parameter)
                    for parameter in parameters
                ):
                    return
                qubits = tuple(isa.find_bit(qubit).index for qubit in instruction.qubits)
                key = (operation.name, qubits, tuple((type(parameter), parameter) for parameter in parameters))
                if key not in seen:
                    seen.add(key)
                    checks.append((operation.name, qubits, parameters))
        operations = tuple(dict.fromkeys(operation for isa in self.isas for operation in _ops(isa)))
        object.__setattr__(self, "static_checks", tuple(checks))
        object.__setattr__(self, "static_operations", operations)

    def _static_score(self, mapping: dict[int, int]) -> float | None:
        """Check the same complete remapping as relabel without cloning every arm."""
        width = self.isas[0].num_qubits
        targets = set(mapping.values())
        spare_sources = [qubit for qubit in range(width) if qubit not in mapping]
        spare_targets = [qubit for qubit in range(width) if qubit not in targets]
        permutation = [0] * width
        for source, target in mapping.items():
            permutation[source] = target
        for source, target in zip(spare_sources, spare_targets, strict=True):
            permutation[source] = target
        for name, original in self.static_operations:
            moved = tuple(permutation[qubit] for qubit in original)
            if any(qubit in self.excluded_qubits for qubit in moved):
                return None
            if name == "cz" and (moved in self.excluded_edges or tuple(reversed(moved)) in self.excluded_edges):
                return None
        if self.static_checks is None:
            raise LiveRunError("static placement checks were not prepared")
        for name, original, parameters in self.static_checks:
            moved = tuple(permutation[qubit] for qubit in original)
            if not self.target.instruction_supported(operation_name=name, qargs=moved, parameters=list(parameters)):
                return None
        return layout_score(packing.relabel(self.isas[0], mapping, ""), self.target)

    def __call__(self, mapping: dict[int, int]) -> float | None:
        if self.matched_x_duration is not None:
            from maximal_experiments import core_x_duration_dt

            # A replica core must drive with the routed core's X duration, which
            # the rebuilt arms subtract from the core's exposure delays.
            src_core, exp_dt = self.matched_x_duration
            if src_core in mapping and core_x_duration_dt(self.target, mapping[src_core]) != exp_dt:
                return None
        if self.static_checks is not None:
            return self._static_score(mapping)
        moved = [packing.relabel(isa, mapping, "") for isa in self.isas]
        for isa in moved:
            if _excluded_operations(isa, self.excluded_qubits, self.excluded_edges) or target_violations(
                isa, self.target
            ):
                return None
        return layout_score(moved[0], self.target)


def place_replicas(snap: Snapshot, isas: list[QuantumCircuit], floor: float, policy: ReplicaPolicy) -> list[Replica]:
    """Disjoint placements of the group's compiled pattern on snap, best layout score first.

    The pattern is every qubit and CZ edge the group's circuits touch, mirror
    twins included, so one mapping moves every member consistently. A
    placement is admissible when every moved operation exists in the Target
    and avoids excluded qubits and edges; the score is the layout score of the
    moved primary circuit, so ranking reads the same calibration as selection.
    """
    graph, candidates, _ = _replica_candidates(snap, isas, floor)
    chosen: list[Replica] = []
    blocked: set[int] = set()
    for candidate in candidates:
        if policy.max_replicas is not None and len(chosen) >= policy.max_replicas:
            break
        qubits = set(candidate.qubits)
        if qubits & blocked:
            continue
        chosen.append(Replica(len(chosen), candidate.mapping, candidate.score))
        blocked |= qubits | {neighbor for qubit in qubits for neighbor in graph.neighbors(qubit)}
    replicas = chosen
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


def _entry_bases(choice: Choice) -> list[tuple[str, QuantumCircuit, np.ndarray, np.ndarray | None]]:
    """Stable non-reference entry definitions for initial and joint placement.

    A mirror twin is cut from the member's single-copy ISA. The later entry
    builder packs the member and twin on identical replicas so corresponding
    samples retain their physical-qubit pairing.
    """
    if choice.entries:
        return [(entry.name, entry.base, entry.ideal, entry.weights) for entry in choice.entries if not entry.reference]
    bases: list[tuple[str, QuantumCircuit, np.ndarray, np.ndarray | None]] = []
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        bases.append((member.name, isa, member.ideal, member.weights))
        if member.mirror:
            name = member.name + MIRROR_SUFFIX
            zeros = np.zeros(2**member.circuit.num_clbits)
            zeros[0] = 1.0
            bases.append((name, mirror_isa(isa, choice.snap.backend, name), zeros, None))
    return bases


def _set_entries(
    choice: Choice,
    replicas: list[Replica],
    policy: ReplicaPolicy,
    bases: list[tuple[str, QuantumCircuit, np.ndarray, np.ndarray | None]] | None = None,
) -> Choice:
    """Rebuild one group's logical entries on an already admitted replica set.

    bases, the group's single-copy entry definitions with their mirror twins,
    is computed once per routed candidate when the caller passes it, since the
    twins come from the transpiler.
    """
    bases = _entry_bases(choice) if bases is None else bases
    choice.replica_floor = replica_floor(choice.group, policy)
    choice.replicas = replicas
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


def build_entries(choice: Choice, policy: ReplicaPolicy) -> Choice:
    """Build one group's independently placed logical entries for candidate selection."""
    bases = _entry_bases(choice)
    floor = replica_floor(choice.group, policy)
    replicas = place_replicas(choice.snap, [base[1] for base in bases], floor, policy)
    return _set_entries(choice, replicas, policy)


def _placement_footprint(pool: _FusionPlacementPool, replica: Replica, graph: Any | None = None) -> set[int]:
    """Replica qubits plus their CZ neighbors in graph (the cluster's admitted graph when None).

    The within-group footprint reads the admitted graph that routing sees;
    the cross-group buffer reads the device's physical CZ graph
    (pool.physical_graph), since a coupler the quality policy excluded still
    couples its endpoints.
    """
    qubits = set(replica.qubits)
    source = pool.graph if graph is None else graph
    return qubits | {neighbor for qubit in qubits for neighbor in source.neighbors(qubit)}


def physical_cz_graph(snapshot: Snapshot) -> Any:
    """The backend's full two-qubit coupling graph, excluded couplers included."""
    graph = rx.PyGraph()
    graph.add_nodes_from(range(snapshot.backend.target.num_qubits))
    edges = {tuple(sorted(edge)) for edge in snapshot.backend.target.build_coupling_map().get_edges()}
    graph.add_edges_from_no_data(sorted(edges))
    return graph


def _choice_execution_kind(choice: Choice) -> str:
    """Classify a routed candidate before placement or its exact packed entries afterward."""
    circuits = [entry.packed for entry in choice.entries] if choice.entries else choice.isas
    if not circuits:
        raise LiveRunError(f"{choice.group.name}: execution-kind classification received no circuits")
    kinds = {"dynamic" if _is_dynamic(circuit) else "static" for circuit in circuits}
    if len(kinds) != 1:
        raise LiveRunError(f"{choice.group.name}: one result group mixes static and dynamic circuits")
    return next(iter(kinds))


def _placement_assignment(
    pools: list[_FusionPlacementPool], occupied: set[int], replicas_per_pool: int = 1, buffer: bool = True
) -> list[tuple[_FusionPlacementPool, Replica]] | None:
    """Search all required replicas together, including alternatives to earlier placements.

    Increasing candidate indices within a pool remove permutations of the same
    replica set without removing any feasible set. The most constrained pool
    advances first. Candidate multiplicities remain in that heuristic.
    Equal-qubit-set branches retain only their first candidate: its earlier
    index permits every continuation available to a later equivalent
    candidate. A failed first branch therefore proves those branches fail.
    Pool state changes only after a complete assignment exists.
    Placed qubits are forbidden to every pool. A placed replica's admitted
    footprint is forbidden to its own pool, so a group's replicas stay one
    hop apart on the graph routing sees; with buffer, its physical footprint
    is forbidden to every other pool, so groups stay one hop apart on the
    device's couplers, an excluded coupler included.
    """
    qubits = [[frozenset(candidate.qubits) for candidate in pool.candidates] for pool in pools]
    footprints = [[_placement_footprint(pool, candidate) for candidate in pool.candidates] for pool in pools]
    physical_footprints = [
        [_placement_footprint(pool, candidate, pool.physical_graph) for candidate in pool.candidates] for pool in pools
    ]
    chosen: list[list[int]] = [[] for _ in pools]
    blocked = [set(pool.blocked) | pool.foreign for pool in pools]
    domains = [
        placement_feasibility.PlacementDomain(
            tuple(
                placement_feasibility.PlacementFootprint(physical_set, frozenset(admitted), frozenset(physical))
                for physical_set, admitted, physical in zip(pool_qubits, pool_footprints, pool_physical, strict=True)
            ),
            frozenset(pool_blocked),
        )
        for pool_qubits, pool_footprints, pool_physical, pool_blocked in zip(
            qubits, footprints, physical_footprints, blocked, strict=True
        )
    ]
    if placement_feasibility.certified_infeasible(domains, frozenset(occupied), replicas_per_pool, buffer):
        return None

    def search(used: set[int]) -> bool:
        available: list[tuple[int, int, int, list[int]]] = []
        for pool_index, pool in enumerate(pools):
            remaining = replicas_per_pool - len(chosen[pool_index])
            if remaining == 0:
                continue
            start = chosen[pool_index][-1] + 1 if chosen[pool_index] else 0
            indices = [
                index
                for index in range(start, len(pool.candidates))
                if not qubits[pool_index][index].intersection(used | blocked[pool_index])
            ]
            if len(indices) < remaining:
                return False
            available.append((len(indices) - remaining, pool.original_index, pool_index, indices))
        if not available:
            return True
        _, _, pool_index, indices = min(available)
        previous = [set(entry) for entry in blocked]
        visited_qubit_sets: set[frozenset[int]] = set()
        for index in indices:
            physical_set = qubits[pool_index][index]
            if physical_set in visited_qubit_sets:
                continue
            visited_qubit_sets.add(physical_set)
            chosen[pool_index].append(index)
            blocked[pool_index] = previous[pool_index] | footprints[pool_index][index]
            if buffer:
                for other in range(len(pools)):
                    if other != pool_index:
                        blocked[other] = previous[other] | physical_footprints[pool_index][index]
            if search(used | qubits[pool_index][index]):
                return True
            chosen[pool_index].pop()
        for position, entry in enumerate(previous):
            blocked[position] = entry
        return False

    if not search(occupied):
        return None
    return [(pool, pool.candidates[index]) for pool, indices in zip(pools, chosen, strict=True) for index in indices]


def _commit_placement_assignment(
    placements: list[tuple[_FusionPlacementPool, Replica]],
    occupied: set[int],
    cluster: list[_FusionPlacementPool] | None = None,
) -> None:
    """Commit a complete assignment and its separation footprints.

    With cluster (the cross-group buffer on), each placed replica's physical
    footprint joins the foreign set of every other pool of the cluster.
    """
    for pool, candidate in placements:
        selected = Replica(len(pool.selected), candidate.mapping, candidate.score)
        pool.selected.append(selected)
        occupied.update(selected.qubits)
        pool.blocked.update(_placement_footprint(pool, selected))
        if cluster is not None:
            physical = _placement_footprint(pool, selected, pool.physical_graph)
            for other in cluster:
                if other is not pool:
                    other.foreign.update(physical)


def allocate_fusion_replicas(
    choices: list[Choice], policy: ReplicaPolicy, cache: dict[tuple[int, float], Any] | None = None
) -> dict[str, Any]:
    """Jointly place every same-backend, same-kind group before cross-group fusion.

    Backtracking searches all required replicas together, revisiting earlier
    placements when a later requirement fails. The required set places two
    replicas when isolated references are enabled, unless --max-replicas=1 explicitly selects the
    single-replica surface. Later rounds advance every group that can still
    participate. A per-group blocked set keeps replicas of that group one CZ
    hop apart; the shared occupied set keeps different groups physically
    disjoint, and with policy.cross_group_buffer each pool's foreign set of
    other groups' physical footprints keeps them one CZ hop apart as well.
    """
    clusters: dict[tuple[str, str], list[tuple[int, Choice]]] = {}
    for choice_index, choice in enumerate(choices):
        kind = _choice_execution_kind(choice)
        clusters.setdefault((choice.snap.name, kind), []).append((choice_index, choice))

    cluster_records: list[dict[str, Any]] = []
    for (backend_name, kind), indexed_choices in clusters.items():
        snapshot = indexed_choices[0][1].snap
        if any(choice.snap is not snapshot for _, choice in indexed_choices):
            raise LiveRunError(f"{backend_name} {kind}: fusion groups do not share one refreshed snapshot object")
        physical = physical_cz_graph(snapshot)
        pools: list[_FusionPlacementPool] = []
        for choice_index, choice in indexed_choices:
            floor = replica_floor(choice.group, policy)
            # Candidate selection retries combinations of the same routed
            # candidates; a shallow-copied trial shares its candidate's isas
            # list, so mirror cuts and embedding scores are computed once per
            # candidate and floor.
            key = (id(choice.isas), floor)
            if cache is not None and key in cache:
                graph, candidates, pattern_width, bases = cache[key]
            else:
                bases = _entry_bases(choice)
                graph, candidates, pattern_width = _replica_candidates(choice.snap, [base[1] for base in bases], floor)
                if cache is not None:
                    cache[key] = (graph, candidates, pattern_width, bases)
            if not candidates:
                raise LiveRunError(
                    f"{backend_name} {kind}: {choice.group.name} has no floor-qualified fusion placement"
                )
            pools.append(
                _FusionPlacementPool(
                    choice, graph, candidates, choice_index, pattern_width, bases, physical_graph=physical
                )
            )

        occupied: set[int] = set()
        cluster_pools: list[_FusionPlacementPool] | None = pools if policy.cross_group_buffer else None
        required_rounds = 2 if policy.isolated_reference and policy.max_replicas != 1 else 1
        assignment = _placement_assignment(pools, occupied, required_rounds, policy.cross_group_buffer)
        if assignment is None:
            diagnostics = {
                pool.choice.group.name: {
                    "pattern_width": pool.pattern_width,
                    "floor_candidates": len(pool.candidates),
                }
                for pool in pools
            }
            raise LiveRunError(
                f"{backend_name} {kind}: cannot satisfy {required_rounds} required joint-placement rounds; "
                f"groups={json.dumps(diagnostics, sort_keys=True)}"
            )

        _commit_placement_assignment(assignment, occupied, cluster_pools)
        allocation_round = required_rounds
        while True:
            under_cap = [
                pool for pool in pools if policy.max_replicas is None or len(pool.selected) < policy.max_replicas
            ]
            eligible = [
                pool
                for pool in under_cap
                if any(
                    not set(candidate.qubits).intersection(occupied | pool.blocked | pool.foreign)
                    for candidate in pool.candidates
                )
            ]
            if not eligible:
                break
            assignment = _placement_assignment(eligible, occupied, 1, policy.cross_group_buffer)
            if assignment is None:
                break
            _commit_placement_assignment(assignment, occupied, cluster_pools)
            allocation_round += 1

        if any(len(pool.selected) < required_rounds for pool in pools):
            missing = {
                pool.choice.group.name: len(pool.selected) for pool in pools if len(pool.selected) < required_rounds
            }
            raise LiveRunError(
                f"{backend_name} {kind}: joint placement left groups below {required_rounds} replicas: {missing}"
            )
        for pool in pools:
            _set_entries(pool.choice, pool.selected, policy, pool.bases)
        cluster_records.append(
            {
                "backend": backend_name,
                "kind": kind,
                "rounds": allocation_round,
                "required_rounds": required_rounds,
                "physical_qubits": sorted(occupied),
                "cross_group_buffer": policy.cross_group_buffer,
                "groups": [
                    {
                        "group": pool.choice.group.name,
                        "pattern_width": pool.pattern_width,
                        "floor_candidates": len(pool.candidates),
                        "selected_replicas": len(pool.selected),
                        "selected_scores": [replica.score for replica in pool.selected],
                        "selected_qubits": [replica.qubits for replica in pool.selected],
                    }
                    for pool in pools
                ],
            }
        )
    return {
        "cross_group_disjoint": True,
        "within_group_one_hop_separated": True,
        "allocation": "required-set-backtracking-then-fair-surplus",
        "clusters": cluster_records,
    }


def _fusion_entry_order(choice: Choice) -> list[Entry]:
    """Primary, shared-PUB replica-0 reference, then remaining entries for aligned fusion rows."""
    if not choice.entries:
        raise LiveRunError(f"{choice.group.name}: fusion received an empty execution set")
    references = [entry for entry in choice.entries if entry.reference]
    if len(references) > 1:
        raise LiveRunError(f"{choice.group.name}: fusion supports one isolated reference, got {len(references)}")
    remaining = [entry for entry in choice.entries[1:] if not entry.reference]
    return [choice.entries[0], *references, *remaining]


def _assign_fusion_indices(choices: list[Choice]) -> None:
    """Persist unique outer-register indices before choices split by backend."""
    assigned = [choice.fusion_index for choice in choices if choice.fusion_index is not None]
    if any(index < 0 for index in assigned) or len(assigned) != len(set(assigned)):
        raise LiveRunError(f"fusion indices must be unique non-negative integers: {assigned}")
    available = (index for index in range(len(choices) + len(assigned)) if index not in assigned)
    for choice in choices:
        if choice.fusion_index is None:
            choice.fusion_index = next(available)


def execution_pubs(choices: list[Choice]) -> list[ExecutionPub]:
    """Fuse corresponding logical entries on each backend and job-kind cluster.

    Row zero aligns every packed primary. Row one aligns every group-isolated
    replica-0 component when the cluster has them, so every comparison uses
    the same global replica-0 reference workload.
    Remaining members and mirrors retain their per-group order. A short group
    simply contributes no component to later rows.
    Explicit group schedules instead use sparse row indices and exclude a
    group's component wherever the schedule leaves the lane idle.
    """
    _assign_fusion_indices(choices)
    clusters: dict[tuple[str, str], list[tuple[int, Choice, dict[int, Entry]]]] = {}
    for choice in choices:
        if choice.fusion_index is None:
            raise LiveRunError(f"{choice.group.name}: fusion index assignment failed")
        if choice.group.execution_rows is None:
            rows = dict(enumerate(_fusion_entry_order(choice)))
        else:
            if any(entry.reference for entry in choice.entries):
                raise LiveRunError(f"{choice.group.name}: explicit execution rows prohibit automatic references")
            if [entry.name for entry in choice.entries] != [member.name for member in choice.group.members]:
                raise LiveRunError(f"{choice.group.name}: explicit execution rows require exact member entries")
            rows = dict(zip(choice.group.execution_rows, choice.entries, strict=True))
        ordered = list(rows.values())
        kinds = {"dynamic" if _is_dynamic(entry.packed) else "static" for entry in ordered}
        if len(kinds) != 1:
            raise LiveRunError(f"{choice.group.name}: one result group mixes static and dynamic circuits")
        clusters.setdefault((choice.snap.name, next(iter(kinds))), []).append((choice.fusion_index, choice, rows))

    pubs: list[ExecutionPub] = []
    for (backend_name, kind), cluster in clusters.items():
        snapshot = cluster[0][1].snap
        if any(choice.snap is not snapshot for _, choice, _ in cluster):
            raise LiveRunError(f"{backend_name} {kind}: fusion groups do not share one refreshed snapshot object")
        explicit_presence = {choice.group.execution_rows is not None for _, choice, _ in cluster}
        if len(explicit_presence) != 1:
            raise LiveRunError(f"{backend_name} {kind}: groups mix explicit and implicit execution rows")
        reference_presence = {any(entry.reference for entry in rows.values()) for _, _, rows in cluster}
        if len(reference_presence) != 1:
            raise LiveRunError(
                f"{backend_name} {kind}: groups mix isolated-reference and non-reference execution surfaces"
            )
        row_indices = sorted({row for _, _, rows in cluster for row in rows})
        for row_index in row_indices:
            components = tuple(
                PubComponent(choice, rows[row_index], f"g{choice_index}_")
                for choice_index, choice, rows in cluster
                if row_index in rows
            )
            name = f"{backend_name}_{kind}_pub_{row_index + 1:02d}"
            circuit = packing.fuse(
                [component.entry.packed for component in components],
                [component.register_prefix for component in components],
                name,
            )
            actual_kind = "dynamic" if _is_dynamic(circuit) else "static"
            if actual_kind != kind:
                raise LiveRunError(f"{name}: fusion changed {kind} components into a {actual_kind} PUB")
            rejected = compiled_violations(circuit, snapshot)
            if rejected:
                raise LiveRunError(f"{name}: fused execution violates {backend_name} Target: {rejected}")
            pubs.append(ExecutionPub(name, backend_name, kind, circuit, components))
    return pubs


def fusion_summary(pubs: list[ExecutionPub]) -> dict[str, Any]:
    """Logical-entry, execution-PUB, and reference cardinalities for the exact fused surface."""
    logical_entries = {"static": 0, "dynamic": 0}
    execution_counts = {"static": 0, "dynamic": 0}
    reference_components = {"static": 0, "dynamic": 0}
    for pub in pubs:
        execution_counts[pub.kind] += 1
        logical_entries[pub.kind] += len(pub.components)
        reference_components[pub.kind] += sum(component.entry.reference for component in pub.components)
    reference_estimand = {
        kind: "global_packed_workload_vs_global_replica0_workload" if reference_components[kind] else None
        for kind in ("static", "dynamic")
    }
    populated_kinds = [kind for kind, count in execution_counts.items() if count]
    referenced_kinds = [kind for kind in populated_kinds if reference_components[kind]]
    if not referenced_kinds:
        strategy = "aligned_members_without_reference"
        combined_estimand = None
    elif len(referenced_kinds) == len(populated_kinds):
        strategy = "aligned_members_with_shared_replica0_reference"
        combined_estimand = "global_packed_workload_vs_global_replica0_workload"
    else:
        strategy = "aligned_members_with_kind_specific_replica0_reference"
        combined_estimand = "available_only_for_kinds_with_shared_replica0_reference"
    return {
        "strategy": strategy,
        "reference_estimand": combined_estimand,
        "reference_estimand_by_kind": reference_estimand,
        "logical_entries": logical_entries,
        "execution_pubs": execution_counts,
        "reference_components": reference_components,
    }


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
            for field_name in ("compile_error", "member_compile_error", "entry_build_error", "duration_mismatch"):
                if field_name in entry:
                    reasons.add(f"{field_name}: {entry[field_name]}")
            for field_name in ("member_rejections", "execution_rejections"):
                for member_name, rejected in entry.get(field_name, {}).items():
                    reasons.update(f"{member_name}: {reason}" for reason in rejected)
        summary[backend_name] = sorted(reasons) or ["no candidate reached final validation"]
    return summary


def select_candidates(group: Group, snaps: list[Snapshot], seeds: int, log: dict[str, Any]) -> list[Choice]:
    """Rank every routed (backend, seed, layout) candidate retained for joint selection."""
    requirements = group_requirements(group)
    candidates: list[Choice] = []
    log[group.name] = {}
    for snap in snaps:
        trace: list[dict[str, Any]] = []
        log[group.name][snap.name] = trace
        capability_rejections = group_admission_violations(group, snap.capabilities)
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
                isa = _compile_primary(primary.circuit, snap, seed)
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
            # Each shared circuit object compiles once per candidate. Bound
            # phase sweeps retain identical routing and measured output sites.
            try:
                templates = {id(primary.circuit): isa}
                isas = []
                if group.name == "spectator_wavefront_ramsey":
                    from maximal_experiments import (
                        build_spectator_wavefront_circuits,
                        core_x_duration_dt,
                        exposure_dt,
                    )

                    target = snap.admission_target or snap.backend.target
                    routed_core = layout[0]
                    cal_x_dt = core_x_duration_dt(target, routed_core)
                    delay_dt = next(
                        int(instruction.operation.duration)
                        for instruction in group.members[1].circuit.data
                        if instruction.operation.name == "delay"
                    )
                    qc_act, qc_ctrl, qc_null = build_spectator_wavefront_circuits(
                        spectator_count=len(group.members[0].circuit.qubits) - 1,
                        delay_dt=delay_dt,
                        x_duration_dt=cal_x_dt,
                    )
                    isa_act = _compile(qc_act, snap, seed, layout)
                    isa_ctrl = _compile(qc_ctrl, snap, seed, layout)
                    isa_null = _compile(qc_null, snap, seed, layout)
                    # Every exposure track of both arms, the driven core included,
                    # must equal delay_dt in both directions.
                    tracks = {
                        f"{arm}_q{qubit}": exposure_dt(isa, qubit, target)
                        for arm, isa in (("active", isa_act), ("control", isa_ctrl))
                        for qubit in layout
                    }
                    mismatched = {name: value for name, value in tracks.items() if value != delay_dt}
                    if mismatched:
                        trace.append(
                            {"seed": seed, "layout": layout, "duration_mismatch": f"delay={delay_dt} {mismatched}"}
                        )
                        continue
                    isas = [isa_act, isa_ctrl, isa_null]
                else:
                    for member in group.members:
                        key = id(member.circuit)
                        if key not in templates:
                            templates[key] = _compile(member.circuit, snap, seed, layout)
                        isas.append(_bind(templates[key], member))
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
            if group.routed_violations is not None:
                compiled_target = snap.admission_target if snap.admission_target is not None else snap.backend.target
                routed_rejections = group.routed_violations(isas, compiled_target)
                if routed_rejections:
                    trace.append({"seed": seed, "layout": layout, "routed_rejections": routed_rejections})
                    continue
            scores = [layout_score(c, snap.backend.target) for c in isas]
            joint = math.exp(sum(math.log(s) for s in scores) / len(scores))
            trace.append({"seed": seed, "joint_score": joint, "layout": layout})
            candidates.append(Choice(group, snap, seed, layout, isas, scores, joint))
    candidates.sort(key=lambda choice: (choice.joint_score, -choice.snap.pending_jobs), reverse=True)
    if candidates:
        return candidates
    failure_summary = _trace_failure_summary(log[group.name])
    raise LiveRunError(
        f"{group.name}: no valid routed candidate; failures={json.dumps(failure_summary, sort_keys=True)}"
    )


def _prepare_individual_candidate(candidate: Choice, log: dict[str, Any], policy: ReplicaPolicy) -> bool:
    """Build and validate one candidate for callers that do not need cross-group fusion."""
    trace = log[candidate.group.name][candidate.snap.name]
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
        return False
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
        return False
    execution_kinds = {"dynamic" if _is_dynamic(entry.packed) else "static" for entry in candidate.entries}
    if len(execution_kinds) != 1:
        trace.append(
            {
                "seed": candidate.seed,
                "layout": candidate.layout,
                "execution_rejections": {"group": ["packed execution set mixes static and dynamic circuits"]},
            }
        )
        return False
    return True


def select(group: Group, snaps: list[Snapshot], seeds: int, log: dict[str, Any], policy: ReplicaPolicy) -> Choice:
    """Best independently placeable candidate for one group."""
    candidates = select_candidates(group, snaps, seeds, log)
    for candidate in candidates:
        if _prepare_individual_candidate(candidate, log, policy):
            return candidate
    failure_summary = _trace_failure_summary(log[group.name])
    raise LiveRunError(
        f"{group.name}: no valid routed and packed candidate; failures={json.dumps(failure_summary, sort_keys=True)}"
    )


def select_fusion_choices(
    candidate_sets: list[list[Choice]], policy: ReplicaPolicy
) -> tuple[list[Choice], dict[str, Any]]:
    """Best-first search of the finite candidate product until joint placement and fusion pass."""
    if not candidate_sets or any(not candidates for candidates in candidate_sets):
        raise LiveRunError("joint fusion selection needs a non-empty candidate set for every group")
    group_names = [candidates[0].group.name for candidates in candidate_sets]
    if len(group_names) != len(set(group_names)) or any(
        candidate.group.name != group_name
        for group_name, candidates in zip(group_names, candidate_sets, strict=True)
        for candidate in candidates
    ):
        raise LiveRunError(f"joint fusion candidate sets have inconsistent group ownership: {group_names}")

    def priority(indices: tuple[int, ...]) -> tuple[float, int, tuple[int, ...]]:
        selected = [candidates[index] for candidates, index in zip(candidate_sets, indices, strict=True)]
        combined_log_score = sum(math.log(candidate.joint_score) for candidate in selected)
        pending_jobs = sum(candidate.snap.pending_jobs for candidate in selected)
        return -combined_log_score, pending_jobs, indices

    initial = tuple(0 for _ in candidate_sets)
    frontier = [priority(initial)]
    queued = {initial}
    attempted = 0
    placement_cache: dict[tuple[int, float], Any] = {}
    rejected_sample: list[dict[str, Any]] = []
    while frontier and attempted < FUSION_MAX_ATTEMPTS:
        negative_score, _, indices = heapq.heappop(frontier)
        selected = [candidates[index] for candidates, index in zip(candidate_sets, indices, strict=True)]
        trial = [copy.copy(candidate) for candidate in selected]
        attempted += 1
        try:
            placement = allocate_fusion_replicas(trial, policy, placement_cache)
            execution_pubs(trial)
        except (LiveRunError, QiskitError, ValueError) as error:
            if len(rejected_sample) < 32:
                rejected_sample.append(
                    {
                        "candidate_indices": list(indices),
                        "reason": f"{type(error).__name__}: {error}",
                    }
                )
        else:
            placement["candidate_selection"] = {
                "strategy": "best_first_combined_log_score",
                "frontier_size": math.prod(len(candidates) for candidates in candidate_sets),
                "attempted_combinations": attempted,
                "rejected_combinations": attempted - 1,
                "rejected_sample": rejected_sample,
                "combined_log_score": -negative_score,
                "selected": [
                    {
                        "group": candidate.group.name,
                        "candidate_index": index,
                        "backend": candidate.snap.name,
                        "seed": candidate.seed,
                        "layout": candidate.layout,
                        "joint_score": candidate.joint_score,
                    }
                    for candidate, index in zip(trial, indices, strict=True)
                ],
            }
            return trial, placement

        for position, candidates in enumerate(candidate_sets):
            if indices[position] + 1 >= len(candidates):
                continue
            neighbor = list(indices)
            neighbor[position] += 1
            neighbor_indices = tuple(neighbor)
            if neighbor_indices in queued:
                continue
            queued.add(neighbor_indices)
            heapq.heappush(frontier, priority(neighbor_indices))

    outcome = "search stopped at FUSION_MAX_ATTEMPTS" if frontier else "frontier exhausted"
    raise LiveRunError(
        f"no jointly placeable fused candidate combination ({outcome}); "
        f"groups={group_names}, frontier={math.prod(len(candidates) for candidates in candidate_sets)}, "
        f"attempted={attempted}, rejected_sample={json.dumps(rejected_sample, sort_keys=True)}"
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


# A snapshot's Target and properties stay fixed for the process, and Aer reads a
# NoiseModel without mutating it, so one model serves every simulator built
# from the same snapshot objects.
_NOISE_MODELS: OrderedDict[tuple[str, int, int], tuple[Any, Any, NoiseModel]] = OrderedDict()


def _noise_model(name: str, view: Any, target: Any, props: Any) -> NoiseModel:
    key = (name, id(target), id(props))
    cached = _NOISE_MODELS.get(key)
    if cached is not None and cached[0] is target and cached[1] is props:
        return cached[2]
    noise = NoiseModel.from_backend(view, readout_error=False)
    for q in range(target.num_qubits):
        try:
            e10, e01 = readout_flips(props, q)
        except Exception:  # BackendPropertyError: no readout calibration at all
            continue
        noise.add_readout_error(ReadoutError([[1.0 - e10, e10], [e01, 1.0 - e01]]), [q])
    _NOISE_MODELS[key] = (target, props, noise)
    while len(_NOISE_MODELS) > local_compute.CACHE_ENTRIES:
        _NOISE_MODELS.popitem(last=False)
    return noise


def noise_simulator(name: str, target: Any, props: Any, compute_policy: dict[str, Any] | None = None) -> AerSimulator:
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
    noise = _noise_model(name, view, target, props)
    # A fixed kernel makes noisy batches independent of the automatic method
    # selector. Aer 0.17.2 miscomputes a reset-only one-bit member following a
    # two-bit feedback member when it switches from statevector to density
    # matrix inside the batch (qpu_planning_contracts verifies the mixed case).
    simulator = AerSimulator.from_backend(view, noise_model=noise, method="density_matrix")
    local_compute.configure(simulator, local_compute.settings() if compute_policy is None else compute_policy)
    return simulator


def simulate(choice: Choice, noise: Any, shots: int = SHOTS) -> dict[str, list[np.ndarray]]:
    """Noisy distribution of every entry's every replica, each simulated as its own single-replica circuit.

    The noise model carries no crosstalk between replicas, so a replica alone
    and a replica inside the packed circuit share one distribution.
    """
    return simulate_entries(noise, choice.entries, shots, SEED_SIMULATOR)


def replay_entries(
    sims: dict[datetime, Any], batches: dict[datetime, list[Entry]], shots: int, seed: int
) -> dict[str, list[np.ndarray]]:
    """Replay every batch under its calibration's noise model, each batch under its own seed.

    Batches run in calibration order and batch k takes seed + k, so entries in
    different batches never share a (seed, batch position) pair and the
    replay is deterministic for one record.
    """
    replayed: dict[str, list[np.ndarray]] = {}
    for offset, calibration in enumerate(sorted(batches)):
        replayed.update(simulate_entries(sims[calibration], batches[calibration], shots, seed + offset))
    return replayed


def simulate_entries(noise: Any, entries: list[Entry], shots: int, seed: int) -> dict[str, list[np.ndarray]]:
    """Noisy distributions of every entry's replicas from one batched Aer run.

    Aer serializes the noise model once per run and derives each experiment's
    seed from seed_simulator and the experiment's position in the batch, so one
    batch in entry order, then replica order, gives every replica its own shot
    draws: the shared replica-0 reference draws independently of packed
    replica 0. Planning batches one choice per call and --collect batches
    one calibration per call (replay_entries), each in a fixed order, so each
    is deterministic for its inputs.
    """
    circuits = [replica for entry in entries for replica in entry.replicas]
    result = local_compute.run(noise, circuits, shots, seed)
    out: dict[str, list[np.ndarray]] = {}
    position = 0
    for entry in entries:
        out[entry.name] = [
            _distribution(result.get_counts(position + k), replica.num_clbits)
            for k, replica in enumerate(entry.replicas)
        ]
        position += len(entry.replicas)
    return out


def readout_corrected(dist: np.ndarray, isa: QuantumCircuit, props: Any, symmetric: bool = False) -> np.ndarray:
    """dist with each classical bit's readout channel inverted, unclipped (readout_inverse)."""
    return np.asarray(readout_inverse(isa, props, symmetric) @ dist)


def readout_inverse(isa: QuantumCircuit, props: Any, symmetric: bool = False) -> np.ndarray:
    """The inverse of the Kronecker product of every classical bit's readout channel.

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
    inverse: np.ndarray = np.ones((1, 1))
    for clbit in reversed(range(isa.num_clbits)):
        e10, e01 = readout_flips(props, writer[clbit])
        if symmetric:
            e10 = e01 = (e10 + e01) / 2.0
        inverse = np.kron(inverse, np.linalg.inv(np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])))
    return inverse


def corrected_covariance(dist: np.ndarray, inverse: np.ndarray) -> np.ndarray:
    """One-shot covariance of inverse @ dist: M (diag(p) - p p^T) M^T for the multinomial law p."""
    return np.asarray(inverse @ (np.diag(dist) - np.outer(dist, dist)) @ inverse.T)


def corrected_summary(
    group: Group, entries: list[Entry], dists: dict[str, list[np.ndarray]], props: Any, symmetric: bool = False
) -> Any:
    """The pooled group summary on readout-inverted replica distributions, or why it is skipped.

    readout_corrected assumes each classical bit passes through its own
    output-only channel. In a feed-forward circuit a misread mid-circuit bit
    changes later quantum evolution, so terminal post-processing cannot recover
    the branch that hardware executed. Such groups report the reason instead of
    a corrected summary. A reset without classical feed-forward does not create
    that dependency by itself. Each replica is inverted with the channels of
    its own readout qubits before the replicas are averaged. props is one
    properties object, or a per-circuit mapping when circuits ran under
    different calibrations.

    The inverted arrays are quasi-probabilities M p, whose one-shot
    covariance is M (diag(p) - p p^T) M^T rather than the multinomial form of
    M p itself; a group that declares summarize_with_covariance receives that
    covariance for every circuit, so its delta-method errors carry the
    inversion.
    """
    runs = [e for e in entries if not e.reference]
    if any(_has_feed_forward(e.replicas[0]) for e in runs):
        return {"skipped": "feed-forward circuit: mid-circuit readout error changes later quantum evolution"}
    propagate = group.summarize_with_covariance is not None
    corrected: dict[str, list[np.ndarray]] = {}
    covariances: dict[str, list[np.ndarray]] = {}
    for e in runs:
        own = props[e.name] if isinstance(props, dict) else props
        inverses = [readout_inverse(rep, own, symmetric) for rep in e.replicas]
        raw = [np.asarray(d, dtype=float) for d in dists[e.name]]
        corrected[e.name] = [np.asarray(m @ d) for m, d in zip(inverses, raw, strict=True)]
        if propagate:
            covariances[e.name] = [corrected_covariance(d, m) for m, d in zip(inverses, raw, strict=True)]
    return _pooled_summaries(group, runs, corrected, covariances if propagate else None)[0]


def _pooled_summaries(
    group: Group,
    runs: list[Entry],
    dists: dict[str, list[np.ndarray]],
    covariances: dict[str, list[np.ndarray]] | None = None,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """The pooled summary and the per-replica summaries of runs' replica distributions.

    covariances carries each replica's one-shot covariance of a readout-inverted
    distribution; a group with summarize_with_covariance summarizes through it.

    Every pooled value is the mean over replicas of that value computed on
    each replica alone, the estimand summary_interval spans. For a ratio, a
    fringe fit, or a TVD this differs from the statistic of averaged
    distributions, and for a mirror-rescaled value it divides each replica's
    witness by that replica's own twin.
    """
    count = len(runs[0].replicas)
    with_covariance = group.summarize_with_covariance
    if covariances is not None and with_covariance is not None:
        per_replica = [
            with_covariance({e.name: dists[e.name][k] for e in runs}, {e.name: covariances[e.name][k] for e in runs})
            for k in range(count)
        ]
    else:
        per_replica = [group.summarize({e.name: dists[e.name][k] for e in runs}) for k in range(count)]
    pooled = {key: float(np.mean([r[key] for r in per_replica])) for key in per_replica[0]}
    return pooled, per_replica


def replica_statistics(
    group: Group,
    entries: list[Entry],
    dists: dict[str, list[np.ndarray]],
    shots: int,
    scope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Pooled, per-replica, interval, variance, global packing, and admission views.

    The pooled summary averages each summary value over the replicas
    (_pooled_summaries), and summary_interval spans it; a value the group
    declares a per-shot rate (Group.rate_keys) also carries its pooled-shot
    Wilson bound. variance decomposes every entry's ideal-weighted score into shot
    and layout variance, and instance_variance adds the instance axis over the
    group's declared instances. global_packing_crosstalk compares packed
    replica 0 with the same group's component in the shared replica-0
    reference PUB. The two PUBs represent the global packed and global
    replica-0 workloads, so the value does not isolate one group's crosstalk.
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
            z = (packed - iso) / sd if sd > 0 else None
            # A detection diagnostic and an equivalence test are different
            # claims: |z| within 3 reads as no difference at this resolution,
            # and only the interval test can bound the cost.
            if z is None:
                resolution = "z diagnostic unavailable: zero per-shot variance in both arms; read the interval"
            elif z < -3:
                resolution = "packed replica 0 scores more than three sigma below the global replica-0 reference"
            elif z > 3:
                resolution = "packed replica 0 scores more than three sigma above the global replica-0 reference"
            else:
                resolution = "the run detected no difference at this resolution"
            # The comparison's scope is the packed PUB's group set: global
            # when the PUB carries more than one group, single_group
            # otherwise; the caller supplies it from the PUB manifests.
            out["global_packing_crosstalk"] = {
                **(scope or {"scope": "unknown", "groups": []}),
                "global_replica0_score": iso,
                "packed_replica0_score": packed,
                "difference": packed - iso,
                "z": z,
                "resolution": resolution,
                "tvd": tvd(dists[e.name][0], dists[runs[0].name][0]),
                **variance.equivalence(packed, packed_var, iso, iso_var, shots, _bernoulli_score(e)),
            }
    if group.admission is not None:
        out["admission"] = group.admission(per_replica, shots)
    return out


def _reference_scope(choice: Choice, scopes: dict[str, dict[str, Any]] | None) -> dict[str, Any] | None:
    """The scope record of the PUB carrying choice's packed primary, when the caller supplies the map."""
    if scopes is None:
        return None
    primary = next((entry for entry in choice.entries if not entry.reference), None)
    return scopes.get(primary.name) if primary else None


def pub_scopes(pubs: list[ExecutionPub]) -> dict[str, dict[str, Any]]:
    """For each logical entry, the scope and group set of the PUB that carries it."""
    scopes: dict[str, dict[str, Any]] = {}
    for pub in pubs:
        groups = sorted({component.choice.group.name for component in pub.components})
        for component in pub.components:
            scopes[component.entry.name] = {
                "scope": "global" if len(groups) > 1 else "single_group",
                "groups": groups,
            }
    return scopes


def _bernoulli_score(entry: Entry) -> bool:
    """Whether every per-shot score weight of entry is 0 or 1, so its score is a proportion."""
    if entry.weights is not None:
        weight = np.asarray(entry.weights, dtype=float)
    else:
        peak = float(np.max(entry.ideal))
        weight = np.asarray(entry.ideal, dtype=float) / peak if peak > 0 else np.zeros_like(entry.ideal, dtype=float)
    return bool(np.all(np.isclose(weight, 0.0) | np.isclose(weight, 1.0)))


def packing_interpretation(schedule: dict[str, Any] | None, crosstalk: dict[str, Any] | None) -> str | None:
    """One reading of the scheduler-residual and fidelity comparisons together.

    A larger packed residual is an unattributed global packing scheduling
    cost: feed-forward, measurement, reset, pulse-channel, and controller
    resources all scale with replica count, and only a matched
    dynamic/control ladder separates them; without feed-forward in the packed
    PUB the cost excludes feed-forward and is attributed no further. Equal residuals with a
    detected yield loss are evidence consistent with quantum, measurement, or
    readout crosstalk. A loss the 95 percent interval resolves is reported
    even when the 90 percent interval sits inside the margin. No reading
    names one group or one physical mechanism.
    """
    if schedule is None or crosstalk is None:
        return None
    loss = bool(crosstalk.get("below_zero_95"))
    gain = bool(crosstalk.get("above_zero_95"))
    within = bool(crosstalk.get("within_margin"))
    if crosstalk.get("verdict") == "insufficient_shots":
        yield_reading = "no yield verdict, since the shots are below the equivalence floor"
    elif loss and within:
        yield_reading = "a detected packed yield loss inside the equivalence margin"
    elif loss:
        yield_reading = "a detected packed yield loss"
    elif gain:
        yield_reading = "a detected packed yield gain"
    elif within:
        yield_reading = "yields equivalent within the margin"
    else:
        yield_reading = "an unresolved yield difference"
    groups = schedule.get("groups") or crosstalk.get("groups") or []
    if len(groups) == 1:
        tail = f"; within {groups[0]} alone, no single mechanism identified"
    else:
        tail = "; no single group or mechanism identified"
    if "residual_difference_dt" not in schedule:
        return f"scheduler residuals unavailable; the fidelity comparison stands alone: {yield_reading}"
    longer = schedule["residual_difference_dt"] > 0
    if not schedule.get("feed_forward"):
        return (
            f"no feed-forward in the packed PUB, so a residual difference is an unattributed packing scheduling "
            f"cost that excludes feed-forward; {yield_reading}"
        )
    if longer:
        return (
            f"larger packed scheduler residual with {yield_reading}: an unattributed global packing scheduling "
            f"cost that only a matched dynamic/control ladder separates into feed-forward, measurement, reset, "
            f"pulse-channel, and controller shares{tail}"
        )
    if loss:
        return (
            f"equal or smaller packed residual with {yield_reading}: evidence consistent with quantum, measurement, "
            f"or readout crosstalk{tail}"
        )
    if within:
        return f"equal or smaller packed residual with {yield_reading}: no packing cost resolved"
    return f"equal or smaller packed residual with {yield_reading} at this resolution"


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
    choice: Choice,
    noisy: dict[str, list[np.ndarray]],
    noise_calibration: str,
    shots: int,
    scopes: dict[str, dict[str, Any]] | None = None,
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
                "feed_forward": _has_feed_forward(entry.base),
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
        **choice.snap.identity,
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
        **replica_statistics(choice.group, choice.entries, noisy, shots, _reference_scope(choice, scopes)),
        "summary_readout_corrected": corrected_summary(choice.group, choice.entries, noisy, choice.snap.properties),
        "placed_qubit_calibration": placed_qubit_calibration(
            choice.snap.properties, sorted({qubit for replica in choice.replicas for qubit in replica.qubits})
        ),
        "members": members,
    }


PLACED_QUBIT_FIELDS = ("T1", "T2", "readout_error", "prob_meas1_prep0", "prob_meas0_prep1", "frequency")


def placed_qubit_calibration(properties: Any, qubits: list[int]) -> dict[str, dict[str, float]]:
    """The snapshot's per-qubit coherence and assignment values for every executing qubit.

    Backend properties report T1 and T2 in microseconds and assignment rates as
    probabilities; a field the backend omits stays absent.
    """
    if properties is None:
        return {}
    placed = {}
    for qubit in qubits:
        values = {item.name: item.value for item in properties.qubits[qubit]}
        placed[str(qubit)] = {
            name: float(values[name]) for name in PLACED_QUBIT_FIELDS if isinstance(values.get(name), (int, float))
        }
    return placed


def discover_snapshots(
    service: QiskitRuntimeService,
    pinned_names: list[str] | None,
    max_pending: int | None,
    *,
    retain_ineligible: bool = False,
    scope: Collection[str] | None = None,
    operator_excluded: Mapping[str, Collection[int]] | None = None,
) -> tuple[list[Snapshot], dict[str, Any], dict[str, Any]]:
    """Refresh the requested inventory and filter candidates unless the caller needs every snapshot.

    Complete-inventory families classify successfully refreshed excluded peers
    independently. Failed probes supply inventory evidence without a Snapshot.
    A backend outside scope (the approved record's eligible set during a
    submission) is recorded as outside_approved_scope without a probe.
    operator_excluded maps a backend to qubits withheld from placement.
    """
    if pinned_names is not None:
        names = list(dict.fromkeys(pinned_names))
    else:
        try:
            discovered = service.backends()
        except Exception as error:
            raise LiveRunError(f"backend discovery failed ({type(error).__name__})") from error
        names = sorted({backend.name for backend in discovered})
    snapshots: list[Snapshot] = []
    skipped: dict[str, Any] = {}
    inventory: dict[str, Any] = {}
    for name in names:
        if scope is not None and name not in scope:
            reason = "outside the approved record's eligible backends"
            skipped[name] = {"reason": reason}
            inventory[name] = {"eligibility": "outside_approved_scope", "reason": reason}
            print(f"{name}: skipped: {reason}")
            continue
        try:
            snapshot = take_snapshot(service, name, (operator_excluded or {}).get(name, ()))
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
        if ineligible is None or retain_ineligible:
            snapshots.append(snapshot)
    return snapshots, skipped, inventory


def approved_backend_scope(approved_dir: Path) -> list[str]:
    """The backends the approved dry run found eligible, which a submission alone plans over.

    Eligibility reads each backend's status and pending-job count when the plan
    runs, so a backend that was ineligible at the dry run (queue above
    --max-pending, maintenance) can turn eligible before the submission
    re-plans and outscore the approved choice. Planning the submission over the
    approved record's `backends` keeps such a backend out; an approved backend
    that changes or turns ineligible still moves the plan, and the
    approved-record comparison refuses it.
    """
    approved = json.loads((approved_dir / "record.json").read_text())
    backends = approved.get("backends")
    if not isinstance(backends, dict) or not backends:
        raise LiveRunError(f"approved record {approved_dir.name} names no eligible backend")
    return sorted(backends)


def plan(service: QiskitRuntimeService, args: argparse.Namespace) -> tuple[list[Choice], dict[str, Any]]:
    available_groups = all_experiment_groups()
    known = {group.name for group in available_groups}
    unknown = sorted(set(args.groups or []) - known)
    if unknown:
        raise LiveRunError(f"unknown experiment groups {unknown}; known: {sorted(known)}")
    snaps, skipped, inventory = discover_snapshots(
        service,
        args.backends,
        args.max_pending,
        retain_ineligible=getattr(args, "family", None) == "folded-correction",
        scope=getattr(args, "approved_scope", None),
        operator_excluded=getattr(args, "exclude_qubits", None),
    )
    if not snaps:
        raise LiveRunError("no eligible backend")
    requested_delay = getattr(args, "rep_delay", None)
    if requested_delay is not None:
        refused = {
            snapshot.name: violations
            for snapshot in snaps
            if (violations := qpu_planning.repetition_delay_violations(snapshot.backend, requested_delay, None))
        }
        if refused:
            raise LiveRunError(f"--rep-delay {requested_delay} s is unavailable: {refused}")
    trace: dict[str, Any] = {}
    design: dict[str, Any] = {}
    if getattr(args, "family", None):
        choices, design = qpu_planning.prepare(sys.modules[__name__], snaps, args, service.usage(), trace)
        groups = [choice.group for choice in choices]
        fusion_placement = {"allocation": "matched-family", "configuration": design["family_configuration"]}
    else:
        if not args.groups:
            groups = experiment_groups()
        else:
            groups = [group for group in available_groups if group.name in args.groups]
            standalone = {group.name for group in standalone_campaign_groups()}
            campaigns = sorted(group.name for group in groups if group.name in standalone)
            if campaigns and len(groups) > 1:
                raise LiveRunError(f"{campaigns[0]} requires an isolated campaign; cannot co-run with other groups")
            if "qubit_baseline" in campaigns and args.dd:
                # The Ramsey and relaxation idles measure free evolution, which
                # dynamical decoupling would fill with echo pulses.
                raise LiveRunError("qubit_baseline runs without dynamical decoupling; omit --dd")
            if "conditional_ramsey" in campaigns:
                # The sector rates are free-evolution phase slopes, which echo pulses
                # refocus, and the reduced model covers one pair: a second replica's
                # qubits beside A or B would add spectator Z Z terms to the rates.
                if args.dd:
                    raise LiveRunError("conditional_ramsey runs without dynamical decoupling; omit --dd")
                if args.max_replicas != 1:
                    raise LiveRunError("conditional_ramsey runs one replica; pass --max-replicas 1")
            if "star_ramsey" in campaigns and args.dd:
                # The sector rates are free-evolution phase slopes, which echo pulses
                # refocus. The replica count stays open: placement blocks every neighbor
                # of a placed replica on the admitted CZ graph, so no two stars share an
                # admitted coupler and a degree-three center's couplers all join its own
                # leaves. A coupler the quality policy excluded still couples its
                # endpoints, so a leaf's outside neighbor across one can belong to
                # another star.
                raise LiveRunError("star_ramsey runs without dynamical decoupling; omit --dd")
            if set(campaigns) & {"scaffold_ab", "readout_delay"}:
                # Both compare members on one tile under one calibration: the idles
                # must stay free of echo pulses, and a second replica is a second tile.
                if args.dd:
                    raise LiveRunError(f"{campaigns[0]} runs without dynamical decoupling; omit --dd")
                if args.max_replicas != 1:
                    raise LiveRunError(f"{campaigns[0]} runs one replica; pass --max-replicas 1")
            if "crossed_tile_template" in campaigns:
                # Each PUB row runs one member on both tiles in the same shots, which
                # needs exactly two replicas, and the crossing matches the rank-sector
                # acquisition it tests, which ran without dynamical decoupling.
                if args.dd:
                    raise LiveRunError("crossed_tile_template runs without dynamical decoupling; omit --dd")
                if args.max_replicas != 2:
                    raise LiveRunError("crossed_tile_template runs one replica per tile; pass --max-replicas 2")
            if "spectator_wavefront_ramsey" in campaigns:
                # The spectator arms read free Ramsey evolution over explicit delays,
                # which dynamical decoupling would fill with echo pulses, and a second
                # replica's driven core would sit within a few hops of these spectators.
                if args.dd:
                    raise LiveRunError("spectator_wavefront_ramsey runs without dynamical decoupling; omit --dd")
                if args.max_replicas != 1:
                    raise LiveRunError("spectator_wavefront_ramsey runs one replica; pass --max-replicas 1")
        candidate_sets = [select_candidates(group, snaps, args.seeds, trace) for group in groups]
        choices, fusion_placement = select_fusion_choices(candidate_sets, _policy(args))
        for choice in choices:
            if choice.group.name == "crossed_tile_template":
                from crossed_tile_template import placement_violation

                # --max-replicas caps the count; the crossing needs exactly one replica on each tile.
                violation = placement_violation(choice.snap.name, [list(replica.qubits) for replica in choice.replicas])
                if violation is not None:
                    raise LiveRunError(violation)
    pubs = execution_pubs(choices)
    record = {
        "schema_version": RECORD_SCHEMA_VERSION,
        "schema_contract": RECORD_SCHEMA_CONTRACT,
        "state": "planned",
        "started": args.started,
        "versions": {
            pkg: version(pkg)
            for pkg in ("numpy", "qiskit", "qiskit-aer", "qiskit-ibm-runtime", "scipy", "rustworkx", "sympy")
        },
        "policy": QUALITY
        | {
            "max_pending": args.max_pending,
            "seeds": args.seeds,
            "joint_candidates": JOINT_CANDIDATES,
            "replica_floor": args.replica_floor,
            "max_replicas": args.max_replicas,
            "isolated_reference": args.isolated_reference,
            "cross_group_buffer": getattr(args, "cross_group_buffer", True),
            # Twirling and DD change the submitted workload without changing
            # the archived circuits, so the approved-record gate compares them.
            "twirl": bool(getattr(args, "twirl", False)),
            "dd": getattr(args, "dd", None),
            "min_remaining_seconds": getattr(args, "min_remaining_seconds", None),
            "max_execution_seconds": getattr(args, "max_execution_seconds", None),
            # The Sampler's execution.rep_delay changes the workload and its
            # charge, so the approved-record gate compares it; the backend
            # default leaves the key out.
            **({"rep_delay_seconds": requested_delay} if requested_delay is not None else {}),
            "operator_excluded_qubits": {
                name: sorted(qubits) for name, qubits in sorted((getattr(args, "exclude_qubits", None) or {}).items())
            },
            "design": qpu_planning.settings(args),
            "local_compute": local_compute.settings(args),
        },
        "shots": args.shots,
        "instance_sha256_12": _instance_hash(service),
        "seed_simulator": SEED_SIMULATOR,
        "experiment_digest": experiment_digest(),
        "code_commit": _code_commit(),
        "system_inventory": inventory,
        "backends": {s.name: s.summary() for s in snaps},
        "skipped_backends": skipped,
        "circuit_requirements": {group.name: group_requirements(group).summary() for group in groups},
        "execution_requirements": {choice.group.name: execution_requirements(choice) for choice in choices},
        "fusion_placement": fusion_placement,
        "fusion_summary": fusion_summary(pubs),
        "execution_pubs": [pub.manifest() for pub in pubs],
        "selection_trace": trace,
        **design,
    }
    record["budget_plan"] = qpu_planning.budget_plan(sys.modules[__name__], choices, args, service.usage())
    record["execution_contract"] = qpu_planning.execution_contract(choices, record)
    if design.get("optimization", {}).get("selected") is None and design:
        record["state"] = "design_infeasible"
    if not record["budget_plan"]["admitted"]:
        record["state"] = "budget_infeasible"
    return choices, record


def _policy(args: argparse.Namespace) -> ReplicaPolicy:
    return ReplicaPolicy(
        args.replica_floor, args.max_replicas, args.isolated_reference, getattr(args, "cross_group_buffer", True)
    )


def evaluate(choices: list[Choice], record: dict[str, Any]) -> None:
    """Noise-simulate each choice under its backend's live properties, after proving they match the Target."""
    # One simulator per snapshot: a group recompiled on a fresh snapshot of a
    # backend is simulated with that snapshot's Target, not an earlier one.
    sims: dict[int, tuple[AerSimulator, str]] = {}
    record["groups"] = []
    record["execution_requirements"] = {choice.group.name: execution_requirements(choice) for choice in choices}
    pubs = execution_pubs(choices)
    record["fusion_summary"] = fusion_summary(pubs)
    record["execution_pubs"] = [pub.manifest() for pub in pubs]
    scopes = pub_scopes(pubs)
    fused_by_snapshot: dict[int, tuple[Snapshot, list[QuantumCircuit]]] = {}
    for pub in pubs:
        snapshot = pub.components[0].choice.snap
        fused_by_snapshot.setdefault(id(snapshot), (snapshot, []))[1].append(pub.circuit)
    for snapshot, fused_circuits in fused_by_snapshot.values():
        check_target_matches_properties(
            fused_circuits,
            snapshot.backend.target,
            snapshot.properties,
            f"{snapshot.name} fused PUBs",
        )
    for choice in choices:
        isas = [entry.packed for entry in choice.entries]
        check_target_matches_properties(isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name)
        key = id(choice.snap)
        if key not in sims:
            sims[key] = (
                noise_simulator(
                    choice.snap.name,
                    choice.snap.backend.target,
                    choice.snap.properties,
                    record.get("policy", {}).get("local_compute", local_compute.settings()),
                ),
                choice.snap.calibration,
            )
        sim, cal = sims[key]
        noisy = simulate(choice, sim, int(record["shots"]))
        entry = _choice_record(choice, noisy, cal, int(record["shots"]), scopes)
        record["groups"].append(entry)
        cz = [m["cz"] for m in entry["members"]]
        summary = {k: round(v, 4) for k, v in entry["summary"].items()}
        scores = [round(r.score, 4) for r in choice.replicas]
        print(
            f"{choice.group.name}: {choice.snap.name} seed={choice.seed} layout={choice.layout} "
            f"joint_score={choice.joint_score:.4f} replicas={len(choice.replicas)} scores={scores} "
            f"cz={cz} summary={summary}"
        )
    record["evaluation_simulation_batches"] = [
        batch for simulator, _calibration in sims.values() for batch in local_compute.batches(simulator)
    ]


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


APPROVED_GROUP_FIELDS = ("backend", "seed_transpiler", "initial_layout", "replica_floor")
APPROVED_RECORD_FIELDS = (
    "experiment_digest",
    "schema_version",
    "schema_contract",
    "shots",
    "pub_shots",
    "policy",
    "versions",
    "instance_sha256_12",
    "family_configuration",
    "observable_contracts",
    "execution_contract",
)


def approved_calibration_drift(record: dict[str, Any], backend_name: str, calibration: str) -> str | None:
    """Why a batch's calibration departs from the one the approved-record gate accepted, or None.

    A run that has sent no batch returns to approval_required; a run with a
    batch already sent keeps its submission lifecycle and records that the
    unsent batches need renewed approval.
    """
    approved = record.get("approved_record", {}).get("calibrations", {})
    if backend_name not in approved or calibration == approved[backend_name]:
        return None
    reason = f"calibration moved after the approved-record check ({approved[backend_name]} -> {calibration})"
    if record.get("submission", {}).get("jobs"):
        record["renewed_approval_for_unsent_batches"] = {"required_at": _now(), "reason": reason}
    else:
        record["state"] = "approval_required"
    return reason


def refreshed_plan_view(record: dict[str, Any], choices: list[Choice], pubs: list[ExecutionPub]) -> dict[str, Any]:
    """A record-shaped view of the plan as it stands after the pre-submission refresh.

    The top-level identity (digest, schema, shots, policy) comes from record;
    the groups and fused PUB manifests come from the refreshed choices and
    PUBs, so a calibration or layout that moved during the refresh is
    compared, not the initial plan's copy.
    """
    return {
        **{k: record.get(k) for k in APPROVED_RECORD_FIELDS},
        "groups": [
            {
                "group": choice.group.name,
                "backend": choice.snap.name,
                "seed_transpiler": choice.seed,
                "initial_layout": list(choice.layout),
                "replica_floor": choice.replica_floor,
                "calibration": choice.snap.calibration,
                "replicas": [{"physical_qubits": list(replica.qubits)} for replica in choice.replicas],
            }
            for choice in choices
        ],
        "execution_pubs": [pub.manifest() for pub in pubs],
    }


APPROVAL_CONSUMED_FILE = "approval-consumed.json"


def consume_approval(approved_dir: Path, run_name: str) -> dict[str, Any]:
    """Mark the approved record's one-attempt authorization as consumed by run_name, exactly once.

    The marker is created with O_EXCL inside the approved record directory,
    so a second invocation that passes every comparison still finds the
    authorization spent and sends nothing.
    """
    marker = approved_dir / APPROVAL_CONSUMED_FILE
    payload = {"consumed_at": _now(), "run": run_name}
    try:
        descriptor = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        try:
            earlier = json.loads(marker.read_text())
        except (OSError, ValueError):
            earlier = {}
        raise LiveRunError(
            f"the approved record {approved_dir.name} was already consumed by run "
            f"{earlier.get('run', 'unknown')} at {earlier.get('consumed_at', 'unknown')}; "
            "a fresh dry run and a renewed written case are required"
        ) from None
    with os.fdopen(descriptor, "w") as handle:
        handle.write(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    # The directory entry reaches disk before the remote call, so a crash
    # after the Sampler accepts the batch leaves the marker in place.
    directory_fd = os.open(approved_dir, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return payload


def approved_record_mismatches(
    approved_dir: Path, record: dict[str, Any], qpy_archive_sha256: str, expected_record_sha256: str | None = None
) -> list[str]:
    """Every way the fresh plan in record differs from the approved submit-free record in approved_dir.

    The approved record is the dry run the owner read before approving the
    command, so the plan that reaches the service has to be that plan: the
    same experiment digest and schema, shots, policy (replica, queue,
    twirling, DD, and remaining-budget settings), dependency versions, IBM
    Cloud instance, groups on the same backends with the same seeds, layouts,
    replica qubits, and floors, the same fused PUB manifests, the same
    calibration on every used backend, and a byte-identical QPY archive. The approved record is itself a dry
    run: planned, with no submission.
    """
    approved = json.loads((approved_dir / "record.json").read_text())
    approved_qpy = hashlib.sha256((approved_dir / "isa.qpy").read_bytes()).hexdigest()
    mismatches: list[str] = []
    if expected_record_sha256 is not None:
        actual = hashlib.sha256((approved_dir / "record.json").read_bytes()).hexdigest()
        if actual != expected_record_sha256.lower():
            mismatches.append("approved record.json sha256 differs from --approved-record-sha256")
    if approved.get("state") != "planned" or "submission" in approved:
        mismatches.append(f"approved record state is {approved.get('state')!r}, not a submit-free plan")
    for field_name in APPROVED_RECORD_FIELDS:
        if approved.get(field_name) != record.get(field_name):
            mismatches.append(f"{field_name} differs")
    approved_groups = {g["group"]: g for g in approved.get("groups", [])}
    fresh_groups = {g["group"]: g for g in record.get("groups", [])}
    if set(approved_groups) != set(fresh_groups):
        mismatches.append(f"groups differ: approved {sorted(approved_groups)}, fresh {sorted(fresh_groups)}")
    for name in sorted(set(approved_groups) & set(fresh_groups)):
        old, new = approved_groups[name], fresh_groups[name]
        for field_name in APPROVED_GROUP_FIELDS:
            if old.get(field_name) != new.get(field_name):
                mismatches.append(f"{name}: {field_name} {old.get(field_name)!r} -> {new.get(field_name)!r}")
        old_qubits = [replica.get("physical_qubits") for replica in old.get("replicas", [])]
        new_qubits = [replica.get("physical_qubits") for replica in new.get("replicas", [])]
        if old_qubits != new_qubits:
            mismatches.append(f"{name}: replica qubits {old_qubits} -> {new_qubits}")
        if old.get("calibration") != new.get("calibration"):
            mismatches.append(f"{name}: calibration {old.get('calibration')} -> {new.get('calibration')}")
    if approved.get("execution_pubs") != record.get("execution_pubs"):
        mismatches.append("fused PUB manifests differ")
    if approved_qpy != qpy_archive_sha256:
        mismatches.append(f"QPY archive {approved_qpy[:12]} -> {qpy_archive_sha256[:12]}")
    return mismatches


def _qpy_digest(circuits: list[QuantumCircuit]) -> str:
    """Stable in-process identity for an ordered execution-circuit set."""
    buffer = io.BytesIO()
    qpy.dump(circuits, buffer)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def choice_change_reasons(choice: Choice, fresh: Snapshot) -> list[str]:
    """Reasons an existing compile needs rebuilding against a fresh snapshot."""
    reasons = group_admission_violations(choice.group, fresh.capabilities)
    if choice.snap.capabilities != fresh.capabilities:
        reasons.append("backend capabilities changed")
    isas = [entry.packed for entry in choice.entries]
    for entry in choice.entries:
        reasons.extend(f"{entry.name}: {reason}" for reason in compiled_violations(entry.packed, fresh))
    try:
        if fingerprint(isas, fresh.backend.target, fresh.properties) != fingerprint(
            isas, choice.snap.backend.target, choice.snap.properties
        ):
            reasons.append("calibration values changed on compiled instructions")
    except Exception as error:
        reasons.append(f"calibration fingerprint failed ({type(error).__name__})")
    return sorted(set(reasons))


def sampler_rep_delay(args: Any) -> dict[str, float]:
    """configure_sampler's rep_delay keyword for --rep-delay; empty, the backend default, without it."""
    value = getattr(args, "rep_delay", None)
    return {} if value is None else {"rep_delay": value}


def planned_repetition_delay_range(record: Mapping[str, Any], backend_name: str) -> list[float] | None:
    """The rep_delay_range the record's execution contract admitted a requested delay in, for backend_name."""
    for entry in record.get("execution_contract", {}).get("backends", []):
        if entry.get("name") == backend_name:
            return entry.get("repetition_delay_range_seconds")
    return None


def _optional_repetition_delay(backend: Any) -> float | None:
    """The backend's configured repetition delay in seconds, or None for a fixed repetition rate."""
    try:
        return qpu_planning.repetition_delay(backend)
    except (ValueError, AttributeError):
        return None


def unchanged_since_planning(
    record: dict[str, Any],
    inventory: dict[str, Any],
    choices: list[Choice],
    fresh: list[Snapshot],
    remaining_seconds: Any,
) -> bool:
    """Whether a pre-submission refresh would rebuild exactly the planned choices.

    Selection reads every backend's inventory entry (eligibility, status,
    queue, calibration, capabilities, repetition delay, medians and
    exclusions) and the optimizer reads the account's remaining quota, so
    each must match its planning value; the entries are captured when the
    snapshot is taken, so a cached backend object refreshed in place still
    compares its planning value. Every chosen backend's compiled instructions
    must also keep their capabilities and calibration fingerprint. The
    backend version and processor type are provenance that selection never
    reads, so they stay out of the comparison.
    """
    planned = record.get("system_inventory")
    if not isinstance(planned, dict) or set(planned) != set(inventory):
        return False
    planned_remaining = record.get("budget_plan", {}).get("remaining_seconds")
    if planned_remaining is None or remaining_seconds != planned_remaining:
        return False
    unread = {"fetched_at", *BACKEND_IDENTITY_FIELDS}
    for name, entry in inventory.items():
        before = planned[name]
        if not isinstance(before, dict) or not isinstance(entry, dict):
            return False
        if {k: v for k, v in before.items() if k not in unread} != {k: v for k, v in entry.items() if k not in unread}:
            return False
    by_name = {snapshot.name: snapshot for snapshot in fresh}
    for choice in choices:
        current = by_name.get(choice.snap.name)
        if current is None or choice_change_reasons(choice, current):
            return False
    return True


def refresh_backend_identity(record: dict[str, Any], inventory: Mapping[str, Any]) -> None:
    """Copy each refreshed backend's version and processor type into the record's provenance entries.

    unchanged_since_planning and the approved-record comparison skip these
    fields, so a plan reused or rebuilt without reselection keeps its
    planning-time backends, system_inventory and group entries; the refresh
    writes the fresh values into each entry that names a probed backend, and
    leaves every other field and every unprobed backend as planned.
    """
    fresh = {
        name: {key: entry[key] for key in BACKEND_IDENTITY_FIELDS if key in entry}
        for name, entry in inventory.items()
        if isinstance(entry, Mapping)
    }
    entries = [
        *(
            (name, entry)
            for section in ("backends", "system_inventory")
            for name, entry in record.get(section, {}).items()
        ),
        *((group.get("backend"), group) for group in record.get("groups", [])),
    ]
    for name, entry in entries:
        if isinstance(entry, dict) and fresh.get(name):
            entry.update(fresh[name])


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


def validated_pub_shots(pub_names: list[str], allocation: Any) -> dict[str, int]:
    """Validate a complete fixed allocation before selecting backend subsets."""
    if len(pub_names) != len(set(pub_names)):
        raise LiveRunError("shot allocation requires unique execution PUB names")
    if not isinstance(allocation, dict) or set(allocation) != set(pub_names):
        raise LiveRunError("shot allocation must cover exactly the execution PUBs")
    if any(type(value) is not int or not 1 <= value <= MAX_JOB_EXECUTIONS for value in allocation.values()):
        raise LiveRunError("PUB shot allocation violates the positive Sampler execution bound")
    return dict(allocation)


def _recorded_job_shots(record: dict[str, Any], job_entry: dict[str, Any]) -> int:
    """Bind collected denominators to the whole record and homogeneous job."""
    shots = job_entry.get("shots", record["shots"])
    if type(shots) is not int or not 1 <= shots <= MAX_JOB_EXECUTIONS:
        raise LiveRunError("recorded job shots must be positive bounded integers")
    if "pub_shots" in record:
        allocation = validated_pub_shots([pub["name"] for pub in record["execution_pubs"]], record["pub_shots"])
        if "shots" not in job_entry or any(allocation.get(pub["name"]) != shots for pub in job_entry["pubs"]):
            raise LiveRunError("job shots differ from the approved PUB allocation")
        if record["shots"] != max(allocation.values()):
            raise LiveRunError("recorded maximum shots differ from the PUB allocation")
    options = job_entry.get("options", {})
    if "default_shots" in options and options["default_shots"] != shots:
        raise LiveRunError("job shot count differs from its retained Sampler options")
    return shots


def batch_shots(batch: list[ExecutionPub], shots: int, pub_shots: dict[str, int] | None = None) -> int:
    """Resolve the one shot count accepted by the client-side Sampler job."""
    if not batch:
        raise LiveRunError("a submission batch must contain at least one PUB")
    if pub_shots is None:
        values = {shots}
    else:
        if any(pub.name not in pub_shots for pub in batch):
            raise LiveRunError("shot allocation omits an execution PUB")
        values = {pub_shots[pub.name] for pub in batch}
    if len(values) != 1 or any(type(value) is not int or value < 1 for value in values):
        raise LiveRunError("each Sampler job requires one positive integer shot count")
    return next(iter(values))


def submission_batches(
    choices: list[Choice], kind: str, shots: int = SHOTS, pub_shots: dict[str, int] | None = None
) -> list[list[ExecutionPub]]:
    """Group whole PUBs by fixed shot count, preserving their relative row order."""
    if kind not in ("static", "dynamic"):
        raise LiveRunError(f"unknown submission kind {kind!r}")
    all_pubs = execution_pubs(choices)
    if pub_shots is not None:
        pub_shots = validated_pub_shots([pub.name for pub in all_pubs], pub_shots)
    elif type(shots) is not int or not 1 <= shots <= MAX_JOB_EXECUTIONS:
        raise LiveRunError(f"{shots} shots cannot fit the {MAX_JOB_EXECUTIONS}-execution Sampler job limit")
    pubs = [pub for pub in all_pubs if pub.kind == kind]
    tiers = sorted({pub_shots[pub.name] if pub_shots is not None else shots for pub in pubs})
    batches = []
    for tier in tiers:
        batch = [pub for pub in pubs if (pub_shots[pub.name] if pub_shots is not None else shots) == tier]
        if len(batch) * tier > MAX_JOB_EXECUTIONS:
            raise LiveRunError(
                f"{len(batch)} {kind} PUBs at {tier} shots exceed the {MAX_JOB_EXECUTIONS}-execution "
                "Sampler job limit; lower the declared shot tier"
            )
        batches.append(batch)
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
    pubs: list[dict[str, Any]],
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
            "pubs": pubs,
            "qpy_archive_sha256": qpy_archive_sha256,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    batch_digest = hashlib.sha256(batch_identity.encode()).hexdigest()[:24]
    return ["gororoba-quantum", f"gororoba-run-{run_digest}", f"gororoba-batch-{batch_digest}"]


def build_submission_plan(
    choices: list[Choice], args: argparse.Namespace, qpy_archive_sha256: str
) -> tuple[dict[str, Any], list[tuple[int, str, str, list[ExecutionPub]]]]:
    """Materialize the complete immutable batch identity before any job call."""
    full_allocation = getattr(args, "pub_shots", None)
    if full_allocation is not None:
        full_allocation = validated_pub_shots([pub.name for pub in execution_pubs(choices)], full_allocation)
    planned_backends = sorted({choice.snap.name for choice in choices})
    by_backend: dict[str, list[Choice]] = {}
    for choice in choices:
        by_backend.setdefault(choice.snap.name, []).append(choice)
    runtime_batches: list[tuple[int, str, str, list[ExecutionPub]]] = []
    planned_jobs: list[dict[str, Any]] = []
    for name, group_choices in by_backend.items():
        backend = group_choices[0].snap.backend
        if any(choice.snap.backend is not backend for choice in group_choices):
            raise LiveRunError(f"{name}: final groups do not share one refreshed backend snapshot")
        for kind in ("dynamic", "static"):
            allocation = (
                {pub.name: full_allocation[pub.name] for pub in execution_pubs(group_choices)}
                if full_allocation is not None
                else None
            )
            batches = submission_batches(group_choices, kind, args.shots, allocation)
            for batch_index, batch in enumerate(batches, start=1):
                selected_shots = batch_shots(batch, args.shots, allocation)
                pub_manifests = [pub.manifest() for pub in batch]
                members = [component.entry.name for pub in batch for component in pub.components]
                batch_count = len(batches)
                recovery_tags = _recovery_tags(
                    args.started,
                    name,
                    kind,
                    batch_index,
                    batch_count,
                    pub_manifests,
                    qpy_archive_sha256,
                )
                sampler = configure_sampler(
                    backend,
                    kind,
                    args.twirl,
                    args.dd,
                    recovery_tags,
                    selected_shots,
                    getattr(args, "max_execution_seconds", None),
                    **sampler_rep_delay(args),
                )
                plan_index = len(planned_jobs)
                planned_jobs.append(
                    {
                        "backend": name,
                        "kind": kind,
                        "batch_index": batch_index,
                        "batch_count": batch_count,
                        "shots": selected_shots,
                        "members": members,
                        "pubs": pub_manifests,
                        "qpy_archive_sha256": qpy_archive_sha256,
                        "calibrations": sorted(
                            {component.choice.snap.calibration for pub in batch for component in pub.components}
                        ),
                        "recovery_tags": recovery_tags,
                        "options": sampler.options.model_dump(mode="json"),
                        "state": "planned",
                    }
                )
                runtime_batches.append((plan_index, name, kind, batch))
    return {
        "started": args.started,
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
        "members": copy.deepcopy(plan_entry["members"]),
        "pubs": copy.deepcopy(plan_entry["pubs"]),
        "qpy_archive_sha256": plan_entry["qpy_archive_sha256"],
        "calibrations": copy.deepcopy(plan_entry["calibrations"]),
        "recovery_tags": copy.deepcopy(plan_entry["recovery_tags"]),
        "budget_before": copy.deepcopy(plan_entry["budget_before"]),
        "options": copy.deepcopy(plan_entry["options"]),
    }
    if "shots" in plan_entry:
        record["shots"] = plan_entry["shots"]
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
    started = submission.get("started")
    if not isinstance(started, str) or not started:
        raise LiveRunError("submission plan has no run-start identity")
    planned_by_key: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    planned_members: set[str] = set()
    planned_pubs: set[str] = set()
    for planned_job in planned_jobs:
        key = _submission_key(planned_job)
        if key in planned_by_key:
            raise LiveRunError(f"duplicate planned job identity {key}")
        if planned_job.get("qpy_archive_sha256") != archive_digest:
            raise LiveRunError(f"planned job {key} differs from the submission QPY archive digest")
        members = planned_job["members"]
        if len(members) != len(set(members)):
            raise LiveRunError(f"planned job {key} repeats a logical member")
        duplicate_members = planned_members.intersection(members)
        if duplicate_members:
            raise LiveRunError(f"planned circuits appear in more than one job: {sorted(duplicate_members)}")
        planned_members.update(members)
        pub_names = [pub["name"] for pub in planned_job.get("pubs", [])]
        if len(pub_names) != len(set(pub_names)):
            raise LiveRunError(f"planned job {key} repeats a fused PUB name")
        for pub in planned_job.get("pubs", []):
            if pub.get("backend") != planned_job["backend"] or pub.get("kind") != planned_job["kind"]:
                raise LiveRunError(f"planned job {key} has a fused PUB with different backend or kind")
        duplicate_pubs = planned_pubs.intersection(pub_names)
        if duplicate_pubs:
            raise LiveRunError(f"fused PUBs appear in more than one job: {sorted(duplicate_pubs)}")
        mapped_members = [component["member"] for pub in planned_job.get("pubs", []) for component in pub["components"]]
        if mapped_members != members:
            raise LiveRunError(f"planned job {key} flat members differ from its ordered PUB component map")
        expected_tags = _recovery_tags(
            started,
            str(planned_job["backend"]),
            str(planned_job["kind"]),
            int(planned_job["batch_index"]),
            int(planned_job["batch_count"]),
            planned_job.get("pubs", []),
            archive_digest,
        )
        if planned_job.get("recovery_tags") != expected_tags:
            raise LiveRunError(f"planned job {key} recovery tags do not bind its fused-PUB manifest")
        planned_pubs.update(pub_names)
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
        for field_name in (
            "members",
            "pubs",
            "shots",
            "qpy_archive_sha256",
            "calibrations",
            "recovery_tags",
            "options",
        ):
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
    fresh_snapshots, skipped, inventory = discover_snapshots(
        service,
        args.backends,
        args.max_pending,
        retain_ineligible=getattr(args, "family", None) == "folded-correction",
        scope=getattr(args, "approved_scope", None),
        operator_excluded=getattr(args, "exclude_qubits", None),
    )
    if not fresh_snapshots:
        raise LiveRunError("no eligible backend remains before submission")
    attempt_trace: dict[str, Any] = {}
    reselected: dict[str, Any] = {}
    if record.get("state") != "planned":
        reasons = record.get("budget_plan", {}).get("reasons", [])
        raise LiveRunError(
            f"submission requires an admitted plan, received {record.get('state')!r}: {'; '.join(reasons)}"
        )
    fresh_design: dict[str, Any] = {}
    unchanged = unchanged_since_planning(
        record, inventory, choices, fresh_snapshots, service.usage().get("usage_remaining_seconds")
    )
    if unchanged:
        # plan() ran in this process against the same calibrations, so a
        # rebuild reproduces its choices exactly; the approved-record
        # comparison below still checks this plan in full.
        fresh_choices = list(choices)
        fresh_fusion_placement = record.get("fusion_placement", {})
        print("pre-submit refresh: every backend's calibration, eligibility and queue match planning; reusing the plan")
    elif getattr(args, "family", None):
        fresh_choices, fresh_design = qpu_planning.prepare(
            sys.modules[__name__], fresh_snapshots, args, service.usage(), attempt_trace
        )
        fresh_fusion_placement = {"allocation": "matched-family", "configuration": fresh_design["family_configuration"]}
        if (
            fresh_design["optimization"]["selected"] is None
            or args.shots != record["shots"]
            or any(
                fresh_design.get(key) != record.get(key)
                for key in ("family_configuration", "observable_contracts", "pub_shots")
            )
        ):
            reselected["statistical_design"] = {
                "reasons": ["statistical admission, shot tier, or matched-family contract changed"]
            }
        record.update(fresh_design)
        record["shots"] = args.shots
    else:
        fresh_candidate_sets = [
            select_candidates(choice.group, fresh_snapshots, args.seeds, attempt_trace) for choice in choices
        ]
        fresh_choices, fresh_fusion_placement = select_fusion_choices(fresh_candidate_sets, _policy(args))
    old_execution_pubs = execution_pubs(choices)
    fresh_execution_pubs = execution_pubs(fresh_choices)
    fused_changed = _qpy_digest([pub.circuit for pub in old_execution_pubs]) != _qpy_digest(
        [pub.circuit for pub in fresh_execution_pubs]
    ) or [pub.manifest() for pub in old_execution_pubs] != [pub.manifest() for pub in fresh_execution_pubs]
    for choice, fresh_choice in zip(choices, fresh_choices, strict=True):
        previous_backend = choice.snap.name
        reasons = choice_reselection_reasons(choice, fresh_choice)
        if reasons:
            print(f"{choice.group.name}: live configuration changed; preparing a revised submit-free plan")
            reselected[choice.group.name] = {
                "previous_backend": previous_backend,
                "selected_backend": fresh_choice.snap.name,
                "reasons": reasons,
            }
    if fused_changed:
        reselected["execution_pubs"] = {"reasons": ["fused PUB circuits or ordered component mapping changed"]}
    requested_delay = getattr(args, "rep_delay", None)
    if requested_delay is not None:
        # A reused plan keeps its planning snapshots, so the fresh
        # configuration of each chosen backend comes from the refresh.
        refreshed = {snapshot.name: snapshot for snapshot in fresh_snapshots}
        delay_backends = {
            choice.snap.name: refreshed.get(choice.snap.name, choice.snap).backend for choice in fresh_choices
        }
        delay_reasons = {
            name: violations
            for name, backend in sorted(delay_backends.items())
            if (
                violations := qpu_planning.repetition_delay_violations(
                    backend, requested_delay, planned_repetition_delay_range(record, name)
                )
            )
        }
        if delay_reasons:
            reselected["repetition_delay"] = {"reasons": delay_reasons}
    choices[:] = fresh_choices
    record["execution_contract"] = qpu_planning.execution_contract(choices, record)
    record.setdefault("revalidation", []).append(
        {
            "attempt": 1,
            "system_inventory": inventory,
            "skipped_backends": skipped,
            "reselected_groups": reselected,
            "rebuilt": not unchanged,
            "fusion_placement": fresh_fusion_placement,
            "selection_trace": attempt_trace,
        }
    )
    refresh_backend_identity(record, inventory)
    if reselected:
        record["system_inventory"] = inventory
        record["backends"] = {snapshot.name: snapshot.summary() for snapshot in fresh_snapshots}
        record["skipped_backends"] = skipped
        record["selection_trace"] = attempt_trace
        record["fusion_placement"] = fresh_fusion_placement
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
    approved_dir = getattr(args, "approved_record", None)
    if approved_dir is not None:
        # The comparison reads the refreshed choices and PUBs, the plan that
        # build_submission_plan sends, since record["groups"] still describes
        # the initial snapshot when the refresh changed nothing routable.
        fresh_view = refreshed_plan_view(record, choices, fresh_execution_pubs)
        mismatches = approved_record_mismatches(
            Path(approved_dir), fresh_view, qpy_archive_sha256, getattr(args, "approved_record_sha256", None)
        )
        record["approved_record"] = {
            "run": Path(approved_dir).name,
            "record_sha256": hashlib.sha256((Path(approved_dir) / "record.json").read_bytes()).hexdigest(),
            "qpy_archive_sha256": hashlib.sha256((Path(approved_dir) / "isa.qpy").read_bytes()).hexdigest(),
            "calibrations": {group["backend"]: group["calibration"] for group in fresh_view["groups"]},
            "mismatches": mismatches,
        }
        if mismatches:
            record["state"] = "approval_required"
            record["renewed_approval"] = {
                "required_at": _now(),
                "reason": "the fresh plan differs from the approved record",
                "mismatches": mismatches,
                "qpy_archive_sha256": qpy_archive_sha256,
            }
            checkpoint()
            raise LiveRunError(
                "the fresh plan differs from the approved record "
                f"{Path(approved_dir).name} ({'; '.join(mismatches)}); a renewed written case and approval are "
                "required; no Runtime job was submitted"
            )
    record["budget_plan"] = qpu_planning.budget_plan(sys.modules[__name__], choices, args, service.usage())
    if not record["budget_plan"]["admitted"]:
        record["state"] = "budget_infeasible"
        checkpoint()
        raise LiveRunError("; ".join(record["budget_plan"]["reasons"]))
    submission, runtime_batches = build_submission_plan(choices, args, qpy_archive_sha256)
    submission["budget_reservation"] = record["budget_plan"]
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
        fresh = take_snapshot(service, name, (getattr(args, "exclude_qubits", None) or {}).get(name, ()))
        ineligible = fresh.ineligible_reason(args.max_pending)
        if ineligible:
            raise LiveRunError(f"{name}: {batch_tag} left the eligibility gate ({ineligible})")
        owner_reasons: dict[str, list[str]] = {}
        seen_owners: set[int] = set()
        for pub in batch:
            for component in pub.components:
                owner = component.choice
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
        # The approved-record check compared calibration timestamps at the
        # refresh; a calibration that rolls between that check and this
        # batch leaves the consumed values unchanged yet is unapproved.
        drift = approved_calibration_drift(record, name, fresh.calibration)
        if drift is not None:
            raise LiveRunError(f"{name}: {batch_tag} {drift}; no circuit in this batch was submitted")
        requested_delay = getattr(args, "rep_delay", None)
        if requested_delay is not None:
            batch_delay_violations = qpu_planning.repetition_delay_violations(
                fresh.backend, requested_delay, planned_repetition_delay_range(record, name)
            )
            if batch_delay_violations:
                reason = "; ".join(batch_delay_violations)
                if record["submission"]["jobs"]:
                    record["renewed_approval_for_unsent_batches"] = {"required_at": _now(), "reason": reason}
                else:
                    record["state"] = "approval_required"
                raise LiveRunError(f"{name}: {batch_tag} {reason}; no circuit in this batch was submitted")
        usage = service.usage()
        check_budget(name, usage, args.min_remaining_seconds)
        # Accepted jobs may remain unbilled. Every ceiling stays reserved until
        # collection supplies attributable final charge; quota snapshots alone
        # cannot release a particular job's reservation.
        remaining = usage.get("usage_remaining_seconds")
        reservation = record["submission"]["budget_reservation"]
        combined_ceiling = reservation["combined_ceiling_seconds"]
        required = combined_ceiling + reservation["reserve_seconds"] if combined_ceiling is not None else None
        if required is not None and remaining is not None and required > float(remaining):
            raise LiveRunError(
                f"{name}: unsettled execution ceilings and reserve require {required} s; remaining {remaining} s"
            )
        sampler = configure_sampler(
            fresh.backend,
            kind,
            args.twirl,
            args.dd,
            plan_entry["recovery_tags"],
            int(plan_entry["shots"]),
            getattr(args, "max_execution_seconds", None),
            **sampler_rep_delay(args),
        )
        effective_options = sampler.options.model_dump(mode="json")
        if effective_options != plan_entry["options"]:
            raise LiveRunError(f"{name}: {batch_tag} effective Sampler options moved after planning")
        ceiling = getattr(args, "max_execution_seconds", None)
        remaining = usage.get("usage_remaining_seconds")
        if ceiling is not None and remaining is not None and float(ceiling) > float(remaining):
            raise LiveRunError(
                f"{name}: {batch_tag} execution ceiling {ceiling} s exceeds the {remaining} s of QPU time remaining"
            )
        if approved_dir is not None and plan_index == runtime_batches[0][0]:
            # The authorization is spent at the first batch of the invocation;
            # a later batch of the same plan belongs to the same attempt.
            try:
                record["approval_consumed"] = consume_approval(Path(approved_dir), record["started"])
            except LiveRunError:
                record["state"] = "approval_required"
                checkpoint()
                raise
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
        job = sampler.run([pub.circuit for pub in batch])
        job_id = job.job_id()
        record["submission"]["jobs"].append(_job_record(plan_entry, job_id))
        plan_entry["state"] = "accepted"
        # The job id is the only handle on QPU time already spent; it reaches
        # disk before the next job is sent.
        record["state"] = "partially_submitted"
        checkpoint()
        component_count = sum(len(pub.components) for pub in batch)
        print(
            f"submitted {len(batch)} {batch_tag} fused PUBs ({component_count} logical entries) to {name}: job {job_id}"
        )
    record["submission"]["complete"] = True
    record["state"] = "submitted"
    checkpoint()


def configure_sampler(
    backend: Any,
    kind: str,
    twirl: bool,
    dd: str | None,
    tags: list[str],
    shots: int = SHOTS,
    max_execution_seconds: int | None = None,
    *,
    rep_delay: float | None = None,
) -> Sampler:
    """The client-side Sampler for one job: twirling and DD apply to static jobs only.

    execution.rep_delay takes rep_delay when given, else the backend default;
    either must lie in the backend's rep_delay_range (repetition-rate guide).

    Every job requests the backend scheduler's per-PUB timing, which
    scheduled_duration reads and packing_schedule compares.

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
    configuration = backend.configuration()
    if getattr(configuration, "dynamic_reprate_enabled", False):
        try:
            sampler.options.execution.rep_delay = qpu_planning.repetition_delay(backend, rep_delay)
        except ValueError as error:
            raise LiveRunError(str(error)) from error
    elif rep_delay is not None:
        raise LiveRunError("the backend runs a fixed repetition rate; --rep-delay needs dynamic_reprate_enabled")
    if max_execution_seconds is not None:
        # The service cancels a job whose system execution time passes this
        # ceiling (OptionsV2.max_execution_time), so the approved case's
        # seconds bound the charge the job can make.
        sampler.options.max_execution_time = int(max_execution_seconds)
    sampler.options.execution.scheduler_timing = True
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


# One classifier assigns IBM job kinds, group admission and the Aer method.
_is_dynamic = local_compute.is_dynamic


def _has_feed_forward(isa: QuantumCircuit) -> bool:
    """Whether classical control flow can make a measurement affect later quantum evolution."""
    return any(isinstance(instruction.operation, ControlFlowOp) for instruction in isa.data)


def _control_flow_count(circuit: QuantumCircuit) -> int:
    """Recursive count of control-flow operations, nested blocks included."""
    total = 0
    for instruction in circuit.data:
        if isinstance(instruction.operation, ControlFlowOp):
            total += 1 + sum(_control_flow_count(block) for block in instruction.operation.blocks)
    return total


def _feed_forward_stages(circuit: QuantumCircuit) -> int:
    """Maximum feed-forward decisions along one execution path: each branch counts one plus its deepest block."""
    stages = 0
    for instruction in circuit.data:
        if isinstance(instruction.operation, ControlFlowOp):
            stages += 1 + max((_feed_forward_stages(block) for block in instruction.operation.blocks), default=0)
    return stages


def _instance_hash(service: Any) -> str:
    """The active IBM Cloud instance as the 12-hex sha256 of its CRN, the only form a record keeps.

    A service without a resolved instance has no quota to plan against, so
    it is refused rather than hashed as the empty string.
    """
    instance = str(service.active_instance() or "")
    if not instance:
        raise LiveRunError("the service resolved no IBM Cloud instance; the saved account must name one")
    return hashlib.sha256(instance.encode()).hexdigest()[:12]


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


@dataclass(frozen=True)
class PubWindows:
    """Execution windows of each PUB in one job and the metadata path that supplied them.

    windows holds None for a PUB no span covers; reason explains an absent or
    unusable source and leaves every window None.
    """

    windows: list[tuple[datetime, datetime] | None]
    source: str | None
    reason: str | None


def pub_windows(result: Any, count: int) -> PubWindows:
    """Start and stop of the execution chunks that hold each PUB's shots.

    The 0.50 executor Sampler's post-processor (sampler_v2_post_processor_v0_1)
    returns result.metadata["executor"], a quantum-program Metadata whose
    chunk_timing lists ChunkSpan(start, stop, parts), each part naming the
    program item, one per PUB, that the chunk executed. IBM's Sampler
    input/output guide ("View execution spans") documents the earlier path
    result.metadata["execution"]["execution_spans"], spans whose pub_idxs name
    the PUBs. Which path a hardware job returns is recorded as the source. A
    chunk can hold several PUBs and a PUB can span several chunks, so a PUB's
    window runs from its first chunk's start to its last chunk's stop. The
    job-level running timestamp can precede the shots by server-side
    preparation, across a calibration update. Naive times are UTC.
    """
    executor = result.metadata.get("executor")
    chunks = getattr(executor, "chunk_timing", None)
    if chunks:
        spans = [(chunk.start, chunk.stop, [part.idx_item for part in chunk.parts]) for chunk in chunks]
        return _windows_from_spans("executor_chunk_timing", spans, count)
    execution = result.metadata.get("execution") or {}
    legacy = execution.get("execution_spans")
    if legacy is not None and len(legacy):
        spans = [(span.start, span.stop, list(span.pub_idxs)) for span in legacy]
        return _windows_from_spans("execution_spans", spans, count)
    keys = sorted(result.metadata)
    reason = f"result metadata carries no executor chunk timing or execution spans; keys {keys}"
    return PubWindows([None] * count, None, reason)


def _windows_from_spans(source: str, spans: list[tuple[datetime, datetime, list[int]]], count: int) -> PubWindows:
    outside = sorted({index for _, _, indices in spans for index in indices if not 0 <= index < count})
    if outside:
        return PubWindows([None] * count, source, f"{source} names PUB indices {outside} outside 0..{count - 1}")
    windows: list[tuple[datetime, datetime] | None] = []
    for idx in range(count):
        own = [(start, stop) for start, stop, indices in spans if idx in indices]
        if not own:
            windows.append(None)
            continue
        start, stop = min(start for start, _ in own), max(stop for _, stop in own)
        windows.append((_as_utc(start), _as_utc(stop)))
    return PubWindows(windows, source, None)


def _as_utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def scheduled_duration(pub_result: Any) -> tuple[int | None, str | None]:
    """The backend scheduler's circuit duration in dt, or None with the reason it is unusable.

    Sampler.options.execution.scheduler_timing asks the service for each PUB's
    compiled schedule, carried at metadata["compilation"]["scheduler_timing"]
    ["circuit_duration"] in dt (ItemMetadata.scheduler_timing). The schedule
    includes the classical latency that the Target omits, so a dynamic PUB's
    value is the duration the control system executes.
    """
    compilation = pub_result.metadata.get("compilation")
    timing = compilation.get("scheduler_timing") if isinstance(compilation, dict) else None
    if not isinstance(timing, dict) or "circuit_duration" not in timing:
        return None, "job returned no scheduler timing for the PUB"
    duration = timing["circuit_duration"]
    if (
        isinstance(duration, bool)
        or not isinstance(duration, (int, float))
        or not math.isfinite(duration)
        or duration != int(duration)
        or duration < 0
    ):
        return None, f"malformed scheduler circuit_duration {duration!r}: expected a nonnegative integer count of dt"
    return int(duration), None


def pub_timing(
    pub_manifest: dict[str, Any],
    window: tuple[datetime, datetime] | None,
    window_reason: str | None,
    scheduled: int | None,
    scheduled_reason: str | None,
    source: str | None,
    execution_bound: int | None = None,
) -> dict[str, Any]:
    """The timing record of one PUB: window, scheduled duration, residual, and structure.

    The residual subtracts the lower bound computed from the Target in force
    when the PUB's shots began (execution_bound); the manifest's plan-time
    bound is kept beside it, since a calibration update between planning and
    execution changes instruction durations, and a PUB without a window has
    no execution-time Target, so its residual is withheld. timing_status is
    complete when the window, the schedule, and a nonnegative residual are
    present; windows_only, schedule_only, or unavailable name what is
    missing; residual_below_target_bound keeps a schedule shorter than the
    Target's own critical path and withholds its interpretation. The
    structure fields come from the plan: the recursive count of control-flow
    operations in the fused PUB, the deepest feed-forward decision chain along
    one replica stream, and the number of replica streams that carry
    feed-forward.
    """
    lower = execution_bound if window else None
    residual = scheduled - lower if scheduled is not None and lower is not None else None
    reasons = [reason for reason in (window_reason, scheduled_reason) if reason]
    if scheduled is not None and lower is None and window is None:
        reasons.append("execution-time Target unknown without a window; residual withheld")
    if residual is not None and residual < 0:
        status = "residual_below_target_bound"
        reasons.append(f"scheduled duration {scheduled} dt is below the Target lower bound {lower} dt")
    elif residual is not None:
        status = "complete"
    elif window:
        status = "windows_only"
    elif scheduled is not None:
        status = "schedule_only"
    else:
        status = "unavailable"
    return {
        "timing_status": status,
        "timing_source": source if window else None,
        "execution_window_start": window[0].isoformat() if window else None,
        "execution_window_stop": window[1].isoformat() if window else None,
        "planned_target_gate_lower_bound_dt": pub_manifest.get("target_gate_lower_bound_dt"),
        "target_gate_lower_bound_dt": lower,
        "scheduled_circuit_duration_dt": scheduled,
        "scheduler_residual_dt": residual,
        "feed_forward_operation_count": pub_manifest.get("feed_forward_operation_count"),
        "sequential_stage_count": pub_manifest.get("sequential_stage_count"),
        "parallel_stream_count": pub_manifest.get("parallel_stream_count"),
        "groups": sorted({component["group"] for component in pub_manifest.get("components", [])}),
        "timing_unavailable_reason": "; ".join(reasons) if reasons else None,
    }


JOB_FINAL_STATES = ("DONE", "CANCELLED", "ERROR")
# The service computes a job's usage after the job ends; collection waits
# this long, polling at this interval, for the usage status to leave pending
# before it records the job as still pending.
USAGE_WAIT_SECONDS = 120.0
USAGE_POLL_SECONDS = 5.0


def wait_for_usage(
    job: Any,
    pub_count: int,
    shots: int,
    wait_seconds: float = USAGE_WAIT_SECONDS,
    poll_seconds: float = USAGE_POLL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """The job's usage record once its status leaves pending, or the pending record after wait_seconds.

    BaseRuntimeJob.usage reports zero until the service finishes the usage
    calculation, which follows the job's terminal state by an unspecified
    delay; a record left pending names the wait and a recollection updates
    only the usage block.
    """
    record = job_usage_record(job, pub_count, shots)
    waited = 0.0
    while record["usage_status"] == "pending" and str(job.status()) in JOB_FINAL_STATES and waited < wait_seconds:
        sleep(poll_seconds)
        waited += poll_seconds
        record = job_usage_record(job, pub_count, shots)
    if record["usage_status"] == "pending" and str(job.status()) in JOB_FINAL_STATES:
        record["throughput_unavailable_reason"] = (
            f"usage calculation still pending {wait_seconds:g} s after the job ended; recollect to update it"
        )
    return record


def job_usage_record(job: Any, pub_count: int, shots: int) -> dict[str, Any]:
    """The job's final QPU charge and submitted-PUB-shot throughput, or why they are withheld.

    job.metrics()["usage"] carries the raw usage metadata and its status;
    job.usage(partial=False) returns the canonical final charge once that
    status leaves pending (BaseRuntimeJob.usage). The numerator is the PUB
    count times the shots per PUB: packed replicas and fused components ride
    inside a PUB and multiply nothing, and only a DONE job, whose charge
    covers the whole workload, gets the quotient. The unit is submitted PUB
    shots per QPU charge second. The charge keeps the service's decimal text exactly; the
    rate rounds to three decimals.
    """
    status = str(job.status())
    metrics = job.metrics()
    raw = metrics.get("usage") if isinstance(metrics, dict) else None
    record: dict[str, Any] = {
        "job_status": status,
        "usage_status": "pending",
        "usage_source": None,
        "submitted_pub_shots": pub_count * shots,
        "qpu_charge_time_seconds": None,
        "pub_shots_per_qpu_second": None,
        "throughput_unavailable_reason": None,
        "raw_usage_metadata": copy.deepcopy(raw) if isinstance(raw, dict) else raw,
    }
    if status not in JOB_FINAL_STATES:
        record["throughput_unavailable_reason"] = f"job status {status} is not final"
        return record
    # The charge of a failed or cancelled job covers whatever part of the
    # workload ran, so dividing the full submitted shots by it overstates the
    # rate; the charge is kept for the budget audit alone.
    divide = status == "DONE"
    if not isinstance(raw, dict):
        record["usage_status"] = "missing"
        record["throughput_unavailable_reason"] = "job metrics carry no usage"
        return record
    if raw.get("status", "pending") == "pending":
        record["throughput_unavailable_reason"] = "usage status is pending"
        return record
    value = job.usage(partial=False)
    record["usage_source"] = "job.usage(partial=False)"
    if value is None:
        record["usage_status"] = "missing"
        record["throughput_unavailable_reason"] = "final usage carries no qpu_charge_time_seconds"
        return record
    try:
        charge = Decimal(str(value))
    except InvalidOperation:
        charge = Decimal("NaN")
    if isinstance(value, bool) or not charge.is_finite() or charge < 0:
        record["usage_status"] = "malformed"
        record["throughput_unavailable_reason"] = f"final usage {value!r} is not a finite nonnegative number"
        return record
    record["usage_status"] = "final"
    record["qpu_charge_time_seconds"] = str(charge)
    if not divide:
        record["throughput_unavailable_reason"] = f"job status {status} did not complete the workload"
        return record
    if charge == 0:
        record["throughput_unavailable_reason"] = "zero QPU charge; the division is withheld"
        return record
    rate = (Decimal(record["submitted_pub_shots"]) / charge).quantize(Decimal("0.001"), rounding=ROUND_HALF_EVEN)
    record["pub_shots_per_qpu_second"] = str(rate)
    return record


def component_execution_records(
    pub_manifest: dict[str, Any],
    window: tuple[datetime, datetime] | None,
    calibration: datetime | None,
    calibration_changed: bool | None,
    window_reason: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Fan one fused PUB's execution window and calibration out to every logical component.

    Timing and usage live once per PUB and job in the collection header; each
    component keeps only its PUB name and the calibration evidence that gates
    its summaries.
    """
    evidence = {
        "pub": pub_manifest["name"],
        "start": window[0].isoformat() if window else None,
        "stop": window[1].isoformat() if window else None,
        "calibration": calibration.isoformat() if calibration else None,
        "calibration_changed_during_shots": calibration_changed,
        "window_unavailable_reason": window_reason,
    }
    return {component["member"]: copy.deepcopy(evidence) for component in pub_manifest["components"]}


def packing_schedule(
    entries: list[Entry], executed: dict[str, dict[str, Any]], timing: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    """Scheduler residual of the packed primary's PUB against the shared replica-0 reference PUB.

    Both PUBs run in one job, so the comparison carries no queue drift; the
    scope is global when the packed PUB carries more than one group and
    single_group otherwise. The difference is a global packing scheduling
    cost: the packed PUB adds every replica's whole circuit, so measurement,
    reset, pulse-channel, and controller resources scale with replica count
    alongside feed-forward, and the difference is attributed to none of them
    without a matched control.
    """
    references = [e for e in entries if e.reference]
    if not references:
        return None
    primary = next(e for e in entries if not e.reference)
    packed, alone = executed.get(primary.name), executed.get(references[0].name)
    if packed is None or alone is None:
        return None
    packed_timing, alone_timing = timing[packed["pub"]], timing[alone["pub"]]
    groups = packed_timing.get("groups") or []
    out: dict[str, Any] = {
        "scope": "global" if len(groups) > 1 else "single_group",
        "groups": groups,
        "packed_pub": packed["pub"],
        "reference_pub": alone["pub"],
        "feed_forward": bool(packed_timing["parallel_stream_count"]),
        "packed_parallel_stream_count": packed_timing["parallel_stream_count"],
        "reference_parallel_stream_count": alone_timing["parallel_stream_count"],
        "packed_scheduled_circuit_duration_dt": packed_timing["scheduled_circuit_duration_dt"],
        "reference_scheduled_circuit_duration_dt": alone_timing["scheduled_circuit_duration_dt"],
        "packed_scheduler_residual_dt": packed_timing["scheduler_residual_dt"],
        "reference_scheduler_residual_dt": alone_timing["scheduler_residual_dt"],
    }
    # The two PUBs hold different gate content (every replica against one
    # copy), so their raw durations differ by gate time alone; only the
    # residuals, each above its own Target bound, compare scheduler time.
    missing = [
        name
        for name, pub in ((packed["pub"], packed_timing), (alone["pub"], alone_timing))
        if pub["scheduler_residual_dt"] is None or pub["timing_status"] != "complete"
    ]
    # One job does not guarantee one calibration: the residuals are compared
    # only when both PUBs ran under the same calibration with no update
    # inside either PUB's shots.
    same_calibration = (
        packed.get("calibration") is not None
        and packed.get("calibration") == alone.get("calibration")
        and not packed.get("calibration_changed_during_shots")
        and not alone.get("calibration_changed_during_shots")
    )
    if missing:
        out["unavailable"] = f"scheduler residual absent or not complete for {missing}"
    elif not same_calibration:
        out["unavailable"] = "the packed and reference PUBs did not both run under one unchanged calibration"
    else:
        out["residual_difference_dt"] = packed_timing["scheduler_residual_dt"] - alone_timing["scheduler_residual_dt"]
    return out


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
    """Why statistics that combine a group's components across PUBs are invalid, or None.

    A group's members occupy aligned cross-group PUBs, and every group summary
    combines multiple components: a dark/bright ratio, a fringe fit, a margin
    over a null, global packing crosstalk, and admission. A calibration update
    between those PUBs would read as the experiment's signal, so every
    contributing PUB needs one shared calibration with no update inside its
    shots.
    """
    ran = [executed[n] for n in names if n in executed]
    unknown = [n for n in names if n in executed and executed[n]["calibration"] is None]
    if unknown:
        return f"execution windows are unavailable for {unknown}, so the calibration at execution is unknown"
    if any(e["calibration_changed_during_shots"] for e in ran) or len({e["calibration"] for e in ran}) > 1:
        return "the group's PUBs did not all run under one calibration"
    return None


def _single_pub_views(stats: dict[str, Any]) -> dict[str, Any]:
    """The views of stats computed within one PUB each: every entry's replica variance."""
    return {"variance": stats["variance"]}


def _validate_archived_pub(pub_manifest: dict[str, Any], circuit: QuantumCircuit, backend: str, kind: str) -> None:
    """Prove one retained PUB manifest describes its exact archived circuit."""
    name = str(pub_manifest.get("name"))
    if name != circuit.name:
        raise LiveRunError(f"fused PUB manifest {name!r} names QPY circuit {circuit.name!r}")
    if pub_manifest.get("backend") != backend or pub_manifest.get("kind") != kind:
        raise LiveRunError(f"{name}: fused PUB manifest differs from its job backend or kind")
    actual_kind = "dynamic" if _is_dynamic(circuit) else "static"
    if actual_kind != kind:
        raise LiveRunError(f"{name}: QPY circuit is {actual_kind}, planned job is {kind}")
    components = pub_manifest.get("components", [])
    if not components:
        raise LiveRunError(f"{name}: fused PUB manifest has no logical components")
    prefixes = [component.get("register_prefix") for component in components]
    if any(not isinstance(prefix, str) or not prefix for prefix in prefixes) or len(prefixes) != len(set(prefixes)):
        raise LiveRunError(f"{name}: fused PUB manifest has invalid or duplicate register prefixes")
    recorded_registers = [
        register_name
        for component in components
        for replica_registers in component.get("registers_by_replica", [])
        for register_name in replica_registers
    ]
    archived_registers = [register.name for register in circuit.cregs]
    if recorded_registers != archived_registers:
        raise LiveRunError(f"{name}: fused PUB manifest register order differs from isa.qpy")

    occupied: set[int] = set()
    touched_by_component: list[set[int]] = [set() for _ in components]
    physical_by_component: list[set[int]] = []
    for component, prefix in zip(components, prefixes, strict=True):
        register_groups = component.get("registers_by_replica", [])
        if not register_groups or any(not group for group in register_groups):
            raise LiveRunError(f"{name}: component {component.get('member')!r} has an empty register group")
        if any(not register_name.startswith(prefix) for group in register_groups for register_name in group):
            raise LiveRunError(f"{name}: component {component.get('member')!r} has a register outside {prefix!r}")
        physical = set(component.get("physical_qubits", []))
        if not physical or any(
            not isinstance(qubit, int) or qubit < 0 or qubit >= circuit.num_qubits for qubit in physical
        ):
            raise LiveRunError(f"{name}: component {component.get('member')!r} has invalid physical qubits")
        overlap = occupied.intersection(physical)
        if overlap:
            raise LiveRunError(f"{name}: fused PUB manifest overlaps component qubits {sorted(overlap)}")
        occupied.update(physical)
        physical_by_component.append(physical)
    for instruction in circuit.data:
        instruction_qubits = {circuit.find_bit(qubit).index for qubit in instruction.qubits}
        if not instruction_qubits:
            continue
        owners = [index for index, physical in enumerate(physical_by_component) if instruction_qubits <= physical]
        if len(owners) != 1:
            raise LiveRunError(f"{name}: QPY instruction qubits {sorted(instruction_qubits)} have {len(owners)} owners")
        touched_by_component[owners[0]].update(instruction_qubits)
    for component, physical, touched in zip(components, physical_by_component, touched_by_component, strict=True):
        # A group's placement reserves the union needed by every member. One
        # member, such as a null control, can touch only a strict subset.
        if not touched or not touched <= physical:
            raise LiveRunError(
                f"{name}: component {component.get('member')!r} touches qubits outside its reserved footprint"
            )


def _archived_entries(record: dict[str, Any], isas: dict[str, QuantumCircuit]) -> dict[str, list[Entry]]:
    """Rebuild logical entries from archived fused PUBs and their component map."""
    weights = {m.name: m.weights for g in [*all_experiment_groups(), *record_groups(record)] for m in g.members}
    planned_jobs = record.get("submission", {}).get("planned_jobs")
    if planned_jobs is None:
        raise LiveRunError("schema-5 collection needs the immutable fused-PUB submission plan")
    components: dict[str, tuple[str, dict[str, Any]]] = {}
    for planned_job in planned_jobs:
        for pub in planned_job["pubs"]:
            if pub["name"] not in isas:
                raise LiveRunError(f"planned fused PUB {pub['name']!r} is absent from isa.qpy")
            _validate_archived_pub(pub, isas[pub["name"]], planned_job["backend"], planned_job["kind"])
            for component in pub["components"]:
                member_name = component["member"]
                if member_name in components:
                    raise LiveRunError(f"logical member {member_name!r} appears in multiple fused PUB components")
                components[member_name] = (pub["name"], component)
    out: dict[str, list[Entry]] = {}
    for group in record["groups"]:
        entries = out.setdefault(group["group"], [])
        for member in group["members"]:
            member_name = member["name"]
            if member_name not in components:
                raise LiveRunError(f"logical member {member_name!r} has no fused PUB component")
            pub_name, component = components[member_name]
            if component["group"] != group["group"] or bool(component["reference"]) != bool(member["reference"]):
                raise LiveRunError(f"logical member {member_name!r} differs between group record and PUB map")
            component_prefix = component["register_prefix"]
            physical_qubits = sorted({qubit for replica in member["replica_qubits"] for qubit in replica})
            if physical_qubits != component["physical_qubits"]:
                raise LiveRunError(f"logical member {member_name!r} differs from its PUB-map physical qubits")
            packed = packing.extract(isas[pub_name], component_prefix, physical_qubits, member_name)
            expected_registers_by_replica = [
                packing.registers(packed, component_prefix + replica_prefix)
                for replica_prefix in member["replica_prefixes"]
            ]
            if component["registers_by_replica"] != expected_registers_by_replica:
                raise LiveRunError(f"logical member {member_name!r} register map differs from isa.qpy")
            prefixes = [component_prefix + prefix for prefix in member["replica_prefixes"]]
            replicas = [
                packing.split(packed, prefix, qubits, member_name)
                for prefix, qubits in zip(prefixes, member["replica_qubits"], strict=True)
            ]
            weight_name = member_name
            if member["reference"] and member_name not in weights:
                weight_name = member_name.removesuffix(ISOLATED_SUFFIX)
            entries.append(
                Entry(
                    name=member_name,
                    base=replicas[0],
                    ideal=np.asarray(member["ideal"]),
                    packed=packed,
                    replicas=replicas,
                    prefixes=prefixes,
                    replica_qubits=member["replica_qubits"],
                    reference=member["reference"],
                    weights=weights.get(weight_name),
                )
            )
    return out


def collect(service: QiskitRuntimeService, run_dir: Path) -> None:
    """Measured replica distributions against the noise model of the calibration in force at execution."""
    record = json.loads((run_dir / "record.json").read_text())
    qpy_bytes = (run_dir / "isa.qpy").read_bytes()
    groups = {g.name: g for g in [*all_experiment_groups(), *record_groups(record)]}
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
    archived_circuits = list(qpy.load(io.BytesIO(qpy_bytes)))
    isas = {circuit.name: circuit for circuit in archived_circuits}
    if len(isas) != len(archived_circuits):
        raise LiveRunError("isa.qpy contains duplicate fused-PUB circuit names")
    if planned_jobs is not None:
        planned_members = [member for planned_job in planned_jobs for member in planned_job["members"]]
        if len(planned_members) != len(set(planned_members)):
            raise LiveRunError("submission plan assigns one logical member to multiple jobs")
        planned_pubs = [pub for planned_job in planned_jobs for pub in planned_job["pubs"]]
        planned_pub_names = [pub["name"] for pub in planned_pubs]
        if len(planned_pub_names) != len(set(planned_pub_names)):
            raise LiveRunError("submission plan assigns one fused PUB to multiple jobs")
        mapped_members = [component["member"] for pub in planned_pubs for component in pub["components"]]
        if mapped_members != planned_members:
            raise LiveRunError("submission plan flat members differ from the ordered fused-PUB component map")
        missing_from_plan = sorted(set(isas) - set(planned_pub_names))
        missing_from_archive = sorted(set(planned_pub_names) - set(isas))
        if missing_from_plan or missing_from_archive:
            raise LiveRunError(
                "submission plan and QPY archive differ: "
                f"archive-only={missing_from_plan}, plan-only={missing_from_archive}"
            )
        for planned_job in planned_jobs:
            for pub in planned_job["pubs"]:
                if pub["name"] not in isas:
                    raise LiveRunError(f"planned fused PUB {pub['name']!r} is absent from isa.qpy")
                _validate_archived_pub(pub, isas[pub["name"]], planned_job["backend"], planned_job["kind"])
        submission_gaps(submission)
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
    jobs_out: dict[str, dict[str, Any]] = {}

    # Checkpoints go to collect.partial.json, so a failure after a job's
    # usage is read keeps that usage without replacing a complete earlier
    # collect.json with an incomplete one; the final write replaces
    # collect.json and removes the partial file.
    def checkpoint(entries_out: list[dict[str, Any]], final: bool = False) -> None:
        text = json.dumps(entries_out, indent=2) + "\n"
        target = run_dir / ("collect.json" if final else "collect.partial.json")
        _replace_atomically(target, lambda handle: handle.write(text), "w")
        if final:
            (run_dir / "collect.partial.json").unlink(missing_ok=True)

    out: list[dict[str, Any]] = [
        {
            "submission_complete": bool(submission.get("complete", False)),
            "backends_without_recorded_job_id": backends_without_id,
            "members_without_recorded_job_id": members_without_id,
            "jobs_without_recorded_id": jobs_without_id,
            "jobs": jobs_out,
        }
    ]
    family_measured: dict[str, list[np.ndarray]] = {}
    family_replayed: dict[str, list[np.ndarray]] = {}
    family_executed: dict[str, Any] = {}
    correction_family = record.get("family_configuration", {}).get("name") == "folded-correction"
    correction_evidence: list[dict[str, Any]] = []
    for job_entry in record["submission"]["jobs"]:
        shots = _recorded_job_shots(record, job_entry)
        job = service.job(job_entry["job_id"])
        pub_manifests = job_entry["pubs"]
        # Usage is read before the results and checkpointed to collect.json
        # at once: a job that ended in ERROR or CANCELLED raises on result()
        # and still carries a QPU charge, and a later job's failure must not
        # lose an earlier job's charge. A job still running when collection
        # starts reports pending usage here; result() waits for it, and the
        # usage is read again once the shots are in.
        job_out = {
            "backend": job_entry["backend"],
            "kind": job_entry["kind"],
            "usage": job_usage_record(job, len(pub_manifests), shots),
            "pub_timing": {},
        }
        jobs_out[job_entry["job_id"]] = job_out
        checkpoint(out)
        # The configuration identity is read once the charge is on disk and
        # before result(), so a job that ended in ERROR or CANCELLED keeps it;
        # a job with results adds the version at each execution start below.
        # Identity is provenance: a backend the account no longer serves
        # records None fields, and only a job with results needs the backend.
        backend: Any = None
        try:
            backend = service.backend(job_entry["backend"])
        except Exception:  # noqa: BLE001 - QiskitBackendNotFoundError and transport faults alike leave identity unread
            backend = None
        job_out["backend_identity"] = execution_identity(backend, {})
        try:
            result = job.result()
        except Exception as error:  # noqa: BLE001 - the service raises its own hierarchy for failed jobs
            # Only a job that ended in ERROR or CANCELLED is expected to
            # raise here; a retrieval or decoding failure on a DONE job
            # propagates, so a transient fault never passes for a result.
            if str(job.status()) not in ("ERROR", "CANCELLED"):
                raise
            job_out["result_unavailable"] = f"{type(error).__name__}: {error}"
            if job_out["usage"]["usage_status"] == "pending":
                job_out["usage"] = wait_for_usage(job, len(pub_manifests), shots)
            checkpoint(out)
            continue
        # The lossless result reaches disk before any count is validated,
        # decoded, replayed, or summarized.
        job_out["raw"] = write_raw_result(
            run_dir, job_entry["job_id"], job, result, [pub["name"] for pub in pub_manifests]
        )
        checkpoint(out)
        if job_out["usage"]["usage_status"] == "pending":
            job_out["usage"] = wait_for_usage(job, len(pub_manifests), shots)
            snapshot_metrics(run_dir, job_entry["job_id"], job)
            checkpoint(out)
        if len(result) != len(pub_manifests):
            raise LiveRunError(
                f"job {job_entry['job_id']} returned {len(result)} PUB results for "
                f"{len(pub_manifests)} planned fused PUBs"
            )
        spans = pub_windows(result, len(pub_manifests))
        twirled_readout = bool(job_entry.get("options", {}).get("twirling", {}).get("enable_measure"))
        if backend is None:
            backend = service.backend(job_entry["backend"])
        # One calibration fetch per distinct execution start: a PUB is replayed
        # under the Target and properties in force when its shots began, and
        # its scheduler residual is read against that Target's durations.
        at: dict[datetime, tuple[Any, Any, Any]] = {}
        for window in spans.windows:
            if window is None or window[0] in at:
                continue
            start = window[0]
            props_then = backend.properties(datetime=start)
            target_then = backend.target_history(datetime=start)
            at[start] = (
                props_then,
                noise_simulator(
                    f"{backend.name}@{start.isoformat()}",
                    target_then,
                    props_then,
                    record.get("policy", {}).get("local_compute", local_compute.settings()),
                ),
                target_then,
            )
            starting = [
                isas[pub_manifest["name"]]
                for other, pub_manifest in zip(spans.windows, pub_manifests, strict=True)
                if other is not None and other[0] == start
            ]
            check_target_matches_properties(starting, target_then, props_then, f"{backend.name}@{start}")
        # Timing and usage are recorded once per PUB and per job; a PUB without
        # a window keeps its counts and loses only its calibration-bound views,
        # the residual among them.
        timing: dict[str, dict[str, Any]] = {}
        for pub_manifest, pub_result, window in zip(pub_manifests, result, spans.windows, strict=True):
            scheduled, scheduled_reason = scheduled_duration(pub_result)
            window_reason = (
                None if window else spans.reason or f"no {spans.source} chunk covers PUB {pub_manifest['name']}"
            )
            execution_bound = target_duration_dt(isas[pub_manifest["name"]], at[window[0]][2]) if window else None
            timing[pub_manifest["name"]] = pub_timing(
                pub_manifest, window, window_reason, scheduled, scheduled_reason, spans.source, execution_bound
            )
        jobs_out[job_entry["job_id"]]["pub_timing"] = timing
        job_out["backend_identity"] = execution_identity(backend, {start: entry[0] for start, entry in at.items()})
        measured: dict[str, list[np.ndarray]] = {}
        props_by_name: dict[str, Any] = {}
        replayed: dict[str, list[np.ndarray]] = {}
        executed: dict[str, dict[str, Any]] = {}
        # Every windowed component of the job replays in one batch per
        # calibration, in manifest order, and replay_entries gives each batch
        # its own seed, so no two components of the job share a (seed,
        # position) pair: a reference at the head of its own batch would
        # otherwise repeat packed replica 0 shot for shot.
        replay_batches: dict[datetime, list[Entry]] = {}
        sims_by_calibration: dict[datetime, Any] = {}
        for pub_index, (pub_manifest, pub_result, window) in enumerate(
            zip(pub_manifests, result, spans.windows, strict=True)
        ):
            if window is None:
                execution_records = component_execution_records(
                    pub_manifest, None, None, None, timing[pub_manifest["name"]]["timing_unavailable_reason"]
                )
            else:
                start, stop = window
                props_then = at[start][0]
                stop_calibration = backend.properties(datetime=stop).last_update_date
                execution_records = component_execution_records(
                    pub_manifest,
                    window,
                    props_then.last_update_date,
                    stop_calibration != props_then.last_update_date,
                )
            for component in pub_manifest["components"]:
                name = component["member"]
                entry = by_name[name]
                replica_counts = [
                    _pub_counts(pub_result, packing.registers(entry.packed, prefix), name) for prefix in entry.prefixes
                ]
                if any(sum(counts.values()) != shots for counts in replica_counts):
                    raise LiveRunError(f"{name}: returned shot count differs from the planned {shots}")
                if correction_family:
                    try:
                        if len(replica_counts) != 1:
                            raise ValueError("correction collection requires exactly one replica")
                        correction_evidence.append(
                            correction_collection.retained_member(
                                run_dir,
                                job_out["raw"],
                                job_id=job_entry["job_id"],
                                pub_index=pub_index,
                                pub_manifest=pub_manifest,
                                member=name,
                                circuit=isas[pub_manifest["name"]],
                                histogram=replica_counts[0],
                                dt_seconds=float(at[window[0]][2].dt) if window else None,
                            )
                        )
                    except (ValueError, KeyError, TypeError, IndexError, AttributeError, OSError) as error:
                        correction_evidence.append({"name": name, "error": str(error)})
                measured[name] = [
                    _distribution(counts, replica.num_clbits)
                    for counts, replica in zip(replica_counts, entry.replicas, strict=True)
                ]
                executed[name] = execution_records[name] | {"shots": shots}
                if window is not None:
                    props_then = at[window[0]][0]
                    props_by_name[name] = props_then
                    calibration = props_then.last_update_date
                    sims_by_calibration.setdefault(calibration, at[window[0]][1])
                    replay_batches.setdefault(calibration, []).append(entry)
        replayed = replay_entries(sims_by_calibration, replay_batches, shots, seed)
        family_measured.update(measured)
        family_replayed.update(replayed)
        family_executed.update(executed)
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
                "job_id": job_entry["job_id"],
                "executed": {n: executed[n] for n in required if n in executed},
                "packing_schedule": packing_schedule(entries, executed, timing),
                "measured": {
                    n: [[round(float(p), 6) for p in dist] for dist in measured[n]] for n in required if n in measured
                },
            }
            if correction_family:
                out_entry["integer_counts"] = {
                    row["name"]: row["counts"]
                    for row in correction_evidence
                    if row["name"] in required and "counts" in row
                }
                comparison_reason = _comparisons_withheld(required, executed)
                if missing or comparison_reason:
                    out_entry["comparisons_withheld"] = comparison_reason or f"missing {missing}"
                out_entry["inference"] = "the header family_analysis gates the sole exact-binomial optimizer decision"
                out.append(out_entry)
                continue
            # A circuit whose shots straddle a calibration update, or whose
            # window is unknown, has no single calibration to correct or replay
            # against; its group keeps the raw measurement and states why the
            # rest is absent.
            straddling = [n for n in required if n in executed and executed[n]["calibration_changed_during_shots"]]
            unwindowed = [n for n in required if n in executed and executed[n]["calibration"] is None]
            if missing:
                out_entry["summary_unavailable"] = f"missing {missing}"
                out.append(out_entry)
                continue
            primary_pub = executed[required[0]]["pub"]
            pub_groups = timing[primary_pub].get("groups") or []
            scope = {"scope": "global" if len(pub_groups) > 1 else "single_group", "groups": pub_groups}
            stats = replica_statistics(group, entries, measured, shots, scope)
            comparison_reason = _comparisons_withheld(required, executed)
            if comparison_reason:
                # Every summary combines components from multiple fused PUBs,
                # so under split calibrations only each entry's own replica
                # variance stands; the raw distributions stay for reanalysis.
                out_entry["comparisons_withheld"] = comparison_reason
                out_entry["measured_statistics"] = _single_pub_views(stats)
                if straddling or unwindowed:
                    unavailable = []
                    if straddling:
                        unavailable.append(f"calibration changed during the shots of {straddling}")
                    if unwindowed:
                        unavailable.append(f"execution windows unavailable for {unwindowed}")
                    out_entry["calibration_dependent_summaries_unavailable"] = "; ".join(unavailable)
                else:
                    out_entry["replayed_statistics"] = _single_pub_views(
                        replica_statistics(group, entries, replayed, shots, scope)
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
            out_entry["packing_interpretation"] = packing_interpretation(
                out_entry["packing_schedule"], stats.get("global_packing_crosstalk")
            )
            out_entry["measured_summary_readout_corrected"] = _without_odr(
                corrected_summary(group, entries, measured, props_by_name, symmetric=twirled_readout),
                pooled_reason,
            )
            out_entry["replayed_statistics"] = _gate_odr(
                replica_statistics(group, entries, replayed, shots, scope), pooled_reason, replica_reason
            )
            out_entry["tvd_measured_to_replayed"] = {
                n: [tvd(m, r) for m, r in zip(measured[n], replayed[n], strict=True)] for n in required
            }
            out.append(out_entry)
    if record.get("pub_shots") is not None:
        out[0]["family_measurements"] = {
            name: {
                "replica_probabilities": [distribution.tolist() for distribution in distributions],
                "execution": family_executed[name],
                "replayed_replica_probabilities": (
                    [distribution.tolist() for distribution in family_replayed[name]]
                    if name in family_replayed and not family_executed[name]["calibration_changed_during_shots"]
                    else None
                ),
                "replay_status": (
                    "calibration_changed_during_shots"
                    if family_executed[name]["calibration_changed_during_shots"]
                    else "calibration_bound"
                    if name in family_replayed
                    else "execution_window_unavailable"
                ),
            }
            for name, distributions in family_measured.items()
        }
    if record.get("observable_contracts") or correction_family:
        # A declared covariance bound is tested on the shot-ordered registers
        # write_raw_result retained above, the bytes a replay reads.
        bounded_pubs = {bound["pub_name"] for bound in record.get("covariance_bounds", [])}
        out[0]["family_analysis"] = qpu_planning.measured_family(
            record,
            family_measured,
            family_executed,
            sys.modules[__name__],
            correction_evidence=correction_evidence if correction_family else None,
            replica_registers=(
                qpu_planning.n21_exact_planning.retained_registers(run_dir, bounded_pubs) if bounded_pubs else None
            ),
        )
    out[0]["invocation_usage"] = invocation_usage(record, jobs_out)
    checkpoint(out, final=True)
    print(json.dumps(out, indent=2))


def invocation_usage(record: dict[str, Any], jobs_out: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compare predicted full-workload charge only after successful final execution."""
    submission = record["submission"]
    final_charges = {
        job_id: Decimal(job["usage"]["qpu_charge_time_seconds"])
        for job_id, job in jobs_out.items()
        if job["usage"].get("usage_status") == "final"
    }
    charge_complete = bool(submission.get("complete")) and len(final_charges) == len(submission["jobs"])
    known_charge = sum(final_charges.values(), Decimal(0))
    selected = record.get("optimization", {}).get("selected")
    selected_prediction: dict[str, Any] = next(
        (
            candidate
            for candidate in record.get("optimization", {}).get("candidates", [])
            if candidate["name"] == selected
        ),
        {},
    )
    prediction = selected_prediction.get("estimated_charge_seconds")
    workload_complete = charge_complete and all(job["usage"].get("job_status") == "DONE" for job in jobs_out.values())
    return {
        "known_final_charge_seconds": str(known_charge),
        "total_charge_seconds": str(known_charge) if charge_complete else None,
        "charge_complete": charge_complete,
        "workload_complete": workload_complete,
        "predicted_charge_seconds": prediction,
        "charge_prediction_residual_seconds": float(known_charge) - prediction
        if workload_complete and prediction is not None
        else None,
        "charge_prediction_residual_withheld": (
            "the complete planned workload lacks final charge or successful completion"
            if not workload_complete
            else "the record contains no selected cost prediction"
            if prediction is None
            else None
        ),
        "jobs_without_final_charge": sorted(set(jobs_out) - final_charges.keys()),
    }


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


def _cost_scenario(value: str) -> dict[str, Any]:
    """Parse an explicit sensitivity assumption; the values carry zero confidence claims."""
    try:
        name, overhead, latency = value.split(":")
        values = [float(overhead), float(latency)]
    except ValueError as error:
        raise argparse.ArgumentTypeError("cost scenario needs NAME:OVERHEAD_SECONDS:LATENCY_US") from error
    if (
        not name
        or name[0] not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        or any(
            character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for character in name
        )
    ):
        raise argparse.ArgumentTypeError("cost scenario name starts with a letter/digit and uses letters/digits/_/-")
    if name == "nominal":
        raise argparse.ArgumentTypeError("cost scenario name nominal is reserved for the base cost model")
    if any(not math.isfinite(number) or number < 0 for number in values):
        raise argparse.ArgumentTypeError("cost scenario overhead and latency must be finite and nonnegative")
    return {"name": name, "job_overhead_seconds": values[0], "classical_latency_us": values[1]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backends", type=lambda s: s.split(","), help="comma-separated pin; default all accessible")
    parser.add_argument("--groups", type=lambda s: s.split(","), help="comma-separated experiment groups")
    parser.add_argument(
        "--exclude-qubits",
        action="append",
        type=_qubit_exclusion,
        metavar="BACKEND:Q[,Q|A-B...]",
        help="withhold these physical qubits of BACKEND from placement whatever their calibration; repeatable",
    )
    parser.add_argument(
        "--family", choices=FAMILY_NAMES, help="complete experiment family with statistical design admission"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="search bounded shot and replica tiers for the experiment family"
    )
    parser.add_argument(
        "--shot-allocation",
        choices=("uniform", "per-pub"),
        default="uniform",
        help="allocate declared shot tiers to complete static algebra PUBs before measurement",
    )
    parser.add_argument(
        "--objective",
        choices=("minimum_charge", "precision_at_budget"),
        default="minimum_charge",
        help="rank admitted designs by charge or worst normalized precision within the declared budget",
    )
    parser.add_argument(
        "--cost-scenario",
        dest="cost_scenarios",
        action="append",
        type=_cost_scenario,
        default=[],
        help="require an additional cost assumption NAME:OVERHEAD_SECONDS:LATENCY_US; repeat for a finite set",
    )
    parser.add_argument(
        "--patch-qubits",
        type=lambda value: [int(item) for item in value.split(",")],
        help="physical qubits of the patch, in patch_characterization.PATCH_ROLES order; "
        "omitted, the planner chooses the best calibrated patch on every eligible backend",
    )
    parser.add_argument("--local-compute", choices=("cpu", "gpu", "auto"), default="auto")
    parser.add_argument(
        "--local-compute-method",
        choices=local_compute.QUALIFIED_METHODS,
        default=local_compute.DYNAMIC_STATEVECTOR,
        help="density_matrix replays records planned before dynamic batches ran statevector trajectories",
    )
    parser.add_argument("--simulation-threads", type=_positive_int, default=parallel.default_threads())
    parser.add_argument("--simulation-memory-mb", type=_positive_int, default=512)
    parser.add_argument(
        "--shot-tiers",
        type=lambda value: [_positive_int(item) for item in value.split(",")],
        default=[2048, 4096, 8192, 16384],
    )
    parser.add_argument(
        "--replica-tiers", type=lambda value: [_positive_int(item) for item in value.split(",")], default=[1, 2, 4]
    )
    parser.add_argument(
        "--optimizer-candidates",
        type=_positive_int,
        default=6,
        help="maximum routed family sets before replica and shot expansion",
    )
    parser.add_argument("--model-shots", type=_positive_int, default=32768)
    parser.add_argument(
        "--model-method",
        choices=("sampled", "exact"),
        default="sampled",
        help="exact plans an N21 family on dynamic_density's branch-resolved law, validated against "
        "--model-shots sampled shots; sampled keeps the finite-simulation allowance",
    )
    parser.add_argument(
        "--replica-variance-bound",
        type=float,
        help="declared per-replica score variance bound with independent replicas (N21 families); "
        "the planner applies it through Cantelli or Chebyshev and the collector after its falsifier passes",
    )
    parser.add_argument(
        "--precision",
        type=float,
        help="simultaneous half-width for family precision endpoints; default 0.08, and "
        "coherence_window.COHERENCE_PRECISION for coherence-window; patch-window preregisters its own",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--power", type=float, default=0.8)
    parser.add_argument("--simulation-alpha", type=float, default=0.01)
    parser.add_argument(
        "--job-overhead-seconds",
        type=float,
        default=2.3,
        help="explicit planning assumption; historical dynamic-job overhead",
    )
    parser.add_argument(
        "--classical-latency-us",
        type=float,
        default=20.0,
        help="explicit unmeasured per-feed-forward-stage cost assumption",
    )
    parser.add_argument("--reserve-seconds", type=float, default=0.0, help="quota retained after all job ceilings")
    parser.add_argument(
        "--max-total-execution-seconds",
        type=float,
        help="combined ceiling across every backend and job; required for submission and diagnostic design",
    )
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS, help="transpiler seeds per group and backend")
    parser.add_argument("--max-pending", type=int, default=DEFAULT_MAX_PENDING)
    parser.add_argument("--out", type=Path, help="directory under which the run's audit record is written")
    parser.add_argument("--submit", action="store_true", help="submit the chosen circuits (spends QPU time)")
    parser.add_argument(
        "--native-dry-run",
        action="store_true",
        help="qualify an admitted archived plan through Runtime mock execution, with dry_run=True",
    )
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
        help="put each group's replica-0 primary in the shared global reference PUB",
    )
    parser.add_argument(
        "--cross-group-buffer",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="keep replicas of different groups one CZ hop apart (the multi-programming crosstalk window)",
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
    parser.add_argument(
        "--preserve-raw",
        type=Path,
        help="run directory whose submitted jobs' results to write losslessly under raw/, without analysis",
    )
    parser.add_argument(
        "--approved-record",
        type=Path,
        help="run directory of the approved dry run; --submit sends nothing unless the fresh plan matches it",
    )
    parser.add_argument(
        "--approved-record-sha256",
        help="sha256 of the approved record's record.json, as the written case names it",
    )
    parser.add_argument(
        "--rep-delay",
        type=float,
        metavar="SECONDS",
        help=(
            "Sampler execution.rep_delay for every job, within each backend's rep_delay_range; the charge model "
            "and the approval bind it; default the backend's default_rep_delay"
        ),
    )
    parser.add_argument(
        "--max-execution-seconds",
        type=int,
        help=(
            "Sampler max_execution_time, the ceiling the written case names: the service cancels a job past "
            "this QPU usage; a dry run carries it so the approved record's policy matches the submission"
        ),
    )
    args = parser.parse_args(argv)
    exclusions: dict[str, set[int]] = {}
    for backend_name, qubits in args.exclude_qubits or []:
        exclusions.setdefault(backend_name, set()).update(qubits)
    args.exclude_qubits = {name: frozenset(qubits) for name, qubits in sorted(exclusions.items())} or None
    if args.native_dry_run and (args.submit or args.collect or args.preserve_raw):
        parser.error("--native-dry-run requires a separate submit-free planning invocation")
    if args.native_dry_run and (not args.out or not args.family):
        parser.error("--native-dry-run needs --out and a statistically admitted --family")
    if args.submit and not args.out:
        parser.error("--submit needs --out so the job ids land in an audit record")
    if args.submit and not args.approved_record:
        parser.error("--submit needs --approved-record, the dry run the written case was approved on")
    if args.approved_record and not args.submit:
        parser.error("--approved-record applies only with --submit")
    if args.submit and not args.approved_record_sha256:
        parser.error("--submit needs --approved-record-sha256, the record.json digest the written case names")
    if args.submit and args.max_execution_seconds is None:
        parser.error("--submit needs --max-execution-seconds, the execution ceiling the written case names")
    if args.approved_record_sha256 and not args.submit:
        parser.error("--approved-record-sha256 applies only with --submit")
    if args.max_execution_seconds is not None and args.max_execution_seconds <= 0:
        parser.error("--max-execution-seconds must be positive")
    if args.rep_delay is not None and (not math.isfinite(args.rep_delay) or args.rep_delay < 0):
        parser.error("--rep-delay must be finite and nonnegative seconds")
    if args.rep_delay is not None and args.family == "folded-correction":
        parser.error("folded-correction binds the backend default repetition delay in its preparation report")
    if args.seeds <= 0:
        parser.error("--seeds must be positive")
    if args.submit and args.max_total_execution_seconds is None:
        parser.error("--submit needs --max-total-execution-seconds, the combined invocation ceiling")
    if args.family and (args.groups or args.twirl or args.dd):
        parser.error("matched families require their complete group set and a common unmitigated execution policy")
    if args.optimize and not args.family:
        parser.error("--optimize requires --family and its explicit scientific observable contract")
    if (args.objective != "minimum_charge" or args.cost_scenarios) and not args.family:
        parser.error("--objective and --cost-scenario require --family scientific admission")
    if args.objective == "precision_at_budget" and args.family != "folded-qpe":
        parser.error("precision_at_budget requires the folded-qpe precision-only family")
    if len({scenario["name"] for scenario in args.cost_scenarios}) != len(args.cost_scenarios):
        parser.error("--cost-scenario names must be distinct")
    if args.family and (args.max_execution_seconds is None or args.max_total_execution_seconds is None):
        parser.error("--family needs per-job --max-execution-seconds and combined --max-total-execution-seconds")
    if args.family == "folded-qpe" and args.max_replicas not in (None, 1):
        parser.error("the folded family uses one fixed physical placement per candidate; --max-replicas must be 1")
    if (args.model_method != "sampled" or args.replica_variance_bound is not None) and (
        args.family not in N21_FAMILIES
    ):
        parser.error("--model-method exact and --replica-variance-bound apply to the N21 families only")
    if args.patch_qubits is not None and args.family not in PATCH_FAMILIES:
        parser.error("--patch-qubits applies to the pinned-patch families only")
    if args.family in PATCH_FAMILIES and args.max_replicas not in (None, 1):
        parser.error("the patch family runs one pinned placement; --max-replicas must be 1")
    if args.family == "folded-correction":
        if args.native_dry_run:
            parser.error("folded-correction uses fresh live calibration and post-execution schedules; mock is disabled")
        if args.max_execution_seconds != 30 or args.max_total_execution_seconds != 30:
            parser.error("folded-correction requires a 30-second per-job ceiling and aggregate cap")
        if not args.cost_scenarios or any(
            scenario["job_overhead_seconds"] < args.job_overhead_seconds
            or scenario["classical_latency_us"] < args.classical_latency_us
            for scenario in args.cost_scenarios
        ):
            parser.error(
                "folded-correction requires explicit cost scenarios with overhead and latency at least nominal"
            )
        if args.shots != 8192 or args.alpha != 0.05 or args.power != 0.8:
            parser.error("folded-correction requires --shots 8192, --alpha 0.05 and --power 0.8")
        if args.max_replicas not in (None, 1):
            parser.error("folded-correction requires exactly one replica")
        if args.optimize and (args.shot_tiers != [8192] or args.replica_tiers != [1]):
            parser.error("folded-correction optimization requires --shot-tiers 8192 --replica-tiers 1")
        if not args.optimize:
            args.shot_tiers = [8192]
            args.replica_tiers = [1]
        correction_backends = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]
        if args.backends is None:
            args.backends = correction_backends
        elif len(args.backends) != 3 or set(args.backends) != set(correction_backends):
            parser.error("folded-correction compares fresh calibration for ibm_fez,ibm_kingston,ibm_marrakesh")
        args.max_replicas = 1
    if args.shot_allocation == "per-pub" and (
        args.family not in ("ripple", "rank-sector", *PATCH_FAMILIES) or not args.optimize
    ):
        parser.error("per-PUB shot allocation requires an optimized algebra or patch family")
    if args.family in ("ripple", "rank-sector"):
        if args.max_replicas not in (None, 1) or (args.optimize and args.replica_tiers != [1]):
            parser.error("static algebra families require --max-replicas 1 and --replica-tiers 1")
    if args.family:
        args.isolated_reference = False
    for name in ("alpha", "power", "simulation_alpha"):
        if not math.isfinite(getattr(args, name)) or not 0 < getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must lie strictly between zero and one")
    if args.precision is None:
        args.precision = COHERENCE_PRECISION if args.family == "coherence-window" else 0.08
    for name in ("precision", "max_total_execution_seconds"):
        value = getattr(args, name)
        if value is not None and (not math.isfinite(value) or value <= 0):
            parser.error(f"--{name.replace('_', '-')} must be finite and positive")
    for name in ("job_overhead_seconds", "classical_latency_us", "reserve_seconds", "min_remaining_seconds"):
        value = getattr(args, name)
        if not math.isfinite(value) or value < 0:
            parser.error(f"--{name.replace('_', '-')} must be finite and nonnegative")
    try:
        local_compute.validate(local_compute.settings(args))
    except ValueError as error:
        if args.out:
            failed_dir = args.out / datetime.now(UTC).strftime("%Y-%m-%dT%H%M%S.%fZ")
            failed_dir.mkdir(parents=True, exist_ok=False)
            write_json(
                failed_dir,
                {
                    "state": "local_compute_unavailable",
                    "policy": local_compute.requested_settings(args),
                    "policy_scope": "requested settings; native compute admission fails",
                    "reason": str(error),
                },
            )
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    service = QiskitRuntimeService()
    try:
        if args.collect:
            collect(service, args.collect)
            return 0
        if args.preserve_raw:
            preserved = preserve_raw(service, args.preserve_raw)
            print(f"raw results preserved for {len(preserved)} jobs under {args.preserve_raw / RAW_DIRECTORY}")
            return 0
        now = datetime.now(UTC)
        args.started = now.isoformat(timespec="microseconds")
        # Microsecond names and exclusive creation keep concurrent runs from
        # sharing a directory.
        run_dir = args.out / now.strftime("%Y-%m-%dT%H%M%S.%fZ") if args.out else None
        args.approved_scope = approved_backend_scope(args.approved_record) if args.submit else None
        choices, record = plan(service, args)
        evaluate(choices, record)
        if run_dir:
            run_dir.mkdir(parents=True, exist_ok=False)
            write_archive(run_dir, choices)
            write_json(run_dir, record)
            if args.native_dry_run:
                from native_preflight import qualify

                native_report = qualify(sys.modules[__name__], service, choices, record, run_dir)
                print(f"native mock qualification: {native_report['status']}")
            if args.family and not args.submit:
                from qpu_cases import write_case

                try:
                    case_path = write_case(run_dir, record)
                except (ValueError, OSError) as exc:
                    raise LiveRunError(f"written case validation failed: {exc}") from exc
                if case_path is not None:
                    print(f"unapproved written case: {case_path}")
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


RAW_DIRECTORY = "raw"


def _jsonable(value: Any) -> Any:
    """A JSON-serializable copy: dataclasses to dicts, datetimes to ISO text, other objects to str."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {member.name: _jsonable(getattr(value, member.name)) for member in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _scrub_instances(value: Any) -> Any:
    """Replace every string carrying an IBM Cloud CRN by the 12-hex sha256 form a record keeps."""
    if isinstance(value, dict):
        return {k: _scrub_instances(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub_instances(v) for v in value]
    if isinstance(value, str) and "crn:" in value:
        return "crn-sha256-12:" + hashlib.sha256(value.encode()).hexdigest()[:12]
    return value


def write_raw_result(run_dir: Path, job_id: str, job: Any, result: Any, pub_names: list[str]) -> dict[str, Any]:
    """Persist a job's result losslessly under raw/<job_id>/ before any analysis reads it.

    Each PUB's classical registers land as shot-ordered bit strings with the
    PUB's metadata (the backend scheduler table among it), the result
    metadata (execution chunks) lands beside them, and index.json carries
    each of those files' sha256. They are written once: a later collection
    that finds a file whose bytes differ from the indexed digest stops,
    since the measurement evidence of a job never changes. job_metrics.json
    carries the provider's latest job metrics (timestamps, usage, circuit
    execution time), which finalize after the job, so it is rewritten on
    every collection and stays outside the index. The files are the
    evidence a later analysis under a different digest reads; collect.json
    holds the preregistered analysis of the same shots.
    """
    directory = run_dir / RAW_DIRECTORY / job_id
    directory.mkdir(parents=True, exist_ok=True)
    files: dict[str, Any] = {}
    for index, pub_result in enumerate(result):
        registers: dict[str, Any] = {}
        for name in pub_result.data:
            array = pub_result.data[name]
            if not hasattr(array, "get_bitstrings"):
                raise LiveRunError(f"job {job_id} PUB {index} register {name} is not a bit array")
            registers[name] = {
                "num_bits": int(array.num_bits),
                "num_shots": int(array.num_shots),
                "bitstrings": list(array.get_bitstrings()),
            }
        files[f"pub_{index:02d}.json"] = {
            "pub_index": index,
            "pub_name": pub_names[index] if index < len(pub_names) else None,
            "registers": registers,
            "metadata": _scrub_instances(_jsonable(pub_result.metadata)),
        }
    files["result_metadata.json"] = _scrub_instances(_jsonable(getattr(result, "metadata", {})))
    digests: dict[str, str] = {}
    for name, payload in files.items():
        text = json.dumps(payload, indent=1, sort_keys=True) + "\n"
        digest = hashlib.sha256(text.encode()).hexdigest()
        target = directory / name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise LiveRunError(f"{target} differs from the result the service returned; raw evidence is write-once")
        else:
            _write_text_atomically(target, text)
        digests[name] = digest
    _write_text_atomically(
        directory / "index.json",
        json.dumps(_merged_index(directory, job_id, digests), indent=1, sort_keys=True) + "\n",
    )
    snapshot_metrics(run_dir, job_id, job)
    return {"directory": f"{RAW_DIRECTORY}/{job_id}", "files": digests}


def _merged_index(directory: Path, job_id: str, digests: dict[str, str]) -> dict[str, Any]:
    """index.json with these result-file digests and any metrics entries an earlier write recorded."""
    index_path = directory / "index.json"
    earlier = json.loads(index_path.read_text()) if index_path.exists() else {}
    return {**{k: v for k, v in earlier.items() if k.startswith("metrics")}, "job_id": job_id, "files": digests}


def snapshot_metrics(run_dir: Path, job_id: str, job: Any) -> str:
    """Append the job's current metrics as a write-once snapshot under raw/<job_id>/ and return its name.

    Job metrics finalize after the job, so each distinct snapshot is kept:
    job_metrics.json first, then job_metrics.<k>.json, every one indexed and
    none rewritten; metrics_latest names the snapshot the newest call saw.
    Collection calls it again after the usage wait, so a run whose usage was
    pending at retrieval carries the finalized metrics in its raw evidence.
    """
    directory = run_dir / RAW_DIRECTORY / job_id
    metrics = job.metrics() if hasattr(job, "metrics") else {}
    metrics_text = json.dumps(_scrub_instances(_jsonable(metrics)), indent=1, sort_keys=True) + "\n"
    snapshots = _metrics_snapshots(directory)
    # Existing snapshots are evidence too: each must still match the digest
    # the index recorded before a new one is appended beside it.
    index_path = directory / "index.json"
    if index_path.exists():
        earlier = json.loads(index_path.read_text())
        for name, digest in zip(earlier.get("metrics", []), earlier.get("metrics_sha256", []), strict=False):
            if not (directory / name).exists() or hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
                raise LiveRunError(f"{directory / name} differs from its indexed sha256; raw evidence is write-once")
    latest = next((name for name in snapshots if (directory / name).read_text() == metrics_text), None)
    if latest is None:
        latest = "job_metrics.json" if not snapshots else f"job_metrics.{len(snapshots)}.json"
        _write_text_atomically(directory / latest, metrics_text)
        snapshots.append(latest)
    metrics_digests = [hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in snapshots]
    index_payload = json.loads(index_path.read_text()) if index_path.exists() else {"job_id": job_id, "files": {}}
    index_payload.update({"metrics": snapshots, "metrics_sha256": metrics_digests, "metrics_latest": latest})
    _write_text_atomically(index_path, json.dumps(index_payload, indent=1, sort_keys=True) + "\n")
    return latest


def _metrics_snapshots(directory: Path) -> list[str]:
    """The job-metrics snapshot files of a raw directory in writing order."""
    names = [p.name for p in directory.glob("job_metrics*.json")]

    def order(name: str) -> int:
        parts = name.split(".")
        return int(parts[1]) if len(parts) == 3 else 0

    return sorted(names, key=order)


def _write_text_atomically(target: Path, text: str) -> None:
    def write(handle: Any) -> None:
        handle.write(text)

    _replace_atomically(target, write, "w")


def preserve_raw(service: QiskitRuntimeService, run_dir: Path) -> dict[str, Any]:
    """Fetch every recorded job of a submitted record and write its raw result files.

    The record's experiment digest plays no part: raw preservation depends
    only on the job ids and the PUB names the submission wrote, so a record
    collected under an earlier revision still gets its measurement evidence.
    """
    record = json.loads((run_dir / "record.json").read_text())
    jobs = record.get("submission", {}).get("jobs") or []
    if not jobs:
        raise LiveRunError(f"{run_dir} records no submitted jobs to preserve")
    preserved: dict[str, Any] = {}
    (run_dir / RAW_DIRECTORY).mkdir(parents=True, exist_ok=True)
    for job_entry in jobs:
        job = service.job(job_entry["job_id"])
        status = str(job.status())
        if status != "DONE":
            preserved[job_entry["job_id"]] = {"result_unavailable": f"job status {status}"}
            continue
        preserved[job_entry["job_id"]] = write_raw_result(
            run_dir, job_entry["job_id"], job, job.result(), [pub["name"] for pub in job_entry["pubs"]]
        )
    text = json.dumps({"preserved_at": _now(), "jobs": preserved}, indent=1, sort_keys=True) + "\n"
    _write_text_atomically(run_dir / RAW_DIRECTORY / "preserved.json", text)
    return preserved


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
    """Write the exact fused Runtime PUB circuits and return the QPY-file digest."""
    archived = []
    for pub in execution_pubs(choices):
        named = copy.copy(pub.circuit)
        named.name = pub.name
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

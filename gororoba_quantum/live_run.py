"""Live system discovery, target-adaptive compilation, simulation, and submission.

Each plan discovers every system accessible to the active account unless
--backends pins a requested set. The runner refreshes each requested backend,
records status and submission-relevant capabilities, derives each experiment
group's requirements, excludes degraded hardware, and removes excluded qubits
and couplers from the Target used for layout and routing. Every routed
instruction is then validated against the unfiltered fresh Target.

For each group and eligible backend, seeded compiles rank valid layouts by
estimated success probability times an idle-dephasing coherence factor. The
best layouts compile every control onto the same initial layout. Local noise
simulation uses the properties and Target from that same fresh snapshot after
their used calibration values agree.

--submit rediscovers the requested systems and reselects affected groups across
all fresh eligible systems until one pass changes nothing. Submission partitions
groups by backend and static or dynamic behavior, then packs complete groups
into client-side Sampler jobs that respect max_circuits. Every batch receives an
immediate hardware refresh. The complete batch ledger, QPY archive digest, and
recovery tags reach disk before the first job. --collect reconciles response-lost
job ids, fetches the Target and properties in force when each submitted circuit
ran, and re-simulates under that execution-time calibration.
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

from experiments import MIRROR_SUFFIX, Group, Member, experiment_groups, tvd

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
MAX_REVALIDATION = 3
RECORD_SCHEMA_VERSION = 3
CONTROL_FLOW_OPERATIONS = frozenset({"if_else", "while_loop", "for_loop", "switch_case", "break_loop", "continue_loop"})
DIRECT_TARGET_OPERATIONS = CONTROL_FLOW_OPERATIONS | {"delay", "measure", "reset", "store"}

EXPERIMENT_SOURCE_MANIFEST = (
    "boolean_anf.py",
    "cd_core.py",
    "designs.py",
    "experiments.py",
    "factoring.py",
    "live_run.py",
    "modular_arithmetic.py",
    "order_finding.py",
    "predict.py",
    "select_lcu.py",
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
            f"group needs {largest_batch} circuits in one result-complete batch; backend limit is "
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
class Choice:
    """The winning compile of a group, with mirror twins appended as entries."""

    group: Group
    snap: Snapshot
    seed: int
    layout: list[int]
    isas: list[QuantumCircuit]
    member_scores: list[float]
    joint_score: float
    entries: list[tuple[str, QuantumCircuit, np.ndarray]] = field(default_factory=list)


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


def attach_mirrors(choice: Choice) -> Choice:
    """Entries: every member's ISA, each followed directly by its mirror twin if it asks for one.

    A twin placed next to its witness runs next to it in the job, which keeps
    the pair inside one calibration whenever the job allows.
    """
    choice.entries = []
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        choice.entries.append((member.name, isa, member.ideal))
        if member.mirror:
            name = member.name + MIRROR_SUFFIX
            twin = mirror_isa(isa, choice.snap.backend, name)
            zeros = np.zeros(2**member.circuit.num_clbits)
            zeros[0] = 1.0
            choice.entries.append((name, twin, zeros))
    return choice


def _trace_failure_summary(trace_by_backend: dict[str, list[dict[str, Any]]]) -> dict[str, list[str]]:
    """Compact selection failures for a terminal CLI diagnostic."""
    summary: dict[str, list[str]] = {}
    for backend_name, entries in trace_by_backend.items():
        reasons: set[str] = set()
        for entry in entries:
            stage = str(entry.get("stage", "routing"))
            reasons.update(f"{stage}: {reason}" for reason in entry.get("rejected", []))
            for field_name in ("compile_error", "member_compile_error", "mirror_compile_error"):
                if field_name in entry:
                    reasons.add(f"{field_name}: {entry[field_name]}")
            for field_name in ("member_rejections", "mirror_rejections"):
                for member_name, rejected in entry.get(field_name, {}).items():
                    reasons.update(f"{member_name}: {reason}" for reason in rejected)
        summary[backend_name] = sorted(reasons) or ["no candidate reached final validation"]
    return summary


def select(group: Group, snaps: list[Snapshot], seeds: int, log: dict[str, Any]) -> Choice:
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
            attach_mirrors(candidate)
        except (QiskitError, ValueError) as error:
            trace.append(
                {
                    "seed": candidate.seed,
                    "layout": candidate.layout,
                    "mirror_compile_error": type(error).__name__,
                }
            )
            continue
        mirror_rejections = {
            name: rejected
            for name, isa, _ in candidate.entries
            if (rejected := compiled_violations(isa, candidate.snap))
        }
        if mirror_rejections:
            trace.append({"seed": candidate.seed, "layout": candidate.layout, "mirror_rejections": mirror_rejections})
            continue
        return candidate
    failure_summary = _trace_failure_summary(log[group.name])
    raise LiveRunError(
        f"{group.name}: no valid routed candidate; failures={json.dumps(failure_summary, sort_keys=True)}"
    )


def _distribution(counts: dict[str, int], clbits: int) -> np.ndarray:
    dist = np.zeros(2**clbits)
    for key, c in counts.items():
        dist[int(key.replace(" ", ""), 2)] += c
    return np.asarray(dist / dist.sum())


def _pub_counts(pub: Any, isa: QuantumCircuit) -> dict[str, int]:
    """Join every classical register in circuit order into global clbit order."""
    register_names = [register.name for register in isa.cregs]
    if not register_names:
        raise LiveRunError(f"{isa.name}: result decoder needs at least one classical register")
    joined = pub.join_data(register_names)
    if not hasattr(joined, "get_counts"):
        raise LiveRunError(f"{isa.name}: joined result data does not provide bit counts")
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


def simulate(choice: Choice, noise: Any, shots: int = SHOTS) -> dict[str, np.ndarray]:
    out = {}
    for name, isa, _ in choice.entries:
        counts = noise.run(isa, shots=shots, seed_simulator=SEED_SIMULATOR).result().get_counts()
        out[name] = _distribution(counts, isa.num_clbits)
    return out


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
    group: Group, dists: dict[str, tuple[np.ndarray, QuantumCircuit]], props: Any, symmetric: bool = False
) -> Any:
    """The group summary on readout-inverted distributions, or why it is skipped.

    readout_corrected assumes each classical bit passes through its own
    output-only channel. In a feed-forward circuit a misread mid-circuit bit
    also steers the conditional gate, so the second bit's distribution depends
    on the first readout error and the separable inversion is biased; such
    groups report the reason instead of a corrected summary. props is one
    properties object, or a per-circuit mapping when circuits ran under
    different calibrations.
    """
    if any(_is_dynamic(isa) for _, isa in dists.values()):
        return {"skipped": "feed-forward circuits: readout error steers the conditional branch"}
    return group.summarize(
        {
            name: readout_corrected(dist, isa, props[name] if isinstance(props, dict) else props, symmetric)
            for name, (dist, isa) in dists.items()
        }
    )


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


def _choice_record(choice: Choice, noisy: dict[str, np.ndarray], noise_calibration: str) -> dict[str, Any]:
    target = choice.snap.backend.target
    members = []
    for name, isa, ideal in choice.entries:
        dynamic = _is_dynamic(isa)
        members.append(
            {
                "name": name,
                "cz": isa.count_ops().get("cz", 0),
                "depth": isa.depth(),
                "duration_s": duration_s(isa, target),
                "duration_bound": "lower_without_classical_latency" if dynamic else "scheduled",
                "dynamic": dynamic,
                "feed_forward": any(isinstance(i.operation, ControlFlowOp) for i in isa.data),
                "physical_qubits": _physical(isa),
                "esp": esp(isa, target),
                "coherence": coherence(isa, target),
                "ideal": [round(float(p), 12) for p in ideal],
                "noisy": [round(float(p), 6) for p in noisy[name]],
                "tvd_noisy_to_ideal": tvd(noisy[name], ideal),
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
        "summary": choice.group.summarize(noisy),
        "summary_readout_corrected": corrected_summary(
            choice.group,
            {name: (noisy[name], isa) for name, isa, _ in choice.entries},
            choice.snap.properties,
        ),
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
    choices = [select(group, snaps, args.seeds, trace) for group in groups]
    record = {
        "schema_version": RECORD_SCHEMA_VERSION,
        "state": "planned",
        "started": args.started,
        "versions": {pkg: version(pkg) for pkg in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
        "policy": QUALITY
        | {"max_pending": args.max_pending, "seeds": args.seeds, "joint_candidates": JOINT_CANDIDATES},
        "shots": args.shots,
        "seed_simulator": SEED_SIMULATOR,
        "experiment_digest": experiment_digest(),
        "code_commit": _code_commit(),
        "system_inventory": inventory,
        "backends": {s.name: s.summary() for s in snaps},
        "skipped_backends": skipped,
        "circuit_requirements": {group.name: group_requirements(group).summary() for group in groups},
        "selection_trace": trace,
    }
    return choices, record


def evaluate(choices: list[Choice], record: dict[str, Any]) -> None:
    """Noise-simulate each choice under its backend's live properties, after proving they match the Target."""
    # One simulator per snapshot: a group recompiled on a fresh snapshot of a
    # backend is simulated with that snapshot's Target, not an earlier one.
    sims: dict[int, tuple[AerSimulator, str]] = {}
    record["groups"] = []
    for choice in choices:
        isas = [isa for _, isa, _ in choice.entries]
        check_target_matches_properties(isas, choice.snap.backend.target, choice.snap.properties, choice.snap.name)
        key = id(choice.snap)
        if key not in sims:
            sims[key] = (
                noise_simulator(choice.snap.name, choice.snap.backend.target, choice.snap.properties),
                choice.snap.calibration,
            )
        sim, cal = sims[key]
        noisy = simulate(choice, sim, int(record["shots"]))
        entry = _choice_record(choice, noisy, cal)
        record["groups"].append(entry)
        cz = [m["cz"] for m in entry["members"]]
        summary = {k: round(v, 4) for k, v in entry["summary"].items()}
        print(
            f"{choice.group.name}: {choice.snap.name} seed={choice.seed} layout={choice.layout} "
            f"joint_score={choice.joint_score:.4f} cz={cz} summary={summary}"
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


def choice_change_reasons(choice: Choice, fresh: Snapshot) -> list[str]:
    """Reasons an existing compile needs rebuilding against a fresh snapshot."""
    reasons = capability_violations(group_requirements(choice.group), fresh.capabilities)
    if choice.snap.capabilities != fresh.capabilities:
        reasons.append("backend capabilities changed")
    isas = [isa for _, isa, _ in choice.entries]
    for name, isa, _ in choice.entries:
        reasons.extend(f"{name}: {reason}" for reason in compiled_violations(isa, fresh))
    try:
        if fingerprint(isas, fresh.backend.target, fresh.properties) != fingerprint(
            isas, choice.snap.backend.target, choice.snap.properties
        ):
            reasons.append("calibration values changed on compiled instructions")
    except Exception as error:
        reasons.append(f"calibration fingerprint failed ({type(error).__name__})")
    return sorted(set(reasons))


def submission_batches(
    choices: list[Choice], kind: str, max_circuits: int | None
) -> list[list[tuple[str, QuantumCircuit, Choice]]]:
    """Pack whole result-complete groups into deterministic first-fit-decreasing jobs."""
    groups: list[tuple[int, list[tuple[str, QuantumCircuit, Choice]]]] = []
    for group_index, choice in enumerate(choices):
        classified = [
            (name, isa, choice, "dynamic" if _is_dynamic(isa) else "static") for name, isa, _ in choice.entries
        ]
        choice_kinds = {entry_kind for _, _, _, entry_kind in classified}
        if len(choice_kinds) != 1:
            raise LiveRunError(f"{choice.group.name}: one result group mixes static and dynamic circuits")
        if kind not in choice_kinds:
            continue
        entries = [(name, isa, owner) for name, isa, owner, _ in classified]
        if max_circuits is not None and len(entries) > max_circuits:
            raise LiveRunError(
                f"{choice.group.name}: {len(entries)} circuits exceed backend per-job limit {max_circuits}"
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
    for planned_job in planned_jobs:
        key = _submission_key(planned_job)
        if key in planned_by_key:
            raise LiveRunError(f"duplicate planned job identity {key}")
        if planned_job.get("qpy_archive_sha256") != archive_digest:
            raise LiveRunError(f"planned job {key} differs from the submission QPY archive digest")
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
    """Re-gate and re-read each chosen backend until nothing moved, then archive and submit.

    Recompiling and re-simulating takes long enough for the calibration, the
    status, or the queue to move again, so the gate repeats on fresh snapshots
    until a pass changes nothing, at most MAX_REVALIDATION passes. The final
    circuits reach isa.qpy before the first job is sent. The exact archive
    digest and recovery tags are checkpointed before each attempt, and each
    returned job id is checkpointed before the next batch.
    """
    for attempt in range(MAX_REVALIDATION):
        fresh_snapshots, skipped, inventory = discover_snapshots(service, args.backends, args.max_pending)
        if not fresh_snapshots:
            raise LiveRunError("no eligible backend remains before submission")
        fresh_by_backend = {snapshot.name: snapshot for snapshot in fresh_snapshots}
        moved = False
        attempt_trace: dict[str, Any] = {}
        reselected: dict[str, Any] = {}
        for idx, choice in enumerate(choices):
            name = choice.snap.name
            reasons = (
                choice_change_reasons(choice, fresh_by_backend[name])
                if name in fresh_by_backend
                else ["chosen backend is unavailable or ineligible"]
            )
            if not reasons:
                choice.snap = fresh_by_backend[name]
                continue
            print(f"{choice.group.name}: live configuration moved on {name}; reselecting across viable systems")
            choices[idx] = select(choice.group, fresh_snapshots, args.seeds, attempt_trace)
            reselected[choice.group.name] = {"previous_backend": name, "reasons": reasons}
            moved = True
        record.setdefault("revalidation", []).append(
            {
                "attempt": attempt + 1,
                "system_inventory": inventory,
                "skipped_backends": skipped,
                "reselected_groups": reselected,
                "selection_trace": attempt_trace,
            }
        )
        if not moved:
            break
        # The record's predictions must describe the circuits that run, and the
        # archive moves with them, so an abort on a later pass still leaves
        # record.json and isa.qpy describing the same circuits.
        evaluate(choices, record)
        record["reevaluated_before_submit"] = attempt + 1
        archive()
    else:
        raise LiveRunError(f"calibration kept moving through {MAX_REVALIDATION} revalidation passes; rerun later")
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


def _odr_withheld_reason(names: list[str], executed: dict[str, dict[str, Any]], shots: int) -> str | None:
    """Why a group's mirror-rescaled values are not valid, or None when they are.

    Rescaling divides a witness's <Z> by its twin's attenuation, which is a
    correction only when both ran under one calibration and enough shots make
    the quotient significant.
    """
    if not any(name.endswith(MIRROR_SUFFIX) for name in names):
        return None
    if shots < ODR_MIN_SHOTS:
        return f"{shots} shots per circuit; ODR needs at least {ODR_MIN_SHOTS}"
    ran = [executed[n] for n in names if n in executed]
    if any(e["calibration_changed_during_shots"] for e in ran) or len({e["calibration"] for e in ran}) > 1:
        return "witnesses and mirror twins did not all run under one calibration"
    return None


def _without_odr(summary: dict[str, Any], withheld: str | None) -> dict[str, Any]:
    """summary minus its mirror-rescaled and twin fields when withheld names a reason."""
    if withheld is None:
        return summary
    return {k: v for k, v in summary.items() if "odr" not in k and not k.startswith("mirror_z")}


def collect(service: QiskitRuntimeService, run_dir: Path) -> None:
    """Measured distributions against the noise model of the calibration in force at execution."""
    record = json.loads((run_dir / "record.json").read_text())
    qpy_bytes = (run_dir / "isa.qpy").read_bytes()
    groups = {g.name: g for g in experiment_groups()}
    if record.get("experiment_digest") != experiment_digest():
        commit = record.get("code_commit", {}).get("head")
        raise LiveRunError(
            f"experiment definitions differ from the run's (digest {record.get('experiment_digest')}); "
            f"collect from commit {commit}, where groups, ideals, and summaries match the archived circuits"
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
        measured: dict[str, np.ndarray] = {}
        props_by_name: dict[str, Any] = {}
        replayed: dict[str, np.ndarray] = {}
        executed: dict[str, dict[str, Any]] = {}
        for idx, (name, pub) in enumerate(zip(members, result, strict=True)):
            isa = isas[name]
            start, stop = windows[idx]
            props_then, sim_then = at[start]
            measured[name] = _distribution(_pub_counts(pub, isa), isa.num_clbits)
            props_by_name[name] = props_then
            counts = sim_then.run(isa, shots=shots, seed_simulator=seed).result().get_counts()
            replayed[name] = _distribution(counts, isa.num_clbits)
            stop_calibration = backend.properties(datetime=stop).last_update_date
            executed[name] = {
                "start": start.isoformat(),
                "stop": stop.isoformat(),
                "calibration": props_then.last_update_date.isoformat(),
                "calibration_changed_during_shots": stop_calibration != props_then.last_update_date,
            }
        for gname, group in groups.items():
            present = [n for n in measured if n in {m.name for m in group.members}]
            if not present:
                continue
            # A summary needs every member and every mirror twin; a job that
            # lacks some still reports the distributions it has.
            required = [m.name for m in group.members] + [m.name + MIRROR_SUFFIX for m in group.members if m.mirror]
            missing = [n for n in required if n not in measured]
            entry: dict[str, Any] = {
                "group": gname,
                "backend": job_entry["backend"],
                "executed": {n: executed[n] for n in required if n in executed},
                "job_usage": metrics.get("usage"),
                "measured": {n: [round(float(p), 6) for p in measured[n]] for n in required if n in measured},
            }
            # A circuit whose shots straddle a calibration update has no single
            # calibration to correct or replay against; its group keeps the raw
            # measurement and states why the rest is absent.
            straddling = [n for n in required if n in executed and executed[n]["calibration_changed_during_shots"]]
            if missing:
                entry["summary_unavailable"] = f"missing {missing}"
            else:
                # A failed ODR gate removes the mirror-rescaled values from
                # every summary the entry publishes, measured, readout-corrected,
                # and replayed alike.
                withheld = _odr_withheld_reason(required, executed, shots)
                if withheld:
                    entry["odr_withheld"] = withheld
                entry["measured_summary"] = _without_odr(group.summarize(measured), withheld)
                if straddling:
                    entry["calibration_dependent_summaries_unavailable"] = (
                        f"calibration changed during the shots of {straddling}"
                    )
                else:
                    entry["measured_summary_readout_corrected"] = _without_odr(
                        corrected_summary(
                            group,
                            {n: (measured[n], isas[n]) for n in required},
                            props_by_name,
                            symmetric=twirled_readout,
                        ),
                        withheld,
                    )
                    entry["replayed_summary"] = _without_odr(group.summarize(replayed), withheld)
                    entry["tvd_measured_to_replayed"] = {n: tvd(measured[n], replayed[n]) for n in required}
            out.append(entry)
    text = json.dumps(out, indent=2) + "\n"
    _replace_atomically(run_dir / "collect.json", lambda handle: handle.write(text), "w")
    print(json.dumps(out, indent=2))


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"needs a positive shot count, got {value}")
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
    """Write the run's named ISA circuits and return the exact QPY-file digest."""
    archived = []
    for choice in choices:
        for name, isa, _ in choice.entries:
            named = copy.copy(isa)
            named.name = name
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

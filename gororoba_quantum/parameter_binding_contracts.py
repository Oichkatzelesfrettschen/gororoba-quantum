"""Verify ISA parameter binding, including its compiled global phase, locally."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from time import perf_counter
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import Parameter, ParameterExpression
from qiskit.circuit.exceptions import CircuitError
from qiskit.quantum_info import Operator

from experiments import Member
from live_run import _bind


def _archive(circuit: QuantumCircuit) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuit, stream)
    return stream.getvalue()


def _value_signature(value: Any) -> dict[str, Any]:
    if isinstance(value, ParameterExpression):
        return {
            "type": "ParameterExpression",
            "expression": str(value),
            "parameters": sorted((parameter.name, str(parameter.uuid)) for parameter in value.parameters),
        }
    return {"type": type(value).__qualname__, "value": repr(value)}


def _source_signature(circuit: QuantumCircuit) -> dict[str, Any]:
    """Record circuit semantics independently of QPY layout-register serialization."""
    layout = circuit.layout
    return {
        "name": circuit.name,
        "qubits": circuit.num_qubits,
        "clbits": circuit.num_clbits,
        "parameters": sorted((parameter.name, str(parameter.uuid)) for parameter in circuit.parameters),
        "phase": _value_signature(circuit.global_phase),
        "instructions": [
            (
                instruction.operation.name,
                tuple(_value_signature(value) for value in instruction.operation.params),
                tuple(circuit.find_bit(qubit).index for qubit in instruction.qubits),
                tuple(circuit.find_bit(clbit).index for clbit in instruction.clbits),
            )
            for instruction in circuit.data
        ],
        "initial_layout": None if layout is None else tuple(layout.initial_index_layout()),
        "final_layout": None if layout is None else tuple(layout.final_index_layout()),
        "metadata": json.dumps(circuit.metadata, sort_keys=True),
    }


def _active_operator(circuit: QuantumCircuit, binding: dict[Parameter, float]) -> np.ndarray:
    """Evaluate the four active physical wires independently of circuit binding."""
    operations = [
        instruction for instruction in circuit.data if instruction.operation.name not in ("barrier", "measure")
    ]
    active = sorted({circuit.find_bit(qubit).index for instruction in operations for qubit in instruction.qubits})
    physical_to_compact = {physical: index for index, physical in enumerate(active)}
    phase = circuit.global_phase
    bound_phase = (
        float(phase.bind(binding, allow_unknown_parameters=True)) if isinstance(phase, ParameterExpression) else phase
    )
    compact = QuantumCircuit(len(active), global_phase=bound_phase)
    for instruction in operations:
        operation = instruction.operation.to_mutable()
        operation.params = [
            float(value.bind(binding, allow_unknown_parameters=True))
            if isinstance(value, ParameterExpression)
            else value
            for value in operation.params
        ]
        compact.append(operation, [physical_to_compact[circuit.find_bit(qubit).index] for qubit in instruction.qubits])
    return np.asarray(Operator(compact).data)


def _member(circuit: QuantumCircuit, binding: dict[Parameter, float] | None) -> Member:
    return Member("parameter_binding", circuit, np.array([1.0, 0.0]), binding)


def _agreement(circuit: QuantumCircuit, binding: dict[Parameter, float]) -> None:
    original_signature = _source_signature(circuit)
    expected = circuit.assign_parameters(binding)
    actual = _bind(circuit, _member(circuit, binding))
    if _source_signature(circuit) != original_signature:
        raise ValueError("parameter binding mutated the source ISA")
    if actual != expected or actual.parameters != expected.parameters:
        raise ValueError("parameter binding differs from the Qiskit circuit or remaining parameters")
    remaining = {parameter: 0.137 for parameter in expected.parameters}
    expected_operator = Operator(expected.assign_parameters(remaining)).data
    actual_operator = Operator(actual.assign_parameters(remaining)).data
    if not np.allclose(actual_operator, expected_operator, atol=1e-12, rtol=0):
        raise ValueError("parameter binding changed the full operator including global phase")
    if actual.metadata != expected.metadata or actual.layout != expected.layout:
        raise ValueError("parameter binding changed circuit metadata or transpilation layout")


def verify() -> dict[str, Any]:
    """Compare full operators for complete, partial, phase-only, and rejected bindings."""
    gate_angle = Parameter("gate_angle")
    shared_angle = Parameter("shared_angle")
    phase_angle = Parameter("phase_angle")
    source = QuantumCircuit(2, name="phase_sensitive_binding")
    source.rx(gate_angle + shared_angle, 0)
    source.cp(shared_angle, 0, 1)
    source.global_phase = 11 * math.pi + phase_angle / 3 + shared_angle / 7
    source.metadata = {"evidence": "exact_phase_binding"}
    bindings = (
        {gate_angle: 0.4, shared_angle: 0.7, phase_angle: 0.2},
        {shared_angle: 0.7},
        {phase_angle: 0.2},
        {gate_angle: 0.4},
        {phase_angle: 0.2, shared_angle: 0.7},
    )
    for binding in bindings:
        _agreement(source, binding)
    phase_only = QuantumCircuit(1, name="phase_only_binding")
    phase_only.global_phase = phase_angle + shared_angle / 2
    _agreement(phase_only, {phase_angle: 0.2})
    _agreement(phase_only, {phase_angle: 0.2, shared_angle: 0.7})
    numeric_phase = QuantumCircuit(1, name="numeric_phase_binding", global_phase=0.3)
    numeric_phase.ry(gate_angle, 0)
    _agreement(numeric_phase, {gate_angle: 0.4})
    empty_bindings: tuple[dict[Parameter, float] | None, ...] = (None, {})
    for empty_binding in empty_bindings:
        if _bind(source, _member(source, empty_binding)) is not source:
            raise ValueError("empty parameter binding changed the existing ISA identity")
    unknown = Parameter("absent_angle")
    rejected = 0
    for binding in ({unknown: 0.1}, {shared_angle: 0.2, unknown: 0.1}):
        original_signature = _source_signature(source)
        try:
            _bind(source, _member(source, binding))
        except CircuitError:
            rejected += 1
        else:
            raise ValueError("parameter binding accepted a parameter absent from the ISA")
        if _source_signature(source) != original_signature:
            raise ValueError("rejected parameter binding mutated the source ISA")
    return {"operator_agreements": 8, "empty_bindings": 2, "unknown_parameters_rejected": rejected}


def _archive_boundary(circuit: QuantumCircuit) -> dict[str, Any]:
    """Verify the physical execution-PUB archive independently of compiler layout metadata."""
    import tempfile
    from pathlib import Path

    from qiskit_ibm_runtime.fake_provider import FakeFez

    from experiments import Group
    from live_run import Choice, Entry, execution_pubs, write_archive
    from packing import Replica, pack
    from runtime_contracts import _fake_snapshot

    active = sorted({circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits})
    replica = Replica(0, {qubit: qubit for qubit in active}, 1.0)
    packed = pack(circuit, [replica], "binding_packed")
    ideal = np.zeros(1 << circuit.num_clbits)
    ideal[0] = 1
    member = Member("binding_member", circuit, ideal)
    group = Group("binding_archive", (member,), lambda _: {}, execution_rows=(0,))
    snapshot = _fake_snapshot(FakeFez())
    entry = Entry(member.name, circuit, ideal, packed, [packed], ["r0_"], [active])
    choice = Choice(group, snapshot, 20261010, [], [circuit], [1.0], 1.0, [entry], [replica])
    pubs = execution_pubs([choice])
    if len(pubs) != 1 or pubs[0].circuit.layout is not None or pubs[0].circuit.parameters:
        raise ValueError("execution archive must contain one fully bound physical PUB")
    expected_operator = _active_operator(circuit, {})
    if not np.allclose(_active_operator(packed, {}), expected_operator, atol=1e-10, rtol=0):
        raise ValueError("replica packing changed the full ISA operator including global phase")
    if not np.allclose(_active_operator(pubs[0].circuit, {}), expected_operator, atol=1e-10, rtol=0):
        raise ValueError("PUB fusion changed the full ISA operator including global phase")
    with tempfile.TemporaryDirectory(prefix="binding-archive-contract-") as directory:
        hashes = {write_archive(Path(directory), [choice]) for _ in range(20)}
    if len(hashes) != 1:
        raise ValueError("execution archive differs across repeated write_archive calls")
    return {
        "execution_pubs": len(pubs),
        "pub_layout_absent": True,
        "pub_parameters": 0,
        "write_archive_unique_hashes_20_calls": len(hashes),
        "full_operator_including_phase_preserved": True,
    }


def benchmark() -> dict[str, Any]:
    """Time both binding paths on one locally compiled walk, outside correctness gates."""
    from qiskit_ibm_runtime.fake_provider import FakeFez

    from ripple_experiments import PAIRS, _walk_template

    source, bindings, _ = _walk_template()
    started = perf_counter()
    compiled = transpile(source, backend=FakeFez(), optimization_level=3, seed_transpiler=20261010)
    compile_seconds = perf_counter() - started
    binding = bindings[PAIRS[0], 4]
    original_signature = _source_signature(compiled)
    original_operator = _active_operator(compiled, binding)
    qpy_hashes_before = {hashlib.sha256(_archive(compiled)).hexdigest() for _ in range(20)}
    started = perf_counter()
    actual = _bind(compiled, _member(compiled, binding))
    simultaneous_seconds = perf_counter() - started
    if _source_signature(compiled) != original_signature:
        raise ValueError("simultaneous phase binding mutated the source ISA structure, parameters, or layout")
    if not np.allclose(_active_operator(compiled, binding), original_operator, atol=1e-12, rtol=0):
        raise ValueError("simultaneous phase binding mutated the source ISA operator")
    # Compiler-layout extra-register ordering can vary between QPY writes.
    # Record serializer behavior separately from the source-preservation gate.
    qpy_hashes_after = {hashlib.sha256(_archive(compiled)).hexdigest() for _ in range(20)}
    started = perf_counter()
    expected = compiled.assign_parameters(binding)
    ordinary_seconds = perf_counter() - started
    reference_source_unchanged = _source_signature(compiled) == original_signature
    reference_operator_unchanged = np.allclose(
        _active_operator(compiled, binding), original_operator, atol=1e-12, rtol=0
    )
    qpy_hashes_reference = {hashlib.sha256(_archive(compiled)).hexdigest() for _ in range(20)}
    if actual != expected or not math.isclose(float(actual.global_phase), float(expected.global_phase), abs_tol=1e-10):
        raise ValueError("compiled walk binding differs from Qiskit's reference result or numeric phase")
    if actual.layout != expected.layout:
        raise ValueError("compiled walk binding changed the transpilation layout")
    bound_qpy_hashes = {hashlib.sha256(_archive(actual)).hexdigest() for _ in range(20)}
    archive_boundary = _archive_boundary(actual)
    return {
        "backend": "FakeFez",
        "compile_seconds": compile_seconds,
        "operations": len(compiled),
        "parameters": len(compiled.parameters),
        "ordinary_binding_seconds": ordinary_seconds,
        "simultaneous_phase_binding_seconds": simultaneous_seconds,
        "speedup": ordinary_seconds / simultaneous_seconds,
        "numeric_global_phase": float(actual.global_phase),
        "compiler_bound_qpy_unique_hashes": len(bound_qpy_hashes),
        "execution_archive": archive_boundary,
        "circuit_agreement": True,
        "layout_agreement": True,
        "source_structure_unchanged_by_simultaneous_binding": True,
        "source_operator_unchanged_by_simultaneous_binding": True,
        "source_structure_unchanged_by_reference_binding": reference_source_unchanged,
        "source_operator_unchanged_by_reference_binding": bool(reference_operator_unchanged),
        "unbound_qpy_unique_hashes_before": len(qpy_hashes_before),
        "unbound_qpy_unique_hashes_after_simultaneous_binding": len(qpy_hashes_after),
        "unbound_qpy_unique_hashes_after_reference_binding": len(qpy_hashes_reference),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true", help="time a local FakeFez walk binding")
    args = parser.parse_args()
    result = verify()
    if args.benchmark:
        result["benchmark"] = benchmark()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

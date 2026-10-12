"""Verify ISA parameter binding, including its compiled global phase, locally."""

from __future__ import annotations

import argparse
import io
import json
import math
from time import perf_counter
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.exceptions import CircuitError
from qiskit.quantum_info import Operator

from experiments import Member
from live_run import _bind


def _archive(circuit: QuantumCircuit) -> bytes:
    stream = io.BytesIO()
    qpy.dump(circuit, stream)
    return stream.getvalue()


def _member(circuit: QuantumCircuit, binding: dict[Parameter, float] | None) -> Member:
    return Member("parameter_binding", circuit, np.array([1.0, 0.0]), binding)


def _agreement(circuit: QuantumCircuit, binding: dict[Parameter, float]) -> None:
    original_bytes = _archive(circuit)
    expected = circuit.assign_parameters(binding)
    actual = _bind(circuit, _member(circuit, binding))
    if _archive(circuit) != original_bytes:
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
        original_bytes = _archive(source)
        try:
            _bind(source, _member(source, binding))
        except CircuitError:
            rejected += 1
        else:
            raise ValueError("parameter binding accepted a parameter absent from the ISA")
        if _archive(source) != original_bytes:
            raise ValueError("rejected parameter binding mutated the source ISA")
    return {"operator_agreements": 8, "empty_bindings": 2, "unknown_parameters_rejected": rejected}


def benchmark() -> dict[str, Any]:
    """Time both binding paths on one locally compiled walk, outside correctness gates."""
    from qiskit_ibm_runtime.fake_provider import FakeFez

    from ripple_experiments import PAIRS, _walk_template

    source, bindings, _ = _walk_template()
    started = perf_counter()
    compiled = transpile(source, backend=FakeFez(), optimization_level=3, seed_transpiler=20261010)
    compile_seconds = perf_counter() - started
    binding = bindings[PAIRS[0], 4]
    original_bytes = _archive(compiled)
    started = perf_counter()
    expected = compiled.assign_parameters(binding)
    ordinary_seconds = perf_counter() - started
    started = perf_counter()
    actual = _bind(compiled, _member(compiled, binding))
    simultaneous_seconds = perf_counter() - started
    if actual != expected or not math.isclose(float(actual.global_phase), float(expected.global_phase), abs_tol=1e-10):
        raise ValueError("compiled walk binding differs from Qiskit's reference result or numeric phase")
    if actual.layout != expected.layout or _archive(compiled) != original_bytes:
        raise ValueError("compiled walk binding changed the layout or source ISA")
    return {
        "backend": "FakeFez",
        "compile_seconds": compile_seconds,
        "operations": len(compiled),
        "parameters": len(compiled.parameters),
        "ordinary_binding_seconds": ordinary_seconds,
        "simultaneous_phase_binding_seconds": simultaneous_seconds,
        "speedup": ordinary_seconds / simultaneous_seconds,
        "numeric_global_phase": float(actual.global_phase),
        "circuit_agreement": True,
        "layout_agreement": True,
        "source_qpy_unchanged": True,
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

"""Check common-template correction witnesses and rejected history mutations."""

from __future__ import annotations

import io
import json
import math
from collections.abc import Callable
from functools import partial
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy, transpile
from qiskit.circuit import CircuitInstruction, IfElseOp
from qiskit.circuit.library import XGate
from qiskit_ibm_runtime.fake_provider import FakeKingston

from correction_circuits import (
    CORRECTION_ARMS,
    FALSE_CORRECTION_ANGLE,
    PHASE_LABEL,
    TRUE_CORRECTION_ANGLE,
    bind_correction_template,
    correction_binding,
    correction_member_metadata,
    correction_template,
    validate_bound_correction_pair,
    validate_correction_pair,
)
from experiments import Member
from live_run import _bind, _compile, target_violations
from qpe_diagnostics import ideal_branch_probabilities
from runtime_contracts import _fake_snapshot


def _reject(action: Callable[[], Any]) -> None:
    try:
        action()
    except ValueError:
        return
    raise RuntimeError("correction contract accepted a forbidden mutation")


def _replace(circuit: QuantumCircuit, position: int, replacement: CircuitInstruction | None) -> QuantumCircuit:
    """Rebuild control-flow instructions through the circuit construction API."""
    rebuilt = circuit.copy_empty_like()
    for index, instruction in enumerate(circuit.data):
        if index != position:
            rebuilt.append(instruction)
        elif replacement is not None:
            rebuilt.append(replacement)
    return rebuilt


def _change_dispatch(circuit: QuantumCircuit, position: int, *, mutation: str) -> QuantumCircuit:
    instruction = circuit.data[position]
    operation = instruction.operation
    true_block, false_block = [block.copy() for block in operation.blocks]
    condition = operation.condition
    if mutation == "condition":
        condition = (condition[0], 0)
    elif mutation == "false_phase":
        false_block.global_phase = math.pi / 7
    elif mutation == "remove_zero_rotation":
        false_block = false_block.copy_empty_like()
    elif mutation == "extra_true_gate":
        true_block.x(0)
    elif mutation != "remove_false_branch":
        raise RuntimeError(f"unknown test mutation {mutation}")
    replacement = IfElseOp(condition, true_block, None if mutation == "remove_false_branch" else false_block)
    return _replace(circuit, position, instruction.replace(operation=replacement))


def verify() -> dict[str, Any]:
    """Validate local native histories without connecting to a quantum service."""
    source = correction_template()
    backend = FakeKingston()
    routed = transpile(
        source,
        backend=backend,
        optimization_level=3,
        seed_transpiler=20261010,
        initial_layout=[95, 79, 93, 92, 94],
    )
    source_copy = source.copy()
    routed_copy = routed.copy()
    unconstrained = _compile(source, _fake_snapshot(backend), 20261010)
    unconstrained_copy = unconstrained.copy()
    reports = []
    for template in (source, routed, unconstrained):
        for phase_label in (1, 3):
            feedback = bind_correction_template(template, phase_label, CORRECTION_ARMS[0])
            independent = bind_correction_template(template, phase_label, CORRECTION_ARMS[1])
            reports.append(validate_correction_pair(template, feedback, independent, phase_label))
            bound_report = validate_bound_correction_pair(feedback, independent, phase_label)
            if bound_report["validation"] != "exact_bound_pair_history_and_ideal_law":
                raise RuntimeError("bound artifact validator claimed a symbolic-template proof")
            for arm, circuit in zip(CORRECTION_ARMS, (feedback, independent), strict=True):
                binding = correction_binding(phase_label, arm)
                expected_law = np.zeros(4)
                expected_law[phase_label] = 1.0
                existing_bound = _bind(template, Member(arm, source, expected_law, binding=binding))
                existing_bound.name = circuit.name
                if circuit != existing_bound:
                    raise RuntimeError("correction binder differs from the existing production binder")
                if template is not source and target_violations(circuit, backend.target):
                    raise RuntimeError("correction binding violates the bundled offline target")
                metadata = correction_member_metadata(phase_label, arm)
                if metadata["backend_schedule_certified"] or metadata["dispatch_removal_test"]:
                    raise RuntimeError("correction metadata overstates the local validation")
                json.dumps(metadata)
            stream = io.BytesIO()
            qpy.dump([feedback, independent], stream)
            stream.seek(0)
            restored_feedback, restored_independent = qpy.load(stream)
            validate_correction_pair(template, restored_feedback, restored_independent, phase_label)
            if validate_bound_correction_pair(restored_feedback, restored_independent, phase_label) != bound_report:
                raise RuntimeError("bound correction archive changed its validated history")
    if source != source_copy or routed != routed_copy or unconstrained != unconstrained_copy:
        raise RuntimeError("binding or pair validation mutated a shared template")

    # A prepared even label checks the otherwise unreachable false branch.
    feedback_binding = {PHASE_LABEL: 0, TRUE_CORRECTION_ANGLE: -math.pi / 2, FALSE_CORRECTION_ANGLE: 0}
    independent_binding = {**feedback_binding, FALSE_CORRECTION_ANGLE: -math.pi / 2}
    if not np.allclose(ideal_branch_probabilities(source.assign_parameters(feedback_binding)), [1, 0, 0, 0]):
        raise RuntimeError("feedback false branch changed its identity action")
    if not np.allclose(ideal_branch_probabilities(source.assign_parameters(independent_binding)), [0.5, 0, 0.5, 0]):
        raise RuntimeError("label-known false branch failed to apply its correction")

    feedback = bind_correction_template(routed, 1, CORRECTION_ARMS[0])
    independent = bind_correction_template(routed, 1, CORRECTION_ARMS[1])
    valid = validate_correction_pair(routed, feedback, independent, 1)
    correction_position = valid["correction_instruction_index"]
    measurements = valid["measurement_writers"]
    reset_position = valid["reset_instructions"][0][0]
    mutations: list[QuantumCircuit] = []
    for mutation in ("condition", "false_phase", "remove_zero_rotation", "extra_true_gate", "remove_false_branch"):
        mutations.append(_change_dispatch(feedback, correction_position, mutation=mutation))
    changed_prefix = feedback.copy()
    changed_prefix.global_phase += math.pi / 11
    mutations.append(changed_prefix)
    mutations.append(_replace(feedback, reset_position, None))
    terminal_position = measurements[1][0]
    terminal = feedback.data[terminal_position]
    mutations.append(_replace(feedback, terminal_position, terminal.replace(clbits=(feedback.clbits[0],))))
    mutations.append(
        _replace(feedback, terminal_position, terminal.replace(qubits=(feedback.qubits[measurements[0][1]],)))
    )
    changed_suffix = feedback.copy()
    changed_suffix.x(measurements[0][1])
    mutations.append(changed_suffix)
    changed_initial_gate = _replace(feedback, 0, feedback.data[0].replace(operation=XGate()))
    mutations.append(changed_initial_gate)
    for mutation_circuit in mutations:
        _reject(partial(validate_correction_pair, routed, mutation_circuit, independent, 1))
        _reject(partial(validate_bound_correction_pair, mutation_circuit, independent, 1))
    _reject(lambda: validate_bound_correction_pair(independent, feedback, 1))
    _reject(lambda: validate_bound_correction_pair(feedback, independent, 3))
    _reject(lambda: validate_correction_pair(routed, independent, feedback, 1))
    _reject(lambda: validate_correction_pair(routed, feedback, independent, 3))
    _reject(lambda: correction_binding(True, CORRECTION_ARMS[0]))
    _reject(lambda: correction_binding(0, CORRECTION_ARMS[0]))
    _reject(lambda: correction_binding(1, "dispatch_removed"))
    _reject(lambda: bind_correction_template(feedback, 1, CORRECTION_ARMS[0]))
    escaped_angle = source.copy()
    escaped_angle.rz(FALSE_CORRECTION_ANGLE, 0)
    _reject(lambda: bind_correction_template(escaped_angle, 1, CORRECTION_ARMS[0]))
    optimized_again = transpile(feedback, backend=backend, optimization_level=3, seed_transpiler=20261010)
    _reject(lambda: validate_correction_pair(routed, optimized_again, independent, 1))
    return {
        "matched_source_and_native_pairs": len(reports),
        "qpy_roundtrip_pairs": len(reports),
        "false_branch_semantic_controls": 2,
        "rejected_mutations": len(mutations) + 8,
        "rejected_bound_pair_mutations": len(mutations) + 2,
        "offline_target": "bundled FakeKingston",
        "native_pair": valid,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))

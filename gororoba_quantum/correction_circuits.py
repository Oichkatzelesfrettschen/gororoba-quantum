"""Match recorded-bit-dependent corrections against label-known corrections.

Both arms keep the first measurement, reset, classical dispatch, and terminal
writer. The label-known arm applies the same phase in both dispatch branches.
The comparison can measure dependence on the recorded bit; dispatch-removal
latency and general unknown-eigenphase order finding remain outside its scope.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import Clbit, ControlFlowOp, Parameter, ParameterExpression

from order_finding import controlled_rotate, eigenstate_prep
from qpe_diagnostics import ideal_compiled_probabilities

PHASE_LABEL = Parameter("correction_phase_label")
TRUE_CORRECTION_ANGLE = Parameter("correction_true_angle")
FALSE_CORRECTION_ANGLE = Parameter("correction_false_angle")
CORRECTION_ARMS = ("measured_feedback", "recorded_bit_independent")
_PARAMETERS = frozenset((PHASE_LABEL, TRUE_CORRECTION_ANGLE, FALSE_CORRECTION_ANGLE))


def correction_template() -> QuantumCircuit:
    """Build one symbolic source for both odd labels and both correction arms."""
    control = QuantumRegister(1, "ctrl")
    work = QuantumRegister(4, "w")
    phase = ClassicalRegister(2, "c")
    circuit = QuantumCircuit(control, work, phase, name="folded_recorded_bit_correction_template")
    work_qubits = [1, 2, 3, 4]
    eigenstate_prep(circuit, work_qubits, 0)
    for work_index in range(1, 4):
        circuit.p(-math.pi * PHASE_LABEL * work_index / 2, work_qubits[work_index])
    circuit.h(0)
    controlled_rotate(circuit, 0, work_qubits, 2)
    circuit.h(0)
    circuit.measure(0, phase[0])
    circuit.reset(0)
    circuit.h(0)
    controlled_rotate(circuit, 0, work_qubits, 1)
    with circuit.if_test((phase[0], 1)) as otherwise:
        circuit.p(TRUE_CORRECTION_ANGLE, 0)
    with otherwise:
        circuit.p(FALSE_CORRECTION_ANGLE, 0)
    circuit.h(0)
    circuit.measure(0, phase[1])
    return circuit


def correction_binding(phase_label: int, arm: str) -> dict[Parameter, float]:
    """Return the complete binding for one supplied odd eigenlabel."""
    if type(phase_label) is not int or phase_label not in (1, 3):
        raise ValueError("correction phase label must be the integer 1 or 3")
    if arm not in CORRECTION_ARMS:
        raise ValueError(f"unknown correction arm {arm!r}")
    return {
        PHASE_LABEL: float(phase_label),
        TRUE_CORRECTION_ANGLE: -math.pi / 2,
        FALSE_CORRECTION_ANGLE: 0.0 if arm == "measured_feedback" else -math.pi / 2,
    }


def correction_member_metadata(phase_label: int, arm: str) -> dict[str, Any]:
    """Describe the finite witness and its scheduling qualification boundary."""
    binding = correction_binding(phase_label, arm)
    return {
        "phase_label": phase_label,
        "arm": arm,
        "bindings": {parameter.name: value for parameter, value in binding.items()},
        "known_eigenlabel_witness": True,
        "first_measurement_retained": True,
        "reset_retained": True,
        "classical_dispatch_retained": True,
        "recorded_bit_independent_correction": arm == "recorded_bit_independent",
        "backend_schedule_certified": False,
        "dispatch_removal_test": False,
        "post_binding_transpilation_allowed": False,
    }


def _parameters(value: Any) -> set[Parameter]:
    return set(value.parameters) if isinstance(value, ParameterExpression) else set()


def _numeric(value: Any) -> float:
    if _parameters(value):
        raise ValueError("correction history contains an unbound parameter")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("correction history contains a nonfinite parameter")
    return result


def _history(circuit: QuantumCircuit) -> dict[str, Any]:
    """Represent every ordered instruction, mapped operand, and branch phase."""
    instructions: list[dict[str, Any]] = []
    for instruction in circuit.data:
        operation = instruction.operation
        entry: dict[str, Any] = {
            "name": operation.name,
            "class": f"{operation.base_class.__module__}.{operation.base_class.__qualname__}",
            "qubits": [circuit.find_bit(bit).index for bit in instruction.qubits],
            "clbits": [circuit.find_bit(bit).index for bit in instruction.clbits],
        }
        if isinstance(operation, ControlFlowOp):
            if operation.name != "if_else":
                raise ValueError("correction history supports only if_else control flow")
            condition_bit, condition_value = operation.condition
            if not isinstance(condition_bit, Clbit):
                raise ValueError("correction condition must use one measured classical bit")
            entry["condition"] = [circuit.find_bit(condition_bit).index, int(condition_value)]
            entry["blocks"] = [_history(block) for block in operation.blocks]
        else:
            entry["parameters"] = [_numeric(value) for value in operation.params]
            if operation.name == "delay":
                entry["unit"] = operation.unit
        instructions.append(entry)
    layout = circuit.layout
    return {
        "num_qubits": circuit.num_qubits,
        "num_clbits": circuit.num_clbits,
        "qregs": [[register.name, [circuit.find_bit(bit).index for bit in register]] for register in circuit.qregs],
        "cregs": [[register.name, [circuit.find_bit(bit).index for bit in register]] for register in circuit.cregs],
        "global_phase": _numeric(circuit.global_phase),
        "initial_layout": None if layout is None else list(layout.initial_index_layout()),
        "final_layout": None if layout is None else list(layout.final_index_layout()),
        "instructions": instructions,
    }


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _template_slots(template: QuantumCircuit) -> tuple[int, list[list[int]], list[list[int]]]:
    if set(template.parameters) != _PARAMETERS or template.num_clbits != 2:
        raise ValueError("correction template requires exactly its three parameters and two measured bits")
    control_positions = [
        index for index, instruction in enumerate(template.data) if isinstance(instruction.operation, ControlFlowOp)
    ]
    if len(control_positions) != 1:
        raise ValueError("correction template requires exactly one classical dispatch")
    correction_index = control_positions[0]
    correction = template.data[correction_index]
    operation = correction.operation
    if operation.name != "if_else" or len(operation.blocks) != 2:
        raise ValueError("correction template requires an explicit true and false branch")
    condition_bit, condition_value = operation.condition
    if (
        not isinstance(condition_bit, Clbit)
        or template.find_bit(condition_bit).index != 0
        or condition_value != 1
        or len(correction.qubits) != 1
        or tuple(correction.clbits) != (condition_bit,)
    ):
        raise ValueError("correction must dispatch on measured bit zero equaling one")
    for block, parameter in zip(operation.blocks, (TRUE_CORRECTION_ANGLE, FALSE_CORRECTION_ANGLE), strict=True):
        if block.num_qubits != 1 or block.num_clbits != 1 or len(block.data) != 1:
            raise ValueError("each correction branch must contain one single-qubit phase operation")
        gate = block.data[0]
        if gate.operation.name not in ("p", "rz") or gate.operation.params != [parameter]:
            raise ValueError("correction branch changed its named angle slot")
        if len(gate.qubits) != 1 or block.find_bit(gate.qubits[0]).index != 0 or gate.clbits:
            raise ValueError("correction phase operation changed its operands")
        if set(block.parameters) != {parameter}:
            raise ValueError("correction branch contains parameters outside its named angle")
        expected_phase = 0.0 if gate.operation.name == "p" else parameter / 2
        if block.global_phase != expected_phase:
            raise ValueError("correction branch lost the exact phase-gate global phase")
    if _parameters(template.global_phase) - {PHASE_LABEL}:
        raise ValueError("correction angles escaped into the top-level global phase")
    measurements: list[list[int]] = []
    resets: list[list[int]] = []
    for index, instruction in enumerate(template.data):
        if index == correction_index:
            continue
        for parameter_value in instruction.operation.params:
            if _parameters(parameter_value) - {PHASE_LABEL}:
                raise ValueError("correction angle escaped the correction branches")
        if instruction.operation.name == "measure":
            measurements.append(
                [index, template.find_bit(instruction.qubits[0]).index, template.find_bit(instruction.clbits[0]).index]
            )
        elif instruction.operation.name == "reset":
            resets.append([index, template.find_bit(instruction.qubits[0]).index])
        elif instruction.clbits:
            raise ValueError("unexpected classical operation outside the correction slot")
    if len(measurements) != 2 or [entry[2] for entry in measurements] != [0, 1] or len(resets) != 1:
        raise ValueError("correction template requires two ordered measurements and one reset")
    if not measurements[0][0] < resets[0][0] < correction_index < measurements[1][0]:
        raise ValueError("correction template changed measurement, reset, or dispatch order")
    if resets[0][1] != measurements[0][1]:
        raise ValueError("reset must act on the first measurement writer")
    if template.find_bit(correction.qubits[0]).index != measurements[1][1]:
        raise ValueError("correction must act on the terminal measurement writer")
    for instruction in template.data[measurements[0][0] + 1 :]:
        if isinstance(instruction.operation, ControlFlowOp):
            continue
        if any(_parameters(value) for value in instruction.operation.params):
            raise ValueError("eigenlabel parameter escaped the preparation prefix")
    return correction_index, measurements, resets


def bind_correction_template(template: QuantumCircuit, phase_label: int, arm: str) -> QuantumCircuit:
    """Bind an already routed template without further optimization or routing."""
    binding = correction_binding(phase_label, arm)
    _template_slots(template)
    bound = template.assign_parameters(binding)
    bound.name = f"correction_{arm}_s{phase_label}"
    return bound


def validate_correction_pair(
    routed_template: QuantumCircuit,
    feedback: QuantumCircuit,
    independent: QuantumCircuit,
    phase_label: int,
) -> dict[str, Any]:
    """Require exact common-template history and ideal laws for both finite arms.

    The signature covers the entire prefix and suffix, including independent
    physical-wire operations interleaved after the terminal Hadamard. Matching
    circuit histories certifies the local artifact, not backend branch timing,
    server optimization, scheduled duration, or instruction-level shot pairing.
    """
    correction_index, measurements, resets = _template_slots(routed_template)
    histories = []
    for arm, circuit in zip(CORRECTION_ARMS, (feedback, independent), strict=True):
        expected = bind_correction_template(routed_template, phase_label, arm)
        history = _history(circuit)
        if history != _history(expected):
            raise ValueError(f"{arm}: circuit differs from its exact common-template binding")
        expected_law = np.zeros(4)
        expected_law[phase_label] = 1.0
        observed_law = ideal_compiled_probabilities(circuit)
        if not np.allclose(observed_law, expected_law, atol=1e-11, rtol=0):
            raise ValueError(f"{arm}: compiled ideal law differs from the supplied odd eigenlabel")
        histories.append(history)
    feedback_history, independent_history = histories
    feedback_operations = feedback_history["instructions"]
    independent_operations = independent_history["instructions"]
    prefix = feedback_operations[:correction_index]
    suffix = feedback_operations[correction_index + 1 :]
    if prefix != independent_operations[:correction_index] or suffix != independent_operations[correction_index + 1 :]:
        raise ValueError("correction pair changed its complete prefix or suffix")
    return {
        "phase_label": phase_label,
        "validation": "exact_common_template_history_and_ideal_law",
        "correction_instruction_index": correction_index,
        "correction_physical_qubit": measurements[1][1],
        "correction_operation": feedback.data[correction_index].operation.blocks[0].data[0].operation.name,
        "dispatch_condition": {"classical_bit": 0, "equals": 1},
        "correction_branch_angles": {
            "measured_feedback": {"then": -math.pi / 2, "else": 0.0},
            "recorded_bit_independent": {"then": -math.pi / 2, "else": -math.pi / 2},
        },
        "measurement_writers": measurements,
        "reset_instructions": resets,
        "protected_history_equal": True,
        "prefix_sha256": _digest(prefix),
        "suffix_sha256": _digest(suffix),
        "feedback_history_sha256": _digest(feedback_history),
        "independent_history_sha256": _digest(independent_history),
        "classical_dispatch_retained": True,
        "backend_schedule_certified": False,
        "dispatch_removal_test": False,
        "scheduler_zero_phase_else_elision_allowed": True,
        "scheduler_elision_scope": (
            "Only the feedback arm's zero-duration else rotation may disappear from scheduler rows; "
            "protected event timing must match and both independent-arm branch rotations must remain. "
            "Both branch rotations remain mandatory in local circuit histories."
        ),
    }

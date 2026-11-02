"""Qiskit behavior the repository's circuits rely on, checked against answers fixed by construction."""

from __future__ import annotations

import io

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, qpy, transpile
from qiskit.circuit import Delay, Parameter
from qiskit.circuit.library import CXGate, Measure, RGate, XGate
from qiskit.quantum_info import Operator
from qiskit.transpiler import InstructionProperties, Target


def bell() -> QuantumCircuit:
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit


def test_transpile_to_a_basis_preserves_the_operator() -> None:
    circuit = bell()
    circuit.append(RGate(0.3, 0.7), [1])
    circuit.append(XGate(), [0])
    lowered = transpile(circuit, basis_gates=["rz", "sx", "x", "cx"], optimization_level=3)
    if not set(lowered.count_ops()) <= {"rz", "sx", "x", "cx"}:
        raise AssertionError(lowered.count_ops())
    if not Operator(lowered).equiv(Operator(circuit)):
        raise AssertionError("transpilation changed the unitary")


def test_transpile_to_a_directed_target_honors_layout_and_supported_instructions() -> None:
    target = Target(num_qubits=3, dt=1e-9)
    target.add_instruction(XGate(), {(qubit,): InstructionProperties(duration=32e-9) for qubit in range(3)})
    target.add_instruction(
        RGate(Parameter("theta"), Parameter("phi")),
        {(qubit,): InstructionProperties(duration=32e-9) for qubit in range(3)},
    )
    target.add_instruction(CXGate(), {pair: InstructionProperties(duration=320e-9) for pair in [(0, 1), (1, 2)]})
    target.add_instruction(Measure(), {(qubit,): InstructionProperties(duration=1e-6) for qubit in range(3)})
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    lowered = transpile(circuit, target=target, initial_layout=[2, 1], optimization_level=1)
    for instruction in lowered.data:
        qubits = tuple(lowered.find_bit(qubit).index for qubit in instruction.qubits)
        if instruction.operation.name != "barrier" and not target.instruction_supported(
            instruction.operation.name, qubits
        ):
            raise AssertionError(f"{instruction.operation.name} on {qubits} is outside the target")
    if lowered.layout.initial_index_layout()[:2] != [2, 1]:
        raise AssertionError(lowered.layout.initial_index_layout())


def test_qpy_round_trip_keeps_parameters_delays_and_registers() -> None:
    theta = Parameter("theta")
    quantum, classical = QuantumRegister(2, "q"), ClassicalRegister(2, "c")
    circuit = QuantumCircuit(quantum, classical)
    circuit.rx(theta, 0)
    circuit.append(Delay(160, "dt"), [1])
    circuit.measure(quantum, classical)
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    buffer.seek(0)
    (loaded,) = qpy.load(buffer)
    if loaded != circuit or loaded.parameters != circuit.parameters:
        raise AssertionError("qpy round trip changed the circuit")

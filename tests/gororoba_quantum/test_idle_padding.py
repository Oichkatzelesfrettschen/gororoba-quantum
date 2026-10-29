"""Contracts of the local idle padding: list-schedule gaps become top-level delays and the schedule is unchanged."""

from __future__ import annotations

import scheduled_idle_replay as replay
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

import idle_padding

LENGTHS = {"sx": 8, "cz": 17, "measure": 100}


def duration(name: str, _: tuple[int, ...]) -> int:
    return LENGTHS[name]


def delays(circuit: QuantumCircuit) -> list[tuple[int, int]]:
    return [
        (circuit.find_bit(i.qubits[0]).index, int(i.operation.duration))
        for i in circuit.data
        if i.operation.name == "delay"
    ]


def test_wait_behind_a_neighbor_becomes_one_delay_and_keeps_the_list_schedule() -> None:
    circuit = QuantumCircuit(QuantumRegister(3, "q"))
    circuit.sx(0)
    circuit.sx(1)
    circuit.cz(1, 2)
    circuit.cz(1, 2)
    circuit.cz(0, 1)
    circuit.delay(40, 2, unit="dt")
    circuit.sx(2)
    padded, inserted = idle_padding.pad(circuit, duration)
    # Qubit 0 waits from 8 to 42 behind the two CZ on 1 and 2; qubit 2's own delay is the circuit's, not inserted.
    if inserted != {0: 34} or delays(padded) != [(0, 34), (2, 40)]:
        raise AssertionError(f"inserted {inserted}, delays {delays(padded)}")
    before = replay.list_schedule_idle(circuit, duration, [0, 1, 2])
    after = replay.list_schedule_idle(padded, duration, [0, 1, 2])
    if before != after:
        raise AssertionError(f"padding moved the list schedule: {before} -> {after}")


def test_barrier_wait_is_padded_and_a_late_first_instruction_is_not() -> None:
    circuit = QuantumCircuit(QuantumRegister(3, "q"))
    for _ in range(3):
        circuit.sx(0)
    circuit.sx(1)
    circuit.barrier(0, 1, 2)
    circuit.sx(1)
    circuit.sx(2)
    padded, inserted = idle_padding.pad(circuit, duration)
    # Qubit 1 waits from 8 to the barrier at 24; qubit 2 first plays at 24 and rests in |0> before it.
    if inserted != {1: 16} or delays(padded) != [(1, 16)]:
        raise AssertionError(f"inserted {inserted}, delays {delays(padded)}")


def test_if_else_aligns_its_qubits_and_occupies_its_body_span() -> None:
    qubits = QuantumRegister(2, "q")
    bits = ClassicalRegister(1, "c")
    circuit = QuantumCircuit(qubits, bits)
    circuit.sx(1)
    circuit.measure(0, bits[0])
    with circuit.if_test((bits[0], 1)):
        circuit.sx(1)
        circuit.sx(1)
    circuit.sx(0)
    circuit.sx(1)
    padded, inserted = idle_padding.pad(circuit, duration)
    # The branch starts when the measure ends at 100: qubit 1 waits 92 after its sx; the body runs to 116 on
    # qubit 1 and plays nothing on qubit 0, which then plays its sx at 100.
    if inserted != {1: 92} or delays(padded) != [(1, 92)]:
        raise AssertionError(f"inserted {inserted}, delays {delays(padded)}")
    names = [i.operation.name for i in padded.data if i.operation.name != "delay"]
    if names != ["sx", "measure", "if_else", "sx", "sx"]:
        raise AssertionError(f"instruction order changed: {names}")


def test_target_duration_refuses_an_instruction_without_a_duration() -> None:
    from qiskit.circuit.library import SXGate
    from qiskit.transpiler import InstructionProperties, Target

    target = Target(num_qubits=1, dt=4e-9)
    target.add_instruction(SXGate(), {(0,): InstructionProperties(duration=32e-9)})
    target.add_instruction(SXGate().copy("sx_unscheduled"), {(0,): InstructionProperties(duration=None)})
    lookup = idle_padding.target_duration(target)
    if lookup("sx", (0,)) != 8:
        raise AssertionError("32 ns at dt 4 ns is 8 dt")
    try:
        lookup("sx_unscheduled", (0,))
    except RuntimeError:
        return
    raise AssertionError("an instruction without a duration was scheduled")


def test_scale_multiplies_inserted_delays_and_keeps_own_delays_and_reported_idle() -> None:
    circuit = QuantumCircuit(QuantumRegister(3, "q"))
    circuit.sx(0)
    circuit.sx(1)
    circuit.cz(1, 2)
    circuit.cz(1, 2)
    circuit.cz(0, 1)
    circuit.delay(40, 2, unit="dt")
    circuit.sx(2)
    tripled, inserted = idle_padding.pad(circuit, duration, 3.0)
    dropped, _ = idle_padding.pad(circuit, duration, 0.0)
    if inserted != {0: 34} or delays(tripled) != [(0, 102), (2, 40)] or delays(dropped) != [(2, 40)]:
        raise AssertionError(f"inserted {inserted}, tripled {delays(tripled)}, dropped {delays(dropped)}")


def test_alap_moves_a_wait_before_the_late_instruction_and_honors_the_measured_bit() -> None:
    qubits = QuantumRegister(2, "q")
    bits = ClassicalRegister(1, "c")
    circuit = QuantumCircuit(qubits, bits)
    circuit.sx(1)
    circuit.sx(1)
    circuit.measure(0, bits[0])
    with circuit.if_test((bits[0], 1)):
        circuit.sx(1)
    circuit.sx(1)
    late, inserted = idle_padding.pad(circuit, duration, placement="alap")
    # Makespan 116: the branch reads the bit when the measure ends at 100, so qubit 1's two sx move to 84 and 92,
    # and its wait of 84 before the first sx is no idle; ASAP leaves qubit 1 idle from 16 to 100 instead.
    if inserted != {} or delays(late) != []:
        raise AssertionError(f"alap inserted {inserted}, delays {delays(late)}")
    _, early = idle_padding.pad(circuit, duration)
    if early != {1: 84}:
        raise AssertionError(f"asap inserted {early}")
    slots = idle_padding.alap(circuit, duration)
    if [slot[0] if slot else None for slot in slots] != [84, 92, 0, 100, 108]:
        raise AssertionError(f"alap starts {slots}")

"""Write the idle of a local list schedule into an ISA circuit as explicit delays.

NoiseModel.from_backend charges T1 and T2 relaxation on gate durations and, through its RelaxationNoisePass, on
top-level `delay` instructions only. An ISA circuit states no delay, so a qubit waiting behind another qubit's
gates relaxes for free in the model. pad() schedules the circuit as soon as possible under a duration function
(the Target's gate durations in dt) and inserts, before each instruction, the delay that separates it from the
qubit's previous instruction. alap() places the same instructions as late as the ASAP makespan allows, the
placement IBM's scheduler plays (docs/evidence/local_idle_padding/README.md). The input is the circuit and the
Target alone, so the planner computes it before submission.

Scheduling rules: an instruction starts once every qubit it acts on is free and every classical bit it reads or
writes holds its last measurement's result; a barrier aligns its qubits without
playing; an `if_else` aligns its qubits and occupies each of them for the span its true body plays on it. Idle
inside a control-flow body stays unpadded, since the relaxation pass reaches top-level delays only. The
measure-to-branch latency of the feed-forward path is not modeled. A qubit's idle starts at its first instruction:
before it the qubit rests in |0>, where relaxation acts trivially.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from qiskit import QuantumCircuit
from qiskit.circuit import Delay

# rz is a virtual frame change and a barrier plays nothing; neither occupies a qubit.
VIRTUAL = frozenset({"rz", "barrier"})

Duration = Callable[[str, tuple[int, ...]], int]


def target_duration(target: Any) -> Duration:
    """duration(name, physical) in dt from the Target's instruction properties."""

    def duration(name: str, physical: tuple[int, ...]) -> int:
        properties = target[name][physical]
        if properties is None or properties.duration is None:
            raise RuntimeError(f"the Target states no duration for {name} on {physical}")
        return round(properties.duration / target.dt)

    return duration


def _body_ends(body: QuantumCircuit, physical: list[int], start: int, duration: Duration) -> dict[int, int]:
    """End time of each of physical's qubits after body plays as soon as possible from start."""
    cursor = dict.fromkeys(physical, start)
    for inner in body.data:
        name = inner.operation.name
        mapped = [physical[body.find_bit(bit).index] for bit in inner.qubits]
        aligned = max(cursor[q] for q in mapped)
        if name == "barrier":
            for q in mapped:
                cursor[q] = aligned
        elif name in VIRTUAL:
            continue
        else:
            span = int(inner.operation.duration) if name == "delay" else duration(name, tuple(mapped))
            for q in mapped:
                cursor[q] = aligned + span
    return cursor


Slot = tuple[int, dict[int, int]] | None


def _span(instruction: Any, physical: list[int], duration: Duration) -> dict[int, int]:
    """Per-qubit length of a played instruction; an if_else lasts as long as its true body plays on each qubit."""
    operation = instruction.operation
    if operation.name == "if_else":
        return _body_ends(operation.blocks[0], physical, 0, duration)
    span = int(operation.duration) if operation.name == "delay" else duration(operation.name, tuple(physical))
    return dict.fromkeys(physical, span)


def asap(circuit: QuantumCircuit, duration: Duration) -> list[Slot]:
    """(start, per-qubit end) of every played instruction, each as early as its qubits and condition bits allow."""
    ready: dict[int, int] = {}
    # A classical bit is ready once the measurement that wrote it ends; a branch reads its condition bits.
    written: dict[int, int] = {}
    slots: list[Slot] = []
    for instruction in circuit.data:
        name = instruction.operation.name
        physical = [circuit.find_bit(bit).index for bit in instruction.qubits]
        bits = [circuit.find_bit(bit).index for bit in instruction.clbits]
        start = max([ready.get(q, 0) for q in physical] + [written.get(c, 0) for c in bits], default=0)
        if name in VIRTUAL:
            if name == "barrier":
                for q in physical:
                    ready[q] = start
            slots.append(None)
            continue
        ends = {q: start + length for q, length in _span(instruction, physical, duration).items()}
        ready.update(ends)
        if name == "measure":
            for c in bits:
                written[c] = ends[physical[0]]
        slots.append((start, ends))
    return slots


def alap(circuit: QuantumCircuit, duration: Duration) -> list[Slot]:
    """(start, per-qubit end) of every played instruction, each as late as the ASAP makespan allows.

    A backward pass from the ASAP makespan places each instruction to end no later than every later instruction on
    its qubits starts. A measurement ends before the next branch that reads its bit starts and before the next
    measurement that overwrites it starts; a branch starts before the next measurement that overwrites a bit it
    reads ends. A barrier aligns its qubits.
    """
    forward = asap(circuit, duration)
    makespan = max((max(slot[1].values()) for slot in forward if slot is not None), default=0)
    deadline: dict[int, int] = {}
    read_by: dict[int, int] = {}
    overwritten: dict[int, int] = {}
    slots: list[Slot] = [None] * len(circuit.data)
    for index in range(len(circuit.data) - 1, -1, -1):
        instruction = circuit.data[index]
        name = instruction.operation.name
        physical = [circuit.find_bit(bit).index for bit in instruction.qubits]
        bits = [circuit.find_bit(bit).index for bit in instruction.clbits]
        if name in VIRTUAL:
            if name == "barrier":
                aligned = min(deadline.get(q, makespan) for q in physical)
                for q in physical:
                    deadline[q] = aligned
            continue
        lengths = _span(instruction, physical, duration)
        start = min(deadline.get(q, makespan) - lengths[q] for q in physical)
        if name == "measure":
            limits = [min(read_by.get(c, makespan), overwritten.get(c, makespan)) for c in bits]
            start = min([start] + [limit - lengths[physical[0]] for limit in limits])
            for c in bits:
                overwritten[c] = start
                read_by.pop(c, None)
        elif bits:
            start = min([start] + [overwritten.get(c, makespan) for c in bits])
            for c in bits:
                read_by[c] = min(read_by.get(c, makespan), start)
        for q in physical:
            deadline[q] = start
        slots[index] = (start, {q: start + lengths[q] for q in physical})
    return slots


PLACEMENTS = {"asap": asap, "alap": alap}


def pad(
    circuit: QuantumCircuit, duration: Duration, scale: float = 1.0, placement: str = "asap"
) -> tuple[QuantumCircuit, dict[int, int]]:
    """circuit with the idle of a list schedule inserted as dt delays, and the scheduled idle per qubit in dt.

    placement names the schedule: ``asap`` starts each instruction as early as possible, ``alap`` as late as the
    ASAP makespan allows (the order IBM's scheduler plays). scale multiplies each inserted delay (rounded to whole
    dt, dropped at zero) and leaves the schedule, the circuit's own delays and the returned idle unchanged.
    """
    out = circuit.copy_empty_like()
    end: dict[int, int] = {}
    inserted: dict[int, int] = {}
    for instruction, slot in zip(circuit.data, PLACEMENTS[placement](circuit, duration), strict=True):
        if slot is not None:
            start, ends = slot
            for bit in instruction.qubits:
                q = circuit.find_bit(bit).index
                if q in end and start > end[q]:
                    length = start - end[q] if scale == 1.0 else round((start - end[q]) * scale)
                    if length > 0:
                        out.append(Delay(length, unit="dt"), [bit])
                    inserted[q] = inserted.get(q, 0) + start - end[q]
                elif q in end and start < end[q]:
                    raise RuntimeError(f"{placement} schedule overlaps qubit {q} at {start} before {end[q]}")
            end.update(ends)
        out.append(instruction)
    return out, inserted

"""Contracts of the idle scaling: stated delays and inserted scheduler idle scale by kind, the schedule stays."""

from __future__ import annotations

import scheduled_idle_replay as replay
import scheduled_idle_scaling as scaling
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

Row = tuple[str, str, str, int, int, str]


def _circuit(segments: tuple[int, ...]) -> tuple[QuantumCircuit, list[Row]]:
    qubits = QuantumRegister(1, "q")
    bits = ClassicalRegister(1, "g0_r0_m")
    circuit = QuantumCircuit(qubits, bits, name="pub")
    circuit.sx(0)
    for segment in segments:
        circuit.delay(segment, 0, unit="dt")
        circuit.x(0)
    rows: list[Row] = [("main", "INIT_0", "Qubit 0", 0, 100, "play"), ("main", "sx_0", "Qubit 0", 100, 8, "play")]
    rows += [("main", "x_0", "Qubit 0", 200 + 1000 * (k + 1), 8, "play") for k in range(len(segments))]
    return circuit, rows


def _delays(dose: float, idle: float, segments: tuple[int, ...] = (100,)) -> tuple[list[int], list[int]]:
    circuit, rows = _circuit(segments)
    padded, _ = replay.padded_replica(scaling.tagged(circuit), rows, [0], ["g0_r0_m"])
    out = scaling.scaled(padded, dose, idle)
    stated = [int(i.operation.duration) for i in padded.data if i.operation.name == "delay" and i.operation.label]
    return stated, [int(i.operation.duration) for i in out.data if i.operation.name == "delay"]


def test_dose_scale_multiplies_stated_delays_and_keeps_the_scheduler_idle() -> None:
    # sx ends at 108, the stated delay of 100 runs to 208, and the scheduler idles 992 more to the x at 1,200.
    if _delays(1.0, 1.0) != ([100], [100, 992]):
        raise AssertionError(f"unscaled: {_delays(1.0, 1.0)}")
    for dose, expected in ((2.0, [200, 992]), (0.25, [25, 992])):
        if _delays(dose, 1.0)[1] != expected:
            raise AssertionError(f"dose scale {dose}: {_delays(dose, 1.0)[1]}")


def test_idle_scale_multiplies_the_inserted_scheduler_idle_as_well() -> None:
    if _delays(2.0, 2.0)[1] != [200, 1984]:
        raise AssertionError(f"all-idle scale 2: {_delays(2.0, 2.0)[1]}")


def test_scaled_split_dose_sums_to_the_rounded_scaled_total() -> None:
    stated, delays = _delays(0.25, 1.0, (438, 876, 438))
    # Stated and inserted delays alternate; rounded one by one the stated ones would sum to 110 + 219 + 110 = 439.
    if stated != [438, 876, 438] or sum(delays[::2]) != round(0.25 * 1752) or delays[1::2] != [654, 116, 554]:
        raise AssertionError(f"scaled delays {delays} from stated {stated}")


def test_a_stated_delay_is_found_on_its_replica_only() -> None:
    circuit, _ = _circuit((100,))
    if not scaling.has_stated_delay(circuit, [0]):
        raise AssertionError("a stated delay goes unnoticed")

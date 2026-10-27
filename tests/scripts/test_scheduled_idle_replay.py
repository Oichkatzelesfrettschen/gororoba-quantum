"""Contracts of the scheduled-idle padding: gaps become delays, virtual gates and split resets stay aligned."""

from __future__ import annotations

import scheduled_idle_replay as replay
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

Row = tuple[str, str, str, int, int, str]


def fused() -> QuantumCircuit:
    qubits = QuantumRegister(3, "q")
    bits = ClassicalRegister(1, "g0_r0_m")
    circuit = QuantumCircuit(qubits, bits, name="pub")
    circuit.sx(0)
    circuit.sx(0)
    circuit.rz(0.3, 1)
    circuit.cz(0, 1)
    circuit.measure(0, bits[0])
    circuit.reset(0)
    circuit.sx(1)
    return circuit


def rows() -> list[Row]:
    return [
        ("main", "INIT_0", "Qubit 0", 0, 100, "play"),
        ("main", "sx_0", "Qubit 0", 100, 8, "play"),
        ("main", "sx_0", "Qubit 0", 104, 0, "shift_phase"),
        ("main", "sx_0", "Qubit 0", 108, 8, "play"),
        ("main", "rz_1", "Qubit 1", 116, 0, "shift_phase"),
        ("main", "cz_0_1", "Qubit 0", 116, 17, "play"),
        ("main", "cz_0_1", "Qubit 1", 116, 17, "play"),
        ("main", "measure_0", "Qubit 0", 133, 64, "play"),
        ("main", "measure_0", "Qubit 0", 197, 108, "play"),
        ("main", "reset_0", "Qubit 0", 400, 300, "play"),
        ("main", "reset_0", "Qubit 0", 950, 8, "play"),
        ("main", "sx_1", "Qubit 1", 900, 8, "play"),
    ]


def test_gaps_become_delays_and_back_to_back_gates_stay_separate() -> None:
    circuit, inserted = replay.padded_replica(fused(), rows(), [0, 1], ["g0_r0_m"])
    # Qubit 0: measure ends at 305, reset starts at 400 (95 dt); the reset's internal latency is not idle.
    # Qubit 1: the CZ ends at 133, sx starts at 900 (767 dt).
    if inserted != {0: 95, 1: 767}:
        raise AssertionError(f"inserted idle {inserted}")
    delays = [instruction for instruction in circuit.data if instruction.operation.name == "delay"]
    if sorted(int(d.operation.duration) for d in delays) != [95, 767]:
        raise AssertionError("delays differ from the scheduled gaps")
    names = [instruction.operation.name for instruction in circuit.data if instruction.operation.name != "delay"]
    if names != ["sx", "sx", "rz", "cz", "measure", "reset", "sx"]:
        raise AssertionError(f"instruction order changed: {names}")


def test_a_qubit_outside_the_replica_is_dropped() -> None:
    circuit, inserted = replay.padded_replica(fused(), rows(), [0, 1], ["g0_r0_m"])
    if set(inserted) != {0, 1} or circuit.num_qubits != 3:
        raise AssertionError("the replica keeps only its qubits' instructions on the full register")


def test_a_schedule_out_of_order_raises() -> None:
    swapped = [row for row in rows() if row[1] != "sx_1"] + [("main", "x_1", "Qubit 1", 900, 8, "play")]
    try:
        replay.padded_replica(fused(), swapped, [0, 1], ["g0_r0_m"])
    except RuntimeError as error:
        if "expects sx" not in str(error):
            raise AssertionError(f"unexpected refusal {error}") from error
        return
    raise AssertionError("a schedule naming a different gate was accepted")


def test_unpadded_replica_matches_and_inserts_nothing() -> None:
    circuit, inserted = replay.padded_replica(fused(), rows(), [0, 1], ["g0_r0_m"], insert=False)
    if inserted != {0: 95, 1: 767}:
        raise AssertionError(f"the unpadded replica reports different scheduled idle {inserted}")
    if any(instruction.operation.name == "delay" for instruction in circuit.data):
        raise AssertionError("an unpadded replica carries a delay")


def test_exact_path_keeps_delay_relaxation_and_drops_body_delays() -> None:
    import math

    from qiskit.circuit import Delay
    from qiskit_aer.noise import NoiseModel
    from qiskit_aer.noise.passes import RelaxationNoisePass

    import dynamic_density

    t1, dt, duration = 100e-6, 4e-9, 5000
    noise = NoiseModel()
    noise._custom_noise_passes.append(RelaxationNoisePass(t1s=[t1], t2s=[t1], dt=dt, op_types=[Delay]))
    qubits = QuantumRegister(1, "q")
    bits = ClassicalRegister(2, "c")
    circuit = QuantumCircuit(qubits, bits)
    circuit.x(0)
    circuit.measure(0, bits[0])
    with circuit.if_test((bits[0], 1)):
        circuit.delay(16, 0, unit="dt")
    circuit.delay(duration, 0, unit="dt")
    circuit.measure(0, bits[1])
    relaxed = replay.relaxed(circuit, noise)
    names = [instruction.operation.name for instruction in relaxed.data]
    if "delay" in names or any(
        inner.operation.name == "delay"
        for i in relaxed.data
        if i.operation.name == "if_else"
        for block in i.operation.blocks
        if block is not None
        for inner in block.data
    ):
        raise AssertionError(f"a delay survived the exact path: {names}")
    law = dynamic_density.probabilities(relaxed, noise)
    survive = math.exp(-duration * dt / t1)
    if not math.isclose(law[0b11], survive, abs_tol=1e-12) or not math.isclose(law[0b01], 1 - survive, abs_tol=1e-12):
        raise AssertionError(f"exact law {law.tolist()} misses the relaxation exp(-t/T1) = {survive}")


def test_contract_values_sum_signed_replica_means() -> None:
    contracts = [
        {
            "name": "c",
            "terms": [
                {"member": "a", "values": [0.0, 1.0, 0.0, -1.0], "sign": 1},
                {"member": "b", "values": [0.0, 1.0, 0.0, -1.0], "sign": -1},
            ],
        }
    ]
    laws = {"a": [[0.25, 0.30, 0.25, 0.20], [0.25, 0.20, 0.25, 0.30]], "b": [[0.25, 0.20, 0.25, 0.30]]}
    value = replay.contract_values(contracts, laws)["c"]
    if abs(value - 0.10) > 1e-12:
        raise AssertionError(f"contract value {value}, expected 0.10")


def test_list_schedule_counts_waits_behind_a_neighbor_and_circuit_delays() -> None:
    qubits = QuantumRegister(3, "q")
    circuit = QuantumCircuit(qubits)
    circuit.sx(0)
    circuit.sx(1)
    circuit.cz(1, 2)
    circuit.cz(1, 2)
    circuit.cz(0, 1)
    circuit.delay(40, 2, unit="dt")
    circuit.sx(2)
    lengths = {"sx": 8, "cz": 17}
    idle = replay.list_schedule_idle(circuit, lambda name, _: lengths[name], [0, 1, 2])
    # Qubit 0 waits from 8 to 42 behind the two CZ on 1 and 2; qubit 2 waits through its own 40 dt delay.
    if idle != {0: 34, 1: 0, 2: 40}:
        raise AssertionError(f"list-schedule idle {idle}")


def test_list_schedule_aligns_qubits_at_a_barrier() -> None:
    circuit = QuantumCircuit(QuantumRegister(2, "q"))
    for _ in range(3):
        circuit.sx(0)
    circuit.sx(1)
    circuit.barrier(0, 1)
    circuit.sx(1)
    idle = replay.list_schedule_idle(circuit, lambda name, _: 8, [0, 1])
    # Qubit 1 ends its first sx at 8 and waits at the barrier until qubit 0 finishes at 24.
    if idle != {0: 0, 1: 16}:
        raise AssertionError(f"barrier idle {idle}")


def test_component_replicas_follow_group_and_reference() -> None:
    record = {
        "groups": [
            {"group": "a", "replicas": [{"physical_qubits": [0, 1]}, {"physical_qubits": [2, 3]}]},
            {"group": "b", "replicas": [{"physical_qubits": [4]}]},
        ]
    }
    packed = replay.component_replicas(record, {"group": "a", "reference": False, "physical_qubits": [0, 1, 2, 3]})
    isolated = replay.component_replicas(record, {"group": "a", "reference": True, "physical_qubits": [0, 1]})
    other = replay.component_replicas(record, {"group": "b", "reference": False, "physical_qubits": [4]})
    if packed != [[0, 1], [2, 3]] or isolated != [[0, 1]] or other != [[4]]:
        raise AssertionError(f"component replicas {packed} {isolated} {other}")


def test_dose_scale_multiplies_isa_delays_and_keeps_the_scheduler_idle() -> None:
    qubits = QuantumRegister(1, "q")
    bits = ClassicalRegister(1, "g0_r0_m")
    circuit = QuantumCircuit(qubits, bits, name="pub")
    circuit.sx(0)
    circuit.delay(100, 0, unit="dt")
    circuit.sx(0)
    schedule: list[Row] = [
        ("main", "INIT_0", "Qubit 0", 0, 100, "play"),
        ("main", "sx_0", "Qubit 0", 100, 8, "play"),
        ("main", "sx_0", "Qubit 0", 300, 8, "play"),
    ]
    if not replay.has_isa_delay(circuit, [0]):
        raise AssertionError("an ISA delay goes unnoticed")
    for scale, expected in ((1.0, [100, 92]), (2.0, [200, 92]), (0.25, [25, 92])):
        padded, inserted = replay.padded_replica(circuit, schedule, [0], ["g0_r0_m"], dose_scale=scale)
        delays = [int(i.operation.duration) for i in padded.data if i.operation.name == "delay"]
        if delays != expected or inserted != {0: 92}:
            raise AssertionError(f"dose scale {scale}: delays {delays}, inserted {inserted}")


def test_scaled_split_dose_sums_to_the_rounded_scaled_total() -> None:
    qubits = QuantumRegister(1, "q")
    bits = ClassicalRegister(1, "g0_r0_m")
    circuit = QuantumCircuit(qubits, bits, name="pub")
    for segment in (438, 876, 438):
        circuit.delay(segment, 0, unit="dt")
        circuit.x(0)
    schedule: list[Row] = [("main", "INIT_0", "Qubit 0", 0, 100, "play")] + [
        ("main", "x_0", "Qubit 0", 538 + 1000 * k, 8, "play") for k in range(3)
    ]
    # insert=False keeps only the scaled ISA delays; rounded one by one they would sum to 110 + 219 + 110 = 439.
    padded, _ = replay.padded_replica(circuit, schedule, [0], ["g0_r0_m"], insert=False, dose_scale=0.25)
    delays = [int(i.operation.duration) for i in padded.data if i.operation.name == "delay"]
    if sum(delays) != round(0.25 * 1752) or len(delays) != 3:
        raise AssertionError(f"scaled segments {delays} miss round(0.25 * 1752) = 438")


def test_idle_scale_multiplies_the_inserted_scheduler_idle_as_well() -> None:
    qubits = QuantumRegister(1, "q")
    bits = ClassicalRegister(1, "g0_r0_m")
    circuit = QuantumCircuit(qubits, bits, name="pub")
    circuit.sx(0)
    circuit.delay(100, 0, unit="dt")
    circuit.sx(0)
    schedule: list[Row] = [
        ("main", "INIT_0", "Qubit 0", 0, 100, "play"),
        ("main", "sx_0", "Qubit 0", 100, 8, "play"),
        ("main", "sx_0", "Qubit 0", 300, 8, "play"),
    ]
    padded, inserted = replay.padded_replica(circuit, schedule, [0], ["g0_r0_m"], dose_scale=2.0, idle_scale=2.0)
    delays = [int(i.operation.duration) for i in padded.data if i.operation.name == "delay"]
    if delays != [200, 184] or inserted != {0: 92}:
        raise AssertionError(f"all-idle scale 2: delays {delays}, inserted {inserted}")

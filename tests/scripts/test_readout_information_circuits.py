"""Check logical preparation and full-register measurement for the candidate."""

import json

import pytest
import readout_actor_schedule_replay as schedule_replay
import readout_information_circuits as circuit_module
from qiskit import transpile
from qiskit.circuit import Delay, Measure, Parameter
from qiskit.circuit.library import XGate
from qiskit.quantum_info import Statevector
from qiskit.transpiler import InstructionProperties, Target
from readout_information_circuits import alternatives


def test_all_input_strata_and_spectator_contexts_have_correct_ideal_states() -> None:
    circuits = alternatives(4, (0, 2))
    if set(circuits) != {(context, value) for context in ("sparse", "dense") for value in range(4)}:
        raise AssertionError("the catalogue must contain both contexts and all four input strata")
    for (context, input_bits), circuit in circuits.items():
        expected = ((input_bits & 1) << 0) | (((input_bits >> 1) & 1) << 2)
        if context == "dense":
            expected |= (1 << 1) | (1 << 3)
        probabilities = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        ).probabilities_dict()
        if probabilities != {f"{expected:04b}": 1.0}:
            raise AssertionError("logical state differs from the target and spectator preparation")
        measurement_map = [
            (circuit.find_bit(item.qubits[0]).index, circuit.find_bit(item.clbits[0]).index)
            for item in circuit.data
            if item.operation.name == "measure"
        ]
        if measurement_map != [(index, index) for index in range(4)]:
            raise AssertionError("each physical-position label must map to the same classical bit")


def test_large_register_catalogue_keeps_the_same_measured_width() -> None:
    circuits = alternatives(156, (3, 81))
    for (context, input_bits), circuit in circuits.items():
        expected_spectator_flips = 154 if context == "dense" else 0
        if circuit.num_qubits != 156 or circuit.num_clbits != 156:
            raise AssertionError("large logical register changed width")
        if circuit.count_ops().get("measure") != 156:
            raise AssertionError("both contexts must measure the full register")
        if circuit.count_ops().get("x", 0) != expected_spectator_flips + input_bits.bit_count():
            raise AssertionError("target or spectator preparation count differs")


@pytest.mark.parametrize("width, targets", [(True, (0, 1)), (2, (0, 0)), (2, (0, 2)), (2, (False, 1))])
def test_invalid_register_and_target_pairs_refuse(width: int, targets: tuple[int, int]) -> None:
    with pytest.raises(ValueError):
        alternatives(width, targets)


def test_actor_catalogue_changes_only_selected_actor_preparations() -> None:
    circuits = circuit_module.actor_alternatives(5, (0, 2), (1, 4))
    if set(circuits) != {(arm, value) for arm in ("idle", "active") for value in range(4)}:
        raise AssertionError("the actor catalogue must include each input in both arms")
    for (arm, input_bits), circuit in circuits.items():
        expected = (input_bits & 1) | (((input_bits >> 1) & 1) << 2)
        if arm == "active":
            expected |= (1 << 1) | (1 << 4)
        probabilities = Statevector.from_instruction(
            circuit.remove_final_measurements(inplace=False)
        ).probabilities_dict()
        if probabilities != {f"{expected:05b}": 1.0}:
            raise AssertionError("the actor intervention or reporter preparation differs")
        measurements = [
            (circuit.find_bit(item.qubits[0]).index, circuit.find_bit(item.clbits[0]).index)
            for item in circuit.data
            if item.operation.name == "measure"
        ]
        if measurements != [(index, index) for index in range(5)]:
            raise AssertionError("all arms must retain the same full-register measurement map")


@pytest.mark.parametrize("actors", [(), (0,), (1, 1), (5,), (True,)])
def test_actor_catalogue_rejects_invalid_or_overlapping_actors(actors: tuple[int, ...]) -> None:
    with pytest.raises(ValueError):
        circuit_module.actor_alternatives(5, (0, 2), actors)


def test_padded_actor_catalogue_matches_measurement_start_with_unequal_x_durations() -> None:
    target = Target(num_qubits=3, dt=4e-9)
    target.add_instruction(
        XGate(), {(index,): InstructionProperties(duration=ticks * target.dt) for index, ticks in enumerate((8, 4, 8))}
    )
    target.add_instruction(Measure(), {(index,): InstructionProperties(duration=40e-9) for index in range(3)})
    target.add_instruction(Delay(Parameter("duration"), unit="dt"), {(index,): None for index in range(3)})
    candidates = circuit_module.padded_actor_alternatives(3, (0, 1), (2,), (8, 4, 8))
    for circuit in candidates.values():
        for method in ("asap", "alap"):
            compiled = transpile(
                circuit, target=target, initial_layout=[0, 1, 2], optimization_level=0, scheduling_method=method
            )
            starts = [
                compiled.op_start_times[index]
                for index, instruction in enumerate(compiled.data)
                if instruction.operation.name == "measure"
            ]
            if starts != [8, 8, 8]:
                raise AssertionError("every arm must align all measurement starts in this test target")


def test_padded_actor_catalogue_rejects_invalid_duration_contract() -> None:
    for durations in ((8, 4), (8, 0, 8), (8, True, 8)):
        with pytest.raises(ValueError):
            circuit_module.padded_actor_alternatives(3, (0, 1), (2,), durations)


def test_retained_kingston_snapshot_replays_all_padded_measurement_starts() -> None:
    result = schedule_replay.replay_retained_snapshot()
    if result["target_scope"] != "restricted historical snapshot: x, measure and delay":
        raise AssertionError("the replay must identify its restricted hardware evidence")
    rows = result["schedules"]
    if not isinstance(rows, list) or len(rows) != 32:
        raise AssertionError("the replay must report padded and unpadded arms under both scheduling methods")
    if any(row["measurement_start_ticks"] != [8] or row["measurement_count"] != 156 for row in rows if row["padded"]):
        raise AssertionError("the retained snapshot must align every padded measurement at tick 8")
    if any(
        row["measurement_start_ticks"] != [0]
        for row in rows
        if not row["padded"] and row["arm"] == "idle" and row["input"] == 0
    ):
        raise AssertionError("the replay must detect the unpadded idle-ground timing discrepancy")
    if any(
        row["measurement_start_ticks"] != [8]
        for row in rows
        if not row["padded"] and (row["arm"] != "idle" or row["input"] != 0)
    ):
        raise AssertionError("the other unpadded arms must start measurement at tick 8")
    for row in rows:
        expected_x = [bit for bit in (0, 1) if row["input"] & (1 << bit)]
        if row["arm"] == "active":
            expected_x.append(2)
        if row["compiled_x_qubits"] != expected_x:
            raise AssertionError("compiled X operations must preserve reporter and actor preparation")


def test_historical_schedule_replay_rejects_missing_x_locus() -> None:
    snapshot = json.loads(schedule_replay.SNAPSHOT.read_bytes())["backends"]["ibm_kingston"]
    snapshot["instructions"]["x"]["qargs"].pop()
    with pytest.raises(ValueError):
        schedule_replay._scheduled_row((snapshot, True, "asap", "idle", 0))

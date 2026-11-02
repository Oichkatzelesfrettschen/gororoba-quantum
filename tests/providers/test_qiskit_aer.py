"""Qiskit Aer simulation and noise behavior in the configurations the repository's simulators use."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay
from qiskit.quantum_info import SuperOp
from qiskit.transpiler import PassManager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    RelaxationNoisePass,
    depolarizing_error,
    pauli_error,
    thermal_relaxation_error,
)
from qiskit_aer.utils import insert_noise
from qiskit_ibm_runtime.fake_provider import FakeManilaV2


def density_simulator(noise_model: NoiseModel | None = None) -> AerSimulator:
    return AerSimulator(
        method="density_matrix",
        device="CPU",
        precision="double",
        max_parallel_threads=1,
        max_parallel_experiments=1,
        max_parallel_shots=1,
        shot_branching_enable=False,
        noise_model=noise_model,
    )


def final_density(circuit: QuantumCircuit, noise_model: NoiseModel | None = None) -> np.ndarray:
    saved = circuit.copy()
    saved.save_density_matrix()
    simulator = density_simulator(noise_model)
    result = simulator.run(transpile(saved, simulator, optimization_level=0), shots=1).result()
    return np.asarray(result.data(0)["density_matrix"])


def test_statevector_counts_stay_on_the_bell_support() -> None:
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()
    counts = AerSimulator(method="statevector").run(circuit, shots=200).result().get_counts()
    if set(counts) - {"00", "11"} or sum(counts.values()) != 200:
        raise AssertionError(counts)


def test_certain_bit_flip_and_full_depolarization_give_exact_states() -> None:
    flip = NoiseModel()
    flip.add_all_qubit_quantum_error(pauli_error([("X", 1.0)]), ["id"])
    circuit = QuantumCircuit(1)
    circuit.id(0)
    if not np.allclose(final_density(circuit, flip), np.diag([0, 1])):
        raise AssertionError("a certain X error must map |0> to |1>")
    mixed = NoiseModel()
    mixed.add_all_qubit_quantum_error(depolarizing_error(1.0, 1), ["id"])
    if not np.allclose(final_density(circuit, mixed), np.eye(2) / 2):
        raise AssertionError("the fully depolarizing channel must give the maximally mixed state")


def test_relaxation_pass_channels_equal_thermal_relaxation_over_each_delay() -> None:
    circuit = QuantumCircuit(2)
    circuit.append(Delay(1000, "dt"), [0])
    circuit.append(Delay(400, "dt"), [1])
    noisy = PassManager(
        RelaxationNoisePass(
            t1s=[50e-6, 60e-6], t2s=[70e-6, 80e-6], dt=1e-9, op_types=[Delay], excited_state_populations=[0.0, 0.1]
        )
    ).run(circuit)
    expected = {
        0: thermal_relaxation_error(50e-6, 70e-6, 1e-6),
        1: thermal_relaxation_error(60e-6, 80e-6, 4e-7, excited_state_population=0.1),
    }
    channels = {
        noisy.find_bit(instruction.qubits[0]).index: instruction.operation
        for instruction in noisy.data
        if instruction.operation.name == "quantum_channel"
    }
    if set(channels) != {0, 1}:
        raise AssertionError(f"channels on wires {sorted(channels)}")
    for wire, channel in channels.items():
        if not np.allclose(SuperOp(channel).data, SuperOp(expected[wire]).data):
            raise AssertionError(f"wire {wire}: the pass channel differs from thermal_relaxation_error")


def test_noise_model_from_a_fake_backend_and_readout_error() -> None:
    backend = FakeManilaV2()
    model = NoiseModel.from_backend(backend)
    if not model.noise_qubits or "measure" not in model.noise_instructions:
        raise AssertionError(model)
    if "errors" not in model.to_dict():
        raise AssertionError("to_dict lost the error list")
    readout = NoiseModel()
    readout.add_all_qubit_readout_error(ReadoutError([[0.0, 1.0], [1.0, 0.0]]))
    circuit = QuantumCircuit(1, 1)
    circuit.measure(0, 0)
    counts = AerSimulator(noise_model=readout).run(circuit, shots=50).result().get_counts()
    if counts != {"1": 50}:
        raise AssertionError(f"a certain readout flip must report 1 every shot: {counts}")


def test_insert_noise_attaches_the_channel_to_each_gate() -> None:
    model = NoiseModel()
    model.add_all_qubit_quantum_error(pauli_error([("X", 0.25), ("I", 0.75)]), ["x"])
    circuit = QuantumCircuit(1)
    circuit.x(0)
    noisy = insert_noise(circuit, model)
    if [instruction.operation.name for instruction in noisy.data] != ["x", "quantum_channel"]:
        raise AssertionError([instruction.operation.name for instruction in noisy.data])
    if not np.allclose(final_density(circuit, model), np.diag([0.25, 0.75])):
        raise AssertionError("a quarter X error after X must leave a quarter of the population in |0>")

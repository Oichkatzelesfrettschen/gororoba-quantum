"""Exact noisy outcome laws of compiled circuits under a retained calibration snapshot.

calibration_snapshot.noise_simulator rebuilds live_run's noise for the whole
device, so Aer carries every qubit of a compiled circuit. live_run's noise is
local: each gate error and relaxation channel reads only its own qubits'
entries, and the readout channel is per qubit. ``restrict`` keeps the
snapshot entries of the qubits a compiled circuit touches, renumbered in
ascending physical order, and ``outcome_law`` simulates the circuit on that
register:

1. every instruction is moved onto the restricted register, and a
   ``replace`` callback may substitute a labeled marker (for example a
   noise-free Hamiltonian unitary in place of a barrier);
2. Aer's density matrix gives the probabilities of the measured qubits just
   before their final measurements;
3. the snapshot's per-qubit assignment channel
   [[1 - e10, e01], [e10, 1 - e01]] maps them to the law over classical bits.

Step 3 equals sampling the measurements because live_run's model attaches no
quantum error to measure; ``outcome_law`` refuses a noise model that does,
and a circuit with an operation after a measurement on the same qubit.
The law is indexed by the classical-register value, clbit 0 least significant.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction

import calibration_snapshot

# replace(operation, physical_qubits) returns the instruction to apply in its
# place on the same qubits, None to drop it, or the operation itself to keep it.
Replace = Callable[[Instruction, list[int]], Instruction | None]


def restrict(snapshot: dict[str, Any], qubits: list[int]) -> dict[str, Any]:
    """The snapshot restricted to ``qubits``, renumbered qubits[k] -> k."""
    index = {q: k for k, q in enumerate(qubits)}
    instructions = {
        op: [dict(row, qargs=[index[q] for q in row["qargs"]]) for row in rows if all(q in index for q in row["qargs"])]
        for op, rows in snapshot["instructions"].items()
    }
    return dict(
        snapshot, num_qubits=len(qubits), qubits=[snapshot["qubits"][q] for q in qubits], instructions=instructions
    )


def active_qubits(compiled: QuantumCircuit) -> list[int]:
    """Physical qubits that any non-barrier instruction touches, ascending."""
    return sorted(
        {
            compiled.find_bit(q).index
            for instruction in compiled.data
            if instruction.operation.name != "barrier"
            for q in instruction.qubits
        }
    )


def restrict_circuit(compiled: QuantumCircuit) -> tuple[QuantumCircuit, list[int]]:
    """compiled with its idle wires removed, on the active qubits in ascending physical order.

    The remaining wires keep their order, so qubit k of the result is
    active_qubits(compiled)[k], the numbering ``restrict`` gives the snapshot;
    classical bits and control-flow blocks are unchanged. Aer then carries a
    noise model of the active qubits only, which samples the same law.
    """
    from qiskit.converters import circuit_to_dag, dag_to_circuit

    qubits = active_qubits(compiled)
    keep = set(qubits)
    dag = circuit_to_dag(compiled)
    dag.remove_qubits(*[wire for wire in dag.qubits if compiled.find_bit(wire).index not in keep])
    return dag_to_circuit(dag), qubits


def _keep(operation: Instruction, qubits: list[int]) -> Instruction | None:
    return None if operation.name == "barrier" else operation


def outcome_law(
    snapshot: dict[str, Any],
    compiled: QuantumCircuit,
    device: str = "CPU",
    replace: Replace = _keep,
    noisy: bool = True,
) -> np.ndarray:
    """Law over the classical register of a circuit compiled to the snapshot's Target.

    ``noisy=False`` drops gate, idle and assignment noise, which checks the
    register move against a statevector law.
    """
    qubits = active_qubits(compiled)
    index = {q: k for k, q in enumerate(qubits)}
    reduced = restrict(snapshot, qubits)
    body = QuantumCircuit(len(qubits))
    measured: dict[int, int] = {}
    for instruction in compiled.data:
        operation = instruction.operation
        physical = [compiled.find_bit(q).index for q in instruction.qubits]
        if any(q in measured for q in physical):
            raise ValueError(f"{operation.name} on {physical} follows a measurement")
        if operation.name == "measure":
            measured[physical[0]] = compiled.find_bit(instruction.clbits[0]).index
            continue
        substitute = replace(operation, physical)
        if substitute is not None:
            body.append(substitute, [index[q] for q in physical])
    order = sorted(measured, key=measured.__getitem__)
    if [measured[q] for q in order] != list(range(compiled.num_clbits)):
        raise ValueError(f"clbits {sorted(measured.values())} are not each measured once")
    body.save_probabilities([index[q] for q in order], label="p")
    if noisy:
        _, noise = calibration_snapshot.noise_model(reduced)
        if noise._local_quantum_errors.get("measure"):
            raise ValueError("the noise model attaches a quantum error to measure")
        simulator = calibration_snapshot.noise_simulator(reduced, device)
    else:
        from qiskit_aer import AerSimulator

        simulator = AerSimulator(method="density_matrix", device=device)
    probabilities = np.asarray(simulator.run(body).result().data(0)["p"], dtype=float)
    if not noisy:
        return probabilities
    channel = np.ones((1, 1))
    for q in order:
        e10, e01 = snapshot["qubits"][q]["e10"], snapshot["qubits"][q]["e01"]
        channel = np.kron(np.array([[1.0 - e10, e01], [e10, 1.0 - e01]]), channel)
    law = channel @ probabilities
    return np.clip(law, 0.0, None) / law.sum()


def self_check(snapshot_path: str) -> str:
    """A routed three-qubit circuit: the restricted noiseless law equals its statevector law,
    and the restricted noisy law equals the whole-device simulation's exact law."""
    from qiskit import transpile
    from qiskit.quantum_info import Statevector

    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    view = calibration_snapshot.snapshot_backend(snapshot)
    device = calibration_snapshot.aer_device()
    circuit = QuantumCircuit(3, 3)
    circuit.h(0)
    circuit.cx(0, 2)
    circuit.ry(0.7, 1)
    circuit.cx(1, 2)
    circuit.delay(800, 1, unit="dt")
    circuit.measure([0, 1, 2], [2, 0, 1])
    compiled = transpile(circuit, view, optimization_level=1, seed_transpiler=7)
    ideal = Statevector(circuit.remove_final_measurements(inplace=False)).probabilities([1, 2, 0])
    law = outcome_law(snapshot, compiled, device, noisy=False)
    if not np.allclose(law, ideal, atol=1e-10):
        raise SystemExit(f"restricted noiseless law {law} differs from the statevector law {ideal}")
    full = calibration_snapshot.noise_simulator(snapshot, device)
    probe = compiled.remove_final_measurements(inplace=False)
    physical = compiled.layout.final_index_layout()[:3]
    probe.save_probabilities(physical, label="p")
    whole = np.asarray(full.run(probe).result().data(0)["p"], dtype=float)
    restricted = outcome_law(snapshot, compiled, device, noisy=True)
    channel = np.ones((1, 1))
    for q in physical:
        e10, e01 = snapshot["qubits"][q]["e10"], snapshot["qubits"][q]["e01"]
        channel = np.kron(np.array([[1.0 - e10, e01], [e10, 1.0 - e01]]), channel)
    clbit_of_logical = [2, 0, 1]
    whole_law = np.zeros(8)
    for outcome, value in enumerate(channel @ whole):
        bits = [(outcome >> k) & 1 for k in range(3)]
        whole_law[sum(bits[k] << clbit_of_logical[k] for k in range(3))] += value
    if not np.allclose(restricted, whole_law, atol=1e-10):
        raise SystemExit(f"restricted noisy law {restricted} differs from the whole-device law {whole_law}")
    active = len(active_qubits(compiled))
    return f"snapshot laws: {active} active qubits; restricted laws equal statevector and whole-device laws"


if __name__ == "__main__":
    import sys

    print(
        self_check(
            sys.argv[1]
            if len(sys.argv) > 1
            else str(Path(__file__).resolve().parent.parent / "docs/evidence/calibration/ibm_kingston.json")
        )
    )

> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e754f0ed062fd08b796a3199ad648692924895f7497c08efe64a54cacb93c272.

# circuit_operations

Full path: iqm.pulse.circuit_operations

Representing quantum circuits as lists of CircuitOperations.

Functions

|  |  |
|----|----|
| [`get_unitary_from_circuit`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_circuit.html#iqm.pulse.circuit_operations.get_unitary_from_circuit "iqm.pulse.circuit_operations.get_unitary_from_circuit")(circuit\[, table, ...\]) | Calculate the overall unitary implemented by a sequence of CircuitOperations. |
| [`get_unitary_from_op`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_op.html#iqm.pulse.circuit_operations.get_unitary_from_op "iqm.pulse.circuit_operations.get_unitary_from_op")(op, table, qubits) | Unitary matrix representing an operation within the context of the circuit. |
| [`reorder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reorder.html#iqm.pulse.circuit_operations.reorder "iqm.pulse.circuit_operations.reorder")(A, perm) | Permutes the order of the qubits in an n-qubit operator matrix. |
| [`reshape_unitary`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.reshape_unitary.html#iqm.pulse.circuit_operations.reshape_unitary "iqm.pulse.circuit_operations.reshape_unitary")(unitary, indices, n_qubits) | Extend a unitary propagator to act on a larger system. |

Classes

|  |  |
|----|----|
| [`Circuit`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "iqm.pulse.circuit_operations.Circuit") | Quantum circuit. |
| [`CircuitOperationList`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.CircuitOperationList.html#iqm.pulse.circuit_operations.CircuitOperationList "iqm.pulse.circuit_operations.CircuitOperationList") | List of [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") objects representing a quantum circuit. |

Inheritance

![Inheritance diagram of iqm.pulse.circuit_operations](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-196a8e21d516c0030cc19844bba7c7754490aeb6.png)

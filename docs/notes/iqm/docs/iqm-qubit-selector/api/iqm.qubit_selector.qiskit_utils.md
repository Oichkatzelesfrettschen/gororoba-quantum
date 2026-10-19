> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b68ee60a0c93cfa8156aee95e031244165a2a7fe67df2f26ad363a49e891c3b2.

# qiskit_utils

Full path: iqm.qubit_selector.qiskit_utils

Utility functions for working with Qiskit circuits.

Functions

|  |  |
|----|----|
| [`active_bits`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.active_bits.html#iqm.qubit_selector.qiskit_utils.active_bits "iqm.qubit_selector.qiskit_utils.active_bits")(input_circ) | Find active bits (quantum and classical) in a transpiled circuit. |
| [`deflate_circuit`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.deflate_circuit.html#iqm.qubit_selector.qiskit_utils.deflate_circuit "iqm.qubit_selector.qiskit_utils.deflate_circuit")(input_circ) | Reduce a transpiled circuit down to only active qubits. |
| [`extract_2q_interactions`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.extract_2q_interactions.html#iqm.qubit_selector.qiskit_utils.extract_2q_interactions "iqm.qubit_selector.qiskit_utils.extract_2q_interactions")(circuit) | Extract 2-qubit interactions excluding directives and single-qubit ops. |
| [`get_circuit`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.get_circuit.html#iqm.qubit_selector.qiskit_utils.get_circuit "iqm.qubit_selector.qiskit_utils.get_circuit")(circuit_type, num_qubits) | Create a quantum circuit of a given type. |
| [`perform_backend_transpilation`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.perform_backend_transpilation.html#iqm.qubit_selector.qiskit_utils.perform_backend_transpilation "iqm.qubit_selector.qiskit_utils.perform_backend_transpilation")(qc_list, ...) | Transpile a list of circuits to backend specifications. |
| [`reduce_to_active_qubits`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits.html#iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits "iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits")(circuit\[, ...\]) | Reduces a quantum circuit to only its active qubits. |

Classes

|  |  |
|----|----|
| [`CircuitType`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.CircuitType.html#iqm.qubit_selector.qiskit_utils.CircuitType "iqm.qubit_selector.qiskit_utils.CircuitType") | Defines quantum circuit types supported by `qubit_selector`. |

Inheritance

![Inheritance diagram of iqm.qubit_selector.qiskit_utils](https://docs.iqm.tech/4.7/iqm-qubit-selector/_images/inheritance-5c166c8172dd1666d5e5750c8d1ff6f2c7575afa.png)

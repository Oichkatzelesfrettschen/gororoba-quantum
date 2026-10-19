> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.get_circuit.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.get_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 499e8304c0beecf17b01d09677f56ab4246ef6be99c05256c234627c054d89f7.

# iqm.qubit_selector.qiskit_utils.get_circuit

iqm.qubit_selector.qiskit_utils.get_circuit(*circuit_type*, *num_qubits*)  
Create a quantum circuit of a given type.

Parameters:  
- **circuit_type** ([*CircuitType*](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.CircuitType.html#iqm.qubit_selector.qiskit_utils.CircuitType "iqm.qubit_selector.qiskit_utils.CircuitType")) – Type of the circuit to create.

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits.

Returns:  
Quantum circuit of a given type.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the requested circuit type is not supported.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a293d3fb1f381994ae1806ba8166d2ad670106f0dedc95530d9e72808039a96e.

# iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits

iqm.qubit_selector.qiskit_utils.reduce_to_active_qubits(*circuit*, *backend_topology=None*, *backend_num_qubits=None*)  
Reduces a quantum circuit to only its active qubits.

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The original quantum circuit.

- **backend_topology** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The backend topology to execute the benchmark on.

- **backend_num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of qubits in the backend.

Returns:  
A new quantum circuit containing only active qubits.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

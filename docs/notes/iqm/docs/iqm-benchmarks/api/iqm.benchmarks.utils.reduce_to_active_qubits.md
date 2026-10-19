> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.reduce_to_active_qubits.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.reduce_to_active_qubits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3a035c5dae57f34699f14dfd57793c4346699340fc63c3a6ebce86cd22fc9074.

# iqm.benchmarks.utils.reduce_to_active_qubits

iqm.benchmarks.utils.reduce_to_active_qubits(*circuit: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*, *backend_topology: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *backend_num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Reduces a quantum circuit to only its active qubits.

Parameters:  
- **backend_topology** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The backend topology to execute the benchmark on.

- **circuit** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – The original quantum circuit.

- **backend_num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of qubits in the backend.

Returns:  
A new quantum circuit containing only active qubits.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")

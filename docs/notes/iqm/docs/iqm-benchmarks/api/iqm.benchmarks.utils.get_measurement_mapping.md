> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_measurement_mapping.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_measurement_mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec6d72df5424827633dfd34ef466d179ba34ae22d4d770286022e1dbea1a8acd.

# iqm.benchmarks.utils.get_measurement_mapping

iqm.benchmarks.utils.get_measurement_mapping(*circuit: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Extracts the final measurement mapping (qubits to bits) of a quantum circuit.

Parameters:  
**circuit** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – The quantum circuit to extract the measurement mapping from.

Returns:  
A dictionary where keys are qubits and values are classical bits.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

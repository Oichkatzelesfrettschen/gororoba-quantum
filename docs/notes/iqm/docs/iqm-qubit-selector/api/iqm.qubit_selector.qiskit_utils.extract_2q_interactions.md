> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.extract_2q_interactions.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.extract_2q_interactions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cd7dcf1b591f5a21690e0a880799a4ad7865f0ecbe962dcb273e41caafe549a4.

# iqm.qubit_selector.qiskit_utils.extract_2q_interactions

iqm.qubit_selector.qiskit_utils.extract_2q_interactions(*circuit*)  
Extract 2-qubit interactions excluding directives and single-qubit ops.

Parameters:  
**circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The quantum circuit from which to extract 2-qubit interactions.

Returns:  
Interactions as a list of tuples, each containing the indices of two qubits that interact.  
The qubit indices are returned in a consistent order (min, max).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

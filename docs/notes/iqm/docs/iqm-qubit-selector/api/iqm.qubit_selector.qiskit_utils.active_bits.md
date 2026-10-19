> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.active_bits.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.active_bits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 38796f9dbeda33996bfe92d63cae09d870a0e1a81d68a2ea89efcfc5c5ab2bdb.

# iqm.qubit_selector.qiskit_utils.active_bits

iqm.qubit_selector.qiskit_utils.active_bits(*input_circ*)  
Find active bits (quantum and classical) in a transpiled circuit.

Parameters:  
**input_circ** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – Input circuit.

Returns:  
A tuple containing two sets - one with active qubits and one with active classical bits.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

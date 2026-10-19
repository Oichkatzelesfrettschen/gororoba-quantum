> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_graph_state.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_graph_state.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2a5c61b1d64d5cff07426504fbdce39f78812ad28015d336ef8138b2da62060e.

# iqm.benchmarks.entanglement.graph_states.generate_graph_state

iqm.benchmarks.entanglement.graph_states.generate_graph_state(*qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → QuantumCircuit  
Generates a circuit with minimal depth preparing a native graph state for a given backend using given qubits.

Parameters:  
- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers representing the qubits.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to target the graph state generating circuit.

Returns:  
The circuit generating a graph state in the target backend.

Return type:  
*QuantumCircuit*

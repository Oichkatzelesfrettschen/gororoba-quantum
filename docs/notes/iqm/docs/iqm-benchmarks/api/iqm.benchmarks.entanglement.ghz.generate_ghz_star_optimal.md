> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c647e1074fc6d8909166d217e91ef8527b764d3cc6ab53fd4cfa801f5117ee5f.

# iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal

iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal(*qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")*, *inv: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generates the circuit for creating a GHZ state by maximizing the number of CZ gates between a pair of MOVE gates.

Parameters:  
- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The layout of qubits for the GHZ state.

- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")) – The backend to be used for the quantum circuit.

- **inv** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to generate the inverse circuit.

Returns:  
A quantum circuit generating a GHZ state on a given number of qubits.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")

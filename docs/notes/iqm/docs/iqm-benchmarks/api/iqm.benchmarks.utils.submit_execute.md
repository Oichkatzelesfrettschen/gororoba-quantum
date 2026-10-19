> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.submit_execute.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.submit_execute.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 10ade2db444656efb0f92ba74ea1a66d2e89b9091dbc126c66bb664fcd049f33.

# iqm.benchmarks.utils.submit_execute

iqm.benchmarks.utils.submit_execute(*sorted_transpiled_qc_list: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *max_gates_per_batch: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *max_circuits_per_batch: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *circuit_compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "(in IQM client v36.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[JobV1\]  
Submit function to execute lists of quantum circuits on the specified backend.

> Organized as a dictionary with keys being identifiers of a batch (normally qubits) and values corresponding lists of quantum circuits. The result is returned as a single list of IQMJob objects.

Parameters:  
- **sorted_transpiled_qc_list** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary of lists of quantum circuits to be executed. \* The keys (Tuple\[int\] \| str) should correspond to final measured qubits. \* The values (List\[QuantumCircuit\]) should be the corresponding list (batch) of quantum circuits.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – the backend to execute the circuits on.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the number of shots per circuit.

- **max_gates_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – the maximum number of gates per batch sent to the backend, used to make manageable batches.

- **max_circuits_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – the maximum number of circuits per batch sent to the backend, used to make manageable batches.

- **circuit_compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "(in IQM client v36.0.0)") *\|* *None*) – Ability to pass a compilation options object, enabling execution with dynamical decoupling, among other options - see qiskit-iqm documentation.

Returns:  
A list of IQMJob objects corresponding to the submitted circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*JobV1*\]

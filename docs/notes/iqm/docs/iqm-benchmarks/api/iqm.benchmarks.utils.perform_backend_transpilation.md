> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.perform_backend_transpilation.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.perform_backend_transpilation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 778488a5435d3503d0d9e7f6aed0bf63bbf0671bbf8fc5ee37a367584d32607b.

# iqm.benchmarks.utils.perform_backend_transpilation

iqm.benchmarks.utils.perform_backend_transpilation(*qc_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *coupling_map: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *basis_gates: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] = ('r', 'cz')*, *qiskit_optim_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 1*, *optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*, *routing_method: [RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = RoutingMethod.SABRE*, *approximation_degree: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 1.0*, *initial_layout: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]  
Transpile a list of circuits to backend specifications.

Parameters:  
- **qc_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]*) – The original (untranspiled) list of quantum circuits.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to execute the benchmark on.

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The qubits to target in the transpilation.

- **coupling_map** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The target coupling map to transpile to.

- **basis_gates** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The basis gates.

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Qiskit “optimization_level” value.

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether SQG optimization is performed taking into account virtual Z.

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether the SQG optimizer drops a final RZ gate.

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") *\|* *None*) – The routing method employed by Qiskit’s transpilation pass.

- **approximation_degree** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – How much the transpiler is allowed to approximate the original circuit in terms of lower gate counts and depth. 1.0 means no deviation allowed, 0.0 means maximum deviation allowed.

- **initial_layout** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Where to place the circuit’s logical qubits, as indices into coupling_map, so the transpiler does not have to search for a layout. With a reduced (fixed-layout) coupling map its node `j` is `qubits[j]`, so a caller that knows which physical qubit each logical qubit belongs on passes those positions within qubits. If None, the identity layout is used when the circuit’s 2-qubit gates are already couplings, and otherwise the transpiler searches as before.

Returns:  
A list of transpiled quantum circuits.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – if Star topology and label 0 is in qubit layout.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.perform_backend_transpilation.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qiskit_utils.perform_backend_transpilation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 104610fe87ed804946b77653ab64d14d26204f2671eeaf80f029743bd2a0efd6.

# iqm.qubit_selector.qiskit_utils.perform_backend_transpilation

iqm.qubit_selector.qiskit_utils.perform_backend_transpilation(*qc_list*, *backend*, *qubits*, *coupling_map*, *basis_gates=('r', 'cz')*, *qiskit_optim_level=1*, *optimize_sqg=True*, *routing_method='sabre'*)  
Transpile a list of circuits to backend specifications.

Parameters:  
- **qc_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*\]*) – The original (untranspiled) list of quantum circuits.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to execute the benchmark on.

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The qubits to target in the transpilation.

- **coupling_map** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The target coupling map to transpile to.

- **basis_gates** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The basis gates.

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Qiskit `optimization_level` value.

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether SQG optimization is performed taking into account virtual Z.

- **routing_method** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The routing method employed by Qiskit’s transpilation pass.

Returns:  
A list of transpiled quantum circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")\]

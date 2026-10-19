> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit_validation.validate_circuit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit_validation.validate_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 64715f448618034c01ef8babb64279c766333dd25f283213d0e25f1e154539ec.

# iqm.qiskit_iqm.iqm_circuit_validation.validate_circuit

iqm.qiskit_iqm.iqm_circuit_validation.validate_circuit(*circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase")*, *validate_moves: MoveGateValidationMode \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *qubit_index_to_name: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate a circuit against the backend.

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)"))

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "iqm.qiskit_iqm.iqm_backend.IQMBackendBase"))

- **validate_moves** (*MoveGateValidationMode* *\|* *None*)

- **qubit_index_to_name** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

Return type:  
None

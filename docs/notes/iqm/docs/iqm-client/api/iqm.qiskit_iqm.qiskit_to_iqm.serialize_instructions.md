> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7e90e345b28b717b4254b22c94e03a17056eeb7ac57167d866a07873e45f971d.

# iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions

iqm.qiskit_iqm.qiskit_to_iqm.serialize_instructions(*circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *qubit_index_to_name: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *allowed_nonnative_gates: [Collection](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] = ()*, *\**, *clbit_to_measure: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[Clbit](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Clbit "(in Qiskit v2.5)"), [CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")\]  
Serialize a quantum circuit into the IQM data transfer format.

This is IQM’s internal helper for [`IQMBackend.serialize_circuit()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit "iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit") that gives slightly more control. See [`IQMBackend.serialize_circuit()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit "iqm.qiskit_iqm.iqm_provider.IQMBackend.serialize_circuit") for details.

The position of a qubit in `circuit` is used as its physical qubit index, which is what Qiskit’s transpiler produces.

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – quantum circuit to serialize

- **qubit_index_to_name** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Mapping from qubit indices to the corresponding qubit names.

- **allowed_nonnative_gates** ([*Collection*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Collection "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Names of gates that are converted as-is without validation. By default, any gate that can’t be converted will raise an error. If such gates are present in the circuit, the caller must edit the result to be valid and executable. Notably, since IQM transfer format requires named parameters and qiskit parameters don’t have names, the i th parameter of an unrecognized instruction is given the name `"p<i>"`.

- **clbit_to_measure** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Clbit*](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Clbit "(in Qiskit v2.5)")*,* [*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*\]* *\|* *None*) – Maps clbits to the latest “measure” instruction to store its result there, or None if nothing has been measured yet.

Returns:  
list of IQM instructions representing the circuit

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – circuit contains an unsupported instruction or is not transpiled in general

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")\]

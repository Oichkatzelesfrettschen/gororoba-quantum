> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 60ca5a43a41139c8bac076c04d16da5ff8e567d1bb6f3c43297d1d263461c472.

# iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions

iqm.qiskit_iqm.qiskit_to_iqm.deserialize_instructions(*instructions: [Iterable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")\]*, *qubit_name_to_index: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *layout: [Layout](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")  
Turn a list of IQM Instructions into a Qiskit QuantumCircuit.

Parameters:  
- **instructions** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*\]*) – The gates in the circuit.

- **qubit_name_to_index** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Mapping from qubit names to their indices, as specified in a backend.

- **layout** ([*Layout*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)") *\|* *None*) – Qiskit representation of a layout for the circuit. The returned Qiskit circuit inherits its QuantumRegisters and Qubits from `layout`. It tells which Qubit object in the circuit matches which physical qubit index. If None, return a QuantumCircuit with just one register called “q”.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Thrown when a given instruction is not supported.

Returns:  
Qiskit circuit represented by the given instructions.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

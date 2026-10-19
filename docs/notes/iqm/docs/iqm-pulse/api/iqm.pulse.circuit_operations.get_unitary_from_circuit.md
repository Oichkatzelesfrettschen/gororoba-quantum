> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_circuit.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 be6746a5b1382c18641d1a94b1a740a776aa63da931b1c13f6b5694557e7ac34.

# iqm.pulse.circuit_operations.get_unitary_from_circuit

iqm.pulse.circuit_operations.get_unitary_from_circuit(*circuit*, *table=None*, *qubit_names=None*)  
Calculate the overall unitary implemented by a sequence of CircuitOperations.

Iterate through the list of operations, skipping over barrier operations, and calculate the unitary for each operation, and then calculate the matrix product of all of them. The unitary definition must be present in the QuantumOpTable given as the second argument.

Parameters:  
- **circuit** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – list of CircuitOperations in order

- **table** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]* *\|* *None*) – Table of all registered quantum ops.

- **qubit_names** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Optionally, the ordering of the qubits.

Returns:  
Array describing the action of the circuit in big endian convention.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

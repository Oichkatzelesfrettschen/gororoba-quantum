> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_op.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.get_unitary_from_op.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ce9c5b62158ff6e93ddf66bee749da929fab689143480d28297bd242e2acf633.

# iqm.pulse.circuit_operations.get_unitary_from_op

iqm.pulse.circuit_operations.get_unitary_from_op(*op*, *table*, *qubits*)  
Unitary matrix representing an operation within the context of the circuit.

First, fetches the unitary corresponding to the correct operation from the QuantumOpTable. If that unitary is a function, gets the matrix by calling the function with values of quantum operation params stored in the operation. Checks whether the size of the unitary is correct. Then, optionally extends that unitary to act on the Hilbert space of the entire circuit.

Parameters:  
- **op** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")) – quantum operation instance

- **table** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – registered quantum operations

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – qubits of the whole circuit, in big-endian order

Returns:  
Unitary matrix representing `op` on the Hilbert space of the circuit.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

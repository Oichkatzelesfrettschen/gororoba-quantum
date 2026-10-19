> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.positions_to_pauli_string.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.positions_to_pauli_string.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b09a7212af6dbd1c673aad3440b83223fcbd706ec498d97c62dcc6dafd371d9f.

# positions_to_pauli_string

iqm.qaoa.transforming_functions.positions_to_pauli_string(*positions*, *num_qubits*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transforming_functions.py#L116-L141)  
Create a string with the character “Z” on the specified positions and the character “I” elsewhere.

The string is intended to be used to construct a [`PauliList`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.PauliList "(in Qiskit v2.5)") and from it a [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)").

Parameters:  
- **positions** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Set of qubit indices where “Z” should be.

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total number of qubits in the system (i.e., the length of the string).

Returns:  
The Pauli string.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If any of the qubit indices is negative or too large (more than `num_qubits-1`).

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

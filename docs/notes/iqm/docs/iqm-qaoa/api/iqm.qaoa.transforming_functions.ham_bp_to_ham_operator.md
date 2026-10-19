> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bp_to_ham_operator.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bp_to_ham_operator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a9f0d6fb2d709a812bf058b1e81358a2a7022ef838cb7c412cf7b4f44b3e67de.

# ham_bp_to_ham_operator

iqm.qaoa.transforming_functions.ham_bp_to_ham_operator(*ham_bp*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transforming_functions.py#L74-L113)  
A function to transform a Hamiltonian represented as a BP into a [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)").

A Hamiltonian as [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)") may be used by [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)") functions that e.g., calculate expectation values. The input `dimod.higherorder.BinaryPolynomial` needs to have sortable variables. This is already the case if the `ham_bp` comes from a [`HUBOInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.hubo.HUBOInstance.html#iqm.applications.hubo.HUBOInstance "iqm.applications.hubo.HUBOInstance").

Parameters:  
**ham_bp** ([*BinaryPolynomial*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.higherorder.polynomial.BinaryPolynomial "(in D-Wave Quantum Computing Products v9.5.0)")) – A `BinaryPolynomial` with `vartype=SPIN`, where each term corresponds to a product of spin variables and its coefficient represents the prefactor of the associated multi-qubit *Z…Z* Pauli operator in the problem Hamiltonian.

Returns:  
The Hamiltonian as [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)") to be used by [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)").

Raises:  
[**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the variables of the input `ham_bp` are not sortable.

Return type:  
[*SparsePauliOp*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)")

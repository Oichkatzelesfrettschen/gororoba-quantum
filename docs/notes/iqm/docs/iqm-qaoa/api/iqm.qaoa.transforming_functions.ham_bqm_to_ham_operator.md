> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2af31433426ab4215a2c13851981fb6bd0c648c2d6035a61f4fa347b4154e7ff.

# ham_bqm_to_ham_operator

iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator(*ham_bqm*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transforming_functions.py#L29-L71)  
A function to transform Hamiltonian represented as a BQM into a [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)").

A Hamiltonian as [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)") may be used by [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)") functions that e.g., calculate expectation values.

Parameters:  
**ham_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – A `BinaryQuadraticModel` with `vartype=SPIN`, i.e., the linear and quadratic terms correspond to the coefficients before the corresponding *Z* and *ZZ* operators in the problem Hamiltonian.

Returns:  
The Hamiltonian as [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)") to be used by [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)").

Return type:  
[*SparsePauliOp*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)")

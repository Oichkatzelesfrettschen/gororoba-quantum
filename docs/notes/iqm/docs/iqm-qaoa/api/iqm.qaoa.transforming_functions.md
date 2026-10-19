> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6de6d0556b1a2c3c682ed0dc17bd6788cacca226bdb724effde2cc383b9c56f7.

# transforming_functions

Full path: iqm.qaoa.transforming_functions

A module for custom functions that transform data from one format to another format.

Functions

|  |  |
|----|----|
| [`ham_bp_to_ham_operator`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bp_to_ham_operator.html#iqm.qaoa.transforming_functions.ham_bp_to_ham_operator "iqm.qaoa.transforming_functions.ham_bp_to_ham_operator")(ham_bp) | A function to transform a Hamiltonian represented as a BP into a [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)"). |
| [`ham_bqm_to_ham_operator`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator.html#iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator "iqm.qaoa.transforming_functions.ham_bqm_to_ham_operator")(ham_bqm) | A function to transform Hamiltonian represented as a BQM into a [`SparsePauliOp`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.quantum_info.SparsePauliOp "(in Qiskit v2.5)"). |
| [`positions_to_pauli_string`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transforming_functions.positions_to_pauli_string.html#iqm.qaoa.transforming_functions.positions_to_pauli_string "iqm.qaoa.transforming_functions.positions_to_pauli_string")(positions, num_qubits) | Create a string with the character "Z" on the specified positions and the character "I" elsewhere. |

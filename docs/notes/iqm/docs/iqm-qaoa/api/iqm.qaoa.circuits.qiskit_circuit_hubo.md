> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_hubo.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_hubo.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7e4618ff80096e26e985b786a04c962f9132d4f3d7de367ebc4e5e276e4751de.

# qiskit_circuit_hubo

iqm.qaoa.circuits.qiskit_circuit_hubo(*qaoa*, *measurements=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L377-L456)  
Construct a Qiskit quantum circuit implementing the QAOA ansatz for a HUBO.

This function builds a parameterized Quantum Approximate Optimization Algorithm (QAOA) circuit for a Higher-Order Unconstrained Binary Optimization (HUBO) problem encoded as a binary polynomial. The resulting circuit alternates between phase-separation and mixing layers.

The QAOA unitary for \\p\\ layers is given by

\\\begin{split}U(\\boldsymbol{\\gamma}, \\boldsymbol{\\beta}) = \\prod\_{\\ell=1}^{p} \\left( e^{-i \\beta\_\\ell \\sum\_{i} X_i} \\, e^{-i \\gamma\_\\ell H_C} \\right),\end{split}\\

where \\H_C\\ is the cost Hamiltonian derived from the HUBO:

\\\begin{split}H_C = \\sum\_{S \\subseteq \\{1, \\dots, n\\}} c_S \\prod\_{i \\in S} Z_i.\end{split}\\

Each term in the Hamiltonian is implemented using an n-qubit Pauli-Z string rotation via [`rnz()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.rnz.html#iqm.qaoa.circuits.rnz "iqm.qaoa.circuits.rnz"), i.e.,

\\\begin{split}e^{-i \\gamma c_S \\prod\_{i \\in S} Z_i}.\end{split}\\

The mixer corresponds to independent single-qubit X-rotations:

\\\begin{split}e^{-i \\beta \\sum_i X_i} = \\prod_i R_X(2\\beta).\end{split}\\

The circuit is initialized in the uniform superposition state by applying Hadamard gates to all qubits.

Parameters:  
- **qaoa** ([*HUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.hubo_qaoa.HUBOQAOA.html#iqm.qaoa.hubo_qaoa.HUBOQAOA "iqm.qaoa.hubo_qaoa.HUBOQAOA")) – QAOA instance containing the HUBO Hamiltonian, number of qubits, number of layers, and variational parameters `gammas` and `betas`.

- **measurements** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, append measurements on all qubits at the end of the circuit. Defaults to `True`.

Returns:  
A Qiskit circuit implementing the QAOA ansatz for the given HUBO.

Return type:  
QuantumCircuit

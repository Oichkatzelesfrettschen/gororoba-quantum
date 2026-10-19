> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.rnz.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.rnz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3615bf559b5def99c2bb5214d63568236d68667128b93fdd739e98aa68a9cf44.

# rnz

iqm.qaoa.circuits.rnz(*n*, *theta*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L346-L374)  
Construct an n-qubit Pauli-Z string rotation circuit.

This circuit implements the unitary

\\\begin{split}U(\\theta) = e^{-i \\frac{\\theta}{2} Z^{\\otimes n}}\end{split}\\

where \\Z^{\\otimes n}\\ denotes the tensor product of Pauli-Z operators acting on all `n` qubits.

The implementation uses a CNOT ladder to compute the parity of qubits `1` through `n-1` onto qubit `0`, applies a single-qubit \\R_Z(\\theta)\\ rotation on qubit `0`, and then uncomputes the parity.

Parameters:  
- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits in the Pauli string.

- **theta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Rotation angle \\\\theta\\.

Returns:  
A quantum circuit implementing the n-qubit Z-string rotation.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

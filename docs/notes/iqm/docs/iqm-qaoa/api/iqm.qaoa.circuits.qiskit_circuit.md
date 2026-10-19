> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 425cf85bcbf72e1ee049ca9dce6379eed5421ee4c94cd64a39afbf5d0b70161c.

# qiskit_circuit

iqm.qaoa.circuits.qiskit_circuit(*qaoa*, *measurements=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L81-L116)  
Constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") from the QAOA angles, ignoring details of the QPU.

Constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") corresponding to the QAOA, assuming perfect connectivity of the qubits and complete set of available quantum gates. This circuit can be used for simulations or it can be transpiled to be run on a real QPU.

Parameters:  
- **qaoa** ([*QUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA")) – A [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA") object whose angles and interaction strengths are used in the construction of the [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)").

- **measurements** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should measurements be added at the end of the circuit? If the circuit is used for statevector simulation, there shouldn’t be measurements. If the circuit is used for sampling, there should be measurements.

Returns:  
A quantum circuit corresponding to the QAOA, excluding any measurements.

Return type:  
QuantumCircuit

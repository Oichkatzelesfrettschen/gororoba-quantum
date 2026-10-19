> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_specific_nodes.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_specific_nodes.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 025691436e34a4cd581c5cf39f7b6d375042eafbd352e9badbc91c6b3a65b708.

# qiskit_circuit_specific_nodes

iqm.qaoa.circuits.qiskit_circuit_specific_nodes(*qaoa*, *starting_qubits*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/circuits.py#L119-L166)  
Constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") for the RCC of given qubits, ignoring details of the QPU.

The *reverse causal cone* (RCC) of a set of qubits contains all the gates and qubits which have any influence on the measurement results on the initial set of qubits. This method constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") containing these gates and extra qubits.

Parameters:  
- **qaoa** ([*QUBOQAOA*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA")) – A [`QUBOQAOA`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.qubo_qaoa.QUBOQAOA.html#iqm.qaoa.qubo_qaoa.QUBOQAOA "iqm.qaoa.qubo_qaoa.QUBOQAOA") object whose angles and interaction strengths are used in the construction of the [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)").

- **starting_qubits** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A set of the starting qubits for which we construct the RCC circuit.

Returns:  
A [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") representing the RCC.

Return type:  
QuantumCircuit

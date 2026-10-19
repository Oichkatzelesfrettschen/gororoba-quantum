> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 99eda81f815cfb4acce1ea6055ffbbd9844e9fa58dffb2265138bd8756d33543.

# circuits

Full path: iqm.qaoa.circuits

Functions that build various types of circuits (e.g., in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)") and [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)")) from the QAOA object.

Functions

|  |  |
|----|----|
| [`qiskit_circuit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit.html#iqm.qaoa.circuits.qiskit_circuit "iqm.qaoa.circuits.qiskit_circuit")(qaoa\[, measurements\]) | Constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") from the QAOA angles, ignoring details of the QPU. |
| [`qiskit_circuit_hubo`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_hubo.html#iqm.qaoa.circuits.qiskit_circuit_hubo "iqm.qaoa.circuits.qiskit_circuit_hubo")(qaoa\[, measurements\]) | Construct a Qiskit quantum circuit implementing the QAOA ansatz for a HUBO. |
| [`qiskit_circuit_specific_nodes`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.qiskit_circuit_specific_nodes.html#iqm.qaoa.circuits.qiskit_circuit_specific_nodes "iqm.qaoa.circuits.qiskit_circuit_specific_nodes")(qaoa, ...) | Constructs a [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)") for the RCC of given qubits, ignoring details of the QPU. |
| [`quimb_tn`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn.html#iqm.qaoa.circuits.quimb_tn "iqm.qaoa.circuits.quimb_tn")(qaoa) | Constructs a [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the quantum circuit. |
| [`quimb_tn_hubo`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.quimb_tn_hubo.html#iqm.qaoa.circuits.quimb_tn_hubo "iqm.qaoa.circuits.quimb_tn_hubo")(qaoa) | Constructs a [`quimb`](https://quimb.readthedocs.io/en/latest/autoapi/quimb/index.html#module-quimb "(in quimb v0.1)") tensor network representing the quantum circuit. |
| [`rnz`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.rnz.html#iqm.qaoa.circuits.rnz "iqm.qaoa.circuits.rnz")(n, theta) | Construct an n-qubit Pauli-Z string rotation circuit. |
| [`transpiled_circuit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.transpiled_circuit.html#iqm.qaoa.circuits.transpiled_circuit "iqm.qaoa.circuits.transpiled_circuit")(qaoa\[, backend, ...\]) | Build a QAOA quantum circuit for the given QAOA instance. |

Classes

|  |  |
|----|----|
| [`TranspilerOption`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.circuits.TranspilerOption.html#iqm.qaoa.circuits.TranspilerOption "iqm.qaoa.circuits.TranspilerOption") | Available transpilation (routing) strategies for QAOA circuits. |

Inheritance

![Inheritance diagram of iqm.qaoa.circuits](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-8a9a35e6b23ba0cff21e88226801a69e3800b4ad.png)

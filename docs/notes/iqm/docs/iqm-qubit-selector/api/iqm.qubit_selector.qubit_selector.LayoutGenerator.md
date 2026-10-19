> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.LayoutGenerator.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.LayoutGenerator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 12f1514a267ca4e910ed8b9a6b8a46575abc149f3b2ee060914866c60a9b14cc.

# LayoutGenerator

Module: [`iqm.qubit_selector.qubit_selector`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.html#module-iqm.qubit_selector.qubit_selector "iqm.qubit_selector.qubit_selector")

*class* iqm.qubit_selector.qubit_selector.LayoutGenerator(*backend*, *quantum_circuit*, *remove_qubits=None*, *num_trials=2000*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Generates unique layouts for quantum circuits based on calibration data and backend architecture.

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)")) – IQM backend instance.

- **quantum_circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The quantum circuit to generate layouts for.

- **weights** – Weights for calibration types.

- **additional_qubits** – Number of additional qubits to consider.

- **remove_qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – List of qubit indices (in qiskit) to remove from consideration.

- **num_trials** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of trial instances for layout generation.

Methods

|  |  |
|----|----|
| [`generate_unique_layouts`](#iqm.qubit_selector.qubit_selector.LayoutGenerator.generate_unique_layouts "iqm.qubit_selector.qubit_selector.LayoutGenerator.generate_unique_layouts") | Generate unique layouts based on the architecture of the backend. |

generate_unique_layouts()  
Generate unique layouts based on the architecture of the backend.

Returns:  
A list of unique layouts represented as lists of qubit indices.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

Inheritance

![Inheritance diagram of iqm.qubit_selector.qubit_selector.LayoutGenerator](https://docs.iqm.tech/4.7/iqm-qubit-selector/_images/inheritance-e3ad3253e345f5066b783ba539e5ef48be157f48.png)

> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CostEvaluator.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CostEvaluator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 480ea192a7aa7e0dcb93df8b7a3c304210f3a796c5d5a28e41a4b62e79174b52.

# CostEvaluator

Module: [`iqm.qubit_selector.qubit_selector`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.html#module-iqm.qubit_selector.qubit_selector "iqm.qubit_selector.qubit_selector")

*class* iqm.qubit_selector.qubit_selector.CostEvaluator(*backend*, *quantum_circuit*, *cost_function=CostFunction.GATE_COST_CZ*, *readoutmode=ReadoutMode.NONE*, *remove_qubits=None*, *num_trials=2000*, *layouts=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Evaluates cost functions for quantum circuit layouts.

This class is responsible for computing the costs associated with different layouts of quantum circuits based on specified cost functions. It utilizes calibration data and backend information to assess the fidelity of quantum operations and idle times, allowing for the optimization of quantum circuit layouts.

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)")) – IQM backend instance.

- **quantum_circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – The quantum circuit to be managed.

- **cost_function** ([*CostFunction*](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CostFunction.html#iqm.qubit_selector.qubit_selector.CostFunction "iqm.qubit_selector.qubit_selector.CostFunction")) – The cost function to be used for optimization.

- **readoutmode** ([*ReadoutMode*](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.ReadoutMode.html#iqm.qubit_selector.qubit_selector.ReadoutMode "iqm.qubit_selector.qubit_selector.ReadoutMode")) – The readoutmode to use for including readout errors in the cost calculation.

- **weights** – Weights for calibration types.

- **remove_qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – List of qubit indices (in qiskit) to remove from consideration.

- **num_trials** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of trial instances for layout generation.

- **additional_qubits** – Number of additional qubits to consider.

- **layouts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – Predefined layouts to evaluate.

Raises:  
[**Exception**](https://docs.python.org/3.11/library/exceptions.html#Exception "(in Python v3.11)") – If there is an error during the transpilation process.

Methods

|  |  |
|----|----|
| [`get_top_layouts`](#iqm.qubit_selector.qubit_selector.CostEvaluator.get_top_layouts "iqm.qubit_selector.qubit_selector.CostEvaluator.get_top_layouts") | Compute the costs associated with different circuit layouts based on the specified cost function. |

get_top_layouts(*num_layouts=1*)  
Compute the costs associated with different circuit layouts based on the specified cost function.

Parameters:  
**num_layouts** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of top layouts to return based on their costs.

Returns:  
A tuple containing two lists with layouts and scores.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

Inheritance

![Inheritance diagram of iqm.qubit_selector.qubit_selector.CostEvaluator](https://docs.iqm.tech/4.7/iqm-qubit-selector/_images/inheritance-b7db8c79b4482fa4ba0e75ce620e97d8565ea89a.png)

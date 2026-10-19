> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a12b4d388791a0d7d824441ffd17c76dfdf602ce243248ed46c9a462784f7bba.

# iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates

iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates(*circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*, *drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *ignore_barriers: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")  
Optimize number of single-qubit gates in a transpiled circuit exploiting the IQM specific gate set.

Parameters:  
- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – quantum circuit to optimize

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Drop terminal RZ gates even if there are no measurements following them (since they do not affect the measurement results). Note that this will change the unitary propagator of the circuit. Defaults to False.

- **ignore_barriers** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Removes barriers from the circuit if they exist (default = False) before optimization.

Returns:  
optimized circuit

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

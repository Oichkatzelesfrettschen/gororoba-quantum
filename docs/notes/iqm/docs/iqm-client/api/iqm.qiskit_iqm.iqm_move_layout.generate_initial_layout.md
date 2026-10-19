> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_move_layout.generate_initial_layout.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_move_layout.generate_initial_layout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ca40a78a3ae8f8db3d59b05ddeedbed336c798650ba3009d157580a32c2cce47.

# iqm.qiskit_iqm.iqm_move_layout.generate_initial_layout

iqm.qiskit_iqm.iqm_move_layout.generate_initial_layout(*target: [IQMTarget](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget")*, *circuit: [QuantumCircuit](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")*) → [Layout](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)")  
Generate an initial layout for the given circuit, for running on the given Star architecture target.

Parameters:  
- **target** ([*IQMTarget*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_target.IQMTarget.html#iqm.qiskit_iqm.iqm_target.IQMTarget "iqm.qiskit_iqm.iqm_target.IQMTarget")) – IQM Star architecture target to run the circuit on, without fictional gates.

- **circuit** ([*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")) – Quantum circuit for which a layout is to be generated.

Returns:  
Layout that maps the virtual/logical qubits of `circuit` to the physical qubits of `target` so that all the gates in `circuit` are available on those loci.

Return type:  
[*Layout*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Layout "(in Qiskit v2.5)")

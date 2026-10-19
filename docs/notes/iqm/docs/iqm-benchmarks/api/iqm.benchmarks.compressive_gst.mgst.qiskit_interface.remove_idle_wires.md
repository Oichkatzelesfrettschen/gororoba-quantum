> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ce3f79970cb874344be17db1f2c0571b763a5dc8eddeace3b9fb076775343e1f.

# iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires

iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires(*qc: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Removes all wires on which no gate acts.

Credit to: [https://quantumcomputing.stackexchange.com/a/37192](https://quantumcomputing.stackexchange.com/a/37192) This shrinks the circuit for the conversion to quantum channels.

Parameters:  
**qc** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – Input circuit from which idle wires are removed.

Returns:  
The circuit with idle wires removed.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 92c96d8af78d9a1c2bb3d98e7c065da3f482d9d94796f23f7ad76c81db7e00c6.

# iqm.benchmarks.compressive_gst.mgst.qiskit_interface

Bridge between mGST and Qiskit.

Functions

|  |  |
|----|----|
| [`add_idle_gates`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.add_idle_gates.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.add_idle_gates "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.add_idle_gates")(gate_set, active_qubits, ...) | Add additional idle gates to a gate set. |
| [`get_composed_qiskit_circuits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_composed_qiskit_circuits.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_composed_qiskit_circuits "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_composed_qiskit_circuits")(gate_sequences, ...) | Turn GST sequences into Qiskit circuits, adding context gates if provided. |
| [`get_gate_sequence`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence")(sequence_number, ...) | Generate a set of random gate sequences. |
| [`get_qiskit_circuits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_qiskit_circuits.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_qiskit_circuits "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_qiskit_circuits")(gate_sequences, ...) | Generate a set of Qiskit quantum circuits from specified gate sequences. |
| [`job_counts_to_mgst_format`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.job_counts_to_mgst_format.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.job_counts_to_mgst_format "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.job_counts_to_mgst_format")(active_qubits, ...) | Turns the dictionary of outcomes from qiskit backend into the format which is used in mGST. |
| [`qiskit_gate_to_operator`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator")(gate_set) | Convert a set of Qiskit gates to their unitary operators. |
| [`remove_idle_wires`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires.html#iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires "iqm.benchmarks.compressive_gst.mgst.qiskit_interface.remove_idle_wires")(qc) | Removes all wires on which no gate acts. |

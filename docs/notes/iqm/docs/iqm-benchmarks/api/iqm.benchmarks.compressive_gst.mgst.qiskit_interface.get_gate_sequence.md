> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 53f537bf07610cc90ece512bc659366ce224ca275e61ebbae9173986928ffb29.

# iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence

iqm.benchmarks.compressive_gst.mgst.qiskit_interface.get_gate_sequence(*sequence_number: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *sequence_length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *gate_set_length: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate a set of random gate sequences.

This function creates a specified number of random gate sequences, each of a given length. The gates are represented by numerical indices corresponding to elements in gate_set. Each sequence is a random combination of these indices.

Parameters:  
- **sequence_number** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of gate sequences to generate.

- **sequence_length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The length of each gate sequence.

- **gate_set_length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The length of the set of gates to be used

Returns:  
An array of shape (sequence_number, sequence_length), where each row represents a randomly generated  
gate sequence.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

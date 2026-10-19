> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0e2eca04d4f93f031d7cdb26d1c9f0b4c29a0019f0c08ddad0f0aad730b40cf9.

# iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator

iqm.benchmarks.compressive_gst.mgst.qiskit_interface.qiskit_gate_to_operator(*gate_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Gate\]*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Convert a set of Qiskit gates to their unitary operators.

This function takes a list of Qiskit gate objects and them into operators, returned as a NumPy array of matrices.

Parameters:  
**gate_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Gate\]*) – A list of Qiskit gate objects. Each gate in the list is converted to its corresponding unitary.

Returns:  
An array of process matrices. Each element in the array is a 2D NumPy array.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

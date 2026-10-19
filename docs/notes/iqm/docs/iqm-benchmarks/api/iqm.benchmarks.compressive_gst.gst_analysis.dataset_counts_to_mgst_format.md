> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.dataset_counts_to_mgst_format.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.dataset_counts_to_mgst_format.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2e72c3a627142fe7db0e35ef65f2ba21ddd53fd72d001448ae14a885e7cab2dc.

# iqm.benchmarks.compressive_gst.gst_analysis.dataset_counts_to_mgst_format

iqm.benchmarks.compressive_gst.gst_analysis.dataset_counts_to_mgst_format(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Turns the dictionary of outcomes obtained from qiskit backend into the format which is used in mGST.

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment and configurations

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of qubits for the current GST experiment

Returns:  
2D array of measurement outcomes for sequences in J; Each column contains the outcome probabilities for a fixed sequence

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

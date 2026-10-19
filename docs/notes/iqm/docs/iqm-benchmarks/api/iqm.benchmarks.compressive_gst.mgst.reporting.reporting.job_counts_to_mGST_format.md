> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.job_counts_to_mGST_format.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.job_counts_to_mGST_format.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 97d3207e53e0352769a6115723b424f56076f89fe85689608ed4d0fc34faf055.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.job_counts_to_mGST_format

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.job_counts_to_mGST_format(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *num_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *result_dict: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Turns the dictionary of outcomes obtained from qiskit backend into the format which is used in mGST.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of active qubits in the experiment

- **num_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of POVM elements in the experiment

- **result_dict** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – The counts from the qiskit backend for each circuit

Returns:  
2D array of measurement outcomes for sequences in J; Each column contains the outcome probabilities for a fixed sequence

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

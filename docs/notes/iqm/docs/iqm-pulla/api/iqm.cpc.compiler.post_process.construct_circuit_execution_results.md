> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_circuit_execution_results.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_circuit_execution_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f177ac4360e6fbd4aa7efe52f119a16e5c317001411315a5cb48442e6f446f9.

# iqm.cpc.compiler.post_process.construct_circuit_execution_results

iqm.cpc.compiler.post_process.construct_circuit_execution_results(*sweep_results*, *context*)  
Construct a [`CircuitExecutionResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html#iqm.cpc.compiler.post_process.CircuitExecutionResults "iqm.cpc.compiler.post_process.CircuitExecutionResults").

The construction is not possible if there are multiple readout triggers per segment for a given readout label

Parameters:  
- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]\]*) – The raw sweep results returned by SC.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The compiler context.

Returns:  
The constructed [`CircuitExecutionResults`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html#iqm.cpc.compiler.post_process.CircuitExecutionResults "iqm.cpc.compiler.post_process.CircuitExecutionResults") instance.

Return type:  
[*CircuitExecutionResults*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.CircuitExecutionResults.html#iqm.cpc.compiler.post_process.CircuitExecutionResults "iqm.cpc.compiler.post_process.CircuitExecutionResults")

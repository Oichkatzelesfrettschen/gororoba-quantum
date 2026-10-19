> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_run_result.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.construct_run_result.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 46bba49d25a61701017ef1a9678e53ba9390f9f8d4cd2e04d1b9cacfe9242291.

# iqm.cpc.compiler.post_process.construct_run_result

iqm.cpc.compiler.post_process.construct_run_result(*sweep_results*, *context*)  
Construct the dataset and attach it to a RunResult object.

Unmaps the hashed readout keys.

Parameters:  
- **sweep_results** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]\]*) – The raw sweep results returned by SC.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The Compiler context.

Returns:  
The RunResult.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

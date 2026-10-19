> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.rename_data_variables.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.rename_data_variables.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 288f35f9c9f8376c2769ad0c20b12d2b81de8a162c569217db62a74af7f73147.

# iqm.cpc.compiler.post_process.rename_data_variables

iqm.cpc.compiler.post_process.rename_data_variables(*run*, *context*)  
Rename the data variables in the dataset and optionally change their data types.

Parameters:  
- **run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The RunResult object.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Compiler context.

Returns:  
The post-processed run results with the data variables renamed.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

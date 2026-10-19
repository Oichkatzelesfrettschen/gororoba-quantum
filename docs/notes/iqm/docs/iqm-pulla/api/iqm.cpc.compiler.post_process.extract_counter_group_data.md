> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.extract_counter_group_data.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.extract_counter_group_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1538e784b775a7db87c73bfc76aa45ad40b31c75f88f52a60b7e4af232911c38.

# iqm.cpc.compiler.post_process.extract_counter_group_data

iqm.cpc.compiler.post_process.extract_counter_group_data(*run*)  
Extracts the data for all counter readout groups into their own data variables in the dataset.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – the run result.

Returns:  
The run result with new data variables for each counter readout group added.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

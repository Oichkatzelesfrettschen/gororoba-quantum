> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counter_averaged_readout.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counter_averaged_readout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 76c1a36b97ab1a0a126c9b42e1fa126fe50976dd00b5b99a8dcd63bad3967ccc.

# iqm.cpc.compiler.post_process.add_counter_averaged_readout

iqm.cpc.compiler.post_process.add_counter_averaged_readout(*run*)  
Add single-qubit excited state probabilities from the multi qubit counter results to the dataset.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The run result.

Returns:  
The run result with new data variables for averaged readout for each component added.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

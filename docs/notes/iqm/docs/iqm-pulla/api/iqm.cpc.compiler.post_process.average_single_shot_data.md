> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.average_single_shot_data.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.average_single_shot_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 13c7328bba548e5c2aa1b6ab890af1b664a90a56091e1beac49ed55102371430.

# iqm.cpc.compiler.post_process.average_single_shot_data

iqm.cpc.compiler.post_process.average_single_shot_data(*run*)  
Average the shots (or more generally the average bins) into a new data variable in the dataset.

If the data is already averaged, it is returned unchanged.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The RunResult object.

Returns:  
The RunResult with the single shot data variables averaged.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

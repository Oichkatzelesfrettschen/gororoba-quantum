> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.contrast_data.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.contrast_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5a3bfba23887c09ccd4a719cdec8f4c2cfb0329f3f6c95eb52e684fc7f0490d1.

# iqm.cpc.compiler.post_process.contrast_data

iqm.cpc.compiler.post_process.contrast_data(*run*)  
Add contrast for several components/readouts.

Contrast is calculated from complex integrated data with PCA. If a data variable is not complex (i.e. it is already discriminated) it is retained as it is.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The RunResult object.

Returns:  
The RunResult with the contrast data variable added for all complex variables.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

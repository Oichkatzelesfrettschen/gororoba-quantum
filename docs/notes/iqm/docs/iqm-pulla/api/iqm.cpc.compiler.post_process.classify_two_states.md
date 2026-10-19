> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.classify_two_states.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.classify_two_states.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3fdbb62cb1832c0f54f34ed8518e92650f999b684f6443206646c086e98271de.

# iqm.cpc.compiler.post_process.classify_two_states

iqm.cpc.compiler.post_process.classify_two_states(*run*)  
Classify the complex data using the calibrated threshold.

If the observations are not available, a warning is logged.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The run result.

Returns:  
The run result with the discriminated shots added.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

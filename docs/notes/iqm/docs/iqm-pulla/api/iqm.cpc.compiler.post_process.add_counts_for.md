> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counts_for.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.add_counts_for.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3005b0a2e07415f8c14a9a9dd5f0ba2b19ab47b317b569ec91929d7b632aed88.

# iqm.cpc.compiler.post_process.add_counts_for

iqm.cpc.compiler.post_process.add_counts_for(*run*)  
Add single-qubit excited state probabilities from the multi qubit counter results to the dataset.

This is done only if the dimensions of the single qubit probabilities are equal.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The run result.

Returns:  
The run result with the counter data added.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

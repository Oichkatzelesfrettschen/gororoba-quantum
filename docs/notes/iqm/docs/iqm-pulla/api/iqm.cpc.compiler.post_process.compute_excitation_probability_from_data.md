> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.compute_excitation_probability_from_data.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.compute_excitation_probability_from_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f4cdb5a79bc669655aeee64aba2c4a830e2f8c89dd844a1e0ae167cc25594f30.

# iqm.cpc.compiler.post_process.compute_excitation_probability_from_data

iqm.cpc.compiler.post_process.compute_excitation_probability_from_data(*run*)  
Compute the excited state probability for several components.

For complex readout data, this is done using the averaged threshold readout observations and for threshold discriminated data using the 01 and 10 assignment error observations. If the aforementioned observations are not available, a warning is thrown.

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The RunResult object.

Returns:  
The RunResult with the excited state probability added into the dataset.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")

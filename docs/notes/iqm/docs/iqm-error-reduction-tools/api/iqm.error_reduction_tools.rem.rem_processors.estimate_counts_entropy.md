> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 265f3097f7839d90d2c0e2fde6cce5d85ddbcf7bf85830344006b538ffbf6371.

# iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy

iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy(*counts*)  
Estimate the Shannon entropy of the measurement probability distribution.

Computes \\H = -\\sum_i p_i \\log_2(p_i)\\ from the observed counts which quantifies the spread of the distribution. Higher entropy means more unique outcomes with similar probabilities, making mitigation more expensive.

Parameters:  
**counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Dictionary mapping bitstrings to their measured counts.

Returns:  
Shannon entropy in bits. Ranges from 0 (single outcome) to \\\\log_2(N)\\ where *N* is the number of unique bitstrings.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

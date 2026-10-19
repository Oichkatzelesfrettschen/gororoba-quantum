> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.is_successful.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.is_successful.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d74cc63e6fbff6a34118847aad3304738c7904034e7537174647a63b03ead9a3.

# iqm.benchmarks.optimization.qscore.is_successful

iqm.benchmarks.optimization.qscore.is_successful(*approximation_ratio: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Check whether a Q-score benchmark returned approximation ratio above beta\*, therefore being successful.

This condition checks that the mean approximation ratio is above the beta\* = 0.2 threshold.

Parameters:  
**approximation_ratio** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The mean approximation ratio of all problem graphs

Returns:  
Whether the Q-score benchmark was successful

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

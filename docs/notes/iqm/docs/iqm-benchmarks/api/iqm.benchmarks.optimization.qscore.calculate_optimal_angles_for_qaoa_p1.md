> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4ef5765c62bf479b99c1ca6b853e3e8ca90d3eca80c3d423b60a94b73d061cad.

# iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1

iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1(*graph: Graph*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Calculates the optimal angles for single layer QAOA MaxCut ansatz.

Parameters:  
**graph** (*Graph*) – The MaxCut problem graph.

Returns:  
Optimal angles gamma and beta.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.cut_cost_function.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.cut_cost_function.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c9a627a5f975d12973bede2467d7c66c8b345cf4ed42777c5b6970f9717f7084.

# iqm.benchmarks.optimization.qscore.cut_cost_function

iqm.benchmarks.optimization.qscore.cut_cost_function(*x: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *graph: Graph*) → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
Returns the number of cut edges in a graph (with minus sign).

Parameters:  
- **x** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Solution bitstring.

- **graph** (*Graph*) – The MaxCut problem graph.

Returns:  
Number of cut edges multiplied by -1.

Return type:  
obj

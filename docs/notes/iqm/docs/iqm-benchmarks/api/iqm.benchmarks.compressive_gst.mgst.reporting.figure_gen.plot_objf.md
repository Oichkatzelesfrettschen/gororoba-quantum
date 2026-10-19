> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 644b25210f3f91927cb9c7990af928cbca961353f0dcbce8f4834fdb651f5db6.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf(*res_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *title: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *delta: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Plots the objective function over iterations in the algorithm.

Parameters:  
- **res_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The residual values

- **title** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The plot title

- **delta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*) – The success threshold, drawn in the figure as a horizontal line

Return type:  
None

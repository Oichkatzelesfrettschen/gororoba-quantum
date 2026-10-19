> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.prepare_plot_data.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.prepare_plot_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8545626dc6eb7ff5276fc1764a6f2f0361717a1249480396c349a76c24e4a828.

# prepare_plot_data

iqm.applications.graph_utils.prepare_plot_data(*data*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L285-L382)  
Generates all layout and color data required for visualization.

Parameters:  
- **data** ([*ProblemData*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.ProblemData.html#iqm.applications.graph_utils.ProblemData "iqm.applications.graph_utils.ProblemData")) – Normalized problem data (output of `_extract_problem_info()`).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Optional seed to make the layout deterministic.

Returns:  
A [`PlotData`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.PlotData.html#iqm.applications.graph_utils.PlotData "iqm.applications.graph_utils.PlotData") object containing positions, colors, widths, and labels needed for rendering the graph.

Return type:  
[*PlotData*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.PlotData.html#iqm.applications.graph_utils.PlotData "iqm.applications.graph_utils.PlotData")

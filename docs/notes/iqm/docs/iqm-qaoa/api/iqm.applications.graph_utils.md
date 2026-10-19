> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b3c971afb78285b78b22e0eda0e817aa90c9496668e7d8c5893f91d6a7b0b926.

# graph_utils

Full path: iqm.applications.graph_utils

Contains utility functions regarding graphs which are generic enough that they deserve having their own module.

Module Attributes

|  |  |
|----|----|
| [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY") | Ordered names of node attributes that may store node weights. |
| [`EDGE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html#iqm.applications.graph_utils.EDGE_ATTR_PRIORITY "iqm.applications.graph_utils.EDGE_ATTR_PRIORITY") | Ordered names of edge attributes that may store edge weights. |

Functions

|  |  |
|----|----|
| [`draw_problem`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.draw_problem.html#iqm.applications.graph_utils.draw_problem "iqm.applications.graph_utils.draw_problem")(\[problem_instance, ...\]) | High-level wrapper that prepares and visualizes a problem graph. |
| [`get_top_n_color_pairs`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.get_top_n_color_pairs.html#iqm.applications.graph_utils.get_top_n_color_pairs "iqm.applications.graph_utils.get_top_n_color_pairs")(max_color_pairs\[, ...\]) | Helper function for the greedy router. |
| [`plot_graph`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.plot_graph.html#iqm.applications.graph_utils.plot_graph "iqm.applications.graph_utils.plot_graph")(plot_data) | Renders the graph using `matplotlib` and `networkx`. |
| [`prepare_plot_data`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.prepare_plot_data.html#iqm.applications.graph_utils.prepare_plot_data "iqm.applications.graph_utils.prepare_plot_data")(data\[, seed\]) | Generates all layout and color data required for visualization. |
| [`residual_degree`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.residual_degree.html#iqm.applications.graph_utils.residual_degree "iqm.applications.graph_utils.residual_degree")(graph, node, visited) | The degree of `node` in the graph, with regards to only non-visited nodes. |

Classes

|  |  |
|----|----|
| [`PlotData`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.PlotData.html#iqm.applications.graph_utils.PlotData "iqm.applications.graph_utils.PlotData") | Precomputed visualization information used for drawing the graph. |
| [`ProblemData`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.ProblemData.html#iqm.applications.graph_utils.ProblemData "iqm.applications.graph_utils.ProblemData") | Normalized problem information extracted and validated before plotting. |

Inheritance

![Inheritance diagram of iqm.applications.graph_utils](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-4359a49424dc5ff249a272f965d9c68351b69d7e.png)

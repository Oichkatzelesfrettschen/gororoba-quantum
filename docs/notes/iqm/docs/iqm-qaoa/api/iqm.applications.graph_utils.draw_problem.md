> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.draw_problem.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.draw_problem.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 53158d60555be3d9bdfd3a5b3ac9ec9a1f86fb083c3d9e2577ec13c220f27175.

# draw_problem

iqm.applications.graph_utils.draw_problem(*problem_instance=None*, *\**, *graph_to_plot=None*, *fixed_vars=frozenset({})*, *bitstring=None*, *seed=None*, *highlight_edge_by_node_count=frozenset({2})*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L431-L477)  
High-level wrapper that prepares and visualizes a problem graph.

This function orchestrates three steps:  
1.  Extraction of problem data via `_extract_problem_info()`.

2.  Conversion into plotting data with [`prepare_plot_data()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.prepare_plot_data.html#iqm.applications.graph_utils.prepare_plot_data "iqm.applications.graph_utils.prepare_plot_data").

3.  Visualization using [`plot_graph()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.plot_graph.html#iqm.applications.graph_utils.plot_graph "iqm.applications.graph_utils.plot_graph").

It exists primarily as a convenience entry point — most argument validation and interpretation is handled by `_extract_problem_info()`.

Parameters:  
- **problem_instance** ([*QUBOInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.qubo.QUBOInstance.html#iqm.applications.qubo.QUBOInstance "iqm.applications.qubo.QUBOInstance") *\|* [*ISInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.ISInstance.html#iqm.applications.mis.ISInstance "iqm.applications.mis.ISInstance") *\|* *None*) – Optional optimization problem instance from which graph and mapping data can be derived.

- **graph_to_plot** (*nx.Graph* *\|* *None*) – Graph object to visualize. Overrides the graph from `problem_instance`, if both are provided.

- **fixed_vars** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Variables that have been fixed and should appear dimmed in the visualization. Overrides the fixed variables from `problem_instance`, if both are provided.

- **bitstring** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Binary string indicating which nodes are highlighted in the graph. Its length must match `len(problem_instance.original_variables)` and represent the state of all original variables (both fixed and unfixed). If the bitstring encodes only unfixed variables, it must first be converted using [`restore_fixed_variables_bitstring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.applications.ProblemInstance.html#iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring "iqm.applications.applications.ProblemInstance.restore_fixed_variables_bitstring").

- **highlight_edge_by_node_count** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Specifies which edges are highlighted based on the number of connected highlighted nodes (subset of `{0, 1, 2}`).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Optional random seed for layout stability.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `graph_to_plot` is not provided or obtainable from provided `problem_instance`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the provided `highlight_edge_by_node_count` is not a subset of `{0, 1, 2}`.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the provided `bitstring` has different length than the graph has nodes.

Return type:  
None

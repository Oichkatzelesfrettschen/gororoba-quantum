> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.get_top_n_color_pairs.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.get_top_n_color_pairs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a27d9420caf26e81e5e516ea65d5e11851083345766cf8d709ff265db77d0cd1.

# get_top_n_color_pairs

iqm.applications.graph_utils.get_top_n_color_pairs(*max_color_pairs*, *problem_graph=None*, *color_sets=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L129-L163)  
Helper function for the greedy router.

Finds an edge coloring of a graph, and then returns `max_color_pairs` largest (by the number of edges) pairs of colors. If there is less than `max_color_pairs` color pairs, then it returns all of them.

Parameters:  
- **max_color_pairs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The maximum number of edge color pairs to return.

- **problem_graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") *\|* *None*) – The graph to be colored. Ignored if `color_sets` is provided.

- **color_sets** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.LogEdge')\]\]* *\|* *None*) – Edge coloring of the graph. If None, obtained by coloring `problem_graph` with [`iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html#iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring "iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring").

Returns:  
The largest color pairs.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If both `problem_graph` and `color_sets` are `None`.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[TypeAliasForwardRef(‘~iqm.qaoa.transpiler.quantum_hardware.LogEdge’)\], [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[TypeAliasForwardRef(‘~iqm.qaoa.transpiler.quantum_hardware.LogEdge’)\]\]\]

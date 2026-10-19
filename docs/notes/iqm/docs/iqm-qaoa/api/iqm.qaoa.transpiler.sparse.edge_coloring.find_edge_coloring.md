> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c054d731029bb9589cfc523b14bfd42c15bc83ebf173eea8a0b6ccae94d2aea3.

# find_edge_coloring

iqm.qaoa.transpiler.sparse.edge_coloring.find_edge_coloring(*input_graph*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/edge_coloring.py#L304-L332)  
Find an edge coloring for the given graph.

It iterates over the graph edges and colors each one using elaborate helper functions. It modifies `input_graph` by adding an attribute `color` to every edge, given by an integer number.

Parameters:  
**input_graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") to be edge-colored.

Returns:  
1.  A list whose i-th entry contains the set of edges colored by the i-th color.

2.  A colored copy of the input `input_graph`.

Return type:  
A tuple containing

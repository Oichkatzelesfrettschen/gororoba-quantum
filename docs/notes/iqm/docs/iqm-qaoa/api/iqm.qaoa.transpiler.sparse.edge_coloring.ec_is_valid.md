> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dfac1ccda5833a668638589c43a710670731dba8e333467abfdcb1c062611b78.

# ec_is_valid

iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_valid(*graph*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/edge_coloring.py#L41-L63)  
Check that a graph’s edge coloring is valid.

Takes a graph whose edges have an attribute `color` and checks that no two neighboring edges have the same color (i.e., the coloring is valid).

Parameters:  
**graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – A [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") whose edges have an attribute `color`.

Returns:  
`True` if the edge coloring is valid, `False` otherwise.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

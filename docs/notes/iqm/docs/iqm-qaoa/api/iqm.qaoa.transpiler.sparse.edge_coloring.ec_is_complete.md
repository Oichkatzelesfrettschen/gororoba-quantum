> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26eccc2bb8e334373069c067ad0fb4d96471556f997f14016d9502b4fa1d7570.

# ec_is_complete

iqm.qaoa.transpiler.sparse.edge_coloring.ec_is_complete(*graph*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/edge_coloring.py#L66-L81)  
Check that a graph’s edge coloring is complete.

Parameters:  
**graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – A [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") whose edge coloring we want to check.

Returns:  
`True` if every edge of the graph has an attribute `color`, `False` otherwise.

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

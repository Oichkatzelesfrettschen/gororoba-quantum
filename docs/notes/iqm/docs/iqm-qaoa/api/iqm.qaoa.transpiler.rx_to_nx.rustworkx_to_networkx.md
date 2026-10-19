> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4d3d14b0830b0420c70b0f1ab9ccd32a3da9001f7dcf49d47b66ccf25b075e77.

# rustworkx_to_networkx

iqm.qaoa.transpiler.rx_to_nx.rustworkx_to_networkx(*graph*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/rx_to_nx.py#L33-L48)  
Convert a `rustworkx` graph to a [`networkx.Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)").

Doesn’t preserve node / edge weights or respect multigraphs.

Parameters:  
**graph** (*PyGraph* *\|* *PyDiGraph*) – The graph to be converted.

Returns:  
The converted graph.

Return type:  
[*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")

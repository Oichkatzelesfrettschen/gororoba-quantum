> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.residual_degree.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.residual_degree.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c9aca1b6fd5f42795a8fb96be9c72b4e328f7c14a58af5c2f8b870ec8ce3bdd6.

# residual_degree

iqm.applications.graph_utils.residual_degree(*graph*, *node*, *visited*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L480-L492)  
The degree of `node` in the graph, with regards to only non-visited nodes.

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – The graph which we’re working with.

- **node** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The node whose reduced degree we want to calculate.

- **visited** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The set of all visited nodes up to now.

Returns:  
The residual degree of the node.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

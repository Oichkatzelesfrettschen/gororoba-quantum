> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7a742b2109eddf632df5b66feb43ba075446997493a4c3654cc06e31853efd63.

# iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges

iqm.qrisp_iqm.passes.default_pass_manager.shift_graph_edges(*edges: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *removed_nodes: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *removed_edges: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Removes specified edges and nodes from a graph, then shifts the indices of the remaining nodes.

Parameters:  
- **edges** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *of* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)") *of* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – List of edges in the graph, where each edge is represented as a tuple (a, b) with node indices.

- **removed_nodes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *of* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – List of node indices to be removed from the graph.

- **removed_edges** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *of* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)") *of* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *or* *None,* *optional*) – List of edges to be removed from the graph before processing node removals and shifts. Each edge should be a tuple (a, b), using the initial node indices. Default is None (no additional edges removed).

Returns:  
**new_edges** – List of edges for the updated graph after specified edges and nodes have been removed, with all node indices shifted so that remaining indices are contiguous from 0 to n - k - 1, where k is the number of removed nodes.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") of [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)") of [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Notes

- All edges in `removed_edges` are eliminated from the initial edge list before node removal and index shifting.

- Edges connected to any removed node are omitted.

- After removal, all node indices greater than the removed nodes are decreased by the number of removed nodes with lower index, to ensure contiguous numbering from 0 upwards.

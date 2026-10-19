> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ed69d0ac46495a2206026f3ab4bf386b32b1459d70176861f7bfc44e0ccae17b.

# iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers

iqm.benchmarks.entanglement.graph_states.generate_minimal_edge_layers(*cp_map: CouplingMap*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]  
Sorts the edges of a coupling map.

The edges are arranged in a dictionary with values being subsets of the coupling map with no overlapping nodes. Each item will correspond to a layer of pairs of qubits in which parallel 2Q gates can be applied.

Parameters:  
**cp_map** (*CouplingMap*) – A list of lists of pairs of integers, representing a coupling map.

Returns:  
A dictionary with values being subsets of the coupling map with no overlapping nodes.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]

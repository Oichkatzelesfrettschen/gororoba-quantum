> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.remove_directed_duplicates_to_list.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.remove_directed_duplicates_to_list.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6817101bcc8fcb867d5446d20a8685a6a410df92c71fa459243db236e01dbfe2.

# iqm.benchmarks.utils.remove_directed_duplicates_to_list

iqm.benchmarks.utils.remove_directed_duplicates_to_list(*cp_map: CouplingMap*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Remove duplicate edges from a coupling map and returns as a list of edges (as a list of pairs of vertices).

Parameters:  
**cp_map** (*CouplingMap*) – A list of pairs of integers, representing a coupling map.

Returns:  
The edges of the coupling map.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

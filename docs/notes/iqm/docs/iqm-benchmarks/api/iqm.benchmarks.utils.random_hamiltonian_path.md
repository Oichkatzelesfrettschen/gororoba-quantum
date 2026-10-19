> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.random_hamiltonian_path.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.random_hamiltonian_path.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6a94861310850f03fba0395f11df3ac5d2793926a89e79f56ca39fa69e7bbb0b.

# iqm.benchmarks.utils.random_hamiltonian_path

iqm.benchmarks.utils.random_hamiltonian_path(*graph: Graph*, *n_vertices: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Generates a random Hamiltonian path with n_vertices from a given NetworkX graph.

Parameters:  
- **graph** (*Graph*) – The input graph.

- **n_vertices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The desired number of vertices in the Hamiltonian path.

Returns:  
A list of edges (tuples of nodes) representing the Hamiltonian path, or an empty list if not possible.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bca6e18d73548c4e9c813f33f08d3d9e3e93bbe7766c15c3be8a933adb6df6c2.

# iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr

iqm.qrisp_iqm.passes.routing.core.graph_processing_tools.reachability_counts_csr(*indptr: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *indices: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *ignore_nodes: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *predecessors: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Count how many nodes each node can reach in a CSR-encoded DAG.

By default (`predecessors=False`) this counts **descendants**: for every node *u* it returns the number of nodes reachable by following edges forward. When `predecessors=True` it counts **predecessors** (ancestors) instead, i.e. the number of nodes from which *u* is reachable — equivalent to computing descendant counts on the transposed graph.

Nodes listed in `ignore_nodes` are excluded from every count (useful for skipping single-qubit gates in a circuit DAG).

Parameters:  
- **indptr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR row-pointer array of the DAG.

- **indices** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR column-index array of the DAG.

- **ignore_nodes** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Boolean (0/1) mask — nodes where the entry is 1 are excluded from counting.

- **predecessors** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Iff True, count predecessors (ancestors) instead of descendants.

Returns:  
Per-node reachability count (self excluded).

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

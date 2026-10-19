> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ab3a6f91afec14df279efd9aa4f70091cacfd4b427a7b71b4cd9990cc6eae1db.

# iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding

iqm.qrisp_iqm.passes.routing.core.vf2pp.is_identity_embedding(*pattern_indices: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *pattern_indptr: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *target_indices: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *target_indptr: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")  
Check whether the pattern graph is a subgraph of the target graph.

Tests the *identity* mapping, i.e. whether node `i` of the pattern graph can stay on node `i` of the target graph. For the layout passes this answers “does the circuit already have a valid layout?”, so circuit qubit `i` maps directly to physical qubit `i`.

Parameters:  
- **pattern_indices** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR neighbor indices of the circuit’s interaction graph, with one node per circuit qubit.

- **pattern_indptr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR index pointer of the circuit’s interaction graph.

- **target_indices** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR neighbor indices of the target graph (device topology with one node per physical qubit). Neighbor lists must be **sorted** — the same requirement the VF2++ search makes.

- **target_indptr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR index pointer of the target graph.

Returns:  
`True` if every edge of the pattern graph is also an edge of the target graph between the nodes of the same indices, `False` otherwise (including when the pattern graph has more nodes than the target graph).

Return type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

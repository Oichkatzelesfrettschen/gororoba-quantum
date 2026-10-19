> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 79500e7f14d78c74c0d911049f4ad4a61b6cdb1ba5554a69ebd8ceaf05b2d66b.

# iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism

iqm.qrisp_iqm.passes.routing.core.vf2pp.vf2pp_subgraph_isomorphism(*pattern_indices: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *pattern_indptr: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *target_indices: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *target_indptr: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *max_attempts: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Find one subgraph isomorphism mapping from pattern graph to target.

Uses a Numba-optimized VF2++-style search.

The first pattern node’s candidates are explored in parallel across CPU cores, each thread with its own budget slice.

Parameters:  
- **pattern_indices** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR column indices of the pattern graph.

- **pattern_indptr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR row pointers of the pattern graph.

- **target_indices** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR column indices of the target graph. Neighbor lists must be **sorted** for binary search to work.

- **target_indptr** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – CSR row pointers of the target graph.

- **max_attempts** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total maximum number of feasible candidate assignments to try (split equally across parallel threads) before giving up. 0 (default) means unlimited.

Returns:  
`mapping[i]` is the target node matched to pattern node `i`. If no mapping is found, returns an array of all -1. If the identity mapping is itself an embedding it is always the one returned, so a pattern that already sits on the target is left where it is.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 698cdbec7b0ece9f746344582d2a69f4b97c8d6c0c870e6dbce699adafa1c652.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array(*front_layer_indices: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *extended_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *instruction_data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *N: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Precompute the depth array.

Computes for a given combination of front layer and extended set.

Parameters:  
- **front_layer_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the front layer.

- **extended_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the extended set.

- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **N** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")) – A topology tuple `(indptr, indices, distance_matrix, predecessors)` as returned by `connectivity_to_topology()`. The distance matrix at `N[2]` determines the output dtype (int16 on NISQ-scale devices).

Returns:  
**depth_array** – An array indicating what layer each instruction from the front layer and extended set lives in.

Return type:  
np.ndarray

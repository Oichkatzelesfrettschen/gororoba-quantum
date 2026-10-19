> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 546c3855f5678758a7c067349946b68fde09e47a902ab8eedf09ebf0f812e0ba.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor(*front_layer_indices: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *instruction_data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Precompute the prefactor of the front layer.

Parameters:  
- **front_layer_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the front layer.

- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **depth_array** (*np.ndarray*) – The depth array indicating the layer of each instruction.

Returns:  
The prefactor.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

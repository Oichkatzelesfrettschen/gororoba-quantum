> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2d27ceedca39ca46942608bdc1ff29741160ddec6264fe89fd75050f308184b1.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change(*instruction_data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *fl_inv_0: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *fl_inv_1: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *es_inv_0: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *es_inv_1: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *old_c2a: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *swap_0: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *swap_1: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *exp_depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *front_layer_prefactor: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *extended_layer_prefactor: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *distance_matrix: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute the cost change induced by a given swap.

For this it only considers the terms that actually contribute, which is much more efficient.

Instead of receiving a full new_c2a array (which requires a copy per call), the swap is described by the two citizen indices (swap_0, swap_1). The new addresses are resolved inline with a branch, avoiding an array allocation per swap candidate.

The involvement lists are passed as 4 separate lists (two per layer type), one for each qubit of the swap. This avoids the allocation of a concatenated list per swap candidate.

Parameters:  
- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **fl_inv_0** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Front layer involvement list of the first swap qubit.

- **fl_inv_1** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Front layer involvement list of the second swap qubit.

- **es_inv_0** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Extended set involvement list of the first swap qubit.

- **es_inv_1** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Extended set involvement list of the second swap qubit.

- **old_c2a** (*np.ndarray*) – An array indicating the current permutation of qubits.

- **swap_0** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The citizen index of the first qubit being swapped.

- **swap_1** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The citizen index of the second qubit being swapped.

- **exp_depth_array** (*np.ndarray*) – An array containing the precomputed weight factors of each instruction.

- **front_layer_prefactor** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The precomputed factor that is used to weight the front layer part of the metric.

- **extended_layer_prefactor** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The precomputed factor that is used to weight the extended set part of the metric.

- **distance_matrix** (*np.ndarray*) – The distance matrix from the topology tuple.

Returns:  
The computed metric change.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

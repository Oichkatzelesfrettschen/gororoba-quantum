> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 362841c9aeb4882c8057c915cf6688359d68857d6c066d6153e6f093d84c6a49.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor

iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor(*extended_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *instruction_data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *exp_depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Precompute the prefactor of the extended set.

Parameters:  
- **extended_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – A list of integers indicating which entries of instruction data constitute the extended set.

- **instruction_data** (*np.ndarray*) – An array describing what instructions are available globally (see graph_processing_tools for more details).

- **exp_depth_array** (*TYPE*) – The array of precomputed prefactors.

Returns:  
The prefactor.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

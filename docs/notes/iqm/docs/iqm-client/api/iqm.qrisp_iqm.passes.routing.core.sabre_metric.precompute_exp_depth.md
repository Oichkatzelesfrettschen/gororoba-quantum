> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 14e90123f86275e9617eb9d9dff9a01866bc8ede1887533f577ca241a19d99b7.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth

iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth(*depth_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Precompute the decay factor from the depth array.

Parameters:  
**depth_array** (*np.ndarray*) – The array indicating which layer each instruction is involved in.

Returns:  
The precomputed prefactors.

Return type:  
np.ndarray

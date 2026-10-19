> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 042a84157160d480c6d5797945e3d7a6d24ff1f99a67b1289604312121abf9fd.

# iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list

iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list(*involvement_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[int16\]*, *scaling_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *threshold: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[int16\]  
Produce a filtered copy of an involvement list.

Keeps only the instruction indices whose scaling_array weight is \>= threshold.

This is called once per `depth_array_update_required` cycle in [`sabre_gen_swaps()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps.html#iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps "iqm.qrisp_iqm.passes.routing.core.sabre_workflow.sabre_gen_swaps") so that the hot [`compute_sabre_cost_change()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change") loop never iterates over entries whose contribution has decayed to near-zero. Filtering once per DAG advance is far cheaper than checking the threshold inside the per-swap-candidate loop.

Parameters:  
- **involvement_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[int16\]*) – A per-qubit list of instruction indices (front-layer or extended-set).

- **scaling_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The combined weight array (exp_depth \* criticality) indexed by instruction index.

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Minimum weight for an entry to survive the filter.

Returns:  
A new list containing only the entries with weight \>= threshold. If *threshold* is zero the input list is returned unchanged (avoids an allocation).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*int16*\]

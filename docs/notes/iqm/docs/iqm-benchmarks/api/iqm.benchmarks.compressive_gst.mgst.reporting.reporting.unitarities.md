> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.unitarities.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.unitarities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 83055dbf7e810f3bbe8821a80b6839230175025c68272af510dd42691b77d670.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.unitarities

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.unitarities(*X_opt_pp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Computes the unitarities of all gates in the gate set.

Parameters:  
**X_opt_pp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array where CPT superoperators in Pauli basis are stacked along the first axis.

Returns:  
List of unitarities for the gates in X_opt_pp.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

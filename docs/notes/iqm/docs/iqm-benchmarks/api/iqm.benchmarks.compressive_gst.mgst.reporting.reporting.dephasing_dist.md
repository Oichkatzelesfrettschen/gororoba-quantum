> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_dist.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_dist.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c8a237dfa4ff8b1b337cba909675703cbb392d61553ab0629c419e300f5cc487.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_dist

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_dist(*prob_vec: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *X_pp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Returns the distance between a given channel and a local dephasing channel with given probabilities.

Parameters:  
- **prob_vec** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – A list of dephasing probabilities

- **X_pp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array where CPT superoperators in Pauli basis are stacked along the first axis.

Returns:  
The norm between the channel difference

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

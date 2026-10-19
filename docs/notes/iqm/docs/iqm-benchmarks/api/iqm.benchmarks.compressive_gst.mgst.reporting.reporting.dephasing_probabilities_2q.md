> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_probabilities_2q.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_probabilities_2q.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 82c3ad65d2533e2e3d0026fce0c1ac9324f727b18fade20493747c1aec0e42e2.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_probabilities_2q

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.dephasing_probabilities_2q(*X_opt_pp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X_ideal_pp: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Determines the local dephasing channel parameters which best describe the noise model.

Works for two qubit gates only

Parameters:  
- **X_opt_pp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array where reconstructed CPT superoperators in Pauli basis are stacked along the first axis.

- **X_ideal_pp** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array where target gate CPT superoperators in Pauli basis are stacked along the first axis.

Returns:  
The two best fit dephasing probabilities

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

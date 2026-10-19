> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.local_dephasing_pp.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.local_dephasing_pp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3672c4d917bd2e6f8027348453126726e7b1a2304b85fa8a015262e551258b55.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.local_dephasing_pp

iqm.benchmarks.compressive_gst.mgst.additional_fns.local_dephasing_pp(*prob_vec: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Returns the tensor product of single qubit dephasing channels in Pauli basis.

Parameters:  
**prob_vec** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – A list of dephasing probabilities

Returns:  
Process matrix of the tensor product of local dephasing channels

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

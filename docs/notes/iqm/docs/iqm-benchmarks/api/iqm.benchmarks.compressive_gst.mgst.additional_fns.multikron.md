> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.multikron.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.multikron.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5be30038d91d86d6b73634d4ccd46fd9349dde1dcd679d6d0f981222ee64c50f.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.multikron

iqm.benchmarks.compressive_gst.mgst.additional_fns.multikron(*matrix_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Computes the Kronecker product of all matrices in an array.

The order is matrix_array\[0\] otimes matrix_array\[1\] otimes …

Parameters:  
**matrix_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – An array containing matrices

Returns:  
The resulting tensor product (potentially a very large array)

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randHerm.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randHerm.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 accf331947139c0ca934672e744119618eea827c40f860a3eb7470f0bbbfa928.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.randHerm

iqm.benchmarks.compressive_gst.mgst.additional_fns.randHerm(*n: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate random square hermitian matrix.

Parameters:  
**n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Matrix dimension

Returns:  
Random hermitian matrix normalized in spectral norm

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

First a matrix with random complex entries is generated (see randvec function). This matrix is then projected onto the space of hermitian matrices and normalized in spectral norm.

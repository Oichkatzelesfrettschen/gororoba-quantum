> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randvec.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randvec.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e5f5fa7e858eefa812c14e6123f27e2b452e6897d866db4c5a86856823fca3c5.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.randvec

iqm.benchmarks.compressive_gst.mgst.additional_fns.randvec(*n: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate vector with real and imaginary part drawn from the normal distribution.

Parameters:  
**n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of elements for the random vector

Returns:  
Length n vector with complex entries whose real and imaginary part is independently drawn from the normal distribution with mean 0 and variance 1.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.depol.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.depol.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 26f4e037d77650b798a7d03d2ba911d03708141675864fcfbce1d9db87e18018.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.depol

iqm.benchmarks.compressive_gst.mgst.additional_fns.depol(*pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *p: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Kraus representation of depolarizing channel.

Parameters:  
- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Physical dimension

- **p** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Error probability

Returns:  
Each entry along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The depolarizing channel is defined as L(rho) = (1-p)\*rho + p/pdim\*Id.

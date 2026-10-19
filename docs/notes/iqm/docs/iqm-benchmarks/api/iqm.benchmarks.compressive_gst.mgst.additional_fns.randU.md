> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randU.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randU.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7c44ae13f5059907bfd5ad87bb326997c861e5dde25ddd9ae13a5c050d25adad.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.randU

iqm.benchmarks.compressive_gst.mgst.additional_fns.randU(*n: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 1*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generates random unitary from a random hermitian generator.

Parameters:  
- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Matrix dimension of the unitary

- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Parameter to control the norm of the hermitian generator

Returns:  
Matrix exponential of random hermitian matrix times the imaginary unit.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

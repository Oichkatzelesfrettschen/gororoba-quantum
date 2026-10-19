> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randHermGS.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.additional_fns.randHermGS.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3d460e37d18551834464d30ef064e437b6c6eb73582897a4b5abd1b6bee0f80f.

# iqm.benchmarks.compressive_gst.mgst.additional_fns.randHermGS

iqm.benchmarks.compressive_gst.mgst.additional_fns.randHermGS(*d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *r: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generates random set of operators that are hermiticity preserving.

Parameters:  
- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of gates

- **r** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Superoperator dimension of the gates given by the square of the physical dimension

Returns:  
Array where random hermiticity preserving operators are stacked along the first axis.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The function randHerm is used to generate random hermitian Choi matrices, whose indies are then rearanged to obtain random hermiticity preserving superoperators.

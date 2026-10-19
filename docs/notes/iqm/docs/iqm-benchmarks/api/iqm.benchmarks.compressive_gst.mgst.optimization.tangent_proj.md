> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.tangent_proj.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.tangent_proj.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6b2b302941d3c76e99ec4e5b7ebf8fc2b3c411f1cfdfb1b0668c94fe9528438f.

# iqm.benchmarks.compressive_gst.mgst.optimization.tangent_proj

iqm.benchmarks.compressive_gst.mgst.optimization.tangent_proj(*K: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *Z: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *d: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *rK: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Projection onto the local tangent space.

Parameters:  
- **K** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current position

- **Z** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the ambient space to be projected onto the tangent space at K

- **d** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of matrices which are projected (i.e. number of gates in the gate set)

- **rK** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Kraus rank of the gate set

Returns:  
Projection of Z onto the tangent space of the Stiefel manifold at position K

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Notes

The projection is done with respect to the canonical metrik.

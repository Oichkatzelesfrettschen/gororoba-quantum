> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_A_geodesic.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_A_geodesic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ff67637320e9cae319eadf8d3b5df0d9fffe0dec7d8d224f165681e64accc623.

# iqm.benchmarks.compressive_gst.mgst.optimization.update_A_geodesic

iqm.benchmarks.compressive_gst.mgst.optimization.update_A_geodesic(*A: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *H: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute a new point on the geodesic for the POVM parametrization.

Parameters:  
- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current position

- **H** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the tangent space at A and local direction of the geodesic

- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Geodesic curve parameter

Returns:  
New position given by A_new = A(a) with A(a) being a geodesic with A(0) = A, \[d/dt A\](https://docs.iqm.tech/4.7/iqm-benchmarks/api/0) = H

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

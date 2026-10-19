> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_K_geodesic.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_K_geodesic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 527138d240b3218ec90d30dcec4be2603c5f28191d58e817b04c03e85cafd605.

# iqm.benchmarks.compressive_gst.mgst.optimization.update_K_geodesic

iqm.benchmarks.compressive_gst.mgst.optimization.update_K_geodesic(*K: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *H: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute a new point on the geodesic.

Parameters:  
- **K** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current position

- **H** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the tangent space at K and local direction of the geodesic

- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Geodesic curve parameter

Returns:  
New position given by K_new = K(a) with K(a) being a geodesic with K(0) = K, \[d/dt K\](https://docs.iqm.tech/4.7/iqm-benchmarks/api/0) = H

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

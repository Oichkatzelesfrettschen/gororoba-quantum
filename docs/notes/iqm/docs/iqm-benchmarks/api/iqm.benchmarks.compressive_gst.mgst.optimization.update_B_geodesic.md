> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_B_geodesic.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.update_B_geodesic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0fe92b037fa05153cc41ad9c2141700025a19c1b5e08d97b44b2e76a987e8e8c.

# iqm.benchmarks.compressive_gst.mgst.optimization.update_B_geodesic

iqm.benchmarks.compressive_gst.mgst.optimization.update_B_geodesic(*B: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *H: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute a new point on the geodesic for the initial state parametrization.

Parameters:  
- **B** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current initial state parametrization

- **H** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the tangent space at B and local direction of the geodesic

- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Geodesic curve parameter

Returns:  
New position given by B_new = B(a) with B(a) being a geodesic with B(0) = B, \[d/dt B\](https://docs.iqm.tech/4.7/iqm-benchmarks/api/t=0) = H

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

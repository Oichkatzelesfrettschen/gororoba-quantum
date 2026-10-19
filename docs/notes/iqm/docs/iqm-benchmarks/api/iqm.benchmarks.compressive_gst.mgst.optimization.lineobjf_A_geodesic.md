> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_geodesic.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_geodesic.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7924a3c04ba53a4661e0f4429d0b125dcda5407eb00007a914eb9d4c6162c99e.

# iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_geodesic

iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_geodesic(*a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *H: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *A: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute objective function at position on geodesic for POVM parametrization.

Parameters:  
- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Geodesic curve parameter

- **H** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Element of the tangent space at A and local direction of the geodesic

- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current gate estimate

- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current position

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current initial state estimate

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row contains the gate indices of a gate sequence

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of measurement outcomes for sequences in J; The columns contain the outcome probabilities for different povm elements

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the log-likelihood objective function is used, otherwise the least squares objective function is used

Returns:  
Objective function value at new position along the geodesic

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.min_spectral_distance.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.min_spectral_distance.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6de3d32f282e65e98f269f099364b6cef8ab1296dfeadcdabb4e7234c317ca7a.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.min_spectral_distance

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.min_spectral_distance(*X1: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X2: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Computes the average absolute distance between the eigenvlues of two matrices.

The matrices are first diagonalized, then the eigenvalues are matched such that the average distance of matched eigenvalue pairs is minimal. The big advantage of this distance metric is that it is gauge invariant and it can thus be used to if the reconstructed gates are similar to the target gates before any gauge optimization.

Parameters:  
- **X1** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The first matrix

- **X2** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The second matrix

Returns:  
The minimal distance

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

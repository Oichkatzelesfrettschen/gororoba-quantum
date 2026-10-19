> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 38df142e44fa014481abb0cd008f362ec9ccb1346b8b6358bfc8fa43cd05f5d5.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf

iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Calculate the objective function value for matrices, POVM elements, and target values.

This function computes the objective function value based on input matrices X, POVM elements E, density matrix rho, and target values y.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 3D array containing the input matrices, of shape (n_matrices, n_rows, n_columns).

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the POVM elements, of shape (n_povm, r).

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 1D array representing the density matrix.

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the indices for which the objective function will be evaluated.

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of shape (n_povm, len(J)) containing the target values.

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the log-likelihood objective function is used, otherwise the least squares objective function is used

Returns:  
The objective function value for the given set of matrices, POVM elements, and target values, normalized by m and n_povm.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

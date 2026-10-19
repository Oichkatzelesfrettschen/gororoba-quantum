> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.dK.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.dK.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b42f4780c86a5efa0822952668608b4b018e5ad7a158656da2fdaf8d2590a590.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.dK

iqm.benchmarks.compressive_gst.mgst.low_level_jit.dK(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *K: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute the derivative of the objective function with respect to the Kraus tensor K.

This function calculates the derivative of the Kraus operator K, based on the input matrices X, E, and rho, as well as the isometry condition.

Args: X : The input matrix X, of shape (pdim, pdim). K : The Kraus operator K, reshaped to (d, rK, -1). E : A 2D array representing the POVM elements, of shape (n_povm, r). rho : A 1D array representing the density matrix. J : A 2D array representing the indices for which the derivatives will be computed. y : A 2D array of shape (n_povm, len(J)) containing the target values. mle : If True, the log-likelihood objective function is used, otherwise the least squares objective function is used

Returns:  
The derivative objective function with respect to the Kraus tensor K, reshaped to (d, rK, pdim, pdim), and scaled by 2/m/n_povm.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **K** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"))

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

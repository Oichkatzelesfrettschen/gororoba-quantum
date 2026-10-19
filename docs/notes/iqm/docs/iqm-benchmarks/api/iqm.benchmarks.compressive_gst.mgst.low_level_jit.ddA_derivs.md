> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddA_derivs.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddA_derivs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cb3e01237a4b6c2e28ddc0ef67c42e0a04fc4ddce58376b6041bc5e2ffaa1b4a.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddA_derivs

iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddA_derivs(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *A: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *B: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *n_povm: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Calculate all nonzero terms of the second derivatives with respect to the POVM tensor A.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The input matrix X, of shape (pdim, pdim).

- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 3D array of shape (n_povm, pdim, pdim) representing the POVM elements.

- **B** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of shape (pdim, pdim) representing the isometry matrix.

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the indices for which the derivatives will be computed.

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of shape (n_povm, len(J)) containing the target values.

- **n_povm** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of POVM elements.

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the log-likelihood objective function is used, otherwise the least squares objective function is used

Returns:  
- dA, the derivative w.r.t. A of shape (n_povm, pdim, pdim).

- dMdM, the product of the measurement map derivatives dM and dM, of shape (n_povm, r, r).

- dMconjdM, the product of the conjugate of dM and dM, of shape (n_povm, r, r).

- dconjdA, the product of the conjugate of dA, of shape (n_povm, r, r).

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

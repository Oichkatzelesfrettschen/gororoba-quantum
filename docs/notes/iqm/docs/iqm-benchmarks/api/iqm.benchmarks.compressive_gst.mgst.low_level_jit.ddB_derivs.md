> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddB_derivs.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddB_derivs.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bbaaa86fa55490394bce502c8516b9297768ec36e874c13172649d67d1230912.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddB_derivs

iqm.benchmarks.compressive_gst.mgst.low_level_jit.ddB_derivs(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *A: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *B: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *r: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]  
Calculate all nonzero terms of the second derivative with respect to the state tensor B.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The input matrix X, of shape (pdim, pdim).

- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 3D array of shape (n_povm, pdim, pdim) representing the POVM elements.

- **B** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of shape (pdim, pdim) representing the isometry matrix.

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the indices for which the derivatives will be computed.

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of shape (n_povm, len(J)) containing the target values.

- **r** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The rank of the problem.

- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The dimension of the input matrices A and B.

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the log-likelihood objective function is used instead of the least squares objective function

Returns:  
- dB: The derivative w.r.t. B, of shape (pdim, pdim).

- dMdM: The product of the derivatives dM and dM, of shape (r, r).

- dMconjdM: The product of the conjugate of dM and dM, of shape (r, r).

- dconjdB: The mixed second derivative of by dB and dB\*, of shape (r, r).

Return type:  
A tuple containing the computed derivatives

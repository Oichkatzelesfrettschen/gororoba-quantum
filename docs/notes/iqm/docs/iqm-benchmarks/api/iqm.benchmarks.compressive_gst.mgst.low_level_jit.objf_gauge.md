> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf_gauge.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf_gauge.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 adfc086e3fb14e1d012ed00204ff9f9ef8a3bf3760013ea9affe5ff4d74844b0.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf_gauge

iqm.benchmarks.compressive_gst.mgst.low_level_jit.objf_gauge(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *U: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *weights: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Calculate the objective function with respect to a unitary gauge transformation.

This function computes the weighted sum of squared Frobenius norm differences between the gauge-transformed gate set and the target gate set, including gates, POVM elements, and the initial state.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 3D array containing the input matrices, of shape (n_gates, pdim\*\*2, pdim\*\*2).

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the POVM elements, of shape (n_povm, pdim\*\*2).

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 1D array representing the density matrix, of shape (pdim\*\*2,).

- **X_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 3D array containing the target gate matrices, of shape (n_gates, pdim\*\*2, pdim\*\*2).

- **E_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array representing the target POVM elements, of shape (n_povm, pdim\*\*2).

- **rho_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 1D array representing the target density matrix, of shape (pdim\*\*2,).

- **U** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D unitary matrix representing the gauge transformation, of shape (pdim, pdim).

- **weights** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – A list of weights for the different components. Length must be n_gates + 2. If None or incorrect length, defaults to all ones.

Returns:  
The normalized objective function value, scaled by pdim\*\*2.

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

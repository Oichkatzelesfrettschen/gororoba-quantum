> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.dB.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.low_level_jit.dB.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e632a9b99fafb548ce3b5a108bc0899348011fc8a32037b8221957076f295e64.

# iqm.benchmarks.compressive_gst.mgst.low_level_jit.dB

iqm.benchmarks.compressive_gst.mgst.low_level_jit.dB(*X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *A: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *B: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Compute the derivative of the objective function with respect to the state tensor B.

Parameters:  
- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of input matrices.

- **A** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of measurement operators.

- **B** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of quantum states.

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of indices corresponding to the sequence of operations.

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array of observed probabilities.

- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Dimension of the density matrices.

Returns:  
Derivative of the objective function with respect to the state tensor B.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

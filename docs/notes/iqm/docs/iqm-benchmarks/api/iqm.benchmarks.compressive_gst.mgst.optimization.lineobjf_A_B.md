> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_B.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_B.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5ecb8dbb3f42770f491e813360cfc0efdac2b72e9358d52931e25c7990972730.

# iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_B

iqm.benchmarks.compressive_gst.mgst.optimization.lineobjf_A_B(*a: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *v: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *delta_v: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *C: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *argument: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Compute objective function at translated position.

Parameters:  
- **a** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Step size

- **v** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current position

- **delta_v** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Step direction

- **X** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current gate estimate

- **C** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current initial state/POVM estimate that is not updated

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of measurement outcomes for sequences in J; The columns contain the outcome probabilities for different povm elements

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row contains the gate indices of a gate sequence

- **argument** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Takes the following options: “E” or “rho”, and indicates which gate set component is optimized over

Returns:  
Objective function value at new position v + a\*delta_v

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

Notes

This function is used for the line search with linear updates v_new = v + a\*delta_v, where v can be either the POVM estimate or the state estimate.

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fadad883b28e14526b2dc5252040e1d17c50e3021c861e5de54160303cc24a06.

# iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess

iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess(*K: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *lam: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.001*, *ls: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'COBYLA'*, *fixed_gates: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Riemannian saddle free Newton step on each gate individually.

Parameters:  
- **K** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current POVM estimate

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current initial state estimate

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of measurement outcomes for sequences in J; Each column contains the outcome probabilities for a fixed sequence

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row contains the gate indices of a gate sequence

- **lam** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Damping parameter for dampled Newton method

- **ls** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Line search method, takes “method” arguments of scipy.optimize.minimize

- **fixed_gates** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – List of gate indices which are not optimized over and assumed as fixed

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to use MLE objective function or least squares objective function

Returns:  
Updated Kraus parametrizations

Return type:  
K_new

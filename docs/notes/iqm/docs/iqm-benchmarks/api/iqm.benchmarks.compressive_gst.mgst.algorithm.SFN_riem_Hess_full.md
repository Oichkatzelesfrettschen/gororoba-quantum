> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 485a52a5859d8413d8ca3d99c21eb15f1e9a8fdca925c90f2d38af0fed8a09c5.

# iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full

iqm.benchmarks.compressive_gst.mgst.algorithm.SFN_riem_Hess_full(*K: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *J: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *lam: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.001*, *ls: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'COBYLA'*, *mle: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Riemannian saddle free Newton step on product manifold of all gates.

Parameters:  
- **K** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Each subarray along the first axis contains a set of Kraus operators. The second axis enumerates Kraus operators for a gate specified by the first axis.

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current POVM estimate

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Current initial state estimate

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array of measurement outcomes for sequences in J; Each column contains the outcome probabilities for a fixed sequence

- **J** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row contains the gate indices of a gate sequence

- **lam** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Damping parameter for dampled Newton method

- **ls** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Line search method, takes “method” arguments of scipy.optimize.minimize

- **mle** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to use MLE objective function or least squares objective function

Returns:  
Updated Kraus parametrizations

Return type:  
K_new

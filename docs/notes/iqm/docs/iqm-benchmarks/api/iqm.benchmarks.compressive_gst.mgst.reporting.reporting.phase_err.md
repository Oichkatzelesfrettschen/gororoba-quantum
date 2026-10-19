> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.phase_err.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.phase_err.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f90382ff29565f31f369101898a58a9330434e910873d338829fa9faa9305cb8.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.phase_err

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.phase_err(*angle: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *U: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *U_t: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")  
Computes norm between two input unitaries after a global phase is added to one of them.

Parameters:  
- **angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – The global phase angle (in rad)

- **U** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The first unitary matrix

- **U_t** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The second unitary matrix (typically the a target gate)

Returns:  
The norm of the difference

Return type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

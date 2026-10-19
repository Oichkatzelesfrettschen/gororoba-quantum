> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad9f7e61a4ff9f29e4c23679efd1033e682fb955dbb98eb18969fb2492b42ba2.

# iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual

iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual(*params: Parameters*, *x: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Calculate total residual for fits of func to several data sets.

Parameters:  
- **params** (*Parameters*) – lmfit Parameters object containing all parameter values for all datasets.

- **x** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Independent variable values.

- **data** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row represents a dataset to fit.

- **func** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The fit function to use for calculating residuals.

Returns:  
Flattened 1D array of residuals for all datasets.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

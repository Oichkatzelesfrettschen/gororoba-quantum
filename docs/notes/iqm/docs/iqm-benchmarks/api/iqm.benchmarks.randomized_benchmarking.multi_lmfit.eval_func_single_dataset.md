> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b12932f55eb0935f198d892c89557a5907167b16e91790e375a6e596436c5caa.

# iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset

iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset(*func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*, *params: Parameters*, *i: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *x: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Returns the evaluation of the fit function for a single dataset.

Parameters:  
- **func** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The fit function to evaluate.

- **params** (*Parameters*) – lmfit Parameters object containing all parameter values.

- **i** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Index of the dataset (0-based).

- **x** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Independent variable values.

Returns:  
Evaluated function values for the given dataset.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

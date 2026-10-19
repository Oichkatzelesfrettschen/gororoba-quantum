> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.lmfit_minimizer.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.lmfit_minimizer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c49d86a5c227c3cf2e581bee6248d85ae6d48ddf11289edc7640c58695bae9da.

# iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.lmfit_minimizer

iqm.benchmarks.randomized_benchmarking.randomized_benchmarking_common.lmfit_minimizer(*fit_parameters: Parameters*, *fit_data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *depths: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*) → MinimizerResult  
Perform minimization using lmfit.

Parameters:  
- **fit_parameters** (*Parameters*) – the parameters to fit

- **fit_data** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – the data to fit

- **depths** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – the depths of the RB experiment

- **func** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – the model function for fitting

Returns:  
The result of the minimization

Return type:  
*MinimizerResult*

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2611410a89f40ceed19fd009e2a1357b2e15e62d55ac68c2e03cef54cc98c746.

# iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params

iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params(*func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*, *data: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *initial_guesses: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *constraints: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *simultaneously_fit_vars: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → Parameters  
Generates lmfit Parameter object with parameters for each line to fit.

Parameters:  
- **func** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The fit function whose parameters will be extracted.

- **data** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 2D array where each row represents a dataset to fit.

- **initial_guesses** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*) – Optional dictionary mapping parameter names to initial values.

- **constraints** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]* *\|* *None*) – Optional dictionary mapping parameter names to constraint dicts with ‘min’ and ‘max’ keys.

- **simultaneously_fit_vars** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Optional list of parameter names that should be fit as a single parameter across all datasets.

Returns:  
lmfit Parameters object with parameters for each dataset, with suffixes \_1, \_2, etc.

Return type:  
*Parameters*

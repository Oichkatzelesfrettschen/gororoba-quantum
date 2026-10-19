> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_1d_fit.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_1d_fit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 41b69072af6bbbae39ca17f44248dc30e1d30bf9af97aa6266521de510687092.

# iqm.cpc.core.dataset.compute_1d_fit

iqm.cpc.core.dataset.compute_1d_fit(*x_values*, *y_values*, *model*, *estimates*, *\*\*curve_fit_kwargs*)  
Compute and return the fit results for a 1-dimensional array of values.

Parameters:  
- **x_values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")) – The ‘true’ data which the curve needs to fit; the independent variable

- **y_values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* [*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")) – Result values of the fit or ‘dependent data’

- **model** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The function to use for fitting

- **estimates** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Guesses of possible parameter values for the fit function

- **curve_fit_kwargs** – Additional named arguments for the curve fit function

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

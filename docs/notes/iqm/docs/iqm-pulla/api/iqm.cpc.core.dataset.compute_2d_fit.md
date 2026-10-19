> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_2d_fit.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.compute_2d_fit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 16ff8afe5f5541addd2f3e36bea5e735382034eec5f0d1fbc50306f5d55c4a57.

# iqm.cpc.core.dataset.compute_2d_fit

iqm.cpc.core.dataset.compute_2d_fit(*x_values*, *y_values*, *z_values*, *model*, *estimates*, *cloned_arguments=None*, *only_index_y=False*, *\*\*curve_fit_kwargs*)  
Compute and return the fit results for a 2-dimensional array of values.

Parameters:  
- **x_values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The primary independent variable

- **y_values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The secondary independent variable, also used as an index

- **z_values** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The dependent variable

- **model** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The function to use for fitting

- **estimates** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")) – Guesses of possible parameter values for the fit function

- **cloned_arguments** (*None* *\|* [*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – list of arguments to the model which should be fitted separately for each y value

- **only_index_y** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – TODO

- **curve_fit_kwargs** – Additional named arguments for the curve fit function

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.apply_along_coordinate.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.apply_along_coordinate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fe2f60bb33f9fc9b122d5729c290c4cea680309d4bd36d5a19ed1b6fb1ab1990.

# iqm.cpc.core.dataset.apply_along_coordinate

iqm.cpc.core.dataset.apply_along_coordinate(*data_array: DataArray*, *coord: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\], [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]\]*, *returns: [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *add_to: Dataset \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *result_parameter: [Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *prefix: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = ''*) → DataArray\
iqm.cpc.core.dataset.apply_along_coordinate(*data_array: DataArray*, *coord: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\], [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]\]*, *returns: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *add_to: Dataset \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *result_parameter: [Parameter](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "(in iqm-exa-common v29.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *prefix: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = ''*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[DataArray, ...\]  
Apply a 1-dimensional function along a selected coordinate axis inside a Nd data array.

Computes the result of function `func` along selected coordinate `coord`. The function should map a 1d array to a new array of equal size. In addition, it may return a dict of scalars for each function call.

The main use case for this is fitting, where `func` returns a fit to some raw data, plus the found fit parameters.

For example, if `data_array` has dimensions A, B, and C, and we apply a fitting function along B, the fitter `func` function is evaluated for each coordinate tuple spanned by A and C and gets arrays of len(B) as input. The result has the same shape and dimensions as `data_array`. Optionally, the fit parameters evaluated at each A,C-coordinate tuple can be returned as separate data arrays if specified in `returns`. These have the shape (len(A), len(C)) and the names are the fit parameters, i.e. keys returned by `func`.

Example

```
def my_fitter(x, y):
    # ... fit function f(x; a) to data y ...
    # Let's say a=5 produces the best fit.
    return {"a": 5}, np.random.rand(len(y))

my_data = xarray.DataArray(
    np.random.rand(5, 3),
    dims=["x", "color"],
    coords=[[1, 2, 3, 4, 5], [0, 125, 255]]
)

fit, a = apply_along_coordinate(
    data_array=my_data,
    coord="x",
    func=my_fitter,
    returns=["a"]
)
assert my_data.sizes == fit.sizes == {'x': 5, 'color': 3}
assert a.sizes == {"color": 3}
```

Parameters:  
- **data_array** – DataArray that contains the Nd data to operate on.

- **coord** – Name of the coordinate over which the 1d operation is performed. Can be any coordinate or dimension of `data_array`.

- **func** – A function that takes 1-dimensional data in format (x, y) and returns a dictionary containing the extra results (e.g. fit parameters), and the computed 1-d array.

- **returns** – Names of extra results to return. Each string should match one of the keys returned by `func`. The arrays are added to the result tuple in the same order as given in `returns`. Note that the computed array is always returned first and does not need to be specified.

- **add_to** – If given, the returned arrays are added to this dataset. The dataset is modified as a side effect.

- **result_parameter** – This parameter represents the computed data. By default will be generated by [`generate_fit_parameter()`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.generate_fit_parameter.html#iqm.cpc.core.dataset.generate_fit_parameter "iqm.cpc.core.dataset.generate_fit_parameter").

- **prefix** – If given, the names of all arrays in `returns` are prefixed with `f"{prefix}_"`. Used to avoid name clashes with existing data variables.

Returns:  
Data arrays depending on `returns`. The first array is always the result produced by applying `func` along the axis `coord`. It has the same \\N\\ dimensions as ``` data_array`. The other arrays have :math:`N-1` dimensions and represent the extras requested in ``returns ```.

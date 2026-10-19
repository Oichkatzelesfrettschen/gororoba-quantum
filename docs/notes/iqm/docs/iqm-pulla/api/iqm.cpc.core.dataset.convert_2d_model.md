> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.convert_2d_model.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.convert_2d_model.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 71cdd6d39f2abff4921a960c220a2885c38bc8a77efb59ddf9baa52742a7479d.

# iqm.cpc.core.dataset.convert_2d_model

iqm.cpc.core.dataset.convert_2d_model(*model*, *cloned_arguments_indices=None*)  
Convert a function to a format usable with curve_fit, by flattening the model by the second dimension.

Parameters:  
- **model** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[...\],* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Original function taking the x, y independent variables, and variadic args.

- **cloned_arguments_indices** (*None* *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Indices of the arguments we would like to clone in the list of all the arguments of the original model.

Returns:  
The new model function, taking x, y, y_indices, and variadic args of the original model.

Return type:  
[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")\[\[…\], [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

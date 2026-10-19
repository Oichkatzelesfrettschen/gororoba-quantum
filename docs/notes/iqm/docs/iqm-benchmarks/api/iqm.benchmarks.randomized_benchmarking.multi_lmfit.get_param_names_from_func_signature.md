> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 42c06071187b62b2aaeb6c745b1220849163f79644d51268e9746f6040d0638e.

# iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature

iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature(*func: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]  
Gets the function parameter names from its signature.

Parameters:  
**func** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The function to extract parameter names from.

Returns:  
- The name of the independent parameter (first parameter)

- A list of fit parameter names (remaining parameters)

Return type:  
A tuple containing

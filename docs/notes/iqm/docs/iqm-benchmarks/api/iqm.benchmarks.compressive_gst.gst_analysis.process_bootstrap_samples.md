> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_bootstrap_samples.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_bootstrap_samples.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 86e86880e1802d5c43dca7f61b91d032ad62124c3ac911c6e607a45c54bf40fb.

# iqm.benchmarks.compressive_gst.gst_analysis.process_bootstrap_samples

iqm.benchmarks.compressive_gst.gst_analysis.process_bootstrap_samples(*y_sampled: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *attrs: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *init: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *target_model: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")\]  
Process a single bootstrap sample for Gate Set Tomography.

This function performs a GST analysis on a sampled dataset, applies gauge optimization, and generates result reports.

Parameters:  
- **y_sampled** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A 2D array of measurement outcomes for sequences in J; Each column contains the outcome probabilities for a fixed sequence

- **attrs** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Dictionary containing configuration parameters for the GST algorithm

- **init** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – Initial values for the gate set optimization \[K, E, rho\]

- **target_model** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – The target gate set model in format \[X_target, E_target, rho_target\]

- **identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – String identifier for the current qubit layout

Returns:  
- X_opt_pp, array of optimized gate tensors in Pauli basis

- E_opt_pp, optimized POVM elements in Pauli basis

- rho_opt_pp, optimized initial state in Pauli basis

- df_g.values, array of gate quality measures

- df_o.values, array of SPAM and other quality measures

- Whether the optimization successfully converged below expected least-squares error.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")\]

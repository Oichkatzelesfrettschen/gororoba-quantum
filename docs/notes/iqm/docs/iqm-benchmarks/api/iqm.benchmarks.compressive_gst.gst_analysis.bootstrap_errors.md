> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.bootstrap_errors.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.bootstrap_errors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b80efb07863ac0d8c3d1e88d94984e01c070669e3eddbade879518893cc9174d.

# iqm.benchmarks.compressive_gst.gst_analysis.bootstrap_errors

iqm.benchmarks.compressive_gst.gst_analysis.bootstrap_errors(*dataset: Dataset*, *y: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *gate_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *target_gate_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]*, *identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *parametric: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Resamples circuit outcomes a number of times and computes GST estimates for each repetition.

All results are then returned in order to compute bootstrap-error bars for GST estimates. Parametric bootstrapping uses the estimated gate set to create a newly sampled data set. Non-parametric bootstrapping uses the initial dataset and resamples according to the corresp. outcome probabilities. Each bootstrap run is initialized with the estimated gate set in order to save processing time.

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment and configurations

- **y** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The circuit outcome probabilities as a num_povm x num_circuits array

- **gate_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – The estimated gate set in format \[K, X, E, rho\]

- **target_gate_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\]*) – The target gate set in format \[X_target, E_target, rho_target\]

- **identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The string identifier of the current benchmark

- **parametric** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If set to True, parametric bootstrapping is used, else non-parametric bootstrapping. Default: False

Returns:  
- X_array, containing all estimated gate tensors of different bootstrapping repetitions along first axis

- E_array, containing all estimated POVM tensors of different bootstrapping repetitions along first axis

- rho_array, containing all estimated initial states of different bootstrapping repetitions along first axis

- df_g_array, containing gate quality measures of bootstrapping repetitions

- df_o_array, containing SPAM and other quality measures of bootstrapping repetitions

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

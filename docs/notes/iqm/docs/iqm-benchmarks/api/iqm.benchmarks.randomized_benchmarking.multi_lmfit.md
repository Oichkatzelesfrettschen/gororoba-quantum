> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2a94be78014819fe99b3b3ec884d7d592a115098bc8ad96238a2bd95d5f53708.

# iqm.benchmarks.randomized_benchmarking.multi_lmfit

Lmfit for multiple datasets.

Generalized and extended version of the shown example in the lmfit documentation: [https://lmfit.github.io/lmfit-py/examples/example_fit_multi_datasets.html#sphx-glr-examples-example-fit-multi-datasets-py](https://lmfit.github.io/lmfit-py/examples/example_fit_multi_datasets.html#sphx-glr-examples-example-fit-multi-datasets-py)

Functions

|  |  |
|----|----|
| [`create_multi_dataset_params`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params.html#iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params "iqm.benchmarks.randomized_benchmarking.multi_lmfit.create_multi_dataset_params")(func, data\[, ...\]) | Generates lmfit Parameter object with parameters for each line to fit. |
| [`eval_func_single_dataset`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset.html#iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset "iqm.benchmarks.randomized_benchmarking.multi_lmfit.eval_func_single_dataset")(func, params, i, x) | Returns the evaluation of the fit function for a single dataset. |
| [`get_param_names_from_func_signature`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature.html#iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature "iqm.benchmarks.randomized_benchmarking.multi_lmfit.get_param_names_from_func_signature")(func) | Gets the function parameter names from its signature. |
| [`multi_dataset_residual`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual.html#iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual "iqm.benchmarks.randomized_benchmarking.multi_lmfit.multi_dataset_residual")(params, x, data, func) | Calculate total residual for fits of func to several data sets. |

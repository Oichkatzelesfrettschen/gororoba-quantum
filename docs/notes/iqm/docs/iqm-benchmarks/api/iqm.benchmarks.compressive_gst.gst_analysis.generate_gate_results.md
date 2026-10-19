> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_gate_results.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_gate_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 81aab12ddba96e382058ab1b6435c10b5f7663a90fdbfe592cf5bdae377d6a1f.

# iqm.benchmarks.compressive_gst.gst_analysis.generate_gate_results

iqm.benchmarks.compressive_gst.gst_analysis.generate_gate_results(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *df_g: DataFrame*, *X_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *bootstrap_results: [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] = None*, *max_evals: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 6*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[DataFrame, DataFrame\]  
Produces all result tables for arbitrary Kraus rank estimates.

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment and configurations

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of qubits for the current GST experiment

- **df_g** (*DataFrame*) – The dataframe with properly formated results

- **X_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The gate set after gauge optimization

- **E_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – An array containg all the POVM elements as matrices after gauge optimization

- **rho_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The density matrix after gauge optmization

- **bootstrap_results** (*None* *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – If provided, contains the results of the bootstrap analysis.

- **max_evals** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The maximum number of eigenvalues of the Choi matrices which are returned.

Returns:  
- df_g_final, the dataframe with properly formated results of standard gate errors

- df_g_evals_final, a dataframe containing eigenvalues of the Choi matrices for all gates

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*DataFrame*, *DataFrame*\]

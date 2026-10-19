> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_unit_rank_gate_results.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.generate_unit_rank_gate_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f4dc053d0813800324a958ed9f018df6b18a3dddd84e843df126c507111cc442.

# iqm.benchmarks.compressive_gst.gst_analysis.generate_unit_rank_gate_results

iqm.benchmarks.compressive_gst.gst_analysis.generate_unit_rank_gate_results(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *df_g: DataFrame*, *X_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *K_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *bootstrap_results: [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[DataFrame, DataFrame, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]  
Produces all result tables for Kraus rank 1 estimates.

This includes parameters of the Hamiltonian generators in the Pauli basis for all gates, as well as the usual performance metrics (Fidelities and Diamond distances). If bootstrapping data is available, error bars will also be generated.

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment and configurations

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The list of qubits for the current GST experiment

- **df_g** (*DataFrame*) – The dataframe with properly formated results

- **X_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The gate set after gauge optimization

- **K_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – The Kraus operators of all target gates, used to compute distance measures.

- **bootstrap_results** (*None* *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – If provided, contains the results of the bootstrap analysis.

Returns:  
- df_g_final, the dataframe with properly formatted results of standard gate errors

- df_g_rotation, a dataframe containing Hamiltonian (rotation) parameters

- Dictionary containing the Hamiltonian parameters for each gate in the Pauli basis. The keys are gate labels and the values are dictionaries with the parameters.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*DataFrame*, *DataFrame*, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]

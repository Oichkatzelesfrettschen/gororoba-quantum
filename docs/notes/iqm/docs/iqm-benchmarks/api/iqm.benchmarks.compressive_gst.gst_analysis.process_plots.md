> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_plots.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_plots.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ad028bbded4fe27cc46d77ca313d7a2389922815e096885b7b98fbc1fcf1b9dc.

# iqm.benchmarks.compressive_gst.gst_analysis.process_plots

iqm.benchmarks.compressive_gst.gst_analysis.process_plots(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *results_dict: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *df_g_final: DataFrame*, *df_o_final: DataFrame*, *df_g_evals_final: DataFrame*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]  
Process and generate all plots for a single qubit layout.

This function creates various visualization plots for gate set tomography results, including gate metrics tables, process matrices, and SPAM (State Preparation And Measurement) matrices in both real and imaginary parts.

Parameters:  
- **dataset** (*Dataset*) – Dataset containing experimental data and configuration attributes

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – List of qubit indices defining the current layout

- **results_dict** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Dictionary containing gauge-optimized gates, POVM elements, and states in both standard and Pauli basis

- **df_g_final** (*DataFrame*) – DataFrame containing gate metrics such as fidelity and diamond distance

- **df_o_final** (*DataFrame*) – DataFrame containing non-gate metrics such as SPAM errors

- **df_g_evals_final** (*DataFrame*) – DataFrame containing Choi matrix eigenvalues (can be empty)

Returns:  
Dictionary mapping plot names to matplotlib Figure objects. Keys follow the pattern `f"layout_{qubit_layout}_{plot_type}"`.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]

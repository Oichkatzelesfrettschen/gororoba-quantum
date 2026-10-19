> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_layout.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.process_layout.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4b1be65c07453aea5ef7a0f31be2fa1b1005007e550d63576799be6ec443774e.

# iqm.benchmarks.compressive_gst.gst_analysis.process_layout

iqm.benchmarks.compressive_gst.gst_analysis.process_layout(*args: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Dataset, [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[BenchmarkObservation](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")\], DataFrame, DataFrame, DataFrame\]  
Process a single qubit layout for Gate Set Tomography analysis.

This function performs the full GST workflow for a single qubit layout: 1. Convert counts to mGST format 2. Run mGST reconstruction 3. Perform gauge optimization 4. Generate reports and metrics 5. Run bootstrap analysis if configured 6. Format results into dataframes and observations

Parameters:  
**args** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[Dataset,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – containing: dataset: xr.Dataset, qubit_layout: List\[int\], pdim: int

Returns:  
- The input qubit layout being processed

- Dictionary containing all raw and processed results

- List of benchmark observations for this layout

- df_g_final, DataFrame containing gate metrics (fidelity, diamond distance, etc.)

- df_o_final, DataFrame containing non-gate metrics (SPAM errors, fit quality)

- df_g_evals, DataFrame containing Choi matrix eigenvalues (for rank \> 1)

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*BenchmarkObservation*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")\], *DataFrame*, *DataFrame*, *DataFrame*\]

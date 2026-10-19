> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.pandas_results_to_observations.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.gst_analysis.pandas_results_to_observations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 598a97808bc95d69644a5ab2464aa4da960246d69d244593dc2af66b67b4fb58.

# iqm.benchmarks.compressive_gst.gst_analysis.pandas_results_to_observations

iqm.benchmarks.compressive_gst.gst_analysis.pandas_results_to_observations(*dataset: Dataset*, *df_g: DataFrame*, *df_o: DataFrame*, *identifier: [BenchmarkObservationIdentifier](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[BenchmarkObservation](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")\]  
Converts high level GST results from a pandas Dataframe to a simple observation dictionary.

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment and configurations

- **df_g** (*DataFrame*) – The dataframe with properly formated gate results

- **df_o** (*DataFrame*) – The dataframe with properly formated non-gate results like SPAM error measures or fit quality.

- **identifier** ([*BenchmarkObservationIdentifier*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier")) – An identifier object for the current GST run

Returns:  
List of observations converted from the pandas dataframes

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*BenchmarkObservation*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")\]

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d5b1b6399b710120581364439ea13b8d1b11406eaafa95d51f0b880fbb06ce63.

# iqm.benchmarks.benchmark_definition

Implementation of the base class for defining a benchmark.

Functions

|  |  |
|----|----|
| [`add_counts_to_dataset`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.add_counts_to_dataset.html#iqm.benchmarks.benchmark_definition.add_counts_to_dataset "iqm.benchmarks.benchmark_definition.add_counts_to_dataset")(counts, identifier, ...) | Adds the counts from a cortex job result to the given dataset. |
| [`default_analysis_function`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.default_analysis_function.html#iqm.benchmarks.benchmark_definition.default_analysis_function "iqm.benchmarks.benchmark_definition.default_analysis_function")(result) | The default analysis that only pass the result through. |
| [`merge_datasets_dac`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.merge_datasets_dac.html#iqm.benchmarks.benchmark_definition.merge_datasets_dac "iqm.benchmarks.benchmark_definition.merge_datasets_dac")(datasets) | Merges a list of datasets recursively to minimize dataset sizes during merge. |
| [`show_figure`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.show_figure.html#iqm.benchmarks.benchmark_definition.show_figure "iqm.benchmarks.benchmark_definition.show_figure")(fig) | Shows a closed figure. |

Classes

|  |  |
|----|----|
| [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")(backend, configuration, \*\*kwargs) | A base class for running Qiskit-based Benchmark experiments. |
| [`BenchmarkAnalysisResult`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")(dataset, circuits, ...) | A dataclass storing the results of the analysis. |
| [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")(\*, benchmark\[, ...\]) | Benchmark configuration base. |
| [`BenchmarkObservation`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservation.html#iqm.benchmarks.benchmark_definition.BenchmarkObservation "iqm.benchmarks.benchmark_definition.BenchmarkObservation")(name, value, identifier) | Dataclass to store the main results of a single run of a Benchmark. |
| [`BenchmarkObservationIdentifier`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier.html#iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier "iqm.benchmarks.benchmark_definition.BenchmarkObservationIdentifier")(\[...\]) | Identifier for observations for ease of use. |
| [`BenchmarkRunResult`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")(dataset, circuits) | A dataclass that stores the results of a single run of a Benchmark. |

Inheritance

![Inheritance diagram of iqm.benchmarks.benchmark_definition](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-a16b8492267cd0f1b3120d6f533bd51d6be9ffcf.png)

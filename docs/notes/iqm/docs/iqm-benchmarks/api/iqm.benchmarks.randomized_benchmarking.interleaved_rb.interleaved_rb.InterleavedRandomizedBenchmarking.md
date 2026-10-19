> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 39424f0fb9969b141b73af1d9fb9a06b015db15c1e4cebff32ca56835559152f.

# iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking

*class* iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [InterleavedRBConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Interleaved RB estimates the average gate fidelity of a specific Clifford gate.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_circuits_to_dataset`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.add_all_circuits_to_dataset "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.add_all_circuits_to_dataset")(dataset) | Adds all generated circuits during execution to the dataset variable. |
| [`add_all_meta_to_dataset`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.add_all_meta_to_dataset "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.analysis_function "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.analysis_function")(run) | Analysis function for an Interleaved RB experiment. |
| [`execute`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.execute "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.execute")(backend) | Executes the benchmark. |
| [`name`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.name "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*InterleavedRBConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for an Interleaved RB experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – An interleaved RB experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to Interleaved RB

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Returns the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

add_all_meta_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Adds all configuration metadata and circuits to the dataset variable.

Parameters:  
**dataset** (*Dataset*) – The xarray dataset

Return type:  
None

add_all_circuits_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Adds all generated circuits during execution to the dataset variable.

Parameters:  
**dataset** (*Dataset*) – The xarray dataset

Return type:  
None

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

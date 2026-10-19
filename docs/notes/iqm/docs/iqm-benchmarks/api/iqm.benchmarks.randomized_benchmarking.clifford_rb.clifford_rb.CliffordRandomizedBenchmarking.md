> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 95c9706e7e93a5114836bcb3b5ff305efcad99a65c316a2a67416a70336ce6a6.

# iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking

*class* iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [CliffordRBConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Clifford RB estimates the average gate fidelity of the n-qubit Clifford group.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_circuits_to_dataset`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.add_all_circuits_to_dataset "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.add_all_circuits_to_dataset")(dataset) | Adds all generated circuits during execution to the dataset variable. |
| [`add_all_metadata_to_dataset`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.add_all_metadata_to_dataset "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.add_all_metadata_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.analysis_function "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.analysis_function")(run) | Analysis function for a Clifford RB experiment. |
| [`execute`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.execute "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.execute")(backend) | Executes the benchmark. |
| [`name`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.name "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*CliffordRBConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a Clifford RB experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A Clifford RB experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to Clifford RB

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Returns the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

add_all_metadata_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
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

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f0712d035e4f3c3e4bc21fd8cca723d46f48b3f5990856ba4f728e820ca49734.

# iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark

*class* iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [EPLGConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.html#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

EPLG estimates the layer fidelity of native 2Q gate layers.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.add_all_meta_to_dataset "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.analysis_function "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.analysis_function")(run) | EPLG analysis function. |
| [`execute`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.execute "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.execute")(backend) | Execute the EPLG Benchmark. |
| [`name`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.name "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.name")() | Returns the name of the benchmark. |
| [`validate_custom_qubits_array`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.validate_custom_qubits_array "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.validate_custom_qubits_array")() | Validates the custom qubits array input . |
| [`validate_random_chain_inputs`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.validate_random_chain_inputs "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark.validate_random_chain_inputs")() | Validates inputs for chain sampling. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*EPLGConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.html#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
EPLG analysis function.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – The result of the benchmark run.

Returns:  
AnalysisResult corresponding to DRB.

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

validate_custom_qubits_array() → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validates the custom qubits array input .

Return type:  
None

validate_random_chain_inputs() → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validates inputs for chain sampling.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the chain inputs are beyond general or EPLG criteria.

Return type:  
None

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Execute the EPLG Benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

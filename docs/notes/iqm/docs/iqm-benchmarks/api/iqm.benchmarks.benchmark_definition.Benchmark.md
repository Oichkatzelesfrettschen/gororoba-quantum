> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3c0701d0062c7efd7555eb6d5a75c4d496645586e2c923c608052280fec70640.

# iqm.benchmarks.benchmark_definition.Benchmark

*class* iqm.benchmarks.benchmark_definition.Benchmark(*backend: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *configuration: [BenchmarkConfigurationBase](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")*, *\*\*kwargs: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*)  
Bases: [`ABC`](https://docs.python.org/3.11/library/abc.html#abc.ABC "(in Python v3.11)")

A base class for running Qiskit-based Benchmark experiments.

In order to write a new benchmark, it is recommended to derive a class from this baseclass. A new benchmark is defined by deriving from this base class and implementing the execute method. Additionally, a custom analysis for the benchmark can be implemented by giving the pointer to the analysis method in `analysis_function` field. The given analysis_function should accept `AnalysisResult` as its input and return the final result.

Attributes

|                   |     |
|-------------------|-----|
| `default_options` |     |
| `options`         |     |

Methods

|  |  |
|----|----|
| [`analysis_function`](#iqm.benchmarks.benchmark_definition.Benchmark.analysis_function "iqm.benchmarks.benchmark_definition.Benchmark.analysis_function")(result) | The default analysis that only pass the result through. |
| [`analyze`](#iqm.benchmarks.benchmark_definition.Benchmark.analyze "iqm.benchmarks.benchmark_definition.Benchmark.analyze")(\[run_index\]) | The default analysis for the benchmark. |
| [`execute`](#iqm.benchmarks.benchmark_definition.Benchmark.execute "iqm.benchmarks.benchmark_definition.Benchmark.execute")(backend) | Executes the benchmark. |
| [`name`](#iqm.benchmarks.benchmark_definition.Benchmark.name "iqm.benchmarks.benchmark_definition.Benchmark.name")() | Return the name of the benchmark. |
| [`run`](#iqm.benchmarks.benchmark_definition.Benchmark.run "iqm.benchmarks.benchmark_definition.Benchmark.run")() | Runs the benchmark using the given backend. |

Parameters:  
- **backend** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

- **configuration** ([*BenchmarkConfigurationBase*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase"))

- **kwargs** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

*static* analysis_function(*result: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
The default analysis that only pass the result through.

Parameters:  
**result** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult"))

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*abstractmethod classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Return the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

*abstractmethod* execute(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

This method should be overridden by deriving classes.

Parameters:  
**backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")) – Qiskit backend used to execute benchmarks.

Returns:  
An xarray dataset which contains to results of the benchmark execution. The dataset should contain all the information necessary for analysing the benchmark results.

Return type:  
*Dataset*

run() → [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")  
Runs the benchmark using the given backend.

Returns:  
The result of the benchmark run.

Return type:  
RunResult

analyze(*run_index: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = -1*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
The default analysis for the benchmark.

Internally uses the function defined by the attribute `analysis_function` to perform the analysis. This function makes a shallow copy of the dataset produced by run. Therefore, it is recommended to not make changes to the data of the dataset but just the structure of the array.

Parameters:  
**run_index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Index for the run to analyze.

Returns:  
An analysis result constructed from the run and updated by the analysis method defined by the `analysis_function` field.

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

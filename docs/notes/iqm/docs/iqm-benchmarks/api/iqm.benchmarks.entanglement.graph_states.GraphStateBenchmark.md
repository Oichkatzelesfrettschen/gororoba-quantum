> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b9ac683c0d7a83c8c892da0acd2bda514a3eb86661d1c87f6c4ccdc792d0bbbf.

# iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark

*class* iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *configuration: [GraphStateConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.html#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

The Graph States benchmark estimates the bipartite entangelement negativity of native graph states.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.add_all_meta_to_dataset "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.analysis_function "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.analysis_function")(run) | Analysis function for a Graph State benchmark experiment. |
| [`execute`](#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.execute "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.execute")(backend) | Executes the benchmark. |
| [`generate_all_circuit_info_for_graph_state_benchmark`](#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.generate_all_circuit_info_for_graph_state_benchmark "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.generate_all_circuit_info_for_graph_state_benchmark")() | Generates all circuits and associated information for the Graph State benchmark. |
| [`name`](#iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.name "iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

- **configuration** ([*GraphStateConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.html#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a Graph State benchmark experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult"))

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

generate_all_circuit_info_for_graph_state_benchmark() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Generates all circuits and associated information for the Graph State benchmark.

> - Generates native graph states
>
> - Identifies all pairs of qubits with disjoint neighbors
>
> - Generates all projected nodes to cover all pairs of qubits with disjoint neighbors

Returns:  
A dictionary containing all circuit information for the Graph State benchmark.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

execute(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
*Dataset*

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d3401fa21f3f214f1efb4b9d049a971c20bda1c916611e34cb1b9a9cbee76857.

# iqm.benchmarks.optimization.qscore.QScoreBenchmark

*class* iqm.benchmarks.optimization.qscore.QScoreBenchmark(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *configuration: [QScoreConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html#iqm.benchmarks.optimization.qscore.QScoreConfiguration "iqm.benchmarks.optimization.qscore.QScoreConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Q-score estimates the size of combinatorial optimization problem that can be solved.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.add_all_meta_to_dataset "iqm.benchmarks.optimization.qscore.QScoreBenchmark.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.analysis_function "iqm.benchmarks.optimization.qscore.QScoreBenchmark.analysis_function")(run) | Analysis function for a QScore experiment. |
| [`choose_qubits_custom`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.choose_qubits_custom "iqm.benchmarks.optimization.qscore.QScoreBenchmark.choose_qubits_custom")(num_qubits) | Choose the qubits to execute the circuits on, according to custom_qubits_array matching num_qubits. |
| [`choose_qubits_naive`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.choose_qubits_naive "iqm.benchmarks.optimization.qscore.QScoreBenchmark.choose_qubits_naive")(num_qubits) | Choose the qubits to execute the circuits on, sequentially starting at qubit 0. |
| [`execute`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.execute "iqm.benchmarks.optimization.qscore.QScoreBenchmark.execute")(backend) | Executes the benchmark. |
| [`generate_maxcut_ansatz`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.generate_maxcut_ansatz "iqm.benchmarks.optimization.qscore.QScoreBenchmark.generate_maxcut_ansatz")(graph, theta\[, rzz_list\]) | Generate an ansatz circuit for QAOA MaxCut, with measurements at the end. |
| [`generate_maxcut_ansatz_star`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.generate_maxcut_ansatz_star "iqm.benchmarks.optimization.qscore.QScoreBenchmark.generate_maxcut_ansatz_star")(graph, theta\[, ...\]) | Generate an ansatz circuit for QAOA MaxCut, with measurements at the end. |
| [`greedy_vertex_cover_with_mapping`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.greedy_vertex_cover_with_mapping "iqm.benchmarks.optimization.qscore.QScoreBenchmark.greedy_vertex_cover_with_mapping")(mapping_graph) | Approximate a minimum vertex cover for a given graph, providing a mapping of nodes to the edges they cover. |
| [`name`](#iqm.benchmarks.optimization.qscore.QScoreBenchmark.name "iqm.benchmarks.optimization.qscore.QScoreBenchmark.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

- **configuration** ([*QScoreConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html#iqm.benchmarks.optimization.qscore.QScoreConfiguration "iqm.benchmarks.optimization.qscore.QScoreConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a QScore experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A QScore experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to QScore

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Returns the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

greedy_vertex_cover_with_mapping(*mapping_graph: Graph*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Approximate a minimum vertex cover for a given graph, providing a mapping of nodes to the edges they cover.

Parameters:  
**mapping_graph** (*Graph*) – The input graph for which the vertex cover is to be computed.

Returns:  
A dictionary where keys are nodes and values are lists of edges that each node covers.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

generate_maxcut_ansatz_star(*graph: Graph*, *theta: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *qubit_set: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → QuantumCircuit  
Generate an ansatz circuit for QAOA MaxCut, with measurements at the end.

Parameters:  
- **graph** (*Graph*) – The MaxCut problem graph

- **theta** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The variational parameters for QAOA, first gammas then betas

- **qubit_set** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – The qubit set to be used for the ansatz

Returns:  
The QAOA ansatz quantum circuit.

Return type:  
*QuantumCircuit*

generate_maxcut_ansatz(*graph: Graph*, *theta: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *rzz_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → QuantumCircuit  
Generate an ansatz circuit for QAOA MaxCut, with measurements at the end.

Parameters:  
- **graph** (*Graph*) – The MaxCut problem graph

- **theta** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The variational parameters for QAOA, first gammas then betas

- **rzz_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – List of RZZ gates grouped for optimal execution

Returns:  
The QAOA ansatz quantum circuit.

Return type:  
QuantumCircuit

add_all_meta_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Adds all configuration metadata and circuits to the dataset variable.

Parameters:  
**dataset** (*Dataset*) – The xarray dataset

Return type:  
None

*static* choose_qubits_naive(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Choose the qubits to execute the circuits on, sequentially starting at qubit 0.

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits to choose.

Returns:  
The list of qubits to execute the circuits on.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

choose_qubits_custom(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Choose the qubits to execute the circuits on, according to custom_qubits_array matching num_qubits.

Parameters:  
**num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits to choose

Returns:  
The list of qubits to execute the circuits on

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

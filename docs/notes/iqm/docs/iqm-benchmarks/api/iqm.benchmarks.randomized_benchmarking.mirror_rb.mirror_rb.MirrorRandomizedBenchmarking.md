> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9ebca02dd50a281ca099faf8f6f0f59dd8789770c717b6760ae8c854b9271508.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking

*class* iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [MirrorRBConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Mirror RB estimates the fidelity of ensembles of n-qubit layers.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.add_all_meta_to_dataset "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.analysis_function "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.analysis_function")(run) | Analysis function for a MRB experiment. |
| [`execute`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.execute "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.execute")(backend) | Executes the benchmark. |
| [`name`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.name "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.name")() | Returns the name of the benchmark. |
| [`submit_single_mrb_job`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.submit_single_mrb_job "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.submit_single_mrb_job")(backend_arg, qubits, ...) | Submit fixed-depth MRB jobs for execution in the specified IQMBackend. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*MirrorRBConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a MRB experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A MRB experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to MRB

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

submit_single_mrb_job(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *sorted_transpiled_circuit_dicts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Submit fixed-depth MRB jobs for execution in the specified IQMBackend.

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – the IQM backend to submit the job

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – the qubits to identify the submitted job

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the depth (number of canonical layers) of the circuits to identify the submitted job

- **sorted_transpiled_circuit_dicts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *...\],* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary containing all MRB circuits

Returns:  
Dict with qubit layout, submitted job objects, type (vanilla/DD) and submission time

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – the IQM backend to execute the benchmark on

Returns:  
The dataset containing all results and metadata of the benchmark execution

Return type:  
*Dataset*

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 10b4b555674e05aee13028479d01b2ffb00a633d69b7df37b5d05a6eeb8bfe46.

# iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking

*class* iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [DirectRBConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Direct RB estimates the fidelity of layers of canonical gates.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.add_all_meta_to_dataset "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.analysis_function "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.analysis_function")(run) | Direct RB analysis function. |
| [`assign_inputs_to_qubits`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.assign_inputs_to_qubits "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.assign_inputs_to_qubits")() | Assigns all DRB inputs to input qubit layouts. |
| [`execute`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.execute "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.execute")(backend) | Executes the Direct Randomized Benchmarking benchmark. |
| [`name`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.name "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.name")() | Returns the name of the benchmark. |
| [`submit_single_drb_job`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.submit_single_drb_job "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking.submit_single_drb_job")(backend_arg, qubits, ...) | Submit fixed-depth DRB jobs for execution in the specified IQMBackend. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*DirectRBConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Direct RB analysis function.

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

assign_inputs_to_qubits() → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]\]  
Assigns all DRB inputs to input qubit layouts.

This method processes optional configuration parameters and assigns them to each qubit layout. If a parameter is not provided or has insufficient values for all qubit layouts, default values are assigned. The method handles different behaviors for EPLG (Edge-Grab Pauli Layers) mode.

Returns:  
- assigned_drb_depths: Sequence of DRB circuit depths.

- assigned_two_qubit_gate_ensembles: Dictionary mapping qubit layout strings to dictionaries of two-qubit gate names and their sampling probabilities.

- assigned_density_2q_gates: Dictionary mapping qubit layout strings to the density of two-qubit gates (probability of sampling 2Q gates per qubit per layer).

- assigned_clifford_sqg_probabilities: Dictionary mapping qubit layout strings to the probability of sampling Clifford single-qubit gates.

- assigned_sqg_gate_ensembles: Dictionary mapping qubit layout strings to dictionaries of single-qubit gate names and their sampling probabilities, or None to indicate Clifford-only sampling.

Return type:  
A tuple containing

submit_single_drb_job(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *sorted_transpiled_circuit_dicts: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Submit fixed-depth DRB jobs for execution in the specified IQMBackend.

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – the IQM backend to submit the job to

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – the qubits to identify the submitted job

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the depth (number of canonical layers) of the circuits to identify the submitted job

- **sorted_transpiled_circuit_dicts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *...\],* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary containing all MRB circuits

Returns:  
Dict with qubit layout, depth, submitted job objects, and submission time

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the Direct Randomized Benchmarking benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The IQM backend to execute the benchmark on

Returns:  
Dataset containing benchmark results and metadata

Return type:  
*Dataset*

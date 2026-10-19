> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 75df68e821b821d85a15b14c0d060a880a675d12f6bb2cf9f9a955b356b2f29c.

# iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark

*class* iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [CLOPSConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

CLOPS reflect the speed of execution of parametrized QV circuits.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_meta_to_dataset`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.add_all_meta_to_dataset "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.analysis_function "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.analysis_function")(run) | Analysis function for a CLOPS (v or h) experiment. |
| [`append_parameterized_unitary`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.append_parameterized_unitary "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.append_parameterized_unitary")(qc, q0, q1, ...) | Append a decomposed, parametrized SU(4) gate using CX gates to the given quantum circuit. |
| [`assign_random_parameters_to_all`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.assign_random_parameters_to_all "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.assign_random_parameters_to_all")(...) | Assigns random parameters to all parametrized circuits. |
| [`clops_cycle`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.clops_cycle "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.clops_cycle")(backend, ...) | Executes a single CLOPS cycle (parameter assignment and execution) for the given update. |
| [`execute`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.execute "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.execute")(backend) | Executes the benchmark. |
| [`generate_circuit_list`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_circuit_list "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_circuit_list")() | Generate a list of parametrized QV quantum circuits, with measurements at the end. |
| [`generate_random_parameters`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_random_parameters "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_random_parameters")() | Generate an array of as many random parameters as needed by the QV template circuits. |
| [`generate_single_circuit`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_single_circuit "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_single_circuit")() | Generate a single parametrized QV quantum circuit, with measurements at the end. |
| [`generate_transpiled_clops_templates`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_transpiled_clops_templates "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.generate_transpiled_clops_templates")() | Generates CLOPS circuit templates transpiled to the backend's physical layout. |
| [`name`](#iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.name "iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*CLOPSConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a CLOPS (v or h) experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A CLOPS experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to CLOPS

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

append_parameterized_unitary(*qc: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*, *q0: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *q1: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *layer: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *pair: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Append a decomposed, parametrized SU(4) gate using CX gates to the given quantum circuit.

Parameters:  
- **qc** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – The quantum circuit to append the SU(4) gate to

- **q0** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The first qubit involved in the gate

- **q1** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The second qubit involved in the gate

- **layer** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The QV layer the gate belongs to

- **pair** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The pair index corresponding to the gate

Return type:  
None

generate_single_circuit() → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generate a single parametrized QV quantum circuit, with measurements at the end.

Returns:  
the QV quantum circuit.

Return type:  
QuantumCircuit

generate_circuit_list() → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]  
Generate a list of parametrized QV quantum circuits, with measurements at the end.

Returns:  
The list of parametrized QV quantum circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

generate_random_parameters() → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Generate an array of as many random parameters as needed by the QV template circuits.

Returns:  
The array of random parameters

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

assign_random_parameters_to_all(*dict_parametrized_circs: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*, *optimize_sqg: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]\]  
Assigns random parameters to all parametrized circuits.

Parameters:  
- **dict_parametrized_circs** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – Dictionary with list of int (qubits) as keys and lists of parametrized quantum circuits as values

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether single qubit gate optimization is applied

Returns:  
- lists of list of float parameter values corresponding to param updates

- dictionary with lists of int (qubits) as keys and lists of quantum circuits as values

Return type:  
A tuple of dictionaries

clops_cycle(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *sorted_transpiled_qc_list: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*, *update: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]  
Executes a single CLOPS cycle (parameter assignment and execution) for the given update.

Parameters:  
- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend to execute the jobs with

- **sorted_transpiled_qc_list** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary of lists of transpiled quantum circuits

- **update** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The current cycle update

Returns:  
The elapsed times for parameter assignment, submission and retrieval of jobs

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

generate_transpiled_clops_templates() → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]  
Generates CLOPS circuit templates transpiled to the backend’s physical layout.

Returns:  
A dictionary of quantum circuits with keys being str(qubit layout)

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

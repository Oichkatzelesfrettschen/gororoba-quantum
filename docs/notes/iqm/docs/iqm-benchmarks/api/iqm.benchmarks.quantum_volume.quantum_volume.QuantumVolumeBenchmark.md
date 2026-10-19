> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9714e0be553c3592e9b0b72fd7b544a8a008384180fefc97ababa3df47de735f.

# iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark

*class* iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark(*backend_arg: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [QuantumVolumeConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

Quantum Volume reflects the deepest circuit a given number of qubits can execute with meaningful results.

Attributes

Methods

|  |  |
|----|----|
| [`add_all_circuits_to_dataset`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.add_all_circuits_to_dataset "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.add_all_circuits_to_dataset")(dataset) | Adds all generated circuits during execution to the dataset variable. |
| [`add_all_meta_to_dataset`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.add_all_meta_to_dataset "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.add_all_meta_to_dataset")(dataset) | Adds all configuration metadata and circuits to the dataset variable. |
| [`analysis_function`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.analysis_function "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.analysis_function")(run) | Analysis function for a Quantum Volume experiment. |
| [`execute`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.execute "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.execute")(backend) | Executes the benchmark. |
| [`generate_circuit_list`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.generate_circuit_list "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.generate_circuit_list")(num_qubits\[, depth, ...\]) | Generate a list of QV quantum circuits, with measurements at the end. |
| [`generate_single_circuit`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.generate_single_circuit "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.generate_single_circuit")(num_qubits\[, depth, ...\]) | Generate a single QV quantum circuit, with measurements at the end. |
| [`get_rem_quasidistro`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.get_rem_quasidistro "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.get_rem_quasidistro")(...) | Computes readout-error-mitigated quasiprobabilities. |
| [`name`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.name "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.name")() | Returns the name of the benchmark. |
| [`submit_single_qv_job`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.submit_single_qv_job "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.submit_single_qv_job")(backend, qubits, ...) | Submit a single set of QV jobs for execution in the specified IQMBackend. |

Parameters:  
- **backend_arg** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*QuantumVolumeConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for a Quantum Volume experiment.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A Quantum Volume experiment run for which analysis result is created

Returns:  
AnalysisResult corresponding to Quantum Volume

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

*static* generate_single_circuit(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *classical_permutation: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")  
Generate a single QV quantum circuit, with measurements at the end.

Parameters:  
- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits of the circuit

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The depth of the QV circuit. Defaults to None, which makes it equal to the number of qubits.

- **classical_permutation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether permutations are classical, avoiding swapping layers.

Returns:  
The QV quantum circuit.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")

generate_circuit_list(*num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *depth: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *classical_permutations: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]  
Generate a list of QV quantum circuits, with measurements at the end.

Parameters:  
- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits of the circuits.

- **depth** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The depth of the QV circuit. Defaults to None, which makes it equal to the number of

- **qubits.**

- **classical_permutations** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether permutations are classical, avoiding swapping layers.

Returns:  
The list of QV quantum circuits.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

get_rem_quasidistro(*sorted_transpiled_qc_list: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*, *sorted_qc_list_indices: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *execution_results: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*, *mit_shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[QuasiCollection\]\]  
Computes readout-error-mitigated quasiprobabilities.

Parameters:  
- **sorted_transpiled_qc_list** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary of lists of quantum circuits, indexed by qubit layouts.

- **sorted_qc_list_indices** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – Dictionary of indices (integers) corresponding to those in the original (untranspiled) list of circuits, with keys being final physical qubit measurements.

- **execution_results** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – Counts from execution of all quantum circuits.

- **mit_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of measurement shots to estimate the readout calibration errors.

Returns:  
A list of lists of quasiprobabilities.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*QuasiCollection*\]\]

submit_single_qv_job(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *qubits: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *sorted_transpiled_qc_list: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\], [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]  
Submit a single set of QV jobs for execution in the specified IQMBackend.

Organizes the results in a dictionary with the qubit layout, the submitted job objects, the type of QV results and submission time.

Parameters:  
- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The IQM backend to submit the job.

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The qubits to identify the submitted job.

- **sorted_transpiled_qc_list** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* *...\],* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]\]*) – A dictionary of lists of quantum circuits.

Returns:  
Dict with qubit layout, submitted job objects, type (vanilla/DD) and submission time.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

execute(*backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

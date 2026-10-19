> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZBenchmark.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZBenchmark.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ab2a0b626c5786b916832ee56935ffc5b55a4f6dcc29a159b7263d7b3e7e62fb.

# iqm.benchmarks.entanglement.ghz.GHZBenchmark

*class* iqm.benchmarks.entanglement.ghz.GHZBenchmark(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [GHZConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZConfiguration.html#iqm.benchmarks.entanglement.ghz.GHZConfiguration "iqm.benchmarks.entanglement.ghz.GHZConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

The GHZ Benchmark estimates the quality of generated Greenberger–Horne–Zeilinger states.

Attributes

Methods

|  |  |
|----|----|
| `_generate_tree_ghz`(qubit_layout, qubit_count) | Build and transpile the GHZ circuit of the "tree" routine. |
| `_transpilation_target`(qubit_layout) | Qubit order and coupling map to transpile this layout's circuits against. |
| [`add_configuration_to_dataset`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.add_configuration_to_dataset "iqm.benchmarks.entanglement.ghz.GHZBenchmark.add_configuration_to_dataset")(dataset) | Creates a xarray.Dataset and adds the circuits and configuration metadata to it. |
| [`analysis_function`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.analysis_function "iqm.benchmarks.entanglement.ghz.GHZBenchmark.analysis_function")(run) | Analyze counts and compute the state fidelity. |
| [`append_rms`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.append_rms "iqm.benchmarks.entanglement.ghz.GHZBenchmark.append_rms")(num_rms, qubit_layout) | Appends 1Q Clifford gates sampled uniformly at random to all qubits in the given circuit. |
| [`execute`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.execute "iqm.benchmarks.entanglement.ghz.GHZBenchmark.execute")(backend) | Executes the benchmark. |
| [`generate_coherence_meas_circuits`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_coherence_meas_circuits "iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_coherence_meas_circuits")(...) | Takes a given GHZ circuit and outputs circuits needed to measure fidelity via mult. |
| [`generate_native_ghz`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_native_ghz "iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_native_ghz")(qubit_layout, ...) | Generate a circuit preparing a GHZ state. |
| [`generate_readout_circuit`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_readout_circuit "iqm.benchmarks.entanglement.ghz.GHZBenchmark.generate_readout_circuit")(qubit_layout, ...) | A wrapper for the creation of different circuits to estimate the fidelity. |
| [`name`](#iqm.benchmarks.entanglement.ghz.GHZBenchmark.name "iqm.benchmarks.entanglement.ghz.GHZBenchmark.name")() | Returns the name of the benchmark. |

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*GHZConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZConfiguration.html#iqm.benchmarks.entanglement.ghz.GHZConfiguration "iqm.benchmarks.entanglement.ghz.GHZConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analyze counts and compute the state fidelity.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – The RunResult object containing a dataset with counts and benchmark parameters.

Returns:  
An object containing the dataset, plots, and observations.

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Returns the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

generate_native_ghz(*qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *qubit_count: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *routine: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [CircuitGroup](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")  
Generate a circuit preparing a GHZ state.

The GHZ state is generated according to a given routine and transpiled to the native gate set and topology.

Parameters:  
- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol, indexed from 0

- **qubit_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits for which a GHZ state should be created. This values should be smaller or equal to the number of qubits in qubit_layout

- **routine** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The routine to generate the GHZ circuit

Returns:  
QuantumCircuit implementing GHZ native state

Return type:  
[*CircuitGroup*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")

generate_coherence_meas_circuits(*qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *qubit_count: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]  
Takes a given GHZ circuit and outputs circuits needed to measure fidelity via mult. q. coherences method.

Parameters:  
- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol, indexed from 0

- **qubit_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits for which a GHZ state should be created. This values should be smaller or equal to the number of qubits in qubit_layout

Returns:  
A list of transpiled quantum circuits to be measured

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

append_rms(*num_rms: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]  
Appends 1Q Clifford gates sampled uniformly at random to all qubits in the given circuit.

Parameters:  
- **num_rms** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – How many randomized measurement circuits are generated

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol, indexed from 0

Returns:  
List of the original circuit with 1Q Clifford gates appended to it

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

generate_readout_circuit(*qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *qubit_count: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [CircuitGroup](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")  
A wrapper for the creation of different circuits to estimate the fidelity.

Parameters:  
- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol, indexed from 0

- **qubit_count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits for which a GHZ state should be created. This values should be smaller or equal to the number of qubits in qubit_layout

Returns:  
A list of transpiled quantum circuits to be measured

Return type:  
[*CircuitGroup*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")

add_configuration_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Creates a xarray.Dataset and adds the circuits and configuration metadata to it.

Parameters:  
**dataset** (*Dataset*) – The dataset containing the benchmark information

Returns:  
Dataset to be used for further data storage

Return type:  
None

execute(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")*) → Dataset  
Executes the benchmark.

Parameters:  
**backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

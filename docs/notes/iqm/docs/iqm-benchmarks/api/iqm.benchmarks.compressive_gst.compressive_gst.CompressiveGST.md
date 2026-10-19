> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f3186e46970d9c7af673f9b042bc89acf6f31bfe1ff8054e8c532b686599ebb0.

# iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST

*class* iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *configuration: [GSTConfiguration](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration")*)  
Bases: [`Benchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")

SPAM-robust characterization of a set of quantum gates.

Attributes

Methods

|  |  |
|----|----|
| [`add_configuration_to_dataset`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.add_configuration_to_dataset "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.add_configuration_to_dataset")(dataset) | Creates an xarray.Dataset and adds the circuits and configuration metadata to it. |
| [`analysis_function`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.analysis_function "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.analysis_function")(run) | Analysis function for compressive GST. |
| [`execute`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.execute "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.execute")(backend) | The main GST execution routine. |
| [`generate_meas_circuits`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.generate_meas_circuits "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.generate_meas_circuits")() | Generate random circuits from the gate set. |
| [`name`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.name "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.name")() | Returns the name of the benchmark. |
| [`validate_gate_context`](#iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.validate_gate_context "iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST.validate_gate_context")() | Validate that the gate context is properly configured. |

Parameters:  
- **backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **configuration** ([*GSTConfiguration*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration"))

*static* analysis_function(*run: [BenchmarkRunResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")*) → [BenchmarkAnalysisResult](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")  
Analysis function for compressive GST.

Parameters:  
**run** ([*BenchmarkRunResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkRunResult.html#iqm.benchmarks.benchmark_definition.BenchmarkRunResult "iqm.benchmarks.benchmark_definition.BenchmarkRunResult")) – A BenchmarkRunResult instance storing the dataset

Returns:  
A BenchmarkAnalysisResult instance with the updated dataset, as well as plots and observations

Return type:  
[*BenchmarkAnalysisResult*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult.html#iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult "iqm.benchmarks.benchmark_definition.BenchmarkAnalysisResult")

*classmethod* name() → [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")  
Returns the name of the benchmark.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

validate_gate_context() → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Validate that the gate context is properly configured.

Checks that: 1. If gate_context is a list, it has the same length as gate_set 2. The qubits used in gate_context don’t overlap with qubits in the layouts

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If gate_context is invalid or if qubits in gate_context overlap with qubits in layouts

Return type:  
None

generate_meas_circuits() → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[BenchmarkCircuit](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit"), [BenchmarkCircuit](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html#iqm.benchmarks.circuit_containers.BenchmarkCircuit "iqm.benchmarks.circuit_containers.BenchmarkCircuit")\]  
Generate random circuits from the gate set.

The random circuits are distributed among different depths ranging from L_MIN to L_MAX, both are configurable and stored in self.configuration.seq_len_list. No transpilation other than mapping to the desired qubits is performed, as the gates need to be executed axactly as described for GST to give meaningful results

Returns:  
The transpiled circuits untranspiled_circuits: The untranspiled circuits circuit_gen_transp_time: The time it took to generate and transpile the circuits

Return type:  
transpiled_circuits

add_configuration_to_dataset(*dataset: Dataset*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Creates an xarray.Dataset and adds the circuits and configuration metadata to it.

Parameters:  
- **self** – Source class

- **dataset** (*Dataset*) – Dataset to which the configuration is added

Returns:  
Dataset to be used for further data storage

Return type:  
dataset

execute(*backend: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)")*) → Dataset  
The main GST execution routine.

Parameters:  
**backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)"))

Return type:  
*Dataset*

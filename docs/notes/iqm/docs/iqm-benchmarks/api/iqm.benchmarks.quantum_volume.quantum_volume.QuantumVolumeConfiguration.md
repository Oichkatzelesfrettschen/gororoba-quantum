> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6474bfef8984c8ef78fcfd04a803890c73e5fb76baf0fd74bf8d867e943c7362.

# iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration

*class* iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, num_circuits: int, num_sigmas: int = 2, choose_qubits_routine: ~typing.Literal\['custom'\] = 'custom', custom_qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\], qiskit_optim_level: int = 3, approximation_degree: float = 1.0, optimize_sqg: bool = True, rem: bool = True, mit_shots: int = 1000*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Quantum Volume configuration.

Parameters:  
- **benchmark** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Benchmark*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")*\]*)

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **max_gates_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **max_circuits_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod"))

- **physical_layout** ([*PhysicalLayout*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout"))

- **use_dd** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* *None*)

- **dd_strategy** ([*DDStrategy*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "(in iqm-station-control-client v14.0.0)") *\|* *None*)

- **active_reset_cycles** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **num_sigmas** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **choose_qubits_routine** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['custom'\]*)

- **custom_qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **approximation_degree** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **rem** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **mit_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

benchmark  
`QuantumVolumeBenchmark`.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

num_circuits  
Number of circuits to use. Should be at least 100 for a meaningful QV experiment.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

num_sigmas  
Number of sample standard deviations to consider with for the threshold criteria. Default by consensus is 2.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

choose_qubits_routine  
Routine to select qubit layouts.

Type:  
Literal\[‘custom’\]

custom_qubits_array  
Physical qubit layouts to perform the benchmark on.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

qiskit_optim_level  
Qiskit transpilation optimization level.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

optimize_sqg  
Whether Single Qubit Gate Optimization is performed upon transpilation.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

routing_method  
Qiskit transpilation routing method to use.

physical_layout  
Whether the coupling map is restricted to qubits in the input layout or not. “fixed” restricts the coupling map to only the specified qubits. “batching” considers the full coupling map of the backend and circuit execution is batched per final layout.

rem  
Whether Readout Error Mitigation is applied in post-processing. When set to True, both results (readout-unmitigated and -mitigated) are produced.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

mit_shots  
The measurement shots to use for readout calibration.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.model_config "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.benchmark "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.benchmark") |  |
| [`num_circuits`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.num_circuits "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.num_circuits") |  |
| [`num_sigmas`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.num_sigmas "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.num_sigmas") |  |
| [`choose_qubits_routine`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.choose_qubits_routine "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.choose_qubits_routine") |  |
| [`custom_qubits_array`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.custom_qubits_array "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.custom_qubits_array") |  |
| [`qiskit_optim_level`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.qiskit_optim_level "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.qiskit_optim_level") |  |
| `approximation_degree` |  |
| [`optimize_sqg`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.optimize_sqg "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.optimize_sqg") |  |
| [`rem`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.rem "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.rem") |  |
| [`mit_shots`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.mit_shots "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.mit_shots") |  |
| `shots` |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| [`routing_method`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.routing_method "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.routing_method") |  |
| [`physical_layout`](#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.physical_layout "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.physical_layout") |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

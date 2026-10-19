> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 503b4da4cbd3dd8517d6e1521a97a2a3b76756bb799ca8b302dc503b5ce56c05.

# iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration

*class* iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRandomizedBenchmarking'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\], sequence_lengths: ~collections.abc.Sequence\[int\], num_circuit_samples: int, parallel_execution: bool = False, interleaved_gate: str, interleaved_gate_params: ~collections.abc.Sequence\[float\] \| None = None, simultaneous_fit: ~collections.abc.Sequence\[~typing.Literal\['amplitude', 'offset'\]\] = \['amplitude', 'offset'\]*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Interleaved RB configuration.

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

- **qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **sequence_lengths** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **num_circuit_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **parallel_execution** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **interleaved_gate** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **interleaved_gate_params** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*)

- **simultaneous_fit** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['amplitude',* *'offset'\]\]*)

benchmark  
InterleavedRandomizedBenchmarking.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits_array  
The array of physical qubit labels with which to execute IRB.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

sequence_lengths  
The length of each random Clifford sequence.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

num_circuit_samples  
The number of circuit samples to generate.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

shots  
The number of measurement shots with which to execute each circuit sample.

parallel_execution  
Whether the benchmark is executed on all qubits in parallel or not.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

interleaved_gate  
The name of the gate to interleave. \* Should be specified as a qiskit circuit library gate name, e.g., “YGate” or “CZGate”.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

interleaved_gate_params  
Any optional parameters entering the gate.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| None

simultaneous_fit  
Optional parameters to fit simultaneously.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[Literal\[‘amplitude’, ‘offset’\]\]

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.model_config "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.benchmark "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.benchmark") |  |
| [`qubits_array`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.qubits_array "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.qubits_array") |  |
| [`sequence_lengths`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.sequence_lengths "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.sequence_lengths") |  |
| [`num_circuit_samples`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.num_circuit_samples "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.num_circuit_samples") |  |
| [`parallel_execution`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.parallel_execution "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.parallel_execution") |  |
| [`interleaved_gate`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.interleaved_gate "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.interleaved_gate") |  |
| [`interleaved_gate_params`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.interleaved_gate_params "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.interleaved_gate_params") |  |
| [`simultaneous_fit`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.simultaneous_fit "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.simultaneous_fit") |  |
| [`shots`](#iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.shots "iqm.benchmarks.randomized_benchmarking.interleaved_rb.interleaved_rb.InterleavedRBConfiguration.shots") |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| `routing_method` |  |
| `physical_layout` |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

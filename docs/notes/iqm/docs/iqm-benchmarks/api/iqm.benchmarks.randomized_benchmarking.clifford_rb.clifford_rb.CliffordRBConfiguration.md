> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e256e5db4168981596a35c32ab89d03f4bfe16daaaa9c7f778bc82ed5e1b75ea.

# iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration

*class* iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRandomizedBenchmarking'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\], sequence_lengths: ~collections.abc.Sequence\[int\], num_circuit_samples: int, parallel_execution: bool = False*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Clifford RB configuration.

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

benchmark  
CliffordRandomizedBenchmarking

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits_array  
The array of qubits on which to execute the benchmark.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

sequence_lengths  
The length of Cliffords sequences with which to execute benchmark.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

num_circuit_samples  
The number of Cliffords circuits per sequence length.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

shots  
The number of measurement shots per circuit.

parallel_execution  
Whether the benchmark is executed on all qubits in parallel or not.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.model_config "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.benchmark "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.benchmark") |  |
| [`qubits_array`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.qubits_array "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.qubits_array") |  |
| [`sequence_lengths`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.sequence_lengths "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.sequence_lengths") |  |
| [`num_circuit_samples`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.num_circuit_samples "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.num_circuit_samples") |  |
| [`parallel_execution`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.parallel_execution "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.parallel_execution") |  |
| [`shots`](#iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.shots "iqm.benchmarks.randomized_benchmarking.clifford_rb.clifford_rb.CliffordRBConfiguration.shots") |  |
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

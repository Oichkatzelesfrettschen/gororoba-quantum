> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 55c8f430c8eeda91701cb38a79b097d0819df397a716e5b79301b9e10319a446.

# iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration

*class* iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGBenchmark'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, drb_depths: ~collections.abc.Sequence\[int\], drb_circuit_samples: int, custom_qubits_array: ~collections.abc.Sequence\[tuple\[int, int\]\] \| None = None, chain_length: int \| None = None, chain_path_samples: int \| None = None, num_disjoint_layers: int \| None = None, max_hamiltonian_path_tries: int \| None = None*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

EPLG Configuration.

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

- **drb_depths** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **drb_circuit_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **custom_qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*)

- **chain_length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **chain_path_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **num_disjoint_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **max_hamiltonian_path_tries** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

drb_depths  
Layer depths to consider for the parallel DRB.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

drb_circuit_samples  
Number of circuit samples to consider for the parallel DRB.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

custom_qubits_array  
Custom qubits array to consider; this corresponds to a `Sequence` of tuple pairs of qubits. If not specified, will proceed to generate linear chains at random, selecting the one with the highest total 2Q gate fidelity.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| None

chain_length  
Length of a linear chain of 2Q gates to consider, corresponding to the number of qubits, if `custom_qubits_array` not specified. Default is None: assigns the number of qubits in the backend minus one.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

chain_path_samples  
Number of chain path samples to consider, if `custom_qubits_array` not specified. Default is None: assigns 20 path samples (arbitrary).

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

num_disjoint_layers  
Number of disjoint layers to consider. Default is None: assigns 2 disjoint layers (arbitrary).

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

max_hamiltonian_path_tries  
Maximum number of tries to find a Hamiltonian path. Default is None: assigns 10 tries (arbitrary).

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.model_config "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `benchmark` |  |
| [`drb_depths`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.drb_depths "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.drb_depths") |  |
| [`drb_circuit_samples`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.drb_circuit_samples "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.drb_circuit_samples") |  |
| [`custom_qubits_array`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.custom_qubits_array "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.custom_qubits_array") |  |
| [`chain_length`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.chain_length "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.chain_length") |  |
| [`chain_path_samples`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.chain_path_samples "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.chain_path_samples") |  |
| [`num_disjoint_layers`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.num_disjoint_layers "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.num_disjoint_layers") |  |
| [`max_hamiltonian_path_tries`](#iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.max_hamiltonian_path_tries "iqm.benchmarks.randomized_benchmarking.eplg.eplg.EPLGConfiguration.max_hamiltonian_path_tries") |  |
| `shots` |  |
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

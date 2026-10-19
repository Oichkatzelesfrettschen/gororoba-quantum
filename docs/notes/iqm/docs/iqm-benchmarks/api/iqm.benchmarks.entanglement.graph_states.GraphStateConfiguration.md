> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 334e5675879c86cb05239db7a576d2a4e30735851dc94fde3d51d6b818e8ab26.

# iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration

*class* iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.entanglement.graph_states.GraphStateBenchmark'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits: ~collections.abc.Sequence\[int\], tomography: ~iqm.benchmarks.entanglement.graph_states.TomographyType = TomographyType.STATE, num_bootstraps: int = 50, n_random_unitaries: int = 100, n_median_of_means: int = 1*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Graph States Benchmark configuration.

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

- **qubits** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **tomography** ([*TomographyType*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.TomographyType.html#iqm.benchmarks.entanglement.graph_states.TomographyType "iqm.benchmarks.entanglement.graph_states.TomographyType"))

- **num_bootstraps** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **n_random_unitaries** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **n_median_of_means** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

benchmark  
`GraphStateBenchmark`.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits  
Physical qubit layout in which to benchmark graph state generation.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

tomography  
Whether to use state or shadow tomography.

Type:  
[iqm.benchmarks.entanglement.graph_states.TomographyType](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.graph_states.TomographyType.html#iqm.benchmarks.entanglement.graph_states.TomographyType "iqm.benchmarks.entanglement.graph_states.TomographyType")

num_bootstraps  
Amount of bootstrap samples to use with state tomography.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

n_random_unitaries  
Number of Haar random single-qubit unitaries to use for (local) shadow tomography.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

n_median_of_means  
Number of mean samples over `n_random_unitaries` to generate a median of means estimator for shadow tomography. NB: The total amount of execution calls will be a multiplicative factor of `n_random_unitaries` x `n_median_of_means`. Default is 1 (no median of means).

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.model_config "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.benchmark "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.benchmark") |  |
| [`qubits`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.qubits "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.qubits") |  |
| [`tomography`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.tomography "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.tomography") |  |
| [`num_bootstraps`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.num_bootstraps "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.num_bootstraps") |  |
| [`n_random_unitaries`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.n_random_unitaries "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.n_random_unitaries") |  |
| [`n_median_of_means`](#iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.n_median_of_means "iqm.benchmarks.entanglement.graph_states.GraphStateConfiguration.n_median_of_means") |  |
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

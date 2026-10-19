> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f789c12c77a943a802d2c7b4d6a9b1c97e1fa38c0dbbf11208e0f47d3b2d814b.

# iqm.benchmarks.entanglement.ghz.GHZConfiguration

*class* iqm.benchmarks.entanglement.ghz.GHZConfiguration(*\**, *benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.entanglement.ghz.GHZBenchmark'\>*, *shots: int = 1024*, *max_gates_per_batch: int \| None = None*, *max_circuits_per_batch: int \| None = None*, *routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE*, *physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED*, *use_dd: bool \| None = False*, *dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None*, *active_reset_cycles: int \| None = None*, *state_generation_routine: str = 'tree'*, *custom_qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\] \| None = None*, *qiskit_optim_level: int = 3*, *optimize_sqg: bool = True*, *fidelity_routine: str = 'coherences'*, *num_rms: int \| None = 100*, *rem: bool = True*, *mit_shots: int = 1000*, *tree_objective: str = 'estimated_fidelity'*, *tree_idle_penalty: float = 1.0*, *tree_depth_penalty: float = 0.05*, *tree_cz_duration: float = 4e-08*, *tree_rank: int = 0*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

GHZ state configuration.

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

- **state_generation_routine** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **custom_qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*)

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **fidelity_routine** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **num_rms** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **rem** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **mit_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **tree_objective** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **tree_idle_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **tree_depth_penalty** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **tree_cz_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **tree_rank** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

benchmark  
GHZBenchmark

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

state_generation_routine  
The routine to construct circuits generating a GHZ state. Must be one of STATE_GENERATION_ROUTINES; an unknown value is rejected rather than silently treated as “log”. Possible values:

- “tree” (default): Optimized GHZ state generation circuit that takes the qubit coupling, the CZ and single-qubit gate fidelities, and the time each qubit spends idling into account. The qubits, the spanning tree and the gate order are chosen together, and what the search minimizes is set by tree_objective below. See iqm.benchmarks.entanglement.ghz_optimal.

- “log”: Optimized circuit with parallel application of CX gates such that the number of CX gates scales logarithmically in the system size. This implementation currently does not take connectivity on the backend into account.

- “naive”: Applies the naive textbook circuit with \#CX gates scaling linearly in the system size.

- “star”, “star_optimal”: For star (resonator) topologies.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

custom_qubits_array  
A sequence (e.g., Tuple or List) of sequences of physical qubit layouts, as specified by integer labels, where the benchmark is meant to be run. If None, takes all qubits specified in the backend coupling map.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| None

qiskit_optim_level  
The optimization level used for transpilation to backend architecture.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

optimize_sqg  
Whether consecutive single qubit gates are optimized for reduced gate count via iqm.qiskit_iqm.iqm_transpilation.optimize_single_qubit_gates

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

fidelity_routine  
The method with which the fidelity is estimated. Possible values:

- “coherences”: The multiple quantum coherences method as in \[Mooney, 2021\]

- “randomized_measurements”: Fidelity estimation via randomized measurements outlined in [https://arxiv.org/abs/1812.02624](https://arxiv.org/abs/1812.02624)

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

num_rms  
The number of randomized measurements used if the respective fidelity routine is chosen

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

rem  
Boolean flag determining if readout error mitigation is used

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

mit_shots  
Total number of shots for readout error mitigation

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

tree_objective  
What the “tree” search minimizes, one of iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES. The default, “estimated_fidelity”, trades gate fidelity against the time qubits spend idling. Set “min_error” to minimize gate error alone, which is what this routine did before the idle term existed and is the setting to use to reproduce older results.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

tree_idle_penalty  
Weight of the idle-decoherence term of the “estimated_fidelity” objective; 0.0 disables it, which makes the objective equivalent to “min_error”. Values above 1.0 buy depth more aggressively.

Type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

tree_depth_penalty  
Cost of one CZ layer for the “depth_penalty” objective, in units of -log(fidelity).

Type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

tree_cz_duration  
Duration assumed for one CZ layer, in seconds. Calibration data carries no gate durations, so this is an assumption rather than a measurement.

Type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

tree_rank  
Which of the ranked “tree” candidates to run, 0 being the best-scoring one. The ranking is logged, so a later run can ask for a different root.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.model_config "iqm.benchmarks.entanglement.ghz.GHZConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.benchmark "iqm.benchmarks.entanglement.ghz.GHZConfiguration.benchmark") |  |
| [`state_generation_routine`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.state_generation_routine "iqm.benchmarks.entanglement.ghz.GHZConfiguration.state_generation_routine") |  |
| [`custom_qubits_array`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.custom_qubits_array "iqm.benchmarks.entanglement.ghz.GHZConfiguration.custom_qubits_array") |  |
| `shots` |  |
| [`qiskit_optim_level`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.qiskit_optim_level "iqm.benchmarks.entanglement.ghz.GHZConfiguration.qiskit_optim_level") |  |
| [`optimize_sqg`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.optimize_sqg "iqm.benchmarks.entanglement.ghz.GHZConfiguration.optimize_sqg") |  |
| [`fidelity_routine`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.fidelity_routine "iqm.benchmarks.entanglement.ghz.GHZConfiguration.fidelity_routine") |  |
| [`num_rms`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.num_rms "iqm.benchmarks.entanglement.ghz.GHZConfiguration.num_rms") |  |
| [`rem`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.rem "iqm.benchmarks.entanglement.ghz.GHZConfiguration.rem") |  |
| [`mit_shots`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.mit_shots "iqm.benchmarks.entanglement.ghz.GHZConfiguration.mit_shots") |  |
| [`tree_objective`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_objective "iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_objective") |  |
| [`tree_idle_penalty`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_idle_penalty "iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_idle_penalty") |  |
| [`tree_depth_penalty`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_depth_penalty "iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_depth_penalty") |  |
| [`tree_cz_duration`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_cz_duration "iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_cz_duration") |  |
| [`tree_rank`](#iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_rank "iqm.benchmarks.entanglement.ghz.GHZConfiguration.tree_rank") |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| `routing_method` |  |
| `physical_layout` |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

|  |  |
|----|----|
| `_check_state_generation_routine`(value) | Reject a routine name that would otherwise silently build the log-depth circuits. |
| `_check_tree_objective`(value) | Reject a tree objective the search does not implement. |

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

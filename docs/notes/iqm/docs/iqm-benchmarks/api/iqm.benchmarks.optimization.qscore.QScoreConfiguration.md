> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7d243e5adc82eb42ab142c5a13917b316bc5f8468def23c48ab06c0f21c9552b.

# iqm.benchmarks.optimization.qscore.QScoreConfiguration

*class* iqm.benchmarks.optimization.qscore.QScoreConfiguration(*\**, *benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.optimization.qscore.QScoreBenchmark'\>*, *shots: int = 256*, *max_gates_per_batch: int \| None = None*, *max_circuits_per_batch: int \| None = None*, *routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE*, *physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED*, *use_dd: bool \| None = False*, *dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None*, *active_reset_cycles: int \| None = None*, *num_instances: int*, *num_qaoa_layers: int = 1*, *min_num_nodes: int = 2*, *max_num_nodes: int*, *use_virtual_node: bool = True*, *use_classically_optimized_angles: bool = True*, *choose_qubits_routine: ~typing.Literal\['naive'*, *'custom'\] = 'naive'*, *min_num_qubits: int = 2*, *custom_qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\] \| None = None*, *qiskit_optim_level: int = 3*, *optimize_sqg: bool = True*, *num_trials: int = 10*, *seed: int = 1*, *REM: bool = False*, *mit_shots: int = 1000*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Q-score configuration.

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

- **num_instances** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **num_qaoa_layers** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **min_num_nodes** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **max_num_nodes** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **use_virtual_node** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **use_classically_optimized_angles** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **choose_qubits_routine** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['naive',* *'custom'\]*)

- **min_num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **custom_qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*)

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **num_trials** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **REM** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **mit_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

benchmark  
QScoreBenchmark

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

num_instances  
Number of random graphs to be chosen.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

num_qaoa_layers  
Depth of the QAOA circuit.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

min_num_nodes  
The min number of nodes to be taken into account, which should be \>= 2.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

max_num_nodes  
The max number of nodes to be taken into account, which has to be \<= num_qubits + 1.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

use_virtual_node  
Parameter to increase the potential Qscore by +1.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

use_classically_optimized_angles  
Use pre-optimised tuned parameters in the QAOA circuit.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

choose_qubits_routine  
The routine to select qubit layouts.

Type:  
Literal\[‘naive’, ‘custom’\]

min_num_qubits  
Minumum number of qubits.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

custom_qubits_array  
The physical qubit layouts to perform the benchmark on. If virtual_node is True, then a given graph with n nodes requires n-1 selected qubits. If virtual_node is set to False, then a given graph with n nodes requires n selected qubits.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| None

qiskit_optim_level  
The Qiskit transpilation optimization level.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

optimize_sqg  
Whether Single Qubit Gate Optimization is performed upon transpilation.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

num_trials  
Number of trials to perform when choosing graph permutations to minimize CZ gates.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

seed  
The random seed.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

REM  
Use readout error mitigation.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

mit_shots  
Number of shots used in readout error mitigation.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.model_config "iqm.benchmarks.optimization.qscore.QScoreConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.benchmark "iqm.benchmarks.optimization.qscore.QScoreConfiguration.benchmark") |  |
| [`num_instances`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_instances "iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_instances") |  |
| [`num_qaoa_layers`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_qaoa_layers "iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_qaoa_layers") |  |
| [`min_num_nodes`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.min_num_nodes "iqm.benchmarks.optimization.qscore.QScoreConfiguration.min_num_nodes") |  |
| [`max_num_nodes`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.max_num_nodes "iqm.benchmarks.optimization.qscore.QScoreConfiguration.max_num_nodes") |  |
| [`use_virtual_node`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.use_virtual_node "iqm.benchmarks.optimization.qscore.QScoreConfiguration.use_virtual_node") |  |
| [`use_classically_optimized_angles`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.use_classically_optimized_angles "iqm.benchmarks.optimization.qscore.QScoreConfiguration.use_classically_optimized_angles") |  |
| [`choose_qubits_routine`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.choose_qubits_routine "iqm.benchmarks.optimization.qscore.QScoreConfiguration.choose_qubits_routine") |  |
| [`min_num_qubits`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.min_num_qubits "iqm.benchmarks.optimization.qscore.QScoreConfiguration.min_num_qubits") |  |
| [`custom_qubits_array`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.custom_qubits_array "iqm.benchmarks.optimization.qscore.QScoreConfiguration.custom_qubits_array") |  |
| [`qiskit_optim_level`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.qiskit_optim_level "iqm.benchmarks.optimization.qscore.QScoreConfiguration.qiskit_optim_level") |  |
| [`optimize_sqg`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.optimize_sqg "iqm.benchmarks.optimization.qscore.QScoreConfiguration.optimize_sqg") |  |
| [`num_trials`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_trials "iqm.benchmarks.optimization.qscore.QScoreConfiguration.num_trials") |  |
| [`seed`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.seed "iqm.benchmarks.optimization.qscore.QScoreConfiguration.seed") |  |
| [`REM`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.REM "iqm.benchmarks.optimization.qscore.QScoreConfiguration.REM") |  |
| [`mit_shots`](#iqm.benchmarks.optimization.qscore.QScoreConfiguration.mit_shots "iqm.benchmarks.optimization.qscore.QScoreConfiguration.mit_shots") |  |
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

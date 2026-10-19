> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 776e8c6cb9b7260bf26932cec968b16e818c00ab2f6ce5f6240d4f658ba7916b.

# iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration

*class* iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.compressive_gst.compressive_gst.CompressiveGST'\>, shots: int = 1024, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubit_layouts: list\[int\] \| list\[list\[int\]\], gate_set: str \| list\[~typing.Any\], gate_context: ~typing.Any \| list\[~typing.Any\] \| None = None, num_circuits: int, rank: int, gate_labels: list \| None = None, seq_len_list: list\[int\] = \[1, 8, 14\], from_init: bool = True, max_inits: int = 20, opt_method: str = 'auto', max_iterations: str \| list\[int\] \| int = 'auto', convergence_criteria: str \| list\[float\] = \[4, 1e-05\], batch_size: str \| int = 'auto', bootstrap_samples: int = 0, verbose_level: int = 1, parallel_execution: bool = False, fixed_elements: list\[str\] \| None = None*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Compressive GST configuration base.

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

- **qubit_layouts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **gate_set** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **gate_context** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*)

- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **rank** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **gate_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *\|* *None*)

- **seq_len_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **from_init** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **max_inits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **opt_method** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **max_iterations** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **convergence_criteria** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **batch_size** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **bootstrap_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **verbose_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **parallel_execution** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **fixed_elements** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

benchmark  
GHZBenchmark

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubit_layouts  
A sequence (e.g., Tuple or List) of sequences of physical qubit layouts, as specified by integer labels, where the benchmark is meant to be run.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

gate_set  
The gate set in given either as a list of qiskit quantum cirucuits, or as one of the predefined gate sets “1QXYI”, “2QXYCZ”, “2QXYCZ_extended”, “3QXYCZ”. A gate set should be tomographically complete, meaning from the specified gates and the vacuum state, one should be able to prepare states that form a frame for the state space. A practical sufficient condition is that the gate set is able the generate all combinations of local Pauli eigenstates.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Any\]

num_circuits  
How many random circuits are generated from the gate set. Guidelines on choosing this value: - At least 50 circuits for a single qubit gate set with 3 gates. - At least 400 circuits for a two qubit gate set with 6 gates. - At least 2000 circuits for a three qubit gate set with 9 gates. The number of random circuits needed is expected to grow linearly in the number of gates and exponentially in the number of qubits.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

rank  
The Kraus rank of the reconstruction. Choose rank=1 for coherent error analysis and rank\<=dim\*\*2 generally.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

shots  
The number of measurement shots per circuit.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

gate_labels  
Names of the gates in the gate set. Used for plots and result tables.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") \| None

seq_len_list  
Three numbers controling the depth of the random sequences. The first is the minimal depth, the last is the maximal depth and the middle number specifies a cutoff depth below which all possible sequences are selected.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

from_init  
Whether the target gate set is used as an initialization to the mGST algorithm.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

max_inits  
If from_init = False, random initial points are tried and this parameter limits the amount of retries.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

opt_method  
Which optimization method is used, can be either of “GD” or “SFN”, for gradient descent or saddle free Newton, respectively.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

max_iterations  
How many iterations to run the optimization algorithm for. Accepted values are either “auto” or a list of two integers. The first specifies the number of iterations for the optimization on batches or circuit data, while the second specifies the number of iterations on the full data for all circuits.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

convergence_criteria  
Two parameters which determine when the optimization algorithm terminates. The first is a multiplier which specifies how close the cost function should get to a threshold for the given shot noise in order for the optimization to be considered “successful”. Values in \[2,10\] are usually sensible. The second parameter sets the relative change in cost function between two consecutive iterations, below which the algorithm terminates.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

batch_size  
The number of circuits per batch in the optimization. This hyperparamters is automatically set and determines the convergence behaviour. A smaller batch size reduces runtime but can lead to erratic jumps in parameter space and lack of convergence.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

bootstrap_samples  
The number of times the optimization algorithm is repeated on fake data to estimate the uncertainty via bootstrapping.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

verbose_level  
The level of verbosity of the output. 0 is minimal, 1 gives optimization updates, 2 outputs optimization plots

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

parallel_execution  
Whether to run the circuits for all layouts in parallel on the backend.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.model_config "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.benchmark "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.benchmark") |  |
| [`qubit_layouts`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.qubit_layouts "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.qubit_layouts") |  |
| [`gate_set`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.gate_set "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.gate_set") |  |
| `gate_context` |  |
| [`num_circuits`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.num_circuits "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.num_circuits") |  |
| [`rank`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.rank "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.rank") |  |
| [`shots`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.shots "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.shots") |  |
| [`gate_labels`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.gate_labels "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.gate_labels") |  |
| [`seq_len_list`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.seq_len_list "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.seq_len_list") |  |
| [`from_init`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.from_init "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.from_init") |  |
| [`max_inits`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.max_inits "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.max_inits") |  |
| [`opt_method`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.opt_method "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.opt_method") |  |
| [`max_iterations`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.max_iterations "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.max_iterations") |  |
| [`convergence_criteria`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.convergence_criteria "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.convergence_criteria") |  |
| [`batch_size`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.batch_size "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.batch_size") |  |
| [`bootstrap_samples`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.bootstrap_samples "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.bootstrap_samples") |  |
| [`verbose_level`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.verbose_level "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.verbose_level") |  |
| [`parallel_execution`](#iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.parallel_execution "iqm.benchmarks.compressive_gst.compressive_gst.GSTConfiguration.parallel_execution") |  |
| `fixed_elements` |  |
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

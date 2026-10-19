> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b50f55a3ba8b45f2e13f804570750afd748a050b9b302c7cf16d6551728eae5a.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration

*class* iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\], depths_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\], num_circuit_samples: int, num_pauli_samples: int, qiskit_optim_level: int = 1, optimize_sqg: bool = False, two_qubit_gate_ensemble: dict\[str, float\] = {'CZGate': 1.0}, density_2q_gates: float = 0.25, clifford_sqg_probability: float = 1.0, sqg_gate_ensemble: dict\[str, float\] \| None = None, simulation_method: ~typing.Literal\['automatic', 'statevector', 'stabilizer', 'extended_stabilizer', 'matrix_product_state'\] = 'stabilizer'*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Mirror RB configuration.

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

- **depths_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **num_circuit_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **num_pauli_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **two_qubit_gate_ensemble** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **density_2q_gates** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **clifford_sqg_probability** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **sqg_gate_ensemble** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*)

- **simulation_method** ([*Literal*](https://docs.python.org/3.11/library/typing.html#typing.Literal "(in Python v3.11)")*\['automatic',* *'statevector',* *'stabilizer',* *'extended_stabilizer',* *'matrix_product_state'\]*)

benchmark  
Benchmark.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits_array  
Array of physical qubits in which to execute MRB.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

depths_array  
Array of physical depths in which to execute MRB for a corresponding qubit list. If len is the same as that of qubits_array, each `Sequence[int]` corresponds to the depths for the corresponding layout of qubits. If len is different from that of `qubits_array`, assigns the first `Sequence[int]`.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]

num_circuit_samples  
Number of random-layer mirror circuits to generate.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

num_pauli_samples  
Number of random Pauli layers to interleave per mirror circuit.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

shots  
Number of measurement shots to execute per circuit.

qiskit_optim_level  
Qiskit-level of optimization to use in transpilation.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

optimize_sqg  
Whether to optimize single-qubit gates in transpilation.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

routing_method  
Routing method to use in transpilation.

two_qubit_gate_ensemble  
Two-qubit gate ensemble to use in the random mirror circuits. Keys correspond to str names of Qiskit circuit library gates, e.g., “CZGate” or “CXGate”. Values correspond to the probability for the respective gate to be sampled.

Type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]

density_2q_gates  
Expected density of 2-qubit gates in the final circuits.

Type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

clifford_sqg_probability  
Probability with which to uniformly sample Clifford 1Q gates.

Type:  
[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")

sqg_gate_ensemble  
Dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities.

Type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| None

simulation_method  
Qiskit’s Aer simulation method.

Type:  
Literal\[‘automatic’, ‘statevector’, ‘stabilizer’, ‘extended_stabilizer’, ‘matrix_product_state’\]

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.model_config "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.benchmark "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.benchmark") |  |
| [`qubits_array`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.qubits_array "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.qubits_array") |  |
| [`depths_array`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.depths_array "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.depths_array") |  |
| [`num_circuit_samples`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.num_circuit_samples "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.num_circuit_samples") |  |
| [`num_pauli_samples`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.num_pauli_samples "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.num_pauli_samples") |  |
| [`qiskit_optim_level`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.qiskit_optim_level "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.qiskit_optim_level") |  |
| [`optimize_sqg`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.optimize_sqg "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.optimize_sqg") |  |
| [`two_qubit_gate_ensemble`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.two_qubit_gate_ensemble "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.two_qubit_gate_ensemble") |  |
| [`density_2q_gates`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.density_2q_gates "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.density_2q_gates") |  |
| [`clifford_sqg_probability`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.clifford_sqg_probability "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.clifford_sqg_probability") |  |
| [`sqg_gate_ensemble`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.sqg_gate_ensemble "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.sqg_gate_ensemble") |  |
| [`simulation_method`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.simulation_method "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.simulation_method") |  |
| [`shots`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.shots "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.shots") |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| [`routing_method`](#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.routing_method "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.routing_method") |  |
| `physical_layout` |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

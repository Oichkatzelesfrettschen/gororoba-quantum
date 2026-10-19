> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd40cdd138d1bcd93f68f30a8ca6a1280d851947c6cd7b55025ecfd48a34f700.

# iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration

*class* iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRandomizedBenchmarking'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits_array: ~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\] \| ~collections.abc.Sequence\[~collections.abc.Sequence\[~collections.abc.Sequence\[int\]\]\], is_eplg: bool = False, parallel_execution: bool = False, depths: ~collections.abc.Sequence\[int\], num_circuit_samples: int, qiskit_optim_level: int = 1, two_qubit_gate_ensembles: ~collections.abc.Sequence\[dict\[str, float\]\] \| None = None, densities_2q_gates: ~collections.abc.Sequence\[float\] \| None = None, clifford_sqg_probabilities: ~collections.abc.Sequence\[float\] \| None = None, sqg_gate_ensembles: ~collections.abc.Sequence\[dict\[str, float\]\] \| None = None*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

Direct RB configuration.

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

- **qubits_array** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]\]*)

- **is_eplg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **parallel_execution** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **depths** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **num_circuit_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **two_qubit_gate_ensembles** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]* *\|* *None*)

- **densities_2q_gates** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*)

- **clifford_sqg_probabilities** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]* *\|* *None*)

- **sqg_gate_ensembles** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]* *\|* *None*)

benchmark  
DirectRandomizedBenchmarking.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits_array  
The array of physical qubits in which to execute DRB. \* It can be specified as a Sequence (e.g. list or tuple) of qubit-index registers, e.g., \[\[0, 1\], \[2, 3\]\], or as Sequences of such Sequences, e.g., \[\[\[0, 1\], \[2, 3\]\], \[\[0, 2\], \[1, 3\]\]\]. In the second case, each Sequence\[Sequence\[int\]\] will execute sequentially, i.e., execution will be done for \[\[0, 1\], \[2, 3\]\] first, then for \[\[0, 2\], \[1, 3\]\], each either in parallel or sequence, according to the (bool) value of parallel_execution.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]

is_eplg  
Whether the DRB experiment is executed as a EPLG subroutine. \* If True: - default parallel_execution below is override to True. - default two_qubit_gate_ensembles is {“CZGate”: 1.0}. - default densities_2q_gates is 0.5 (probability of sampling 2Q gates is 1). - default clifford_sqg_probabilities is 0.0. - default sqg_gate_ensembles is {“IGate”: 1.0}. \* Default is False.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

parallel_execution  
Whether DRB is executed in parallel for all qubit layouts in qubits_array. \* If is_eplg is False, it executes parallel DRB with MRB gate ensemble and density defaults.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

depths  
The list of layer depths in which to execute DRB for all qubit layouts in qubits_array.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

num_circuit_samples  
The number of random-layer DRB circuits to generate.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

shots  
The number of measurement shots to execute per circuit.

qiskit_optim_level  
The Qiskit-level of optimization to use in transpilation.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

routing_method  
The routing method to use in transpilation.

Type:  
[iqm.benchmarks.utils.RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")

two_qubit_gate_ensembles  
The two-qubit gate ensembles to use in the random DRB circuits. \* Keys correspond to str names of qiskit circuit library gates, e.g., “CZGate” or “CXGate”. \* Values correspond to the probability for the respective gate to be sampled. \* Each Dict\[str,float\] corresponds to each qubit layout in qubits_array. \* If len(two_qubit_gate_ensembles) != len(qubits_array), the first Dict is assigned by default. \* Default is None, which assigns {str(q): {“CZGate”: 1.0} for q in qubits_array}.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\] \| None

densities_2q_gates  
The expected densities of 2-qubit gates in the final circuits per qubit layout. \* If len(densities_2q_gates) != len(qubits_array), the first density value is assigned by default. \* Default is None, which assigns 0.25 to all qubit layouts.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| None

clifford_sqg_probabilities  
Probability with which to uniformly sample Clifford 1Q gates per qubit layout. \* Default is None, which assigns 1.0 to all qubit layouts.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| None

sqg_gate_ensembles  
A dictionary with keys being str specifying 1Q gates, and values being corresponding probabilities. \* If len(sqg_gate_ensembles) != len(qubits_array), the first ensemble is assigned by default. \* Default is None, which leaves only uniform sampling of 1Q Clifford gates.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\] \| None

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.model_config "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.benchmark "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.benchmark") |  |
| [`qubits_array`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.qubits_array "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.qubits_array") |  |
| [`is_eplg`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.is_eplg "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.is_eplg") |  |
| [`parallel_execution`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.parallel_execution "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.parallel_execution") |  |
| [`depths`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.depths "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.depths") |  |
| [`num_circuit_samples`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.num_circuit_samples "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.num_circuit_samples") |  |
| [`qiskit_optim_level`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.qiskit_optim_level "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.qiskit_optim_level") |  |
| [`two_qubit_gate_ensembles`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.two_qubit_gate_ensembles "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.two_qubit_gate_ensembles") |  |
| [`densities_2q_gates`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.densities_2q_gates "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.densities_2q_gates") |  |
| [`clifford_sqg_probabilities`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.clifford_sqg_probabilities "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.clifford_sqg_probabilities") |  |
| [`sqg_gate_ensembles`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.sqg_gate_ensembles "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.sqg_gate_ensembles") |  |
| [`routing_method`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.routing_method "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.routing_method") |  |
| [`shots`](#iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.shots "iqm.benchmarks.randomized_benchmarking.direct_rb.direct_rb.DirectRBConfiguration.shots") |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| `physical_layout` |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f00fb8e4fbd9bc827b6f14c20c201b8aa396d2fda65c2b28dfbf37d3beb2c91a.

# iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration

*class* iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration(*\*, benchmark: type\[~iqm.benchmarks.benchmark_definition.Benchmark\] = \<class 'iqm.benchmarks.quantum_volume.clops.CLOPSBenchmark'\>, shots: int = 256, max_gates_per_batch: int \| None = None, max_circuits_per_batch: int \| None = None, routing_method: ~iqm.benchmarks.utils.RoutingMethod = RoutingMethod.SABRE, physical_layout: ~iqm.benchmarks.utils.PhysicalLayout = PhysicalLayout.FIXED, use_dd: bool \| None = False, dd_strategy: ~iqm.station_control.interface.models.circuit.DDStrategy \| None = None, active_reset_cycles: int \| None = None, qubits: ~collections.abc.Sequence\[int\], num_circuits: int = 100, num_updates: int = 10, num_shots: int = 100, clops_h_bool: bool = False, qiskit_optim_level: int = 3, optimize_sqg: bool = True*)  
Bases: [`BenchmarkConfigurationBase`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase")

CLOPS configuration.

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

- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **num_updates** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **num_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **clops_h_bool** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **qiskit_optim_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **optimize_sqg** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

benchmark  
CLOPS Benchmark.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\]

qubits  
Sequence of physical qubit labels in which to run the benchmark. The physical qubit layout should correspond to the one used to establish QV.

Type:  
[collections.abc.Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]

num_circuits  
Number of parametrized circuit layouts. By definition of arXiv:2110.14108 \[quant-ph\] set to 100.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

num_updates  
Number of parameter assignment updates per circuit layout to perform. By definition of arXiv:2110.14108 \[quant-ph\] set to 10.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

num_shots  
Number of measurement shots per circuit to perform. By definition of arXiv:2110.14108 \[quant-ph\] set to 100.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

clops_h_bool  
Whether a CLOPS value with layer definition of CLOPS_H is estimated. Default is False. This will not estimate a rigorous CLOPS_H value (as loosely defined in www.ibm.com/quantum/blog/quantum-metric-layer-fidelity)

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

qiskit_optim_level  
Qiskit transpilation optimization level. The optimization level should correspond to the one used to establish QV.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

optimize_sqg  
Whether Single Qubit Gate Optimization is performed upon transpilation. The `optimize_sqg` value should correspond to the one used to establish QV.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

routing_method  
Qiskit transpilation routing method to use. The `routing_method` value should correspond to the one used to establish QV.

physical_layout  
Whether the coupling map is restricted to qubits in the input layout or not. “fixed” restricts the coupling map to only the specified qubits. “batching” considers the full coupling map of the backend and circuit execution is batched per final layout.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.model_config "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.benchmark "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.benchmark") |  |
| [`qubits`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.qubits "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.qubits") |  |
| [`num_circuits`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_circuits "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_circuits") |  |
| [`num_updates`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_updates "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_updates") |  |
| [`num_shots`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_shots "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.num_shots") |  |
| [`clops_h_bool`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.clops_h_bool "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.clops_h_bool") |  |
| [`qiskit_optim_level`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.qiskit_optim_level "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.qiskit_optim_level") |  |
| [`optimize_sqg`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.optimize_sqg "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.optimize_sqg") |  |
| `shots` |  |
| `max_gates_per_batch` |  |
| `max_circuits_per_batch` |  |
| [`routing_method`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.routing_method "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.routing_method") |  |
| [`physical_layout`](#iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.physical_layout "iqm.benchmarks.quantum_volume.clops.CLOPSConfiguration.physical_layout") |  |
| `use_dd` |  |
| `dd_strategy` |  |
| `active_reset_cycles` |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b69bfaed98813475cb78b7ff7aaa23d3d0632dd765117c3277ec64ad1c0094aa.

# iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase

*class* iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase(*\**, *benchmark: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\] \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 256*, *max_gates_per_batch: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *max_circuits_per_batch: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *routing_method: [RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod") = RoutingMethod.SABRE*, *physical_layout: [PhysicalLayout](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout") = PhysicalLayout.FIXED*, *use_dd: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = False*, *dd_strategy: [DDStrategy](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "(in iqm-station-control-client v14.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *active_reset_cycles: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: `BaseModel`

Benchmark configuration base.

Parameters:  
- **benchmark** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*Benchmark*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **max_gates_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **max_circuits_per_batch** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **routing_method** ([*RoutingMethod*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod"))

- **physical_layout** ([*PhysicalLayout*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout"))

- **use_dd** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* *None*)

- **dd_strategy** ([*DDStrategy*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "(in iqm-station-control-client v14.0.0)") *\|* *None*)

- **active_reset_cycles** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

benchmark  
Benchmark configuration.

Type:  
[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[iqm.benchmarks.benchmark_definition.Benchmark](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.benchmark_definition.Benchmark.html#iqm.benchmarks.benchmark_definition.Benchmark "iqm.benchmarks.benchmark_definition.Benchmark")\] \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

shots  
Number of shots to use in circuit execution. The default for all benchmarks is 2\*\*8.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

max_gates_per_batch  
Maximum number of gates per circuit batch. The default for all benchmarks is None.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

max_circuits_per_batch  
Maximum number of circuits per batch. The default for all benchmarks is None.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

routing_method  
Qiskit routing method to use in transpilation. The default for all benchmarks is “sabre”.

Type:  
[iqm.benchmarks.utils.RoutingMethod](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")

physical_layout  
Whether physical layout is constrained during transpilation to selected physical qubits. “fixed”: physical layout is constrained during transpilation to the selected initial physical qubits. “batching”: physical layout is allowed to use any other physical qubits, and circuits are batched according to final measured qubits. The default for all benchmarks is “fixed”.

Type:  
[iqm.benchmarks.utils.PhysicalLayout](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout")

use_dd  
Boolean flag determining whether to enable dynamical decoupling during circuit execution. The default for all benchmarks is False.

Type:  
[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") \| None

dd_strategy  
Dynamical decoupling strategy.

Type:  
[iqm.station_control.interface.models.circuit.DDStrategy](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html#iqm.station_control.interface.models.circuit.DDStrategy "(in iqm-station-control-client v14.0.0)") \| None

active_reset_cycles  
Number of active reset cycles to apply after each circuit execution. If None, passive reset is used.

Type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| None

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.model_config "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`benchmark`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.benchmark "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.benchmark") |  |
| [`shots`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.shots "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.shots") |  |
| [`max_gates_per_batch`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.max_gates_per_batch "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.max_gates_per_batch") |  |
| [`max_circuits_per_batch`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.max_circuits_per_batch "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.max_circuits_per_batch") |  |
| [`routing_method`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.routing_method "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.routing_method") |  |
| [`physical_layout`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.physical_layout "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.physical_layout") |  |
| [`use_dd`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.use_dd "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.use_dd") |  |
| [`dd_strategy`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.dd_strategy "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.dd_strategy") |  |
| [`active_reset_cycles`](#iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.active_reset_cycles "iqm.benchmarks.benchmark_definition.BenchmarkConfigurationBase.active_reset_cycles") |  |

Methods

model_config*: ClassVar\[ConfigDict\]* *= {}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

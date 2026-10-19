> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitMetrics.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.CircuitMetrics.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 feb3845de25c955189f63a33f6fd433c48ee699eda910ca4fd43dea1e8f19b3c.

# CircuitMetrics

Module: [`iqm.cpc.interface.circuit_execution`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.interface.circuit_execution.html#module-iqm.cpc.interface.circuit_execution "iqm.cpc.interface.circuit_execution")

*class* iqm.cpc.interface.circuit_execution.CircuitMetrics(*components*, *component_pairs_with_gates*, *gate_loci=\<factory\>*, *schedule_duration=0.0*, *min_execution_time=0.0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Metrics describing a circuit and its compilation result.

Attributes

|  |  |
|----|----|
| [`min_execution_time`](#iqm.cpc.interface.circuit_execution.CircuitMetrics.min_execution_time "iqm.cpc.interface.circuit_execution.CircuitMetrics.min_execution_time") | shots \* (instruction schedule duration + reset), in seconds. |
| [`schedule_duration`](#iqm.cpc.interface.circuit_execution.CircuitMetrics.schedule_duration "iqm.cpc.interface.circuit_execution.CircuitMetrics.schedule_duration") | Duration of the instruction schedule created for the circuit, in seconds. |
| [`components`](#iqm.cpc.interface.circuit_execution.CircuitMetrics.components "iqm.cpc.interface.circuit_execution.CircuitMetrics.components") | Locus components used by the operations in the circuit. |
| [`component_pairs_with_gates`](#iqm.cpc.interface.circuit_execution.CircuitMetrics.component_pairs_with_gates "iqm.cpc.interface.circuit_execution.CircuitMetrics.component_pairs_with_gates") | Pairs of locus components which have two-component gates between them in the circuit. |
| [`gate_loci`](#iqm.cpc.interface.circuit_execution.CircuitMetrics.gate_loci "iqm.cpc.interface.circuit_execution.CircuitMetrics.gate_loci") | Mapping from operation name to mapping from implementation name to a counter of loci of that operation in the circuit. |

Methods

Parameters:  
- **components** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **component_pairs_with_gates** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

- **gate_loci** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Counter*](https://docs.python.org/3.11/library/collections.html#collections.Counter "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]\]\]*)

- **schedule_duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **min_execution_time** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

components*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Locus components used by the operations in the circuit. Does not include things added by the compiler, for example extra probe instructions for the terminal measurement.

component_pairs_with_gates*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Pairs of locus components which have two-component gates between them in the circuit.

gate_loci*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Counter](https://docs.python.org/3.11/library/collections.html#collections.Counter "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\]\]\]*  
Mapping from operation name to mapping from implementation name to a counter of loci of that operation in the circuit.

schedule_duration*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
Duration of the instruction schedule created for the circuit, in seconds.

min_execution_time*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 0.0*  
shots \* (instruction schedule duration + reset), in seconds.

Type:  
Lower bound on the actual execution time

Inheritance

![Inheritance diagram of iqm.cpc.interface.circuit_execution.CircuitMetrics](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-6954a201a967ec8f10de7066c256744e8f77f542.png)

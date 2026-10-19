> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.BenchmarkCircuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e373736a8216727009d54dcda19c758e7c104ac51e65f5a412db49a37b37efd3.

# iqm.benchmarks.circuit_containers.BenchmarkCircuit

*class* iqm.benchmarks.circuit_containers.BenchmarkCircuit(*name: str*, *circuit_groups: list\[~iqm.benchmarks.circuit_containers.CircuitGroup\] = \<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

A class grouping a list of CircuitGroup into a single purpose.

This can typically represent, for example, all of the transpiled circuits that are executed.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **circuit_groups** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitGroup*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")*\]*)

name  
Name of the BenchmarkCircuit.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

circuit_groups  
List of CircuitGroup contained inside

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[iqm.benchmarks.circuit_containers.CircuitGroup](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")\]

Attributes

|  |  |
|----|----|
| [`group_names`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.group_names "iqm.benchmarks.circuit_containers.BenchmarkCircuit.group_names") | Names of all the contained CircuitGroup. |
| [`groups`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.groups "iqm.benchmarks.circuit_containers.BenchmarkCircuit.groups") | The circuit groups inside. |
| [`qubit_indices`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_indices "iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_indices") | Set of all the qubits used in all the CircuitGroup, represented as an integer. |
| [`qubit_layouts`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_layouts "iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_layouts") | Set of all the qubit layouts used, where the qubits are represented as an instance of Qubit. |
| [`qubit_layouts_by_index`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_layouts_by_index "iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubit_layouts_by_index") | Set of all the qubit layouts used, where the qubits are represented as an integer. |
| [`qubits`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubits "iqm.benchmarks.circuit_containers.BenchmarkCircuit.qubits") | Set of all the qubits used in all the CircuitGroup, represented as an instance of Qubit. |
| [`name`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.name "iqm.benchmarks.circuit_containers.BenchmarkCircuit.name") |  |
| [`circuit_groups`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.circuit_groups "iqm.benchmarks.circuit_containers.BenchmarkCircuit.circuit_groups") |  |

Methods

|  |  |
|----|----|
| `__eq__`(other) | Return self==value. |
| `__getitem__`(key) | Get a circuit group by name. |
| `__repr__`() | Return repr(self). |
| `__setitem__`(key, value) | Set a circuit group with the given key as its name. |
| [`get_circuit_group_by_name`](#iqm.benchmarks.circuit_containers.BenchmarkCircuit.get_circuit_group_by_name "iqm.benchmarks.circuit_containers.BenchmarkCircuit.get_circuit_group_by_name")(name) | Gets a CircuitGroup by name. |

get_circuit_group_by_name(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [CircuitGroup](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Gets a CircuitGroup by name.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the group.

Returns:  
The desired CircuitGroup, or None if it does not exist.

Return type:  
[*CircuitGroup*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup") \| None

*property* groups*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[CircuitGroup](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html#iqm.benchmarks.circuit_containers.CircuitGroup "iqm.benchmarks.circuit_containers.CircuitGroup")\]*  
The circuit groups inside.

*property* group_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*  
Names of all the contained CircuitGroup.

*property* qubit_indices*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Set of all the qubits used in all the CircuitGroup, represented as an integer.

*property* qubits*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[Qubit\]*  
Set of all the qubits used in all the CircuitGroup, represented as an instance of Qubit.

*property* qubit_layouts_by_index*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\], ...\]\]*  
Set of all the qubit layouts used, where the qubits are represented as an integer.

*property* qubit_layouts*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Qubit, ...\], ...\]\]*  
Set of all the qubit layouts used, where the qubits are represented as an instance of Qubit.

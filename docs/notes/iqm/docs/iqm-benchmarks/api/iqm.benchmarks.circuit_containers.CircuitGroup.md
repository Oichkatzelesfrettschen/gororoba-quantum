> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.circuit_containers.CircuitGroup.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 944944ff1989b3af1a032bb134d884803e321d01dde4127f8b004d456191d74e.

# iqm.benchmarks.circuit_containers.CircuitGroup

*class* iqm.benchmarks.circuit_containers.CircuitGroup(*circuits: list\[~iqm.qiskit_iqm.iqm_circuit.IQMCircuit\] = \<factory\>*, *name: str \| None = ''*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Group of IQMCircuits. It represents a list of circuits with a common purpose, typically executed in a batch.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*\]*)

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

circuits  
List of IQMCircuit.

Type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[iqm.qiskit_iqm.iqm_circuit.IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")\]

name  
Name of the group.

Type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| None

Attributes

|  |  |
|----|----|
| [`circuit_names`](#iqm.benchmarks.circuit_containers.CircuitGroup.circuit_names "iqm.benchmarks.circuit_containers.CircuitGroup.circuit_names") | Name of all the circuits contained in the group as a string. |
| [`name`](#iqm.benchmarks.circuit_containers.CircuitGroup.name "iqm.benchmarks.circuit_containers.CircuitGroup.name") |  |
| [`qubit_layouts`](#iqm.benchmarks.circuit_containers.CircuitGroup.qubit_layouts "iqm.benchmarks.circuit_containers.CircuitGroup.qubit_layouts") | The qubit layouts contained in all the circuits, where the qubits are represented by an instance of Qubit. |
| [`qubit_layouts_by_index`](#iqm.benchmarks.circuit_containers.CircuitGroup.qubit_layouts_by_index "iqm.benchmarks.circuit_containers.CircuitGroup.qubit_layouts_by_index") | The qubit layouts contained in all the circuits, where the qubits are represented by an integer. |
| [`qubits`](#iqm.benchmarks.circuit_containers.CircuitGroup.qubits "iqm.benchmarks.circuit_containers.CircuitGroup.qubits") | The set of active qubits in all of the circuits. |
| [`circuits`](#iqm.benchmarks.circuit_containers.CircuitGroup.circuits "iqm.benchmarks.circuit_containers.CircuitGroup.circuits") |  |

Methods

|  |  |
|----|----|
| `__eq__`(other) | Return self==value. |
| `__getitem__`(key) | Get a circuit by name. |
| `__repr__`() | Return repr(self). |
| `__setitem__`(key, value) | Set a circuit with the given key as its name. |
| [`add_circuit`](#iqm.benchmarks.circuit_containers.CircuitGroup.add_circuit "iqm.benchmarks.circuit_containers.CircuitGroup.add_circuit")(circuit) | Adds a circuit to the internal list. |
| [`get_circuits_by_name`](#iqm.benchmarks.circuit_containers.CircuitGroup.get_circuits_by_name "iqm.benchmarks.circuit_containers.CircuitGroup.get_circuits_by_name")(name) | Returns a list of the internal circuits that share the same name. |

*property* qubit_layouts_by_index*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), ...\], ...\]*  
The qubit layouts contained in all the circuits, where the qubits are represented by an integer.

Returns:  
All qubit layouts.

*property* qubit_layouts*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Qubit, ...\], ...\]*  
The qubit layouts contained in all the circuits, where the qubits are represented by an instance of Qubit.

Returns:  
All qubit layouts.

*property* qubits*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[Qubit\]*  
The set of active qubits in all of the circuits.

Returns:  
A set of Qubit

add_circuit(*circuit: [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Adds a circuit to the internal list.

Parameters:  
**circuit** ([*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)")) – Circuit to add.

Return type:  
None

*property* circuit_names*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Name of all the circuits contained in the group as a string.

Returns:  
List of strings

get_circuits_by_name(*name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Returns a list of the internal circuits that share the same name.

Parameters:  
**name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the circuit to return as a string

Returns:  
The circuit with the desired name as a string, or None if they are not found.

Return type:  
[*IQMCircuit*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html#iqm.qiskit_iqm.iqm_circuit.IQMCircuit "(in IQM client v36.0.0)") \| None

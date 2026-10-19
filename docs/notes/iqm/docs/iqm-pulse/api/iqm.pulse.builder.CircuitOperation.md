> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 874406f9d790f6a2416e97e7a5dea0fe3595f1d3464abe62df8d9ed61357b808.

# CircuitOperation

Module: [`iqm.pulse.builder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.html#module-iqm.pulse.builder "iqm.pulse.builder")

*class* iqm.pulse.builder.CircuitOperation(*name*, *locus*, *args=\<factory\>*, *implementation=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Specific quantum operation applied on a specific part of the QPU, e.g. in a quantum circuit.

We currently support the following native operations for circuit execution:

| name | \# of qubits | args | description |
|----|----|----|----|
| measure | \>= 1 | `key: str`, `feedback_key: str` | Measurement in the Z basis. |
| prx | 1 | `angle: float`, `phase: float` | Phased x-rotation gate. |
| cc_prx | 1 | `angle: float`, `phase: float`, `feedback_qubit: str`, `feedback_key: str` | Classically controlled PRX gate. |
| reset | \>= 1 |  | Reset the qubit(s) to \\\|0\rangle\\. |
| cz | 2 |  | Controlled-Z gate. |
| move | 2 |  | Move a qubit state between a qubit and a computational resonator, as long as at least one of the components is in the \\\|0\rangle\\ state. |
| barrier | \>= 1 |  | Execution barrier. |
| delay | \>= 1 | `duration: float` | Force a delay between circuit operations. |

For each CircuitOperation you may also optionally specify [`implementation`](#iqm.pulse.builder.CircuitOperation.implementation "iqm.pulse.builder.CircuitOperation.implementation"), which contains the name of an implementation of the operation to use. Support for multiple implementations is currently experimental and in normal use the field should be omitted, this selects the default implementation for the operation for that locus.

See the submodules under [`iqm.pulse.gates`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.html#module-iqm.pulse.gates "iqm.pulse.gates") for more details about each operation.

Attributes

|  |  |
|----|----|
| [`implementation`](#iqm.pulse.builder.CircuitOperation.implementation "iqm.pulse.builder.CircuitOperation.implementation") | name of the implementation |
| [`name`](#iqm.pulse.builder.CircuitOperation.name "iqm.pulse.builder.CircuitOperation.name") | name of the quantum operation |
| [`locus`](#iqm.pulse.builder.CircuitOperation.locus "iqm.pulse.builder.CircuitOperation.locus") | names of the information-bearing QPU components (qubits, computational resonators...) the operation acts on |
| [`args`](#iqm.pulse.builder.CircuitOperation.args "iqm.pulse.builder.CircuitOperation.args") | arguments for the operation |

Methods

|  |  |
|----|----|
| [`validate`](#iqm.pulse.builder.CircuitOperation.validate "iqm.pulse.builder.CircuitOperation.validate") | Validate the operation against a table of operation definitions. |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

- **args** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
name of the quantum operation

locus*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
names of the information-bearing QPU components (qubits, computational resonators…) the operation acts on

args*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
arguments for the operation

implementation*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
name of the implementation

validate(*op_table*)  
Validate the operation against a table of operation definitions.

Parameters:  
**op_table** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – table containing allowed quantum operations

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – operation is not valid

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.builder.CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-5acb1575b4d3815d0997b715e8b8fbaed0fe782e.png)

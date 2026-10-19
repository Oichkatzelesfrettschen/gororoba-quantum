> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f6204aeff7736dd41bd0eb66046c0e851827bcb22dcf0dc4902110dd2fa70d69.

# Circuit

Module: [`iqm.pulse.circuit_operations`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.html#module-iqm.pulse.circuit_operations "iqm.pulse.circuit_operations")

*class* iqm.pulse.circuit_operations.Circuit(*name*, *instructions*, *metadata=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Quantum circuit.

Used e.g. for client-server communication.

Consists of a sequence of native quantum operations, each represented by an instance of the `CircuitOperation` class.

Attributes

|  |  |
|----|----|
| [`metadata`](#iqm.pulse.circuit_operations.Circuit.metadata "iqm.pulse.circuit_operations.Circuit.metadata") | optional metadata for the circuit |
| [`name`](#iqm.pulse.circuit_operations.Circuit.name "iqm.pulse.circuit_operations.Circuit.name") | name of the circuit |
| [`instructions`](#iqm.pulse.circuit_operations.Circuit.instructions "iqm.pulse.circuit_operations.Circuit.instructions") | operations comprising the circuit |

Methods

|  |  |
|----|----|
| [`all_locus_components`](#iqm.pulse.circuit_operations.Circuit.all_locus_components "iqm.pulse.circuit_operations.Circuit.all_locus_components") | Return the names of all locus components (typically qubits) in the circuit. |
| [`validate`](#iqm.pulse.circuit_operations.Circuit.validate "iqm.pulse.circuit_operations.Circuit.validate") | Validate the circuit against the supported quantum operations. |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **instructions** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*,* *...\]*)

- **metadata** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*)

name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
name of the circuit

instructions*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation"), ...\]*  
operations comprising the circuit

metadata*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
optional metadata for the circuit

all_locus_components()  
Return the names of all locus components (typically qubits) in the circuit.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

validate(*supported_operations*)  
Validate the circuit against the supported quantum operations.

Parameters:  
**supported_operations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")*\]*) – mapping of supported quantum operation names to their definitions

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – circuit is not valid

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.circuit_operations.Circuit](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-e40340b9465d5807bae56f35f2c404e9e7818020.png)

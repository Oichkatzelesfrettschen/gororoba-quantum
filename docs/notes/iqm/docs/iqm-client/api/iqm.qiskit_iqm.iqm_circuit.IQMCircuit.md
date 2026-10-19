> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.IQMCircuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d42f8dcbdcb532966caab5227c1bb9d586ada2b14e3b9f8a20bd5c5fb1738fa2.

# IQMCircuit

Module: [`iqm.qiskit_iqm.iqm_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_circuit.html#module-iqm.qiskit_iqm.iqm_circuit "iqm.qiskit_iqm.iqm_circuit")

*class* iqm.qiskit_iqm.iqm_circuit.IQMCircuit(*\*regs: [Register](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Register "(in Qiskit v2.5)") \| [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [Sequence](https://docs.python.org/3.11/library/typing.html#typing.Sequence "(in Python v3.11)")\[[Bit](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Bit "(in Qiskit v2.5)")\]*, *name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *global_phase: ParameterExpression \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0*, *metadata: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *inputs: [Iterable](https://docs.python.org/3.11/library/typing.html#typing.Iterable "(in Python v3.11)")\[[Var](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Var "(in Qiskit v2.5)")\] = ()*, *captures: [Iterable](https://docs.python.org/3.11/library/typing.html#typing.Iterable "(in Python v3.11)")\[[Var](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Var "(in Qiskit v2.5)") \| [Stretch](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Stretch "(in Qiskit v2.5)")\] = ()*, *declarations: [Mapping](https://docs.python.org/3.11/library/typing.html#typing.Mapping "(in Python v3.11)")\[[Var](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Var "(in Qiskit v2.5)"), [Expr](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Expr "(in Qiskit v2.5)")\] \| [Iterable](https://docs.python.org/3.11/library/typing.html#typing.Iterable "(in Python v3.11)")\[[Tuple](https://docs.python.org/3.11/library/typing.html#typing.Tuple "(in Python v3.11)")\[[Var](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Var "(in Qiskit v2.5)"), [Expr](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit_classical#qiskit.circuit.classical.expr.Expr "(in Qiskit v2.5)")\]\] = ()*)  
Bases: [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

Extends the QuantumCircuit class, adding a shortcut for applying the MOVE gate.

Attributes

|        |                                        |
|--------|----------------------------------------|
| `name` | A human-readable name for the circuit. |

Methods

|  |  |
|----|----|
| [`move`](#iqm.qiskit_iqm.iqm_circuit.IQMCircuit.move "iqm.qiskit_iqm.iqm_circuit.IQMCircuit.move") | Applies the MOVE gate to the circuit. |

Parameters:  
- **regs** (*Register* *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *Sequence\[Bit\]*)

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **global_phase** (*ParameterValueType*)

- **metadata** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") *\|* *None*)

- **inputs** (*Iterable\[expr.Var\]*)

- **captures** (*Iterable\[expr.Var* *\|* *expr.Stretch\]*)

- **declarations** (*Mapping\[expr.Var,* *expr.Expr\]* *\|* *Iterable\[Tuple\[expr.Var,* *expr.Expr\]\]*)

move(*qubit: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *resonator: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Applies the MOVE gate to the circuit.

Note: at this point the circuit layout is only guaranteed to work if the order of the qubit and the resonator is correct (qubit first, resonator second).

Parameters:  
- **qubit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the logical index of the qubit

- **resonator** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the logical index of the resonator

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.iqm_circuit.IQMCircuit](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-530822180b5efcc604af26ea9c7c01ed3a2ba0ab.png)

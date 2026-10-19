> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3645f75e51ae5268b9c224f360482c68d38a6305af4cbe3072c4f967224e5db2.

# MoveGate

Module: [`iqm.qiskit_iqm.move_gate`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.html#module-iqm.qiskit_iqm.move_gate "iqm.qiskit_iqm.move_gate")

*class* iqm.qiskit_iqm.move_gate.MoveGate(*label: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`Gate`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.Gate "(in Qiskit v2.5)")

MOVE gate.

The MOVE operation is a unitary population exchange operation between a qubit and a resonator. Its effect is only defined in the invariant subspace \\S = \text{span}\\\|00\rangle, \|01\rangle, \|10\rangle\\\\, where it swaps the populations of the states \\\|01\rangle\\ and \\\|10\rangle\\. Its effect on the orthogonal subspace is undefined.

MOVE has the following presentation in the subspace \\S\\:

\\\text{MOVE}\_S = \|00\rangle \langle 00\| + a \|10\rangle \langle 01\| + a^{-1} \|01\rangle \langle 10\|,\\

where \\a\\ is an undefined complex phase that is canceled when the MOVE gate is applied a second time.

To ensure that the state of the qubit and resonator has no overlap with \\\|11\rangle\\, it is recommended that no single qubit gates are applied to the qubit in between a pair of MOVE operations.

Note

The MOVE gate must always be be applied on the qubit and the resonator in the order `[qubit, resonator]`, regardless of which component is currently holding the state.

Attributes

Methods

Parameters:  
**label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.move_gate.MoveGate](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-e504c4b6176278c9549ecddc633344db65bd79c5.png)

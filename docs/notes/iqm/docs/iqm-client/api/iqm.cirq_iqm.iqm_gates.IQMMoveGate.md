> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_gates.IQMMoveGate.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_gates.IQMMoveGate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e587a211f89d9f26c2d019b8bdb3231a78e057e23880d558ec3e417c58f7b0bb.

# IQMMoveGate

Module: [`iqm.cirq_iqm.iqm_gates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_gates.html#module-iqm.cirq_iqm.iqm_gates "iqm.cirq_iqm.iqm_gates")

*class* iqm.cirq_iqm.iqm_gates.IQMMoveGate(*\**, *exponent: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| Expr = 1.0*, *global_shift: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.0*)  
Bases: `EigenGate`

The MOVE gate, a unitary population exchange operation between a qubit and a resonator.

Its effect is only defined in the invariant subspace \\S = \text{span}\\\|00\rangle, \|01\rangle, \|10\rangle\\\\, where it swaps the populations of the states \\\|01\rangle\\ and \\\|10\rangle\\. Its effect on the orthogonal subspace is undefined.

MOVE has the following presentation in the subspace \\S\\:

\\\text{MOVE}\_S = \|00\rangle \langle 00\| + a \|10\rangle \langle 01\| + a^{-1} \|01\rangle \langle 10\|,\\

where \\a\\ is an undefined complex phase that is canceled when the MOVE gate is applied a second time.

To ensure that the state of the qubit and resonator has no overlap with \\\|11\rangle\\, it is recommended that no single qubit gates are applied to the qubit in between a pair of MOVE operations.

Note: At this point the locus for the move gate must be defined in the order: `[qubit, resonator]`. Additionally, the matrix representation of the gate set to be a SWAP gate, even though this is not what physically happens.

Attributes

Methods

|  |  |
|----|----|
| [`num_qubits`](#iqm.cirq_iqm.iqm_gates.IQMMoveGate.num_qubits "iqm.cirq_iqm.iqm_gates.IQMMoveGate.num_qubits") | The number of qubits this gate acts on. |

Parameters:  
- **exponent** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *Expr*)

- **global_shift** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

num_qubits() → [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")  
The number of qubits this gate acts on.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

Inheritance

![Inheritance diagram of iqm.cirq_iqm.iqm_gates.IQMMoveGate](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-7ffd984dc644e5d1f15a97b62daa4d019775c661.png)

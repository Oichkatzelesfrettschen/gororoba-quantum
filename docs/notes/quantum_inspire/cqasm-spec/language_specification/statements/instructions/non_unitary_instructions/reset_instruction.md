> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 16daf344e358a367b7935429c6725d1947d1f74b48b7169cccf81860915f64fe;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Reset instruction

A **`reset`** instruction resets the state of the qubit to $`|0\rangle`$. It does this by first measuring the qubit and then, conditioned on the outcome being 1, applying a Pauli X gate.

Note

Even though the **`reset`** instruction internally measures the qubit state, it does not store the measurement outcome in the measurement register, *i.e.*, the measurement register is unaffected by the **`reset`** instruction. The measurement outcome is only used to determine whether or not a Pauli X gate needs to be performed, in order to bring the qubit into the state $`|0\rangle`$.

The general form of a **`reset`** instruction is as follows:

 **`reset`** *qubit-argument*

Grammar for **`reset`** instruction

*reset-instruction*:\
  **`reset`** *qubit-argument*

*qubit-argument*:\
  *qubit-variable*\
  *qubit-index*

*qubit-variable*:\
  *identifier*

*qubit-index*:\
  *index*

Example

Reset of a single qubitReset of multiple qubits through their register index

```
qubit q
reset q
```

```
qubit[5] q
reset q[2, 4]
```

Note

The **`reset`** instruction accepts [SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html), similar to gates.

The following code snippet shows how the **`reset`** instruction might be used in context.

```
version 3.0

qubit[2] q
bit[2] b

H q[0]
CNOT q[0], q[1]

reset q[0]  // Resets the state of qubit q[0] to |0>

b = measure q
```

The **`reset`** instruction is performed by measuring **`q[0]`** along the computational basis. Based on the measurement outcome, either no operation is performed (in case the outcome is 0) or a Pauli X gate is applied (in case the outcome is 1). The result of the subsequent **`measure`** instruction will be **`00`** in roughly half of the cases and **`10`** in the remaining cases, with the qubit register indices decreasing from left to right, *i.e.*, **`q[n]...q[0]`**.

Info

Qubits that are part of an entangled state, are disentangled from that state, when the **`reset`** instruction is applied to them.

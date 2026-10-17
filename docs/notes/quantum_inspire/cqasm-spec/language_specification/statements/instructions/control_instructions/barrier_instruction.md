> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 9730a79abb4f4b48a04deaf660db93adf0735ab792c8f20830facc41f8ec77c1;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Barrier instruction

The **`barrier`** instruction is a single-qubit control instruction that is used to constrain the optimization of a scheduler. It tells a scheduler that instructions on the specified qubit(s) cannot be scheduled across the barrier. See the [**`wait`** instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html), to impose a time delay following a barrier.

The general form of the **`barrier`** instruction is as follows:

 **`barrier`** *qubit-argument*

Grammar for **`barrier`** instruction

*barrier-instruction*:\
  **`barrier`** *qubit-argument*

*qubit-argument*:\
  *qubit-variable*\
  *qubit-index*

*qubit-variable*:\
  *identifier*

*qubit-index*:\
  *index*

Note

The **`barrier`** instruction accepts [SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html). SGMQ notation allows you to express the application of an instruction to multiple qubits. However, SGMQ notation does not guarantee simultaneity. In general, a compiler will unpack this notation to separate consecutive single-qubit instructions on each respective qubit. This will depend on the scheduling optimization that is applied during the compilation process.

For certain backends, groups of consecutive **`barrier`** instructions are linked together to form a *uniform* barrier, across which no instructions on the specified qubits can be scheduled. Note that one can create a group of consecutive **`barrier`** instructions, *i.e.* a *uniform* barrier, using SGMQ notation.

Example

Single qubitMultiple qubits

```
qubit q
X q
barrier q
X q
```

```
qubit[3] q
X q[0]
barrier q[0, 1]
H q[0]
X q[2]
H q[1]
```

In the examples above it is shown how the **`barrier`** instruction can be used with a single qubit and multiple qubits. In the case of the single qubit, an optimizer would generally fuse the two **`X`** gates into a single identity gate, **`I`**. However, because of the presence of the **`barrier`** instruction, the user explicitly states that the instructions on **`q`** are not permitted to be optimized across the barrier. The second example shows that a barrier can be placed for multiple qubits. Note that the **`barrier`** instruction is applied to qubits **`q[0]`** and **`q[1]`**. Qubit **`q[2]`** can be optimized freely across this circuit, *i.e.*, be scheduled before or after the barrier.

The following code snippet illustrates how the **`barrier`** instruction might be used in context.

```
version 3.0

qubit[2] q
init q

// Phi+ state
H q[0]
CNOT q[0], q[1]
barrier q
b[0,1] = measure q

barrier q
reset q

// Psi+ state
H q[0]
X q[1]
CNOT q[0], q[1]
barrier q
b[2, 3] = measure q
```

In the above code snippet, the $`\Phi_{+}`$ and $`\Psi_{+}`$ Bell states are generated and measured, successively. The **`barrier`** instruction is used to guarantee that the [**`measure`** instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html) is scheduled *after* the respective states have been generated. Moreover, an extra **`barrier`** instruction is used to separate the generation and measurement of the two Bell states.

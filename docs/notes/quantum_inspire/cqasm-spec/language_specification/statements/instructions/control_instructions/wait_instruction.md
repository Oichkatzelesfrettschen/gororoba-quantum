> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 c86292d81c0f9395a17e91b54a68830f21bcd532ab9f3ae867b3200c67a87601;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Wait instruction

The **`wait`** instruction is a single-qubit control instruction that is used to constrain the optimization of a scheduler. It tells the scheduler to delay the subsequent instructions on the specified qubit(s) by a given time. The delay time is passed along with the instruction as a dimensionless parameter, the unit of which represents the duration of a single-qubit gate on the backend, *i.e.*, an execution cycle. Moreover, the **`wait`** instruction will also function as a [*barrier*](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html), telling the scheduler that instructions on the specified qubit(s) cannot be scheduled across the position of the **`wait`** instruction.

Warning

The [**`barrier`** instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html) may be considered equal to the **`wait`** instruction with a time delay set to 0. Note however that for certain backends, groups of consecutive **`barrier`** instructions are linked together to form a *uniform* barrier, across which no instructions on the specified qubits can be scheduled. This is **not** the case for the **`wait`** instruction; consecutive **`wait`** instructions on different qubits are considered to be independent instructions.

Multiple successive **`wait`** instructions on the *same* qubit, however, may be fused into a single **`wait`** instruction, where the delay time is set to the sum of the delay times of the separate instructions. For example,

```
wait(3) q[0]
wait(4) q[1]
wait(2) q[0]
```

could be optimized to:

```
wait(5) q[0]
wait(4) q[1]
```

The general form of the **`wait`** instruction is as follows:

 **`wait(`** *parameter* **`)`** *qubit-argument*

Grammar for **`wait`** instruction

*wait-instruction*:\
 **`wait(`** *parameter* **`)`** *qubit-argument*

*parameter*:\
  *integer-literal*

*qubit-argument*:\
  *qubit-variable*\
  *qubit-index*

*qubit-variable*:\
  *identifier*

*qubit-index*:\
  *index*

Note

The **`wait`** instruction accepts [SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html), similar to gates.

Example

Single qubitMultiple qubits

```
qubit q
X q
wait(5) q  // time delay of 5 execution cycles
X q
```

```
qubit[3] q
X q[0]
wait(5) q[0, 1]  // time delay of 5 execution cycles
H q[0]
X q[2]
H q[1]
```

In the examples above it is shown how the **`wait`** instruction can be used with a single qubit and multiple qubits. In the case of the single qubit, the **`wait`** instruction tells the scheduler to schedule a delay of 5 execution cycles between the successive **`X`** gates. Note that it also implicitly places a [barrier](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html) between the two **`X`** gates, such that they cannot be fused into a single identity gate, **`I`**. In the second example, using SGMQ notation, the **`wait`** instruction is applied to qubits **`q[0]`** and **`q[1]`**. Enforcing a delay of 5 execution cycles on any following instructions involving those qubits, *e.g.*, here **`H q[0]`** and **`H q[1]`**. Qubit **`q[2]`** can be optimized freely across this circuit, *i.e.*, be scheduled before or after **`wait`** instruction, regardless of any specified time delay.

The following code snippet illustrates how the **`wait`** instruction might be used in context.

```
version 3.0

qubit[2] q
bit[2] b
init q

wait(100) q[0]
b[0] = measure q[0]
```

Here, the [measurement](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html) of **`q[0]`** is forced to be scheduled at least 100 execution cycles after the [initialization](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html) of the qubit is complete.

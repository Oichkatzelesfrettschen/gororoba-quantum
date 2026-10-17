> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 25794e28a48165f67ebe319fb9238d9222cd0cf80924f0e15838bb4570370c92;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Init instruction

In general, qubits are initialized in the $`|0\rangle`$ state. Nonetheless, to explicitly initialize (particular) qubits in the $`|0\rangle`$ state one can use the **`init`** instruction. The general form of an **`init`** instruction is as follows:

 **`init`** *qubit-argument*

Grammar for **`init`** instruction

*init-instruction*:\
  **`init`** *qubit-argument*

*qubit-argument*:\
  *qubit-variable*\
  *qubit-index*

*qubit-variable*:\
  *identifier*

*qubit-index*:\
  *index*

Example

Initialize a single qubitInitialize multiple qubits through their register index

```
qubit q
init q
```

```
qubit[5] q
init q[2, 4]
```

Note

The **`init`** instruction accepts [SGMQ notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html), similar to gates.

The following code snippet shows how the **`init`** instruction might be used in context.

```
version 3.0

qubit[2] q
bit[2] b

init q  // Initializes the qubits to |0>

H q[0]
CNOT q[0], q[1]

b = measure q
```

In the code example above, the qubits are first declared and subsequently initialized. Note that the initialization of qubits needs to be done before any instruction (excluding a control instruction) is applied to them (see warning below). If one wishes to *reset* the state of the qubit to $`|0\rangle`$ mid-circuit, one should use the [**`reset`**](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html) instruction.

Warning

Initialization of a qubit can only be done immediately after declaration of the qubit, *i.e.*, it is not possible to initialize a qubit, if prior to that an instruction was applied to the qubit (excluding a control instruction).

Invalid initializationValid initialization

```
version 3.0

qubit[2] q

barrier q  // Control instructions may be applied to qubits before initialization
H q[1]

init q[1]  // Invalid use, since the H gate was applied to q[1] before initialization
```

```
version 3.0

qubit[2] q

barrier q  // Control instructions may be applied to qubits before initialization
H q[1]

init q[0]  // Valid use, because no instruction is applied to q[0] before initalization
```

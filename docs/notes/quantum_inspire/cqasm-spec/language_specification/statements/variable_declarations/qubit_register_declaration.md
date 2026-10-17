> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 ca29447772776338cef0883cc7be4acfaf8f3528c2d567c33ce43447fd8da173;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Qubit (register) declaration

A qubit (register) must be declared before it can be used. The general form is given as follows:

 **`qubit[`***size***`]`***identifier*

Grammar for bit (register) declaration

*qubit-declaration*:\
  **`qubit`** *array-size-declaration*_(opt) *identifier*

*array-size-declaration*:\
  **`[`** *integer-literal* **`]`**

Its form is similar to the declaration of an arbitrary variable, whereby the type of the variable is specified first, *i.e.* **`qubit`** denotes that the declared variable is of type [Qubit](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html). and **`qubit[`***size***`]`** denotes that the declared variable is of type [QubitArray](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html). The size of a qubit register is declared by an integer value between square brackets **`[`***size***`]`**. The name of the qubit (register) is defined through an [identifier](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html).

The declaration of a qubit (register) is *optional*.

Note

The qubit (register) declaration replaces the qubit statement, *i.e.*,

 **`qubits`** *size*

of previous versions of the cQASM language.

Find below examples, respectively, of a single qubit declaration and qubit register declaration.

Example

Single qubit declarationQubit register declaration

```
version 3

qubit q  // Single qubit declaration of a qubit named 'q'.
qubit b

H q

b = measure q
```

```
version 3

qubit[5] q  // Qubit register declaration of a register containing 5 qubits, named 'q'.
bit[2] b

H q[0]
CNOT q[0], q[1]

b[0, 1] = measure q[0, 1]
```

The individual qubits of a qubit register can be referred to by their register index, *e.g.*, in the example of the *Qubit register declaration*, the statement **`H q[0]`** indicates the application of a Hadamard gate **`H`** on the qubit located at index **`0`** of the qubit register **`q`**. Note that in the case of a single qubit, the qubit is referred to through its identifier, not through a register index.

Qubits, either declared as a single qubit or as elements of a register, are presumed to be initialized in the state $`|0\rangle`$ of the standard/computational basis.

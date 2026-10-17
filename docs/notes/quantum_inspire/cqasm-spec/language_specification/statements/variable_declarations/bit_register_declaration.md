> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/bit_register_declaration.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/bit_register_declaration.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 5ff7f3f618b6e60bc0f8b277678eccd4fc2dce0d088d155cfb770356708ebf89;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Bit (register) declaration

A bit or bit register must be declared before they can be used. The general form is given as follows:

 **`bit[`***size***`]`***identifier*

Grammar for bit (register) declaration

*bit-declaration*:\
  **`bit`** *array-size-declaration_(opt)* *identifier*

*array-size-declaration*:\
  **`[`***integer-literal***`]`**

Its form is similar to the declaration of an arbitrary variable, whereby the type of the variable is specified first, *i.e.* **`bit`** denotes that the declared variable is of type [Bit](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html). and **`bit[`***size***`]`** denotes that the declared variable is of type [BitArray](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html). The size of a bit register is declared by an integer value between square brackets **`[`***size***`]`**. The name of the bit (register) is defined through an [identifier](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html).

The declaration of a bit (register) is *optional*, Nevertheless, since measurement outcomes are stored as bits, [measure instructions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html) require a previously declared bit (register).

Find below examples, respectively, of a single bit declaration and bit register declaration.

Example

Single bit declarationBit register declaration

```
version 3

qubit q
qubit b  // Single bit declaration of a bit named 'b'.

H q

b = measure q
```

```
version 3

qubit[5] q
bit[2] b  // Bit register declaration of a register containing 2 bits, named 'b'.

H q[0]
CNOT q[0], q[1]

b[0] = measure q[0]
b[1] = measure q[1]
```

The individual bits of a bit register can be referred to by their register index, *e.g.* in the example of the *Bit register declaration*, the statement **`b[0] = measure q[0]`** indicates that the measurement outcome is stored at the bit located at index **`0`** of the bit register **`b`**. Note that in the case of a single bit, the bit is referred to through its identifier, not through a register index.

> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 0893e5a72a1faf59076d967efeb454d734f7f1e84002564f1bf2878144ad4462;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Language specification

The cQASM language specification consists of a description of its [tokens](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#tokens), [statements](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#statements), [types](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#types), and [expressions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#expressions). Additional information is provided on the [case sensitivity](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#case-sensitivity) of the language, the preferred [file extension](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#file-extension) of a cQASM program, and a brief explanation on how to interpret the [grammar sections](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#grammar-sections) of this specification.

## Tokens

A cQASM program can contain the following types of tokens:

- [Newlines](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/newlines.html)
- [Literals](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html)
- [Identifiers](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html)
- [Keywords](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html)
- [Raw text string](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/raw_text_string.html)
- [Operators and punctuators](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/operators_and_punctuators.html)

[Whitespace and comments](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/whitespace_and_comments.html) are ignored except as they serve to separate tokens.

## Statements

A cQASM program consists of a list of *statements*, more concretely, a *version statement* followed by *variable declarations* and *instructions*. In essence, a quantum algorithm is expressed via a sequence of unitary and non-unitary quantum operations applied to qubit arguments (*e.g.*, the [*measure instruction*](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html)). The unitary operations, commonly know as gates, can be either [*named gates*](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#named-gates) or compositions of [*gate modifiers*](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#gate-modifiers) acting on a named gate.

Note

For simplicity, throughout this documentation, we use the term *gate* to refer to a *named gate*. However, it is important to note that the result of applying a gate modifier is also a gate. When we need to refer explicitely to a named gate such as `H` or `Rz`, and not to a gate resulting from applying a gate modifier, we use the term *named gate*.

- [Version statement](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/version_statement.html) (*mandatory*)
- Variable declarations:
  - [Qubit (register) declaration](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/qubit_register_declaration.html)
  - [Bit (register) declaration](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/variable_declarations/bit_register_declaration.html)
- Instructions:
  - [Unitary instructions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html) (*i.e.*, gates)
  - Non-unitary instructions:
    - [Init instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/init_instruction.html)
    - [Measure instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/measure_instruction.html)
    - [Reset instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/non_unitary_instructions/reset_instruction.html)
  - Control instructions:
    - [Barrier instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/barrier_instruction.html)
    - [Wait instruction](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/control_instructions/wait_instruction.html)
  - [Single-gate-multiple-qubit (SGMQ) notation](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/single-gate-multiple-qubit-notation.html)
- [Assembly declaration](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/assembly_declaration.html)

Example cQASM programSmallest valid cQASM program

```
// Example program according to the cQASM language specification

// Version statement
version 3.0

// Qubit register declaration
qubit[3] q

// Bit register declaration
bit[2] b

// Initialization instruction
init q

// Gates
H q[0]
CNOT q[0], q[1]
CSWAP q[0], q[1], q[2]

// Reset instruction
reset q[1]

// Gate modifier
ctrl.X q[0], q[1]

// Control instruction: Barrier
barrier q[0, 1]

// Control instruction: Wait
wait(5) q[0]

// Measure instruction
b[0, 1] = measure q[0, 1]
```

```
version 3
```

## Types

The set of types supported by cQASM can be found in the section [Types](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html).

## Expressions

The following expressions can appear in a statement:

- [Indices](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/indices.html)
- [Predefined constants](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html)
- [Built-in functions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html)

## Case sensitivity

cQASM is now a case-sensitive language, in contrast to previous versions. The following lines of code are all semantically distinct

```
H q[0]
h Q[0]
```

In the first line of the example above, the Hadamard gate **`H`** is applied to the qubit at index **`0`** of the qubit register **`q`**. The next line starts with an undefined gate **`h`** that operates on the qubit at index **`0`** of the qubit register **`Q`**, which in turn does *not* refer to the qubit register **`q`**.

Take care that case sensitivity not only applies to [identifiers](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/identifiers.html), but also to all other lexical components of the language, like [keywords](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/keywords.html), [types](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/types.html), [predefined constants](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/predefined_constants.html), and [built-in functions](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/expressions/builtin_functions.html).

Note

Gate names are identifiers and are therefore case-sensitive. The syntax of the gates defined in cQASM are listed in the [cQASM standard gate set](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html). Even though it is common practice to write variable names or function identifiers in lowercase, we choose to define the gate names in the predefined cQASM standard gate set in UPPERCASE or CamelCase, as this is more in line with how these gates are represented in the field of quantum information processing (QIP).

## File extension

The preferred file extension for a cQASM file is `*.cq`.

## *How to read*

### *Grammar sections*

In the notation and grammar descriptions appearing throughout this language specification, syntactic categories are indicated by *italic* type, and literal words and characters in **`bold constant width`** type. Alternatives are listed on separate lines except in a few cases where a long set of alternatives is presented on one line, with the quantifiers 'one of', 'through', or 'or'. For example,

 one of **`a`** through **`z`** or **`A`** through **`Z`**

indicates any lowercase or uppercase alphabetic character.

An optional terminal or non-terminal symbol is indicated by the subscript _(opt), so

 **`{`** *expression*_(opt)**`}`**

indicates an optional expression enclosed in curly braces.

Names for syntactic categories have generally been chosen according to the following rules:

- *X-sequence* is one or more *X*’s without intervening delimiters, *e.g.*, *digit-sequence* is a sequence of digits.
- *X-list* is one or more *X*’s separated by intervening commas, *e.g.*, *index-list* is a sequence of indices separated by commas.

### *Qubit state ordering, measurement bit ordering, and matrix representation*

In this specification, qubit states are represented using the ket-vector notation $`|\Psi\rangle`$ and measurement outcomes are represented as bit strings.

Qubits in a ket-vector are ordered with qubit indices decreasing from left to right, *i.e.*, $`|\Psi\rangle = \sum c_i~(|q_n\rangle\otimes |q_{n-1}\rangle\otimes~...\otimes~|q_1\rangle\otimes |q_0\rangle)_i`$ $`=\sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i`$. For example, given the state $`|01\rangle`$, $`q_0`$ is in state $`|1\rangle`$ and $`q_1`$ is in state $`|0\rangle`$.

Measurement outcomes are represented by a bit string, which adheres to the same ordering convention as qubit states, *i.e.* with the (qu)bit indices decreasing from left to right.

Consider a qubit register of size 3, `qubit[3] q`, where each individual qubit can be referred to by its index as `q[0]`, `q[1]`, and `q[2]`. If the state of this qubit register is $`|110\rangle`$, then measuring it will result in the following bit string:

| `q[2]` | `q[1]` | `q[0]` |
|:------:|:------:|:------:|
|  `1`   |  `1`   |  `0`   |

The same ordering applies to bit registers, *i.e.*, for a bit register `b`, the ordering is given by `b[n-1]b[n]...b[1]b[0]`.

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

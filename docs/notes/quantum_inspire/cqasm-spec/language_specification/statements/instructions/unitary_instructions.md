> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 f6283be8a580af7f3413847a354ab886f0c0ba2e4bae3e0812bda8d218ad5888;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Unitary instructions

Unitary instructions, commonly known as gates, define single-qubit or multi-qubit operations that change the state of a qubit register in a reversible and deterministic fashion. They include:

- [named gates](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#named-gates), or
- compositions of [gate modifiers](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#gate-modifiers) acting on a named gate.

Note that a composition of gate modifiers acting on a named gate is itself a gate.

Grammar for unitary instructions

*unitary-instruction*:\
  *gate* *qubit-arguments*

*gate*:\
  *inv-gate*\
  *pow-gate*\
  *ctrl-gate*\
  *named-gate*

*inv-gate*:\
  `inv.`gate

*pow-gate*:\
  `pow(`*parameter*`).`*gate*

*ctrl-gate*:\
  `ctrl.`*gate*

*named-gate*:\
  *identifier* *parameters*_(opt)

*parameters*:\
  **`(`** *parameter-list* **`)`**

*parameter-list*:\
  *parameter*\
  *parameter-list* **`,`** *parameter*

*parameter*:\
  *integer-literal*\
  *floating-literal*

*qubit-arguments*:\
  *qubit-argument-list*

*qubit-argument-list*:\
  *qubit-argument*\
  *qubit-argument-list* **`,`** *qubit-argument*

*qubit-argument*:\
  *qubit-variable*\
  *qubit-index*

*qubit-variable*:\
  *identifier*

*qubit-index*:\
  *index*

## Named gates

Named gates comprise particular unitary operations that have been given their own unique label, *e.g.*, the [Hadamard gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) **`H`** or the [controlled-NOT gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CNOT.html) **`CNOT`**. In general, we simply refer to them as gates. All recognized (named) gates are listed in the [standard gate set](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/index.html). Moreover, we use the term *named gate* to distinguish them from unitary operations consisting of compositions of gate modifiers acting on a named gate, *i.e.*, modified gates. Named gates are, thus, unmodified gates and can simply be used on their own or modified (multiple times) through gate modifiers.

The general form of a named gate is given by the gate name followed by the (comma-separated list of) qubit operand(s), *e.g.*, [**`X q[0]`**](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html):

 *gate* *qubit-arguments*

A named gate can be parameterized. The general form of a parameterized gate is given by the gate name followed by its (comma-separated list of) parameter(s) that is enclosed in parentheses, which in turn is followed by the (comma-separated list of) qubit operand(s), *e.g.*, [**`CRk(2) q[0], q[1]`**](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html):

 *gate***`(`***parameters***`)`** *qubit-arguments*

Note that the parameters, either single or a list of multiple parameters, appear within parentheses directly following the gate name. We distinguish between the *parameters* of a parameterized gate, in terms of number [literals](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/tokens/literals.html), and the *qubit arguments* that a (parameterized) gate acts on.

A few examples of gates are shown below.

```
// A single-qubit Hadamard gate
H q[0]

// A two-qubit controlled-Z gate (control: q[0], target: q[1])
CZ q[0], q[1]

// A parameterized single-qubit Rx gate (with π/2 rotation around the x-axis)
Rx(pi/2) q[0]

// A parametrized two-qubit controlled phase-shift gate (control: q[1], target: q[0])
CRk(2) q[1], q[0]
```

## Gate modifiers

A gate modifier is an operator *Q* that takes a gate as input and returns a modified gate as output (*Q: gate → gate*), *i.e.*, it transforms an arbitrary unitary $`U`$ into $`U'`$, based on the particular modifier that is applied. We consider the following gate modifiers:

- The *inverse* modifier **`inv`**, which modifies the gate $`U`$ into $`U^\dagger`$, *e.g.*, **`inv.X q[0]`**.
- The *power* modifier **`pow`**, which raises the gate $`U`$ to the specified power $`a`$, *i.e.*, $`U^a`$, where $`a`$ is a float, *e.g.*, **`pow(pi/2).X q[0]`**.
- The *control* modifier **`ctrl`**, which changes the gate $`U`$ into the controlled-$`U`$ gate, *e.g.*, **`ctrl.X q[0], q[1]`**, where the control qubit is prepended to the list of qubit operands.

Since gate modifiers return gates, they can be applied in a nested manner, *e.g.*, **`inv.pow(2).X`**, where a gate modifier **`inv`** is applied to the modified gate **`pow(2).X`**, which in turn resulted from applying the gate modifier **`pow(2)`** on the (named) gate **`X`**.

The current version of the language only allows gate modifiers to act on single-qubit gates.

 **`inv.`***gate* *qubit-argument*\
 **`pow(`***exponent***`).`***gate* *qubit-argument*\
 **`ctrl.`***gate* *qubit-arguments*

A few examples of gates are shown below.

```
// Inverse of X
inv.X q

// S gate implemented as a power of T
pow(2).T q

// CZ implemented as a controlled-Z
ctrl.Z q[0], q[1]

// Composition of gate modifiers (modifiers are applied from right to left)
ctrl.pow(1/2).inv.X q[0], q[1]
```

Notice that, **`inv`** and **`pow`** map an *n*-qubit gate to an *n*-qubit gate, and **`ctrl`** maps an *n*-qubit gate to a (*n*+1)-qubit gate.

Warning

The current version of the language does not support the use of gate modifiers on multi-qubit gates. For example, the following instructions are *not* supported:

- **`inv.CRk(2) q[0], q[1]`**, where the *inverse* modifier is applied to a two-qubit [named gate](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#named-gates).
- **`inv.ctrl.X q[0], q[1]`**, where the *inverse* modifier is applied to a two-qubit [modified gate](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/statements/instructions/unitary_instructions.html#gate-modifiers).

Considering the latter example, note that the following use of gate modifiers *is* permitted:

- **`ctrl.inv.X q[0], q[1]`**, since the *inverse* modifier is first applied to the single-qubit named gate **`X`**, resulting in a single-qubit modified gate, which only then is modified through the *control* modifier into a two-qubit modified gate.

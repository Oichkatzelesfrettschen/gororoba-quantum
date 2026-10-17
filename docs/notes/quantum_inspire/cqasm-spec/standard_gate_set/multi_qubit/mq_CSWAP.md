> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CSWAP.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CSWAP.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 af2aed1fa0ec21278aee02fa1cea0e286a3baae0130a08ed8d12267524a628c7;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Fredkin gate

| Identifier | Operator | Example statement            |
|------------|----------|------------------------------|
| CSWAP      | $`CSWAP`$ | **`CSWAP q[0], q[1], q[2]`** |

## Description

The Fredkin gate, also known as the controlled-[SWAP](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SWAP.html) or CSWAP, gate is a three-qubit gate. It swaps the states of the second and third qubits, conditional on the state of the first qubit. The first qubit is referred to as the control qubit and the second and third qubits as the swap qubits.

In the standard computational basis for three qubits $`\{|000\rangle, |001\rangle, |010\rangle, |011\rangle, |100\rangle, |101\rangle, |110\rangle, |111\rangle\}`$, the CSWAP gate:

- leaves the control qubit unchanged;
- swaps the states of the two swap qubits when the control qubit is in state $`|1\rangle`$;
- leaves both swap qubits unchanged when the control qubit is in state $`|0\rangle`$.

Note

The notion of a control qubit and swap qubits (for any controlled operation) only holds for the standard computational basis. Generally, in another basis, all states could be affected.

### Aliases

Also known as the *controlled-SWAP* or *CSWAP* gate.

### Properties

- [Involutory](https://en.wikipedia.org/wiki/Involutory_matrix) operation (its own inverse);
- [Controlled](https://en.wikipedia.org/wiki/Quantum_logic_gate#Controlled_gates) gate;
- Universal for reversible classical computation.

## Representation

```math
\begin{align}
CSWAP &= \left(\begin{matrix}
1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\
0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 1
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
CSWAP\,|000\rangle &= |000\rangle \\
\\
CSWAP\,|001\rangle &= |001\rangle \\
\\
CSWAP\,|010\rangle &= |010\rangle \\
\\
CSWAP\,|011\rangle &= |101\rangle \\
\\
CSWAP\,|100\rangle &= |100\rangle \\
\\
CSWAP\,|101\rangle &= |011\rangle \\
\\
CSWAP\,|110\rangle &= |110\rangle \\
\\
CSWAP\,|111\rangle &= |111\rangle
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For this three-qubit controlled gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ and $`q_2`$ are the *swap* qubits; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle \otimes |q_2\rangle`$.

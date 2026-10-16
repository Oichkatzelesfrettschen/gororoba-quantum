> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SWAP.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_SWAP.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 c024482b2923518eefc88b4422259b26a5687d5769b46f1fe4bdc2d67e26209c;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# SWAP gate

| Identifier | Operator | Example statement     |
|------------|----------|-----------------------|
| SWAP       | $`SWAP`$ | **`SWAP q[0], q[1]`** |

## Description

The SWAP gate is a two-qubit gate. It *swaps* the state of the two qubits.

### Properties

- [Clifford](https://en.wikipedia.org/wiki/Clifford_gates) gate;
- [Involutory](https://en.wikipedia.org/wiki/Involutory_matrix) operation (its own inverse).

## Representation

```math
\begin{align}
SWAP &= \left(\begin{matrix}
1 & 0 & 0 & 0 \\
0 & 0 & 1 & 0 \\
0 & 1 & 0 & 0 \\
0 & 0 & 0 & 1 
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
SWAP\,|00\rangle &= |00\rangle \\
\\
SWAP\,|01\rangle &= |10\rangle \\
\\
SWAP\,|10\rangle &= |01\rangle \\
\\
SWAP\,|11\rangle &= |11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

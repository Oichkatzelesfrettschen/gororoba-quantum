> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_InvSqrtSWAP.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 49be2255be137da67f832036d89ac8b83a2e084a6339fa1a7e5853e46b08f292;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Inverse-square-root-SWAP gate

| Identifier  | Operator | Example statement            |
|-------------|----------|------------------------------|
| InvSqrtSWAP | $`\sqrt{SWAP}^\dagger`$ | **`InvSqrtSWAP q[0], q[1]`** |

## Description

The inverse-square-root-SWAP gate is a two-qubit gate. It reverses the action of the square-root-SWAP gate.

## Representation

```math
\begin{align}
\sqrt{SWAP}^\dagger &= \left(\begin{matrix}
 1 & 0 & 0 & 0 \\
 0 & \frac{1}{2} \left ( 1-i \right ) & \frac{1}{2} \left ( 1+i \right ) & 0 \\
 0 & \frac{1}{2} \left ( 1+i \right ) & \frac{1}{2} \left ( 1-i \right ) & 0 \\
 0 & 0 & 0 & 1
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
\sqrt{SWAP}^\dagger\,|00\rangle &= |00\rangle \\
\\
\sqrt{SWAP}^\dagger\,|01\rangle &= \tfrac{1}{2} \left ( 1-i \right )\,|01\rangle + \tfrac{1}{2} \left ( 1+i \right )\,|10\rangle \\
\\
\sqrt{SWAP}^\dagger\,|10\rangle &= \tfrac{1}{2} \left ( 1+i \right )\,|01\rangle + \tfrac{1}{2} \left ( 1-i \right )\,|10\rangle \\
\\
\sqrt{SWAP}^\dagger\,|11\rangle &= |11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

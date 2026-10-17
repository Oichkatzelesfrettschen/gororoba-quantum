> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ECR.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ECR.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 6542e326317cfe0df75af1865af9b85cf10825d5af0e543abe21a01c007264eb;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Echoed Cross-Resonance gate

| Identifier | Operator | Example statement    |
|------------|----------|----------------------|
| ECR        | $`ECR`$ | **`ECR q[0], q[1]`** |

## Description

The echoed cross-resonance, or ECR, gate is a two-qubit gate. It is an entangling two-qubit gate commonly used in superconducting QPUs, such as IBM quantum systems.

### Properties

- Perfect Entangler (maximally entangles specific product states);
- Maximum Entangling Power over all uniformly random product states;
- Ising gate.

## Representation

```math
\begin{align}
ECR &= \frac{1}{\sqrt{2}} \left(\begin{matrix}
 0 & 0 & 1 & i \\
 0 & 0 & i & 1 \\
 1 & -i & 0 & 0 \\
 -i & 1 & 0 & 0
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
ECR\,|00\rangle &= \tfrac{1}{\sqrt{2}} |01\rangle - \tfrac{i}{\sqrt{2}} \,|11\rangle \\
\\
ECR\,|01\rangle &= \tfrac{1}{\sqrt{2}} |00\rangle + \tfrac{i}{\sqrt{2}} \,|10\rangle \\
\\
ECR\,|10\rangle &= -\tfrac{i}{\sqrt{2}} \,|01\rangle + \tfrac{1}{\sqrt{2}} |11\rangle \\
\\
ECR\,|11\rangle &= \tfrac{i}{\sqrt{2}} \,|00\rangle + \tfrac{1}{\sqrt{2}} |10\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_M.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_M.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 33ba698eaaf3e8dd677e71794148757dae5fce5d03145c757b664e0f9743fa9b;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Magic gate

| Identifier | Operator | Example statement  |
|------------|----------|--------------------|
| M          | $`M`$ | **`M q[0], q[1]`** |

## Description

The Magic, or M, gate is a two-qubit gate. Its columns are the magic-basis vectors, which are equal to the four Bell states with specific phase factors. The magic gate is an important component in KAK circuit decomposition and is used to transform any two-qubit unitary from the standard basis to the magic basis, which makes the extraction of canonical parameters much easier than working in the computational basis.

## Properties

- Perfect Entangler (maximally entangles specific product states);
- Ising gate.

## Representation

```math
\begin{align}
M &= \frac{1}{\sqrt{2}} \left(\begin{matrix}
  1 & i & 0 & 0 \\
  0 & 0 & i & 1 \\
  0 & 0 & i & -1 \\
  1 & -i & 0 & 0
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
M\,|00\rangle &= \tfrac{1}{\sqrt{2}}|00\rangle + \tfrac{1}{\sqrt{2}}|11\rangle \\
\\
M\,|01\rangle &= \tfrac{i}{\sqrt{2}}|10\rangle + \tfrac{i}{\sqrt{2}}|01\rangle \\
\\
M\,|10\rangle &= \tfrac{i}{\sqrt{2}}|00\rangle - \tfrac{i}{\sqrt{2}}|11\rangle \\
\\
M\,|11\rangle &= \tfrac{1}{\sqrt{2}}|10\rangle - \tfrac{1}{\sqrt{2}}|01\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

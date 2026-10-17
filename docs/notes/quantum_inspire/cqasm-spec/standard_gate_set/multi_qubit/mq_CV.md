> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CV.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CV.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 14018961128cd4d5a18ad8c023c022b85db93a294f4c6faa4080cb31eaaa41ea;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# CV gate

| Identifier | Operator | Example statement   |
|------------|----------|---------------------|
| CV         | $`CV`$ | **`CV q[0], q[1]`** |

## Description

The CV gate is a two-qubit gate. Note that $`V = X^{1/2}`$, *i.e.*, CV is the controlled-square-root-of-X (CSX) gate. It performs an X90 gate on the second qubit, conditional on the state of the first qubit.

### Aliases

Also known as the, *controlled-V*, *controlled-X90*, or *controlled-square-root-of-X* gate.

### Properties

- [Controlled](https://en.wikipedia.org/wiki/Quantum_logic_gate#Controlled_gates) gate;
- Ising gate.

## Representation

```math
\begin{align}
CV &= \left(\begin{matrix}
 1 & 0 & 0 & 0\\
 0 & 1 & 0 & 0\\
 0 & 0 & \tfrac{1}{2} (1 + i) & \tfrac{1}{2} (1 - i)\\
 0 & 0 & \tfrac{1}{2} (1 - i) & \tfrac{1}{2} (1 + i)
\end{matrix}\right)
\end{align}
```

which is equal to:

```math
CV = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes V.
```

## Operation examples

### Standard basis

```math
\begin{align}
CV\,|00\rangle &= |00\rangle \\
\\
CV\,|01\rangle &= \tfrac{1}{2} (1 + i)\,|01\rangle + \tfrac{1}{2} (1 - i)\,|11\rangle \\
\\
CV\,|10\rangle &= |10\rangle \\
\\
CV\,|11\rangle &= \tfrac{1}{2} (1 - i)\,|01\rangle + \tfrac{1}{2} (1 + i)\,|11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

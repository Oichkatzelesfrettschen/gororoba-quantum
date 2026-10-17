> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CY.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CY.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 144110a33a6f8d5d60e02a58463767ae7c5bc82776751cbbfd5379cc46bc5759;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# CY gate

| Identifier | Operator | Example statement   |
|------------|----------|---------------------|
| CY         | $`CY`$ | **`CY q[0], q[1]`** |

## Description

The CY gate is a two-qubit gate. It is the controlled-Y gate. It performs a Y gate on the second qubit, conditional on the state of the first qubit.

### Properties

- [Clifford](https://en.wikipedia.org/wiki/Clifford_gates) gate;
- [Controlled](https://en.wikipedia.org/wiki/Quantum_logic_gate#Controlled_gates) gate;
- Ising gate.

## Representation

```math
\begin{align}
CY &= \left(\begin{matrix}
 1 & 0 & 0 & 0\\
 0 & 1 & 0 & 0\\
 0 & 0 & 0 & -i\\
 0 & 0 & i & 0
\end{matrix}\right)
\end{align}
```

which is equal to:

```math
CY = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes Y.
```

## Operation examples

### Standard basis

```math
\begin{align}
CY\,|00\rangle &= |00\rangle \\
\\
CY\,|01\rangle &= i\,|11\rangle \\
\\
CY\,|10\rangle &= |10\rangle \\
\\
CY\,|11\rangle &= -i\,|01\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

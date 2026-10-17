> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ISWAP.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_ISWAP.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 096a4596278405e57dcdf16d2a139b205e3c94136108983788fca929fb7ca4d6;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# iSWAP gate

| Identifier | Operator | Example statement      |
|------------|----------|------------------------|
| ISWAP      | $`iSWAP`$ | **`ISWAP q[0], q[1]`** |

## Description

The iSWAP gate is a two-qubit gate. It swaps the state of two qubits, while adding an $`i`$ phase factor to part of the state.

### Properties

- [Clifford](https://en.wikipedia.org/wiki/Clifford_gates) gate;
- Perfect Entangler (maximally entangles specific product states);
- Maximum Entangling Power over all uniformly random product states.

### Properties

- [Clifford](https://en.wikipedia.org/wiki/Clifford_gates) gate

## Representation

```math
\begin{align}
iSWAP &= \left(\begin{matrix}
 1 & 0 & 0 & 0 \\
 0 & 0 & i & 0 \\
 0 & i & 0 & 0 \\
 0 & 0 & 0 & 1
\end{matrix}\right)
\end{align}
```

## Operation examples

### Standard basis

```math
\begin{align}
iSWAP\,|00\rangle &= |00\rangle \\
\\
iSWAP\,|01\rangle &= i\,|10\rangle \\
\\
iSWAP\,|10\rangle &= i\,|01\rangle \\
\\
iSWAP\,|11\rangle &= |11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CR.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CR.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 a2bbb8dc2a0c1356ca0e63167d73f5184557e12a937e371d5fc8816e8c066043;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Controlled phase shift gate

| Identifier | Operator | Example statement       |
|------------|----------|-------------------------|
| CR         | $`CR(\theta)`$ | **`CR(pi) q[0], q[1]`** |

## Description

The Controlled phase shift, or CR, gate is a two-qubit gate. It is the controlled version of the phase shift gate, with angle $`\theta`$ (radians).

The CR gate is a generalization of the [CZ gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CZ.html): $`CZ = CR(\pi)`$

## Properties

- Ising gate.

## Representation

```math
\begin{align}
CR(\theta) &= \left(\begin{matrix}
1 & 0 & 0 &  0 \\
0 & 1 & 0 &  0 \\
0 & 0 & 1 &  0 \\
0 & 0 & 0 & e^{i\theta} 
\end{matrix}\right)
\end{align}
```

which is equal to:

```math
CR(\theta) = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes R(\theta),
```

with

```math
R(\theta) = \left(\begin{matrix}
1 & 0  \\
0 & e^{i\theta}  
\end{matrix}\right).
```

## Operation examples

### Standard basis

```math
\begin{align}
CR(\theta)\,|00\rangle &= |00\rangle \\
\\
CR(\theta)\,|01\rangle &= |01\rangle \\
\\
CR(\theta)\,|10\rangle &= |10\rangle \\
\\
CR(\theta)\,|11\rangle &= e^{i\theta}|11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

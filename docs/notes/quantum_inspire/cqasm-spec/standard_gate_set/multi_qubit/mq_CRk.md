> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 38c9a075ce338e5cef13b382790f3b87ef3724b853e711afacdb675f1a87b58d;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Parametrized controlled phase shift gate

| Identifier | Operator | Example statement       |
|------------|----------|-------------------------|
| CRk        | $`CRk(\theta)`$ | **`CRk(2) q[0], q[1]`** |

## Description

The parametrized controlled phase shift, or CRk, gate is a two-qubit gate. It is the parametrized version of the [controlled phase shift gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/multi_qubit/mq_CRk.html), with angle $`\theta`$, parametrized by an integer $`k`$: $`\theta(k) = \frac{2\pi}{2^k}`$.

The CRk gate is especially useful for calculating the Quantum Fourier Transform.

Special cases of the CRk gate include:

- $`I = CR_k(0)`$,
- $`CZ = CR_k(1)`$,
- $`CR(2\pi/2^k) = CR_k(k)`$.

## Properties

- Ising gate.

## Representation

```math
\begin{align}
CR_k(k) &= \left(\begin{matrix}
1 & 0 & 0 &  0 \\
0 & 1 & 0 &  0 \\
0 & 0 & 1 &  0 \\
0 & 0 & 0 & e^{i\frac{2\pi}{2^k}} 
\end{matrix}\right)
\end{align}
```

which is equal to:

```math
CR_k(k) = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes R_k(k),
```

with

```math
R_k(k) = \left(\begin{matrix}
1 & 0  \\
0 & e^{i\frac{2\pi}{2^k}}  
\end{matrix}\right).
```

## Operation examples

### Standard basis

```math
\begin{align}
CR_k(k)\,|00\rangle &= |00\rangle \\
\\
CR_k(k)\,|01\rangle &= |01\rangle \\
\\
CR_k(k)\,|10\rangle &= |10\rangle \\
\\
CR_k(k)\,|11\rangle &= e^{i\frac{2\pi}{2^k}}|11\rangle \\
\end{align}
```

Qubit state ordering convention and matrix representation

Note that [qubits in a ket are ordered](https://qutech-delft.github.io/cQASM-spec/latest/language_specification/index.html#qubit-state-ordering-measurement-bit-ordering-and-matrix-representation) with qubit indices decreasing from left to right, *i.e.*,

```math
|\psi\rangle = \sum c_i~|q_nq_{n-1}~...q_1q_0\rangle_i
```

Note that for matrices a **reversed** basis ordering convention is adopted, as is done in most textbooks. For instance, in the case of a two-qubit control gate, the matrix is represented such that $`q_0`$ is the *control* qubit and $`q_1`$ is the *target* qubit; the state on which the matrix is applied should then effectively be written as $`|q_0\rangle \otimes |q_1\rangle`$.

> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 13e9d36c714deaf9916d950d16a13c86a0365def3ab0b3121d4920cd85616cfe;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Pauli-X gate

| Identifier | Operator | Example statement |
|------------|----------|-------------------|
| X          | $`X`$ | **`X q[0]`**      |

## Description

The Pauli-X, or X, gate is an anti-clockwise rotation of $`\pi`$ \[rad\] about the $`\hat{\mathbf{x}}`$-axis and a global phase of $`\pi/2`$ \[rad\].

### Aliases

Also known as the *bit-flip* gate.

### Properties

- [Clifford gate](https://en.wikipedia.org/wiki/Clifford_gates)

## Representation

```math
X = \sigma_x = \sigma_1 = \left(\begin{matrix}
0 & 1 \\
1 & 0 
\end{matrix}\right)
```

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the [canonical representation $`R_\hat{\mathbf{n}}`$](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

The Pauli-X gate is given by:

```math
\begin{align}
X &= R_\hat{\mathbf{n}}\left([1, 0, 0]^T, \pi, \frac{\pi}{2}\right) = e^{i\frac{\pi}{2}} \cdot e^{-i\frac{\pi}{2} \sigma_x}, \\
\\
X &= \left(\begin{matrix}
0 & 1 \\
1 & 0 
\end{matrix}\right).
\end{align}
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the Pauli-X gate $`X_H`$ is given by:

```math
X_H = HXH = \left(\begin{matrix}
1 & 0 \\
0 & -1 
\end{matrix}\right)=Z.
```

## Operation examples

### Standard basis

```math
\begin{align}
X\,|0\rangle &= |1\rangle \\
\\
X\,|1\rangle &= |0\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
X\,|+\rangle &= |+\rangle \\
\\
X\,|-\rangle &= -|-\rangle 
\end{align}
```

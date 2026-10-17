> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Sdag.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Sdag.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 ea881ae88a8d1930727e7e986e246aa45c93912d0ee3f360aaf682a9d369c031;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# S-dagger gate

| Identifier | Operator | Example statement |
|------------|----------|-------------------|
| Sdag       | $`S^\dagger`$ | **`Sdag q[0]`**   |

## Description

The S-dagger gate, *i.e.*, the complex conjugate (inverse) of the [S gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_S.html), is an anti-clockwise rotation of $`-\pi / 2`$ \[rad\] about the $`\hat{\mathbf{z}}`$-axis and a global phase of $`-\pi / 4`$ \[rad\].

It is equal to *half* the inverse of the $`Z`$ rotation: $`S^{\dagger} = Z^{-1/2}`$.

### Aliases

Also known as the *Minus-Z90* or *mZ90* gate.

### Properties

- [Clifford gate](https://en.wikipedia.org/wiki/Clifford_gates)

## Representation

```math
\begin{align}
S^\dagger &= \left(\begin{matrix}
1 & 0 \\
0 & -i 
\end{matrix}\right)
\end{align}
```

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the [canonical representation $`R_\hat{\mathbf{n}}`$](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

The S-dagger gate is given by:

```math
\begin{align}
S^\dagger &= R_\hat{\mathbf{n}}\left([0, 0, 1]^T, -\frac{\pi}{2}, -\frac{\pi}{4}\right) = e^{-i\frac{\pi}{4}} \cdot e^{i\frac{\pi}{4}\sigma_z}, \\
\\
S^\dagger &= \left(\begin{matrix}
1 & 0 \\
0 & -i 
\end{matrix}\right).
\end{align}
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the S-dagger gate $`S^\dagger_H`$ is given by:

```math
S^\dagger_H = HS^\dagger H = \frac{1}{2}\left(\begin{matrix}
1 - i & 1 + i \\ 
1 + i & 1 - i 
\end{matrix}\right)=X^{-1/2}.
```

## Operation examples

### Standard basis

```math
\begin{align}
S^\dagger\,|0\rangle &= |0\rangle \\
\\
S^\dagger\,|1\rangle &= -i|1\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
S^\dagger\,|+\rangle &= \tfrac{1}{2}(1 - i)|+\rangle + \tfrac{1}{2}(1 + i)|-\rangle \\
\\
S^\dagger\,|-\rangle &= \tfrac{1}{2}(1 + i)|+\rangle + \tfrac{1}{2}(1 - i)|-\rangle \\
\end{align}
```

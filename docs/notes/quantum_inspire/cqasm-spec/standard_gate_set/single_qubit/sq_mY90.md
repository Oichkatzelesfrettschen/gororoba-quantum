> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mY90.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mY90.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 94d3088b780b06746fd412280d3b515174b3fad952d44ff179f351586759bb68;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# minus-Y90 gate

| Identifier | Operator | Example statement |
|------------|----------|-------------------|
| mY90       | $`Y^{-1/2}`$ | **`mY90 q[0]`**   |

## Description

The minus-Y90 gate or mY90 gate, *i.e.*, the complex conjugate (inverse) of the [Y90 gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Y90.html), is an anti-clockwise rotation of $`-\pi/2`$ \[rad\] about the $`\hat{\mathbf{y}}`$-axis and a global phase of $`-\pi/4`$ \[rad\].

It is equal to *half* the inverse of the $`Y`$ rotation: $`Y^{-1/2}`$.

### Properties

- [Clifford gate](https://en.wikipedia.org/wiki/Clifford_gates)

## Representation

```math
\begin{align}
Y^{-1/2} &= \frac{1}{2}\left(\begin{matrix}
1 - i  & 1 - i \\
-1 + i & 1 - i 
\end{matrix}\right)
\end{align}
```

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the [canonical representation $`R_\hat{\mathbf{n}}`$](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

The minus Y90 gate is given by:

```math
\begin{align}
Y^{-1/2} &= R_\hat{\mathbf{n}}\left([0, 1, 0]^T, -\frac{\pi}{2}, -\frac{\pi}{4}\right) = e^{-i\frac{\pi}{4}} \cdot e^{i\frac{\pi}{4}\sigma_y}, \\
\\
Y^{-1/2} &= \frac{1}{2}\left(\begin{matrix}
1 - i  & 1 - i \\
-1 + i & 1 - i 
\end{matrix}\right).
\end{align}
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the minus Y90 gate $`Y^{-1/2}_H`$ is given by:

```math
Y^{-1/2}_H = HY^{-1/2}H = \frac{1}{2}\left(\begin{matrix}
1 - i & -1 + i \\
1 - i & 1 - i 
\end{matrix}\right)=(Y^{-1/2})^T.
```

## Operation examples

### Standard basis

```math
\begin{align}
Y^{-1/2}\,|0\rangle &= \tfrac{1}{2}(1 - i)|0\rangle + \tfrac{1}{2}(-1 + i)|1\rangle \\
\\
Y^{-1/2}\,|1\rangle &= \tfrac{1}{2}(1 - i)|0\rangle + \tfrac{1}{2}(1 - i)|1\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
Y^{-1/2}\,|+\rangle &= \tfrac{1}{2}(1 - i)|+\rangle + \tfrac{1}{2}(1 - i)|-\rangle \\
\\
Y^{-1/2}\,|-\rangle &= \tfrac{1}{2}(-1 + i)|+\rangle + \tfrac{1}{2}(1 - i)|-\rangle \\
\end{align}
```

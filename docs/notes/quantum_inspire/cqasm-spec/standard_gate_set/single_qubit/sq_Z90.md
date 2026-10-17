> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z90.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Z90.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 024116a4ae157ca83352e231a6f6cdc689d5db1f0254925dc9fbb01e4d359fdc;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Z90 gate

| Identifier | Operator | Example statement |
|------------|----------|-------------------|
| Z90        | $`Z^{1/2}`$ | **`Z90 q[0]`**    |

## Description

The Z90 gate or Phase gate is an anti-clockwise rotation of $`\pi / 2`$ \[rad\] about the $`\hat{\mathbf{z}}`$-axis and a global phase of $`\pi / 4`$ \[rad\].

It is equal to the [S gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_S.html): $`S = Z^{1/2}`$.

### Aliases

Also known as the *S* gate.

### Properties

- [Clifford gate](https://en.wikipedia.org/wiki/Clifford_gates)

## Representation

```math
\begin{align}
Z^{1/2} &= \left(\begin{matrix}
1 & 0 \\
0 & i 
\end{matrix}\right)
\end{align}
```

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the [canonical representation $`R_\hat{\mathbf{n}}`$](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

The Z90 gate is given by:

```math
\begin{align}
Z^{1/2} &= R_\hat{\mathbf{n}}\left([0, 0, 1]^T, \frac{\pi}{2}, \frac{\pi}{4}\right) = e^{i\frac{\pi}{4}} \cdot e^{-i\frac{\pi}{4}\sigma_z}, \\
\\
Z^{1/2} &= \left(\begin{matrix}
1 & 0 \\
0 & i 
\end{matrix}\right).
\end{align}
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the Z90 gate $`Z^{1/2}_H`$ is given by:

```math
Z^{1/2}_H = HZ^{1/2}H = \frac{1}{2}\left(\begin{matrix}
1 + i & 1 - i \\ 
1 - i & 1 + i 
\end{matrix}\right)=X^{1/2}.
```

## Operation examples

### Standard basis

```math
\begin{align}
Z^{1/2}\,|0\rangle &= |0\rangle \\
\\
Z^{1/2}\,|1\rangle &= i|1\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
Z^{1/2}\,|+\rangle &= \tfrac{1}{2}(1 + i)|+\rangle + \tfrac{1}{2}(1 - i)|-\rangle \\
\\
Z^{1/2}\,|-\rangle &= \tfrac{1}{2}(1 - i)|+\rangle + \tfrac{1}{2}(1 + i)|-\rangle \\
\end{align}
```

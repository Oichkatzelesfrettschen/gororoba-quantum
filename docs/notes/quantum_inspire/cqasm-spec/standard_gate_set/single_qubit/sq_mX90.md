> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mX90.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_mX90.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 c08a32ffbe4ec7776d74a382138dce211b4cd553a292c39880b288ed64b72754;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# minus-X90 gate

| Identifier | Operator | Example statement |
|------------|----------|-------------------|
| mX90       | $`X^{-1/2}`$ | **`mX90 q[0]`**   |

## Description

The minus-X90 gate or mX90 gate, *i.e.*, the complex conjugate (inverse) of the [X90 gate](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_X90.html), is an anti-clockwise rotation of $`-\pi/2`$ \[rad\] about the $`\hat{\mathbf{x}}`$-axis and a global phase of $`-\pi/4`$ \[rad\].

It is equal to *half* the inverse of the $`X`$ rotation: $`X^{-1/2}`$.

### Aliases

Also known as the *V-dagger* gate ($`V^\dagger`$).

### Properties

- [Clifford gate](https://en.wikipedia.org/wiki/Clifford_gates)

## Representation

```math
\begin{align}
X^{-1/2} &= V^\dagger = \frac{1}{2}\left(\begin{matrix}
1 - i & 1 + i \\
1 + i & 1 - i 
\end{matrix}\right)
\end{align}
```

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the [canonical representation $`R_\hat{\mathbf{n}}`$](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

The minus X90 gate is given by:

```math
\begin{align}
X^{-1/2} &= R_\hat{\mathbf{n}}\left([1, 0, 0]^T, -\frac{\pi}{2}, -\frac{\pi}{4}\right) = e^{-i\frac{\pi}{4}} \cdot e^{i\frac{\pi}{4}\sigma_x}, \\
\\
X^{-1/2} &= \frac{1}{2}\left(\begin{matrix}
1 - i & 1 + i \\
1 + i & 1 - i 
\end{matrix}\right).
\end{align}
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the minus X90 gate $`X^{-1/2}_H`$ is given by:

```math
X^{-1/2}_H = HX^{-1/2}H = \left(\begin{matrix}
1 & 0 \\
0 & -i 
\end{matrix}\right)=S^\dagger.
```

## Operation examples

### Standard basis

```math
\begin{align}
X^{-1/2}\,|0\rangle &= \tfrac{1}{2}(1 - i)|0\rangle + \tfrac{1}{2}(1 + i)|1\rangle \\
\\
X^{-1/2}\,|1\rangle &= \tfrac{1}{2}(1 + i)|0\rangle + \tfrac{1}{2}(1 - i)|1\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
X^{-1/2}\,|+\rangle &= |+\rangle \\
\\
X^{-1/2}\,|-\rangle &= -i|-\rangle 
\end{align}
```

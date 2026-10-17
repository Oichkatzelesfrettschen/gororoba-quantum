> Full piece: [https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html)
> Retrieved 2026-10-16T21:53Z by scripts/capture_qi_docs.py --spec (urllib, pandoc);
> fetched HTML sha256 d014480baad3529d03d2bb43c7b627ebc2a2ee95c5973f6bad69c1955287102b;
> site built from QuTech-Delft/cQASM-spec gh-pages commit 91cff84b22553062cdb2aeebd968a1dd2a6a3ef6.

# Rn gate

| Identifier | Operator | Example statement            |
|------------|----------|------------------------------|
| Rn         | $`R_\hat{\mathbf{n}}(\hat{\mathbf{n}}, \theta, \phi)`$ | **`Rn(1,0,0,pi,pi/2) q[0]`** |

## Description

The canonical Rn gate is an anti-clockwise rotation with an angle of $`\theta`$ \[rad\] about the specified axis $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ and a global phase of $`\phi`$.

Note

The **`Rn`** instruction expects the separate components of the axis $`\hat{\mathbf{n}}`$, *i.e.* $`n_x`$, $`n_y`$, and $`n_z`$, as input arguments:

**`Rn(`**$`n_x`$**`,`** $`n_y`$**`,`** $`n_z`$**`,`** $`\theta`$**`,`** $`\phi`$**`)`** *qubit-argument*

as shown in the ***Example statement*** in the table above.

### Properties

The canonical representation of unitary matrices $`U(2)`$ yields special unitary matrices $`SU(2)`$, with determinant $`\text{det} = +1`$, when $`\phi`$ equals zero. $`SU(2)`$ is the special unitary group of degree $`2`$, and has a double cover of $`SO(3)`$, the group of rotations in 3-dimensional space. This means that each element in $`SO(3)`$ corresponds to two elements in $`SU(2)`$.

Operations on Spin-$`\tfrac{1}{2}`$ qubits, such as electron spin qubits, are represented by $`SU(2)`$ matrices. As an example, when a spin-qubit is operated on by an Rx gate it does not return to the same state after a $`2\pi`$ rotation, but only after a $`4\pi`$ rotation.

The difference is a global phase of $`\pi`$, which is insignificant by itself, but will be relevant when using it in combination with the *control* modifier **`ctrl`**, which changes the gate $`U`$ into the controlled- $`U`$ gate.

- [Special Unitary $`SU`$](https://en.wikipedia.org/wiki/Special_unitary_group)

## Representation

Any single-qubit operation in $`U(2)`$ (including global phase) can be expressed by 5 parameters in the canonical representation:

```math
R_\hat{\mathbf{n}}\left([n_x, n_y, n_z]^T, \theta, \phi\right) = e^{i\phi} \cdot e^{-i\frac{\theta}{2}\left(n_x\cdot\sigma_x + n_y\cdot\sigma_y + n_z\cdot\sigma_z\right)},
```

where $`\hat{\mathbf{n}}=[n_x, n_y, n_z]^T`$ denotes the axis of rotation, $`\theta\in(-\pi, \pi]`$ the angle of rotation \[rad\], and $`\phi\in[0,2\pi)`$ the global phase angle \[rad\].

Which expands to the matrix representation:

```math
R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right) = e^{i\phi} \cdot \left(\begin{matrix}
\cos\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right) & -n_y \sin\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right) \\
n_y \sin\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right) &  \cos\left(\theta / 2\right) + i n_z \sin\left(\theta / 2\right)
\end{matrix}\right).
```

In the [Hadamard](https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_H.html) basis $`\{|+\rangle, |-\rangle\}`$, the Rn gate $`R_{\hat{\mathbf{n}},H}`$ is given by:

```math
R_{\hat{\mathbf{n}},H}\left(\hat{\mathbf{n}}, \theta, \phi\right) = H R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right) H = e^{i\phi} \cdot \left(\begin{matrix}
\cos\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right) & n_y \sin\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right) \\
-n_y \sin\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right) &  \cos\left(\theta / 2\right) + i n_x \sin\left(\theta / 2\right)
\end{matrix}\right)
```

## Operation examples

### Standard basis

```math
\begin{align}
R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right)\,|0\rangle &= \left[\cos\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right)\right]|0\rangle + \left[n_y \sin\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right)\right]|1\rangle \\
\\
R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right)\,|1\rangle &= \left[-n_y \sin\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right)\right]|0\rangle + \left[\cos\left(\theta / 2\right) + i n_z \sin\left(\theta / 2\right)\right]|1\rangle \\
\end{align}
```

### Hadamard basis

```math
\begin{align}
R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right)\,|+\rangle &= \left[\cos\left(\theta / 2\right) - i n_x \sin\left(\theta / 2\right)\right]|+\rangle + \left[-n_y \sin\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right)\right]|-\rangle \\
\\
R_\hat{\mathbf{n}}\left(\hat{\mathbf{n}}, \theta, \phi\right)\,|-\rangle &= \left[n_y \sin\left(\theta / 2\right) - i n_z \sin\left(\theta / 2\right)\right]|+\rangle + \left[\cos\left(\theta / 2\right) + i n_x \sin\left(\theta / 2\right)\right]|-\rangle \\
\end{align}
```

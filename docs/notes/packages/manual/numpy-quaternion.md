# numpy-quaternion(3) -- a compiled quaternion dtype for numpy arrays

## NAME

`quaternion` 2024.0.13 (PyPI `numpy-quaternion`, Arch `python-numpy-quaternion`): a numpy
dtype `quaternion` with vectorized ufuncs, rotation conversions, interpolation (slerp,
squad), time-series calculus and rotor means. Release binding:
[../numpy-quaternion.md](../numpy-quaternion.md).

## SYNOPSIS

```python
import numpy as np
import quaternion

q = quaternion.quaternion(1, 2, 3, 4)                     # (w, x, y, z) on (1, i, j, k)
a = quaternion.as_quat_array(np.random.default_rng(0).normal(size=(1000, 4)))
a * a.conj(), np.exp(a), np.log(a), quaternion.as_float_array(a)
quaternion.as_rotation_matrix(q.normalized()), quaternion.from_rotation_vector([0, 0, np.pi / 2])
```

## DESCRIPTION

The `quaternion` scalar type is a C extension registered as a numpy dtype, so arrays of
quaternions multiply, add, exponentiate and compare element-wise in compiled loops; the
Python layer adds conversions, calculus on sampled time series (`quaternion.calculus`),
interpolation and means.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `quaternion(w, x, y, z)`, `as_quat_array`, `from_float_array`, `from_vector_part`, constants `one x y z zero` | |
| products | `* / + -`, `**`, numpy ufuncs on arrays | |
| conjugate, norm, inverse | `conj()` / `conjugate()`, `norm()` (squared magnitude), `abs()` / `absolute()`, `inverse()` / `reciprocal()`, `normalized()`, `w x y z`, `vec`, `components`, `imag`, `real` | |
| exp, log, roots | `exp()`, `log()`, `sqrt()`, `square()`, numpy `np.exp`, `np.log` | |
| rotations | `as_rotation_matrix`, `from_rotation_matrix`, `as_rotation_vector`, `from_rotation_vector`, `as_euler_angles`, `from_euler_angles`, `as_spherical_coords`, `from_spherical_coords`, `rotate_vectors`, `as_spinor_array`, `rotor_intrinsic_distance`, `rotation_chordal_distance`, ... | |
| interpolation, calculus | `slerp`, `slerp_evaluate`, `squad`, `squad_evaluate`, `unflip_rotors`, `derivative`, `antiderivative`, `definite_integral`, `indefinite_integral`, `spline*`, `angular_velocity`, `integrate_angular_velocity`, `minimal_rotation`, `mean_rotor_in_chordal_metric`, `optimal_alignment_in_*` | |
| parity | `x_parity_conjugate` and the other `*_parity_*` methods | |
| associator, commutator, matrices | none (associative); `as_float_array` gives `[..., 4]` floats | |
| symbolic support | none; float64 components | |
| dimension range | D = 4 | |
| dtype, batching, GPU | numpy dtype; vectorized on CPU; no GPU | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import quaternion
print([n for n in dir(quaternion) if not n.startswith("_") and n not in ("np", "numba_wrapper")])
q = quaternion.quaternion(1, 2, 3, 4)
print([n for n in dir(q) if not n.startswith("_") and n not in dir(__import__("numpy").ndarray)])
```

```text
['allclose', 'angular_velocity', 'antiderivative', 'as_euler_angles', 'as_float_array', 'as_quat_array', 'as_rotation_matrix', 'as_rotation_vector', 'as_spherical_coords', 'as_spinor_array', 'as_vector_part', 'calculus', 'definite_integral', 'derivative', 'fd_definite_integral', 'fd_derivative', 'fd_indefinite_integral', 'from_euler_angles', 'from_float_array', 'from_rotation_matrix', 'from_rotation_vector', 'from_spherical_coords', 'from_vector_part', 'indefinite_integral', 'integrate_angular_velocity', 'isclose', 'mean_rotor_in_chordal_metric', 'means', 'minimal_rotation', 'numpy_quaternion', 'one', 'optimal_alignment_in_Euclidean_metric', 'optimal_alignment_in_chordal_metric', 'quaternion', 'quaternion_time_series', 'rotate_vectors', 'rotation_chordal_distance', 'rotation_intrinsic_distance', 'rotor_chordal_distance', 'rotor_intrinsic_distance', 'slerp', 'slerp_evaluate', 'spline', 'spline_definite_integral', 'spline_derivative', 'spline_indefinite_integral', 'squad', 'squad_evaluate', 'unflip_rotors', 'x', 'y', 'z', 'zero']
['a', 'abs', 'absolute', 'angle', 'b', 'components', 'copysign', 'equal', 'exp', 'greater', 'greater_equal', 'inverse', 'isfinite', 'isinf', 'isnan', 'less', 'less_equal', 'log', 'norm', 'normalized', 'not_equal', 'parity_antisymmetric_part', 'parity_conjugate', 'parity_symmetric_part', 'reciprocal', 'sqrt', 'square', 'vec', 'w', 'x', 'x_parity_antisymmetric_part', 'x_parity_conjugate', 'x_parity_symmetric_part', 'y', 'y_parity_antisymmetric_part', 'y_parity_conjugate', 'y_parity_symmetric_part', 'z', 'z_parity_antisymmetric_part', 'z_parity_conjugate', 'z_parity_symmetric_part']
```

2. The table against `cd_core`, vectorized products, and the meaning of `norm()`.

<!-- example -->
```python
import numpy as np
import quaternion
from cd_core import cd_sign
u = [quaternion.quaternion(*np.eye(4)[k]) for k in range(4)]
bad = sum(quaternion.as_float_array(u[p] * u[q])[p ^ q] != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("mismatches", bad)
a = quaternion.as_quat_array(np.random.default_rng(0).normal(size=(100000, 4)))
print((a * a.conj()).dtype, a.shape, np.allclose(quaternion.as_float_array(a * a.conj())[:, 0], np.abs(a) ** 2))
q = quaternion.quaternion(1, 2, 3, 4)
print("norm", q.norm(), " abs", abs(q))
```

```text
mismatches 0
quaternion (100000,) True
norm 30.0  abs 5.477225575051661
```

3. Rotations, exp and log.

<!-- example -->
```python
import numpy as np
import quaternion
r = quaternion.from_rotation_vector([0, 0, np.pi / 2])
print(np.round(quaternion.as_rotation_matrix(r), 12).tolist())
print(np.round(quaternion.rotate_vectors(r, [1, 0, 0]), 12).tolist())
q = quaternion.quaternion(0.3, 0.1, -0.2, 0.4)
print(np.allclose(quaternion.as_float_array(np.exp(np.log(q))), [0.3, 0.1, -0.2, 0.4]))
```

```text
[[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
[0.0, 1.0, 0.0]
True
```

4. `copy.copy` and `copy.deepcopy` of a quaternion scalar return objects that share storage.

<!-- example -->
```python
import copy
import quaternion
q = quaternion.quaternion(1, 2, 3, 4)
r = copy.deepcopy(q)
r.w = 0
print("q after writing r.w:", q)
s = quaternion.quaternion(q.w, q.x, q.y, q.z)
s.x = 9
print("q after writing a constructed copy:", q)
```

```text
q after writing r.w: quaternion(0, 2, 3, 4)
q after writing a constructed copy: quaternion(0, 2, 3, 4)
```

## MAPPING TO cd_core

Identity at D = 4: components `(w, x, y, z)` are `cd_core` `(e0, e1, e2, e3)` (EXAMPLES 2;
`docs/evidence/algebra_packages/tables.json`, [checks](checks/interplay_tables.json)).
[Octonion-Sedenion](octonion-sedenion.md) doubles over this dtype;
[Cayley-Calculator](cayley-calculator.md) only accepts it as constructor input, and
[hyprat](hyprat.md) converts to and from it.

## TRAPS

- `norm()` is the squared magnitude (the Cayley norm); `abs()` is the magnitude (EXAMPLES 2).
- `copy.copy` and `copy.deepcopy` of a scalar share storage, so writing a component of the
  copy writes the original (EXAMPLES 4); construct a new quaternion from the components.
  This aliasing is the mechanism behind [Octonion-Sedenion](octonion-sedenion.md)'s
  in-place `polar()` defect.
- The module name `quaternion` differs from the distribution name and from `quaternionic`
  and `pyquaternion`.

## LICENSE

MIT (dist-info `License-Expression`).

## SEE ALSO

[quaternionic](quaternionic.md), [pyquaternion](pyquaternion.md), [interplay](../interplay.md).

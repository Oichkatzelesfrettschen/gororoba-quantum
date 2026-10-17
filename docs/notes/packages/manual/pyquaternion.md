# pyquaternion(3) -- scalar quaternions for 3D rotation bookkeeping

## NAME

`pyquaternion` 0.9.9 (PyPI `pyquaternion`, Arch `python-pyquaternion`): a pure-Python
`Quaternion` class with rotation constructors, matrices, exp and log maps, slerp,
distances and integration. Release binding: [../pyquaternion.md](../pyquaternion.md).

## SYNOPSIS

```python
from pyquaternion import Quaternion

q = Quaternion(1, 2, 3, 4)                         # (w, x, y, z)
r = Quaternion(axis=[0, 0, 1], angle=3.14159265 / 2)
q * r, q.conjugate, q.inverse, q.norm, r.rotate([1, 0, 0]), r.rotation_matrix
Quaternion.exp(q), Quaternion.log(q), Quaternion.slerp(q.unit, r, 0.5)
```

## DESCRIPTION

`Quaternion` stores a length-4 numpy array `q` and implements the Hamilton product in
Python (the installed `pyquaternion/quaternion.py`). Constructors accept four scalars, an
array, a rotation matrix, axis and angle, or another quaternion.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `Quaternion(w, x, y, z)`, `Quaternion(array=...)`, `Quaternion(matrix=...)`, `Quaternion(axis=..., angle=... or radians=... or degrees=...)`, `Quaternion.random()` | |
| products | `* / + - **`, `@` | |
| conjugate, norm, inverse | `conjugate`, `inverse`, `norm` and `magnitude` (the magnitude), `unit` / `normalised`, `is_unit()`, `w x y z`, `elements`, `scalar` / `real`, `vector` / `imaginary` | properties |
| exp, log | `Quaternion.exp(q)`, `Quaternion.log(q)`, `exp_map`, `log_map`, `sym_exp_map`, `sym_log_map` | |
| rotations | `rotate(v)`, `rotation_matrix`, `transformation_matrix`, `axis`, `get_axis()`, `angle`, `radians`, `degrees`, `yaw_pitch_roll`, `polar_angle`, `polar_unit_vector`, `polar_decomposition` | |
| interpolation, calculus | `slerp`, `intermediates`, `derivative`, `integrate` | |
| distances | `absolute_distance`, `distance`, `sym_distance` | |
| associator, commutator, matrices | none (associative) | |
| symbolic support | none; float64 array | |
| dimension range | D = 4 | |
| dtype, batching, GPU | scalar objects only | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
from pyquaternion import Quaternion
print(sorted(n for n in dir(Quaternion) if not n.startswith("_")))
```

```text
['absolute_distance', 'angle', 'axis', 'conjugate', 'degrees', 'derivative', 'distance', 'elements', 'exp', 'exp_map', 'get_axis', 'imaginary', 'integrate', 'intermediates', 'inverse', 'is_unit', 'log', 'log_map', 'magnitude', 'norm', 'normalised', 'polar_angle', 'polar_decomposition', 'polar_unit_vector', 'radians', 'random', 'real', 'rotate', 'rotation_matrix', 'scalar', 'slerp', 'sym_distance', 'sym_exp_map', 'sym_log_map', 'to_degrees', 'to_radians', 'transformation_matrix', 'unit', 'vector', 'w', 'x', 'y', 'yaw_pitch_roll', 'z']
```

2. The table against `cd_core`; `norm` is the magnitude; rotation of a vector.

<!-- example -->
```python
import numpy as np
from pyquaternion import Quaternion
from cd_core import cd_sign
u = [Quaternion(*np.eye(4)[k]) for k in range(4)]
bad = sum((u[p] * u[q]).elements[p ^ q] != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("mismatches", bad)
q = Quaternion(1, 2, 3, 4)
print("norm", q.norm, " magnitude", q.magnitude)
r = Quaternion(axis=[0, 0, 1], angle=np.pi / 2)
print(np.round(r.rotate([1, 0, 0]), 12).tolist())
print(np.allclose(Quaternion.exp(Quaternion.log(q)).elements, q.elements))
```

```text
mismatches 0
norm 5.477225575051661  magnitude 5.477225575051661
[0.0, 1.0, 0.0]
True
```

## MAPPING TO cd_core

Identity at D = 4 on `(w, x, y, z)` = `(e0, e1, e2, e3)` (EXAMPLES 2;
`docs/evidence/algebra_packages/tables.json`, [checks](checks/interplay_tables.json)).
[pyoctonion](pyoctonion.md) multiplies through this class.

## TRAPS

- `norm` here is the magnitude, while numpy-quaternion and quaternionic call the squared
  magnitude `norm` (EXAMPLES 2).
- Scalar objects only; arrays belong to numpy-quaternion or quaternionic.

## LICENSE

MIT (dist-info `License: MIT`).

## SEE ALSO

[pyoctonion](pyoctonion.md), [numpy-quaternion](numpy-quaternion.md), [interplay](../interplay.md).

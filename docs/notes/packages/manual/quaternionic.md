# quaternionic(3) -- numba-accelerated quaternion arrays as a numpy subclass

## NAME

`quaternionic` 1.0.18 (PyPI `quaternionic`, Arch `python-quaternionic`): `quaternionic.array`,
a numpy subclass whose last axis of length 4 holds `(w, x, y, z)`, with numba-compiled
algebra ufuncs, rotation converters, distances, alignment and interpolation. Release
binding: [../quaternionic.md](../quaternionic.md).

## SYNOPSIS

```python
import numpy as np
import quaternionic

q = quaternionic.array([1, 2, 3, 4])
a = quaternionic.array(np.random.default_rng(0).normal(size=(1000, 4)))
a * a.conjugate(), np.exp(a), np.log(a), a.ndarray, a.to_rotation_matrix
quaternionic.array.from_rotation_vector([0, 0, np.pi / 2])
```

## DESCRIPTION

`quaternionic.array` subclasses `numpy.ndarray`; `QuaternionicArray(jit, dtype)` builds the
class around numba-compiled ufuncs (`quaternionic.algebra`). Properties
(`quaternionic.properties`) and converters (`quaternionic.converters`) are attached as
attributes and class methods.

## API SURFACE

Enumerated in EXAMPLES 1.

| Capability | API | Behavior |
|---|---|---|
| construction | `array(input)`, `array.from_scalar_part`, `from_vector_part`, `from_rotation_matrix`, `from_rotation_vector`, `from_axis_angle`, `from_euler_angles`, `from_euler_phases`, `from_spherical_coordinates`, `from_angular_velocity`, `array.random`; constants `one i j k x y z` | |
| products | `* / + -`, `**`, `algebra_ufuncs` (`multiply`, `divide`, `float_power`, `bitwise_or`, `bitwise_xor`, `left_shift`, `right_shift`, ...) | |
| conjugate, norm, inverse | `conjugate()` / `conj`, `inverse`, `norm` (squared magnitude), `abs`, `magnitude`, `modulus`, `mag2`, `abs2`, `absolute_square`, `normalized`, `w x y z i j k`, `scalar`, `vector`, `ndarray` | |
| exp, log, roots | `np.exp`, `np.log`, `np.sqrt`, `np.square` through the ufuncs | |
| rotations | `rotate`, `to_rotation_matrix`, `to_transformation_matrix`, `to_rotation_vector`, `to_axis_angle`, `to_euler_angles`, `to_euler_phases`, `to_spherical_coordinates`, `to_angular_velocity`, `to_minimal_rotation`, `canonicalized`, `two_spinor` | |
| distances, alignment, interpolation | `quaternionic.distance` (`rotor`, `rotation` metrics), `align`, `slerp`, `squad`, `unflip_rotors` | |
| associator, commutator, matrices | none (associative) | |
| symbolic support | none | |
| dimension range | D = 4 | |
| dtype, batching, GPU | float64 arrays; numba JIT on CPU; no GPU | |

## EXAMPLES

1. Public surface.

<!-- example -->
```python
import numpy as np
import quaternionic
print([n for n in dir(quaternionic) if not n.startswith("_") and n not in ("importlib_metadata",)])
q = quaternionic.array([1, 2, 3, 4])
print(sorted(n for n in dir(q) if not n.startswith("_") and n not in dir(np.ndarray)))
```

```text
['QuaternionicArray', 'algebra', 'algebra_ufuncs', 'align', 'alignment', 'array', 'arrays', 'boolean', 'converters', 'distance', 'float64', 'guvectorize', 'i', 'interpolation', 'j', 'jit', 'k', 'one', 'properties', 'slerp', 'squad', 'unflip_rotors', 'utilities', 'x', 'y', 'z']
['abs', 'abs2', 'absolute_square', 'canonicalized', 'flattened', 'from_angular_velocity', 'from_axis_angle', 'from_euler_angles', 'from_euler_phases', 'from_rotation_matrix', 'from_rotation_vector', 'from_scalar_part', 'from_spherical_coordinates', 'from_vector_part', 'i', 'inverse', 'iterator', 'j', 'k', 'mag2', 'magnitude', 'modulus', 'ndarray', 'norm', 'normalized', 'random', 'rotate', 'scalar', 'to_angular_velocity', 'to_axis_angle', 'to_euler_angles', 'to_euler_phases', 'to_minimal_rotation', 'to_rotation_matrix', 'to_rotation_vector', 'to_scalar_part', 'to_spherical_coordinates', 'to_transformation_matrix', 'to_vector_part', 'two_spinor', 'vector', 'w', 'x', 'y', 'z']
```

2. The table against `cd_core`; `norm` is the squared magnitude.

<!-- example -->
```python
import numpy as np
import quaternionic
from cd_core import cd_sign
u = [quaternionic.array(np.eye(4)[k]) for k in range(4)]
bad = sum((u[p] * u[q]).ndarray[p ^ q] != cd_sign(4, p, q) for p in range(4) for q in range(4))
print("mismatches", bad)
q = quaternionic.array([1, 2, 3, 4])
print("norm", q.norm, " abs", q.abs, " mag2", q.mag2)
```

```text
mismatches 0
norm 30.0  abs 5.477225575051661  mag2 30.0
```

3. Rotations and exp, log on arrays; a scalar's component access goes through `.ndarray`.

<!-- example -->
```python
import numpy as np
import quaternionic
r = quaternionic.array.from_rotation_vector([0, 0, np.pi / 2])
print(np.round(r.to_rotation_matrix, 12).tolist())
a = quaternionic.array(np.random.default_rng(1).normal(size=(5, 4)) * 0.3)
print(np.allclose(np.exp(np.log(a)).ndarray, a.ndarray))
q = quaternionic.array([1, 2, 3, 4])
print(q.ndarray[1], q.x)
try:
    q[1]
except ValueError as e:
    print("ValueError:", e)
```

```text
[[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
True
2.0 2.0
ValueError: len(input_array.shape) == 0
```

## MAPPING TO cd_core

Identity at D = 4 on `(w, x, y, z)` = `(e0, e1, e2, e3)` (EXAMPLES 2;
`docs/evidence/algebra_packages/tables.json`, [checks](checks/interplay_tables.json)).

## TRAPS

- `norm` is the squared magnitude; `abs` and `magnitude` are the magnitude (EXAMPLES 2).
- Indexing a single quaternion (`q[1]`) raises `ValueError`; read `q.ndarray` (EXAMPLES 3).
- The first call of each function compiles with numba.

## LICENSE

MIT (dist-info `License`).

## SEE ALSO

[numpy-quaternion](numpy-quaternion.md), [pyquaternion](pyquaternion.md), [interplay](../interplay.md).

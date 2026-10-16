# numpy-quaternion 2024.0.13

- Release: [PyPI numpy-quaternion 2024.0.13](https://pypi.org/project/numpy-quaternion/2024.0.13/), sdist sha256 `e155853fefdfb972b4674f47c30ddb12c825f3ab135a2ea14c67472905c49fd1`; source [moble/quaternion](https://github.com/moble/quaternion); MIT.
- Module: `quaternion`; a compiled numpy dtype. Arch package python-numpy-quaternion (AUR); a Kaggle kernel installs the pinned wheel.

## What it implements

A `quaternion` numpy dtype with vectorized arithmetic, `as_float_array`,
rotations, slerp and squad. Octonion-Sedenion builds its higher levels on
it; Cayley-Calculator accepts its quaternions as constructor input and
multiplies without it (with `import quaternion` blocked its D = 16 table is
still identical to `cd_core`, interplay.md).

## Relation to cd_core

`quaternion(w, x, y, z)` with components in the order (1, i, j, k) has the
D = 4 table of `cd_core` exactly (i j = k, j i = -k), checked on all 16 basis
pairs.

## Correct use

- Large arrays of quaternions: rotations, rotor fields, batched products.
- The quaternion coefficient algebra beneath an octonion or sedenion
  doubling, as Octonion-Sedenion uses it.

## Pitfalls

- The dtype is compiled; `--install` takes the wheel and `--extract` binds
  only its Python files to the sdist.
- Its module name is `quaternion`, distinct from `quaternionic` and
  `pyquaternion`.

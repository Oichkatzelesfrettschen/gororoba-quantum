# pyquaternion 0.9.9

- Release: [PyPI pyquaternion 0.9.9](https://pypi.org/project/pyquaternion/0.9.9/), sdist sha256 `b1f61af219cb2fe966b5fb79a192124f2e63a3f7a777ac3cadf2957b1a81bea8`; source [KieranWynn/pyquaternion](https://github.com/KieranWynn/pyquaternion); MIT.
- Module: `pyquaternion`; pure Python on numpy. Arch package python-pyquaternion (AUR).

## What it implements

A scalar `Quaternion(w, x, y, z)` class for 3D rotations: axis-angle,
rotation matrices, slerp, `.elements`.

## Relation to cd_core

Identical to the D = 4 table of `cd_core`, checked on all 16 basis pairs.

## Correct use

- Single quaternions in rotation bookkeeping; pyoctonion multiplies through it.

## Pitfalls

- Scalar objects only; arrays of quaternions belong to numpy-quaternion or
  quaternionic.

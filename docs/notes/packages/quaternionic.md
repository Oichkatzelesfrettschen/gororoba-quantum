# quaternionic 1.0.18

- Release: [PyPI quaternionic 1.0.18](https://pypi.org/project/quaternionic/1.0.18/), sdist sha256 `9c5ee261650a52d09b9319e66b59dfa69d0b2025ab0db3eba6dff6ec63f5443b`; source [moble/quaternionic](https://github.com/moble/quaternionic); MIT.
- Module: `quaternionic`; numba-accelerated. Arch package python-quaternionic (AUR, built from the v1.0.18 tag; its installed files are byte-identical to the sdist).

## What it implements

`quaternionic.array`, a numpy subclass whose last axis of length 4 holds
(w, x, y, z), with numba-compiled products, exp, log, rotations and
spin-weighted function support (the `spherical` package builds on it).

## Relation to cd_core

Identical to the D = 4 table of `cd_core`, checked on all 16 basis pairs.

## Correct use

- Pure-numpy quaternion arrays with numba speed, where a compiled dtype
  (numpy-quaternion) is unwanted.

## Pitfalls

- Indexing a single quaternion's component (`q[1]`, or iterating `q`)
  raises `ValueError: len(input_array.shape) == 0`; read components through
  `q.ndarray`.
- The first call of each function compiles with numba.

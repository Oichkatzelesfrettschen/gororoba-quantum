# pyoctonion 3.12

- Release: [PyPI pyoctonion 3.12](https://pypi.org/project/pyoctonion/3.12/), sdist sha256 `a0ed5c58dc0f19368cc794eb076403b48a7cc6e35cf0a8bfe1e45f7d6b906d0c`; no license file or license metadata.
- Module: `pyoctonion`; pure Python on numpy, sympy and pyquaternion. Arch package python-pyoctonion (local PKGBUILD).

## What it implements

`Octonion(x_0, ..., x_7)` with multiplication by the doubling on two
pyquaternion halves, `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`,
conjugate, norm and inverse.

## Relation to cd_core

The doubling formula is the one `cd_core` uses, and the D = 8 table is
identical to `cd_core` on all 64 basis pairs.

## Correct use

- Reading and small cross-checks of octonion identities; it is a third
  independent octonion implementation beside hypercomplex and cayley-dickson.

## Pitfalls

- It imports `pyquaternion`, which its metadata does not declare; the local
  PKGBUILD depends on python-pyquaternion.
- `cal_multiply(x, y)` prints every product to stdout; the `*` operator
  returns an `Octonion` without printing.
- No license accompanies the code: read and cross-check only, vendor nothing.

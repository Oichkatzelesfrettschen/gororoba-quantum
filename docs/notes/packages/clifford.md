# clifford 1.5.1

- Release: [PyPI clifford 1.5.1](https://pypi.org/project/clifford/1.5.1/), sdist sha256 `3484b312cff0e2d5e14fb99409b8242193c358dfaa6af7bc6ea230c4606e66f3`; source [pygae/clifford](https://github.com/pygae/clifford); BSD-3-Clause.
- Module: `clifford`; numba-accelerated. Arch package python-clifford (local PKGBUILD).

## What it implements

Numerical geometric algebra `Cl(p, q)` of any signature: `clifford.Cl(p, q)`
returns a layout and its blades; multivectors carry the geometric, inner and
outer products, reversion, duals, rotors and conformal geometric algebra.

## Relation to cd_core

`Cl(0, 2)` on blades (1, e1, e2, e12) in the layout's bitmask order is the
quaternion algebra, identical to the D = 4 table of `cd_core` on all 16
basis pairs; its (1, e1) block is `Cl(0, 1)`, the complex numbers (D = 2).
A Clifford algebra is associative, so no signature yields the octonions or
sedenions: a Clifford result enters the evidence only through these two
subalgebras.

## Correct use

- Rotors, spinors and reflections: `Cl(3)` or `Cl(0, 3)` for rotations,
  conformal GA for rigid motions.
- Associative baselines beside a Cayley-Dickson computation, for instance
  the quaternion subalgebra `<e_0, e_i, e_j, e_i e_j>` of an octonion triple.

## Pitfalls

- Blade names follow the layout (`e12`, `e123`); read `layout.names` before
  indexing `.value`.
- A signature `Cl(p, q)` puts the first p generators at square +1; the
  quaternions need q = 2 with p = 0.
- The first operation compiles with numba and takes seconds.

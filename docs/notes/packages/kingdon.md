# kingdon 3.0.0

- Release: [PyPI kingdon 3.0.0](https://pypi.org/project/kingdon/3.0.0/), sdist sha256 `77e6f3442b30f75daae33c73dc6086f175e9c70e5c2809bf411ecf7ff97d6e92`; source [tBuLi/kingdon](https://github.com/tBuLi/kingdon); MIT.
- Module: `kingdon`. Arch package python-kingdon (local PKGBUILD).

## What it implements

Geometric algebra `Algebra(p, q, r)` with code-generated products that run
on numpy, sympy symbols, PyTorch or JAX arrays, and projective and conformal
GA; `anywidget` drives its notebook graphics.

## Relation to cd_core

`Algebra(p=0, q=2)` on blades (e, e1, e2, e12) is identical to the D = 4
table of `cd_core` on all 16 basis pairs. The octonions and sedenions have
no Clifford image (see [clifford](clifford.md)).

## Correct use

- Symbolic or batched geometric-algebra products where one code path runs
  on numpy, sympy and torch alike.

## Pitfalls

- `blades` keys are names; a product's `keys()` are blade bitmasks
  (e12 is 3).
- Import pulls in `anywidget` for graphics even in a headless run.

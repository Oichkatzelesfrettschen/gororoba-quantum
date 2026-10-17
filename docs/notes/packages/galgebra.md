# galgebra 0.6.0

- Release: [PyPI galgebra 0.6.0](https://pypi.org/project/galgebra/0.6.0/), sdist sha256 `2e8db0172286bcb7ff6d37c4d7e99476ffe178570dea78a2345d34cc78da10f1`; source [pygae/galgebra](https://github.com/pygae/galgebra); BSD-3-Clause.
- Module: `galgebra`; symbolic, on SymPy. Arch package python-galgebra (local PKGBUILD).

## What it implements

Symbolic geometric algebra and geometric calculus: `Ga.build` with any
metric, including curvilinear coordinates, gradient operators and
LaTeX output.

## Relation to cd_core

`Ga.build("e1 e2", g=[-1, -1])` on (1, e1, e2, e1^e2) is identical to the
D = 4 table of `cd_core` on all 16 basis pairs; the octonions and sedenions
have no Clifford image (see [clifford](clifford.md)).

## Correct use

- Exact symbolic identities in an associative algebra, for instance a
  closed-form rotor or a metric-dependent sign, cross-checked against
  clifford's numbers.

## Pitfalls

- A one-generator `Ga.build("e1", g=[-1])` raises
  `ValueError: coords must be entered`; build `Cl(0, 2)` and use its
  (1, e1) block for the complex numbers.
- `ga.mv(1, "scalar")` holds a Python int: `s * e1` works, while `e1 * s`
  and `blade_coefs` fail; pass `sympy.S.One`.
- Read coefficients with `mv.blade_coefs(basis)`.

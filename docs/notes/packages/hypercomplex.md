# hypercomplex 0.3.4

- Release: [PyPI hypercomplex 0.3.4](https://pypi.org/project/hypercomplex/0.3.4/), sdist sha256 `04241e5d01b3f10e813c70882a2caa9b7dc168f8b921d47156c3d964363f9352`; source [discretegames/hypercomplex](https://github.com/discretegames/hypercomplex); MIT.
- Module: `hypercomplex`; depends on [mathdunders](mathdunders.md).

## What it implements

`reals(base)` makes a one-dimensional number class over `base` (default
`float`); `cayley_dickson_construction(cls)` doubles a class;
`cayley_dickson_algebra(level, base)` applies the doubling `level` times.
Named classes run from `Real` to `Voudon` (D = 256). Instances support
`+ - * /`, `**` with integer exponents, `conjugate()`, `inverse()`, `norm()`,
`norm_squared()`, `coefficients()`, `e(i)` and `e_matrix()`.

## Relation to cd_core

Identical basis table: every `e(i) * e(j)` equals `cd_core.cd_sign(D, i, j) e_{i xor j}`
for D = 8 and 16 exhaustively and for 400 sampled pairs at D = 32 and 64
([tables.json](../../evidence/algebra_packages/tables.json)). The manual's
octonion `e_matrix` (row e1: `-e0 e3 -e2 e5 -e4 -e7 e6`) is the same table.

## Correct use

- Exact rational arithmetic: `cayley_dickson_algebra(n, fractions.Fraction)`
  keeps coefficients as `Fraction` through products and inverses. Use it to
  certify a specific product, conjugate or inverse exactly, for example a
  zero-divisor witness `x y = 0`.
- Independent cross-check of `cd_core.cd_multiply` on general (non-basis)
  elements at small D.
- Not for large D: products recurse through every level and cost grows
  quickly; use [hypercomplex-engine](hypercomplex-engine.md) for basis signs
  at D up to 4096 and beyond.

## Pitfalls

- `inverse()` returns `conj(x) / |x|^2` for any nonzero x, including zero
  divisors; it satisfies `x x^-1 = 1` while `L_x` is singular. See rule 4 in
  the [index](README.md).
- Default `float` base introduces rounding; equality tests on float results
  need tolerances or the `Fraction` base.
- Printing uses the `g` format, so exact `Fraction` values display rounded.

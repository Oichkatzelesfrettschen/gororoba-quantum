# hypercomplex-algebra 0.2.0.2

- Release: [PyPI hypercomplex-algebra 0.2.0.2](https://pypi.org/project/hypercomplex-algebra/0.2.0.2/), sdist sha256 `aa043b53a00409c4c1a6c83ecdfae188a20358aaddae587d489de46bff22f52a`; source [maher1719/hypercomplex-algebra](https://github.com/maher1719/hypercomplex-algebra); Apache-2.0.
- Module: `hypercomplex_algebra`; depends on [hypercomplex-engine](hypercomplex-engine.md).

## What it implements

A string-expression layer over the engine: `multiply_expressions("3e1 + 2e2",
"e1 - e2")`, `multiply_many_expressions` (left fold), split, dual, dual-split
and tensor-product variants (`e[1,3,2]` slot notation), plus conjugate, norm
and inverse on an `ExpressionMultiplier`. Its resolvers wrap the engine's
`FastStandard` and `FastSplit`.

## Relation to cd_core

Identical to the engine by construction; `multiply_expressions("e5", "e6")`
returns `-e3`, matching `cd_core.cd_sign(8, 5, 6) = -1`.

## Correct use

- A parsing and formatting convenience for hand checks and notebooks.
- Not a second witness: agreement between this package and the engine tests
  the wrapper, not the multiplication law.

## Pitfalls

- `multiply_many_expressions` folds from the left; in a non-associative
  algebra the bracketing is part of the answer, so state it.
- Tensor products multiply slot by slot with signs multiplied; they are a
  different algebra from any Cayley-Dickson level.

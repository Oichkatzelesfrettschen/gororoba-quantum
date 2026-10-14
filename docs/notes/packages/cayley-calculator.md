# Cayley-Calculator 1.3.1

- Release: [PyPI Cayley-Calculator 1.3.1](https://pypi.org/project/Cayley-Calculator/1.3.1/), sdist sha256 `65922fc90cc0d8159830e5d90424cb7cda6c6306824bea628542c647f364d55b`; source [Kadelka/Cayley_Calculator](https://github.com/Kadelka/Cayley_Calculator); MIT per its build recipe.
- Modules: `Cayley_Calculator` plus top-level `compl`, `quat`, `octonion`, `sedenion`, `pathion`, `chingon`, `routon` placed on `sys.path` by `.pth` files.

## What it implements

Number classes from complex to routons (D = 128) with elementary functions
(`exp`, `log`, trigonometric and hyperbolic), linear-algebra helpers and
equation solving. The manual's doubling is
`(x1, y1)(x2, y2) = (x1 x2 + gamma s(y2) y1, y1 s(x2) + y2 x1)` with conjugation
`s`; `gamma = -1` gives the ordinary algebra and `gamma = +1` the split one.

## Relation to cd_core

With `gamma = -1` the formula is the repository's doubling with the two terms
of each component reordered. The sedenion basis table is identical to
`cd_core` at D = 16.

## Correct use

- Independent evaluation of elementary functions of hypercomplex numbers;
  the repository has no equivalent.
- Split forms through `gamma = +1` are separate algebras.

## Pitfalls

- **Module-name collision.** The manual's `import Cayley_Calculator` then
  `from octonion import *` loads the [octonion](octonion.md) PyTorch package
  when both are installed, because that package's `octonion/` resolves before
  the `octonion.py` this package adds to `sys.path`. Its `sedenion`,
  `pathion`, `chingon` and `routon` modules do not collide. Import the
  sedenion module (octonions embed as a subalgebra) or adjust `sys.path`
  explicitly.
- The `.pth` files modify `sys.path` for every Python process in the
  environment.

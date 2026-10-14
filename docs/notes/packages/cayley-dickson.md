# cayley-dickson (thoppe), commit abf96e707e2a

- Release: [GitHub archive at abf96e707e2af10c0f66480ebb00205d3d159e54](https://github.com/thoppe/Cayley-Dickson/archive/abf96e707e2af10c0f66480ebb00205d3d159e54.tar.gz), sha256 `446b43f2c955c563f79660045a728b1c96d7c3ee4f7fbc0ae1ae109e90465164`; the repository carries no license, so all rights are reserved.
- Module: `cayley_dickson`; depends on numpy and pandas. The installed distribution reports version 0.1.0 regardless of commit; the commit identifies it.

## What it implements

`KD(a, b)` is an ordered pair with `conjugate() = KD(conj(a), -b)` and
`KD(a, b) * KD(c, d) = KD(a c - conj(d) b, d a + b conj(c))`;
`expand_basis` doubles a basis; `KD_construction` builds a pandas
multiplication table.

## Relation to cd_core

The product formula is the repository's doubling verbatim, and the basis
tables are identical at D = 8 and 16.

## Correct use

- Local reading and cross-checking only. No code from this package enters the
  repository, and repository code does not import it in CI.

## Pitfalls

- The Arch package python-cayley-dickson also installs the archive's `src/`
  directory as a top-level `src` package in site-packages, so `import src`
  in any process that lacks its own `src` on `sys.path` resolves to it.

- `KD_construction` assigns `K[a][b] = a * b`, which pandas stores at column
  `a`, row `b`: reading the frame row-first gives the transpose of the
  multiplication table.
- `__mul__` is memoized on the operand pair, keyed by value through
  `__hash__` of `(a, b)`; large tables keep every intermediate product alive.

# SplitOct, commit e29e72f805c2

- Release: [GitHub archive at e29e72f805c2b2e15d904e2dc4d0955e02418390](https://github.com/EQUINOX24/SplitOct/archive/e29e72f805c2b2e15d904e2dc4d0955e02418390.tar.gz), sha256 `a192a1d5d9734b31670092be16c19a40b12a79db51ea2cfdfcb1e8a90a6505d6`; GPL-3.0-or-later. Distribution name `splitoct` 0.16.
- Module: `SplitOct`; depends on SymPy.

## What it implements

`SplitOctonion([x0, ..., x7])` with symbolic or numeric coefficients, named
units `j1, j2, j3, oI, J1, J2, J3`, conjugation variants, `inv`,
`quadrance`, `dot` and SymPy simplification.

## Relation to cd_core

Split octonions are a different real algebra from the octonions. Its basis
table is XOR-indexed, has every one of the 512 basis associator signs equal
to the ordinary octonions, and squares `j1, j2, j3` to -1 and the other four
units to +1. It equals the split table of
[hypercomplex-engine](hypercomplex-engine.md) exactly.

## Correct use

- The negative control for any test that relies on associator signs alone:
  identical associators, different quadratic form (signature (4, 4)), and
  nonzero isotropic elements.
- Symbolic identities over split octonions through SymPy.

## Pitfalls

- `inv` exists only where the quadrance is nonzero; isotropic elements have
  none.
- GPL terms attach to code that incorporates it; repository code does not
  import it in CI.

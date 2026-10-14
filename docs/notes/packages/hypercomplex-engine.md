# hypercomplex-engine 0.5.0

- Release: [PyPI hypercomplex-engine 0.5.0](https://pypi.org/project/hypercomplex-engine/0.5.0/), sdist sha256 `05634d7421e1b6bc427bbc9cb8b0b91599c46cf1b1321e1d0f3e2f259dc08cb7`; source [maher1719/hypercomplex-engine](https://github.com/maher1719/hypercomplex-engine); Apache-2.0.
- Module: `hypercomplex_engine`; depends on numpy.

## What it implements

Basis-element arithmetic for four kinds: `standard` Cayley-Dickson, `split`
(standard parent with one split doubling at the top), `dual` (adjoined
nilpotent epsilon) and `dual_split`. Facade: `build_table(kind, n)` returns
sign and index tables; `multiply(kind, (sign, i), (sign, j), dim=None,
engine="fast"|"holographic")` returns `(sign, index)`; `format_element`,
`print_table` and `export_csv` format results. The `fast` engine evaluates
signs in closed form (the author's "OPMT" sign law); `holographic` descends
the doubling recursively.

## Relation to cd_core

- `standard`: identical basis table at D = 8 and 16 exhaustively, and 6,000
  sampled products (3,000 pairs, both engines) at every D from 32 to 4096
  with zero mismatches.
- `split` at n = 3: XOR-indexed, every associator sign equal to the ordinary
  octonions, and imaginary squares `-1,-1,-1,+1,+1,+1,+1`; identical to
  [splitoct](splitoct.md).

## Correct use

- Fast, independent oracle for basis signs at large dimension; the census
  and proof work can cross-check `cd_core.cd_sign` against it.
- Split and dual algebras are separate algebras with their own quadratic
  forms; compare them with `cd_core` only through the split negative control
  (same associators, different squares), never as the ordinary algebra.

## Pitfalls

- `multiply` takes and returns `(sign, index)` basis tuples, not general
  elements; linear extension is the caller's job.
- `dim` is required for `split`, `dual` and `dual_split` and changes which
  doubling is split.
- The engine's own claims of formal verification refer to its author's
  preprints; within this repository its standing is differential agreement.

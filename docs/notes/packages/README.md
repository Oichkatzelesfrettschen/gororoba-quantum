# External hypercomplex packages: conventions, independence and correct use

The repository's algebra lives in `gororoba_quantum/cd_core.py`: the doubling
`(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`, basis products
`e_p e_q = s(p, q) e_{p xor q}`, and the associator sign
`omega(p, q, r) = s(p, q) s(p xor q, r) s(q, r) s(p, q xor r)`. Every census,
proof and circuit in this repository derives from that one specification.
Eight external Python packages implement related algebra; this directory
holds one note per package and states how each one relates to `cd_core`.

## Measured relation to cd_core

[scripts/algebra_package_tables.py](../../../scripts/algebra_package_tables.py)
reads each package's basis table (`--extract ARCHIVES`, local) and the CI
gate verifies the declared relation against `cd_core` without importing any
package (`--check`). Extraction first binds each installed distribution to
its pinned release: exactly one file in ARCHIVES carries the pinned sha256,
PyPI releases report the pinned version, and every installed `.py` file is
byte-identical to a member of that archive. The single exception is a
declared packaging shim, the one-line re-export `cayley_dickson/__init__.py`
that the local build adds to the cayley-dickson commit archive, recorded
with its digest. The retained tables, the binding counts and the seeded
product samples are
[tables.json](../../evidence/algebra_packages/tables.json).

| Package | Relation to cd_core | Range checked | Independence |
|---|---|---|---|
| [hypercomplex](hypercomplex.md) | identical table | D = 8, 16 exhaustive; 32, 64 with 400 seeded pairs each | independent recursive implementation |
| [hypercomplex-engine](hypercomplex-engine.md) | identical table (standard); split variant | D = 8, 16 exhaustive; 32 to 4096, 6000 sampled products each, both engines | independent closed-form sign evaluator |
| [hypercomplex-algebra](hypercomplex-algebra.md) | identical (delegates to the engine) | 200 seeded expression products below 64, retained and checked | **not independent**: wraps hypercomplex-engine |
| [Cayley-Calculator](cayley-calculator.md) | identical table | D = 16 exhaustive | independent; Bourbaki-form doubling with gamma = -1 |
| [cayley-dickson](cayley-dickson.md) | identical table | D = 8, 16 exhaustive | independent; same doubling formula |
| [octonion](octonion.md) | signed relabeling (Fano labeling) | D = 8 exhaustive | independent; octonions only |
| [splitoct](splitoct.md) | split octonions: same associators, different squares | D = 8 exhaustive | independent; equals the engine's split table |
| [mathdunders](mathdunders.md) | none | not applicable | operator-method plumbing, not an algebra |

## Rules

1. **One specification.** `cd_core` is the reference. A package result enters
   repository evidence only through a declared map onto `cd_core`: identity,
   or a signed relabeling `T(e_p) = (-1)^eta(p) e_pi(p)` with
   `T(xy) = T(x) T(y)` checked on every basis pair.
2. **Agreement is evidence only between independent implementations.**
   hypercomplex, hypercomplex-engine, Cayley-Calculator, cayley-dickson and
   octonion are separately written; hypercomplex-algebra repeats its engine,
   and mathdunders computes no products. Majority agreement is never the
   criterion; the declared map and `cd_core` are.
3. **Associator signs do not identify the algebra.** The split tables of
   splitoct and hypercomplex-engine carry exactly the associator signs of the
   ordinary octonions (512 of 512 triples) while three of seven imaginary
   units square to -1 instead of seven. A qualification checks basis squares,
   the quadratic-form signature (the basis squares), not only associators.
4. **An element inverse is not an invertible operator.** For
   `x = e1 + e10` in the sedenions, hypercomplex returns
   `x^-1 = -(e1 + e10)/2` with `x x^-1 = x^-1 x = 1`, while `L_x` has rank
   12 of 16, `x (e4 - e15) = 0`, and `x^-1 (x y) = 0` differs from
   `(x^-1 x) y = y`. Kernel and rank statements come from `L_x`
   (`cd_core.left_mult_matrix`), never from a package `inverse()`.
5. **Exact arithmetic.** hypercomplex built with `base=fractions.Fraction`
   keeps rational coefficients exactly (its printing uses float formatting);
   it suits exact certificates of products and inverses. The engine returns
   signs and indices only and suits large-dimension sign evaluation.
6. **Licenses.** cayley-dickson declares all rights reserved, octonion is
   AGPL-3.0-or-later and splitoct is GPL-3.0-or-later. Repository code does
   not import them in CI and vendors none of their code; the retained tables
   are mathematical facts read from the installed packages.
7. **Provenance.** Each note binds its package to the public release by the
   sha256 of the PyPI sdist or GitHub archive, which equals the digest the
   local build verified.

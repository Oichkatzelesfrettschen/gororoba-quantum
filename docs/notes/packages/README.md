# External hypercomplex packages: conventions, independence and correct use

The repository's algebra lives in `gororoba_quantum/cd_core.py`: the doubling
`(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`, basis products
`e_p e_q = s(p, q) e_{p xor q}`, and the associator sign
`omega(p, q, r) = s(p, q) s(p xor q, r) s(q, r) s(p, q xor r)`. Every census,
proof and circuit in this repository derives from that one specification.
Eighteen external Python packages implement related algebra, and
python-flint and pyadic serve as exact-arithmetic backends with no
Cayley-Dickson table; this directory holds one note per package and states
how each one relates to `cd_core`. The [manual](manual/README.md) documents
every package's API with run examples, and [interplay.md](interplay.md) maps
where they overlap and where they stay isolated.

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
| [SageMath](sagemath.md) | opposite algebra in natural order; sign flip on e3, e5, e6 is an isomorphism | D = 8 exhaustive, from a retained export | independent; Sage library construction, exact |
| [splitoct](splitoct.md) | split octonions: same associators, different squares | D = 8 exhaustive | independent; equals the engine's split table |
| [mathdunders](mathdunders.md) | none | not applicable | operator-method plumbing, not an algebra |
| [numpy-quaternion](numpy-quaternion.md) | identical table | D = 4 exhaustive | independent compiled dtype; Octonion-Sedenion builds on it (Cayley-Calculator multiplies without it) |
| [quaternionic](quaternionic.md) | identical table | D = 4 exhaustive | independent numba arrays |
| [pyquaternion](pyquaternion.md) | identical table | D = 4 exhaustive | independent scalar class; pyoctonion builds on it |
| [clifford](clifford.md) | Cl(0,2) identical to the D = 4 table | D = 4 exhaustive | independent geometric algebra; associative, so quaternions and complexes only |
| [kingdon](kingdon.md) | Cl(0,2) identical to the D = 4 table | D = 4 exhaustive | independent code-generated geometric algebra |
| [galgebra](galgebra.md) | Cl(0,2) identical to the D = 4 table | D = 4 exhaustive | independent symbolic geometric algebra |
| [pyoctonion](pyoctonion.md) | identical table | D = 8 exhaustive | doubling over pyquaternion |
| [Octonion-Sedenion](octonion-sedenion.md) | identical table | D = 8, 16 exhaustive | doubling over numpy-quaternion; sedenions read with its own octonion module bound |

Each package is installed as the Arch package named in the docs/notes/algebra_circuit_rules.md
algebra section and rebuilt from its local PKGBUILD when broken; a rebuild
re-runs `--extract` so the pinned digest binds the reinstalled files.

A Kaggle kernel builds every package above except SageMath from the same
pinned archives and regenerates `tables.json` byte for byte before its entry
runs (`docs/notes/kaggle/hypercomplex-stack.md`).

## Manual and interplay

[manual/](manual/README.md) holds one manpage per package with its API by capability and
examples replayed on the build host; [interplay.md](interplay.md) maps which package reaches
which algebra through which map onto `cd_core`, with the checks that verify each claim.

## Rules

1. **One specification.** `cd_core` is the reference. A package result enters
   repository evidence only through a declared map onto `cd_core`: identity,
   or a signed relabeling `T(e_p) = (-1)^eta(p) e_pi(p)` with
   `T(xy) = T(x) T(y)` checked on every basis pair.
2. **Agreement is evidence only between independent implementations.**
   hypercomplex, hypercomplex-engine, Cayley-Calculator, cayley-dickson,
   octonion, pyoctonion and Octonion-Sedenion are separately written octonion
   or sedenion implementations; hypercomplex-algebra repeats its engine, and
   mathdunders computes no products. pyoctonion and Octonion-Sedenion double
   over other packages' quaternions, so a quaternion defect would reach both. Majority agreement is never the
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
   AGPL-3.0-or-later, splitoct is GPL-3.0-or-later, and pyoctonion and
   Octonion-Sedenion carry no license. Repository code does
   not import them in CI and vendors none of their code; the retained tables
   are mathematical facts read from the installed packages.
7. **Provenance.** Each note binds its package to the public release by the
   sha256 of the PyPI sdist, wheel or GitHub archive, which equals the digest
   the local build verified.
8. **Clifford algebras are associative.** clifford, kingdon and galgebra
   reach `cd_core` only through `Cl(0,1)` (the complex numbers) and `Cl(0,2)`
   (the quaternions). They model rotors, spinors and associative baselines;
   an octonion or sedenion statement never rests on them.

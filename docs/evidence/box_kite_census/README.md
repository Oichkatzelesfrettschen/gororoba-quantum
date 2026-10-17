# Box-kite census

`census.json` is the exact census of the seven sedenion box-kites that the
experiment program in [docs/notes/box_kites/experiment-program.md](../../notes/box_kites/experiment-program.md)
cites. `scripts/box_kite_census.py` derives every entry from
`gororoba_quantum/cd_core.py`, then recomputes the basis-product, sign and
zero-product facts through each Cayley-Dickson package (below): products are integer sums of
`cd_sign(16, p, q)` terms, the Design B products are checked term for term
against `cd_core.cd_multiply`, and the two-blade zero products are required to
equal `cd_core.sedenion_zero_divisor_corpus()` row for row. Values are
integers and exact fractions written as strings; the record carries no
floats, paths, timestamps or worker counts, so the pooled and serial
(`GOROROBA_WORKERS=1`) runs write the same bytes.

## Replay

```sh
"$PYTHON" -B -W error scripts/box_kite_census.py --check docs/evidence/box_kite_census/census.json
"$PYTHON" -B -W error scripts/box_kite_census.py --self-test
```

Gates core-372 (`--check`) and core-373 (`--self-test`) run both in normal and
optimized Python. `--check` recomputes the census and requires byte equality
with the canonical JSON (sorted keys, indent 1, ASCII). `--self-test` applies
twenty mutations to the retained record (an edge sign type, a swapped strut,
a dropped assessor, a Design B probability, a post-selected coherence, a face
class, an annihilator dimension, a twist target, the uniform associator
baseline, an associator class count, the twist mismatch count, two
open_gororoba agreement counts, a non-kite plane, a package fact digest, a
package agreement flag, a split-control verdict, a pinned release, a wrapper
expression and a cd_core reference digest) and requires `--check` to reject
each.

Regeneration needs an open_gororoba checkout and the package stack on the
build host (it multiplies through every package, 6.5 minutes on 12 CPUs):

```sh
"$PYTHON" scripts/box_kite_census.py --write docs/evidence/box_kite_census/census.json \
    --open-gororoba ~/Github/open_gororoba
```

## Contents

| Field | Content |
|---|---|
| `two_blades` | 210 elements e_i + t e_j; ordered products by squared norm N: 336 at 0, 43428 at 4, 336 at 8; the 336 zero products equal the cd_core corpus and hold in both orders |
| `assessors`, `nonkite_planes` | the 42 planes carrying a zero product; the 7 planes (l, l^8) carrying none |
| `kites` | per strut constant S: X = 8^S, index set {1..15} minus {S, 8, X}, 6 assessors (L, L^X), 3 struts (lows xor to S) with their sign products, 12 edges with zero sign set, type and sign products p0 = g(L,L')g(U,U'), p1 = g(L,U')g(U,L'), 8 faces with class, and the twist image of every edge and strut |
| `edge_totals`, `theorem3_...` | 42 same-sign and 42 opposite-sign edges; over all 1176 pairs of the 49 low/high planes the number of zero sign choices is 0 (1092 pairs) or 2 (84 pairs) |
| `eta_parity` | the anti-diagonal parity psi(L,U') xor psi(U,L') is 1 exactly on same-sign edges; the diagonal parity agrees on all 84 edges, so D = 16 does not separate the two formulas |
| `frustration_minimum` | switching minimum per kite: 0 with sign -1 on same-sign edges, 4 with sign -1 on opposite-sign edges |
| `annihilators` | per diagonal: the 4 left and 4 right two-blade partners; ker L_x and ker R_x have dimension 4, spanned by the partners; every other two-blade has nullity 0 |
| `twist` | 28224 signed basis tests, 0 mismatches, 1344 zero products; P(s=0) preserved on all 1008 within-kite and non-kite rows; the twist swaps the sign type of all 84 edges and sends struts to (l, l^8) pairs |
| `design_b` | `within_kite`: 840 rows (7 kites x 30 ordered assessor pairs x 4 signs) with P(s=0), the reduced two-label encoding (labels, selector-0 coefficients c0 c1, selector-1 coefficients d0 d1), the post-selected coherences and the full-encoding settings count 2^popcount(X); `cross_kite_controls` (168), `nonkite_pairs` (168), the negative fixture (1,10)+ x (2,13)-, and the all-pairs check that every cross-kite or non-kite signed pair gives 1/2 |
| `associator` | omega classes of ordered kite index triples (identical in all 7 kites), the deterministic-class exemplars, the fixed-pair witness with uniform k (0 on 84 pairs, -1/2 on the 21 pairs (l, 8), (l, l^8), (8, h)), the fixed-i witness with uniform (j, k), and the uniform baseline 25/256 with P(c=1) = 231/512 |
| `experiment_counts` | row and setting counts the experiment program budgets against |
| `open_gororoba_comparison` | sha256 of the four de_marrais CSVs and the agreement counts under the identity map |

## Package witnesses

`package_witnesses` recomputes the box-kite facts through every package of
the repository's Cayley-Dickson stack (root AGENTS.md, "Cayley-Dickson,
quaternion and Clifford packages"; `docs/notes/packages/`) under the map the
AGENTS.md table declares, with `scripts/box_kite_packages.py`. A fact is the
sha256 of its canonical JSON, and a witness agrees when its digest equals
cd_core's; packages are never polled against each other.

| Witness | Map onto cd_core | Arithmetic |
|---|---|---|
| hypercomplex (D = 16, 8) | identity | exact Fraction, `cayley_dickson_algebra(n, fractions.Fraction)` |
| hyprat (D = 16, 8) | identity, mu = -1 | exact rationals |
| hypercomplex-engine (D = 16, 8) | identity | basis sign oracle `multiply("standard", ...)`, bilinear |
| cayley-dickson (D = 16, 8) | identity | integer KD doubling objects |
| Cayley-Calculator (D = 16) | identity | float64, every coefficient required integral |
| Octonion-Sedenion (D = 16, 8) | identity | its own octonion module bound for the sedenion import |
| pyoctonion (D = 8) | identity | `*` (not `cal_multiply`, which prints) |
| octonion (D = 8) | signed relabeling pi = (0, 1, 2, 4, 3, 6, 7, 5), flip on its e6 | torch float64 `octonion_mul` |
| sagemath (D = 8), two entries | opposite algebra in natural order; e3/e5/e6 sign flip | `OctonionAlgebra(QQ)` |
| splitoct, hyprat signs (-1, -1, +1), engine split table (D = 8) | split relation | negative control |
| hypercomplex-algebra | wrapper of the engine | three fixture expressions, not a witness |

numpy-quaternion, quaternionic, pyquaternion, clifford, kingdon, galgebra and
mathdunders are not witnesses: they carry no D = 8 or D = 16 product, and
root AGENTS.md rests no octonion or sedenion statement on a Clifford algebra.

D = 16 facts: `two_blade_norms` (210 x 210), `kite_structure` (assessors,
struts and edge zero sign sets derived from the norms), `design_b_products`
(every census Design B row), `annihilator_nullities` (left and right, every
two-blade), `twist_counts` and `associator_classes`. D = 8 facts:
`two_blade_zero_products`, `two_blade_left_nullities`, `associator_signs`
(512), `basis_signs` (64) and `strut_lines`, the 21 triples (u, v, S) of
strut lows with u ^ v = S, required to be the kite struts and associative
octonion triples. Every identity, relabeling and Sage witness must agree on
every fact. Every split control must agree on `associator_signs` and
`strut_lines` and differ on the two zero-product facts; `split_control`
lists, per control, which facts it shares and which differ.

CI imports no package. `--write` (build host, with `--open-gororoba`)
multiplies with each package's own arithmetic and retains the digests, the
installed version and the release pinned in
`docs/evidence/algebra_packages/tables.json` (or the SageMath export's
version line). `--check` and `--self-test` recompute every digest through
the package's retained basis table under the same map (tables.json, and
`sagemath_octonion_table.json` for both Sage entries) and require equality
with the retained element verdicts; the wrapper's expressions are re-parsed
against cd_core. A package that fails to import is retained with its error
and no facts, and is rebuilt from its PKGBUILD (root AGENTS.md) before the
record is regenerated.

## open_gororoba comparison

The map is the identity on (low, high) and on signs, with the CSV's
`box_kite` id replaced by its `strut_signature`, which is the census strut
constant. Under it the assessor list (42 of 42), the kite membership (42 of
42), the strut table's assessor sets (7 of 7) and every edge's
`sign_solutions` (84 of 84) agree. Reading the strut table's A..F columns as
the strut pairs (A,F), (B,E), (C,D) agrees on kite S = 7 only: the CSV writer
(`artifact_regen.rs`) sorts each kite's assessors by (low, high) before
filling the columns, so the letters there are positions, not the canonical
labeling of `strut_table.rs`. Without `--open-gororoba`, `--check` binds the
retained comparison to the census totals (42, 42, 7, 7, 84) and to the
consistency of its disagreement list; the digests are re-verified only
against a checkout.

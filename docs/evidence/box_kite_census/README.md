# Box-kite census

`census.json` is the exact census of the seven sedenion box-kites that the
experiment program in [docs/notes/box_kites/experiment-program.md](../../notes/box_kites/experiment-program.md)
cites. `scripts/box_kite_census.py` derives every entry from
`gororoba_quantum/cd_core.py`: products are integer sums of
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
fourteen mutations to the retained record (an edge sign type, a swapped strut,
a dropped assessor, a Design B probability, a post-selected coherence, a face
class, an annihilator dimension, a twist target, the uniform associator
baseline, an associator class count, the twist mismatch count, two
open_gororoba agreement counts and a non-kite plane) and requires `--check`
to reject each.

Regeneration needs an open_gororoba checkout:

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

# The half-rotation composite leaves D_(5,12)

`result.json` is the output of `scripts/rank_locus_rotation_composite.py --out`,
and `audit.json` of its `--audit-out` on the build host. All arithmetic is
exact over Q. The question is the third computation of the
[gap note](../../notes/rank_locus_two_dimension_gap.md): a certified
15-dimensional piece of D_(5,12) through a nonzd-axis witness
x0 = {e_i, 0}, i = 1, 2, 3.

## The candidate

The [second-order record](../rank_locus_second_order/README.md) certifies
two exact curves at x0: `rotation_curve` turns the upper half toward e_8,
or the lower half toward e_24, and keeps nullity 12. The candidate piece
composes both turns over the {a, 0} family. On the unit slice

    a = ((1 - beta^2 - gamma^2) e_i + 2 beta e_(i+8) + 2 gamma e_(j+8)) / n,   n = 1 + beta^2 + gamma^2,

with sigma = n s and tau = n t,

    Psi = ((1 - sigma^2)(1 + tau^2) p + 2 n sigma (1 + tau^2) e_8,
           (1 + sigma^2)(1 - tau^2) q + 2 n tau (1 + sigma^2) e_24),

for {a, 0} = (p, q). At tau = 0 or sigma = 0 at x0, Psi equals
`rotation_curve(x0, 0)` or `rotation_curve(x0, 1)` vector for vector; the
record checks both equalities.

## Result

| Point (beta, gamma, sigma, tau) | rank L | nullity |
| --- | --- | --- |
| x0 (0, 0, 0, 0) | 20 | 12 |
| differential at x0, on the cone | rank 16 | |
| upper turn (0, 0, 2, 0), lower turn (0, 0, 0, 3) | 20 | 12 |
| composite (0, 0, 2, 3) | 32 | 0 |
| family, u and v parallel: (1, 0), (-2/5, 0) | 20 | 12 |
| one turn by 5/3 from those points | 20 | 12 |
| family, generic: (1, 2), (1/3, -2/7) | 20 | 12 |
| one turn by 5/3 from those points | 28 | 4 |

The table holds at all three witnesses.

- **The composite fails.** Rank 32 at one rational point exhibits a nonzero
  21-minor of L_Psi, a polynomial in (beta, gamma, sigma, tau). The
  composite therefore leaves D_(5,12) on an open dense set of its
  parameters. The two turns are certified only from points of {a, 0}, and
  after the first turn the upper half has left C_4^perp.
- **The turns are special.** One turn keeps nullity 12 from the retained
  family points whose octonion halves u, v of a = u + v e_8 are parallel,
  the stratum of the witnesses. From the retained generic points the same
  turn drops to nullity 4, so it leaves the locus off a proper closed
  subset of the family. Turning the whole of x0 toward e_8 + e_24 or e_8 - e_24 gives
  rank 32 at u = 1/2, 1, 2, 3 (exploratory, not retained).
- **The gap is a family property.** At three generic non-zero-divisor
  points of C_4^perp (rank L_a = 16 in A_4, one on the complex line
  -3 e_1 + 4 e_9), the tangent bound of
  `rank_locus_local_dimension.tangent_bound` is 15, as at the witnesses.
- **The local dimension stays open.** The failure of one candidate map
  bounds nothing. A tangent cone or a set of failed curves gives no upper
  bound either; that needs equations that cut out D_(5,12) near x0.

## Symmetry

`audit.json` records the SageMath 10.10 computation behind any reduction of
the parameter count.

- der(O) from `OctonionAlgebra(QQ)` has dimension 14 and equals the
  cd_core derivations of `rank_locus_gap_directions.derivations()` under
  the sign flip on e3, e5, e6.
- The related triples (D1, D2, D3) with D1(x y) = D2(x) y + x D3(y) form an
  18-dimensional algebra on A_5 (structure constants from
  python-hypercomplex). The flow of D2 preserves nullity. The D2 parts span
  17 dimensions: der(O) on each half, the identity and two maps that move
  e_8 into the lower half and e_24 into the upper half.
- On the family cone the orbit has dimension 8 at e_1 and 13 at generic
  slice points, inside the 14-dimensional family cone. The record retains
  the cross-half e_8 and e_24 entries of the two extra generators.

## Package audit

hyprat 0.2.0 and python-hypercomplex 0.3.4 rebuild L at every retained
point column by column, and each table's sha256 equals cd_core's. Both
annihilate the 12-dimensional rational kernel at every x0
([package notes](../../notes/packages/README.md)).

## Replay

```sh
"$PYTHON" -B -W error scripts/rank_locus_rotation_composite.py --check docs/evidence/rank_locus_rotation_composite/result.json
"$PYTHON" -B -W error scripts/rank_locus_rotation_composite.py --self-test
"$PYTHON" -B -W error scripts/rank_locus_rotation_composite.py --audit-check docs/evidence/rank_locus_rotation_composite/audit.json
```

Gates core-585 (check and self-test, normal and `-O`) and core-586 (audit
check, normal and `-O`) run them. `--audit-out` imports hyprat,
python-hypercomplex and SageMath and runs on the build host only, about
100 s.

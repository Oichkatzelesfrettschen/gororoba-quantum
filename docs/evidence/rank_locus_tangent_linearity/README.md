# Does the tangent bound of a rank-locus witness lie in the closed rank cone?

`result.json` is written by `scripts/rank_locus_tangent_linearity.py --out`
and recomputed by `--check` (gate core-663, about 2 seconds), which compares
the complete record. At each of the 29 witnesses of
[rank_locus_local_dimension](../rank_locus_local_dimension/README.md) the
script computes the left and right null spaces U, V of L_x and a basis of the
tangent bound T(x) = {y : U^T L_y V = 0} over the rationals with FLINT
(`rank_locus_gap_directions.verified_kernel`, which checks each basis
vector against its integer equations), then the exact rank of L_y at six seeded
integer combinations y of that basis, weights in [-50, 50]; the record
carries every weight vector beside its rank.

D_(5,k) is the unit stratum of nullity k, and its cone lies in the closed
determinantal cone R_k = {y : rank L_y <= 32 - k}, whose Zariski tangent space
at x is T(x). A piece of D_(5,k) through x of dimension dim T(x) - 1 spans a
cone of dimension dim T(x) inside R_k with tangent space in T(x); a linear such
cone equals T(x), so T(x) would lie inside R_k and the piece would decide
`a5-nonzero-divisor-two-dimension-gap` there. One sample with rank above
32 - k is an exact certificate that T(x) is not inside R_k
(`sample_refutes_tangent_inside_cone`); samples that keep rank 32 - k would
refute nothing.

| Witnesses | Nullity k | dim T(x) | Sample ranks |
| --- | --- | --- | --- |
| zd-axis (3) | 16 | 12 | 20 at every sample |
| nonzd-axis (3), Proposition 8.2 (7) | 12 | 16 | 32 |
| zd-zd-locus (3) | 12 | 18 | 32 |
| zd-zd-generic (3) | 8 | 24 | 32 |
| zd-nonzd-locus (3) | 8 | 22 | 32 |
| zd-nonzd-generic, nonzd-nonzd-locus (6), Moreno unequal norm (1) | 4 | 28 | 32 |

Reading: T(x) is not inside R_k at any witness, so the cone over a piece of
the tangent-bound dimension through a witness, if one exists, is curved. The
zero-divisor-axis witnesses are the control: there the tangent bound equals
the family dimension and the family is the curved cone of sedenion zero
divisors, yet T(x) fails the test too, so the result excludes only a linear
piece and leaves the local dimension where the earlier certificates put it.

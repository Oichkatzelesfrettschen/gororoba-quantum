# Is the tangent bound of a rank-locus witness a linear piece of D_(5,k)?

`result.json` is written by `scripts/rank_locus_tangent_linearity.py --out`
and recomputed by `--check` (gate core-663, about 2 seconds), which compares
the complete record. At each of the 29 witnesses of
[rank_locus_local_dimension](../rank_locus_local_dimension/README.md) the
script computes the left and right null spaces U, V of L_x and a basis of the
tangent bound T(x) = {y : U^T L_y V = 0} over the rationals with FLINT
(`exact_rank.rational_kernel`), then the exact rank of L_y at six seeded
integer combinations y of that basis, weights in [-50, 50].

If T(x) lay inside D_(5,k) = {y : rank L_y <= 32 - k}, it would be a linear
piece of the tangent-bound dimension through x and would decide
`a5-nonzero-divisor-two-dimension-gap` there. One sample with rank above
32 - k is an exact certificate that it does not.

| Witnesses | Nullity k | dim T(x) | Sample ranks |
| --- | --- | --- | --- |
| zd-axis (3) | 16 | 12 | 20 at every sample |
| nonzd-axis (3), Proposition 8.2 (7) | 12 | 16 | 32 |
| zd-zd-locus (3) | 12 | 18 | 32 |
| zd-zd-generic (3) | 8 | 24 | 32 |
| zd-nonzd-locus (3) | 8 | 22 | 32 |
| zd-nonzd-generic, nonzd-nonzd-locus (6), Moreno unequal norm (1) | 4 | 28 | 32 |

Reading: T(x) is not inside D_(5,k) at any witness, so a piece of the
tangent-bound dimension through a witness, if one exists, is curved. The
zero-divisor-axis witnesses are the control: there the tangent bound equals
the family dimension and the family is the curved cone of sedenion zero
divisors, yet T(x) fails the test too, so the result excludes only a linear
piece and leaves the local dimension where the earlier certificates put it.

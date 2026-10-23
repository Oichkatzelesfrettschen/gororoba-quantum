# Local dimension of D_(5,12) at the {a, 0} witnesses: extended-precision probe

`result.json` is written by `scripts/rank_locus_nullity12_refinement.py --out`
and recomputed by `--check` (full-tier gate core-662, about 2 minutes on 12
workers), which compares the complete record, its precision settings and
versions included; distances and spectra are recorded at three significant
digits.
The three nonzd-axis witnesses x0 = {e_p, 0} of
[rank_locus_local_dimension](../rank_locus_local_dimension/README.md) carry
the {a, 0} family of unit dimension 13 and the tangent bound 15; the second-
and third-order tests are vacuous there
([rank_locus_second_order](../rank_locus_second_order/README.md)), so a
direction tangent to T(x0) but not to D_(5,12) keeps sigma_21 of order 4 or
higher and no float64 tolerance separates the two cases.

Each witness gets four seeded starts x0 + eps d (eps 0.03 and 0.003, a random
direction and one weighted toward e_8 and e_24). Alternating projection onto
the rank-20 cone lands each start in float64, and a 110-digit refinement
(`mpmath.eigsy` on L^T L) drives sigma_21 / sigma_1 below 1e-40.

| Quantity | Range over the 12 points |
| --- | --- |
| relative distance from the family cone, float64 and refined | 4.28e-4 to 2.47e-2, equal at three digits before and after refinement |
| distance from the witness | 1.51e-3 to 2.68e-2 |

A cloud of 64 perturbations at scale 1e-2 around each witness, projected back
in float64, has 16 singular values of order 0.4 and the rest at 1.1e-3 to
1.5e-3: the displacements span the 16 directions of T(x0). The span bounds
the local dimension of the cone at x0 from above only, since several
lower-dimensional branches through x0 can together span 16 directions; it
excludes the family alone, whose cone spans 14.

Reading: nullity-12 points off the family persist at 110 digits and
accumulate at every witness, so the {a, 0} family is not the whole of
D_(5,12) near x0. The falsifier was a refined distance below half its
float64 value or a cloud span below 16; neither occurred. The record is
numerical and certifies nothing. It leaves the unit-norm local dimension
between 13, the family's, and 15, the tangent bound: points off the family
exclude nothing below the bound, because they may lie on further branches
through x0 of any dimension up to it, and the claim
`a5-nonzero-divisor-two-dimension-gap` stays open until an exact
parameterized piece or equations cutting out D_(5,12) near a witness decide
it.

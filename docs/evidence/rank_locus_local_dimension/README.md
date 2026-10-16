# Local dimension of the A_5 rank loci at named witnesses

`result.json` is the output of `scripts/rank_locus_local_dimension.py --out`.
It covers 21 bracket witnesses in H_5^perp and 8 witnesses outside H_5^perp,
all in exact rational arithmetic. For each witness it certifies the nullity
of L_x, and it gives an upper bound on the local dimension of D_(5,k) at x
that holds for every real point near x.

## The bound

D_(5,k) is the unit section of the cone S_k = {x : rank L_x = 32 - k}, the
preimage of the rank-(32 - k) matrix manifold under x -> L_x.
- **Tangent containment.** Let V span ker L_x and U span ker L_x^T. Then
  every curve of S_k through x has its velocity in
  T(x) = {y : U^T L_y V = 0}.
- **Dimension bound.** A semialgebraic set has the local dimension of its
  tangent cone. Here that cone lies in T(x), which contains x, so the unit
  locus has local dimension at most dim T(x) - 1.
- **Exactness.** The rank of y -> U^T L_y V is computed modulo 2^61 - 1. That
  rank is at most the rational rank, so 31 - rank_p is a valid upper bound.

## The families

Each witness sits on a smooth family whose nullity Theorem 1.5 of
math/0702075 fixes ([source note](../../notes/math-0702075.md)). The family
dimensions use one more published fact: the unit zero divisors of A_4 form
V_2(R^7), of dimension 11 (Theorem 15.7 at n = 4). Where a family's
dimension meets the bound, D_(5,k) has exactly that local dimension at the
witness.

| Family ({a, b} in H_5^perp) | Nullity | Family dimension | Tangent bound | Local dimension |
| --- | --- | --- | --- | --- |
| a zero divisor, b = 0 | 16 | 11 | 11 | 11, certified |
| a, b zero divisors, b in V(a) | 12 | 17 | 17 | 17, certified |
| a, b zero divisors, off the D-locus | 8 | 23 | 23 | 23, certified |
| a not a zero divisor, b = 0 | 12 | 13 | 15 | 13 to 15 |
| a zero divisor, b in W(a) | 8 | 19 | 21 | 19 to 21 |
| a zero divisor, b not, off the locus | 4 | 25 | 27 | 25 to 27 |
| neither, C-orthogonal | 4 | 25 | 27 | 25 to 27 |

| Witness outside H_5^perp | Nullity | Tangent bound |
| --- | --- | --- |
| (i_4, e_p) = e_8 + e_(16+p), p = 1..7 (Proposition 8.2) | 12 | 15 |
| e_1 + e_10 + 2 e_24 (Moreno) | 4 | 27 |

W(a), the D-locus space of b when only a is a zero divisor, is 8-dimensional
at every witness: the 14 dimensions of C_4^perp minus 6 independent
constraints (C-orthogonality to a, orthogonality to Ann(a)).

Every witness's certified nullity equals its family's, and no family
dimension exceeds its tangent bound. The falsifier stated before the run
would have been either failure.

## What the gap says

- **Families of zero divisors only.** Every such family is certified. There
  T(x) has the dimension of the family's tangent space and contains it, so
  the two are equal. The tangent cone of D_(5,k) at those witnesses
  therefore lies inside H_5^perp: no curve leaves H_5^perp to first order.
  For nullity 16, Theorem 8.1 confines the whole locus to H_5^perp. At
  nullity 12 and 8 these first-order facts are local, and the source does
  not state them.
- **Families with a non-zero-divisor.** Every such family has a gap of
  exactly 2.
- **Points outside H_5^perp.** Proposition 8.2's witnesses, at nullity 12,
  reach the same bound of 15 as {a, 0}. Moreno's element, at nullity 4,
  reaches the same bound of 27 as the nullity-4 families.
- **Where the 2 points.** A unit zero-product pair has x_0 = x_16 = 0, which
  leaves two coordinates of H_5 free: e_8 and e_24.

Conjecture: near a witness with a non-zero-divisor coordinate, D_(5,k) has
local dimension two above its H_5^perp family. Its extra directions leave
H_5^perp through e_8 and e_24, and Proposition 8.2's elements lie on that
larger piece. Straight lines from {e_1, 0} along e_8 and e_24 drop to
nullity 0, so any such directions curve. The conjecture is open, and a
certified lower bound needs an explicit family of the larger dimension.

## Scope

This is a local slice of roadmap item 3 in
[RANK_STRATUM_TOPOLOGY.md](../../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#global-classification-roadmap-and-admission-gates).
- **Covered:** local dimensions at named exact points.
- **Not covered:** a covering of D_(5,4), D_(5,8) or D_(5,12), their
  connected components, smoothness away from the witnesses, and the members
  outside H_5^perp beyond the points listed.

## Replay

`"$PYTHON" scripts/rank_locus_local_dimension.py --check docs/evidence/rank_locus_local_dimension/result.json`
recomputes every witness and requires the record byte for byte. It runs in
about 4 s on 12 CPUs, and serially with `GOROROBA_WORKERS=1`. The gate is
core-328, in normal and `-O` mode.

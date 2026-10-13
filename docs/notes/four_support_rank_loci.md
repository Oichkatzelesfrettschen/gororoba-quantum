# Exact rank loci on the support {1, 10, 18, 25}

The [four-support classifier](../../gororoba_quantum/four_support_rank.py)
classifies every real coefficient tuple in
`x=a e1+b e10+c e18+d e25`, including zero coefficients and the origin.
The certificate derives eight polynomial matrix blocks from the repository's
Cayley-Dickson sign recursion. Positive minor identities establish the real
rank bounds; rational tests independently check the executable evaluator.

The result extends the repository's selected
[polynomial path](../../gororoba_quantum/rank_attachments.py) to its full
four-dimensional coefficient support. The remaining 28 coefficient
directions, complete incidence attachments, and global topology remain
separate obligations. The [Koebisu research note](koebisu_rank_stratum_research.md)
places the result within the larger dimension-32 rank question.

## Complete restricted classification

Define the squared norm, quadric, and four linear coordinates by

```text
N = a^2+b^2+c^2+d^2,
Delta = a^2+b^2-c^2-d^2,
p = a-b-c-d,  q = a-b+c+d,
r = a+b-c+d,  s = a+b+c-d.
```

The coefficient transformation `T:(a,b,c,d)->(p,q,r,s)` satisfies
`T T^T=4I`. Therefore `T` is invertible over the reals. The polynomial
identity `2 Delta=pq+rs` relates the cone and hyperplanes.
For every nonzero coefficient tuple,

```text
nullity(L_x) = 4*(number of zero entries in (p,q,r,s) + indicator(Delta=0)).
```

The origin has nullity 32. The following mutually exclusive rows cover all
real tuples. Each nonzero row has an independently certified rational
witness in the [retained replay](../evidence/four_support_rank/result.json).

| Linear-coordinate conditions | Nullity | Rank |
| --- | --- | --- |
| All four entries nonzero and `pq+rs != 0` | 0 | 32 |
| All four entries nonzero and `pq+rs = 0` | 4 | 28 |
| Exactly one zero entry | 4 | 28 |
| Exactly two zeros, the pair `{p,q}` or `{r,s}` | 8 | 24 |
| Exactly two zeros, one from each pair `{p,q}`, `{r,s}` | 12 | 20 |
| Exactly three zero entries | 16 | 16 |
| All four entries zero | 32 | 0 |

Exactly one zero leaves one nonzero product in `pq+rs`. Exactly two zeros
in the same pair leave the other product nonzero. Two zeros from different
pairs or three zeros annihilate both products. These observations exhaust
the apparent rank cases excluded by the formula.

The rank-28 locus already contains distinct cone and hyperplane portions.
A determinant-only zero test or a sparse signed census conceals their
separate kernel mechanisms.

## Polynomial proof for every real tuple

The support equals `1 XOR H`, where `H={0,11,19,24}` is an XOR subgroup.
For `j=0,...,7`, order input columns as `C_j=(j XOR h: h in H)` and
output rows as `R_j=(1 XOR c: c in C_j)`. Both collections partition the
32 coordinates. The replay checks every off-sector entry and proves that
all such entries vanish as polynomials. Independent row and column
permutations therefore decompose `L_x` into eight `4x4` blocks `B_j`.

For `j=0,1,2,3`, the replay expands and verifies

```text
det B_j = epsilon_j*N*Delta,  epsilon=(-1,-1,+1,+1),
sum_(all 16 minors M of size 3) det(M)^2 = 2*N*(N^2+Delta^2).
```

At every real point away from the origin, `N>0` and the second expression
is strictly positive. At least one size-three minor remains nonzero.
Consequently each block has rank three on `Delta=0` and rank four on its
complement. The sum-of-squares identity supplies the all-real sufficiency
argument without a rational-density or floating-point rank assumption.

For the other four blocks, put

```text
K = [[ 1, 1, 1, 1],
     [-1,-1, 1, 1],
     [-1, 1,-1, 1],
     [-1, 1, 1,-1]],
D = diag(1,-1,-1,1),  ell=(p,q,r,s).

B4*K     =  D*K*diag(ell),
B5*(D*K) =   -K*diag(ell),
B6*K     = -D*K*diag(ell),
B7*(D*K) =    K*diag(ell).
```

Both constant frames have Gram matrix `4I`, so each block has rank equal
to the number of nonzero entries of `ell`. Adding the eight block ranks
proves the formula. The polynomial argument uses ordered real-field
positivity. Complex coefficient tuples fall outside the stated domain.

## Complete kernel frames and pivot-chart comparison

Write `S=ad-bc` and `U=ac+bd`. On the nonzero cone use the local columns

```text
v0=(0,N,2S,2U),    v1=(b,-a,-d,c),
v2=(d,-c,b,-a),   v3=(-2S,-2U,0,N).
```

The replay certifies all residual identities:

```text
B0*v0 = Delta*(-b,a,d,-c),
B1*v1 = Delta*(0,1,0,0),
B2*v2 = Delta*(0,0,0,-1),
B3*v3 = Delta*(d,-c,b,-a).
```

The squared norms of `v1,v2` equal `N`. The squared norms of `v0,v3`
equal `N^2+4(a^2+b^2)(c^2+d^2)`, which equals `2N^2` on the cone.
Every retained cone vector is nonzero away from the origin. Each linear
block contributes the columns of `K` or `DK` corresponding to its zero
linear forms. Lifting local columns through `C_j` gives the complete
32-coordinate kernel frame. Distinct sectors have disjoint support;
columns within each linear block are orthogonal. Positive Gram diagonals
therefore certify independence, and the rank formula certifies completeness.

Every locus with a fixed vanishing pattern of `(p,q,r,s,Delta)` away from
the origin has the stated global polynomial frame. Dividing columns by
the positive square roots of their Gram diagonals gives a continuous
orthonormal frame on that locus. The statement concerns a vector bundle
on each constant-pattern locus; the replay does not assert a smooth or
Whitney stratification of the base.

The rational evaluator accepts exactly four integers or `Fraction` values.
It rejects approximate, complex, symbolic, Boolean, and incorrectly sized
inputs. The all-real theorem concerns polynomial identities; the evaluator
does not implement an equality oracle for arbitrary real encodings.
`support_coordinates()` embeds four coefficients into the 32-vector used
by the general [rank-chart API](../../gororoba_quantum/rank_charts.py).
The independent verifier checks the support frame against a certified
rank-sized minor and the exact multiplication matrix.

For a support frame `F` and a general pivot-chart frame `K_A`, the chart's
free coordinate rows give `T_A=F[free_rows,:]`. Then `K_A T_A=F` and
`T_A` is invertible wherever the pivot chart applies on the fixed pattern.
Transitions between two pivot charts equal `T_A T_B^(-1)` when expressed
from chart B to chart A. The replay checks an exact rational overlap and
its Gram metric through the existing `chart_transition()` implementation.
Changing rank introduces new kernel directions and requires additional
attachment analysis.

## Connection to the general spectral predicates

The sector identities give the full Gram characteristic polynomial

```text
chi_(L_x^T L_x)(z) =
  [(z-N)^2*(z^2-2Nz+Delta^2)*product_i(z-ell_i^2)]^4.
```

After removing one fourfold block equal to `N`, the degree-seven reduced
polynomial is `(z-N)*(z^2-2Nz+Delta^2)*product_i(z-ell_i^2)`.
Let `e_j` denote the elementary symmetric polynomials in the four
`ell_i^2`, with `e_0=1` and `e_j=0` outside `0<=j<=4`. Its coefficients are

```text
E_j=e_j+3N*e_(j-1)+(2N^2+Delta^2)*e_(j-2)+N*Delta^2*e_(j-3).
E_7=N*Delta^2*(pqrs)^2.
```

The replay verifies the multivariate expansion and cross-checks all eight
coefficients against the independent Newton evaluator in
[rank_polynomials.py](../../gororoba_quantum/rank_polynomials.py).
The support formula refines the general rank predicates on a bounded
family; the general evaluator retains its wider coefficient domain.

The existing path specializes `ell` and `Delta` to

```text
ell = (0, 2t(2-t), (t-1)(t-2), t^2-t+2),
Delta = (t-1)(t-2)*(t^2-t+2)/2.
```

The strict positivity `t^2-t+2=(t-1/2)^2+7/4` leaves exactly the existing
exceptional parameters `0,1,2`, with nullities `8,12,16`; other real
parameters have nullity four.

## Provenance, replay, and remaining obligations

The [replay instructions](../evidence/four_support_rank/README.md) record
source hashes, environment versions, exact output, and mutation controls.
The checks reject a changed CD sign, a duplicate sector, an omitted kernel
column, and invalid coefficient domains. A positive coefficient `10^-40`
retains its exact nonzero contribution. Normal and optimized Python
executions retain the same checks because the implementation uses explicit
exceptions instead of removable assertions.

The [annihilator ledger](cayley_dickson_annihilator_sources.md) and
[rank-topology ledger](cayley_dickson_rank_topology_sources.md) attribute
the existing Biss-Dugger-Isaksen rank bounds, Reggiani bundle theorem,
and Koebisu polynomial construction. The fixed-support certificate
combines the repository's XOR reduction with determinant and elementary
linear-algebra identities. The result is a derived repository extension;
publication priority remains unestablished.

A complete dimension-32 answer still requires the other coefficient
directions, compatible smooth strata, explicit closure/attachment maps,
and a global topological model with integral invariants. The fixed-support
frames supply data for that program. They establish neither the topology
of every dimension-32 pair nor an unrestricted all-dimensional theorem.

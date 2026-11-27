# Transitions between the annihilator dimensions of A_5: paths, limiting kernels and the compression pencil

`result.json` is the output of [`scripts/a5_nullity_transitions.py`](../../../scripts/a5_nullity_transitions.py)
`--out`. For y in the 32-dimensional Cayley-Dickson algebra A_5 the nullity of left multiplication L_y is 0, 4, 8, 12
or 16 ([rank strata](../a5-zero-divisor-strata/README.md)). The record joins the four nonzero values by explicit
polynomial paths, certifies the limiting kernels at one junction, and determines the first-order structure that
governs every nullity-4 approach to the nullity-8 point e_1 + e_10. Every decision is an exact rational rank, a
polynomial identity or an exact real-root count; no random draw enters. `--check` recomputes the record and compares
its bytes; `--self-test` runs five controls, each a property that fails on a mutated input, in normal and `-O` modes.

The paths gamma_1, gamma_2, gamma_3 and the pair of limiting planes of statement 3 come from an outside report
([review](../../archive/reviews/a5-outside-transition-report/README.md)); statements 2 (the second end of gamma_3)
and 5 to 7 are computed here first. Ledger rows A5-650 to A5-657 of
[the claim ledger](../a5-exceptional-fibers/ledger.tsv) carry the statements.

## Conventions

The product is the cd_core doubling (a,b)(c,d) = (ac - conj(d) b, da + b conj(c)), e_p e_q = cd_sign(dim, p, q)
e_(p XOR q). The record checks every basis product of dimensions 8, 16 and 32 against an independent recursive
implementation of that formula (`convention`). A path is y(s) with coefficients in Q[s]. Its Gram operator
L_y(s)^T L_y(s) is symmetric and positive semidefinite at every real s, so the nullity at s is the order of x in the
characteristic polynomial. Over Q[s] the lowest nonzero coefficient c_k(s) gives the generic nullity k, and the
parameters with a larger nullity are exactly the real roots of c_k, counted by Sturm's theorem.

## Statements

Each statement has a `require` in the script's `validate`; the name of the record entry is in parentheses.

1. **Three paths join the four strata** (`paths`). gamma_1(s) = e_1 + e_10 + s (e_9 + e_26) has nullity 4 at every
   real s other than 0 and nullity 8 at 0. gamma_2(s) = (1 - s)(e_1 + e_10) + s (e_3 + e_20) has nullity 8 at every
   real s other than 1 and nullity 12 at 1. gamma_3(s) = e_3 + e_20 + s (e_12 - e_27) has nullity 12 at every real s
   other than -1 and 1 and nullity 16 at both. Each c_k has the listed rational roots as its only real roots.
2. **Orbits of the junctions** (`orbits`). Under the classifier of
   [hardware orbits](../a5-exceptional-fibers/hardware-orbits/README.md): gamma_1(1) lies in the nullity-4 part of
   V(G) minus V(Q); e_1 + e_10 and the interior of gamma_2 lie in W8; e_3 + e_20 lies in VB; gamma_3(1) lies in N-
   and gamma_3(-1) in N+. One line through a VB point therefore meets both nullity-16 orbits, the pattern
   A5-208 records for a W8 line.
3. **Two limiting planes at e_1 + e_10** (`limits`). Along gamma_1 and along beta(s) = e_1 + e_10 + s (e_2 + e_17)
   the orthogonal projector onto ker L is constant on the punctured line (certificate of
   [kernel limits](../kernel_limits/README.md), exceptional polynomial s^3 + s). The two limiting 4-planes are
   orthogonal, and their sum is the 8-dimensional kernel of L_(e_1 + e_10).
4. **First-order compression** (`compressions`). With K a frame of the kernel at a junction and w the path
   direction, the skew form K^T L_w K has rank 4 at all four junctions (kernels 8, 12, 16, 16): four kernel
   directions leave at first order and the rest persist.
5. **The compression pencil at e_1 + e_10** (`pencil`). The forms K^T L_w K of the 31 imaginary units span a space
   of dimension 7 with basis the units 1, 2, 8, 16, 17, 18, 24 (the forms of 9, 10, 25, 26 repeat them up to sign,
   and the other twenty vanish). The operators commuting with the pencil form a 4-dimensional algebra, the Lie
   algebra the pencil generates has dimension 10, and in the coordinates (u, m, v) of R^3 + R + R^3 on those units

       Pf(K^T L_w K) = 16 ((u.u + m^2 + v.v)^2 - 4 ((u.u)(v.v) - (u.v)^2)).

   The right side is the quartic invariant G = Q^2 - 4 Delta of A5-357 written on seven real variables.
6. **The real rank-4 cone** (argument on statement 5). By Lagrange's identity (u.u)(v.v) - (u.v)^2 = |u x v|^2 and
   2 |u x v| <= 2 |u| |v| <= u.u + v.v, so the Pfaffian vanishes at a real point exactly when m = 0, u is orthogonal
   to v and |u| = |v|: the cone over the Stiefel manifold V_2(R^3). On ten rational points of that cone the
   compression rank is 4 and the line e_1 + e_10 + s w has nullity 4 at s = 1, 2, 3 (`pencil.stiefel`); the pair
   u = v has rank 8 (self-test).
7. **Limiting planes depend on u x v** (`pencil`). For the ten Stiefel pairs the limiting plane N(u, v) =
   K ker(K^T L_w K) satisfies trace(P P') = 2 (1 + cos angle(u x v, u' x v')) on all 55 pairs, and two pairs with
   parallel normals give one plane. Among the 930 signed two-term directions e_i +- e_j, 32 have rank 4 and give
   six planes: three orthogonal pairs, every other pair at trace 2. The planes of statement 3 are one orthogonal pair
   (normals +-e_3 of the u x v space).
8. **Elementary identities** (`gram_identity`, `three_form`, `section`). At levels 16, 32, 64, with J the left
   table of the doubling unit, L_a^T J + J^T L_a = 0 for every imaginary unit a of the lower half and J^T J = I, so
   L_(a,t)^T L_(a,t) = L_(a,0)^T L_(a,0) + t^2 I for imaginary a; this is A5-622 with a vanishing mixed associator.
   <e_i, e_j e_k> is alternating on the imaginary units at levels 8 to 64. On u = a e_1, v = b e_2, mu = i,
   Q = a^2 + b^2 - 1 and G = ((a + b)^2 - 1)((a - b)^2 - 1).

## Reading of statements 5 to 7 (argued; open rows A5-655 to A5-657)

A real skew form on R^8 that commutes with a quaternion algebra has rank 0, 4 or 8, which is the mechanism of the
step 4 at this junction. The dimension 10 is that of sp(2), the skew operators of H^2 commuting with H, so the
kernel reads as H^2 and a limiting plane as a quaternionic line, a point of HP^1 = S^4; the overlap law of statement
7 is the law of quaternionic lines at spherical distance angle(n, n'). hypothesis: the limiting planes of all
nullity-4 arcs into a W8 point form a round 2-sphere in that S^4, orthogonal planes being antipodal. The record
decides the law on ten rational pairs; a proof over the whole cone, arcs whose first-order form has rank 0 or 8, and
the same pencil at VB, N- and N+ are open.

## Predictions

Written before the first run (`predictions`, `prediction_held`). P1, P2 and P4 to P8 held. P3 failed in one
clause: it named s = 1 as the only exceptional parameter of gamma_3, and the count of real roots gives s = -1 as well.

## Replay

    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --check docs/evidence/a5-nullity-transitions/result.json
    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --self-test

Measured on the compute workstation: 7 s and 90 MiB for the record, 1 s for the self-test.

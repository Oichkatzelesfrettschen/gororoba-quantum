# Transitions between the annihilator dimensions of A_5: paths, limiting kernels and the compression pencil

`result.json` is the output of [`scripts/a5_nullity_transitions.py`](../../../scripts/a5_nullity_transitions.py)
`--out`. For y in the 32-dimensional Cayley-Dickson algebra A_5 the nullity of left multiplication L_y is 0, 4, 8, 12
or 16 ([rank strata](../a5-zero-divisor-strata/README.md)). The record joins the four nonzero values by explicit
polynomial paths, certifies the limiting kernels at one junction, and determines the first-order structure that
governs every nullity-4 approach to the nullity-8 point e_1 + e_10. Every decision is an exact rational rank, a
polynomial identity or an exact real-root count; no random draw enters. `--check` recomputes the record and compares
its bytes; `--self-test` runs six controls, each a property that fails on a mutated input, in normal and `-O` modes.

The paths gamma_1, gamma_2, gamma_3 and the pair of limiting planes of statement 3 come from an outside report
([review](../../archive/reviews/a5-outside-transition-report/README.md)); statements 2 (the second end of gamma_3)
and 5 to 9 are computed here first. Ledger rows A5-650 to A5-660 of
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
5. **The compression pencil at e_1 + e_10** (`pencil`, `structure`). K is the frame of the kernel with Gram
   matrix 2 I. The forms K^T L_w K of the 31 imaginary units span a space of dimension 7 with basis the units 1, 2,
   8, 16, 17, 18, 24 (the forms of 9, 10, 25, 26 repeat them up to sign, and the other twenty vanish). The commutant
   of the pencil has dimension 4, is noncommutative, and its trace form is negative definite on the traceless part:
   it is a quaternion algebra. The Lie algebra the pencil generates has dimension 10, the dimension of the skew
   operators that commute with the quaternions, so it is sp(2) acting on the kernel as H^2. In the coordinates
   (u, m, v) of R^3 + R + R^3 on those units, in the frame K,

       Pf(K^T L_w K) = 16 ((u.u + m^2 + v.v)^2 - 4 ((u.u)(v.v) - (u.v)^2)).

   The constant 16 is det K^T K to the power 1/2 and changes with the frame; the dimensions do not.
6. **The Pfaffian is the tangent cone of G** (`tangent_cone`). In the coordinates z_k = y_k + i y_(16+k) of the
   strata record the six doubly pure coordinate units are the real and imaginary parts of zeta = u + i v on
   (z_1, z_2, z_8), and on the line y_0 + s w

       G = s^2 (zeta.zeta) (4 + 4 s zeta_1 + s^2 zeta.zeta).

   G vanishes to order 2 at the base point, and at m = 0 the Pfaffian is the squared modulus of the leading
   coefficient 4 zeta.zeta. The unit e_16 lies outside the doubly pure domain of G and enters through m^2.
7. **The real rank-4 cone** (argument on statement 5; `pencil.stiefel`). By Lagrange's identity
   (u.u)(v.v) - (u.v)^2 = |u x v|^2 and 2 |u x v| <= 2 |u| |v| <= u.u + v.v <= u.u + m^2 + v.v, so the Pfaffian
   vanishes at a real point exactly when m = 0, u.v = 0 and |u| = |v|, which is zeta.zeta = 0: the isotropic vectors
   of C^3. Away from the apex the compression rank there is 4. By statement 6 the line y_0 + s w lies in V(G) for
   every such w, and its nullity is 4 near the base point: at least 4 on V(G), and at most the dimension of
   ker K^T L_w K, which contains every limit of kernel vectors. Ten rational points confirm rank 4 and nullity 4 at
   s = 1, 2, 3; the pair u = v has rank 8 (self-test).
8. **Limiting planes** (`clifford`, `pencil`). The limiting planes of the normals e_1, e_2, e_3 of the u x v space
   define E_k = 2 P(e_k) - I on the kernel: three symmetric traceless involutions that anticommute. For symbolic
   (u, v), every entry of K^T L_w K (|u|^2 I + (u x v).E) lies in the ideal (u.v, u.u - v.v), and the reversed
   normal fails on 48 entries. On the cone the limiting plane is therefore the range of (I + n.E)/2 with
   n = u x v / |u|^2: it depends on the isotropic line of zeta alone, and
   trace(P P') = 2 (1 + n.n') for every pair, since trace E_j E_k = 8 delta_jk. The 55 pairs of the ten rational
   directions agree. Among the 930 signed two-term directions e_i +- e_j, 32 have rank 4, and their six planes are
   the planes of the normals +-e_1, +-e_2, +-e_3; the planes of statement 3 are one antipodal pair.
9. **The structure depends on the point of W8** (`structure`, `structure_orbits`). Eight points classify as W8
   with orbit rank 12, and each has pencil dimension 7. Six have a quaternion commutant and Lie closure of dimension
   10: e_1 + e_10, e_1 - e_10, e_17 + e_26, e_1 + e_10 + e_4 + e_15, e_1 + e_10 + e_17 + e_26 and
   e_1 + e_10 + 2 (e_18 - e_25). Two, both on the line gamma_2, have commutant the scalars and Lie closure of
   dimension 28, all of so(8): e_1 + e_10 + e_3 + e_20 and 2 (e_1 + e_10) + e_3 + e_20. Three candidate criteria are
   refuted by these points: the number of terms (the fourth point), lying in one half (the fifth) and proportional
   halves (the sixth). At the VB point e_3 + e_20 the self-test reads kernel 12, pencil 9, commutant 1 and closure 66.
10. **Elementary identities** (`gram_identity`, `three_form`, `section`). At levels 16, 32, 64, with J the left
    table of the doubling unit, L_a^T J + J^T L_a = 0 for every imaginary unit a of the lower half and J^T J = I, so
    L_(a,t)^T L_(a,t) = L_(a,0)^T L_(a,0) + t^2 I for imaginary a; this is A5-622 with a vanishing mixed associator.
    <e_i, e_j e_k> is alternating on the imaginary units at levels 8 to 64. On u = a e_1, v = b e_2, mu = i,
    Q = a^2 + b^2 - 1 and G = ((a + b)^2 - 1)((a - b)^2 - 1).

## Reading and open questions (ledger rows A5-656, A5-657, A5-660)

At e_1 + e_10 the limiting planes of the lines of statement 7 are the points of the conic zeta.zeta = 0 in the
projective plane of C^3, a 2-sphere, embedded in the quaternionic lines HP^1 = S^4 of the kernel H^2 with the round
overlap law. The record covers lines in the six coordinate units; curved arcs, and directions with a component on
the twenty units of zero compression, are open (A5-660). The quaternion commutant is absent at two W8
points, so the hypothesis that every W8 point carries it is refuted (A5-656); which real invariant of a W8 point
decides the commutant, and which type is generic, are open (A5-660), as are the pencils at VB and N+- (A5-657).

## Predictions

Written before the runs they concern (`predictions`, `prediction_held`). P1, P2 and P4 to P8 held. P3 failed in one
clause: it named s = 1 as the only exceptional parameter of gamma_3, and the count of real roots gives s = -1 as well.
P9 failed: it predicted the quaternion commutant at the four-term W8 point e_1 + e_10 + e_3 + e_20. P10 held (an
upper-half and a four-term lower-half point are quaternionic). P11 failed: it predicted a non-quaternionic commutant
at e_1 + e_10 + 2 (e_18 - e_25), whose halves are linearly independent.

## Reviews

Two red-team reports ([review record](../../archive/reviews/a5-outside-transition-report/README.md), "Red team") supplied the
tangent-cone derivation of statement 6, the involution formula of statement 8 and the test that separates the
quaternions from the other algebras of dimension 4.

## Replay

    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --check docs/evidence/a5-nullity-transitions/result.json
    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --self-test

Measured on the compute workstation: 10 s and 90 MiB for the record, 4 s and 110 MiB for the self-test.

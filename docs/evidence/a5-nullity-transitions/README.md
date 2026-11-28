# Transitions between the annihilator dimensions of A_5: paths, limiting kernels and the compression pencil

`result.json` and `sign-census.json` are outputs of [`scripts/a5_nullity_transitions.py`](../../../scripts/a5_nullity_transitions.py)
`--out`. For y in the 32-dimensional Cayley-Dickson algebra A_5 the nullity of left multiplication L_y is 0, 4, 8, 12
or 16 ([rank strata](../a5-zero-divisor-strata/README.md)). The record joins the four nonzero values by explicit
polynomial paths, certifies the limiting kernels at one junction, and determines the first-order structure that
governs every nullity-4 approach to the nullity-8 point e_1 + e_10. Every decision is an exact rational rank, a
polynomial identity or an exact real-root count; no random draw enters. `--check` recomputes the record and compares
its bytes; `--self-test` runs ten controls, each a property that fails on a mutated input, in normal and `-O` modes.

`certificates.json` is the output of [`scripts/a5_pencil_certificates.py`](../../../scripts/a5_pencil_certificates.py)
`--out` and carries statements 16 to 18, which need computations beyond the sympy record: the tower at levels 7 and 8,
the N+- Pfaffian and the common kernels of sedenion zero divisors.

The paths gamma_1, gamma_2, gamma_3 and the pair of limiting planes of statement 3 come from an outside report
([review](../../archive/reviews/a5-outside-transition-report/README.md)); statements 2 (the second end of gamma_3)
and 5 to 9 are computed here first. Ledger rows A5-650 to A5-668, A5-670 and A5-671 of
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
9. **The structure depends on the point of W8** (`structure`, `structure_orbits`). Ten points classify as W8
   with orbit rank 12, and each has pencil dimension 7; statement 13 names the three types. Six have a quaternion
   commutant and Lie closure of dimension 10: e_1 + e_10, e_1 - e_10, e_17 + e_26, e_1 + e_10 + e_4 + e_15, e_1 + e_10 + e_17 + e_26 and
   e_1 + e_10 + 2 (e_18 - e_25). Two, both on the line gamma_2, have commutant the scalars and Lie closure of
   dimension 28, all of so(8): e_1 + e_10 + e_3 + e_20 and 2 (e_1 + e_10) + e_3 + e_20. Two, e_1 + e_10 + 2 (e_20 + e_31) and
   e_1 + e_10 + 2 (e_21 - e_30), have a commutative commutant of dimension 2 and Lie closure of dimension 15. Three
   candidate criteria for the quaternion type are
   refuted by these points: the number of terms (the fourth point), lying in one half (the fifth) and proportional
   halves (the sixth). At the VB point e_3 + e_20 the self-test reads kernel 12, pencil 9, commutant 1 and closure 66.
10. **Elementary identities** (`gram_identity`, `three_form`, `section`). At levels 16, 32, 64, with J the left
    table of the doubling unit, L_a^T J + J^T L_a = 0 for every imaginary unit a of the lower half and J^T J = I, so
    L_(a,t)^T L_(a,t) = L_(a,0)^T L_(a,0) + t^2 I for imaginary a; this is A5-622 with a vanishing mixed associator.
    <e_i, e_j e_k> is alternating on the imaginary units at levels 8 to 64. On u = a e_1, v = b e_2, mu = i,
    Q = a^2 + b^2 - 1 and G = ((a + b)^2 - 1)((a - b)^2 - 1).

11. **Order of vanishing at the junctions** (`paths`). At each exceptional parameter the lowest coefficient c_k(s)
    vanishes to order 8 with a positive cofactor (2^40 on gamma_1, 2^32 on gamma_2, 2^52 at both ends of gamma_3):
    four Gram eigenvalues vanish quadratically, so four singular values of L vanish linearly.
12. **Tower** (`tower`). At e_1 + e_10 in A_4 the kernel has dimension 4, the pencil and its Lie closure have
    dimension 3 and the commutant is a quaternion algebra. At the same element in A_6 the kernel has dimension 16
    and splits as two equal 8-dimensional parts across the halves, the pencil has dimension 15, the commutant is a
    quaternion algebra and the Lie closure has dimension 36. With statement 5 the three levels read sp(1), sp(2),
    sp(4) on H, H^2, H^4, with pencil dimensions 3, 7, 15.
13. **Three types of pencil on W8** (`structure`, `sampled_structure`, `split_scan`). Write y = (p, q) with p, q
    in A_4. For a nonzero doubly pure y the kernel meets the lower half A_4 + 0 and the upper half 0 + A_4 in the
    same subspace A = ker L_p n ker L_q of A_4 (from (p, q)(c, 0) = (pc, q conj(c)) and
    (p, q)(0, d) = (-conj(d) q, dp), a zero divisor of A_4 being pure). On every W8 point of the record the pencil
    has dimension 7 and one of three types, named by its commutant:

    | dim A | commutant | Lie closure | points |
    |---|---|---|---|
    | 0 | R | so(8), dimension 28 | 2 named, 240 of the four-term representatives, 36 of the scan |
    | 2 | C | dimension 15: su(4) | 2 named, 4 of the scan |
    | 4 | H | sp(2), dimension 10 | 6 named, 72 of the four-term representatives, 3 of the scan |

    The four-term representatives are 474 points e_1 +- e_a +- e_b +- e_c of nullity 8, one per index triple (the
    first sign pattern of nullity 8); 312 of them lie in W8. The scan takes p = e_1 + e_10 and (p, lam q) for the
    two-term zero divisors q = e_i +- e_j of A_4 and lam = 1, 2 (168 cases): its four points with dim A = 2 are
    e_1 + e_10 + 2 (e_20 + e_31) and three like it, and with lam = 1 the same lines have nullity 12. The commutant of
    type C is commutative of dimension 2 with a negative-definite traceless part, a copy of C; the skew operators
    commuting with it form u(4), and a subalgebra of u(4) of dimension 15 is su(4). The scan records dim A and the
    commutant dimension of each point; the Lie closure 15 is computed at the two named points. The counts overlap:
    the named points of types C and H with p = e_1 + e_10 lie in the scan, and the 474 representatives lie in the
    census below. A rule by the order of the XOR
    group of the support fails in both directions (e_1 + e_12 + e_13 + e_30 has order 8 and type R,
    e_1 + e_2 + e_11 + e_12 order 16 and type H).

    A separate record, `sign-census.json` (`--sign-census`), classifies all 29,232 signed points
    e_1 +- e_a +- e_b +- e_c: 2,448 lie in W8, 1,920 of type R and 528 of type H, none of another type.
14. **Pencils at VB and N+-** (`strata_pencils`, `vb_pfaffian`). At e_3 + e_20 the kernel has dimension 12, the
    pencil dimension 9, the commutant is the scalars and the Lie closure is so(12), of dimension 66. At the N- and
    N+ ends of gamma_3 the kernel has dimension 16 and meets each half in one 4-dimensional subspace, the pencil
    has dimension 19, the commutant is the scalars and the Lie closure is so(16), of dimension 120, so the types of
    statement 13 belong to W8. In a frame with Gram 2 I the Pfaffian of the VB pencil is -64 times an irreducible
    polynomial of degree 6 with 50 terms in nine coordinates, one of them on e_16. Restricted to the eight doubly
    pure coordinates it has 16 terms and equals

        -|lead Q|^2 |lead G|^2,

    the product of the squared moduli of the leading coefficients of Q (order 1) and G (order 2) on the lines
    along the eight doubly pure coordinate units: three quadratic factors over Q. The tangent-cone form of statement 6 holds at VB as well.
15. **Arcs outside the coordinate lines** (`arcs`). Twenty imaginary units have zero compression at e_1 + e_10.
    The line along each has nullity 0 at s = 3 and s = 5. Of the 380 lines along signed pairs of them, 200 read
    nullity 0, 160 nullity 8 and 20 nullity 4 at both parameters. Each of the 20 has generic nullity 4
    (certificate) and, with a zero first-order form, a limiting plane equal to the plane of the unit normal e_3
    (10 lines) or -e_3 (10 lines). Two curved arcs y_0 + s w(t_0 + s) along the conic
    zeta(t) = (1 - t^2, i (1 + t^2), 2 t), at t_0 = 1 and 2, have generic nullity 4 and limit on the plane of the
    normal of w(t_0).

16. **Tower at levels 7 and 8** (`certificates.json`: `tower`, `calibration`). At e_1 + e_10 in A_7 the kernel has
    dimension 32, meeting each half in 16, the pencil dimension 31, the commutant is a quaternion algebra and the Lie
    closure has dimension 136, that of sp(8); in A_8 the kernel has dimension 64, meeting each half in 32, the pencil
    dimension 63, the commutant is a quaternion algebra and the closure has dimension 528, that of sp(16). The
    commutant and the closure carry two-sided bounds. A rank modulo the prime 32749 never exceeds the rational rank,
    so the nullity mod p of the commutation system bounds the commutant above, and four elements reconstructed from
    p and checked to commute with every pencil element over Q bound it below. The mod-p span of brackets of three
    fixed pencil elements bounds the closure below. The Gram-skew operators that commute with the verified commutant
    contain the closure, and their dimension mod p bounds it above. The bounds meet at 3, 10, 36, 136 and 528 for
    n = 4 to 8. At the type-R point e_1 + e_10 + e_3 + e_20 they meet at commutant 1 and closure 28. At the type-C
    point e_1 + e_10 + 2 (e_20 + e_31) the closure lies between 15 and 16, so the certificate is tight for types H
    and R only.
17. **Pfaffian at N+-** (`strata`). At N- and N+ the pencil has 19 coordinate units, 18 of them doubly pure. On
    the lines along those 18 units Q has order 1 and G order 3. Restricted to them, the Pfaffian, expanded in an
    integer polynomial ring, has degree 8 and 8,395 terms. It factors over Q as a quadratic times an irreducible
    sextic, and it equals c |lead Q|^2 |lead G|^2, with |c| = 2 in a frame of Gram 2 I. The same computation
    reproduces the VB identity of statement 14 with |c| = 1. With the coordinate on e_16 kept, the VB identity
    fails, the mutant of the self-test, as P14 recorded. A second implementation shares no code with cd_core or the
    polynomial ring (`determinant`): products by the doubling formula, and Q and G as Gaussian-integer polynomials
    in s. It reads, at 60 integer points over all 30 doubly pure imaginary units at each of N- and N+, the
    coefficients of Q below order 1 and of G below order 3 as zero and det = 4 (|lead Q|^2 |lead G|^2)^2 in a
    frame of Gram 2 I. So the identity extends beyond the 18 basis units at those points. The full Pfaffian with the
    coordinate on e_16 is not computed at N+-.
18. **Common kernels of sedenion zero divisors** (`anticommutation`, `census`). In A_4, L_(e_8) anticommutes with the
    left multiplication by each of the 14 other imaginary units and squares to -I, and every imaginary unit acts
    by a skew matrix. Both sides are bilinear, so the basis check covers every element. This is the complex
    structure of Biss, Dugger and Isaksen ("Large annihilators in Cayley-Dickson algebras", arXiv math/0511691,
    Proposition 5.3 and Lemma 6.4, read for this record): A_n is a vector space over C_n = <1, i_n> by left
    multiplication, and L_x is conjugate-linear for x orthogonal to C_n. The evenness below is a corollary of
    that structure; the record adds the census. For p = p_0 + p_8 e_8 + p' the Gram operator is
    (p_0^2 + p_8^2) I + L_(p')^T L_(p'), so a zero divisor has p_0 = p_8 = 0. Then L_p anticommutes with
    L_(e_8), so ker L_p is invariant under L_(e_8), and ker L_p n ker L_q is a complex subspace of a 4-dimensional
    kernel: its dimension is 0, 2 or 4. The census takes the 26,096 elements (a, b) with a, b pure octonions with
    entries in {-1, 0, 1}, |a|^2 = |b|^2 <= 3 and a.b = 0. Each has nullity 4 and a kernel invariant under
    L_(e_8). Over 3,523,095 pairs (each i with i + 1, i + 98, ...), the common kernels have dimension 0 (3,518,410),
    2 (4,268) and 4 (417). The census classifies no W8 point, so prediction P25 is not run.

## Reading and open questions (ledger rows A5-656, A5-657, A5-660)

At e_1 + e_10 the limiting planes of the lines of statement 7 are the points of the conic zeta.zeta = 0 in the
projective plane of C^3, a 2-sphere, embedded in the quaternionic lines HP^1 = S^4 of the kernel H^2 with the round
overlap law. The record covers lines in the six coordinate units, two curved arcs along the conic and the lines along pairs
of zero-compression units (statement 15), all of which limit on the 2-sphere; a proof for every arc is open (A5-660). The quaternion commutant is absent at four of the ten named W8
points, so the hypothesis that every W8 point carries it is refuted (A5-656). The dimension of ker L_p n ker L_q decides
the type on every tested point (A5-667, survives); a proof is open, and statement 18 proves that the dimension is
even. A red-team derivation
([review](../../archive/reviews/a5-nullity-tower-split/README.md)) argues that dimension 4 forces type H and that
the tower of statement 12 continues as sp(2^(n-4)) at every level; statement 16 confirms the tower at levels 7 and
8, and both remain arguments awaiting a machine proof for every level. On the doubly pure coordinates the
Pfaffian at N+- is the product of the squared moduli of the leading forms, as at VB (A5-657, statement 17).

The nearest published result is S. Koebisu, "Principal angles between annihilators of real sedenion zero
divisors", arXiv 2611.30652 (abstract read): two sedenion annihilators with axes at angle theta have principal
cosines (p, p, q, q) with cos^2(theta/2) <= p <= cos(theta/2) and q <= p. The limiting planes of statement 8
satisfy P P' P = cos^2(theta/2) P (with a = n.E and b = n'.E, a b a = 2 (n.n') a - b, so
(1 + a)(1 + b)(1 + a) = 2 (1 + n.n')(1 + a)), so all four cosines equal cos(theta/2), the upper
end of that range; the planes here are limits of A_5 annihilators inside one 8-dimensional kernel, indexed by a
2-sphere. Three arXiv queries of 2026-11-27 on limits, tangent cones and Pfaffians of Cayley-Dickson
left multiplication returned no other work; that search bounds the novelty claim.

## Predictions

Written before the runs they concern (`predictions`, `prediction_held`). P1, P2 and P4 to P8 held. P3 failed in one
clause: it named s = 1 as the only exceptional parameter of gamma_3, and the count of real roots gives s = -1 as well.
P9 failed: it predicted the quaternion commutant at the four-term W8 point e_1 + e_10 + e_3 + e_20. P10 held (an
upper-half and a four-term lower-half point are quaternionic). P11 failed: it predicted a non-quaternionic commutant
at e_1 + e_10 + 2 (e_18 - e_25), whose halves are linearly independent. Of the second round, P12 and P13 (the tower),
P16 (curved arcs), P17 (types H and R against the kernel split) and P18 (the VB Pfaffian on the doubly pure
coordinates as the product of leading forms) held; P14 (the same for the full nine-coordinate Pfaffian), P15 (the
XOR-order rule) and P19 (no W8 point with dim A = 2) failed. The third round, in `certificates.json`, was written
to a scratch file before its runs ([third-round-predictions.md](third-round-predictions.md), kept verbatim) and
restated in the script: P20 and P21 (the tower at levels 7 and 8),
P22 (commutant 1 and closure 28 at the type-R point), P23 (the N+- Pfaffian on the doubly pure coordinates as the
product of leading forms), P24 (common kernels of dimension 0, 2 or 4 only) and P26 (the determinant route over
all 30 doubly pure units, written after the first record run and before that route was coded) held. A first calibration run used
two pencil elements as Lie generators and read the bounds 2 and 15 at the type-R point. Its bounds did not meet,
so it certified nothing, and three generators close them. P25 (the pencil type on W8 points of the census) is not
run.

## Reviews

Two red-team reports ([review record](../../archive/reviews/a5-outside-transition-report/README.md), "Red team") supplied the
tangent-cone derivation of statement 6, the involution formula of statement 8 and the test that separates the
quaternions from the other algebras of dimension 4.

## Replay

    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --check docs/evidence/a5-nullity-transitions/result.json
    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --self-test

    "$PYTHON" -B -W error scripts/a5_nullity_transitions.py --check-sign-census docs/evidence/a5-nullity-transitions/sign-census.json

    "$PYTHON" -B -W error scripts/a5_pencil_certificates.py --check docs/evidence/a5-nullity-transitions/certificates.json
    "$PYTHON" -B -W error scripts/a5_pencil_certificates.py --self-test

Measured on the compute workstation (32 threads): the record takes 102 s of wall time and 992 CPU seconds at
260 MiB, the self-test 12 s, the sign census 326 s of wall time and 3,470 CPU seconds. The certificates take 347 s of wall
time and 980 CPU seconds at a peak of 2.6 GiB resident; the level-8 item takes most of the wall time, and the
self-test takes 3 s.

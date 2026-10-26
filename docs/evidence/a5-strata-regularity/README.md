# Orbit stratification, singular loci and normal links of the A_5 rank strata

`result.json` is the output of [`strata_regularity.py`](strata_regularity.py) `--out`. The record settles roadmap item 4
of [the global classification](../../notes/rank_locus_two_dimension_gap.md#route-to-the-global-classification-roadmap-items-3-8)
for the A_5 zero-divisor set: the singular locus of every piece of every rank stratum, a Whitney stratification of
C^15 whose strata refine the nullity strata, the closure incidences between the strata, and the transverse germ of
every piece along every stratum of nullity at least 8, with the normal link wherever the germ type is identified.
The mechanism is a symmetry group: the rank strata are unions of orbits of
H = G_2(C) x SO(2, C) x C^*, the locus of nullity at least 8 is a union of twelve orbits and the origin, and every
local question along an orbit becomes one computation at one point.

Seven statements are established:

1. **Symmetry.** H and the reflection mu' -> -mu' carry every rank locus R_k into itself.
2. **Orbits.** R_8 minus 0 is the disjoint union of the twelve H-orbits of the table below.
3. **Incidences.** The closure of each orbit is the closed set of the table, and the closure order is the order of the
   table's last column. In particular W8 n E8-bar = B9 and W8 n V = V n B9.
4. **Singular loci.** The singular locus of every closure, of V(Q) and of V(G) is the union of orbits listed below.
5. **Nullity 4.** V(Q) is smooth off 0, Sing V(G) = W8 u V, and V(Q) n V(G) is an irreducible normal complete
   intersection of dimension 13, smooth off R_8, where V(Q) and V(G) cross transversally.
6. **Stratification.** The twelve orbits, the origin, the three nullity-4 strata and the nullity-0 stratum form a
   Whitney stratification of C^15; each R_k and each nullity stratum S_k is a union of strata.
7. **Germs and links.** The transverse germ of each closure along each orbit has the invariants of the germ table. At
   x0 = e_1 + e_18 the normal link of R_12 = V u B9 is S^1 disjoint union S^3.

Every decision is an exact computation: python-flint ranks of rational matrices, and Singular 4.4.1 standard bases,
radicals, saturations and minimal associated primes over Q, all in global orderings. No random draw enters; every point
is an explicit integer vector.

## Conventions

The coordinates, split coordinates, pieces and the slice families are those of
[the strata record](../a5-zero-divisor-strata/README.md) and [the equations record](../a5-rank-strata-equations/README.md).
A doubly pure y of A_5 is the vector z' = (u', mu', v') in C^15 in split coordinates, with u', v' in the 7-dimensional
module of the split octonions, eta the invariant form diag(-, -, +, -, +, +, -) and x x y the cross product. R_k is the
closed set of nullity at least k and S_k = R_k minus R_(k+4). Write s = u' + v' and d = u' - v'.

**Real and complex.** The map y -> z' is an R-linear isomorphism of the doubly pure subspace R^30 onto C^15, and
D_(5,k) is the unit section of the cone S_k. Every statement below is about the complex cones read as real sets:
complex smoothness is real smoothness, a complex orbit of dimension n has real dimension 2n, and the link of a complex
germ of dimension n is a real manifold or stratified space of dimension 2n - 1. All strata are cones under the real
scaling, so the unit sphere S^29 meets every stratum transversally and the stratification restricts to D_(5,k) with
every stratum dimension dropping by one.

**The group.** G_2(C) acts by its 14 derivations on u' and v' alike, C^* by scaling, and SO(2, C) by the boost
(u', v') -> (c u' + s v', s u' + c v'), c^2 - s^2 = 1, which is the rotation of (u, v) in original coordinates. H has
dimension 16; the orbit dimension at z' is the rank of the 16 tangent vectors `h_generators` there.

**Closures.** Each orbit has a closure with the generators below, in split coordinates; "isotropic" means
eta(u') = eta(v') = eta(u', v') = 0.

| Closure | Equations | Open orbit | dim | nullity | Representative (u', mu', v') |
| --- | --- | --- | --- | --- | --- |
| W8 | mu' = 0, eta(s) = eta(d) = 0 | pairs spanning a nondegenerate plane | 12 | 8 | (e'_1, 0, e'_3) |
| E8-bar | Q = 0, Delta = 0, rank [u'; v'; u' x v'] <= 2 | P3a, P3b pairs with mu' != 0 | 11 | 8 | (A + 3 e'_1, 4, 2 A + 5 e'_1) |
| Iso | mu' = 0, isotropic | independent pairs in a generic isotropic plane | 11 | 8 | (n, 0, e'_2 + e'_5) |
| X_+ | E8-bar, mu' = 0, eta(d) = 0 | P3a, P3b pairs with mu' = 0, d null | 10 | 8 | (A + e'_1, 0, e'_1) |
| X_- | E8-bar, mu' = 0, eta(s) = 0 | P3a, P3b pairs with mu' = 0, s null | 10 | 8 | (A + e'_1, 0, -e'_1) |
| B9 | mu' = 0, isotropic, u' x v' = 0 | independent pairs in a special isotropic plane | 9 | 12 | (n + 2 k, 0, 3 n + 5 k) |
| V | rank [u'; v'] <= 1, Q = 0 | (alpha w, beta w), eta(w) != 0, mu' != 0 | 8 | 12 | (3 e'_1, 4, 5 e'_1) |
| VB = V n B9 | mu' = 0, isotropic, rank [u'; v'] <= 1 | (alpha n, beta n), n null, alpha^2 != beta^2 | 7 | 12 | (n, 0, 0) |
| V^a_+ | mu' = 0, v' = u' | v' = u', eta(u') != 0 | 7 | 12 | (e'_1, 0, e'_1) |
| V^a_- | mu' = 0, v' = -u' | v' = -u', eta(u') != 0 | 7 | 12 | (e'_1, 0, -e'_1) |
| N_+ | mu' = 0, v' = u', eta(u') = 0 | itself minus 0 | 6 | 16 | (n, 0, n) |
| N_- | mu' = 0, v' = -u', eta(u') = 0 | itself minus 0 | 6 | 16 | (n, 0, -n) |

Here n = e'_1 + e'_3 (null), k = e'_4 + e'_6 (null, n x k = 0) and A = e'_2 + e'_3 (null, in V_+ of e'_1). The pieces of
the strata record are W8, E8-bar, B9, V, N_+ and N_-; Iso, X_+, X_-, VB, V^a_+ and V^a_- are new closures of lower
orbits. V^a_+ and V^a_- carry the {a, 0} and {0, a} families of the strata record's reconciliation.

**Closure order** (`representatives.lower`, the representative of Y lies in X):

| X | closures strictly inside X |
| --- | --- |
| W8 | Iso, B9, VB, N_+, N_- |
| E8-bar | X_+, X_-, B9, V, VB, V^a_+, V^a_-, N_+, N_- |
| Iso | B9, VB, N_+, N_- |
| X_+ | B9, VB, V^a_+, N_+, N_- |
| X_- | B9, VB, V^a_-, N_+, N_- |
| B9 | VB, N_+, N_- |
| V | VB, V^a_+, V^a_-, N_+, N_- |
| VB | N_+, N_- |
| V^a_+ | N_+ |
| V^a_- | N_- |

## Computations

Each part of `result.json` is an exact computation, and its `pass` flag requires every value this section lists: the
script carries the closure order, the plane table and the germ table as constants and compares each computed value with
them.

1. **Identities** (`identities`). Over Z[z']: Q = eta(s, d) - mu'^2 and G = eta(s) eta(d) - 2 mu'^2 eta(s, d) + mu'^4,
   with Q and G the polynomials of the equations record.
2. **Symmetry** (`symmetry`). For every closure ideal of the table and for Q and G, the boost derivation
   sum_k (v'_k d/du'_k + u'_k d/dv'_k) maps every generator into the ideal, and the reflection mu' -> -mu' maps the
   ideal into itself (reduction modulo a standard basis).
3. **Representatives** (`representatives`). At the twelve points: the nullity of the 32 x 32 matrix L_y, the rank of
   the 16 H-generators (equal to the closure dimension), and the membership pattern in the twelve closures. The
   twelve patterns are distinct, they reproduce the closure-order table, every closure listed below X has smaller
   dimension, and every representative lies in V(G) and, except that of W8, in V(Q).
4. **Closure dimensions** (`closure_dims`). The Krull dimension of each closure ideal equals the dimension of the
   table.
5. **Orbit certificate** (`certificate`). For each slice plane (A, B) of Lemma 5: r_G, the dimension of the G_2-orbit
   of the pair (A, B), and the subalgebra s of gl_2 induced by the stabilizer of the plane:

   | Slice | r_G | dim s |
   | --- | --- | --- |
   | P2 | 11 | 1 |
   | P3a, P3b | 9 | 2 |
   | P3c | 11 | 2 |
   | P4s | 9 | 4 |
   | P4g | 11 | 4 |

   For each slice and each closure X, the locus of independent slice pairs in X (det Mc != 0,
   Mc = [[a, b], [c, d]]) where the orbit rank is below dim X lies in the closures below X, and the independent part of
   X outside them has one component on the slices that carry the open orbit of X (P2 for W8; P3a and P3b for E8-bar,
   X_+ and X_-; P4s for B9; P4g for Iso) and none elsewhere.
6. **Isotropic closure** (`iso`). The four generators of Iso cut out dimension 11 in C^15 (a complete intersection of
   codimension 4), and on every slice the 4 x 4 minors of their Jacobian vanish only on VB.
7. **Nullity 4** (`nullity4`). On every slice: the radical of (G, dG) equals the radical of I(W8) n I(V), and every
   minimal prime of the radical of (Q, G, 2 x 2 minors of [dQ; dG]) contains the ideal of Iso or of E8-bar.
8. **Germs** (`germs`). For each closure X, for V(Q) and V(G), and for each orbit O inside X: the affine slice
   z' = p + sum t_j e'_(c_j) through the representative p of O, with coordinate directions c_j completing the orbit
   tangent space (`transverse_columns`, greedy in index order, at VB with z3 tried before z1); the minimal primes of
   the restricted ideal through p, whose intersection is the reduced germ; for the germ and each prime, the dimension,
   the embedding dimension (slice dimension minus the Jacobian rank at p), and the tangent cone by deformation to the
   normal cone, (X(h t) : h^infinity) at h = 0, whose degree is the multiplicity; the rank of the tangent-cone quadric
   when the germ is a hypersurface of multiplicity 2 in its embedding; and for two sheets the largest minimal prime of
   their sum through p. Every row must equal the germ table of the script, and every sheet through p must have the
   full germ dimension.

The self-test breaks each part: the compact rotation (u', v') -> (v', -u') fails the symmetry check (it does not
preserve Q); the representatives of V^a_+ and V^a_- swapped fail their membership patterns; B9 without u' x v' = 0
fails its dimension; the Iso certificate on P4s with B9 removed from its lower closures reports an escaping drop
locus; and V with the mu'^2 term removed from Q loses its A_1 germ at N_+.

## Theorem 1: symmetry

R_16 = N_+ u N_-, R_12 = V u B9, R_8 = W8 u E8-bar and R_4 = V(Q G) (the strata and equations records). Computation 2
shows that the boost derivation preserves each of these ideals, so the one-parameter group it generates maps each
variety into itself; SO(2, C) is that group. G_2 preserves every R_k by the equivariance [D, C'_z] = C'_(D z) of the
strata record, and C^* because every R_k is a cone. The reflection preserves each ideal by computation 2. QED

The boost does not conjugate C_z: it preserves the rank loci, which are cut out by G_2-invariant data (Q, Delta, the
span of (u', v') and the cross product), while acting on the pair (u', v') rather than on the algebra.

## Theorem 2: the orbit decomposition of R_8

*Orbit rank on a slice.* Let p = (a A + b B, m, c A + d B) be a slice point. If Mc = [[a, b], [c, d]] is invertible,
the G_2-tangent space at (u', v') is Mc applied to the G_2-tangent space of (A, B), of dimension r_G, and its
intersection with the pairs in span(A, B) is s (A, B). The scaling vector is independent of everything else through
its mu' entry when m != 0, and the boost vector (v', u') is the pair Mc^-1 J Mc (A, B), J the row swap. So the orbit
dimension is r_G + [m != 0] + the rank of {N_b, [m = 0] I} modulo s, with N_b = adj(Mc) J Mc up to the unit det Mc.
`certificate_job` writes the minors of these small matrices as polynomials in (a, b, c, d) and intersects them with
each closure.

If Mc is singular, (u', v') = (alpha w, beta w). The G_2-orbit of w != 0 has dimension 6 (F1 for eta(w) != 0, F3 for w
null; the strata record), and its tangent space at w contains w exactly when w is null (the null cone minus 0 is one orbit,
while eta(g w, w) = 0 for g in the Lie algebra forbids g w = lambda w, lambda != 0, when eta(w) != 0). The orbit
dimension is therefore 6 + [m != 0] + the rank of {(beta, alpha), [m = 0] (alpha, beta)} modulo [w null] (alpha, beta):

- eta(w) != 0, m != 0: 8, the orbit of V (Q = 0 forces alpha^2 != beta^2);
- eta(w) != 0, m = 0: Q = 0 forces alpha = +-beta, giving 7, the orbits V^a_+ and V^a_-;
- w null: Q = 0 forces m = 0; 7 when alpha^2 != beta^2 (VB), 6 when alpha = +-beta (N_+, N_-).

Every dependent point of R_8 satisfies Q = (alpha^2 - beta^2) eta(w) - m^2 = 0. On E8-bar this is an equation. On W8,
m = 0 and eta(s) = (alpha + beta)^2 eta(w) = 0, eta(d) = (alpha - beta)^2 eta(w) = 0, so w is null or alpha = beta = 0,
and Q = 0 again. Hence the dependent part of every closure lies in the union of V, V^a_+-, VB and N_+-, and in each
closure X in the lower closures of X: Iso, B9 and W8 force w null; X_+ excludes V^a_- because eta(d) = 4 eta(u') != 0
there, and X_- excludes V^a_+ likewise.

*Proof of the decomposition.* Induct on the closures in order of dimension. Let X be a closure with dim X = n, and
suppose every closure below X is a union of listed orbits. Every closure is irreducible: W8, E8-bar, B9, V, N_+ and
N_- by the strata and equations records; Iso because it is a complete intersection (computation 6) whose singular
locus lies in VB of dimension 7, codimension 4 >= 2, so it is normal by Serre's criterion, and a normal cone is
connected and so irreducible; VB as the image of C^2 x N; V^a_+ and V^a_- as linear spaces. X_+ and X_- are
irreducible by two arguments. First, on X_+ the conditions mu' = 0 and eta(d) = 0 reduce E8-bar to
rank [s; d; s x d] <= 2 with eta(s, d) = 0; over the null vector d = n the fiber in s is a linear 4-space, and G_2 is
transitive on nonzero null vectors (F3), so X_+ n {d != 0} is the image of G_2 times a linear space, irreducible of
dimension 10, and X_+ n {d = 0} = V^a_+ lies in its closure along the curve (e'_1 + c A, 0, e'_1 - c A)
([verification.md](verification.md)); X_- is the same with s and d exchanged. Second, from this record alone: H is
connected and preserves the ideal of X, so it fixes each minimal prime, and an H-stable component of dimension below
dim X is the closure of a lower orbit O and appears in the germ at the representative of O as a sheet of dimension
below the germ dimension; computation 8 finds every sheet of full dimension. By the
certificate and the dependent case, every point of X outside the closures below it has orbit dimension n. Orbits of
dimension n in the irreducible n-dimensional X are open, and two open subsets of an irreducible space meet, so X minus
the lower closures is one orbit, which contains the representative. Every point of R_8 lies in W8 or E8-bar, so R_8
minus 0 is the union of the twelve orbits. QED

The representatives fix the nullities: R_16 is N_+ u N_-, R_12 is the union of the orbits of V, B9, VB, V^a_+ and V^a_-
and N_+-, and S_8 is the union of the orbits of W8, E8-bar, Iso, X_+ and X_-.

*Non-nested intersections.* The orbits in both W8 and E8-bar are those of B9, VB and N_+-, so W8 n E8-bar = B9; the
orbits in both W8 and V are those of VB and N_+-, so W8 n V = VB = V n B9. Every intersection of closures is the
union of the closures of the orbits they share.

## Theorem 3: singular loci

A closure X is smooth along an orbit O exactly when its transverse germ at the representative of O is smooth
(multiplicity 1 and embedding dimension equal to dimension): the action map H x (slice) -> C^15 is a submersion at
(1, p), and X is H-stable, so X is locally the product of O with its slice germ. By homogeneity this holds along
all of O. From the germ table:

| Closure | Singular locus | Smooth along |
| --- | --- | --- |
| N_+, N_-, VB, B9, V(Q) | {0} | every orbit in it |
| V^a_+, V^a_- | empty (linear) | every orbit |
| V | N_+ u N_- | VB, V^a_+, V^a_- |
| W8 | N_+ u N_- | Iso, B9, VB |
| Iso | VB (with N_+-) | B9 |
| X_+ | V^a_+ (with N_+) | B9, VB, N_- |
| X_- | V^a_- (with N_-) | B9, VB, N_+ |
| E8-bar | V u B9 = R_12 | X_+, X_- |
| V(G) | W8 u V | E8-bar, X_+, X_- and the nullity-4 strata |

V(G) is singular along all of W8 (an A_1 germ along the open orbit of W8) and smooth along the open orbit of E8-bar,
although both lie in R_8. Computation 7 confirms Sing V(G) = W8 u V on every slice by radical equality.

The generators of X_+ in the closure table have Jacobian rank 3 or 4 at the representatives of B9, VB and N_- (X_- at
B9, VB and N_+), below the codimension 5, so that generating set is not radical there. Smoothness of X_+- along those
orbits rests on the germ of the radical ideal (computation 8), never on the Jacobian of the listed generators.

## Theorem 4: the nullity-4 locus

V(Q) is a nondegenerate quadric cone (Hessian of rank 15), smooth off 0. Sing V(G) = W8 u V (computation 7; also from
the gradient of G in s, d, mu', which vanishes on G = 0 exactly where eta(d) s = mu'^2 d, eta(s) d = mu'^2 s and
mu' Q = 0). The points of V(Q) n V(G) where dQ and dG are dependent lie in Iso u E8-bar, of dimension 11 (computation 7); the
independent verification sharpens this to Iso u V.
So V(Q) n V(G) is a complete intersection of dimension 13 whose singular locus has codimension 2; it is normal by Serre's
criterion, connected as a cone, and therefore irreducible. Off R_8 the two hypersurfaces are smooth and cross
transversally along V(Q) n V(G), so S_4 is the union of three connected smooth strata:

- V(Q) minus (V(G) u R_8), complex dimension 14;
- V(G) minus (V(Q) u R_8), complex dimension 14;
- V(Q) n V(G) minus R_8, complex dimension 13, an irreducible smooth variety minus a proper closed set.

The normal link of the third stratum in R_4 is the Hopf link: two circles in S^3, the link of {x y = 0} in C^2.

## Theorem 5: the Whitney stratification

The strata are the twelve orbits, the origin, the three strata of Theorem 4 and C^15 minus R_4. Each is smooth, locally
closed and H-stable; the closure of each is a union of strata (Theorem 2 for the orbits, Theorem 4 and the memberships
of the representatives in V(Q) and V(G) for the others). Whitney's condition (b) holds for every pair (X, Y) with Y in
the closure of X: the set of points of Y where it fails is nowhere dense in Y (Whitney's theorem for algebraic
strata), it is H-stable because H acts by algebraic diffeomorphisms, and every Y of nullity at least 8 is a single
orbit, so the set is empty. At the origin every stratum X is a cone, so the secant from 0 to x is the radial line,
which lies in the tangent space of X at x, and condition (b) holds. Pairs within S_4 consist of submanifolds of the smooth hypersurfaces V(Q) and V(G),
and the open stratum satisfies (b) trivially. By the Thom-Mather isotopy lemma the germ, and hence the normal link, of
every stratum is constant along it.

Rank loci and smooth strata stay distinct: R_8 is one rank locus made of two irreducible pieces (W8, E8-bar), and its
smooth strata are the five orbits of S_8 and the seven orbits of R_12; the nullity-8 stratum alone needs five strata.

## Theorem 6: transverse germs

For each closure X and orbit O inside it, `germs` reports the reduced transverse germ of X at the representative of O.
"Sheets" counts minimal primes through the point; a germ of multiplicity 2 that is a hypersurface in its embedding with
a tangent-cone quadric of full rank is analytically the quadric cone (Morse lemma), whose link is the Stiefel manifold
V_2(R^m), m the embedding dimension (V_2(R^3) = RP^3). Smooth germs of dimension n have link S^(2n - 1).

| Closure along orbit | germ dim | mult | embdim | type | link |
| --- | --- | --- | --- | --- | --- |
| V along N_+- | 2 | 2 | 3 | A_1, quadric rank 3 | RP^3 |
| W8 along N_+- | 6 | 2 | 7 | quadric cone, rank 7 | V_2(R^7) |
| Iso along VB | 4 | 2 | 5 | quadric cone, rank 5 | V_2(R^5) |
| Iso along N_+- | 5 | 2 | 6 | quadric rank 5, corank 1 | open |
| E8-bar along V | 3 | 2 | 6 | two smooth sheets meeting at the point | S^5 disjoint union S^5 |
| E8-bar along V^a_+- | 4 | 2 | 7 | two smooth sheets meeting in a curve | two S^7 glued along a circle |
| X_+ along V^a_+ (X_- along V^a_-) | 3 | 2 | 6 | two smooth sheets meeting at the point | S^5 disjoint union S^5 |
| E8-bar along B9 | 2 | 2 | 3 | A_1, quadric rank 3 | RP^3 |
| E8-bar along VB | 4 | 2 | 7 | one minimal prime | open |
| E8-bar along N_+- | 5 | 3 | 8 | one minimal prime | open |
| X_+ along N_+ (X_- along N_-) | 4 | 2 | 7 | one minimal prime | open |
| V(G) along the open orbit of W8 | 2 | 2 | 3 | A_1, quadric rank 3 | RP^3 |
| V(G) along V | 6 | 2 | 7 | quadric cone, rank 7 | V_2(R^7) |
| V(G) along V^a_+- | 7 | 2 | 8 | quadric rank 7, corank 1 | open |
| V(G) along Iso, VB, B9 | 3, 7, 5 | 2 | 4, 8, 6 | quadric rank 2 | open |
| V(G) along N_+- | 8 | 3 | 9 | | open |

Along V^a_+- the script computes the meet of the two sheets as a curve, and the critical review
([2026-10-26-a5-strata-regularity-critical.md](../../archive/reviews/2026-10-26-a5-strata-regularity-critical.md))
found that reduced meet to be a smooth curve, whose link is the circle of the table. Every other pair in `result.json`
is a smooth germ. "Open" means the record computes the invariants and does not
identify the link.

**The link at x0.** x0 = e_1 + e_18 has split coordinates u' = e'_2 - i e'_1 (null), mu' = 0, v' = 0; G_2 and C^* carry
it to (n, 0, 0), the representative of VB. In the 8-dimensional slice transverse to VB, the germ of V is a smooth curve
and the germ of B9 is a smooth surface (V and B9 are smooth along VB), and they meet only at the point (VB is one
point of the slice). The normal link of R_12 = V u B9 along VB is therefore S^1 disjoint union S^3, constant along VB
(Theorem 5). This identifies the Bouligand cone A15 u B17 of
[the selected-center note](../../notes/nullity_twelve_local_geometry.md): the tangent spaces of V (real dimension 16,
unit dimension 15) and B9 (18, unit 17) meeting in the tangent space of VB (14, unit 13).

## Independent verification

[verification.md](verification.md) re-derives every statement from `gororoba_quantum/cd_core.py` with separate code,
[verify_regularity_independent.py](verify_regularity_independent.py), whose output is
[verification.json](verification.json). It uses a finite boost element instead of the boost derivation, orthogonal
complements instead of coordinate slices, and the deformation to the normal cone with global orderings instead of
local standard bases. It confirms every statement and every row of the singular-locus and germ tables, including the
A_1 type of E8-bar along B9. It does not re-prove computation 5: it replaces the drop-locus certificate by an exhaustive
search of the six slices (a Gaussian box, an integer box and all of F_13^5), which finds no point of R_8 outside the
twelve orbits, so computation 5 remains the only proof of that step. A
[critical review](../../archive/reviews/2026-10-26-a5-strata-regularity-critical.md) of the draft found no fatal
defect; its findings and their disposition are recorded there.

## Imported results

- The pieces, the equations of every R_k, the slice families and Lemma 5's covering (strata record Theorems 6 and 7,
  equations record), the G_2-equivariance of C'_z and the orbit facts F1 to F4, the irreducibility of W8, E8-bar, B9,
  V and N_+-, and the element of G_2 mapping the P3b plane to the P3a plane.
- Standard facts: the orbit dimension of a connected algebraic group action is the rank of its Lie algebra at the
  point; an irreducible variety has at most one open orbit; Serre's normality criterion for complete intersections; a
  normal connected variety is irreducible; Whitney's theorem that the (b)-bad set is nowhere dense, and the
  Thom-Mather isotopy lemma; the Morse lemma for a germ with nondegenerate Hessian; the link of
  {x_1^2 + ... + x_m^2 = 0} in C^m is V_2(R^m); the tangent cone at 0 is the special fiber of the deformation to
  the normal cone, and its degree is the multiplicity; transverse slices through a point of an orbit give isomorphic
  germs.
- Singular 4.4.1 (std, radical, sat, intersect, minAssGTZ, minor) and python-flint 0.9.0.

## Falsifiers and scope

Each of the following refutes the statement where it occurs: a closure ideal not preserved by the boost; a
representative of the wrong nullity, orbit rank or pattern; two equal patterns; a closure of the wrong dimension; an
escaping prime in the certificate, or an open component on an unexpected slice; a Jacobian drop of Iso off VB; Sing
V(G) differing from W8 u V on a slice; a dependent point of V(Q) n V(G) outside Iso u E8-bar; a germ invariant
differing from the germ table, or a sheet of less than the germ dimension. None occurred.

Out of scope: the link topology of the germs marked open; analytic (as opposed to algebraic) branch counts where a
germ has one minimal prime; kernel bundles, attachments and homology (roadmap items 5 to 8); a Rocq formalization.

## Replay

Singular 4.4.1 must be on PATH. It is not in the hosted CI image, so this record is a retained replay rather than a
gate.

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-strata-regularity/strata_regularity.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-strata-regularity/strata_regularity.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-strata-regularity/strata_regularity.py \
    --out docs/evidence/a5-strata-regularity/result.json
```

`result.json` records the Python, python-flint and Singular versions and the script's sha256. Its `seconds`,
`timings_s` and `total_s` fields vary from run to run; every other field is deterministic.

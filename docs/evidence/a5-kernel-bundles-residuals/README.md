# Kernel-bundle residuals

This record settles the residuals that `bundle_invariants.py` lists outside its classification denominator
(`out_of_denominator_residuals` in [the kernel-bundle record](../a5-kernel-bundles/bundle-invariants-result.json)).
The [open work program](../../design/dimension32-global-topology-program.md) states each residual's method and
falsifier.

## The quaternionic four-plane `xi_R` over `V_2(R^7)` is actually nontrivial

The kernel-bundle record shows `xi_R + R^4 = R^8`, so `xi_R` is stably trivial, and leaves its actual type open.
`xi_R` is actually nontrivial:

1. `G_2` acts transitively on orthonormal pairs `(a, b)` of imaginary octonions, with stabilizer the group fixing
   `H = span(1, a, b, ab)` pointwise, so `V_2(R^7) = G_2 / SU(2)` and `xi_R = G_2 x_SU(2) H^perp`.
2. `xi_real_type.py` solves the derivation algebra of the octonions exactly over Q on the `cd_core` basis
   (dimension 14) and its stabilizer of `(e1, e2)` (dimension 3, acting by zero on `H`). On `H^perp` the stabilizer
   is purely self-dual: self-dual rank 3, anti-self-dual rank 0. It lies in one `su(2)` factor of
   `so(4) = su(2) + su(2)`, so `pi_4(SU(2)) = Z/2` injects into `pi_4(SO(4)) = Z/2 + Z/2` under the structure map.
3. Over the fiber `S^5 = SU(3) / SU(2)` of `V_2(R^7) -> S^6`, `xi_R` restricts to `SU(3) x_SU(2) C^2`, whose clutching
   class is the image of the generator under the boundary map `pi_5(S^5) -> pi_4(SU(2))` of
   `SU(2) -> SU(3) -> S^5`. Because `pi_4(SU(3)) = 0`, that map is onto, so the class is the generator of `Z/2`.
4. The second item carries that nonzero class into `pi_4(SO(4))`, so `xi_R` restricted to `S^5` has no real frame,
   and neither does `xi_R`.

The same restriction shows the complex doublet `xi` nontrivial on `S^5`, in agreement with the record's
"actually nontrivial per copy".

The falsifier was a derivation dimension other than 14, a stabilizer other than three-dimensional or moving `H`, or a
stabilizer meeting both `so(4)` factors. None occurred. The mutation adds an anti-self-dual generator; the rank test
then reads (3, 1) and rejects it. The homotopy facts in the third item (`pi_4(SU(3)) = 0`, the fibration's long exact
sequence) are standard and enter as written arguments; the producer covers the representation-theoretic premise.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/xi_real_type.py --check` (about 10 s, exact).

Prior computation: Skiouris, "Algebraic Hiddenness in the Sedenion Algebra" (Zenodo record 22016333, published
2026-08-19; [note](../../notes/papers/skiouris-2026-algebraic-hiddenness.md)), Theorem 6.4, proves the sedenion
kernel bundle K = G2 x_SU(2) H over the aphanic slice V_2(R^7) topologically nontrivial by the same restriction to the
S^5 fiber of S^5 -> V_2(R^7) -> S^6. The two bundles are equal: Skiouris's kernel basis (e7 + e12, -e6 + e13, e5 + e14,
-e4 + e15) at p0 = e1 + e2 l (equation (25), Theorem 6.3) carries the doubled action of the three stabilizer
derivations by the same three 4 x 4 matrices as (e4, e5, e6, e7) carries on H^perp, so e4, e5, e6, e7 -> v1, v2, v3,
v4 is an SU(2)-equivariant isomorphism and K = G2 x_SU(2) K0 = xi_R (replay:
`"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/skiouris_intertwiner.py --check`, exact, under 1 s). The priority of the
nontriviality statement belongs to that paper; the record here adds the exact `cd_core` representation certificate and
the stable-triviality identity xi_R + R^4 = R^8 (Skiouris's stable-triviality sentence infers it from vanishing
characteristic classes alone, which does not suffice).

## Smaller reductions on nullity 12

The residual has two readings, and the record now settles one and bounds the other.

*Topological.* The five nullity-twelve complex bundles are trivial (the kernel-bundle record's class table: `C^6`
on every piece), and a trivial `C^6 = H^3` admits a global quaternionic structure anticommuting with `J`, so a
topological `Sp(3)` reduction exists on every piece.

*Equivariant.* An antilinear map commuting with a circle sends its weight-`w` eigenspace to weight `-w`. On `B9` the
connected stabilizer `U(1)` acts on the kernel with weights `-1` and `-2` only (`3 C_(-1) + 3 C_(-2)`), and on `VB` the
central weights of `V_(0,-4) + 2 V_(1,-3) + V_(0,-2)` are all negative, so neither piece carries a stabilizer-equivariant
quaternionic structure. A change of lift convention flips every sign together (`-(w+t)` in the record's conversion)
and keeps the weights of one sign. On `V` with `0 < rho < 1` the stabilizer `SU(2)` acts by `2 V_0 + 2 V_1`, which
admits an equivariant quaternionic structure at each point (both summands are quaternionic after tensoring with
`C^2`), and at `rho = 1` the `SU(3)` module `3 + conjugate(3)` admits one swapping the two summands. Whether those
pointwise structures glue to a global equivariant one over the `V` moduli is open, and so is the aligned pair
`V^a_+-`, whose stabilizer representation this record has not read.

Falsifier for the equivariant exclusion: a stabilizer weight of positive sign on `B9` or `VB` in the record's
stabilizer computation.

## Full component group: reduction to the `G_2` centralizer

`Out(g_2)` is trivial (the Dynkin diagram of `G_2` has no symmetry), and `g_2` is the derived algebra of the Lie
algebra of `K`, so conjugation by any element of `K` preserves `G_2` and agrees on it with conjugation by an element
of `G_2`: every component of `K` meets the centralizer `Z = Z_K(G_2)`, and `pi_0(Z) -> pi_0(K)` is onto. It is
one-to-one because `Z` meets the identity component `K^0 = G_2 T` in the centralizer of `G_2` there, which is the
central torus `T` (`G_2` has trivial center) and is connected.
Hence `pi_0(K) = pi_0(Z_K(G_2))`.
`probes/g2_commutant.py` computes the commutant of the fourteen octonion-derivation triples
in each slot of the transport triple exactly over Q: dimension 32 with a 4-dimensional invariant subspace in every
slot, so each slot decomposes as `4 R + 4 R^7` and the centralizer is `GL(4) x GL(4)` per slot
([log](probes/g2-commutant.log)). `Z_K(G_2)` is therefore the solution set of the group-level transport equations in
96 unknowns, with Lie algebra the four central directions.

## The component group is the visible `S_3 x Z_2`

[`centralizer_components.py`](centralizer_components.py) counts the components of the complex group `Z_C` of
`Z = Z_K(G_2)`; the record is [`centralizer-components-result.json`](centralizer-components-result.json). The
identity component of `Z` is the torus `T` of the four central directions. `J = L_(e_16)` and `R = R_(e_16)`
commute and square to `-1`, and their joint eigenspaces are four lines on the unit multiplicity space and two
planes on the vector multiplicity space, where only the sign pairs `(e, -e)` occur. Proof of the reduction to patterns, each
hypothesis of which this record or the kernel-bundle record checks: `Z` normalizes
`T`, so `P` and `Q` permute the four unit lines and the two vector planes and `G` permutes the two eigenspaces of
`J` on the doubly pure space; a pattern is a choice of these permutations, 4,608 in all, and within a pattern the
unknowns are ten scalars and six 2 x 2 blocks. `T` scales the unit scalars by characters, four of which generate
its character lattice (index 1, read from the exact eigenvalues of the four generators), so setting those four
scalars to 1 meets each coset of `T` once.

**Observed:** over `Q(i)` the gauge-fixed ideal (the equations `Q L_y = L_(G y) P` on eigen-coordinates, the gauge
and the inverses of every scalar and block determinant, 50 variables) is empty for 4,606 patterns and
zero-dimensional and radical with 6 points for two: the identity pattern and the pattern that exchanges every sign
pair with its negative. No pattern has positive dimension. `Z_C` therefore has 12 components. On the character
lattice of `T` complex conjugation fixes a cocharacter lattice of rank 2, and the norms fill it (elementary
divisors 1, 1), so the real points of `T` are connected. Controls: the identity triple solves the identity
pattern, and with one structure sign flipped the identity pattern has 1 point in place of 6. The equations are
imposed for `y` on one unit eigenvector per class and on the vector eigenvectors of octonion index 1; on both
patterns with points the equations for the indices 1 to 7 reduce to zero modulo that ideal.

**Proved (`A5-379`)**, from the counts above: two real
points of `Z` in one component of `Z_C` differ by a real point of `T`, which is
connected, so the real group has at most 12 components. The visible subgroup `S_3 x Z_2` occupies 12 distinct
components ([kernel bundles](../a5-kernel-bundles/README.md#a-visible-s_3-x-z_2-occupies-twelve-components)), so
`pi_0(K) = pi_0(Z) = S_3 x Z_2`: every constant kernel-pencil symmetry is a product of an element of the identity
component and one of the twelve visible automorphisms. The deduction uses the reduction of the section above and
the Lie algebra of the kernel-bundle record.

A pattern with a point outside the two listed, a pattern of positive dimension, a gauge index other than 1, a
disconnected real torus, or a flipped sign that leaves the count falsifies the record. The replay takes 1 minute
42 seconds of wall time and 84 MiB in the parent on two workers under an 8 GiB memory scope
(Python 3.14.9, sympy 1.14.0, python-flint 0.9.0, Singular 4.4.1) on the build host.

## Nullity-4 strata carry continuous moduli

The kernel symmetry triples are solved once over the whole doubly pure base, so the same 18-dimensional algebra acts
on the nullity-4 strata, with base action of rank 16. `probes/nullity4_orbit_ranks.py` evaluates the tangent rank of
the orbit at the 66 nullity-4 points of an exact integer grid in split coordinates (the strata record's `V(G)` point
included) and sorts them by `V(Q)` and `V(G)` membership ([log](probes/nullity4-orbit-ranks.log)):

| Stratum | Real unit dimension | Generic orbit rank | Real moduli | Points (rank 16, rank 13) |
|---|---:|---:|---:|---|
| `V(Q)` minus `V(G)` | 27 | 16 | 11 | 3, 9 |
| `V(G)` minus `V(Q)` | 27 | 16 | 11 | 23, 29 |
| `V(Q) n V(G)` | 25 | 16 | 9 | 2, 0 |

Rank 16 equals the base rank, so it is the generic value; rank 13 marks a special sublocus. The nullity-4 kernel
bundles are therefore families over moduli spaces of real dimension 11, 11 and 9, and the homogeneous
stabilizer-representation route of the higher nullities does not classify them alone; their classes come from the
kernel Gauss map into `Gr(2, C^16)` (real nullity 4, complex rank 2) over those moduli.

[`nullity4-kernel-gauss-result.json`](nullity4-kernel-gauss-result.json) starts that Gauss-map computation without
collapsing the continuous moduli. On all 66 retained exact grid points, `nullity4_kernel_gauss.py` constructs an
order-fourteen principal-Pfaffian Schur frame of `ker A(z, conjugate(z))`, realifies it to a four-frame of
`ker L_y`, and records the 120 normalized Plucker coordinates of the resulting point of `Gr(2,C^16)`. Every frame
identity, Pfaffian-square identity, real kernel identity, and Plucker quadric holds exactly, and the coordinates equal
those of an independently computed nullspace. On the first fixture of each stratum that comparison rejects all 120
single-coordinate shifts and the vector (1, 0, ..., 0), which satisfies every Plucker quadric and names another plane. The general principal-rank theorem supplies 120 local charts, indexed by the two free rows;
on a double overlap the transition is the target frame restricted to the source free rows.

This is a fixture-level chart and coordinate certificate, not the requested nullity-four classification. It does not
give equations for the Gauss image over the nine- and eleven-dimensional moduli, a finite cover of those moduli by
explicit parameter charts, global transition functions, stabilizer jumps, or a bundle class. The
[section below](#the-nullity-4-kernel-gauss-map-factors-through-the-planes-of-the-three-planes-ker-mz) measures the
image modulo 32029: its dimension, its linear span and its quadric equations on each stratum. The falsifier of a
classification stays a transition outside the claimed structure group or two exact points with the same proposed
moduli invariants and different Plucker images.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_kernel_gauss.py --check` (exact). The producer
uses the repository worker cap through `parallel.ordered_map`; the 66 fixtures are independent.


## The nullity-4 kernel Gauss map factors through the planes of the three-planes ker M(z)

The bordered matrix `A(z, w)` has first row `-w` and lower 15 x 15 skew block `M(z)`, linear in `z`; a real point has
`w = conjugate(z)`. [`nullity4_gauss_image.py`](nullity4_gauss_image.py) takes `z` and `w` as independent
variables and computes modulo 32029 with `i = 9115`, at points fixed by a hash of a label and a counter; the
record is [`nullity4-gauss-image-result.json`](nullity4-gauss-image-result.json).

**Observed (`A5-429`), modulo 32029 at four points of each stratum:** `M(z)` has rank 12 and `z` lies in its
kernel; `A(z, w)` has rank 14 for each of three sampled `w` off the stratum and one on it; `ker A(z, w)` has first
coordinate zero, lies in `ker M(z)` and is orthogonal to `w`. At a point off both hypersurfaces `M(z)` has rank 14
with kernel `z` and `A(z, w)` is invertible. In characteristic 0 the retained exact record agrees at its 66 real
fixtures: the 15 Plucker coordinates `p_(0 j)` vanish at each.

**Proved, in any characteristic other than 2, from rank `M(z)` = 12:** write `K = ker M(z)`. `M` is skew, so its
image is `K-perp`. A vector `(a, x)` lies in `ker A(z, w)` exactly when `w . x = 0` and `M x = -a w`. When `w` is
nonzero on `K`, `w` lies outside the image of `M`, so `a = 0` and `ker A(z, w) = {0} x (K n w-perp)`, a plane of
the three-plane `K`: the Gauss map lands in `Gr(2, 15)`. At a real point `w = conjugate(z)` and `z` lies in `K`
with `w . z = |z|^2 > 0`, so the condition holds at every real point of the strata. When `w` vanishes on `K`
(`w = 0` is one case) a kernel vector with `a = 1` exists and the statement fails.

| Stratum | Complex dimension of the projective stratum | Rank of `z -> ker M(z)` | Rank of the Gauss map | Rank of the pair (Gauss map, conjugate Gauss map) | Span of 300 sampled planes in `P^104` | Quadrics vanishing on 6,100 sampled planes |
|---|---:|---:|---:|---:|---:|---:|
| `V(Q)` minus `V(G)` | 13 | 13 | 15 | 26 | 105 | 1,678 |
| `V(G)` minus `V(Q)` | 13 | 13 | 15 | 26 | 105 | 1,543 |
| `V(Q) n V(G)` | 12 | 10 | 12 | 24 | 90 | 2,940 |

These ranks are computed at independent pairs `(z, w)` of sampled points, `w` on the conjugate stratum: they are
ranks of the complexified maps at the sampled pairs, and the rank of the Gauss map is the same with `w` free. The
quadric count is 5,565 monomials in the 105 Plucker coordinates minus the rank of their values at 6,100 sampled
planes, and the rank is the same at 5,800; the Plucker ideal of `Gr(2, 15)` has 1,365 quadrics. A quadric that
vanishes on the image vanishes on the sampled planes, so each count is an upper bound for the quadrics of the
image, and 105 and 90 are lower bounds for the dimension of its linear span.

**Proved (`A5-430`): the fibers are linear.** `A(z, w)` is linear in `(z, w)`, so the pairs whose kernel plane
is a given `P` and whose conjugate kernel plane is a given `P'` lie in the linear space
`L = {(z, w): A(z, w) P = 0, A-bar(w, z) P' = 0}`, which contains the scalings of `z` and of `w`. `P` and `P'`
have first coordinate zero, so `L = L_z x L_w` with `L_z = {z: M(z) P = 0, z perpendicular to P'}` and
`L_w = {w: M-bar(w) P' = 0, w perpendicular to P}`. Every `z` in `L_z` has `P` in `ker M(z)`, so `M(z)` has rank
at most 12, and the identity `P_j = Q G z_j` (`A5-364`) gives `Q(z) G(z) = 0`. `L_z` is irreducible and lies in
one hypersurface. On `V(Q)` minus `V(G)` and on `V(G)` minus `V(Q)`, therefore, the fiber of the pair (Gauss map,
conjugate Gauss map) through a pair of the stratum is an open subset of `L`, and the differential of the pair has
rank at most the tangent dimension minus `dim L`. On `V(Q) n V(G)` the same holds where `L` lies in both
hypersurfaces, as at the two exact fixtures, where `L` is the plane of scalings. At a real point the conjugation
`(z', w') -> (conjugate(w'), conjugate(z'))` preserves `L` and exchanges `L_z` and `L_w`, so the real fiber has
real dimension `dim L` and its image in the projective stratum is an open subset of the projective space of
`L_z` (the points on the other hypersurface or of lower rank are removed), of real dimension `dim L - 2`.

**At the 66 exact real fixtures, on the real locus `w' = z'`:** the differentials are computed modulo 32029,
where the rank of the pair is a lower bound for the rank over the reals of `z -> ker A(z, conjugate(z))` in
characteristic 0 (the pivot block is invertible modulo the prime and the tangent space keeps its dimension);
`dim L` is exact over `Q(i)`; the orbit rank of the 18-dimensional kernel symmetry algebra and the nullity of the
kernel vectors are exact over `Q`.

| Stratum | Fixtures | Orbit rank | Rank of `z -> ker M(z)` | Rank of the Gauss map | Real rank | `dim L` | Nullity of the kernel vectors | Fixtures sharing a kernel plane |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `V(Q)` minus `V(G)` | 3 | 16 | 13 | 15 | 26 | 2 | 4 | 0 |
| `V(Q)` minus `V(G)` | 9 | 13 | 13 | 15 | 26 | 2 | 4 | 0 |
| `V(G)` minus `V(Q)` | 23 | 16 | 13 | 15 | 26 | 2 | 4 | 0 |
| `V(G)` minus `V(Q)` | 13 | 13 | 13 | 13 | 22 | 6 | 12 | 10 |
| `V(G)` minus `V(Q)` | 16 | 13 | 13 | 10 | 16 | 12 | 16 | 12 |
| `V(Q) n V(G)` | 2 | 16 | 10 | 12 | 24 | 2 | 4 | 0 |

In every row the real rank modulo 32029 equals the tangent dimension (28, 28, 26) minus the exact `dim L`, so it
is the real rank in characteristic 0 (`A5-430`). At the 37 fixtures with `dim L = 2` the real Gauss map is an
immersion of the projective stratum. Through each of the other 29 it has a linear fiber of real dimension 4 or 10.
The nullity column is the least nullity, as elements of the algebra, among six vectors of the real kernel of left
multiplication by the fixture: where the fiber is large, the six sampled kernel vectors are zero divisors of a
deeper stratum, which bounds the nullity of a general kernel vector from above only (`A5-538`).

**Proved in characteristic 0 (`A5-431`): the real Gauss map is not injective on `V(G)` minus `V(Q)`.** The
retained fixture record gives the normalized Plucker vector of the kernel plane at each fixture; the 66 fixtures
are 66 projective points and carry 54 planes. Ten planes are each shared by two or three fixtures, 22 in all, each
with `dim L` of 6 or 12; the split points `e_1 + t (e_8 + e_9) + e_13` for `t` = 1, 2, 3 are one example.

**Refuted (`A5-432`): "`dim L > 2` exactly at orbit rank 13".** The fixtures of `V(G)` minus `V(Q)` and of
`V(Q) n V(G)` fit that statement. A grid of 41,616 integer points `e_1 + a e_2 + b e_3 + m e_8 + v` (`v` with
at most three nonzero coordinates among `e_9..e_15`) has 3,687 points of nullity 4, classified modulo 32029 on the
real locus:

| Stratum | Orbit rank | `dim L` | Nullity of a kernel vector | Grid points |
|---|---:|---:|---:|---:|
| `V(Q)` minus `V(G)` | 13 | 2 | 4 | 371 |
| `V(Q)` minus `V(G)` | 16 | 2 | 4 | 1,725 |
| `V(G)` minus `V(Q)` | 13 | 6 | 12 | 61 |
| `V(G)` minus `V(Q)` | 13 | 12 | 16 | 78 |
| `V(G)` minus `V(Q)` | 16 | 2 | 4 | 1,042 |
| `V(G)` minus `V(Q)` | 16 | 2 | 12 | 8 |
| `V(G)` minus `V(Q)` | 16 | 12 | 16 | 14 |
| `V(Q) n V(G)` | 16 | 2 | 4 | 384 |
| `V(Q) n V(G)` | 16 | 6 | 12 | 4 |

Rows 7 and 9 are points of orbit rank 16, the maximum and therefore exact, with a large fiber. Row 1 has orbit
rank 13 modulo 32029, a lower bound for the exact rank, with the smallest fiber; the exact leg of that direction
is the 9 exact fixtures of `V(Q)` minus `V(G)` with orbit rank 13 and `dim L = 2`. At the 26 points of rows 6, 7
and 9 `dim L` is recomputed exactly over `Q(i)` and the kernel nullity exactly over `Q`, and both agree.

**Inferred, modulo 32029:** on `V(Q)` minus `V(G)` and on `V(G)` minus `V(Q)` the three-planes `ker M(z)` form a
family of dimension 13, the projective dimension of the stratum, and the Gauss image is the projection to
`Gr(2, 15)` of the bundle of pairs `(K, P)`, `P` a plane of the three-plane `K = ker M(z)`; the image has
dimension 15 in the 26-dimensional `Gr(2, 15)`. The projection is not injective: two exact fixtures that share a
kernel plane (`A5-431`) have different three-planes, which span a 4-space. On `V(Q) n V(G)` the three-plane map has
fibers of dimension 2 and the image has dimension 12.

#### The fiber read from the kernel plane

**Proved** (`A5-435`): the signs of the lower block satisfy `SIGNS[r][r ^ c] = -SIGNS[r][c]`, so
`M(z) p = -M(p) z`. For a basis `p1, p2` of the kernel plane `P = ker A(z, w)` the `z`-part of the fiber is

`L_z = {z in ker M(p1) n ker M(p2): z orthogonal to the conjugate kernel plane P'}`,

the `w`-part is its mirror image, and `dim L = 2 dim L_z` at a real point. Every `z` of `L_z` has `P` inside
`ker M(z)`. `kernel_form` computes modulo 32029 the nullity of `M(p)` at a general `p` of `P` (3 at a general
point; a higher value makes `p` a higher zero divisor), the dimension of `ker M(p1) n ker M(p2)` before and after
the cut by `P'`, and the nullities of `M(k)` on a net of 342 vectors `k` of the three-plane `ker M(z)`, which
lie on 145 points of its projective plane. For each nullity the record holds the count of net vectors and
points, the dimension of their span (2 for points of one projective line) and that dimension with `P` added
(unchanged when the line is `P`).

**Computed, modulo 32029,** at the 3,687 nullity-4 grid points:

| Stratum | `dim L` | Nullity on `P` | `ker M(p1) n ker M(p2)` | After the cut by `P'` | Grid points |
|---|---:|---:|---:|---:|---:|
| `V(Q)` minus `V(G)` | 2 | 3 | 1 | 1 | 2,096 |
| `V(G)` minus `V(Q)` | 2 | 3 | 1 | 1 | 1,041 |
| `V(G)` minus `V(Q)` | 2 | 7 | 1 | 1 | 1 |
| `V(G)` minus `V(Q)` | 2 | 7 | 3 | 1 | 8 |
| `V(G)` minus `V(Q)` | 6 | 7 | 3 | 3 | 61 |
| `V(G)` minus `V(Q)` | 12 | 9 | 6 | 6 | 92 |
| `V(Q) n V(G)` | 2 | 3 | 3 | 1 | 384 |
| `V(Q) n V(G)` | 6 | 7 | 5 | 3 | 4 |

`dim L` is twice the last dimension in every row. The third column is the nullity at one probe vector
`p1 + 7 p2` of the plane, modulo the prime. At the 9 points of rows 3 and 4 the nullity of `M(p)` is recomputed
over `Q(i)` at six pairwise independent vectors of the kernel plane and at the probe vector. It is 7 at all
seven at the 8 points of row 4; rank at most 8 is the vanishing of forms of degree
5 on the plane, so every vector of the plane has nullity at least 7 there. Row 4 refutes "`dim L > 2` exactly
where the kernel plane consists of higher zero divisors" (`A5-436`), which holds at all 66 exact fixtures: the
common kernel has dimension 3 and the conjugate plane cuts it to the line of `z`. At the point of row 3,
`e_1 + 2 e_3 + 2 e_8 + 2 e_9 + 2 e_13 - e_14`, the exact nullity is 3 at the six vectors and 7 at the probe
vector: the plane meets the higher zero divisors of `ker M(z)` in the single point that the probe hits, so the
nullity at a general vector of that plane is 3. A large fiber occurs only on planes where the probe has nullity
7 or 9 modulo the prime.

At the 29 exact fixtures with `dim L` of 6 or 12 the 16 net points of nullity 7 or 9 span the real kernel plane,
inside a three-plane where the other net vectors have nullity 3 (`A5-437`). Rank at most `15 - n` of the skew
`M(k)` is the vanishing of Pfaffians of degree `(17 - n) / 2`, so 16 collinear points put the whole line in the
locus of nullity at least `n` modulo the prime: the real kernel plane is a line of higher zero divisors. Four
fixtures of `V(G)` minus `V(Q)` with `dim L = 2` carry a line of nullity 9 that differs from the real kernel
plane: 16 collinear net points at two fixtures and 8 at the other two, against degree 4. At the 12 fixtures of
`V(Q)` minus `V(G)` the net holds no such line: 7 fixtures have no higher zero divisor on the net, 4 have one net
point of nullity 5 or 7, which lies in the real kernel plane, and one has two net points of nullity 5, at least
one of them off that plane.

469 real points of `V(Q)` minus `V(G)` with Gaussian-integer split coordinates, where `w'` is the conjugate of
`z'` and independent of it, have `dim L = 2`, nullity 3 on the kernel plane and common kernel the line of `z`
(`A5-438`). They are the second intersections with the quadric `V(Q)` of the lines from its 12 exact fixtures
along 40 Gaussian directions each; 11 of the 480 pairs are discarded: 2 directions are real, 8 are
tangent to the quadric and return the fixture, and one line lies in `V(Q)` modulo the prime. At 25 sampled points `z0` of each stratum,
every one of 40 general planes `P` of `ker M(z0)` off `z0` has `{z: P in ker M(z)}` of dimension 1 on the two
hypersurface strata and 3 on `V(Q) n V(G)`.

#### Higher zero divisors of the kernel three-plane

`kernel_three_plane_zero_divisors.py` and its record `kernel-three-plane-zero-divisors-result.json` replace the
finite net by equations for the higher zero divisors inside `K = ker M(z)` at a nullity-4 point `z`.

**Proved** (`A5-440`): `K` lies in the hypersurface of `z`. For `k` in `K`, `M(k) z = -M(z) k = 0` and
`M(k) k = 0`, so `M(k)` has nullity at least 3 and every maximal Pfaffian `Q G k_j` vanishes at `k`; `Q G` is
zero on the linear space `K`, and the factor that is nonzero at `z` is excluded.

On `V(G)` minus `V(Q)` (`A5-441`) the quadric `Q` restricted to `K` is a nonzero multiple of the square of a
linear form. Its zero line, the polar line `l_z = K n ker dQ_z`, consists of higher zero divisors:

| Points | `P = l_z` | Nullity on `l_z` | `dim L` | Count |
|---|---|---:|---:|---:|
| 52 fixtures, exact over `Q(i)` | no | 7 | 2 | 2 |
| | no | 9 | 2 | 21 |
| | yes | 7 | 6 | 13 |
| | yes | 9 | 12 | 16 |
| 1,203 grid points, modulo 32029 | no | 7 | 2 | 364 |
| | yes | 7 | 2 | 8 |
| | yes | 7 | 6 | 61 |
| | no | 9 | 2 | 678 |
| | yes | 9 | 12 | 92 |

At the fixtures the rank of `M(k)` is 8 or 6 at six pairwise independent vectors of the exact line, which
decides the whole line (Pfaffians of degree 5 and 4), and 12 at a vector off it; modulo 32029 the 91 principal
12 x 12 Pfaffians of `M(k)` span exactly the multiples of the square of `Q` restricted to `K`, so at the fixtures
the higher zero divisors of `K` are exactly the line. Every point of the stratum
that was tested carries the line, of either orbit rank; the fiber is large only where the real kernel plane `P`
is that line, and the 8 grid points with `P = l_z` and `dim L = 2` are the points of `A5-436`. A kernel plane
other than `l_z` meets it in one point of the projective plane of `K`, the single higher zero divisor that the
probe vector hit at the ninth point of `A5-436`.

On `V(Q)` minus `V(G)` (`A5-442`) the locus is a curve. At the 12 fixtures the 91 principal 12 x 12 Pfaffians of
`M(k)` restricted to a coordinate hyperplane, sextic forms on `K`, span exactly the multiples of the plane
quartic `G` restricted to `K`. The quartic has a singular scheme of length 3 and contains no line over the
algebraic closure of GF(32029): a quartic `L C` has the length-3 scheme `V(L, C)` inside its singular scheme on
the line `L = 0`, and the certificate shows that no line meets the singular scheme in length 3 or more. A line of
higher zero divisors over `Q(i)` would reduce to one modulo the prime, so the fixtures have none in
characteristic 0; the identification with the quartic and the length of its singular scheme are statements
modulo 32029. At 40 points of the stratum with sha256 coordinates the singular scheme has length 3 and the
quartic has no line. On the grid the quartic is nonzero and free of lines at all 2,096 points; its singular scheme
has length 3 at 2,064 points and length 5 at 32 points of one slice, `e_1 + e_2 + 2 e_3 + e_8 + v`.

These results refute the finiteness clause of `A5-439`: the higher zero divisors of `K` on `V(Q)` minus `V(G)`
are a curve at the fixtures. Its clause that confines the line on `V(G)` minus `V(Q)` to a proper closed subset
of the orbit-rank-16 points is contradicted by every tested point, including 40 points of the stratum with
sha256 coordinates (Gram rank 1, nullity 7 on the polar line, 3 off it); finitely many points do not refute it,
and `A5-444` stated the corrected form, which `A5-534` proves. The net of `A5-437` met the quartic at its few points of small height and saw the polar
line only where it is a line of the net.

##### Orbit normal forms decide the kernel-plane hypotheses

`nullity4_orbit_normal_forms.py` (record `nullity4-orbit-normal-forms-result.json`) reduces both strata to one
normal form (`A5-530`). `Delta` is nonzero on `V(Q)` minus `V(G)` and on `V(G)` minus `V(Q)`, so the plane of
`u` and `v` is nondegenerate, and `G_2(C)`, the rotation of `(u, v)` by 120 degrees and the scaling carry every
point to `z = (e_1; mu; v_1 e_1 + rho e_2)` with `rho` nonzero, in the imaginary part of the octonion subalgebra
`O'` on the units 0, 1, 2, 3, 8, 9, 10, 11. For `t` in those seven coordinates `M(t)` is the direct sum of a
7 x 7 block and an 8 x 8 block whose Pfaffian is `G(t)`, and the `SL_2` that fixes `O'` acts on `K(z)`.

**Proved in characteristic 0 on `V(Q)` minus `V(G)`.** `K(z)` lies in `O'` and is the set of
`k(c0, s, t) = (x; r; y)`, `x = (c0, -t, s)`, `r = mu c0 + rho s`,
`y = (c0 v_1 - rho t, c0 rho - mu s + v_1 t, -mu t - v_1 s)`, with product `M(k) k' = 2 (s t' - s' t) z`. The
kernel quartic is `4 (n (n + r^2) + q^2)`, `n = c0^2 + s^2 + t^2`, `q = v_1 (c0^2 - s^2 - t^2) - 2 rho c0 t`.

- `A5-531`: the higher zero divisors of `K(z)` are exactly the zero set of the quartic at every point, and the
  quartic contains no line. On a line `n (n + r^2) = -q^2` as binary quartics, which leaves the line `r = 0` and
  the two tangents of the conic `n = 0` at its points on `r = 0`; the first fails at the mixed monomial of `q`
  (coefficient `-2 rho^2`), the second at the coefficient `2 rho^2 (v_1 - eps)`, `eps^2 = 1 + v_1^2`.
- `A5-532`: a plane of `K(z)` off `z` has common kernel `C z`, because the Heisenberg product `M(p1) p2` is a
  nonzero multiple of `z` and of every general point of the common kernel. So `dim L = 2` at every real point,
  and the real Gauss map is an injective immersion of the projectivized real points of the stratum: the
  derivative of the kernel plane of a constant-rank family vanishes in a direction `d` exactly when `A(d) P = 0`,
  so the kernel of the differential is `L`.
- `A5-533`: the quartic is -4 times the squared length of `x cross y`, singular at the base points of that net
  of conics, which are the roots of `chi = lambda^3 + v_1 lambda^2 - (1 + 2 v_1^2 + 2 rho^2) lambda + v_1`. The
  points with singular scheme longer than 3 form a proper closed subset, and a quartic of length 3 that
  contains no line is irreducible.

Modulo 32029 the singular scheme has length 3 at 68 normal-form points off the discriminant of `chi` and length
4 at 5 points on it. The 32 grid points of length 5 lie at the triple root `v_1 = 0`, `2 rho^2 + 1 = 0`
(`u.v = 0` and `u.u + 2 v.v = 0`).

**Proved in characteristic 0 on `V(G)` minus `V(Q)`.** At a rank-12 normal-form point `K(z) = C z + l_z`, with
`l_z` the kernel of the 8 x 8 block, an irreducible `SL_2`-module, and `Q` on `K(z)` is `Q(z) s^2`.

- `A5-534`: the higher zero divisors of `K(z)` are exactly the polar line `l_z`. They form a closed
  `SL_2`-stable set that misses `z`, and the three orbits are the point of `z`, the line and their complement.
- `A5-535`: a plane of `K(z)` off `z` other than `l_z` has common kernel `C z`, so at a real point `dim L > 2`
  only where the kernel plane is `l_z`. A second vector of the common kernel would make the 8 x 8 block of `M(h)`,
  `h = M(z) grad G(z)`, kill `l_z`; three Groebner bases equal to (1) show that this happens only at the
  rank-10 point `(v_1, mu, rho) = (0, 0, sigma)`. The certificate rejects `h = z`.
- `A5-536`: at a real rank-12 point whose `u` and `v` lie in one quaternion subalgebra, the kernel plane is
  `l_z` and `dim L` is at least 6. The 29 fixtures in that position have `dim L` of 6 or 12, the other 23 have
  `dim L = 2`, and at all 66 fixtures the orbit rank is 13 exactly in that position.

| Points, modulo 32029 | `mu = 0` | Rank of `M` on `l_z` | `dim C(l_z)` | Of it in `O'` | `dim C(P)`, `P` other than `l_z` | Count |
|---|---|---:|---:|---:|---:|---:|
| normal form | no | 8 | 3 | 3 | 1 | 60 |
| normal form | yes | 6 | 6 | 4 | 1 | 60 |
| fixtures | no | 8 | 3 | | 1 | 15 |
| fixtures | yes | 6 | 6 | | 1 | 37 |

`A5-441` stated these facts at the fixtures and the grid and is superseded: `A5-530`, `A5-534` and `A5-535` exclude
its three falsifiers at every point, and its clause "nullity at least 7 on `l_z`" continues as `A5-537`. `A5-442`
is superseded the same way: `A5-531` proves its zero-set and no-line statements at every point, and its modular
lengths of the singular scheme continue in `A5-533` and `A5-540`.

These rows replace `A5-433`, `A5-441`, `A5-442`, `A5-443`, `A5-444` and `A5-445`. The five hypotheses that remained open, with their state:

- `A5-537`, proved (`nullity4_polar_line_module.py`, record `nullity4-polar-line-module-result.json`): the rank
  of `M` on `l_z` minus 0 is 8 where `mu` is nonzero and 6 where `mu = 0`, and `C(l_z)` is three trivial
  `SL_2`-summands inside `O'`, or four trivial summands inside `O'` and one standard summand outside it. The three
  derivations that fix `e_1`, `e_2` make the eight outer coordinates a module of the quaternions over `C`, so
  `rank M(p) = 2 rank B(p)` for the 7 x 8 block `B` and the rank is constant on `l_z` minus 0; unit ideals in the
  ring of `x = (rho - sigma, v_1, mu)` modulo the cone `x.x = 0` fix `rank B` at 4 off `mu = 0` and 3 on it; `nullity4_polar_line_stack.sing` replays the rank 8 of the stack
  of `B` and `B D_1` off `mu = 0` as a row module that spans the free module, a second route to that unit ideal.
  Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_polar_line_module.py --check` (about 10 s).
- `A5-538`, superseded by `A5-550` (proved) and `A5-551` (open), both from `nullity4_real_polar_line.py` (record
  `nullity4-real-polar-line-result.json`). For every nonzero `p`, `ker A(p, conjugate(p))` has complex dimension
  `nullity M(p) - 1`, 6 and 8 on `l_z`; the real nullities 12 and 16 are twice these (`A5-554`, proved:
  `real_nullity_bordered_matrix.py` shows that the bordered matrix of these records equals the one on which `A5-364`
  proves the transport of left multiplication, exactly, and the 66 fixtures agree). Where `mu = 0`, `l_z` lies in `E_eps = {(a; 0; eps i a)}` and
  `C(l_z)` in `C z + E_(-eps)`; these subspaces are Hermitian-orthogonal and preserved by the group, so `P = l_z`
  gives `dim L = 12`, and 8 and 10 never occur. Where `mu` is nonzero, `dim L` is 2, 4 or 6. The value 4 occurs
  (`A5-551`, certified): `nullity4_real_polar_fiber_four.py` moves the normal-form point `(s, v_1, mu) = (4, 3, 5i)`
  by `Theta = exp(i sum xi_k D_k)` and encloses, in an arb Krawczyk box of radius `2^-24` on six coordinates, one
  zero of the system `z_0^* Pi l = 0`, `det N = 0` with `Pi = Theta^* Theta`; there the kernel plane is `l_z` and
  the pairing has rank 1. The ranks at the normal form are exact and constant on the orbit; the point is a
  certified existence with no algebraic description (`A5-562` gives an algebraic point in another chart). The Krawczyk test gives the same containment,
  contraction and pairing bound at 131 and 400 bits. Two exact searches for an algebraic point end in closed forms
  (`A5-561`, proved as a bounded negative, `nullity4_real_polar_rational_charts.py`, record
  `nullity4-real-polar-rational-charts-result.json`): the stabilizers of `z_0`, of `l` and of `C(l)` in
  `g_2(C)` are one three-dimensional subalgebra that keeps the pairing zero, the 24 root subgroups
  `exp(t (D_a +- i D_b))` that keep the incidence keep it zero as well, the other 76 meet the incidence at the
  identity alone, and on the two four-parameter families of
  Hermitian elements of the subgroups `SO(4, C)` of the pairs `(4, 7)` and `(5, 6)` the pairing has rank 0 or
  2. Replay:
  `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_rational_charts.py --check` (about 6 s).
- `A5-562`, certified (`nullity4_real_polar_sl3_chart.py`, record `nullity4-real-polar-sl3-chart-result.json`): a
  real algebraic point with `dim L = 4` in a rational chart. The Hermitian elements
  `g = e_4 e_4^T + (W A W^* + conj(W) A^(-T) conj(W)^*) / 2` of the subgroup `SL(3, C)` that fixes `e_4`, with
  `A = L D L^*`, `D = diag(1, d_2, 1 / d_2)` and `L` unit lower triangular with entries `x_21`, `i y_31`, `-i / 2`,
  are rational in three real parameters, and `M(G t) = G M(t) G^T` holds as an identity. At the normal form of
  `A5-551` the incidence `F = z_0^* g^2 l` and the minor of `R` on the rows `k_1`, `k_2` are real, with numerators
  `p_0`, `p_1`, `p_2` in `Z[d_2, x_21, y_31]` of degrees 8, 8 and 16. An arb Krawczyk box of radius `2^-30` holds
  exactly one real zero of them, at 200 and at 400 bits, and an entry of `R` is bounded away from zero on the box,
  so the pairing has rank 1 there. The zero is isolated with an invertible Jacobian, so its coordinates are
  algebraic. `computed:` msolve 0.9.4 gives a zero-dimensional ideal with a quotient of dimension 164 (Singular
  4.4.1 agrees) and an eliminating polynomial of degree 140 for `t = 1 / d_2 + 2 x_21 + 3 y_31 + 4 d_2`, retained
  in `nullity4-real-polar-sl3-chart-eliminant.json`; the record factors it (degrees 2, 2, 2, 4, 6, 36, 88) and
  shows that the factor of degree 88 is the only one whose ball at the point holds zero. The degree 88 rests on
  the eliminant, which the record does not recompute. This settles the hypothesis that `A5-551` carried; the
  chart is the lead of the red-team review of pull request 929. Replay:
  `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_sl3_chart.py --check` (about 12 s);
  `--msolve-input` prints the input of the elimination.
- `A5-539`, proved (same producer): at every point with `Delta` nonzero the orbit rank is 16 minus the dimension
  of the stabilizer of the real span of `u` and `v` in the compact `g_2`, which is 3 in quaternion position and 0
  otherwise, so the orbit rank is 13 exactly in quaternion position and 16 elsewhere. Replay:
  `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_line.py --check` (about 4 s).
- `A5-540`, proved (`nullity4_quartic_discriminant.py` with two Singular scripts, record
  `nullity4-quartic-discriminant-result.json`): the singular scheme has length `3 + deg gcd(chi, chi')` at every
  point, with an `A_{2e-1}` point at the base point of a root of multiplicity `e`, and the quartic is absolutely
  irreducible. The partials of `F = -4 w.w`, `w = x cross y`, lie in the base ideal `I_B`; unit ideals over Q
  keep the singular points on `B` and off the conic `n = 0`, so `F` is a unit times `f' g'` with
  `(f', g') = I_B` there: two smooth branches with contact `e`. The length is `6 - N` for `N` distinct roots,
  while two smooth conics would give `8 - N`. Both triple branches, `v_1 = 0`, `2 rho^2 + 1 = 0` (the 32 grid
  points) and `v_1^2 = 27`, `rho^2 = -32`, have length 5. Replay, with Singular 4.4:
  `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_quartic_discriminant.py --check` (about 3 s).
- `A5-541`, refuted by `A5-552` (proved, `nullity4_qg_intersection.py`, record `nullity4-qg-intersection-result.json`).
  On `V(Q) n V(G)` the product on `K` vanishes, so `K` lies in `C(P)` and `dim L = 2 (dim C(P) - 2)`. A point with
  `u.u` nonzero is `z(s) = (1 + s^2) (e_1; beta; lambda e_1 + i e_2 + e_3 - i e_4 + e_5)` on the conic
  `beta^2 + lambda^2 = -1`; the vectors of `K` of nullity above 3 form three lines, whose planes `P_x`, `P_y`, `P_z`
  have `dim C(P)` of 5, 4, 4. Exact real points over Q(i) at `s = 0` and `s = 2` have these kernel planes, so
  `dim L` is 6, 4 and 4 there: the value 4 occurs, and `fiber_dimension` of
  `nullity4_gauss_image.py`, the routine of the grid classes, returns the same 6, 4, 4 there. At a real point with kernel plane `P_x` and `s^2` other
  than 1 the vectors of `P` have nullity 7. No other value occurs, and every point with `dim L = 6` has plane nullity 7 (`A5-555` to `A5-558`, proved,
  `nullity4_qg_orbit_types.py`, which succeed `A5-553`): at `s = +-1` the plane `P_x` lies in the
  `G_2(C)`-invariant subspace `E_eps` and its Hermitian complement in `K` lies in the cone `J`, so no real point
  has kernel plane `P_x` and 10 does not occur; the point `(beta, lambda) = (i, 0)` has the dimensions 5, 4, 4 in
  the chart `1 / s`; exact maximal minors of the plane stacks show that a plane with `dim C(P) = 5` is `P_x` with
  `s^2` other than 1; the points with `u.u = 0` are rotation images of four chart points; the totally isotropic
  pairs hold no nullity-4 point (rank at most 10 by `A5-359`, 8 on the special planes `u x v = 0` by `A5-360`). Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_intersection.py
  --check` (about 45 s).
- `A5-559` and `A5-560`, proved (`nullity4_qg_plane_incidence.py`, record
  `nullity4-qg-plane-incidence-result.json`); they settle the hypothesis that `A5-555` carried and the fiberwise and local parts of the one that `A5-558`
  carried. The stratum is the disjoint union of the sets `K` minus `J`, and in each the real points with kernel
  plane `P_j` are one complex line minus its points of `J`, so the points with `dim L = 6` and those with
  `dim L = 4` have real codimension 4 inside every fiber; at the six exact witnesses the real Jacobian of the
  incidence map has rank 4 on a tangent space of dimension 13, so they form a submanifold of codimension 4 there.
  `hypothesis:` both sets have real dimension 22 in the stratum; the missing lemma is that the kernels form a
  family of real dimension 20 over which the exceptional lines are line bundles (`A5-558`). At `s = +-1` the vector `q` lies in `P_y` and
  `P_z` and is Hermitian-orthogonal to `g P_x` for every `g` of `G_2(C)`, so the Hermitian complement of
  `g P_y` or `g P_z` in `g K` lies in `g P_x`, inside the cone: neither plane is the kernel plane of a real
  point, and the type holds `dim L = 2` alone. The exact check runs at the base frame and at a unipotent element
  that is not unitary. Replay:
  `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_plane_incidence.py --check` (about 3 s).

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_orbit_normal_forms.py --check` (about 45 s).
The [review record](../../archive/reviews/pr904/README.md) holds the brief, both reviewer reports and the
reconciliation of their findings; the [review record of the residual rows](../../archive/reviews/pr907/README.md)
holds those of the rows from `A5-537` on, and the
[review record of the open rows](../../archive/reviews/pr915/README.md) those of `A5-551` and `A5-554` to `A5-558`,
and the [review record of the open hypotheses](../../archive/reviews/pr929/README.md) those of `A5-559` to `A5-561`.

The count of quadrics on each image (`A5-434`, superseded by `A5-460`) is tested and taken apart in the next
subsection. `hypothesis:` the complexified ranks of the first table hold in characteristic 0 and at every point of
each stratum outside a proper closed subset.

#### Stratification of the real nullity-4 points by the fiber of the Gauss maps

One table for the three nullity-4 strata. A real point is a doubly pure `y` with complex coordinates `z`; `P` is
its kernel plane `ker A(z, conjugate(z))`, `C(P)` the common kernel of `M` on `P`, and `dim L` the real dimension
of the fiber of the pair of Gauss maps (`A5-430`, `A5-435`). The fifth column is the real nullity of left
multiplication by a vector `p` of `P`, which is `2 (nullity M(p) - 1)` (`A5-554`). Each cell is `proved` unless
it carries another mark: `certified` (interval certificate), `measured` (exact at sampled points), `hypothesis` or
`open` (no row decides it).

| Stratum | Kernel plane `P` | `dim C(P)` | `dim L` | Real nullity on `P` | Rows |
|---|---|---|---|---|---|
| `V(Q)` minus `V(G)` | any plane | 1 | 2 | 4 at 469 sampled points (measured) | `A5-532`, `A5-438` |
| `V(G)` minus `V(Q)` | not the polar line `l_z` | 1 | 2 | open | `A5-535` |
| `V(G)` minus `V(Q)`, `mu` nonzero | `l_z`, pairing rank 2 | 3 | 2 (occurs next to the point of `A5-551`, whose zero is transverse: certified) | 12 | `A5-550`, `A5-537`, `A5-551` |
| `V(G)` minus `V(Q)`, `mu` nonzero | `l_z`, pairing rank 1 | 3 | 4 (certified; an algebraic point of degree 88 in a rational chart, degree computed) | 12 | `A5-551`, `A5-562`, `A5-561` |
| `V(G)` minus `V(Q)`, `mu` nonzero | `l_z`, pairing rank 0 | 3 | 6 | 12 | `A5-550`, `A5-536` |
| `V(G)` minus `V(Q)`, `mu = 0` | `l_z` | 6 | 12 | 16 | `A5-550`, `A5-537` |
| `V(Q) n V(G)` | a plane of `K` outside the cone `J` | 3 | 2 | 4 at a vector outside `J` | `A5-552` |
| `V(Q) n V(G)`, `s^2` other than 1 | `P_x` | 5 | 6 | 12 | `A5-552`, `A5-557` |
| `V(Q) n V(G)`, off the roots of `s^4 + 14 s^2 + 1` | `P_y` or `P_z` | 4 | 4 | above 4; value open | `A5-552`, `A5-556`, `A5-557` |
| `V(Q) n V(G)`, roots of `s^4 + 14 s^2 + 1` | `P_y = P_x` or `P_z = P_x` | 5 | 6 | 12 | `A5-557`, `A5-558` |
| `V(Q) n V(G)`, `s = +-1` | `P_x`, `P_y`, `P_z` (`dim C` = 7, 4, 4) are the kernel plane of no real point | 3 | 2 alone | 4 at a vector outside `J` | `A5-555`, `A5-560` |

The values 8 and 10 of `dim L` occur on no stratum (`A5-550`, `A5-555`). On `V(Q) n V(G)` the real points with
`dim L = 6` and those with `dim L = 4` form in each fiber `K` minus `J` a punctured complex line or nothing, and a
submanifold of real codimension 4 near six exact witnesses (`A5-559`); that each set has real dimension 22 in the
whole stratum is a hypothesis (`A5-558`, with its missing lemma on the image of `z -> K(z)`). The dimension of the
`dim L = 4` and `dim L = 6` loci on `V(G)` minus `V(Q)` is open.

#### The quadrics of the Gauss images

`gauss_image_quadrics.py` (record `gauss-image-quadrics-result.json`) works modulo 32029 at 760 points `z` of each
stratum, in the frame of the kernel vectors, where `Q` is the sum of the squares of the 15 coordinates, and
exactly over `Q(i)` at the 66 fixtures. `M(t) v` is the imaginary part of the product `t v` of two imaginary
elements of the 16-dimensional Cayley-Dickson algebra, so `K(z) = ker M(z)` is the space of imaginary elements that
commute with `z`.

**Proved** (`A5-459`): the kernel plane at `(z, w)` is `K(z) n w-perp` and `w` is free, so the image is the union
of the projective planes `P(Lambda^2 K(z))`, each linear in the Plucker space. A quadric vanishes on the image
exactly when its polar form vanishes on `S^2(Lambda^2 K(z))` for every `z`: the quadrics beyond the 1,365 Plucker
quadrics are the annihilator of the span of these six-dimensional spaces in a space of dimension 4,200.

Sampled (`A5-460`, survives): the six products of a basis of `Lambda^2 K(z)` at the 760 points have the ranks of
the first table, whose planes are another draw of the same sampler under another label.

| stratum | rank | saturates at | first `rank` planes of the first draw | both draws | with the exact fixtures | quadrics beyond Plucker |
|---|---|---|---|---|---|---|
| `V(Q)` minus `V(G)` | 3,887 | 648 three-planes | 3,887 | 3,887 | 3,887 (12 fixtures) | 313 |
| `V(G)` minus `V(Q)` | 4,022 | 671 three-planes | 4,022 | 4,022 | 4,022 (52 fixtures) | 178 |
| `V(Q) n V(G)` | 2,625 | 438 three-planes | 2,625 | 2,625 | 2,625 (2 fixtures) | 1,575 |

The rank grows by six per three-plane until it saturates, and the fixtures, which no sampler drew, add nothing.
Each rank is a lower bound for the dimension of the degree-2 part of the coordinate ring over `F_32029`; the
count of quadrics stays an upper bound, since the vanishing of a quadric on the whole image is an identity of
degree 12 in `z` that the record does not prove, and the record holds no lift of the points to characteristic 0.

Sampled and exact at the fixtures (`A5-461`, survives): the product `k, k' -> M(k) k'` on `K(z)`, skew because
`M(u) v = -M(v) u` and equal to half the commutator, has one type per stratum at all 760 points and at all 66
fixtures.

| stratum | products `M(k) k'` | double products | type of `K(z)` |
|---|---|---|---|
| `V(Q)` minus `V(G)` | multiples of `z` | zero | Heisenberg algebra with center `z` |
| `V(G)` minus `V(Q)` | one line outside `K(z)`, not the line of `z` | nonzero | not closed |
| `V(Q) n V(G)` | zero | zero | abelian |

Write `mu(u ^ v) = M(u) v`, a linear map from `Lambda^2 V` to `V` of rank 15, and `Pi(p)` for the skew matrix of
a bivector `p`. Two identities govern the sandwiches `Pi(p) D Pi(p)` of a symmetric form `D`:

- **Proved** (`A5-467`): a form that vanishes on a three-plane `K` gives `Pi(p) D Pi(p) = 0` on `Lambda^2 K`,
  because every term of the expansion carries a value of `D` on `K`. The norm `N` vanishes on `K(z)` at every
  nullity-4 point of `V(Q)` minus `V(G)` (`A5-440`), so the 120 entries of `Pi(p) N Pi(p)` are quadrics on that
  image, independent modulo the Plucker quadrics (rank 1,485 of the two families).
- **Proved** (`A5-470`): the combination of the entries with a symmetric `c` is minus the mixed discriminant of
  `c` and `D` on the plane of `p`. Where `D` has rank one on `K`, `D = l^2`, the combination vanishes on
  `Lambda^2 K` exactly when `c` vanishes on the plane `K n ker l` (characteristic other than 2). A form that
  vanishes on no `K(z)` still yields quadrics on the image where its restrictions are degenerate.

Over `F_32029` at most one symmetric form vanishes on every `K(z)` of a stratum inside `V(Q)`, the norm, and none
on `V(G)` minus `V(Q)` (`A5-468`, proved from the spans of `S^2 K(z)`); the norm does vanish at the sampled points
and the two fixtures of `V(Q) n V(G)`, and at every nullity-4 point of that stratum in characteristic 0 (`A5-489`).

The doubling forms are the three diagonal forms `N1 = t_1^2 + ... + t_7^2`, `N2 = t_8^2`,
`N3 = t_9^2 + ... + t_15^2` of the decomposition `O + R e_8 + O e_8` of the imaginary units as the double of the
octonions. Their ranks on `K(z)` separate the two hypersurfaces (`A5-469`, survives):

| stratum | rank of `N`, `N1`, `N2`, `N3` on `K(z)`, 760 points | exact at the fixtures |
|---|---|---|
| `V(Q)` minus `V(G)` | 0, 3, 1, 3 | 0, 3, 1, 3 at 12 |
| `V(G)` minus `V(Q)` | 1, 1, 1, 1 | 1, 1, and 0 or 1 for `N2` and `N3`, at 52 |
| `V(Q) n V(G)` | 0, 1, 1, 1 | 0, 1, 0, 1 at 2 |

The table lists, per family of quadrics, how many independent ones it adds to the families before it.

| family | written | `V(Q)` minus `V(G)` | `V(G)` minus `V(Q)` | `V(Q) n V(G)` |
|---|---|---|---|---|
| Plucker quadrics | 1,365 | 1,365 | 1,365 | 1,365 |
| vanishing linear form times coordinate | 105 per form | no form | no form | 1,455 (15 forms) |
| coordinates of `p ^ mu(p)` | 455 | 98 | 3 | 0 |
| `mu(p)_a mu(p)_b` | 120 | 0 | 3 | 0 |
| `Pi(p) M(e_j) mu(p)` | 225 | 119 | 14 | 0 |
| entries of `Pi(p) M(e_j) Pi(p)` | 1,575 | 0 | 133 | 0 |
| entries of `Pi(p) N Pi(p)`, `N` the norm | 120 | 96 | no form | 96 |
| entries of `Pi(p) D Pi(p)`, `D` the three doubling forms | 360 | 0 | 25 | 24 |
| total | | 1,678 | 1,543 | 2,940 |
| quadrics on the sampled span | | 1,678 | 1,543 | 2,940 |
| outside the families | | 0 | 0 | 0 |

On `V(Q)` minus `V(G)` four families span every quadric of the sample (`A5-463`), and the Heisenberg product
explains the two middle ones: `mu(p) = omega(p) z` puts `p ^ mu(p)` in `Lambda^3 K(z)`, whose span over the
stratum has dimension 356 of 455, which leaves 99 linear forms; and `Pi(p) M(e_j) z = -Pi(p) M(z) e_j = 0`
because `p` lies in `Lambda^2 ker M(z)`. The Plucker quadrics with all entries of `Pi(p) M(e_j) mu(p)` and of
`Pi(p) N Pi(p)` already have rank 1,678 as whole families. On `V(Q) n V(G)` the 15 linear forms that cut the span
of the image down to dimension 90 are the coordinates of `mu` (`A5-464`). On the two strata inside `V(G)` the
families built from `mu`, the blocks and the norm leave 25 and 24 quadrics, and the doubling forms supply all of
them (`A5-469`): 57 and 152 combinations of the 360 entries vanish. The sign changes `e_k -> chi(k) e_k` of the
coordinates preserve `M`, `Q` and `G`, and the 25 and 24 lie 3 and 2 in the trivial character, one in each of
the characters 1 to 8 and two in each of the characters 9 to 15. A family built from an equation of `V(G)` was
the first reading of that split and is refuted by the doubling forms, which use none (`A5-466`).

**Proved in characteristic 0** (`A5-479`): at every nullity-4 point `z` of `V(Q)` the product of two kernel
vectors is a multiple of the point, `M(k) k'` in `C z`, and on `V(Q) n V(G)` it is zero. The entries of
`Pi(p) M(e_j) mu(p)` and of `Pi(p) N Pi(p)` therefore vanish identically on the image of `V(Q)` minus `V(G)`,
and their rank 1,678 with the Plucker quadrics, a rank of integer vectors, gives at least 313 quadrics beyond
Plucker in characteristic 0 (`A5-481`). The commutant of a null imaginary octonion has the same Heisenberg type
(test).

**Proved** (`A5-494`, every field): the tensor of the order-12 Pfaffians of `M(z)` has a polynomial formula, and at
rank 12 in odd characteristic it is the product on `K(z)`. For a triple `I` of indices
let `P_I(z)` be the Pfaffian of `M(z)` without the rows and columns of `I`, with the sign of the shuffle
`(I, complement)`, and let `tau(a ^ b ^ c) = Im(a b) (x) c + Im(b c) (x) a + Im(c a) (x) b`. The tensor
`T(z) = tau(sum_I P_I(z) e_I)` has entries of degree 6 in `z` with integer coefficients, and

`T(z) = -grad(Q G)(z) (x) z - Q(z) G(z) I` at every point `z`.

`P(z)` is the dual of the twelve-form `sum_J Pf(M_J) t_J`, the sixth divided power of the two-form of `M(z)`. Its
coordinates transform under congruence by an identity of integer polynomials, and the block normal form of an
alternating matrix of rank 12 makes it the product of twelve coordinates, so over every field `P(z)` at a rank-12
point is a nonzero multiple of the three-vector of `K(z)`, and there `T(z) = c M(k_1) k_2 (x) z` with `c` nonzero
for a basis `z, k_1, k_2` of `K(z)` (`A5-490`). On the zero-divisor variety `Q G = 0`, so the kernel commutator is the
gradient of its equation: `c M(k_1) k_2 = -grad(Q G)(z)`, which is `-2 G z` on `V(Q)` (`A5-486`) and
`-Q grad G` on `V(G)` (`A5-491`). The consequences:

- The product is nonzero at every nullity-4 point of `V(Q)` minus `V(G)`, the points with `N1(z) = 0` included,
  so `K(z)` is a Heisenberg algebra with center `C z` at each of them (`A5-487`, which closes the hypothesis
  `A5-480`), and in every odd characteristic at every rank-12 point (`A5-495`).
- The product is nonzero at every nullity-4 point of `V(G)` minus `V(Q)` (`A5-492`): the singular points of
  `V(G)` off `V(Q)` are the points with `t_8 = 0`, `N1 = N3` and `p = 0`, where rank `M(z)` is at most 10
  (`A5-493`). At nullity 4 the product vanishes exactly on `V(Q) n V(G)`. The rank bound and the nonvanishing
  hold in every odd characteristic (`A5-497`, `A5-498`, below).
- Every point of `V(Q)` with rank `M(z)` below 12 lies in `V(G)`, so every point of `V(Q)` minus `V(G)` has
  nullity exactly 4 (`A5-488`).
- `K(z)` is null at every nullity-4 point of `V(Q) n V(G)` as it is on `V(Q)` minus `V(G)`, by closure through
  the contraction of `P(z)` with itself (`A5-489`, which closes the sampled `A5-462`).

The proof has three steps. On `V(Q)` and on `V(G)` the identity `T = -grad(Q G) (x) z` is a polynomial identity
on an irreducible hypersurface: `T` is equivariant under `G2(C)`, the slices of the paragraph on the three proofs
below meet a dense set of orbits, and on the parametrizations `FQ`, `FG+` and `FG-` each entry of the difference
has bounded degree in each generator (6 in each of `A`, `B`, `C`; 6 in `m` and 12 in `u`) and is homogeneous, so
its exact vanishing on a 7 x 7 grid at `C = 1` and on two 7 x 13 grids decides it. The difference
`T + grad(Q G) (x) z` then vanishes on `V(Q G)`, has degree 6, and so equals `Q G` times a matrix of constants,
which two exact points off the variety give as `-I`. `kernel_product_pfaffian_tensor.py` holds the grids, three
exact points with `N1(z) = 0`, three singular points of `V(G)`, the two general points and the 66 fixtures.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_product_pfaffian_tensor.py --check` (exact
over `Q(i)`; 98.8 CPU seconds, 121 seconds of wall time and 84 MiB on two workers, measured with the host at
load average 28 from unrelated jobs; Python 3.14.9 with sympy 1.14.0).

**Proved in odd characteristic** (`A5-497`): at a singular point `z = (a, 0, b)` of `V(G)` off `V(Q)`, where
`N(a, b) = 0` and `N(a) = N(b) = nu` is nonzero, the kernel contains an explicit subspace of dimension 5. For an
octonion `y` let `x = [a, b, y]` be the associator; then `k(y) = (nu x, 0, -(b x) a)` lies in `K(z)`, and `z` with
the `k(y)` spans a space of dimension 5, so rank `M(z)` is at most 10. The octonion associator alternates,
vanishes on the quaternion subalgebra `H = span(1, a, b, a b)` and runs through its orthogonal complement, so the
two components of the product `z k(y)` cancel term by term. That subspace is the whole kernel (`A5-499`): a
sedenion `(c, d)` with `z (c, d) = 0` has `c = -a (conj(d) b) / nu`, and `d` satisfies
`nu d a = b ((b d) a)`, which on the associative `H` reads `2 nu d a = 0` and forces `d = 0`; the solutions `d`
therefore meet `H` in zero and span at most 4 dimensions, and `K(z)` is the line of `z` plus the imaginary
annihilators of `z`, so rank `M(z)` equals 10 and `z` with the `k(y)` spans `K(z)`, a basis when `y` runs
through a basis of the complement of `H`. The formula has integer coefficients and uses only the alternative law and the
norm, so it replaces the orbit argument of `A5-493` and settles the hypothesis `A5-496`. With `A5-495` the
product on `K(z)` is nonzero at every rank-12 point of `V(G)` minus `V(Q)` over every field of characteristic
other than 2 (`A5-498`). `singular_kernel_formula.py` checks the formula over the integers at 6,524 pairs
`(a, b)` with entries in `-1, 0, 1`, and the dimension 5 and rank 10 over `Q` at all of them and modulo 3, 5
and 7 at every pair whose norm stays nonzero modulo the prime: 924, 6,524 and 6,524 pairs, since the 5,600 pairs
of norm 3 leave the locus modulo 3.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/singular_kernel_formula.py --check` (integer
arithmetic; 50.8 CPU seconds, 34 seconds of wall time and 89 MiB on two workers with the host at load average 25
from unrelated jobs, Python 3.14.9 with sympy 1.14.0).

**Proved** (`A5-472`): for `z = (a, b)` and `k = (c, d)` in the doubling the commutator is
`([a, c] - (conj(d) b - conj(b) d), 2 (d a - b c))` over the integers, so in characteristic other than 2 `K(z)`
is cut out by `d a = b c` and `[a, c] = conj(d) b - conj(b) d`, and the multiplicative octonion norm gives
`N1(k, k') (N2 + N3)(z) = (N2 + N3)(k, k') N1(z)` on `K(z)` at every point.

**Proved in characteristic 0** (`A5-476`): at every nullity-4 point of `V(G)` the three doubling forms are
multiples of one square on `K(z)`, `Ni(z) Nj(k, k') = Ni(k, z) Nj(k', z)`. Where `N1(z)` is nonzero (`A5-477`),
`K(z) = C z + K0(z)` with `K0(z) = K(z) n ker N1(., z)`, `t_8` vanishes on `K0(z)`, and every vector of `K0(z)`
is a pair `(c, d')` of null imaginary octonions with product `c d' = 0`. The 25 symmetric forms these conditions
give, the 15 products `t_8 t_k`, the norms `N1` and `N3` and the 8 coordinates of `c d'`, therefore vanish on
`K0(z)`, and by `A5-470` each of their combinations `trace(c Pi(p) D Pi(p))` with a doubling form `D` vanishes
on `Lambda^2 K(z)` at every nullity-4 point of `V(G)` (`A5-483`).

Sampled (`A5-482`, survives): at the sampled points `t_8` is a nonzero multiple of `N1(., z)` on `K(z)`, and
the symmetric forms that vanish on every sampled `K0(z)` are exactly those 25. That the combinations of
`A5-483` are all of the 25 and 24 quadrics the other families leave is the sampled count of `A5-469`.

The hypothesis `N1(z)` nonzero is needed (`A5-478`): `V(G)` has nullity-4 points with `N1(z) = 0`, the identity
makes `N1(., z)` vanish on all of `K(z)` there, and at the exact point
`z = (0, 1, i, 0, 0, 0, 0, 2 i, -2, 0, -2, 0, 0, 0, 0)` the vector `z` of `K(z)` has `t_8 = 2 i`. Two earlier
forms of the statement are superseded: `A5-473` named the plane by `ker t_8`, which is all of `K(z)` at the 39
of the 54 exact fixtures with `z_8 = 0` (`A5-484`), and `A5-485` omitted the hypothesis.

The three proofs share one shape. `G2(C)` acts on the doubling by `(a, b) -> (g a, g b)` and preserves the
block, the kernel, the doubling forms, `Q` and `G`. Up to scale and that action, a point with `N1` and `Delta`
nonzero is `(e_1, beta + lambda e_1 + s e_2)` with the parameters on a quadric cone (`V(G)`) or a quadric
surface (`V(Q)`), because the orbit of `(e_1, e_2)` is dense in the orthonormal pairs (the derivations have
rank 11 on it). `kernel_plane_identities.py` checks each statement over the function field of that slice, and
the statements are closed conditions on the open set of nullity-4 points, so they hold at every one.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_plane_identities.py --check` (exact over
`Q(i)` and its function fields; 40 CPU seconds and 87 MiB on two workers, 38 seconds of wall time, Python 3.14.9
with sympy 1.14.0).

The record gives no equations of degree 3 or more, no generators of the image ideal, no transition functions and
no bundle class. Each ledger row names its falsifier.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/gauss_image_quadrics.py --check` (modulo 32029 and exact over Q(i) at the fixtures; 357 CPU seconds and 3.4 GiB on two workers under an 8 GiB memory scope, 3 minutes 14 seconds of wall time, same versions and host as the last replay).

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/kernel_three_plane_zero_divisors.py --check` (modulo 32029 and exact over Q(i) at the fixtures; 72 CPU seconds and 86 MiB on two workers, 53 seconds of wall time, same versions and host as the next replay).

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_gauss_image.py --check` (exact modulo 32029 and over Q(i); 326 CPU seconds and 1.2 GiB on two workers under an 8 GiB memory scope, 3 minutes 33 seconds of wall time, Python 3.14.9, python-flint 0.9.0, sympy 1.14.0, on the build host).

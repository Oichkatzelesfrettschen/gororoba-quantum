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
[section below](#the-nullity-4-gauss-image-is-a-plane-bundle-over-the-three-plane-map-z---ker-mz) measures the
image modulo 32029: its dimension, its linear span and its quadric equations on each stratum. The falsifier of a
classification stays a transition outside the claimed structure group or two exact points with the same proposed
moduli invariants and different Plucker images.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_kernel_gauss.py --check` (exact). The producer
uses the repository worker cap through `parallel.ordered_map`; the 66 fixtures are independent.


## The nullity-4 Gauss image is a plane bundle over the three-plane map z -> ker M(z)

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
is a given `P` and whose conjugate kernel plane is a given `P'` form an open subset of the linear space
`L = {(z, w): A(z, w) P = 0, A-bar(w, z) P' = 0}`. `L` contains the scalings of `z` and of `w`, and the
differential of the pair (Gauss map, conjugate Gauss map) has rank at most the tangent dimension minus `dim L`.

**At the 66 exact real fixtures, on the real locus `w' = z'`:** the differentials are computed modulo 32029,
where the rank of the pair is a lower bound for the rank over the reals of `z -> ker A(z, conjugate(z))` in
characteristic 0 (the pivot block is invertible modulo the prime and the tangent space keeps its dimension);
`dim L`, the orbit rank of the 18-dimensional kernel symmetry algebra and the nullity of the kernel vectors are
exact.

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
multiplication by the fixture: where the fiber is large, the kernel consists of zero divisors of a deeper
stratum.

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

Rows 7 and 9 are points of orbit rank 16, the maximum, with a large fiber; row 1 is orbit rank 13 with the
smallest fiber. At the 26 points of rows 6, 7 and 9 `dim L` and the kernel nullity are recomputed exactly over
`Q(i)` and agree.

**Inferred, modulo 32029:** on `V(Q)` minus `V(G)` and on `V(G)` minus `V(Q)` the three-planes `ker M(z)` form a
family of dimension 13, the projective dimension of the stratum, and the Gauss image is the bundle of planes in
those three-planes, of dimension 15 in the 26-dimensional `Gr(2, 15)`. On `V(Q) n V(G)` the three-plane map has
fibers of dimension 2 and the image has dimension 12.

`hypothesis` (`A5-433`, open): on `V(G)` minus `V(Q)` every real point of orbit rank 13 has `dim L` of 6 or 12
(139 grid points, 29 fixtures); on `V(Q)` minus `V(G)` every real point has `dim L = 2` (2,096 grid points, 12
fixtures); a real point with `dim L` of 6 or 12 has kernel vectors of nullity 12 or 16 (157 grid points, 29
fixtures), and row 6 shows that nullity 12 does not force a large fiber. The grid is one integer family; the
record holds no equations for the locus `dim L > 2` and no real point with non-real split coordinates.

`hypothesis` (`A5-434`, open): the sampled planes span the quadrics of each image, so that the images carry 313,
178 and 1,575 quadric equations beyond the Plucker quadrics, the first two images differ and the third lies in a
linear space of codimension 15; the record holds no certificate that the deterministic samples are general for
degree 2. `hypothesis:` the complexified ranks of the first table hold in characteristic 0 and at every point of
each stratum outside a proper closed subset.

The record gives no equations of degree 3 or more, no generators of the image ideal, no transition functions and
no bundle class. Each ledger row names its falsifier.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_gauss_image.py --check` (exact modulo 32029 and over Q(i); 1 minute 51 seconds of wall time, 165 CPU seconds and 3.2 GiB on two workers under an 8 GiB memory scope, Python 3.14.9, python-flint 0.9.0, sympy 1.14.0, on the build host).

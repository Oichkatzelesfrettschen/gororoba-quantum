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

`Out(g_2)` is trivial, so every component of the kernel symmetry group `K` meets the centralizer of `G_2` in `K`, and
`pi_0(K) = pi_0(Z_K(G_2))`. `probes/g2_commutant.py` computes the commutant of the fourteen octonion-derivation triples
in each slot of the transport triple exactly over Q: dimension 32 with a 4-dimensional invariant subspace in every
slot, so each slot decomposes as `4 R + 4 R^7` and the centralizer is `GL(4) x GL(4)` per slot
([log](probes/g2-commutant.log)). `Z_K(G_2)` is therefore the solution set of the group-level transport equations in
96 unknowns, with Lie algebra the four central directions.

## The component group is the visible `S_3 x Z_2`

[`centralizer_components.py`](centralizer_components.py) counts the components of the complex group `Z_C` of
`Z = Z_K(G_2)`; the record is [`centralizer-components-result.json`](centralizer-components-result.json). The
identity component of `Z` is the torus `T` of the four central directions. `J = L_(e_16)` and `R = R_(e_16)`
commute and square to `-1`, and their joint eigenspaces are four lines on the unit multiplicity space and two
planes on the vector multiplicity space, where only the sign pairs `(e, -e)` occur. **Inferred:** `Z` normalizes
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
pattern, and with one structure sign flipped the identity pattern has 1 point in place of 6.

**Inferred (`A5-379`):** two real points of `Z` in one component of `Z_C` differ by a real point of `T`, which is
connected, so the real group has at most 12 components. The visible subgroup `S_3 x Z_2` occupies 12 distinct
components ([kernel bundles](../a5-kernel-bundles/README.md#a-visible-s_3-x-z_2-occupies-twelve-components)), so
`pi_0(K) = pi_0(Z) = S_3 x Z_2`: every constant kernel-pencil symmetry is a product of an element of the identity
component and one of the twelve visible automorphisms. The deduction uses the reduction of the section above and
the Lie algebra of the kernel-bundle record.

A pattern with a point outside the two listed, a pattern of positive dimension, a gauge index other than 1, a
disconnected real torus, or a flipped sign that leaves the count falsifies the record. The replay takes 2 minutes
55 seconds of wall time, 287 CPU seconds and 84 MiB in the parent on two workers under an 8 GiB memory scope
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
explicit parameter charts, global transition functions, stabilizer jumps, or a bundle class. The next decisive
bounded computation is elimination of the moduli parameters against these 120 Plucker coordinates, one component
and one chart at a time; its falsifier is a transition outside the claimed structure group or two exact points with
the same proposed moduli invariants and different Plucker images.

Replay: `"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/nullity4_kernel_gauss.py --check` (exact). The producer
uses the repository worker cap through `parallel.ordered_map`; the 66 fixtures are independent.

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
96 unknowns, with Lie algebra the four central directions. Its component group is the next computation; a component
outside the visible `S_3 x Z_2` falsifies exhaustiveness.

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

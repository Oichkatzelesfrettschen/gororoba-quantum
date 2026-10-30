# Dimension-32 global topology: open work program

The claim `dimension32-global-topology` in `docs/state/research_state.json` asks for a classification of the
complete dimension-32 two-sided rank strata: components, smooth strata, closure incidences, attachments and integral
invariants. The roadmap table in [rank_locus_two_dimension_gap.md](../notes/rank_locus_two_dimension_gap.md#route-to-the-global-classification-roadmap-items-3-8)
fixes each item's first deliverable and admission rule. Components (item 3), regularity and links (item 4) and the
kernel bundles on `D_(5,16)`, `D_(5,12)` and `D_(5,8)` (item 5) are discharged. This program lists every open work
package that stands between those records and the claim, with its input, method, falsifier, substrate and the record
that will carry it. The plan record `dimension32-global-topology` in `docs/state/plans/` tracks status.

## Kernel-bundle residuals

`bundle_invariants.py` records three residuals outside its classification denominator
(`out_of_denominator_residuals` in [bundle-invariants-result.json](../evidence/a5-kernel-bundles/bundle-invariants-result.json)).
Each is independent of the exceptional-fiber computations and runs now.

**Real type of the quaternionic four-plane `xi_R` over `V_2(R^7)`.** Settled: `xi_R` is actually nontrivial, with
the exact producer check and the written argument in
[the residuals record](../evidence/a5-kernel-bundles-residuals/README.md) (gate core-756). The argument:

1. `G_2` acts transitively on orthonormal pairs `(a, b)` of imaginary octonions with stabilizer the `SU(2)` that fixes
   the quaternion subalgebra `H = span(1, a, b, ab)` pointwise, so `V_2(R^7) = G_2 / SU(2)` and
   `xi_R = G_2 x_SU(2) H^perp`.
2. That `SU(2)` acts on `H^perp` by one-sided quaternion multiplication, the standard representation; its image in
   `SO(4) = (S^3 x S^3) / {+-1}` is one `S^3` factor, so `pi_4(SU(2)) = Z/2` injects into
   `pi_4(SO(4)) = Z/2 + Z/2`.
3. Fix `a`. The fiber of `V_2(R^7) -> S^6` over `a` is the sphere `S^5 = SU(3) / SU(2)`, and `xi_R` restricted there
   is `SU(3) x_SU(2) C^2`, whose clutching class is the boundary map `pi_5(S^5) -> pi_4(SU(2))` of the fibration
   `SU(2) -> SU(3) -> S^5`. Since `pi_4(SU(3)) = 0`, that map is onto, so the clutching class is the generator.
4. By the injection in the second item, the restriction of `xi_R` to `S^5` is a nontrivial real bundle, so `xi_R` is
   actually nontrivial while stably trivial.

Falsifier: a global frame of `H^perp` over the fiber `S^5`, or a computation showing the stabilizer acts on
`H^perp` through both `S^3` factors. Deliverable: the argument written into the kernel-bundle README with a
producer check of the stabilizer's action on `H^perp` (commutant with left and right multiplications at sampled
points, exact over Q(i)), reviewed by an independent referee. Substrate: the host, seconds.

**Full component group of the kernel symmetry group.** The identity component and the visible `S_3 x Z_2` are
computed; exhaustiveness is not. Method: compute the normalizer of the constant-triple identity component inside
`O(32)` acting on the stratum, as the stabilizer of the kernel-transport ideal, by exact linear algebra on the Lie
algebra's normalizer followed by a finite enumeration of the component group modulo the identity component on each
nullity-12 and nullity-16 orbit. Falsifier: a component outside `S_3 x Z_2` that transports kernels at every
representative. Substrate: Kaggle CPU (the normalizer computation is a linear system in 1024 unknowns per
generator). Status: reduced to the `G_2` centralizer, `GL(4) x GL(4)` per slot, 96 unknowns ([record](../evidence/a5-kernel-bundles-residuals/README.md#full-component-group-reduction-to-the-g_2-centralizer)).

**Smaller reductions on nullity 12.** The canonical `U(6)` reduction is classified; nonconstant smaller reductions are
not. Method: test for global anticommuting complex structures in the exact Pfaffian atlas
(`transition_atlas.py` charts): solve for `J'` with `J'^2 = -1`, `J J' = -J' J`, commuting with the transition
cocycle, as a polynomial system per chart and glue. Falsifier: a global solution, which reduces the structure group
to `Sp(3)`. Substrate: the host or Kaggle CPU. Status: the topological reduction exists (trivial bundles) and the equivariant one is excluded on `B9` and `VB` by stabilizer weights; the gluing of pointwise structures over `V` and the aligned pair remain ([record](../evidence/a5-kernel-bundles-residuals/README.md#smaller-reductions-on-nullity-12)).

## Attachments (roadmap item 6)

The exceptional-fiber program ([a5-kernel-attachments-program.md](a5-kernel-attachments-program.md), findings in
[a5-exceptional-fiber-findings.md](../notes/topics/a5-exceptional-fiber-findings.md)) computes how partner spheres
specialize along the closure incidences of `D_(5,12)` and `D_(5,8)`. Open packages:

- reduced-support decomposition of the four exceptional fibers by projective charts (running on Kaggle CPU for Iso
  and W8 to N-minus);
- kernel-plane limits along the formal arcs of each reduced component, which turn a support into an attaching map;
- the X-minus arc certificate inside its `P^11`;
- the nullity-8 Grassmannian limit sets that the nullity-8 record leaves open
  ([a5-kernel-bundles-nullity8 README](../evidence/a5-kernel-bundles-nullity8/README.md)).

Admission: attaching maps on every admitted incidence, not a frontier matrix.

## Kernel bundles on the nullity-4 strata

The orbit count is done ([residuals record](../evidence/a5-kernel-bundles-residuals/README.md#nullity-4-strata-carry-continuous-moduli)): the generic orbit has unit dimension 16 on every nullity-4 stratum, leaving real moduli of dimension 11, 11 and 9, so the classes come from the kernel Gauss map into `Gr(2, C^16)` (real nullity 4, complex rank 2) over those moduli rather than from stabilizer representations alone. The item-5 records stop at nullity 8. The nullity-4 strata `D_(5,4)` are the generic rank stratum's boundary; their
kernel bundles need the same sequence the higher nullities used: kernel symmetry algebra, compact-orbit moduli,
stabilizer representations, transition cocycle, classes. The orbits of `G_2(C) x SO(2, C) x C^*` on `R_4` from the
regularity record are the starting charts. Falsifier for a claimed class: a transition outside the claimed
structure group or a characteristic class differing on two charts. Substrate: host for the symbolic steps, Kaggle CPU
for pooled sampling.

## Global model (roadmap item 7)

Deliverable: a finite model of `Z_5 = {(x, y) : x y = 0}` normalized, with a proved map to `Z_5`, its homology and cup
products. On the restricted polynomial path the model is a union of mapping cylinders of literal inclusions
`S(W) -> S(K_i)` ([RANK_STRATUM_TOPOLOGY.md](../../gororoba_quantum/RANK_STRATUM_TOPOLOGY.md#a-complete-topological-model-for-the-restricted-path)).
The general model replaces those inclusions with the attaching maps of item 6 over every stratum, assembled as a
homotopy colimit over the incidence poset, with chain-level maps checked against the sphere-bundle data of item 5.
Inputs: items 3 to 6 at every nullity, including the nullity-4 bundles. Admission: chain maps and selected homotopy
invariants; homology agreement alone does not admit. Falsifier: a chain map that fails to commute with an attaching
map, or a cup product that differs between the model and a direct computation on a sampled sub-complex.

## Uniform structure in n (roadmap item 8)

Deliverable: a recurrence across the Cayley-Dickson doubling ladder, as a theorem. Inputs: item 7 at `n = 5` and the
restricted family's sparse chain construction. Method: compute the same model at `n = 4` (sedenions, dimension 16)
from the existing low-dimensional records, compare the incidence posets, attaching maps and classes at `n = 4` and
`n = 5`, and state the recurrence that maps one to the other. Admission: a proof, distinct from an algorithm that
accepts `n`. Falsifier: an invariant at `n = 5` that the recurrence applied to `n = 4` does not produce.

## Order of work

The kernel-bundle residuals and the nullity-4 kernel symmetry algebra depend on nothing open and run now. The
attachment packages run in parallel with them. The global model waits on attachments and nullity-4 bundles; the
uniform structure waits on the global model.

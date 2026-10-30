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

## Open residuals

The full component group of the kernel symmetry group and the smaller reductions on nullity 12 remain open; the
program file gives their methods.

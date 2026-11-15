# PR 915 review

Reviewed head `efaa3a824efa9ae09f750db85286e3a6ca00f1b9`.

Core claims survive review. I found no counterexample or central proof gap, but three non-blocking evidence/implementation defects remain.

## Ranked findings

1. **Medium — proved: A5-551’s producer overstates one of its own checks.**

   The identity named `rank_8_on_the_polar_line` at [nullity4_real_polar_fiber_four.py:119](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_fiber_four.py) evaluates only five vectors at [line 228](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_fiber_four.py). Five samples cannot prove constant rank on a projective line.

   The ledger basis is accurate: it says those five points are checked here and the universal statement comes from A5-537. A5-537 supplies the missing exact module/Pfaffian argument. Thus A5-551 remains certified, but this producer’s `--check` is not a standalone verifier of its identity label.

   Remedy: rename the identity to `rank_8_at_five_polar_vectors`, or bind and replay the A5-537 certificate/result as an explicit dependency.

2. **Medium — proved: the second-chart “cross-check” test is tautological.**

   [test_a5_nullity4_qg_orbit_types.py:64](../../../../tests/test_a5_nullity4_qg_orbit_types.py) claims to check that scaling by `-1` identifies the types of `s` and `1/s`, but lines 66–67 compare hand-written constants:

   - `SIGMA_FACTS` against `qg.SPECIAL_S`;
   - `SIGMA_WITNESSES` against `qg.WITNESS_FACTS`.

   It never applies the stated scaling map or compares recomputed subspaces. The producer independently recomputes both endpoint facts, and the algebraic scaling argument is sound, so A5-556 survives. The test itself can pass without testing its named mechanism.

   Remedy: construct the scaling map, transform the `sigma=0` kernel/planes, and compare their spans exactly with the `s=0` objects.

   A related calibration weakness occurs at [test_a5_nullity4_qg_orbit_types.py:41](../../../../tests/test_a5_nullity4_qg_orbit_types.py): the planted block-mixing derivation also violates skewness, so its failure does not isolate eigenline preservation.

3. **Low — proved: independent symbolic work remains serial contrary to repository policy.**

   CPU-bound independent iterations occur without `parallel.py` in:

   - the 256 symbolic constructor entries at [real_nullity_bordered_matrix.py:76](../../../../docs/evidence/a5-kernel-bundles-residuals/real_nullity_bordered_matrix.py);
   - the 14 derivations at [nullity4_qg_orbit_types.py:223](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_orbit_types.py);
   - six independent Jacobian finite-difference columns at [test_a5_nullity4_real_polar_fiber_four.py:112](../../../../tests/test_a5_nullity4_real_polar_fiber_four.py).

   The gates finish in seconds, so this affects repository conformance rather than the mathematical verdict.

## Claim audit

### A5-554 — proved

The symbolic comparison is universal, not sampled:

- `z1..z15` and independent `w1..w15` symbols are constructed at [real_nullity_bordered_matrix.py:71](../../../../docs/evidence/a5-kernel-bundles-residuals/real_nullity_bordered_matrix.py).
- Every one of the 256 entries is expanded and compared at lines 74–82.
- All 32 basis left-multiplication matrices are compared through lines 86–95.
- `germs.transport()` checks all 30 doubly pure basis elements against all 32 input basis vectors at [a5_stiefel_pfaffian_germs.py:258](../../../../scripts/a5_stiefel_pfaffian_germs.py).

This is the same `bordered_matrix` constructor used by A5-364, so the transport applies to the constructor compared here. Real linearity in `y` and `x` extends the basis checks universally.

The dimension argument is sound: `x ↦ conjugate(phi(x))` is a real-linear bijection from `R^32` to the underlying real space of `C^16`; its target kernel is complex-linear, hence has twice its complex dimension. Positivity of `conjugate(z)·z` for nonzero real-derived `z` forces the bordered coordinate to vanish and gives `dim_C ker A = nullity M(z)-1`.

The row remains correctly limited to nonzero doubly pure elements.

### A5-551 — certified

The six equations are sufficient:

- `F=z₀*Πl=0` contributes four real equations and makes the two-dimensional transformed polar line equal the kernel plane.
- `det N=0` contributes two real equations.
- Six selected real coordinates vary; the remaining eight are fixed dyadics. Existence on this slice is sufficient for existence in the full orbit.
- The full-box enclosure of one entry of `N` excludes rank zero, so `det N=0` gives rank exactly one.

The interval implementation uses Arb balls throughout the decisive path:

- `exp(2H)` is evaluated on ball matrices at [nullity4_real_polar_fiber_four.py:351](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_real_polar_fiber_four.py).
- The block-exponential upper-right block encloses each derivative.
- The determinant derivative is evaluated from ball entries at lines 362–372.
- `J(X)`, not merely `J(x*)`, enters the Krawczyk operator at lines 393–400.
- Strict lower/upper comparisons establish interior inclusion.
- Using a dyadic midpoint approximation for `C` is valid: Krawczyk permits any nonsingular approximate inverse.

The Krawczyk inclusion theorem supplies existence and uniqueness inside this box. The point is real because all six unknowns are real intervals and `z=exp(iΣξD)z₀`; it has `μ=5i`, `Q=10`, and `G=0`.

“Certified” here means a rigorous interval proof of existence and uniqueness at 200-bit Arb precision, combined with exact symbolic orbit identities. It is stronger than floating-point measurement but does not provide exact algebraic coordinates; that distinction justifies the ledger status relative to the exact-symbolic `proved` rows.

### A5-555–558 — proved

The orbit argument closes.

- The producer checks that the 14 matrices span the derivation algebra, preserve `E_±`, and are equivariant at [nullity4_qg_orbit_types.py:217](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_orbit_types.py). The standard connected-group/Lie-algebra invariance theorem then extends infinitesimal invariance to connected `G₂(C)`.
- At `s=±1`, `P_x⊂E_ε` and its complement `Cq⊂E_-ε`. Since `E_+⊥E_-`, this remains the Hermitian complement after any `g∈G₂(C)`, even though complex `G₂` is not unitary. Because `q∈J` has nullity seven while the candidate point has nullity three, that point cannot lie on `Cq`; hence its kernel plane cannot be `P_x`.
- One nonzero maximal minor per stack is enough: a rank drop forces every maximal minor, including the selected one, to vanish. Its roots therefore form a finite superset of all possible exceptional parameters. The code then resolves every root:
  - `s=0,±1` by exact ranks;
  - `s=±i` as points outside this chart;
  - the `D1/D2` roots by exact plane coincidence;
  - infinity by the `sigma=0` chart.
- At `sigma=0`, the pencil calculation uses the gcd of principal Pfaffians in `c₂=1` plus a nonzero value at `(1:0)`, covering the entire projective line.
- A5-552 supplies the `u·u≠0` normal form. Rotation moves every remaining non-totally-isotropic point into that form. A5-359’s two isotropic slice families cover every totally isotropic pair and make all order-12 Pfaffians vanish, so rank is at most ten; A5-360 identifies the special `u×v=0` part at rank eight.
- `P_y` and `P_z` at `s=±1` have `dim C=4`; even if realized, they could only give `dim L=4`, already in the claimed set. They cannot introduce a new value.

Thus the possible common-kernel dimensions of an actual kernel plane are exactly `3,4,5`, giving `dim L=2,4,6`. The exact A5-552 witnesses establish occurrence of all three values.

### Dispositions

Every A5-553 clause has a successor:

- `s=±1`, exclusion of `dim L=10`: A5-555.
- Missing conic point `(i,0)`: A5-556.
- Global `dim C(P)=5` lemma and plane nullity seven: A5-557.
- `u·u=0`, totally isotropic exclusion, and exact value set `{2,4,6}`: A5-558.
- Real-nullity conversion: A5-554.

Each new row names A5-553 in its `supersedes` column. A5-553 retains its old basis as historical evidence, while README lines 469–475 name its successors. No clause was dropped or silently strengthened.

## Deterministic verification

On clean remote head `efaa3a824efa9ae09f750db85286e3a6ca00f1b9`:

```text
sh ci/pr_checks.sh gates --gates core-a5-real-nullity-bordered-matrix,core-a5-nullity4-real-polar-fiber-four,core-a5-nullity4-qg-orbit-types

PASS core-a5-real-nullity-bordered-matrix          1.2s
PASS core-a5-nullity4-qg-orbit-types               7.9s
PASS core-a5-nullity4-real-polar-fiber-four        1.4s
3 passed, 0 skipped, 0 failed
```

```text
pytest -n 4 --dist loadgroup <three focused modules>
88 passed in 12.04s
```

```text
ruff format --check: 6 files already formatted
ruff check: All checks passed!
mypy: Success: no issues found in 6 source files
```

Independent interval probes produced:

```text
two_half_radius_diagonals_enclosed: True
box_jacobian_has_width: True
constant_shifted_system_interior: False
```

The first probe’s final mutation attempt initially hit Python multiprocessing’s known inability to spawn from `<stdin>`; rerunning that leg with `GOROROBA_WORKERS=1` produced the rejection above.

An exact probe of the unresolved `P_y,P_z` question at the base `s=±1` frames produced:

```text
 1 y rank 6 nullity 9
 1 z rank 6 nullity 9
-1 y rank 6 nullity 9
-1 z rank 6 nullity 9
```

Both local and remote trees remained clean. `git diff --check origin/main...origin/a5-nullity4-open-row-certificates` produced no output.

## New hypotheses

- **Hypothesis — exact A5-551 point.** The rank-one locus contains a real algebraic point in a rational root-subgroup or Cayley chart of `G₂(C)`.  
  **Falsifier:** exact elimination shows `F=0` and `det N=0` imply `N=0`, or the real radical is empty.  
  **Cheapest test:** replace the exponential chart with a rational `G₂` chart, eliminate five coordinates, and isolate a remaining real root exactly or with Arb. This fits the prescribed four-vCPU proof host.

- **Hypothesis — dimensions of the exceptional fiber loci.** In the affine real 26-dimensional nullity-4 open stratum of `V(Q)∩V(G)`, each of `dim L=4` and `dim L=6` has real dimension 22, hence projective real dimension 20. For fixed `K`, each exceptional plane selects one complex line in the three-dimensional complex fiber, a real codimension-four condition.  
  **Falsifier:** the incidence Jacobian has rank other than four at an exact `s=0` or `s=2` witness, or an orbit component lacks the corresponding plane.  
  **Cheapest test:** compute exact tangent ranks of the plane-incidence equations at the six retained witnesses and verify constancy on one generic orbit chart on the proof host.

- **Hypothesis — `P_y,P_z` at `s=±1`.** Neither plane occurs as a real kernel plane throughout those orbit types, so the types contribute only the generic `dim L=2`. The exact base-frame complements above already lie in `J` with rank six.  
  **Falsifier:** one exact `g∈G₂(C)` for which the Hermitian complement of `gP_y` or `gP_z` has rank twelve.  
  **Cheapest test:** parameterize one nonunitary rational root subgroup, transform `K,P_y,P_z`, and eliminate the principal `8×8` Pfaffians of their complements on the proof host.

Verdict: the mathematical core is sound. The remaining work is oracle precision—make the A5-551 rank label honest, replace the tautological chart test with the actual scaling map, and route the remaining independent symbolic loops through the repository’s parallel machinery.
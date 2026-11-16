# PR 907 review

Reviewed clean head `ac3255d55db143020a14863f786132d884162579`; the remote checkout remained clean at the same head.

## Ranked findings

1. **High — computed: both Singular gates can accept a failed process.**

   The quartic runner invokes Singular with `check=False`, then ignores `returncode` and `stderr`; a marker in stdout is sufficient: [nullity4_quartic_discriminant.py:318](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_quartic_discriminant.py). It also omits `--no-rc` and verifies only that some `Singular` exists, not version 4.4.1 at [line 311](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_quartic_discriminant.py).

   The polar-stack audit likewise compares stdout but ignores status and stderr: [test_a5_nullity4_polar_line_stack.py:91](../../../../tests/test_a5_nullity4_polar_line_stack.py). Neither gate enforces the 4.4.1 requirement stated by [ci/AGENTS.md:136](../../../../ci/AGENTS.md) and [ci/AGENTS.md:210](../../../../ci/AGENTS.md).

   Deterministic remote probes planted status 7, fatal stderr, and acceptable stdout:

   ```text
   quartic: ACCEPTED ['MARKER DONE planted']
   stack:   ACCEPTED nonzero status 7 and fatal stderr
   ```

   The genuine replays did pass with Singular 4.4.1, so this does not falsify A5-537 or A5-540. It means their gates can pass for the wrong reason. Require status zero, `--no-rc`, an allow-listed or empty stderr, and exact version 4.4.1; add the two planted failures as regressions.

2. **High — proved: A5-550 and A5-552 promote an explicitly unproved identification into proved claims.**

   A5-550 is `proved` while claiming real nullities 12 and 16 “through the identification of A5-554”: [ledger.tsv:521](../../../../docs/evidence/a5-exceptional-fibers/ledger.tsv). A5-552 similarly claims real nullity 12: [ledger.tsv:523](../../../../docs/evidence/a5-exceptional-fibers/ledger.tsv).

   A5-554 remains only `survives` and expressly says the correspondence between real left multiplication and the complex bordered matrix “is not derived in a record”: [ledger.tsv:525](../../../../docs/evidence/a5-exceptional-fibers/ledger.tsv). The associated test checks 66 fixtures, not the universal change-of-basis identity: [test_a5_nullity4_real_polar_line.py:120](../../../../tests/test_a5_nullity4_real_polar_line.py).

   The complex statement in A5-550 is independent of A5-554 and is proved:  
   `ker A(p,conj p) = {0} × (ker M(p) ∩ conj(p)⊥)` and its complex dimensions survive review. Either remove the real-nullity parentheticals from the proved rows or derive the real/complex matrix equivalence symbolically.

3. **High — proved: the surviving universal clause of refuted A5-541 has no complete successor.**

   A5-541 says its universal clause—every `dim L=6` point has kernel-vector real nullity 12—“holds (A5-552)”: [ledger.tsv:520](../../../../docs/evidence/a5-exceptional-fibers/ledger.tsv).

   A5-552 proves the relevant plane-nullity statement only for `P_x` in the covered `u·u ≠ 0`, `s² ≠ 1` normal-form family. A5-553 explicitly leaves `s=±1`, the missing conic point, and totally isotropic pairs open: [ledger.tsv:524](../../../../docs/evidence/a5-exceptional-fibers/ledger.tsv).

   The missing lemma is:

   > Every real nullity-4 point with `dim C(P)=5`, equivalently `dim L=6`, belongs to the covered `P_x`, `s²≠1` orbit family.

   No current argument proves it. A missing-orbit point with `dim C(P)=5` and another rank on `P` is the candidate counterexample. The clause should remain open until orbit coverage is proved.

   The `primes` field of A5-541 also remains `32029`, although its decisive refutation now uses exact `Q(i)` witnesses. It should be `char0`, or the legacy modular row and characteristic-zero successor should be separated.

4. **Medium — proved from the recorded measurements: the CI-runtime diagnostic rule overgeneralizes.**

   The timings at [ci-runtime.md:201](../../../../docs/runbooks/ci-runtime.md) establish that contention can trigger the wall-time budget and that one named unit moved from 3.12 seconds to 19.55 seconds under the stated load.

   They do not support [lines 208–210](../../../../docs/runbooks/ci-runtime.md):

   > a unit that fails only on a loaded host, with the call-budget text, is no regression

   A real performance regression can cross the threshold only under contention and produce the same text. Conversely, another failure text can still be environmental. The valid operational rule is to rerun unloaded or with the call-budget check disabled, compare the unit’s result and unloaded timing, and classify only then.

   The macOS remote-HTTPS paragraph at [lines 97–105](../../../../docs/runbooks/ci-runtime.md) is properly bounded: observations are named, non-reproduction is explicit, and the proposed mechanism is labeled `hypothesis` with a discriminating capture.

## Claim audit

- **A5-537 — proved, with the gate defect above.** Both `σ=±1` branches are quantified. The `μ≠0` localization uses `1-wμ`; the `μ=0` cone is covered by the `s` and `v₁` localizations because their simultaneous zero is the excluded rank-10 point. `ρ≠0` follows from the stratum. Full rank of the stacked `[B;BD₁]` module makes the complementary common kernel zero. A5-530 supplies global normal-form coverage.

- **A5-540 — proved, with the gate defect above.** Hilbert–Burch gives base-scheme length three; Smith form gives local length `e`; the nonzero Hessian and local factorization give two smooth branches of contact `e`, hence `A_{2e-1}` and singular length `2e-1`. Summing gives `6-N = 3+deg gcd(χ,χ′)`. Over an algebraic closure, a reducible quartic without a line must be two smooth conics, whose singular length is `8-N`, a contradiction. Double conics and singular conics are separately excluded. `ρ=0` is outside the stratum and serves only as the retained length-seven calibration.

- **A5-539 — proved.** Under `Δ≠0`, `dim W=1` is impossible. A real two-plane lies in its generated quaternionic three-plane and has stabilizer `SU(2)`, dimension three. For `dim W=3`, that stabilizer remains only in quaternion position; any vector outside the quaternionic plane kills it by the stated norm identity. `dim W=4` is necessarily outside and likewise has zero stabilizer. Thus ranks 14 and 15 do not occur.

- **A5-550 — partly proved as described above.** Its complex kernel identity and the classification `dim L∈{2,4,6}` for `μ≠0`, `dim L=12` for the stated `μ=0` position, and exclusion of 8 and 10 are independent of A5-554. Only the conversion to real left-multiplication nullity leaks the surviving identification.

- **A5-551 — correctly open.** The row says exactly that two double-precision witnesses exist and records their gaps; it claims neither an exact point nor existence as a theorem.

- **A5-552 witnesses — computed and valid.** At `s=0,2`, the exact `Q(i)` construction checks `Q=G=0`, rank 12, and fibers `6,4,4`. The new exact routine computes the common kernel and Hermitian cut at [nullity4_qg_intersection.py:498](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_intersection.py); the same witnesses are passed to the predecessor `kernel_form` at [lines 553–568](../../../../docs/evidence/a5-kernel-bundles-residuals/nullity4_qg_intersection.py), and both return the same `L`.

- **Other dispositions — proved consistent.** A5-441, A5-442, and A5-538 have successors for their clauses. Rows A5-530, A5-531, A5-533, A5-534, and A5-535 changed only in `supersedes`. Their characteristic/status fields remain consistent. A5-541 is the exception above.

- **Tests — no other wrong-reason pass found.** The apparent self-comparison at [test_a5_nullity4_quartic_discriminant.py:109](../../../../tests/test_a5_nullity4_quartic_discriminant.py) checks repeatability only; the retained record independently pins the parameter list and the preceding test verifies stratum membership. Mutants otherwise fail at their intended verdict field. Singular absence produces declared skips rather than passes.

## Suggested next certificates and conjectures

- **Hypothesis — A5-551:** the rank-one pairing locus is a nonempty positive-codimension real algebraic stratum, separated from the normal-form rank-zero locus.  
  **Falsifier:** an exact implication `det(pairing)=0 ⇒ pairing=0` on the `μ≠0`, `P=l_z` locus.  
  **Cheapest test:** fix a deterministic dyadic slice through one retained witness and apply python-flint Arb interval Newton/Krawczyk to eight real equations: `Re/Im G`, the two complex equations `conj(z)⊥l_z`, and `Re/Im det(pairing)`. Interval-certify `Q≠0`, `μ≠0`, rank `M(z)=12`, polar rank eight, and one nonzero pairing entry. This fits the 4-vCPU proof host well under the ten-minute cap.

- **Hypothesis — `s=±1`:** `P_x` is excluded from the real Gauss image throughout the compact orbit, so its formal `dim C(P_x)=7` never yields `dim L=10`.  
  **Falsifier:** an exact compact-frame transform whose Hermitian-orthogonal vector lies outside `J` and has rank 12.  
  **Cheapest test:** parameterize one compact `G₂` root subgroup over `Q(i)`, transform `K` and `P_x`, and eliminate the condition that the orthogonal vector remains in `J`; run on the proof host.

- **Hypothesis — missing conic point `(β,λ)=(i,0)`:** the second affine chart has the same three-line higher-nullity cone and produces no fiber dimension beyond `2,4,6`.  
  **Falsifier:** an exact real point in that chart with `dim C(P)=6` or `7`.  
  **Cheapest test:** rebuild `K`, its Pfaffian restriction, and the three plane stacks directly in the second chart over `Q(i)`; this is a small SymPy/Singular proof-host computation.

- **Hypothesis — totally isotropic pairs:** every independent pair with `u·u=u·v=v·v=0` has `rank M=10`, so this orbit contributes no nullity-4 points.  
  **Falsifier:** one exact independent pair with rank 12.  
  **Cheapest test:** classify the `G₂(C)` orbits of independent orthogonal null pairs and evaluate one representative per orbit. A fallback Singular certificate saturates the `12×12` Pfaffians by the independence minors and proves a `10×10` minor is locally nonzero. Run on the proof host.

Together these imply the broader **hypothesis** of A5-553: the real nullity-4 intersection has only fiber dimensions `2,4,6`.

## Remote verification

All computations used the prescribed remote checkout and fixed inputs.

```text
nullity4_polar_line_module.py --check
pass: 7 identities, 2 signs, 172 retained points

polar-line-stack audit
1 passed, 2 deselected in 0.30s

nullity4_quartic_discriminant.py --check
pass: 8 identities, 6 certificates, 8 fibers

nullity4_real_polar_line.py --check
pass: 5 identities, 8 lines, 2 witnesses, 64 fixtures

nullity4_qg_intersection.py --check
pass: 9 identities, 6 witnesses, 32027 scanned s

five focused test modules
151 passed in 25.07s

ruff format/check
9 files already formatted
All checks passed!

mypy
Success: no issues found in 9 source files

Singular
Singular for x86_64-Linux version 4.4.1
```

No files were changed.
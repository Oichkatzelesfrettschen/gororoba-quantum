# Review of pull request 817

Reviewed committed `HEAD` `f01757c4b` against `origin/main` `1e302aed1`. The artifact combines exact finite-field linear algebra, sampled algebraic geometry, and reproducibility records.

A concurrent uncommitted `--plus` edit appeared in `fiber_plucker_map.py` during review. The review excludes that edit and leaves it untouched.

## Findings, ranked by consequence

1. **SERIOUS — computed evidence is summarized beyond independent auditability.**

   The result writer retains ranks and counts but omits the fitted matrix `T`, row scalars `c`, pivot indices, sample identifiers, fiber points, Plücker vectors, and their digests (`HEAD:docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py:119-161`). For example, `fiber-plucker-map-iso-p32009.json` ends with aggregate fields at line 26.

   Consequently, the retained JSON cannot independently establish that fitted and held-out fiber points differ, reproduce `T`, or run a pairing mutation. The complete generator remains deterministic, but replaying a 1–23 minute computation is the only route back to the witnesses.

   Remedy: retain ordered sample and held-out hashes, hashes or compressed forms of `c` and `T`, pivot indices, a residual digest, and an explicit pairing-mutation result.

2. **SLOPPY — the parametrization identity has the wrong sign as written.**

   `vb_special_arcs.py` lines 3–5 and `README.md` lines 137–139 state
   `k/(1+k²)=iω` and `e=(1+ik)/(1-ik)`. Direct substitution gives
   `ω=ik/(1+k²)`, hence `iω=-k/(1+k²)`.

   The executed mapping is nevertheless correct: the VB value `k=-9` uses the E8-header parameter `+9`. The modular probe printed:

   ```
   32009 ... k_v/(1+k_v^2) 27715 i*omega 27715 same True written_same_k_formula False
   32029 ... k_v/(1+k_v^2) 14452 i*omega 14452 same True written_same_k_formula False
   ```

   Remedy: name the two coordinates separately and state `k_E8=-k_VB`; remove “up to the sign convention” as a substitute for an equation.

3. **SLOPPY — SHA-256 does not prove algebraic genericity.**

   `HEAD:.../fiber_plucker_map.py:52-56` claims that reducing SHA-256 output modulo 101 makes the parameter points satisfy no common low-degree relation. A hash provides deterministic dispersion, not an algebraic-independence theorem.

   The actual degree-one through degree-three evaluation ranks are meaningful computed checks and partially replace this unsupported claim. They cannot rule out every higher-degree or family-specific subvariety.

   Remedy: state only that hashing avoids the known affine-line construction, then make the measured Veronese ranks the genericity evidence.

4. **SLOPPY — the driver detects a failed fit but declares no verdict.**

   `HEAD:.../fiber_plucker_map.py:191-203` always writes and prints the record. A failed fit merely omits `delta`, while failed validation merely lowers `held_out_proportional`; the process still exits successfully.

   Remedy: record an explicit `verdict`, and add a deterministic mutation mode whose expected rejection participates in that verdict.

5. **SLOPPY — ledger A5-295 exceeds its retained record on execution provenance.**

   `ledger.tsv` asserts “6.5 minutes on the 32-thread laptop.” Neither `vb-special-arcs-result.json` nor `vb_special_arcs.py` records elapsed time, worker count, or host. The mathematical fields are supported; that measured provenance is not.

## Is claim 2 a real test?

**PROVED:** Yes, as a finite-sample projective interpolation test.

Let `V` contain the rows `vδ(y_s)` and let `N` span its left nullspace. For each Plücker coordinate `j`,

`diag(c) Pl[:,j] ∈ col(V)` iff `N diag(Pl[:,j]) c = 0`.

This is the annihilator characterization of a column space. Checking only pivot columns of `Pl` is sufficient because every omitted column is a fixed linear combination of them; lines 145–154 then reconstruct `T` and test the residual against every Plücker coordinate.

The systems are far from tautological. For opposite-sign X, degree two gives 1,884 displayed equations before dependencies against 320 scalar unknowns and leaves nullity one. For the combined W8 sample, the analogous construction has 75,504 rows against 640 scalars.

**MEASURED mutation calibration:** A deterministic synthetic quadratic map through the committed `fit` routine produced:

```
synthetic_control: delta 2, solution_dimension 1, held_out_proportional 10
training_plucker_cyclic_mutation: no delta
held_plucker_cyclic_mutation: held_out_proportional 0
```

Thus a Plücker permutation is detected. The code reports the failure through missing or reduced fields, but not through a verdict or exit status.

**COMPUTED separation:** All 360 raw parameter tuples were distinct for X, same-sign X, Iso, W8 degree-30, and W8 degree-20, with zero fit/held-out overlap. The retained records do not permit the stronger check that fitted and held-out normalized `y` values are disjoint.

**PROVED normalization invariance:** Replacing `y_s` by `λ_s y_s` scales `v₂(y_s)` by `λ_s²`; rescaling a Plücker representative scales it by another nonzero row scalar. Both changes are absorbed into `c_s`. The normalization cannot manufacture or conceal the existence of the projective quadratic fit.

## Claim verdicts

1. **COMPUTED, survives with a documentation correction.** The JSON records both primes with order 24, finite-family rank 22, control rank 22, special rank 18, total rank 34, and 480 special limits. Every listed special/control arc has base nullity 12 and arc nullity 8. The mirror and neighbor controls add nothing, while `e0(9)` raises 22 to 34. The executed `+9 ↔ -9` mapping is correct; the displayed same-symbol formula is not.

2. **COMPUTED, survives only as a sample statement.** The exact linear system is equivalent to the claimed fit, the two-prime records report the stated ranks, degree one has no solution, degree two has a one-dimensional nonzero-scalar solution, and all retained held-out counts pass. The evidence does not prove a global morphism on the full fibers.

3. **HYPOTHESIS, accurately bounded.** `README.md` lines 182–188 say “on each sampled family” and immediately state the sample scope. Same-sign X reports rank 12 of 15 in degree one and 45 of the certified 51-dimensional degree-two fiber piece. The sentence does not claim coverage of the missing directions.

4. **PARTLY FALSIFIED.** A5-296 states no more than the committed source and aggregate records. A5-295’s mathematical content is supported, but its laptop runtime and worker-count assertion lacks a retained measurement.

## Unstated conjectures suggested by the evidence

- **HYPOTHESIS — global quadratic morphism.** The sampled maps may extend to quadratic morphisms on the complete reduced fibers, with the W8 restrictions glued by one `T`. Falsifier: one valid arc whose plane is not proportional to `v₂(y)T`, or a point where `v₂(y)T=0`. Cheapest test: retain `T`, generate a second deterministically salted parameter family, and evaluate without refitting.

- **HYPOTHESIS — characteristic-zero lift.** The matching ranks and identical integer parameter sets at both primes suggest that the projective matrices lift to one matrix over `Q` or `Q(i)`. Falsifier: normalized matrices at the two primes admit no compatible CRT or rational reconstruction. Cheapest test: retain pivot-normalized `T` at both primes and reconstruct only its pivot-coordinate block first.

- **HYPOTHESIS — functorial exterior-power origin.** The uniform degree two may arise from the second-order leading kernel complex rather than accidental interpolation. Falsifier: the reconstructed `T` disagrees with the appropriate compound/exterior-power map after the documented basis changes. Cheapest test: compare that construction on opposite-sign X, where the degree-two space has dimension six.

## Verification boundary

**MEASURED:** `git diff --check origin/main...HEAD` emitted no output; AST parsing passed for both new Python files; all nine new JSON records parsed.

A full geometric mutation replay was not completed: the repository’s slice reconstruction stopped before sampling with `xp-nm elimpart blocked_error: Singular exited with status 1`. That harness failure supplies no mathematical evidence.

**Verdict:** The central rank computations and finite-sample quadratic fits are internally sound. The pull request should preserve its hypothesis status, correct the sign equation, replace the SHA genericity claim, and retain enough witness material plus an explicit mutation verdict to make A5-296 independently auditable.


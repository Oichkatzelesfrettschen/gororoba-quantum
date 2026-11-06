# Codex gpt-daybreak-blue-latest review of pull request #729 at 5deb80f95

Reviewed the complete `origin/main...5deb80f95` diff and every changed commit blob. Fields: statistical inference, simulation reproducibility, and provider-case admission.

## Findings

**FATAL — the “exact” permutation test permutes fictional experimental units.**  
`scripts/belenos_mesh_persistence.py:185-194,211-243`; `docs/design/belenos-mesh-persistence-case.md:73-82`

The four compilation seeds produce four whole-mesh vectors spanning all six blocks. The implementation nevertheless permutes mesh labels independently in each block, creating `24^6` recombinations that the acquisition never randomized. An exact test of the four seed-level units has 24 common permutations, with one permutation applied across all blocks.

The cells also lack marginal exchangeability: the primary share pools two iterations while each replicate uses one. Consequently, its binomial variance differs before any mesh effect enters. The power simulation assumes independent per-block mesh errors and reports null rejection 0.047, which calibrates one chosen model; the simulation does not turn the acquisition into an exact randomization design.

**Fix:** use common whole-mesh permutations and equal exposures, or state and justify a separately exchangeable block model and calibrate it against plausible seed-wide and slot-wide correlations. Rename the resulting p-value model-conditional unless the acquisition supplies the required randomization.

**SERIOUS — the Student-t “upper bound” has no demonstrated coverage for these residuals.**  
`scripts/belenos_mesh_persistence.py:234-244,270-285`; `docs/design/belenos-mesh-persistence-case.md:79-80`

The calculation applies an ordinary through-origin t interval with 17 residual degrees of freedom. The residuals are correlated by within-block centering, have unequal binomial variances because their denominators differ, share seed-level acquisition units, and use noisy retained deviations as predictors. Those conditions do not yield the iid normal errors required by the stated t bound. The simulation’s 0.0485 false-`redrawn` rate at beta 0.5 establishes coverage only under its independent Gaussian cell-error model.

**Fix:** obtain the upper limit from a preregistered clustered/parametric bootstrap that retains denominators and seed-wide dependence, or label the current quantity a model-calibrated decision score rather than a confidence bound.

**SERIOUS — the tests do not bind the preregistered decision rule or the power record.**  
`tests/scripts/test_belenos_mesh_persistence.py:37-66,108-162`

The brute-force test begins after `relabeled_values` and copies the implementation’s `1e-12` tolerance. The endpoint fixture checks slopes ±1, while the reading fixtures use p=0.5 and bounds 0.2/0.9. Mutations such as alpha 0.05→0.10, useful slope 0.5→0.3, residual dof 17→18, or drift alpha 0.01 changes survive. No test calls `power`, checks seed spawning/clipping/retained denominators, or replays `belenos-mesh-persistence-power.json`; no gate names that record.

**Fix:** add independent full-statistic enumeration, exact boundary cases for every threshold and degree of freedom, drift withholding tests, planted mutants, and a deterministic record replay gate.

## Checks that found nothing

Normalized case rows exactly matched their retained sources; the new circuit was byte-identical to job-09; QRNG index 2 resolved to 21344; duration, credits, iteration budgets, identity hashes, approval requirement, document mapping, retained-record handling, parallel mapping, and mock-result exclusion matched repository rules. The corrected mesh-selection numbers followed the retained JSON. `git diff --check` and pinned Ruff 0.17.1 lint/format checks were clean.

The review process wrote no file. Concurrent worktree edits appeared in four tracked files; every finding above references commit `5deb80f95`, not those edits.

**Verdict:** the identity-first hardware case is sound, but its persistence inference is not exact as claimed. The pull request should not use the p-value or t bound for a scientific reading until the experimental unit and coverage defects are corrected.

Review completed in 10 minutes 40 seconds.

# Review: PR #149 (jax_bridge_sweep structure) and branch sim/atlas-fringe-amplitudes

Read-only. Main is now b9b71f2 (#146 merged on top of #144).

## A. PR #149 kaggle/jax-bridge-structure (head cb36d78)

Verdict: the code is sound; one gate-name collision with main needs fixing at merge.

Observed:
- Diff over base touches ci/gates.json (+2 gates), jax_bridge.py, jax_bridge_sweep.py, one note. All changed text is ASCII, no line over 120 columns (pyproject line-length 120).
- CI on cb36d78: shards 0, 3, 4, 5 green; shard 1 failed only core-339 (ghost_error_scale, inherited from #147/#148 base); shard 2 failed only sources-123 and sources-124 (docs/verify_sources.py, base). Read from the job logs. The two gates unique to this PR (core-327 and core-337, the `--self-test` runs, normal and -O) ran and passed.
- Rescale correctness: `cz_error` is min(factor * reported, CZ_CAP), the entry ghost_error_scale.scaled writes, and None passes through. The self-test compares the rescaled Kraus stack's SuperOp against a freshly built Aer scaled noise model for every driven coupler and every coupler above the 4/5 cap. It uses factors 1e-3, 0.5, 12 and 1000, which reach the zero-depolarizing, interior, error-cap and depolarizing-cap branches, and `require` fails if any branch is unreached. It also asserts that every non-CZ channel of the scaled model equals the factor-1 one, which justifies the single-template design. Tolerance is 1e-12.
- Parity sampling: `parity_labels` sorts the labels and draws with `default_rng([seed, sha256(run)[:8]])`. It does not use Python `hash()`, so it is stable across processes. The self-test asserts determinism, no repeats and that `all` returns every label. Parity is checked at factor 1 only. Other factors rest on the self-test's per-factor reproduction, which is reasonable.
- Parallelism rule: the CPU loops in `self_test` (scaled-model builds, superop distances, numpy evolutions) go through parallel.ordered_map. The sweep itself uses the batched JAX replay and one Aer call per snapshot. This satisfies AGENTS.md.
- Determinism: dict ordering is by first appearance, the output sorts `parity_checked`, and the seed is recorded in the output.

Findings:
1. MUST-FIX (merge-time, 15 min): gate names core-327 and core-337 collide with main. Main already has core-327 (qi_crosstalk_teleport_cases --check) and core-337 (n21_conjugation_noise --check, full tier). merge-tree against main conflicts in ci/gates.json, AGENTS.md, docs/notes/kaggle/substrates.md and scripts/kaggle_run.py. Duplicate names break `ci/run_gates.py` sharding and `ci/check_run_gates.py`, so rename after merging main. Free names exist (main has no core-339, 342-345 or 349+, but #147 takes 339). Also, commit daa28c8 says "core-327 and core-328", but the tree carries 327 and 337; the message is wrong and cannot be amended without a force-push, so mention it in the PR body.
2. SHOULD-FIX (10 min): the gate seconds for both self-tests are the same 61.0 s, which looks like a placeholder. Replace with the measured CI seconds, since shards assign longest-first by these numbers.
3. SHOULD-FIX (5 min): sorted `member#k` labels are lexicographic (`#10` before `#2`). Harmless for determinism, but the docstring should say "sorted as strings".
4. BOUNDARY: host memory holds every program (10 factors times replicas, with Kraus arrays) of a run at once. `--batch-bytes` bounds only the device-side stacks. At the 93 MB retained set this is fine; it is untested beyond that and is not a documented-interface defect.
5. BOUNDARY: jax_bridge.py changes (+271 lines) were outside the stated scope and not line-reviewed; the self-test exercises them.

Merge order: #147 -> #148 -> #149, each retargeted to main per AGENTS.md before the base branch is deleted. #149 then needs a merge of main (4 conflicting files above), a gate rename, and a rerun of the `pr` tier. #147's core-339 and the sources-123/124 failures must be fixed on #147/#148, not here.

## B. sim/atlas-fringe-amplitudes (4 commits over edf76a06, no remote)

Verdict: the science and the replay are sound. The branch is not ready for a PR as-is: the gate names collide, and the completed 14-lane run is neither retained nor evaluated.

Observed:
- Replay: `cd gororoba_quantum && python3 -B -W error ../scripts/atlas_fringe_amplitudes.py --check ../docs/evidence/atlas_fringe_amplitudes/result.json --runs ibm_fez,ibm_kingston --lanes 4` passed ("lanes ... and the structure of [fez, kingston] reproduced") in 51.1 s wall, normal mode, default workers. The gate's recorded 395 s (227 s normal, 168 s -O) is at one worker; I did not rerun at one worker or in -O.
- Statistics: DerSimonian-Laird tau^2 = max(0, (Q - dof) / (sum w - sum w^2 / sum w)) is correct. sigma_y^2 = sigma_hw^2 + sigma_replay^2 is the right independence assumption. The 2000-draw bootstrap has a sampling error of about 1.6 percent of the sd, against a 10 percent falsifier. The ideal-normalized vs replay-normalized chi-square comparison was correctly dropped for tau, since sigma differs between them. The pre-registered falsifiers are in the docstring.
- Bootstrap spread is 4.10 percent (Kaggle) and 4.06 percent (retained) at its worst, all 14 lanes validated.
- Kaggle run 2026-10-17T010313Z: state COMPLETE, output/output/exit.json returncode 0, empty stderr, dataset 659 files with `mismatched: []`, git_commit 3da37a8 equals HEAD, no untracked inputs. It is complete. Note the exit.json sits at output/output/, not at the run root.
- Consistency with retained evidence: all of inputs, runs, models and bootstrap are identical. Lane-4 fits are identical except one field. The structure block differs only in `bootstrap_over_propagated` (about 1 to 4 percent per edge). Inference (medium confidence; a Kaggle-numpy vs 2.5.4 rerun would settle it): a different numpy binomial stream, because the seeds are fixed and the inputs are equal. Also `ibm_kingston` lane 4 `readout_plus_constant.fold_condition_max` is null on Kaggle and 1.27e16 in the retained file, a BLAS-dependent number for a rank-deficient fold. core-341 sits in the full tier, so the first CI exposure is a main push or the nightly run; a different BLAS on the runner could turn it into inf/null and fail the check.
- Confirmation criterion (pre-registered, README line 175): idle_relaxation_plus_constant must beat lane_constant on at least 6 of 8 confirming lanes. By leave-one-out RMS from the Kaggle output it wins on Fez 0, 1, 6 and Kingston 1, and loses on Fez 2, 3, 5 and Kingston 0: 4 of 8, so it is REFUTED. The kappa = 1 prediction is refuted on 13 of 14 lanes (Kingston 3 is not). This is the finding, and nothing on the branch records it. The untracked report still says "Full 14-lane run (Kaggle, not run)".
- Untracked report: docs/notes/atlas-fringe-amplitudes-report.md carries process history that the instruction files bar from durable text ("Branch `...`", a Commits list with SHAs, "not run"), duplicates the README tables, and says "within 4 percent" where the worst case is 4.1 percent. docs/notes/coherent-error-families-report.md is the precedent for notes, and the tables belong in docs/evidence/atlas_fringe_amplitudes/README.md.
- Merge: `git merge-tree` conflicts only in ci/gates.json. Main took core-340 (qi_ibm_noise_replay) and core-341 (check_qi_platform_retention); the branch also uses core-340 and core-341.

Findings:
1. MUST-FIX (15 min): rename core-340 and core-341 to free names (for example core-342/343, confirm at merge) and fix the references in the README (lines 186 to 200), the coherent-error-families note, and any report text. Merge main and resolve the single ci/gates.json conflict (also the core-001/002/039 file lists, which should auto-merge).
2. MUST-FIX (30 min): retain the 14-lane run and write its verdict. Add the run directory under results/kaggle/ (1.1 MB; the layout matches tracked runs, and `.gitignore` already admits `output/*.log`). Add a README section "14-lane result" stating criterion 4 of 8, so refuted, with the per-lane table. Without it the pre-registered criterion has no outcome in the tree.
3. SHOULD-FIX (45 min): add a gate for the Kaggle record, in the pattern of core-334. A byte `cmp` fails on bootstrap_over_propagated and fold_condition_max, so use a tolerant comparison of the Kaggle output against result.json: exact everywhere except those two fields, with the ratios bounded by the 10 percent falsifier. Alternatively rerun the entry with `--ci-env` so the stream matches CI, at about 35 CPU-minutes. Without one of these the Kaggle file is unchecked evidence.
4. SHOULD-FIX (20 min): make the rank-deficient `fold_condition_max` platform-stable, either null when a fold is rank-deficient or capped, so core-341 passes on a CI runner whose BLAS returns inf where this host returns 1.3e16.
5. SHOULD-FIX (15 min): resolve the untracked note. Fold the verdict and falsifier table into the evidence README and delete the note, or keep a short docs/notes file with no branch name, commit list or "not run" section, and correct the 4 percent figure.
6. BOUNDARY: criterion scoring uses leave-one-out RMS (my reading of "scores"); the README does not name the metric. State it in finding 2.

Commits that land the dirty files correctly (after the rename and merge of main):
1. `ci: atlas_fringe_amplitudes gates take free names` (gates.json plus README and note references).
2. `results: atlas fringe amplitudes 14-lane run on a Kaggle CPU kernel` (the run directory only).
3. `atlas_fringe_amplitudes evidence: 14-lane result, idle relaxation refuted on 4 of 8 confirming lanes` (README, the note decision, the tolerant gate and the stable fold_condition_max).
Both commits carry `Assisted-by: Claude Code (model)` per AGENTS.md. Then push the branch by name, open the PR, and run `@codex review`.

Files: sim/atlas-fringe-amplitudes: {scripts/atlas_fringe_amplitudes.py, docs/evidence/atlas_fringe_amplitudes/README.md, docs/notes/atlas-fringe-amplitudes-report.md, results/kaggle/2026-10-17T010313Z-gororoba-atlas-fringe-amplitudes/}; kaggle/jax-bridge-structure: scripts/jax_bridge_sweep.py.

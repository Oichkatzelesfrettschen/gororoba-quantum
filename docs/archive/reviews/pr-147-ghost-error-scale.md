# Review: PR #147 kaggle/ghost-error-scale (head 1a099fe)

Worktree: kaggle/ghost-error-scale. The branch is 17 commits over main, with merge base edf76a0 (#145). origin/main is now 4a383df (#156).
Read-only review. The only things written are scratch scripts under the session scratchpad. `git status` of the worktree shows no tracked changes.

## Verdict

PR #147 cannot merge. Three blockers, all verified:

1. **The `ci/gates.json` conflict also collides gate names.** `mergeable_state` was `dirty`, and GitHub creates no `pull_request` run for a PR whose test merge ref it cannot build. So no CI exists for 6decf4a, 078489b, dfb4384 or 1a099fe. On top of the text conflict, main now owns core-330..338, and the branch reuses five of those numbers.
2. **core-339 fails on all three retained parts.** The parts carry doubled coupler counts. The fix is the three ghost-error-scale kernels already RUNNING on Kaggle; no code change is needed.
3. **The PR body is false at head on two points.** It says "five kernels running", but four were cancelled and the one that finished is stale. It also says "core-339 passes", which 078489b's own message contradicts.

## 1. Commits

The list runs oldest first.

| Commit | What it does | Findings |
| --- | --- | --- |
| 2298108 | Adds scripts/ghost_error_scale.py: a per-run (c, r) grid of 10 x 5 points under a common seed, a resample floor, a PUB bootstrap, and --check/--report. | The kernels ran this commit. Later commits superseded its diagnostics (couplers doubled) and its metadata key `cap`. |
| 04cfb6d | Merges origin/main. | None. |
| 2a5a7d4 | Adds scripts/ghost_idle_budget.py and idle_budget.json; gates core-330 and core-331. | The gate names now collide with main's QI gates (see section 2). For the physics, see the ghost_idle_budget.py section below. |
| 9f46a5b | README: the per-PUB excess and three predictions for part a. | The registration order is verifiable: this commit precedes d7b7b72, which retains part a. |
| d794ab5 | Idle-budget docstring: how measurement and reset are treated. | None. |
| 7e8534b | Adds scripts/ghost_event_scale.py (padding, per-event m, CZ factor); gates core-332 and core-333; SCHEMA set to v2. | The gate names collide with main's core-332/333 (qi_coupler_zz_map, #146). |
| dd87dfb | Records draw timing; adds the --pad split and merge. | None. |
| b0c43d0 | Docstring: padded-draw cost factor 2.4. | None. |
| 7fa1830 | Merges origin/main. | None. |
| 9593724 | Retains parts b and c; gate core-338 compares them with cmp. | core-338 collides with main's linear_conjugation merge gate (#142). |
| 69103ee | Event-scale readout axis, near-best sets, three-valued readings, --readout split. | A dynamic run's readout_fit binds the part's sha256. Every regeneration of the parts therefore invalidates any event-scale record made before it (see section 4). |
| d7b7b72 | Retains part a; gate core-339; member-coverage check uses sets. | None. |
| ae4502d | Records the parts dataset (results/kaggle/datasets/gororoba-ghost-error-scale-parts.json). | Its digests are those of the old parts, so a re-upload is owed after the regeneration. This is the last commit CI ran on (success). |
| 6decf4a | Merges origin/main at edf76a0. | e81342a (#142, core-335..338) landed on main at 17:38:07, twelve seconds after this merge. From then on, every push conflicts in ci/gates.json. |
| 078489b | ghost_error_scale: pooled grid through parallel.ordered_map; one CZ entry per unordered coupler; separate cz_cap/readout_cap; replica-row tolerance in ghost_error_scale and ghost_run. | The body states correctly that "core-339 fails until they rerun". The PR body was not updated to match and still claims core-339 passes. The parts were not regenerated. That is open Codex thread 4300542973. |
| dfb4384 | Event axis: an X flip before each mid-circuit measure and after each reset, replacing a depolarizing channel after the event. | It changes the physics of m without bumping SCHEMA, which stays `ghost-event-scale-v2`. Records made under the old semantics (a1) pass `load()` and are caught only by a CPU rerun at m > 0. |
| 1a099fe | Event scale: pooled padding, floor replica-count checks, PROVENANCE check in load(). | Codex has not reviewed it (summary head = dfb4384). |

### scripts/ghost_error_scale.py (549 lines, new)

- L109-155, `diagnostics()`. The dedup is right: every retained snapshot lists both orientations with equal error (checked on every file under docs/evidence/calibration/history). So the fix changes `couplers` only, and the reported means and cap counts stay the same.
- L226-227. `circuit_shots` is computed in the grid loop and never used there. The pooled sampler rebuilds the shot list itself. This is dead code; ruff misses it because the name is rebound and used at L242/244.
- L238-256. The floor loop runs serially over snapshot groups, at most two draws per group, with Aer using its own threads. This is acceptable.
- L316-324, `load()`. It checks schema and grid only. It does not check seed, device, max_qubits, versions or `scaled` across parts, which ghost_event_scale.load now does through PROVENANCE. Old parts that carry `scaled.cap` instead of `cz_cap`/`readout_cap` load without complaint.
- L406-414, `tolerance()`. The replica-row count is right because the mean runs over rows. The bound 5*sqrt(2 mean(1/shots)/rows) treats each row's TV variance as 1/shots, which is a conservative upper scale. It needs no change.
- L417-459, `validate()`. It requires exact equality of the rebuilt diagnostics, which is why the old parts fail (section 3). It runs serially over all 15 audited runs, and each run calls ghost_run.prepare. AGENTS.md requires CPU-bound loops over independent items to go through parallel.py, so this is a rule violation. check() rebuilds 15 runs on every CI execution, so the cost lands on CI.
- L462-504, `check()`. It has no -O mode in core-339, while core-331 and core-333 run both modes. It also has no negative self-test: nothing proves that validate rejects an altered part.
- No gate runs ruff, ruff format or mypy on this file. core-001, core-002 and core-039 list ghost_run.py but not ghost_error_scale.py, while the other two new scripts have dedicated lint gates. Locally the file passes ruff 0.14.11 (`uvx ruff@0.14.11 check/format --check`) and mypy, so the gap is coverage, not a defect today.
- Voice is mechanism-first throughout and ASCII-clean.

### scripts/ghost_event_scale.py (1298 lines, new)

- L234-250, `readout_fits()`. It binds the sha256 of the whole part file. A metadata-only regeneration of the parts (the coupler fix) therefore invalidates every event-scale record without changing any fitted r. It could bind the run's `mean_tvd` digest instead, but binding the file is defensible. Whichever is kept, it fixes the ordering: parts land first, then the event-scale kernels.
- L200, SCHEMA. It was not bumped in dfb4384 (see above). A bump to v3 makes load() reject the a1 record and the cancelled kernels' outputs on sight.
- L387-401, `event_positions()`. `last_use` counts an `if_else` on the measured qubit as a later use. A terminal measure followed by a conditional virtual rz on the same qubit would get an m flip. The retained runs probably do not contain that pattern; the self-test does not cover it.
- L404-416, `with_events()`. This matches the docstring: X before a mid-circuit measure, X after a reset. The probe in self_test, L1202-1209, pins both placements.
- L682-716, `merge()`. The floor-at-merged-minimum argument holds because each part's floor sits at the part's own first-in-grid-order minimum.
- L961-998, `check()`. It validates serially over runs, which is the same parallel-rule issue as above. With `--runs all` as the default it reruns every retained run on the CPU, so the future retained-result gate must pass a reduced `--runs` (080216).
- L1157-1158, self_test. It runs prepare serially over the 10 default runs. Each prepare pools its own padding, so the outer loop is the serial one.
- Voice: the docstring names specific runs (2026-10-13T083417) as data facts, which is acceptable. It is ASCII-clean.

### scripts/ghost_idle_budget.py (231 lines, new)

- L74-77. The process fidelity (1 + e^{-t/T1} + 2 e^{-t/T2})/4 and the conversion F_avg = (2F+1)/3 are right for one qubit.
- L139 and L193. `c_idle = 1 + E_idle/E_cz` adds a sum of one-qubit average infidelities to a sum of reported two-qubit EPG. The units differ by the dimension factor: (d+1)/d relates average and process infidelity, which is 3/2 for one qubit and 5/4 for two. The ratio therefore carries an error of order 20 percent. The docstring already calls the budget an upper estimate. One sentence naming the mismatch would close the gap.
- It uses parallel.ordered_map over runs (L209), so the parallel rule is satisfied.
- `--check` recomputes and compares byte for byte, so the gate is deterministic.

### scripts/ghost_run.py (6 lines)

The tolerance now counts replica rows, and the code is right. The commit claims core-287 passes under the tighter bound, but no CI has run since. Treat that claim as not verified on CI.

### docs/evidence/ghost_error_scale/README.md (127 lines, new)

- L15, L74 and L78 cite core-331, core-338 and core-339. Those names must follow the renumbering.
- L74-77 say "The kernels ran commit 2298108; four files differ ... Aer device selection". This becomes false once the parts come from the dfb4384 kernels.
- L26-36 and L110-111 report fitted r = 0.5, the grid floor, for 070853, 020454, 022433 and 055624. The README never says these fits sit at the axis edge, where the true minimum may lie below the grid.
- L113-115 read the result as "idle-only fails, per-broadcast fails, CZ-proportional holds". That rests on a single shared-seed argmin plus a PUB bootstrap. That is exactly the selection-within-model-noise problem that ghost_event_scale's near-best and resolution rule exists to handle, and L122-123 admit the bootstrap does not cover it. The wording needs either a stated resolution unit or softer readings.
- L99. The CZ-proportional prediction for 055624 ("c between 2 and 5") contains the idle-only value (c near 2). On that run it is a weak falsifier.
- Chronology ("Recorded before part a's kernel finished") is preregistration content in an evidence note, and the git order backs it. This is acceptable here.

### ci/gates.json (+48 lines)

The branch adds six gates: core-330 to core-333, core-338 and core-339. See section 2 for the collisions. core-339 is recorded at 110 s, just under the 120 s `pr`-tier line on a 2-vCPU runner. After a regeneration, re-measure it on Kaggle CPU shards rather than on the build host.

### Retained Kaggle directories (results/kaggle/2026-10-16T1607*Z-gororoba-ghost-error-scale-{a,b,c})

- All three are complete: collect.json shows state COMPLETE, and exit.json shows returncode 0.
- Wall times were 26.2 ks, 19.4 ks and 9.2 ks.
- The only non-ASCII content is pip progress bars in the retained kernel logs. These are raw retained bytes, which is acceptable.
- No `/home/` path appears anywhere in the diff.

## 2. CI on 1a099fe

**What the REST data show:**

- `gh api .../pulls/147` returned `mergeable: false, mergeable_state: dirty` on the first read. A later read returned `unknown`, while GitHub recomputed after main moved to 4a383df.
- The workflow runs for the branch show one run only: ae4502d, `pull_request`, success, at 00:12Z.

**Why no run exists.** ci.yml has no skip rule. GitHub's own behavior is the cause: for a conflicted PR it cannot create `refs/pull/147/merge`, so it fires no `pull_request` event.

**How the conflict arose:**

- 6decf4a merged edf76a0, which lacks #142.
- e81342a (#142) then landed core-335..338.
- #144 landed core-327, core-330, core-331, core-340, core-341 and core-346..348.
- #146 landed core-332 and core-333.
- #156 also landed after that.

**What a merge produces.** `git merge-tree --write-tree origin/main 1a099fe` reports one content conflict, in ci/gates.json, in the hunk after core-334. A textual resolution that keeps both sides passes silently: ci/run_gates.py and ci/check_run_gates.py have no uniqueness check on gate names. It would leave five duplicated names:

| Branch gate | Taken on main by |
| --- | --- |
| core-330 | qi_zero_divisor_cases --replay |
| core-331 | qi_crosstalk_teleport_cases --replay |
| core-332 | qi_coupler_zz_map --check |
| core-333 | qi_coupler_zz_map --analyze |
| core-338 | linear_conjugation_search --merge |

core-339 is free.

**Free names on main:** core-339, core-342, core-343, core-344, core-345, core-349 and up. Main's AGENTS.md L656-657 cites core-330..333 as QI gates, so the branch's gates are the ones that move.

**Required resolution:**

1. Merge origin/main into the branch.
2. Keep every main gate.
3. Renumber the branch gates. One assignment: idle lint to core-342, idle check to core-343, event lint to core-344, event self-test to core-345, parts cmp to core-349, and parts --check keeps core-339.
4. Update the README citations.
5. Add a duplicate-name assertion to ci/check_run_gates.py, so the next collision fails CI.

**Downstream:** #148 (2aa0559) and #149 (cb36d78) claim core-330..339 as well, so they collide with main the same way. They need their own renumbering after #147 lands.

## 3. core-339 failure: root cause and fix

**Symptom on #148/#149:** `results/live/2026-10-11T152922.787095Z: docs/evidence/calibration/history/ibm_kingston/20261011T0757410700.json diagnostics differ`.

**Mechanism:**

- 078489b changed `diagnostics()` (ghost_error_scale.py L112-120) to keep one Target entry per unordered coupler.
- `validate()` (L450-459) rebuilds each snapshot's diagnostics, strips `model_infidelity_mean`, and requires exact equality with the retained entry.
- The parts were written by the 2298108 kernels, which counted each coupler in both orientations.

**Measured:** I rebuilt the diagnostics of every retained run (scratch script diag_diff.py, read-only). `couplers` is the only field that differs, and it halves exactly in 14 of the 15 snapshot entries:

| Part | Run | Retained -> rebuilt couplers |
| --- | --- | --- |
| a | 152922 | 72 -> 36 |
| a | 055624 | 10 -> 5 |
| b | 020454 | 8 -> 4 |
| b | 022433 | 8 -> 4 |
| b | 080216 | 6 -> 3 |
| b | 083417 | 6 -> 3 |
| b | 201757 | 6 -> 3 |
| c | 025444 | 86 -> 43 |
| c | 032011 | 48 -> 24 |
| c | 030748 | 6 -> 3 |
| c | 030903 | 48 -> 24 |
| c | 031229 (both snapshots) | 86 -> 43 |
| c | 070853 | 64 -> 32 |

- 070847 (0 couplers) matches.
- Reported CZ and readout means and every cap count are unchanged, because both orientations carry equal error.
- The `scaled.cap` vs `cz_cap`/`readout_cap` metadata difference does not fail the gate, because load() never reads it.

**Relation to the Codex thread.** The open thread 4300542973 names part_b and 080216 (6 vs 3). That is accurate, but it understates the scope: every part fails, and part_a fails first. part_a is first in the gate's argument list, and 152922 is its first run, which is exactly the run in the #148/#149 error. `scripts/codex_review_status.sh 147` reports `verdict=open-threads`, summary-head dfb4384, with this thread as the only unresolved one. The other eight threads were answered "Fixed in ..." and resolved.

**Which fix:**

- **Code change: none.** The code is right; the evidence is stale. Making `validate()` accept legacy counts would hide the defect.
- **Hand-editing the parts is ruled out.** core-338 requires the parts to equal the Kaggle outputs byte for byte, and retained kernel outputs are never rewritten.
- **A local regeneration is also ruled out.** It would break the kernel-output provenance that core-338 encodes.
- **The fix is to regenerate on Kaggle, and that is already in flight.** `kaggle kernels status` shows gororoba-ghost-error-scale-a, -b and -c RUNNING. The untracked directories results/kaggle/2026-10-17T0046{13,17,20}Z-* show they were pushed from dfb4384. `git diff dfb4384 1a099fe` over scripts/ghost_error_scale.py, scripts/ghost_run.py, gororoba_quantum/, kaggle_kernel/ and scripts/kaggle_run.py is empty, so they run head's code. The run sets equal the old parts' run sets.

**Expected outcome.** Points, means, floors and bootstrap inputs come back byte-identical to the old parts: 078489b's message claims the pooled grid reproduces the serial sweep on 080216 byte for byte. Only `couplers` and `scaled` change. After collection, diff old against new with a JSON key-by-key comparison. Any TVD difference is itself a finding, because it refutes the pooled-equals-serial claim on the larger runs.

**Cost:**

- Old wall times were 26.2 ks, 19.4 ks and 9.2 ks with serial grids and 4-thread Aer.
- The claimed 2.3x pooling gain puts the new runs at about 3.2 h, 2.3 h and 1.1 h. Allow 3 to 7 h.
- They occupy 3 of the 5 concurrent Kaggle CPU sessions and spend no GPU, TPU or IBM quota.
- Hands-on work afterwards is about 1 h.

**Work after collection:**

1. Run `kaggle_run.py collect` for the three kernels.
2. Copy each `output/output/repo/results/kaggle_out/ghost_error_scale_{a,b,c}.json` to docs/evidence/ghost_error_scale/part_{a,b,c}.json.
3. Repoint core-338 (renamed) at the 2026-10-17T0046*Z directories.
4. Decide what happens to the old 2026-10-16T1607*Z directories: keep them as superseded, or drop them from the gate.
5. Re-run `ghost_error_scale.py --report` and confirm the README tables are unchanged.
6. Rewrite README L74-77: the kernels ran dfb4384, and the bundle equals head for the closure.
7. Re-upload the gororoba-ghost-error-scale-parts dataset and update its record under results/kaggle/datasets/ with the new digests.
8. Run core-339 locally and the PR-tier shards.
9. Reply `Fixed in <sha>` on 4300542973, run resolve_answered_threads.sh, and request `@codex review`.

## 4. Untracked worktree content

| Path | State | Disposition |
| --- | --- | --- |
| results/kaggle/2026-10-16T232834Z-gororoba-ghost-event-scale-a1 | Complete: exit 0, environment.json and collect.json present. 055624, pad off, r = 1. Pushed from d7b7b72. Best (pad off, c 3, m 0.2, r 1), floor 0.0077. | Stale on two counts. Its m is the old depolarizing-after-event channel, which dfb4384 replaced. Its readout_fit binds part_a sha256 6e5f304d..., which the regeneration replaces, so `validate()` fails with "readout_fit differs". Do not land it as evidence. If a retained negative record is wanted, put it under results/kaggle only, with no gate. |
| ...232848Z-...-c1, ...232852Z-...-d1, ...232855Z-...-d2 (d7b7b72), ...233020Z-...-e2 (ae4502d) | Only kernel/ and submission.json exist. Kaggle reports CANCEL_ACKNOWLEDGED. | No output exists. Do not commit them. trash-put them, or keep them untracked as a push log. |
| results/kaggle/2026-10-17T0046{13,17,20}Z-gororoba-ghost-error-scale-{a,b,c} | Pushed from dfb4384. RUNNING. Only kernel/ and submission.json exist so far. | These are the core-339 fix. Commit them after `collect` writes collect.json, the output tree, exit.json and environment.json. |
| docs/notes/ghost-event-scale-020454-local.json and -local-report.json | Schema `ghost-event-scale-v1`: r fixed at 1, the old m. The current load() rejects them. They come from a build-host run, not Kaggle. | Do not commit them. They are superseded and fail the schema. docs/notes holds notes, and docs/evidence holds gated retained results. |
| docs/notes/ghost-event-scale-report.md | A session build report: "(not pushed)", "as instructed", "Not done, and why", commit hashes, host load averages. It describes the obsolete depolarizing m and fixed r. ASCII-clean. | Do not commit it, because it breaks the voice and chronology rules. Two parts are worth keeping. The padding-vs-idle-budget table can go into the evidence README in mechanism-first voice. The cost model can go into ghost_event_scale's Kaggle docstring paragraph, which already carries part of it. |

**The PR body is wrong in three places:**

- "Five Kaggle CPU kernels are running from this branch": one finished stale, and four were cancelled.
- "core-339 (73 s on the build host)" passes: it fails at head.
- "The kernels bundled 2298108": this changes with the regeneration.

**Commits that land this correctly, in order:**

1. `ci: merge origin/main and renumber the ghost gates to core-339, core-342..345, core-349`. This is the merge commit plus the renumbering, the README citations, and a duplicate-name check in ci/check_run_gates.py.
2. `ghost_error_scale evidence: retain the dfb4384 parts with one CZ entry per coupler`. This carries the new parts, the three 2026-10-17T0046*Z result directories, core-349 repointed, the README provenance paragraph, and the re-uploaded dataset record. Body: couplers halve, points and floors are byte-identical (state the diff result), and core-339 passes.
3. Optional, in this PR or the next: `ghost_event_scale: schema v3 for the pre-measurement flip`, plus `ghost_error_scale: lint and type gate, parallel validate`.
4. A later PR: re-push the full event-scale sweep (a, b, c, d, e) from the post-regeneration head against the new parts dataset. Retain its parts under docs/evidence/ghost_event_scale/ with a cmp gate and a reduced `--check --runs 080216` gate. Its cost is about a day of CPU sessions: the docstring estimates 10 to 25 ks per kernel, plus the 2.4x padded factor. Kernel b (055624 padded) is at risk of the 12 h limit.

## 5. Ranked list

### Must fix before merge

| # | Item | Effort |
| --- | --- | --- |
| M1 | Merge origin/main, resolve the ci/gates.json conflict, and renumber the five colliding gates (330, 331, 332, 333, 338). Update the README citations. Without this, no CI runs at all. | 30 min |
| M2 | Regenerate parts a, b and c, already running. Collect, copy into docs/evidence, repoint the cmp gate, re-diff the TVD fields, and update the README provenance (L74-77) and the dataset record. This closes Codex thread 4300542973. | 3-7 h Kaggle wall, 1 h hands-on |
| M3 | Rewrite the PR body: drop the "five kernels running" and "core-339 passes" claims, and name the regenerated-parts commit. | 10 min |
| M4 | Get one green CI round on the merged head, then one clean Codex round, since 1a099fe was never reviewed. | 1 CI round, plus the Codex wait |
| M5 | Keep the untracked docs/notes files and the stale or cancelled event-scale directories out of the PR. | 5 min |

### Should fix

| # | Item | Effort |
| --- | --- | --- |
| S1 | Add ruff, ruff format and mypy gates for scripts/ghost_error_scale.py, or add it to core-001, core-002 and core-039. Add a -O run of its --check. | 15 min |
| S2 | Run ghost_error_scale.validate and ghost_event_scale.validate/self_test prepare loops through parallel.ordered_map. This is the AGENTS.md parallel rule, and it shortens core-339. | 30-45 min |
| S3 | Bump ghost_event_scale SCHEMA to v3, or put the event model in PROVENANCE, so records made under the old m semantics fail on load. | 10 min |
| S4 | Add a duplicate-gate-name assertion to ci/check_run_gates.py. | 10 min |
| S5 | README statistics: flag the r = 0.5 fits on 070853, 020454, 022433 and 055624 as grid-edge fits. State the resolution unit behind the part-a readings, or reword "holds/fails" to readings at the shared-seed argmin. Note that the 055624 CZ-proportional interval contains the idle-only value. | 30 min |
| S6 | ghost_error_scale.load: compare seed, device, max_qubits and versions across parts, as event-scale's PROVENANCE check does. | 15 min |
| S7 | Remove the dead `circuit_shots` at ghost_error_scale.py L227. | 2 min |
| S8 | ghost_idle_budget docstring: one sentence on the one-qubit vs two-qubit infidelity units inside c_idle. | 5 min |

### Boundary, no fix needed

| # | Item | Reason |
| --- | --- | --- |
| B1 | event_positions treats a conditional rz after a terminal measure as a later use. | No retained circuit carries that pattern. State the boundary in a reply if Codex raises it. |
| B2 | The tolerance assumes per-row TV variance of 1/shots. | It is a conservative upper scale, inside the documented 5-sigma replay bound. |
| B3 | Non-ASCII pip progress bars in retained kernel logs. | They are raw retained bytes, and existing kernel directories on main carry the same. |
| B4 | readout_fits binds the whole part file's digest. | It is defensible. It only fixes the ordering: parts first, then event-scale kernels. |
| B5 | #148 and #149 also collide on core-334..339. | Their own follow-up, after #147 lands. |

## Not run

- Full `ghost_error_scale.py --check` (core-339). The diagnostic rebuild above isolates the failing field directly, and the full gate would only repeat that first failure.
- The CI shards. CI is the merge authority, and the branch currently has no mergeable ref.
- The comparison of modeled-infidelity rows after dedup: a background scratch job was still running when this report was written. The dedup keeps the first-listed orientation of each edge, and both orientations carry equal error and symmetric relaxation, so `model_infidelity_mean` is expected to match within 9-digit rounding. Confidence is moderate. The core-339 rerun of 080216 compares those rows exactly and settles it.

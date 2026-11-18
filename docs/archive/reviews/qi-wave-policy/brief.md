# Brief: hardware wave policy in qi_platform and the in-batch bracketed twin case (PR 881 head 088021c80)

Read first: the workspace AGENTS.md, then
gororoba-quantum/AGENTS.md and its ci/AGENTS.md. Work read-only: change no file
except by printing your report; never commit, push, stash, submit to a provider or start a cloud resource, and read no
token or key file; spawn no subagents. You may run git, and the pinned interpreter
`the CI-pinned interpreter` with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`;
keep each computation under 10 minutes, in a scratch directory outside every repository (for example under
`a scratch directory`; do not write inside the worktree). A random sample takes its seed from
`docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json` values at indices 900 to 910; name the indices you use.

Material: worktree `the session worktree`, branch
`qi-one-cz-null-twin-rule-v2`, commits `d80d0ba46..088021c80` (`git log --oneline faf9a05a7..088021c80`,
`git diff faf9a05a7..088021c80 -- scripts tests docs ci`; generated case directories under
`results/quantum_inspire/cases/pathion_one_cz_null_bracketed_*` are outputs of
`scripts/qi_pathion_one_cz_null_bracketed_cases.py`).

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. `scripts/qi_platform.py` (`HARDWARE_POLICIES`, `hardware_policy`, `hardware_limits`, `hardware_pause_state`,
   `hardware_admission`) applies `min(policy value, backend record value)`, leaves a manifest without `hardware_policy` on the
   legacy 3-circuit, 1-batch policy, and refuses an unknown policy before any service read. Status: computed (tests in
   `tests/scripts/test_qi_platform_wave_policy.py`, 36 passed). Falsifier: a manifest, backend record or service state that
   passes a guard it should refuse, or a legacy path whose behavior changed.
2. Under `wave-v1` a batch is admitted while fewer than 3 batches of the same backend type are in flight, the unfinished
   batches of that type set no pause, every finished batch keeps its pause, and an unfinished job on any other hardware type
   refuses. Status: computed (same tests). Falsifier: a state in which a wave submit skips the pause of a finished batch, or
   admits a fourth batch, or mis-groups a batch (for example a batch with zero listed jobs, a `planned` batch, a batch whose jobs
   finish between the two reads of `/batch_jobs` and `/jobs`).
3. Both submit routes (`qi_platform._submit`, `qi_platform_submission_deadline._submit`) read the one policy table through
   `hardware_admission`, and `scripts/check_qi_platform_retention.py` `batch_limit` reads the manifest's policy.
   Status: computed. Falsifier: any other file that still caps a hardware batch or queue with the legacy constants where a
   `wave-v1` manifest would reach it (`git grep -n -E 'HARDWARE_BATCH_CIRCUITS|HARDWARE_QUEUED_BATCHES'`).
4. In the bracketed twin case each twin pair runs in one batch `[readout-0, coin-0 twin, coin-1 twin, readout-1]` and the
   twin contrast is P1 - P0 with variance v(P1) + v(P0) (the batch offset c cancels). Status: proved by algebra in the
   module docstring; computed in `tests/scripts/test_qi_pathion_one_cz_null_bracketed.py`. Falsifier: a coin-conditioned
   selector dropout, or a context difference between the two twins, that the estimator would mis-handle.
5. Layout counts: 19 batches, 7 waves of at most 3 batches, 64 jobs, 2,555,904 shots, 1,521.0 to 1,675.8 s execution, 6
   pauses of 30 s. Status: computed (`design()`, test `test_jobs_shots_and_seconds_follow_plain_arithmetic`). Falsifier: a
   recount from `results/quantum_inspire/cases/pathion_one_cz_null_bracketed_tuna_17/batch-*/cases.json`.
6. Operating characteristics (`prediction.json`, `operating_characteristics`; CASE.md "Operating characteristics"): under
   a drift of 0.003 common to each pair the dropout and superposition-only worlds decide in 82.1 and 86.9 percent
   (>= 80, the preregistered power rule); under an independent drift of 0.003 on every contrast they decide in 72.5 and 77.1
   percent (< 80). Status: computed (20,000 series per world, seed = value 0 of the draw file named in the record).
   Falsifier: a flaw in the simulation model (`_series_label`, `operating_characteristics`) that moves either share across
   0.80, or an argument that the independent-drift model is the governing one, or the common-drift model is.
7. The QX series (4 batches of `[readout-0, coin-0 twin, coin-1 twin, readout-1, base]`, 5 circuits) keeps the QX control and
   bracket arithmetic. Status: computed on noiseless expected counts only; a local qxelarator run of this version is not run.

## Questions to answer

- Does any state of the account (Ry and Tuna-17 jobs, finished and unfinished, `planned` batches) let a wave submit exceed
  3 queued batches on one type, or skip the account-wide pause?
- Is the ordering claim true: submitting a wave's batches one after another keeps the platform queue in series order?
- Does anything else read the series layout (gates, ledgers, `docs/state`, notes) with the old 27-batch numbers?
- Conjecture where nothing is posited: failure modes of the wave guard under concurrent sessions (`SUBMIT_LOCK`).
- Defects: code, claims and records, with file:line.

Report ranked by consequence, every claim tied to a file:line, a command with its output, or a theorem name, each marked
proved, computed, measured or hypothesis. Print your report as your final answer, under 150 lines.

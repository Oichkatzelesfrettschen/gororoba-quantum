# Adversarial review brief: does the frozen per-seed correction table hold prospectively on Ascella job-09?

Review read-only: change no file, run no provider, network or job command, spawn no subagent. Read the workspace guide
`~/Projects/gororoba-workspace/AGENTS.md`, then `AGENTS.md` in the worktree
`~/worktrees/gororoba-quantum/quandela/ascella-prospective-correction` (branch `quandela/ascella-prospective-correction`,
commit `044995233`). Local Python reads of retained files are allowed with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3`; if no temporary directory is writable, reason from the files.

## Subject

The branch's three commits against `origin/main` (`git log origin/main..HEAD`, `git diff origin/main...HEAD`):

- `scripts/ascella_correction_score.py` (`--freeze`, `--score`, `--mesh-gate`, `--power`) and
  `tests/scripts/test_ascella_correction_score.py`,
- `docs/evidence/ascella-order-coefficients/correction-table.json`, `correction-power.json`, `correction-score-09.json`,
  `long-horizon-reading-08-09.json`,
- the changes to `scripts/ascella_coherence_request.py` (job-09, `Job.admit_statuses`) and
  `scripts/ascella_long_horizon_reading.py` (`PAIR_SEED`),
- the section "Prospective correction case (job-09)" of `docs/design/ascella-signed-coherence-conformance.md`, the
  "Per-seed correction" section of `docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md`, the
  plan `docs/state/plans/ascella-prospective-correction-case.json`, and the Belenos deferral paragraph in
  `docs/design/belenos-mesh-persistence-case.md`,
- the retained runs `results/quandela/runs/2026-11-07T042004Z-sim_ascella-ascella_signed_coherence-job-09-sim` and
  `results/quandela/runs/2026-11-07T042228Z-qpu_ascella-ascella_signed_coherence-job-09`, and for comparison job-02,
  job-03 and job-08 of `ascella_signed_coherence`.

## Questions

1. Prospectivity: was anything that decides the reading (table, estimator, rule, threshold 2, alpha, bootstrap,
   mesh tolerance, seed indices) chosen or changed after job-09's data existed? Use git history and timestamps
   (commit `2698c83c9`, job-09's `submission.json`).
2. Statistic: is R = var(d) / var(d - t) with a percentile bootstrap over meshes a sound decision statistic here? Is
   the 98 % interval honest given the table's own noise and the meshes' heteroscedastic counting variance? Recompute
   R, its interval and the noise-limited ratio from the retained runs.
3. Power: does `--power`'s generative model (true error S = t - n, persistent a S + c, redrawn rho S + f + c) reflect
   the data, and are the counting variances right for 32,768 samples?
4. Request and submission: does job-09 repeat job-02's seeds by name, does the order follow the stated draw rule, does
   `admit_statuses` change any earlier job's request or plan, and does the retained submission match the frozen body?
5. Readings: are `correction-score-09.json` and `long-horizon-reading-08-09.json` computed as the case states, and
   do the three earlier long-horizon readings still replay unchanged under `PAIR_SEED`?
6. Claims: does any sentence in the design outcome, the first-principles note or the PR text overstate what job-09
   shows (for example "about 90 %", "almost to the noise floor", the reach beyond 56 seeds of one setting)?

Report only findings verified against the files, most severe first, each with path and line, the evidence and the
concrete fix, under 900 words. Name the checks that found nothing.

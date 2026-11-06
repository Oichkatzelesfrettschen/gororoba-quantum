# Adversarial review brief: is Ascella's persistent per-seed mesh error real, and what does it mean?

Review read-only: change no file, run no provider, network or job command, spawn no subagent. Read the workspace guide
`~/Projects/gororoba-workspace/AGENTS.md`, then `AGENTS.md` in the worktree
`~/worktrees/gororoba-quantum/quandela/ascella-long-horizon-seed-repeat` (branch `quandela/ascella-long-horizon-seed-repeat`,
commit `782b189ad`). Local Python reads of retained files are allowed with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 python3`; if no temporary directory is writable, reason from the files.

## Subject

- `docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md` (the findings and assumption ledger),
- `docs/evidence/ascella-order-coefficients/long-horizon-controls.json` and `scripts/ascella_mesh_error_controls.py`,
- `docs/evidence/ascella-order-coefficients/long-horizon-reading-03-08.json`, `long-horizon-reading-02-08.json`,
  `long-horizon-rehearsal-02-03.json`, and `scripts/ascella_long_horizon_reading.py`,
- the earlier results they build on: `seed-repeat-reading.json` (job-03), `heater-coupling.json`, the replication
  case and `replication-sensitivity.json`, described in `docs/design/ascella-signed-coherence-conformance.md`
  (sections from "Perturbed-compilation case (job-02)" to "Long-horizon seed-repeat case (job-08)"),
- the retained runs under `results/quandela/runs/` for job-02, job-03 and job-08 of `ascella_signed_coherence`.

## Questions

1. Try to show that the persistent per-mesh error is an artifact of the analysis or of agent error rather than the
   chip: attribution of iterations to settings, the block counts and any background subtraction behind z, the
   anchor definition, the centering, the relabeling tests, the ceiling and reliability arithmetic, and the
   served-ideal computation. Recompute any number you doubt.
2. Try to show that it is a deterministic compiler or mathematical effect: could the served circuit differ from what
   the chip runs, could computed_input differ from the true input, could the X statistic's denominator or the mode
   mapping introduce a mesh-dependent bias with no physical error?
3. Test the interpretation "pattern kept, amplitude scaled down by about 11 %": is it supported, or do the slope,
   r against its ceiling and the standard deviations admit another reading (for example a redrawn share, a changed
   counting model, or job-02-based s_c being wrong for job-08)?
4. Test the per-seed correction: is the 7.7-fold variance reduction out of sample and fairly computed, and is the
   residual decomposition right?
5. Check every row of the assumption ledger and name missing assumptions.
6. Judge the section on 32- and 64-dimensional Cayley-Dickson algebras: is the mode-count argument right, and is
   there any route by which the repository's higher-dimensional work could improve accuracy here?

Report only findings verified against the files, most severe first, each with path and line, the evidence and the
concrete fix, under 900 words. Name the checks that found nothing.

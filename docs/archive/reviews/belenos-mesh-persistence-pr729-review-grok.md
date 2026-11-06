# Grok Build review of pull request #729 at 5deb80f95

Commit `5deb80f95` is a preregistered exact test of whether four retained Belenos meshes recur after recalibration. The statistics match the design. One drift-gate edge does not.

## Defect

**Serious.** `scripts/belenos_mesh_persistence.py:334` turns a missing two-sample z into zero, and line 338 still gives that block a degree of freedom.

`two_sample_z` (`scripts/belenos_mode_swap_interleaved.py:529`) returns `None` when either count is zero. `drift += (z or 0.0) ** 2` stores 0, and `chi2.sf(drift, len(blocks))` keeps 6 degrees of freedom. A new primary repeat with no single-click counts in a block then leaves D unchanged, so the drift p-value stays large and the gate at `p < 0.01` does not withhold the persistence reading. The same `None` is also returned when both shares are 0 or 1 and the standard error is 0. That case is a zero contribution. A zero count is a missing contrast. The retained packed set-4 primaries all have counts, so the design's quoted drift is unaffected: D = 13.133, chi-square p = 0.041. `tests/scripts/test_belenos_mesh_persistence.py` never builds a zero-count block.

Fix: if either new primary repeat has `n = 0`, stop with an explicit reading and skip the persistence statistic. Add 0 only when `two_sample_z` returns `None` with both counts positive.

## Checks that found nothing

1. **Statistic.** On the retained 6×4 table, centering, T, and the slope through the origin match `preregistered()` and the design. A self-replay has slope 1, 17 residual degrees of freedom, and p = 1/24^6. The upper bound is β + t(0.95, 17) × s / √∑e²_old. The 1e-12 comparison includes ties. Slots 4 and 5 are chip slots 4 and 5, and the secondary results get no reading. The design table matches the retained shares to three decimals (centered SD 0.0567 on 18 df). Clipping of the power-model shares never binds: under seed 21344, all 2,000 true shares at each slope stay inside (0.17, 0.89).

2. **Power.** Recomputing `power(21344, 0.05150455979158212)` reproduced every frequency in `results/quandela/belenos-mesh-persistence-power.json`. The seed is draw `2026-11-01T054809Z` index 2, value 21344, spawned once per slope. Primary cells use the pooled retained counts.

3. **Label-invariant test.** `sign_flip_cross_product` matches the new JSON fields: cross products −0.01136 and 0.02042, one-sided p 0.0625 (4/64) and 0.015625 (1/64). Flipping either mesh of any one input changes the permutation r and its p-value. Winner and loser correct-events per sample are 0.09764 and 0.10951. The gain over a random mesh is half the expected gap, 0.02303. The acceptance Wald statistic is 65.94. The five leading −Z herald patterns carry 8.2% to 15.9% of that input's chi-square, and each clicks a1 or q1. Five of the six top patterns click a1, with +Z the exception. The mesh-versus-null chi-square ratio is 6.17. The harmonic-mean sample-size ratio is 1.315.

4. **Repository rules.** The first-principles JSON only gains fields. The new seed is one unused ledger entry. The power draws run through `ordered_map`. The case document has a `docs/README.md` row. The power file is a labeled simulation, and `--analyze` reads collected counts.

5. **Hardware case.** The frozen manifest is five iterations, `max_samples` 150000, `max_shots` 450000, which `iteration_budgets` splits to 30,000 samples and 90,000 shots. The duration bound is 257.14 s against the 270 s margin. The credit ceiling is 1.09. The circuit hash equals job-09. The script's commands are `--build`, `--check`, `--power`, and `--analyze`. Submission stays a separate `qd_platform.py submit` after approval.

6. **Tests.** The convolution test matches a brute-force tail. A common shift must give slope 1 and the reading `persists`. A reversed pattern must not. The reversed block-key fixture fails a positional match. An identity mismatch withholds persistence. The tests do not pin α = 0.05, the 0.5 slope cutoff, the t degrees of freedom, or the drift gate. Those match the preregistration by inspection.

The persistence slope, the exact relabeling p-value, the power table, and the mesh-selection correction are doing what the case says. The drift gate needs an explicit stop when a primary repeat has no single-click counts.

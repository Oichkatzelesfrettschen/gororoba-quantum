# Readout-flip nuisance and the final design round of the phase-scan decision

Records behind rule R6 of [the phase-scan case](../../../../results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/CASE.md):
the selector flip of the predecessor (probability f that the selector reads flipped when d0 reads 0) fitted as one
nuisance parameter per series and world, over f = 0 to 0.06 in steps of 0.0025. Evidence class: numerical
simulation of the case's forward model with Gaussian sampling noise. Every seed here is a fixed pseudo-random
exploration seed, never a value of the QRNG draw; the case's recorded characteristics come from value 12 of that
draw through the generator.

## Files

| File | Content |
|---|---|
| `nuisance.py` | the decision with the flip as nuisance, reimplemented on `fit_batch()` (`finish()`), beside its flip-0 slice (rule R5); seed 20261117; `--check`, `--time`, `--run SERIES [--only TEXT]` |
| `nuisance_check.log`, `nuisance_time.log` | the checks (retention cache bit for bit, flip-0 slice equal to the R5 `decide()`, a flip-only truth recovered at its own flip) and the timing |
| `nuisance_first12.log`, `nuisance_rest.log`, `nuisance_gap.log` | label counts of 200 noisy series per scenario, both rules: 12 flip-plus-damping nulls; the truths, flip-0.05 nulls, flip-only nulls, true phases beside flip 0.0166 and the mixed scenarios (33); true phases beside flips 0.036 and 0.042 and drifting flips (14) |
| `final_round.py`, `final_round.log` | rule R5 against a model-light least-contrast gate, true phases beside a flip, and drifting truths; 300 noisy series per scenario, seed 20261119 |
| `r6_regression.py`, `r6_regression_value11.log`, `r6_regression_nuisance.log` | the R6 generator with the flip fixed at 0 reproduces the value-11 label counts of all 25 scenarios of `prediction_value11.json`; on the full grid its `decide()` reproduces `nuisance.py`'s labels on 20 series of 4 scenarios |
| `prediction_value11.json` | the prediction record of rule R5 (flip fixed at 0, separation 40) on value 11 of the draw, which R6 replaced |
| `record_diff.py`, `record_diff_wsl.log` | the value-11 record rebuilt on a second host: only the `limits` string, edited after the write, differs |

The scripts were written against the R5 generator; under the R6 generator `decide(..., flips=(0.0,))` is R5, and
the copies here call it that way. Run them from the repository root under the pinned interpreter with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`; part files and per-series records go to the ignored
`docs/local/rebuild/`. Runtime on a 32-thread host: about 7 minutes per 200-series scenario on one worker.

## Findings

1. Rule R5 reads `none_adequate` beside a readout flip whatever the phase: a true q12 phase of -0.18 rad beside
   flip 0.0166 read it in 290 of 300 series, beside 0.036 in 300; a coupler phase of -0.25 rad beside either flip
   in 300 of 300; a q8 phase of -0.25 rad beside 0.036 in 300 of 300 (`final_round.log`). The predecessor's
   readout points to a flip near 0.036 to 0.042, so under R5 the scan would most likely read `none_adequate`
   whatever its phase.
2. With the flip fitted, those truths read their own label: q12 199/200 (flip 0.0166), 196 and 199 (0.036), 200 and
   196 (0.042, both signs); coupler 199, 195 and 197; q8 180 (0.036) and 188 (0.042). Truths without a flip keep
   their counts within a few series (q12 -0.18: 198 against 199; q8 -0.25: 178 against 180).
3. No null reads a deciding label under either rule: 12 flip-plus-damping nulls, 4 flip-0.05 nulls, flip-only nulls
   of 0.025 and 0.05, and 4 nulls whose flip drifts during the series (0 to 0.036, 0 to 0.05, 0.0166 to 0.036 with
   CZ phase damping 0.13, 0.036 to 0.0166 with pulse phase damping 0.10), 200 series each. The fitted flip moves
   such series from `none_adequate` to `phase_unresolved` or `exact_parabola`.
4. A drifting flip costs power: a true q12 -0.18 rad or coupler -0.25 rad beside a flip drifting from 0 to 0.036
   reads its own label in 98 and 100 of 200 series, and `none_adequate` or `phase_mixed` otherwise, never another
   phase.
5. The mixed scenarios (z12 and z8c batches from different mechanisms) read `none_adequate` in 184 to 200 of 200
   under both rules and no deciding label.
6. The model-light least-contrast gate (a deciding q12 or q8 label only when a weighted parabola through the
   pooled z12 or z8c arms reaches 0 within 3 standard errors) fails at expected values: the z12 parabola's least
   value under a pure q12 phase of -0.18 rad is +0.0080 +- 0.0010, and the gate rejects 293 to 297 of 300 true q12
   labels. The refutation covers this five-point estimator; the forward model still cancels the phase exactly
   (`--self-test`). The gate is not part of any rule.
7. The fitted exact-world flip recovers a flip-only truth within 0.0004 beside pulse damping and lies 0.001 to
   0.002 high beside CZ phase damping, which it partly absorbs.

Cost: the R6 fit takes 25 times the fits of R5 per series (0.83 s against 0.044 s warm per series; 92 s against
4.7 s cold, under host load 15 to 57). The generator fits every series of a simulation at one flip before the next,
so a worker holds one flip's tables at a time.

# Case: packing the BDSC diagnostic request into fuller qpu:belenos jobs

Status: proposed on 2026-11-20 at the owner's direction ("cram as much in per job as the guides allow"); nothing is
built or submitted. The owner chooses a shape below; the chosen shape then needs its preregistration, a fresh QRNG
draw, the full review course and the owner's approval before any job, as the
[rehearsal record](../../../docs/design/quandela-successor-acquisition-rehearsal.md) requires for a change of the
frozen diagnostic request.

## Billing and limit

Each completed qpu:belenos diagnostic job billed 1.08 credits: `free_credits` on qpu:belenos moved 30.30742, 31.38742,
32.46742, 33.54742, 34.62742 across `2026-10-22T160023Z`, `2026-10-22T160340Z`, `2026-10-23T073329Z` and
`2026-10-23T081314Z` (`submission.json` before, `results.json` after). Each job used 960000 shots under an 80000-shot
cap per iteration, so the bill is 1 credit plus 1e-6 credit per shot of the largest iteration cap, not of the shots
used (`price_per_shot` 1e-06 in the platform catalogue of 2026-11-20). Iterations added inside one job at the same
cap therefore add no credit; a larger cap adds 1e-6 credit per cap shot. The job limit is `max_duration` 300 s on
both qpu:belenos and sim:belenos, and two retained qpu:belenos jobs of other shapes were canceled at it
(`2026-10-30T202246Z-qpu_belenos-teleportation_rehearsal-job-01` at 318 s,
`2026-10-31T060538Z-qpu_belenos-belenos_mode_swap_interleaved-job-00` at 339 s).

## Measured durations of the diagnostic shape

Each job holds 24 iterations of 40000 samples under an 80000-shot cap: one block of the frozen design is 2 templates x
4 seed slots x 6 states = 48 iterations in two jobs (`SLOTS`, `BLOCKS` and `LABELS` in `scripts/bdsc_diagnostic.py`).

| Platform | Runs | Reported duration | Seconds per iteration |
|---|---|---|---|
| qpu:belenos | the four runs above | 164, 164, 164, 171 s | 6.83 to 7.13 |
| sim:belenos | `2026-11-14T203218Z-...-b1-j1`, `2026-11-15T180000Z-...-b1-j2` | 300 s; 305 s canceled at the limit | about 12.5 |
| sim:belenos, 12 iterations | the three completed jobs of the [timing case](../../../docs/design/quandela-successor-acquisition-rehearsal.md#measured-timing-case-of-the-b1-shape) | 156 to 161 s | 13.0 to 13.4 |

The repository's QPU timing rule (`SECONDS_PER_ITERATION` 6.3 plus `SECONDS_PER_SAMPLE` 2.6e-5 per sample, in
`scripts/bdsc_diagnostic.py`) gives 7.34 s per iteration at 40000 samples, above every measured qpu:belenos job. A
sim:belenos job also failed twice with the provider error "Worker timeout"
(`2026-10-21T063940Z-sim_belenos-bdsc_qualification-tc-def-e1` and slot 4 of the timing case); slot 4 billed nothing,
and the earlier job's usage report does not separate its bill from its neighbors'.

## Shapes

Predicted seconds per job use the timing rule (upper value) and the measured 6.83 s per iteration (lower value);
`hypothesis:` duration is linear in iterations, with the falsifier a packed job that exceeds the rule's prediction.

| Shape | Per job | Predicted qpu:belenos seconds | Credits for four jobs | What changes |
|---|---|---|---|---|
| A, recommended | 36 iterations: 6 seed slots per template, 6 groups | 246 to 264 | 4.32 | `SLOTS` 4 to 6; 144 iterations, 1.5 times the frozen 96 |
| B | 42 iterations: 7 seed slots per template | 287 to 308 | 4.32 | `SLOTS` 4 to 7; the rule's prediction exceeds the limit |
| D | 24 iterations of about 150000 samples, cap 300000 | about 245 by the rule; no measured rate at this sample count | 5.20 (1.30 per job) | `TRIALS` 40000 to 150000; the same groups, 3.75 times the samples per state |
| frozen | 24 iterations of 40000 samples | 164 to 171 measured | 4.32 | none |

A job holds whole groups of six states, and a block holds two jobs, so fewer jobs per block break the
`require_schedule` rule that job 2 of a block starts after job 1 ends. Shape A buys more independent compilations
(seed slots); shape D buys more samples per state at the same compilations. `hypothesis:` with `SLOTS` 6 the block
schedule, the one-hour gap and the matched check of the frozen design apply unchanged, and the decision rules keep
their thresholds; `DRAW_VALUES` grows from 100 to 150 and the power statement of the preregistration changes. Shape A
leaves 36 s of margin under the limit by the rule and 54 s by the measured rate.

## Rehearsal

A 36-iteration job needs about 480 s on sim:belenos, so the simulator cannot rehearse shape A whole. The rehearsal
runs the shape-A request split into two 18-iteration jobs (about 240 s each) for 2.0 credits, which exercises build,
plan, submit, collect and admission; the qpu:belenos duration stays a prediction until the first QPU job.

## What the chosen shape needs before approval

1. Changes in `scripts/bdsc_diagnostic.py` (`SLOTS` or `TRIALS`, `DRAW_VALUES`, the instance layout and the analysis
   that reads it) and `scripts/bdsc_diagnostic_acquisition_case.py` (the job split), with tests, under the
   repository's review course; the frozen diagnostic record keeps its bytes, so the change lands as a versioned
   successor.
2. A fresh ANU draw of the new size (`docs/evidence/anu_qrng/draw-2026-11-15T190401Z.json` is unclaimed and reserved
   for the reviewed successor, and holds 100 values, fewer than 150).
3. The preregistration of the diagnostic updated for the shape, with its power statement recomputed.
4. The pre-flight of `qd_platform.py plan` on the built tree, then the owner's approval of the jobs.

# Case: packing the BDSC diagnostic request into fuller qpu:belenos jobs

Status: proposed on 2026-11-20 at the owner's direction ("cram as much in per job as the guides allow"); nothing is
built or submitted. The owner chooses a shape below; the chosen shape then needs its preregistration, a fresh QRNG
draw, the full review course and the owner's approval before any job, as the
[rehearsal record](../../../docs/design/quandela-successor-acquisition-rehearsal.md) requires for a change of the
frozen diagnostic request.

## Billing and limit

A qpu:belenos job bills 1 credit plus 1e-6 credit per shot up to the largest iteration cap (`price_per_shot` 1e-06 in
the platform catalogue of 2026-11-20; the diagnostic receipts carry `max_credits` 1.08 for an 80000-shot cap). The
job limit is `max_duration` 300 s on both qpu:belenos and sim:belenos. The bill does not grow with the iteration
count, so iterations added to a job that stays inside 300 s cost nothing.

## Measured durations of the diagnostic shape

Each job holds 24 iterations of 40000 samples under an 80000-shot cap (four groups of six states).

| Platform | Runs | Reported duration | Seconds per iteration |
|---|---|---|---|
| qpu:belenos | `2026-10-22T160023Z-...-b1-j1`, `2026-10-22T160340Z-...-b1-j2`, `2026-10-23T073329Z-...-b2-j1`, `2026-10-23T081314Z-...-b2-j2` | 164, 164, 164, 171 s | 6.83 to 7.13 |
| sim:belenos | `2026-11-14T203218Z-...-b1-j1`, `2026-11-15T180000Z-...-b1-j2` | 300 s; 305 s canceled at the limit | about 12.5 |
| sim:belenos, 12 iterations | the three completed jobs of the [timing case](../bdsc_diagnostic_billing_rule_sim_belenos/CASE.md#run-record) | 156 to 161 s | 13.0 to 13.4 |

The quantum processor runs this shape about twice as fast as the simulator. A sim:belenos job also failed twice with
the provider error "Worker timeout" (`2026-10-21T063940Z-sim_belenos-bdsc_qualification-tc-def-e1` and slot 4 of the
timing case); slot 4 billed nothing, and the earlier job's usage report does not separate its bill from its neighbors'.

## Shapes

Iterations come in groups of six states, so a job holds a multiple of six. Predicted seconds use 6.83 to 7.13 s per
iteration on qpu:belenos (`hypothesis:` linear in iterations; falsifier: a packed job whose duration exceeds the
prediction by more than 10 %).

| Shape | Jobs x iterations | Predicted qpu:belenos seconds per job | Credits | Iterations bought |
|---|---|---|---|---|
| A, recommended | 4 x 36 (six groups per job) | 246 to 257 | 4.32 (4 x 1.08) | 144, 1.5 times the frozen request |
| B | 4 x 42 | 287 to 299 | 4.32 | 168; under 13 s of margin, so a slow job reaches the limit |
| C | 3 x 32 | 219 to 228 | 3.24 | 96, the frozen total; three jobs break the two-block schedule of `bdsc_diagnostic.require_schedule` |
| frozen | 4 x 24 | 164 to 171 measured | 4.32 | 96 |

Shape A keeps the two blocks of two jobs, the one-hour block gap and the matched check, so `require_schedule` and the
decision rules of the diagnostic stand; it adds two groups per job, each with its own compilation slot from the new
draw, and leaves 43 to 54 s of margin under the limit. Shape C saves one credit but needs a new schedule design.

## Rehearsal

A 36-iteration job needs about 480 s on sim:belenos, so the simulator cannot rehearse shape A whole. The rehearsal
runs the shape-A request split into two 18-iteration jobs (about 240 s each) for 2.0 credits, which exercises build,
plan, submit, collect and admission; the qpu:belenos duration stays a prediction until the first QPU job.

## What the chosen shape needs before approval

1. A builder change in `scripts/bdsc_diagnostic_acquisition_case.py` for six groups per job, with tests, under the
   repository's review course.
2. A fresh ANU draw for the compilation slots (`docs/evidence/anu_qrng/draw-2026-11-15T190401Z.json` is unclaimed and
   reserved for the reviewed successor).
3. The preregistration of the diagnostic updated for the iteration count, with its power statement recomputed.
4. The pre-flight of `qd_platform.py plan` on the built tree, then the owner's approval of the jobs.

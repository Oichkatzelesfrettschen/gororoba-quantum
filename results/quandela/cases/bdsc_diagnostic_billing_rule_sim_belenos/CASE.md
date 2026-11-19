# Case: sim:belenos b1 completion-time repeat (timing only)

Status: written case awaiting the owner's approval; nothing has been submitted to any backend, the simulator included.
The owner approved writing this case on 2026-11-16 (leftover W-160, "approve a controlled sim:belenos b1 repeat or drop the
hypothesis") and again on 2026-11-19; the approval of the run itself is the open step. Request files, the successor builder
variant and the run directory do not exist yet, and no command below sends a job.

## Retained records

The two sim:belenos jobs of the b1 shape belong to this case's tree, `bdsc_diagnostic_billing_rule_sim_belenos`, and to
[the rehearsal record](../../../../docs/design/quandela-successor-acquisition-rehearsal.md) ("Measured rehearsal results" and
"Measured second rehearsal job"). Each holds 24 iterations of 40000 samples under an 80000-shot cap, 960000 samples in all.

| Job | Run | Groups | Created (UTC) | Collected (UTC) | Reported duration | Outcome |
|---|---|---|---|---|---|---|
| `b1-j1`, 544e010f | `results/quandela/runs/2026-11-14T203218Z-sim_belenos-bdsc_diagnostic-b1-j1` | out-s0, out-s1, rev-s2, rev-s3 | 2026-11-14 20:32:51 | 2026-11-14 20:38:13 | 300 s | completed, 24 of 24 iterations, progress 1.0 |
| `b1-j2`, fa2da727 | `results/quandela/runs/2026-11-15T180000Z-sim_belenos-bdsc_diagnostic-b1-j2` | out-s2, out-s3, rev-s0, rev-s1 | 2026-11-15 18:47:36 | 2026-11-15 18:53:11 | 305 s | canceled, "Max duration reached (300.0 seconds)", progress 0.9587, 23 iterations plus a missing 24th (920000 of 960000 samples) |

Both jobs ran with the token idle (`max_concurrent_jobs` 1, `max_jobs_in_queue` 1), `max_duration` 300 and `price_per_shot`
0.0 on the platform record, and both billed 1.0 credit (usage report: jobs 24 to 25 and 25 to 26 on sim:belenos). The
QPU timing rule of 6.3 s plus 2.6e-05 s per sample per iteration predicted 176.16 s for each, and both exceeded it.

## Hypothesis

`hypothesis:` the completion time of the 24-iteration b1 shape sits at the platform's 300 s limit, so whether a job
completes depends on a spread of a few percent that the records cannot attribute. Derived rates, from the table: j1 finished
in at most 300 s, at most 12.5 s per iteration; j2 completed 23 iterations plus 0.96 of the 24th in 305 s, about 13.2 s per
iteration (305 s divided by 24 x 0.9587), at least 6 % slower. Two sources of that gap remain open, because the jobs differ
in request (different seed groups and template order) and in time (a day apart) and the records hold no iteration
timestamps or provider load figures.

- Request cost: some (template, seed) groups cost more per iteration than others.
- Service variation: the same request takes a different time on a different run, through provider load or compilation
  caching.

A third reading, that the 24-iteration shape needs about 300 s and j1 stopped at the limit by coincidence, is the null of
this case: no per-request or per-run spread beyond a few percent, and the shape does not fit.

Falsifiers, each from the contrast it names in "Decision rules": request cost fails when repeats of the two requests agree
with each other; service variation fails when repeats of one request agree with each other.

## What the run measures

Wall time and progress of 12-iteration jobs built from the b1 groups, two requests each run twice. A 12-iteration job
carries two groups of six states (f, g, +, -, +i, -i), costs about half the retained jobs, and so completes inside 300 s
whatever the spread. A simulation of the provider cannot answer it: the quantity is the provider simulator's own execution
time. The jobs' counts are not analyzed and no diagnostic branch reads them; this case does not replace the frozen
diagnostic request, whose change of shape needs its own preregistration, resource estimate, review and approval.

| Request | Groups (iterations in order of the builder) | Iterations | Samples per iteration | Cap per iteration |
|---|---|---|---|---|
| P1 | out-s0, out-s1 (j1's first two groups) | 12 | 40000 | 80000 shots |
| P2 | rev-s0, rev-s1 (j2's last two groups, where the overrun fell) | 12 | 40000 | 80000 shots |

The caps equal the retained caps, so per-iteration cost is unchanged (retained iterations used 40000 or 40001 shots). On
sim:belenos the cap does not enter the bill (price 0.0 per shot), and equal caps are the optimum of
[ascella-job-economics](../../../../docs/design/ascella-cz-tomography-reference-case.md) in the same way: the largest cap
sets the bill and nothing else binds. The order of jobs is P1, P2, P1, P2, so a slow provider drift touches both requests
alike. Jobs run one at a time (`max_concurrent_jobs` 1), each submitted after the previous one is collected.

Recorder. For each job the run polls the job's status through the platform client at intervals of at most 10 s from
submission to the terminal state and writes (UTC time, status, progress, progress message) to a log in the run directory.
Progress steps of 1/12 give per-iteration times, the telemetry the retained runs lack. If the client cannot poll progress,
the contrasts below hold at job level on the reported duration and the per-iteration reading is lost.

## Expected seconds and credits

| Quantity | Value | Source |
|---|---|---|
| Per-iteration time | 12.2 to 13.3 s | retained rates above; 12.2 s if a fixed start-up of 6.3 s is separated (300 - 6.3 over 24) |
| Seconds per job | 147 to 160 s | 12 iterations at the per-iteration range |
| Seconds, four jobs | 590 to 640 s of execution; ceiling 1200 s (4 x 300) | `max_duration` 300 on the platform record |
| Credits per job | 1.0 | both retained jobs, usage report; sim:belenos price 0.0 per shot |
| Credits, four jobs | 4.0; ceiling 4.32 (4 x 1.08, the receipt `max_credits` of the retained jobs) | same |

A job at the limit is canceled and still bills 1.0 credit (the `b1-j2` usage report), so the ceiling is the bill.

## Pre-flight record

1. Hypothesis: the b1 completion time varies near the 300 s limit through request cost, service variation, or neither (the
   shape needs about 300 s).
2. Quantity: reported `duration` of each job (seconds) and, from the status log, seconds per iteration; the provider's
   `duration` field is unread beyond the retained values, and its definition (queue, start-up and collection included or
   not) is marked unread.
3. Falsifier: repeats of P1 and of P2 that each agree within 5 % and agree with each other falsify both sources; repeats of
   one request that disagree by more than 10 % falsify the null.
4. Predicted outcome and budget: 150 to 160 s per job, 4 jobs, 4.0 credits, 590 to 640 s; power is modest (two repeats per
   request) and detects a spread of 10 % or more, not 3 %.
5. Each result's consequence: see "Decision rules".

## Comparison with the retained runs

Per job and per iteration, a 12-iteration job at 12.2 to 13.3 s per iteration predicts 147 to 160 s. The two retained jobs
and the four new ones fit a line of seconds against iterations, T = a + b n, with a, the fixed start-up, now separable
from b (the retained pair sits at one iteration count and fixes only their ratio). A new per-iteration rate outside 12.2 to
13.3 s, in either direction, is a deviation and is recorded as the finding before any rule below is applied.

## Decision rules

Let d(P) be the relative difference of the two repeats of request P, and m1, m2 the repeat means of P1 and P2.

| Outcome | Reading | Next step |
|---|---|---|
| d(P1) or d(P2) above 10 % | service variation supported: one request takes different times on different runs | any 24-iteration job needs margin; cap iterations per job near 16 (about 200 s at 12.5 s) and record the spread as a provider property |
| d(P1) and d(P2) at most 5 %, and |m1 - m2| / mean above 10 % | request cost supported: groups differ in cost | read the status logs for the costly groups; reorder or split them in a successor preregistration |
| d(P1) and d(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 24 x (mean seconds per iteration) above 295 s | the null: the 24-iteration shape does not fit; j1's 300 s was the limit | drop the spread hypothesis, size every b1 successor from the measured rate, and record that the shape needs fewer iterations per job |
| d(P1) and d(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 24 x (mean seconds per iteration) at most 295 s | both retained jobs were outliers of one provider state | drop the hypothesis as unreproduced; one repeat of `b1-j2` in full is the only remaining test and needs its own approval |
| any other pattern (for example d between 5 % and 10 %) | inconclusive at this power | no change to the frozen request; report and record an open row |
| any job reaching the limit or failing | the stop condition below fires | read the status log, record the failure, do not rerun without approval |

Dropping the hypothesis closes its ledger row with the evidence of this case; an inconclusive outcome keeps the row open.

## Stop conditions

- `scripts/qd_platform.py plan` refuses the platform or the rebuilt tree.
- A job body differs from the empty mitigation list of the retained request, or a result is not an integer BSCount.
- A job's status is canceled or failed, or the next job would start before the previous one is collected.
- Spent credits reach 4.32 or elapsed execution seconds reach 1200.

## Implementation steps before approval

The retained tree refuses a later plan on the changed digest of `scripts/qd_platform.py`. The case needs a successor
builder variant that emits P1 and P2 from the frozen group definitions with the iteration subset, a plan whose output restates
credits and seconds above, the review packet and the free ANU draw the builder requires (the unclaimed draw of 2026-11-15 in
`docs/evidence/anu_qrng/` serves, or a fresh free draw per the QRNG guide). None of these exists; this file asks only for
the written-case approval.

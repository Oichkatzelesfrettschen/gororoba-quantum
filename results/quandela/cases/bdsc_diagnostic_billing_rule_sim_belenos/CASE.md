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
completes depends on a spread of a few percent that the records cannot attribute. Job-level facts, from the table: j1
completed 24 of 24 iterations with reported duration 300 s; j2 was canceled at the limit with reported duration 305 s and
23 complete iterations (920000 / 40000; the progress value 0.9587 is not read as a fraction of an iteration), so no
per-iteration latency is identified by the records. Two sources of that gap remain open, because the jobs differ
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

Wall time of 12-iteration jobs built from the b1 groups, two requests with three runs each (six jobs). A 12-iteration job
carries two groups of six states (f, g, +, -, +i, -i) and costs about half the retained jobs. A simulation of the provider
cannot answer it: the quantity is the provider simulator's own execution time. The jobs' counts are not analyzed and no
diagnostic branch reads them; this case does not replace the frozen diagnostic request, whose change of shape needs its
own preregistration, resource estimate, review and approval.

| Request | Groups (iterations in order of the builder) | Iterations | Samples per iteration | Cap per iteration |
|---|---|---|---|---|
| P1 | out-s0, out-s1 (j1's first two groups) | 12 | 40000 | 80000 shots |
| P2 | rev-s0, rev-s1 (j2's last two groups, where the overrun fell) | 12 | 40000 | 80000 shots |

The caps equal the retained caps, so per-iteration cost is unchanged (retained iterations used 40000 or 40001 shots). On
sim:belenos the cap does not enter the bill (price 0.0 per shot; completed simulator jobs bill a fixed 1.0 credit). The
order of jobs is counterbalanced, P1 P2 P2 P1 P1 P2 (blocks P1 P2, P2 P1, P1 P2), so each request occupies early and late
slots equally often. Residual assumption: order, warm-cache and odd/even service state remain only partly balanced, so
outcomes read as more consistent with request cost or with service variation, not as causal separation. Jobs run one at a
time (`max_concurrent_jobs` 1), each submitted after the previous one is collected.

Recorder. For each job the run polls the job's status through the platform client at intervals of at most 10 s and writes
(UTC time, status, progress, progress message) to a log in the run directory. Only job-level timing (submission to terminal
state, and the reported duration) is analyzed; progress transitions are retained as logged but are not read as
iteration completions unless validated against the completed result entries of that job.

## Expected seconds and credits

| Quantity | Value | Source |
|---|---|---|
| Seconds per job | about 150 s (hypothesis: half of the retained 300 and 305 s) | retained durations; no per-iteration latency is identified by the records |
| Seconds, six jobs | about 900 s expected; execution-limit budget 1800 s (6 x 300 s platform cancellation threshold); reported duration of a canceled job can reach 305 s each (1830 s for six) | `max_duration` 300 on the platform record; `b1-j2` reported 305 s |
| Wall clock | not bounded by the above: it includes submission, polling and collection between jobs and is recorded separately | |
| Credits per job | 1.0 measured bill of a completed job | both retained usage reports; sim:belenos price 0.0 per shot |
| Credits, six jobs | 6.0 expected; authorization cap 6.48 (6 x 1.08, the receipt `max_credits` of the retained jobs; the receipt `credit_ceiling` is 1.0 per job) | same |

The measured bill of each retained job is 1.0 credit, and the 1.08 is an authorization cap, not a bill. Retained
`b1-j2` was canceled at the limit and its usage report also advanced by one job and 1.0 credit; a canceled job may
leave credits unchanged elsewhere, so each job's bill is read from the usage report.

## Pre-flight record

1. Hypothesis: the b1 completion time varies near the 300 s limit through request cost, service variation, or neither (the
   shape needs about 300 s).
2. Quantity: reported `duration` of each job (seconds); the provider's `duration` field is unread beyond the retained
   values, and its definition (queue, start-up and collection included or not) is marked unread.
3. Falsifier: three replicates of P1 and of P2 whose relative ranges are each at most 5 % and whose means agree within
   5 % falsify both sources; a relative range above 10 % within one request falsifies the null.
4. Predicted outcome and budget: half the retained duration, about 150 s per job (hypothesis: the retained 300 s and 305 s
   divided by two; no fixed start-up is separated), six jobs, 6.0 credits, about 900 s of execution; with three replicates
   the design flags an observed spread above 10 %, not 3 %.
5. Each result's consequence: see "Decision rules".

## Comparison with the retained runs

The retained jobs record job-level durations only: 300 s for 24 of 24 iterations (j1) and 305 s for 23 complete iterations
(920000 of 960000 samples at 40000 per iteration, j2), with no per-iteration latency identified. The six new jobs of 12
iterations are compared with the retained pair at job level: a duration of 12 iterations well below half of 300 s, or above
it, is a deviation and is recorded as the finding before any rule below is applied. Start-up and per-iteration cost are
not separated, because iteration count changes together with request composition.

## Decision rules

Each request has three replicates. Let s(P) be the relative range of its three durations, (max - min) / mean, and m1, m2 the
replicate means of P1 and P2. The order is counterbalanced at the block level (see above), and the readings are "more
consistent with" request cost or service variation, because order, warm-cache and odd/even service state are only
partly balanced.

| Outcome | Reading | Next step |
|---|---|---|
| s(P1) or s(P2) above 10 % | observed spread above 10 %: more consistent with service variation (one request takes different times on different runs) | any 24-iteration job needs margin; record the spread as a provider property and size by the longest observed duration |
| s(P1) and s(P2) at most 5 %, and |m1 - m2| / mean above 10 % | more consistent with request cost: groups differ in cost | read the job records for the costly groups; reorder or split them in a successor preregistration |
| s(P1) and s(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 2 x (mean duration) above 295 s | the null: the 24-iteration shape needs about 300 s | drop the spread hypothesis, size every b1 successor from the measured duration, and record that the shape needs fewer iterations per job |
| s(P1) and s(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 2 x (mean duration) at most 295 s | both retained jobs were outliers of one provider state | drop the hypothesis as unreproduced; one repeat of `b1-j2` in full is the only remaining test and needs its own approval |
| any other pattern (for example s between 5 % and 10 %) | inconclusive at this power | no change to the frozen request; report and record an open row |
| any job reaching the limit or failing | the stop condition below fires | read the job record, record the failure, do not rerun without approval |

Three replicates flag an observed spread above 10 %; no power calculation is made, so a smaller spread is neither detected
nor excluded. Dropping the hypothesis closes its ledger row with the evidence of this case; an inconclusive outcome keeps
the row open.

## Stop conditions

- `scripts/qd_platform.py plan` refuses the platform or the rebuilt tree.
- A job body differs from the empty mitigation list of the retained request, or a result is not an integer BSCount.
- A job's status is canceled or failed, or the next job would start before the previous one is collected.
- Spent credits reach 6.48 (the authorization cap), or the sum of provider-reported durations reaches 1800 s (6 x 300 s,
  the platform cancellation threshold per job). The reported duration of a canceled job can exceed 300 s (305 s observed),
  so the stop is checked after each job and wall-clock elapsed time is recorded separately.

## Implementation steps before approval

The retained tree refuses a later plan on the changed digest of `scripts/qd_platform.py`. The case needs a successor
builder variant that emits P1 and P2 from the frozen group definitions with the iteration subset, a plan whose output restates
credits and seconds above, the review packet and the free ANU draw the builder requires (the unclaimed draw of 2026-11-15 in
`docs/evidence/anu_qrng/` serves, or a fresh free draw per the QRNG guide). None of these exists; this file asks only for
the written-case approval.

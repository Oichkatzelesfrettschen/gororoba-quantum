# Case: sim:belenos b1 completion-time repeat (timing only)

Status: approved by the owner on 2026-11-20 and run the same day; stopped after slot 4 by its own stop condition. The
read-only plan (`docs/archive/reviews/bdsc-diagnostic-timing/plan-2026-11-20.json`) read 1.0 credit per job, price 0.0
per shot and no mitigations before the approval. The section "Run record" holds the outcome; the requests P1 and P2
live in `results/quandela/cases/bdsc_diagnostic_timing_sim_belenos/`, built by `scripts/bdsc_diagnostic_timing_case.py`.
## Run record

The submit loop of "Implementation steps before approval" ran on 2026-11-20 from commit `b67d19f60`, one job at a
time with the token idle. The usage counter of sim:belenos (`free_credits` and `nb_jobs` in each run's
`submission.json` and `results.json`) reads the bill of each job.

| Slot | Request | Job | Run | Reported duration | Status | Bill |
|---|---|---|---|---|---|---|
| 1 | P1 | 7266d221 | `results/quandela/runs/2026-11-20T231935Z-sim_belenos-bdsc_timing-p1` | 159 s | completed | 1.0 credit (24.0 to 25.0) |
| 2 | P2 | 04d355e3 | `results/quandela/runs/2026-11-20T232303Z-sim_belenos-bdsc_timing-p2` | 161 s | completed | 1.0 credit (25.0 to 26.0) |
| 3 | P2 | 0c0e22c7 | `results/quandela/runs/2026-11-20T232631Z-sim_belenos-bdsc_timing-p2` | 156 s | completed | 1.0 credit (26.0 to 27.0) |
| 4 | P1 | f141e80d | `results/quandela/runs/2026-11-20T233005Z-sim_belenos-bdsc_timing-p1` | 82 s | error, "Worker timeout" | none (27.0 to 27.0; `nb_jobs` 29 to 30) |

Slot 4 reached progress 0.5007 at 23:32:02 UTC, 100 s after submission, and its status log (`status-log.jsonl`, one
read every 10 s) shows that value and status `running` unchanged for 20 minutes until the job ended `error` with
status message "Worker timeout" at about 23:52 UTC. The platform's 300 s limit did not end it, and its reported
duration of 82 s counts compute time only, not the stalled interval. The stop condition on a failed job ended the case
before slot 5: three jobs completed and 3.0 credits were spent of the 6.48 authorized.

Each completed duration lies above 150 s, so each is a deviation under "Comparison with the retained runs". `analyze`
reads six runs and does not run on three; no decision row of "Decision rules" applies, and the request-cost and
service-variation contrasts stay unmeasured (one P1 replicate, two P2 replicates). Measured: the 12-iteration requests
took 156 to 161 s, above half the retained 300 s. `hypothesis:` a 24-iteration b1 job needs about 320 s and does not
fit the 300 s limit; the falsifier is a 24-iteration job that completes below 300 s, as `b1-j1` did once at 300 s.
A resumed or packed successor needs its own written case and approval.

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
| P1 | out-s0, out-s1 (two of j1's four groups) | 12 | 40000 | 80000 shots |
| P2 | rev-s0, rev-s1 (two of j2's four groups; the cancelled 24th iteration of j2 is out-s2-pi, which P2 omits) | 12 | 40000 | 80000 shots |

Each retained job holds four groups; P1 omits rev-s2 and rev-s3 (j1) and P2 omits out-s2 and out-s3 (j2), and the
settings of `b1-j2` are in shuffled order, so the group sequence of the builder does not locate the overrun. The
retained `cases.json` lists out-s2-pi last (compilation seed 20439) and the results hold 23 iterations. The six jobs
therefore measure the durations of P1 and P2 only; no outcome below bounds the retained 24-iteration requests.
The caps equal the retained caps, so per-iteration cost is unchanged (retained iterations used 40000 or 40001 shots). On
sim:belenos the cap does not enter the bill (price 0.0 per shot; completed simulator jobs bill a fixed 1.0 credit). The
order of jobs is P1 P2 P2 P1 P1 P2 (blocks P1 P2, P2 P1, P1 P2): P1 takes slots 1, 4 and 5 (mean slot 3.33) and P2 slots 2, 3
and 6 (mean 3.67); three replicates per request cannot balance six slots, so P1 runs slightly earlier on average. Residual assumption: order, warm-cache and odd/even service state remain only partly balanced, so
outcomes read as more consistent with request cost or with service variation, not as causal separation. Jobs run one at a
time (`max_concurrent_jobs` 1), each submitted after the previous one is collected.

Recorder. For each job the run reads the job's status through the platform client on a fixed 10 s cadence (a read slower
than the cadence delays the next) and writes (UTC time, status, progress, progress message) to a log in the run directory.
Only job-level timing (submission to terminal
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
iterations are compared with the retained pair at job level: a duration of 12 iterations below 135 s (10 % under half of 300 s), or above
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
| s(P1) and s(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 2 x (mean duration) above 295 s | inconclusive for the original 24-iteration requests: P1 and P2 omit the groups rev-s2, rev-s3, out-s2 and out-s3, so doubling a 12-iteration duration bounds neither retained request | keep the hypothesis open for the original requests; no change to the frozen request; a full 24-iteration repeat needs its own approval |
| s(P1) and s(P2) at most 5 %, |m1 - m2| / mean at most 5 %, and 2 x (mean duration) at most 295 s | the doubled P1 and P2 durations fit under the limit; this says nothing about the omitted groups, so the retained requests stay inconclusive and the outliers are not attributed | keep the hypothesis open for the original requests; one repeat of `b1-j1` and `b1-j2` in full is the only remaining test and needs its own approval |
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

The retained tree refuses a later plan on the changed digest of `scripts/qd_platform.py`, so the requests live in a tree of
their own.

- Builder: `scripts/bdsc_diagnostic_timing_case.py build` writes `results/quandela/cases/bdsc_diagnostic_timing_sim_belenos/`:
  `case.json` (requests, slot order, expected seconds and credits, stop conditions and decision thresholds of this file)
  and `p1/`, `p2/`. Each request keeps the settings of its groups from the retained `b1-j1` or `b1-j2` manifest byte for
  byte and in the retained iteration order, with 12 iterations, `max_samples` 480000 and `max_shots` 960000; its
  `circuit.json` is the retained file. `successor_sources` binds the builder, `qd_platform.py`, `oq_platform.py` and
  `qd_records.py`; a change to one of them before the first run calls for `build` again, and `check` compares the tree
  with a fresh build byte for byte.
- QRNG: the case takes no new value. The settings carry the compilation seeds and draw indices of
  `docs/evidence/anu_qrng/draw-2026-11-14T203208Z.json`, which the retained jobs consumed, and a seed that reproduces a
  retained request is an identifier (AGENTS.md, "Seeds"). The earlier text of this section named a free draw because it
  assumed a fresh build of the frozen request; a subset of the retained manifests needs none, and the unclaimed draw
  `draw-2026-11-15T190401Z.json` stays unclaimed. The P manifests keep the retained `diagnostic_case_sha256` and `draw`, so
  `bdsc_diagnostic.draw_claims` still admits the retained tree's rebuild, and the diagnostic analyzer refuses a P run
  because `p1` and `p2` are not jobs of the diagnostic.
- Recorder: `bdsc_diagnostic_timing_case.py record RUN` reads the job status on a fixed 10 s cadence (each read starts
  10 s after the previous one started), writes each read or its transient error to `RUN/status-log.jsonl` with the
  time the read returned, and collects the run through `qd_platform.collect` at the terminal status. A read slower
  than the cadence delays the next one; the log shows the actual spacing.
- Submission: each manifest names `scripts/bdsc_diagnostic_timing_case.py submit` as its `submit_wrapper`, so
  `qd_platform.py submit` refuses a P run sent directly. `bdsc_diagnostic_timing_case.py submit RUN --approval TEXT`
  calls `qd_platform.submit` with a verify step that runs under the token's submit lock, after the plan whose body is
  posted. It refuses a request other than the next slot's, a token with a running or queued job (the plan's
  availability counters), a body with mitigations and every stop condition below. Each manifest also carries
  `max_credits` 1.08, the case ceiling `qd_platform.plan` enforces.
- Stop conditions: `bdsc_diagnostic_timing_case.py next` finds every submitted P run under `results/quandela` (a
  directory with a submission receipt; a checkpoint without a receipt stops the case until `qd_platform.py recover`
  writes it) and orders them by submission time. It refuses when a job ended canceled or failed, reported a duration at
  the 300 s limit, ran on another platform or with mitigations, was submitted before the previous job was collected,
  or ran in the wrong slot. Before a further submission it also refuses when the spent credits plus one job's 1.08
  authorization exceed 6.48 or the reported durations reach 1800 s. A rerun or a dropped run cannot escape these
  checks, because `next` reads the runs from the tree, not from its arguments.
- Decision rules: `bdsc_diagnostic_timing_case.py analyze` applies "Decision rules" to the six runs in exact rational
  arithmetic, so a ratio equal to a threshold falls on the side the table names. It lists each duration above 150 s
  or below 135 s as a deviation from the prediction. The caps gate a further submission only, so the sixth run is
  read whatever they hold.
- Plan and review packet: `bdsc_diagnostic_timing_case.py plan` runs `qd_platform.plan` on `p1` and `p2` in the tree,
  reads the live platform and restates credits, seconds and the body's mitigation list per job (read-only); it runs before the approval request, and its output enters the
  approval record. `submit` repeats the plan under the lock before each job. `qd_platform.py review` writes a
  packet only for an Ascella acquisition (`acquisition_sources` requires the predecessor analyzer identities), and the
  retained sim:belenos jobs were submitted without one, so this case's review packet is the review record of the
  builder's pull request under `docs/archive/reviews/bdsc-diagnostic-timing/`.
- Bound sources: once the first job is submitted the tree keeps its bytes, and a change to a file of
  `successor_sources` makes `plan`, `submit` and `collect` refuse the remaining slots. The six jobs therefore run
  from one commit of main in one session (about an hour); a source change that lands mid-case stops it, and a
  successor tree with its own approval restarts it.

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="${QUANDELA_TOKEN_FILE:?set to the token file}"
TREE=results/quandela/cases/bdsc_diagnostic_timing_sim_belenos
"$PYTHON" scripts/bdsc_diagnostic_timing_case.py check
# before the approval request (read-only):
"$PYTHON" scripts/bdsc_diagnostic_timing_case.py plan
# after the owner's approval, one slot at a time; the loop ends when "next" prints complete or refuses (exit 1),
# and analyze refuses a case that holds fewer than six admitted runs:
while NAME=$("$PYTHON" scripts/bdsc_diagnostic_timing_case.py next) && [ "$NAME" != complete ]; do
  RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-sim_belenos-bdsc_timing-$NAME
  mkdir -p "$RUN"
  cp "$TREE/$NAME/cases.json" "$TREE/$NAME/circuit.json" "$RUN"/
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py submit "$RUN" --approval "APPROVAL TEXT"
  "$PYTHON" scripts/bdsc_diagnostic_timing_case.py record "$RUN"
done
"$PYTHON" scripts/bdsc_diagnostic_timing_case.py analyze
```

# Case: Tuna-17 selector offset of the null block, in-batch bracketed coin twins and rule v2

Status: the four-batch hosted QX control was approved, submitted and collected on 2026-11-15 (the retained run directories
are authoritative); the Tuna-17 series below awaits its own approval and has not been submitted. Generator and checker:
`scripts/qi_pathion_one_cz_null_bracketed_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../pathion_one_cz_null_bracketed_qx/`). Submission: `scripts/qi_platform_wave.py series` with `--sanity-command` set to the successor's `--sanity`. Ledger row: A5-186.
The predecessor case `../pathion_one_cz_null_tuna_17/` (producer `scripts/qi_pathion_one_cz_null_cases.py`) keeps its
bytes; this case imports its circuit texts, twins, readouts and calibration circuits.

## What the run measures

The question and the three mechanisms are the predecessor's: the null block b0 (operand e1 + e17, 21 routed CZ) reads a
raw selector contrast of +0.0164 +- 0.0039 where every arm-symmetric product readout and every unital or relaxation
channel gives 0, and the over-rotation, the coin-conditioned selector dropout and the q12 flip each reproduce it
(`docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt`, `c2_one_cz_twins.txt`; predicted contrasts in the
predecessor's CASE.md and in `prediction.json` here, `predicted_contrast`, in ten-thousandths). The decision uses the
predecessor's thresholds, block gate and b0-like band; it differs in five places (owner rulings 2026-11-14, issue 791
items 1 to 3, the layout ruling of the successor wave and the executed-order ruling of 2026-11-16):

- both coin twins of a template run in one batch between that batch's own readout-0 and readout-1, as
  `[readout-0, coin-0 twin, coin-1 twin, readout-1]` (the mirror round reverses the twins): four circuits per batch,
  which the `wave-v1` hardware policy admits (below);
- twin-control rule v2 (`scripts/qi_pathion_one_cz_null_rule_v2.py`) and the finite-count error of a deterministic arm
  (`scripts/qi_pathion_one_cz_null_analysis.py`, `arm_variance`) are preregistered from the start;
- four replicates of every template and kind at half the predecessor's shots per circuit (16,384 per circuit, b0's base
  at 65,536), with the same 2,555,904 shots, and the batch heterogeneity gate at the alpha 0.001 chi-square bound of the
  replicates' degrees of freedom: 16.266 at 3 degrees of freedom, where the predecessor's 10.828 is the 1-degree value of
  its 2 replicates (13.816 at 3 replicates). The predecessor case and its `prediction.json` keep their bytes;
- the decision reads the order and the times the provider executed, recorded per job as `queued_at` and ranked by
  instant (item 6): a drift fit on the executed position offsets of the twin batches with the template contrasts
  pooled under their shared-drift covariance, base levels read at their executed times, a monitor of the bracket
  offsets and five labels that withhold a decision. The text of that rule is stated once, in the `preregistered` block
  of each Tuna-17 `cases.json` and of `prediction.json` (the keys `estimates`, `executed_order`, `base_level`,
  `drift_monitor` and `withheld`). The four QX manifests keep the plain-pool text that the hosted run's submission
  receipts bind by sha256 (`cases_sha256`; a test pins the four digests): the QX control decides no twin series and
  reads no stamp, so its text is a record of the control that ran.

## Hardware policy

The case manifests select `"hardware_policy": "wave-v1"` (`scripts/qi_platform_wave.py`, `HARDWARE_POLICIES`; the pinned
`scripts/qi_platform.py` keeps its bytes and its legacy limits): a hardware batch holds at most 5 circuits and up to 3
batches may be queued per account and backend type, a wave of 15 circuits in 3 batches, each capped by the live backend
record (`max_jobs_per_batch_job`, `batchjobs_per_queue_limit`), and a 60 s pause follows a finished wave. A manifest
without the field keeps the legacy policy (3 circuits, 1 queued batch), which refuses a 4-circuit batch. The owner
ruled on 2026-11-14 that "job" in the FAQ's "not more than 3 jobs in the queue for a hardware backend" means a batch job;
the FAQ does not say it (`docs/notes/quantum_inspire/usage.md`, "Queue rules"). Evidence that the service accepts the
numbers: catalogue `max_jobs_per_batch_job` 5 and `batchjobs_per_queue_limit` 5 on every backend type; two retained
Tuna-17 batches of 5 circuits that were accepted and completed (`results/quantum_inspire/runs/2026-10-16T211635Z-tuna_17`,
`.../2026-10-16T221133Z-zero_divisor_tuna_17`); the SDK (`qi_jobs.py`) checks the batch size and nothing about the queue.

A wave is three consecutive batches of the series, listed in the series `cases.json` (`waves`): 12 waves (eleven of three
batches, a last of two), at most 11 circuits each. Pause semantics (owner ruling 2026-11-14): no more than 3 batches
queued at a time, and 60 s between runs of those three before queuing the next. `qi_platform_wave.py series` submits the
three batches of a wave back to back, collects all three, runs the sanity check on each, and the next wave's first batch
is refused until every job of the account has been finished for 60 s (`pause_seconds` of the policy row; a higher
`QI_HARDWARE_PAUSE_SECONDS` ladder step raises it); the driver sleeps the refusal's remainder and retries. Each batch is
refused while three batches of the account are in flight on the backend type. The driver enforces eleven intervals of 61 seconds from the last finish of one wave to the next enqueue, 671 seconds in
total (the policy requires 60 seconds and the retry adds a one-second margin; measured by
`test_a_twelve_wave_series_pays_eleven_pauses_of_the_policy_and_never_queues_a_fourth_batch`) between its 12 waves. Submitting a wave's batches in series order requests that order; the service owns the execution
order (its terms allow priority without regard to the queue), so the mirrored layout's cancellation is read from the
retained `queued_at` times, not assumed. An unfinished job on another hardware backend type refuses the batch, and the
pause clock is account-wide across every `is_hardware` type, the Ry emulator included
(`docs/notes/quantum_inspire/ry-emulator.md`), so a finished Ry job delays the next Tuna-17 batch by the rest of its
pause and Ry batches do not count toward the three Tuna-17 batches. The driver checks every run directory before its first submission and resumes nothing: a stop leaves the submitted
batches queued, and `qi_platform_wave.py collect` (after `qi_platform.py reconcile` for an uncertain enqueue) recovers
each one. The admission checks read one snapshot of the account and `SUBMIT_LOCK` excludes only sessions on one host; `qi_platform_wave.recheck_before_enqueue` reads the account again, leaving the batch's own planned row out, immediately before the enqueue PATCH and refuses at the policy's queued count. That narrows the window between the snapshot and the enqueue to one read and one PATCH; a rival on another host can still enqueue inside it, and a refused batch stays created and un-enqueued with `submission-state.json` at phase `enqueue-refused`.

Residual risk of the policy: the FAQ sentence is ambiguous. If the provider reads "job" as a circuit, a wave of 15 circuits
queues five times the stated 3; the abuse clause removes the account. The owner accepted that reading for this case; a
provider answer would settle it.

## Derived coefficients and the design they force

Items 2, 3, 5 and 7 are re-derived in `tests/scripts/test_qi_pathion_one_cz_null_bracketed.py`; the retained-record
statistics of item 4 come from the selector counts of the retained run directories named there and are not re-derived by
the tests.

1. Four circuits per batch. A twin pair plus its bracket is four circuits, which the legacy policy refuses and `wave-v1`
   admits (Hardware policy above).
2. Ideal selector marginal. Every twin of the predecessor case (b0, k4, k8, k12 at coin 0 and 1) has ideal
   P(s = 0) = 1/2 exactly (the `ideal` rows of its `batch-*/cases.json`, selector at index 3 of the five logical bits,
   little-endian); the same holds for the twins here.
3. Readout model. With e01 = P(read 1 | prepared 0) from readout-0 and e10 = P(read 0 | prepared 1) from readout-1 of the
   selector (physical q8), a raw reading of P(s = 0) is P = e10 + lambda p with lambda = 1 - e01 - e10, so
   P - 1/2 = lambda (p - 1/2) + (e10 - e01) / 2. The readout-0 circuit leaves all 17 qubits in |0>; the readout-1
   circuit excites the five region qubits q2, q4, q8, q11 and q12 and leaves the other twelve in |0>.
4. Why the pair stays in one batch. The retained one-CZ series reads the selector's e01 between 0.0254 and 0.0310 over
   its twelve readout-0 references (chi-square 84.4 about the mean on 11 degrees of freedom) and e10 between 0.0275 and
   0.0322 over twelve readout-1 references (chi-square 58.0 on 11), and adjacent batches step by about 0.005
   (`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, `drift_covariate.references`, measured on
   Tuna-17, 2026-11-07). Over the 8 retained batches that hold both readouts (00, 03, 04, 07, 08, 11, 12, 15),
   c = (e10 - e01)/2 of the selector has chi-square 61.56 on 7 degrees of freedom about its weighted mean and ranges from
   -0.00136 to +0.00319, so a raw contrast of twins from two batches carries a c difference of up to about 0.0045 (1.6
   pooled twin standard errors). Both twins of a pair share the batch, so that difference is zero by construction.
5. Twin estimator. The bracket offset of a batch is c = (e10 - e01) / 2 and a twin reading is P - c. Both twins of a pair
   carry the one bracket of their batch, so the twin contrast t = (P1 - c) - (P0 - c) = P1 - P0 is the predecessor's raw
   contrast: the offset cancels exactly and its variance is v(P1) + v(P0), each v the arm variance of a rate over its shots
   (`arm_variance`, the Agresti-Coull interval variance at a deterministic arm, issue 791 item 3, which QX readouts
   exercise since they misassign no shot).
   - Its expectation is lambda1 (p1 - 1/2) - lambda0 (p0 - 1/2), the raw scale of the predicted contrasts and of the raw
     base contrasts, so the r and c - d comparisons mix no scales.
   - Design standard error at 16,384 shots per circuit and P = 1/2: contrast se 0.005524, pooled over four replicates
     0.002762 (`design`: `twin_batch_se_micro` 5524, `pooled_se_micro.twin` 2762), the pooled error of the predecessor's
     two replicates at 32,768 shots. The bracket offset has se 0.000925 per batch at the retained means e01 = 0.0281,
     e10 = 0.0296 (`bracket_offset_se_micro` 925).
   - The bracket reports c and the offset-corrected reading P - c of each twin per batch (`twin_brackets` of the analysis
     record: a drift of the selector offset within the series, and a readout-0 against readout-1 context check); the
     decision does not read it. The predecessor's single readout per twin batch gives the same contrast; the second
     readout adds the per-batch c and its se at a cost of one circuit per twin batch.
   - A coin-conditioned selector dropout acts on the coin-1 twin's own shots; the batch's readout contexts are common to
     both twins, so the dropout's twin contrast (+0.0170 at the sized model) survives.
6. Order. The forward round is b0 base, b0 twin, k4 twin, k4 base, k8 base, k8 twin, k12 twin, k12 base (8 batches); the
   rounds alternate forward, mirror (the list reversed and, inside each twin batch, the twin order reversed: coin 1 then
   coin 0), forward, mirror (32 batches), so a linear drift per circuit position enters the four replicates of t as +g,
   -g, +g and -g and cancels in the pooled twin contrast (exactly for equal replicate weights, to first order for the
   analyzer's inverse-variance pool) for the order the case requests. Measured: the platform ran the twins of some
   retained batches in the reverse of their listed order, so the cancellation holds only for batches that run in the
   requested order, and a reordered batch leaves a +g or -g term in its t. The analyzer therefore reads the twin contrasts on the
   executed order (registered rule, owner decision 2026-11-16 on issue 791, `evaluate` of
   `qi_pathion_one_cz_null_bracketed_cases`): the per-job start stamps (`queued_at`, which follows the previous job's
   `finished_at` by 0.03 to 0.19 s in the retained series) give the executed position of the two twins of every twin
   batch, and `qi_pathion_one_cz_null_executed_order` fits one drift shared by the twin batches beside one contrast per
   template, so a reordered batch costs precision and no decision (`docs/design/bracketed-executed-order-analysis.md`
   holds the model, the five labels and the operating characteristics). A start stamp is ISO 8601 text with a UTC
   offset and ranks by its instant (`stamp_instant`, integer microseconds, so `...:38Z` and `...:38.000000Z` are one
   instant); a stamp of any circuit of any batch that is missing, null, not text, not ISO 8601 or without an offset, or
   two circuits of a twin batch at one instant, reads `unresolved_order` and no exception reaches the caller. Measured
   2026-11-17: all 631 jobs of the 221 collected run directories on main and all 623 jobs of the 213 on the branch that
   retains the hosted QX run carry `created_on`, `queued_at` and `finished_at` as `YYYY-MM-DDThh:mm:ss.ffffffZ` (six
   fractional digits, UTC; none null, missing or written otherwise), and no two jobs of one run directory share a
   `queued_at`. Twin
   batches that leave every template one offset read
   `unresolved_order_confounded`; a template whose own drift departs from the shared one by more than three
   errors of the difference reads `unresolved_drift_heterogeneity`. Every record carries the label of the pool that
   ignores the order (`order_ignored_label`; a withheld decision repeats it as `label_if_order_ignored`), and the strict
   reading of every batch (`order_gate`) stays in the record and decides nothing. Measured from the retained `queued_at` stamps, 7 of the predecessor series' 19
   batches (01, 06, 08, 10, 12, 15 and 16) ran out of the listed order and 2 of the 8 twin batches of that series had
   their twins reversed; the case requests the order and the analysis reads the order that ran. The three X-only
   calibration batches of the predecessor follow (3, 3 and 2
   circuits): 35 batches. b0 is `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte, as in the predecessor. The
   platform sets the execution order of the jobs of a batch (the retained `queued_at` stamps show reversed twins in 7 of
   the 19 predecessor batches, the twins reversed in 2 of its 8 twin batches, while `created_on` follows the requested order
   in all 19), which the executed-order fit reads. A base contrast is a level, so its position inside a batch does not enter and its start time does: each
   template's four base replicates are read at their executed starts through a weighted line, and the base level is
   taken at the mean executed start of the template's twin circuits (`docs/design/bracketed-base-contrast-weights.md`);
   template base replicates that share one start time read `unresolved_base_drift_confounded`. For a series that keeps
   its order the weights cost almost nothing, because the mirror rounds put the four base replicates symmetrically about the
   twin reference time: on the requested layout (jobs 14 s apart, waves 61 s apart; `_simulation_layout`) the weighted
   base time lies +15, +15, 0 and -15 s from the reference of b0, k4, k8 and k12, the variance cost f^2 is 1.000, 1.001,
   1.000 and 1.001, and the base level moves from the plain pool by at most 0.00011 (one standard deviation with no
   drift, 0.03 plain standard errors) or 0.00004 at the largest plausible drift of 0.01 per hour (0.02 standard errors);
   after a reordering the shift is the drift accumulated between the weighted base time and the reference time.
   The twin contrasts of different templates share the drift g, so they are correlated: cov(t_T, t_U) = x_T x_U var(g),
   zero when either template kept its order. The decision pools them with that covariance (the pooled 6-CZ twin
   contrast d and the chi-square of the three blocks by generalized least squares, the error of r - m with cov(t0, d);
   `decide_correlated`). Size and direction, by exact enumeration of the 2^16 sign-flip patterns of the 16 twin batches
   at equal batch errors 0.0055 and a flip rate of 0.25 (3 of 12 retained twin batches reversed; 7/19 in brackets): the
   largest correlation of two template contrasts is 0.13 to 0.15 in fixtures of three reordered templates; the error of
   d that the independent pool reports is too small (liberal) in 24 percent of series (27) and too large in the rest,
   with a true-to-reported ratio of 0.95 to 1.05 between the 5th and 95th percentiles (extremes 0.69 and 1.46); the error
   of r - m is too small in 30 percent (32) with ratios 0.88 to 1.26; the mean three-block chi-square of the independent
   pool is 2.000 under either rate. The sign of x_T x_U sets the direction, so the term is included. The bracket offset of
   each of the 32 base and twin batches, placed at the mean start of its two readouts, must stay a line in executed time
   (residual chi-square at alpha 0.001) or the series reads `unresolved_drift_model`; the line's slope bound sizes a
   systematic for each calibration batch, reported beside the decision as `unresolved_calibration_drift` when it
   exceeds that batch's standard error. The offset is placed at the mean start of its two readouts although e01 and
   e10 are read apart: for assignment-error slopes u and v per second and a readout gap D the placed offset carries
   (u + v) D / 4, which is 5.8e-5 in a twin batch (gap 3 jobs, 42 s) and 3.9e-5 in a base batch (28 s) at u = v = 0.01
   per hour, 6.3 and 4.2 percent of the per-batch offset standard error 0.000925 (9.7 percent at a 65 s gap).
7. Shots and time. b0 base batches run at 65,536 shots per circuit, every other base batch and every twin batch at
   16,384, calibration at 16,384 (the predecessor's shots halved except the calibration). Jobs: 120 (16 base x 3, 16 twin
   x 4, 8 calibration); shots 2,555,904, equal to the predecessor's two-replicate layout at twice the shots
   (predecessor: 56 jobs, 2,293,760). A pooled error depends on replicates times shots, so the layout keeps the pooled
   errors (twin 0.002762, base 0.003906, b0 base 0.001953) and gains the degrees of freedom of the batch gates.
8. Heterogeneity bound. Replicate batches of one template and kind agree within chi-square 16.266 (3 degrees of freedom,
   alpha 0.001; `CHI2_ALPHA_001`, checked in the tests against the closed-form survival function). At four replicates
   the predecessor's 10.828 would trip each of the eight gates with probability 0.0127 under no drift (the chi-square survival function at 3 degrees of freedom), so the layout
   would lose power to false `unresolved_batch` readings: simulated at drift 0.003, 62.8 and 66.0 percent (dropout and
   superposition-only) against 82.1 and 85.3 with the matched bound. The three 6-CZ blocks keep 9.210 (2 degrees of
   freedom, alpha 0.01).

### Designs rejected

- A third replicate at full shots, more replicates of only the twin or of only the base batches, and twice the shots,
  priced by simulation (20,000 series per cell, independent drift 0.003, the matched bound, one value of the draw below
  per cell, values 911 to 919 in index order). `scripts/qi_pathion_one_cz_null_bracketed_pricing.py` computes each
  cell from its value and `docs/evidence/qi-bracketed-pricing/cells.jsonl` retains the nine results, which the script
  regenerates count for count (`--check`, gate `core-pathion-one-cz-null-bracketed-pricing-cells`; issue 903). The draw
  belongs to the case manifest, so the seed ledger holds no row for these values. Power in percent, dropout / superposition-only, independent drift and
  common-pair drift:

  | replicates (base / twin) and shots per circuit | batches | waves | jobs | shots | execution s | independent | common |
  |---|---|---|---|---|---|---|---|
  | 2 / 2 at 32,768 (the previous layout) | 19 | 7 | 64 | 2,555,904 | 1,521 to 1,676 | 72.2 / 76.9 | 82.0 / 86.7 |
  | 2 / 3 at 32,768 | 23 | 8 | 80 | 3,080,192 | 1,841 to 2,027 | 71.9 / 79.5 | 82.8 / 89.7 |
  | 3 / 2 at 32,768 | 23 | 8 | 76 | 3,244,032 | 1,917 to 2,113 | 71.0 / 78.5 | 80.2 / 87.3 |
  | 3 / 3 at 32,768 | 27 | 9 | 92 | 3,768,320 | 2,236 to 2,465 | 69.9 / 80.1 | 80.0 / 89.7 |
  | 2 / 4 at 32,768 | 27 | 9 | 96 | 3,604,480 | 2,160 to 2,378 | 71.1 / 80.2 | 82.9 / 91.1 |
  | 2 / 2 at 65,536 | 19 | 7 | 64 | 4,980,736 | 2,806 to 3,108 | 51.3 / 65.0 | 68.9 / 83.9 |
  | 2 / 2 at 16,384 | 19 | 7 | 64 | 1,343,488 | 878 to 960 | 73.9 / 58.8 | 80.4 / 62.1 |
  | 3 / 3 at 16,384 | 27 | 9 | 92 | 1,949,696 | 1,273 to 1,391 | 81.6 / 77.3 | 86.7 / 81.9 |
  | 4 / 4 at 16,384 (this case) | 35 | 12 | 120 | 2,555,904 | 1,667 to 1,821 | 82.1 / 85.3 | 86.9 / 90.0 |

  More shots alone lowers power (65,536: 51.3 / 65.0) because the base-contrast drift 0.003 then exceeds the batch
  standard error and trips the gates; more replicates with the matched bound raise it. The layout reaches 80 percent in
  both worlds under both drift models at the previous layout's total shots, with the cost of 35 batches and 12 waves.
- Split pairs `[readout-0, twin, readout-1]` in 27 batches under the legacy 3-circuit policy: two adjacent batches sit a
  queue interval apart (23 to 207 minutes between retained batches, against 10 to 147 s inside one), which the in-batch
  pair avoids. Its simulated power under the stress below was 0.609 (dropout) and 0.650 (superposition-only).
- A mid-circuit selector reference or a measured classical coin in the twin: either adds a measurement on the coin edge,
  which is a coin-conditioned readout channel, the mechanism under test, and its misassignment is unmeasured on
  Tuna-17.
- A data-qubit-fixed twin, a QX remote run as the decision, and the Ry emulator as the decision: as in the predecessor.

## Circuits and batches

Every circuit measures all 17 qubits. A coin-fixed twin is the routed template with the coin's first single-qubit run (the
Hadamard, checked up to a global phase) removed and the coin prepared in |0> or |1>; the predecessor's `twin_entry`
builds it. Twin contrast t as in item 5; base contrast s = P(s = 0 | coin read 1) - P(s = 0 | coin read 0) as in the
predecessor, read raw.

- Batches 00-31: the 32 template batches of item 6. A base batch is `[readout-0, template, readout-1]`; a twin batch is
  `[readout-0, coin-0 twin, coin-1 twin, readout-1]` (mirror rounds: coins reversed).
- Batches 32-34: the eight X-only preparations of (q2, q8, q12), 16,384 shots, a secondary readout calibration in a
  terminal-assignment context (D and G of the predecessor, reported beside the outcome).
- The routing seeds are those of the predecessor (values 0, 64 and 128 of
  `docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json`); the three operating-characteristics tables are seeded from
  values 920 to 929 of `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`, one each, in that order (the three tables of the
  pool that ignores the order, then the seven tables of the executed-order rule).
- QX twin: per template one batch `[readout-0, coin-0 twin, coin-1 twin, readout-1, base]`, 4 batches of 5 circuits (the
  service ceiling) at 2,048 shots; the QX emulator is no hardware backend and takes no policy field.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7), region q2, q4, q8, q11, q12 (as the predecessor); QX emulator (type 1) for the twin.
- Jobs and shots: 120 jobs in 35 batches of at most 4 circuits in 12 waves, 2,555,904 shots, every job at or under 65,536
  shots. The longest job, a 65,536-shot b0 base circuit, takes 41.3 s (2.6 s plus the coin series' maximum measured
  0.5906 ms per shot), under the 300 s job limit.
- Expected time: 1,666.6 to 1,821.4 s of execution (120 jobs at 2.6 s plus 0.53 ms to 0.5906 ms per shot), excluding the
  pauses; 11 pauses of 60 s (660 s) between the 12 waves, so 2,326.6 to 2,481.4 s plus queue time. With the rounded
  0.59 ms per shot the longest job reads 41.3 s.
- Quota: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this account.

## Preregistered decision rules

Z = 3 standard errors; the raw counts are read. The rule is the predecessor's (items 1 to 5 of its CASE.md, with the
thresholds 16.266 (3 degrees of freedom, item 8 above) and 9.21 for the heterogeneity gates and `B0_LIKE_Z` 2.0) on the
estimates above, with item 4 replaced by rule v2:

> b0 twin contrast t0 above 3 se; if not, t0 within 3 se of zero (|t0| <= 3 se) and s0 - t0 above 3 combined se, the offset
> exists only with the coin in superposition; t0 below -3 se is unresolved (negative twin); otherwise unresolved.

A t0 below -3 se reads `unresolved_negative_twin`, which decides nothing and leaves A5-186 unchanged. The pooled errors
use `ana.pooled`, which refuses an error that is not positive and finite; a deterministic arm takes the finite-count
interval variance. `prediction.json` (`preregistered`, `outcomes`) holds the text of every row.

### Operating characteristics

`prediction.json` (`operating_characteristics`) holds ten tables, shares in ten-thousandths, 20,000 simulated series per
world. Each seeds from its own value of `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`, indices in increasing
order, each used once (`seed_indices`): the three tables of the pool that ignores the order (920 to 922) and the seven
tables of the registered executed-order rule (923 to 929).

#### The registered rule: executed order, drift and reordering

`executed_order_model` states the assumptions (hypotheses, not measurements of Tuna-17): a batch runs its circuits in a
uniformly random permutation with probability 0.5 and in the requested order otherwise, so a twin batch reverses its
twins with probability 0.25 (3 of 12 retained twin batches did; the strict gate counted 7 of 19 predecessor batches out
of order, 0.37); jobs start 14 s apart and waves 61 s apart; the twin drift shared by every template is 0.003 per
executed position and the base level and the bracket offset drift 0.01 per hour (the largest plausible drift of
`docs/design/bracketed-base-contrast-weights.md`); a planted departure adds to the k4 twin drift. A twin contrast keeps
its binomial estimator noise and the decision is `decide_executed` on the simulated contrasts, executed offsets and times, so
every fit, weight, covariance, monitor, gate and label of the rule counts. Share of series, nine worlds for the first
three tables and the `absent`, `coin_dropout` and `superposition_only` worlds for the planted departures:

| table (seed value) | dropout world reads b0-like | superposition-only world reads its row | negative-twin world reads its row | gate fired, no planted departure (nine worlds) |
|---|---|---|---|---|
| `executed_in_order` (923): no reordering, no drift | 0.916 | 0.933 | 0.965 | 0.0097 to 0.0121 |
| `executed_reordered_stationary` (924): reordering, no drift | 0.917 | 0.921 | 0.961 | 0.0086 to 0.0114 |
| `executed_reordered_linear_drift` (925): reordering, linear drift | 0.917 | 0.924 | 0.963 | 0.0091 to 0.0115 |
| `executed_reordered_independent_drift_sd_0.003` (928): reordering, drift 0.003 on every base and twin contrast (the stress of the power rule) | 0.816 | 0.838 | 0.894 | 0.0303 to 0.0331 |
| `executed_reordered_pair_common_drift_sd_0.003` (929): reordering, drift 0.003 on the base contrasts (a pair-common drift cancels in the twin contrast) | 0.872 | 0.892 | 0.945 | 0.0095 to 0.0109 |

| planted departure of the k4 twin drift per position (seed value) | gate fired, absent / dropout / superposition-only |
|---|---|
| 0.0075 (926) | 0.457 / 0.469 / 0.458 |
| 0.015 (927) | 0.944 / 0.945 / 0.944 |

The rule meets the power rule of 80 percent at the design effect in every table, including the stress that the rule is
defined on: 81.6 and 83.8 percent under a drift of 0.003 on every contrast (928; the pool that ignores the order reads 82.1 and
85.2) and 87.2 and 89.2 under the pair-common drift (929; 86.8 and 90.1), 91.6 to 93.3 percent where the drift is the shared
linear drift that the fit removes; reordering at 0.5 per batch costs at most 1.2 points of it. The independent-drift stress
is the binding one: the margin over 80 percent is 1.6 points for the dropout world at a Monte Carlo standard error of 0.27. The drift-heterogeneity gate fires on about 1.0 percent of series when no
template departs (false-alarm rate, three errors of the difference on four correlated templates, 0.27 percent each; 3.1
percent when every contrast carries an independent drift of 0.003, which the shared-drift model reads as a departure),
and detects a departure of 0.0075 per position (2.5 times the shared drift) in 46 percent and of 0.015 in 94 percent of
series. The remaining losses of the dropout world under linear drift are `intermediate` 0.045, `unresolved_block` 0.020
and `unresolved_drift_heterogeneity` 0.0105 (the false alarms), and `unresolved_batch` stays under 0.005. The tables simulate the drift that the
rule corrects, linear in executed position and time; a drift of another shape is the monitor's and the gate's business
and is not tabulated (hypothesis: a step or a burst trips `unresolved_drift_model`, as the monitor tests pin).

#### The pool that ignores the order (`order_ignored_label`)

The three older tables describe the label that every record carries beside the decision, `order_ignored_label`: the plain
pool of the batch contrasts, which the registered rule replaces. Stationary 920, `batch_drift_sd_0.003` 921,
`pair_common_drift_sd_0.003` 922. A base contrast is a Gaussian draw at the design standard error; the two twins of a batch draw
binomial selector counts at P = 1/2 + c -/+ t / 2 and the real estimator reads them. Three tables: stationary; the
preregistered stress `batch_drift_sd_0.003`, an independent drift of 0.003 on every base contrast and every twin contrast
(the predecessor's convention); and `pair_common_drift_sd_0.003`, a drift of 0.003 on every base contrast and a drift of
each batch common to its two twins, which cancels in their difference. Worlds: the eight of the predecessor and the
negative twin. Share of runs that read each row, stationary:

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.965 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.034 |
| q12 correlation | 0.967 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.032 |
| coin-conditioned dropout | 0.000 | 0.921 | 0.046 | 0.000 | 0.000 | 0.000 | 0.033 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.938 | 0.001 | 0.000 | 0.060 |
| no offset | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.973 | 0.027 |
| worst admitted over-rotation (Y axis) | 0.493 | 0.000 | 0.475 | 0.001 | 0.000 | 0.000 | 0.030 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.076 | 0.875 | 0.000 | 0.000 | 0.000 | 0.050 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.895 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.105 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.002 | 0.969 | 0.000 | 0.030 |

Independent drift 0.003 on every contrast (`batch_drift_sd_0.003`):

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.896 | 0.000 | 0.003 | 0.001 | 0.000 | 0.000 | 0.101 |
| q12 correlation | 0.896 | 0.000 | 0.003 | 0.001 | 0.000 | 0.000 | 0.100 |
| coin-conditioned dropout | 0.000 | 0.821 | 0.081 | 0.001 | 0.000 | 0.000 | 0.097 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.852 | 0.004 | 0.000 | 0.144 |
| no offset | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 | 0.901 | 0.098 |
| worst admitted over-rotation (Y axis) | 0.460 | 0.000 | 0.441 | 0.001 | 0.000 | 0.000 | 0.098 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.102 | 0.774 | 0.002 | 0.000 | 0.000 | 0.122 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.801 | 0.000 | 0.000 | 0.002 | 0.000 | 0.000 | 0.198 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.005 | 0.905 | 0.000 | 0.090 |

Drift 0.003 on the base contrasts, common to each pair (`pair_common_drift_sd_0.003`):

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.936 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 | 0.061 |
| q12 correlation | 0.937 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 | 0.061 |
| coin-conditioned dropout | 0.000 | 0.868 | 0.072 | 0.000 | 0.000 | 0.000 | 0.060 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.901 | 0.001 | 0.000 | 0.098 |
| no offset | 0.000 | 0.000 | 0.000 | 0.001 | 0.000 | 0.937 | 0.062 |
| worst admitted over-rotation (Y axis) | 0.479 | 0.000 | 0.458 | 0.001 | 0.000 | 0.000 | 0.062 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.096 | 0.819 | 0.001 | 0.000 | 0.000 | 0.085 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.854 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 | 0.145 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.002 | 0.942 | 0.000 | 0.056 |

For that pool, stationary, the four deciding worlds decide in 96.5 (over-rotation), 96.7 (q12 correlation), 92.1 (dropout)
and 93.8 (superposition-only) percent. The power rule asks 80 percent of the dropout and superposition-only worlds under
a drift of 0.003, and the layout meets it under both models: with an independent drift on every contrast it decides them in 82.1
and 85.2 percent, with the drift common to each pair in 86.8 and 90.1 percent (the Monte Carlo standard error of a cell
is 0.27 percent at 20,000 series). The pricing run that sized the layout (seed value 918, same code and layout) read 82.1
and 85.3, so the 0.1-point difference of the superposition-only cell is Monte Carlo noise. The previous two-replicate
layout met the rule only under the common-drift model (82.1 and 86.9 against 72.5 and 77.1 under the independent one).
The two models bracket the truth: the in-batch pair removes every drift that shifts both twins together, and the stress
leaves a drift between the two twins of a batch, 10 to 147 s apart in the retained series, unexcluded. Which model
governs is a hypothesis; the retained twin forward-against-mirror comparison (chi-square 14.77 on 8 degrees of freedom, p 0.064: the sum of z^2
over the 8 twin coin arms' raw selector rate, forward against mirror, 32,768 shots per arm; recomputed 2026-11-17 as
14.7723, p 0.0637, from batches 01 and 14 (b0), 02 and 13 (k4), 05 and 10 (k8) and 06 and 09 (k12) of the predecessor
series, with z = (P forward - P mirror) / sqrt of the two `arm_variance` terms) shows no twin drift above the sampling
noise. It is a different statistic from the 46.87 on 8 degrees of freedom of the contrast-pair comparison in the
residual risks below. Under the independent model the losses of the dropout world are `intermediate` 0.081, `unresolved_batch` 0.047 and
`unresolved_block` 0.042, and those of the superposition-only world `unresolved` 0.048, `unresolved_batch` 0.047 and
`unresolved_block` 0.046 (`prediction.json`); the gates and the b0-like band share the loss, and the gate losses fall to
about 0.03 each under the common-drift model. Hypothesis: the gates read base-contrast drift, which no layout change of the
twins reaches; the cheapest test reuses the draws and disables one gate at a time. A wrong refutation of A5-186 (a b0-like
reading of an over-rotation world) occurs in 7.6 percent of stationary runs of the world that rotates before every
single-qubit gate, Rz included, and in under 0.1 percent of runs of any admitted world.

## QX and Ry check plan

- QX local (qxelarator in the Quantum Inspire environment, `docs/notes/quantum_inspire/qx-runs.md`, "Run QX locally"; no
  account, queue or approval). The check reads the QX series through the successor's analyzer (`--qx-check`): every data
  circuit within twice the sampling floor of its ideal law, the selector's readout arms deterministic (zero misassigned
  shots), every bracket offset 0, and the twin contrast equal to the raw contrast. Run for the in-batch layout on
  2026-11-15 (issue 896): 20 circuits at 2,048 shots on qxelarator 0.10.0, each circuit's seed derived from value 1 of
  `docs/evidence/anu_qrng/draw-2026-11-15T163052Z.json` by `scripts/qx_local_series.py`; every circuit passes (the
  largest total variation distance is 1.31 times its sampling floor, the bound 2), no readout shot is misassigned and
  every bracketed twin contrast equals its raw one. The retained counts
  `results/quantum_inspire/pathion_one_cz_null_bracketed_qx_local_counts.json` replay through gate
  `core-pathion-one-cz-null-bracketed-qx-local-control`, which re-reads the retained counts and runs no new qxelarator
  execution; a local qxelarator run says nothing about the hosted emulator
  (the remote QX run below is the plumbing check) or about Tuna-17.
- QX remote (type 1): the same series, 4 batches of 5 circuits at 2,048 shots, run on 2026-11-15 under the owner's approval
  (runs `results/quantum_inspire/runs/2026-11-15T184810Z-pathion_one_cz_null_bracketed_qx-batch-00` to `-03`, analysis
  `results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json`, replay gate
  `core-pathion-one-cz-null-bracketed-qx-analysis-replay`): `qx_control.pass` and `qx_brackets.pass` are true. The
  hosted emulator accepts all five circuits, returns ten-bit outcomes in the expected logical-bit ordering and passes the
  control and bracket checks; this control neither requires nor establishes the requested circuit execution order. The
  written case of 2026-11-15, retained at `results/quantum_inspire/runs/2026-11-15T184810Z-pathion_one_cz_null_bracketed_qx-batch-00/written-case-at-approval.md` (sha256 24f001feb8082f6d84e63534df093a68fbf33785622d7ce5c8eec1f79e6e6e67; batches 01 to 03 are the same series), stated the estimate the approval rested on, 4 batches, 20 jobs, 40,960 shots,
  under 120 s and 0 credits; the series executed in 2.85 s of execution time and charged 0. Measured from the retained
  `queued_at` stamps, batches 02 and 03 of this emulator run executed out of the requested order (batch 02: readout-0,
  k8-coin1, readout-1, k8, k8-coin0; batch 03: both twins before readout-0), so the platform reorders a batch of five
  circuits on the emulator as well, 2 of 4 batches. The approval field of each receipt carries the owner's sentence
  followed by a session-written parenthetical. The hosted sampling randomness is the provider's and no receipt records a
  sampling seed; the circuit-generation seeds are the QRNG-bound ones of the case manifests. Before commit d96c12ca6 the series driver's default sanity
  check was the predecessor's, which refused the bracketed run directory after batch 0, so the run resumed under the same stamp with
  `SANITY_COMMAND` naming `qi_pathion_one_cz_null_bracketed_cases.py --sanity`; the driver now selects the bracketed check for a bracketed series.
- Ry (type 5): not built for the decision (predecessor CASE.md, owner decision 2026-11-07: 1,024 shots per job and an
  undocumented noise model). The one Ry check that adds information is the bracket arithmetic on a backend with nonzero
  readout error: a single `[readout-0, coin-0 twin, coin-1 twin, readout-1]` batch of b0 on a 5-qubit translation
  (`docs/notes/quantum_inspire/ry-emulator.md`, "Do a Ry emulator run"), whose corrected twin readings land within 3
  standard errors of 1/2 while the raw readings carry (e10 - e01) / 2. Ry is flagged `is_hardware`, so a manifest that
  selects `wave-v1` gives it 5 circuits per batch, 3 queued batches, a 60 s pause after a wave and the account's one
  pause clock (Hardware policy above). Written case, owner approval, not run.

## Residual risk

- The registered rule meets the 80 percent power rule in every executed-order table (Operating characteristics): 81.6 and 83.8
  percent under an independent drift of 0.003 on every contrast, 87.2 and 89.2 under a pair-common drift, 91.6 to 93.3 where
  the drift is the linear one that it corrects; the stress that governs the hardware is a hypothesis, the margin over 80
  percent under the independent drift is 1.6 points, and a drift of another shape reads `unresolved_drift_model` or
  `unresolved_drift_heterogeneity` and decides nothing. The pool that ignores the order meets the rule under both of its
  drift models. The batch bound 16.266 is a case-specific change of the preregistered gate, and a gate tripped by real
  drift reads `unresolved_batch`, as it did in the retained series.
- The FAQ's "job" is ambiguous (Hardware policy); a provider answer settles whether a wave reads as 3 or 15 jobs.
- The retained b0 base replicates differ: 0.0162 then 0.0393 (se 0.0028 each, 0.0039 for the difference, chi-square
  34.86 above both 10.83 and 16.27; this is the b0 base pair's share of a different statistic, the contrast-pair
  chi-square of the base and twin pairs, recomputed at 46.87 on 8 degrees of freedom and, without the b0 base pair, at
  12.01 on 7 degrees of freedom, p 0.10), so the retained series reads `unresolved_batch`. Hypothesis: a drift of the offset itself, which the
  bracket does not correct (the bracket removes the readout offset, and the offset under test is the quantity that
  drifts); the unchanged heterogeneity gate reads it as `unresolved_batch`.
- A readout-context difference between the two brackets (readout-1 excites the five region qubits only) shifts c for both
  twins alike and cancels in t; a coin-conditioned part of the selector error is bracketed by no readout circuit, and the
  X-only calibration estimates it.
- hypothesis: the retained readout-0 selector error e01 behaves as steps rather than independent batch scatter; the
  operating characteristics draw independent drift and do not simulate steps.
- The Ry check has little statistical power: at 1,024 shots a twin's P(s = 0) carries a standard error of about 0.016,
  so it distinguishes the corrected from the raw reading only when |e10 - e01| / 2 on Ry exceeds about 0.05.
- The X-only calibration (batches 32 to 34) covers the assignment context; a q12 correlation that appears only after the
  template's CZ and X90 schedule stays open, and no outcome label changes.

## Submission command templates and run status

The QX command below ran on 2026-11-15 (historical); the Tuna-17 command has not run.

The owner's approval is quoted in `--approval`. The QX twin runs through the one-batch script on the pinned runner; the
Tuna-17 series runs through the wave driver, which submits a wave's batches back to back, collects them, runs
`--sanity-command` on each collected run directory and waits the policy's 60 s pause before the next wave.

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
SANITY="$PYTHON scripts/qi_pathion_one_cz_null_bracketed_cases.py --sanity"

"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --check "$CASES"
"$QI_PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: four batches, then the control analysis.
sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_one_cz_null_bracketed_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_qx-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json

# Tuna-17: twelve waves of at most three batches, under the wave-v1 policy the manifests name.
"$QI_PYTHON" scripts/qi_platform_wave.py series "$CASES/pathion_one_cz_null_bracketed_tuna_17" "$RUNS" "$STAMP" \
	--backend-type-id 7 --approval "QUOTE" --sanity-command "$SANITY"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run directories, the
analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

## Pre-flight record (2026-11-15, before any Tuna-17 spend)

Five lines, then the comparison with the retained shape and the decision each outcome changes.

1. Hypothesis: the +0.0164 +- 0.0039 raw selector contrast of the null block b0 is produced by one of three mechanisms
   (over-rotation, coin-conditioned selector dropout, q12 flip), which the twin contrast and the in-batch brackets separate
   (`prediction.json`, `predicted_contrast`; issue 791 items 1 to 3).
2. Quantity: the pooled twin contrast t = P1 - P0 of each template and the base offset, as `qi_pathion_one_cz_null_analysis.py`
   and `qi_pathion_one_cz_null_rule_v2.py` define them (definitions in this repository; no external paper defines them).
3. Falsifier: a label that the preregistered world rows do not predict, or any `unresolved_*` label (batch, block, negative
   twin, order), which decides nothing and leaves A5-186 unchanged.
4. Predicted outcome and budget: power 81.6 / 83.8 percent (dropout / superposition-only world) under the registered
   executed-order rule with reordering and an independent drift of 0.003 on every contrast, 87.2 / 89.2 under common-pair
   drift and 91.7 / 92.4 under the linear drift that it corrects (82.1 / 85.3 and 86.9 / 90.0 for the pool that ignores the
   order), for 120 jobs, 2,555,904 shots, 1,667 to 1,821 s of execution plus 671 s of
   pauses (hypothesis: the drift model; the retained forward-against-mirror comparison shows no twin drift above noise).
5. Next step by outcome: a label confirms or rules out one mechanism and moves A5-186; `unresolved_batch` repeats the
   predecessor's b0 base-replicate heterogeneity and moves the design to drift control; `unresolved_order` is the case below.

Comparison with the retained shape (the strict gate, superseded by the ruling below). The predecessor's 19 batches had 7 out of the requested order by `queued_at` (batches 01,
06, 08, 10, 12, 15 and 16). The strict gate required every one of the 35 batches (32 base and twin batches and 3 calibration batches) in order. If the batches reorder independently at
the predecessor's rate of 7/19 = 0.37, the chance that all 35 are intact is 1.0e-7; at half that rate 8.0e-4; at a quarter
3.4e-2; the rate that leaves an even chance is 0.020 per batch. The predicted power above is therefore conditional on an order
rate that the retained data contradict by a factor of at least 18. The prediction for this series as written is
`unresolved_order`, with the label the rule would have read beside it.

Decision before spending. A rate of 0.02 cannot be confirmed by a probe (35 intact batches bound the rate below 0.086 at 95
percent), so a probe does not rescue the strict gate. Two ways remain, each for the owner's ruling and a review round before any
job: (A) keep the strict order gate and accept that the series almost surely reads `unresolved_order`, which spends 2.6
million shots to learn the platform's order rate; (B) preregister an executed-order analysis before the run, which reads each
batch's circuit positions from `queued_at` (the stamp that follows the previous job's `finished_at` by 0.03 to 0.19 s in the
retained batches) and fits the linear drift on the position offset of the twins, so a reordered twin batch costs precision and
no decision; the base and calibration batches have no such rule yet (`docs/design/bracketed-executed-order-analysis.md`). The
cheaper way to learn the rate is one wave (3 batches, 15 circuits, about 15 x 12 s of device time) of the cheapest circuits,
which measures how this layout's submission pattern reorders without claiming a decision.

Owner ruling 2026-11-16 23:52Z on issue 791, "Preregistered executed-order analysis": way (B). The analysis is registered on the
order the provider executed, recorded per job (`queued_at`), so a reordered batch stays usable, and the strict order gate no
longer decides. This section supersedes the prediction `unresolved_order` of the paragraphs above and leaves them as the
record of the choice; the case is unapproved, and the rule text of item 6 of the series description was rewritten in
place for that reason. The registered twin rule (`docs/design/bracketed-executed-order-analysis.md`) is integrated in
`evaluate` and pinned by tests that feed a reordered series and compare it with the series that kept its order, and that
fail closed on a missing, null or tied stamp. The base time weights, the drift monitor and the
calibration systematic of `bracketed-base-contrast-weights.md` are integrated with it, so the rule is complete; the power
tables under reordering are in `prediction.json` (Operating characteristics); what stays open is the injection and blinding
harness (the design notes, "Not done").

Results already in hand and what they change: the hosted QX run passes its noiseless control (`qx_control.pass`,
`qx_brackets.pass`), so the batch of five circuits parses and returns ten-bit outcomes in the expected logical-bit ordering, and
2 of its 4 batches executed out of the requested order by `queued_at` on the emulator, so the order question is not particular
to the device. The current `analyze` on the four retained run directories (2026-11-17) reads claim kind control,
`qx_control.pass` and `qx_brackets.pass` true and the whole analysis record equal to the retained one, which is the QX
prediction above; its twenty stamps are six-digit-fraction Z text, none null, and the executed twin offsets are +1, +1, -3
and +1 (batch 02 ran coin 1 first, three places early; batch 03 ran its readouts before its twins and kept the twin
order). `evaluate` needs the 35-batch Tuna-17 layout and the retained 4-batch QX layout, one twin batch per template, is confounded by construction
(`ConfoundedOrder`: every template keeps one offset), so the QX series yields a control verdict and no twin-decision
label; the sim:belenos b1-j1 job finished at 300 s of a 300 s limit, which predicted that the same shape
could be cut off, and b1-j2 was (305 s, 23 of 24 iterations): a result at a limit is a warning for the next job of its shape.

Statements of 2026-11-17 (a verification pass at head 27bab9471; the case stays unapproved):

- The four QX manifests under `results/quantum_inspire/cases/pathion_one_cz_null_bracketed_qx/` are retained records of the
  earlier plain-pooling rule. The hosted run's receipts bind them by `cases_sha256`, so they keep their bytes and their
  control text; the executed-order rule with the base time weights governs every later series, the Tuna-17 manifests and
  `prediction.json` among them.
- Power at an independent drift of 0.003 on every base and twin contrast (table
  `executed_reordered_independent_drift_sd_0.003`, 20,000 series per world, a series that the heterogeneity gate leaves
  unresolved counted as a miss): the dropout world reads b0-like in 16,328 of 20,000 series, 81.64 percent (Wilson 95
  percent interval 81.10 to 82.17), and the superposition-only world reads its row in 83.83 percent (83.31 to 84.33). The
  gate withholds about 3.1 percent of these series (3.14 and 3.08 percent). The margin over 80 percent is a Monte Carlo
  statement; the drift model is an assumption.
- A gate-silent null (absent world, 100,000 series per row): the false-claim rate is 0.014 percent at a planted departure
  of 0 (14 of 98,988 silent series), 0.019 percent at 0.0075 per position (10 of 53,781; Wilson 0.010 to 0.034 percent)
  and 0 of 5,618 at 0.015. At 0.0075 the cost is a rise of `unresolved_block` among the silent series from 2 to 10
  percent, not false claims.
- The registered 35-batch layout (16 base, 16 twin and 3 joint batches; requested twin offsets +1, -1, +1, -1 per
  template) has no batch confounded by construction: at a reorder rate of 0.5, 0 of 1,000 simulated series read
  `unresolved_order_confounded`. The confound belongs to the retained 4-batch QX layout alone.
- The base time weights shift the in-order pooled base value by 0.027 standard errors on the modeled timeline, 0.017 on
  the 12-minute series of 2026-11-16 and 0.112 on the 15.8-hour series of 2026-11-07 (f squared 1.0126); on that long
  series the plain pool carries up to 2.35 standard errors of drift bias at 0.01 per hour, which the weights remove. A
  long queue makes the time weights matter, which is the reason for the rule.
- `evaluate` cannot read the retained 19-batch record that holds the 46.87 chi-square: its layout differs and it holds no
  bracket readouts, so no twin label exists for that record.
- Equal start instants: two circuits of one twin batch that start at one instant have no executed order, so the decision
  reads `unresolved_order`, whatever the spelling of the two stamps; a gap of one microsecond ranks. A tie among circuits
  that the layout does not rank (a base batch) orders nothing, is counted by the strict `order_gate` and withholds
  nothing.


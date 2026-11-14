# Case: Tuna-17 selector offset of the null block, in-batch bracketed coin twins and rule v2

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
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
predecessor's thresholds, block gate and b0-like band; it differs in four places (owner rulings 2026-11-14, issue 791
items 1 to 3, and the layout ruling of the successor wave):

- both coin twins of a template run in one batch between that batch's own readout-0 and readout-1, as
  `[readout-0, coin-0 twin, coin-1 twin, readout-1]` (the mirror round reverses the twins): four circuits per batch,
  which the `wave-v1` hardware policy admits (below);
- twin-control rule v2 (`scripts/qi_pathion_one_cz_null_rule_v2.py`) and the finite-count error of a deterministic arm
  (`scripts/qi_pathion_one_cz_null_analysis.py`, `arm_variance`) are preregistered from the start;
- four replicates of every template and kind at half the predecessor's shots per circuit (16,384 per circuit, b0's base
  at 65,536), with the same 2,555,904 shots, and the batch heterogeneity gate at the alpha 0.001 chi-square bound of the
  replicates' degrees of freedom: 16.266 at 3 degrees of freedom, where the predecessor's 10.828 is the 1-degree value of
  its 2 replicates (13.816 at 3 replicates). The predecessor case and its `prediction.json` keep their bytes.

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
refused while three batches of the account are in flight on the backend type. The series pays 11 pauses of 60 s (660 s)
between its 12 waves. Submitting a wave's batches in series order requests that order; the service owns the execution
order (its terms allow priority without regard to the queue), so the mirrored layout's cancellation is read from the
retained `queued_at` times, not assumed. An unfinished job on another hardware backend type refuses the batch, and the
pause clock is account-wide across every `is_hardware` type, the Ry emulator included
(`docs/notes/quantum_inspire/ry-emulator.md`), so a finished Ry job delays the next Tuna-17 batch by the rest of its
pause and Ry batches do not count toward the three Tuna-17 batches. The driver checks every run directory before its first submission and resumes nothing: a stop leaves the submitted
batches queued, and `qi_platform_wave.py collect` (after `qi_platform.py reconcile` for an uncertain enqueue) recovers
each one. The admission checks read one snapshot of the account and `SUBMIT_LOCK` excludes only sessions on one host.

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
   requested order, a reordered batch leaves a +g or -g term in its t, and no gate orients the decision by the executed
   order (issue 894); the retained `queued_at` and `created_on` times show which batches ran as requested. The three X-only calibration batches of the predecessor follow (3, 3 and 2
   circuits): 35 batches. b0 is `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte, as in the predecessor. The
   platform sets the execution order of the jobs of a batch (the retained `created_on` shows reversed twins in some
   batches), so the estimator uses batch co-membership, not the listed order.
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
  priced by a scratch simulation (20,000 series per cell, independent drift 0.003, the matched bound, seeds from values
  911 to 919 of the draw below; the scratch code is not retained, so the cells are computed and not replayable from the
  tree). Power in percent, dropout / superposition-only, independent drift and common-pair drift:

  | replicates (base / twin) and shots per circuit | batches | waves | jobs | shots | execution s | independent | common |
  |---|---|---|---|---|---|---|---|
  | 2 / 2 at 32,768 (the previous layout) | 19 | 7 | 64 | 2,555,904 | 1,521 to 1,676 | 72.2 / 76.9 | 82.0 / 86.7 |
  | 2 / 3 at 32,768 | 23 | 8 | 80 | 3,080,192 | 1,841 to 2,027 | 71.9 / 79.5 | 82.8 / 89.7 |
  | 3 / 2 at 32,768 | 23 | 8 | 76 | 3,244,032 | 1,917 to 2,113 | 71.0 / 78.5 | 80.2 / 87.3 |
  | 3 / 3 at 32,768 | 27 | 9 | 92 | 3,768,320 | 2,236 to 2,465 | 69.9 / 80.1 | 80.0 / 89.7 |
  | 2 / 4 at 32,768 | 27 | 9 | 96 | 3,604,480 | 2,160 to 2,378 | 71.1 / 80.2 | 82.9 / 91.1 |
  | 2 / 2 at 65,536 | 19 | 7 | 64 | 4,980,736 | 2,806 to 3,108 | 51.3 / 65.0 | 68.9 / 83.9 |
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
  values 920, 921 and 922 of `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`, one each, in that order.
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

`prediction.json` (`operating_characteristics`, shares in ten-thousandths; 20,000 simulated series per world). Each table
seeds from its own value of `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`, indices in increasing order, each used
once: stationary 920, `batch_drift_sd_0.003` 921, `pair_common_drift_sd_0.003` 922 (`seed_indices`). A base contrast is a Gaussian draw at the design standard error; the two twins of a batch draw
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

Stationary, the four deciding worlds decide in 96.5 (over-rotation), 96.7 (q12 correlation), 92.1 (dropout) and 93.8
(superposition-only) percent. The power rule asks 80 percent of the dropout and superposition-only worlds under a drift
of 0.003, and the layout meets it under both models: with an independent drift on every contrast it decides them in 82.1
and 85.2 percent, with the drift common to each pair in 86.8 and 90.1 percent (the Monte Carlo standard error of a cell
is 0.27 percent at 20,000 series). The pricing run that sized the layout (seed value 918, same code and layout) read 82.1
and 85.3, so the 0.1-point difference of the superposition-only cell is Monte Carlo noise. The previous two-replicate
layout met the rule only under the common-drift model (82.1 and 86.9 against 72.5 and 77.1 under the independent one).
The two models bracket the truth: the in-batch pair removes every drift that shifts both twins together, and the stress
leaves a drift between the two twins of a batch, 10 to 147 s apart in the retained series, unexcluded. Which model
governs is a hypothesis; the retained twin forward-against-mirror comparison (chi-square 14.77 on 8 degrees of freedom)
shows no twin drift above the sampling noise. Under the independent model the losses of the dropout world are `intermediate` 0.081, `unresolved_batch` 0.047 and
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
  shots), every bracket offset 0, and the twin contrast equal to the raw contrast. Not run for the in-batch layout of this
  version: the tests exercise the check on noiseless expected counts of the 20 circuits; a local run at 2,048 shots per
  circuit precedes the owner's approval request.
- QX remote (type 1): the same series, a written case for the owner's approval (repository rule), 4 batches.
- Ry (type 5): not built for the decision (predecessor CASE.md, owner decision 2026-11-07: 1,024 shots per job and an
  undocumented noise model). The one Ry check that adds information is the bracket arithmetic on a backend with nonzero
  readout error: a single `[readout-0, coin-0 twin, coin-1 twin, readout-1]` batch of b0 on a 5-qubit translation
  (`docs/notes/quantum_inspire/ry-emulator.md`, "Do a Ry emulator run"), whose corrected twin readings land within 3
  standard errors of 1/2 while the raw readings carry (e10 - e01) / 2. Ry is flagged `is_hardware`, so a manifest that
  selects `wave-v1` gives it 5 circuits per batch, 3 queued batches, a 60 s pause after a wave and the account's one
  pause clock (Hardware policy above). Written case, owner approval, not run.

## Residual risk

- The power rule holds under both drift models (Operating characteristics); the stress that governs the hardware is a
  hypothesis. The batch bound 16.266 is a case-specific change of the preregistered gate, and a gate tripped by real
  drift reads `unresolved_batch`, as it did in the retained series.
- The FAQ's "job" is ambiguous (Hardware policy); a provider answer settles whether a wave reads as 3 or 15 jobs.
- The retained b0 base replicates differ: 0.0162 then 0.0393 (se 0.0028 each, 0.0039 for the difference, chi-square
  34.86 above both 10.83 and 16.27), so the retained series reads `unresolved_batch`. Hypothesis: a drift of the offset itself, which the
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

## Submission commands (not run)

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
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_one_cz_null_bracketed_qx" "$RUNS" "$STAMP" "QUOTE"
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

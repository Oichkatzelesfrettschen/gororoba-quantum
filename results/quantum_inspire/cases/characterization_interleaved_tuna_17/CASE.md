# Case: Tuna-17 interleaved T1 at per-qubit delays, drive-context crosstalk arm and q12 Ramsey phase scan

Status: approved by the owner on 2026-11-19, the QX twin first; the QX twin is submitted and collected (its case records the outcome). Tuna-17 is not yet submitted to any backend; a waiter submits each batch when the device reads idle.
Generator and checker: `scripts/qi_tuna17_interleaved_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this
directory except this one, and the QX twin `../characterization_interleaved_qx/`). The case follows the record of
[the 2026-11-16 characterization](../../../../docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md) and its
[case](../characterization_tuna_17/CASE.md).

The batch order comes from one retained QRNG draw, `docs/evidence/anu_qrng/draw-2026-11-19T164737Z.json` (ANU, 256 uint16 values, sha256
f1c4bd68917eaf5142c716814fe7e6127e68ad78c450e80036eafe3187e34e65; the order consumes 59 plus any rejected values), which `qrng_request.json`
names and `DRAW` in the generator holds. The batch directories, their circuits and `schedule.json` are written from it, and `--check` reproduces them.

## What the run measures

Three arms, each its own series directory, on the same 17-qubit register as the retained series.

- `interleaved_t1`: the T1 shape at per-qubit delays. The retained series found a single exponential on 2 of 17 qubits, a 5 us point
  below the fit on 14 of 17 and an 80 us point above it on 16 of 17, and a positive step on the batch that held the three longest delays.
  Here qubit i waits d(i, m) cycles for six multipliers m of 0.5, 1, 2, 4, 8 and 12 times its retained plateau T (the generator's
  `PLATEAU_T_US`, rounded half up to a 20 ns cycle), in three rounds, and every provider batch carries both anchors.
- `crosstalk`: drive-and-readout context dependence. The coupler graph splits into class A = {0, 4, 5, 6, 10, 11, 12, 16} and class B' = {1, 3, 7, 8, 9, 13,
  14, 15} (class B without qubit 2). Six conditions (T1 at 5, 20 and 80 us; the X90 ladder at 32, 128 and 256 pulses) each run one batch of
  {A driven, B' driven, all 17 driven}. One batch of context anchors holds {readout-0, A prepared in 1, B' prepared in 1}. One batch holds
  {q1 alone, q2 alone, all 17} at the 128-pulse ladder, the direct test of the q1/q2 pair (retained: q2 reads 0.046 alone and 0.893 with q1
  driven, [experiments](../../../../docs/notes/quantum_inspire/experiments.md)), which share no coupler and so are not separated by the class split.
- `q12_phase`: a Ramsey circuit X90, Rz(angle), X90 on q12 only, six angles k pi/3 (the processor's pi/36 grid, virtual and zero time), at waits of
  0 and 25 cycles. The fringe offset is the static z rotation between two pulses, which the null-rotation scan's refit
  ([record](../../../../docs/notes/quantum_inspire/tuna17-null-rotation-scan-phase-refit.md)) places at about -0.151 rad on q12 after each pulse.

## Why a simulation and the retained data cannot answer it

The retained T1 batches hold each delay once, so a batch step and a tail share the same columns of the design; with one job per delay no replicate
exists to separate them, and the anchors lie in other batches. The half-drive comparison needs qubits driven in subsets, which no retained circuit
holds. The q12 term is a post-hoc fit of the retained counts; only a new measurement on that qubit tests it. A noise simulation takes the quantities
as inputs.

## Circuits and batches

A hardware batch holds at most three circuits (`qi_platform.py`, `HARDWARE_BATCH_CIRCUITS`). A provider batch is the unit that showed the step, so the
case keeps that name for it and calls the full pass of six multipliers a round.

| Arm | Provider batches | Content of a batch | Jobs | Shots per job |
|---|---|---|---|---|
| interleaved_t1 | 18 (3 rounds of 6) | readout-0, t1-0 and one delay circuit of one multiplier, in a rotating order | 54 | 8,192 |
| crosstalk | 8 | six conditions of {A, B', all}; the context anchors; the q1/q2 pair; the three circuits in a seeded order | 24 | 8,192 |
| q12_phase | 4 | one triad of three Ramsey angles at one wait, the waits interleaved 0, 25, 0, 25 | 12 | 4,096 |

Totals: 30 provider batches, 90 jobs, 688,128 shots (54 x 8,192 + 24 x 8,192 + 12 x 4,096) and 660.2 s of execution by the model of 2.6 s per job
plus 0.53 ms per shot plus the circuit's wait per shot, against the retained series' 6 batches, 14 jobs, 147,456 shots and 115.8 s: 5.7 times the
retained expected seconds. Per arm: 433.7 s, 169.2 s and 57.3 s. Each arm is its own series and its own admission, so the owner may approve them
separately.

- Timing. For multiplier m, d(i, m) is qubit i's delay and D(m) the largest over the 17 qubits. The delay circuit gives every qubit a chain of exactly
  D(m): `wait(D - d)`, `X`, `wait(d)`, then the common `barrier` and `measure`; a wait of 0 cycles is omitted. The X-to-barrier wait of qubit i is d(i, m)
  whether the scheduler places a chain early or late, so the circuit does not depend on the scheduler direction. Both anchors of the batch carry the
  same D(m): readout-0 is `wait(D)` on every qubit; t1-0 is `wait(D)` on every qubit, then X on every qubit. `--self-test` and the tests assert, for
  every circuit, that each qubit's summed wait before the barrier equals D(m) and that its X-to-barrier wait equals d(i, m), that no wait or gate follows the barrier
  (the barrier closes each qubit's timing), and that each crosstalk, context-anchor, readout and Ramsey circuit runs its stated gate sequence (the driven qubits' X and
  wait or X90 pulses, the Ramsey target's X90, wait, Rz and X90, and nothing on the other qubits); a circuit that breaks any of these is rejected.
- The longest delay is 17,423 cycles (348.5 us, qubit 10 at 12 T, plateau T 29.04 us), 4.4 times the longest retained wait of 4,000 cycles (80 us). A
  job of that batch waits about 2.9 s per 8,192 shots and lasts about 9.8 s, inside the 300 s limit.
- Order. A seeded permutation pi of the six multipliers sets round 1 (pi0 to pi5); round 2 is the cyclic shift by two and round 3 the shift by four; the
  two entries of each consecutive pair are swapped by a seeded coin. The three circuits of a batch take a seeded order that rotates through the three
  slots across rounds, so each circuit holds each slot once per multiplier. The provider may reorder the jobs of a batch (a retained batch ran its
  circuits in an order the platform chose), so the analysis records the round and the executed start of every job.
- Crosstalk circuits. The all-17 T1 and ladder circuits are the retained circuits byte for byte; a class circuit drives and waits on the class qubits only.
  Context anchors are readout-0 and a prepared-1 circuit per class.
- Ramsey angles are k pi/3, written `Rz(angle)` between two `X90` pulses. With a z rotation z after the first pulse the population of the driven qubit is
  (1 + cos(angle + z)) / 2 in the circuit's own sign convention. The two triads {0, 2 pi/3, 4 pi/3} and {pi/3, pi, 5 pi/3} each sum to zero in sine and in
  cosine, so a level shared by the three jobs of a batch is orthogonal to both quadratures of the fringe in an unweighted fit; the fit weights points by
  binomial variance, which cuts a batch level of 0.03 to about a third of the bias a contiguous split leaves.

## Toolchain

The texts use only `X`, `X90`, `Rz`, `wait`, `barrier` and `measure`, all native to the processor ([cQASM notes](../../../../docs/notes/quantum_inspire/cqasm.md)); the
retained runs submitted `wait(40)` and `wait(4000)` and the scan runs submitted `Rz`. hypothesis: the provider accepts `wait(17423)` on 17 qubits; the longest
retained wait is 4,000 cycles and the knowledge base states no bound. `scripts/qi_toolchain_check.py` has not run on these texts (not run: it needs the Quantum
Inspire environment). Its record covers a circuit through the batch manifest that lists it, so this case writes no circuit before the draw and the record
needs a regeneration with the change that sets `DRAW`.

Residual risk and stop rule. The delays rest on unequal waits up to 17,423 cycles that no retained run has exercised, and the arm measures decay beside
neighbors excited at staggered times, which differs from the retained series' simultaneous excitation. A rejected or failed first T1 batch stops the arm
at `--sanity` and the layout returns to the owner; no fallback layout runs automatically.

## Estimator and decision rule

Written before any data of this case; `--analyze` applies it. `--self-test` exercises the design ranks, the order, the admission and submit guards, the circuit timing and
gate sequences, the record validators on one valid and one empty record, the estimator's classes on exact synthetic series, the phase fit and the crosstalk flag and
analysis. Only the test file (`tests/scripts/test_qi_tuna17_interleaved_cases.py`) exercises the replicate gate, the tail-statistic threshold of 200, each field of
the two records, the detuning aggregate, the unusable counts and the simultaneous-versus-staggered comparison. `--self-test` also checks the flag sigma floor and the three tail-verdict outcomes.

1. Population. Each delay job of batch b gives x = (p - a0) / (a1 - a0) from the batch's own prepared-0 and prepared-1 jobs, for qubit i at its own delay d(i, m).
   A level shift common to the three jobs cancels; the zero-delay population is 1 by construction.
2. Variance. Each point carries the binomial terms of its three jobs (with the quarter-count term of the retained analyzer) and the job-specific level variance
   tau squared on each of the three jobs, estimated per qubit from the scatter of the batch spans a1 - a0 beyond their binomial variance, floored at 0 (a
   sigma of 0.0034 pooled over 17 qubits from the retained anchors).
3. Models, by weighted least squares over the 18 points: single exponential (T), plateau (T and a constant c), two-rate (fast T, slow T and slow weight). The
   lack-of-fit probability of a model is the upper chi-square tail of its weighted sum of squares.
4. Replicate check. The three rounds repeat each multiplier, so the 6 groups give a pure-error chi-square (12 degrees of freedom) that needs no model.
5. Per-qubit label, descriptive. Lack-of-fit probability of the single exponential at least 0.01 gives `single_exponential` or `level_shift` (by the unanchored fit) when
   the replicate probability is also at least 0.01, and `unresolved` otherwise; a rejected single exponential gives `tail_plateau` or `two_rate` when that fit
   reaches 0.01 and an AICc gain of 4, the replicates hold and the choice between the two follows the AICc; otherwise `unresolved`. The labels and every count
   of them decide nothing.
6. Registered statistic. The pooled verdict (`pooled.tail_verdict`) is `tail_confirmed` when `tail_statistic` >= 200, `inconclusive` when it is below 200 and fewer than 15 of the 17
   qubits are usable (`MIN_USABLE_QUBITS`; a chip with fewer qubits needs all of them), and `not_confirmed` otherwise, so too many dropped qubits cannot read as a failed tail. `tail_statistic` is the sum over usable qubits of the AICc gain of the
   lower-AICc tail fit over the single exponential, counted only where that fit's own lack-of-fit probability and the replicate probability both reach 0.01.
   A qubit that reads `unusable` (anchors too close or too few points) adds nothing to `tail_statistic`, a sum of nonnegative gains, so a dropped qubit moves the verdict
   toward the null; `pooled.unusable_qubits` records the count, and the crosstalk and phase arms record `unusable_normalizations` and `unusable_scans`.
   Descriptive fields (`descriptive_single_exponential_accepted`, `descriptive_single_exponential_rejected` and `descriptive_label_count_reaches_mark`) carry the
   label counts.

Expected standard errors from the retained counts (`prediction.json`, `interleaved_t1.expected_errors`; the retained plateau model is the truth, tau as above): T1 to
0.09 to 0.25 us per qubit, the plateau constant to 0.0019 to 0.0024, the plateau at least 3 standard errors from 0 on 15 of 17 qubits (qubit 8, whose retained
plateau is 0, and qubit 6 at 2.7 excepted) and at least 4 on 13. With every batch level free and the anchors in the fit, the plateau error of qubit 9
(`design_qubit`; delays 512, 1,024, 2,047, 4,094, 8,189 and 12,283 cycles) is 0.0020 and the design matrix has full column rank (21 of 21); the same design
without anchors has rank 18 of 19 columns, so the anchors, and not the delay rows, identify the batch level. `--self-test` checks both ranks.

## Crosstalk arm: rule and predictions

- Contrasts. A class qubit and condition contrasts its own class circuit (A or B' driven) with the all-17 circuit of the same batch. The arm forms 96 class
  contrasts (16 qubits x 6 conditions; qubit 2 sits in neither class) and 2 pair contrasts (q1 and q2 alone against all 17), 98 in all. A contrast is flagged when
  the readings differ by more than 3.49 standard errors of the difference, the two-sided normal quantile of a Bonferroni level of 0.05 over 102 contrasts, which
  holds the familywise level below 0.05 for the 98 formed. The variance of a reading is its binomial variance plus the job-level variance. The arm holds one anchor
  pair per context, too few to estimate it, so the flag sigma comes from the interleaved arm when the analysis holds it: per qubit, max(the square root of
  `job_level_variance` over the qubit's 18 prepared-0 and 18 prepared-1 interleaved anchor jobs, 0.0034). The floor, the retained pooled value, keeps a zero estimate (7 of
  17 retained qubits read 0 from three pairs) from making the flag anti-conservative. Without the interleaved arm every qubit uses 0.0102, the largest retained per-qubit value
  (q6). The q1/q2 pair contrast uses the larger of its two qubits' sigmas. Each row records its sigma and source (`flag_sigma`, `sigma_source`; `pooled.flag_sigma_by_qubit`). At a
  true job-level sigma of 0.0102 the rule with 0.0102 flags a family of 98 null contrasts with probability 0.046 at populations near 0.5, 0.05 and 0, and the floor 0.0034
  alone would flag it with probability 0.994 near 0.5 and 1.0 near 0.05 and 0 (`crosstalk.family_false_flag_rate_at_true_sigma`); these figures are computed for independent contrasts, and the contrasts of one
  condition batch share one all-17 job, so they are not exact familywise rates. The analysis keeps the reading at 0.0034 as the descriptive field
  `z_at_retained_sigma` and counts the flags it would give (`descriptive_flagged_at_retained_sigma`); the verdict reads the registered flag only. Verdict words:
  "drive-and-readout context dependence"; the arm names no neighbor mechanism.
- Normalization. Half-drive populations and ladder values P(0) normalize by the anchors of their own class context (readout-0 and the class prepared in 1); the
  all-drive reading of a qubit normalizes by the same anchors, so the readout context of the all-drive circuit (the retained q13 reads 0.090 with its neighbors
  excited against 0.044 otherwise) is not separated from the drive; the verdict words name both. The flag reads the raw difference and is unaffected. A class
  qubit whose context anchors span too little keeps its z and flag and loses the normalized values; `pooled.unusable_normalizations` counts those rows.
- Prediction. The pair contrast of q2 flags (the retained 0.046 against 0.893 is far beyond 3.49 standard errors). Falsifier: q2 alone reads within 3.49 standard
  errors of its all-17 reading, which puts the retained q2 failure on another cause. No class contrast carries a prediction; the flagged count is descriptive.
- Descriptive comparison, no decision. `simultaneous_versus_staggered` of the analysis sets the all-drive T1 readings at 5, 20 and 80 us, normalized by each
  qubit's class anchors, beside the qubit's own interleaved fit (the lower-AICc accepted model, the single exponential when none is accepted) evaluated at that wait, and records the
  difference in standard errors of the difference per qubit and wait with the fit's prediction error. A raw interleaved point at the nearest delay would differ in delay as well
  as in context and so measure decay. A systematic sign points at neighbor-state relaxation or assignment under staggered excitation; the registered
  statistic does not read it.
- Follow-up. A single-drive follow-up of the flagged qubits is a second stage with its own admission and is not generated here. It holds about 18 jobs when six of
  eight flagged qubits persist and about 33 when all 11 retained ladder failures persist (clears on 3, 6, 8, 12, 13 and 15).

## q12 phase arm: predictions

- Prediction: the q12 fringe offset with no wait lies in [-0.20, -0.10] rad (the refit's -0.1507 and the window of its stability), with a standard error of 0.0088 rad
  at six angles and 4,096 shots (cosine amplitude 0.45, binomial errors; `expected_phase_se_rad`). Verdict `supports_target` needs the window, a standard error at
  most 0.02 and a cosine fit whose chi-square probability reaches 0.01 (a fit below it reads `poor_fit` before any phase label).
- Detuning: the difference of the two q12 offsets (25 cycles against none) divided by 0.5 us is zero within 0.05 rad over the wait. `q12_phase.detuning` of the
  analysis carries, per qubit, the wrapped difference, its propagated standard error from the two fits, the detuning in rad per us and the registered verdict
  "zero within 0.05 rad" (the difference plus twice its error lies inside 0.05 rad), or "unresolved" when either fringe reads `no_fringe` or `poor_fit`.
- Falsifier of the pulse-located term: a q12 offset at no wait within 0.05 rad of zero (`null`). That refutes a static z rotation between two `X90` pulses as the
  cause of the refit's gain. It leaves the CZ-located term open: the refit fits a z rotation after each pulse and after each CZ to the same chi-square (42,848.82
  for both), and this arm contains no CZ. An offset of +0.15 rad reads `supports_target_opposite_sign` and flags a sign convention difference, not a null.
- What it would change: with `supports_target` the phase-scan case adopts the measured offset and its standard error as a held-out constraint, fixes z12 at it
  in a later refit (one parameter fewer) and the row of the hypothesis moves from post-hoc to confirmed on one day and one qubit. With `null` the q12 term of the
  refit is read as absorbing another misfit and drops to a lead. With `other` the term stays open. The controls q8 and q4 of the earlier layout are not run.
- The static rotation measured here includes any frame offset of the drive; the arm separates it from a detuning only through the two waits, and not from a
  pulse-count-dependent term.

## Admission

Each condition holds immediately before each batch is submitted; `--submit` enforces them, and none holds today, since nothing has run. The wording separates two cases:
the initial admission of a batch, which refuses before a run directory or a remote write exists, and a retry after a pause refusal, which reads again and refuses
with the run directory and its earlier admission record already in place.

- The compute API reads, before every submit attempt (a retry after a pause refusal reads again), the Tuna-17 backend type and every instance of it as exactly
  `idle` and the account's queue on the type at 0 (`status_label` and `admission` in the generator, over `qi_status.account`). Any other reading, a missing reading, an
  error document or a type without instances refuses the initial admission before a run directory or a remote write exists; the retained series submitted batch 00 while its status
  read `calibrating` and executed 8 h 20 min later.
- No other series of the account is in flight, as in the retained case. The pause and the one-batch-queued rule are account-wide.
- The QX dry run of the twin is collected and its analysis reads the noiseless expectation (`--local` and the twin's own analysis).
- The retained draw named in `qrng_request.json` is in `docs/evidence/anu_qrng/` and `DRAW` names it.
- The owner approves each arm.

## Provenance fields

Every run directory (named STAMP-CASE-ARM-batch-NN) holds `admission.json` (the status label, queue and attempt number read immediately before its submit) and
`status-trace.json` (the status read once at submission and every 15 s while the collection waits, and once after). `--sanity` validates every field of both
records (schema, the series' backend type, status `idle`, own queue 0, a positive attempt number and a UTC stamp for `admission.json`; schema, the poll interval and each
row's UTC stamp, status text and own-queue reading for `status-trace.json`), also requires
`backend_status_at_submit` of `submission.json` to read `idle`, and takes each job's start from `queued_at` in `results.json` (the retained notes read it as the
execution start), assigns it the last trace read at or before it, and stops the series when that read is not `idle` or `executing` or lies more than 45 s earlier. The
analysis lists the round and that start for every T1 job. The status reader of `--submit` calls `qi_status.account` through the Quantum Inspire interpreter and has not run against
the live service.

## Pre-flight

- Hypothesis: the single exponential fails on the retained T1 data because of a tail or a two-rate decay and not because of a batch level; the retained ladder
  failures and the q1/q2 reading depend on which qubits are driven together; and a static z rotation of about -0.15 rad on q12 exists between two X90 pulses.
- Quantity: `tail_statistic` (the sum of gated AICc gains, registered threshold 200) from the anchored population of each qubit at six own delays in three rounds;
  per class qubit and condition the half-drive minus all-drive reading in standard errors; the fringe offset of q12 in radians with its standard error.
- Falsifier: `tail_statistic` below 200 with at least 15 usable qubits (fewer reads inconclusive); no pair or class contrast above 3.49; a q12 offset within 0.05 rad of zero.
- Predicted outcome: `tail_statistic` at or above 200; the q2 pair contrast flagged; q12 at -0.15 rad (window -0.20 to -0.10) with a standard error of 0.0088 rad.
- Simulated figures (compute-host pass of the layout review, 1,000 joint series per tail cell and 10,000 per null; the analyzer's own tau estimate from the simulated
  anchors, constrained plateau, two-rate fit and replicate gate over all rounds): the null 99.9th percentile of the statistic is 23.5; the worst-cell power of
  `tail_statistic` >= 200 over three tail truths and six nuisances is 0.996; the old count rule (12 of 17 qubits) has power 0.000 under a two-level batch shift.
  These are simulated figures. Limits: qubits share a batch shift only in one scenario, the model has no readout-context term and no neighbor-history term, and
  the truths are the retained fits without parameter uncertainty.
- Budget and retained-rate comparison: 30 batches, 90 jobs, 688,128 shots, 660.2 s by the model (5.7 times the retained 115.8 s), 0 credits (every retained job charged 0);
  the series lasts its execution, the account-wide pauses of 30 s per batch and the queue wait of each batch. The QX twin's expected seconds are in its `prediction.json`, an upper
  figure for the emulator (the retained twin took 178 s against 44 s predicted, from gate-count growth that these circuits do not have).

## Record

`--sanity RUN_DIR` after each collection: every job completed with all its shots, the anchor circuits read their fixed outcome on all but three qubits, the run holds
its admission record and status trace, and no job started outside `idle` or `executing`. Batches that hold no anchor circuit (the crosstalk condition batches and the
Ramsey batches) get the job and provenance checks alone. `--analyze OUT RUN_DIR...` after a series, with `--prediction` naming this directory's `prediction.json`. The change that
retains the runs extends `scripts/qi_retained_context.py` to read the analysis rows, and its ledger row takes the seed indices of `schedule.json`.

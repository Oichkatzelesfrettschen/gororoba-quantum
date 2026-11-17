# Case: Tuna-17 interleaved T1, single-qubit arm and q12 Ramsey phase scan

Status: written case awaiting the owner's approval; nothing has been submitted to any backend, the emulator included.
Generator and checker: `scripts/qi_tuna17_interleaved_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this
directory except this one, and the QX twin `../characterization_interleaved_qx/`). The case follows the record of
[the 2026-11-16 characterization](../../../../docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md) and its
[case](../characterization_tuna_17/CASE.md), whose circuit bytes it reuses for the six retained delays.

The batch order waits for one retained QRNG draw. `qrng_request.json` names the ANU request (256 uint16 values; the order consumes
190 plus any rejected values); no draw was made while this case was written, so the batch directories and `schedule.json`
do not exist yet and `--check` prints a skip. Setting `DRAW` in the generator to the retained path and running `--write` creates them.
No batch can be submitted before that.

## What the run measures

Three arms, each its own series directory, on the same 17-qubit register as the retained series.

- `interleaved_t1`: the T1 shape. The retained series found a single exponential on 2 of 17 qubits, a 5 us point below the fit on 14
  of 17 and an 80 us point above it on 16 of 17, and a positive step on the batch that held the three longest delays
  (batch 02). That batch also held the only delays no other batch repeated, so a level shift and a tail were aliased with the
  delay. Here every delay runs in two rounds, in a different seeded random order each, and every provider batch carries
  both anchors.
- `single_qubit`: qubits 5, 7 and 14 (predicted to clear the X90 ladder, did not) and 0, 4, 10, 11 and 16 (no prediction, failed),
  one qubit driven at a time with the other sixteen idle, for the T1 populations at 5, 20 and 80 us and the ladder at 32, 128 and
  256 pulses. A difference from the 17-qubit values is a simultaneous-drive effect; no difference puts the figure on the qubit.
- `q12_phase`: a Ramsey circuit X90, Rz(angle), X90 on one qubit, eight angles in steps of pi/4 (the processor's pi/36 grid,
  virtual and zero time), on q12 with no wait and with a 500 ns wait, and on q8 and q4 with no wait. The fringe offset is the static
  z rotation between two pulses, which the null-rotation scan's refit
  ([record](../../../../docs/notes/quantum_inspire/tuna17-null-rotation-scan-phase-refit.md)) places at about -0.151 rad on q12 after each pulse.
  The refit chose that term from ten candidates on the retained counts, and the arm tests it on counts the fit never saw.

## Why a simulation and the retained data cannot answer it

The retained T1 batches hold each delay once, so a batch step and a tail share the same columns of the design; with one job per
delay no replicate exists to separate them, and the anchors lie in other batches. The single-qubit comparison needs qubits driven
alone, which no retained circuit holds. The q12 term is a post-hoc fit of the retained counts; only a new measurement on that
qubit tests it. A noise simulation takes the quantities as inputs.

## Circuits and batches

A hardware batch holds at most three circuits (`qi_platform.py`, `HARDWARE_BATCH_CIRCUITS`), so "every batch holds the full delay set" cannot hold.
A provider batch is the unit that showed the step, so the case keeps that name for it and calls the full pass of delays a round.

| Arm | Provider batches | Content of a batch | Jobs | Shots per job |
|---|---|---|---|---|
| interleaved_t1 | 22 (2 rounds of 11) | readout-0, t1-0 and one delay circuit, in a seeded random order | 66 | 8,192 |
| single_qubit | 32 (8 qubits of 4) | per qubit: three batches of readout-0, the qubit's prepared-1 circuit and one of its T1 circuits; one batch of its three ladder circuits; the four in a seeded random order | 96 | 8,192 |
| q12_phase | 11 | three of the 32 Ramsey circuits in a seeded random order (the last batch holds two) | 32 | 8,192 |

- `t1-0` (X on every qubit, no wait) is the prepared-1 anchor and the zero-delay point; `readout-0` (no gate) is the prepared-0 anchor. Both
  are in every interleaved batch, and their text is the retained `readout-1` and `readout-0`.
- Delays of `interleaved_t1`, in 20 ns cycles (the cycle is the retained series' reading and the processor's documented one): 50, 125, 250, 375,
  500, 1,000, 2,000, 4,000, 6,000, 8,000 and 12,000, that is 1, 2.5, 5, 7.5, 10, 20, 40, 80, 120, 160 and 240 us. The retained six
  (0, 5, 10, 20, 40, 80 us) stay byte for byte. The four points at 1 to 7.5 us resolve the fast scale of 3 to 9 us the biexponential fits
  gave on qubits 9, 11, 12, 14 and 15. The points at 120 to 240 us bound the slow scale, which the retained window left open above on 8
  of 17 qubits. The longest job of the series waits 12,000 cycles on 8,192 shots (about 2.0 s of wait) inside a 300 s limit.
- Single-qubit circuits drive and wait on one qubit and read all 17. Their readout pair is the batch's own `readout-0` and the qubit's
  prepared-1 circuit, so the pair is taken in the same context as the data.
- Ramsey angles are k pi/4 for k = 0 to 7, written `Rz(angle)` between two `X90` pulses. With a z rotation z after the first pulse the
  population of the driven qubit is (1 + cos(angle + z)) / 2 in the circuit's own sign convention, which is the refit's (`gate_noise_histogram_fit.py`
  applies the circuit's `Rz` and its z-after-pulse term through one rotation function, read in both branches). The wait of 25 cycles on q12 adds a phase of
  detuning times 500 ns, so a detuning shows as a difference between the two q12 scans.

Totals: 65 provider batches, 194 jobs, 1,589,248 shots, 1,364.9 s of execution by the model below, against the retained series' 6 batches,
14 jobs, 147,456 shots and 115.8 s. The series is 11.8 times the retained cost in expected execution seconds. It exceeds the retained cost
because a round of eleven delays under a three-circuit batch limit needs eleven batches with their anchors, and the single-qubit arm
holds eight qubits at four batches each. Each arm is its own series and its own admission, so the owner may approve them separately:
22 batches, 66 jobs and 469 s for `interleaved_t1`; 32 batches, 96 jobs and 673 s for `single_qubit`; 11 batches, 32 jobs and 222 s for
`q12_phase`. A compact layout (anchors in two batches of a five-batch round, three delays per batch) would cost 15 jobs a round and
cannot measure a batch level directly (see the decision in the pull request).

## Toolchain

The 101 texts of the tuna_17 profile and the twin's use only `X`, `X90`, `Rz`, `wait` and `measure`, all native to the processor
([cQASM notes](../../../../docs/notes/quantum_inspire/cqasm.md)); the retained runs submitted `wait(40)` and the scan runs submitted `Rz`.
hypothesis: the provider accepts `wait(12000)` on 17 qubits; the longest retained wait is 4,000 cycles and the knowledge base states no
bound. `scripts/qi_toolchain_check.py` has not run on these texts (not run: it needs the Quantum Inspire environment). A rejected job stops its
series at `--sanity` and keeps the batches before it.

## Estimator and decision rule

Written before any data of this case; `--analyze` applies it and `--self-test` recovers its classes from exact synthetic series.

1. Population. Each delay job of batch b gives x = (p - a0) / (a1 - a0) from the batch's own prepared-0 and prepared-1 jobs. A level
   shift common to the three jobs cancels; the zero-delay population is 1 by construction.
2. Variance. Each point carries the binomial terms of its three jobs (with the quarter-count term of the retained analyzer) and the
   job-specific level variance tau squared on each of the three jobs. tau squared is the scatter of the batch spans a1 - a0 beyond
   their binomial variance, over two, per qubit and floored at 0: a level shift common to the two anchors of a batch cancels in the span,
   as it does in the population, so tau squared holds only the levels the jobs of a batch do not share. Its value from the retained anchors
   (three prepared-0 and three prepared-1 jobs per qubit, in pairs; the middle pair straddles two batches, which leans tau high) is a sigma
   of 0.0034 pooled over 17 qubits. The retained anchors scattered beyond binomial (pooled chi-square 71.0 on 17 degrees of freedom for
   prepared 1), which is why a binomial-only rule is not used. `--self-test` and the tests keep a plateau of 0.01 and of 0.02 readable as
   `tail_plateau` under batch levels of 0.0145.
3. Models, by weighted least squares over the 22 points: single exponential (T), plateau (T and a constant c), two-rate (fast T, slow T
   and slow weight). The lack-of-fit probability of a model is the upper chi-square tail of its weighted sum of squares.
4. Replicate check. The two rounds repeat each delay, so the 11 replicate differences give a pure-error chi-square (11 degrees of freedom) that
   needs no model.
5. Verdict per qubit, in order. Lack-of-fit probability of the single exponential at least 0.01: `single_exponential` if the replicate
   probability is also at least 0.01 and the unanchored fit (pooled prepared pair of all 22 batches, binomial errors) is also acceptable, `level_shift` if the
   unanchored fit fails at 0.01 (the retained misfit was a batch level, which anchoring removes), `unresolved` if the replicates scatter beyond tau.
   Otherwise `tail_plateau` if the plateau fit reaches probability 0.01 and an AICc gain of 4 over the single exponential, `two_rate` if the
   two-rate fit does the same and beats the plateau by a further 4 or the plateau fails, and `unresolved` otherwise.
6. Pooled. The tail is confirmed when 12 or more of the 17 qubits read `tail_plateau` or `two_rate`; a batch level explains the retained misfit when 12
   or more read `single_exponential` or `level_shift`; between them the result is mixed.

Expected standard errors from the retained counts (`prediction.json`, `interleaved_t1.expected_errors`; the retained plateau model is the truth, tau as above): T1 to
0.09 to 0.26 us per qubit, the plateau constant to 0.0018 to 0.0027, the plateau at least 3 standard errors from 0 on 15 of 17 qubits (qubit 8, whose retained plateau is 0, and qubit 6 at 2.7 excepted) and at least 4 on 13. With every batch level free and the anchors in the fit, the plateau error of qubit
`design_qubit` is 0.0021 and the design matrix has full column rank (25 of 25); the same design without anchors has rank 22 of 23 columns, so the
anchors, and not the delay rows, identify the batch level. `--self-test` checks both ranks.

Predictions, from the retained rows. The single exponential is rejected on the 15 qubits whose retained fit failed (all except 8 and 13) and
accepted on 8 and 13. Falsifier: it is accepted on 6 or more of those 15, or on 3 or more of the six qubits 2, 9, 11, 12, 14 and 15 whose retained step
exceeded every anchor shift, which would put the retained misfit on the batch level after all. A batch level would show as `level_shift` on 12 or more
qubits. The pooled prediction is the tail confirmed.

## Single-qubit arm: predictions

Per qubit, from the retained ladder and T1 rows (`prediction.json`, `single_qubit`). The rule: a retained corrected P(0) of 0.25 or below at any count needs a
coherent rotation, which dephasing by neighbors does not make (it drives P(0) toward 0.5), so that qubit keeps failing; a qubit whose lowest P(0) lies
above 0.25 is predicted to clear (hypothesis: the stated rule separates crosstalk from the qubit's own pulse; this case tests it).

| Qubit | Retained P(0) at 32, 128, 256 | Predicted single-qubit ladder | Retained 17-drive population at 5, 20, 80 us |
|---|---|---|---|
| 5 | 0.389, 0.767, 0.530 | clears | 0.787, 0.349, 0.029 |
| 7 | 0.923, 0.463, 0.135 | fails | 0.778, 0.462, 0.055 |
| 14 | 0.029, 0.843, 0.713 | fails | 0.617, 0.339, 0.092 |
| 0 | 0.914, 0.485, 0.532 | clears | 0.734, 0.319, 0.017 |
| 4 | 0.940, 0.551, 0.192 | fails | 0.821, 0.371, 0.056 |
| 10 | 0.892, 0.088, 0.840 | fails | 0.852, 0.517, 0.106 |
| 11 | 0.012, 0.781, 0.417 | fails | 0.801, 0.449, 0.066 |
| 16 | 0.901, 0.199, 0.559 | fails | 0.789, 0.421, 0.042 |

- Ladder: six of eight keep failing and two (0 and 5) clear. Falsifier: 4 or more clear, which makes crosstalk the larger part, as issue 941 proposed; 6 or more
  failing is the pooled reading that places the error on the qubit's own pulse.
- T1: the single-qubit populations at 5, 20 and 80 us equal the arm A anchored populations at those delays within 3 combined standard errors on 6 or more
  of 8 qubits. Falsifier: 5 or more qubits with a larger difference at any delay, which makes the neighbors' state matter for T1.
- The ladder verdict is the retained one (corrected P(0) at least 0.5 at all three counts) with the mean of the qubit's three readout pairs; the T1 populations use the pair of their own batch.

## q12 phase arm: predictions

- Prediction: the q12 fringe offset with no wait lies in [-0.20, -0.10] rad (the refit's -0.1507 and the window of its stability), with a standard
  error near 0.005 rad at 8 angles and 8,192 shots (cosine amplitude 0.45, binomial errors). Verdict `supports_target` needs the window and a standard
  error at most 0.02.
- Controls q8 and q4, no wait: the refit has no z term on them, so the prediction is a null, `|phase| + 2 se <= 0.05`.
- Detuning: the difference of the two q12 offsets (25 cycles against none) divided by 0.5 us is zero within 0.05 rad over the wait; the sensitivity is about 0.02 rad/us.
- Falsifier of the pulse-located term: a q12 offset at no wait within 0.05 rad of zero (`null`). That refutes a static z rotation between two `X90` pulses as the
  cause of the refit's gain. It leaves the CZ-located term open: the refit fits a z rotation after each pulse and after each CZ to the same chi-square (42,848.82 for both),
  and this arm contains no CZ. An offset of +0.15 rad reads `supports_target_opposite_sign` and flags a sign convention difference, not a null.
- What it would change: with `supports_target` the phase-scan case adopts the measured offset and its standard error as a held-out constraint, fixes z12
  at it in a later refit (one parameter fewer) and the row of the hypothesis moves from post-hoc to confirmed on one day and one qubit. With `null` the q12 term of the refit
  is read as absorbing another misfit and drops to a lead; the five-term models stand. With `other` the term stays open.
- The static rotation measured here includes any frame offset of the drive; the arm separates it from a detuning only through the two waits, and not from a
  pulse-count-dependent term, which a longer pulse train would test and this arm does not.

## Admission

Each condition holds immediately before each batch is submitted; `--submit` enforces them, and none holds today, since nothing has run.

- The compute API reads, before every submit attempt (a retry after a pause refusal reads again), the Tuna-17 backend type and every instance of it as exactly `idle` and the account's queue on the type at 0 (`status_label` and `admission`
  in the generator, over `qi_status.account`). Any other reading, a missing reading, an error document or a type without instances refuses before a run directory or a
  remote write exists; the retained series submitted batch 00 while its status read `calibrating` and executed 8 h 20 min later.
- No other series of the account is in flight, as in the retained case. The pause and the one-batch-queued rule are account-wide.
- The QX dry run of the twin is collected and its analysis reads the noiseless expectation (`--local` and the twin's own analysis).
- The retained draw named in `qrng_request.json` is in `docs/evidence/anu_qrng/` and `DRAW` names it.
- The owner approves each arm.

## Provenance fields

Every run directory (named STAMP-CASE-ARM-batch-NN) holds `admission.json` (the status label, queue and attempt number read immediately before its submit) and `status-trace.json` (the status read once at
submission and every 15 s while the collection waits, and once after, appended file-wide after each read so a resumed collection keeps the earlier rows). `--sanity` also requires `backend_status_at_submit` of `submission.json` to read `idle`, and takes each job's start from `queued_at` in `results.json` (the retained notes read it as the
execution start), assigns it the last trace read at or before it, and stops the series when that read is not `idle` or `executing` or lies more than 45 s earlier. The
trace's spacing is a bound, not a measurement of the start: a status that changed inside a gap shows only at the next read. The status reader of `--submit` calls
`qi_status.account` through the Quantum Inspire interpreter and has not run against the live service. A trace file in a run directory passes `qi_records`, which reads only the
files it names.

## Pre-flight

- Hypothesis: the single exponential fails on the retained T1 data because of a tail or a two-rate decay and not because of a batch level; the ladder failures of
  0, 4, 5, 7, 10, 11, 14 and 16 persist at six of eight qubits with the neighbors idle; and a static z rotation of about -0.15 rad on q12 exists between two X90 pulses.
- Quantity: per qubit the anchored population at 11 delays in two rounds with its lack-of-fit probabilities and AICc; per arm qubit the single-drive population at
  5, 20 and 80 us and the corrected ladder P(0); the fringe offset of q12, q8 and q4 in radians with its standard error.
- Falsifier: the single exponential accepted on six of the 15 qubits that failed it, or on three of the six step qubits; four or more single-qubit ladders clearing; five or more qubits with a
  T1 population differing from the 17-drive value; a q12 offset within 0.05 rad of zero.
- Predicted outcome: tail confirmed on 12 or more qubits; single exponential accepted on 8 and 13; six of eight ladders failing; six of eight single-drive T1 populations within 3 standard errors of
  the 17-drive ones; q12 at -0.15 rad (window -0.20 to -0.10) with a standard error of 0.005 rad; q8 and q4 null.
- Budget and retained-rate comparison: 65 batches, 194 jobs, 1,589,248 shots, 1,364.9 s by the model (11.8 times the retained 115.8 s), 0 credits (every retained job charged 0);
  the series lasts its execution, 64 account-wide pauses of 30 s and the queue wait of each batch. The QX twin costs 612 s by the same model, an upper figure for the emulator
  (the retained twin took 178 s against 44 s predicted, from gate-count growth that these circuits do not have).

## Record

`--sanity RUN_DIR` after each collection: every job completed with all its shots, the anchor circuits read their fixed outcome on all but three qubits, the run holds
its admission record and status trace, and no job started outside `idle` or `executing`. Batches that hold no anchor circuit (the ladder batches and the Ramsey batches) get the job and
provenance checks alone. `--analyze OUT RUN_DIR...` after a series, with `--prediction` naming this directory's `prediction.json`. The change that retains the runs extends
`scripts/qi_retained_context.py` to read the analysis rows, and its ledger row takes the seed indices of `schedule.json`.

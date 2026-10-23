# Tuna-17: result registers, readout drift and operating rules

Tuna-17 (backend type 7, `tuna_17`) is the Quantum Inspire device the
repository runs its hardware cases on. This note collects what the retained
runs establish about its result format, its readout calibration, and the
procedures that kept a shared account's batches intact. Each statement names
the run, record or gate that carries its evidence; a statement marked
"inferred" has no retained probe behind it.

## Result registers

- Tuna-17 returns the full classical bit register. A `bit[34]` circuit on
  `qubit[17]` comes back as 34-character strings that carry every mid-circuit
  outcome (the series P and Q runs under `results/quantum_inspire/runs/`;
  claim `qi-tuna17-register-and-readout-state`). The readout ring-down
  analysis uses those bits for its postselection check.
- QX returns its measurement register, not the bit register (C21 in
  [qx-runs.md](qx-runs.md)), so a case that reads mid-circuit bits on
  Tuna-17 has no QX counterpart for them.
- The Ry emulator rejects any bit declaration and fails `measure` at compile
  ([ry-emulator.md](ry-emulator.md), gate core-385 over the three probe runs).
- QX and Tuna put qubit 0 at the rightmost character; the Ry emulator puts it
  at the leftmost (README.md, Binding rules, execution facts).

## Readout calibration drift

The platform publishes no calibration data, so the readout-0 and readout-1
circuits of the retained runs are the only calibration record. The device
context (`results/quantum_inspire/readout_ringdown_tuna_17_device_context.json`,
gate core-387) lists them per qubit in timestamp order; a change is located
only to the interval between two retained runs.

- q9 idle P(1|0) measured 0.026 to 0.027 in the coupler-map and series P
  batch-00 runs, 0.271 in the first series P recalibration batch, and 0.276 to
  0.288 in every later run through the three zero-divisor batches. The gates
  applied on the qubit in those circuits, so the shift is a readout or
  state-preparation change of the qubit.
- q0 and q6 prepared in |1> read P(1|1) of 0.847 and 0.670 after a 2 us wait
  in series P batch-00 and 0.393 and 0.144 in the recalibration run that
  follows the platform calibration. With no wait the zero-divisor batches
  read 0.565 and 0.163, so for q6 the loss does not grow with the wait: the
  readout of |1> collapsed. The implied-T1 formula of the device context
  assumes an unchanged assignment between runs and gives 14.2 us for q0 and
  5.5 us for q6 from the earlier pair only.
- q15 prepared in |1> read P(1|1) of 0.730 after a 2 us wait in series Q
  batch-00 and 0.914 after the same wait in the Q-recal-053951 run. With no
  wait it reads 0.975 to 0.979, so the 2 us wait cost 0.06 to 0.25 depending
  on the run. A single T1 cannot produce both (inferred: readout variability
  between runs).
- The platform's "calibrating" and "benchmarking" states hold queued jobs
  (observed through the hardware status read; the states are not retained, so
  no record carries their durations). The platform schedules them itself,
  and a job that meets one waits ([site/faq.md](site/faq.md), "automated
  tuning program"); the account-wide pause in `qi_platform.py submit` paces
  the account and is not needed for them.

- The fault cleared by the afternoon. The box-kite pre-T0 batch (jobs
  finished 15:38Z, after the platform benchmarking the operator observed at
  15:34Z) reads Q0 P(1|1) 0.973, Q6 0.957 and Q9 P(1|0) 0.018, against the
  morning's 0.39, 0.14 and 0.27 to 0.29; every qubit of the box-kite layout
  reads P(1|1) 0.912 to 0.975 and P(1|0) at most 0.045. Its double-X
  discriminator was not read, because its precondition requires the fault
  (claim `qi-tuna17-boxkite-pre-t0-readout-recovered`).

Consequence for the ring-down analysis: the preregistered rule inverts the
series' batch-00 readout assignment for every batch. Where the device drifts
after batch-00, a target's Ramsey visibility leaves [0, 1] (q6 at 1.08 in
series P, q15 at 1.28 to 1.46 in series Q) and its tail class rests on a
stale correction. A time-nearest calibration is a sensitivity analysis
outside the rule.

## Readout ring-down results

- Series P, targets Q0, Q4, Q5, Q6, Q10, Q11, Q12, Q16: verdict "not
  detected" (3 of 7 usable targets classify as tails); claim
  `qi-tuna17-readout-ringdown-P`, gate core-386.
- Series Q, targets Q1, Q2, Q3, Q7, Q8, Q9, Q13, Q14, Q15: verdict "not
  detected" (3 of 7 usable targets, Q9, Q14 and Q15, classify as tails,
  Q15 under the all-shot estimator only; Q7 and Q8 fail the 0.3 visibility
  floor); claim `qi-tuna17-readout-ringdown-Q`,
  gate core-430. Series Q uses one readout batch (Q-batch-00); the
  Q-recal-053951 run is a repeated calibration outside the analysis, because
  duplicate readout files raise.
- Neither series fits the tail model on its classified targets in general:
  the rule compares H2 with H1 and tests neither fit, so a tail class marks
  arm-to-arm structure beyond shot noise. Series Q fits H2 on Q9 alone
  (chi2 6.95 on 3 degrees of freedom).

## Sanity checks and exemptions

`qi_readout_ringdown_cases.py --sanity RUN_DIR` guards each series with a
readout-error ceiling (`--sanity-readout-error`, 0.35 for series Q) and
exempts named qubits (`--sanity-exempt`). An exemption covers every check on
the qubit: the series Q batch-01 mid-circuit P1 check kept failing on an
exempted qubit until the exemption reached that check.

## Runner and account rules

- A run directory that holds `submission.json` and no `results.json` is
  submitted and uncollected; `qi_platform.py collect` finishes it and no
  resubmit is ever needed. A runner refuses an existing run directory so a
  resumed series cannot write a batch's files into another run's folder.
- Process control reads the run directories, never a harness task-output
  file, whose lines are flushed late: a handover keyed to those lines can stop
  a runner moments after a submit.
- The quantuminspire 4.1 `AuthManager.refresh_tokens` rotates tokens in
  memory and never saves them, and it exchanges only within 5 s of expiry.
  A second process then presents a spent refresh token. With reuse detection
  (inferred; no probe), that revokes the login. `Client.refresh` in
  `scripts/qi_platform.py` takes an flock, rereads the file, exchanges near
  expiry and writes the rotated tokens back. A long-lived process started
  before that rule, such as an MCP server, holds stale tokens and restarts
  after `qi login`.
- Sessions that share the account alternate hardware batches at Ramsey-pair
  boundaries, paced by the account-wide pause (`HARDWARE_PAUSE_SECONDS`,
  [usage.md](usage.md#pause-escalation)). Series P and Q calibrate
  readout once per series, in batch-00 and in separate recalibration runs;
  batches Q-05 to Q-08 hold Ramsey arms only, so readout drift after the
  last calibration enters their correction unseen, as the stale Q15
  correction above shows. A series that must correct each batch for its
  own readout state carries a readout-0/readout-1 pair in every batch.
- The pause guard refuses an early submit before any remote write and prints
  the seconds left; the guard counts Ry jobs too, since Ry reports
  `is_hardware: true` ([ry-emulator.md](ry-emulator.md)). A series runner
  therefore retries a refused submit every 30 s, at most 10 times, and
  stops the series when the tenth attempt is refused; a retry never
  duplicates a batch, because the refusal precedes the submission-state
  checkpoint.

## Box-kite T0 depth ladder

Three batches of the reduced two-label LCU of edge (1,10)(4,15) of kite 3
at CZ depths 1, 5 and 9 on the pairs (1,4), (10,13) and (12,14), 16384
shots per circuit, each corrected with its own batch's readout pair
(`results/quantum_inspire/box_kite_tuna_17_pre_t0_analysis.json`, gate
core-425; claim `qi-tuna17-boxkite-t0-depth-ladder`): C(1) = 0.954, C(5) =
0.857 and C(9) = 0.710 (standard errors 0.003), r = 0.9654 per CZ with 99%
interval [0.9638, 0.9671], inside the decision band [0.87, 0.97] as
preregistered and above the prediction [0.87, 0.96]. Every
batch passed its sanity checks, and the QX twins of the three witness
circuits read every replica exactly. C(1) lies above its preregistered
[0.72, 0.82] because that prediction carried the selector's readout factor
(about 0.87) while C(n) is readout-corrected; 0.82 / 0.874 = 0.94.

## Shot order: a 50 Hz line

The retained raw lists are in time order, and that order carries a line at
the 50 Hz grid frequency (`scripts/qi_shot_record_line.py`,
`results/quantum_inspire/tuna_17_shot_record_line.json`, gate core-426 and
gate `core-self-test-09` (`tests/test_cli_self_tests.py`); claim `qi-tuna17-shot-record-50hz-line`).

- A band scan at 0.019 to 0.021 cycles per shot finds it in 72 of 159
  Tuna-17 jobs and in none of 113 QX jobs. On Tuna-17 it is absent from
  all 51 readout circuits, at up to 131072 shots, and all 8 depth-1 LCU
  circuits.
  It is present in Ramsey, CZ-ladder, walk, additivity and Walsh-exemplar
  circuits.
- Its amplitude in P(1) reaches 0.43 on q7 (ring-down Ramsey) and 0.39 on q5
  (coupler-ZZ Ramsey).
- In the follow series the three bright-edge selectors oscillate at 0.19 to
  0.26 at CZ depth 9 and 0.09 to 0.13 at depth 5, and stay below 0.0175 at
  depth 1. Within one job they share one phase on all three pairs.
- The ring-down arms differ only in a wait of tau cycles. Their peak
  frequency rises with tau at 50.4 +- 4.0 Hz, so the source runs in
  wall-clock time, not on the shot index.
- At 50 Hz one shot takes 402.9 to 404.6 us in the ring-down circuits and
  400.7 us in the follow series; the period grows with circuit length, which
  is the slope above. The fitted execution cost of 0.53 ms per shot therefore
  includes about 0.13 ms of per-shot time outside the repetition period.

The inferred mechanism is a chip-wide modulation of qubit frequency or flux
pulses at the mains frequency. No retained probe separates flux pickup from
any other 50 Hz path.

Consequences:
- A job's mean averages its outcome over the line's phase. Any contrast that
  depends on accumulated phase is lowered by an amount set by the modulation
  depth, and that depth can differ between batches.
- The shot index plus a per-job phase gives every shot its line phase. A
  demodulated analysis therefore recovers phase-resolved contrast from data
  a job already returns.
- Block stationarity (16 block means per bit; the smallest per-bit tail
  times the bits scanned) falls below 0.01 in 61 to 75 percent of the
  morning ring-down jobs and in 11 to 33 percent of the box-kite jobs. Within-job
  stationarity depends on the device's state, so each series checks it.

## Readout context

q13's |1> misassignment depends on what the rest of the chip is prepared in.
In the ladder series, readout-1 (all 17 excited) gives e10 = 0.090 and 0.086
and readout-iso-x (q1, q13, q14 alone) gives 0.044 and 0.040, about 45
standard errors apart; q1 and q14 read alike in both contexts (claim
`qi-tuna17-boxkite-ladder-readout-context`). The two circuits differ in the
neighbors' state at measurement and in the X pulses on the neighbors, so
state-dependent readout and drive crosstalk on q13's preparation stay
unseparated. A witness whose data qubit sits beside idle neighbors is
corrected with the isolated rate: on (10,13) the depth-1 coherence reads
-0.997 that way and -1.104 with readout-1. q10's e01 rises by about 0.012
beside an excited q13.

## Run design

[tuna-17-run-design.md](tuna-17-run-design.md) holds the platform
configuration that prices a Tuna-17 batch (decompose-only compilation, the
fitted 2.6 s per job plus 0.53 ms per shot, no published calibration) and the
box-kite follow series built on it: seven batches whose readout pairs bracket
fifteen packed witnesses, sized from T0's r, the readout drift across the T0
batches and the coupler-ZZ map (`docs/evidence/box_kite_follow_design/design.json`,
gate `core-record-check-05` (`tests/test_cli_record_checks.py`) and gate `core-self-test-09` (`tests/test_cli_self_tests.py`)). The series ran on 2026-10-17 from 23:08Z to
23:29Z with every preregistered decision as the census predicts: all six
classification rows, twist equality at |z| at most 2.44 in all four
crossovers, every depth-1 X coherence sign and both walk signs. Its results
section records the depth-9 batch-to-batch scatter of about 0.03, the drift
against T0 seven and a half hours earlier (-0.209 on (12,14) at depth 9) and
the context-dependent q13 readout error (claims
`qi-tuna17-boxkite-follow-crossover` and
`qi-tuna17-boxkite-follow-ladder-drift`).

## Kernel cancellation probe

The kernel cancellation series of 2026-10-23
([qi_cancellation_cases.py](../../../scripts/qi_cancellation_cases.py), claim
`qi-tuna17-kernel-cancellation`) ran a 45-CZ circuit on q4, q8, q11, q12 and
q14 with every rotation on the pi/36 grid, six batches of three circuits at
16384 shots, each batch submitted to collected in about four minutes. The
control q8 read e01 0.030 and e10 0.022. The bright vector, whose ideal odd
part is zero, carried a signed response of -0.0167 +- 0.0039, as large as
the kernel's -0.0222 at phi = pi/36, so a Tuna-17 case preregisters its
decision on the difference from a matched control
([principles](../topics/algebra-hardware-probe-principles.md)); this
series preregistered the kernel against zero, so its matched difference is a
post hoc reading. The kernel's
odd part implies a visibility of 0.134 through its batch pair's readout,
against Garnet's 0.36 at 37 CZ. A three-circuit batch holds one readout
reference, so a pair reads e01 in one batch and e10 in the other and neither
batch's own assignment factor is identified; the spread of the three e01 and
three e10 readings (factor spread 0.0024) enters every corrected error and
moves no decision. Each circuit of a batch runs as its own job
in an order the platform chooses: one listed +, -, -, + contrast ran +, -,
+, -, so an analysis reads the executed order from the jobs' start times.

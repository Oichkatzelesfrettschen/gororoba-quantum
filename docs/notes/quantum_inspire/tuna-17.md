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
  at the leftmost (AGENTS.md, Quantum Inspire execution facts).

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
  no record carries their durations). The account-wide pause in
  `qi_platform.py submit` leaves room for them between batches.

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
  boundaries, and the account-wide pause (`HARDWARE_PAUSE_SECONDS`) gives
  the platform room to calibrate between batches. Series P and Q calibrate
  readout once per series, in batch-00 and in separate recalibration runs;
  batches Q-05 to Q-08 hold Ramsey arms only, so readout drift after the
  last calibration enters their correction unseen, as the stale Q15
  correction above shows. A series that must correct each batch for its
  own readout state carries a readout-0/readout-1 pair in every batch.

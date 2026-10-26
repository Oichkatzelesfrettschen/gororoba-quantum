# N=21 orbit window-dose sweep on ibm_fez: the mechanism case

[UNAPPROVED_CASE.md](UNAPPROVED_CASE.md) is the planner's binding:
- record.json SHA-256 `3d3966ecaab88765fbfdd372c987b453c6380fbb845a36a50ea59ddebfdfce38`;
- one dynamic job of 14 PUBs x 16,384 shots;
- an estimated 25.0 s against a 30 s ceiling, on the backup instance with 412 s remaining.

The layout search and the planning simulation take QRNG seeds. `--seed-transpiler` is
`qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#0` (6224) and `--seed-simulator` is index 1 of the same
draw; both are registered in the runtime ledger.

This note states why the run is needed, what each outcome means, and the decisions the result is read against.
The decisions are preregistered before submission.

## Why this run

Two retained N=21 runs bound the mechanism from either side:
- **Encoded circuit** (ibm_kingston, 336 CZ). The scheduled leaf idle of about 15,000 dt took a contrast the model
  predicted at +0.031 down to a measured +0.0027.
- **Orbit circuit** (ibm_fez, 28 CZ). With about 2,000 dt of idle it kept +0.197.

One parameter-free incoherent idle model fits both (claims `hw-n21-feedback-null-scheduled-idle` and
`hw-n21-orbit-scheduled-idle-control`). Two things remain unsettled:
- Both replays are retrospective and compare different circuits on different backends.
- Fez qubit 143's two-line beat (claim `hw-n21-q143-segmented-lines`) shows that idle error on some qubits is a
  coherent detuning mixture that a T1/T2 model cannot express.

This run adds idle to the short circuit in controlled doses, in one job on one calibration, with and without an
echo that refocuses static detuning. The executed replica sits on ibm_fez qubits 16, 22, 23 and 24, calibration
2026-10-26T01:54:38-07:00; the planner chose ibm_fez over ibm_kingston for this seed. A simulation cannot answer the question: the question is whether the
hardware's idle loss follows the Target's T1/T2, and the simulation assumes that it does.

## Arms

The arms are pairs of feed-forward and omitted-correction members of the bracketed orbit circuit, each scored by
its contrast difference.

| Dose (dt) | Dose (us) | Plain arm, model | Echo arm, model | Model echo gain |
|---|---|---|---|---|
| 0 | 0 | +0.191 | n/a | n/a |
| 3,500 | 14 | +0.122 | +0.136 | +0.014 |
| 7,000 | 28 | +0.059 | +0.092 | +0.034 |
| 14,000 | 56 | -0.045 | +0.027 | +0.071 |

- **Model.** The values are the dry run's sampled planning model (131,072 shots, simulation allowance +-0.023). They
  charge the explicit doses but not the service-scheduled idle, which cost the orbit circuit about 0.03 at dose 0 on
  ibm_fez (+0.208 unpadded against +0.179 padded). They size the run; the decisions use the exact model below.
- **Echo gain under the incoherent model.** The model's echo gain is not zero. The two X pulses on the work bits
  reverse T1's population drift halfway, so amplitude damping biases the echo arm less. A coherent effect therefore
  shows up as echo gain beyond the model's gain, not as gain above zero.
- **Doses.** The 14,000 dt dose matches the encoded circuit's leaf idle.
- **Schedule.** A full-width barrier after the control's reset starts every nonzero dose once the reset ends.

## Preregistered decisions

After `live_run.py --collect`, two scripts at this branch's head run on the run directory:
- `scripts/scheduled_idle_replay.py RUN_DIR --out RUN_DIR/idle-replay.json` writes the model. It is the
  idle-padded exact branch-resolved law under the Target and properties in force at the PUB's execution start, with
  the explicit doses and the service-scheduled idle both charged (`contracts.idle_padded_exact`).
- `scripts/n21_dose_decisions.py RUN_DIR --out RUN_DIR/dose-decisions.json` computes every decision. It takes each
  contract's measured value and shot standard error sigma from the measured laws in `collect.json` and the record's
  score vectors and shot count. An echo gain's error is the two arms' errors in quadrature.

The model is exact, so no simulation allowance enters.
- **D1, idle response exists.** The plain contrast at 14,000 dt minus the plain contrast at dose 0 has a one-sided
  95 percent upper bound below zero. A failure means 56 us of added idle costs no contrast, which contradicts the
  mechanism outright.
- **D2, the incoherent model accounts for the plain arms.** Each plain arm's z = (measured - model) / sigma lies
  within the Bonferroni two-sided 95 percent bound over the four doses, |z| <= 2.498.
  - A pass says the Target's T1/T2, charged on both the doses and the scheduled idle, account for the contrast's
    dependence on idle on these qubits.
  - A failure with the measurement above the model at long dose says the model overstates idle damage here, and the
    encoded null then needs part of its explanation elsewhere.
  - A failure below the model says idle costs more than T1/T2 state.
- **D3, coherent detuning.** The excess echo gain, measured gain minus model gain at 14,000 dt, is tested
  one-sided at 95 percent.
  - A lower bound above zero reads as coherent detuning refocused beyond the model only if D2 holds at 14,000 dt.
    Otherwise it is inconclusive, because an effective T1 that departs from the Target's also changes the echo gain
    the model expects.
  - An upper bound below zero says the echo's X pulses cost more than they refocus.
  - Otherwise D3 is unresolved, and the idle loss is consistent with the incoherent model at this precision.
- **D4, the encoded null amplitude.** Reported, not decided: the plain contrast at 14,000 dt against the encoded
  Kingston run's measured +0.0027 and this run's dose-0 contrast. It places the encoded null's idle length on a
  measured dose-response curve, on other qubits and another backend.

## Expected precision

At 16,384 shots per arm, sigma_c is about 0.008 and sigma_g about 0.011.
- **D1.** The model's dose-0 to 14,000 dt drop is 0.236, about 20 sigma.
- **D3.** An excess echo gain of 0.03 would be resolved at about 2.7 sigma.

## Cost and account

The planner estimates 25.0 s under a 30 s ceiling on `backup-ibm-quantum-platform`, which reported 412 s remaining
at the dry run. The record's approval is consumed once; a changed calibration or layout at submission stops the run
for re-approval.

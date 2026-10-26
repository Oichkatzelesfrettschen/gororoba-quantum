# N=21 orbit window-dose sweep on ibm_kingston: the mechanism case

[UNAPPROVED_CASE.md](UNAPPROVED_CASE.md) is the planner's binding:
- record.json SHA-256 `a0138b9433e407c1e3ff2470561b9d1437d69e5fb8a161b1c80019f632d83876`;
- one dynamic job of 14 PUBs x 16,384 shots;
- an estimated 25.6 s against a 30 s ceiling, on the backup instance with 435 s remaining.

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
echo that refocuses static detuning. The executed replica sits on Kingston qubits 104, 105, 106 and 117 (control
117), qubits the encoded null also ran on. A simulation cannot answer the question: the question is whether the
hardware's idle loss follows the Target's T1/T2, and the simulation assumes that it does.

## Arms

The arms are pairs of feed-forward and omitted-correction members of the bracketed orbit circuit, each scored by
its contrast difference.

| Dose (dt) | Dose (us) | Plain arm, model | Echo arm, model | Model echo gain |
|---|---|---|---|---|
| 0 | 0 | +0.217 | n/a | n/a |
| 3,500 | 14 | +0.151 | +0.169 | +0.018 |
| 7,000 | 28 | +0.087 | +0.129 | +0.042 |
| 14,000 | 56 | -0.017 | +0.064 | +0.081 |

- **Model.** The values are the dry run's sampled noise model (131,072 shots, simulation allowance +-0.023).
- **Echo gain under the incoherent model.** The model's echo gain is not zero. The two X pulses on the work bits
  reverse T1's population drift halfway, so amplitude damping biases the echo arm less. A coherent effect therefore
  shows up as echo gain beyond the model's gain, not as gain above zero.
- **Doses.** The 14,000 dt dose matches the encoded circuit's leaf idle.

## Preregistered decisions

`live_run.py --collect` writes the measured summary (`window_dose_*_contrast_difference`, `window_dose_echo_gain_*`)
and the model replay under the calibration in force at execution (`replayed_statistics`). Every decision below
compares the measured value with that execution-calibration replay. The shot-noise standard error of a measured
contrast difference, sigma_c, comes from the collected per-member shot variances; that of an echo gain is
sigma_g = sqrt(sigma_c(plain)^2 + sigma_c(echo)^2). Each decision is its own two-sided or one-sided 95 percent
test, as stated; no family correction is applied.

- **D1, idle response exists.** The plain contrast at 14,000 dt lies below the plain contrast at dose 0, with the
  one-sided 95 percent upper bound of the difference below zero. A failure means added idle of 56 us does not cost
  contrast, which contradicts the mechanism outright.
- **D2, incoherent model accounts for the plain arms.** At every dose, |measured - replayed| <= 1.96 sigma_c +
  0.023 (the simulation allowance).
  - A pass at all four doses says the Target's T1/T2 account for the contrast's dependence on idle on these
    qubits.
  - A failure in which measured contrast stays above the model at long dose says the model overstates idle damage
    here. The encoded null would then need part of its explanation elsewhere.
  - A failure below the model says idle costs more than T1/T2 state.
- **D3, coherent detuning.** The excess echo gain, measured gain minus replayed gain at 14,000 dt, is tested
  one-sided.
  - A lower bound above zero says the echo refocuses a coherent idle error the model lacks, of the kind the QET
    window phase and Fez's two-line beat show.
  - An upper bound below zero says the echo's X pulses cost more than they refocus.
  - Otherwise D3 is unresolved, and the idle loss is consistent with the incoherent model at this precision.
- **D4, the Kingston null amplitude.** Reported, not decided: the plain contrast at 14,000 dt against the encoded
  run's measured +0.0027 and the orbit dose-0 contrast. It places the encoded null on the measured dose-response
  curve of the same qubits.

## Expected precision

At 16,384 shots per arm, sigma_c is about 0.008 and sigma_g about 0.011.
- **D1.** The model's dose-0 to 14,000 dt drop is 0.234, about 20 sigma.
- **D3.** An excess echo gain of 0.03 would be resolved at about 2.7 sigma.

## Cost and account

The planner estimates 25.6 s under a 30 s ceiling on `backup-ibm-quantum-platform`, which reported 435 s remaining
at the dry run. The record's approval is consumed once; a changed calibration or layout at submission stops the run
for re-approval. The record carries the planner's default seeds and draws no new one. Its reproduction seeds are
`seed_transpiler` 20261012 and `seed_simulator` 20261011, as the retained orbit-rca runs use.

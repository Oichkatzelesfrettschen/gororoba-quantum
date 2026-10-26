# N=21 orbit window-dose sweep: the calibration-adaptive approval envelope

This case asks approval for a rule and its bounds, not for one calibration's values. A plan made at one
calibration lapses within the 30-40 minute calibration cycle of IBM Heron r2 backends
([calibration-jobs.md](../notes/ibm_quantum/calibration-jobs.md)), so `scripts/n21_dose_run.sh --submit` plans on
the calibration in force, checks the plan against this envelope with `scripts/n21_dose_decisions.py --preflight`,
and submits that plan within the same minute. The layout, the replica sets and the model values are the fresh
plan's own. Every bound below is enforced by the preflight or by live_run.py, and a plan outside any of them sends
nothing.

## Question

Two retained N=21 runs bound the feedback-contrast loss from either side: the encoded circuit on ibm_kingston (336
CZ, about 15,000 dt of scheduled leaf idle) measured +0.0027 against a predicted +0.031, and the orbit circuit on
ibm_fez (28 CZ, about 2,000 dt) kept +0.197 against the idle-padded model's +0.179. One parameter-free incoherent
idle model fits both (claims `hw-n21-feedback-null-scheduled-idle` and `hw-n21-orbit-scheduled-idle-control`),
retrospectively and across circuits and backends. This run adds idle to the orbit circuit in controlled doses, in
one job on one calibration, with and without an echo that refocuses static detuning. It answers two questions:
- does the contrast fall with added idle as the Target's T1 and T2 predict (D1, D2);
- does the echo recover more than the model's own echo gain, which comes from the T1 asymmetry of the echo's X
  pulses, as a static detuning would make it (D3)?

A noise simulation cannot answer either: it assumes the Target's T1/T2 description that the run tests, and Fez
qubit 143's two-line beat (claim `hw-n21-q143-segmented-lines`) shows idle error that such a description cannot
express.

## Circuit

The `n21-orbit-rca` family with `--window-doses-dt 0,1752,3500,5252,7000,10500,14000`, built by
`qpe_diagnostics` (`window_dose` and `window_dose_echo` variants). After the control's mid-circuit measurement and
reset, a barrier across the replica's four wires precedes the dose, so every dose delay starts after that
replica's reset. The plain arm
holds `delay(D)` on all four wires; the echo arm holds `delay(D/4) X delay(D/2) X delay(D/4)` on work bits 1 and
16 and `delay(D)` on the control and the bit for 4. Each dose is a pair of feed-forward and omitted-correction
members scored by their contrast difference; dose 0 has no echo arm. That gives 13 contracts and 26 members, one
PUB per member, each PUB packing every admitted disjoint replica of the four-qubit circuit with its own barriers.
The initialization herald (`--init-herald`) measures every qubit into its own register before the circuit, so
the preparation error at the chosen delay is recorded beside each contrast.

## Bounds

| Bound | Value | Enforced by |
|---|---|---|
| Account | backup instance, `GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform` | runner |
| Backends | ibm_fez, ibm_kingston, ibm_marrakesh (Heron r2), the planner's choice among those operational | preflight |
| Shots | 8,192 per PUB | preflight |
| Repetition delay | 20 us; 50 us when no plan is admitted at 20 us, or as the single retry below | preflight, runner |
| Replicas | replica tier 24, replica floor 0.45, at least 4 placed | preflight |
| Ceiling | 30 s estimated charge and 30 s `max_execution_time` for the one job | preflight, live_run.py |
| Execution | twirling and dynamical decoupling off, cross-group buffer on, one dynamic job | preflight, live_run.py |
| Seeds | `--seed-transpiler` `qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#0`, `--seed-simulator` index 1 | preflight |
| Code | the plan is made from a clean tree at the checked-out commit | preflight |

**Retry.** The 20 us delay lies at the floor IBM's changelog sets for Heron. Two 0 us jobs and the 20 us jobs of a
100,000-shot design under a 6 s ceiling all ended in error 1305, and none of the 20 us jobs separated a stalled
shot loop from an overrun ceiling
([REP_DELAY_ZERO_CONTROL_FINDINGS.md](../../results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md)). This plan's
estimated charge sits far below its 30 s ceiling, so a 1305 here with zero circuit execution time reads as a
stalled loop. That outcome admits one retry, `sh scripts/n21_dose_run.sh --delay 5e-05 --submit`, under this
envelope; any other failure ends the case.

## Decisions

`scripts/n21_dose_decisions.py RUN --out RUN/dose-decisions.json` reads the collected run against
`scripts/scheduled_idle_replay.py RUN --out RUN/idle-replay.json`, the exact branch-resolved law of every replica
with the explicit doses and the service-scheduled idle charged under the execution Target. A collection whose
comparisons the collector withheld (its PUBs did not run under one calibration) is refused.

- **D1, idle response.** The pooled plain contrast at 14,000 dt lies below the dose-0 contrast at one-sided 95
  percent. Its failure falsifies the claim that idle on these wires costs feedback contrast.
- **D2, incoherent model.** At each nonzero dose, the pooled plain dose response, measured(d) - measured(0),
  agrees with the model's within the Bonferroni two-sided 95 percent bound over the six nonzero doses (|z| at most
  2.638). A dose-independent offset (readout, initialization at a 20 us delay, the orbit run's 0.018 residual, the
  baseline idle of packed replicas) cancels in the response. A failure falsifies the Target's T1/T2 as the
  description of added idle on this circuit.
- **D3, coherent detuning.** At 14,000 dt, each replica's excess echo gain, (echo - plain) measured minus the same
  in the model, enters a chi-square across replicas at 5 percent. A static detuning shifts each replica's plain arm
  by a first-order term with the sign of that replica's detuning, which a replica mean cancels; the per-replica
  test keeps it. A rejection reads as coherent detuning refocused by the echo only when the echo arm's own dose
  response agrees with the model across replicas (chi-square at 5 percent) and D2 holds at 14,000 dt; otherwise it
  is inconclusive, because an effective T1 off the Target's moves the echo arm as well.

## Plan at the dry run

The values below come from the dry run named here and illustrate the envelope; the submitted plan replaces them
with its own calibration's.

Dry run `results/live/2026-10-26T221115.366606Z` (record.json SHA-256
`9c190f9f4e31efd2398d45caabe9ac9115abc4faf9fa0ad5df4e422fc273eac7`, commit `2677994`): ibm_kingston, calibration
2026-10-26T14:25:32-07:00, 19 replicas, 26 PUBs x 8,192 shots at a 20 us repetition delay, an estimated 17.1 s
against the 30 s ceiling on the backup instance, whose rolling window held 390 s at the time of writing. The
plan took 18 min 46 s of wall time at nice 19 with a 1.3 GiB peak; Kingston's calibration had moved to
15:18:32-07:00 by the time it was read again, so a plan of this duration lapses before its submission re-plans.

| Dose (dt) | Plain arm, model | Echo arm, model | Model echo gain |
|---|---|---|---|
| 0 | +0.198 | n/a | n/a |
| 1,752 | +0.172 | +0.169 | -0.002 |
| 3,500 | +0.140 | +0.160 | +0.019 |
| 5,252 | +0.118 | +0.141 | +0.023 |
| 7,000 | +0.088 | +0.117 | +0.029 |
| 10,500 | +0.050 | +0.085 | +0.035 |
| 14,000 | +0.013 | +0.050 | +0.037 |

The planner's model values come from 32,768 sampled shots per member (a simulation radius of about 0.055 per
contrast); the decisions read the idle replay's exact per-replica laws instead.

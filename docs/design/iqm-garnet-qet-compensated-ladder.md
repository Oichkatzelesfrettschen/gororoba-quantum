# Phase-compensated QET ladder on IQM Garnet

The two-qubit quantum energy teleportation (QET) ladder of
[gororoba_quantum/qet_ladder.py](../../gororoba_quantum/qet_ladder.py) asks whether a measured record lowers Bob's
local energy below every record-independent operation. On ibm_kingston the compensated ladder
([findings](../../results/live/2026-10-25T233207.284563Z/FINDINGS.md)) gave:
- an information excess of +0.107 +- 0.006 over 14 pairs, the record-steered drop below the best record-independent
  unitary, about 93 percent of the ideal 0.115;
- a channel floor margin of -0.073 +- 0.015. That is the energy-below-vacuum test, and it fails because the
  reference state starts 0.18 above the vacuum value.

This case replicates both endpoints on a second platform with a different feed-forward mechanism. Garnet's `cc_prx`
is a PRX conditioned on a fast-feedback readout bit, where Heron r2 uses an `if_else` broadcast. It also qualifies a
non-pi conditional angle on Garnet hardware, which published `cc_prx` examples do not use.

## Circuits

`scripts/iqm_qet_ladder.py build results/iqm/cases/qet-compensated-ladder --calibration-dir DIR` lowers each of the
18 `qet_ladder.compensated_arms` into Garnet native operations with virtual-Z frame tracking:
- **Feedback rule.** Bob's record-steered RY(-mu phi*), mu = 1 - 2r, becomes an unconditional prx(-phi*) followed by
  `cc_prx`(2 phi*) on Alice's bit.
- **Idle-rule arms.** They carry `cc_prx` at angle 0, so every arm has the same measure-to-pulse wait.
- **Alice's measures.** Her mid-circuit measure carries `key` and `feedback_key`; she is read again in the same
  frame.
- **Exactness.** `--self-test` checks the lowering against `qet_ladder.compensated_ideal` to 3.4e-15 at three
  injected window phases. Flipping the frame sign fails it by 0.20.

Four angle-qualification circuits read a target qubit after `cc_prx` from a source in |1> or |0>, at angle 2 phi*
(ideal P(1) = sin^2 phi* = 0.100 or 0) and at angle pi (1 or 0).

The circuits pack five pairs, Alice first: QB4-QB1, QB7-QB6, QB8-QB13, QB16-QB17 and QB18-QB19. They form an
induced matching of Garnet's couplers, chosen by predicted margin under the calibration set `be070414` read
2026-10-25 (copied into the case's `calibration/`). Every circuit runs one active-reset cycle and all-zeros
heralding, which keeps a predicted 48 percent of shots.

## Jobs

| Job | QC | Circuits x shots | Expected execution | Expected credits | max_credits |
|---|---|---|---|---|---|
| `accept` | `garnet:mock` | 22 x 200 | 0.08 s | 0.00 | 0.0 |
| `ladder` | `garnet` | 22 x 10900 | 4.39 s + 1.6 s fixed, billed 6 s | 3.0 at 0.50/s | 4.0 |

- **The mock job comes first and costs nothing.** It confirms the server accepts the operation set that no earlier
  case used: `barrier`, a `feedback_key` distinct from `key`, `cc_prx` at angle 0, at a negative-phase frame and
  at a non-pi angle, and the CZ loci in calibration order. Its bits are random, so it decides acceptance and the
  compiled runtime estimate only.
- **The QPU job pins `be070414`.** A refusal of a retired set creates no job, and the case is then rebuilt and
  re-approved. `iqm_jobs.py collect` cancels the job once its runtime nears the ceiling.
- **Budget.** The account holds 9.00 credits, expiring 2026-11-01.
- **Shot time.** The modeled shot is 18.3 us. If the mock's estimate exceeds 21 us per shot, the case is rebuilt
  with fewer shots before the QPU job.

## Why a simulation cannot answer it

The prediction (`prediction.json`, an exact density-matrix law with no sampling) models:
- depolarizing gate error from RB and IRB;
- per-qubit readout and herald-conditioned initialization;
- T1/T2 relaxation over the ASAP schedule;
- the 290 ns `cc_prx` control delay.

It omits the effects that decided the Kingston margin:
- the coherent window phase Kingston measured at -1.06 to +0.21 rad;
- crosstalk between packed pairs;
- measurement-induced dephasing and readout non-QNDness.

Whether Garnet realizes a non-pi `cc_prx` angle is a device property. Prediction under `be070414`, pooled over the
five pairs with shot-noise standard errors at 5275 kept shots per circuit:

| Endpoint | Predicted | Kingston measured |
|---|---|---|
| information excess at the selected alpha | +0.121 +- 0.015 | +0.107 +- 0.006 |
| channel floor margin at the selected alpha | -0.160 +- 0.011 | -0.073 +- 0.015 |
| reference unitary floor | 0.271 +- 0.011 | 0.177 +- 0.013 |
| qualification P(1), source 1, angle 2 phi* | 0.10 to 0.11 | not measured |

The retained idle-schedule case measured an apparent T1 at 0.53 of calibrated. Under that, the predicted margin
falls to about -0.24 and the excess rises to +0.15.

## Preregistered decisions

`iqm_qet_ladder.py analyze RUN_DIR` computes every endpoint per pair with `qet_ladder.summarize_compensated` and
pools it with a t-interval over the five pairs (4 degrees of freedom).

- **H1, QET information signature.** It is reproduced on Garnet when the pooled information excess has a one-sided
  95 percent lower bound above 0, and refuted when its upper bound is below 0.
- **H2, energy below the vacuum value.** It passes when the pooled channel floor margin has a one-sided 95 percent
  lower bound above 0. The model predicts a failure. A pass would place Kingston's failure in Heron-specific
  preparation or window error rather than in the protocol.
- **H3, non-pi conditional angle.** Garnet realizes `cc_prx`(2 phi*) when, on every target, P(1) after a |1> source
  lies within 0.05 to 0.15 and after a |0> source below 0.03, with Wilson 99 percent intervals inside those bands. A
  target outside them marks that pair's feedback arms as unscored.
- **H4, window phase.** Each pair's reference phase atan2(-<X_A Y_B>, -<X_A X_B>) is reported against Kingston's.
  A pooled magnitude above 0.2 rad means `cc_prx` feedback carries a coherent window phase of Kingston's order.

The hypotheses are falsified by the endpoints themselves; no model value enters a decision.

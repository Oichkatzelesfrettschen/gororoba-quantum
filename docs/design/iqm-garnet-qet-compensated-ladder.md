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

`scripts/iqm_qet_ladder.py build results/iqm/cases/qet-compensated-ladder --calibration-dir DIR --reset passive
--herald none --max-credits 8.0` lowers the compensated arms into Garnet native operations with virtual-Z frame
tracking.

- **Arms.** The four reference arms and two calibrations are those of `qet_ladder.compensated_arms`. The feedback
  arms run over a Garnet grid `GARNET_ALPHAS` = -0.9 to +0.9 in steps of 0.3, symmetric because Garnet's window phase
  is unmeasured. Every phase within 1.05 rad of zero lies within 0.15 rad of a grid point. Kingston's grid (-0.3 to
  1.2) would clip a positive phase above 0.45 rad.
- **Feedback rule.** Bob's record-steered RY(-mu phi*), mu = 1 - 2r, is `cc_prx`(2 phi*) on Alice's bit followed by
  an unconditional prx(-phi*).
  - The conditional half comes first. Under ASAP scheduling an unconditional prx listed first plays before Alice's
    readout, which would split Bob's rotation around the window phase that rz(alpha) undoes.
  - At -1.06 rad the split lowers the selected excess from 0.104 to 0.021.
  - Both halves rotate about one axis in one frame, so they commute.
- **Idle-rule arms.** They carry `cc_prx` at angle 0, so every arm has the same measure-to-pulse wait.
- **Alice's measures.** Her mid-circuit measure carries `key` and `feedback_key`; she is read again in the same
  frame.
- **Exactness.** `--self-test` and the tests check the lowering against `qet_ladder.compensated_ideal` to 3.5e-15.
  The window phase is injected at the barrier and after the readout window. Two mutations fail the check: a flipped
  frame sign, and the unconditional half moved ahead of `cc_prx`.

Four angle-qualification circuits read Bob after `cc_prx` from an Alice source in |1> or |0>, at angle 2 phi*
(ideal P(1) = sin^2 phi* = 0.100 or 0) and at angle pi (1 or 0).

The 24 circuits pack five pairs, Alice first: QB4-QB1, QB7-QB6, QB8-QB13, QB16-QB17 and QB19-QB18. They form an
induced matching of Garnet's couplers, chosen by predicted margin under the calibration set `7b30f37a`, read
2026-10-26 02:40Z and copied into the case's `calibration/`.

Every pair also respects the fast-feedback wiring. Bob's drive must accept fast feedback from Alice's readout
probe line: QB8, QB13, QB14, QB15, QB18 and QB19 take only PL-3 sources, and the rest take PL-1 and PL-2 (the
snapshot's `chip-design-records.json` and `channel-properties.json`, copied as `calibration/feedback.json`). The
second `garnet:mock` acceptance job (`01a17675-111d-731e-9c6f-2132756f1686`) refused the previous pair QB3-QB8 at
circuit resolution: "QB8 does not support fast feedback from QB3 (probe line: PL-2)". The planner now admits only
compatible orientations, and `validate_circuit` refuses a crossing pair.

Every circuit runs passive reset with no heralding.
- **Why passive.** The station control admits one feedback signal label per drive AWG in a playlist segment, and
  active reset conditions every qubit's drive on its own readout.
- **Evidence.** The first `garnet:mock` acceptance job (`01a17621-1452-701f-8874-ba08a138aec4`, active reset with
  heralding) reached the end of compilation and was then refused with "unique feedback signal labels: 2/1" on
  exactly the five Bob drives (claim `iqm-garnet-cc-prx-feedback-label-limit`).
- **Cost of the fix.** A passive-reset shot ran 316.2 us on the reset and billing pilot. An active-reset shot ran
  16 to 37.5 us on the retained Garnet jobs.
- **Initial state.** The base model is a folded terminal-error approximation. It starts each qubit in the ground
  state and lets the unheralded readout errors carry the passive initialization error, so an excited input's
  propagation through the gates is not modeled. QB1 read 0.0065 against 0.0046 predicted; no other qubit was measured. A
  sensitivity row starts every qubit at its calibrated `init_error` instead. That row can double-count the population
  the assignment errors already carry, so it bounds the effect rather than offering a second prediction.

## Jobs

| Job | QC | Circuits x shots | Expected execution | Expected credits | max_credits |
|---|---|---|---|---|---|
| `accept` | `garnet:mock` | 24 x 200 | 1.52 s | 0.00 | 0.0 |
| `ladder` | `garnet` | 24 x 1600 | 12.20 s + 1.6 s fixed, billed 14 s at most | 7.0 at 0.50/s | 8.0 |

- **The mock job comes first and costs nothing.** The refused mock already compiled the operation set: `barrier`,
  a `feedback_key` distinct from `key`, `cc_prx` at angle 0 and at a non-pi angle, and negative prx angles. This
  run confirms the passive-reset playlist passes the station's instrument checks. Its bits are random. The
  garnet:mock passive estimate ran about 0.41 ms per shot on the pilot, against 0.316 ms on the QPU, so its
  estimate gates nothing.
- **The QPU job pins `7b30f37a`.** A refusal of a retired set has been observed only on the mock, where it charged
  nothing. If the set retires, the case is rebuilt from a fresh read, and the owner re-approves it before the QPU job.
- **Cost limits.** `iqm_jobs.py collect` holds the 8.0-credit ceiling. It cancels the job when the QPU's compiled
  estimate cannot finish within it, or once the runtime comes within 1.0 s of the 16 s the ceiling buys.
- **Budget.** The account holds 9.00 credits, expiring 2026-11-01. The pilot billed ceil(runtime), so 12 to 14 s,
  6.0 to 7.0 credits, is expected.

## Why a simulation cannot answer it

The prediction (`prediction.json`, an exact density-matrix law with no sampling) models:
- depolarizing gate error from RB and IRB;
- per-qubit unheralded readout;
- T1/T2 relaxation over the ASAP schedule;
- the 290 ns `cc_prx` control delay.

It omits the effects that decided the Kingston margin:
- the coherent window phase Kingston measured at -1.06 to +0.21 rad;
- crosstalk between packed pairs;
- measurement-induced dephasing and readout non-QNDness.

Whether Garnet realizes a non-pi `cc_prx` angle is a device property. Prediction under `7b30f37a`, pooled over the
five pairs with shot-noise standard errors at 1600 shots per circuit:

| Endpoint | Predicted | Relaxation x 0.53 | Calibrated init_error | Kingston measured |
|---|---|---|---|---|
| information excess at the selected alpha | +0.119 +- 0.027 | +0.150 | +0.114 | +0.107 +- 0.006 |
| channel floor margin at the selected alpha | -0.190 +- 0.020 | -0.261 | -0.241 | -0.073 +- 0.015 |
| reference unitary floor | 0.285 +- 0.020 | 0.387 | 0.320 | 0.177 +- 0.013 |
| qualification P(1), source 1, angle 2 phi* | 0.10 to 0.12 | | | not measured |

Per pair, the shot-noise standard error is about 0.06 on the excess and 0.04 on the margin. These delta-method
errors hold the selected alpha fixed. The predicted phases sit 3.3 to 3.65 phase standard errors from the nearest
grid midpoint, where a selection switch would add variance the formula does not carry. The relaxation column
uses the apparent T1 the retained idle-schedule case measured, a median 0.53 of calibrated.

## Preregistered decisions

`iqm_qet_ladder.py analyze RUN_DIR` computes the decisions (`decisions` and `angle_qualification` in the script);
no model value enters them.
- **Per-pair endpoints.** Each pair's endpoints come from the Garnet summary, `qet_ladder.summarize_compensated`
  over `GARNET_ALPHAS`.
- **Selected alpha.** The alpha nearest minus the pair's own reference phase. The reference arms are independent of
  the feedback arms they select, so selection adds no bias to the scored endpoint.
- **Pooling.** Each hypothesis is its own one-sided t test at 95 percent across pairs: t(0.95, n - 1), 2.132 at five
  pairs. A verdict needs two pairs.
- **All pairs are primary.** H1, H2 and H4 pool every pair; the same tests over the pairs H3 scores are reported as
  secondary. Excluding H3 failures would bias H1 upward: a `cc_prx` that never fires runs the fixed -phi* rotation,
  a record-independent unitary, so its excess falls to zero or below. One that fires on the wrong bit runs the
  reversed rule, and one that under-rotates gives less. A test checks that one never-firing pair lowers the
  all-pairs excess.
- **No family correction.** H1 is the primary test. H2 to H4 answer separate questions and are reported at their
  own level.

The hypotheses:
- **H3, non-pi conditional angle.** Only the shots whose recorded Alice bit matches the prepared source enter, since
  `cc_prx` reads that bit. Bob's assignment errors come from the pair's own `cal_00` and `cal_11` arms in the same
  job.
  - The corrected interval maps the target's Wilson 99 percent interval through those errors.
  - Each side is widened in quadrature by the delta-method uncertainty of the two assignment errors (z = 2.576),
    so the calibration arms' binomial noise enters the interval.
  - A test checks that a `cc_prx` firing on bit 0 unscores its pair.
  - Through them, the readout-corrected conditional angle 2 asin(sqrt p) from the |1> source must lie within
    2 phi* +- 0.15 rad (0.494 to 0.794 rad) across its Wilson 99 percent interval.
  - The readout-corrected P(1) from the |0> source must stay below 0.03 at its Wilson 99 percent upper bound.
  - A pair that fails is excluded from the secondary tests only. The fitted angle and the pi-arm angle are reported
    for every pair.
  - The angle interval at 1600 shots is about +- 0.06 rad, so the band admits a calibration error of about 30
    percent of 2 phi* and no larger.
- **H1, QET information signature.** It is reproduced on Garnet when the information excess has a lower bound above
  0, and refuted when its upper bound is below 0. Its power at the predicted +0.119 with a per-pair standard error of
  0.06 is 0.97 at five pairs and 0.90 at four, with no between-pair spread beyond shot noise. An extra
  between-pair spread of 0.04, 0.06, 0.09 or 0.12 lowers the five-pair power to 0.91, 0.82, 0.65 or 0.50.
  - The model predicts a spread of 0.018; Kingston's pairs scattered more than its model did.
  - A refuting verdict with a pair whose reference phase lies beyond the 1.05 rad reach reads "inconclusive". Such
    a pair's selected alpha sits at the grid edge, and its low excess measures the finite grid rather than
    feed-forward. A failing H2 verdict is treated the same way.
- **H2, energy below the vacuum value.** It passes when the channel floor margin's lower bound is above 0, and fails
  when its upper bound is below 0. The model predicts a failure. A pass would place Kingston's failure in
  Heron-specific preparation or window error rather than in the protocol.
- **H4, window phase.** The mean per-pair magnitude of the reference phase atan2(-<X_A Y_B>, -<X_A X_B>) is compared
  with 0.2 rad. A lower bound above 0.2 means `cc_prx` feedback carries a coherent window phase of Kingston's order;
  an upper bound below it means it does not. A phase beyond 1.05 rad lies outside the grid's correction, and the
  pair's selected alpha then reads the grid edge.

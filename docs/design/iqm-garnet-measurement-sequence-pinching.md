# IQM Garnet measurement-sequence pinching

This case tests whether a Garnet mid-circuit measurement acts as ideal pinching, the nonselective projective
measurement in Z, on QB1, QB3, QB7 and QB14. The case directory is
[results/iqm/cases/measurement-sequence-pinching](../../results/iqm/cases/measurement-sequence-pinching/cases.json),
built by `scripts/iqm_measurement_sequence.py build DIR [--calibration-dir DIR]`. The script's docstring states the
preregistered decisions, and `prediction.json`, bound by digest into `cases.json`, holds the model the margins below
come from.

calibration set: `be070414-7624-4943-ac7e-1e2678f05684` (created 2026-10-25T16:45:12Z, read 2026-10-25); QB3 reads e01 0.124 and e10 0.254 under it, so its readout-corrected endpoints carry about twice the standard error of the other three qubits

The built case pins the set in `calibration/excerpt.json`; that excerpt is built from the retained set
`9069c4ef-7ab6-4e50-be4f-c91d71c3a06d`. Garnet refuses a job pinned to a retired set, so the orchestrator rebuilds
the case with `--calibration-dir` pointing at a directory holding the live `set.json`, `metrics.json` and
`dynamic-quantum-architecture.json` before approval.

## What it measures

A pinched qubit keeps the Z populations and loses the coherences, so its Bloch z multiplies by cos(THETA/N) after
each rotation of THETA/N about X. With THETA = 8 pi/9 the chain of N rotations, each followed by a recorded
measurement (the measure arm), ends at P0 = (1 + cos(THETA/N)^N)/2: 0.0302, 0.5151, 0.6722, 0.8040 and 0.8914 for
N = 1, 2, 4, 8 and 16. Three arms run:

| arm | N | mid-circuit operation | ideal P0 | role |
|---|---|---|---|---|
| measure | 1, 2, 4, 8, 16 | `measure`, own key per step | 0.0302, 0.5151, 0.6722, 0.8040, 0.8914 | the object under test |
| unitary | 16 | none; N rotations back to back | 0.0302 | mutation null: the measurements removed |
| delay | 1, 2, 4, 8, 16 | `delay` of the measure duration | 0.0302 | elapsed-time control, descriptive |

The unitary rotations compose to one rotation of THETA, so the N = 16 contrast measure minus unitary is the
measurement's own action, ideally 0.8612. The delay arm holds the elapsed time of the measure arm but dephases: idle
time acts as a partial Z measurement, so its P0 rises with N without any measurement. It therefore cannot serve as the
null, and it quantifies how much of the measure arm's Zeno effect idle dephasing alone produces. Measurement-induced
transitions and leakage lower the measure arm below its ideal-projective prediction; the three-state readout reports
P(2) directly.

## Why a noise simulation cannot answer it

The calibration noise model of `scripts/iqm_sim.py` treats a measurement as an ideal projective readout with
assignment errors, so measurement-induced transitions and leakage are absent from every model it builds, and the
mock twin returns random bits. The question concerns the device's readout, so only Garnet answers it.

## Qubits

QB1, QB3, QB7 and QB14 run the same arm in parallel in every circuit. The retained architecture lists no CZ locus
among them (QB1: QB2, QB4; QB3: QB4, QB8; QB7: QB6, QB12; QB14: QB13, QB15, QB18, QB9), and the build refuses a
calibration that lists one. `measure_012` is calibrated on all four (and on QB9, unused here).

## Circuits

The job holds 54 circuits.

- **Zeno chains, 44.** For each N in (1, 2, 4, 8, 16) the measure group beside the delay group, and at N = 16 the
  unitary group; each group is four signed circuits in the order +, -, -, +. Each step is `prx(sign*THETA/N, 0)` on
  every qubit, then one joint `measure` with its own key (`m0`, `m1`, ...) in the measure arm, one joint `delay` in
  the delay arm, or nothing in the unitary arm, and a final `measure` with key `f`. Outcomes are recorded and never
  condition a gate.
- **Leakage, 6.** N = 16 in all three arms, + and - once each, ordered measure +, delay +, unitary +, unitary -,
  delay -, measure -, with a `measure_012` final readout.
- **Readout calibration, 4.** `ro0` and `ro1` (a pi pulse) with `measure`, and the same pair with `measure_012`, on
  all four qubits. The pi pulse of `ro1` carries its own over-rotation, which the correction absorbs into the readout
  scale.

**Idle operation.** The circuit-job body takes a native `delay` operation whose `duration` is in seconds, at least
that long and rounded up to hardware granularity
([operations table and Delay](../notes/iqm/docs/iqm-client/api/iqm.iqm_client.models.md); every Target lists `delay`,
[os-4.7.md](../notes/iqm/os-4.7.md)). Garnet's dynamic quantum architecture lists no `delay` gate and the OpenAPI
operation name is a free string, so acceptance on the QPU is unverified; the garnet:mock run settles it, and a
rejection removes the delay arm and leaves the unitary null and the departure test unchanged.

**Measure duration.** The calibration's probe pulse lasts 364, 444, 556 and 420 ns on QB1, QB3, QB7 and QB14
(`gates.measure.constant.QBn.duration`, set `9069c4ef`). A measure runs as a ReadoutTrigger whose duration follows
the acquisition rather than the probe pulse
([Measure_CustomWaveforms](../notes/iqm/docs/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.md)), so
the delay is the longest `acquisition_delay + integration_length` over the four qubits (465.5 ns + 556 ns on QB7)
rounded up to the 4 ns granularity: 1.024 us. That figure is an inference from the gate parameters; no retained
record carries a compiled measure duration. The two free mock jobs below check it.

**Elapsed time.** The delay arm matches the measure arm's elapsed time to the extent of that inference.

## Initialization

The job runs one active-reset cycle without heralding. All-zeros heralding over four qubits discards about a
quarter of the shots, and passive reset takes 316 us per shot against 37.5 us ([timing pilot](iqm-garnet-timing-pilot.md)).
Rotations and pinching act linearly on the Bloch z, so an initialization excitation p scales the final z by
(1 - 2p), the factor `ro0` and `ro1` measure; the readout correction removes it exactly. T1 relaxation toward |0> is
the non-unital residue and enters at second order.

## Shots, billing and max_credits

- **Shots:** 2700 per circuit, one job.
- **Per-shot schedule assumed:** 2.3510 ms summed over the 54 circuits. Each circuit costs the 37.5 us of an
  unheralded active-reset shot, measured on QB1 by the reset and billing pilot ([timing pilot](iqm-garnet-timing-pilot.md)),
  plus 16 ns per rotation layer and 1.024 us per mid-circuit measure or delay.
- **Expected execution:** 6.348 s of shots plus the fixed 1.6 s per job gives 7.948 s, billed as 8 s, or 4.00
  credits at 0.50 credits/s.
- **max_credits:** 5.00 on `garnet` (10 billed seconds) and 0.00 on `garnet:mock`. The build refuses a plan that
  leaves less than 2 s below the ceiling, because `collect` cancels a run within 1.0 s of it and runtimes ran up to
  1.39 s above their estimates ([README, Cost](../notes/iqm/README.md#what-the-garnet-runs-measured)).

## Decision rule

Per qubit, from the readout-corrected P0 pooled over the four signed circuits, with binomial standard errors
propagated through the correction by the delta method:

- the mutation test passes when the N = 16 contrast (measure minus unitary) exceeds 0.5 by at least 3 standard
  errors;
- the device departs from ideal pinching when the measured N = 16 measure-arm P0 lies below the prediction of an ideal
  projective measurement by at least 3 standard errors. The prediction (`prediction.json`) iterates the Bloch vector:
  a rotation, an ideal pinch, then T1 relaxation toward |0> over the rotation and the 1.024 us measure window, and
  readout through the calibrated errors. T2 does not enter it, because the state is diagonal after every measurement.
  Its inputs are each qubit's calibrated T1, the window, the rotation time, e01 and e10, and the assumed 6.8 %
  initialization excitation.

Reported without a decision: the delay arm's measured and modeled (T1 and T2) P0 per N with their difference, and the
measured delay minus unitary difference at N = 16 against the model's; the per-N measure-arm deficit against the
ideal; the fit of P0(N) = (1 + ((1 - 2 eps) cos(THETA/N))^N)/2 for eps per qubit (it ignores relaxation, so it
absorbs T1 into eps); the transition rate between consecutive mid-circuit outcomes against sin(THETA/(2N))^2 (about
0.008 at N = 16, below the 1 to 2 % readout error, so reported raw); and P(2) per qubit in each arm with the
`measure_012` assignment floor from `ro0` and `ro1`.

## Predicted outcome

Model values from set `9069c4ef` (`prediction.json`). Measure-arm P0 at N = 1, 2, 4, 8, 16 is the departure
prediction at N = 16; the delay arm uses T1 and T2; the unitary arm is the N = 16 mutation null.

| qubit | measure P0 (N = 1, 2, 4, 8, 16) | delay P0 (N = 1, 2, 4, 8, 16) | unitary P0 (N = 16) | contrast | departure SE | delay minus unitary |
|---|---|---|---|---|---|---|
| QB1 | 0.0702, 0.5379, 0.7005, 0.8348, 0.9216 | 0.0702, 0.1177, 0.1837, 0.2956, 0.4651 | 0.0398 | 0.8821 | 0.0067 | 0.4253 |
| QB3 | 0.0751, 0.5407, 0.7039, 0.8383, 0.9246 | 0.0751, 0.1207, 0.1868, 0.2994, 0.4705 | 0.0398 | 0.8850 | 0.0070 | 0.4307 |
| QB7 | 0.0504, 0.5267, 0.6868, 0.8203, 0.9081 | 0.0504, 0.1010, 0.1621, 0.2646, 0.4195 | 0.0388 | 0.8696 | 0.0072 | 0.3807 |
| QB14 | 0.0513, 0.5272, 0.6874, 0.8210, 0.9088 | 0.0513, 0.1129, 0.1842, 0.2998, 0.4658 | 0.0405 | 0.8682 | 0.0071 | 0.4253 |

The contrast standard error is 0.009 to 0.010, so the model device passes the mutation test by 36 to 41 standard
errors. Dephasing over 16 steps of 1.04 us against T2 of 7.7 to 11 us lifts the delay arm to 0.42 to 0.47: idle
dephasing alone produces about 0.4 of the 0.86 Zeno rise, which is why the delay arm is a control and the unitary arm
the null. T1 lifts the measure arm 0.017 to 0.033 above its ideal 0.8914, and the departure test compares the run with
that raised prediction, so a real transition rate is not hidden by relaxation.

## Sequence

1. Rebuild the case against the live calibration set and run `check`.
2. Run the job on `garnet:mock` at 0.00 credits: it settles whether the mock accepts `delay` and `measure_012` and
   returns the runtime estimate. Mock outcomes never enter the analysis.
3. Run two free mock jobs, one N = 16 measure circuit and one N = 16 delay circuit at equal shots, and compare their
   runtime estimates to check the 1.024 us delay.
4. Approval of this written case, then `submit` on `garnet` with `--approved-cases-sha256` and `--max-credits 5.0`,
   and `collect` right after.
5. `analyze RUN_DIR --out FILE` writes the decisions.

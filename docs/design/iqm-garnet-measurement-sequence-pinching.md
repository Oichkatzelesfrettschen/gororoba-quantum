# IQM Garnet measurement-sequence pinching

This case tests whether a Garnet mid-circuit measurement acts as ideal pinching, the nonselective projective
measurement in Z, on six pairwise uncoupled qubits. The case directory is
[results/iqm/cases/measurement-sequence-pinching](../../results/iqm/cases/measurement-sequence-pinching/cases.json),
built by `scripts/iqm_measurement_sequence.py build DIR [--calibration-dir DIR]`. The script's docstring states the
preregistered decisions, and `prediction.json`, bound by digest into `cases.json`, holds the planning values and the
standard errors the margins below come from.

calibration set: `be070414-7624-4943-ac7e-1e2678f05684` (created 2026-10-25T16:45:12Z, read 2026-10-25)

The built case pins that set in `calibration/excerpt.json`. Garnet refuses a job pinned to a retired set, so the
orchestrator rebuilds the case with `--calibration-dir` pointing at a directory holding the then live `set.json`,
`metrics.json` and `dynamic-quantum-architecture.json` before submission; the qubit selection reruns on that set.

## What it measures

A pinched qubit keeps the Z populations and loses the coherences, so its Bloch z multiplies by cos(THETA/N) after
each rotation of THETA/N about X. With THETA = 8 pi/9 the chain of N rotations, each followed by a recorded
measurement (the measure arm), ends at P0 = (1 + cos(THETA/N)^N)/2: 0.0302, 0.5151, 0.6722, 0.8040 and 0.8914 for
N = 1, 2, 4, 8 and 16. Four arms run:

| arm | N | mid-circuit operation | ideal P0 | role |
|---|---|---|---|---|
| measure | 1, 2, 4, 8, 16 | `measure`, own key per step | 0.0302, 0.5151, 0.6722, 0.8040, 0.8914 | the object under test |
| unitary | 16 | none; N rotations back to back | 0.0302 | mutation null: the measurements removed |
| delay | 1, 2, 4, 8, 16 | `delay` of 1.096 us | 0.0302 | elapsed-time control, descriptive |
| settle | 16 | `measure`, then `delay` of 2.0 us | 0.8914 | readout-tail control for the departure decision |

The unitary rotations compose to one rotation of THETA, so the N = 16 contrast measure minus unitary is the
measurement's own action, ideally 0.8612. Every step of every arm at every N is built from two prx(pi/2) pulses (see
"Circuits"), the construction the diagnostic's D6 circuit tested at N = 16, so the N scaling compares one construction
and the N = 16 null applies thirty-two pulses. The delay arm holds the elapsed time of the measure arm but dephases: idle
time acts as a partial Z measurement, so its P0 rises with N without any measurement. It therefore cannot serve as the
null; it quantifies how much of the measure arm's Zeno effect idle dephasing alone produces.

## Why a noise simulation cannot answer it

The calibration noise model of `scripts/iqm_sim.py` treats a measurement as an ideal projective readout with
assignment errors, so measurement-induced transitions and leakage are absent from every model it builds, and the
mock twin returns random bits. The question concerns the device's readout, so only Garnet answers it.

## Qubits

The six qubits come from the live calibration set by one rule: the six of smallest e01 + e10 among those whose T1 is at
least the set's median (37.96 us), taken in that order, skipping any that shares a cz coupler with one already taken
and any in `EXCLUDED_QUBITS`; when fewer qualify, the choice extends by the uncoupled remainder in decreasing T1. Only
3 uncoupled qubits clear the median once the exclusions below apply (QB6, QB13 and QB15), so the choice
extends to QB20 (36.3 us), QB9 (34.8 us) and QB18 (33.4 us), which lowers the T1 floor to 33.4 us. No qubit pair of the
choice shares a coupler, and the build refuses a calibration that says otherwise. Each qubit runs the same arm in
parallel in every circuit.

| qubit | T1 (us) | T2 Ramsey (us) | e01 | e10 | e01 + e10 | prx error |
|---|---|---|---|---|---|---|
| QB6 | 39.6 | 8.2 | 0.0152 | 0.0270 | 0.0422 | 0.00134 |
| QB9 | 34.8 | 11.1 | 0.0146 | 0.0366 | 0.0512 | 0.00154 |
| QB13 | 46.5 | 14.1 | 0.0274 | 0.0214 | 0.0488 | 0.00119 |
| QB15 | 40.8 | 10.5 | 0.0130 | 0.0452 | 0.0582 | 0.00109 |
| QB18 | 33.4 | 12.1 | 0.0056 | 0.0224 | 0.0280 | 0.00068 |
| QB20 | 36.3 | 28.6 | 0.0238 | 0.0168 | 0.0406 | 0.00082 |

**Exclusions.** `EXCLUDED_QUBITS` carries each reason with its numbers into the selection record of `prediction.json`.
The [diagnostic job](iqm-garnet-measurement-sequence-diagnostic.md#results) (`01a1753f-3b98-7437-9433-83d0b4b87721`,
set `be070414`, 1000 shots) fixes the first five; the unitary-arm guard is two-sided (|z| >= 3), so the rule excludes a
qubit whose projected |z| reaches 3 on either sign. The projection divides the diagnostic's D6 corrected difference by
the statistical standard error of the main case's unitary arm at 3000 shots
([table and the check of the model](iqm-garnet-measurement-sequence-diagnostic.md#results)):

| qubit | projected z | reason |
|---|---|---|
| QB5 | -3.91 | the pair circuit reads 0.0331 below its model |
| QB7 | -14.23 | 0.1233 below its model; prx error 0.00545 |
| QB11 | unusable | T1 collapsed in situ (the prepared excited state reads P(0) = 0.172 at once and 0.522 after the 2 us idle, about 4 us against 47.8 us in the set); readout scale 0.384 under the 0.5 floor |
| QB14 | -5.27 | 0.0420 below its model |
| QB17 | +6.52 | 0.0527 above its model |
| QB12 | not diagnosed | prx error 0.00436, 2.6 to 6.6 times the other five qubits of the previous selection (0.00066 to 0.00169): its departure standard error of 0.041 adds little to the pooled test, and when the pooled rule fires every usable qubit contributes, so a randomized-benchmarking underestimate on QB12 alone can move the device verdict |

QB19 (projected z +2.05) stays eligible and is not selected, because it shares couplers with QB15, QB18 and
QB20. A model change was tested first and rejected: dropping or rescaling the dephasing during the drive does not
reduce the D6 residuals on all five usable qubits
([relaxation under the drive](iqm-garnet-measurement-sequence-diagnostic.md#results)).

None of the six chosen qubits was in the diagnostic, so the unitary-arm guard is untested on them: four of the five
diagnosed usable qubits project past 3, and the long-T2 qubits of this choice (QB13 14.1 us, QB20 28.6 us) are the kind
whose residual read positive on QB17. The pre-flight probe below reads their raw unitary and measure circuits; at 100
shots it resolves a 0.05 shift in P0 only at about 1.5 standard errors.

## Circuits

The job holds 57 circuits. Every circuit, `ro0` and `ro1` included, waits 2.0 us (a `delay`) before its final
`measure`, the rule of the `SETTLE_CYCLES` comment in `scripts/qi_readout_ringdown_cases.py`: photons a preceding
readout leaves in the resonator would otherwise bias the final assignment in the measure arm only, and `ro0` and
`ro1` could not correct that. Relaxation over the wait is affine in z, so `ro0` and `ro1`, which wait as long, absorb it
exactly.

- **Zeno chains, 48.** For each N in (1, 2, 4, 8, 16) the measure group beside the delay group, and at N = 16 the
  unitary and settle groups; each group is four signed circuits in the order +, -, -, +. Each step, at every N, is two
  `prx(pi/2)` pulses on every qubit with the virtual Z frame folded into their phases (step k plays phase a_k = pi/2 +
  k alpha, then a_k + pi + alpha, alpha = sign x THETA/N; the product is RX(alpha) up to Z rotations that commute with
  the pinch, the delays and the relaxation, checked to 1e-12 for every N and both signs by the self-test, and valid at
  any alpha, which the single small-angle `prx` at N = 2, 4 and 8 of the earlier form was not); then one joint `measure` with its own key (`m0`, `m1`, ...) in the measure
  and settle arms, one joint `delay` in the delay arm, or nothing in the unitary arm; the settle arm adds a 2.0 us
  `delay` after its measure. Outcomes are recorded and never condition a gate.
- **Readout and T1 series, 9.** `ro0` (the initialized state), `ro1` (`prx(pi)`, the t = 0 point of the series) and
  seven T1 circuits `t1-004` to `t1-150`: `prx(pi)`, a `delay` of 4, 10, 20, 40, 60, 100 or 150 us, the pre-readout
  delay, `measure`. The 100 and 150 us points extend the 0 to 60 us series of the request: with a T1 of 28 to 62 us the
  asymptote is out of reach below 60 us, and the departure standard error is then 3 to 4 times larger (0.02 against
  0.005 in `prediction.json`'s model) at a cost of 0.75 s of execution.

**Idle operation.** The circuit-job body takes a native `delay` operation whose `duration` is in seconds, at least that
long and rounded up to hardware granularity
([operations table and Delay](../notes/iqm/docs/iqm-client/api/iqm.iqm_client.models.md); every Target lists `delay`,
[os-4.7.md](../notes/iqm/os-4.7.md)). Garnet's dynamic quantum architecture lists no `delay` gate; garnet:mock
accepted it, and a rejection by the QPU removes the delay arm and leaves the unitary null and the departure test
unchanged.

**Measure window and prx layer.** The calibration's probe pulse lasts 364 to 556 ns and `acquisition_delay +
integration_length` 1.0 us on the earlier qubits; neither is the compiled window, because a measure runs as a
ReadoutTrigger whose duration follows the acquisition
([Measure_CustomWaveforms](../notes/iqm/docs/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.md)). Two
single-circuit QPU probes of 100 shots
([case](../../results/iqm/cases/measurement-window-qpu-probe/cases.json)) fix Garnet's compiled schedule on set
`be070414`, with the case's own circuits on its six qubits and their 2 us pre-readout delay. The compiler's estimate per
shot, the job's `execution_runtime_estimate_seconds` less the fixed 1.6 s over 100 shots:

| circuit | job | qpu_execution per shot | runtime, billed |
|---|---|---|---|
| unitary, N = 16 | `01a174be-d1f7-75fc-b324-d27d7133409b` | 7.032 us | 0.221 s, 1 s |
| measure, N = 16 | `01a174be-e68b-776e-8241-8bb3d259ae57` | 24.568 us | 0.277 s, 1 s |

So a mid-circuit measure compiles to (24.568 - 7.032)/16 = 1.096 us, and the delay arm idles for 1.096 us. The
unitary circuit's 7.032 - 2.0 = 5.032 us is one per-circuit base and 16 prx layers; the base of the retained
active-reset pilot job (`2026-10-22T212742Z`, two circuits summing to 8.688 us) is 4.344 us per circuit, which leaves
(5.032 - 4.344)/16 = 43 ns per layer, consistent with the 40 ns that garnet:mock compiles and used in the models; the 16
x 40 ns increment also shows the compiler kept the sixteen unitary-arm prx pulses separate. The predicted compiled
schedule is therefore 4.344 us per circuit + 40 ns per layer + 1.096 us per mid-circuit measure + the explicit delays.
The 40 ns layer underpredicts both single-circuit probes by 48 ns per shot (16 x 3 ns), 0.7 % of the unitary probe's
7.032 us; on the full case it dilutes to about 0.18 % (760 layers x 3 ns against the 1.246 ms per-shot schedule, which the
explicit delays dominate), so it cannot trip the 1 % re-solve, and the constant stays at 40 ns.

History: garnet:mock compiles a different schedule, 8.684 us per circuit and 1.772 us per measure (five probes,
[case](../../results/iqm/cases/measurement-timing-probe/cases.json): `ro0` 8.684, unitary 9.324, measure N = 16 37.676,
measure N = 1 10.496 and delay of 1.024 us N = 16 25.708 us per shot, jobs `01a1747a-dd17-76ae-abf5-cb2840e5bdbd`,
`-74f4-`, `-9d43-`, `-d133-` and `-ab9e-`), which is 0.62 of the QPU's estimate for the retained idle-schedule job
(`01a1707f-6157-75dc-aca8-6f30e5f0280b`, 24 circuits, 3089 prx layers). A timing taken from the mock needs a QPU check;
a mock run of this case compiles at 1.772 us and shows a schedule ratio off 1, which `analyze --mock` reports without
re-solving the window.

## Readout, T1 and initialization, measured in the job

One active-reset cycle without heralding initializes the qubits. Heralding is a job-level option, so it would cut
every circuit's shots to the all-zeros fraction, and passive reset takes 316 us per shot against 37.5 us
([timing pilot](iqm-garnet-timing-pilot.md)).

`ro0` and `ro1` read z = +-(1 - 2 p) through the assignment channel and the wait, with p the initialization excitation
after reset, so the correction (Zobs - o)/s with o and s from the pair returns the true z before the wait divided by
(1 - 2 p). The T1 series then reads y_t = (z_eq - (z_eq + 1 - 2 p) exp(-t/T1))/(1 - 2 p) = q (1 - exp(-t/T1)) -
exp(-t/T1) with q = z_eq/(1 - 2 p), where z_eq is the equilibrium z, 1 - 2 times the thermal excitation of an idle qubit.
The series fixes T1 and the one combination q, so the fit does not assume the idle qubit is cold, and p enters the
predictions only through q. The model predicts the corrected z of an arm as a + b q, with a the chain's response to
the initial z and b its response to the relaxation source; the analysis recomputes every prediction (the departure
prediction, the settle prediction, the delay-arm model) at the fitted T1 and q. `prediction.json` keeps the planning
values at the calibrated T1 and T2 and an assumed p of 0.068 (README, "Reset"), and says so.

**p_init sensitivity.** The planning prediction for the N = 16 measure arm moves from 0.877 to 0.900 at p = 0 to 0.978 to 1.018 at p = 0.20 across p = 0, 0.05, 0.10, 0.15 and 0.20 (per qubit in
`prediction.json`), a spread of 0.094 to 0.123 in P0, or 7.1 to 15.0 departure standard errors. The prediction and the corrected
estimate live in the same space, the ro0/ro1-normalized z, and the ro0/ro1 normalization cancels the p dependence of
a's term: a z0 / z0 = a. What remains is the relaxation offset divided by the initial z, b/(1 - 2 p). That offset is
not small: the measure arm spends 16 x 1.14 us = 18 us relaxing toward |0> at a T1 of 33 to 47 us, so for QB13
a = 0.487 and b = 0.282, and b/(1 - 2 p) grows from 0.282 to 0.470 across the range. The diagnostic read the starting excitation below
0.068 on four qubits (about 0.02 to 0.05); the in-job fit measures it. A corrected value above 1 at large p is the
quotient by (1 - 2 p), not a probability. The sensitivity therefore requires measuring q in the job; the T1 series does
it without a heralded circuit, and its uncertainty (0.005 to 0.008 on the equivalent p) propagates into the departure standard
error.

## Shots, billing and max_credits

- **Shots:** 3000 per circuit, one job. The worst case leaves 3.2 s below the cancel threshold, and 4250 shots would
  leave 1.04 s and lower the standard errors by 16 % at 4 credits instead of 3, so they stay at 3000.
- **Execution model:** over the seven retained active-reset Garnet QPU jobs (`01a16583-43fc-75e5-82b0-5b192921a4c5`,
  `01a16630-b928-72d1-b66e-b7779c623df5`, `01a16631-2b7c-7668-a276-3341e9d17bdd`,
  `01a167ac-58d4-74f0-96fe-9af62e1f1dfe`, `01a167ac-e6f3-711a-a9be-86bb8bfe89f9`,
  `01a167ac-ec22-7645-b50d-74b793ed808d`, `01a1707f-6157-75dc-aca8-6f30e5f0280b`), execution seconds = compiled
  schedule (the record's estimate less 1.6 s) + 0.141 s + 7.967 us per circuit-shot, with residuals of at most 0.162 s;
  runtime exceeded execution by 0.04 to 0.411 s, and billing is `ceil(runtime)` with no fixed 1.6 s term.
- **Prediction:** compiled schedule 3.738 s (the QPU-calibrated schedule, 1.246 ms per shot over the 57 circuits, the
  pairs adding 376 layers of 40 ns, 15 us, to each shot), plus 0.141 s plus 57 x 3000 x 7.967 us = 1.362 s gives 5.241 s of
  execution; the worst-case runtime adds 0.17 s of fit residual and 0.42 s of runtime over execution, 5.831 s, billed as
  6 s, or 3.00 credits at 0.50 credits/s.
- **max_credits:** 5.00 on `garnet` (10 billed seconds) and 0.00 on `garnet:mock`. `collect` cancels a run within 1.0 s
  of that, at 9.0 s of runtime, so the worst case sits 3.17 s below the cancel threshold. The build refuses less than
  1.0 s.

## Decision rule

Per qubit, from the readout-corrected P0 pooled over the four signed circuits, with binomial standard errors of every
circuit group propagated through the joint correction and T1 fit by the delta method:

- the mutation test passes when the N = 16 contrast (measure minus unitary) exceeds 0.5 by at least 3 standard
  errors;
- the departure test compares the measured N = 16 measure-arm P0 with the ideal-projective prediction at the fitted T1
  and q (a rotation with the prx depolarizing error, an ideal pinch, then T1 relaxation toward |0> over the rotation
  layer and the measure window; T2 does not enter, because the state is diagonal after every measurement) and names
  one outcome from z = (measured - predicted)/SE, the SE including the T1 and q fit and a systematic of 100 % of the
  calibrated prx error (a randomized-benchmarking average over other sequences, which the job cannot measure):
  `departs_below` (z <= -3), `exceeds_prediction` (z >= +3) or `consistent`;
- a qubit whose ro0/ro1 readout scale lies below 0.5 makes no decision.

**Device verdict.** Six qubits times about four 3-SE tests give about a 6 % chance of at least one false flag, so the
per-qubit verdicts stay descriptive and the device-level verdict is the decision. The device departs below the
prediction when at least 2 of the usable qubits return `departs_below`, or the inverse-variance pooled departure z over
the usable qubits is at or below -3 (the pooling treats the qubits as independent). The device exceeds the prediction by
the same rule with `exceeds_prediction` and z >= +3, and the settle arm attributes a readout tail to the device by the
same rule with `tail_attributed` and the pooled settle gap z >= +3.

**Gate-error guard.** A randomized-benchmarking underestimate of the prx error is shared across qubits, so the
independent prx systematic does not cover it, and the README records coherent error dominating first-order
observables. Pooling then accumulates it: a prx error twice the calibrated one on every qubit pools to a departure z of
-2.02 and three times to -3.97, which crosses -3. A device `departs_below` or `exceeds_prediction` is therefore attributed to the
measurement only if, on every qubit that contributes to it (the named qubits, or all usable qubits when the pooled z
fired), the unitary arm's N = 16 measured-minus-modeled difference lies within 3 statistical standard errors; sixteen
unmeasured pulses shift the unitary P0 by about 7.5 x the prx error, so the unitary arm is the in-job check. The
statistical standard error excludes the prx systematic, which would hide the error the check asks about. Otherwise the
device status reads `gate_model_inconsistent`, the device verdict is not set and the departure is not attributed.

Reported without a decision: the settle gap; the readout-history diagnostic (the N = 1 measure arm against the N = 1
delay arm, both ideally 0.0302 with equal models, where only the measure arm has a measurement before the final one,
so a difference of 3 standard errors or more reads as residual readout-history bias, or as a measurement-induced
transition at N = 1, about 0.94 eps in P0, which the eps fit over N tells apart); the delay arm's measured and
modeled (T1 and T2) P0 per N with their difference and the measured delay minus unitary difference at N = 16 against
the model's; the per-N measure-arm deficit against the ideal; the fit of P0(N) = (1 + ((1 - 2 eps) cos(THETA/N))^N)/2 for
eps per qubit and the same fit against the relaxed model; the transition rate between consecutive mid-circuit outcomes
against sin(THETA/(2N))^2 (about 0.008 at N = 16, below the 1 to 4 % readout error, so reported raw).

## Readout tail control

A frequency shift of the qubit that the readout leaves behind and that persists into the next prx pulse changes that
pulse. The state is diagonal after each measurement, so the shift enters only during the pulse, at second order in
delta*tau. For tau <= 100 ns and delta <= 2 pi 100 kHz the exact detuned-rotation flip probability at N = 16 moves by
about -2.5e-6 per step for THETA = 8 pi/9, far below the departure threshold. A departure larger than that bound is
therefore not explained by such a shift, and the settle arm tests the remaining readout-tail causes: it repeats the
measure arm with a `delay` of 2.0 us after each mid-circuit measure, several ring-down times of the readout resonator
(the scale is an assumption: [heron-r2-readout-resonator.md](../notes/ibm_quantum/heron-r2-readout-resonator.md) records
no Garnet ring-down figure, and the Tuna-17 ring-down arms in [tuna-17.md](../notes/quantum_inspire/tuna-17.md) are the
repository's ring-down design). Its ideal P0 equals the measure arm's 0.8914.

The settle arm relaxes for 16 x 2.0 us longer, which raises its P0 above the measure arm's on any device, so the
comparison is model-adjusted. The analysis solves, per qubit, for the per-step z loss at which the Bloch model
reproduces the measure arm's readout-corrected N = 16 P0, predicts the settle arm's P0 at that loss and the fitted
T1 and p, and reports the settle arm's measured P0 minus that prediction with its standard error
(`settle_n16.tail_gap`). When a qubit departs, a gap within 3 standard errors of zero is a match that excludes a
readout tail as the cause; a gap at least 3 standard errors above zero attributes part of the departure to the tail.
The raw settle minus measure difference is reported beside it. The arm decides nothing.

## Compiled-window check

The analysis compares the QPU job's compiled schedule (its `execution_runtime_estimate_seconds` less 1.6 s) with the
case's predicted 1.246 ms per shot summed over the circuits, times 3000 shots (3.738 s), and reports the ratio. When
they differ by more than 1 %, it solves the measure window from the QPU total, assuming the QPU-calibrated per-circuit
base and layer time, and recomputes every prediction at that window and the fitted T1 before any decision, reporting the
planned and the recomputed values. A solved window outside a factor of four of 1.096 us means the assumption fails, and
the planned window stays with the rejection reported; the per-circuit `runtime_estimates` artifact (`iqm_jobs.py
collect` keeps it, with its sha256 in the analysis) then settles the base, layer and window separately. A garnet:mock
analysis reports the ratio and the window it would solve and keeps the plan, since mock numbers decide nothing.

## Predicted outcome

Planning values from the live set `be070414` at the calibrated T1 and T2 and p = 0.068 (`prediction.json`). The
standard errors apply the run's estimator, the T1 and q fit and the prx systematic included, to the model's expected
counts at 3000 shots.

| qubit | measure P0 at N = 1, 2, 4, 8, 16 (the N = 16 value is the planning departure prediction) | delay P0 at N = 1, 2, 4, 8, 16 | unitary N = 16 | settle N = 16 | contrast | contrast SE | mutation z | departure SE |
|---|---|---|---|---|---|---|---|---|
| QB6 | 0.0633, 0.5331, 0.6929, 0.8226, 0.9020 | 0.0633, 0.1293, 0.2093, 0.3368, 0.5128 | 0.1065 | 0.9630 | 0.7950 | 0.0102 | 28.8 | 0.0137 |
| QB9 | 0.0668, 0.5356, 0.6969, 0.8289, 0.9122 | 0.0668, 0.1177, 0.1856, 0.2993, 0.4686 | 0.0968 | 0.9751 | 0.8157 | 0.0107 | 29.5 | 0.0153 |
| QB13 | 0.0579, 0.5305, 0.6908, 0.8227, 0.9066 | 0.0579, 0.0984, 0.1530, 0.2476, 0.3966 | 0.0827 | 0.9610 | 0.8235 | 0.0104 | 31.1 | 0.0133 |
| QB15 | 0.0617, 0.5327, 0.6932, 0.8249, 0.9081 | 0.0617, 0.1146, 0.1824, 0.2952, 0.4619 | 0.0923 | 0.9666 | 0.8163 | 0.0107 | 29.6 | 0.0119 |
| QB18 | 0.0673, 0.5365, 0.6994, 0.8348, 0.9238 | 0.0673, 0.1138, 0.1777, 0.2866, 0.4534 | 0.0825 | 0.9849 | 0.8419 | 0.0103 | 33.1 | 0.0082 |
| QB20 | 0.0638, 0.5349, 0.6981, 0.8352, 0.9277 | 0.0638, 0.0859, 0.1241, 0.1944, 0.3160 | 0.0634 | 0.9850 | 0.8644 | 0.0107 | 34.1 | 0.0098 |

The model device passes the mutation test by 29 to 34 standard errors, with a contrast of 0.80 to 0.86 against the ideal 0.861 (32 pulses
carry the depolarizing error and 32 layers of relaxation). The fitted T1 carries 0.7 to 1.3 us of standard error and p
0.005 to 0.008. T1 and the divided-by-(1 - 2 p) correction move the measure arm +0.011 to +0.036 against its ideal 0.8914, so the departure
test needs the fitted values. Dephasing over 16 steps of 1.14 us against T2 of 8.2 to 28.6 us lifts the delay arm to 0.32 to
0.51: idle dephasing alone produces part of the Zeno rise of the pinched arm on the short-T2 qubits (QB6 0.51), which is why
the delay arm is a control and the unitary arm the null.

**Estimator sweep.** `scripts/iqm_measurement_sequence.py sweep` (the self-test runs its reduced grid) builds raw
`measurements.json` files in the format the mock returned (per circuit and key, 3000 rows of six 0/1 outcomes in locus
order) from a model device's expected per-qubit probabilities, with no random draw: qubit j reads 1 in the shots whose
index i satisfies (i x a_j) mod 3000 < ones, with a_j coprime to 3000, and each mid-circuit key is a per-qubit
Bresenham path whose consecutive-outcome flips match the expected pair count. Each qubit's paths are independent of the
others' by construction, so the construction says nothing about cross-qubit correlation. The real `analyze` path then
runs on each device: readout correction, T1 and q fit, prediction recompute, decisions. One axis moves at a time from
the planning point, then a corner moves all four; the pass rule is |departure z| < 1, settle `match` and a passing
mutation test on every qubit, and no device-level flag.

| device | p | thermal | T1 / calibrated | prx / calibrated | departure z over the six qubits | pooled z | settle | `departs_below` status | mutation z (min) |
|---|---|---|---|---|---|---|---|---|---|
| planning | 0.068 | 0 | 1.0 | 1 | -0.02 to +0.02 | +0.01 | match | none | 28.8 |
| p=0 | 0.0 | 0.0 | 1.0 | 1 | -0.01 to +0.01 | -0.00 | match | none | 40.1 |
| p=0.15 | 0.15 | 0.0 | 1.0 | 1 | -0.02 to +0.02 | +0.01 | match | none | 21.7 |
| thermal 0.02 | 0.068 | 0.02 | 1.0 | 1 | -0.03 to +0.02 | -0.01 | match | none | 28.2 |
| T1  x 0.8 | 0.068 | 0 | 0.8 | 1 | -0.01 to +0.03 | +0.01 | match | none | 28.9 |
| T1  x 1.2 | 0.068 | 0 | 1.2 | 1 | -0.02 to +0.01 | -0.01 | match | none | 28.7 |
| pr x   x 0.5 | 0.068 | 0 | 1.0 | 0.5 | +0.39 to +0.47 | +1.03 | match | none | 30.1 |
| pr x   x 2 | 0.068 | 0 | 1.0 | 2 | -0.91 to -0.75 | -2.02 | match | none | 26.3 |
| pr x   x 3 | 0.068 | 0 | 1.0 | 3 | -1.78 to -1.52 | -3.97 | match | gate_model_inconsistent | 23.9 |
| corner | 0.15 | 0.02 | 0.8 | 2 | -0.87 to -0.64 | -1.82 | match | none | 20.3 |

The thermal row passes because the model takes q = z_eq/(1 - 2 p) from the T1 series rather than a p with a cold idle
qubit. The prx rows pass because the standard errors carry the prx systematic. A prx error twice the calibrated one on
every qubit pools to a device z of -2.02, below the device rule's threshold; three times pools to -3.97, where the
gate-error guard reads `gate_model_inconsistent` (unitary-arm z of +2.1 to +4.3 over the qubits, QB9 largest)
instead of attributing the departure, which is the pass rule of the prx x 3 row. The two-sided row runs the other way: a
prx error half the calibrated one lifts the measure arm over its prediction by 0.39 to 0.47 standard errors per qubit
(pooled +1.03), the guard's unitary-arm z is -1.1 to -0.6, and the device status stays none. A row that
drops the dephasing during the drive is absent: the [scan of the diagnostic](iqm-garnet-measurement-sequence-diagnostic.md#results)
does not support that model. The pairs double the prx count, so the
same prx error moves the unitary arm twice as far as with single pulses.

**Cross-check.** `scripts/iqm_measurement_sequence_aer_check.py run CASE_DIR --calibration-dir DIR` runs every arm and N
of every qubit through an independent Aer density-matrix simulation built on `scripts/iqm_sim.py`'s calibration noise
model (prx depolarizing error per qubit) with thermal relaxation on every wait (`iqm_signed_probe.relaxation`), the
pinch as a Kraus channel, the case's own pulses (the pi/2 pairs with their phases) and the live set's T1 and T2, from
|0>. Against the Bloch model with the prx error the largest gap over the 72 points is 3e-15 in P0. The check
verifies the model's algebra and time accounting, not the estimator, which the sweep covers.

## Pre-flight stop rule

The first form of this check read the two window probes against corrected planning values and stopped the main job on a
comparison across spaces (below). The restated rule compares raw readings with the raw model of the same circuit, and
it reads the rebuilt case's own circuits, because the pi/2-pair steps are new and the diagnostic read none of the six
chosen qubits.

The probe case [results/iqm/cases/measurement-sequence-pinching-probe](../../results/iqm/cases/measurement-sequence-pinching-probe/cases.json)
holds the main case's `ro0`, `ro1`, `unitary-n16-s0p` and `measure-n16-s0p` circuits byte for byte, 100 shots, one job
(`probe`), `max_credits` 1.0 on `garnet` and 0.0 on `garnet:mock`, a predicted worst-case runtime of 0.74 s and 0.5
credits. `scripts/iqm_measurement_preflight.py build DIR` copies the circuits and its `check` and self-test compare them
with the main case; `prediction.json` binds the main case's `cases.json` digest. The raw P(0) of the final key `f` per
qubit is compared with the band of `prediction.json` (`raw_band`), the raw model over the starting excitation p = 0 to
0.068:

| qubit | ro0 | ro1 | unitary-16 | measure-16 |
|---|---|---|---|---|
| QB6 | 0.923 to 0.985 | 0.074 to 0.136 | 0.171 to 0.220 | 0.846 to 0.873 |
| QB9 | 0.924 to 0.985 | 0.090 to 0.150 | 0.176 to 0.225 | 0.857 to 0.882 |
| QB13 | 0.911 to 0.973 | 0.061 to 0.123 | 0.137 to 0.189 | 0.837 to 0.867 |
| QB15 | 0.926 to 0.987 | 0.090 to 0.151 | 0.173 to 0.223 | 0.855 to 0.883 |
| QB18 | 0.932 to 0.994 | 0.079 to 0.141 | 0.154 to 0.206 | 0.872 to 0.898 |
| QB20 | 0.914 to 0.976 | 0.068 to 0.130 | 0.126 to 0.180 | 0.858 to 0.886 |

**Stop rule.** The orchestrator submits the main case only if, on every qubit, each of the four readings lies within 3
binomial standard errors of its band (the standard error taken at the nearest band edge and the probe's 100 shots, 0.03
to 0.045), the ro0 minus ro1 contrast is at least 0.6, and every key (`f` in the first three circuits, `f` and `m0` to
`m15` in measure-16) returns one outcome per shot. `analyze RUN_DIR --out FILE` prints PASS or FAIL per qubit with the
four readings, the contrast and the largest |z|, and ends with `proceed` or `stop`. A collapse like QB11's (ro1 at 0.52
against a band of 0.07 to 0.15) or a reading like the first form's QB19 (0.38 against 0.13 to 0.22) fails it. The check
gates the submission only and never enters the analysis.

**Replay on the diagnostic's readings.** The rule applied to the proportions the diagnostic measured at 1000 shots on
three qubits that were read, with the standard error of a 100-shot probe (D1 is `ro0`, D2 is `ro1`, D6 is the
pi/2-pair circuit, which is `unitary-16` with the sign +). The raw model at the README's p = 0.068 alone put `ro0` near
0.927, below the readings of 0.958 (QB5) and 0.971 (QB14); the earlier band, p = 0.02 to 0.068, reached 0.969 on QB14 and
left that reading outside its upper edge by 0.12 standard errors. The widening to p = 0 was elective: no replayed
reading came near 3 under the old band (largest |z| 1.39), and the wider band loosens the rule by the distance
between the two lower edges.

| qubit | ro0 (D1) | ro1 (D2) | unitary-16 (D6) | contrast | unitary-16 z at 1000 shots |
|---|---|---|---|---|---|
| QB5 | 0.958 in [0.931, 0.994], z +0.00 (old band +0.00) | 0.080 in [0.072, 0.135], z +0.00 (old band -0.36) | 0.135 in [0.160, 0.211], z -0.68 (old band -1.05) | 0.878 | -2.15 |
| QB14 | 0.971 in [0.924, 0.988], z +0.00 (old band +0.12) | 0.058 in [0.055, 0.118], z +0.00 (old band -0.60) | 0.116 in [0.153, 0.203], z -1.03 (old band -1.39) | 0.913 | -3.26 |
| QB19 | 0.919 in [0.902, 0.962], z +0.00 (old band +0.00) | 0.102 in [0.069, 0.130], z +0.00 (old band +0.00) | 0.199 in [0.159, 0.208], z +0.00 (old band +0.00) | 0.817 | +0.00 |

The largest |z| is 1.03 against the new band, so the known-good readings pass with margin. These qubits are not in
the rebuilt case; the replay tests the rule's calibration, not the new qubits. It also shows the rule's reach: QB14
passes at 100 shots (z -1.03) although the guard's projection for it is -5.27, and the same reading at 1000 shots reads
-3.26 and stops.

**Power.** One standard error of a 100-shot reading is 0.03 to 0.04 in P(0), so the probe stops a collapse or a gross
shift and cannot resolve the 0.03 to 0.06 systematic that the unitary-arm guard reads at 3000 shots (statistical
standard error 0.008). The same four circuits at 1000 shots (`build DIR --shots 1000`) are predicted to bill the same 1
s and 0.5 credits (worst-case runtime 0.81 s, 0.19 s below the cancel threshold) and cut the standard error by 3.2.

**Earlier form and its record.** The first form read the two retained window probes (100 shots each of measure-n16 and
unitary-n16 with single pi/18 pulses; jobs `01a174be-e68b-776e-8241-8bb3d259ae57` and
`01a174be-d1f7-75fc-b324-d27d7133409b`) and required every qubit to read 0.80 to 0.98 on measure-n16 and 0.00 to 0.20 on
unitary-n16. It stopped: unitary-n16 read 0.19, 0.21, 0.25, 0.14, 0.22 and 0.38 on QB5, QB7, QB11, QB14, QB17 and QB19,
which the note compared with the corrected planning values of 0.053 to 0.094 (3.2 to 13.3 binomial standard errors) and
attributed to a coherent error of the sixteen pi/18 pulses, from per-pulse fits that the final keys could not
separate; a hidden Markov fit of the mid-circuit keys then disfavored a shared under-rotation.

**Correction.** The comparison compared raw readings with corrected values, which live in different spaces. Against the
raw model of the same circuit (0.182, 0.218, 0.172, 0.169, 0.164, 0.177 at p = 0.068) the probe readings sit at +0.2,
-0.2, +2.1, -0.8, +1.5 and +5.3 standard errors; only QB19 is far from its model, and the 0.00 to 0.20 band sits below
the raw model of four of the six qubits. The [diagnostic case](iqm-garnet-measurement-sequence-diagnostic.md) read the
readout in situ on the QPU and returned `no_excess`: the raw N = 16 unitary reading matched its model on five usable
qubits and QB19's 0.38 did not reproduce (0.191 at 1000 shots), so the stop rule fired on a comparison across spaces
and one noisy reading. Its [results](iqm-garnet-measurement-sequence-diagnostic.md#results) also found QB11's T1
collapsed and QB17's pi/2-pair excess, and the preregistered rebuild criterion rebuilt this case with pi/2-pair steps.

## Window sensitivity

The planned measure window of 1.096 us comes from two QPU probes on this set and carries their rounding (a layer of 43
ns instead of 40 ns moves it by 3 ns). The planning prediction at the N = 16 measure arm and the settle arm over the
window, per qubit (`prediction.json`, `window_sensitivity`); the last column is the shift to the 1.772 us that
garnet:mock compiles, in departure standard errors:

| qubit | measure P0 at 0.6 / 0.8 / 1.096 / 1.4 / 1.772 us | settle P0 at 0.6 / 1.096 / 1.772 us | dP0/dw measure, settle (per us) | shift 1.096 to 1.772 us, measure |
|---|---|---|---|---|
| QB6 | 0.8803 / 0.8895 / 0.9020 / 0.9138 / 0.9268 | 0.9511 / 0.9630 / 0.9769 | 0.0406, 0.0225 | 0.0248 (1.8) |
| QB9 | 0.8888 / 0.8987 / 0.9122 / 0.9247 / 0.9383 | 0.9631 / 0.9751 / 0.9886 | 0.0433, 0.0222 | 0.0261 (1.7) |
| QB13 | 0.8880 / 0.8958 / 0.9066 / 0.9168 / 0.9282 | 0.9500 / 0.9610 / 0.9739 | 0.0349, 0.0208 | 0.0216 (1.6) |
| QB15 | 0.8874 / 0.8961 / 0.9081 / 0.9194 / 0.9318 | 0.9551 / 0.9666 / 0.9800 | 0.0387, 0.0217 | 0.0237 (2.0) |
| QB18 | 0.9005 / 0.9104 / 0.9238 / 0.9361 / 0.9494 | 0.9734 / 0.9849 / 0.9977 | 0.0428, 0.0212 | 0.0256 (3.1) |
| QB20 | 0.9064 / 0.9154 / 0.9277 / 0.9390 / 0.9514 | 0.9741 / 0.9850 / 0.9974 | 0.0394, 0.0203 | 0.0238 (2.4) |

A window error of 0.1 us moves the measure-arm prediction by 0.003 to 0.004, 0.3 to 0.5 departure standard errors.

## Readout crosstalk

`ro1` puts all six qubits in |1> at once, while the measure arm's neighbor states vary from shot to shot, so
state-dependent simultaneous-readout crosstalk is not calibrated and enters the corrected P0 as an unmodeled systematic.
The case adds no circuit for it. `analyze` reports descriptively, per qubit, the largest absolute correlation of its
final outcome with another qubit's in `ro0`, `ro1` and the N = 16 measure arm (`readout_crosstalk`), against the 0.018
shot noise of 3000 shots.

## Leakage readout

A leakage reading through `measure_012` is unavailable through circuit jobs on the mock, and the QPU path is untested.
The approved mock job `01a17474-d704-754e-9f02-88a9801da412` failed validation with "Error in stage circuit_stage
pass _validate_circuits: Circuit 45: Circuit contains no measurements", because circuit 45 (`delay-n16-012-p`) read
out only through `measure_012`, which the validator does not count as a measurement. The probe mock job
`01a17476-59e7-7133-b4ac-05f867b44ea9` ([case](../../results/iqm/cases/measure-012-probe/cases.json)) ran `prx(pi)`
on QB1 and QB3, a plain `measure` on QB20 (key `s`) and a four-qubit `measure_012` (key `f`); it completed, and
`measurements.json` returned only key `s`. The circuit API accepts `measure_012` and returns no outcome for it, so
this case carries no leakage circuits and no P(2) readout.

## Evidence

- Diagnostic job on the QPU (`01a1753f-3b98-7437-9433-83d0b4b87721`, 0.50 credits):
  [run](../../results/iqm/runs/2026-10-25T224718Z-garnet-measurement-sequence-diagnostic-diagnostic/results.json),
  [analysis](../../results/iqm/measurement_sequence_diagnostic_analysis.json), and its
  [design](iqm-garnet-measurement-sequence-diagnostic.md).
- Mock run of this case (pi/2 pairs at every N, the symmetric exclusion; job 01a1755f-4e86-77ee-81be-7b1de90a3c0a; all 57
  circuits returned every key; compiled schedule 1.30 times the QPU-calibrated prediction, the mock's own base and
  window):
  [run](../../results/iqm/runs/2026-10-25T232219Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Mock run of the earlier pair form (pairs at N = 16 only, on QB1, QB5, QB8, QB12, QB14 and QB19; job
  01a17548-7e68-72ab-8a27-38f1b6f3d94f), superseded and not replayable by the current script:
  [run](../../results/iqm/runs/2026-10-25T225725Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Pre-flight probe case: [case](../../results/iqm/cases/measurement-sequence-pinching-probe/cases.json), built by
  `scripts/iqm_measurement_preflight.py`; not yet run on the QPU.
- Failed mock job of the first, 54-circuit form of this case:
  [run](../../results/iqm/runs/2026-10-25T190614Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Mock run of the second, 50-circuit form (job 01a17484):
  [run](../../results/iqm/runs/2026-10-25T192310Z-garnet_mock-measurement-sequence-pinching-pinching/results.json) and
  [its analysis](../../results/iqm/measurement_sequence_pinching_mock_analysis.json), produced by an earlier revision of
  the script; the circuits it ran differ from this case's, so the current script cannot replay it.
- Mock run of the hardened 57-circuit form (job 01a174a7), compiled schedule ratio 1.0000:
  [run](../../results/iqm/runs/2026-10-25T200157Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Window probes on the QPU, jobs `01a174be-d1f7-75fc-b324-d27d7133409b` and `01a174be-e68b-776e-8241-8bb3d259ae57`,
  1.00 credit in all: [case](../../results/iqm/cases/measurement-window-qpu-probe/cases.json), runs
  `results/iqm/runs/2026-10-25T2027*Z-garnet-measurement-window-qpu-probe-*`.
- Timing probe case and its five mock runs:
  [case](../../results/iqm/cases/measurement-timing-probe/cases.json), runs
  `results/iqm/runs/2026-10-25T1912*Z-garnet_mock-measurement-timing-probe-*`.
- `measure_012` probe case and its mock run:
  [case](../../results/iqm/cases/measure-012-probe/cases.json),
  [run](../../results/iqm/runs/2026-10-25T190754Z-garnet_mock-measure-012-probe-probe/results.json).

## Sequence

1. Rebuild the case against the live calibration set and run `check`; a rebuilt case changes its digest, so rebuild the
   probe with `scripts/iqm_measurement_preflight.py build` and run its `check`.
2. Run the pre-flight probe on the QPU after the owner approves its 0.5 credits (`iqm_jobs.py submit` of the probe case,
   `collect`, then `iqm_measurement_preflight.py analyze RUN_DIR --out FILE`) and apply its stop rule.
3. Approval of this written case, then `submit` on `garnet` with `--approved-cases-sha256` and `--max-credits 5.0`,
   and `collect` right after.
4. `analyze RUN_DIR --out FILE` writes the decisions.

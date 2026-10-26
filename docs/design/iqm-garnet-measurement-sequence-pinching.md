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

The six qubits come from the live calibration set by one rule, which reads calibration data and measured failures
only. The recorded rule takes the six qubits of smallest e01 + e10 among those whose T1 is at least the set's median
(37.96 us), in that order, skipping any that shares a cz coupler with one already taken, and extends by the uncoupled
remainder in decreasing T1 when fewer qualify. Its output on set `be070414` with no other condition is QB5, QB7, QB11,
QB14, QB17 and QB19. Two conditions remove qubits from the candidates:

- **A measured failure** (`EXCLUDED_QUBITS`): QB11. The [diagnostic job](iqm-garnet-measurement-sequence-diagnostic.md#results)
  (`01a1753f-3b98-7437-9433-83d0b4b87721`, 1000 shots) read its prepared excited state at P(0) = 0.172 at once and 0.522
  after the 2 us idle, a T1 of about 4 us against 47.8 us in the set, and a readout scale of 0.384 under the 0.5 floor.
- **A calibrated prx error above 2 times the set's median** (0.00112, a limit of 0.00224), applied to every qubit:
  QB12 (0.00436), QB3 (0.00970), QB7 (0.00545). Such a qubit's departure standard error is dominated by the gate
  systematic and it adds little to the pooled test; the diagnostic's QB7 shows it, with a D6 standard error of 0.063
  against 0.016 to 0.022 on the others.

Only 4 uncoupled qubits clear the median once those are removed (QB5, QB14, QB17 and QB19), so the choice
extends to QB8 (32.3 us) and QB1 (27.5 us), which lowers the T1 floor to 27.5 us. No qubit pair of the choice shares a
coupler, and the build refuses a calibration that says otherwise. Each qubit runs the same arm in parallel in every
circuit.

| qubit | T1 (us) | T2 Ramsey (us) | e01 | e10 | e01 + e10 | prx error |
|---|---|---|---|---|---|---|
| QB1 | 27.5 | 9.9 | 0.0076 | 0.0154 | 0.0230 | 0.00169 |
| QB5 | 45.8 | 9.3 | 0.0058 | 0.0306 | 0.0364 | 0.00102 |
| QB8 | 32.3 | 8.3 | 0.0060 | 0.0404 | 0.0464 | 0.00122 |
| QB14 | 44.9 | 7.0 | 0.0124 | 0.0124 | 0.0248 | 0.00066 |
| QB17 | 46.3 | 14.1 | 0.0096 | 0.0162 | 0.0258 | 0.00094 |
| QB19 | 59.1 | 7.9 | 0.0376 | 0.0380 | 0.0756 | 0.00092 |

QB1 and QB8 were not in the diagnostic. The diagnostic's pi/2-pair residuals of the other four chosen qubits are
descriptive, not exclusions. Its corrected D6 differences against the model were z = -1.63 (QB5), -2.64 (QB14),
+2.71 (QB17) and +0.80 (QB19); with QB7's -1.96 they give chi-square 21.5 on 5 degrees of freedom against standard
errors that already carry the prx systematic, a qubit-level model scatter of about 0.03 in P0 with mixed signs. A
1000-shot estimate projected to the 3000-shot standard error as if it were exact would read
-3.91, -5.27, +6.52 and +2.05 against an absolute model, which is the reason the decision rule
below does not test the unitary arm against the absolute model. The projection is `iqm_measurement_sequence.py
project`; a scan of the diagnostic's counts under each model of the drive's relaxation keeps the calibrated model
([relaxation under the drive](iqm-garnet-measurement-sequence-diagnostic.md#results)).

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

**p_init sensitivity.** The planning prediction for the N = 16 measure arm moves from 0.871 to 0.889 at p = 0 to 0.947 to 1.028 at p = 0.20 across p = 0, 0.05, 0.10, 0.15 and 0.20 (per qubit in
`prediction.json`), a spread of 0.076 to 0.139 in P0, or 1.5 to 3.0 departure standard errors. The prediction and the corrected
estimate live in the same space, the ro0/ro1-normalized z, and the ro0/ro1 normalization cancels the p dependence of
a's term: a z0 / z0 = a. What remains is the relaxation offset divided by the initial z, b/(1 - 2 p). That offset is
not small: the measure arm spends 16 x 1.14 us = 18 us relaxing toward |0> at a T1 of 28 to 59 us, so for QB1
a = 0.359 and b = 0.418, and b/(1 - 2 p) grows from 0.418 to 0.697 across the range. The diagnostic read the starting excitation below
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
  runtime exceeded execution by 0.04 to 0.411 s, and billing is `ceil(runtime)` with no fixed 1.6 s term. This fit held no job with many mid-circuit
  measures and underpredicted the run by 3.55 s (Results); the corrected fit is in the
  [IQM notes](../notes/iqm/README.md#cost), and its worst case for these circuits, 9.41 s, would need a `max_credits`
  of 5.71.
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
  one outcome from z = (measured - predicted)/SE, the SE including the T1 and q fit, a systematic of 100 % of the
  calibrated prx error (a randomized-benchmarking average over other sequences, which the job cannot measure) and the
  gate-model systematic below: `departs_below` (z <= -3), `exceeds_prediction` (z >= +3) or `consistent`;
- a qubit whose ro0/ro1 readout scale lies below 0.5 makes no decision.

**Device verdict.** Six qubits times about four 3-SE tests give about a 6 % chance of at least one false flag, so the
per-qubit verdicts stay descriptive and the device-level verdict is the decision. The device departs below the
prediction when at least 2 of the informative qubits return `departs_below`, or the inverse-variance pooled departure z
over the informative qubits is at or below -3 (the pooling treats the qubits as independent); a qubit is informative
unless it is `uninformative` (below). The device exceeds the prediction by
the same rule with `exceeds_prediction` and z >= +3, and the settle arm attributes a readout tail to the device by the
same rule with `tail_attributed` and the pooled settle gap z >= +3.

**Gate-model systematic.** The unitary arm has no measurement, so its N = 16 residual against the model is gate-model
error alone, and the [diagnostic](iqm-garnet-measurement-sequence-diagnostic.md#results) found those residuals
scattering across qubits by about 0.03 in P0 with mixed signs. A test of the unitary arm against the absolute model
within 3 x 0.008 could only return a null, so the case does not withhold on the unitary arm's size. It withholds only
the measure-arm shift that a gate-model error consistent with the observed unitary residual could produce. Per qubit,
from the model at the fitted T1 and q, the ratio of the measure arm's N = 16 corrected-P0 shift to the unitary arm's
for a small change of each error class (`gate_class_ratios`, central differences):

| qubit | axis phase per pulse, preregistered (+1 sign) | axis phase per pulse, sign-pooled | dephasing rate during the layers | composite pulse-angle scale | depolarizing prx error | departure SE before | departure SE after |
|---|---|---|---|---|---|---|---|
| QB1 | +0.324 | -0.018 | -0.435 | +0.657 | -0.683 | 0.0155 | 0.0464 |
| QB5 | +0.353 | -0.019 | -0.478 | +0.735 | -0.749 | 0.0114 | 0.0496 |
| QB8 | +0.334 | -0.019 | -0.453 | +0.683 | -0.711 | 0.0122 | 0.0470 |
| QB14 | +0.352 | -0.019 | -0.482 | +0.729 | -0.757 | 0.0085 | 0.0491 |
| QB17 | +0.353 | -0.019 | -0.471 | +0.739 | -0.739 | 0.0110 | 0.0492 |
| QB19 | +0.364 | -0.020 | -0.497 | +0.763 | -0.779 | 0.0115 | 0.0514 |

The computed ratios differ from the values a first-order argument suggests: the depolarizing error moves the measure arm -0.78 to -0.68 of the unitary arm's shift (not -1, because the pinch and the relaxation share the loss), the composite-angle scale +0.66 to +0.76 (not +0.4; the pair composite barely moves the unitary arm, so the ratio rests on a small denominator) and the dephasing-during-drive scale -0.50 to -0.44.

**Axis phase and the four signed circuits.** The preregistered evaluation computed every ratio on the +1 signed circuit, which gives the axis phase +0.32 to +0.36. The experiment pools four signed circuits (+, -, -, +). The reflection x -> -x maps the sign -1 chain at an axis-phase advance d onto the sign +1 chain at advance -d, so the pooled response is even in the advance: its first-order term cancels (the pooled central difference of the unitary arm is about 1e-16), and the ratio of the measure arm's to the unitary arm's curvature, f(h) + f(-h) - 2 f(0), is -0.020 to -0.018. The other three classes are reflection invariant, and their sign-pooled ratios equal the one-sign values. The sign-pooled column is the one the `--gate-model sign-pooled` analysis uses; the preregistered analysis keeps the one-sign column, and [the reanalysis](#sign-pooled-reanalysis) reports both.

The departure standard error of each qubit adds, in quadrature over the four classes, ratio_c x s, with s the root of the squared unitary residual and its squared statistical standard error, floored at 0.04 (`RAW_MODEL_SCATTER`, the diagnostic's measured model scatter, which keeps the standard error from narrowing when the unitary residual happens to be small). The device pooling weights each qubit by the inverse of the widened variance. The right-hand column is the departure standard error at the floor, which a unitary arm matching its model and one off by up to 0.04 share. The quadrature sum ignores the signs of the ratios, which makes it conservative for a single class and not for a mixture, and the pooling treats the per-qubit systematics as independent although a shared gate error is not; the sweep tests both. The prx systematic of 100 % of the calibrated error stays in the standard error beside the depolarizing class.

**Uninformative qubits and devices.** A qubit is `uninformative` when its mutation test fails or its widened departure
standard error exceeds 2 x its planning value in `prediction.json` (`UNINFORMATIVE_SE_FACTOR`, preregistered); the count
and pooled rules skip it. The device reads `uninformative`, and attributes nothing, when fewer than 2 informative qubits
remain. A gate so far from its model that the unitary arm leaves P0 near 0.5 (the broken-gate sweep row) then reads
`uninformative` and not `none`, which a clean null also reads.

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
| QB1 | 0.0759, 0.5410, 0.7037, 0.8371, 0.9215 | 0.0759, 0.1321, 0.2083, 0.3337, 0.5146 | 0.1044 | 0.9893 | 0.8170 | 0.0104 | 30.6 | 0.0464 |
| QB5 | 0.0587, 0.5307, 0.6904, 0.8207, 0.9017 | 0.0587, 0.1172, 0.1890, 0.3060, 0.4741 | 0.0957 | 0.9576 | 0.8063 | 0.0100 | 30.6 | 0.0496 |
| QB8 | 0.0697, 0.5372, 0.6987, 0.8307, 0.9136 | 0.0697, 0.1346, 0.2160, 0.3465, 0.5280 | 0.1051 | 0.9787 | 0.8084 | 0.0106 | 29.0 | 0.0470 |
| QB14 | 0.0596, 0.5310, 0.6903, 0.8198, 0.8991 | 0.0596, 0.1346, 0.2207, 0.3541, 0.5311 | 0.1055 | 0.9563 | 0.7932 | 0.0097 | 30.2 | 0.0491 |
| QB17 | 0.0577, 0.5306, 0.6912, 0.8238, 0.9092 | 0.0577, 0.0981, 0.1525, 0.2468, 0.3959 | 0.0794 | 0.9631 | 0.8296 | 0.0098 | 33.5 | 0.0492 |
| QB19 | 0.0533, 0.5272, 0.6851, 0.8127, 0.8893 | 0.0533, 0.1206, 0.1979, 0.3200, 0.4873 | 0.1011 | 0.9388 | 0.7884 | 0.0107 | 27.0 | 0.0514 |

The model device passes the mutation test by 27 to 33 standard errors, with a contrast of 0.79 to 0.83 against the ideal 0.861 (32 pulses
carry the depolarizing error and 32 layers of relaxation). The fitted T1 carries 0.5 to 2.3 us of standard error and p
0.005 to 0.012. T1 and the divided-by-(1 - 2 p) correction move the measure arm +-0.002 to +0.030 against its ideal 0.8914, so the departure
test needs the fitted values. Dephasing over 16 steps of 1.14 us against T2 of 7.0 to 14.1 us lifts the delay arm to 0.40 to
0.53: idle dephasing alone produces part of the Zeno rise of the pinched arm on the short-T2 qubits, which is why
the delay arm is a control and the unitary arm the null.

**Estimator sweep.** `scripts/iqm_measurement_sequence.py sweep` (the self-test runs its reduced grid) builds raw
`measurements.json` files in the format the mock returned (per circuit and key, 3000 rows of six 0/1 outcomes in locus
order) from a model device's expected per-qubit probabilities, with no random draw: qubit j reads 1 in the shots whose
index i satisfies (i x a_j) mod 3000 < ones, with a_j coprime to 3000, and each mid-circuit key is a per-qubit
Bresenham path whose consecutive-outcome flips match the expected pair count. Each qubit's paths are independent of the
others' by construction, so the construction says nothing about cross-qubit correlation. The real `analyze` path then
runs on each device: readout correction, T1 and q fit, prediction recompute, gate-model systematic, decisions. The
rows move one nuisance at a time from the planning point, then a corner moves four; the injected rows add a gate-model
error the analysis does not model (a scale on the dephasing rate during the layers, an axis phase per pulse; the
nominal prediction keeps the calibrated model) and, where marked, a true departure: a per-step z loss that lowers the
measure arm's N = 16 P0 by 4 departure standard errors of the same device without it. The pass rule per row is its
last column: `nuisance` (every qubit |departure z| < 1, settle `match`, no flag), `none` (no device flag),
`never_attributed`, `attributed`, or `broken` (the device reads `uninformative`).

| device | p | thermal | T1 / calibrated | prx / calibrated | model error | injected departure | unitary residual (P0) | departure SE | departure z over the six qubits | pooled z | informative qubits | `departs_below` status | mutation z (min) | pooled z, sign-pooled | status, sign-pooled | rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| planning | 0.068 | 0 | 1 | 1 | none | none | -0.000 to +0.000 | 0.046 to 0.051 | -0.01 to +0.00 | -0.00 | 6 | none | 27.0 | -0.01 | none | nuisance |
| p=0 | 0 | 0 | 1 | 1 | none | none | -0.000 to +0.000 | 0.045 to 0.050 | -0.00 to +0.00 | +0.00 | 6 | none | 37.3 | +0.00 | none | nuisance |
| p=0.15 | 0.15 | 0 | 1 | 1 | none | none | -0.000 to +0.000 | 0.049 to 0.053 | -0.01 to +0.00 | -0.00 | 6 | none | 20.1 | -0.00 | none | nuisance |
| thermal 0.02 | 0.068 | 0.02 | 1 | 1 | none | none | -0.000 to +0.000 | 0.046 to 0.051 | -0.00 to +0.00 | -0.00 | 6 | none | 26.5 | -0.00 | none | nuisance |
| T1 x0.8 | 0.068 | 0 | 0.8 | 1 | none | none | -0.000 to +0.000 | 0.044 to 0.050 | -0.01 to +0.01 | +0.00 | 6 | none | 27.1 | +0.00 | none | nuisance |
| T1 x1.2 | 0.068 | 0 | 1.2 | 1 | none | none | -0.000 to +0.000 | 0.048 to 0.052 | -0.00 to +0.00 | -0.00 | 6 | none | 26.8 | -0.00 | none | nuisance |
| prx x0.5 | 0.068 | 0 | 1 | 0.5 | none | none | -0.011 to -0.004 | 0.046 to 0.051 | +0.06 to +0.17 | +0.26 | 6 | none | 27.8 | +0.27 | none | nuisance |
| prx x2 | 0.068 | 0 | 1 | 2 | none | none | +0.008 to +0.021 | 0.046 to 0.051 | -0.31 to -0.13 | -0.51 | 6 | none | 25.3 | -0.53 | none | nuisance |
| prx x3 | 0.068 | 0 | 1 | 3 | none | none | +0.017 to +0.041 | 0.047 to 0.051 | -0.58 to -0.26 | -0.99 | 6 | none | 23.6 | -1.03 | none | never_attributed |
| corner | 0.15 | 0.02 | 0.8 | 2 | none | none | +0.008 to +0.021 | 0.046 to 0.052 | -0.32 to -0.14 | -0.52 | 6 | none | 19.1 | -0.54 | none | nuisance |
| drive x0.5 | 0.068 | 0 | 1 | 1 | drive_t2_scale 0.5 | none | -0.029 to -0.015 | 0.046 to 0.051 | +0.15 to +0.28 | +0.54 | 6 | none | 30.0 | +0.56 | none | none |
| drive x0.5 + departure | 0.068 | 0 | 1 | 1 | drive_t2_scale 0.5 | 4 SE | -0.029 to -0.015 | 0.046 to 0.051 | -3.85 to -3.71 | -9.24 | 6 | attributed | 12.4 | -9.64 | attributed | attributed |
| drive x1.5 | 0.068 | 0 | 1 | 1 | drive_t2_scale 1.5 | none | +0.014 to +0.027 | 0.046 to 0.051 | -0.28 to -0.15 | -0.52 | 6 | none | 24.0 | -0.54 | none | none |
| drive x1.5 + departure | 0.068 | 0 | 1 | 1 | drive_t2_scale 1.5 | 4 SE | +0.014 to +0.027 | 0.046 to 0.052 | -4.27 to -4.14 | -10.29 | 6 | attributed | 4.8 | -10.73 | attributed | attributed |
| axis 0.02 | 0.068 | 0 | 1 | 1 | advance 0.02 | none | +0.028 to +0.030 | 0.046 to 0.051 | -0.02 to -0.01 | -0.03 | 6 | none | 24.6 | -0.03 | none | none |
| axis 0.02 + departure | 0.068 | 0 | 1 | 1 | advance 0.02 | 4 SE | +0.028 to +0.030 | 0.046 to 0.051 | -4.01 to -4.00 | -9.80 | 6 | attributed | 5.6 | -10.22 | attributed | attributed |
| axis 0.1 (broken gate) | 0.068 | 0 | 1 | 1 | advance 0.1 | none | +0.526 to +0.556 | 0.576 to 0.667 | -0.02 to -0.02 | n/a | 0 | uninformative | -33.7 | n/a | uninformative | broken |
| axis 0.02 + prx x2 | 0.068 | 0 | 1 | 2 | advance 0.02 | none | +0.036 to +0.048 | 0.049 to 0.056 | -0.27 to -0.14 | -0.49 | 6 | none | 23.0 | -0.51 | none | never_attributed |
| prx x3 + drive x0.5 | 0.068 | 0 | 1 | 3 | drive_t2_scale 0.5 | none | -0.012 to +0.023 | 0.046 to 0.051 | -0.43 to +0.02 | -0.49 | 6 | none | 26.6 | -0.51 | none | never_attributed |
| drive x0.5 + departure + prx x2 | 0.068 | 0 | 1 | 2 | drive_t2_scale 0.5 | 4 SE | -0.021 to +0.001 | 0.046 to 0.051 | -4.12 to -3.85 | -9.77 | 6 | attributed | 10.3 | -10.18 | attributed | either |

Each signed circuit of a model device takes the chain of its own sign, so an axis phase moves the four circuits differently (the first generation of this sweep copied the +1 sign's result into all four). The unitary residuals of the model-error rows are the injected scatter: the dephasing scales give about +-0.015 to 0.03 and the axis phase of 0.02 rad about +0.028 to +0.030. The broken-gate row (0.1 rad per pulse) turns the unitary arm to P0 near 0.5, fails the mutation test on every qubit and reads `uninformative`. Every non-injected row reads `none` under both analyses, a prx error of three times the calibration is never attributed (pooled z -0.99, sign-pooled -1.03), and every injected departure reads `attributed`, with or without the prx error of twice the calibration. The row "axis 0.02 + prx x2" pools to -0.49 (sign-pooled -0.51) and reads `none`. On the first, one-sign generation of the sweep that row's unitary residual cancelled to near 0 (the axis phase read -0.019, the prx error +0.008 to +0.021) and, without the floor, it pooled to z = -3.82 and read `attributed`; that was the rationale stated for the floor. With each signed circuit on its own chain the two residuals add (+0.036 to +0.048), the floor is inactive on the row, and the device reads `none` with or without it. The floor stays because it was preregistered, and its stated rationale is the diagnostic's measured scatter of 0.04, which a unitary residual that happens to be small must not narrow. A 4-standard-error departure at the floored standard error is a P0 shift of about 0.2, which lowers the contrast and the mutation z (minimum 4.8 on an injected row).

**Minimum detectable departure.** `iqm_measurement_sequence.py detect [--gate-model ...]` raises the injected departure in steps of 0.5 departure standard errors per qubit (the standard error of the same device without the departure) until the device reads `attributed`; each cell is the smallest step (the mean P0 shift in brackets) under the preregistered and the sign-pooled analysis, and the last column the status along the grid 0.5, 1, 1.5, 2, 2.5, 3, 4 under the preregistered analysis:

| device | preregistered analysis | sign-pooled analysis | status along the grid (preregistered) |
|---|---|---|---|
| planning | 1.5 (0.073) | 1.5 (0.073) | 0.5:non / 1.0:non / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |
| drive x0.5 | 1.5 (0.073) | 1.5 (0.073) | 0.5:non / 1.0:non / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |
| drive x1.5 | 1.5 (0.073) | 1 (0.049) | 0.5:non / 1.0:non / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |
| axis 0.02 | 1.5 (0.073) | 1.5 (0.073) | 0.5:non / 1.0:non / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |
| prx x2 | 1.5 (0.073) | 1 (0.049) | 0.5:non / 1.0:non / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |
| prx x3 | 1 (0.049) | 1 (0.049) | 0.5:non / 1.0:att / 1.5:att / 2.0:att / 2.5:att / 3.0:att / 4.0:att |

A per-qubit shift of k standard errors pools to about sqrt(6) k when the six qubits share it, so the pooled rule fires
near k = 1.2 on independent errors. The pooling is not conservative for a shared gate error, and the minimum
detectable departure above is the shift at which the rule fires, not a guarantee of its false-positive rate under a
shared error; the prx-x3 and model-error rows are the evidence for that.

**Reach, sidedness and scope of the verdict, fixed before any data.**

- *Reach in the physical parameter.* The sweep injects a departure as `eps`, the fraction of z each mid-circuit
  measurement loses to transitions (`bloch_z`). On the ideal law P0 = (1 + ((1 - 2 eps) cos(THETA/16))^16)/2 the
  detectable shifts of 0.049 and 0.073 at N = 16 correspond to eps of 0.0042 and 0.0064 per measurement. Read instead
  as incomplete pinching on the ideal noiseless chain, where each measurement keeps a fraction eta of the transverse
  coherence, the same shifts correspond to eta of 0.22 and 0.31. A `none` verdict therefore bounds the measurement
  to a transition probability below about 0.006 per measurement, or to less than about 30 % of the coherence
  surviving each measurement, and no tighter. The 0.04 gate-model floor limits this reach, not the shot count: with
  propagation ratios of order 1, no shot count brings the detectable shift much below 0.05 on this chip.
- *One-sided in practice.* At the floored departure standard error of about 0.048, `exceeds_prediction` cannot fire
  on a single qubit, because the planning P0 near 0.93 plus three standard errors passes 1. Pooled, it sits near that
  ceiling. The test reads `departs_below` or `none`.
- *Scope of `attributed`.* `attributed` holds only while every gate-model error class stays within the diagnostic
  scatter that sets the floor. Two classes that cancel in the unitary arm at twice the floor, the same way on every
  qubit, can still produce a false attribution. An `attributed` verdict enters the research registry as exploratory.
  A stronger claim needs a confirmation run with a different pulse construction.
- *Settle comparison.* The settle arm's tail gap carries its delta-method standard error with no gate-model floor
  (`evaluate_qubit`). The settle and measure arms play identical pulses, so their difference is close to immune to
  gate-model error.

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
holds the main case's `ro0`, `ro1`, `unitary-n16-s0p` and `measure-n16-s0p` circuits byte for byte, 1000 shots, one job
(`probe`), `max_credits` 1.0 on `garnet` and 0.0 on `garnet:mock`, a predicted worst-case runtime of 0.81 s (0.19 s
below the cancel threshold) and 0.5 credits, the same billed second as 100 shots. `scripts/iqm_measurement_preflight.py build DIR` copies the circuits and its `check` and self-test compare them
with the main case; `prediction.json` binds the main case's `cases.json` digest. The raw P(0) of the final key `f` per
qubit is compared with the band of `prediction.json` (`raw_band`), the raw model over the starting excitation p = 0 to
0.068:

| qubit | ro0 | ro1 | unitary-16 | measure-16 |
|---|---|---|---|---|
| QB1 | 0.931 to 0.992 | 0.084 to 0.146 | 0.138 to 0.268 | 0.829 to 0.931 |
| QB5 | 0.931 to 0.994 | 0.072 to 0.135 | 0.120 to 0.251 | 0.813 to 0.923 |
| QB8 | 0.933 to 0.994 | 0.098 to 0.159 | 0.152 to 0.280 | 0.826 to 0.930 |
| QB14 | 0.924 to 0.988 | 0.055 to 0.118 | 0.113 to 0.243 | 0.803 to 0.912 |
| QB17 | 0.927 to 0.990 | 0.057 to 0.121 | 0.091 to 0.225 | 0.814 to 0.925 |
| QB19 | 0.902 to 0.962 | 0.069 to 0.130 | 0.119 to 0.248 | 0.776 to 0.887 |

**Stop rule.** The orchestrator submits the main case only if, on every qubit, each of the four readings lies within 3
binomial standard errors of its band (the standard error taken at the nearest band edge and the probe's 1000 shots,
0.010 to 0.015), the ro0 minus ro1 contrast is at least 0.6, and every key (`f` in the first three circuits, `f` and `m0` to
`m15` in measure-16) returns one outcome per shot. `analyze RUN_DIR --out FILE` prints PASS or FAIL per qubit with the
four readings, the contrast and the largest |z|, and ends with `proceed` or `stop`. A collapse like QB11's (ro1 at 0.52
against a band of 0.07 to 0.15) or a reading like the first form's QB19 (0.38 against 0.13 to 0.22) fails it. The check
gates the submission only and never enters the analysis.

**Replay on the diagnostic's readings.** The rule applied to the proportions the diagnostic measured at 1000 shots on
the four chosen qubits that were read, with the standard error of a 1000-shot probe (D1 is `ro0`, D2 is `ro1`, D6 is
the pi/2-pair circuit, which is `unitary-16` with the sign +). The raw model at the README's p = 0.068 alone put `ro0`
near 0.927, below the readings of 0.958 (QB5) and 0.971 (QB14); the band therefore starts at p = 0, and the earlier
band (p = 0.02 to 0.068) left QB14's `ro0` reading outside its upper edge by 0.12 standard errors at 100 shots.

| qubit | ro0 (D1) | ro1 (D2) | unitary-16 (D6) | contrast |
|---|---|---|---|---|
| QB5 | 0.958 in [0.931, 0.994], z +0.00 | 0.080 in [0.072, 0.135], z +0.00 | 0.135 in [0.120, 0.251], z +0.00 | 0.878 |
| QB14 | 0.971 in [0.924, 0.988], z +0.00 | 0.058 in [0.055, 0.118], z +0.00 | 0.116 in [0.113, 0.243], z +0.00 | 0.913 |
| QB17 | 0.967 in [0.927, 0.990], z +0.00 | 0.051 in [0.057, 0.121], z -0.87 | 0.172 in [0.091, 0.225], z +0.00 | 0.916 |
| QB19 | 0.919 in [0.902, 0.962], z +0.00 | 0.102 in [0.069, 0.130], z +0.00 | 0.199 in [0.119, 0.248], z +0.00 | 0.817 |

The largest |z| is 0.87 at 1000 shots (0.28 at 100 shots). The two N = 16 bands widen by 0.04 on both sides
(`RAW_MODEL_SCATTER`, the root mean square of the diagnostic's corrected D6 differences on these four qubits): without
the widening QB14's unitary reading (0.116 against a lower edge of 0.153) sits 3.3 standard errors outside at 1000
shots and would stop a qubit whose scatter the decision rule already carries.

**QB11 replay.** The diagnostic's QB11 readings (ro0 0.906, ro1 0.522, pi/2-pair unitary 0.586, contrast 0.384), run
through the probe's stop rule against QB11's own bands, read FAIL: `ro1` at 0.522 against a band of 0.065 to 0.127 is
37 standard errors outside, and the contrast of 0.384 is under the 0.6 floor. `tests/test_iqm_measurement_preflight.py`
pins it.

**Power.** One standard error of a 1000-shot reading is 0.010 to 0.015 in P(0), against 0.03 to 0.04 at 100 shots. The
probe stops a collapse or a gross shift. The gate-model scatter of about 0.03 sits near its 3-standard-error limit, so
it is a diagnostic and no substitute for the in-job unitary arm.

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
| QB1 | 0.8938 / 0.9057 / 0.9215 / 0.9357 / 0.9508 | 0.9772 / 0.9893 / 1.0025 | 0.0500, 0.0221 | 0.0293 (0.6) |
| QB5 | 0.8825 / 0.8905 / 0.9017 / 0.9122 / 0.9239 | 0.9463 / 0.9576 / 0.9709 | 0.0360, 0.0214 | 0.0223 (0.4) |
| QB8 | 0.8887 / 0.8993 / 0.9136 / 0.9268 / 0.9410 | 0.9665 / 0.9787 / 0.9923 | 0.0457, 0.0225 | 0.0274 (0.6) |
| QB14 | 0.8794 / 0.8877 / 0.8991 / 0.9098 / 0.9219 | 0.9448 / 0.9563 / 0.9698 | 0.0370, 0.0218 | 0.0228 (0.5) |
| QB17 | 0.8907 / 0.8985 / 0.9092 / 0.9193 / 0.9307 | 0.9522 / 0.9631 / 0.9759 | 0.0347, 0.0206 | 0.0215 (0.4) |
| QB19 | 0.8735 / 0.8801 / 0.8893 / 0.8982 / 0.9083 | 0.9283 / 0.9388 / 0.9514 | 0.0302, 0.0200 | 0.0190 (0.4) |

A window error of 0.1 us moves the measure-arm prediction by 0.003 to 0.005, 0.1 to 0.1 departure standard errors.

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

## Results

The main run (job `01a175ac-da6c-718e-8efc-438c1bff1c46`, 57 circuits x 3000 shots, set `be070414`, 5.0 credits;
[run](../../results/iqm/runs/2026-10-26T004701Z-garnet-measurement-sequence-pinching-pinching/results.json),
[analysis](../../results/iqm/measurement_sequence_pinching_analysis.json)) followed a pre-flight probe (job
`01a175ac-522d-73e4-ae3e-7404b2335bf6`, 1000 shots, 0.5 credits;
[run](../../results/iqm/runs/2026-10-26T004628Z-garnet-measurement-sequence-pinching-probe-probe/results.json),
[analysis](../../results/iqm/measurement_sequence_pinching_preflight.json)). Both are exploratory in the registry, per the
scope fixed above.

**Verdicts, preregistered.**

- **Departure from ideal pinching: `none`.** `departs_below` and `exceeds_prediction` both read `none`, pooled z
  +1.65, with all six qubits informative (mutation z 36 to 56, contrast 0.80 to 0.83 against the ideal
  0.861). By the reach fixed before the data, a `none` bounds the measurement to a transition probability below about
  0.006 per measurement, or to less than about 30 % of the coherence surviving each measurement, and no tighter. It does
  not establish ideal pinching below that reach.
- **Settle tail: `attributed`**, pooled z +4.81, by the count rule (QB14 +3.15 and QB5 +3.43).
  What the rule tests: the settle arm differs from the measure arm only by a 2.0 us idle after each measure, and the
  rule compares its P0 with the model's prediction from the measure arm's own N = 16 loss and the in-job T1. P0 of the
  settle arm exceeds that prediction on five of six qubits (QB1 +0.0066, QB5 +0.0161, QB8 +0.0056, QB14 +0.0156, QB17 +0.0125, QB19 -0.0056 in P0). The observation is that
  lengthening the post-measurement idle from zero to 2 us raises P0 beyond the model's prediction. The effect may come
  from a readout tail or from measurement-induced relaxation during the idle, and a tail slower than 2 us stays
  unexcluded; the run names no mechanism.
- **Compiled schedule, execution and billing.** The compiled schedule was 0.9935 times the QPU-calibrated prediction (inside the 1 %
  tolerance, window kept). Execution took 8.793 s against a predicted 5.241 s and the IQM estimate of
  5.314 s; runtime was 9.035 s, within 1 s of `collect`'s 10 s cancel threshold (+0.035 s from the 9.0 s the
  ceiling allows), billed 10 s, 5.0 credits, leaving 9.00. The billing fit had no job with many mid-circuit measures
  and underpredicted this run by 3.55 s; the corrected fit is in [the IQM notes](../notes/iqm/README.md#cost).

**Pre-flight probe.** It printed `proceed`: all six qubits PASS, the largest |z| 2.69 (QB14's `ro0`, 0.997 against the
band's upper edge). Raw P(0) with the z outside the band in parentheses:

| qubit | ro0 | ro1 | unitary-16 | measure-16 | contrast |
|---|---|---|---|---|---|
| QB1 | 0.986 (+0.00) | 0.102 (+0.00) | 0.204 (+0.00) | 0.903 (+0.00) | 0.884 |
| QB5 | 0.989 (+0.00) | 0.060 (-1.44) | 0.179 (+0.00) | 0.867 (+0.00) | 0.929 |
| QB8 | 0.991 (+0.00) | 0.085 (-1.36) | 0.207 (+0.00) | 0.900 (+0.00) | 0.906 |
| QB14 | 0.997 (+2.69) | 0.046 (-1.24) | 0.119 (+0.00) | 0.894 (+0.00) | 0.951 |
| QB17 | 0.987 (+0.00) | 0.060 (+0.00) | 0.195 (+0.00) | 0.895 (+0.00) | 0.927 |
| QB19 | 0.912 (+0.00) | 0.121 (+0.00) | 0.234 (+0.00) | 0.841 (+0.00) | 0.791 |

**Per-qubit readings** (the measure arm's N = 16 corrected P0; z is measured less predicted over the SE, which includes
the gate-model systematic floored at 0.04; the pre-systematic columns repeat the statistical-plus-prx SE):

| qubit | measured P0 | predicted | difference | SE | z | SE before the systematic | z before | contrast | mutation z |
|---|---|---|---|---|---|---|---|---|---|
| QB1 | 0.9095 | 0.8872 | +0.0223 | 0.0448 | +0.50 | 0.0145 | +1.55 | 0.831 | 42.0 |
| QB5 | 0.9029 | 0.8660 | +0.0369 | 0.0494 | +0.75 | 0.0105 | +3.51 | 0.826 | 56.1 |
| QB8 | 0.9122 | 0.8808 | +0.0313 | 0.0435 | +0.72 | 0.0105 | +2.98 | 0.802 | 45.1 |
| QB14 | 0.8997 | 0.8580 | +0.0417 | 0.0488 | +0.85 | 0.0074 | +5.66 | 0.823 | 55.7 |
| QB17 | 0.9018 | 0.8699 | +0.0319 | 0.0484 | +0.66 | 0.0099 | +3.22 | 0.809 | 53.2 |
| QB19 | 0.9057 | 0.8780 | +0.0276 | 0.0479 | +0.58 | 0.0100 | +2.76 | 0.822 | 36.4 |

Unitary-arm check (descriptive; measured less modeled N = 16 unitary P0 with its statistical SE) and settle tail gap
(measured settle P0 less the prediction from the measure arm's loss):

| qubit | unitary difference | statistical SE | z | tail gap | SE | z | tail verdict |
|---|---|---|---|---|---|---|---|
| QB1 | -0.0256 | 0.0074 | -3.44 | +0.0066 | 0.0033 | +1.98 | match |
| QB5 | -0.0176 | 0.0051 | -3.43 | +0.0161 | 0.0047 | +3.43 | tail_attributed |
| QB8 | +0.0043 | 0.0064 | +0.68 | +0.0056 | 0.0032 | +1.77 | match |
| QB14 | -0.0281 | 0.0052 | -5.40 | +0.0156 | 0.0049 | +3.15 | tail_attributed |
| QB17 | +0.0137 | 0.0052 | +2.62 | +0.0125 | 0.0048 | +2.63 | match |
| QB19 | -0.0188 | 0.0073 | -2.56 | -0.0056 | 0.0052 | -1.07 | match |

Fitted T1, initialization excitation and q from the in-job series, and the eps fits (a per-step z loss, against the
ideal law and against the relaxed model; chi-square on 4 degrees of freedom):

| qubit | T1 (us) | p_init | q | eps, ideal law | chi2 | eps, relaxed | chi2 |
|---|---|---|---|---|---|---|---|
| QB1 | 27.6 +- 0.6 | -0.0033 +- 0.0037 | 0.9935 | -0.00174 | 154.7 | -0.00251 | 18.5 |
| QB5 | 54.4 +- 1.6 | -0.0430 +- 0.0117 | 0.9208 | -0.00107 | 107.4 | -0.00365 | 28.0 |
| QB8 | 27.5 +- 0.6 | -0.0211 +- 0.0034 | 0.9594 | -0.00172 | 195.7 | -0.00329 | 48.8 |
| QB14 | 54.0 +- 1.7 | -0.0669 +- 0.0132 | 0.8820 | -0.00069 | 64.7 | -0.00402 | 18.8 |
| QB17 | 51.6 +- 1.6 | -0.0643 +- 0.0119 | 0.8861 | -0.00100 | 108.6 | -0.00317 | 37.4 |
| QB19 | 42.5 +- 1.2 | -0.0015 +- 0.0093 | 0.9970 | -0.00133 | 58.4 | -0.00272 | 14.6 |

**Descriptive readings** (outside the preregistered verdicts):

- **The measure arm reads above its prediction on every qubit**, by 0.022 to 0.042 in P0. The widened standard error
  (0.044 to 0.049) puts that at 0.5 to 0.85 SE; before the gate-model systematic it is +1.55 (QB1), +5.66 (QB14), +3.22
  (QB17), +2.76 (QB19), +3.51 (QB5) and +2.98 (QB8) SE. The pooled +1.65 is the widened-variance figure.
- **QB14's unitary arm repeats the diagnostic's sign**: -0.0281 against the diagnostic's -0.042, statistical z -5.4. QB5 (-0.0176,
  z -3.43) repeats it too (diagnostic -0.033), and QB17 (+0.0137) has the diagnostic's positive sign at a smaller size (+0.053);
  QB19 (-0.0188) reverses (+0.018 in the diagnostic). Three qubits (QB1, QB5, QB14) read beyond 3
  statistical SE, which an absolute test of the unitary arm would have read as a gate-model inconsistency on half the
  device; the widened departure standard error is what kept the verdict from resting on it.
- **Negative fitted p_init.** Four qubits fit a p_init below zero by 3.7 to 6.2 SE (QB8 -0.021, QB5 -0.043, QB17
  -0.064, QB14 -0.067); QB1 (-0.003) and QB19 (-0.002) sit within one error of zero. No initialization excitation is
  negative. In the readout model p comes from q = z_eq/(1 - 2 p), the asymptote of the T1 series corrected by `ro0` and
  `ro1`, with the idle qubit assumed cold (z_eq = 1). A fitted q below 1 (0.88 to 0.92 on QB14, QB17 and QB5) means the
  corrected series ends below 1. A thermal excitation of the idle qubit of 4 to 6 % after the 100 to 150 us delays
  (z_eq < 1) produces that with p = 0, and so does an assignment error that differs between `ro1`, read 2 us after the
  pi pulse, and the long-delay circuits. The fit separates neither. The prediction uses q and not p alone, so the
  departure test does not depend on which of them q is attributed to.
- **Poor eps fits.** The one-parameter fit of a per-step loss to P0(N) has chi-square 58 to 196 on 4 degrees of freedom against the ideal law and
  15 to 49 against the relaxed model, with negative eps (-0.0040 to -0.0025 relaxed): a loss per measurement
  cannot make P0 exceed the model at N = 16 while the lower N follow it, so the N dependence is not that of a single
  transition loss, and the family is the wrong description of the residual. The consecutive-outcome flip rate at N = 16
  is 0.013 to 0.065 against the ideal 0.0076 (QB19 0.065), reported raw beside the 1 to 4 % readout error.
- **Readout crosstalk.** The largest correlation of one qubit's outcome with another's is 0.03 to 0.06 against a shot
  noise of 0.018 (QB14 and QB17 0.060).

## Sign-pooled reanalysis

The preregistered gate-model systematic evaluated the axis-phase class on the +1 signed circuit only (`gate_class_ratios`), while the experiment pools the circuits +, -, -, +. The reflection x -> -x makes the pooled axis-phase response even in the advance, so the pooled first-order ratio vanishes and the curvature ratio is -0.018 (QB14), against +0.344 one-sign; the other three classes are unchanged. `analyze --gate-model sign-pooled` recomputes the run's analysis with the pooled ratios
([analysis](../../results/iqm/measurement_sequence_pinching_sign_pooled_analysis.json), replay gate `core-710`); the preregistered analysis file stays as written. The same run, preregistered / sign-pooled:

| qubit | axis ratio | axis ratio, pooled | gate systematic | gate systematic, pooled | departure SE | departure SE, pooled | z | z, pooled | departure verdict | settle verdict | informative |
|---|---|---|---|---|---|---|---|---|---|---|---|
| QB1 | +0.309 | -0.017 | 0.0424 | 0.0405 | 0.0448 | 0.0430 | +0.499 | +0.519 | consistent / consistent | match / match | True / True |
| QB5 | +0.347 | -0.018 | 0.0483 | 0.0462 | 0.0494 | 0.0474 | +0.746 | +0.778 | consistent / consistent | tail_attributed / tail_attributed | True / True |
| QB8 | +0.305 | -0.017 | 0.0422 | 0.0404 | 0.0435 | 0.0417 | +0.721 | +0.751 | consistent / consistent | match / match | True / True |
| QB14 | +0.344 | -0.018 | 0.0483 | 0.0463 | 0.0488 | 0.0469 | +0.854 | +0.890 | consistent / consistent | tail_attributed / tail_attributed | True / True |
| QB17 | +0.342 | -0.018 | 0.0474 | 0.0454 | 0.0484 | 0.0465 | +0.659 | +0.687 | consistent / consistent | match / match | True / True |
| QB19 | +0.338 | -0.018 | 0.0469 | 0.0449 | 0.0479 | 0.0460 | +0.576 | +0.601 | consistent / consistent | match / match | True / True |

Device: pooled departure z +1.649 preregistered, +1.718 sign-pooled; `departs_below` none / none, `exceeds_prediction` none / none; the settle tail reads `attributed` under both (pooled z +4.81, QB14 and QB5), because the tail gap carries no gate-model systematic. The corrected values narrow the departure standard errors by 0.0018 to 0.0020, and no verdict changes. The reach is unchanged: the smallest detectable shifts under the sign-pooled analysis are 0.049 to 0.073 in P0 (table above), which map to eps = 0.0042 to 0.0064 per measurement, or 22 to 31 % of the coherence surviving each measurement. The sibling analyses (the diagnostic and the pre-flight probe) decide on single-sign circuits only (the diagnostic's D4 to D8 and the probe's `unitary-n16-s0p` and `measure-n16-s0p` all play the +1 sign), so the one-sign evaluation is the right one there and their retained analyses do not change.

## Evidence

- Diagnostic job on the QPU (`01a1753f-3b98-7437-9433-83d0b4b87721`, 0.50 credits):
  [run](../../results/iqm/runs/2026-10-25T224718Z-garnet-measurement-sequence-diagnostic-diagnostic/results.json),
  [analysis](../../results/iqm/measurement_sequence_diagnostic_analysis.json), and its
  [design](iqm-garnet-measurement-sequence-diagnostic.md).
- Mock run of this case's circuits (pi/2 pairs at every N, the calibration-only selection; job
  01a17585-dd26-7086-9e63-655882ecc988; all 57 circuits returned every key; compiled schedule 1.30 times the
  QPU-calibrated prediction, the mock's own base and window). It ran under the cases.json digest 918d7bd5, before the
  departure-standard-error floor changed prediction.json; its circuits are byte for byte those of the current case:
  [run](../../results/iqm/runs/2026-10-26T000425Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Mock run of the projected-exclusion form (QB6, QB9, QB13, QB15, QB18, QB20; job 01a1755f-4e86-77ee-81be-7b1de90a3c0a),
  superseded and not replayable by the current script:
  [run](../../results/iqm/runs/2026-10-25T232219Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Mock run of the earlier pair form (pairs at N = 16 only, on QB1, QB5, QB8, QB12, QB14 and QB19; job
  01a17548-7e68-72ab-8a27-38f1b6f3d94f), superseded and not replayable by the current script:
  [run](../../results/iqm/runs/2026-10-25T225725Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Pre-flight probe case: [case](../../results/iqm/cases/measurement-sequence-pinching-probe/cases.json), built by
  `scripts/iqm_measurement_preflight.py`; run as job `01a175ac-522d-73e4-ae3e-7404b2335bf6`, see Results.
- Main run: job `01a175ac-da6c-718e-8efc-438c1bff1c46`, [run](../../results/iqm/runs/2026-10-26T004701Z-garnet-measurement-sequence-pinching-pinching/results.json),
  [analysis](../../results/iqm/measurement_sequence_pinching_analysis.json) and its
  [sign-pooled reanalysis](../../results/iqm/measurement_sequence_pinching_sign_pooled_analysis.json); probe run
  [analysis](../../results/iqm/measurement_sequence_pinching_preflight.json).
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

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
| delay | 1, 2, 4, 8, 16 | `delay` of 1.772 us | 0.0302 | elapsed-time control, descriptive |
| settle | 16 | `measure`, then `delay` of 2.0 us | 0.8914 | readout-tail control for the departure decision |

The unitary rotations compose to one rotation of THETA, so the N = 16 contrast measure minus unitary is the
measurement's own action, ideally 0.8612. The timing probe's 16 x 40 ns increment per layer
(see "Circuits") shows Garnet's compiler kept the sixteen unitary-arm prx pulses separate rather than merging them,
so the null still applies sixteen pulses. The delay arm holds the elapsed time of the measure arm but dephases: idle
time acts as a partial Z measurement, so its P0 rises with N without any measurement. It therefore cannot serve as the
null; it quantifies how much of the measure arm's Zeno effect idle dephasing alone produces.

## Why a noise simulation cannot answer it

The calibration noise model of `scripts/iqm_sim.py` treats a measurement as an ideal projective readout with
assignment errors, so measurement-induced transitions and leakage are absent from every model it builds, and the
mock twin returns random bits. The question concerns the device's readout, so only Garnet answers it.

## Qubits

The six qubits come from the live calibration set by one rule: the six of smallest e01 + e10 among those whose T1 is at
least the set's median (37.96 us), taken in that order, skipping any that shares a cz coupler with one already taken.
No qubit pair of the choice shares a coupler, and the build refuses a calibration that says otherwise. Each qubit
runs the same arm in parallel in every circuit.

| qubit | T1 (us) | T2 Ramsey (us) | e01 | e10 | e01 + e10 | prx error |
|---|---|---|---|---|---|---|
| QB5 | 45.8 | 9.3 | 0.0058 | 0.0306 | 0.0364 | 0.00102 |
| QB7 | 41.8 | 7.8 | 0.0122 | 0.0392 | 0.0514 | 0.00545 |
| QB11 | 47.8 | 12.2 | 0.0130 | 0.0252 | 0.0382 | 0.00113 |
| QB14 | 44.9 | 7.0 | 0.0124 | 0.0124 | 0.0248 | 0.00066 |
| QB17 | 46.3 | 14.1 | 0.0096 | 0.0162 | 0.0258 | 0.00094 |
| QB19 | 59.1 | 7.9 | 0.0376 | 0.0380 | 0.0756 | 0.00092 |

An earlier choice of QB1, QB3, QB7 and QB14 followed from `measure_012`, which the circuit API returns no outcomes
for (see "Leakage readout"); QB3 reads e01 0.124 and e10 0.254 and would misfire active reset.

## Circuits

The job holds 57 circuits. Every circuit, `ro0` and `ro1` included, waits 2.0 us (a `delay`) before its final
`measure`, the rule of the `SETTLE_CYCLES` comment in `scripts/qi_readout_ringdown_cases.py`: photons a preceding
readout leaves in the resonator would otherwise bias the final assignment in the measure arm only, and `ro0` and
`ro1` could not correct that. Relaxation over the wait is affine in z, so `ro0` and `ro1`, which wait as long, absorb it
exactly.

- **Zeno chains, 48.** For each N in (1, 2, 4, 8, 16) the measure group beside the delay group, and at N = 16 the
  unitary and settle groups; each group is four signed circuits in the order +, -, -, +. Each step is
  `prx(sign*THETA/N, 0)` on every qubit, then one joint `measure` with its own key (`m0`, `m1`, ...) in the measure
  and settle arms, one joint `delay` in the delay arm, or nothing in the unitary arm; the settle arm adds a 2.0 us
  `delay` after its measure. Outcomes are recorded and never condition a gate.
- **Readout and T1 series, 9.** `ro0` (the initialized state), `ro1` (`prx(pi)`, the t = 0 point of the series) and
  seven T1 circuits `t1-004` to `t1-150`: `prx(pi)`, a `delay` of 4, 10, 20, 40, 60, 100 or 150 us, the pre-readout
  delay, `measure`. The 100 and 150 us points extend the 0 to 60 us series of the request: with a T1 of 40 to 60 us the
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
([Measure_CustomWaveforms](../notes/iqm/docs/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.md)). Five
single-circuit mock jobs of 100 shots ([case](../../results/iqm/cases/measurement-timing-probe/cases.json)) fix the
compiled schedule. The compiler's estimate per shot, the job's `execution_runtime_estimate_seconds` less the fixed 1.6 s
over 100 shots, was:

| circuit | job | qpu_execution per shot |
|---|---|---|
| `ro0` | `01a1747a-dd17-76ae-abf5-cb2840e5bdbd` | 8.684 us |
| unitary, N = 16 | `01a1747a-74f4-7343-90cf-309ff22ec8aa` | 9.324 us |
| measure, N = 16 | `01a1747a-9d43-72dd-8656-a44458628ca9` | 37.676 us |
| measure, N = 1 | `01a1747a-d133-7756-8fae-5bcfde902635` | 10.496 us |
| delay of 1.024 us, N = 16 | `01a1747a-ab9e-77d1-bc48-4f93ad45b5a8` | 25.708 us |

So a prx layer lasts (9.324 - 8.684)/16 = 40 ns, a mid-circuit measure (37.676 - 9.324)/16 = 1.772 us (N = 1 agrees:
10.496 - 8.684 - 0.040 = 1.772), and the delay probe's 1.024 us comes back exactly. The delay arm idles for 1.772 us
and the models use 1.772 us and 40 ns. These are compiler estimates of garnet:mock under its calibration set
`f04fe114`, not measured durations, and they need not carry to the QPU: its retained idle-schedule job
(`01a1707f-6157-75dc-aca8-6f30e5f0280b`, 24 circuits, 3089 prx layers) estimated 204.76 us per shot against 332 us
from the mock's numbers, a ratio of 0.62. The analysis therefore checks the QPU job's own estimate (see
"Compiled-window check").

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

**p_init sensitivity.** The planning prediction for the N = 16 measure arm moves from 0.898 to 1.056 across p = 0,
0.05, 0.10, 0.15 and 0.20 (per qubit in `prediction.json`), a spread of 0.116 to 0.146 in P0, or 17 to 28 departure
standard errors. The prediction and the corrected estimate live in the same space, the ro0/ro1-normalized z, and the
ro0/ro1 normalization cancels the p dependence of a's term: a z0 / z0 = a. What remains is the relaxation offset
divided by the initial z, b/(1 - 2 p). That offset is not small here: the measure arm spends 16 x 1.81 us = 29 us
relaxing toward |0> at a T1 of 40 to 60 us, so for QB5 a = 0.409 and b = 0.422, and b/(1 - 2 p) grows from 0.422 to
0.703 across the range, 0.28 in z and 0.14 in P0. A corrected value above 1 at p = 0.15 and 0.20 is the quotient by
(1 - 2 p), not a probability. The sensitivity therefore requires measuring q in the job; the T1 series does it without a
heralded circuit, and its uncertainty (0.007 to 0.012 on the equivalent p) propagates into the departure standard
error.

## Shots, billing and max_credits

- **Shots:** 3000 per circuit, one job. Raising them to 3380 would lower the standard errors by 6 % and leave 1.0 s
  below the cancel threshold instead of 1.8 s, so they stay at 3000.
- **Execution model:** over the seven retained active-reset Garnet QPU jobs (`01a16583-43fc-75e5-82b0-5b192921a4c5`,
  `01a16630-b928-72d1-b66e-b7779c623df5`, `01a16631-2b7c-7668-a276-3341e9d17bdd`,
  `01a167ac-58d4-74f0-96fe-9af62e1f1dfe`, `01a167ac-e6f3-711a-a9be-86bb8bfe89f9`,
  `01a167ac-ec22-7645-b50d-74b793ed808d`, `01a1707f-6157-75dc-aca8-6f30e5f0280b`), execution seconds = compiled
  schedule (the record's estimate less 1.6 s) + 0.141 s + 7.967 us per circuit-shot, with residuals of at most 0.162 s;
  runtime exceeded execution by 0.04 to 0.411 s, and billing is `ceil(runtime)` with no fixed 1.6 s term.
- **Prediction:** compiled schedule 5.068 s (the mock's numbers, 1.689 ms per shot over the 57 circuits), plus
  0.141 s plus 57 x 3000 x 7.967 us = 1.362 s gives 6.571 s of execution; the worst-case runtime adds 0.17 s of fit
  residual and 0.42 s of runtime over execution, 7.161 s, billed as 8 s, or 4.00 credits at 0.50 credits/s.
- **max_credits:** 5.00 on `garnet` (10 billed seconds) and 0.00 on `garnet:mock`. `collect` cancels a run within 1.0 s
  of that, at 9.0 s of runtime, so the worst case sits 1.84 s below the cancel threshold. The build refuses less than
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
case's predicted 1.689 ms per shot summed over the circuits, times 3000 shots (5.068 s), and reports the ratio. When
they differ by more than 1 %, it solves the measure window from the QPU total, assuming the mock's per-circuit base and
layer time, and recomputes every prediction at that window and the fitted T1 before any decision, reporting the
planned and the recomputed values. A solved window outside a factor of four of 1.772 us means the assumption fails
(the idle-schedule job above ran at 0.62 of the mock's model), and the planned window stays with the rejection
reported; the per-circuit `runtime_estimates` artifact (`iqm_jobs.py collect` keeps it, with its sha256 in the
analysis) then settles the base, layer and window separately.

## Predicted outcome

Planning values from the live set `be070414` at the calibrated T1 and T2 and p = 0.068 (`prediction.json`). The
standard errors apply the run's estimator, the T1 and q fit and the prx systematic included, to the model's expected counts at 3000 shots.

| qubit | measure P0 at N = 1, 2, 4, 8, 16 (the N = 16 value is the planning departure prediction) | delay P0 at N = 1, 2, 4, 8, 16 | unitary N = 16 | settle N = 16 | contrast | contrast SE | mutation z | departure SE |
|---|---|---|---|---|---|---|---|---|
| QB5 | 0.0713, 0.5401, 0.7064, 0.8486, 0.9486 | 0.0713, 0.1571, 0.2561, 0.4076, 0.6059 | 0.0596 | 0.9902 | 0.8891 | 0.0104 | 37.5 | 0.0071 |
| QB7 | 0.0771, 0.5423, 0.7067, 0.8433, 0.9328 | 0.0771, 0.1786, 0.2913, 0.4545, 0.6509 | 0.0936 | 0.9802 | 0.8392 | 0.0106 | 32.0 | 0.0248 |
| QB11 | 0.0697, 0.5391, 0.7050, 0.8466, 0.9460 | 0.0697, 0.1376, 0.2214, 0.3563, 0.5465 | 0.0562 | 0.9872 | 0.8900 | 0.0104 | 37.6 | 0.0077 |
| QB14 | 0.0719, 0.5406, 0.7073, 0.8502, 0.9513 | 0.0719, 0.1815, 0.2981, 0.4653, 0.6661 | 0.0629 | 0.9927 | 0.8883 | 0.0101 | 38.5 | 0.0060 |
| QB17 | 0.0708, 0.5398, 0.7061, 0.8483, 0.9484 | 0.0708, 0.1304, 0.2073, 0.3343, 0.5201 | 0.0531 | 0.9899 | 0.8954 | 0.0101 | 39.1 | 0.0069 |
| QB19 | 0.0622, 0.5346, 0.6990, 0.8391, 0.9374 | 0.0622, 0.1610, 0.2665, 0.4216, 0.6153 | 0.0610 | 0.9754 | 0.8765 | 0.0112 | 33.7 | 0.0083 |

The model device passes the mutation test by 32 to 39 standard errors. The fitted T1 carries 1.1 to 2.3 us of
standard error (2 to 4 %) and p 0.007 to 0.012. T1 and the divided-by-(1 - 2 p) correction lift the measure arm 0.04 to
0.06 above its ideal 0.8914, so the departure test needs the fitted values; the lift is 6 to 9 departure standard errors on
the five qubits other than QB7 and 1.7 on QB7. Dephasing over 16 steps of 1.81 us against T2 of 7.0 to 14.1 us lifts the
delay arm to 0.52 to 0.67: idle dephasing alone produces 0.47 to 0.60 of the 0.86 Zeno rise, which is why the delay arm
is a control and the unitary arm the null.

**Estimator sweep.** `scripts/iqm_measurement_sequence.py sweep` (the self-test runs its reduced grid) builds raw
`measurements.json` files in the format the mock returned (per circuit and key, 3000 rows of six 0/1 outcomes in locus
order) from a model device's expected per-qubit probabilities, with no random draw: qubit j reads 1 in the shots whose
index i satisfies (i x a_j) mod 3000 < ones, with a_j coprime to 3000, and each mid-circuit key is a per-qubit
Bresenham path whose consecutive-outcome flips match the expected pair count. Each qubit's paths are independent of the
others' by construction, so the construction says nothing about cross-qubit correlation. The real `analyze` path then
runs on each device: readout correction, T1 and q fit, prediction recompute, decisions. One axis moves at a time from
the planning point, then a corner moves all four; the pass rule is |departure z| < 1, settle `match` and a passing
mutation test on every qubit, and no device-level flag.

| device | p | thermal | T1 / calibrated | prx / calibrated | departure z over the six qubits | settle | mutation z (min) | fitted T1 error (max) |
|---|---|---|---|---|---|---|---|---|
| planning | 0.068 | 0 | 1.0 | 1 | -0.01 to +0.02 | match | 32.0 | 8e-4 |
| p = 0 | 0 | 0 | 1.0 | 1 | -0.03 to +0.03 | match | 44.3 | 6e-4 |
| p = 0.15 | 0.15 | 0 | 1.0 | 1 | -0.00 to +0.04 | match | 24.3 | 6e-4 |
| thermal 0.02 | 0.068 | 0.02 | 1.0 | 1 | -0.01 to +0.03 | match | 31.2 | 8e-4 |
| T1 x 0.8 | 0.068 | 0 | 0.8 | 1 | +0.00 to +0.03 | match | 32.1 | 4e-4 |
| T1 x 1.2 | 0.068 | 0 | 1.2 | 1 | -0.03 to +0.02 | match | 31.8 | 8e-4 |
| prx x 2 | 0.068 | 0 | 1.0 | 2 | -0.94 to -0.55 | match | 27.3 | 8e-4 |
| corner | 0.15 | 0.02 | 0.8 | 2 | -0.94 to -0.44 | match | 21.6 | 5e-4 |

The thermal row passes because the model takes q = z_eq/(1 - 2 p) from the T1 series rather than a p with a cold idle
qubit. The prx rows pass because the standard errors carry the prx systematic: without it QB7 reads -4.4 at prx x 2 and
-3.4 at the corner, since its calibrated prx error is 0.0054 against 0.0007 to 0.0011 elsewhere. QB7's departure
standard error is 0.025 where the others' is 0.006 to 0.008, so the departure test is weakest on QB7. A prx error twice
the calibrated one on every qubit pools to a device z of about -1.5, below the device rule's threshold.

**Cross-check.** `scripts/iqm_measurement_sequence_aer_check.py run CASE_DIR --calibration-dir DIR` runs every arm and N
of every qubit through an independent Aer density-matrix simulation built on `scripts/iqm_sim.py`'s calibration noise
model (prx depolarizing error per qubit) with thermal relaxation on every wait (`iqm_signed_probe.relaxation`), the
pinch as a Kraus channel and the live set's T1 and T2, from |0>. Against the Bloch model with the prx error the largest
gap over the 72 points is 6e-15 in P0. Against the model without it, as first written, the gap reached 0.024 in P0 on
QB7's measure arm (4.6 departure standard errors) and 0.037 on its unitary arm: the Bloch model omitted the per-prx
depolarizing error, which is now an input (`prx_p`) of every table. The check verifies the model's algebra and time
accounting, not the estimator, which the sweep covers.

## Window sensitivity

The planned measure window of 1.772 us is a garnet:mock compiler estimate and need not hold on the QPU. The planning
prediction at the N = 16 measure arm and the settle arm over the window, per qubit (`prediction.json`,
`window_sensitivity`):

| qubit | measure P0 at 1.0 / 1.4 / 1.772 / 2.0 us | settle P0 at 1.0 / 1.772 / 2.0 us | dP0/dw measure, settle (per us) | shift 1.0 to 1.772 us, measure (departure SE) |
|---|---|---|---|---|
| QB5 | 0.9254 / 0.9380 / 0.9486 / 0.9545 | 0.9767 / 0.9902 / 0.9937 | 0.0269, 0.0158 | 0.0232 (3.3) |
| QB7 | 0.9060 / 0.9207 / 0.9328 / 0.9397 | 0.9649 / 0.9802 / 0.9841 | 0.0310, 0.0178 | 0.0268 (1.1) |
| QB11 | 0.9233 / 0.9356 / 0.9460 / 0.9518 | 0.9737 / 0.9872 / 0.9907 | 0.0264, 0.0159 | 0.0226 (2.9) |
| QB14 | 0.9280 / 0.9407 / 0.9513 / 0.9572 | 0.9793 / 0.9927 / 0.9962 | 0.0270, 0.0157 | 0.0233 (3.8) |
| QB17 | 0.9254 / 0.9380 / 0.9484 / 0.9543 | 0.9764 / 0.9899 / 0.9934 | 0.0267, 0.0158 | 0.0230 (3.3) |
| QB19 | 0.9179 / 0.9284 / 0.9374 / 0.9426 | 0.9626 / 0.9754 / 0.9788 | 0.0233, 0.0153 | 0.0196 (2.3) |

A window 0.77 us shorter than planned lowers the measure-arm prediction by 2.3 to 3.8 departure standard errors on five
qubits (1.1 on QB7); the shift reaches 3 standard errors on three qubits and 2.9 on a fourth, so a wrong window reads as
a departure.
The compiled-window check below detects a window error only through the job's total, and the rejection branch leaves
the planned window in place; two single-circuit QPU window probes would fix it directly.

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

- Failed mock job of the first, 54-circuit form of this case:
  [run](../../results/iqm/runs/2026-10-25T190614Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Mock run of the second, 50-circuit form (job 01a17484):
  [run](../../results/iqm/runs/2026-10-25T192310Z-garnet_mock-measurement-sequence-pinching-pinching/results.json) and
  [its analysis](../../results/iqm/measurement_sequence_pinching_mock_analysis.json), produced by an earlier revision of
  the script; the circuits it ran differ from this case's, so the current script cannot replay it.
- Mock run of the hardened 57-circuit form (job 01a174a7), compiled schedule ratio 1.0000:
  [run](../../results/iqm/runs/2026-10-25T200157Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Timing probe case and its five mock runs:
  [case](../../results/iqm/cases/measurement-timing-probe/cases.json), runs
  `results/iqm/runs/2026-10-25T1912*Z-garnet_mock-measurement-timing-probe-*`.
- `measure_012` probe case and its mock run:
  [case](../../results/iqm/cases/measure-012-probe/cases.json),
  [run](../../results/iqm/runs/2026-10-25T190754Z-garnet_mock-measure-012-probe-probe/results.json).

## Sequence

1. Rebuild the case against the live calibration set and run `check`.
2. Run the job on `garnet:mock` at 0.00 credits: it settles whether the mock accepts the circuits and returns the
   runtime estimate and, through `collect`, the `runtime_estimates` artifact. Mock outcomes never enter the decisions;
   `analyze --mock` exercises the pipeline on them.
3. Approval of this written case, then `submit` on `garnet` with `--approved-cases-sha256` and `--max-credits 5.0`,
   and `collect` right after.
4. `analyze RUN_DIR --out FILE` writes the decisions.

# IQM Garnet measurement-sequence pinching

This case tests whether a Garnet mid-circuit measurement acts as ideal pinching, the nonselective projective
measurement in Z, on QB1, QB3, QB7 and QB14. The case directory is
[results/iqm/cases/measurement-sequence-pinching](../../results/iqm/cases/measurement-sequence-pinching/cases.json),
built by `scripts/iqm_measurement_sequence.py build DIR [--calibration-dir DIR]`. The script's docstring states the
preregistered decisions, and `prediction.json`, bound by digest into `cases.json`, holds the model the margins below
come from.

calibration set: `be070414-7624-4943-ac7e-1e2678f05684` (created 2026-10-25T16:45:12Z, read 2026-10-25); QB3 reads e01 0.124 and e10 0.254 under it, so its readout-corrected endpoints carry about twice the standard error of the other three qubits

The built case pins the set in `calibration/excerpt.json`, built from that live set. Garnet refuses a job pinned to a
retired set, so the orchestrator rebuilds the case with `--calibration-dir` pointing at a directory holding the then
live `set.json`, `metrics.json` and `dynamic-quantum-architecture.json` before submission.

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
measurement's own action, ideally 0.8612. The delay arm holds the elapsed time of the measure arm but dephases: idle
time acts as a partial Z measurement, so its P0 rises with N without any measurement. It therefore cannot serve as the
null, and it quantifies how much of the measure arm's Zeno effect idle dephasing alone produces. Measurement-induced
transitions lower the measure arm below its ideal-projective prediction.

## Why a noise simulation cannot answer it

The calibration noise model of `scripts/iqm_sim.py` treats a measurement as an ideal projective readout with
assignment errors, so measurement-induced transitions and leakage are absent from every model it builds, and the
mock twin returns random bits. The question concerns the device's readout, so only Garnet answers it.

## Qubits

QB1, QB3, QB7 and QB14 run the same arm in parallel in every circuit. The retained architecture lists no CZ locus
among them (QB1: QB2, QB4; QB3: QB4, QB8; QB7: QB6, QB12; QB14: QB13, QB15, QB18, QB9), and the build refuses a
calibration that lists one.

## Circuits

The job holds 50 circuits.

- **Zeno chains, 48.** For each N in (1, 2, 4, 8, 16) the measure group beside the delay group, and at N = 16 the
  unitary and settle groups; each group is four signed circuits in the order +, -, -, +. Each step is `prx(sign*THETA/N, 0)` on
  every qubit, then one joint `measure` with its own key (`m0`, `m1`, ...) in the measure arm, one joint `delay` in
  the delay arm, or nothing in the unitary arm, and a final `measure` with key `f`. Outcomes are recorded and never
  condition a gate.
- **Readout calibration, 2.** `ro0` and `ro1` (a pi pulse) with `measure` on all four qubits. The pi pulse of `ro1`
  carries its own over-rotation, which the correction absorbs into the readout scale.

**Idle operation.** The circuit-job body takes a native `delay` operation whose `duration` is in seconds, at least
that long and rounded up to hardware granularity
([operations table and Delay](../notes/iqm/docs/iqm-client/api/iqm.iqm_client.models.md); every Target lists `delay`,
[os-4.7.md](../notes/iqm/os-4.7.md)). Garnet's dynamic quantum architecture lists no `delay` gate and the OpenAPI
operation name is a free string, so acceptance on the QPU is unverified; the garnet:mock run settles it, and a
rejection removes the delay arm and leaves the unitary null and the departure test unchanged.

**Measure window.** The calibration's probe pulse lasts 364, 444, 556 and 420 ns on QB1, QB3, QB7 and QB14
(`gates.measure.constant.QBn.duration`, set `9069c4ef`), and `acquisition_delay + integration_length` gives 1.024 us
(465.5 ns + 556 ns on QB7, rounded up to the 4 ns granularity). Neither is the compiled window: a measure runs as a
ReadoutTrigger whose duration follows the acquisition
([Measure_CustomWaveforms](../notes/iqm/docs/iqm-pulse/api/iqm.pulse.gates.measure.Measure_CustomWaveforms.md)).
Five single-circuit mock jobs of 100 shots on the four qubits
([case](../../results/iqm/cases/measurement-timing-probe/cases.json)) fix the compiled schedule. The compiler's
estimate per shot, the job's `execution_runtime_estimate_seconds` less the fixed 1.6 s over 100 shots, was:

| circuit | job | qpu_execution per shot |
|---|---|---|
| `ro0` | `01a1747a-dd17-76ae-abf5-cb2840e5bdbd` | 8.684 us |
| unitary, N = 16 | `01a1747a-74f4-7343-90cf-309ff22ec8aa` | 9.324 us |
| measure, N = 16 | `01a1747a-9d43-72dd-8656-a44458628ca9` | 37.676 us |
| measure, N = 1 | `01a1747a-d133-7756-8fae-5bcfde902635` | 10.496 us |
| delay of 1.024 us, N = 16 | `01a1747a-ab9e-77d1-bc48-4f93ad45b5a8` | 25.708 us |

So a prx layer lasts (9.324 - 8.684)/16 = 40 ns, a mid-circuit measure (37.676 - 9.324)/16 = 1.772 us (N = 1 agrees:
10.496 - 8.684 - 0.040 = 1.772), and the delay probe's 1.024 us comes back exactly. The delay arm therefore idles for
1.772 us, which the compiled measure window equals, and the departure prediction and the delay model use 1.772 us and
40 ns. These are compiler estimates of garnet:mock under its calibration set `f04fe114`, not measured durations; the
analysis compares the QPU job's own estimate with the case's predicted schedule.

**Elapsed time.** The delay arm matches the measure arm's elapsed time to the precision of the mock's compiler
estimate.

## Initialization

The job runs one active-reset cycle without heralding. All-zeros heralding over four qubits discards about a
quarter of the shots, and passive reset takes 316 us per shot against 37.5 us ([timing pilot](iqm-garnet-timing-pilot.md)).
Rotations and pinching act linearly on the Bloch z, so an initialization excitation p scales the final z by
(1 - 2p), the factor `ro0` and `ro1` measure; the readout correction removes it exactly. T1 relaxation toward |0> is
the non-unital residue and enters at second order.

## Shots, billing and max_credits

- **Shots:** 2400 per circuit, one job (2700 would exceed the 2 s headroom below the ceiling once the settle arm is added).
- **Per-shot schedule assumed:** 2.5709 ms summed over the 50 circuits. Each circuit costs the 37.5 us of an
  unheralded active-reset shot, measured on QB1 by the reset and billing pilot ([timing pilot](iqm-garnet-timing-pilot.md)),
  plus 40 ns per rotation layer and 1.772 us per mid-circuit measure or delay.
- **Expected execution:** 6.170 s of shots plus the fixed 1.6 s per job gives 7.770 s, billed as 8 s, or 4.00
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
  a rotation, an ideal pinch, then T1 relaxation toward |0> over the 40 ns rotation layer and the 1.772 us measure window, and
  readout through the calibrated errors. T2 does not enter it, because the state is diagonal after every measurement.
  Its inputs are each qubit's calibrated T1, the window, the rotation time, e01 and e10, and the assumed 6.8 %
  initialization excitation.

Reported without a decision, as support for the departure decision: the settle arm's readout tail check (next
section). Also reported without a decision: the delay arm's measured and modeled (T1 and T2) P0 per N with their difference, and the
measured delay minus unitary difference at N = 16 against the model's; the per-N measure-arm deficit against the
ideal; the fit of P0(N) = (1 + ((1 - 2 eps) cos(THETA/N))^N)/2 for eps per qubit (it ignores relaxation, so it
absorbs T1 into eps); the transition rate between consecutive mid-circuit outcomes against sin(THETA/(2N))^2 (about
0.008 at N = 16, below the 1 to 2 % readout error, so reported raw).

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
reproduces the measure arm's readout-corrected N = 16 P0, predicts the settle arm's P0 at that loss, and reports the
settle arm's measured P0 minus that prediction with its standard error (`settle_n16.tail_gap`). When a qubit departs,
a gap within 3 standard errors of zero is a match that excludes a readout tail as the cause; a gap at least 3
standard errors above zero attributes part of the departure to the tail. The raw settle minus measure difference is
reported beside it. The arm decides nothing.

## Predicted outcome

Model values from the live set `be070414` (`prediction.json`). Measure-arm P0 at N = 1, 2, 4, 8, 16 is the departure
prediction at N = 16; the delay arm uses T1 and T2; the unitary arm is the N = 16 mutation null.

| qubit | measure P0 (N = 1, 2, 4, 8, 16) | delay P0 (N = 1, 2, 4, 8, 16) | unitary P0 (N = 16) | settle P0 (N = 16) | contrast | contrast SE | departure SE | delay minus unitary |
|---|---|---|---|---|---|---|---|---|
| QB1 | 0.0920, 0.5503, 0.7152, 0.8494, 0.9337 | 0.0920, 0.1721, 0.2739, 0.4296, 0.6285 | 0.0538 | 0.9576 | 0.8801 | 0.0099 | 0.0072 | 0.5747 |
| QB3 | 0.1016, 0.5557, 0.7215, 0.8554, 0.9382 | 0.1016, 0.2087, 0.3332, 0.5086, 0.7076 | 0.0616 | 0.9624 | 0.8767 | 0.0229 | 0.0153 | 0.6460 |
| QB7 | 0.0713, 0.5386, 0.7013, 0.8357, 0.9223 | 0.0713, 0.1709, 0.2801, 0.4387, 0.6306 | 0.0560 | 0.9439 | 0.8663 | 0.0107 | 0.0075 | 0.5745 |
| QB14 | 0.0685, 0.5370, 0.6994, 0.8337, 0.9206 | 0.0685, 0.1774, 0.2921, 0.4543, 0.6444 | 0.0580 | 0.9416 | 0.8625 | 0.0099 | 0.0074 | 0.5864 |

The model device passes the mutation test by 16.5 (QB3, whose readout errors double its standard errors) to 40.7
standard errors. Dephasing over 16 steps of 1.81 us against T2 of 7.0 to 9.9 us lifts the delay arm to 0.63 to 0.71:
idle dephasing alone produces about 0.57 to 0.65 of the 0.86 Zeno rise, which is why the delay arm is a control and
the unitary arm the null. T1 lifts the measure arm 0.029 to 0.047 above its ideal 0.8914, and the departure test
compares the run with that raised prediction, so a real transition rate is not hidden by relaxation.

The QPU job's `analyze` output carries the compiled-schedule check: the job's estimated qpu_execution (estimate less
1.6 s) against the case's predicted 1.1301 ms per shot summed over the circuits, times 2400 shots (2.712 s), and their
ratio.

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

- Failed mock job of the earlier 54-circuit form of this case:
  [run](../../results/iqm/runs/2026-10-25T190614Z-garnet_mock-measurement-sequence-pinching-pinching/results.json).
- Timing probe case and its five mock runs:
  [case](../../results/iqm/cases/measurement-timing-probe/cases.json), runs
  `results/iqm/runs/2026-10-25T1912*Z-garnet_mock-measurement-timing-probe-*`.
- `measure_012` probe case and its mock run:
  [case](../../results/iqm/cases/measure-012-probe/cases.json),
  [run](../../results/iqm/runs/2026-10-25T190754Z-garnet_mock-measure-012-probe-probe/results.json).

## Sequence

1. Rebuild the case against the live calibration set and run `check`.
2. Run the job on `garnet:mock` at 0.00 credits: it settles whether the mock accepts `delay` and
   returns the runtime estimate. Mock outcomes never enter the analysis.
3. The five timing-probe mock jobs above are retained; rebuilt jobs of the case keep the compiler's
   `runtime_estimates` artifact (`iqm_jobs.py collect`) for the comparison.
4. Approval of this written case, then `submit` on `garnet` with `--approved-cases-sha256` and `--max-credits 5.0`,
   and `collect` right after.
5. `analyze RUN_DIR --out FILE` writes the decisions.

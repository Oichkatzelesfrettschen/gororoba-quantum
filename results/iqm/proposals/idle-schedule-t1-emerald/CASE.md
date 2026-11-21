# IQM Emerald idle schedule with delay-measured T1

Status: written case awaiting review and the owner's approval of the Emerald submission; the `emerald:mock` check ran
(job `01a1ff21`, run `results/iqm/runs/2026-11-21T172247Z-emerald_mock-idle-schedule-t1-emerald-probe`, approval
"owner AskUserQuestion 2026-11-21T17:09Z: Build successor (Recommended), check against emerald:mock (free)").

Successor of [idle-schedule-train-readout-emerald](../idle-schedule-train-readout-emerald/CASE.md). That case's H2 asks
whether the decay beyond the ASAP prediction is one per-pulse timing gap g common to the qubits or a T1 calibration
error, and states that its own circuits cannot separate the two: r_i = d / (d + g_i) x T1_true_i / T1_cal_i fits a
common g and a common T1 bias alike. This case adds the measurement that separates them, a T1 read by delay circuits in
the same job, and keeps the twelve circuits of the predecessor byte for byte.

Backend `iqm:emerald` (Crystal 54, pay-as-you-go 0.75 credits per second). Calibration set
`ecec1d0a-1529-4c90-9b02-d1b30ddaa2e3`, read live on 2026-11-21 (`calibration/`); the job pins it, and a retired set
needs a rebuild with `--live`, which changes the approved `cases.json` digest.

## Circuits

Sixteen circuits at 4000 shots, one active-reset cycle, heralding `none`, each read by one joint `measure` over QB5,
QB10, QB14, QB18, QB20, QB24, QB26, QB30, QB34, QB37, QB42 and QB44.

- The predecessor's twelve: six idle layouts (train QB20 or QB26 at 0, 500 or 1000 `prx(pi)`, every uncoupled
  measured qubit pulsed once) and six parallel readout and train circuits.
- Four delay circuits `t1-8us`, `t1-16us`, `t1-32us`, `t1-64us`: `prx(pi)` on all twelve, one `delay`
  instruction on all twelve (IQM's circuit delay, duration in seconds, rounded up to the hardware's step; documented in
  the IQM client's instruction model), then the joint measure.

A pulse train waits N (d + g) for the 24 ns prx length d and a per-pulse gap g. IQM documents a delay as at least its
requested duration, rounded up to the hardware step, and possibly longer depending on the other operations. If a
requested duration t is realized as a t + b, the offset b enters the fitted amplitude and not the slope, so the delay
fit gives T1 independently of g; the scale a is assumed to be 1. A scale a != 1 makes the fit read T1 / a and moves g
with it, and no reading of this job detects a, since the decay stays a single exponential and both train lengths see
the same a. T1 below is therefore T1 per requested delay second, and H2 is conditional on a = 1. The playlist repeats all sixteen circuits 4000 times, so the T1 and the trains are read over the
same minutes: IQM documents that a playlist's segments run in order and the whole sequence repeats once per shot,
with an undefined delay between chunks when a playlist exceeds memory (`docs/notes/iqm/docs/iqm-pulse/concepts.md`,
the repository's mirror of iqm-pulse "Concepts and classes"), and the mock estimate reports `playlist_repeats` 4000.

## Pre-flight

1. Hypothesis. H1 (unchanged): Emerald schedules ASAP. H2: the decay of the 1000-pulse arms beyond the delay-measured
   T1 is one gap g common to the qubits. Gated on H1; under ALAP, mixed or unresolved schedules H2 reports
   `unidentifiable`.
2. Quantity. Per qubit, T1 from a weighted log-linear fit of the readout-corrected excited population of the four
   delay circuits (points at least 3 standard errors above zero; at least 3 points). Per pulsed qubit, the train's decay
   rate k from its 1000-pulse arm (layouts pooled by inverse variance), and g = d (k / k_T1 - 1) with k_T1 = 1 / T1. A
   qubit enters H2 only when its delay fit's chi-square survival is at least 0.001, its bare readout pair
   (par-ro0, par-ro1) leaves a positive contrast, and every train arm gives a decay rate. H2 corrects readout through
   that pair and not through the parallel train fit, whose over-rotation model failed on 7 of 20 Garnet qubits
   (`results/iqm/idle_schedule_probe_analysis.json`) without invalidating their readout. The preregistered test covers all twelve pulsed qubits: one excluded qubit makes H2 `unidentifiable`, and the
   analysis names it.
3. Decision and falsifier. A common g is rejected when the chi-square of the qubits' g about their weighted mean has
   survival below 0.01 (11 degrees of freedom with all twelve qubits, chi-square above 24.7): `per-qubit`. Otherwise
   `common`, reporting the mean and its standard error. The 500-pulse arms repeat the estimate on the same qubits; a
   mean that differs from the 1000-pulse mean by more than 3 combined standard errors falsifies the stationary gap model
   and is recorded as a finding. The combined error ignores the T1 and readout the two means share; the calibration
   study below measures the test's false-alarm rate. The ratio T1_delay / T1_cal per qubit (`over_calibrated`) is
   descriptive: it reads the calibration copy's error per requested delay second.
4. Predicted outcome and power. The calibration study
   ([calibration-study.json](calibration-study.json), `iqm_idle_schedule_probe.py study`, seed 50182 from
   `docs/evidence/anu_qrng/draw-2026-11-21T184244Z.json` index 0) runs the estimator on a model device built from this
   case's calibration and circuits, at expected counts and in 400 binomial replicates at 4000 shots per planted gap.
   With no gap the expected counts read -0.02 ns and the replicates -0.06 ns on average (spread 0.23 ns); with a
   planted 14 ns gap, 13.96 ns and 13.92 ns (spread 0.31 ns). The mean +- one standard error covers the truth in 0.67
   and 0.69 of the replicates, the per-qubit gap and T1 z-scores have standard deviations 0.99 to 1.04, the common-gap
   test rejects a true common gap in 0.50 and 0.75 percent of the replicates (nominal 1 percent), the stationarity test
   raised no false alarm, and 0.5 percent of the replicates read `unidentifiable` through an excluded qubit. The
   readout correction's own uncertainty is left out of the standard errors, and the replicates show it costs no
   coverage at these shots. The model device draws each qubit's counts independently, so a correlation between the
   twelve qubits of one joint shot (readout crosstalk) is outside the study. The Garnet carry-over (r = 0.53 at 16 ns, g = 14 ns) would read about 40 standard errors
   from zero; a pure T1 calibration bias reads g near zero with T1_delay / T1_cal near the predecessor's r.
5. What each result changes. `common` g: the effective pulse time d + g sets the pulse-count budgets of the pinching
   and QET cases on Emerald, now with a mechanism (timing) and a measured T1. g near zero with T1_delay below T1_cal:
   the excess is the calibration copy's T1, and later cases price with a fresh T1 read. `per-qubit`: the gap varies by
   qubit; later cases use per-qubit d + g_i from this run. Stationarity failure: the decay model is reopened first.

## Why a simulation cannot answer it

The schedule, the per-pulse occupation of the control stack and the qubits' present T1 are properties of the Emerald
chip at the time of the run. `iqm_sim` takes all three as inputs, and `emerald:mock` runs a different chip and
returns random bits.

## Cost

IQM bills a job's compilation plus execution seconds, rounded up to whole seconds, at the computer's price; there is no
charge per shot, circuit or job beyond those seconds (`scripts/iqm_jobs.py`, `ceiling_breach`). The mock estimate
of this job is 3.12 s of execution (`raw/runtime_estimates.json`: sweep 3.121 s, QPU 1.521 s), against 2.50 s for the
predecessor's twelve circuits. The predecessor's Emerald job (`01a1f811`, ceiling-cancelled at no charge) compiled for
1.80 s and was still executing after 3.66 s, so its execution ran at least 1.46 times its mock estimate. If that factor
repeats, this job needs about 4.6 s of execution and 6.4 s in all: 7 billed seconds, 5.25 credits; one unfinished run
bounds the factor from below only. The builder's `expected_seconds` (3.168 s) prices shots with Garnet's 37.5 us per
active-reset shot and is a planning figure; the mock estimate is the better one. Requested approval: backend
`iqm:emerald`, 16 circuits x 4000 shots, active reset, ceiling 12.00 credits (16 billed seconds; `collect` cancels at
15.0 s of runtime, which covers an execution of 4.2 times the mock estimate after 1.8 s of compilation). A cancelled
job bills nothing, as `01a1f811` shows, and returns no data. Balance read 2026-11-21: 29.00 credits, expiring
2026-12-01.

## Retained measurements

- Predecessor Emerald job `01a1f811` (2026-11-20): ceiling-cancelled at 5.30 s of runtime under a 4.50-credit
  ceiling, billed 0 (`results/iqm/runs/2026-11-20T082726Z-emerald-idle-schedule-train-readout-emerald-probe`).
- This case's mock job `01a1ff21` (2026-11-21): completed all sixteen circuits at 4000 shots, so the mock station
  accepted the `delay` instruction; the run record names no station-control version (the retained platform notes,
  `docs/notes/iqm/os-4.7.md`, give 50.0.0, which the live computer listing also reports for Emerald). Its bits are
  random and are not analyzed.
- Garnet idle-schedule job `01a1707f`: all 68 pulsed arms ASAP, apparent T1 a median 0.53 of the calibrated value.

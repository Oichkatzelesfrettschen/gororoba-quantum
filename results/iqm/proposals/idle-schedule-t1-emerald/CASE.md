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

A pulse train waits N (d + g) for the 24 ns prx length d and a per-pulse gap g. A delay waits its duration plus one
offset shared by every delay circuit, which enters the fitted amplitude and not the slope, so the delay fit gives T1
independently of g. The playlist repeats all sixteen circuits 4000 times, so the T1 and the trains are read over the
same minutes.

## Pre-flight

1. Hypothesis. H1 (unchanged): Emerald schedules ASAP. H2: the decay of the 1000-pulse arms beyond the delay-measured
   T1 is one gap g common to the qubits. Gated on H1; under ALAP, mixed or unresolved schedules H2 reports
   `unidentifiable`.
2. Quantity. Per qubit, T1 from a weighted log-linear fit of the readout-corrected excited population of the four
   delay circuits (points at least 3 standard errors above zero; at least 3 points). Per pulsed qubit, the train's decay
   rate k from its 1000-pulse arm (layouts pooled by inverse variance), and g = d (k T1 - 1).
3. Decision and falsifier. A common g is rejected when the chi-square of the qubits' g about their weighted mean has
   survival below 0.01 (11 degrees of freedom, chi-square above 24.7): `per-qubit`. Otherwise `common`, reporting
   the mean and its standard error. The 500-pulse arms repeat the estimate; a mean that differs from the 1000-pulse mean
   by more than 3 combined standard errors falsifies the stationary gap model and is recorded as a finding. The ratio
   T1_delay / T1_cal per qubit is descriptive: it reads the calibration copy's error directly.
4. Predicted outcome and power (model device on this calibration, `scripts/iqm_idle_schedule_probe.py`): with no gap
   the estimator reads -0.52 +- 0.22 ns (the model's own offset from the pulsed qubit's first prx and the measure
   alignment), `common`; with a planted 14 ns gap it reads 13.74 +- 0.33 ns, `common`. Per-qubit g carries 0.7 to
   1.5 ns of shot noise, and each T1 2 to 3 percent. The Garnet carry-over (r = 0.53 at 16 ns, g = 14 ns) would read
   about 40 standard errors from zero; a pure T1 calibration bias reads g near zero with T1_delay / T1_cal near the
   predecessor's r.
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
1.80 s and was still executing after 3.66 s, so Emerald's execution ran at least 1.46 times the mock estimate. Scaled
the same way this job needs at least 4.6 s of execution and 6.4 s in all: at least 7 billed seconds, 5.25 credits,
and about 6.75 credits at 9 s. Requested approval: backend `iqm:emerald`, 16 circuits x 4000 shots, active reset,
ceiling 9.00 credits (12 billed seconds; `collect` cancels at 11.0 s of runtime). Balance read 2026-11-21: 29.00
credits, expiring 2026-12-01.

## Retained measurements

- Predecessor Emerald job `01a1f811` (2026-11-20): ceiling-cancelled at 5.30 s of runtime under a 4.50-credit
  ceiling, billed 0 (`results/iqm/runs/2026-11-20T082726Z-emerald-idle-schedule-train-readout-emerald-probe`).
- This case's mock job `01a1ff21` (2026-11-21): completed, `delay` accepted by the Emerald mock station
  (station control 50.0.0, the version Emerald reports), random bits not analyzed.
- Garnet idle-schedule job `01a1707f`: all 68 pulsed arms ASAP, apparent T1 a median 0.53 of the calibrated value.

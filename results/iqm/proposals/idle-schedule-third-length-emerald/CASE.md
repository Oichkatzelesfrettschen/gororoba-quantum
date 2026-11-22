# IQM Emerald idle trains at a third length

Status: written case awaiting review and the owner's approval of the Emerald submission. Nothing has been sent to
`iqm:emerald` or `emerald:mock`, and no IQM API call, calibration read included, was made in building it; the build
reads the calibration copy of the predecessor case.

Successor of [idle-schedule-t1-emerald](../idle-schedule-t1-emerald/CASE.md), whose result
([note](../../../../docs/notes/iqm/emerald-idle-schedule-t1-result.md)) leaves open the hypothesis that the per-pulse
gap of an idle train follows g(N) = 21.4 ns + 5.84 us / N. The line passes exactly through the eleven-qubit means at
500 pulses (33.06 +- 0.58 ns) and 1000 pulses (27.21 +- 0.47 ns), so those two points cannot test it. This case reads
trains of 250 and 2000 pulses, which the line predicts, and repeats the 500 and 1000 pulse trains in the same job as
anchors.

Backend `iqm:emerald` (Crystal 54, pay-as-you-go 0.75 credits per second). The build is
`results/iqm/cases/idle-schedule-third-length-emerald/`, made by
`scripts/iqm_idle_schedule_probe.py build --qc emerald-third` from the predecessor's calibration copy (set
`ecec1d0a-1529-4c90-9b02-d1b30ddaa2e3`, read 2026-11-21). The job pins that set; a retired set fails the job at
compilation, and a rebuild with `--live` (a calibration read, which needs its own approval step) changes the approved
`cases.json` digest.

## What it measures

The decay rate of one pi pulse's excited population on each qubit that shares no coupler with a train qubit, while the
train qubit runs N pi pulses, and from it the per-pulse gap g beyond the nominal 24 ns prx length, with the estimator
of the predecessor unchanged: the delay-measured T1 of the same job, the readout pair, and
g = d (k / k_T1 - 1) (`gap_test`). Two things are new. The train lengths are 250 and 2000 pulses
(`EMERALD_THIRD.pulses`), and `h3_line` (`line_test`) decides the line against them.

## Circuits

Twenty circuits at 4000 shots, one active-reset cycle, heralding `none`, each read by one joint `measure` over QB5,
QB10, QB14, QB18, QB20, QB24, QB26, QB30, QB34, QB37, QB42 and QB44. The sixteen circuits of the predecessor are kept
byte for byte (`third_length_self_test` compares them), and four are added: `idle-QB20-250`, `idle-QB26-250`,
`idle-QB20-2000` and `idle-QB26-2000`. The 500 and 1000 pulse trains already in the job are the anchors, so no
train circuit changed to fit them. The estimator needs the delay circuits `t1-8us` to `t1-64us`, the readout pair
`par-ro0`, `par-ro1` and the four `par-amp` circuits that `evaluate` fits for every qubit, and they stay.

QB24 is measured with the cohort: it passes the delay-fit gate by the widest margin of the twelve (chi-square 0.36 on
2 degrees of freedom, T1 63.0 +- 1.5 us) and reads 30.5 +- 1.7 ns at 500 pulses and 25.8 +- 1.4 ns at 1000.

## Why a simulation cannot answer it

The gap is the chip's realized schedule and control-stack timing, which `iqm_sim` takes as an input, not an output,
and `emerald:mock` runs a different chip and returns random bits. The case asks whether one measured quantity keeps
a functional form across train lengths on the physical device.

## Pre-flight

1. Hypothesis (the note's first open hypothesis): the gap of a train of N pulses is g(N) = a + b / N with
   a = 21.37 ns and b = 5.842 us. Falsifier: a subject's gap at 250 or 2000 pulses more than three combined standard
   errors from the line.
2. Quantity. Per length N and subject, the inverse-variance mean of the subject's per-qubit gaps (`pooled`, the
   estimator the retained means used). Subjects: `cohort`, the eleven qubits of the retained means (QB44 excluded, as
   there), and `QB24`. The line through each subject's own 500 and 1000 pulse gaps is written into
   `prediction.json` (`line`, built from `results/iqm/idle_schedule_t1_emerald_analysis.json`, sha256
   `f69b9c1d...b210`).
3. Predictions, written before any run (nanoseconds; the standard error is the line's, from the two retained points):

   | subject | 250 pulses | 2000 pulses |
   |---|---|---|
   | cohort | 44.74 +- 1.97 | 24.29 +- 0.77 |
   | QB24 | 40.04 +- 5.83 | 23.40 +- 2.30 |

4. Decision rule (`line_test`, `h3_line` of the analysis). For each subject and length, z is the observed mean minus
   the reference over the root sum of squares of the observed and reference standard errors; the runs are independent.
   - `unidentifiable`: a named qubit lacks a gap at some length (schedule not ASAP, or a qubit without a usable delay
     fit or readout contrast).
   - `anchors-moved`: the cohort's gap at 500 or 1000 pulses lies more than 3 combined standard errors from its
     retained value. The device then differs from the one that fixed the line, and the line stays untested.
   - `off-line`: otherwise, any subject at 250 or 2000 pulses has |z| above 3. This falsifies the line.
   - `on-line`: otherwise. The line survives at two lengths; it is not proved.
   The `stationarity` field of `h2_gap` compares the shortest and longest trains and is expected to read
   `falsified` under the line (its mean falls from 44.7 to 24.3 ns); it decides nothing here. QB44 may again fail its
   delay fit and make `h2_gap` read `unidentifiable`; `h3_line` does not depend on QB44.
5. Power, arithmetic at expected counts with no random draw (`power`, `power.json` beside this file). A model
   device whose gap follows the line gives the cohort mean a standard error of 0.75 ns at 250 pulses and 0.42 ns at
   2000 pulses at 4000 shots. Against the line's own 1.97 and 0.77 ns the combined errors are 2.11 and 0.88 ns, so a
   deviation of 6.3 ns (14 percent of the prediction) at 250 and 2.6 ns (11 percent) at 2000 sits three combined
   errors out. Doubling the shots to 8000 lowers those to 6.1 and 2.5 ns, 3 to 6 percent, because the two retained
   points dominate the combined error, and it doubles the cost, so 4000 shots stay, the retained case's count and the
   estimator's. QB24 alone resolves 18.8 ns at 250 and 7.9 ns at 2000 (its retained points carry 1.4 to 1.7 ns each),
   so the QB24 subject can reject a gross departure and the cohort carries the test. For scale, a constant gap equal
   to the 1000 pulse mean (27.2 ns) sits 8 combined errors from the line at 250 pulses.
6. Limits. The combined error leaves out the T1 and readout error each qubit's two lengths share within this job
   and any change of the chip between the retained run and this one; the anchors check the second, and the first
   moves both lengths of a qubit together. The model device draws each qubit's counts independently, so correlation
   among the twelve qubits of one joint shot is outside the power arithmetic. The scale of the delay instruction
   (a = 1) stays assumed, as in the predecessor.
7. What each result changes. `on-line`: the term b / N is a per-train overhead of the control stack, and the pulse-count
   budgets of the pinching and QET cases on Emerald take d + g(N) from the line. `off-line`: the two-parameter line is
   rejected, and the form of g(N) is reopened (the sign of z at 250 and at 2000 pulses discriminates a shape that
   flattens from one that keeps rising). `anchors-moved`: the retained gap is not a stable property of the chip over
   the interval, and the stationarity of the gap comes before the line.

## Cost

IQM bills the job's compilation plus execution seconds, rounded up to whole seconds, at 0.75 credits per second
(`scripts/iqm_jobs.py`). The retained Emerald job `01a1ffe5` (sixteen circuits, 4000 shots) executed in 2.408 s and
compiled in 0.233 s. The builder's plan figure for that job (3.168 s) over-read its execution by 1.32 times.

- Execution. Shots times the schedule: the retained job fixes a per-circuit shot cost of 20.2 us once its trains
  (at 24 ns plus the measured gap) and delays are subtracted. Twenty circuits cost 403 us, the trains of this job
  387 us (7500 pulses at 24 ns plus g(N)), the delays 120 us: 910 us per shot, 3.64 s at 4000 shots. Scaling the
  retained execution by the builder's plan figures instead (4.2 s for this job, 0.76 of it) gives 3.19 s; the
  expectation is 3.2 to 3.7 s.
- Compilation scales with the circuit count: about 0.29 s.
- Expected runtime 3.5 to 4.0 s, billed 4 s, 3.00 credits; 3.75 credits if the runtime crosses 4.0 s.
- Requested approval: backend `iqm:emerald`, 20 circuits x 4000 shots, active reset, ceiling 9.00 credits (12
  billed seconds). `collect` cancels at 11.0 s of runtime (`iqm_jobs.cancel_threshold_seconds`), about 2.8 times the
  expected runtime, which covers the slow execution of the cancelled predecessor (`01a1f811`, at least 1.46 times
  its mock estimate) with room. A cancelled job bills nothing and returns no data. The submitter's own bound holds:
  ceil(1.6 + 4.2) x 0.75 = 4.5 credits is below 9.00. The balance read 26.75 credits on 2026-11-21 and expires
  2026-12-01.

## Seeds

The case draws no random number: the prediction, the power arithmetic and the self-test use expected counts. The
builder's existing seeds are unchanged.

## Not run

`emerald:mock` was not run. The mock accepted the predecessor's circuits (job `01a1ff21`); the added circuits carry
up to 2000 `prx` instructions, twice the predecessor's longest, so mock acceptance of them is untested and the owner
may add a free mock run before the Emerald submission.

## Retained measurements

- Predecessor run `results/iqm/runs/2026-11-21T205643Z-emerald-idle-schedule-t1-emerald-probe`, job `01a1ffe5`,
  analysis `results/iqm/idle_schedule_t1_emerald_analysis.json`.
- Falsifier of this case: the cohort or QB24 off the line at 250 or 2000 pulses by more than three combined standard
  errors, with the anchors unmoved.

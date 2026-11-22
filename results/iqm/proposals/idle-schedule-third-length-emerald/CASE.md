# IQM Emerald idle trains at a third length

Status: written case awaiting the owner's approval of a free `emerald:mock` check and of the Emerald submission. Nothing
has been sent to `iqm:emerald` or `emerald:mock`, and building this case made no IQM API call: its calibration files
are a read of Emerald's default set made beforehand through the IQM service, retained under `calibration/`.

Successor of [idle-schedule-t1-emerald](../idle-schedule-t1-emerald/CASE.md), whose result
([note](../../../../docs/notes/iqm/emerald-idle-schedule-t1-result.md)) leaves open the hypothesis that the per-pulse
gap of an idle train follows g(N) = 21.4 ns + 5.84 us / N. The line passes exactly through the eleven-qubit means at
500 pulses (33.06 +- 0.58 ns) and 1000 pulses (27.21 +- 0.47 ns), so those two points cannot test it. This case reads
trains of 250 and 2000 pulses and repeats the 500 and 1000 pulse trains in the same job, so that all four lengths are
measured at once and the form is tested inside one job.

Backend `iqm:emerald` (Crystal 54, pay-as-you-go 0.75 credits per second). The build is
`results/iqm/cases/idle-schedule-third-length-emerald/`, made by `scripts/iqm_idle_schedule_probe.py build --qc
emerald-third --calibration-from DIR`.

## Calibration

Calibration is a property of the run, so the case is built from a read of Emerald's default set and is rebuilt from a
new read immediately before submission. The build reads set `7d7ebe74-3674-4b32-baa2-fa0117ecbef9` (created
2026-11-22T05:13Z, the default when read at 2026-11-22T16:53Z), in place of the predecessor's retained copy of set
`ecec1d0a`. The two files are kept byte for byte in `calibration/`. Their metrics file names the set it describes
under `calibration_set_id` where the predecessor's copy says `describes_id`, and carries no observation-set fields;
`iqm_sim.Calibration.load` accepts either key for the check that the metrics and the architecture describe one set, and
`calibration_set_of` refuses a folder whose two files name different sets or whose metrics name none. No other reader
changes. The job pins the set (`calibration_set_id`), and `analyze` refuses a run compiled against another set.

Before submission, in the process that submits, the case is rebuilt from the default set read then (`build ... --live`,
a read-only calibration fetch that needs no approval, or `--calibration-from` on a folder read just before), checked
with `check`, and the approval digest of `cases.json` is refreshed: a rebuild changes `prediction.json`, so the
digest of this build (`cases.json` sha256 `179329baa22d19dccb8186f82185ec59acbebd0abe5011aed34766ab0b26978b`) holds only
while Emerald's default set stays `7d7ebe74`. The set enters the prediction's ASAP and ALAP schedule contrasts and the
job's pin; the decision below reads the run's counts and no calibration value.

## What it measures

The decay rate of one pi pulse's excited population on each qubit that shares no coupler with a train qubit, while the
train qubit runs N pi pulses, and from it the per-pulse gap g beyond the nominal 24 ns prx length, with the estimator
of the predecessor unchanged: the delay-measured T1 of the same job, the readout pair, and
g = d (k / k_T1 - 1) (`gap_test`). The train lengths are 250, 500, 1000 and 2000 pulses (`EMERALD_THIRD.pulses`), and
`h3_line` (`line_decision`) decides the line against them.

## Circuits

Twenty circuits at 4000 shots, one active-reset cycle, heralding `none`, each read by one joint `measure` over QB5,
QB10, QB14, QB18, QB20, QB24, QB26, QB30, QB34, QB37, QB42 and QB44. The sixteen circuits of the predecessor are kept
byte for byte (`third_length_self_test` compares them; they depend on the couplers, which the new set leaves
unchanged), and four are added: `idle-QB20-250`, `idle-QB26-250`, `idle-QB20-2000` and `idle-QB26-2000`. The 500 and
1000 pulse trains already in the job repeat the retained anchors. The estimator needs the delay circuits `t1-8us` to
`t1-64us`, the readout pair `par-ro0`, `par-ro1` and the four `par-amp` circuits, and they stay.

QB24 is measured with the cohort: it passes the delay-fit gate by the widest margin of the twelve (chi-square 0.36 on
2 degrees of freedom, T1 63.0 +- 1.5 us) and reads 30.5 +- 1.7 ns at 500 pulses and 25.8 +- 1.4 ns at 1000.

## Why a simulation cannot answer it

The gap is the chip's realized schedule and control-stack timing, which `iqm_sim` takes as an input, not an output,
and `emerald:mock` runs a different chip and returns random bits. The case asks whether one measured quantity keeps
a functional form across train lengths on the physical device.

## Pre-flight

1. Hypothesis (the note's first open hypothesis): the gap of a train of N pulses is g(N) = a + b / N with
   a = 21.37 ns and b = 5.842 us. Falsifier: the gap at 250 or 2000 pulses more than three standard errors from the
   line through the same job's gaps at 500 and 1000 pulses.
2. What the form means. With up the readout-corrected excited population before the train and down(N) after it,
   g(N) = (ln up - ln down(N)) / (k_T1 N) - d. The line g = a + b / N holds exactly when ln down(N) is linear in N:
   a constant decay per pulse, with an intercept. The intercept b is the sum of every N-independent loss between the
   N = 0 reference and the first pulse: a fixed wait in the train (a control-stack overhead), a fixed population drop
   (a fast initial decay, leakage, a state-preparation step), or both. They enter ln down(N) identically, so no length
   of this job separates them. The retained run supports this limit (recomputed from its counts): the eleven per-qubit b_i vary 11.7-fold (1.9 to
   21.8 us) and correlate with -T1_i ln(A_i / up) from the delay fits with r = 0.89, where A_i is the fitted
   amplitude of each qubit's delay decay. **`on-line` therefore tests the form a + b / N and the constant per-pulse gap a. It does
   not attribute b to a control-stack wait.** The nonzero lengths cancel a population drop between N = 0 and N > 0
   (the deviations below and the `nonzero_gap` reading use nonzero lengths only) and cancel b with it.
3. Quantity. For each subject and tested length n, the deviation of the gap from the line through the same job's gaps at
   the anchors a = 500 and b = 1000: L(n) = g(n) - alpha g(a) - (1 - alpha) g(b), alpha = (1/n - 1/b) / (1/a - 1/b),
   that is g(250) - 3 g(500) + 2 g(1000) and g(2000) - 1.5 g(1000) + 0.5 g(500). The coefficients sum to zero and sum to
   zero against 1 / N, so per (qubit, layout) cell L = -(1 / k_T1) sum c_i ln(p_i - r) / N_i: the baseline arm
   `idle-b-0`, the readout contrast (s - r) and the nominal pulse length drop out, and k_T1 enters as a scale. Subjects:
   `cohort`, the eleven qubits of the retained means (QB44 excluded, as there), and `QB24`. Cells pool by inverse
   variance within a qubit, and qubits by inverse variance of their L.
4. Covariance. Every quantity is a smooth function of independent binomial counts (one per circuit and qubit), and the
   analysis propagates them by the delta method (`Dual`, `contrast_reading` docstring): Var(L) = sum over counts of
   (dL/dp)^2 Var(p), with the arms at the contrast's lengths, the bare readout one-fraction r that every arm and the T1
   fit of the qubit share, the one-fraction s and the delay circuits behind k_T1. Two contrasts covary through the
   counts they share (the 500 and 1000 pulse arms, r, k_T1). The test against central differences of the estimator
   (`decision_self_test`) holds the delta method to 1e-3 of each derivative. The retained line's own error carries the
   same covariance: the two anchor gaps share the delay fit and the baseline, so the line's error is 1.40 ns at 250
   pulses and 0.59 ns at 2000 for the cohort, below the 1.97 and 0.77 ns that independent anchors give, and the
   covariance through the delay fit alone is 0.157 ns^2.
5. Predictions, written before any run. Each contrast L(n) is zero under the line (nanoseconds). The retained line's
   gap at the tested lengths, a secondary reading, is:

   | subject | 250 pulses | 2000 pulses |
   |---|---|---|
   | cohort | 44.74 +- 1.40 | 24.29 +- 0.59 |
   | QB24 | 40.04 +- 3.95 | 23.40 +- 1.73 |

6. Decision rule (`line_decision`, `h3_line` of the analysis). A subject's verdict, in this order:
   - `unidentifiable`: fewer qubits than its minimum (7 for the cohort, 1 for QB24) enter a tested length. A qubit enters
     a length through its own readings: its delay fit passes `usable_t1` (chi-square survival at least 0.001), its
     readout pair has a positive contrast, and at least one of its layouts has every arm of the contrast above 3
     standard errors of zero population with an `asap` schedule verdict of its own. A qubit that fails drops out and no
     other qubit's reading changes.
   - `off-line`: either L(250) or L(2000) lies more than 3 standard errors from zero. This falsifies the line.
   - `anchors-moved`: otherwise, the subject's gap at 500 or 1000 pulses lies more than 3 combined standard errors
     (this job's, the retained run's; independent runs) from the retained value. The device then differs from the one
     that fixed the retained numbers; the form inside the job stands.
   - `on-line`: otherwise. The line survives at two lengths; it is not proved.

   The case verdict is `off-line` when any subject is off-line, and otherwise the cohort's verdict; a QB24 that drifts reads
   `anchors-moved` in its own row without blocking the cohort. Two deviations are tested, so the false-alarm rate of
   the pair is 0.0051 (their correlation is -0.62, `power.json`). Secondary readings decide nothing but
   `anchors-moved`: the gap at the tested lengths against the retained line (`retained_line`), the per-pulse gap
   between 250 and 2000 pulses against the retained run's between 500 and 1000 (`nonzero_gap`, which a fixed
   population drop cannot move), and each layout's deviation separately (`by_layout`).
7. Dependence on QB44. `h3_line` reads each named qubit's own arms, delay fit and readout pair, and QB44 is no subject's
   qubit. The `h1_schedule` verdict over all twelve qubits and `h2_gap` (which excludes QB44 if its delay fit fails
   again, as in the retained run, and reads `unidentifiable`) are computed as before and decide nothing for `h3_line`.
8. Layouts. The decision pools the QB20 and QB26 layouts of each qubit because the retained run's layout split reads
   the same gap in both (16 comparisons, mean z 0.52; the note's second bullet), and the question concerns the line of
   the qubit's gap, not of the train qubit's. A gap that tracks the train qubit has no branch in the decision; each
   layout's deviation and its error are reported (`by_layout`) as readings.
9. Unidentifiable probability (`power.json`, `unidentifiable`). Model: each cohort qubit passes the delay-fit gate with
   the probability that a noncentral chi-square variable (the fit's dof, noncentrality the retained fit's chi-square less
   its dof) stays below the gate's critical value; arms are normal at the model device's populations; qubits and arms
   are independent. The delay-fit pass probabilities run from 0.66 (QB5) to 0.999. Under the retained run's rule, which
   needed all eleven, the repeat is unidentifiable with probability 0.81. With a minimum of seven qubits it is 0.0034;
   every arm of every cohort cell passes its population gate with probability within 1e-6 of one (the weakest modeled arm sits 18 standard errors above zero population). The model's one input
   (the retained fits' excess chi-square) comes from a single run.
10. Power, arithmetic at expected counts with no random draw (`power`, `power.json` beside this file). The model device
    is the retained run's readout, delay and anchor arms with each qubit's tested lengths on its own line, so no pulse
    length is rounded and the retained T1 and readout errors apply. At 4000 shots the cohort deviation has a standard
    error of 1.38 ns at 250 pulses and 0.52 ns at 2000, so a deviation of 4.1 ns (9 percent of the 44.7 ns prediction) at
    250 and 1.6 ns (6.5 percent of 24.3 ns) at 2000 sits three errors out. With the smallest accepted cohort (seven
    qubits, the ones of least weight) the figures are 5.9 and 2.2 ns. QB24 alone resolves 11.9 ns at 250 and 4.5 ns at 2000.
    Doubling the shots lowers the errors by about 1.4 times but doubles the cost, and the retained fits' excess
    chi-square doubles with the counts: at 8000 shots only five cohort qubits pass the delay-fit gate, below the
    minimum, so 4000 shots stay.
11. Limits. The decision treats the twelve qubits' counts as independent although one joint shot reads them together;
    correlation among them is outside the covariance. The scale of the delay instruction (a = 1) stays assumed, as in the
    predecessor, and enters L only as the scale k_T1. The delta method is first order: the logarithm of an arm at
    the 3 standard error gate is biased by one sixth of the arm's own error, and the bias falls in proportion to the error as
    the population moves away from zero, at 18 standard errors or more for every arm of the model device. The qubit weights are fixed at
    their estimated values.
12. What each result changes. `on-line`: ln(population) is linear in the pulse count from 250 to 2000 pulses, the per-pulse
    gap a is the constant the retained anchors fix, and the pulse-count budgets of the pinching and QET cases on Emerald
    take d + a per pulse plus an intercept b that no budget may split into wait and loss. `off-line`: the two-parameter
    line is rejected, and the sign of L at 250 and at 2000 pulses discriminates a shape that flattens from one that keeps
    rising. `anchors-moved`: the retained gap is not a stable property of the chip over the interval, and the stationarity
    of the gap comes before the line.

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
  billed seconds, three times the expected bill). `collect` cancels at 11.0 s of runtime
  (`iqm_jobs.cancel_threshold_seconds`), about 2.8 times the expected runtime, which covers the slow execution of the
  cancelled predecessor (`01a1f811`, at least 1.46 times its mock estimate) with room. IQM can bill a failed or
  cancelled job (`iqm_jobs.settled_unrun` frees a job only on an explicit zero), so a cancelled job bills the seconds it
  ran, at most 9.00 credits, and returns no data. The submitter's own bound holds: ceil(1.6 + 4.2) x 0.75 = 4.5 credits
  is below 9.00. The balance read 26.75 credits on 2026-11-21 and expires 2026-12-01.

## Mock check first

A free `emerald:mock` run of this case (20 circuits x 4000 shots, price 0) comes before the Emerald submission and needs
the owner's approval, since the mock is a provider job. Its purpose is the 2000-pulse trains, which no job has run: a
train of 2000 pulses lasts about 97 us (2000 x 48.3 ns), 11 times the 8.6 us T2 of QB34, and the longest accepted so far
is 1000 pulses. The mock accepts or rejects the circuits at validation and reports an execution runtime estimate to
compare with the plan's 4.2 s; it decides nothing about the device, and its outcomes are random bits that never enter
the analysis. A rejection at 2000 pulses ends the case before any credit is spent.

## Seeds

The case draws no random number: the prediction, the power arithmetic and the self-test use expected counts and finite
differences. The builder's existing seeds are unchanged.

## Retained measurements

- Predecessor run `results/iqm/runs/2026-11-21T205643Z-emerald-idle-schedule-t1-emerald-probe`, job `01a1ffe5`,
  analysis `results/iqm/idle_schedule_t1_emerald_analysis.json`. The line and its errors are rebuilt from the run's
  counts (`prediction.json` `line`, `source_sha256` `f69b9c1d...b210`, measurements sha256 `66514dca...8fa0`); the build
  checks that the recomputed per-qubit gaps equal the analysis record's.
- Falsifier of this case: the cohort or QB24 off the line at 250 or 2000 pulses by more than three standard errors of the
  within-job deviation.

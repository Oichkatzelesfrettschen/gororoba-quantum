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
digest of this build (`cases.json` sha256 `2c118f7b1ebfaa6782ded87aa650512b4c0fbda7a256ad68356ef66ee0591e4c`) holds only
while Emerald's default set stays `7d7ebe74`. The set enters the prediction's ASAP and ALAP schedule contrasts and the
job's pin; the decision below reads the run's counts and no calibration value.

## What it measures

The decay rate of one pi pulse's excited population on each qubit that shares no coupler with a train qubit, while the
train qubit runs N pi pulses, and from it the per-pulse gap g beyond the nominal 24 ns prx length, with the estimator
of the predecessor unchanged: the delay-measured T1 of the same job, the readout pair, and
g = d (k / k_T1 - 1) (`gap_test`). The train lengths are 250, 500, 1000 and 2000 pulses (`EMERALD_THIRD.pulses`), and
`h3_line` (`line_decision`) decides the line against them.

## Circuits

Twenty-one circuits at 4000 shots, one active-reset cycle, heralding `none`, each read by one joint `measure` over QB5,
QB10, QB14, QB18, QB20, QB24, QB26, QB30, QB34, QB37, QB42 and QB44. The sixteen circuits of the predecessor are kept
byte for byte (`third_length_self_test` compares them; they depend on the couplers, which the new set leaves
unchanged), and five are added: `idle-QB20-250`, `idle-QB26-250`, `idle-QB20-2000`, `idle-QB26-2000` and the delay circuit `t1-96us`
(`prx(pi)` on the twelve, one 96 us delay, the joint measure). The 500 and
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
   line through the same job's gaps at 500 and 1000 pulses, after the delay-measured curvature below.
2. What the form means. With up the readout-corrected excited population before the train and down(N) after it,
   g(N) = (ln up - ln down(N)) / (k_T1 N) - d. For single-exponential decay and linear timing T = tau N + b the line
   g = a + b / N holds exactly when ln down(N) is linear in N: a constant decay per pulse, with an intercept. The
   intercept b is the sum of every N-independent loss between the N = 0 reference and the first pulse: a fixed wait in
   the train (a control-stack overhead), a fixed population drop (a fast initial decay, leakage, a state-preparation
   step), or both. They enter ln down(N) identically, so no length of this job separates them. The retained run supports
   this limit (recomputed from its counts): the eleven per-qubit b_i vary 11.7-fold (1.9 to 21.8 us) and correlate with
   -T1_i ln(A_i / up) from the delay fits with r = 0.89, where A_i is the fitted amplitude of each qubit's delay decay.
   **`on-line` therefore tests the form a + b / N and the constant per-pulse gap a. It does not attribute b to a
   control-stack wait.** The nonzero lengths cancel a population drop between N = 0 and N > 0 (the deviations below
   use nonzero lengths only) and cancel b with it.
3. Curvature of the delay decay. The retained delay fits are not single exponentials: their chi-square is 66.9 on 22
   degrees of freedom over the eleven cohort qubits, with one residual sign pattern across the chip. Read as linear timing, a curved decay mimics a curved gap: on the
   model device that carries the retained curvature, the cohort deviation at 2000 pulses reads -5.35 standard errors
   without correction, an `off-line` verdict from a device whose timing is linear (probability 0.998). The job
   therefore adds one delay circuit, `t1-96us`, whose 96 us spans the 2000-pulse train (about 97 us), and fits each
   qubit's delay decay with ln(p - r) = c0 + c1 t + c2 t^2 over the five delay circuits. The rate k_T1 of the gap stays
   the log-linear fit of the four short delays, so the retained anchors compare like with like; the long circuit enters
   only through c2. A train of time T = tau N + b then reads g_measured = g_true - c2 T^2 / (k_T1 N), and a contrast
   carries -(c2 / k_T1) tau^2 sum c_i N_i, with tau the pulse length plus the line's offset (sum c_i = 0 and
   sum c_i / N_i = 0 remove b). The correction adds +(c2 / k_T1) tau^2 sum c_i N_i to each cell, with c2's covariance.
   On the same model device the corrected deviations read z = 0 and the case-level false-alarm rate is the
   no-deviation value in item 6; the correction is exact only for a decay that is quadratic in ln(p - r) through 96 us.
   **`off-line` therefore means that ln(p - r) is not linear in N after the quadratic delay correction, under linear
   timing: a failure of the line, of the quadratic curvature model or of linear timing, which this job does not
   separate.**
4. Quantity. For each subject and tested length n, the deviation of the gap from the line through the same job's gaps at
   the anchors a = 500 and b = 1000: L(n) = g(n) - alpha g(a) - (1 - alpha) g(b), alpha = (1/n - 1/b) / (1/a - 1/b),
   that is g(250) - 3 g(500) + 2 g(1000) and g(2000) - 1.5 g(1000) + 0.5 g(500), with the curvature correction. The
   coefficients sum to zero and sum to zero against 1 / N, so per (qubit, layout) cell
   L = -(1 / k_T1) sum c_i ln(p_i - r) / N_i + (c2 / k_T1) tau^2 sum c_i N_i: the baseline arm `idle-b-0`, the readout
   contrast (s - r) and the nominal pulse length drop out. Subjects: `cohort`, the eleven qubits of the retained means
   (QB44 excluded, as there), and `QB24`. Cells pool by inverse variance within a qubit, and qubits by inverse variance
   of their L.
5. Covariance. Every quantity is a smooth function of independent binomial counts (one per circuit and qubit), and the
   analysis propagates them by the delta method (`Dual`, `contrast_reading` docstring): Var(L) = sum over counts of
   (dL/dp)^2 Var(p), with the arms at the contrast's lengths, the bare readout one-fraction r that every arm and the
   delay fits of the qubit share, the one-fraction s and the delay circuits behind k_T1 and c2. Two contrasts covary
   through the counts they share (the 500 and 1000 pulse arms, r, k_T1, c2). The test against central differences of the
   estimator (`decision_self_test`) holds every derivative of the corrected deviation to 1e-3. The delay fit's rate and
   the pooled anchor gaps hold the fit weights and the pooling weights fixed, and central differences of the production
   estimators, whose weights follow the data, read their errors within 10 percent of the delta method's (0.99 to 1.05 at
   the retained counts); the anchors enter `anchors-moved` and the retained-line reading only. The retained line's own
   error carries the same covariance: 1.40 ns at 250 pulses and 0.59 ns at 2000 for the cohort, below the 1.97 and
   0.77 ns that independent anchors give.
6. Predictions, written before any run. Each corrected contrast L(n) is zero under the line (nanoseconds). The retained
   line's gap at the tested lengths, a secondary reading, is:

   | subject | 250 pulses | 2000 pulses |
   |---|---|---|
   | cohort | 44.74 +- 1.40 | 24.29 +- 0.59 |
   | QB24 | 40.04 +- 3.95 | 23.40 +- 1.73 |

7. Decision rule (`line_decision`, `h3_line` of the analysis). A subject's verdict, in this order:
   - `unidentifiable`: fewer qubits than its minimum (7 for the cohort, 1 for QB24) pass at every tested length. A qubit
     passes through its own readings: a readout contrast s - r of at least 0.5 and ten of its standard errors; a
     log-linear delay fit and a quadratic delay fit with chi-square survival at least 0.001; in at least one layout every
     arm of the contrast above 3 standard errors of zero population with an `asap` schedule verdict of its own; and a
     population that falls from 250 to 2000 pulses by more than 3 standard errors. A qubit that fails drops out and no
     other qubit's reading changes. The cohort is the set of qubits that pass at both tested lengths, so both deviations
     read the same qubits.
   - `off-line`: either L(250) or L(2000) lies more than 3 standard errors from zero (meaning as in item 3).
   - `anchors-moved`: otherwise, the subject's gap at 500 or 1000 pulses lies more than 3 combined standard errors
     (this job's, the retained run's; independent runs) from the retained value. The device then differs from the one
     that fixed the retained numbers; the form inside the job stands.
   - `on-line`: otherwise. The four lengths are consistent with the line within the stated errors; the line is not
     proved.

   The case verdict is `off-line` when any subject is off-line, and otherwise the cohort's verdict; a QB24 that drifts reads
   `anchors-moved` in its own row without blocking the cohort. Six statistics can reject the case: the cohort
   and QB24 deviations at 250 and 2000 pulses, and the cohort's gap at 500 and at 1000 pulses against the retained
   value. Their rates under no deviation come from their full covariance (`decision_correlation`,
   `family_false_alarm`, a deterministic quasi-random integration; `power.json`): **0.0105 for `off-line` over the four
   deviations and 0.0153 for the six-statistic rejection (`off-line` or `anchors-moved`) given the modeled membership**,
   the cohort of eleven and QB24 as built. That rate excludes `unidentifiable`, which has its own bound (item 10: at most
   0.036 under any dependence, 3.5e-9 for independent qubits), so the probability of a verdict other than `on-line` is at
   most 0.0153 + 0.036 = 0.051 under no deviation (the anchors correlate +0.59 with each other and
   -0.44 and -0.47 with the cohort deviations). QB24 stays decision-producing, since it is the one subject that tests a
   single tightly fitted qubit. Secondary readings decide nothing but `anchors-moved`: the gap at the tested lengths against
   the retained line (`retained_line`), the per-pulse gap between 250 and 2000 pulses against the retained run's between
   500 and 1000 (`nonzero_gap`, which a fixed population drop cannot move and which the delay curvature does move, so it
   is read uncorrected), and each layout's deviation separately (`by_layout`).
8. Dependence on QB44. `h3_line` reads each named qubit's own arms, delay fits and readout pair, and QB44 is no subject's
   qubit. The `h1_schedule` verdict over all twelve qubits and `h2_gap` (which excludes QB44 if its delay fit fails
   again, as in the retained run, and reads `unidentifiable`) are computed as before and decide nothing for `h3_line`.
9. Layouts. The decision pools the QB20 and QB26 layouts of each qubit because the retained run's layout split reads
   the same gap in both (16 comparisons, mean z 0.52; the note's second bullet), and the question concerns the line of
   the qubit's gap, not of the train qubit's. A gap that tracks the train qubit has no branch in the decision; each
   layout's deviation and its error are reported (`by_layout`) as readings.
10. Unidentifiable probability (`power.json`, `unidentifiable`). The gate is the quadratic delay fit (two degrees of
    freedom with five points): a cohort qubit passes with the probability that a noncentral chi-square variable
    (noncentrality the retained four-point quadratic fit's chi-square less its one degree of freedom) stays below the
    critical value, 0.89 (QB20) to 0.999; arms are normal at the model device's populations. Independent qubits give
    **3.5e-9**. The retained residuals share one chip-wide sign pattern, so independence is not assumed: the comonotone
    case (the qubits fail together in order of their failure probabilities) gives 0.0010 and Markov's bound over every
    dependence gives **0.036**. Under the retained run's rule, which needed all eleven qubits to pass a log-linear gate,
    the repeat is unidentifiable with probability 0.81 (independent qubits). The model takes the per-arm schedule verdict
    (`asap`, separated from `alap` by at least 25 standard errors in the prediction), the fall of the population and the
    delay fit's five-point requirement as certain at the model device's size. The model's one input (the retained
    residuals) comes from a single run. Under this case's calibration set (`7d7ebe74`) the weakest cohort arm is QB30 at
    2000 pulses, 3.3 standard errors above zero population against the gate's 3.0 (the retained run read 18): a QB30
    that falls under the gate leaves ten qubits, above the minimum.
11. Power, arithmetic at expected counts with no random draw (`power`, `power.json` beside this file). The model device
    is the retained run's readout, delay curvature and anchor arms with each qubit's tested lengths on its own line, so no
    pulse length is rounded and the retained T1 and readout errors apply. At 4000 shots the corrected cohort deviation has
    a standard error of 1.41 ns at 250 pulses and 0.61 ns at 2000, so a deviation of 4.2 ns (9.5 percent of the 44.7 ns
    prediction) at 250 and 1.8 ns (7.5 percent of 24.3 ns) at 2000 sits three errors out. With the smallest accepted
    cohort (seven qubits, the ones of least weight) the figures are 6.0 and 2.5 ns. QB24 alone resolves 12.2 ns at 250
    and 5.4 ns at 2000. These figures perturb the population of an arm by exp(-k1 N delta) on the nominal curve. A
    physical timing deviation acts through the decay law at the shifted train time T + N delta, ln p moving by
    (c1 + 2 c2 T) N delta + c2 N^2 delta^2, so the statistic responds with the local decay rate and not k1. Under that
    alternative (`power.json`, `physical_resolvable_deviation_ns`; the self-test's recovery check uses it and matches
    the decay law to 1e-3) a reading of three errors needs a true shift of 4.0 ns at 250 pulses (reading 1.05 of the
    shift) and **2.4 ns at 2000 pulses** (reading 0.75 of the shift) for the cohort, and 12.0 and **5.9 ns** for QB24
    (readings 1.02 and 0.91). The cohort's 2000-pulse sensitivity is a third worse than the population figure and the
    QB24 one a tenth; 2.4 ns is 10 percent of the 24.3 ns prediction and 5.9 ns is 25 percent of QB24's 23.4 ns, which
    serves the stated purpose of a three-error test of the line at two lengths. More shots are therefore not needed:
    8000 shots lower the errors by 1.4 times and double the cost, and the 4000 shots stay. Doubling the shots lowers the errors by about 1.4 times (1.00 and 0.43 ns) and doubles the cost;
    the expected number of cohort qubits passing the quadratic gate is 10.4 of 11 at 8000 shots (the probability of fewer
    than seven is 1.5e-7), so the gate leaves the doubled counts usable, and 4000 shots stay for the cost.
12. Limits. The decision treats the twelve qubits' counts as independent although one joint shot reads them together;
    correlation among them is outside the covariance. The scale of the delay instruction (a = 1) stays assumed, as in the
    predecessor, and enters L only as the scale k_T1. The delta method is first order: the logarithm of an arm at the 3
    standard error gate is biased by one sixth of the arm's own error, and the bias falls in proportion to the error as
    the population moves away from zero. The qubit weights are fixed at their estimated values. The curvature
    correction assumes the delay decay is quadratic in ln(p - r) up to 96 us, that the train shares the delay decay's
    curvature, and linear timing.
13. What each result changes. `on-line`: the four measured lengths are consistent with linearity within the stated
    errors; the run does not distinguish the surviving mechanisms. The pulse-count budgets of the pinching and QET cases
    on Emerald may take d + a per pulse plus an intercept b, as a description consistent with the data, and no budget may
    split b into wait and loss. `off-line`: ln(p - r) is not linear in N after the delay correction, under linear
    timing, and the sign of L at 250 and at 2000 pulses discriminates a shape that flattens from one that keeps rising.
    `anchors-moved`: the retained gap is not a stable property of the chip over the interval, and the stationarity of
    the gap comes before the line.

## Cost

IQM bills the job's compilation plus execution seconds, rounded up to whole seconds, at 0.75 credits per second
(`scripts/iqm_jobs.py`). The retained Emerald job `01a1ffe5` (sixteen circuits, 4000 shots) executed in 2.408 s and
compiled in 0.233 s. The builder's plan figure for that job (3.168 s) over-read its execution by 1.32 times.

- Execution. Shots times the schedule: the retained job fixes a per-circuit shot cost of 20.2 us once its trains
  (at 24 ns plus the measured gap) and delays are subtracted. Twenty-one circuits cost 424 us, the trains of this job
  387 us (7500 pulses at 24 ns plus g(N)), the delays 216 us (8 + 16 + 32 + 64 + 96 us): 1.027 ms per shot, 4.11 s at
  4000 shots. Scaling the retained execution by the builder's plan figures instead (4.734 s for this job, 0.76 of it)
  gives 3.6 s; the expectation is 3.6 to 4.1 s. The added 96 us circuit costs 0.46 s of it (0.38 s of delay and 0.08 s of
  per-circuit overhead per 4000 shots), about 0.35 credits.
- Compilation scales with the circuit count: about 0.30 s.
- Expected runtime 3.9 to 4.4 s, billed 4 or 5 s, 3.00 to 3.75 credits (3.75 if the runtime crosses 4.0 s).
- Requested approval: backend `iqm:emerald`, 21 circuits x 4000 shots, active reset, ceiling 9.00 credits (12
  billed seconds, 2.4 times the larger expected bill). The added circuit changes the expected runtime by 12 percent, so
  the ceiling stays: `collect` cancels at 11.0 s of runtime (`iqm_jobs.cancel_threshold_seconds`), 2.5 times the
  expected runtime, which covers the slow execution of the cancelled predecessor (`01a1f811`, at least 1.46 times its
  mock estimate, here 6.9 s) with room. IQM can bill a failed or cancelled job (`iqm_jobs.settled_unrun` frees a job
  only on an explicit zero), so a cancelled job bills the seconds it ran and returns no data. The ceiling is best effort:
  IQM takes no runtime limit with a job, so `collect` holds the 9.00 credits by polling and cancelling at 11.0 s, and a
  late poll can let the runtime pass it. The submitter's own bound holds: ceil(1.6 + 4.734) x 0.75 = 5.25 credits is
  below 9.00. The balance read 26.75 credits on 2026-11-21 and expires 2026-12-01.

## Mock check first

A free `emerald:mock` run of this case (21 circuits x 4000 shots, price 0) comes before the Emerald submission and needs
the owner's approval, since the mock is a provider job. Its purpose is the longest circuits, which no job has run: the
2000-pulse trains last about 97 us (2000 x 48.3 ns), 11 times the 8.6 us T2 of QB34, the longest accepted so far is
1000 pulses, and the added `t1-96us` delay is 1.5 times the longest delay accepted (64 us). The mock accepts or rejects
the circuits at validation and reports an execution runtime estimate to compare with the plan's 4.734 s; it decides
nothing about the device, and its outcomes are random bits that never enter the analysis. A rejection at 2000 pulses or
at 96 us ends the case before any credit is spent.

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

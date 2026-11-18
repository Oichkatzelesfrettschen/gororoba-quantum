# Tuna-17 per-qubit characterization, 2026-11-16

The series of [characterization_tuna_17](../../../results/quantum_inspire/cases/characterization_tuna_17/CASE.md)
(14 circuits on all 17 qubits: readout pair, six T1 waits, four X90 repetition
counts, closing readout pair) ran on Tuna-17 under an approval of 2026-11-16
after its QX twin ([characterization_qx](../../../results/quantum_inspire/cases/characterization_qx/CASE.md))
returned the noiseless outcome of all 14 circuits. The runs are retained as
`results/quantum_inspire/runs/2026-11-16T0401Z-characterization_tuna_17-characterization_tuna_17-batch-00`
to `-batch-05` and the twin's `2026-11-16T0355Z-characterization_qx-...`
directories; the analysis rows are
`results/quantum_inspire/characterization_tuna_17_analysis.json` and
`characterization_qx_analysis.json`, produced by `--analyze` of
`scripts/qi_tuna17_characterization_cases.py`, which `--sanity` accepted on
all 12 run directories before the analysis.

## Provenance

- Batch 00 (jobs 1742700 and 1742701, batch job 959020) was submitted at
  04:01:27Z while the batch's own `backend_status_at_submit` reads
  `calibrating`. The case's admission rule requires the instance to read
  `idle` before the first batch; the series was submitted without that read,
  a lapse of the admission gate. The six batches record `calibrating`,
  `idle`, `idle`, `executing`, `executing`, `executing` at submission
  (`submission.json` of each), and each found the account's user queue empty
  at submission.
- Batch 00 executed between 12:21:29Z and 12:21:51Z, 8 h 20 min after submission
  (`created_on` against `queued_at` of the two jobs in `results.json`).
  The collector, which waits for the batch to start, timed out twice with
  "execution deadline expired before resource-request initiation": after 3600 s
  at 05:01Z, and after the 21600 s limit of the resumed collection at 11:07Z.
  Both resumptions read the same batch under the same series stamp and
  submitted nothing; the third collection began at about 12:13Z. The first
  attempt ran at repository commit 78c780bc6 and the final one at ed55e4dbc;
  the case, the analyzer, the Quantum Inspire reader and the submit script are
  identical at both. The timeout instants, the restart time and the two
  commits come from the collector's logs, which this change does not retain; every other timestamp here is in the retained
  `submission.json` and `results.json` files.
- Batches 01 to 05 were submitted from 12:22:32Z to 12:32:25Z and collected by
  12:34:01Z. The opening readout pair therefore executed 12 min before the
  closing pair (12:21:51Z and 12:33:52Z), and the T1 waits ran between them,
  in two batches 2 min apart (12:25Z and 12:27Z).
- Backend state. The retained files read the backend status at submission only.
  Batch 00 reads `calibrating` at 04:01:27Z and its first job began executing
  at 12:21:29Z (`queued_at`); the next read, at the submission of batch 01
  (12:22:32Z), is `idle`, 41 s after batch 00's last job finished (12:21:51Z).
  No retained file holds a status between the two reads, so the files do not
  show whether execution began after the backend left `calibrating`; they show
  `idle` after batch 00 ran.
- Summed execution time is 119.8 s against the predicted 115.8 s (+3.5%), 0
  credits charged (the ledger snapshot of this change holds no transaction).

## Readout

Measured on all 17 qubits, 16,384 shots per circuit. Opening pair: P(1|0)
0.006 to 0.055 (mean 0.027), P(1|1) 0.911 to 0.985 (mean 0.959); closing pair:
P(1|0) 0.006 to 0.049 (mean 0.026), P(1|1) 0.917 to 0.984 (mean 0.959).

- Stability: the largest opening-to-closing change of any probability is
  0.0136 (qubit 7), mean per-qubit maximum 0.0054; `readout_stable` is true
  on all 17 qubits (tolerance 0.03).
- Against the 2026-10-17 retained rows, `readout_within_tolerance` (closing
  pair) is true on 16 qubits and false on qubit 8, whose P(1|1) rose by 0.036
  (0.9457 retained, 0.9818 closing). The opening pair also leaves tolerance on
  qubit 6 (P(1|1) up 0.041, closing 0.027); the analyzer scores the closing
  pair only. The falsifier "a move above 0.03" is met on qubit 8 and,
  by the opening pair, on qubit 6; the null predicted none.

## T1

One exponential fits the points above a corrected population of 0.05 (5 or 6
points per qubit; the readout correction uses the mean of both pairs).

| Qubit | T1 fit (us) | points | chi-square / dof | single exponential | implied 2026-10-17 (us) | ratio |
|---|---|---|---|---|---|---|
| 0 | 17.1 +- 0.2 | 5 | 14.7 / 3 | false | 14.2 | 1.20 |
| 1 | 19.6 +- 0.2 | 5 | 17.8 / 3 | false | 25.5 | 0.77 |
| 2 | 24.8 +- 0.2 | 5 | 703.3 / 3 | false | 17.8 | 1.40 |
| 3 | 13.2 +- 0.1 | 5 | 250.0 / 3 | false | 9.3 | 1.42 |
| 4 | 24.9 +- 0.2 | 6 | 275.6 / 4 | false | 15.6 | 1.59 |
| 5 | 20.4 +- 0.2 | 5 | 36.2 / 3 | false | 15.1 | 1.35 |
| 6 | 16.2 +- 0.2 | 5 | 70.2 / 3 | false | 5.5 | 2.95 |
| 7 | 27.7 +- 0.3 | 6 | 146.7 / 4 | false | 52.0 | 0.53 |
| 8 | 19.0 +- 0.2 | 5 | 6.0 / 3 | true | 18.1 | 1.05 |
| 9 | 22.1 +- 0.2 | 5 | 153.1 / 3 | false | 5.1 | 4.29 |
| 10 | 32.2 +- 0.3 | 6 | 69.6 / 4 | false | 18.7 | 1.72 |
| 11 | 26.4 +- 0.2 | 6 | 132.8 / 4 | false | 22.4 | 1.18 |
| 12 | 22.9 +- 0.2 | 5 | 146.1 / 3 | false | 21.0 | 1.09 |
| 13 | 23.8 +- 0.3 | 5 | 5.7 / 3 | true | 23.0 | 1.04 |
| 14 | 23.6 +- 0.2 | 6 | 1984.9 / 4 | false | 13.1 | 1.81 |
| 15 | 24.7 +- 0.2 | 6 | 665.7 / 4 | false | 6.3 | 3.94 |
| 16 | 22.2 +- 0.2 | 5 | 13.4 / 3 | false | 16.6 | 1.34 |

- Fitted T1 spans 13.2 to 32.2 us (median 22.9 us), against the predicted
  5.1 to 52.0 us. The pre-flight falsifier "T1 outside a factor of two of its
  implied value" is met on qubits 6 (2.95), 9 (4.29) and 15 (3.94), the three
  qubits with the lowest implied values (5.5, 5.1 and 6.3 us; each implied
  value rests on one 2 us wait); qubit 7 sits at
  0.53, inside the factor.
- The single-exponential verdict is false on 15 of 17 qubits (true only on
  qubits 8 and 13), against a prediction of true on all 17. The quoted
  standard errors are binomial only and leave out the covariance of the shared
  readout pair (CASE.md, "Predictions and verdicts"), so they and the
  chi-square probabilities are approximate and understated; the reduced
  chi-square runs from 1.9 to 496.
- Measured shape: the decay length from the two-point slope slows with delay on
  15 of 17 qubits. The ratio of the 40 to 80 us length to the 0 to 10 us length
  is 0.87 to 1.69 on 16 qubits and 4.3 on qubit 14, whose population at 80 us
  (0.092) is the largest after qubit 10's (0.106). The case lists a two-rate decay as the
  falsifier of the single exponential. hypothesis: the late points are biased by the
  readout pair, which is taken with every neighbor prepared in the excited
  state while late T1 points are read with neighbors near the ground state
  (CASE.md, last hypothesis), or a second, slower population contributes; no
  arm in this series separates the two; "T1 shape: results" below refits the
  counts.

## T1 shape: predictions written before the refit

The single-exponential verdict fails on 15 of 17 qubits where the case predicted
17 of 17. This section records the hypotheses, each with its prediction and
falsifier, before any refit of the retained counts ran; the results follow in
"T1 shape: results". The inputs are the retained counts only (no provider
read): six delays (0, 250, 500, 1000, 2000, 4000 cycles) at 8,192 shots, and
the opening and closing readout pairs at 16,384 shots. The registered verdict
rule and the retained `--analyze` rows stay unchanged.

Method, fixed in advance. Each T1 point is a binomial count; the goodness of fit
is Pearson chi-square with the model's fitted probability in the variance (the
retained analyzer uses the observed fraction), and the intervals are profile
likelihoods of the binomial deviance (68.3% at a deviance rise of 1.00), widened
by the factor sqrt(chi-square / dof) where that exceeds 1. No bootstrap runs, so
no random seed enters. Model comparison uses the binomial deviance with AICc and
BIC at six points, where three parameters leave 3 degrees of freedom and an
AICc penalty that is itself uncertain; a 3-parameter model counts as supported
only on the agreement of AICc and BIC with the fit quality below.

- H1, readout floor. The retained analyzer already maps each point through the
  mean readout pair, (p - e01) / (e11 - e01), so the model
  P1(t) = e01 + (e11 - e01) exp(-t / T1) with e01 and e11 fixed from the opening
  pair, the closing pair and their mean differs from the retained fit only in
  keeping every point (the analyzer drops points under a corrected population of
  0.05) and in fitting P1 directly instead of its logarithm. Prediction: the
  offsets are already in the retained fit, so the refit leaves chi-square / dof
  above 3 on at least 9 of 17 qubits for each of the three choices, with the
  late points above the model. A variant that takes e01 and e11 as free
  parameters constrained by the readout counts (the joint likelihood) carries
  the covariance of the shared pair. Falsifier: chi-square / dof at most 3 on at
  least 9 qubits and a median at most 2 supports H1.
- H2, delay unit or idle-gate calibration. Prediction: every wait line reads
  `wait(N)` with N the file's delay on all 17 qubits, `cases.json` and
  [cqasm.md](cqasm.md) give 20 ns per cycle, and the execution time of the six
  jobs rises with N by 0.164 ms per cycle (20 ns x 8,192 shots) to within 25%.
  A one-parameter rescale of time changes T1 and leaves the shape, so the
  discriminating test is a common warp: the stretched exponent fitted per qubit
  carries a shared value only if one clock error acts on all qubits. Falsifier:
  consistent units, a slope within 25% of nominal and a per-qubit exponent
  spread that rejects a common exponent (likelihood ratio, 16 degrees of
  freedom, p below 0.01) refute H2; a common exponent other than 1 with a
  nonlinear execution-time slope supports it.
- H3, two-rate decay. Prediction: a plateau (one residual fraction c), a
  stretched exponential or a biexponential reaches chi-square / dof at most 3 on
  at least 12 of 17 qubits and lowers AICc by more than 4 against the single
  exponential on at least 12; the second scale is slower than the first, with a
  positive weight, on at least 15 of 17 qubits. The window ends at 80 us, about
  3.5 T1, so the slow scale is bounded below and unbounded above on most
  qubits; I expect "supported in sign, undecided in magnitude" for the tail.
  Falsifier: chi-square / dof above 3 on most qubits for every model of at most
  3 parameters, a faster second scale on 4 or more qubits, or an AICc gain
  under 2.
- H4, drift during the 8 h 20 min queue and the 12 min run. Prediction:
  refuted. The opening-to-closing change of any readout probability is at most
  0.0136 (mean per-qubit maximum 0.0054), which moves a corrected population by
  at most 0.015, below the excess at 80 us. Test: e01 and e11 interpolated
  linearly in the job finish times between the opening and the closing pair, and
  the step between batch 01 and batch 02 (2 min apart). Falsifier: the
  interpolated model brings chi-square / dof to at most 3 on at least 9 qubits,
  or the batch step exceeds 2 standard errors on at least 9 qubits.
- H5, simultaneous driving and crosstalk. All 17 qubits are excited and read
  together, so a qubit's decay sits beside neighbors in the same state. Test, on
  the joint 17-bit strings and the 24-edge coupling map of the catalogue:
  Spearman correlation of each qubit's standardized residual (the 80 us point
  against the single-exponential fit to the earlier points) with its degree and
  with the mean residual of its neighbors, and the connected correlation of
  coupled against uncoupled pairs at 80 us. Prediction: |rho| below 0.6 on both
  (n = 17), and a coupled-pair excess within 3 standard errors of the uncoupled
  pairs; the series holds no single-qubit arm, so a null here narrows the claim
  to "no map-aligned pattern in this series". Falsifier: |rho| at least 0.6 (p
  below 0.01) or a coupled-pair excess above 3 standard errors supports H5.
- Standard-error mechanism. The retained fit is a weighted straight-line fit of
  the logarithm of the corrected population, whose slope variance
  sw / (sw sxx - sx^2) assumes the line is right, so it carries no factor of
  chi-square / dof, and it ignores the covariance of the shared readout pair.
  Prediction: scaling the quoted standard errors by sqrt(chi-square / dof)
  (1.4 to 22 over the retained rows) widens them to 0.3 to 4.5 us, and the
  spread of T1 over the alternative analyses (retained log fit, direct fit with
  the opening, closing or mean pair) then falls inside the scaled interval.
  Falsifier: a spread above the scaled standard error on 5 or more qubits
  leaves a second source of error beyond the missing scale factor.

### Additions registered after the first refit

The first refit (H1 to H5 as registered above, plus the H2b model below) ran
before these two entries were written. H2b is therefore a prediction recorded
after its result, with no pre-registration status; H6 is registered before its
model runs.

- H2b, a delay offset that exists only when a wait instruction exists.
  Chosen after the corrected populations of the six delays had been read, and
  run in the first refit: the `t1-0` circuit holds no wait line, so a fixed idle or
  scheduling overhead t0 in every wait would shorten the `t1-N` points (N > 0)
  by exp(-t0 / T1) and leave the `t1-0` point alone. The model
  exp(-(t + t0 [N > 0]) / T1) has 2 parameters. Prediction: a hardware
  overhead is one value shared by the qubits, so a common t0 is not rejected
  (likelihood ratio, 16 degrees of freedom, p above 0.01); falsifier: p below
  0.01 refutes a shared overhead.
- H6, a distribution of T1 inside one job. A qubit whose T1 switches between
  values during the 7 s of one job (a coupled two-level defect or quasiparticle
  bath) averages exp(-t / T1) over that distribution, which lengthens the tail.
  The 2-parameter model takes a lognormal T1 with median T and log-width
  sigma. Prediction, written after the refit showed the 80 us point above the
  single-exponential fit on 16 of 17 qubits and the 5 us point below it on 14
  of 17: sigma is 0.2 to 0.8 and the model lowers AICc by more than 4 against
  the single exponential on at least 12 qubits, and it leaves chi-square / dof
  above 3 on at least 12 (it does not remove the 5 us dip, which is a fast
  loss, not a tail). Falsifier: chi-square / dof at most 3 on at least 12
  qubits supports H6 as the shape.

### Batch-offset test registered before its last two pieces ran

The delays split across two batches: 0, 250 and 500 cycles (0, 5 and 10 us) in
batch 01 and 1000, 2000 and 4000 cycles (20, 40 and 80 us) in batch 02, so a
level shift between the batches and a change of decay shape act on disjoint
groups of delays. The residual signs of the single exponential (5 us below the
fit, 80 us above) resemble a step, and the two-parameter `single_step` fit
(T1 and an additive step of batch 02, 4 degrees of freedom) was already in the
record before this entry: chi-square / dof at most 3 on 3 of 17 qubits, the
step positive on 16 of 17 with a likelihood-ratio gain above 4 on 13. That
result is exploratory. This entry registers, before they run, the prediction
and falsifier for H4b and the two pieces not yet computed: a three-parameter
step model and an anchor comparison.

- H4b, one offset between batch 01 and batch 02 plus a single exponential.
  Model `single_amplitude_step`: P1(t) = e01 + (e11 - e01) A exp(-t / T1) +
  s [batch 02], with e01 and e11 from the mean readout pair, a free amplitude A
  (0.5 to 1.5) and a free step s (-0.2 to 0.2). The third parameter is the
  amplitude because it frees the zero-delay level of batch 01, so the step is
  not pinned by an assumed readout value there; six points and three
  parameters leave 3 degrees of freedom, and the two-parameter step model keeps
  4. Profile-likelihood intervals of s and A follow the method above.
- Anchor circuits. The prepared-1 circuit with no wait is byte-identical
  across batches (`t1-0.cq` of batch 01, `readout-1.cq` of batches 00 and 05;
  the three files have one sha256), and the prepared-0 circuit is as well
  (`x90-0.cq` of batch 03, `readout-0.cq` of batches 00 and 05). Each qubit
  therefore holds a prepared-1 level at three job times and a prepared-0 level at
  three job times, ordered by the finish time of each job. Batch 02 holds no
  anchor, so the anchors measure level shifts between its neighbors in time (01
  and 03) and bound a shift at 02 by interpolation; they do not measure the
  step itself. The anchor shift d0 is the batch-03 prepared-0 level minus the
  level interpolated linearly in time between batches 00 and 05, and d1 the
  batch-01 prepared-1 level minus the same interpolation of the prepared-1
  pair, each with its binomial standard error (16,384 shots in batches 00 and 05
  and 8,192 in batches 01 and 03) and its z. The comparison of a fitted step
  with the anchors uses d0, because the batch-02 points sit near the ground
  state, and reports d1 beside it.
- Prediction. The three-parameter step model reaches chi-square / dof at most 3
  on at most 7 of 17 qubits (about the same as the two-parameter model, 3 of
  17), because a constant offset of the three longest delays cannot produce the
  early dip at 5 us and the 80 us excess together. The anchor shifts d0 and d1
  stay below 0.015 in magnitude on at least 15 of 17 qubits (the opening-to-closing
  drift of the readout pair is at most 0.0136), and the pooled sum of z squared
  over the 17 qubits stays within the chi-square range of 17 degrees of freedom
  (p between 0.01 and 0.99). The fitted step then exceeds |d0| by more than 3
  standard errors on at least 4 of the 6 qubits whose two-parameter step is 0.02
  or more (qubits 2, 9, 11, 12, 14 and 15).
- Verdict rules, fixed now. Supported: chi-square / dof at most 3 on at least
  12 qubits for the three-parameter model and, on at least 12 qubits, a fitted
  step within 2 standard errors of d0 (combined). Refuted as the sufficient
  explanation: chi-square / dof at most 3 on at most 7 qubits; the step can
  still contribute where the anchors show a shift. Refuted as a level shift:
  the model fits (at least 12 qubits) while the anchors place |d0| more than 3
  standard errors below the fitted step on more than 6 qubits (the step then
  absorbs shape). Otherwise not separable from the decay shape with this
  design. A design that separates the two runs each delay in both batches
  (interleaved within one batch), as in "What would decide" below.
- Backend state at execution. The retained files carry the backend status at
  submission only (`backend_status_at_submit` of each batch); a status at the
  start of execution is not retained. The report states what the job
  timestamps bound.

## T1 shape: results

`scripts/qi_tuna17_t1_shape.py` refits the retained counts (no provider read) with
the binomial-likelihood models of `gororoba_quantum/qi_decay_models.py` and writes
`results/quantum_inspire/characterization_tuna_17_t1_shape_analysis.json`
(command: `"$PYTHON" scripts/qi_tuna17_t1_shape.py OUT RUN_DIR...` over the six
run directories of the series; the interpreter is the analysis one with numpy 2.5.4
and scipy 1.18.1). The retained `--analyze` rows and the case's verdict rule are
unchanged. The records use the mean of the opening and closing readout pairs
unless a row says otherwise. The 80 us population is the last of six points, and
the intervals are profile likelihoods (68.3%), also given widened by
sqrt(chi-square / dof).

| Hypothesis | Measured | Verdict |
|---|---|---|
| H1 readout floor | chi-square / dof at most 3 on 2 of 17 qubits for the opening, mean and time-interpolated pair and for the joint likelihood, and on 1 of 17 for the closing pair (median 34.8, range 1.4 to 465 for the mean pair) | refuted |
| H2 delay unit or idle gate | wait lines read N on all 17 qubits for all six delays (`results.json` of the jobs carries no cycle time, so 20 ns per cycle rests on `cases.json` of the case and [cqasm.md](cqasm.md)); execution time rises 4.7 +- 15.0 ns per cycle per shot against 20 nominal; a common stretched exponent (0.90; per qubit 0.58 to 1.01) and a common delay offset (1.70 us; per qubit 0 to 13.5 us) are rejected (likelihood ratios 2310 and 2504 on 16 degrees of freedom, p below 1e-300) | refuted as one global calibration; realized delay undecided |
| H3 two-rate decay | chi-square / dof at most 3 on 3 (biexponential), 2 (plateau) and 4 (stretched) of 17 qubits against 12 predicted; AICc falls by more than 4 on 12, 13 and 9 | not supported as a 3-parameter shape; tail excess real |
| H4 drift | readout drift 0.001 to 0.014 (median 0.004); interpolated pair leaves chi-square / dof at most 3 on 2 of 17; a batch step is positive on 16 of 17 and its likelihood ratio exceeds 4 on 13 | drift of the readout pair cannot account for the misfit; the batch step is tested in "Batch-offset test: results" (H4b) |
| H5 crosstalk | Spearman rho 0.15 (p 0.56) with degree and -0.23 (p 0.37) with the neighbor mean; coupled against uncoupled pairs |z| at most 2.32 and Welch p at least 0.089 on all 10 circuits; overdispersion 0.99 to 1.03 | refuted within this series; crosstalk undecided |
| H2b delay offset (after the fact) | chi-square / dof at most 3 on 2 of 17; AICc gain over 4 on 9 | common offset refuted |
| H6 T1 distribution | sigma median 0.30 but range 0.01 to 1.33 (predicted 0.2 to 0.8); AICc gain over 4 on 12 (predicted at least 12); chi-square / dof at most 3 on 3 of 17 (predicted fewer than 12) | the AICc and chi-square clauses held, the sigma range did not; not sufficient as the shape |
| Standard-error mechanism | the factor sqrt(chi-square / dof) (`se_scale`) is 1.4 to 22 (median 5.8) for the retained chi-square / dof of 1.9 to 496 (the refit's is 1.4 to 465); the retained standard error of 0.12 to 0.31 us times that factor is 0.25 to 4.6 us (`scaled_se_us`); the spread over six analyses (retained log fit, four readout choices, joint likelihood) exceeds the scaled error on 1 of 17 | supported |

Predictions that failed. H3 predicted chi-square / dof at most 3 on at least 12
qubits for a 2- or 3-parameter model and reaches 2 to 4. H4 predicted a batch
step under 2 standard errors on at least 9 qubits and reads above on 13 (the
second clause of its falsifier); its drift prediction held. H6 predicted sigma
0.2 to 0.8 and reads 0.01 to 1.33. H2 predicted an execution-time slope within
25% of 20 ns per cycle per shot and reads 4.7 ns (+- 15.0), which the error
makes uninformative, and H2b predicted a common offset and reads a rejected one
(recorded after the fact). The H1, H5 and standard-error predictions held.

### Observations

- The single exponential leaves two residuals that share a sign across qubits:
  the 5 us point lies below the fit on 14 of 17 qubits (median -2.5 standard
  deviations, sign test p = 0.013) and the 80 us point above it on 16 of 17
  (median +4.7, p = 0.0003). The 0, 10, 20 and 40 us points show no coherent sign
  (median |z| at most 1.3). A fast loss in the first microseconds followed by a
  slower tail is the pattern these six delays suggest and cannot establish
  (in "Batch-offset test: results" the anchors exclude a level step as the source
  of the larger steps on 6 qubits and leave it open on the other 11); neither lengthening alone (stretched exponent below 1
  on 10 of 17 qubits at the scaled interval) nor a plateau alone (nonzero on 11
  of 17) describes it.
- The misfit concentrates on a few qubits. Qubits 8 and 13 fit a single
  exponential (chi-square / dof 1.4 and 2.2). Qubits 2, 3 and 4 stay above 40 for
  the single exponential and above 13 under every other model; qubits 14 and 15
  fall from 465 and 166 to 2.5 (stretched) and 3.7 (biexponential). No model wins
  across qubits: seven of the eight models are the lowest-AICc model on some
  qubit (batch step on 5, plateau on 4, delay offset on 3, biexponential on 2,
  single, free amplitude and stretched on 1 each; the lognormal on none).
- The refit leaves T1 unchanged: 12.8 to 31.8 us (median 22.5) against the
  retained 13.2 to 32.2 (median 22.9). The retained log fit differs from the
  direct fit by up to 25% (qubit 14: 23.6 against 17.8 us); the retained fit
  weights the logarithm of each point and leaves its intercept free, where the
  direct fit anchors the 0 us point at the measured e11.
- The pre-registered H1 readout variants agree because the retained analyzer
  already applies the same linear map (e01, e11 from the mean pair). The joint
  likelihood, which carries the covariance of the shared readout pair, widens
  the nominal T1 interval by 3% to 12% (32,768 readout shots per state); it
  cannot account for chi-square / dof of 1.4 to 465.
- The delay offset of H2b, fitted per qubit, reaches 5.8, 13.5 and 6.4 us on
  qubits 2, 14 and 15 and stays at most 0.5 us on qubits 1, 4, 5, 6, 8, 10, 13
  and 16, so it follows the misfit and is not a shared overhead. The execution-time slope cannot decide the
  realized delay: its standard error (15 ns per cycle per shot) is as large as
  the nominal 20 ns.
- The overdispersion index of the 17-bit records (variance of the number of
  excited qubits over the sum of binomial variances) is 0.99 to 1.03 at every
  delay, so decay events of different qubits are independent to within 3% and
  no common-mode burst hides in the counts.

### Batch-offset test: results

`scripts/qi_tuna17_batch_step.py` writes
`results/quantum_inspire/characterization_tuna_17_batch_step_analysis.json` from the
retained counts (no provider read; the output is byte-identical at 1, 8 and 32
workers). The models are the registered ones: `single_step` (T1 and an additive
step on batch 02, 4 degrees of freedom) and `single_amplitude_step` (T1, a free
amplitude and the step, 3 degrees of freedom), on the mean readout pair.

- Fit quality. The three-parameter model reaches chi-square / dof at most 3 on 3
  of 17 qubits (0, 8 and 13; median 25.6, range 1.2 to 220), the count of the
  two-parameter model. The fitted amplitude is 0.99 to 1.00, so the free
  zero-delay level adds nothing; the step is positive on 16 of 17 qubits (median
  0.0092; 0.0003 below zero to 0.109) and its profile interval excludes zero on 15
  of 17; AICc falls by more than 4 against the single exponential on 10 of 17. The
  prediction (at most 7 qubits clear) held. The plateau, which is also a
  late-delay offset, has the lower AICc than the step on 6 qubits and the step the
  lower on 11 (median step minus plateau -2.5), so the two descriptions of the
  three longest delays are not separated.
- Anchors. Two circuits repeat byte for byte in three batches (sha256 of the
  circuit text): the prepared-1 circuit (`readout-1` of batch 00 finished
  12:21:40Z, `t1-0` of batch 01 12:25:32Z, `readout-1` of batch 05 12:33:52Z) and
  the prepared-0 circuit (`readout-0` of batch 00 12:21:51Z, `x90-0` of batch 03
  12:29:53Z, `readout-0` of batch 05 12:33:41Z). The shift d of the middle job
  against the time interpolation of the outer two is
  -0.0028 to +0.0056 (median +0.0009, standard error 0.001 to 0.003) for the prepared-0
  circuit and -0.0145 to +0.0060 (median 0.0000, standard error 0.0015 to 0.0035) for the
  prepared-1 circuit. No shift exceeds 0.015 (prediction held). The prepared-0 shifts have
  `|z|` above 2 on 2 qubits (6 and 11), none above 3, a pooled sum of z squared of
  23.5 on 17 degrees of freedom (p 0.13, prediction held) and are positive on 13 of
  17 (sign test p 0.049). The prepared-1 shifts have `|z|` above 2 on 3 qubits (6, 11,
  15) and above 3 on qubit 6 (z -6.2), and a pooled sum of 71.0 (p 1.5e-8), so the
  registered pooled clause failed for the prepared-1 circuit: levels differ from
  job to job by more than binomial noise. The three-level homogeneity statistic
  pools to 110.9 (prepared 0) and 161.2 (prepared 1) on 34 degrees of freedom, which
  includes the opening-to-closing readout drift of at most 0.0136 already
  measured.
- Steps against anchors. On the six qubits whose step is 0.02 or more (2, 9, 11, 12,
  14, 15; 0.028 to 0.109) the step exceeds the prepared-0 shift by more than 3
  standard errors on 6 of 6 (prediction: at least 4), and each step exceeds the
  largest anchor shift of any qubit (0.0145) by a factor of 1.9 to 7.5. Over all 17
  qubits the step exceeds the prepared-0 shift by more than 3 nominal standard
  errors on 9 and lies within 2 on 7; the nominal errors are understated where the
  model misfits, and with the profile widened by sqrt(chi-square / dof) the count
  above 3 falls to 3 and 13 lie within 2.
- Verdict. Step supported: no (3 of 17 clear, against the 12 required). Step
  refuted as the sufficient explanation: yes (3 of 17 clear, at most 7 required),
  whatever the anchors show. Step as a level shift: for the six qubits with a step of
  0.02 or more, a level shift of the size the anchors measure (at most 0.0145) does
  not produce the step, so the step there describes the shape of the three longest
  delays; for the other 11 qubits the fitted step (at most 0.013) is of the size of
  the batch-to-batch level scatter (anchor shifts up to 0.0145), so a level shift is
  not excluded and is not separable from the tail with this design. The anchors
  bound level shifts between the neighbors of batch 02 in time (batches 01 and 03)
  and carry no job of batch 02, so a level that moved only during that batch is not
  seen. An interleaved design (each delay in both batches) separates the two.

### What would decide

- A dense scan of 0 to 10 us (about 0.5 us steps) tells a fast first-microsecond
  loss, a coherent exchange with a defect and an aliased oscillation apart; the
  6 delays here cannot.
- Each delay run twice in interleaved order across batches separates the batch
  step (positive on 16 of 17 qubits, aliased with delay because batch 02 holds
  the three longest delays; "Batch-offset test: results" bounds it with anchors
  and cannot resolve it below 0.02) from a shape effect.
- A scan to about 300 us bounds the tail scale that is open above on 8 of 17
  qubits.
- The single-qubit arm that the case calls for (see "Open") separates a neighbor
  effect from the qubit's own T1: this series cannot, since all 17 qubits are
  excited together.
- The parameter bounds force a positive second-component weight, so the sign of
  a second scale cannot be tested here; the residual sign pattern is the only
  sign evidence.

### Corrected T1

No registered model fits, so T1 is the effective single-exponential value with
intervals widened by sqrt(chi-square / dof):

| Qubit | T1 fit (us) | 68% interval | widened interval | chi-square / dof | joint-likelihood chi-square / dof | retained fit (us) |
|---|---|---|---|---|---|---|
| 0 | 17.2 | 17.0 to 17.3 | 16.8 to 17.6 | 7.6 | 6.8 | 17.1 +- 0.2 |
| 1 | 19.8 | 19.6 to 20.0 | 19.4 to 20.2 | 6.1 | 5.8 | 19.6 +- 0.2 |
| 2 | 23.9 | 23.7 to 24.1 | 21.3 to 26.9 | 215.3 | 212.7 | 24.8 +- 0.2 |
| 3 | 12.8 | 12.7 to 12.9 | 11.9 to 13.7 | 64.9 | 63.3 | 13.2 +- 0.1 |
| 4 | 24.2 | 24.0 to 24.4 | 22.7 to 25.8 | 57.8 | 57.2 | 24.9 +- 0.2 |
| 5 | 20.5 | 20.3 to 20.7 | 20.0 to 21.1 | 10.1 | 9.9 | 20.4 +- 0.2 |
| 6 | 15.9 | 15.8 to 16.1 | 15.3 to 16.6 | 22.4 | 20.3 | 16.2 +- 0.2 |
| 7 | 27.3 | 27.0 to 27.5 | 25.9 to 28.8 | 34.8 | 34.6 | 27.7 +- 0.3 |
| 8 | 19.0 | 18.8 to 19.1 | 18.8 to 19.2 | 1.4 | 1.4 | 19.0 +- 0.2 |
| 9 | 22.0 | 21.8 to 22.2 | 20.7 to 23.3 | 43.2 | 42.0 | 22.1 +- 0.2 |
| 10 | 31.8 | 31.5 to 32.0 | 30.7 to 32.9 | 14.7 | 14.3 | 32.2 +- 0.3 |
| 11 | 25.3 | 25.1 to 25.5 | 24.0 to 26.7 | 38.3 | 34.9 | 26.4 +- 0.2 |
| 12 | 23.0 | 22.8 to 23.2 | 21.9 to 24.2 | 37.7 | 37.3 | 22.9 +- 0.2 |
| 13 | 23.9 | 23.7 to 24.1 | 23.6 to 24.2 | 2.2 | 2.1 | 23.8 +- 0.3 |
| 14 | 17.8 | 17.6 to 18.0 | 14.4 to 22.0 | 465.1 | 362.9 | 23.6 +- 0.2 |
| 15 | 22.9 | 22.7 to 23.1 | 20.4 to 25.7 | 165.6 | 156.1 | 24.7 +- 0.2 |
| 16 | 22.5 | 22.3 to 22.7 | 22.0 to 23.1 | 7.8 | 7.5 | 22.2 +- 0.2 |

T1 spans 12.8 to 31.8 us (median 22.5). The widened half-widths of this table
(the profile interval of the refit's `single` model widened by the square root of the
refit's chi-square / dof of 1.4 to 465) run 0.20 to 3.8 us (median 1.1). They differ
from the 0.25 to 4.6 us of the standard-error row above (`scaled_se_us`: the retained
log fit's standard error of 0.12 to 0.31 us times the square root of its own chi-square /
dof of 1.9 to 496), because the refit fits P1 directly and the retained fit its
logarithm; both stand against the retained standard errors of 0.1 to 0.3 us. The
timescale of the exponential component under the plateau model has median 20.5
us (11.1 to 29.0) and the median of the lognormal model is 21.3 us, so the
model choice moves a qubit's T1 by about 10%, and by 40% on qubit 14.

### Model table

Pearson chi-square / dof of each model on the mean readout pair (6 points; the
dof of the models with 1, 2 and 3 parameters are 5, 4 and 3), and the model of
the lowest AICc:

| Qubit | single | free amplitude | delay offset | batch step | plateau | stretched | lognormal | biexponential | lowest AICc |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 7.6 | 8.8 | 4.1 | 1.6 | 3.1 | 2.4 | 2.0 | 2.9 | single_step |
| 1 | 6.1 | 7.6 | 7.6 | 6.2 | 4.6 | 7.4 | 6.0 | 6.1 | plateau |
| 2 | 215.3 | 248.4 | 30.4 | 166.4 | 232.2 | 93.7 | 147.6 | 40.5 | delay_offset |
| 3 | 64.9 | 75.9 | 13.9 | 71.3 | 75.8 | 32.7 | 51.2 | 18.6 | delay_offset |
| 4 | 57.8 | 71.5 | 72.3 | 70.3 | 58.0 | 72.0 | 65.8 | 77.4 | plateau |
| 5 | 10.1 | 12.6 | 12.6 | 12.1 | 9.9 | 12.7 | 11.7 | 13.2 | plateau |
| 6 | 22.4 | 19.3 | 28.0 | 27.7 | 26.5 | 27.9 | 28.0 | 35.3 | single_amplitude |
| 7 | 34.8 | 42.7 | 27.5 | 42.5 | 42.3 | 34.9 | 39.9 | 36.6 | delay_offset |
| 8 | 1.4 | 1.7 | 1.3 | 1.8 | 1.8 | 1.7 | 1.8 | 2.4 | single |
| 9 | 43.2 | 51.1 | 38.2 | 27.2 | 40.9 | 33.2 | 35.3 | 42.6 | single_step |
| 10 | 14.7 | 17.6 | 18.3 | 16.7 | 9.4 | 16.7 | 13.1 | 12.5 | plateau |
| 11 | 38.3 | 35.5 | 18.5 | 6.5 | 17.1 | 8.2 | 8.2 | 9.0 | single_step |
| 12 | 37.7 | 46.0 | 12.8 | 19.9 | 34.3 | 13.8 | 22.3 | 13.2 | biexponential |
| 13 | 2.2 | 2.6 | 2.1 | 0.9 | 1.6 | 1.8 | 1.7 | 2.1 | single_step |
| 14 | 465.1 | 503.8 | 45.1 | 45.7 | 102.4 | 2.5 | 3.7 | 8.6 | stretched |
| 15 | 165.6 | 190.1 | 5.6 | 60.6 | 105.3 | 10.7 | 29.8 | 3.7 | biexponential |
| 16 | 7.8 | 9.7 | 7.6 | 4.3 | 4.7 | 7.2 | 6.4 | 6.2 | single_step |

Parameters of the shape models (the intervals widen the profile by
sqrt(chi-square / dof); "open" marks an end at a parameter bound; the biexponential
fast scale sits at its 0.5 us bound on qubits 2, 3 and 7, and the slow scale at its
bound of 1000 times the fast one on qubits 1, 4, 5, 6, 10, 13 and 16, where its
weight is 0.01 to 0.04):

| Qubit | plateau T (us) | plateau fraction | stretched exponent | lognormal sigma | biexp. fast (us) | biexp. slow / fast | biexp. slow weight |
|---|---|---|---|---|---|---|---|
| 0 | 16.6 | 0.009 (0.006 to 0.013) | 0.95 (0.93 to 0.96) | 0.30 | 13.6 | 1.8 | 0.36 |
| 1 | 19.2 | 0.010 (0.004 to 0.016) | 0.99 (0.96 to 1.02) | 0.21 | 19.2 | 1000 (bound) | 0.01 |
| 2 | 21.3 | 0.040 (open to 0.107) | 0.78 (0.70 to 0.87) | 0.74 | 0.5 | 62.6 | 0.83 |
| 3 | 12.5 | 0.007 (open to 0.024) | 0.85 (0.79 to 0.91) | 0.48 | 0.5 | 31.3 | 0.84 |
| 4 | 22.5 | 0.025 (open to 0.053) | 0.99 (0.91 to 1.08) | 0.27 | 22.5 | 1000 (bound) | 0.02 |
| 5 | 20.0 | 0.010 (0.000 to 0.021) | 1.00 (0.96 to 1.04) | 0.18 | 20.0 | 1000 (bound) | 0.01 |
| 6 | 15.7 | 0.006 (open to 0.019) | 1.01 (0.94 to 1.08) | 0.02 | 15.7 | 1000 (bound) | 0.01 |
| 7 | 26.6 | 0.011 (open to 0.046) | 0.94 (0.88 to 1.01) | 0.28 | 0.5 | 58.8 | 0.95 |
| 8 | 19.0 | 0.000 (open to 0.002) | 0.99 (0.98 to 1.01) | 0.01 | 19.0 | 31.3 | 0.00 |
| 9 | 20.5 | 0.023 (0.002 to 0.047) | 0.91 (0.85 to 0.97) | 0.42 | 5.6 | 4.5 | 0.87 |
| 10 | 29.0 | 0.039 (0.019 to 0.059) | 0.98 (0.93 to 1.02) | 0.31 | 29.0 | 1000 (bound) | 0.04 |
| 11 | 22.2 | 0.046 (0.028 to 0.065) | 0.88 (0.85 to 0.90) | 0.53 | 9.3 | 3.5 | 0.75 |
| 12 | 21.5 | 0.022 (0.003 to 0.042) | 0.90 (0.86 to 0.93) | 0.43 | 3.7 | 7.1 | 0.89 |
| 13 | 23.4 | 0.008 (0.003 to 0.014) | 0.98 (0.96 to 0.99) | 0.20 | 23.4 | 1000 (bound) | 0.01 |
| 14 | 11.1 | 0.133 (0.094 to 0.172) | 0.58 (0.56 to 0.59) | 1.33 | 4.7 | 9.4 | 0.51 |
| 15 | 18.0 | 0.084 (0.037 to 0.133) | 0.74 (0.71 to 0.77) | 0.90 | 2.9 | 11.3 | 0.78 |
| 16 | 21.6 | 0.016 (0.008 to 0.024) | 0.97 (0.94 to 1.00) | 0.26 | 21.6 | 1000 (bound) | 0.02 |

## X90 repetition ladder

Corrected P(0) after 32, 128 and 256 pulses (`ladder_clears` requires each
at least 0.5). The ladder bounds no single-pulse error (CASE.md); P(0) is
periodic in a coherent over-rotation, so no amplitude or phase error per
pulse follows from these rows and none is reported.

| Qubit | P(0) at 32 | at 128 | at 256 | clears | predicted | agrees |
|---|---|---|---|---|---|---|
| 0 | 0.914 | 0.485 | 0.532 | false | none | unpredicted |
| 1 | 0.923 | 0.181 | 0.640 | false | open | open |
| 2 | 0.953 | 0.708 | 0.235 | false | fail | yes |
| 3 | 0.537 | 0.848 | 0.710 | true | none | unpredicted |
| 4 | 0.940 | 0.551 | 0.192 | false | none | unpredicted |
| 5 | 0.389 | 0.767 | 0.530 | false | clear | no |
| 6 | 0.635 | 0.689 | 0.694 | true | fail | no |
| 7 | 0.923 | 0.463 | 0.135 | false | clear | no |
| 8 | 0.944 | 0.844 | 0.834 | true | fail | no |
| 9 | 0.916 | 0.633 | 0.291 | false | fail | yes |
| 10 | 0.892 | 0.088 | 0.840 | false | none | unpredicted |
| 11 | 0.012 | 0.781 | 0.417 | false | none | unpredicted |
| 12 | 0.648 | 0.766 | 0.531 | true | none | unpredicted |
| 13 | 0.969 | 0.925 | 0.824 | true | clear | yes |
| 14 | 0.029 | 0.843 | 0.713 | false | clear | no |
| 15 | 0.964 | 0.875 | 0.799 | true | clear | yes |
| 16 | 0.901 | 0.199 | 0.559 | false | none | unpredicted |

- `ladder_clears` is true on qubits 3, 6, 8, 12, 13 and 15 and false on the
  other 11. Of the nine qubits with a retained prediction (qubit 1 open), four
  agree (2, 9, 13, 15) and five do not: qubits 6 and 8 clear where a failure
  was predicted, and qubits 5, 7 and 14 fail where a clear was predicted.
  Qubits 0, 4, 10, 11 and 16 fail and qubits 3 and 12 clear without a
  retained prediction.
- Per the case, a failure on a qubit predicted to clear or unpredicted opens a
  single-qubit-arm case to separate crosstalk from the qubit's own pulse; this
  record opens none. Qubits 11 and 14 read 0.012 and 0.029 after 32 pulses and
  0.78 and 0.84 after 128, the pattern of a coherent over-rotation near a
  ladder period (hypothesis; this series holds no arm that tests it).

## Comparison with the QX twin

The twin returned exactly the noiseless outcome of every circuit: P(1|0) = 0
and P(1|1) = 1 on all 10 qubits in both pairs, corrected populations of 1 at
every T1 wait and every ladder count, `ladder_clears` true and no T1 fitted
(a flat decay), as the twin's `CASE.md` states. Its execution time was 178.2
s against the 44.2 s of the twin's `prediction.json`, which its `CASE.md` calls an
upper figure for the emulator: the 2,565-line `x90-64` text
took 109.5 s, `x90-32` 54.8 s and `x90-8` 13.8 s at 1,024 shots, so the
emulator's time grows with the gate count while the model of
[usage.md](usage.md) carries no gate term. The Tuna-17 jobs ran 6.0 to 11.3 s
each: 10.2 s for `x90-64` and 6.0 s for `x90-0` at 8,192 shots.

## Open

- No claim cites the twelve new acquisitions; the claim that interprets this
  series is a later change.
- The single-qubit arm that the case's rule calls for on qubits 5, 7 and 14
  (predicted to clear, failed) and on 0, 4, 10, 11 and 16 (unpredicted failures)
  is proposed in
  [issue 941](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/941).
  It is also the control that removes the neighbor-state candidate of the T1
  shape. The written follow-up case, with interleaved T1 rounds and a q12 phase
  scan beside the drive-context crosstalk arm (the single-qubit arm stays the
  separate follow-up of issue 941), is
  [characterization_interleaved_tuna_17](../../../results/quantum_inspire/cases/characterization_interleaved_tuna_17/CASE.md).
- The T1 shape stays open as a mechanism: the registered explanations do not
  restore the single exponential, a batch step is refuted as the sufficient
  explanation, excluded as a level shift on the 6 qubits with a step of 0.02 or
  more and not separable from the tail on the other 11, the decisive
  measurements are a dense 0 to 10 us scan and an interleaved repeat of each delay
  ("What would decide"), and the
  case's verdict rule keeps its registered form.
- The retained-context document reads these analysis rows: a newer series
  replaces a qubit's `readout` and `implied_t1` (the dashboard's figures) and
  keeps the earlier row in `baseline_readout` and `baseline_implied_t1`, where
  `scripts/qi_tuna17_characterization_cases.py` reads its tolerance baseline;
  `--analyze` over the six runs with the regenerated document reproduces the
  retained analysis rows byte for byte. The dashboard column "Implied T1" shows
  the series' fitted T1 for these qubits, a single-exponential fit and no longer
  a two-run difference.
- Twenty jobs of the usage ledger, 1742623 to 1742642, have no retained run:
  QX emulator jobs (backend type 1) of 2,048 shots in four batch jobs of five
  (958991 to 958994), created 2026-11-15 between 18:48 and 18:54 UTC, all
  completed with 0 credits and 0.004 to 0.80 s of execution. The ledger records
  no circuit names, and no retained run directory names these ids, so the ledger
  alone does not identify their owner; nothing here changes them.

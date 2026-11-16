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
  commits come from the run host's collector logs and session notes, which
  this change does not retain; every other timestamp here is in the retained
  `submission.json` and `results.json` files.
- Batches 01 to 05 were submitted from 12:22:32Z to 12:32:25Z and collected by
  12:34:01Z. The opening readout pair therefore executed 12 min before the
  closing pair (12:21:51Z and 12:33:52Z), and the T1 waits ran between them,
  in two batches 2 min apart (12:25Z and 12:27Z).
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
  arm in this series separates the two.

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
- CASE.md "Record" asks the retaining change to extend
  `scripts/qi_retained_context.py` to read these analysis rows so the
  dashboard's table shows the new date; that reader is not extended here,
  because the analyzer's default `--retained` input is that document.
- `CASE.md` still reads "nothing has been submitted"; it is not edited here.

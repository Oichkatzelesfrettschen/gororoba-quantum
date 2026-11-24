# Tuna-17 matched-response analysis

This record freezes the analysis of the unsubmitted
[matched-response series](tuna17-zero-divisor-matched-response.md) before any shot exists.
The approved circuits are those of the
[region-2 selector q11 proposal](tuna17-matched-response-region2-selector-q11.md).
`scripts/qi_matched_response_analysis.py` reads the three collected batches and calls
`gororoba_quantum/qi_matched_response.py`; neither contacts a provider.

## Decision rule

- The primary statistic is the residual `F_R2 - B_R1 + F_R1 - D_R2` of the six readout-corrected
  selector-zero probabilities, in the order of `primary_contrast.order` of the proposal, with weights
  `(0, 0, -1, 1, 1, -1)` and the standard error of the full 6 x 6 covariance below.
- The common-affine response (batch offsets, one fixed region offset, one visibility) is rejected when
  the corrected residual has `abs(z) >= 3`.
- The raw residual, built from uncorrected selector-zero frequencies with the witness covariance alone,
  is reported beside the corrected one.
- A rejection does not identify drift, crosstalk or a control-error channel. A compatible residual leaves
  region-dependent visibility and time-dependent region offsets unresolved: with visibilities `v1` and
  `v2` in the two regions the residual is `(v2 - v1) / 2`.
- The residual equals `(v2 - v1) / 2` for region-dependent visibility and equally `(w2 - w1) / 2` for a
  visibility that drifts between batches 1 and 2, so it separates neither.
- The regions run 81 and 96 controlled-Z gates ([successor proposal](tuna17-matched-response-region2-selector-q11.md)),
  so a residual from depth alone is predicted at about -0.024 (z about -2.9) and a rejection has
  probability near one half; a rejection is a statement about the device response, not about the zero-divisor
  property.
- The per-region half-spacings `(B_r - D_r) / 2` span two batches and keep their batch offsets, so they
  are secondary.

## Limit of the decision rule

The standard error of the contrast, about 0.0084 for the matched series, is shot noise only. A region-by-batch
interaction (one region drifting between batches) does not cancel in the residual, and enters it as the sum of
four independent cell terms, so its variance under the null is `4 s^2 + 0.0084^2` for a cell standard
deviation `s`. The only retained design that estimates `s` is the three-region Latin run
(`results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17/analysis.json`, nine readout-corrected
cells of 16384 shots, circuit by region). Fitting circuit, region and one visibility times the ideal leaves 3
degrees of freedom with mean square 3.6e-4; subtracting the shot variance 1.9e-5 gives `s` = 0.018, with a 90
percent interval of 0.011 to 0.055 from the chi-squared law on 3 degrees of freedom. The fit also absorbs any
non-affine case response, so `s` is an upper estimate of the interaction. The residual standard deviation under
the null is then 0.038 (0.023 to 0.11), and the rate of false rejection at `abs(z) >= 3` with z computed from
0.0084 is about 0.50 (0.28 to 0.82); at s = 0 the rate is 0.0027. The notes also retain a depth-9 batch-to-batch
scatter of about 0.03 and a 50 Hz line in the shot record of deep circuits
([tuna-17.md](../notes/quantum_inspire/tuna-17.md)); both point the same way. The rule is unchanged: a rejection
at `abs(z) >= 3` is expected from drift alone about half the time, so it supports no inference about the
common-affine response without an interaction estimate from the same series, which three batches of two regions
leave at one degree of freedom, the residual itself.

## Binding

The analysis accepts only the approved circuits. It carries the order of the six labels as a constant and
refuses a proposal whose `primary_contrast.order` differs. The script computes the sha256 of
`proposal.json`, of each batch `cases.json` and of each of the nine circuit files from the proposal
directory, and compares them with the digests of the manifest and circuit files that each collected run
directory holds (`qi_records.load_run`, validated by `validate_run` against the bytes the submission
receipt uploaded). A run whose manifest or circuits differ from the proposal is refused. The digests enter
the analysis output under `binding`.

## Covariance

- Each circuit is one multinomial sample. The two selector bits of a circuit form a joint outcome, so the
  two regions of one witness circuit share every shot and carry the covariance `(f11 - m1 m2) / n` of
  their read-1 frequencies.
- A region's corrected estimate is `v = (m1 - mw) / (m1 - m0)` with `mw`, `m0` and `m1` the read-1
  frequencies of its selector in the witness, readout-0 and readout-1 circuits of the batch. The two
  estimates of a batch share both readout circuits, and the delta method propagates their sampling error
  into both through the gradient of `v`.
- Batches are independent submissions, so the covariance is block-diagonal with one 2 x 2 block per batch.
  The delta method is a first-order approximation; a nonpositive readout contrast `m1 - m0` is refused.

## Refusals

The analysis refuses a batch whose circuit lacks collected shots, whose shot count differs from the
manifest, whose shots are not 17-bit strings, whose manifest differs from the proposal, or whose order
lacks a case the manifests carry.

## Validation

`tests/scripts/test_qi_matched_response_analysis.py` runs on synthetic shots: the null model gives an
unbiased residual below the threshold, a region-dependent visibility gives `(v2 - v1) / 2`, the
covariance is symmetric and positive semidefinite and its same-shot entries match a Monte Carlo estimate,
a swapped order, a changed witness byte, a changed manifest and incomplete batches are refused.

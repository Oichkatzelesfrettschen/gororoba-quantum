# Tuna-17 matched-response analysis

This record freezes the analysis of the unsubmitted
[matched-response series](tuna17-zero-divisor-matched-response.md) before any shot exists.
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
- The regions run 81 and 105 controlled-Z gates, so a rejection is expected from depth alone and is a
  statement about the device response, not about the zero-divisor property.
- The per-region half-spacings `(B_r - D_r) / 2` span two batches and keep their batch offsets, so they
  are secondary.

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

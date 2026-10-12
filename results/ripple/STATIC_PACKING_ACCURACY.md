# Practical accuracy audit for the packed algebra acquisitions

The static acquisitions test whether calibrated implementations retain useful
interference and coefficient-normalized norm patterns under the declared
neighboring workloads. The completed folded-QPE jobs and the proposed correction
pilot cannot answer those questions: their circuits, physical patches, observables and controls
differ. Ripple and rank therefore retain separate scientific admission after
the correction decision, with ceilings of 80 and 60 seconds respectively.

The practical packing tolerance is 10 percent of each control's single-arm
score range. That coarse tolerance supports inspection of large distribution
features and conspicuous packing distortion. It does not certify high-fidelity
computation, a one-percent engineering tolerance, or arbitrary algorithm reuse.
The tolerance is fixed before observing the new hardware outcomes. The
existing 0.08 precision setting remains the planning contract in its recorded
score units; the normalized tolerance below is a separate interpretation rule.

For every preregistered packed-minus-isolated control, let `w` be its recorded
score vector, `R = max(w) - min(w)`, and `D = E[w(packed)] - E[w(isolated)]`.
The two arms use the same score vector and physical lane. Normalize the
collector's simultaneous confidence interval `[L, U]` to `[L/R, U/R]`.
Apply the following rules to every control, retaining the complete denominator:

- Coarse equivalence: `L/R > -0.10` and `U/R < 0.10`.
- Positive practical distortion: `L/R > 0.10`.
- Negative practical distortion: `U/R < -0.10`.
- Unresolved: every other interval, including a boundary equality.
- Withheld: an existing count, identity, calibration or inference gate fails.

For the normalized score `f = (w - min(w))/R`, every outcome has
`0 <= f <= 1`, so `|D/R| <= TV(packed, isolated)`. A certified practical
distortion therefore establishes a total-variation distance exceeding 0.10.
Scalar equivalence supplies no upper bound on that distance: other outcome
redistributions can cancel in the chosen score. The result concerns the
observed arms; drift and neighboring activity remain competing explanations.

These classifications reuse the existing simultaneous coverage and introduce
zero newly measured endpoints. Each family's alpha remains 0.05 across its complete
endpoint set. A joint 95-percent claim across both families remains outside
the contract. Independent stationary repetitions within each PUB remain an
assumption; shared-shot components may be dependent. Equal shot indices from
different PUBs remain separate observations. Changed neighboring activity,
execution order and drift limit causal attribution to crosstalk.

The [endpoint audit](static-practical-accuracy-admission.json) binds every
control name, score range, planned interval width and record identity. At the
frozen allocation, ripple's Bernoulli packing controls have normalized
half-width 0.074671; rank controls have 0.068679. Consequently, both coarse
equivalence and practical distortion are possible outcomes of those controls.
Their interval centers must lie within approximately 0.025329 and 0.031321
of zero, respectively, to establish equivalence. Centers beyond approximately
0.174671 and 0.168679 in magnitude establish practical distortion.

Weighted Design C controls retain their actual score ranges. The dimension-32
control has range 0.5625; the dimension-16 control has range 0.25. Applying
raw plus-or-minus 0.10 to the latter would permit 40 percent of its score
range. The dimension-16 control's normalized half-width is 0.112006, so the
frozen allocation cannot establish ten-percent equivalence for that control.
It can establish practical distortion when its normalized center exceeds
approximately 0.212006 in magnitude. Retain the expected under-resolution;
never widen the tolerance after viewing outcomes to obtain a passing label.

The execution coordinator adopts this prospective criterion as the static
scientific case, subject to the remaining execution gates. The endpoint audit
retains its original proposal status; the coordination ledger records adoption
separately. The case supports an accuracy audit with informative possible
defects and unresolved outcomes, without a guaranteed whole-family
packing-preservation certificate. A favorable subset establishes
only those named representatives. The under-resolved control prevents a
blanket equivalence statement under this protocol even if the other controls
qualify. Every control and failed gate remains visible in the report.

The remaining geometry views retain their preregistered probability intervals,
directional contrasts, exact-model references and descriptive hardware-minus-
model residuals. The preregistered directional test must reject the zero null
before its directional claim is admitted; a positive point estimate alone
supplies neither that claim nor a practical-effect threshold. Noise-model
residuals remain descriptive unless the recorded inference contract supplies
their full uncertainty. Readout controls remain displayed observations rather
than an unplanned inversion or mitigation step.

Rank-sector measurements report selector-success probability
`p = ||L_a(t) y||^2 / (alpha(t)^2 ||y||^2)`. Unit-input squared-norm displays
multiply both probability estimates and interval endpoints by the recorded
`alpha(t)^2`, giving `||L_a(t) y||^2 / ||y||^2`. Given-coordinate squared-norm
displays additionally multiply every endpoint by `||y||^2`. A probability
tolerance never silently becomes a constant unnormalized norm tolerance.
These observations test implementation accuracy
for supplied probes. Exact rank, kernel dimension, topology and a full Gram
matrix require their separate mathematical evidence.

Admission retains all 146 ripple and 36 rank PUBs, matched companions,
isolated controls and readout witnesses. Their combined 140-second ceiling
adds to the correction's 30-second ceiling within the user's 180-second cap.
The fixed allocation purchases the complete declared questions at the audited
cost. It claims neither globally optimal information per second nor that every
possible smaller design has been excluded. The execution owner must still
close reviewed-merge, correction-decision, source/calibration/QPY, quota and
single-use submission gates before either static acquisition.

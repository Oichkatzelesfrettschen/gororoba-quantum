# BDSC acceptance diagnostics and root-cause boundaries

This note analyses the retained qualification runs at commit
`365ed05d355de838bf6873f748be8d854438b101`. It supplements the
[qualification design](../../design/bdsc-qualification.md) and
[frozen runbook](../../runbooks/bdsc-qualification-case.md); it does not change
an approved case, a contrast, a margin, an epoch, or a retained record.
No provider read, acquisition, retry, QRNG draw, or additional expenditure is
authorized here. Epoch-1 interpretations remain exploratory while the
observation contract and the frozen complete readout remain outstanding.

## Evidence scope

The source review covers the current case generator, one-click readout,
collection path, Ascella control, submitted target columns, and run receipts.
Independent arithmetic below uses two complete 24-mode one-click count
vectors extracted from `tc-none-e1`, plus its receipt and the `mm-none-e1`
receipt. It is not an end-to-end replay of all 48 settings or of the compressed
raw responses. The reported 9/16 violated sum rules are the campaign's
exploratory readout, not an independently regenerated verdict in this note.

Source locations under `results/quandela/runs/`:

- `2026-10-21T162332Z-qpu_belenos-bdsc_qualification-tc-none-e1/`:
  `cases.json`, `submission.json`, `results.json`.
- `2026-10-21T165036Z-qpu_belenos-bdsc_qualification-mm-none-e1/`:
  `cases.json`, `submission.json`.
- `2026-10-21T122531Z-qpu_belenos-bdsc_qualification-tc-def-e1/`:
  `submission.json`.
- `2026-10-21T203428Z-qpu_ascella-bdsc_ascella_control-job-00/`:
  `results.json`.

A returned count is called a returned count, not an independently established
raw detector event. Relative `t_out` fields are sensitivity-model weights,
not calibrated absolute efficiencies or an acceptance certificate.

## The sum-rule conclusion

For orthonormal f,g, the ensembles {f,g}, {+,-}, and {+i,-i} each sum to the
same density operator. For a fixed effect F and correctly prepared inputs,

    p(+) + p(-) = p(f) + p(g) = p(+i) + p(-i).

The identity also survives every fixed linear trace-preserving preparation
channel: dephasing, a common coherent phase error, and a fixed unitary do not
alone invalidate it. A violation rejects the combined preparation,
common-effect, linear-observation and stationarity assumptions. It does not
isolate preparation error, nor does it exclude detector/acceptance effects.
A diagonal phase applied only at the output cannot change Fock intensities.
State-dependent compilation or errors remain possible, but must be separated
from conditioning and processing.

The actually analysed probability is one-click conditioned. With selected
unconditional effect G and acceptance effect D,

    p_s = Tr(G rho_s) / Tr(D rho_s).

The linear identity need not hold for this ratio. Correct states and a fixed
physical detector suffice to violate it when D is not scalar.

Exact countermodel: in the f,g basis choose D = diag(0.06, 0.04),
G = diag(0, 0.04). Both are positive and G <= D <= I. Perfect preparation gives
probabilities (0, 1, 0.4, 0.4, 0.4, 0.4) on (f,g,+,-,+i,-i), with both residuals
-0.2. No phase error, varying measurement, or incorrect preparation is needed.

## A receipt-predicted alternative explains the leading shift

Assume, only for a sensitivity calculation, an ideal requested output column
v and terminal detection weights w_m proportional to the reported `t_out`.
Then the conditional distribution is

    q_m = w_m |v_m|^2 / sum_j w_j |v_j|^2.

This uses ratios only. Values exceeding 100 are not interpreted as
probabilities. The weights are taken from each run's receipt without fitting
them to the measured histogram.

### Target-complement pair

The manifest sends f to mode 0, g to mode 12, and each of the four
superpositions to equal intensities on those two modes. Mode 12 is selected;
mode 0 is complementary. `tc-none-e1` reports w_0 = 109.69 and w_12 = 81.10.
Thus perfect inputs predict

    p(f) = 0, p(g) = 1,
    p(+) = p(-) = p(+i) = p(-i) = 81.10 / 190.79
                                     = 0.425074689449,
    Delta_R = Delta_I = -0.149850621102.

This prediction is inside the reported 0.375--0.437 superposition range and
has the sign and approximate size of the reported -0.17 sum-rule deficit.
It explains why apparently good basis endpoints do not exclude detector
imbalance: a single occupied mode stays certain after conditioning.
The two-mode acceptance anisotropy in this scenario is about 0.14985, not the
small acceptance deviation assumed in optimistic certificate planning.
It is not a measured bound on D.

### Middle-middle pair

The target maps e1 to equal intensity on modes 8 and 20, and e2 to modes 9
and 21. The latter mode of each pair is selected. The `mm-none-e1` receipt gives
w_8 = 99.75, w_20 = 59.40, w_9 = 84.98 and w_21 = 119.63. Therefore

    p(f) = 59.40 / (99.75 + 59.40) = 0.373232799246,
    p(g) = 119.63 / (84.98 + 119.63) = 0.584673280876,
    p(each superposition) = (59.40 + 119.63) / 363.76
                          = 0.492165163844,
    Delta_R = Delta_I = 0.026424247567.

The reported basis probabilities, about 0.356--0.370 and 0.547--0.590, need
not be attributed first to phase error. The receipt-weight model already
predicts their asymmetric direction and approximate scale. It is not an
explanation of every residual or a substitute for device calibration.

## Independently checked returned-count examples

The selected set is {12,13,16,18,19,20,21,22,23,4,6,7}.
The two 24-component vectors below are ordered by mode 0 through 23.

`tc-none-e1/out-m`:

    [171468,1524,241,20,121,1796,153,39,55,169,31,37,
     123810,44,10,32,55,52,40,29,72,29,29,24]

There are 299880 one-click records, 124445 selected records, 40 zero-click
records and 80 multiple-click records; the total is 300000. The selected
fraction is 0.414982659731. Of the one-click records, 1.5346% lie outside the
intended two-output support. On the intended outputs alone,

    n_12 / n_0 = 0.722058926447,
    w_12 / w_0 = 0.739356367946.

The ratio of these odds is 0.976604730480. Applying the receipt's inverse
weights as a sensitivity calculation gives 0.494081955497 on the intended
pair, or 0.487869865444 across all outputs. Neither number is an observed
probability, an admitted correction, or confirmatory evidence.

`tc-none-e1/out-f`:

    [280390,6533,1560,7684,279,1579,299,230,229,263,235,218,
     12,36,12,13,44,57,45,32,59,22,21,27]

There are 299879 one-click records, 1106 selected records, 92 zero-click
records and 29 multiple-click records. The selected fraction is
0.003688154222. However, 6.49896% of the one-click records lie outside the
intended single output, mode 0. A small selected fraction alone therefore
hides substantial wrong-mode response in other complementary outputs.

Removing a fraction d of returned records changes one bounded outcome
probability by at most d. If each of four settings drops at most 0.0006,
the sum-rule change caused solely by that removal is at most 0.0024.
That cannot account for a residual near -0.17. It does not bound the much
larger or state-dependent optical losses absent from the returned records.

## Separate even response shifts from phase-sensitive response

For a six-state cell define

    m_Z = (p_f + p_g)/2,
    m_X = (p_+ + p_-)/2,
    m_Y = (p_+i + p_-i)/2,
    d_X = (p_+ - p_-)/2,
    d_Y = (p_+i - p_-i)/2.

One fixed unconditioned effect has m_X = m_Y = m_Z. The d components describe
its two coherent quadratures. The reported common depression of all four
superpositions is primarily an even-component anomaly, not by itself a
phase-fringe measurement. Fit the even and odd components separately.

For a common filtered measurement in a two-dimensional test space, write
D = d0 I + d.sigma and G = g0 I + g.sigma. On Bloch direction n,

    p(n) = (g0 + g.n) / (d0 + d.n).

Test the model with 0 <= G <= D, not by forcing conditional probabilities
into a linear effect. Six probabilities generally do not identify all
parameters or the physical location of the filter. A feasible model is a
counterexplanation, not a unique root-cause assignment.

## Offline diagnosis before any new case

1. Bind each setting to its case, submitted body, QRNG indices, echoed seed,
   observation index and run. Preserve actual start/stop timestamps. The
   four-hour queue wait makes submission-time calibration potentially stale.
2. Export every per-mode count vector and every excluded category. Preserve
   selected probability and wrong-support probability separately.
3. Evaluate the ideal-column and receipt-weight scenarios without fitting.
   On default-mitigated outputs, keep the unmitigated scenario explicitly a
   counterfactual rather than a prediction of the processed estimator.
4. Evaluate complete submitted and returned circuit columns, including
   coherent phases. Matching parameter echoes proves attribution, not
   physical phase accuracy or preservation of a common measurement.
5. Fit successively richer diagnostic models: scalar acceptance; diagonal
   terminal weights; constrained G,D filtering; additive wrong-mode response;
   template/seed/epoch-dependent transfer. Use held-out settings or epochs
   for predictive checks. Do not use an unrestricted per-setting fit as an
   explanation.
6. Keep the frozen 96-observation formal readout unchanged. A receipt-weight
   adjustment is exploratory and never replaces its counts or likelihood.

A future separately approved matched output-swap probe can help separate
routing from terminal weights. For intended two-port odds o and stable
relative efficiency r, forward and swapped logical output assignments give
O_f = r o and O_s = o/r. Then sqrt(O_f O_s) = o and sqrt(O_f/O_s) = r.
This requires stable transfer apart from the declared swap, negligible or
modelled background, and complete outcome accounting. It is not a license to
relabel the already acquired masks or add settings to epoch 2.

## Ascella incident and the scope of a comparison

Job `c2edef5d-5e6f-4161-83fc-aadd024171fb` returns zero shots and samples after
one second, with

    hardware_info.circuit_input_ports must be defined in the hardware_config
    to use Instruments.set_pic_input().

This localizes the failed dispatched path to provider instrument input-port
configuration before useful acquisition. It does not establish that every
Ascella endpoint or possible job fails, nor does it independently certify
cloud compatibility of the submitted circuit. Local Perceval validates the
ideal mathematics, not provider configuration.

The retained Ascella control is not an identical hardware counterfactual:
`scripts/bdsc_ascella_control.py` uses a seeded dense twelve-mode pair, input
4 and odd-output selection. Belenos uses sparse target/complement and
middle/middle columns in 24 modes. Success on one does not isolate the cause
on the other; failure on both can involve shared compilation, processing or
preparation assumptions. Compare matched support, logical transformations,
selection rules and calibrated acceptance before making device-local causal
claims.

Report the exact job ID, endpoint, timestamps, error, source mode and
processing request to the provider through an approved communication. Retry
only under the existing approval scope or a new written case after a
configuration remedy or independently justified readiness check. The public
`available` status is not an end-to-end instrument-health guarantee.

## Collection and epoch controls

The status-read retry change is correctly separated from submitting a new
job. Retrying a GET after 408/429/5xx is not permission to retry POST creation.
Inspect the terminal data/result/usage reads as well: the current retry loop
covers status polling, while those later reads can still fail transiently.
Retain successful raw result bytes independently of a subsequent accounting
read so an accounting outage cannot block preservation of scientific data.

`result_summary` currently returns an empty summary upon the first non-count
error entry of a failed iterated job. For a future partially successful job,
that discards earlier count-bearing iterations from the derived summary
(the original raw response remains retained). A future collector revision
must preserve each successful/error iteration separately and must never admit
that partial result into the frozen complete BDSC readout. Test mixed success,
error, malformed and missing iterations, not only an all-error result.

The scheduled maintenance window on the run receipts is
2026-10-22 07:30--11:00 UTC (00:30--04:00 America/Los_Angeles).
The scheduled end is not proof of a completed calibration or a healthy input
configuration. Record actual readiness and an acquisition-time calibration
identity. Preserve epoch 2 as a separate intervention/replication epoch; do
not pool across calibration changes merely because both batches completed.

## Research grounding

The canonical BDSC source map is [bdsc_sources.md](bdsc_sources.md).
The registered detector-tomography and gate-set-tomography notes distinguish
known preparations from unknown measurements and joint identifiability:
[0807.2444](../papers/0807.2444.md) and
[2009.07301](../papers/2009.07301.md). Drift requires appropriately retained
time information: [1907.13608](../papers/1907.13608.md).

External primary sources used for the conditioning interpretation:

- Orsucci, Bancal, Sangouard and Sekatski, *How post-selection affects
  device-independent claims under the fair sampling assumption*, Quantum 4,
  238 (2020): https://quantum-journal.org/papers/q-2020-03-02-238/
- Perceval 1.3 error-mitigation contract:
  https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/index.html
- DetectorBalancing's declared purpose and model dependence:
  https://perceval.quandela.net/docs/v1.3/reference/runtime/error_mitigation/detector_balancing.html

The source-map registration is not changed by this note. No new theorem of
sedenion algebra, altered likelihood, or physical detector correction is
claimed. The strongest current diagnosis is an identifiable acceptance
confound with a quantitatively relevant receipt-based prediction, plus
residual wrong-mode and template dependence whose mechanisms remain open.

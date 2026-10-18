# Tuna-17 Design B: secondary covariance-aware analysis

Claim kind: **secondary hardware reanalysis**. This independent analytic audit complements the retained common-response bootstrap and adds corrected regional estimates.

Run: `results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17`. The JSON sidecar binds every input by SHA256.

## Counts and case estimates

Each Latin-square circuit and each readout calibration contains 16,384 shots. Each case appears once in each of the three Latin-square circuits, totaling 49,152 attempts per case. The estimates below pool three fixed regions; the same-shot covariance is retained between cases.

| Case | Selector-zero successes / attempts | Raw P(s=0) | Readout-corrected P(s=0) |
|---|---:|---:|---:|
| dark | 23140 / 49152 | 0.470784505 | 0.457107580 |
| bright | 25180 / 49152 | 0.512288411 | 0.500601426 |
| fixture | 24529 / 49152 | 0.499043783 | 0.483587704 |

All six pooled point estimates reproduce the original analysis. Bright is above 0.5; it is the endpoint midpoint that lies below 0.5.

## Joint uncertainty

The intervals are pointwise normal 95% intervals. The corrected rows include the shared calibration's finite-shot uncertainty and cross-selector covariance. These secondary tests have no multiplicity adjustment.

| Scale | Observable | Estimate | Standard error | 95% interval | z against zero |
|---|---|---:|---:|---|---:|
| raw | B-D | +0.041503906 | 0.003197548 | [+0.035237, +0.047771] | +12.980 |
| raw | D+B-1 | -0.016927083 | 0.003172301 | [-0.023145, -0.010709] | -5.336 |
| raw | F-0.5 | -0.000956217 | 0.002254303 | [-0.005375, +0.003462] | -0.424 |
| raw | H = F-(D+B)/2 | +0.007507324 | 0.002757516 | [+0.002103, +0.012912] | +2.722 |
| readout corrected | B-D | +0.043493846 | 0.003353744 | [+0.036921, +0.050067] | +12.969 |
| readout corrected | D+B-1 | -0.042290994 | 0.003481774 | [-0.049115, -0.035467] | -12.146 |
| readout corrected | F-0.5 | -0.016412296 | 0.002448164 | [-0.021211, -0.011614] | -6.704 |
| readout corrected | H = F-(D+B)/2 | +0.004733201 | 0.002943001 | [-0.001035, +0.010501] | +1.608 |

The approximately 13-standard-error ordering survives covariance and calibration propagation. The original raw fixture consistency result also reproduces. However, fixture consistency is **raw-only**: under the retained correction model, the pooled fixture is below 0.5 by about 6.7 standard errors. The correction therefore does not preserve that conclusion.

H tests a common affine response in the ideal selector probability. Its raw z is about 2.72 and its corrected z about 1.61, below the preregistration's absolute-z benchmark of 3. H itself was not preregistered, so this comparison does not convert it into a preregistered test. Corrected H is compatible with a common affine probability response at this precision; this non-rejection does not establish that response or a mechanism.

## Comparison with the retained bootstrap

The upstream secondary analysis belongs to the existing `qi-tuna17-zero-divisor-common-response` claim. Its raw point estimates and complete case covariance independently reproduce after the explicit n/(n-1) variance adjustment: the upstream empirical covariance uses n, while this audit uses n-1. The bootstrap resamples whole same-shot selector vectors and the shared readout calibrations.

| Corrected observable | Analytic estimate | Analytic SE | Bootstrap mean | Bootstrap SE | Bootstrap 95% interval |
|---|---:|---:|---:|---:|---|
| B-D | +0.043493846 | 0.003353744 | +0.043502062 | 0.003323723 | [+0.036887, +0.049988] |
| D+B-1 | -0.042290994 | 0.003481774 | -0.042279333 | 0.003524576 | [-0.049325, -0.035508] |
| H = F-(D+B)/2 | +0.004733201 | 0.002943001 | +0.004677329 | 0.002971837 | [-0.001161, +0.010546] |
| F-0.5 | -0.016412296 | 0.002448164 | -0.016462338 | 0.002482925 | [-0.021400, -0.011736] |

The retained bootstrap uses 4,000 draws with seed 20261016. The standard errors differ by at most 1.4%. These methods give the same substantive pooled conclusions. Their numerical difference also includes finite bootstrap sampling and first-order versus nonlinear propagation; this is a method comparison, not an independent hardware replication.

## Regions, selectors and circuit costs

| Region | Selectors D / B / F | CZ D / B / F | Raw B-D (95% interval) | Corrected B-D (95% interval) |
|---|---|---|---|---|
| [0, 1, 2, 4, 5] | 2 / 2 / 4 | 66 / 66 / 70 | 0.001709 [-0.009117, +0.012535] | 0.001784 [-0.009517, +0.013085] |
| [7, 8, 10, 11, 13] | 11 / 11 / 11 | 66 / 66 / 70 | 0.050964 [+0.040152, +0.061777] | 0.054458 [+0.042902, +0.066013] |
| [9, 12, 14, 15, 16] | 12 / 12 / 12 | 66 / 66 / 70 | 0.071838 [+0.061040, +0.082636] | 0.074240 [+0.063079, +0.085401] |

The corner has **no resolved contrast**, not an established exact zero. All dark and bright replicas use 66 CZ. A difference of four CZ between dark and bright does not explain their endpoint asymmetry: those four additional gates belong to the fixtures.

The corner fixture is measured on Q4, while its dark and bright witnesses use Q2. The other regions keep the same selector for all three cases. H therefore also compares different selector responses in the corner, and every fixture differs in state preparation and depth from the endpoints. It is a descriptive model check, not a controlled isolation of one noise channel.

| Region | Raw fixture P(s=0) | Corrected fixture P(s=0) | Raw H (z) | Corrected H (z) |
|---|---:|---:|---:|---:|
| [0, 1, 2, 4, 5] | 0.518433 | 0.499444 | +0.026733 (+5.591) | +0.018366 (+3.496) |
| [7, 8, 10, 11, 13] | 0.497253 | 0.482163 | +0.005280 (+1.104) | +0.005641 (+1.104) |
| [9, 12, 14, 15, 16] | 0.481445 | 0.469156 | -0.009491 (-1.987) | -0.009808 (-1.986) |

The raw fixture's regional deviations have opposite signs, so pooled agreement with 0.5 does not establish agreement in every region. The corner's H is largest, including after correction, but it is also where the selector changes. A single Latin square balances additive region and row effects without independently replicating all interactions or drift.

## Noise interpretation and assumptions

D+B-1 tests a common symmetric contraction around 0.5. Allowing different effective contractions for the two circuits can reproduce both endpoints with depolarizing-form maps. Equal CZ counts constrain a gate-count-only explanation but do not establish equal effective channels. The measurements do not identify coherent, non-unital or coupler error uniquely.

The readout inversion is p_corrected=(p_raw-beta)/(1-alpha-beta), where alpha=P(read 1|prepared 0) and beta=P(read 0|prepared 1). Its derivatives with respect to (p_raw, alpha, beta) are (1/d, p_corrected/d, (p_corrected-1)/d), with d=1-alpha-beta. Combining these gradients before covariance propagation retains cancellation and correlation when multiple estimates share calibration shots.

The intervals assume independent shots within each acquisition and independence between jobs. They include same-shot dependence among selectors, but not between-job drift. They also assume the all-zero/all-one calibration represents readout after the witness. Those preparations include preparation error and do not establish a pure assignment channel; model misspecification is outside the reported intervals.

## Reproduction

```sh
"$PYTHON" scripts/qi_zero_divisor_secondary.py --check results/quantum_inspire/secondary --self-test
```

The self-test uses exactly correlated and anticorrelated selector samples, and verifies that shared readout offsets cancel in the appropriate contrasts. The acquisition blocks retain covariance matrices and input hashes in the JSON sidecar. This analysis submits no hardware job.

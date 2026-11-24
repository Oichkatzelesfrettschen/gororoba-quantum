# Tuna-17 matched response, replicated design

This note freezes a successor to the
[region-2 selector q11 proposal](tuna17-matched-response-region2-selector-q11.md) before any shot exists. The
predecessor decides at `abs(z) >= 3` with a shot-noise standard error of 0.0084, while the retained
three-region run puts the null standard deviation of its residual near 0.038 (0.023 to 0.11 on 3 degrees of
freedom; see [Limit of the decision rule](tuna17-matched-response-analysis.md)). Its weighted witnesses sit in
different batches, and a batch boundary is a calibration boundary, so a region-by-batch interaction stays in the
residual. The replicated design takes the standard error from the scatter of the replicate residuals, which is
valid whatever the interaction is. Nothing here is submitted: `provider_execution_authorized` is false.

## Question

Is the device response common-affine across region 1 (selector q4) and region 2 (selector q11)? The run tests the
device. The zero-divisor algebra is certified offline: `qi_zero_divisor_cases.certify()` checks every product
of the three cases against `cd_core`, and the Lean proof of the sedenion witness products of the selector case is a
draft pull request of gororoba-math (not merged at this writing, so no digest is cited). The residual is zero at
equal products of readout factor and visibility in the two regions whatever the algebra says, so a rejection or a
non-rejection says nothing about the zero-divisor property.

## Estimand and null

A replicate is one batch of three circuits: `witness-a` (bright in region 1, fixture in region 2),
`witness-b` (fixture in region 1, dark in region 2) and one readout circuit. The circuit bytes are those of
batches 1 and 2 of the q11 proposal, so no new compile runs; the producer
`scripts/qi_matched_zero_divisor_replicated.py` verifies each against the frozen digests of
`gororoba_quantum/qi_matched_response.py` and copies them. Batch 0 of the predecessor has weight 0 and is dropped.

With `p` the raw (not readout-corrected) selector-zero frequency, the per-replicate residual is

    r = (p_a2 - p_a1) + (p_b1 - p_b2) = F_R2 - B_R1 + F_R1 - D_R2.

Under an affine response `p_obs = a_region + g_region p_ideal` with a batch offset common to both regions, the
ideal values bright 1, fixture 1/2, dark 0 give

    r = (a2 + g2/2 - a1 - g1) + (a1 + g1/2 - a2 - 0) = (g2 - g1) / 2.

The offsets `a_region` and the batch offset cancel because both witnesses share one batch. The raw null is
`g1 = g2`: equal products of readout factor and visibility in the two regions. The readout-corrected residual (the
`v = (m1 - mw) / (m1 - m0)` of the frozen analysis) is exploratory: it pools the readout pair over each block of
four replicates, uses complete blocks only, and no decision rests on it.

## Schedule

Replicate `i` runs `witness-a, witness-b, readout` for even `i` and `witness-b, witness-a, readout` for odd
`i`; the readout circuit is `readout-0` for `i mod 4` in {0, 1} and `readout-1` for {2, 3}. Each block of
four replicates meets each witness order with each readout circuit once. The proposal fixes 60 batches
(`rep-00` to `rep-59`) and the schedule of each; the manifest order is the submission order, so a reordered
schedule changes the manifest digest, the job order of the run and the job ids, and the analysis refuses each.
The batch stays at the 3-circuit cap (`HARDWARE_BATCH_CIRCUITS`).

## Test: Stein two-stage t

Stage 1 takes `n1 = 12` replicates. Their sample standard deviation `s1` (11 degrees of freedom) alone fixes the
total `N = max(12, ceil(s1^2 / c))`; the stage-1 mean never enters the rule. The statistic is
`t = mean(r_0 .. r_(N-1)) sqrt(N) / s1`, rejected at `abs(t) >= t_{0.995, 11} = 3.1058065155392804` (two-sided
alpha 0.01).

Derivation of `c`. With `U = s1 / sigma` and `Z` standard normal independent of `U` (the mean of the `N`
residuals is independent of `s1` for normal residuals, and `N` is a function of `s1`), `t = delta sqrt(N) / s1 +
Z / U`. The first term is at least `delta / sqrt(c)`, and `Z / U` is a central t variable on 11 degrees of
freedom, so `t >= shift + T`. The shift that gives two-sided power 0.80 at level 0.01 solves
`P(abs(shift + T) >= 3.1058) = 0.80`, which is `shift = 3.9812975678033524`. Then `c = 0.024^2 / shift^2 =
3.6339019606546454e-05`, so the target effect is `abs(delta) = 0.024`. For normal, exchangeable per-replicate
residuals the level is exact for every sigma at delta 0 (there `t = Z / U`); heavy-tailed residuals carry no
exactness claim, and the simulation below measures the level under Student t residuals on 3 degrees of
freedom; the power is at least 0.80 for every sigma whose `N` stays within the cap (for normal residuals). The three
constants are frozen as decimal literals, and a test recomputes them with scipy.

Cap. `N` is capped at 60, which binds at `s1 = sqrt(60 c) = 0.0467`. When the rule asks for more, the case stops
after stage 1 with the verdict `undecided_at_cap` and reports the stage-1 mean with its 99 percent interval
`mean +- 3.1058 s1 / sqrt(12)` and the effect detectable at power 0.80, `3.98 s1 / sqrt(12)`.

### Seeded simulation (400000 trials per row, `scripts/qi_replicated_stein_simulation.py`)

The simulation draws the replicate residuals and calls the module's own `required_replicates`,
`stein_statistic`, `CAP` and `T_CRIT`. Rates are measured with the seeds of
`docs/evidence/quantum_inspire/tuna17-replicated-stein-simulation.json`.

| sigma | delta | reject (capped design) | undecided at cap | reject given within cap | reject (uncapped rule) | median N |
|---|---|---|---|---|---|---|
| 0.01 | 0 | 0.0101 | 0.0000 | 0.0101 | 0.0101 | 12 |
| 0.01 | -0.024 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 12 |
| 0.02 | 0 | 0.0103 | 0.0000 | 0.0103 | 0.0103 | 12 |
| 0.02 | -0.024 | 0.9011 | 0.0000 | 0.9011 | 0.9007 | 12 |
| 0.038 | 0 | 0.0100 | 0.1206 | 0.0114 | 0.0102 | 38 |
| 0.038 | -0.024 | 0.7013 | 0.1206 | 0.7975 | 0.8080 | 38 |
| 0.08 | 0 | 0.0026 | 0.9770 | 0.1151 | 0.0099 | 166 |
| 0.08 | -0.024 | 0.0156 | 0.9770 | 0.6799 | 0.8020 | 166 |
| 0.038 (t3) | 0 | 0.0112 | 0.1258 | 0.0128 | not simulated | 25 |

The uncapped columns sit at 0.010 for delta 0 (within 0.0003) and at or above 0.80 for delta -0.024 at every sigma,
so the rule holds its level and power; the cap is what lowers the power at large sigma. Reading: at the retained
estimate sigma = 0.038 the design decides about 88 percent of cases and rejects a true effect of -0.024 in about 70
percent of all cases (80 percent of the decided ones). At sigma = 0.08 it almost always stops after stage 1.

The `0.038 (t3)` row draws Student t residuals on 3 degrees of freedom scaled to SD 0.038 (the t3 variance is 3,
so each draw is divided by sqrt(3)), with seed index 12 of the same draw file. Its measured level at delta 0 is
0.0112 for the capped design (400000 trials, binomial standard error 0.00016), against 0.0100 for normal residuals,
and 0.0128 among the cases that decide within the cap. The level therefore sits about 12 percent above its nominal
value under this tail; the heavy tail also moves the median required total to 25 and the undecided-at-cap rate to
0.126. The uncapped column stays empty for this row because the uncapped shortcut draws the later residuals as one
normal variable. The simulation covers one tail shape at one sigma, and its `--check` mode recomputes the whole
table against the retained file without writing.

## Exchangeability, preregistered

The t test treats the replicate residuals as exchangeable. Two checks accompany the verdict.

- The lag-1 autocorrelation of `r_i` with its white-noise interval `rho +- 1.96 / sqrt(N)`. The estimate marks
  the t test unreliable when `abs(rho) > 0.3` and `abs(rho)` exceeds the interval half-width; the verdict then
  stays as computed and carries the mark.
- The difference of mean residuals between the two witness orders (even minus odd replicates) with a Welch 95
  percent interval. It is reported without a threshold.

## Interpretation

| Outcome | Reading | What it leaves open |
|---|---|---|
| Rejected | The mean residual differs from zero: `g1 != g2`, a region-dependent product of readout factor and visibility. | A fixed spectator or context effect of the circuit pairing gives the same signal; so does any affine departure that differs between the regions (the regions run 81 and 96 controlled-Z gates). The algebra is not in question. |
| Not rejected | The mean lies in the 99 percent interval `mean +- 3.1058 s1 / sqrt(N)`; effects above `3.98 s1 / sqrt(N)` are excluded at power 0.80 (0.0239 at N = 40 and s1 = 0.038). | An effect below that bound, and non-affine response that cancels in the residual. |
| Undecided at the cap | The rule asked for more than 60 replicates: sigma is above 0.0467. | The stage-1 mean and its interval are reported; no effect is excluded or shown. |
| Unreliable mark | Lag-1 autocorrelation beyond the bound: the replicates are not exchangeable. | The t verdict stays computed and is not evidence. |

## Cost

Per-circuit device seconds come from the q11 proposal (`expected_device_seconds` over its nine jobs, 11.28352 s),
16384 shots each, pauses at `QI_HARDWARE_PAUSE_SECONDS = 120`, 0 credits.

| | Stage 1 (12 batches) | Cap (60 batches) |
|---|---|---|
| Jobs | 36 | 180 |
| Shots | 589824 | 2949120 |
| Device seconds | 406.20672 | 2031.0336 |
| Pauses between batches (seconds) | 1320 | 7080 |
| Credits | 0 | 0 |

At the retained sigma, N is about 40: 120 jobs, about 23 device minutes and 39 pauses (78 minutes).

## Binding and refusals

`gororoba_quantum/qi_replicated_response.py` binds to `proposal.json` by its sha256, to each replicate manifest by
the digest recorded in the schedule, and to every circuit file by its digest; `qi_records.load_run` and
`verify_run_binding` of the frozen analysis bind each collected run. It refuses a wrong proposal, a wrong or
changed circuit or manifest, a reordered schedule (manifest order, submitted job order and rising job ids), a
missing or out-of-sequence replicate, fewer than 12 replicates, stage-2 data whose count differs from the rule's
`N`, stage-2 data after a stop at the cap, a short or absent shot list, a witness case assignment other than the
frozen one and a readout error above 0.2. `tests/scripts/test_qi_replicated_response.py` mutates a run for each
refusal and runs a synthetic end-to-end series under the null and under `(g2 - g1)/2 = -0.024`.

## Offline check

Four replicates (`rep-00` to `rep-03`: both orders, both readout circuits) ran on the local qxelarator
emulator at 16384 shots per circuit. Selector-zero frequencies for (region 1, region 2): witness-a
(1.0, 0.5067), (1.0, 0.4982), (1.0, 0.4925), (1.0, 0.4950); witness-b (0.4990, 0.0), (0.5031, 0.0), (0.5063,
0.0), (0.4908, 0.0). The raw residuals are 0.0056, 0.0013, -0.0012 and -0.0142 (ideal 0, shot noise about
0.008 each); the readout circuits read 0 and 1 on both selectors; the exploratory block-corrected residual is
-0.0021. The emulator checks syntax, register shape and the noiseless law, and says nothing about the device.

The red-team round on this proposal and its reconciliation are in the
[review record](../archive/reviews/tuna17-matched-response-replicated/reconciliation.md).

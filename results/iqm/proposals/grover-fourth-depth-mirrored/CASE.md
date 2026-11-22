# IQM Garnet fourth Grover depth at mirrored positions

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made in
the repairs that added the analyzer, the mirror-pair and heterogeneity gates, the rate domains, the leave-one-pair-out
influence check, the readout correction, the mirrored readout block and the calibrated family threshold. The copy counts
follow the owner's decision of 2026-11-22 on the power of the family verdict ("Power and its cost").

Backend `iqm:garnet` (20 qubits, pay-as-you-go 0.50 credits per second; limits 20,000 shots per circuit, 100 circuits and
2,000,000 executions per job, [limits](../../../../docs/evidence/iqm/qc/garnet/limits.json)). The case directory
[grover-fourth-depth-mirrored](../../cases/grover-fourth-depth-mirrored/cases.json) holds one job of 38 circuits at 20,000
shots, built by `scripts/iqm_grover_fourth_depth.py` against Garnet calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a`
(created 2026-11-22T03:02Z; the copy sits in the case's `calibration/`, read by `iqm_sim.Calibration.from_directory` without
a key change).

## Question

The retained Garnet Grover-depth run ([design](../../../../docs/design/iqm-garnet-grover-depth-sedenion-walsh.md), "Open
hypotheses") measured the marked-state retention of the line-native Grover of mark 101 on QB20-QB16-QB17 at depths 1, 2 and 3
as lambda = 0.831, 0.730, 0.519 (the model reads 0.843, 0.753, 0.683) and a bend f = lambda_3 - lambda_2^2 / lambda_1 =
-0.122 against the model's +0.010. Two causes stay open: positional drift across the job, and a coherent error that
accumulates with iterations, which the density-matrix model omits. The retained bytes already exclude linear and symmetric
drift ([positions evidence](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/iqm-qb12-fault-models/docs/evidence/iqm-garnet-grover-positions/README.md),
PR 979). This case puts every depth arm, k = 1 to 4, at positions mirrored about the job's center, so no drift linear in
position enters the depth statistics, and adds the fourth depth, where the two causes continue differently.

1. Does the bend persist with every depth mirrored? (resolved when f differs from the model's f by 3 standard errors; a
   persistent bend removes linear positional drift as its cause.)
2. Over the four depths, does a geometric excess loss (rho_k = a s^k) or a coherent oracle-phase error (rho_k = s^k
   (Q_k(eps) - 1/8) / (P_k - 1/8), eps radians per iteration) describe the retention beyond the model, where rho_k =
   lambda_k / model lambda_k?

## Why a simulation cannot answer it

`iqm_sim` carries depolarizing gates, idle decay and readout and no coherent error, so it reads rho = 1 by construction. The
question is whether the device's own coherent error and drift reproduce the retained bend, which only the chip shows.

## Circuits and shots

62 circuits, one job, 20,000 shots, heralding `zeros`, one active-reset cycle: line-native Grover of mark 101 (14 CZ per
iteration; 56 CZ and 82 prx at depth 4) on QB20-QB16-QB17 (QB12 lies outside Garnet's gate set and is not used), at depth 1,
2, 3 and 4 in 14, 4, 4 and 24 copies, and the eight readout preparations `ro-xyz` in two copies each (`ro-xyz` and
`ro-xyz-m`, one on each side of the job's center): 46 depth circuits and 16 readout circuits, inside Garnet's 100 circuits,
20,000 shots and 2,000,000 executions per job (1,240,000). Order (`arrangement()`): a first half of 31 circuits (half the
copies of every depth and each readout preparation once), then the first half reversed, so every kind's summed position is
its count times the center and each readout preparation sits at mirrored positions on both sides. The squared offsets of the
kinds differ by 0.6 % (a spread of 2.0 in about 320), which balances a quadratic drift to that order. The first half is the
constant `FIRST_HALF` of the script, the local optimum of single exchanges of two circuits from an even spread
(`best_first_half()`, every round's exchanges scored through `parallel.ordered_map`; the orderings, about 10^15, are too
many to list, so the exhaustive optimum of the 38-circuit design is not claimed); a build verifies its invariants and a test
reruns the search against the constant and checks that no exchange lowers the spread. The case draws no random number and
takes no seed.

## Resolution arithmetic

- Retained ratios rho = lambda / model lambda at depths 1 to 3: 0.9855, 0.9697, 0.7605. Fitted by each family (generalized
  least squares at the retained kept shots 13,450, 3,377, 3,383): geometric a = 1.0260, s = 0.9634 (chi2 11.29 on one
  degree of freedom); coherent eps = 0.3043, s = 1.0134 (chi2 0.85). The coherent fit's s above 1 means the model's loss
  slightly overstates the device's at small depth.
- Continued to depth 4 and scaled by this calibration's model lambda_4 = 0.5805: geometric lambda_4 = 0.5130, coherent
  0.5262 (difference 0.0132). Both continuations decrease from their depth-3 values, so monotonicity does not separate
  them; the separation is 0.0132 in lambda, 0.0228 in rho.
- Kept shots at 0.84 of requested (retained 0.841 to 0.846): 235,200 at depth 1, 67,200 at depths 2 and 3 and 403,200 at depth 4. The
  standard error of rho_4 is 0.00626 with the binomial scatter and the readout covariance, so the continuations separate by
  3.63 standard errors (3.77 binomial alone). With one of the twelve depth-4 mirror pairs gone the separation z is 3.49, with
  two 3.34 and with three 3.18; the bend's standard error is 0.0092 with all copies and 0.0092, 0.0099 and 0.0124 with one pair
  gone from depth 1, 2 and 3.
- Over four depths, if the data equal the coherent values the geometric fit leaves the chi2 of `decisions.continuation`, and
  if they equal the geometric values the coherent fit leaves the other; both exceed the calibrated threshold of 7.
- The bend uses three arms: its standard error at the planned shots is 0.0092 against the retained
  f of -0.122 against the model's +0.010 (a deviation of 0.133, about 14 standard errors if the bend repeats).
- The eight readout preparations measure the marked row of the job's assignment matrix at 33,600 kept shots each (two
  copies); the four corrected depth frequencies carry a common-mode standard error of 0.00067, 0.00074, 0.00027 and 0.00011
  (`decisions.readout.planned_frequency_sd`), against binomial 0.00096, 0.00166, 0.00171 and 0.00037.
- Limit of the arithmetic: the continuations come from fits of three retained points whose own uncertainty is not
  propagated (a red-team computation puts the retained difference of rho_4 at 0.0198 +- 0.0228), so the z of 3.63 is a
  sizing number and the probabilities below hold at the two retained continuations, not at every pair the retained data
  allow. The decisions compare the new run's four depths with the model, a within-job contrast that needs no retained
  covariance.

## Preregistered decision rule

Fixed in `results/iqm/cases/grover-fourth-depth-mirrored/prediction.json` (`decisions.rule`, `decisions.heterogeneity`, bound by
`cases.json.prediction_sha256`) and implemented by `grover_depth_families.read_copies` and `verdict`:

- Pooled marked counts per depth over the surviving mirror pairs, each frequency corrected to the model's readout by the
  eight readout preparations (see "Readout"); lambda_k = (y - 1/8) / (P_k - 1/8) from the corrected frequencies y; binomial
  variances at the observed frequencies plus the readout covariance, which ties the four depths together; every statistic
  below takes the full 4 x 4 covariance.
- bend: z = (f - model f) / SE over depths 1 to 3; z <= -3 reads "bends beyond the model at mirrored positions" (drift
  linear in position is excluded as the cause); z >= 3 "bends upward of the model"; otherwise "no bend resolved".
- family: chi2 of each family's fit to rho_1..rho_4 (two degrees of freedom, generalized least squares) over the rate
  domains of "Gates"; "neither family fits" when both exceed 9.21; "coherent" when chi2_geometric - chi2_coherent >= delta;
  "geometric" when <= -delta; otherwise "unresolved"; a rate bound turns a reading into "out of domain" only when the
  bound-limited fit is what it rests on ("Gates", "Domains"). delta is 7.0, the smallest threshold whose calibrated
  misclassification probabilities are all at most 0.01 ("Calibration"). The two fits read one data set, so the difference
  is taken on those data and no cross-job quantity enters the decision.
- influence: each of the bend and family readings stands only when every leave-one-mirror-pair-out refit reads the same
  category; otherwise it reads "not evaluated: the reading depends on one mirror pair" ("Gates").
- Reported beside and deciding nothing: rho_4 against the retained fits' continuations, and whether lambda decreases with
  depth.
- The model's own expected counts read "no bend resolved" and "unresolved" (`decisions.model.verdict_on_the_model_at_planned_shots`).

## Gates

Per-subject gating. A copy with fewer than half its planned kept shots (16,800 per copy planned) leaves its depth together
with the copy at its mirrored position (position p and 61 - p), so the surviving positions of every depth stay centered on
the job and a drift linear in position leaves each pooled frequency unchanged. A depth without a surviving pair is unusable;
the bend then needs depths 1 to 3 and reads "not evaluated" if one is missing, and the family comparison runs on any three
depths (one degree of freedom, adequacy 6.63) and is "not evaluated" below three. A copy without its mirror image in the
record raises.

Pair heterogeneity. The chi-square of the surviving mirror pairs of every depth (a copy and its image about the
center, pooled) about that depth's pooled marked frequency, sum over pairs of (M - N p)^2 / (N p (1 - p)) with M and N the pair's
marked count and kept shots and pairs - 1 degrees of freedom per depth, is summed over the depths (19 degrees of freedom with all 62 circuits kept: 6, 1, 1 and 11) and compared with the 0.99 chi-square quantile of its degrees of freedom (34.81 at 19),
which `prediction.json` holds for every degree of freedom (`decisions.heterogeneity.threshold_by_dof`). A drift linear in
position moves a copy and its image in opposite directions and leaves every pair, hence the statistic, unchanged; the
statistic sees what the pairing leaves (one copy displaced from its siblings, a quadratic or other symmetric drift, a step).
Above the threshold the bend and the family decisions both read "not evaluated": a depth's pooled frequency no longer
describes pairs that differ beyond binomial scatter. An earlier version of the gate took the chi-square of single copies; it
fired on exactly the linear drift the mirroring cancels (probability 0.30 or 0.99999 at the retained slope, depending on how
the drift reaches the depths), and the pair statistic replaced it.

The first reviewer's counterexamples: one depth-1 copy 0.04 above its siblings (read "geometric" at delta chi2 -18.5 under the
earlier pooling) reads "not evaluated" (statistic 31.2 on 11 degrees of freedom against 24.72, test
`test_a_copy_raised_by_four_points_reads_not_evaluated_on_raw_counts`); a dropped copy with a slope of -0.005 per
position (which read a bend at z -3.68 when the surviving positions were off center) leaves with its image, the surviving
positions stay centered and the linear slope cancels in every pair (test
`test_a_dropped_copy_and_a_linear_slope_read_the_centered_verdict`, which also plants -0.00003 per position): a depth-4 pair
that leaves reads the centered verdict "no bend resolved", and a depth-1 pair that leaves reads "not evaluated: the reading
depends on one mirror pair", because the one pair left at depth 1 cannot be refit without its depth. A symmetric quadratic
drift reads "not evaluated" (`test_a_symmetric_quadratic_drift_reads_not_evaluated`).

Influence. The heterogeneity statistic sums over depths and over pairs, so one defective copy can stay under its
threshold while it moves a decision: the second reviewer's depth-3 copy at position 4, lowered by 0.03, gives a statistic of
19.9 against 24.72, the family reading "coherent" (delta chi2 17.0) and a bend at z -3.96. Each reading therefore also needs
every leave-one-mirror-pair-out refit: the verdict on the pooled counts without one surviving pair (15 refits at the planned
design: 2, 2, 2 and 9 pairs at depths 1 to 4, run through `parallel.ordered_map`), each with the same readout correction,
must read the same category, the family's category of the rule and the bend's direction or none. A reading that changes
reads "not evaluated: the reading depends on one mirror pair", and the full reading stays beside it in
`decisions.influence`. The lowered copy now reads "not evaluated" for both decisions with the gate passed (test
`test_one_depth_3_copy_lowered_by_three_points_passes_the_gate_and_reads_not_evaluated`, whose refit without the pair at
positions 4 and 33 reads "unresolved" and no bend); the pooled counts of the same run read "coherent" and a bend, so the
plant is not vacuous. A depth with one surviving pair cannot lose it without becoming unusable, so its decisions need
that pair and read "not evaluated" there.

Readout. The eight preparations run in two copies each, `ro-xyz` and `ro-xyz-m` at mirrored positions, so the pooled marked row averages a drift linear in position as the depth arms do, and a glitch or a step inside the block shows as a difference between the two sides. Their marked fractions r'_j, the model's r_j and the model's distribution of each depth over the
prepared states (q_kj, from A^-1 applied to the depth's predicted distribution, A being the eight predicted preparations
as columns; `decisions.readout`) correct each depth's marked frequency to the model's readout by
y_k = p_k - sum_j q_kj (r'_j - r_j), and the shared rows give the four frequencies the common-mode covariance
sum_j q_kj q_lj r'_j (1 - r'_j) / n_j beside the binomial diagonal. A readout row 0.06 below the model's at the marked preparation lowers the depths by 0.042, 0.047, 0.017 and 0.004; the raw counts read a bend, the corrected ones read "no bend resolved" (test `test_a_readout_row_mismatch_reads_no_bend_once_the_job_readout_corrects_it`). Three preregistered readout gates turn both decisions into "not evaluated" (`decisions.readout`): the two sides of the block differ by more than their binomial scatter (a chi-square over the eight preparations against its 0.99 quantile at 8 degrees of freedom, 20.09); a preparation keeps under half its planned shots (so no division by zero reaches a statistic); a corrected frequency moves by more than the tolerance 0.05, 50 times its planned standard error, past which the first-order correction is not the small adjustment it is derived for. The record lists each row, its shift, its standard error and its chi-square against the model's rows beside.
A marked-frequency offset that the preparations do not share, such as a common -0.01 on every depth arm alone, is
indistinguishable from a retention loss and is outside what any readout analysis removes.

Power cost of the gate (`decisions.heterogeneity.power`, noncentral chi-square at the planned shots):

- Under the model, and under a drift linear in position of either kind (the same retention slope at every depth, or the same
  marked-frequency slope at every depth), the gate returns "not evaluated" with probability 0.01: at the retained slope
  of -0.000303 per position in marked frequency (-0.00046 in retention) the firing probability is 0.01 under both drift
  models, since no pair moves.
- One copy of depth 1 displaced from its siblings by 0.04 is detected with probability 0.94; the displacement detected half
  the time is 0.027 and nine tenths of the time 0.038. A displacement of 0.01 (the pooled-depth bias that 0.04 on one of four
  copies produces) is therefore the size the gate detects with probability near 0.5 or more; smaller ones pass and enter the
  pooled depth as a bias of a quarter of themselves.
- A symmetric quadratic drift (marked frequency moving by c times the squared offset from the center) trips it with
  probability 0.5 at c = 1.5e-5 per squared position and 0.9 at 2.0e-5 (in retention: 5.5e-5 and 7.6e-5). The retained job's
  inner copies minus its outer copies read -0.00053 +- 0.00364 in marked frequency, a curvature of 1.9e-6 +- 1.3e-5 per squared
  position: the gate fires with probability 0.012 at that point estimate and 0.49 at one standard error above it (0.010 and
  0.039 for a drift that follows the retention span). The data do not exclude a curvature the gate detects half the time.
- The pooled retention, hence the bend, is unbiased by a drift linear in position; a symmetric drift of curvature below the
  gate's detection remains in the pooled frequencies (the squared-offset spread of the depths, under a quarter, bounds how
  differently it enters them).

Domains. Both families search the rate s over one symmetric box [0.30, 1.20] (its offset
eps over a half period, since the family is even in eps; the geometric amplitude without bound). A bound blocks a reading
only when the bound-limited fit is what the reading rests on: the selected family's own fit sits on its bound, or no
family is selected ("neither family fits", "unresolved") while a fit sits on a bound; the reading is then "out of domain: the
... fit ends on its rate bound", because the bound, not the data, may have ended that fit's search. A bound-limited fit
that loses to an adequate interior fit by delta does not block and is named beside the reading
(`beside.fits_on_a_rate_bound`). Exact geometric data of amplitude 0.5 at s 0.7, 0.6, 0.5 and 0.4 read "geometric", coherent data at s 0.45 and 1.12 (outside the earlier coherent box, where the unequal boxes made a red team read "geometric") read "coherent", and coherent data (eps 1.5, s 0.9) read "coherent" although the geometric fit ends on 0.30; planted data at s 1.25 and 0.28 of either family read "out of domain". The retained fits (s 0.963 and 1.013) lie inside by at least 0.24 and 0.09.

Analyzer. `"$PYTHON" scripts/iqm_grover_fourth_depth.py analyze RUN_DIR --out OUT.json` reads one collected run through
`garnet_followup_analysis.read_job` (record checks, case and prediction digests, calibration set, measurement order, one run
of job `grover` on `garnet`; a `garnet:mock` run is refused), binds each circuit's file digest, depth (14 CZ per iteration),
position and mirror image to its counts, and applies the gates and the rule above (`gororoba_quantum/grover_depth_analysis.py`,
`grover_depth_families.read_copies`). It is tested on planted raw records (the model device; the two counterexamples; mock,
foreign-prediction and wrong-calibration runs; a mislabeled position, depth and circuit).

## Calibration

The difference of two non-nested chi-squares has no textbook null law, and the bounds, the readout covariance and the
influence check change it, so its threshold is computed (`gororoba_quantum/grover_depth_calibration.py`, recorded in
`decisions.calibration`). The method is quadrature, not simulation, and draws nothing at random: at these shots the four
corrected marked frequencies are Gaussian (3,000 or more kept shots per pair), with the binomial-plus-readout covariance at
the truth, so the probability of every reading is an integral over a four-dimensional standard normal vector, evaluated at
the 8,192 points of the unscrambled Sobol' sequence (`scipy.stats.qmc`, scrambling off, points 1 to 8,192) mapped through
the normal quantile; the case takes no seed. Agreement of the first 4,096 points with all 8,192 reads the quadrature's
own error (a test replays the first half). Truths: the retained geometric and coherent continuations and the model itself
(rho = 1, which both families contain, so either family named there is an error). Threshold: the smallest of 1.0, 1.5, ... 30
at which, on the first half and on all points, the geometric truth read as coherent, the coherent truth read as geometric
and the model read as either family each have probability at most 0.01. The result is delta = 7.0 (the earlier 9 was the
square of 3 sigma, a normal-theory number): at 7.0 the model reads a family with probability 0.0096 (0.0090 on the first
half), the geometric truth reads coherent and the coherent truth geometric with probability 0 in both halves. Readings at
7.0:

| truth | named correctly | unresolved | neither family fits | the other family |
|---|---|---|---|---|
| geometric | 0.990 | 0.000 | 0.010 | 0 |
| coherent | 0.992 | 0 | 0.008 | 0 |
| model | 0.984 (unresolved) | , | 0.006 | 0.010 (coherent 0.002, geometric 0.008) |

"Neither family fits" at about 0.01 under a true family is the 0.99 adequacy quantile itself. The bend reads "beyond the
model" under the coherent continuation and "no bend resolved" under the geometric one and the model, each with probability
above 0.99. The gates (bounds, heterogeneity, influence, readout) only turn a reading into "out of domain" or "not
evaluated", so these probabilities bound the misclassification of the gated rule from above. They hold at the three truths
named, not at every parameter pair of the two families, and the families are the oracle-phase representative and the
geometric loss only ("Residual risk").

## Power and its cost

Owner decision of 2026-11-22: with every gate on (pair heterogeneity, leave-one-pair-out influence, readout covariance, the
calibrated delta), the probability of the correct family verdict is at least 0.95 under both continuations, and z at the
planned shots stays at or above 3 after one depth-4 pair is lost, inside Garnet's limits and with the mirrored palindromic
arrangement. The power is computed by `calibration.influence_power` (`decisions.calibration.influence_power`: a Sobol'
set of 2,048 points in 4 + sum(pairs - 1) = 24 dimensions, the four pooled frequencies and the pairs' deviations from them,
since the pairs of a depth are iid at the planned shots; the pair-heterogeneity gate is the squared norm of the deviations;
the first half of the points sits beside as the quadrature's check). Chosen allocation, 14, 4, 4 and 24 copies of depths 1
to 4 (7, 2, 2 and 12 mirror pairs, 23 refits) and 16 readout circuits, 62 circuits:

| truth | pooled rule behind the heterogeneity gate | with every leave-one-pair-out refit |
|---|---|---|
| geometric continuation | 0.988 | 0.967 (first half 0.969) |
| coherent continuation | 0.989 | 0.965 (first half 0.966) |
| bend, geometric / coherent | 0.993 / 0.996 | 0.990 / 0.996 |

z at depth 4 is 3.63 with all twelve pairs and 3.49 after one is lost. Allocations tried (14.5 us per circuit-shot,
0.5 credits per second; power with every gate under the single-readout 38-circuit-style design and the unequal rate boxes,
1,024 points, delta 7.0; power is the one measured at that allocation under the single-readout design):

| copies at depths 1, 2, 3, 4 | circuits with 16 readout circuits | geometric | coherent | z after a depth-4 pair is lost |
|---|---|---|---|---|
| 4, 4, 4, 18 (before) | 46 | 0.632 | 0.967 | 2.93 |
| 8, 4, 4, 18 | 50 | 0.890 | 0.967 | 2.93 |
| 8, 4, 4, 22 | 54 | 0.899 | 0.966 | 3.24 |
| 8, 6, 6, 22 | 58 | 0.904 | 0.965 | 3.24 |
| 8, 8, 8, 24 | 64 | 0.911 | 0.967 | 3.38 |
| 8, 4, 4, 30 | 62 | 0.917 | 0.971 | 3.75 |
| 8, 6, 6, 34 | 70 | 0.925 | 0.964 | 3.97 |
| 8, 8, 8, 36 | 76 | 0.935 | 0.971 | 4.07 |
| 8, 4, 4, 40 | 72 | 0.936 | 0.972 | 4.26 |
| 10, 6, 6, 40 | 78 | 0.957 | 0.966 | 4.26 |
| 12, 8, 8, 40 | 84 | 0.961 | 0.972 | 4.26 |
| 10, 4, 4, 36 | 70 | 0.947 | 0.962 | 4.07 |
| 10, 4, 4, 40 | 74 | 0.953 | 0.965 | 4.26 |
| 12, 4, 4, 32 | 68 | 0.957 | 0.967 | 3.86 |
| 12, 4, 4, 36 | 72 | 0.957 | 0.966 | 4.07 |
| 12, 4, 4, 40 | 76 | 0.959 | 0.970 | 4.26 |
| 14, 4, 4, 32 | 70 | 0.962 | 0.967 | 3.86 |
| 12, 4, 4, 24 | 60 | 0.950 | 0.966 | 3.38 |
| 12, 4, 4, 28 | 64 | 0.951 | 0.964 | 3.63 |
| **14, 4, 4, 24 (chosen)** | **62** | 0.960 | 0.967 | 3.38 |
| 14, 4, 4, 28 | 66 | 0.959 | 0.966 | 3.63 |
| 16, 4, 4, 24 | 64 | 0.962 | 0.965 | 3.38 |
| 16, 4, 4, 28 | 68 | 0.966 | 0.969 | 3.63 |

Depth 1 limits the geometric continuation: with two pairs there a refit without one halves the depth. Pairs at depth 1 are
cheap (a depth-1 circuit is short), 12 copies at depth 4 carry z, and depths 2 and 3 keep two pairs each. The 12, 4, 4, 24
allocation reaches 0.9502 on the 1,024-point quadrature, inside that quadrature's error of 0.95, so 14 copies at depth 1 are
taken; the final design (mirrored readout, one symmetric rate box) was then run at 2,048 points and reads the table above.
The search was not repeated for the final design, so a cheaper allocation may meet the targets there.

## Falsifier

The bend repeats (z <= -3) at mirrored positions and "coherent" wins: a coherent error that accumulates with iterations is
supported within this family (an oracle phase error); the positional-drift cause is excluded at linear order. No bend
(|z| < 3): the retained bend came from drift of higher order than the mirroring cancels, or from chance, and the coherent
reading is unsupported. "Geometric" wins with the bend present: an incoherent depth-dependent loss the model omits.
"Not evaluated" (a failed heterogeneity gate): the mirror pairs of a depth differ by more than binomial scatter, a copy-specific or
non-linear positional effect that the mirroring does not cancel; neither decision is read, and the run shows the drift instead
of deciding the question. "Not evaluated: the reading depends on one mirror pair": the decision changes when one mirror pair
leaves, so a single pair, not the retention law, carries it. "Out of domain": a rate outside the stated box, reported as such. "Neither family fits": another mechanism (for example a ZZ phase or leakage) remains, and the oracle-phase family is refuted
as the sole cause.

## Cost

Expected seconds 17.98 (62 circuits x 20,000 shots x 14.5 us; the retained job measured 13.9 us per heralded circuit-shot,
1.99852 s over 144,000, and the depth-4 circuits add about 14 CZ at 40 ns; the refit of
[billing v3](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/iqm-billing-v3/docs/evidence/iqm-garnet-billing-v3/billing_v3.json),
PR 980, gives 0.1347 s + 7.62e-6 s per circuit-shot = 9.6 s plus the compiler's schedule estimate, which a free
`garnet:mock` compile reads and which was not read). Billed ceiling credits = ceil(1.6 + 17.98) x 0.50 = 10.0. max_credits
11.5 (23 billed seconds; `cancel_threshold_seconds` 22.0 s, 4.0 s above the expected run). The earlier 38-circuit case
carried 11.02 s, 6.5 credits and max_credits 8.0; the owner approved the added spend in principle on 2026-11-22 (the
approval of the digest below waits for the owner). Expected spend about 9 credits. The case rule of `scripts/iqm_jobs.py`
cancels a job that reaches the threshold, and IQM can bill a failed or cancelled job, so the ceiling bounds the spend and is
not a guarantee of zero cost on a cancellation. `cases.json` binds the regenerated prediction and has sha256
`6cec34c14011a4bbb6536bd3b66f9aaae9de40f0116f2bca72a6282581108854` on calibration set `a0e725eb` (a live rebuild may change
it, and the approvals name the digest after that rebuild).

## Steps before a submission (owner approval needed for each paid or provider step)

Every step runs through `scripts/iqm_jobs.py` (the IQM path); `scripts/approved_run.sh` and `live_run.py` drive the IBM runtime and
take no part.

1. Calibration is a property of the run: the case is rebuilt first with
   `"$PYTHON" scripts/iqm_grover_fourth_depth.py build results/iqm/cases/grover-fourth-depth-mirrored --live` (a free read of
   Garnet's current default calibration set), which regenerates the circuits, the prediction and the digest of `cases.json`;
   the sizing numbers above are re-read from the new prediction. The set `a0e725eb` build is the written case. The digest
   `cases.json` carries after the rebuild is the digest the approvals below name.
2. The owner approves the refreshed written case and its digest for the free mock. The mock runs
   `IQM_TOKENS_FILE=TOKENS.json "$PYTHON" scripts/iqm_jobs.py submit results/iqm/cases/grover-fourth-depth-mirrored grover --qc garnet:mock --approval QUOTE --approved-cases-sha256 DIGEST --max-credits 0`
   and `collect RUN_DIR`, to confirm the job is accepted and counts return in the case's shape; its random outcomes never
   enter analysis (the analyzer refuses a mock run). Not run; it needs the owner's approval.
3. The owner approves the identical digest for Garnet (backend, circuits, shots, expected seconds, credits, max_credits,
   falsifier): `submit ... --qc garnet --approved-cases-sha256 DIGEST --max-credits 8.0`, then `collect RUN_DIR`, then
   `analyze RUN_DIR --out OUT.json`.
4. A rebuild that changes the digest between steps 2 and 3 repeats step 2 for the new digest; the mock always exercises the
   digest that Garnet then runs.

## Residual risk

- **Not repaired: the coherent family.** It is the oracle-phase representative with a fixed prefactor. A red team's exact
  simulation of the committed circuits with a CZ conditional-phase error of -0.03 rad or a PRX amplitude error of -2 %
  reproduces the retained bend and reads "neither family fits", and a 3 % common SPAM factor on exact oracle-phase data fails
  adequacy. A circuit-level coherent family (a CZ phase error and a PRX amplitude error fitted by exact simulation of the
  line-native circuits, a free depth-independent prefactor on both families) with its own calibration and allocation search
  is open work; until it lands, "neither family fits" is the likely reading of a circuit-level coherent error and the 0.95
  targets hold for the two representatives only.
- **Not repaired: the retained fits' uncertainty.** The sizing takes the two retained continuations as exact; a red-team
  sample of the three retained points gives a difference of rho_4 of 0.0198 +- 0.0228, so the probability that the run
  resolves the families at all is not the 0.96 and 0.97 above but their average over that spread, which is not computed.
- The ledger binding of the case's float records to the runner image (`ci/runner_image_records.json`) is not done; it needs
  a podman host's receipts.
- Mirroring cancels drift linear in position; drift that is not linear stays, balanced to the order of the squared-offset
  spread.
- The pair-heterogeneity gate (power figures here are those of the earlier 38-circuit design) detects a copy displaced by 0.04 with probability 0.94 and a displacement of 0.027 half the time;
  smaller single-copy displacements and symmetric drifts under its detection enter the pooled depths unflagged, and the
  data's curvature estimate (1.9e-6 +- 1.3e-5 per squared position) leaves a gate-detectable curvature within one standard error.
- A rate bound still blocks a reading that rests on a bound-limited fit (the selected family's own fit, "neither family
  fits", "unresolved"), so data whose true rate lies outside a box read "out of domain" and no verdict.
- The threshold's misclassification probabilities are computed at three truths (the two retained continuations and the
  model) on a Gaussian approximation of the four frequencies; other parameter pairs of the families and the tails beyond
  the normal limit are not covered, and the quadrature's own error is about 0.001 (first half against all points).
- The influence check costs each continuation about 0.02 of resolution probability at the planned copies ("Power and its
  cost"); a readout block of two copies per preparation is guarded by its own side-to-side gate, and a step that crosses
  the depth arms and the readout arms equally is the mirrored-position drift the design cancels.
- The readout correction is first-order linear in the marked row and takes the model's depth distributions q as exact;
  a readout change that is not a change of the marked row (a changed row of another outcome that leaks into the mark
  through the depth's state) enters through q alone.

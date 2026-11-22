# IQM Garnet fourth Grover depth at mirrored positions

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made in
the repairs that added the analyzer, the mirror-pair and heterogeneity gates, the rate domains, the leave-one-pair-out
influence check, the readout correction and the calibrated family threshold. **Open design decision: the influence check
leaves the geometric continuation a resolution probability of 0.63 at the planned copies (see "Power and its cost").**

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

38 circuits, one job, 20,000 shots, heralding `zeros`, one active-reset cycle: line-native Grover of mark 101 (14 CZ per
iteration; 56 CZ and 82 prx at depth 4) on QB20-QB16-QB17 (QB12 lies outside Garnet's gate set and is not used), at depth 1,
2, 3 and 4 in 4, 4, 4 and 18 copies, and the eight readout preparations `ro-xyz`. Order (`arrangement()`): half of every
depth's copies, the eight readouts, the first half reversed, so every depth's summed position is its copy count times the
center (verified by the self-test and `tests/test_iqm_grover_fourth_depth.py`) and the squared offsets of the depths differ by
less than a quarter, which also balances a quadratic drift to that order. The first half is the constant `FIRST_HALF` of the
script, the optimum of the exhaustive search over the 450,450 orderings (`best_first_half()`, sharded through
`parallel.ordered_map`); a build verifies its invariants, and a test reruns the search against the constant. The case draws no
random number and takes no seed.

## Resolution arithmetic

- Retained ratios rho = lambda / model lambda at depths 1 to 3: 0.9855, 0.9697, 0.7605. Fitted by each family (weighted
  least squares at the retained kept shots 13,450, 3,377, 3,383): geometric a = 1.0260, s = 0.9634 (chi2 11.29 on one
  degree of freedom); coherent eps = 0.3043, s = 1.0134 (chi2 0.85). The coherent fit's s above 1 means the model's loss
  slightly overstates the device's at small depth.
- Continued to depth 4 and scaled by this calibration's model lambda_4 = 0.5805: geometric lambda_4 = 0.5130, coherent
  0.5262 (difference 0.0132). Both continuations decrease from their depth-3 values (lambda_3 is 0.547 coherent and 0.649 geometric on this
  calibration, so lambda_4 is 0.526 and 0.513), so monotonicity does not separate them; the separation is 0.0132 in lambda, 0.0228 in rho.
- Kept shots at 0.84 of requested (retained 0.841 to 0.846): 67,200 at depths 1 to 3 and 302,400 at depth 4. The standard
  error of rho_4 is 0.00734 with the binomial scatter and the eight readout preparations' covariance (0.00695 binomial
  alone), so the continuations separate by 3.09 standard errors (3.27 before the readout covariance); they resolve at 3
  down to a kept fraction of 0.79 at depth 4 (z scales with the root of the kept shots: 0.84 x (3 / 3.09)^2).
- Pairs leave the pooled depths together (see "Gates"), and the influence check refits without each pair in turn: with one of
  the nine depth-4 mirror pairs gone the separation z falls from 3.09 to 2.93, with two to 2.76 and with three to 2.57; the
  bend's standard error is 0.0094 with all copies and 0.0097, 0.0101 and 0.0126 with one pair gone from depth 1, 2 and 3,
  still 10 standard errors from the retained deviation of 0.133. The family comparison below does not use the retained
  continuations.
- Over four depths, if the data equal the coherent values the geometric fit leaves chi2 = 175.8 (183.2 binomial only), and
  if they equal the geometric values the coherent fit leaves chi2 = 18.1 (24.9); both exceed the calibrated threshold of 7.
- The bend uses three arms: its standard error at the planned shots is 0.0094 against the retained
  f of -0.122 against the model's +0.010 (a deviation of 0.133, about 14 standard errors if the bend repeats).
- The eight readout preparations ro-xyz measure the marked row of the job's assignment matrix at 16,800 kept shots each;
  the four corrected depth frequencies carry a common-mode standard error of 0.00095, 0.00105, 0.00038 and 0.00016
  (`decisions.readout.planned_frequency_sd`), against binomial 0.0018, 0.0017, 0.0017 and 0.0004.
- Limit of the arithmetic: the continuations come from fits of three retained points whose own uncertainty is not
  propagated, so the z of 3.27 is a sizing number. The decisions below compare the new run's four depths with the model, a
  within-job contrast that needs no retained covariance.

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
with the copy at its mirrored position (position p and 37 - p), so the surviving positions of every depth stay centered on
the job and a drift linear in position leaves each pooled frequency unchanged. A depth without a surviving pair is unusable;
the bend then needs depths 1 to 3 and reads "not evaluated" if one is missing, and the family comparison runs on any three
depths (one degree of freedom, adequacy 6.63) and is "not evaluated" below three. A copy without its mirror image in the
record raises.

Pair heterogeneity. The chi-square of the surviving mirror pairs of every depth (a copy and its image about the
center, pooled) about that depth's pooled marked frequency, sum over pairs of (M - N p)^2 / (N p (1 - p)) with M and N the pair's
marked count and kept shots and pairs - 1 degrees of freedom per depth, is summed over the depths (11 degrees of freedom with
all 38 circuits kept: 1, 1, 1 and 8) and compared with the 0.99 chi-square quantile of its degrees of freedom (24.72 at 11),
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

Readout. The eight preparations `ro-xyz` sit at the center of the job, where the mirrored depth arms average a drift
linear in position. Their marked fractions r'_j, the model's r_j and the model's distribution of each depth over the
prepared states (q_kj, from A^-1 applied to the depth's predicted distribution, A being the eight predicted preparations
as columns; `decisions.readout`) correct each depth's marked frequency to the model's readout by
y_k = p_k - sum_j q_kj (r'_j - r_j), and the shared rows give the four frequencies the common-mode covariance
sum_j q_kj q_lj r'_j (1 - r'_j) / n_j beside the binomial diagonal. A readout row 0.1 below the model's at the marked
preparation lowers the depths by 0.071, 0.078, 0.028 and 0.006; the raw counts read a bend (z -5.6), the corrected ones read
"no bend resolved" (test `test_a_readout_row_mismatch_reads_no_bend_once_the_job_readout_corrects_it`). The record lists
each row, its shift, its standard error and its chi-square against the model's rows beside, which decides nothing.
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

Domains. The geometric family's rate s is searched over [0.30, 1.20] and the coherent family's over [0.50, 1.10] (its offset
eps over a half period, since the family is even in eps; the geometric amplitude without bound). A bound blocks a reading
only when the bound-limited fit is what the reading rests on: the selected family's own fit sits on its bound, or no
family is selected ("neither family fits", "unresolved") while a fit sits on a bound; the reading is then "out of domain: the
... fit ends on its rate bound", because the bound, not the data, may have ended that fit's search. A bound-limited fit
that loses to an adequate interior fit by delta does not block and is named beside the reading
(`beside.fits_on_a_rate_bound`). Exact geometric data of amplitude 0.5 at s 0.7, 0.6, 0.5 and 0.4 read "geometric" although
the coherent fit ends on its bound of 0.5 (chi2 1,822 at s 0.7 where the geometric fit leaves 0), and coherent data
(eps 1.5, s 0.9) read "coherent" although the geometric fit ends on 0.30; planted data at s 1.25 (geometric) and 0.28, and
at s 1.11 (coherent), read "out of domain". The retained fits (s 0.963 and 1.013) lie inside by at least 0.24 and 0.09.

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
square of 3 sigma, a normal-theory number): at 7.0 the model reads a family with probability 0.0087 (0.0088 on the first
half; 0.0125 at 6.5), the geometric truth reads coherent and the coherent truth geometric with probability 0 in both
halves, and at 9 the model reads a family with probability 0.0028. Readings at 7.0:

| truth | named correctly | unresolved | neither family fits | the other family |
|---|---|---|---|---|
| geometric | 0.908 | 0.083 | 0.009 | 0 |
| coherent | 0.991 | 0 | 0.009 | 0 |
| model | 0.985 (unresolved) | , | 0.006 | 0.009 (coherent 0.002, geometric 0.007) |

The bend reads "beyond the model" with probability 1.00 under the coherent continuation and "no bend resolved" with 0.997
under the geometric one and under the model. The gates (bounds, heterogeneity, influence) only turn a reading into "out of
domain" or "not evaluated", so these probabilities bound the misclassification of the gated rule from above. They hold at
the three truths named, not at every parameter pair of the two families.

## Power and its cost

The influence check refits without each of the 15 surviving mirror pairs and requires the reading to stand
(`decisions.calibration.influence_power`, a Sobol' set of 2,048 points in 15 dimensions: the four pooled frequencies and the
pairs' deviations from them, since the pairs of a depth are iid at the planned shots; the first half of the points sits beside
as the quadrature's check). Probability that the reading names the truth:

| truth | pooled rule | with every leave-one-pair-out refit |
|---|---|---|
| geometric continuation | 0.906 | **0.635** (refits that differ: depth 1 0.260, depth 4 0.061, depth 3 0.041, depth 2 0.006) |
| coherent continuation | 0.994 | 0.970 |
| model | 0.987 | 0.955 |
| bend, any of the three truths | 0.997 to 1.000 | 0.991 to 1.000 |

The geometric continuation loses most because depths 1 to 3 hold two mirror pairs each: a refit without one halves that
depth's data, and depth 1 anchors the amplitude of the geometric fit. The separation z at depth 4 is 3.09 with all nine
pairs there and 2.93 with eight, below the resolution of 3 that the case was sized for (3.27 before the readout covariance).
Arithmetic of the repair, from the same quadrature (not run on hardware): eight depth-1 copies (four mirror pairs, 4 more
circuits) raise the geometric continuation's probability with the influence check from 0.635 to 0.893 (pooled 0.973), and eight
copies at each of depths 1 to 3 to 0.900; two more depth-4 copies (ten pairs) restore z = 3.09 after a pair leaves.
Six more circuits make 44 circuits, 12.76 expected seconds at the 14.5 us bound, ceiling credits 7.5 and max_credits 9.0
(now 38, 11.02, 6.5 and 8.0), a change of the approved spend that waits for the owner.

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

Expected seconds 11.02 (38 circuits x 20,000 shots x 14.5 us; the retained job measured 13.9 us per heralded circuit-shot,
1.99852 s over 144,000, and the depth-4 circuits add about 14 CZ at 40 ns; the refit of
[billing v3](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/iqm-billing-v3/docs/evidence/iqm-garnet-billing-v3/billing_v3.json),
PR 980, gives 0.1347 s + 7.62e-6 s per circuit-shot = 5.9 s plus the compiler's schedule estimate, which a free
`garnet:mock` compile reads and which was not read). Billed ceiling credits = ceil(1.6 + 11.02) x 0.50 = 6.5. max_credits 8.0
(16 billed seconds; `cancel_threshold_seconds` 15.0 s, 3.7 s above the expected run). Expected spend about 6 credits. The
case rule of `scripts/iqm_jobs.py` cancels a job that reaches the threshold, and IQM can bill a failed or cancelled job, so
the ceiling bounds the spend and is not a guarantee of zero cost on a cancellation. The repairs of the analyzer, the gates, the readout correction and the threshold
leave the circuits, shots, expected seconds and credits as they were; `cases.json` binds the regenerated prediction and has
sha256 `5abaec9abe1a88d9968cc65ae4ab20d93b597cbc5e7decca738d10b3162f9e9d` on calibration set `a0e725eb` (a live rebuild may change
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

- The coherent family is one representative (an oracle phase error per iteration); a different coherent error (ZZ,
  leakage) can bend the law outside it, in which case the verdict is "neither family fits" or a family that fits by accident.
- The coherent fit's s above 1 and the three-point fits carry uncertainty that the sizing does not propagate.
- The ledger binding of the case's float records to the runner image (`ci/runner_image_records.json`) is not done; it needs
  a podman host's receipts.
- Mirroring cancels drift linear in position; drift that is not linear stays, balanced to the order of the squared-offset
  spread.
- The pair-heterogeneity gate detects a copy displaced by 0.04 with probability 0.94 and a displacement of 0.027 half the time;
  smaller single-copy displacements and symmetric drifts under its detection enter the pooled depths unflagged, and the
  data's curvature estimate (1.9e-6 +- 1.3e-5 per squared position) leaves a gate-detectable curvature within one standard error.
- A rate bound still blocks a reading that rests on a bound-limited fit (the selected family's own fit, "neither family
  fits", "unresolved"), so data whose true rate lies outside a box read "out of domain" and no verdict.
- The threshold's misclassification probabilities are computed at three truths (the two retained continuations and the
  model) on a Gaussian approximation of the four frequencies; other parameter pairs of the families and the tails beyond
  the normal limit are not covered, and the quadrature's own error is about 0.001 (first half against all points).
- The influence check costs the geometric continuation about 0.27 of resolution probability at the planned copies
  ("Power and its cost"); the copies that remove most of it add circuits and spend, and wait for the owner.
- The readout correction is first-order linear in the marked row and takes the model's depth distributions q as exact;
  a readout change that is not a change of the marked row (a changed row of another outcome that leaks into the mark
  through the depth's state) enters through q alone.

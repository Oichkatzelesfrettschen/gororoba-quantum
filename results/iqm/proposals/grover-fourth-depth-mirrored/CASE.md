# IQM Garnet fourth Grover depth at mirrored positions

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made in
any repair. The copy counts and the coherent families follow the owner's decisions of 2026-11-22 ("Power and its
allocation").

Backend `iqm:garnet` (20 qubits, pay-as-you-go 0.50 credits per second; limits 20,000 shots per circuit, 100 circuits
and 2,000,000 executions per job, [limits](../../../../docs/evidence/iqm/qc/garnet/limits.json)). The case directory
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

38 circuits, one job, 20,000 shots (760,000 executions), heralding `zeros`, one active-reset cycle: line-native Grover of
mark 101 (14 CZ per iteration; 56 CZ and 82 prx at depth 4) on QB20-QB16-QB17 (QB12 lies outside Garnet's gate set and is
not used), at depth 1, 2, 3 and 4 in 4, 4, 4 and 10 copies (22 depth circuits), and the eight readout preparations
`ro-xyz` in two copies each (`ro-xyz` and `ro-xyz-m`, one on each side of the job's center: 16 readout circuits). Order
(`arrangement()`): a first half of 19 circuits (half the copies of every depth and each readout preparation once), then the
first half reversed, so every kind's summed position is its count times the center and each readout preparation sits at
mirrored positions on both sides. The squared offsets of the kinds differ by 1 % (a spread of 1.25 in about 120), which
balances a quadratic drift to that order. The first half is the constant `FIRST_HALF` of the script, the local optimum of single
exchanges of two circuits from an even spread (`best_first_half()`, every round's exchanges scored through
`parallel.ordered_map`; a build verifies its invariants and a test reruns the search against the constant and checks that no
exchange lowers the spread). The case draws no random number and takes no seed.

## The three families

Every family describes rho_k = lambda_k / M_k, the ratio of the retention at depth k to the density-matrix model's, which is
1 when the model holds. Each has the same free depth-independent prefactor a and a per-iteration rate s in [0.30, 1.20]:

- geometric: rho_k = a s^k, an incoherent loss beyond the model that compounds per iteration;
- coherent, CZ conditional phase: rho_k = a s^k R_k(x), where R_k(x) is the marked probability of the committed depth-k
  circuit above the uniform floor, relative to its ideal value, when every CZ applies the conditional phase pi + x
  (|x| <= 0.3 rad), by exact simulation of the committed circuits (`gororoba_quantum/grover_depth_circuits.py`, which
  reproduces `iqm_garnet_followup.ideal` to 1e-12 at x = 0);
- coherent, PRX amplitude: the same with every PRX rotating by theta (1 + x) (|x| <= 0.10).

The bounds are symmetric about the ideal gate and far beyond the calibrated gates of the device. The coherent families nest
the geometric one (x = 0) and the geometric one nests the model (a = s = 1), so the rule compares nested fits. The coherent
fits have three parameters and the geometric two, so four depths leave one and two degrees of freedom; the family decision
needs all four depths. Exact simulation with a CZ phase of -0.03 rad gives R = (1.0209, 0.9744, 0.7469, 0.8055) at
depths 1 to 4 and a PRX amplitude of -2 % gives (1.0178, 0.9743, 0.7123, 0.7649): a dip at depth 3 that the three retained
depths see as the bend and a rebound at depth 4 that no geometric law has (test
`test_the_circuit_simulation_reproduces_the_ideal_outcomes_and_the_exact_error_values`).

## Resolution arithmetic

- Retained ratios rho = lambda / model lambda at depths 1 to 3: 0.9855, 0.9697, 0.7605 (standard errors 0.0073, 0.0125,
  0.0518). Fitted by each family (generalized least squares at the retained kept shots 13,450, 3,377, 3,383): geometric
  a = 1.0260, s = 0.9634 (chi2 11.29 on one degree of freedom); each coherent family fits the three ratios exactly with
  three parameters: CZ phase x = -0.0309 rad (a 0.9347, s 1.0323), PRX amplitude x = -1.73 % (a 0.9498, s 1.0216).
- Continued to depth 4 and scaled by this calibration's model lambda_4 = 0.5805: geometric lambda_4 = 0.5130, CZ phase
  0.4920, PRX amplitude 0.4832 (the continuations of rho_4: 0.884, 0.848 and 0.832).
- Kept shots at 0.84 of requested (retained 0.841 to 0.846): 67,200 at depths 1 to 3 and 168,000 at depth 4. The standard
  error of rho_4 is 0.0096 with the binomial scatter and the readout covariance, so the geometric and CZ-phase continuations
  separate by z = 3.76 (3.82 binomial alone) and the geometric and PRX ones by 5.30. With one of the five depth-4 mirror
  pairs gone z is 3.38 and 4.75, with two 2.93 and 4.13, with three 2.40 and 3.38. The bend's standard error is 0.0094 with
  all copies and `0.0096`, `0.0101` and `0.0126` with one pair gone from depth 1, 2 and 3.
- If the data equal the CZ-phase (PRX) continuation the geometric fit leaves chi2 232.3 (238.4); if they
  equal the geometric continuation the model leaves chi2 465.7; both exceed the calibrated delta of 9.5.
- The eight readout preparations measure the marked row of the job's assignment matrix at 33,600 kept shots each (two
  copies); the four corrected depth frequencies carry a common-mode standard error of 0.00067, 0.00074, 0.00027, 0.00011
  (`decisions.readout.planned_frequency_sd`).

## Retained uncertainty and the probability of resolving the families

The sizing above takes the retained fits as exact. They are not: three retained ratios carry standard errors of 0.007,
0.012 and 0.052, and the retained difference of rho_4 between the geometric and CZ-phase continuations is
0.041 +- 0.028 over the moved retained data. `decisions.retained_uncertainty` propagates it: 64 points of the
unscrambled Sobol' sequence of dimension 3 move the retained ratios within their covariance, each family is refitted and
continued to depth 4, and the planned run's pooled rule (with the binomial and readout covariance, 256 Sobol' points of
its own noise, no seed) reads that continuation. Probability that the run names the true family when the retained data
follow it:

| hypothesis | names the true family | names a family | rho_4 of the family |
|---|---|---|---|
| geometric | 0.996 +- 0.000 | 0.996 | 0.885 +- 0.031 |
| coherent, CZ phase | 0.996 +- 0.031 | 0.999 | 0.844 +- 0.043 |
| coherent, PRX amplitude | 0.993 +- 0.029 | 0.996 | 0.829 +- 0.045 |

The probability that the run resolves the families at all, with the retained uncertainty propagated, is
0.995 (the mean over the three hypotheses, pooled rule; the gates of "Gates" lower it by the
amounts of "Power and its allocation"). The probability rests on the geometric, CZ-phase and PRX-amplitude families
being the candidates; another error (ZZ, leakage, a drift of the error between depths) is outside it.

## Preregistered decision rule

Fixed in `results/iqm/cases/grover-fourth-depth-mirrored/prediction.json` (`decisions.rule`, `decisions.heterogeneity`,
`decisions.calibration`, `decisions.readout`, bound by `cases.json.prediction_sha256`) and implemented by
`grover_depth_families.read_copies` and `verdict`:

- Pooled marked counts per depth over the surviving mirror pairs, each frequency corrected to the model's readout by the
  eight readout preparations ("Gates"); lambda_k = (y - 1/8) / (P_k - 1/8); binomial variances at the observed frequencies plus the
  readout covariance, which ties the four depths together; every statistic takes the full 4 x 4 covariance.
- bend, a decision of its own that stands whatever the family reads: z = (f - model f) / SE over depths 1 to 3 with
  f = lambda_3 - lambda_2^2 / lambda_1; z <= -3 reads "bends beyond the model at mirrored positions" (drift linear in
  position is excluded as the cause); z >= 3 "bends upward of the model"; otherwise "no bend resolved".
- family, over all four depths with delta = 9.5 (calibrated below) and the 0.99 chi-square quantile at the fit's degrees of freedom
  as its adequacy (9.21 at two, 6.63 at one): "neither family fits" when the geometric chi-square exceeds 9.21 and the
  better coherent one exceeds 6.63; else "coherent" when the better coherent fit is adequate and the geometric chi-square
  exceeds its own by delta; else "geometric" when the geometric fit is adequate and the model's chi-square (rho = 1) exceeds
  the geometric one by delta (a loss beyond the model); else "unresolved". A fit on a bound blocks a reading only when the
  reading rests on it: "coherent" blocks when the coherent fit sits on a bound, every other reading when either fit does,
  as "out of domain". The better coherent family (CZ phase or PRX amplitude) is named beside the reading.
- influence: each of the bend and family readings stands only when every leave-one-mirror-pair-out refit reads the same
  category; otherwise it reads "not evaluated: the reading depends on one mirror pair".
- Reported beside and deciding nothing: rho_4 against the retained continuations, the fits on a bound, and whether the
  retention decreases with depth.
- The model's own expected counts read "no bend resolved" and "unresolved" (`decisions.model.verdict_on_the_model_at_planned_shots`).

## Gates

Per-subject gating. A copy with fewer than half its planned kept shots (16,800 per copy planned) leaves its depth together
with the copy at its mirrored position (position p and 37 - p), so the surviving positions of every depth stay centered on
the job and a drift linear in position leaves each pooled frequency unchanged. A depth without a surviving pair is unusable;
the bend then reads "not evaluated" if depth 1, 2 or 3 is missing, and the family comparison (four depths) reads "not
evaluated" if any is. A copy without its mirror image in the record raises.

Pair heterogeneity. The chi-square of the surviving mirror pairs of every depth about that depth's pooled marked frequency,
sum over pairs of (M - N p)^2 / (N p (1 - p)) with M and N the pair's marked count and kept shots and pairs - 1 degrees of
freedom per depth, is summed over the depths (7 degrees of freedom with all 38 circuits kept: 1, 1, 1 and 4) and compared with
the 0.99 chi-square quantile of its degrees of freedom (18.48 at 7), which `prediction.json` holds for every degree of
freedom (`decisions.heterogeneity.threshold_by_dof`). A drift linear in position moves a copy and its image in opposite
directions and leaves every pair unchanged; the statistic sees what the pairing leaves (one copy displaced from its
siblings, a quadratic or other symmetric drift, a step between a copy and its image). Above the threshold the bend and the
family decisions both read "not evaluated".

Influence. The heterogeneity statistic sums over depths and pairs, so one defective copy can stay under its threshold
while it moves a decision. Each reading therefore also needs every leave-one-mirror-pair-out refit (11 refits at the
planned design: 2, 2, 2 and 5 pairs at depths 1 to 4, through `parallel.ordered_map`), each with the same readout
correction, to read the same category (the family's category, the bend's direction or none); a reading that changes reads
"not evaluated: the reading depends on one mirror pair" and the full reading stays beside it in `decisions.influence` (tests
`test_one_depth_3_copy_lowered_by_under_three_points_passes_the_gate_and_reads_not_evaluated`,
`test_a_dropped_copy_and_a_linear_slope_read_the_centered_verdict`). A depth with one surviving pair cannot lose it without
becoming unusable, so its decisions need that pair and read "not evaluated" there; with two pairs per depth at depths 1 to
3, one failed copy there takes the family decision and the bend with it.

Readout. The eight preparations run in two copies each, `ro-xyz` and `ro-xyz-m` at mirrored positions, so the pooled marked
row averages a drift linear in position as the depth arms do, and a glitch or a step inside the block shows as a difference
between the two sides. Their marked fractions r'_j, the model's r_j and the model's distribution of each depth over the
prepared states (q_kj, from A^-1 applied to the depth's predicted distribution, A the eight predicted preparations as columns;
`decisions.readout`) correct each depth's marked frequency to the model's readout by y_k = p_k - sum_j q_kj (r'_j - r_j), and the
shared rows give the four frequencies the common-mode covariance sum_j q_kj q_lj r'_j (1 - r'_j) / n_j beside the binomial
diagonal. Three preregistered readout gates turn both decisions into "not evaluated": the two sides of the block differ by
more than their binomial scatter (a chi-square over the eight preparations against its 0.99 quantile at 8 degrees of freedom,
20.09); a preparation keeps under half its planned shots (so no division by zero reaches a statistic); a corrected frequency
moves by more than the tolerance 0.05, 50 times its planned standard error. A readout row 0.06 below the model's at the
marked preparation lowers the depths by 0.042, 0.047, 0.017 and 0.004: the raw counts read a bend, the corrected ones read
"no bend resolved" (test `test_a_readout_row_mismatch_reads_no_bend_once_the_job_readout_corrects_it`). A marked-frequency offset
that the preparations do not share, such as a common -0.01 on every depth arm alone, is indistinguishable from a retention
loss and outside what any readout analysis removes.

Power cost of the pair gate (`decisions.heterogeneity.power`, noncentral chi-square at the planned shots): under the model and under a
drift linear in position the gate returns "not evaluated" with probability 0.01; one copy of depth 1 displaced from its
siblings by 0.04 is detected with probability 0.97, the displacement detected half the time is
0.025; a symmetric quadratic drift of marked frequency trips it with probability 0.5 at 1.7e-5 per squared position.
Smaller single-copy displacements and symmetric drifts under its detection enter the pooled depths unflagged.

Domains. The three families search the rate s over one box [0.30, 1.20] and the coherent error over its symmetric bound
(0.3 rad, 10 %). A fit on a bound blocks only a reading that rests on it ("The three families"); data of either coherent
family past its bound read "out of domain", and exact geometric data of amplitude 0.5 at s 0.7, 0.5, 0.4 and 0.32 read
"geometric" (tests `test_data_inside_the_boxes_read_their_family`,
`test_data_outside_a_bound_read_out_of_domain_not_neither_family`).

Analyzer. `"$PYTHON" scripts/iqm_grover_fourth_depth.py analyze RUN_DIR --out OUT.json` reads one collected run through
`garnet_followup_analysis.read_job` (record checks, case and prediction digests, calibration set, measurement order, one run
of job `grover` on `garnet`; a `garnet:mock` run is refused), binds each circuit's file digest, depth (14 CZ per iteration),
position and mirror image to its counts, and applies the gates and the rule above (`gororoba_quantum/grover_depth_analysis.py`,
`grover_depth_families.read_copies`). It is tested on planted raw records.

## Calibration

The difference of nested chi-squares has no textbook null law once the bounds, the readout covariance, the circuit-level
families and the influence check enter, so the threshold is computed (`gororoba_quantum/grover_depth_calibration.py`, recorded in
`decisions.calibration`). The method is quadrature, not simulation, and draws nothing at random: at these shots the four
corrected marked frequencies are Gaussian (3,000 or more kept shots per pair), with the binomial-plus-readout covariance at the
truth, so the probability of every reading is an integral over a four-dimensional standard normal vector, evaluated at the
8,192 points of the unscrambled Sobol' sequence (`scipy.stats.qmc`, scrambling off, points 1 to 8,192) mapped through the normal
quantile; the case takes no seed. Agreement of the first 4,096 points with all of them reads the quadrature's own error (a test replays
the first half). Truths: the retained geometric, CZ-phase and PRX-amplitude continuations and the model itself (rho = 1, which
every family contains, so a family named there is an error). Threshold: the smallest of 1.0, 1.5, ... 30 at which, on the first
half and on all points, the geometric truth read as coherent, either coherent truth read as geometric and the model read as
either family each have probability at most 0.01. The result is delta = 9.5: at that value the model names a family
with probability 0.0099 (0.0081 on the first half). Readings at delta 9.5:

| truth | named correctly | unresolved | neither family fits | the other family |
|---|---|---|---|---|
| geometric | 0.990 | 0.004 | 0.004 | 0.002 |
| coherent, CZ phase | 0.994 | 0.000 | 0.006 | 0.000 |
| coherent, PRX amplitude | 0.994 | 0.000 | 0.006 | 0.000 |
| model | 0.986 (unresolved) | , | 0.004 | 0.010 |

Adequacy. The 0.99 chi-square quantiles at one and two degrees of freedom (6.63, 9.21) are the adequacy limits; the measured
"neither family fits" rate under a true family is 0.004 to 0.006, inside the nominal 0.01, so the limits are kept. The bend reads "beyond the model" under both coherent
continuations and "no bend resolved" under the geometric one and the model, each with probability above 0.99. The gates (bounds,
heterogeneity, influence, readout) only turn a reading into "out of domain" or "not evaluated", so these probabilities bound
the misclassification of the gated rule from above. They hold at the four truths named, not at every parameter triple of the
families.

## Power and its allocation

Owner decision of 2026-11-22: with every gate on (pair heterogeneity, leave-one-pair-out influence, readout covariance, the
calibrated delta), the probability of the correct family verdict is at least 0.95 under both continuations (the CZ-phase and
PRX-amplitude coherent ones and the geometric one), and z at the planned shots stays at or above 3 after one depth-4 pair is
lost, inside Garnet's limits with the mirrored palindromic arrangement; choose the cheapest allocation. The power is
computed by `calibration.influence_power` (`decisions.calibration.influence_power`: a Sobol' set of 2048 points in
4 + sum(pairs - 1) = 11 dimensions, the four pooled frequencies and the pairs' deviations from them, since the pairs of a depth
are iid at the planned shots; the pair-heterogeneity gate is the squared norm of the deviations; the first half of the points
sits beside as the quadrature's check). Chosen allocation, 4, 4, 4 and 10 copies of depths 1 to 4 and 16 readout circuits:

| truth | pooled rule behind the heterogeneity gate | with every leave-one-pair-out refit (first half) |
|---|---|---|
| geometric continuation | 0.985 | 0.962 (0.966) |
| coherent, CZ phase | 0.988 | 0.976 (0.981) |
| coherent, PRX amplitude | 0.988 | 0.979 (0.979) |
| bend, geometric / CZ / PRX | 0.991 / 0.994 / 0.994 | 0.985 / 0.994 / 0.994 |

z after one depth-4 pair is lost is 3.38 (CZ phase) and 4.75 (PRX amplitude). Allocations tried (power with every gate on, at
delta 9.0 from a 1,024-point quadrature, so about 0.007 of quadrature error; circuits include the 16 readout circuits; z is the
smaller of the two coherent continuations after a depth-4 pair is lost):

| copies at depths 1, 2, 3, 4 | circuits | geometric | CZ phase | PRX amplitude | z after a pair is lost |
|---|---|---|---|---|---|
| 14, 4, 4, 24 | 62 | 0.971 | 0.980 | 0.985 | 5.48 |
| 8, 4, 4, 18 | 50 | 0.970 | 0.982 | 0.982 | 4.72 |
| 4, 6, 6, 18 | 50 | 0.968 | 0.979 | 0.982 | 4.72 |
| 4, 4, 4, 24 | 52 | 0.968 | 0.981 | 0.982 | 5.48 |
| 4, 4, 4, 18 | 46 | 0.966 | 0.978 | 0.979 | 4.72 |
| 4, 4, 4, 12 | 40 | 0.967 | 0.980 | 0.978 | 3.76 |
| **4, 4, 4, 10 (chosen)** | **38** | 0.966 | 0.981 | 0.979 | 3.38 |
| 4, 4, 4, 8 | 36 | 0.968 | 0.977 | 0.977 | 2.93 (fails) |
| 4, 4, 4, 6 | 34 | 0.966 | 0.975 | 0.976 | 2.40 (fails) |
| 4, 4, 4, 4 | 32 | 0.966 | 0.979 | 0.977 | 1.70 (fails) |

The power does not depend on the copy counts in this range: the circuit-level families separate at depth 3 (a dip the
retained bend already shows), where 67,200 kept shots resolve the families, so the z criterion at depth 4 binds. Every
depth needs two mirror pairs for the influence check, which fixes depths 1 to 3 at 4 copies, and depth 4 at 10 copies is
the smallest count whose z after a pair is lost reaches 3 (8 copies reach 2.93). The 38 circuits and the shots are those of the
case before the owner's decision, so expected seconds, credits and max_credits are unchanged.

## Falsifier

The bend repeats (z <= -3) at mirrored positions and "coherent" wins: a coherent error of the gates that accumulates with
iterations is supported (a CZ conditional-phase or PRX amplitude error of the size the better coherent fit names); the
positional-drift cause is excluded at linear order. No bend (|z| < 3): the retained bend came from drift of higher order than
the mirroring cancels, or from chance, and the coherent reading is unsupported. "Geometric" with the bend present: an
incoherent depth-dependent loss the model omits. "Unresolved": neither a loss beyond the model nor a coherent error is
resolved at these shots. "Not evaluated" (a failed heterogeneity or readout gate): the mirror pairs of a depth, or the two
sides of the readout block, differ by more than binomial scatter, a copy-specific or non-linear positional effect that the
mirroring does not cancel; neither decision is read, and the run shows the drift instead of deciding the question. "Not
evaluated: the reading depends on one mirror pair": the decision changes when one mirror pair leaves, so a single pair, not
the retention law, carries it. "Out of domain": a rate or error outside the stated box, reported as such. "Neither family
fits": another mechanism (for example a ZZ phase, leakage or an error that differs between depths) remains, and the three
families are refuted as the sole cause.

## Cost

Expected seconds 11.02 (38 circuits x 20,000 shots x 14.5 us; the retained job measured 13.9 us per heralded circuit-shot,
1.99852 s over 144,000, and the depth-4 circuits add about 14 CZ at 40 ns; the refit of
[billing v3](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/iqm-billing-v3/docs/evidence/iqm-garnet-billing-v3/billing_v3.json),
PR 980, gives 0.1347 s + 7.62e-6 s per circuit-shot = 5.9 s plus the compiler's schedule estimate, which a free
`garnet:mock` compile reads and which was not read). Billed ceiling credits = ceil(1.6 + 11.02) x 0.50 = 6.5. max_credits 8
(16 billed seconds; `cancel_threshold_seconds` 15.0 s, 3.98 s above the expected run). Expected spend about 6 credits. The
case rule of `scripts/iqm_jobs.py` cancels a job that reaches the threshold, and IQM can bill a failed or cancelled job, so
the ceiling bounds the spend and is not a guarantee of zero cost on a cancellation. `cases.json` binds the regenerated
prediction and has sha256 `8cffbeb5c8fac7ee361551dc892678c0915ec75fc862862074103a7aa855fc3b` on calibration set `a0e725eb` (a live rebuild may change it, and the approvals
name the digest after that rebuild).

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

- Three hypotheses are fitted: a geometric loss, a CZ conditional-phase error and a PRX amplitude error, each with a free
  prefactor and rate. A coherent error of another kind (ZZ crosstalk, leakage, an error that differs between depths or gates)
  reads "neither family fits" or the better-fitting of the three by accident; the case rejects only these three.
- A hypothesis fitted to three retained points has no degree of freedom left, so its continuation to depth 4 carries the full
  retained uncertainty ("Retained uncertainty"); the probabilities of the case are taken over that uncertainty for these
  three families only.
- The ledger binding of the case's float records to the runner image (`ci/runner_image_records.json`) is not done; it needs
  a podman host's receipts.
- Mirroring cancels drift linear in position; drift that is not linear stays, balanced to the order of the squared-offset
  spread.
- The pair gate detects only displacements above its power curve; smaller ones enter the pooled depths.
- Depths 1 to 3 hold two mirror pairs each, so one failed copy there reads the family and the bend as "not evaluated".
- The threshold's misclassification probabilities are computed at four truths on a Gaussian approximation of the four
  frequencies; other parameter triples and the tails beyond the normal limit are not covered, and the quadrature's own error
  is about 0.001.
- The readout correction is first-order linear in the marked row and takes the model's depth distributions q as exact.

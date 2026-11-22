# IQM Garnet fourth Grover depth at mirrored positions

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made in
the repair that added the analyzer, the mirror-pair and heterogeneity gates and the rate domains.

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
- Kept shots at 0.84 of requested (retained 0.841 to 0.846): 67,200 at depths 1 to 3 and 302,400 at depth 4. The binomial
  standard error of rho_4 is 0.00695, so the continuations separate by 3.27 standard errors; they resolve at 3 down to a
  kept fraction of 0.71 at depth 4 (z scales with the root of the kept shots: 0.84 x (3 / 3.27)^2).
- Pairs leave the pooled depths together (see "Gates"): with one of the nine depth-4 mirror pairs gone the separation z falls
  from 3.27 to 3.08, with two to 2.88 and with three to 2.67; one pair gone from each of depths 1 to 3 (two of their copies
  each) raises the bend's standard error from 0.0094 to 0.0132, still 10 standard errors from the retained deviation of
  0.133. The family comparison below does not use the retained continuations.
- Over four depths, if the data equal the coherent values the geometric fit leaves chi2 = 183.2, and if they equal the
  geometric values the coherent fit leaves chi2 = 24.9; both exceed the preregistered difference of 9.
- The bend uses three independent arms: its standard error at the planned shots is 0.0094 against the retained
  f of -0.122 against the model's +0.010 (a deviation of 0.133, about 14 standard errors if the bend repeats).
- Limit of the arithmetic: the continuations come from fits of three retained points whose own uncertainty is not
  propagated, so the z of 3.27 is a sizing number. The decisions below compare the new run's four depths with the model, a
  within-job contrast that needs no retained covariance.

## Preregistered decision rule

Fixed in `results/iqm/cases/grover-fourth-depth-mirrored/prediction.json` (`decisions.rule`, `decisions.heterogeneity`, bound by
`cases.json.prediction_sha256`) and implemented by `grover_depth_families.read_copies` and `verdict`:

- Pooled marked counts per depth over the surviving mirror pairs; lambda_k = (p - 1/8) / (P_k - 1/8) from raw frequencies; binomial
  standard errors at the observed frequencies.
- bend: z = (f - model f) / SE over depths 1 to 3; z <= -3 reads "bends beyond the model at mirrored positions" (drift
  linear in position is excluded as the cause); z >= 3 "bends upward of the model"; otherwise "no bend resolved".
- family: chi2 of each family's fit to rho_1..rho_4 (two degrees of freedom) over the rate domains of "Gates"; "out of domain"
  when a fit sits on its rate bound; else "neither family fits" when both exceed 9.21;
  "coherent" when chi2_geometric - chi2_coherent >= 9; "geometric" when <= -9; otherwise "unresolved". The two fits read
  one data set, so the difference is taken on those data and no cross-job quantity enters the decision.
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

Copy heterogeneity. The chi-square of the surviving copies of every depth about that depth's pooled marked frequency,
sum (m - n p)^2 / (n p (1 - p)) with copies - 1 degrees of freedom per depth, is summed over the depths (26 degrees of
freedom with all 38 circuits kept) and compared with the 0.99 chi-square quantile of its degrees of freedom (45.64 at 26),
which `prediction.json` holds for every degree of freedom (`decisions.heterogeneity.threshold_by_dof`). Above it the bend and
the family decisions both read "not evaluated": a depth's pooled frequency no longer describes copies that differ beyond
binomial scatter. The reviewer's two counterexamples (one depth-1 copy 0.04 above its siblings, which read "geometric" at
delta chi2 -18.5 under the earlier pooling; a dropped depth-1 copy with a slope of -0.005 per position, which read a bend
at z -3.68) now read "not evaluated" (tests `test_a_copy_raised_by_four_points_reads_not_evaluated_on_raw_counts` and
`test_a_dropped_copy_and_a_linear_slope_read_not_evaluated_or_the_centered_verdict`, which also plants a slope of -0.00003
per position and reads the centered verdict "no bend resolved").

Power cost of the gate (`decisions.heterogeneity.power`):

- Under the model the gate returns "not evaluated" with probability 0.01, the whole run's loss of its two decisions.
- A drift of the retention linear in position trips it with probability 0.5 at 0.00054 per position and 0.9 at 0.00073 per
  position (noncentral chi-square at the planned shots; the drift moves each depth's marked frequency by its retention
  scale P_k - 1/8). The retained run's depth-1 copies gave a raw marked-frequency slope of -0.000303 +- 0.000317 per
  position, which is -0.00046 per position in retention: the gate fires with probability 0.30 at that point estimate and
  0.04 at half of it. A drift of that size is the kind the mirroring cancels in the pooled frequencies, so the gate
  withholds a decision that the design could have made. Retained copies, where positions 0 to 35 carry the four copies of
  each depth-1 arm, read 13.3 on 16 degrees of freedom over all the retained copy-bearing arms (p 0.65).

Domains. The geometric family's rate s is searched over [0.30, 1.20] and the coherent family's over [0.50, 1.10] (its offset
eps over a full period, the geometric amplitude without bound). A fit whose rate sits on a bound reads "out of domain: the
... fit ends on its rate bound" and decides nothing, because the bound, not the data, ended its search and the other
chi-square comparison would then favor the other family. The retained fits (s 0.963 and 1.013) lie inside by at least 0.24 and 0.09;
planted data at s 1.25 (geometric) and 1.11 (coherent), and at 0.28 and 0.48, read "out of domain" where the hidden box had
read "neither family fits"; data at 1.19 and 1.09 read their family and data at 0.52 stay in domain.

Analyzer. `"$PYTHON" scripts/iqm_grover_fourth_depth.py analyze RUN_DIR --out OUT.json` reads one collected run through
`garnet_followup_analysis.read_job` (record checks, case and prediction digests, calibration set, measurement order, one run
of job `grover` on `garnet`; a `garnet:mock` run is refused), binds each circuit's file digest, depth (14 CZ per iteration),
position and mirror image to its counts, and applies the gates and the rule above (`gororoba_quantum/grover_depth_analysis.py`,
`grover_depth_families.read_copies`). It is tested on planted raw records (the model device; the two counterexamples; mock,
foreign-prediction and wrong-calibration runs; a mislabeled position, depth and circuit).

## Falsifier

The bend repeats (z <= -3) at mirrored positions and "coherent" wins: a coherent error that accumulates with iterations is
supported within this family (an oracle phase error); the positional-drift cause is excluded at linear order. No bend
(|z| < 3): the retained bend came from drift of higher order than the mirroring cancels, or from chance, and the coherent
reading is unsupported. "Geometric" wins with the bend present: an incoherent depth-dependent loss the model omits.
"Not evaluated" (a failed heterogeneity gate): the copies of a depth differ by more than binomial scatter, a copy-specific or
non-linear positional effect that the mirroring does not cancel; neither decision is read, and the run shows the drift instead
of deciding the question. "Out of domain": a rate outside the stated box, reported as such. "Neither family fits": another mechanism (for example a ZZ phase or leakage) remains, and the oracle-phase family is refuted
as the sole cause.

## Cost

Expected seconds 11.02 (38 circuits x 20,000 shots x 14.5 us; the retained job measured 13.9 us per heralded circuit-shot,
1.99852 s over 144,000, and the depth-4 circuits add about 14 CZ at 40 ns; the refit of
[billing v3](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/blob/iqm-billing-v3/docs/evidence/iqm-garnet-billing-v3/billing_v3.json),
PR 980, gives 0.1347 s + 7.62e-6 s per circuit-shot = 5.9 s plus the compiler's schedule estimate, which a free
`garnet:mock` compile reads and which was not read). Billed ceiling credits = ceil(1.6 + 11.02) x 0.50 = 6.5. max_credits 8.0
(16 billed seconds; `cancel_threshold_seconds` 15.0 s, 3.7 s above the expected run). Expected spend about 6 credits. The
case rule of `scripts/iqm_jobs.py` cancels a job that reaches the threshold, and IQM can bill a failed or cancelled job, so
the ceiling bounds the spend and is not a guarantee of zero cost on a cancellation. The repair of the analyzer and the gates
leaves the circuits, shots, expected seconds and credits as they were; `cases.json` binds the regenerated prediction and has
sha256 `0f49c5762bd388439816e98f27da2f89f5fe2ce710f20f99ff1b61bf7ef56e30` on calibration set `a0e725eb` (a live rebuild may change
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
- The heterogeneity gate also fires on a drift linear in position of the size the retained run's point estimate shows
  (probability 0.30), which the mirroring would have cancelled; the alternative statistic on mirror-pair sums would not
  fire on it, and the choice between the two is the owner's (the brief names the per-copy statistic).
- The coherent fit's rate bound at 0.50 makes strongly lossy data (geometric s below about 0.8) read "out of domain" rather
  than "geometric", since the coherent fit is cut off by its bound.

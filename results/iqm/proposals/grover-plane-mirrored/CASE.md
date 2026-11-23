# IQM Garnet depth dependence of the Grover retention as a mechanism-free departure, with a mark contrast

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
This run is a prospective replication or refutation of the retained depth-3 anomaly of mark 101 (eps 0.041 +- 0.011 under the
plane family, one marked-probability point). It does not identify a CZ, ZZ, PRX or leakage mechanism, and it is no algorithmic
novelty: the plane reduction of noisy Grover search with leakage and dephasing and the bounds on a rotation-angle error are prior
work (Khan and Faryad, arXiv 2611.16398, 12 November 2026), and the plane model is the analysis frame here.
A variant without the mark 011 arms is the case [grover-plane-mirrored-101](../grover-plane-mirrored-101/CASE.md); the owner
chooses between them at the spend question (see "Variants").
It succeeds the case `grover-fourth-depth-mirrored` of 913f73b20 (PR 987), whose bytes stay reproducible; its decision rule,
response tables, estimator, calibration, circuits and cost are replaced for the reasons in the plane-model note
([design](../../../../docs/design/iqm-garnet-grover-plane-model.md), "Falsification log").

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (copy in the case's `calibration/`). One job of 52
circuits at 16,000 shots (832,000 executions; the limits are 100 circuits and 2,000,000 executions), built by
`scripts/iqm_grover_plane_case.py`; the `cases.json` sha256 is in `docs/evidence/iqm-garnet-grover-plane/variant_sizing.json`
(a live rebuild changes it, and an approval names the digest after that rebuild).

## Question

1. With the line-native Grover of mark 101 at depths 1 to 4, at positions mirrored about the job's center, does the marked
   probability depart from the geometric law of the calibrated model toward a rotation of the Grover plane per iteration,
   whatever gate error causes it? The primary decision names no gate: a CZ phase, a PRX amplitude and a ZZ coupling each rotate
   the plane to first order, and the response of each, computed in the calibrated noisy path, is fitted by the one family
   P_k = 1/8 + a (Q_k(s, eps) - 1/8).
The approval question asks question 1 alone. The 14 mark 011 circuits buy a reading beside it, which the spend approval
does not rest on: does mark 011 (depths 1 to 3) rotate as a CZ phase (eps_011 = 0) or as a PRX amplitude (eps_011 = 1.194651206
eps_101, the ratio of the case's fitted slopes) predicts?
   This contrast is the test of a pattern read post hoc from the retained depth run (z -0.93 against CZ, -3.14 against PRX
   from the exact fits); it decides nothing and a ZZ coupling reads like a CZ phase. Its power below omits the pair and readout
   gates (see the contrast bullet below); simulating them inside the contrast power would cost about 15 minutes of compute and is not done.

## Why a simulation cannot answer it

`iqm_sim` carries depolarizing gates, idle decay and readout; no coherent error. The question is whether Garnet's own
coherent error and drift reproduce the retained bend, which only the chip shows.

## Circuits, order and estimator

Mark 101 depths 1 to 4 in 4, 4, 10, 4 copies; mark 011 depths 1 to 3 in 4, 4, 6 copies; the eight readout preparations in two
copies each. Both marks use the same preparations through their own marked row and model depth distributions. The first half
of the order (`FIRST_HALF`, the local optimum of single exchanges under the placement rules, rerun by a test) is repeated
reversed. A kind of two pairs sits at least 11 positions from its mirror image, so no pair is back to back at the center;
the last first-half position holds a readout and no depth sits at adjacent positions. Each pair enters as the mean of its
two copy frequencies with equal side weights and propagated binomial variances (a linear drift cancels whatever the kept shots
of each side); the readout preparations pair the same way. Mean squared offsets from the center: depth kinds 198.3 to 208.9
(spread 10.7), readout preparations 278.3, so a quadratic drift is balanced among the depths and not between the depths and
the readouts.

## Preregistered rule

(`prediction.json`, `decisions`; `grover_plane_decision.read_pairs` per mark, `decision.contrast`.)

- Response. The depth frequencies are corrected to the model's readout by the eight preparations and fitted by
  Response(circuits, calibration), rebuilt at analysis from the run's own circuit files and calibration copy; the analysis refuses
  a run whose response digest (`decisions.response.sha256`, `decisions.mark_011.response.sha256`) or model probabilities differ.
- Departure of mark 101. T = chi2(a, s) - chi2(a, s, eps): "coherent" when T >= delta = 7.5 and the rotation fit is adequate
  (chi2(a, s, eps) under the 0.99 quantile on 1 dof); "non-geometric, not a rotation" when T >= delta and it is not; "geometric"
  only when T < delta and |eps| + 1.645 SE(eps) <= 0.01 rad per iteration; "unresolved" otherwise; "out of domain" when the
  selected fit sits on a bound of the fitting box, which is the calibrated box (a in [0.80, 1.20], s in [0.75, 1.15]).
- Loss and offset. A per-iteration loss reads "resolved" only when s - 1 <= -3 SE(s); the offset a is reported with its SE and is
  not a loss (a planted a = 0.97, s = 1 reads "not resolved").
- Mark 011 gets the same fit with three depths (no adequacy test at zero degrees of freedom). Contrast: z_CZ = eps_011 / SE
  and z_PRX = (eps_011 - r eps_101) / sqrt(SE_011^2 + (r SE_101)^2) with r = 1.194651206, the PRX slope ratio at an amplitude
  of 0.2 percent. The ratio is a model quantity that grows with the amplitude (1.1947, 1.1964, 1.2016, 1.2168 at 0.2, 0.8, 1.6
  and 3 percent), so a PRX amplitude counts as rejected only when it is rejected at every ratio of [1.1947, 1.2168]. "CZ-phase-like"
  when |z_CZ| <= 2 and that rejection holds (|z_PRX| >= 3 over the interval), "PRX-like" when |z_CZ| >= 3 and some ratio of the
  interval gives |z_PRX| <= 2, "unresolved" otherwise. The contrast reads only when both marks pass every gate below, the box
  and the adequacy of the rotation; a failed gate of either mark removes its rotation fit from the contrast, which then reads
  "not evaluated".
- Gates, each turning a reading into "not evaluated": a pair with a copy under half its planned kept shots leaves its depth; a depth
  that keeps fewer than two pairs (a sole pair has neither a heterogeneity test nor a leave-one-pair-out refit, so one displaced
  circuit in it could name a verdict); pair-mean heterogeneity (chi-square about the depth mean, 0.99 quantile at its dof, variance
  scaled by the phi of the covariance);
  leave-one-pair-out refits must read the same departure category; readout: a preparation under half its shots, the two
  sides' outcome distributions over all eight outcomes of every preparation (0.99 quantile), a corrected frequency moved by
  more than 0.05.
- Overdispersion. Every pair variance carries phi = 1.54, the 95 percent upper bound of the retained copy-to-copy Pearson
  dispersion (chi-square 19.02 on 22 dof, phi 0.86; the retained copies are depth 1 only). z and power are conditional on that
  bound; the heterogeneity gate uses the same phi, so a copy dispersion that the covariance allows does not fire it.

## Calibration and power

Every rate below is an estimate at the cells and truths listed, from unscrambled Sobol' points of the normal quantile (no seed).
delta is chosen on the selection points (Sobol' indices 1 to 2^n); the false-alarm rates are read on validation points that share
no point with them (indices 2^n + 1 to 2^(n + 1) - 1, the half of the same draw that the selection leaves out), so a rate is not
the tail fraction that delta was fitted to. Each interval is the exact (Clopper-Pearson) 95 percent binomial interval of the
counts, which treats quasi-Monte-Carlo points as independent draws and is therefore approximate. The intervals exclude the
dependence between the points, the cells between the evaluated cells (the maximum is a maximum over evaluated cells, biased upward
by taking the maximum of noisy rates) and the model itself (the response, phi and the readout covariance as planned). No claim
covers the continuous box.

- Null cells: 41 (32 Sobol' cells of the fitting box and nine of the offset line s = 1), the four corners of the box
  (a 0.80 or 1.20, s 0.75 or 1.15) and 54 cells of a search of the box boundary (24 equal steps of the perimeter, then five
  bisections around the three highest false-alarm rates), 99 in all, each with 4,096 selection points (1,024 on the boundary search) and 4,095 validation points (the first 1,024 on the boundary
  search).
- delta = 8.0. The worst cell is a boundary cell (a 1.20, s 0.75) with 0.99 quantile 7.76; the 41 null cells alone gave 7.5 and the
  boundary search raised it. The chi-square(1) quantile is 6.63 and its tail at 8.0 is 0.0047.
- False "coherent", validated on the held-out points: 8 of 1,024 (0.0078, interval 0.0034 to 0.0153) at the boundary cell of the
  largest selection rate (a 1.20, s 0.75), which is also the largest validation rate over the 99 cells; 0.0039 to 0.0061 at the four
  corners (4,095 points each, upper interval ends up to 0.0090); at most 0.0056 on the offset line (23 of 4,095, interval 0.0036 to
  0.0084). The mean over the cells is 0.0054. The in-sample tail fractions that chose delta read 0.0078 at most.
- False "non-geometric, not a rotation", validated: 0 of 4,095 at the cell of the largest selection rate (interval 0 to 0.0009); at
  most 1 of 4,095 in any cell (0.00024, interval 0.000006 to 0.0014), 7e-6 on average.
- Power through the departure rule at delta (the pooled rule), mark 101, 2,048 points per truth, exact 95 percent intervals of
  half-width at most 0.022 (at a rate near one half; 0.955 to 0.972 for the lowest resolved truth):

| Truth | Estimated "coherent" rate |
|---|---|
| plane rotation \|eps\| = 0.02, four corners of a and s and 28 cells of a 0.90 to 1.10, s 0.90 to 1.05 | 0.985 to 0.992 |
| plane rotation \|eps\| = 0.03 (corners) | 0.990 to 0.993 |
| plane rotation \|eps\| = 0.015 (corners) | 0.874 to 0.992 |
| plane rotation \|eps\| = 0.01 (corners) | 0.435 to 0.938 |
| CZ phase -0.015 and +0.015 rad (corners) | 0.980 to 0.992 |
| PRX amplitude -0.8 and +0.8 percent (corners; the lowest is +0.8 percent at a 0.92, s 0.92) | 0.964 to 0.989 |
| ZZ coupling -10 and +10 kHz (corners) | 0.982 to 0.991 |

  The case claims no resolution below |eps| = 0.015.
- Power through the pair gates (the two-pair floor, heterogeneity, leave-one-pair-out; 256 points, standard error up to 0.03),
  at mechanism corners and the plane rotation 0.02 at a 0.92, s 0.92. Heterogeneity gate at phi = 1.54 (the gate of the rule) or
  phi = 1 (binomial), pair frequencies of binomial dispersion (noise phi 1) or of the bound 1.54:

| Gate phi, noise phi | "coherent" | reads "not evaluated" |
|---|---|---|
| 1.54, 1 | 0.949 to 1.000 | up to 0.047 |
| 1.54, 1.54 | 0.805 to 0.953 | 0.047 to 0.188 |
| 1, 1 | 0.938 to 0.988 | up to 0.055 |
| 1, 1.54 | 0.770 to 0.895 | 0.105 to 0.223 |

  The gate at the dispersion of the covariance (1.54) raises power at overdispersed copies (0.805 against 0.770 at worst) and costs
  little at binomial copies.
- Readout gates, by pass rate when the device follows the model at the planned shots: the shift tolerance 0.05 passes with
  probability 1.0 (the planned shift has standard deviation of about 0.003); the two-sides chi-square (0.99 quantile on 56
  dof) passes with 0.9995 at phi 0.86 (the retained estimate), 0.99 at phi 1 and 0.458 at the dispersion bound 1.54, where the
  analysis then reads "not evaluated". The copy floor (a preparation keeping under half its planned shots) is not modeled; it
  needs a herald loss rate the retained jobs bound only from above. The powers above are conditional on these gates passing.
- Contrast, through the departure rule of each mark at delta (box and adequacy gates, the adequacy tested at every T so that a fit failing it reads "not evaluated"; not the pair or readout gates;
  the approval does not rest on this reading), binomial
  copies: a CZ phase of -0.03 rad reads "CZ-phase-like" 0.942 to 0.951; a PRX amplitude of -1.6 percent reads "PRX-like" 0.925 to
  0.939; a ZZ coupling of +20 kHz reads "CZ-phase-like" 0.734 to 0.864 (its mark 011 slope is a tenth of its mark 101 slope), so the
  contrast does not separate ZZ from a CZ phase; "not evaluated" 0.007 to 0.015.
- Power at |eps| = 0.01 is 0.435 at worst, beside 0.985 at 0.02. The leak L = s - mu (weight contraction against Bloch
  contraction) is not identifiable from the marked probabilities: the weight that leaves the plane returns through the complement
  functional, which the four depths fix only together with eps (the eight-cell refit of the design note frees the complement and
  eps loses its identification: 0.027 +- 0.011 uniform, 0.007 +- 0.138 with every cell free).

Outside the claimed region the false-alarm rate is estimated at the cells above and power is not claimed. The plane family reproduces
the exact noisy response of a coherent error to at most 1.5e-3 in P.

## Cost

Billing v4 sizing (`docs/evidence/iqm-billing-v4`, coefficients pinned in `billing_v4_inputs.json`): the three Garnet models
v3, v4_sum and v4_max price this job at 11.7 to 12.8 s of execution (schedule 6.33 s plus the model's excess), expected billed
7.0 to 7.5 credits. The band adds the model's largest leave-one-out residual and the schedule error of all retained jobs
(3.0 s); the worst case adds 0.44 s of runtime over execution; `max_credits` buys 1.5 times it: 13.0 (v3), 12.5, 12.0, of which
the case takes 13.0 (26 billed seconds, cancel threshold 25 s). Under the Grover-jobs schedule error the credits are 11.0, 10.5
and 10.0. Margin of the 25 s threshold over the longest expected runtime (13.24 s): 5.1 s at a runtime overrun of 1.5 times, and
-4.1 s at 2.2 times (the sibling Emerald run's overrun), which the ceiling does not cover: such a run would be cancelled and billed.
The `garnet:mock` compile estimate (`execution_runtime_estimate_seconds`) is required before approval and not read here.
DECISION NEEDED (owner): read the mock estimate and either keep 13.0 credits or raise it.

## Variants

| | this case (A) | [mark 101 only](../grover-plane-mirrored-101/CASE.md) (B) |
|---|---|---|
| circuits, executions | 52, 832,000 | 38, 608,000 |
| expected execution, v3 / v4_sum / v4_max (s) | 12.81 / 11.67 / 12.21 | 9.30 / 8.47 / 8.88 |
| expected billed credits (v3, v4) | 7.5, 7.0 | 5.5, 5.5 |
| max_credits (all-jobs band), cancel threshold | 13.0, 25 s | 9.5, 18 s |
| max_credits (Grover-jobs band) | 11.0 | 8.5 |
| primary test, worst resolved truth (PRX +0.8 percent, a 0.92, s 0.92) | 0.964 (0.955 to 0.972) | 0.964 (0.955 to 0.972) |
| margin at 1.5 times / 2.2 times the expected runtime | 5.1 s / -4.1 s | 3.4 s / -3.4 s |
| mark contrast reading (outside the approval question) | yes | none |

The primary test is the same in both: the mark 101 arms, their copies and the covariance do not change, so the power does not.
B drops the contrast, the 14 mark 011 circuits and about a quarter of the credits; its `max_credits` is 9.5 where the earlier
headroom formula gave 9.0. The digests are in `variant_sizing.json`.

## Steps before a submission

As the case of PR 987: `build --live` (free read of the current calibration set), owner approval of the digest for the mock,
mock run and collect, owner approval of the identical digest for Garnet, `submit`, `collect`, `analyze`. Not run. `analyze` has
run on synthetic collected records of this case (a model device, a planted CZ phase, a planted PRX amplitude, a refused mock run).

## Falsifier

"coherent" with eps of either sign: a rotation of the plane per iteration, whatever its source; the contrast is a lead for
a later case. "non-geometric, not a rotation": a depth dependence a rotation does not describe. "geometric": the coherent term is
bounded by 0.01 rad per iteration at the data's SE. "unresolved": no conclusion on a term up to 0.01. "Not evaluated": a gate failed;
the run shows the drift instead of deciding.

## Residual risk

- The plane family is a first-order reduction; it fits exact noisy responses to 1.5e-3 in P up to eps 0.1 and is untested for
  coherent leakage (qutrit), tilt of order eps, or a non-uniform complement (the retained unmarked counts reject uniform).
- The retained evidence for a rotation is one depth-3 point of mark 101 (eps 0.041 +- 0.011); the 011 arms show none, and the
  PRX rejection is 3.0 to 3.1 sigma, post hoc.
- Mirroring cancels linear drift only; quadratic drift enters at the squared-offset spread above.
- phi = 1.54 is a depth-1 bound applied to every depth; ZZ is not separated from a CZ phase by the contrast; at that bound the readout
  sides gate fails 54 percent of runs, so a run at the bound reads "not evaluated" more often than power suggests.
- The PRX ratio comes from the calibrated model and moves with the calibration set; the interval covers the amplitude only.
- The uniform complement is contradicted by the unmarked counts and no tested nonuniform fixed point fits them (design note, "Eight-cell
  refit"); the depth-3 rotation is identified under the uniform and per-qubit forms and not under the shell and free forms.
- Power at |eps| 0.01 is 0.435 at worst; the case claims no resolution there.
- The ledger binding of the case's float records to the runner image is not done.
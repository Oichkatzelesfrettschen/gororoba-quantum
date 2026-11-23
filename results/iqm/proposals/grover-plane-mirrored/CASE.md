# IQM Garnet depth dependence of the Grover retention as a mechanism-free departure

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
It succeeds the case `grover-fourth-depth-mirrored` of 913f73b20 (PR 987), whose bytes stay reproducible; its decision rule,
response tables, estimator, calibration and cost are replaced for the reasons in the plane-model note
([design](../../../../docs/design/iqm-garnet-grover-plane-model.md), "Falsification log").

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (copy in the case's `calibration/`). One job of 38
circuits at 16,000 shots, built by `scripts/iqm_grover_plane_case.py`; `cases.json` sha256
`0d7851b733ce60fff68438acfd09448e9f6bc881b0ebb9e90f5651da7871f385` (a live rebuild changes it, and an approval names the digest after
that rebuild).

## Question

With the line-native Grover of mark 101 at depths 1 to 4 at positions mirrored about the job's center, does the marked
probability depart from the geometric law of the calibrated model toward a rotation of the Grover plane per iteration,
whatever gate error causes it? The primary decision names no gate: a CZ phase, a PRX amplitude and a ZZ coupling each
rotate the plane to first order, and the response of each (computed in the calibrated noisy path) is fitted by the one family P_k = 1/8 + a (Q_k(s, eps) - 1/8). A mechanism attribution (eps per unit error: CZ -1.294 per rad, PRX
-2.24 per fraction, ZZ 2.0e-6 per Hz at mark 101) is reported beside and decides nothing.

## Why a simulation cannot answer it

`iqm_sim` carries depolarizing gates, idle decay and readout; no coherent error. The question is whether Garnet's own
coherent error and drift reproduce the retained bend, which only the chip shows.

## Circuits, order and estimator

COPIES 4, 4, 10, 4 of depths 1 to 4 and the eight readout preparations in two copies each. The first half of the order
(`FIRST_HALF`, the local optimum of single exchanges under the placement rules, rerun by a test) is repeated reversed. Depths
of two mirror pairs (1, 2, 4) sit at first-half positions up to 13, so their pairs lie at least 11 positions apart and no pair
is back to back at the center; the position next to the center holds a readout. Each pair enters as the mean of its two copy
frequencies with equal side weights and propagated binomial variances (a linear drift cancels whatever the kept shots of
each side); the readout preparations pair the same way. Mean squared offsets from the center: depths 160.3, 157.3, 159.8, 157.3 (spread 3.0), readout
preparations 67.0, so a quadratic drift is balanced among the depths and not between the depths and the readouts.

## Preregistered rule

(`prediction.json`, `decisions`; `grover_plane_decision.read_pairs`.)

- Response. The four depth frequencies are corrected to the model's readout by the eight preparations and fitted by
  Response(circuits, calibration) rebuilt at analysis from the run's own circuit files and calibration copy; the analysis
  refuses a run whose response digest (`decisions.response.sha256`) or model probabilities differ from `prediction.json`.
- Departure. T = chi2(a, s) - chi2(a, s, eps) over four depths with the full covariance: "coherent" when T >= delta = 6.635;
  "geometric" only when T < delta and |eps| + 1.645 SE(eps) <= 0.01 rad per iteration; otherwise "unresolved" (a coherent term of
  up to 0.01 rad is not excluded). An unresolved coherent term is never read as geometric.
- Loss and offset. A per-iteration loss reads "resolved" only when s - 1 <= -3 SE(s) in the fit the departure selects; the
  depth-independent offset a is reported with its SE and is not a loss (a planted a = 0.97, s = 1 reads "not resolved").
- Gates, each turning the reading into "not evaluated": a pair with a copy under half its planned kept shots leaves its depth
  with its partner; a depth without a pair; pair-mean heterogeneity (chi-square about the depth mean, 0.99 quantile at its
  dof, binomial variance); leave-one-pair-out refits must read the same departure category; readout: a preparation under
  half its shots, the two sides' outcome distributions over all eight outcomes of every preparation (chi-square at the 0.99
  quantile), a corrected frequency moved by more than 0.05.
- Overdispersion. Every pair variance carries phi = 1.54, the 95 percent upper bound of the retained copy-to-copy Pearson
  dispersion (chi-square 19.02 on 22 dof from the retained copies of one circuit, phi 0.86; depths 2 to 4 have no retained
  copies, so the bound is a depth-1 bound). z and power are conditional on that bound; the heterogeneity gate uses phi = 1.

## Calibration and power (whole box, not four points)

Quadrature, no seed: unscrambled Sobol' points of the normal quantile (1,024 per cell). Null box: 39 cells of a in [0.90, 1.10],
s in [0.85, 1.10] and the offset line s = 1. delta = 6.635; worst null cell (a 1.0875, s 0.866) has its own 0.99 quantile 6.47;
false "coherent" at most 0.0098 (0.0088 on the offset line); "geometric" read in at least 0.59 of every null cell.
Power (512 points per truth) at |eps_eff| = 0.02 over CZ -0.015 and +0.015 rad, PRX -0.8 and +0.8 percent and ZZ -10 and +10 kHz at
four corners of (a, s) in {0.92, 1.06} x {0.92, 1.04}, and the plane rotation at 32 Sobol' cells: at least 0.986 (worst cell PRX +0.8
percent, a 0.92, s 0.92). At |eps| 0.015: at least 0.92; at 0.01: at least 0.53 (the case does not claim resolution there). Through
the gated rule (256 points): 0.961 to 0.988 with binomial copies, 0.871 to 0.926 at the dispersion bound (the remainder "not
evaluated"). The rule's fit box (a 0.5 to 1.5, s 0.3 to 1.2) is wider than the calibrated truth box above; outside the calibrated box
the false-alarm rate and power are not established. The plane family reproduces the exact noisy response of a coherent error to at most 1.5e-3 in P; its error
at the planned standard error of depth 3 (0.0017) is the limit of the "mechanism-free" claim.

## Cost

Execution from the retained job (1.9985 s, 144,000 circuit-shots) scaled by the ratio of ASAP schedule totals (16 ns PRX, 40 ns CZ,
480 ns measurement) 5.40: 10.79 s (10.22 s with the retained 0.13 s fixed part removed); compilation 0.44 s. Billed expectation
ceil(1.6 + 10.79) = 13 s, 6.5 credits. `max_credits` 9.0 (18 billed seconds, cancel threshold 17 s) holds 1.5 times the estimate with
compilation. A run at the sibling Emerald's 2.2 times (23.7 s) would be cancelled and could be billed. The `garnet:mock` compile
estimate (`execution_runtime_estimate_seconds`) is required before approval and not read here; the retained-rate premise is the one
the red teams of PR 987 refuted for its own sizing, and this ratio method has the same uncertainty. DECISION NEEDED (owner): read
the mock estimate and either keep 9.0 credits or raise it.

## Steps before a submission

As the case of PR 987: `build --live` (free read of the current calibration set), owner approval of the digest for the mock,
mock run and collect, owner approval of the identical digest for Garnet, `submit`, `collect`, `analyze`. Not run.

## Falsifier

"coherent" with eps of either sign: a rotation of the plane per iteration, whatever its source; the mechanism reading
(eps against CZ, PRX, ZZ slopes) is a lead for a later case. "geometric": the coherent term is bounded by 0.01 rad per
iteration at the data's SE, and the retained bend came from drift of higher order than mirroring cancels, or chance.
"unresolved": no conclusion on a term up to 0.01. "Not evaluated": a gate failed; the run shows the drift instead of deciding.

## Residual risk

- DECISION NEEDED: "coherent" follows T >= delta; `rotation_adequate` gates nothing, so an incoherent non-geometric loss would read
  "coherent". Folding adequacy in changes the digest. The owner also decides on the mock estimate, mark 011 arms, and an
  end-to-end `analyze` run, which has not been executed on any record (the decision layer is tested on planted counts).
- The plane family is a first-order reduction; it fits exact noisy responses to 1.5e-3 in P up to eps 0.1 and is untested for
  coherent leakage (qutrit), tilt of order eps, or a non-uniform complement.
- The retained evidence for a rotation is one depth-3 point of mark 101 (eps 0.041 +- 0.011); the 011 arms show no rotation.
  Mark 011 arms at depths 3 and 4 would add a second contrast (CZ phase: eps_011 = 0; PRX: 1.4 eps_101); not in this case.
- Mirroring cancels linear drift only; quadratic drift enters at the squared-offset spread of the placement.
- phi = 1.54 is a depth-1 bound applied to depths 2 to 4.
- Power at |eps| 0.01 is 0.53 at worst.
- The ledger binding of the case's float records to the runner image is not done.

# IQM Garnet depth dependence of the Grover retention as a mechanism-free departure, with a mark contrast

Status: written case awaiting the owner's approval; nothing submitted, the `garnet:mock` twin included, and no IQM call made.
It succeeds the case `grover-fourth-depth-mirrored` of 913f73b20 (PR 987), whose bytes stay reproducible; its decision rule,
response tables, estimator, calibration, circuits and cost are replaced for the reasons in the plane-model note
([design](../../../../docs/design/iqm-garnet-grover-plane-model.md), "Falsification log").

Backend `iqm:garnet`, calibration set `a0e725eb-a020-43d3-8aaf-072b926e425a` (copy in the case's `calibration/`). One job of 52
circuits at 16,000 shots (832,000 executions; the limits are 100 circuits and 2,000,000 executions), built by
`scripts/iqm_grover_plane_case.py`; `cases.json` sha256 is recorded in the review report (a live rebuild changes it, and an
approval names the digest after that rebuild).

## Question

1. With the line-native Grover of mark 101 at depths 1 to 4, at positions mirrored about the job's center, does the marked
   probability depart from the geometric law of the calibrated model toward a rotation of the Grover plane per iteration,
   whatever gate error causes it? The primary decision names no gate: a CZ phase, a PRX amplitude and a ZZ coupling each rotate
   the plane to first order, and the response of each, computed in the calibrated noisy path, is fitted by the one family
   P_k = 1/8 + a (Q_k(s, eps) - 1/8).
2. Does mark 011 (depths 1 to 3) rotate as a CZ phase (eps_011 = 0) or as a PRX amplitude (eps_011 = 1.19 eps_101) predicts?
   This contrast is the test of a pattern read post hoc from the retained depth run (z -0.93 against CZ, -3.14 against PRX
   from the exact fits); it decides nothing and a ZZ coupling reads like a CZ phase.

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
  and z_PRX = (eps_011 - 1.19 eps_101) / sqrt(SE_011^2 + (1.19 SE_101)^2); "CZ-phase-like" when |z_CZ| <= 2 and |z_PRX| >= 3,
  "PRX-like" in the converse, "unresolved" otherwise.
- Gates, each turning a reading into "not evaluated": a pair with a copy under half its planned kept shots leaves its depth; a depth
  without a pair; pair-mean heterogeneity (chi-square about the depth mean, 0.99 quantile at its dof, binomial variance);
  leave-one-pair-out refits must read the same departure category; readout: a preparation under half its shots, the two
  sides' outcome distributions over all eight outcomes of every preparation (0.99 quantile), a corrected frequency moved by
  more than 0.05.
- Overdispersion. Every pair variance carries phi = 1.54, the 95 percent upper bound of the retained copy-to-copy Pearson
  dispersion (chi-square 19.02 on 22 dof, phi 0.86; the retained copies are depth 1 only). z and power are conditional on that
  bound; the heterogeneity gate uses phi = 1.

## Calibration and power

Quadrature, no seed: unscrambled Sobol' points of the normal quantile (1,024 per null cell, 512 per power truth, 256 through
the gates). Null box: 41 cells of the fitting box and the offset line s = 1. delta = 7.5; the worst null cell (a 1.2, s 1) has
its own 0.99 quantile 7.07; false "coherent" at most 0.0088 in every cell and on the offset line.

Power is claimed over a in [0.90, 1.10], s in [0.90, 1.05]:

| Quantity | Value |
|---|---|
| pooled rule, |eps_eff| = 0.02 (CZ, PRX, ZZ at four corners; 32 Sobol' cells of the plane rotation) | at least 0.969 |
| the same at 0.015 and at 0.01 | at least 0.89 and 0.46 |
| through the gates, binomial copies, mechanism corners | 0.949 to 0.988 (0.949: PRX +0.8 percent, |eps_eff| 0.018) |
| through the gates, binomial copies, plane rotation |eps| = 0.02, worst corner | 0.969 to 0.973 |
| through the gates at the dispersion bound phi = 1.54 | 0.79 to 0.90 (the rest reads "not evaluated") |
| contrast: CZ phase -0.03 rad reads "CZ-phase-like" | 0.95 to 0.96 |
| contrast: PRX amplitude -1.6 percent reads "PRX-like" | 0.94 to 0.95 |
| contrast: ZZ +20 kHz reads "CZ-phase-like" | 0.74 to 0.89 |

Outside the claimed region the false-alarm rate is controlled and power is not claimed. The plane family reproduces the exact
noisy response of a coherent error to at most 1.5e-3 in P.

## Cost

Execution from the retained job (1.9985 s, 144,000 circuit-shots) scaled by the ratio of ASAP schedule totals (16 ns PRX, 40 ns
CZ, 480 ns measurement) 7.95: 15.89 s (14.99 s with the retained 0.13 s fixed part removed); compilation 0.44 s. Billed
expectation ceil(1.6 + 15.89) = 18 s, 9.0 credits. `max_credits` 13.0 (26 billed seconds, cancel threshold 25 s) holds 1.5 times
the estimate with compilation (24.5 s). A run at the sibling Emerald's 2.2 times (35.0 s) would be cancelled and could be
billed. The `garnet:mock` compile estimate (`execution_runtime_estimate_seconds`) is required before approval and not read here;
the ratio method rests on one retained job. DECISION NEEDED (owner): read the mock estimate and either keep 13.0 credits or raise it.

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
- phi = 1.54 is a depth-1 bound applied to every depth; ZZ is not separated from a CZ phase by the contrast.
- Power at |eps| 0.01 is 0.46 at worst; the case claims no resolution there.
- The ledger binding of the case's float records to the runner image is not done.

# IQM Garnet plane model of the line-native Grover retention

The line-native Grover iteration on QB20-QB16-QB17 acts on a two-dimensional plane of the eight-dimensional state, and
the marked probability at every depth reads that plane. This note derives the noisy iteration as an affine map of the
plane's Bloch vector, checks it against exact density-matrix simulation of the committed circuits, fits it to every
retained Garnet Grover acquisition, and records where it fails. Its decision form is the case
[grover-plane-mirrored](../../results/iqm/proposals/grover-plane-mirrored/CASE.md). Evidence:
[iqm-garnet-grover-plane](../evidence/iqm-garnet-grover-plane/README.md). Code: `gororoba_quantum/grover_plane_sim.py`
(engine and response), `grover_plane.py` (affine plane family), `grover_plane_decision.py`, `grover_plane_calibration.py`,
`grover_plane_analysis.py`, `scripts/iqm_grover_plane_case.py`, `scripts/iqm_grover_plane_retained.py`.

## Mechanism

Let |m> be the marked basis state and |p> the uniform superposition of the other seven, sin theta = 1/sqrt 8. The ideal
iteration G rotates span(|p>, |m>) by the Hilbert angle 2 theta (the Bloch angle 4 theta about the y axis) and acts as -1
on the six-dimensional complement. A plane block rho_P = (n I + x X + y Y + z Z)/2 in the basis (p, m), z = rho_mm - rho_pp,
has the marked probability (n + z)/2 and the maximally mixed state at n = 1/4, x = y = z = 0. The retention
lambda_k = (P_k - 1/8) / (P_k^ideal - 1/8) is the plane's distance from that point relative to the ideal one.

The native circuit is cut after the 14 j-th CZ (two seven-CZ CCZ networks per iteration). The cut state is R_j |psi_j>,
with R_j = U_native(through cut j) L_j^dagger and L_j the logical unitary of the Hadamards and j iterations. The cut
superoperator S_j (noise included) gives the logical-frame channel Lambda_j = R_j^dagger S_j R_{j-1}, equal to G for the
noiseless circuit. Restricting Lambda_j to the plane and replacing the complement by its uniform state, which carries the
weight 1 - n, gives the affine map

    v' = M v + w (1 - n),    v = (n, x, y, z),

so v_k = v* + A^k (v_0 - v*) with A = M - w e_n^T and v* the fixed point. The reduced parameters of A are the Bloch
contraction s, the rotation error eps = omega - 4 theta, the weight contraction mu = M_nn, the tilt (the y couplings of
the x and z rows) and the leak L = s - mu. The geometric law is eps = 0 with the weight and Bloch contractions equal;
eps != 0 is a coherent rotation. The marked probability reads v_k through the circuit's own tail and readout:
P_k = e_k . v_k + (1 - n_k) h_k.

The scalar closed form lambda_k = a [ (3/4) mu^k - s^k cos(2 theta + k omega) ] / [ 3/4 - cos((4k + 2) theta) ] holds
when M is a rotation block plus a decoupled weight and the fixed point is the maximally mixed state. It misses the exact
model by 6 to 74 percent (a = 1; computed). hypothesis: the cause is the fixed point n* = 0.2249 (computed from the plane map
by n* = w_n / (1 - M_nn + w_n), against 0.25) that the idle relaxation of Garnet's qubits produces, together with the tail
and readout functional (n and z weights 0.485 and 0.483 at depth 4, computed); the scalar form was not repaired. The matrix
form is the derivation that this note checks and uses.

## Checks against exact simulation (known-good before use)

All values from `scripts/iqm_grover_plane_retained.py` (evidence `fits.json`, `engine_checks`).

| Check | Value |
|---|---|
| engine (depolarizing PRX and CZ, ASAP idle T1 and T2, herald-conditioned readout) against the committed `prediction.json` arms | max 4.97e-10 (the file's 9-digit rounding) |
| noiseless Lambda_j against G, depths 1 to 4 | max 4.7e-15 |
| noisy Lambda_2, Lambda_3, Lambda_4 against one another | max 3.7e-13 (Lambda_1 differs from Lambda_2 by 2.6e-3 in the largest entry of M: it carries the preparation) |
| affine plane closure of the model, lambda error at k = 1, 2, 3, 4 | -3.7e-6, -7.3e-5, -6.4e-4, +3.2e-3 |
| Bloch residual of the closure at k = 4 | 5.9e-4 |

The model's plane map on calibration a0e725eb has s = 0.8921, mu = 0.9224, eps_model = -4.97e-4 rad, y-y 0.883, tilt
entries below 7.1e-4 and w_n = 0.0225: the model is a near-pure rotation with weight returning from the complement, so
L = s - mu = -0.030.

Coherent errors, injected into the same noisy path (not the noiseless product a s^k R_k(x)):

| Error | eps per unit error, mark 101 | mark 011 |
|---|---|---|
| CZ conditional phase pi + x | -1.294 per rad | +5e-3 per rad (no rotation) |
| PRX amplitude theta (1 + x) | -2.24 per unit fraction | -2.68 (1.19 times mark 101) |
| rotating-frame ZZ on both couplers | 2.0e-6 per Hz (0.020 per 10 kHz) | 1.7e-7 per Hz |

The family (a, s, eps) fitted to the exact noise-free response of a coherent error reproduces it to max |dP| 6.6e-5 (CZ
0.015 rad), 1.9e-4 (0.03), 9.9e-5 (0.06), 1.5e-3 (0.1) and 6.7e-4 (PRX 0.8 percent), 1.1e-3, 9.9e-4, 1.4e-3 (PRX 1.6, 3,
6 percent). The 4 x 4 affine map built from the coherent channel itself is weaker: for CZ x = -0.03 its R_3 is 0.730
against the exact 0.747, and at x = -0.1 it is 0.13 against 0.29 (the leaked weight returns coherently). The decision
therefore uses the family fitted to exact responses, not the affine closure, and the closure is the explanation of why
a rotation describes a gate error at all.

Limit of validity. The family needs the coherent leak to stay small: it holds to about 1.5e-3 in P up to eps = 0.11 for
a CZ phase and 0.13 for PRX; it is untested for coherent leakage out of the computational subspace (a qutrit
simulation), for a complement that stays non-uniform (the sector invariant under the six cube symmetries fixing the
marked vertex is four-dimensional, and the plane is two of its dimensions), and for tilt of order eps.

## Fits to the retained acquisitions

The data are the readout-corrected marked probabilities (`grover_line_analysis.Readout`, through
`iqm_records.read_run`) against the response of each run's own circuits and calibration copy. Parameters: a (depth-
independent factor on P - 1/8), s (global depolarizing factor per iteration beyond the model), eps (rotation per
iteration, radians).

| Run, mark | depths | geometric (a, s) chi2 | rotation (a, s, eps) | rotation (s, eps), a = 1 |
|---|---|---|---|---|
| line-ccz, 101 | 1, 2 | exact (a 1.009, s 0.9585 +- 0.0148) | not identifiable | eps 0.005 +- 0.012 |
| line-ccz, 011 | 1, 2 | exact (a 0.969, s 0.960 +- 0.020) | not identifiable | eps -0.018 +- 0.019 |
| depth, 101 | 1, 2, 3 | 11.64 on 1 dof (a 1.024, s 0.961) | exact: a 0.924, s 1.034 +- 0.026, eps +0.0410 +- 0.0112 | chi2 5.02 on 1: eps 0.0194 +- 0.0069 |
| depth, 011 | 1, 2, 3 | 0.90 on 1 dof | exact: eps -0.0138 +- 0.0149 | chi2 0.13 on 1: eps -0.0096 +- 0.0091 |

L was not fitted. Marked probabilities alone do not separate the weight contraction mu from the Bloch contraction s, and the
unmarked counts that would constrain it were not used; the fits keep the model's mu/s ratio and report no per-run L.

Joint fits over the four groups (10 points; a per group):

| Parameters beyond a | chi2 | dof | Values |
|---|---|---|---|
| s shared | 12.59 | 5 | s 0.9606 |
| s per mark | 12.57 | 4 | s 0.962 (011), 0.960 (101) |
| s shared, one eps | 9.67 | 4 | eps 0.0152, s 0.983 |
| s shared, eps per mark | 6.71 | 3 | eps 0.0233 +- 0.0098 (101), 0.0067 +- 0.0100 (011) |
| s per mark, eps per mark | 1.47 | 2 | eps 0.0373 +- 0.0111 (101), -0.0129 +- 0.0139 (011); s 1.016 +- 0.020 (101), 0.943 +- 0.024 (011) |

No single parameter set fits all runs: the three families without a rotation per mark leave chi2 above their 0.95
quantiles (11.07, 9.49, 9.49); the two with a rotation per mark fit (p 0.08 and 0.48), and the better one needs an s that
differs by 0.07 between marks.

## Falsification log

1. The parent's formulation (one rotation eps with a calibrated nested test) holds as a reduction and fails as a law of
   the retained data. eps = 0 with a shared s: chi2 12.59 on 5 dof (p 0.028); one shared eps: 9.67 on 4 (p 0.046).
2. The evidence for eps != 0 is one marked-probability point: the depth-3 arm of mark 101 (lambda 0.519 against 0.727).
   eps = 0.041 +- 0.011 (3.7 sigma) rests on three points and three parameters; the 101 and 011 depth runs disagree on
   its sign (0.041 against -0.014 +- 0.015).
3. Mark dependence at depth 1, where the model predicts none (0.7051 against 0.7048): the corrected marked probabilities of
   011 sit below those of 101 by 0.0185 +- 0.0099 (depth run) and 0.0220 +- 0.0097 (line-ccz run), together 0.0202 +- 0.0069
   (z 2.9). A per-mark excess loss, not a shared one, is what the data ask for; the nested rule cannot assign it to a gate.
4. The exact fit has s = 1.034 +- 0.026 and a = 0.924: the incoherent excess loss per iteration is not resolved above
   the model's, and a and s are strongly anticorrelated with eps at three points.
5. Mechanism pattern (post hoc: it was read from the retained data after the three-family case was written, so it is a
   lead and not a test). In the calibrated noisy path a CZ phase leaves the plane of mark 011 unrotated (eps_011 per radian
   +5e-3 against -1.29 for mark 101) and a PRX amplitude rotates it 1.19 times as much as mark 101 (-2.68 against -2.24).
   The retained eps_101 = 0.041 +- 0.011 and eps_011 = -0.014 +- 0.015 read z = -0.93 against a CZ phase and z = -3.14
   against a PRX amplitude (`decision.contrast`, which carries the uncertainty of both fits); the eight-parameter joint fit
   reads -0.92 and -2.99. An earlier draft of this note and the hand-off report gave 4.7 sigma against PRX: that figure used
   a PRX ratio of 1.4 from a noise-free slope and ignored the standard error of eps_101, and it is withdrawn. The retained
   evidence rejects a PRX amplitude at about 3 sigma, consistent with the CZ phase; the `fits.json` record (`mark_contrast`)
   is replayed by a gate.
6. The closure assumes the leaked weight returns as the uniform state of the complement. The retained depth run rejected
   uniform unmarked error (Wald 95.7 on 6 degrees of freedom against the model's uniform prediction, design note of the
   follow-up case), so that assumption is contradicted by the data; the plane family absorbs it into (a, s) and eps and does
   not model it.
7. Coherent error is not seen by calibration benchmarking at this size: a CZ phase of 0.0286 rad costs an average gate
   infidelity of 1.2e-4 per CZ against the calibrated 4.2e-3 (3 percent), and a PRX amplitude error of 1.0 percent on a
   pi/2 rotation costs 4.3e-5 against 2.8e-4 to 5.5e-4. The calibration neither supports nor refutes eps = 0.04.
8. A first version of the case fitted a and s over a box wider than the one calibrated, and a second narrowed the fit box
   to a in [0.90, 1.10], s in [0.85, 1.10]: fits of the corner truths then sat on a bound and the gated power fell to 0.77.
   The case now fits and calibrates over one box, a in [0.80, 1.20], s in [0.75, 1.15], and claims power only around the
   retained fits (a in [0.90, 1.10], s in [0.90, 1.05]).

Verdict: the plane model survives as the derivation, the effective-parameter family and the mechanism-free test statistic;
the three-family contest of PR 987 does not survive as its decision rule, for the reasons recorded in the case
(attribution of ZZ and coherent leakage to a named family, the fallback that calls an unresolved coherent term geometric,
unequal-weight pooling, noiseless response tables, unbounded overdispersion, a four-point calibration and an
unsupported runtime). The case now carries mark 011 arms, whose contrast with mark 101 is the retained pattern's test.

## Priors from the repository's records

- Calibration a0e725eb (`results/iqm/cases/grover-fourth-depth-mirrored/calibration/`): CZ infidelity 4.23e-3 (QB20-QB16)
  and 4.16e-3 (QB16-QB17); PRX infidelity 3.9e-4 (QB20), 2.8e-4 (QB16), 5.5e-4 (QB17); T1 31.5, 47.6, 35.3 microseconds and
  T2 23.8, 8.4, 14.2 microseconds on QB20, QB16, QB17. These are the incoherent inputs of the model.
- Retained readout fault on QB12 and the packed Pauli job one minute earlier
  (`docs/evidence/iqm-garnet-packed-pauli-run/readout_split.json`): QB12 is not on the path, so the fault does not enter these
  circuits; the fault-model evidence of `docs/evidence/iqm-garnet-qb12-models/` and the positions evidence of
  `docs/evidence/iqm-garnet-grover-positions/` live on other branches and were not read.
- Cross-platform: the Tuna-17 interleaved characterization
  (`docs/notes/quantum_inspire/tuna17-interleaved-characterization-2026-11-20.md`) measured a fringe offset of +0.027 +- 0.008 rad
  on q12 and a drive-and-readout context dependence on 15 qubits. The record shows that coherent offsets of a few hundredths
  of a radian occur on a different superconducting device; no translation to a Garnet CZ phase is valid (other gates,
  other calibration, other readout), so it is a plausibility statement only. IBM Heron records
  (`docs/notes/ibm_quantum/`) were not read in this round and carry no stated translation.

## Depth-4 prediction

From the three retained depth-run points of mark 101, propagated through 64 Sobol' draws of the three probabilities
(`continuation_to_depth_4`), on the case's calibration (marked probability of the true state, no readout):

| Hypothesis | P_4 | lambda_4 |
|---|---|---|
| model (a = s = 1, eps = 0) | 0.0592 | 0.583 |
| geometric (eps = 0, a 1.024, s 0.961) | 0.0674 +- 0.0021 | 0.511 +- 0.018 |
| rotation (a 0.924, s 1.034, eps 0.041) | 0.0716 +- 0.0034 | 0.474 +- 0.030 |

The retained uncertainty exceeds the planned binomial standard error of P_4 (0.0011 at 53,760 kept shots), so depth 4
separates the two continuations only weakly; the case decides on depths 1 to 4 jointly, with depth 3 carrying the
rotation (dP_3/d eps = -0.84 at P_3 = 0.24).

## Power and cost of the case

Design: 52 circuits at 16,000 shots (832,000 executions; the job limits are 100 circuits and 2,000,000 executions): mark 101
at depths 1 to 4 in 4, 4, 10 and 4 copies, mark 011 at depths 1 to 3 in 4, 4 and 6 copies, and 16 readout circuits (each
preparation on both sides of the center; both marks read the same preparations through their own marked row and depth
distributions). Kept shots 13,440 per copy. The 101 arms are the arms of the earlier design, so the primary test keeps its
Fisher standard error of eps in the worst (a, s) cell, 0.0035 rad with phi = 1.54.

Calibration over the null box (41 Sobol' cells of a in [0.80, 1.20], s in [0.75, 1.15] and the offset line s = 1, 1,024 points
each): delta = 7.5 (the chi-square(1) 0.99 quantile is 6.63; the worst cell, a = 1.2, s = 1, lies on the box edge where the
fit clips, and has quantile 7.07), false "coherent" at most 0.0088, also on the offset line. The rotation reading needs an
adequate rotation fit (chi-square of (a, s, eps) below the 0.99 quantile on 1 dof), so an incoherent departure from
geometric reads "non-geometric, not a rotation"; planted, a depth-2 deficit of 0.05 reads it, and a fit on a box bound reads
"out of domain".

Power, claimed over a in [0.90, 1.10] and s in [0.90, 1.05] (CZ, PRX and ZZ truths at four corners and 32 Sobol' cells of the
plane rotation): the pooled rule reads "coherent" at |eps_eff| = 0.02 with probability at least 0.969 (worst corner PRX
+0.8 percent, a 0.92, s 0.92), at 0.015 at least 0.89, at 0.01 at least 0.46. Through the whole gated rule (pair
heterogeneity, leave-one-pair-out, readout, box) with binomial copies: 0.949 to 0.988 over the mechanism corners (the 0.949 is
the PRX +0.8 percent corner, |eps_eff| 0.018) and 0.969 to 0.973 for the plane rotation at |eps| = 0.02 in the worst
corner; at the 95 percent dispersion bound phi = 1.54 (the heterogeneity gate runs at phi = 1, so it fires and the
remainder reads "not evaluated"): 0.79 to 0.90. Outside the claimed region the false-alarm rate is controlled and power is
not claimed; the "geometric" reading reaches at least 0.17 of the null cells (weak-signal cells at the box edge).

Mark contrast, binomial copies: for a CZ phase of -0.03 rad (eps_101 0.037, eps_011 about 0) the contrast reads
"CZ-phase-like" with probability 0.95 to 0.96; for a PRX amplitude of -1.6 percent (eps_011 1.19 eps_101) it reads "PRX-like"
with probability 0.94 to 0.95; a ZZ coupling of +20 kHz reads "CZ-phase-like" with probability 0.74 to 0.89 (its mark-011
slope is a tenth of its mark-101 slope), so the contrast does not separate ZZ from a CZ phase. The contrast decides nothing.

Cost: execution of the retained job (1.9985 s, 144,000 circuit-shots) scaled by the ratio of ASAP schedule totals, 7.95, is
15.89 s (14.99 s with the retained fixed 0.13 s removed); compilation 0.44 s. Expected billed seconds ceil(1.6 + 15.89) = 18,
9.0 credits. The ceiling is 26 billed seconds (cancel threshold 25 s), 13.0 credits, which holds 1.5 times the estimate with
compilation (24.5 s) plus the margin; the sibling Emerald run took 2.2 times its estimate (35.0 s here), which the ceiling does
not cover. The `garnet:mock` compile estimate is required before approval and was not read.

Retained mark contrast (post hoc, replayed by a gate on `fits.json`): see the fifth item of the falsification log.

## A5 and Cayley-Dickson contributions

- The sedenion sign-oracle algebra (`gororoba_quantum/sedenion_sign_oracle.py`, [the follow-up design](iqm-garnet-grover-depth-sedenion-walsh.md))
  writes a left row as a phase polynomial whose eight parities sit at odd multiples of pi/4; the Grover oracle and
  diffuser use the same primitive, the seven-parity phase polynomial of the cubic monomial x0 x1 x2 (the line-native CCZ).
  The shared object is that gate network and its Walsh spectrum; it fixes which CZ errors rotate which mark's plane
  (the table above), computed here numerically and not derived from the algebra.
- The A5 records (Gaussian certificates, kernel bundles, Schur entry forms, zero-divisor strata) concern A5 representations
  and zero-divisor strata; none bears on a three-qubit circuit's noise, and they were read by name only.
- The circuit's own symmetry is the group of the six cube automorphisms that fix the marked vertex, which gives the
  four-dimensional invariant sector noted under the limit of validity.
- No novelty claim and no literature check: `docs/notes/prior_work_synthesis.md` records no Grover noise literature, and none
  was searched in this round.
- Open problems of mathematics resolved: none. The case is an engineering test of a rotation term in one device.

## Open design points

- The reading "geometric" needs |eps| + 1.645 SE <= 0.01 rad and is rare in weak-signal cells; the case claims no resolution
  below |eps| = 0.015.
- Quadratic drift is balanced among the depth kinds (mean squared offsets from the center 205.3, 198.3, 199.4, 198.3, 199.3,
  202.3, 208.9; spread 10.7) and not between the depths and the readout preparations (278.3): the placement rules push the
  readouts to the ends and the center.
- phi = 1.54 is a depth-1 bound applied to every depth.

## Not done

Qutrit simulation of coherent leakage; the S3-symmetric four-dimensional extension; the `garnet:mock` compile estimate; the QB12
fault-model, positions and Heron records (the first two are not on any remote branch of this clone); the Tuna-17 TLS note;
`analyze` has run end to end on synthetic collected records only (a model device, a CZ phase and a PRX amplitude planted, a
mock refusal), not on a Garnet record.

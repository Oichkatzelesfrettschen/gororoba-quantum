# IQM Garnet plane model of the line-native Grover retention

The line-native Grover iteration on QB20-QB16-QB17 acts on a two-dimensional plane of the eight-dimensional state, and
the marked probability at every depth reads that plane. This note derives the noisy iteration as an affine map of the
plane's Bloch vector, checks it against exact density-matrix simulation of the committed circuits, fits it to every
retained Garnet Grover acquisition, and records where it fails. Its decision form is the case
[grover-plane-mirrored](../../results/iqm/proposals/grover-plane-mirrored/CASE.md). Evidence:
[iqm-garnet-grover-plane](../evidence/iqm-garnet-grover-plane/README.md). Code: `gororoba_quantum/grover_plane_sim.py`
(engine and response), `grover_plane.py` (affine plane family), `grover_plane_decision.py`, `grover_plane_calibration.py`,
`grover_plane_analysis.py`, `scripts/iqm_grover_plane_case.py`, `scripts/iqm_grover_plane_retained.py`.

## Prior work

Khan and Faryad, "Loss of the quadratic speedup in Grover search under local and coherent noise" (arXiv 2611.16398,
12 November 2026), reduce noisy Grover search to Bloch-type equations for the part of the state that stays in the
two-dimensional search plane, with the noise appearing as leakage and dephasing, derive the rates for bit-flip, phase-flip,
depolarizing and amplitude-damping noise, and bound the success probability under a coherent error in the rotation angle by a
band that widens linearly with depth. This note's plane reduction, its rotation error eps and its affine map with a leak
are that frame applied to the committed line-native circuits of one device; the plane model is an analysis frame here and is
claimed as no new result. What the repository adds is the exact density-matrix response of the committed circuits under the
calibrated noise, the fits to the retained Garnet acquisitions and the decision rule of the case below. (hypothesis: the
paper's closed-form rates and bands could replace the numerical response for the depolarizing part; they were not
compared with the circuit-derived response in this round.)

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

## Eight-cell refit with a nonuniform complement

The fits above read the marked cell only. `scripts/iqm_grover_plane_complement.py` (evidence `complement.json`) refits the same four
(run, mark) groups on all eight outcome cells of every depth (seven independent cells per depth, the delta-method covariance of
the corrected counts, depths independent), with the exact noisy path of the committed circuits, a per group offset a, a per mark
contraction s and rotation eps, and the contraction `rho -> s rho + (1 - s) tr(rho) Sigma` ending at a fixed point Sigma: the
uniform state (the plane family), the S3-invariant sector of the marked vertex (weights of the marked state and the Hamming shells
of distance 1, 2 and 3, per mark), per-qubit populations (shared by both marks), or every cell free (per mark). The marked-cell
fit reproduces the joint fit of the table above (chi2 1.474 on 2 dof, eps 0.0373 and -0.0129, s 1.016 and 0.943).

| Fixed point Sigma | chi2 without eps (dof) | chi2 with eps (dof) | eps_101 | eps_011 | rotation T (2 dof, p) |
|---|---|---|---|---|---|
| uniform | 699.7 (64) | 688.2 (62) | 0.0268 +- 0.0113 (z 2.4) | -0.0330 +- 0.0138 | 11.5 (0.003) |
| S3 shell weights | 624.8 (58) | 621.0 (56) | 0.0169 +- 0.0172 (z 1.0) | -0.068 +- 0.171 | 3.8 (0.15) |
| per-qubit populations | 486.4 (61) | 473.2 (59) | 0.0208 +- 0.0062 (z 3.4) | -0.0097 +- 0.0090 | 13.2 (0.001) |
| every cell free | 385.8 (50) | 382.7 (48) | 0.007 +- 0.138 (z 0.05) | -0.016 +- 0.188 | 3.1 (0.21) |

Readings (computed from the retained counts; hypothesis marks an interpretation).

- The uniform complement is contradicted: shell weights lower chi2 by 74.8 for six parameters (p 4e-14) and per-qubit populations
  by 213.2 for three (p 6e-46), at one rotation each.
- No tested fixed point fits. The best form, every cell free, leaves chi2 386 on 50 dof (250 on 50 after dividing by phi = 1.54), so
  the eight-cell structure of the retained depths is not a diagonal fixed point of one contraction, and no nonuniform form earns
  the role of the model the decision rests on. The case's decision therefore keeps the marked-probability plane family, whose
  response is the exact noisy path and whose excess contraction (s, a) is only an effective description. hypothesis: the unmarked
  cells carry a per-qubit, depth-dependent term (wrong-bit probabilities 0.154, 0.180 and 0.178 on QB20, QB16 and QB17 in the
  earlier review) that the circuit model lacks.
- The depth-3 rotation of mark 101 survives the uniform form (z 2.4) and the per-qubit form (z 3.4, eps 0.021) and is not identified
  once the complement may take other shapes (z 1.0 for shell weights, 0.05 for free cells, whose standard errors of 0.017 and 0.14
  exceed the effect). The marked probabilities alone cannot separate a rotation from a nonuniform return of the leaked weight, so
  the retained eps = 0.041 is a depth-3 anomaly of one mark under the plane family and no more.
- The leak L = s - mu is not identifiable from the marked probabilities: the weight that leaves the plane returns through the
  complement's functional (1 - n_k) h_k, which the depths measured fix only together with eps, as the loss of identification of eps
  above shows.

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
   follow-up case), so that assumption is contradicted by the data; the plane family absorbs it into (a, s) and eps. The
   section "Eight-cell refit with a nonuniform complement" fits all eight outcome cells and reads the consequence: the
   uniform fixed point is rejected, no tested nonuniform fixed point fits, and the depth-3 rotation survives in two of
   the four forms and is not identified in the other two.
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

The run is a prospective replication or refutation of the retained depth-3 anomaly of mark 101 (eps 0.041 +- 0.011, one
marked-probability point under the plane family). It does not identify a CZ, ZZ, PRX or leakage mechanism: a "coherent" reading says
that the plane rotates and not why, ZZ reads like a CZ phase in the contrast, and the leak L = s - mu is not identifiable from the
marked probabilities (the section "Eight-cell refit" frees the complement and eps then loses its identification). The values below
are summarized from the cases' `prediction.json`; [the case](../../results/iqm/proposals/grover-plane-mirrored/CASE.md) and
[its mark 101 variant](../../results/iqm/proposals/grover-plane-mirrored-101/CASE.md) hold the full tables.

Design (variant A): 52 circuits at 16,000 shots (832,000 executions; the job limits are 100 circuits and 2,000,000 executions): mark 101
at depths 1 to 4 in 4, 4, 10 and 4 copies, mark 011 at depths 1 to 3 in 4, 4 and 6 copies, and 16 readout circuits. Kept shots 13,440 per
copy. Variant B drops the 14 mark 011 circuits (38 circuits, 608,000 executions) and keeps the primary test unchanged: its Fisher
standard error of eps in the worst (a, s) cell stays 0.0035 rad with phi = 1.54.

Calibration and power are estimates at listed cells, each with an exact binomial interval (approximate, since the quasi-Monte-Carlo
points are not independent draws); none is a bound over the continuous box. The null evaluation covers 41 Sobol' and offset-line
cells, the four corners of the box and 54 cells of a boundary search, each with 4,096 selection points per cell and 1,024 on the boundary
search: delta = 8.0 (the boundary cell a 1.20, s 0.75 has 0.99 quantile 7.76; the 41 cells alone gave 7.5). The false-alarm rates are
read on validation points that share no point with the selection points (Sobol' indices 2^n + 1 to 2^(n + 1) - 1 of the same draw,
4,095 per cell, 1,024 on the boundary search): false "coherent" 8 of 1,024 (0.0078, interval 0.0034 to 0.0153) at the cell of the
largest selection rate, which is also the largest validation rate over the 99 cells; "non-geometric, not a rotation" at most 1 of 4,095
(interval 0.000006 to 0.0014). The intervals exclude the dependence between points, the box between cells and the model. The build of
variant A took 924 s on the Windows workstation under load from other jobs, the held-out evaluation included. Power at |eps| = 0.02:
0.985 to 0.992 over the corners and 28 cells of the claimed region; at 0.015: 0.874 to 0.992; at 0.01: 0.435 to 0.938 (no resolution is
claimed below 0.015). Mechanism corners (CZ 0.015 rad, PRX 0.8 percent, ZZ 10 kHz): 0.964 to 0.992. Through the pair gates (two-pair floor,
heterogeneity at the covariance's phi, leave-one-pair-out) 0.949 to 1.000 at binomial copies and 0.805 to 0.953 at the dispersion bound
phi = 1.54; with a binomial-phi heterogeneity gate the bound case falls to 0.770 to 0.895. The readout gates pass with probability 1.0
(shift tolerance) and 0.9995, 0.99 and 0.458 (two-sides chi-square at phi 0.86, 1 and 1.54); the copy floor is not modeled.

Mark contrast (variant A), through the departure rule of each mark: a CZ phase of -0.03 rad reads "CZ-phase-like" 0.942 to 0.951, a PRX
amplitude of -1.6 percent reads "PRX-like" 0.925 to 0.939, ZZ +20 kHz reads "CZ-phase-like" 0.734 to 0.864. The PRX ratio carries the
interval [1.1947, 1.2168] of the amplitudes 0.2 to 3 percent; the rejection of a PRX amplitude must hold over it.

Cost, billing v4 sizing (`variant_sizing.json`, coefficients pinned in `billing_v4_inputs.json`):

| | A | B |
|---|---|---|
| expected execution v3 / v4_sum / v4_max (s) | 12.81 / 11.67 / 12.21 | 9.30 / 8.47 / 8.88 |
| max_credits (all-jobs band), cancel threshold | 13.0, 25 s | 9.5, 18 s |
| margin of the threshold at 1.5 and 2.2 times the longest expected runtime | 5.1 s, -4.1 s | 3.4 s, -3.4 s |

The 2.2 times overrun of the sibling Emerald run is not covered in either variant. The `garnet:mock` compile estimate is required before
approval and was not read.

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
- No novelty claim. The plane reduction of noisy Grover search with leakage and dephasing, and bounds on a rotation-angle error,
  are prior work (Khan and Faryad, arXiv 2611.16398, see "Prior work"); `docs/notes/prior_work_synthesis.md` records no Grover
  noise literature, and only that one paper was read against this note.
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
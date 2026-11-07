# Mechanisms behind three results of the pathion hardware runs

Each conjecture lists its candidate mechanisms with the signature each predicts in the retained data and the number
from a log in this directory that decides it. [README.md](README.md) holds the interpreter, the run command and the
script index; the findings and their confidences are in
[the findings document](../../../../results/live/PATHION_KERNEL_MAP_FINDINGS.md).
"Observed" is read from a retained file; "inferred" is computed from a model. A statistic that a bootstrap or Monte
Carlo draw carries (a standard error, a draw mean) changes in its last digits with the seed; the seeds are fixed, so a
rerun reproduces each log.

Two facts govern how the retained IBM numbers read.

1. The null-offset values in each IBM `record.json` (ibm_fez blocks 0.050, 0.019, 0.015, 0.013, operand 0.096;
   ibm_marrakesh 0.035, 0.009, 0.015, 0.017, operand 0.075) are noise-model predictions (state `submitted`;
   `groups[0].summary` is built from the simulated `noisy` laws by `live_run.replica_statistics`). The measured values
   are in `collect.json[1].measured_statistics`, and `c2_scale.txt` recomputes them from `raw/pub_*.json` (17 and 11
   replicas) and matches the repository summary to four digits.
2. The estimator `N_hat = (sum_y c(y) / 2) / V` keeps an ideal zero only under a symmetric product readout
   (`c2_algebra.txt`). A readout error common to both arms maps the zero to zero for the selector contrast and not
   for `N_hat`.

## C1. Ascella two-block job: the mirror failure is not a per-mode efficiency effect

Data: `results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00`, the one-block
predecessor `results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00`,
`scripts/ascella_pathion_coset_block_pairs_analysis.py`, `mirror_test.py`.

Observed (`c1_observed.txt`): 46 mirror pairs, 9 over 0.07, |d| median 0.0259, max 0.1082, rms 0.0488 (d = calibrated
level in slot orientation 0 minus orientation 1). Each iteration's `result_fields.computed_circuit` is the compiled mesh
(66 MZI blocks, 132 BS with theta 1.42 to 1.45 rad, 126 phase shifters); `c1_mesh.txt` shows that the single-photon
propagation through it matches the ideal label law to 1.9e-4 for all 52 iterations. Identical settings carry
bit-identical meshes (iterations 0/51, 1/50, 2/49).

| Mechanism | Predicted signature | Result | Verdict |
|---|---|---|---|
| counting statistics | z = d/se near 1 | bootstrap se median 0.0041; z rms 11.33; chi2 5908 on 46 (`c1_observed.txt`) | refuted |
| drift | abs(d) grows with separation | Spearman -0.050 (p 0.743); identical-mesh repeats differ at most 0.0055 raw; predecessor repeats rms 0.0024 against 0.0028 from counting (`c1_observed.txt`, `c1_predecessor.txt`) | refuted |
| per-mode efficiency | a nine-parameter model predicts d | median 0.0026, max 0.0155 in sample, max 0.0167 held out on orientation 0, flags 0 of the 9 failing pairs; residual rms 0.0461 against 0.0488 observed, about a tenth of the variance (`mirror_test.txt`) | refuted |
| multiphoton or threshold events | abs(d) tracks excluded events | invalid share at most 5.26e-4 and sentinel share at most 7.86e-4 against \|d\| of order 0.03; rank correlation of abs(d) with the invalid share +0.609 | refuted by size |
| count rate | `shots_used` or `physical_perf` tracks the pairs | `shots_used` 131072 in every iteration; Spearman(abs d, abs of the perf difference) -0.334 | no support |
| anchor calibration | a wrong B/A ratio gives an antisymmetric slot term | below | dominant |
| random phase error per shifter | rms d rises with sigma | below | reproduces the magnitude |
| static per-shifter error | out-of-sample prediction of the other orientation | below | partial |
| global BS theta shift | one signed parameter | held-out correlation -0.720 and -0.497 (`c1_heldout.txt`) | refuted |

Anchor calibration (`c1_anchor.txt`). A two-parameter slot model (offset 0.0057, gain 0.0761) cuts the rms from 0.0488
to 0.0248 (`c1_observed.txt`). The anchor efficiencies are A 1.0064 and B 1.0886 (B/A 1.082); the mode fit over all
iterations gives A 1.0721 and B 1.064 (B/A 0.992).

| efficiency (A, B) | failing of 46 | median | max | rms |
|---|---|---|---|---|
| anchor-calibrated, as analyzed (1.0064, 1.0886) | 9 | 0.0259 | 0.1082 | 0.0488 |
| no division (1, 1) | 1 | 0.0142 | 0.0752 | 0.0250 |
| equal, anchor mean (1.0475, 1.0475) | 1 | 0.0141 | 0.0737 | 0.0246 |
| mode-fit slot sums (1.0721, 1.064) | 0 | 0.0138 | 0.0698 | 0.0237 |

The rms-minimizing B/A is 0.985. Anchor B reads raw 1.042 (2 percent above ideal) and anchor A 1.004. Under white phase
error of 0.033 rad the gain coefficient has sd 0.0566, so +0.0761 is z +1.4 (24 of 300 draws at or above it): the
anchor meshes' own error, carried by the calibration into every level, suffices for the slot term. The equalized
analysis uses this job's own iterations and is a diagnostic; it does not replace the preregistered admission rule.

Random phase error, anchor-calibrated (`c1_phase.txt`, 300 draws): sigma 0.020 gives rms 0.0296 and 1.6 failing pairs;
0.030 gives 0.0441 and 5.5; 0.050 gives 0.0750 and 12.8; the observed rms 0.0488 with 9 failing matches sigma 0.033.
With the mode-fit efficiencies (`c1_phase_eq.txt`; observed rms 0.0237, 0 failing) sigma 0.020 gives rms 0.0240 and
0.6 failing. Cross-checks (`c1_predecessor.txt`): the predecessor's per-iteration rms departure from ideal is 0.0127
(sigma 0.033 predicts 0.0137, sigma 0.020 predicts 0.0083), so the shared value is 0.02 to 0.03 rad; a fluctuating
error predicts a predecessor repeat-pair rms of 0.0189 against 0.0024 observed, so the error is static per
configuration. Static per-shifter models scored on the held-out orientation (`c1_heldout.txt`): per-shifter gain
correlation +0.543 and +0.561 with held-out level rms 17 and 13 percent below the efficiency-only base; per-shifter
offset +0.273 and +0.546; global gain +0.510 and +0.358; global BS theta -0.720 and -0.497 with rms 20 and 9 percent
above the base. The fits carry a ridge prior and leave a held-out level rms of 0.0195 to 0.0306 (`c1_static.txt`), several times the
counting error, so they are not an error map.
`c1_static_null.txt` repeats the held-out score with shuffled links between configurations and their errors.

Which pairs fail (`c1_controls.txt`): the simulated phase sensitivity has Spearman +0.633 with abs(d), and the
ideal level alone +0.676; the partial rank correlation given the item's ideal level, total level, entropy and lit
modes is +0.007 (p 0.965), so the sensitivity adds no prediction beyond the level.

Verdict C1. Part one (the mirror failure is not per-mode efficiency) survives at 0.9. Part two, that the cause is
configuration-specific phase error, survives weaker and redirected at 0.55: the failure count follows the anchor
calibration (B/A 1.082 from two anchor meshes against about 0.99 from the rest), and without that division 0 or 1
pairs fail, below the allowance of 4. A static residual of rms 0.024 (six times the counting se) matches about 0.02
rad per shifter and is not shown to be a per-setting mesh error rather than slot structure. Raises it: several anchor
configurations (compilation seeds) per slot whose B/A scatters by about 0.09, and failing settings replayed at
identical configuration reproducing d within 0.005. Lowers it: anchors agreeing near 1.08. Not run: static
non-unitary per-path loss (per-component loss is not retained).

## C2. The positive Tuna-17 null offset

Tuna b0 = e1 + e17 on basis (16, 1, 2); coset 0 is ibm block k0.

(a) One scale from raw counts (`c2_scale.txt`; IBM mean over replicas with replica-spread se; Tuna with a 2000-draw
bootstrap):

| quantity | Tuna coin b0 | Tuna stopped | ibm_fez k0 | ibm_marrakesh k0 |
|---|---|---|---|---|
| N_hat | +0.1537 +- 0.0314 | +0.1517 +- 0.0424 | +0.0257 +- 0.0122 | +0.0289 +- 0.0243 |
| half-sum of c | +0.0680 +- 0.0138 | +0.0733 +- 0.0205 | +0.0203 +- 0.0091 | +0.0178 +- 0.0149 |
| visibility V | 0.442 | 0.483 | 0.759 | 0.748 |
| selector contrast | +0.0164 +- 0.0039 | +0.0167 +- 0.0055 | -0.0019 +- 0.0020 | -0.0003 +- 0.0033 |

Tuna coin minus ibm_fez N_hat z +3.8 and minus ibm_marrakesh z +3.1; the two Tuna designs agree (+0.002 +- 0.053).
ibm_fez k4, k8 and k12 read N_hat +0.0112, +0.0042 and +0.0039; ibm_marrakesh +0.0544, +0.0510 and +0.0528 (se 0.024
to 0.027); all selector contrasts lie within 0.004 of 0. Readout-corrected (`c2_scale.txt`, `c2_tuna.txt`): ibm_fez
-0.0102, -0.0028, -0.0119, -0.0130; ibm_marrakesh +0.0025, +0.0483, +0.0439, +0.0454; Tuna b0 +0.0805 +- 0.0307.

(b) Estimator algebra (`c2_algebra.txt`, `c2_mech.txt`): any arm-symmetric product readout sends the ideal selector
contrast to 0 (at most 2.2e-16 over 5000 draws); N_hat keeps zero only under symmetric readout (e01 = e10); an
asymmetric one gives sum c up to 0.709 over 5000 draws, and +0.0452 for ibm_fez replica 0's calibrated qubits. A
correlated readout breaks even the selector zero (up to 0.022). The finite-sample ratio bias at 8192 shots is at
most 1.9e-4 in magnitude.

(c) Mechanisms on the actual circuits (`c2_mech.txt` and `c2_mech.json`: a density-matrix simulator of the ibm_fez
replica sub-circuits from `isa.qpy` with calibrated T1, T2 and readout; the routed Tuna `.cq` circuits in
`c2_tuna_mech.txt` and `c2_stopped.txt`). The plus and minus circuits differ by one virtual rz on IBM and one Rz in
the stopped Tuna series, so incoherent noise is arm-symmetric by construction; only a coherent error that treats the
arms differently gives a selector contrast.

| mechanism | ibm_fez N_hat k0 / k4-k12 | ibm_fez selector k0 | Tuna coin b0 N_hat | Tuna selector |
|---|---|---|---|---|
| measured | +0.0257 / +0.0112, +0.0042, +0.0039 | -0.0019 +- 0.0020 | +0.154 +- 0.031 | +0.0164 +- 0.0039 |
| calibrated readout only | +0.0358 / +0.0163 | 0 | +0.0703 | 0 |
| T1 and T2, gates only | +0.0038 / +0.0007 | 0 | +0.085 (25 us) to +0.108 (12 us), with readout | 0 |
| all calibrated incoherent | +0.0395 / +0.0170 | 0 | +0.0842 (depolarizing 0.02 and T1 25 us) | 0 |
| all calibrated incoherent with measurement-time T1 | +0.0969 / +0.0638 | 0 | not run | not run |
| sx or X90 over-rotation +0.03 rad | +0.0079 / -0.0037 | +0.0167 | +0.0931 | +0.0167 |
| sx or X90 over-rotation -0.03 rad | +0.0084 / -0.0035 | -0.0128 | +0.0804 | -0.0092 |
| CZ phase +0.05 (IBM) or +0.06 rad (Tuna) | +0.0059 / 0 | -0.0003 | +0.0493 | -0.0006 |
| CZ phase -0.05 (IBM) or -0.06 rad (Tuna) | +0.0038 / 0 | +0.0003 | +0.0797 | +0.0006 |
| ZZ at the Tuna coupler table (x1) | not run | not run | +0.0666 | -0.0003 |

The independent compile (stopped series, transpiler seed 3704, separate plus and minus circuits, 20 CZ;
`c2_stopped.txt`) gives selector 0.0000 for readout only, +0.0160 for an over-rotation of +0.029 rad against the
observed +0.0167 +- 0.0055, -0.0103 for -0.029 rad, and about 0 for CZ phase and T1. The 1-CZ blocks (k4, k8, k12)
read selector 0 for any over-rotation (`c2_mech.json`). `c2_overrotation.txt` inverts each compile's response through
its own measured selector contrast: the Tuna coin value implies an over-rotation of +0.0295 +- 0.0070 rad and the
stopped series +0.0302 +- 0.0100 rad; ibm_fez implies -0.0044 +- 0.0046 rad and ibm_marrakesh -0.0007 +- 0.0069 rad.
The Tuna coin angle exceeds ibm_fez's by 0.0340 rad (7.3 sigma of the IBM error alone, 4.0 sigma of both errors) and
ibm_marrakesh's by 0.0302 rad (4.4 and 3.1 sigma).

(d) Other operands (`c2_resid_informative.txt`; 22 informative blocks per device; the 10 all-aligned N_b = 4 blocks
read 4 under any noise): ibm_fez ideal-zero blocks measured minus calibrated prediction +0.0046 +- 0.0030 (corr
+0.74); ibm_marrakesh +0.0232 +- 0.0049 (corr +0.77), with the excess in `e1pe17` k4, k8 and k12 and in `e1pe10` k16
(`c2_resid_marrakesh.txt`). Nonzero-nullity blocks show no additive offset: the six N_b = +2 blocks read +0.056 to
+0.082 on ibm_fez against +0.076 to +0.112 predicted, and +0.036 to +0.097 on ibm_marrakesh against +0.089 to +0.147.

Verdict C2. The ibm_fez N_hat offset is an estimator-plus-readout effect at 0.8 (it vanishes after readout
correction); the three low-CZ blocks of ibm_marrakesh at +0.05 stay open. The Tuna selector contrast is not an
estimator artifact (zero under every product readout and unital or T1 channel); its size and sign are reproduced by one
coherent X90 over-rotation of about +0.03 rad in two independent compiles, at 0.75, and the IBM selector contrasts sit
3.1 to 4.0 combined standard errors away from that angle. A correlated selector readout is not excluded. Next: a Tuna
1-CZ null block (k4 type) added to the coin design (an over-rotation predicts selector 0; an arm-asymmetric or
correlated-readout offset predicts about +0.016). A mirrored recompile cannot decide it, since virtual-Z conjugation
keeps the sign of the pulse error. IBM control: the 20-CZ k0-type null block on at least 17 placements plus the 1-CZ
blocks, reporting selector contrast and readout-corrected N_hat.

## C3. The Tuna-17 `ba` misses follow the logical bit d2

Layout at measurement (`c3_readout.txt`): `ba` d0 on q11, d1 on q12, d2 on q4; `bb` d0 on q12, d1 on q11, d2 on q4;
`b0` d0 on q12, d1 on q4, d2 on q11; selector q8 and coin q2 in all; CZ per edge (4,8), (8,11), (8,12), (2,4): `ba`
10, 4, 6, 1; `bb` 10, 8, 4, 1; `b0` 10, 6, 4, 1. The readout-corrected cross-platform comparison of the retained
analysis (`results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json`, `decisions.cross_platform`) fails `ba`
on bins 1, 5 and 7 against ibm_fez and on bins 5 and 7 against ibm_marrakesh (bin y = d0 + 2 d1 + 4 d2); every
failing bin has d0 = 1. Walsh decomposition of the corrected misfit (`c3_walsh.txt`): the d2 main effect appears in
all three templates, `ba` +0.066 (z 8.3), `bb` +0.044 (z 4.5) and `b0` +0.063 (z 7.6), although d2 sits on q4, q4 and
q11; split by physical qubit the effects disagree. `ba` alone adds d0 x d2 +0.053 (z +6.7). The readout-corrected IBM
ratios deviate from the ideal +-1 by at most 0.051 (ibm_fez) and 0.067 (ibm_marrakesh) in any bin.

Mechanism fits on the 24 raw bins (`c3_corr.txt`, `c3_multi.txt`, `c3_zz.txt`, `c3_mech2.txt`, `c3_depol.txt`);
the baseline of the bracket product readout with a contraction per template has chi2 288.9 (21 dof):

| mechanism | chi2 |
|---|---|
| best correlated readout over one physical pair (q4 onto q11) | 214.6 |
| best correlated readout over one logical pair (d2 onto the selector) | 149.8 |
| one physical source onto the rest, best (q4) | 182.0 |
| one logical source onto the rest, best (d2) | 141.2 |
| ZZ at the coupler table, scale -1.08 (best) to +1 | 285.0 to 299.7; larger ZZ is worse |
| X90 over-rotation +-0.03 rad | 289.1 and 387.8 |
| CZ conditional phase +-0.03 and +-0.06 rad | 231.8 (+0.06) to 453.2 (-0.06) |
| T1 12 to 100 us (T2 = 2 T1) | 193.2 to 267.7 |
| gate depolarizing, p2 0.03 (reproduces a per-CZ contraction near 0.97) | 143.3 |
| T1 25 us with p2 0.02 | 154.2 |

Verdict C3. A per-template coupling set by routing is refuted at 0.75: no physical-qubit or coupler formulation
reproduces the pattern, whose main effect follows the logical bit d2 across three different physical placements. The
best partial explanation is gate-level noise on the compiled structure acting on logical d2, at 0.5 (chi2 about 143
against a baseline of 288.9, still about seven times the degrees of freedom). Next: the same template on a placement
related by a device-graph automorphism (identical compiled structure, different qubits), and a joint readout
calibration of the routed qubits.

## Not run, and limits

- Static non-unitary per-path loss for C1 (per-component loss is not retained).
- IBM ZZ crosstalk beyond the scan of `c2_mech.txt` (Heron publishes no coupler table); the IBM simulation uses
  calibrated target errors only.
- Tuna-17 gate durations (20 ns, 60 ns CZ) and T1 are assumed (no published calibration); the T1 and ZZ rows are
  scans.
- The static shifter fits use a ridge prior and are not an error map.

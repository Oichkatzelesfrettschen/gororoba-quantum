# Pathion kernel map on ibm_fez (2026-11-06)

The written case `2026-11-06T180755.872625Z/CASE.md` ran through `scripts/approved_run.sh` with
`scripts/pathion_kernel_map_check.py` as its check: binding dry run
[2026-11-06T183051.978364Z](2026-11-06T183051.978364Z/record.json), run
[2026-11-06T183538.809814Z](2026-11-06T183538.809814Z/collect.json), job `dbn1tv8qtr0c73ac82eg` on ibm_fez, backup
account, 24 PUBs, 16,384 shots, five replicas, 18 s charged (14.8 s estimated). Acquisition
`ibm-fez-pathion-kernel-map`.

## Per-circuit visibility and nullity estimate

V is the signed mean of the per-output contrasts against the ideal signs; N_hat is half their sum over V
(`gororoba_quantum/pathion_kernel_map.py`). Intervals are Student t over the five replicas.

| Operand (m = i ^ j) | Routed CZ | V pooled [interval] | V per replica r0..r4 | N_hat [interval] | Ideal | Model | Signs |
|---|---:|---|---|---|---:|---:|---:|
| e1 + e17 (16) | 151 | 0.345 [0.30, 0.39] | .39 .30 .31 .36 .37 | 1.54 [-0.47, 3.54] | 0 | 0.25 | 32/32 |
| e1 + e26 (27) | 167 | 0.094 [-0.03, 0.22] | .00 -.03 .20 .14 .16 | unresolved | 4 | 4.26 | 23/32 |
| e2 + e27 (25) | 142 | 0.169 [0.04, 0.30] | .06 .06 .26 .26 .22 | 8.25 [3.65, 12.84] | 4 | 4.28 | 27/32 |
| e1 + e10 (11) | 136 | 0.184 [0.02, 0.35] | .21 -.03 .30 .28 .16 | 7.30 [0.85, 13.74] | 8 | 8.37 | 28/32 |
| e1 + e18 (19) | 162 | 0.139 [0.09, 0.19] | .13 .08 .17 .18 .13 | 12.65 [11.87, 13.42] | 12 | 12.37 | 26/32 |
| e1 + e24 (25) | 142 | 0.138 [0.01, 0.27] | .10 -.02 .23 .24 .14 | 8.37 [-1.77, 18.51] | 12 | 12.57 | 25/32 |
| twin e17 - e10 (27) | 155 | 0.122 [0.00, 0.24] | .03 .01 .18 .20 .20 | unresolved | 4 | 3.91 | 25/32 |
| twin e17 - e2 (19) | 153 | 0.243 [0.19, 0.29] | .22 .21 .22 .27 .30 | 11.87 [10.93, 12.81] | 12 | 12.34 | 31/32 |
| cocycle-free e1 + e10 | 48 | 0.496 [0.41, 0.58] | .42 .44 .55 .57 .51 | -6.78 [-7.52, -6.04] | -6 | -6.36 | 32/32 |
| cocycle-free e1 + e18 | 50 | 0.593 [0.57, 0.62] | | -1.31 [-2.05, -0.58] | -2 | -2.14 | 32/32 |
| flipped e1 + e18 | 173 | 0.207 [0.15, 0.26] | .20 .17 .17 .22 .27 | 11.39 [10.78, 11.99] | 11 | 11.50 | 30/32 |

Skeleton P(s = 0) = 0.990 [0.979, 1.001].

## Preregistered rules

1. Resolution (visibility above zero and at least 31 of 32 signs): holds for the null, the twin e17 - e2 and both
   cocycle-free controls; fails for the other deep operands (23 to 30 of 32).
2. Nullity, primary readout: e1 + e18, the twin e17 - e2 and the flipped arm sit inside their bands; e2 + e27, e1 + e10
   and e1 + e24 are too wide to decide; e1 + e26 and the twin e17 - e10 are unresolved.
3. Differences: flipped minus unflipped e1 + e18 = -1.26, the predicted one-unit step; the twin e17 - e2 differs from
   e1 + e18 by -0.77 [-1.36, -0.19], an interval that excludes zero by 0.19; cocycle-free values are negative.
4. Ratios: outside their bands (12/4 ratio 1.48), as rule 4 anticipated when the visibility differs by operand.
5. Depth scaling: the calibrated model's 0.49 to 0.58 is refuted (pooled 0.09 to 0.24 deep, 0.50 to 0.59 at 48 to 50
   CZ against a modeled 0.77 to 0.84); the compounded-excess branch, 0.20 to 0.27, survives at its band or below it.
6. Nulls: the e1 + e17 interval covers 0.25; the skeleton reads one minus the selector's readout error.

## The operand-dependent collapse

On replicas r0 (qubits 24-26, 37, 44, 45) and r1 (123, 124, 136, 142-144) the visibility falls to about zero exactly
for the operands with m in {25, 27} (bits 0, 3, 4), while the operands with m = 19 (bits 0, 1, 4) keep 0.13 to 0.30 on
the same qubits. The SELECT's CX fan-out from the selector follows the bits of m, so the loss rides on the selector's
path to the data qubit carrying bit 3 in those two placements. Hypothesis: a weak coupler or a TLS-affected qubit on
that path; the CZ error and T1 of those placements at the run's calibration decide it.

## Consequence for the design

At 136 to 173 routed CZ the full map loses most of its contrast; the coset-block decomposition reproduces every
per-output contrast of the full map exactly (four blocks of four XOR pairs, block half-sums summing to N) at 18 to 27
routed CZ on Heron r2 targets, which the next case uses on ibm_fez and ibm_marrakesh.

# Coset-block map on ibm_fez and ibm_marrakesh (2026-11-06)

The written case [2026-11-06T194735.738910Z/CASE.md](2026-11-06T194735.738910Z/CASE.md) tiled each operand by the four
cosets of a 3-dimensional subspace containing i ^ j (`gororoba_quantum/pathion_coset_block.py`, group
`pathion_coset_map`, 64 four-qubit circuits at 1 to 20 routed CZ) and ran through `scripts/approved_run.sh` with the
check `pathion_kernel_map_check.py pathion_coset_map 8 30`:

- ibm_fez, backup account: binding dry run `2026-11-06T200151.405088Z`, run
  [2026-11-06T201037.234804Z](2026-11-06T201037.234804Z/collect.json), job `dbn3a55t7fqc73ais42g`, 17 replicas,
  18 s charged; acquisition `ibm-fez-pathion-coset-map`.
- ibm_marrakesh, primary account: binding dry run `2026-11-06T200151.093434Z`, run
  [2026-11-06T200832.558771Z](2026-11-06T200832.558771Z/collect.json), job `dbn38t0ou4as73b3q1n0`, 11 replicas,
  24 s charged; acquisition `ibm-marrakesh-pathion-coset-map`, retained with the primary account at 44 s, below the
  inventory's 60 s reserve, which the audit now records (`account_reserve_met`) rather than enforcing at retention.

| Operand (ideal N) | Fez N_hat [interval] | Fez readout-corrected | Marrakesh N_hat [interval] | Marrakesh readout-corrected | Signs |
|---|---|---|---|---|---|
| e1 + e17 (0) | 0.05 [-0.02, 0.12] | -0.04 | 0.19 [0.03, 0.35] | 0.14 | 32/32 |
| e1 + e26 (4) | 4.25 [4.15, 4.35] | 4.02 | 4.28 [4.19, 4.38] | 4.05 | 32/32 |
| e2 + e27 (4) | 4.23 [4.13, 4.33] | 4.03 | 4.26 [4.10, 4.42] | 4.04 | 32/32 |
| e1 + e10 (8) | 8.05 [8.01, 8.09] | 8.00 | 8.07 [8.02, 8.13] | 8.04 | 32/32 |
| e1 + e18 (12) | 12.02 [12.00, 12.04] | 11.98 | 12.02 [11.98, 12.05] | 11.99 | 32/32 |
| e1 + e24 (12) | 12.14 [12.05, 12.24] | 11.99 | 12.11 [12.02, 12.19] | 11.87 | 32/32 |
| twin e17 - e2 (12) | 12.03 [12.00, 12.05] | 11.99 | 12.03 [12.01, 12.06] | 12.01 | 32/32 |
| cocycle-free e1 + e18 (-2) | -2.14 [-2.21, -2.07] | -1.96 | -2.15 [-2.30, -2.00] | -1.85 | 32/32 |

Rules of the case: (1) resolution holds on every operand of both devices; (2) every N_hat lies within 0.5 of its model
value, and the readout-corrected values lie within 0.15 of the integer nullity; (3) the twin difference is 0.008
[-0.018, 0.033] (Fez) and 0.014 [-0.017, 0.045] (Marrakesh), the cocycle-free value within 0.15 of -2; (4) the pooled
block visibility 0.76 to 0.87 lies mostly below the calibrated model's 0.84 to 0.93 and at the top of the Fez-excess
branch's 0.70 to 0.80; (5) no replica shows the i ^ j-dependent loss: the largest gap between the m in {25, 27} and
m = 19 blocks is 0.064 (Fez) and 0.089 (Marrakesh), and on the very qubits where the full map collapsed (24-26 with 37,
136 with 142-144) the m in {25, 27} blocks read 0.84 to 0.86 against 0.86 to 0.89 for m = 19, so the loss of the full
map comes from its depth, not from a broken coupler; (6) the two devices agree on every operand within their
intervals.

# Cross-platform runs: Tuna-17 and Ascella (2026-11-07)

This section interprets the acquisitions retained with the Tuna-17 and Ascella runs: the first Tuna-17 series that
stopped on its drift rule (QX emulator batches `qi-pathion-coset-block-qx-2026-11-06t221242-batch-00` to `-07` and
Tuna-17 batches `qi-pathion-coset-block-tuna-17-2026-11-06t221626-batch-00` to `-03`), the coin-arm series (QX control
`qi-pathion-coset-coin-qx-2026-11-07t000930-batch-00` and Tuna-17 batches
`qi-pathion-coset-coin-tuna-17-2026-11-07t001031-batch-00` to `-03`), and the two Ascella pathion jobs, each with its
`sim:ascella` twin (`qd-sim-ascella-pathion-four-term-blocks`, `qd-qpu-ascella-pathion-four-term-blocks`,
`qd-sim-ascella-pathion-coset-block-pairs`, `qd-qpu-ascella-pathion-coset-block-pairs`). Registry claims:
`hw-tuna17-pathion-coset-coin`, `hw-tuna17-pathion-coset-block-stopped`, `hw-ascella-pathion-four-term-blocks` and
`hw-ascella-pathion-coset-block-pairs`. The two parallel-coset runs on ibm_fez and ibm_kingston receive their findings
with their own claim. The mechanism probes behind the conjecture results are in
[the conjectures directory](../../docs/evidence/pathion-kernel-map/conjectures/README.md); each mechanism statement
below is a `hypothesis:` unless a retained file decides it.

## Tuna-17: the stopped series and the coin-arm series

The first series ran the QX control (8 batches) and Tuna-17 batches 00 to 03 of the coset-block design and stopped when
the readout-1 circuit of batch 03 read q11 e10 = 0.1066 against 0.2762 in batch 01, a change of -0.1696 against the
0.02 limit (`results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json`, `references.flagged`). Its coin-free
null block b0 (e1 + e17, basis 16, 1, 2) reads selector contrast +0.0167 +- 0.0055 (pinned as `STOPPED_B0_SELECTOR` in
`scripts/qi_pathion_coset_coin_cases.py`; recomputed from the raw shots in `c2_scale.txt`). The series stays as the
coin-free reference for the null.

The coin series (QX control, then Tuna-17 batches 00 to 03 on qubits 2, 4, 8, 11, 12) treats a readout drift as a
covariate, not a stop. The analysis `results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json` is complete with
`all_decisions_met` false:

| Decision | Result | Measured value |
|---|---|---|
| resolution (every one of 8 bins reads its ideal sign) | holds for `ba` and `bb` | selector contrast `ba` 0.2350 +- 0.0038 (z 61.6), `bb` 0.1749 +- 0.0039 (ideal 0.5 for both); every bin z at least 25.5 |
| pattern (bins 2 and 6, where the ideal signs of the two blocks differ) | holds | z 25.5 and 32.8 |
| cocycle-free control | holds | `xor_ba` selector contrast -0.7181 +- 0.0054 (z -132.3) against `ba` +0.2350 (z 61.6) |
| null (selector contrast of b0 is 0) | fails | 0.0164 +- 0.0039, z 4.19; the stopped series reads 0.0167 +- 0.0055 (difference z -0.03) |
| cross-platform agreement of the readout-corrected ratios, at least 7 of 8 bins per template and device | fails | `b0` 7 of 8 on both devices, `bb` 7 of 8 on both, `ba` 5 of 8 against ibm_fez and 6 of 8 against ibm_marrakesh |

The QX control passes its analysis-path gate (`pathion_coset_coin_qx_analysis.v2.json`, `qx_control.pass` true, every
arm within twice its sampling floor). The implied contraction per routed CZ is 0.9688 (`ba`), 0.9643 (`bb`) and 0.9680
(`b0`). The cross-platform result does not depend on the readout bracket: the bins within agreement stay at 5 and 6 for
`ba` under each batch's bracket (`drift_covariate.cross_platform_under_each_bracket`).

The cocycle-free result carries the physics claim: with every SELECT sign table replaced by its XOR permutation the
selector contrast flips from +0.235 to -0.718, so the Tuna-17 block reads the A_5 sign network and not its XOR
permutation.

### The null offset

The b0 selector contrast is zero under any arm-symmetric product readout and any unital or T1 channel
(`c2_algebra.txt`, `c2_tuna_mech.txt`), so the +0.0164 offset is physics, not an estimator artifact. On IBM the same
block (e1 + e17, coset k0) reads -0.0019 +- 0.0020 on ibm_fez and -0.0003 +- 0.0033 on ibm_marrakesh, measured values
from `collect.json` (`c2_scale.txt`; the `record.json` numbers are noise-model predictions). Two independent compiles
of the null block (the coin design and the stopped series, 20 CZ each) respond to a single X90 over-rotation with
selector contrast +0.0167 per +0.03 rad and +0.0160 per +0.029 rad, against +0.0164 and +0.0167 observed
(`c2_tuna_mech.txt`, `c2_stopped.txt`); CZ phase error, T1 and depolarizing noise move the selector by at most 0.0006 and the
retained ZZ coupler table by -0.0003 (0.0018 at ten times the table); `c2_overrotation.txt` inverts the responses.

hypothesis: one coherent X90 over-rotation of about +0.03 rad (+0.0295 +- 0.0070 rad from the coin series, +0.0302 +-
0.0100 rad from the stopped series) produces the Tuna-17 offset. IBM reads -0.0044 +- 0.0046 rad on ibm_fez and -0.0007
+- 0.0069 rad on ibm_marrakesh, which sit 4.0 and 3.1 combined standard errors below the Tuna-17 angle (7.3 and 4.4
against the IBM error alone). Confidence 0.75. A correlated selector readout is not excluded and would also give
about +0.016. A Tuna-17 1-CZ null block (the k4 type of the IBM coset map) added to the coin design decides it: an
over-rotation predicts selector 0 there (every 1-CZ block reads 0 for any angle, `c2_mech.json`), a
correlated-readout offset predicts about +0.016. A
repetition on one more Tuna-17 calibration raises the confidence; a nonzero 1-CZ selector contrast lowers it.

### The `ba` misses follow the logical bit d2

The failing `ba` bins (1, 5, 7 against ibm_fez; 5, 7 against ibm_marrakesh; bin y = d0 + 2 d1 + 4 d2) all have d0 = 1.
The readout-corrected Tuna ratios there read 0.835 and 0.947 where d2 = 0 and 1.124 and 1.133 where d2 = 1; the d0 = 0
bins agree with both devices within 0.07, and the IBM ratios sit within 0.051 (ibm_fez) and 0.067 (ibm_marrakesh) of
the ideal +-1 (`pathion_coset_coin_tuna_17_analysis.json`, `decisions.cross_platform`). The Walsh decomposition of the
corrected misfit puts the d2 main effect in all three templates, `ba` +0.066 (z 8.3), `bb` +0.044 (z 4.5) and `b0` +0.063
(z 7.6), although d2 sits on physical qubit q4, q4 and q11 (`c3_walsh.txt`, `c3_readout.txt`). A coupling set by the
routed physical qubits does not reproduce this: the best correlated readout over one physical pair (q4 onto q11)
reaches chi2 214.6 against a baseline of 288.9 on 24 raw bins, one over the logical pair (d2 onto the selector) 149.8,
ZZ at the retained coupler table 285.0 to 299.7, X90 over-rotation 289.1 and above, CZ phase 231.8 and above
(`c3_corr.txt`, `c3_multi.txt`, `c3_zz.txt`, `c3_mech2.txt`). Gate depolarizing noise of p2 0.03 reaches 143.3 and
reproduces the per-CZ contraction near 0.97 (`c3_depol.txt`).

hypothesis: gate-level noise on the compiled structure acts on the logical bit d2 and leaves a bin-dependent contraction
that the per-qubit assignment correction cannot remove. Confidence 0.5; chi2 about 143 is still seven times the degrees of
freedom. The routing-coupling alternative is refuted at 0.75. The same template on a placement related by a device-graph
automorphism (identical compiled structure, different qubits) decides it: a d2 effect that follows the logical bit raises
the confidence, an effect that follows the qubits lowers it. A joint four-state readout of the routed d0 and d2 qubits
costs no IBM time and tests the correlated-readout form.

## Ascella: four-term blocks (one block per photon)

The qpu:ascella job `f3a11b5f-b045-42be-9205-de7da91cbfec` (88 iterations of 32,768 samples, 1.032768 credits) passes
admission and conformance (`results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00/analysis.json`):
anchor 0.9989, dark 0.0023, anchor drift 3.4e-8, null levels 0.2813 and 0.2494 against 0.25, repeated arm pairs 0 of 44
over the limit. All 8 pathion readings (B12 blocks 2, 3, 6, 7 at ideal 0.75; C8 blocks 4 to 7 at ideal 0.6545) and both
D = 16 reference readings lie within 0.07, and all 11 mutation readings read their mutated level. The C8 class spreads by
0.048 (blocks 4, 5, 6 read 0.0234, 0.0253 and 0.0241 low, block 7 reads 0.0227 high), under its 0.05 flag. The matching
`sim:ascella` job returns the ideal levels (maximum pooled departure 0.0035). The result is conformance of programmed
operator blocks to their interference law on one 12-mode mesh; the client computes every cd_core sign, so the chip does
not compute the algebra.

## Ascella: two coset blocks per photon (instrument not admitted)

The qpu:ascella job `db6355f7-87d5-4e7a-91f5-b898c33c839a` (52 iterations of 131,072 samples, 161 s against 166.4 s
expected, 1.131072 credits) fails admission on mirror agreement: 9 of 46 mirrored readings (the same setting in the
other slot orientation) differ by more than 0.07 against an allowance of 4
(`results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00/analysis.json`).
The other admission conditions pass: anchors 1.0037 (slot A) and 1.0419 (slot B), darks 0.0023 and 0.0013, anchor drift
at most 0.0055, dark drift at most 0.0008, sentinel share at most 0.0008, null levels within 0.017 of 0.25. The matching
`sim:ascella` job is admitted (maximum pooled departure 0.0039), so the pipeline closes and the failure belongs to the
device. Per the preregistration the verdict is instrument not admitted, and conformance, mutation, crosstalk and
independence are not interpreted; their raw readings (16 of 16 true arms and 17 of 17 mutation arms within 0.07,
crosstalk excess at most 0.0031, partner ranges 0.044 and 0.050) are descriptive and carry no verdict. The fold is not
admitted at 0.07 on Ascella with per-slot anchors and darks.

The predecessor's C8 spread (+0.047, job `f3a11b5f`) is not reproduced: the contrast reads -0.0162 (slot A) and +0.0051
(slot B) against the 0.0235 threshold, in a run whose instrument is not admitted. The C8 cells carry slot offsets of
opposite sign (slot A cells +0.0057 to +0.0301, slot B cells -0.0524 to -0.0209), the same open cause as the mirror
failure.

Retraction. The mechanism recorded before this analysis, that per-mode efficiencies (fitted 0.926 to 1.055 over modes 0
to 8) shrink the C8 slot cells from up to 0.0524 to at most 0.0061 and that a per-mode calibration would admit the fold, is
withdrawn. It read `c8_spread_under_mode_efficiencies` of `analysis.json`, the spread that the efficiency model itself
predicts, as if it were corrected data. The model predicts a mirror difference with median 0.0026 and maximum 0.0155
against 0.0259 and 0.1082 observed, flags none of the 9 failing pairs, and does the same when fitted on orientation 0
only (maximum 0.0167); `mirror_test.txt` holds the numbers and `c1_observed.txt` the observed distribution. Nine
single-mode anchors are not the remedy.

Result of the mechanism probes (`c1_*.txt`): counting statistics, drift, multiphoton events and count rate are refuted
or unsupported; the failure count follows the per-slot anchor calibration. The anchors give B/A 1.082 against about
0.99 from the mode fit over all iterations; with no efficiency division or equal efficiencies 1 of the 46 pairs fails,
with the mode-fit slot sums 0, below the allowance of 4 (`c1_anchor.txt`). White phase error of 0.033 rad per shifter reproduces the
observed rms (0.0488) and the gain term of the slot model at z +1.4, and the error is static per configuration
(predicted repeat-pair rms 0.0189 against 0.0024 observed, `c1_predecessor.txt`). The equalized analysis is a diagnostic
on this job's own iterations and does not readmit the instrument.

hypothesis: the two anchor meshes carry a phase error that the per-slot calibration spreads into every level, and a
static residual of rms 0.024 (about 0.02 rad per shifter) remains. Confidence 0.55; the finding that per-mode
efficiencies do not explain the failure stands at 0.9. Several anchor configurations (compilation seeds) per slot whose B/A scatters by about 0.09
raise it, anchors that agree near 1.08 lower it, and failing settings replayed at identical configuration reproducing
the difference within 0.005 test the static-error form.

## Conjecture results

| Conjecture | Verdict | Confidence | Next measurement |
|---|---|---|---|
| C1: the mirror failure is not per-mode efficiency; its cause is a configuration-specific phase error | not per-mode efficiency survives; the anchor calibration dominates the failure count and a phase error is the residual | 0.9 and 0.55 | anchor configurations per slot; replay of failing settings at identical configuration |
| C2: the positive null offset is a cross-platform systematic | refuted for the Tuna-17 selector contrast, which a coherent X90 over-rotation of +0.03 rad reproduces; the ibm_fez N_hat offset is estimator plus readout | 0.75 and 0.8 | Tuna-17 1-CZ null block added to the coin design; 20-CZ k0-type null block on at least 17 IBM placements with the 1-CZ blocks |
| C3: the `ba` misses come from a per-template coupling set by routing | refuted; the pattern follows the logical bit d2 and gate-level noise on the compiled structure explains part of it | 0.75 and 0.5 | the template on a graph-automorphic placement; joint four-state readout of the routed d0 and d2 qubits |

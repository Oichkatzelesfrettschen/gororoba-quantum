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
of the null block (the coin design at 21 CZ and the stopped series at 20 CZ) respond to a single X90 over-rotation with
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
against 0.0259 and 0.1082 observed and leaves a residual rms of 0.0461 against 0.0488 (about a tenth of the variance
explained), flags none of the 9 failing pairs, and does the same when fitted on orientation 0 only (maximum 0.0167); `mirror_test.txt` holds the numbers and `c1_observed.txt` the observed distribution. Nine
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
| C2: the positive null offset is a cross-platform systematic | refuted for the Tuna-17 selector contrast, which a coherent X90 over-rotation of +0.03 rad reproduces; the ibm_fez N_hat offset is estimator plus readout | 0.75 and 0.8 | Tuna-17 1-CZ null block added to the coin design; 20-CZ k0-type null block on at least 17 IBM placements with the 1-CZ blocks (run 2026-11-07 on 17 and 16 placements, see the section below) |
| C3: the `ba` misses come from a per-template coupling set by routing | refuted; the pattern follows the logical bit d2 and gate-level noise on the compiled structure explains part of it | 0.75 and 0.5 | the template on a graph-automorphic placement; joint four-state readout of the routed d0 and d2 qubits |

# Parallel coset blocks on ibm_fez and ibm_kingston (2026-11-07)

This section scores the two parallel coset-block runs of the written case
[2026-11-07T035554.327341Z/CASE.md](2026-11-07T035554.327341Z/CASE.md) (group `pathion_parallel_coset`, 111 four-qubit
circuits plus live_run's isolated reference, one fused PUB per circuit over every placement). ibm_fez, backup account:
run [2026-11-07T042521.359670Z](2026-11-07T042521.359670Z/collect.json), job `dbnai2oqtr0c73acl9gg`, 17 placements, 57 s
charged; acquisition `ibm-fez-pathion-parallel-coset`. ibm_kingston, primary account: run
[2026-11-07T042346.084449Z](2026-11-07T042346.084449Z/collect.json), job `dbnahh5t7fqc73aj7bdg`, 16 placements, 32 s
charged; acquisition `ibm-kingston-pathion-parallel-coset`. Registry claim: `hw-ibm-pathion-parallel-coset`. The
script `scripts/pathion_parallel_coset_analysis.py` applies every preregistered rule in the case's order, with Student t
intervals at 95 percent over the placements and each placement's model value taken from the approved dry run of the
record (`prediction_reuse.approved_record`); it writes [pathion_parallel_coset_analysis.json](pathion_parallel_coset_analysis.json),
which holds every number below. Its per-placement summaries and per-placement readout-corrected summaries (each
placement's own confusion matrices, the measured qubit of each clbit read from `isa.qpy`) reproduce the collector's
`measured_statistics` and `measured_summary_readout_corrected` to below 5e-7.

The runs differ from the approved case in four recorded facts, and the bands stay as the case wrote them: ibm_fez ran
16,384 shots per member (case: 14,336) under a 65 s ceiling (case: 60 s), ibm_kingston ran 8,192 shots under a 42 s
ceiling (case: 40 s), the models are the approved dry runs `2026-11-07T041623.255956Z` and `2026-11-07T041624.522872Z`
(case prose: `035554.327341Z` and `040239.842834Z`; ibm_fez model calibration 2026-11-06T19:35:16-08:00 against the
executed 20:05:31-08:00). The case's cost model reproduces the ibm_fez charge of 57 s at 16,384 shots with a residual of
6.9 us per execution (6.6 to 7.2 us after integer-second rounding; retained runs 6.6 to 7.1 us) and the ibm_kingston
charge of 32 s with 8.7 us (8.1 to 9.2 us; the case priced 9.0 us). The model N_hat per operand on ibm_fez differs from
the case prose by at most 0.01 (0.122 against 0.12, 12.169 against 12.17).

| Rule | ibm_fez | ibm_kingston |
|---|---|---|
| resolution (32 of 32 pooled signs; block visibility above 0.5) | PASS | PASS |
| nullity bands (N_hat within 0.5 of the model; corrected within 0.15 of the integer) | PASS | PASS |
| null selector contrast (two standard errors and 0.006) | FAIL (k8 base) | FAIL (k8 flip) |
| null N_hat per placement (1-CZ blocks within +-0.02) | UNINFORMATIVE | FAIL |
| odd part O within +-0.04 of the model | UNINFORMATIVE | FAIL |
| even part E within +-0.03 of the model | UNINFORMATIVE | PASS |
| placement spread (slope in [0.7, 1.3], R squared above 0.5) | FAIL | FAIL |
| within-arm repeats (two standard errors and 0.02) | PASS | FAIL (within plus) |
| parallel crosstalk (90 percent interval inside +-0.015) | PASS | PASS |
| four-term blocks B12 and C8 | PASS | PASS |
| devices (N_hat agree; odd and even pass against each model) | FAIL | |

## Resolution, nullity and the devices

Both devices read all 32 per-output signs on every one of the eight operands in the pooled map (and on every
placement), and the lowest block visibility interval is [0.658, 0.773] (ibm_fez, e1 + e24, coset 8) and [0.770, 0.827]
(ibm_kingston, e1 + e10, coset 0), above the 0.5 floor. The N_hat of the six operands, the twin and the cocycle-free
control covers each model value within 0.5, and the readout-corrected values lie within 0.15 of the integer nullity:
ibm_fez 0.009, 4.074, 4.027, 8.006, 11.981, 11.973, twin 11.974, cocycle-free -1.943 and ibm_kingston -0.077, 4.082,
4.081, 7.964, 11.985, 12.008, twin 12.010, cocycle-free -1.958 (nullities 0, 4, 4, 8, 12, 12, 12, -2). The compiled sign
network agrees with `cd_core` on every operand of both devices. The two devices' N_hat agree within the sum of their
intervals on all eight operands (largest difference 0.049 on e1 + e17 against 0.198 allowed), so the devices rule fails
only through the odd-part band of ibm_kingston and the unresolved bands of ibm_fez below.

## Null selector contrast

The k0 selector contrast of the null operand, the observable that a coherent sx over-rotation raises by 0.57 per rad,
reads -0.0020 +- 0.0015 on ibm_fez and -0.0000 +- 0.0011 on ibm_kingston (flip twin +0.0015 +- 0.0021 and +0.0009 +-
0.0021), and the 1-CZ blocks k4, k8, k12 read +0.0008, -0.0028, -0.0004 (ibm_fez) and +0.0019, -0.0007, -0.0015
(ibm_kingston). The rule fails as written on each device through one block: ibm_fez k8 reads -0.0028 +- 0.0014, which
exceeds two standard errors by 0.00001, and the ibm_kingston k8 flip twin reads -0.0048 +- 0.0023 (2.1 standard errors).
The sx over-rotation signature (k0 above +0.006 with the 1-CZ blocks at zero) is absent on both devices. Both
excursions are negative, 2 of 16 tests exceed two standard errors where chance gives 0.8, and the one-sided band
(+0.006) is far from both, so `hypothesis:` the two FAILs are the tail of 16 independent tests and carry no mechanism;
the per-block k8 values are the first thing a repeat run would check. `d1_ibm_overrotation.txt`: the implied angle is
-0.0036 +- 0.0027 rad (ibm_fez) and -0.0000 +- 0.0019 rad (ibm_kingston), 4.4 and 4.1 combined standard errors below
the Tuna-17 coin angle +0.0295 +- 0.0070 rad (12.4 and 15.3 against the IBM error alone); with the earlier ibm_fez and
ibm_marrakesh angles the four IBM readings pool to -0.0015 +- 0.0014 rad (chi2 1.60 on 3 degrees of freedom), 4.3
combined standard errors below the Tuna angle with a 95 percent upper bound of +0.0013 rad. IBM excludes the Tuna-17
angle at more than 3 sigma on every reading; the scope is the case's 0.57 per rad response, which no ibm_kingston
compile confirmed.

## Null N_hat and the odd and even decomposition

The retained ibm_marrakesh 1-CZ null blocks read +0.045 after the pooled readout correction. With each placement's own
confusion matrices the readout-corrected N_hat of k4, k8, k12 reads +0.0057, +0.0045, +0.0070 on ibm_fez (standard
errors 0.022 to 0.024, 95 percent half-width 0.045, so the rule is UNINFORMATIVE and the intervals span +0.045) and
-0.0283, -0.0313, -0.0297 on ibm_kingston (standard errors 0.010, FAIL: below -0.02, opposite in sign to ibm_marrakesh,
and each mean lies 7.3 to 8.0 standard errors below +0.045; `d2_null_offset.txt`). The raw means are +0.030, +0.027,
+0.031 and +0.009, +0.007, +0.008, so the correction moves ibm_kingston below zero: its flip twin reads +0.031, +0.035,
+0.026 after correction, the mirror image. The odd part O of the null operand's N_hat measures +0.0888 (model +0.1151,
paired -0.0263 +- 0.0629) on ibm_fez and +0.0501 (model +0.1349, paired -0.0848 +- 0.0302) on ibm_kingston, and the even
part E +0.0244 (model +0.0067, paired +0.0177 +- 0.0145) and +0.0138 (model -0.0040, paired +0.0178 +- 0.0128). The
signature table selects, on ibm_kingston, readout asymmetry after the X below its calibrated size (row 1, O under the
band by 0.045 beyond the band edge) with relaxation and residual excitation at the model's size (row 2, E inside the
band), and flags the within-arm repeat below; on ibm_fez it selects the same two rows with O and E unresolved (95
percent half-widths 0.133 and 0.031 against bands 0.04 and 0.03). The placement spread fails on both devices: slope
+1.23 (95 percent [-0.02, +2.49]) with R squared 0.227 on ibm_fez and +0.26 ([-0.13, +0.66], R squared 0.130) on
ibm_kingston, where the case expected a slope standard error of 0.12 and the runs give 0.59 and 0.18, so the per-placement
O carries more sampling variance than the case assumed (ibm_fez placements 13 and 15 read O +0.50 and +1.08, placement 9
reads E +0.23). Exploratory sensitivity, not a verdict: dropping the three ibm_fez placements beyond 3.5 robust sigma
on paired O or paired E (placements 9, 13, 15) moves the paired O to -0.1012 +- 0.0320, the same sign and size as
ibm_kingston, and E to +0.0065 +- 0.0087. The odd part of the ideal laws pushed through the executed confusion matrices
alone is +0.1394 (ibm_kingston) and +0.1101 (ibm_fez), within 0.005 of the dry-run model's +0.1349 and +0.1151, so a
calibration change between the dry run and the run does not explain the shortfall: measured minus this readout-only
part is -0.0893 +- 0.0290 (ibm_kingston) and, without the three placements, -0.0976 +- 0.0301 (ibm_fez).
`hypothesis:` the calibrated confusion matrix overstates the readout asymmetry that the circuits see by about 0.09 on the
operand total (0.085 +- 0.030 on ibm_kingston, 0.10 +- 0.03 on ibm_fez without three placements), which makes a
calibration-based correction overcorrect the null operand; confidence 0.5. A readout-calibration arm on the same
placements (the four qubits prepared 0 or 1 and read, with and without the X) measures the in-circuit asymmetry directly and
decides it. The ibm_marrakesh +0.045 does not recur: ibm_kingston excludes it and ibm_fez does not resolve it.

## Within-arm repeats and packing

The within-arm repeats of the null operand read +0.0004 +- 0.0063 (minus), +0.0068 +- 0.0048 (plus) and a pair gap of
+0.0064 +- 0.0069 on ibm_fez (PASS) and +0.0031 +- 0.0076, +0.0127 +- 0.0047 and +0.0096 +- 0.0090 on ibm_kingston. The
ibm_kingston plus repeat exceeds two standard errors (2.7) at a size below 0.02, so the rule fails as written and marks a
small position or drift effect inside the plus arms; `hypothesis:` it is one of six tests and the size is well below the
0.02 band. Packed against isolated replica 0 of the k0 minus arm, the 90 percent Newcombe-Wilson interval reads -0.0042
[-0.0090, +0.0007] on ibm_fez (16,384 shots, half-width 0.0048) and -0.0018 [-0.0082, +0.0046] on ibm_kingston (8,192
shots, half-width 0.0064), recomputed from the raw shot lists (`d3_crosstalk.txt`) and equal to the collector's
interval: inside the +-0.015 band on both, which shows no crosstalk at the one-hop separation with 17 and 16 placements
active. Both differences are negative (inverse-variance mean -0.0033 +- 0.0023, 90 percent interval [-0.0071,
+0.0005]), the earlier 8,192-shot runs read +0.0011 and +0.0059, and the interval half-width matches the case's
prediction.

## Four-term blocks and Ascella

B12 (coset 2) and C8 (coset 5) pass every four-term rule on both devices. Visibility reads 0.799 [0.761, 0.838] (B12)
and 0.754 [0.715, 0.794] (C8) on ibm_fez and 0.849 [0.826, 0.873] and 0.825 [0.790, 0.859] on ibm_kingston, where the
dry-run models read 0.87 to 0.91, so the model overpredicts the visibility by 0.06 to 0.11. The closures of F, E0, E1,
D2 and N differ from the model's by at most 0.0184 in magnitude (N of B12 on ibm_fez) and the closure of C lies 0.009 below the
model's on every block, all inside 0.03; the separations T - F, T - C, T - N read 0.405, 0.636, 0.176 (B12) and 0.443, 0.531,
0.163 (C8) on ibm_fez and 0.425, 0.667, 0.183 and 0.484, 0.567, 0.180 on ibm_kingston, each above half its ideal; the E0
and E1 levels sit within 0.0122 of the model's. `d4_four_term.txt` normalizes each IBM placement with the dark arm D as
zero and the basis arms E0 and E1 (ideal 1/4) as the scale, so T keeps its own reading, and compares with the Ascella
readings of A5-188 on arms of equal ideal level: T reads 0.727 and 0.726 (B12; Ascella 0.7495, ideal 0.75) and 0.649 and
0.658 (C8; Ascella 0.642, ideal 0.6545), F 0.236 and 0.242 (Ascella 0.2496), N 0.512 and 0.518 (B12; Ascella 0.538, ideal
0.5625); the largest gap to Ascella is -0.045 (ibm_fez) and -0.033 (ibm_kingston) on the B12 C arm, which reads -0.047 and
-0.035 on IBM; every matched arm lies within 0.07 of the other platform and of its ideal. The C8 C arm is not run: no
Ascella C8 block carries its ideal level 0. `hypothesis:` the negative C level on IBM follows the dark arm's depth: D
routes to 18 CZ and reads 0.057 and 0.044 where C (8 CZ) reads 0.021 and 0.014, so the D-based zero over-subtracts at
low depth.

## Bearing on the ledger rows

A5-185 (the Tuna-17 null block reads selector contrast 0, and its ratios agree with IBM) stays refuted; its IBM
comparator reads zero again on two more devices (k0 selector contrast -0.0020 and -0.0000). A5-186 (a coherent X90
over-rotation of about +0.03 rad on Tuna-17, which IBM does not show) keeps its confidence of 0.75 for the over-rotation
and rises to 0.9 for the IBM half: four IBM readings pool to -0.0015 +- 0.0014 rad, 4.3 combined standard errors below
the Tuna angle; the decisive Tuna-17 1-CZ null block is still owed. A5-188 (qpu:ascella realizes the pathion 4 x 4
coset blocks within 0.07) gains an independent platform: the same B12 and C8 block classes on ibm_fez and ibm_kingston
agree with the Ascella readings within 0.046 on every matched arm. The new rows A5-192 to A5-199 of
`docs/evidence/a5-exceptional-fibers/ledger.tsv` record the nullity result (survives), the IBM selector contrast
(survives), the 1-CZ null band (refuted on ibm_kingston), the calibrated odd part (refuted), the overstated-asymmetry
hypothesis (survives at 0.5), the within-arm repeat (refuted on ibm_kingston), packing (survives) and the four-term
agreement (survives).

# Ascella mesh persistence: what failed the two-block mirror test (2026-11-07)

The [mesh-persistence case](../../docs/design/ascella-pathion-mesh-persistence-case.md) replayed the 52 settings of the
two-block job (`db6355f7`) on `qpu:ascella` with their original seeds and circuit parameters, added seven fresh anchor
seeds, the eight failing settings at fresh seeds and a fresh dark, and read the result against preregistered decisions
([reading](../../scripts/ascella_pathion_mesh_persistence_analysis.py), [runbook](../../docs/runbooks/ascella-block-run-design.md)).
Runs: `sim:ascella` gate `86cc1405`
([run](../quandela/runs/2026-11-07T181127Z-sim_ascella-ascella_pathion_mesh_persistence-sim-00/analysis.json)) and
`qpu:ascella` job `6bc382af`, 84 iterations, 11,010,048 samples
([run](../quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00/analysis.json)).
Registry claim: `hw-ascella-pathion-mesh-persistence`.

Mesh identity. The simulator gate served all 52 replay meshes identical to the original simulator run (largest gap
0.0); three requests (a-h-CC o1, a-h-NN o0, b-f-EE o0) compile to different meshes on `sim:ascella` and `qpu:ascella`,
in the original jobs and again here, so the gate was amended before the QPU job to compare simulator with simulator
(case document, "Amendment after the simulator run"). The QPU job then served all 52 replay meshes identical to the
original QPU job, so no design left the reading (A5-204).

Persistence. The 46 calibrated mirror differences of the replay correlate with the original job's at r 0.9966 against
the fixed-mesh cutoff 0.988 (relabeling p 5e-5; raw levels r 0.979), and the same 9 of 46 exceed 0.07. The replayed
anchor pair reads B/A 1.0876 against 1.082. Within the job the early and late replay halves read r 0.994 and 0.996 and
the replayed anchors 1.027 and 1.028, so no drift enters. A per-mesh table from the original job leaves 0 of 46 above
0.07 (rms 0.0486 to 0.0040); that table subtracts each mesh's departure from its ideal level, so it shows persistence
and does not validate any block level. Admission passes: anchors 1.007 and 1.048, darks 0.0010 and 0.0007, sentinel
share 0.0009 (A5-200).

Fresh meshes. The nine failing items at fresh seeds give an aligned mean of -0.0024 against the original 0.0376 (rule:
below 0.0181 the failure follows the mesh), carried fraction -0.06 with 99 percent interval [-0.64, 0.51]: the failure
does not follow the block or slot design (A5-201). Seven fresh anchor seeds give B/A 0.84 to 1.05 (median 0.951, sd
0.067), none within 0.03 of 1.082; the preregistered anchor rule reads "unresolved" because the median falls 0.041
below the mode-fit band, and a slot efficiency of 1.08 is excluded (A5-203). hypothesis: the mode-fit 0.992 is itself a
mixture of mesh errors, so the center of the anchor-ratio distribution is near 0.95 rather than 0.99.

Static map. The per-shifter gain map frozen from the original job (`c1_static.npz`, commit cc8d8107c) predicts the
fresh iterations' raw departures at r 0.446 with seed-block relabeling p 0.0016, share 0.20 of the resolvable variance;
the offset map reads r 0.444, p 0.011, above the preregistered 0.005 (A5-202). The gain map is a partial carrier of the
order the signed-coherence program measured on its own family's unseen meshes (shares 0.025 to 0.105 there).

Consequence for the pathion block cases. Each served mesh carries a fixed error of rms about 0.025 in level that a
seed-specific table removes, and one anchor mesh per slot puts that mesh's error into every reading of its slot. A
block case that folds several blocks per photon calibrates its slots from many anchor seeds or a per-mesh table, and a
block level is admitted only after that calibration; the
[runbook](../../docs/runbooks/ascella-block-run-design.md) carries the rules and the open questions.

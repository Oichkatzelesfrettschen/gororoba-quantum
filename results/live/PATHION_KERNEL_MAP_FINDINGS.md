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

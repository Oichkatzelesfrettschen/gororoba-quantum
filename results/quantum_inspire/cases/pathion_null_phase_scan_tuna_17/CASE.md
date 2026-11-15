# Case: Tuna-17 selector offset of the null block against injected phases at coupler 8-12

Status: written case awaiting its review and the owner's approval; nothing has been submitted, on the emulator or
on hardware. Generator and checker: `scripts/qi_pathion_null_phase_scan_cases.py` (`--check
results/quantum_inspire/cases` reproduces every file of this directory except this one, and the QX twin
`../pathion_null_phase_scan_qx/`). Ledger row: A5-186. Predecessor: the injected-rotation scan
([case](../pathion_null_rotation_scan_tuna_17/CASE.md), verdict `unresolved_none`) and its exploratory reading
([tuna17-null-rotation-scan-line-phase.md](../../../../docs/notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md)),
whose [draft](../../../../docs/notes/quantum_inspire/tuna17-null-phase-scan-case-draft.md) this case builds.

## What the run measures

Terms. Each shot reads five bits on the region's qubits: the coin (q2), the selector (q8) and three data bits d0
(q12), d1 (q4) and d2 (q11). The selector contrast is P(selector 0 | coin 1) - P(selector 0 | coin 0), and the d2
split is that contrast among shots with d2 = 1 less the one among d2 = 0. The visibility is the size of the
contrast inside the bins of d0 and d1, where b0's ideal law gives +-1. The fit models the device's loss by a noise
model: a contraction (a retention r mixes the ideal law toward the uniform one, and the contraction share says how
much of that loss falls on the data bits alone) or CZ damping (amplitude and phase damping on both qubits after
every CZ) with a uniform contraction on top.

The null block b0 (21 routed CZ on q2, q4, q8, q11, q12; 49 pulses: 34 on q8, 8 on q4, 5 on q12, 1 on q2, 1 on
q11) reads a raw selector contrast of +0.0145 +- 0.0010 over the eleven center circuits of the predecessor, where
exact gates give 0. The predecessor varied pulse amplitudes, and none of its preregistered worlds fits (least
chi-square 234.5 against 37.70). In the exploratory reading two elementary errors outside those worlds lead: a
rotation about z before each pulse of q12 and a conditional-phase error of the CZ gates of coupler 8-12
(chi-square 205 and 187 with one parameter per batch). Neither is adequate, and with exact pulses both give a
contrast that is even in the error, so the retained offset fixes a size near 0.18 rad for the q12 phase and leaves
its sign open.

This case injects known phases on both sides of coupler 8-12. An `Rz(phi)` before each of q12's five pulses (the
z12 arms) adds phi to the phase that precedes that pulse: under a phase theta on q12 the contrast against phi is
the exact curve shifted by -theta and reads zero at phi = -theta. An `Rz(phi)` on q8 after each of the four CZ
gates of coupler 8-12 (the z8c arms) acts on the selector's side of the coupler, where the q12 and coupler worlds
differ most: at the expected values below the z8c batches alone separate them by 66 to 190 in chi-square. The same
arms fit a third error world, a phase on q8 after each CZ of coupler 8-12, which without its own world reads as the
coupler's phase near +0.1 and -0.17 rad. With exact gates the z12 curve is even in phi and reads zero at phi = 0,
so a static offset of another origin adds a constant.

Schedule. The provider lists `Rz` as a native operation and gives native single-qubit gates 20 ns under
as-late-as-possible scheduling (`docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md`), so an
added `Rz` may cost time. Every arm of a data batch, and the bridge's padded center, therefore carries the same
nine `Rz` at the same places, at angle 0 where the arm injects nothing, and the arms differ in angles alone.
OpenSquirrel 0.9.1, the platform's compiler, keeps `Rz(0.0)` as its own instruction
(`docs/evidence/quantum_inspire/toolchain-token-recovery.json`:
the compiled padded center holds its four q8 and five q12 zero-angle `Rz`, and the compiled text differs from the
source by angle rounding alone), and its scheduler exporter gives every `Rz`, zero angle included, one 20 ns
cycle. hypothesis: the control stack after the compiler keeps the zero-angle `Rz` too. The two bridge batches
hold the predecessor's unpadded center (`b0-rx`, twice) beside the padded center (`b0-rxz`) and measure what the
padding changes.

Predicted raw selector contrast per arm at the retention where the center reads visibility 0.42, contraction
share 0, through the mean bracket readout of the predecessor (`prediction.json`, `truths`). "CZ damping" is
amplitude 0.019 and phase 0.031 per CZ qubit, the values that took the predecessor's full-histogram chi-square
from 182,795 to 51,767 on 925 degrees of freedom in an exploratory refit; "x1.25" and "x3" scale both. The rows
with "phase damping" put pure phase damping of that size on each qubit after every CZ or every pulse, outside the
fit's noise models. A truth whose noise keeps the center below visibility 0.42 at every retention is taken at the
largest visibility it reaches. The last column is the readout flip at which the label's world fits (rule 3).

<!-- generated from prediction.json by scripts/qi_pathion_null_phase_scan_cases.py: truths -->
| truth | center | q4 -10 | q4 -5 | q4 +5 | q4 +10 | z12 -30 | z12 -10 | z12 +10 | z12 +30 | z8c -10 | z8c +10 | label | fitted flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coupler 8-12 phase +0.25 rad | +0.0204 | +0.0035 | +0.0118 | +0.0285 | +0.0353 | +0.0551 | +0.0111 | +0.0503 | +0.1315 | +0.0001 | +0.0502 | `coupler_phase` | 0 |
| coupler 8-12 phase -0.25 rad | +0.0157 | +0.0305 | +0.0236 | +0.0075 | -0.0001 | +0.1635 | +0.0546 | +0.0036 | +0.0656 | +0.0417 | -0.0014 | `coupler_phase` | 0 |
| coupler 8-12 phase -0.25 rad with CZ damping | +0.0139 | +0.0297 | +0.0223 | +0.0052 | -0.0028 | +0.1509 | +0.0498 | +0.0033 | +0.0634 | +0.0413 | -0.0030 | `coupler_phase` | 0 |
| coupler 8-12 phase -0.25 rad with CZ damping x1.25 | +0.0114 | +0.0250 | +0.0187 | +0.0039 | -0.0031 | +0.1252 | +0.0411 | +0.0028 | +0.0534 | +0.0350 | -0.0029 | `coupler_phase` | 0 |
| coupler 8-12 phase -0.25 rad, selector flip 0.036 | +0.0319 | +0.0454 | +0.0393 | +0.0238 | +0.0160 | +0.1696 | +0.0682 | +0.0210 | +0.0807 | +0.0554 | +0.0157 | `coupler_phase` | 0.035 |
| exact gates | 0 | 0 | 0 | 0 | 0 | +0.0911 | +0.0127 | +0.0129 | +0.0954 | +0.0032 | +0.0095 | `offset_absent` | - |
| exact gates with CZ damping | -0.0001 | +0.0001 | 0 | -0.0001 | -0.0002 | +0.0936 | +0.0130 | +0.0132 | +0.0980 | +0.0038 | +0.0106 | `offset_absent` | - |
| exact gates, selector flip 0.0166 when q12 reads 0 | +0.0073 | +0.0070 | +0.0072 | +0.0072 | +0.0070 | +0.0955 | +0.0196 | +0.0200 | +0.1004 | +0.0102 | +0.0164 | `exact_parabola` | 0.0175 |
| exact gates, selector flip 0.0166, CZ phase damping 0.10 | +0.0054 | +0.0056 | +0.0056 | +0.0051 | +0.0047 | +0.0782 | +0.0176 | +0.0115 | +0.0657 | +0.0107 | +0.0098 | `exact_parabola` | 0.0175 |
| exact gates, selector flip 0.025, CZ phase damping 0.13 | +0.0058 | +0.0060 | +0.0060 | +0.0055 | +0.0051 | +0.0595 | +0.0154 | +0.0091 | +0.0456 | +0.0105 | +0.0082 | `exact_parabola` | 0.025 |
| exact gates, selector flip 0.025, pulse phase damping 0.10 | +0.0054 | +0.0055 | +0.0056 | +0.0052 | +0.0049 | +0.0516 | +0.0124 | +0.0109 | +0.0496 | +0.0076 | +0.0090 | `exact_parabola` | 0.025 |
| exact gates, selector flip 0.036 when q12 reads 0 | +0.0162 | +0.0155 | +0.0160 | +0.0160 | +0.0155 | +0.1010 | +0.0279 | +0.0286 | +0.1065 | +0.0186 | +0.0249 | `exact_parabola` | 0.035 |
| exact gates, selector flip 0.036, CZ phase damping 0.16 | +0.0059 | +0.0061 | +0.0061 | +0.0057 | +0.0053 | +0.0452 | +0.0135 | +0.0074 | +0.0311 | +0.0099 | +0.0070 | `exact_parabola` | 0.0375 |
| q12 phase +0.18 rad | +0.0141 | +0.0031 | +0.0086 | +0.0194 | +0.0237 | +0.0469 | 0 | +0.0511 | +0.1465 | +0.0060 | +0.0339 | `q12_phase` | 0 |
| q12 phase -0.15 rad | +0.0099 | +0.0190 | +0.0148 | +0.0049 | +0.0001 | +0.1331 | +0.0429 | +0.0003 | +0.0569 | +0.0261 | +0.0063 | `q12_phase` | 0 |
| q12 phase -0.15 rad with CZ damping | +0.0097 | +0.0201 | +0.0153 | +0.0039 | -0.0014 | +0.1308 | +0.0421 | +0.0002 | +0.0559 | +0.0262 | +0.0072 | `q12_phase` | 0 |
| q12 phase -0.15 rad with CZ damping x1.25 | +0.0081 | +0.0171 | +0.0129 | +0.0031 | -0.0015 | +0.1092 | +0.0352 | +0.0002 | +0.0467 | +0.0220 | +0.0063 | `q12_phase` | 0 |
| q12 phase -0.15 rad with CZ damping x3 | +0.0020 | +0.0052 | +0.0037 | +0.0002 | -0.0015 | +0.0289 | +0.0091 | +0.0001 | +0.0132 | +0.0060 | +0.0024 | `offset_absent` | - |
| q12 phase -0.18 rad | +0.0144 | +0.0254 | +0.0203 | +0.0082 | +0.0024 | +0.1420 | +0.0512 | 0 | +0.0499 | +0.0338 | +0.0075 | `q12_phase` | 0 |
| q12 phase -0.18 rad, selector flip 0.036 | +0.0305 | +0.0404 | +0.0361 | +0.0244 | +0.0183 | +0.1488 | +0.0648 | +0.0173 | +0.0647 | +0.0483 | +0.0234 | `q12_phase` | 0.035 |
| q8 phase at coupler 8-12 +0.10 rad | +0.0041 | -0.0027 | +0.0006 | +0.0074 | +0.0103 | +0.0649 | +0.0079 | +0.0230 | +0.1069 | -0.0002 | +0.0196 | `phase_unresolved` | - |
| q8 phase at coupler 8-12 -0.17 rad | +0.0031 | +0.0130 | +0.0083 | -0.0021 | -0.0068 | +0.1466 | +0.0311 | +0.0055 | +0.0858 | +0.0174 | +0.0001 | `phase_unresolved` | - |
| q8 phase at coupler 8-12 -0.25 rad | +0.0090 | +0.0233 | +0.0166 | +0.0014 | -0.0056 | +0.1794 | +0.0448 | +0.0064 | +0.0864 | +0.0272 | -0.0002 | `q8_phase_at_coupler` | 0 |
| q8 phase at coupler 8-12 -0.25 rad, CZ phase damping 0.12 | +0.0103 | +0.0200 | +0.0155 | +0.0049 | -0.0001 | +0.1121 | +0.0334 | +0.0052 | +0.0432 | +0.0249 | +0.0014 | `phase_unresolved` | - |
| q8 phase at coupler 8-12 -0.25 rad, pulse phase damping 0.10 | +0.0055 | +0.0144 | +0.0102 | +0.0007 | -0.0035 | +0.0888 | +0.0234 | +0.0033 | +0.0397 | +0.0149 | +0.0003 | `phase_unresolved` | - |
| q8 phase at coupler 8-12 -0.25 rad, selector flip 0.042 | +0.0280 | +0.0409 | +0.0351 | +0.0204 | +0.0132 | +0.1878 | +0.0611 | +0.0263 | +0.1025 | +0.0428 | +0.0205 | `q8_phase_at_coupler` | 0.0425 |
<!-- end of generated table -->

The standard error of one contrast at 131,072 shots is 0.0028 and of one d2 split 0.0056. The z8c curve is
asymmetric under exact gates (+0.0032 at -10 degrees, +0.0095 at +10), and its d2 split carries most of the
separation: under the coupler phase of -0.25 rad the z8c arms read d2 splits of +0.040 and -0.007, under a q12
phase of -0.18 rad +0.006 and +0.018. A q8 phase at coupler 8-12, the error the z8c arms inject, is the third
error world of the fit. Without it, q8 phases of -0.17 and +0.10 rad fit the coupler world adequately at 29.4 and
27.4 (readout flip fixed at 0), 69 and 32 below the q12 world, and read `coupler_phase`. With it, q8 phases of -0.25,
-0.17 and +0.10 rad fit their own world at 0 with the coupler world 64.7, 29.4 and 27.4 above; the first reads
`q8_phase_at_coupler`, and the two smaller ones lie within the separation of rule 4 and read `phase_unresolved`.

CZ damping. The fit computes the laws at every multiple of the retained strength from 0 to 3 in steps of 1/16. At
expected values the q12 truth of -0.15 rad reads `q12_phase` from multiple 0 through 2.125 and the coupler truth of
-0.25 rad reads `coupler_phase` from 0 through 1.875 (`coverage.json` in
`docs/evidence/qi-null-phase-scan-decision-probes/`, computed with the readout flip fixed at 0). Stronger damping
reads `phase_unresolved`, and from multiple 2.875 on the q12 truth's center offset falls below the control's
threshold and reads `offset_absent`; no multiple reads a wrong error world. With the flip fitted, the truths at
multiples 1, 1.25 and 3 read the same labels at expected values.

The predecessor's readout world beside exact gates (a selector flip when d0 reads 0) is fitted by rule 3: flips of
0.0166 and 0.036 read `exact_parabola` at expected values with the exact world's flip at 0.0175 and 0.035, the
grid points nearest the truth. With the flip held at 0, as the decision held it before value 12, the exact world
scored 121.9 and 598.3 against its bound and the series read `none_adequate`; so did a true q12 or coupler phase
beside such a flip, in 290 to 300 of 300 exploratory series, which would have made `none_adequate` the likely
reading of a device with both. The flip beside phase damping on every CZ or every pulse reads `exact_parabola`
or `phase_unresolved`, and in the 48 combinations of `nulls.json` (same directory, flip fixed at 0) no error
world. The fitted flip is not a clean readout measurement when a phase is present: under a q12 phase of -0.18
rad the exact world fits its best flip at 0.03, and beside a true flip of 0.036 at the grid's end, 0.06, while
the q12 world takes the flip itself. Rule 4's scaled separation stays: under the unscaled separation of 25, two
flip-and-damping nulls read `q12_phase` in 29 and 48 of 500 series (value 8 of the draw below); at a scaled
separation of 30, one read it once in 500 (value 10, `separation_30_value_10.json`); at 40 none does, with the
flip fixed (value 11) or fitted (value 12). `exact_parabola` beside exact gates without a flip appears at centers
of +0.0023 to +0.0050, 1.0 to 2.3 times the control's threshold of 0.0022 and well below the predecessor's
+0.0145, so the falsifier of the phase reading at the observed offset is `exact_parabola` or `none_adequate`
together with a z12 parabola whose least point sits at phi = 0 (rule 5).

Operating characteristics (`prediction.json`, `operating_characteristics`): 5,000 simulated series per scenario
of exact gates and 500 per other scenario, Gaussian contrasts and d2 splits at the design standard errors, every
batch admitted, a static d2 split of +0.0083 on every circuit, seeded from value 12 of
`docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json`. The last column counts the deciding labels that misread the
scenario (any error world for exact gates and for a mixed scenario, another error world for a single phase) with
the one-sided 95% Clopper-Pearson upper bound on their rate. Value 0 of the same draw calibrated the consistency
margin of rule 4 (at margin 0 a single mechanism read `phase_mixed` in up to 94 of 500 series; at 6.63 in at most
7) and value 9 the separation (`calibration.json` and `separation_calibration.json` in
`docs/evidence/qi-null-phase-scan-decision-probes/`).

<!-- generated from prediction.json by scripts/qi_pathion_null_phase_scan_cases.py: operating_characteristics -->
| scenario | series | label counts | misreading deciding labels (one-sided 95% upper bound) |
|---|---|---|---|
| coupler 8-12 phase +0.25 rad | 500 | `coupler_phase` 493, `none_adequate` 2, `phase_mixed` 2, `phase_unresolved` 3 | 0 (< 0.60%) |
| coupler 8-12 phase -0.25 rad | 500 | `coupler_phase` 496, `none_adequate` 1, `phase_mixed` 3 | 0 (< 0.60%) |
| coupler 8-12 phase -0.25 rad with CZ damping | 500 | `coupler_phase` 491, `none_adequate` 1, `phase_mixed` 8 | 0 (< 0.60%) |
| coupler 8-12 phase -0.25 rad with CZ damping x1.25 | 500 | `coupler_phase` 493, `none_adequate` 1, `phase_mixed` 3, `phase_unresolved` 3 | 0 (< 0.60%) |
| coupler 8-12 phase -0.25 rad, selector flip 0.036 | 500 | `coupler_phase` 499, `phase_mixed` 1 | 0 (< 0.60%) |
| exact gates | 5000 | `exact_parabola` 7, `offset_absent` 4982, `offset_reversed` 11 | 0 (< 0.06%) |
| exact gates with CZ damping | 5000 | `exact_parabola` 1, `offset_absent` 4990, `offset_reversed` 9 | 0 (< 0.06%) |
| exact gates, selector flip 0.0166 when q12 reads 0 | 5000 | `exact_parabola` 4987, `none_adequate` 6, `phase_unresolved` 7 | 0 (< 0.06%) |
| exact gates, selector flip 0.0166, CZ phase damping 0.10 | 5000 | `exact_parabola` 648, `none_adequate` 36, `phase_unresolved` 4316 | 0 (< 0.06%) |
| exact gates, selector flip 0.025, CZ phase damping 0.13 | 5000 | `exact_parabola` 507, `none_adequate` 14, `phase_unresolved` 4479 | 0 (< 0.06%) |
| exact gates, selector flip 0.025, pulse phase damping 0.10 | 5000 | `exact_parabola` 4959, `none_adequate` 6, `phase_unresolved` 35 | 0 (< 0.06%) |
| exact gates, selector flip 0.036 when q12 reads 0 | 5000 | `exact_parabola` 4993, `none_adequate` 2, `phase_unresolved` 5 | 0 (< 0.06%) |
| exact gates, selector flip 0.036, CZ phase damping 0.16 | 5000 | `exact_parabola` 787, `none_adequate` 21, `phase_unresolved` 4192 | 0 (< 0.06%) |
| q12 phase +0.18 rad | 500 | `none_adequate` 2, `phase_mixed` 4, `phase_unresolved` 1, `q12_phase` 493 | 0 (< 0.60%) |
| q12 phase -0.15 rad | 500 | `none_adequate` 2, `phase_mixed` 3, `q12_phase` 495 | 0 (< 0.60%) |
| q12 phase -0.15 rad with CZ damping | 500 | `phase_mixed` 1, `q12_phase` 499 | 0 (< 0.60%) |
| q12 phase -0.15 rad with CZ damping x1.25 | 500 | `none_adequate` 3, `phase_mixed` 3, `q12_phase` 494 | 0 (< 0.60%) |
| q12 phase -0.15 rad with CZ damping x3 | 500 | `exact_parabola` 6, `none_adequate` 1, `offset_absent` 297, `phase_unresolved` 196 | 0 (< 0.60%) |
| q12 phase -0.18 rad | 500 | `none_adequate` 1, `phase_mixed` 4, `q12_phase` 495 | 0 (< 0.60%) |
| q12 phase -0.18 rad, selector flip 0.036 | 500 | `none_adequate` 4, `phase_mixed` 4, `q12_phase` 492 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 +0.10 rad | 500 | `offset_absent` 3, `phase_unresolved` 474, `q8_phase_at_coupler` 23 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 -0.17 rad | 500 | `offset_absent` 52, `phase_unresolved` 419, `q8_phase_at_coupler` 29 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 -0.25 rad | 500 | `none_adequate` 1, `phase_mixed` 4, `phase_unresolved` 55, `q8_phase_at_coupler` 440 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 -0.25 rad, CZ phase damping 0.12 | 500 | `none_adequate` 23, `phase_unresolved` 476, `q8_phase_at_coupler` 1 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 -0.25 rad, pulse phase damping 0.10 | 500 | `none_adequate` 1, `phase_unresolved` 499 | 0 (< 0.60%) |
| q8 phase at coupler 8-12 -0.25 rad, selector flip 0.042 | 500 | `none_adequate` 1, `phase_mixed` 5, `phase_unresolved` 35, `q8_phase_at_coupler` 459 | 0 (< 0.60%) |
| z12 from coupler phase -0.25, z8c from q12 phase -0.18 | 500 | `none_adequate` 456, `phase_mixed` 4, `phase_unresolved` 40 | 0 (< 0.60%) |
| z12 from q12 phase -0.18, z8c from coupler phase -0.25 | 500 | `none_adequate` 500 | 0 (< 0.60%) |
<!-- end of generated table -->

No scenario reads a deciding label that misreads it: 0 in 40,000 series of exact gates (each null's rate below
0.06%) and 0 in 10,000 series of phases and mixed scenarios. Each single q12 or coupler mechanism reads its own
label in 491 to 499 of 500 series, a selector flip of 0.036 or CZ damping up to 1.25 times the retained strength
included. The q8 phase of -0.25 rad reads its own in 440 (459 beside a flip of 0.042); the smaller q8 phases lie
within the separation and read `phase_unresolved` in most series and their own label in 23 and 29. A selector
flip alone reads `exact_parabola` in 4,987 and 4,993 of 5,000; beside phase damping it reads `exact_parabola` or
`phase_unresolved`. Exact gates read `exact_parabola` or `offset_reversed` in 18 and 10 of 5,000, the control's
3-standard-error tails. The last two rows draw the z12 batches from one mechanism and the z8c batches from the
other; they read no deciding label.

### Circuits

Every circuit is the retained b0 text with each `X90` as `Rx(pi/2)`. Angles are multiples of pi/36, the
processor's angle grid.

- `b0-rx`: byte for byte the predecessor's center arm, in the bridge batches alone.
- `b0-rxz`: `b0-rx` with `Rz(0.0)` before each of q12's 5 pulses and on q8 after each of the 4 CZ gates of
  coupler 8-12; the center of every data batch.
- `b0-rxz-z12-m30`, `-m10`, `-p10`, `-p30`: the five q12 `Rz` at -30, -10, +10, +30 degrees.
- `b0-rxz-z8c-m10`, `-p10`: the four q8 `Rz` at -10 and +10 degrees.
- `b0-rxz-q4-m10`, `-m5`, `-p5`, `-p10`: q4's 8 pulses at 80, 85, 95 and 100 degrees. Under q12 phases of
  +-0.15 and +-0.18 rad and coupler phases of +-0.25 rad a straight line through these four recovers the q4 zero
  within 0.49 degrees on either sign (0.485 at a q12 phase of +0.18 rad, against the zero found by root finding);
  the earlier set (-5, +5, +10, +15) missed by up to 2.4 degrees on the positive side.

### Batches

29 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch. Fourteen data batches at 131,072 shots per circuit:

- forward round: bridge [`b0-rx`, `b0-rxz`, `b0-rx`], z12 +-10, z8c +-10, q4 +-5, z12 +-30, q4 +-10,
  z8c +-10, each [minus arm, `b0-rxz`, plus arm];
- mirror round: the same seven in reverse order with the outer arms exchanged.

Each data batch carries its own center, so a drift of the offset between batches (0.001 to 0.020 in the
predecessor) enters no within-batch comparison. The readout batch between the two rounds brackets two z8c batches;
a jump of q11 there drops both batches' d2 splits and keeps their contrasts. The QX twin holds the twelve distinct
circuits in four batches of 3 at 2,048 shots.

## Why simulation cannot answer it

Whether the device carries a phase on q12, a conditional phase on coupler 8-12, or neither is a calibration fact of
Tuna-17 that the provider does not publish. The retained series cannot separate them: it varies pulse amplitudes
alone, both errors fit its contrasts almost equally, and its response is even in the error.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12 (q15 and q13 stay out). QX emulator (type 1)
  for the twin.
- Jobs and shots: 72 jobs in 29 batches, 6,488,064 shots (42 data jobs at 131,072, 30 readout jobs at 32,768),
  every job at or under 131,072 shots. The longest job takes about 80 s against the 300 s job limit.
- Expected time: 60 to 67 minutes of execution (3,626 to 4,019 s), 28 pauses budgeted at the 120 s top step of the
  pause ladder (3,360 s; the series starts at the 30 s step), about 2 hours in all plus queue time. The
  predecessor's 21 batches took 66 minutes. QX twin: 12 jobs of 2,048 shots (24,576 shots) in 4 batches.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  (`docs/notes/quantum_inspire/usage.md`, "Queue rules: the FAQ governs").
- Quota and credits: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this
  account; the ledger snapshot after the predecessor lists its 62 jobs with no charge. Expected credits 0, read
  again from a fresh usage snapshot before the submission.

## Preregistered decision rules

`cases.json` of every batch carries these rules (`preregistered`); `decide()` applies rules 1 to 4. The
deciding kinds are z12-10, z12-30 and z8c-10.

1. Admission. A data batch is admitted when e01 and e10 of each qubit the contrast reads (q12, q4, q8, q2)
   change by at most 0.02 between the readout batch before it and the one after. Its d2 splits enter the fit only
   when d2's qubit (q11) passes the same bound; otherwise the batch is fitted on its three contrasts. The
   decision needs an admitted batch of each deciding kind; otherwise `unresolved_guard`. Applied to retained
   brackets, the four-qubit guard admits 10 of 10 data batches of the predecessor and 19 of 19 bracket pairs of
   the one-CZ series; q11 passes in 10 of 10 and in 15 of 19 (its e10 moved by up to 0.34 there).
2. Control. The inverse-variance mean of the center contrast over the admitted batches exceeds 3 standard errors;
   otherwise `offset_absent` (within) or `offset_reversed` (below).
3. Fit. For each of four worlds (exact gates, a rotation about z before each pulse of q12, a conditional-phase
   error of the CZ gates of coupler 8-12, a rotation about z on q8 after each CZ of coupler 8-12) one parameter per
   admitted deciding batch is fitted to its three contrasts and to the d2 split of each outer arm less its center
   arm's, at the retention that reproduces the batch's center visibility through its own bracket readout; a noise
   model whose center reaches no visibility within 0.0083 (3 over the square root of 131,072 shots) of the batch's
   does not fit that batch. The chi-squares are summed at the one noise model and readout flip that make the sum
   least. The noise models are the predecessor's 13 contraction shares, or CZ damping at multiples 0 to 3 of the
   retained strength in steps of 1/16. The readout flip is the probability that the selector reads flipped when
   d0 (q12) reads 0, the predecessor's readout world, which the bracket circuits (all inputs 0, all inputs 1) do
   not measure; it is composed onto each batch's bracket readout, takes one value from 0 to 0.06 in steps of
   0.0025 per series and world, and a tie keeps the smaller. A world is adequate when its sum is at most the upper
   0.001 point (the 99.9th percentile) of chi-square with one degree of freedom per fitted value (5 per deciding
   batch, 3 when its d2 splits are left out), less one per fitted parameter, one for the noise model and one for
   the readout flip: 70.70 (exact) and 59.70 (error world) for eight whole batches.
4. Labels. `exact_parabola`: the exact world is adequate, so a phase on or around q12 is falsified as the cause of
   the offset. `q12_phase`, `coupler_phase` or `q8_phase_at_coupler`: that world has the least sum, is adequate,
   lies below every other error world by at least the separation, and each deciding kind, summed over its admitted
   replicates, reads it at or below the upper 0.001 point on its own degrees of freedom (26.12 for the two-batch
   z12 kinds, 39.25 for z8c) and at most 6.63 above every other error world. The separation is 40 times the larger
   of 1 and the least sum per degree of freedom (30 for eight whole batches): a world that fits worse than the
   sampling noise allows must lead by more, as the errors would be scaled by the square root of that ratio.
   `phase_mixed`: the sums prefer one error world and a kind does not. `phase_unresolved`: an error world is
   adequate and the least lies closer than the separation to another. `none_adequate`: no world is adequate. The
   labels are tested in this order, so each series reads exactly one.
5. Reported beside the label, outside it: the fitted parameter, noise model and readout flip of each world, and
   the worlds whose flip lies at the grid's end, 0.06, where the excess of a larger flip is outside the fit; the
   injected phase of least
   contrast from weighted parabolas through the z12 arms and their centers and through the z8c arms and their
   centers; the d2 split of every arm of the deciding kinds pooled over the replicates whose d2 qubit passed its
   guard; each arm's visibility over its center's beside the exact circuit's ratio.
6. Bridge, outside the label: the padded center's contrast less the mean of the two plain arms in each admitted
   bridge batch, pooled, and whether it lies within 3 standard errors of zero.
7. q4 line, outside the label: a weighted straight line through the origin of the contrast of each q4 arm less
   its batch center against q4's injected angle (-10, -5, +5, +10 degrees), with its chi-square, its slope and the
   angle at which the pooled center plus the line reads zero. When the bridge reads within its bound and the slope
   of the new +-10 degree arms lies within 3 standard errors of the slope of the predecessor's admitted q4 +-10
   degree points, the same line is also reported with those points added. The bridge compares centers alone; the
   slope comparison keeps a padding that changes the q4 response out of the pooled line.
8. Line phase, outside this analysis: the shot-order fold of
   `docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.py` is run on the retained jobs afterwards and
   decides nothing.

| label | outcome | effect on A5-186 |
|---|---|---|
| `q12_phase` | a single-qubit phase at q12's pulses is adequate and preferred in each deciding kind; its sign and size per batch are reported. A rotation about z after each pulse gives the same laws as one before each pulse, so the label leaves the placement open | changes to that statement |
| `coupler_phase` | a conditional phase of coupler 8-12 is adequate and preferred in each deciding kind | changes to that statement |
| `q8_phase_at_coupler` | a single-qubit phase on q8 after each CZ of coupler 8-12 is adequate and preferred in each deciding kind | changes to that statement |
| `phase_mixed` | the series prefers one error world and a deciding kind disagrees or fits it badly: two mechanisms, a change during the series, or sampling noise (up to 8 of 500 simulated series of one mechanism) | unchanged; the numbers are reported |
| `phase_unresolved` | an error world is adequate and the least is not separated from another | unchanged; the numbers are reported |
| `exact_parabola` | the deciding arms and their centers follow exact gates at the fitted readout flip; the offset is not a phase on or around q12, and a fitted flip above 0 names a selector misread conditioned on q12 reading 0 as its candidate cause | unchanged; the phase reading is falsified and the fitted flip is reported |
| `none_adequate` | no world fits at any noise model and readout flip of the fit | unchanged |
| `offset_absent`, `offset_reversed`, `unresolved_guard` | numbers reported | unchanged |

## Limits stated before the run

- The retained data reject both phase worlds by wide margins under the contraction model (contrast chi-square
  187 and 205 with one parameter per batch, d2 split 211 and 427). The CZ damping models narrow that gap in the
  exploratory refit but were fitted to the same data. `none_adequate` is a likely outcome; it changes nothing in
  the ledger and reports the numbers.
- The noise models are the contraction shares and CZ damping at one ratio of amplitude to phase damping (0.019 to
  0.031). Pulse damping, depolarizing CZ noise and other ratios are outside the fit. The operating characteristics
  cover CZ damping at that ratio (multiples 1, 1.25 and 3) and six truths outside the fit (a selector flip beside
  CZ or pulse phase damping, a q8 phase beside pulse or CZ phase damping), with Gaussian noise and every batch
  admitted.
- The fit carries one readout flip per series and world, conditioned on q12 reading 0. A flip that drifts during
  the series, a flip conditioned on another qubit, or one above 0.06 lies outside it. Without the flip, a true q12
  or coupler phase beside a flip of 0.0166 to 0.042 read `none_adequate` in 290 to 300 of 300 exploratory series;
  with it, its own label in 195 to 200 of 200. In the same exploratory draws a null whose flip drifts from 0 to
  0.036 or 0.05 during the series read no deciding label, and a true q12 or coupler phase beside a flip drifting
  from 0 to 0.036 read its own label in about half its series and `none_adequate` or `phase_mixed` otherwise
  (`docs/evidence/qi-null-phase-scan-decision-probes/readout-flip/`; pseudo-random seeds, not draw values).
- Choosing among 62 noise models and 25 readout flips costs more than the two degrees of freedom the bound
  removes; the bound is calibrated by the operating characteristics, not by the count.
- The consistency margin of rule 4 (6.63) was calibrated on value 0 of the draw for the decision with two error
  worlds before value 1 was read (`calibration.json` in
  `docs/evidence/qi-null-phase-scan-decision-probes/`); the order rests on the files' modification times alone.
  The decision with three error worlds keeps that margin. Its scaled separation was calibrated on value 9 (no
  wrong label at 30, 35 or 40), recorded at 30 on value 10 (one wrong label in 500 series of one null), fixed at
  40 by the owner, and recorded on value 11 with the readout flip fixed at 0; value 12 records the rule with the
  fitted flip, which keeps the margin and the separation; values 2 to 7 seeded a reviewer's replication and value
  8 the unscaled rule. The separation of 40 costs power on q8 phases of 0.17 rad and less, which read
  `phase_unresolved` in most series.
- The fitted values of one batch share shots and a center arm; the chi-square adds them as independent. On
  expected laws the correlation of a circuit's contrast and d2 split is below 0.002.
- The offset drifts on a scale of minutes, so a fitted phase is a value per batch.
- Placement. Every q12 operation between two of its pulses is diagonal, so a rotation about z after each pulse
  gives exactly the laws of one before each pulse (`--self-test`). The label `q12_phase` names a single-qubit
  phase on q12 and no placement. A phase on q8 at the coupler is a world of the fit; a phase on q8 elsewhere in
  b0's 34 pulses is not.
- Schedule. The padding makes the arms' instruction lists equal; that the control stack keeps `Rz(0.0)` is a
  hypothesis, and the bridge measures its consequence on the center alone. A control stack that dropped `Rz(0.0)`
  but played a nonzero `Rz` would lengthen the injected arms alone; the bridge reads equal centers in that case
  too, so the hypothesis stays open after the run.
- The exploratory reading chose these worlds after seeing the predecessor's data. This case fixes its rules before
  any new shot.

## Commands

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=${STAMP:-$(date -u +%Y-%m-%dT%H%M%SZ)}
echo "STAMP=$STAMP"
SCAN=scripts/qi_pathion_null_phase_scan_cases.py

"$PYTHON" "$SCAN" --check "$CASES"
"$PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: four batches, then the control analysis, which exits 1 unless the series is complete and every circuit
# reads its ideal law; the Tuna-17 lines run only after it exits 0.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_null_phase_scan_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_phase_scan_qx-batch-* \
	--out results/quantum_inspire/pathion_null_phase_scan_qx_analysis.json

# Tuna-17: twenty-nine batches in order, with Tuna-17 online and the account's queue empty.
SANITY_COMMAND="$PYTHON $SCAN --sanity" sh scripts/qi_pathion_one_cz_null_submit.sh 7 \
	"$CASES/pathion_null_phase_scan_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_phase_scan_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_null_phase_scan_tuna_17_analysis.json
```

The full fit builds the damped law tables once (192 tables, 3,009 s on a 12-thread host) in the scratch directory that
`GOROROBA_SCAN_TABLES` names, the system temporary directory by default. Never resubmit a directory that holds
`submission.json` (`qi_platform.py reconcile` recovers its receipt); see `docs/notes/quantum_inspire/usage.md`,
"Run on Tuna-17". The retention change that follows holds the run directories, both analyses and their replay
gates, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

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
gates of coupler 8-12 (the z8c arms) acts on the selector's side of the coupler, where the two error worlds differ
most: at the expected values below the z8c batches alone separate them by 71 to 194 in chi-square. With exact
gates the z12 curve is even in phi and reads zero at phi = 0, so a static offset of another origin adds a constant.

Schedule. The provider lists `Rz` as a native operation and gives native single-qubit gates 20 ns under
as-late-as-possible scheduling (`docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md`), so an
added `Rz` may cost time. Every circuit but the bridge's plain arm therefore carries the same nine `Rz` at the
same places, at angle 0 where the arm injects nothing, and the arms differ in angles alone. OpenSquirrel 0.9.1,
the platform's compiler, keeps `Rz(0.0)` as its own instruction (`docs/evidence/quantum_inspire/toolchain-token-recovery.json`:
the compiled padded center holds its four q8 and five q12 zero-angle `Rz`, and the compiled text differs from the
source by angle rounding alone), and its scheduler exporter gives every `Rz`, zero angle included, one 20 ns
cycle. hypothesis: the control stack after the compiler keeps the zero-angle `Rz` too. The two bridge batches
hold the predecessor's unpadded center (`b0-rx`, twice) beside the padded center (`b0-rxz`) and measure what the
padding changes.

Predicted raw selector contrast per arm at the retention where the center reads visibility 0.42, contraction
share 0, through the mean bracket readout of the predecessor (`prediction.json`, `truths`). "CZ damping" is
amplitude 0.019 and phase 0.031 per CZ qubit, the values that took the predecessor's full-histogram chi-square
from 182,795 to 51,767 on 925 degrees of freedom in an exploratory refit; "x1.25" and "x3" scale both.

| truth | center | q4 -10 | q4 -5 | q4 +5 | q4 +10 | z12 -30 | z12 -10 | z12 +10 | z12 +30 | z8c -10 | z8c +10 | label |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coupler 8-12 phase +0.25 rad | +0.0204 | +0.0035 | +0.0118 | +0.0285 | +0.0353 | +0.0551 | +0.0111 | +0.0503 | +0.1315 | +0.0001 | +0.0502 | `coupler_phase` |
| coupler 8-12 phase -0.25 rad | +0.0157 | +0.0305 | +0.0236 | +0.0075 | -0.0001 | +0.1635 | +0.0546 | +0.0036 | +0.0656 | +0.0417 | -0.0014 | `coupler_phase` |
| coupler 8-12 phase -0.25 rad with CZ damping | +0.0139 | +0.0297 | +0.0223 | +0.0052 | -0.0028 | +0.1509 | +0.0498 | +0.0033 | +0.0634 | +0.0413 | -0.0030 | `coupler_phase` |
| coupler 8-12 phase -0.25 rad with CZ damping x1.25 | +0.0114 | +0.0250 | +0.0187 | +0.0039 | -0.0031 | +0.1252 | +0.0411 | +0.0028 | +0.0534 | +0.0350 | -0.0029 | `coupler_phase` |
| exact gates | 0 | 0 | 0 | 0 | 0 | +0.0911 | +0.0127 | +0.0129 | +0.0954 | +0.0032 | +0.0095 | `offset_absent` |
| exact gates with CZ damping | -0.0001 | +0.0001 | 0 | -0.0001 | -0.0002 | +0.0936 | +0.0130 | +0.0132 | +0.0980 | +0.0038 | +0.0106 | `offset_absent` |
| exact gates, selector flip 0.0166 when q12 reads 0 | +0.0073 | +0.0070 | +0.0072 | +0.0072 | +0.0070 | +0.0955 | +0.0196 | +0.0200 | +0.1004 | +0.0102 | +0.0164 | `none_adequate` |
| exact gates, selector flip 0.036 when q12 reads 0 | +0.0162 | +0.0155 | +0.0160 | +0.0160 | +0.0155 | +0.1010 | +0.0279 | +0.0286 | +0.1065 | +0.0186 | +0.0249 | `none_adequate` |
| q12 phase +0.18 rad | +0.0141 | +0.0031 | +0.0086 | +0.0194 | +0.0237 | +0.0469 | 0 | +0.0511 | +0.1465 | +0.0060 | +0.0339 | `q12_phase` |
| q12 phase -0.15 rad | +0.0099 | +0.0190 | +0.0148 | +0.0049 | +0.0001 | +0.1331 | +0.0429 | +0.0003 | +0.0569 | +0.0261 | +0.0063 | `q12_phase` |
| q12 phase -0.15 rad with CZ damping | +0.0097 | +0.0201 | +0.0153 | +0.0039 | -0.0014 | +0.1308 | +0.0421 | +0.0002 | +0.0559 | +0.0262 | +0.0072 | `q12_phase` |
| q12 phase -0.15 rad with CZ damping x1.25 | +0.0081 | +0.0171 | +0.0129 | +0.0031 | -0.0015 | +0.1092 | +0.0352 | +0.0002 | +0.0467 | +0.0220 | +0.0063 | `q12_phase` |
| q12 phase -0.15 rad with CZ damping x3 | +0.0020 | +0.0052 | +0.0037 | +0.0002 | -0.0015 | +0.0289 | +0.0091 | +0.0001 | +0.0132 | +0.0060 | +0.0024 | `offset_absent` |
| q12 phase -0.18 rad | +0.0144 | +0.0254 | +0.0203 | +0.0082 | +0.0024 | +0.1420 | +0.0512 | 0 | +0.0499 | +0.0338 | +0.0075 | `q12_phase` |
| q8 phase at coupler 8-12 -0.25 rad | +0.0090 | +0.0233 | +0.0166 | +0.0014 | -0.0056 | +0.1794 | +0.0448 | +0.0064 | +0.0864 | +0.0272 | -0.0002 | `none_adequate` |

The standard error of one contrast at 131,072 shots is 0.0028 and of one d2 split 0.0056. The z8c curve is
asymmetric under exact gates (+0.0032 at -10 degrees, +0.0095 at +10), and its d2 split carries most of the
separation: under the coupler phase of -0.25 rad the z8c arms read d2 splits of +0.040 and -0.007, under a q12
phase of -0.18 rad +0.006 and +0.018. A q8 phase at coupler 8-12, the error the z8c arms inject, is no world of
the fit; its truth reads `none_adequate`. A q12 phase beside CZ damping three times the retained strength
shrinks the center's offset below the control's threshold and reads `offset_absent`.

The predecessor's readout world beside exact gates (a selector flip when d0 reads 0) reads no phase label: its exact
world scores 121.9 and 598.3 against the bound of 72.05. `exact_parabola` is therefore reached only by an offset
near the control's threshold, and the falsifier of the phase reading at the observed offset is `none_adequate`
together with a z12 parabola whose least point sits at phi = 0 (rule 5).

Operating characteristics (`prediction.json`, `operating_characteristics`): 500 simulated series per scenario,
Gaussian contrasts and d2 splits at the design standard errors, every batch admitted, a static d2 split of +0.0083
on every circuit, seeded from value 1 of `docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json`. Value 0 of the
same draw calibrated the consistency margin of rule 4 before value 1 was read (at margin 0 a single mechanism read
`phase_mixed` in up to 94 of 500 series; at 6.63 in at most 7).

| scenario | label counts |
|---|---|
| coupler 8-12 phase +0.25 rad | `coupler_phase` 494, `none_adequate` 1, `phase_mixed` 5 |
| coupler 8-12 phase -0.25 rad | `coupler_phase` 496, `none_adequate` 3, `phase_mixed` 1 |
| coupler 8-12 phase -0.25 rad with CZ damping | `coupler_phase` 493, `none_adequate` 3, `phase_mixed` 4 |
| coupler 8-12 phase -0.25 rad with CZ damping x1.25 | `coupler_phase` 500 |
| exact gates | `offset_absent` 498, `offset_reversed` 2 |
| exact gates with CZ damping | `exact_parabola` 1, `offset_absent` 498, `offset_reversed` 1 |
| exact gates, selector flip 0.0166 when q12 reads 0 | `none_adequate` 500 |
| exact gates, selector flip 0.036 when q12 reads 0 | `none_adequate` 500 |
| q12 phase +0.18 rad | `none_adequate` 3, `phase_mixed` 2, `q12_phase` 495 |
| q12 phase -0.15 rad | `none_adequate` 2, `phase_mixed` 1, `q12_phase` 497 |
| q12 phase -0.15 rad with CZ damping | `none_adequate` 4, `phase_mixed` 1, `q12_phase` 495 |
| q12 phase -0.15 rad with CZ damping x1.25 | `phase_mixed` 2, `q12_phase` 498 |
| q12 phase -0.15 rad with CZ damping x3 | `exact_parabola` 1, `offset_absent` 330, `phase_unresolved` 159, `q12_phase` 10 |
| q12 phase -0.18 rad | `none_adequate` 2, `phase_mixed` 7, `q12_phase` 491 |
| q8 phase at coupler 8-12 -0.25 rad | `none_adequate` 496, `phase_mixed` 4 |
| z12 from coupler phase -0.25, z8c from q12 phase -0.18 | `none_adequate` 475, `phase_mixed` 24, `q12_phase` 1 |
| z12 from q12 phase -0.18, z8c from coupler phase -0.25 | `coupler_phase` 2, `none_adequate` 406, `phase_mixed` 92 |

No single mechanism reads the other mechanism's label. Each reads its own in 491 to 500 of 500 series, CZ damping
off the fitted grid included. The last two rows draw the z12 batches from one mechanism and the z8c batches from
the other; they read a deciding label in 2 and 1 of 500 series.

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
  within 0.5 degrees on either sign; the earlier set (-5, +5, +10, +15) missed by up to 2.4 degrees on the
  positive side.

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
3. Fit. For each of three worlds (exact gates, a rotation about z before each pulse of q12, a conditional-phase
   error of the CZ gates of coupler 8-12) one parameter per admitted deciding batch is fitted to its three
   contrasts and to the d2 split of each outer arm less its center arm's, at the retention that reproduces the
   batch's center visibility through its own bracket readout. The chi-squares are summed at the one noise model
   that makes the sum least: the predecessor's 13 contraction shares, or CZ damping at multiples 0 to 3 of the
   retained strength in steps of 1/16. A world is adequate when its sum is at most the upper 0.001 point (the
   99.9th percentile) of chi-square with one degree of freedom per fitted value (5 per deciding batch, 3 when its
   d2 splits are left out), less one per fitted parameter and one for the noise model: 72.05 (exact) and 61.10
   (error world) for eight whole batches.
4. Labels. `exact_parabola`: the exact world is adequate, so a phase on or around q12 is falsified as the cause of
   the offset. `q12_phase` or `coupler_phase`: that world is adequate, its sum lies at least 25 below the other
   error world's, and each deciding kind, summed over its admitted replicates, reads that world at or below the
   upper 0.001 point on its own degrees of freedom (26.12 for the two-batch z12 kinds, 39.25 for z8c) and at most
   6.63 above the other error world. `phase_mixed`: the sums prefer one error world and a kind does not.
   `phase_unresolved`: an error world is adequate and the two are closer than 25. `none_adequate`: no world is
   adequate. The labels are tested in this order, so each series reads exactly one.
5. Reported beside the label, outside it: the fitted parameter and noise model; the injected phase of least
   contrast from weighted parabolas through the z12 arms and their centers and through the z8c arms and their
   centers; the d2 split of every arm of the deciding kinds pooled over the replicates whose d2 qubit passed its
   guard; each arm's visibility over its center's beside the exact circuit's ratio.
6. Bridge, outside the label: the padded center's contrast less the mean of the two plain arms in each admitted
   bridge batch, pooled, and whether it lies within 3 standard errors of zero.
7. q4 line, outside the label: a weighted straight line through the origin of the contrast of each q4 arm less
   its batch center against q4's injected angle (-10, -5, +5, +10 degrees), with its chi-square, its slope and the
   angle at which the pooled center plus the line reads zero. When the bridge reads within its bound, the same
   line is also reported with the predecessor's admitted q4 +-10 degree points added.
8. Line phase, outside this analysis: the shot-order fold of
   `docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.py` is run on the retained jobs afterwards and
   decides nothing.

| label | outcome | effect on A5-186 |
|---|---|---|
| `q12_phase` | a single-qubit phase at q12's pulses is adequate and preferred in each deciding kind; its sign and size per batch are reported. A rotation about z after each pulse gives the same laws as one before each pulse, so the label leaves the placement open | changes to that statement |
| `coupler_phase` | a conditional phase of coupler 8-12 is adequate and preferred in each deciding kind | changes to that statement |
| `phase_mixed` | the series prefers one error world and a deciding kind disagrees or fits it badly: two mechanisms, a change during the series, or sampling noise (1 to 7 of 500 simulated series of one mechanism) | unchanged; the numbers are reported |
| `phase_unresolved` | an error world is adequate and the two are not separated | unchanged; the numbers are reported |
| `exact_parabola` | the deciding arms and their centers follow exact gates; the offset is small and not a phase on or around q12 | unchanged; the phase reading is falsified |
| `none_adequate` | no world fits; a selector readout flip beside exact gates and a q8 phase at the coupler read this label | unchanged |
| `offset_absent`, `offset_reversed`, `unresolved_guard` | numbers reported | unchanged |

## Limits stated before the run

- The retained data reject both phase worlds by wide margins under the contraction model (contrast chi-square
  187 and 205 with one parameter per batch, d2 split 211 and 427). The CZ damping models narrow that gap in the
  exploratory refit but were fitted to the same data. `none_adequate` is a likely outcome; it changes nothing in
  the ledger and reports the numbers.
- The noise models are the contraction shares and CZ damping at one ratio of amplitude to phase damping (0.019 to
  0.031). Pulse damping, depolarizing CZ noise and other ratios are outside the fit; the operating characteristics
  cover CZ damping at that ratio alone, between grid points included, with Gaussian noise and every batch admitted.
- Choosing among 62 noise models costs more than the one degree of freedom the bound removes; the bound is
  calibrated by the operating characteristics, not by the count.
- The fitted values of one batch share shots and a center arm; the chi-square adds them as independent. On
  expected laws the correlation of a circuit's contrast and d2 split is below 0.002.
- The offset drifts on a scale of minutes, so a fitted phase is a value per batch.
- Placement. Every q12 operation between two of its pulses is diagonal, so a rotation about z after each pulse
  gives exactly the laws of one before each pulse (`--self-test`). The label `q12_phase` names a single-qubit
  phase on q12 and no placement. A phase on q8 at the coupler, which the z8c arms inject, is no world of the fit.
- Schedule. The padding makes the arms' instruction lists equal; that the control stack keeps `Rz(0.0)` is a
  hypothesis, and the bridge measures its consequence on the center alone.
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

The full fit builds the damped law tables once (about 8 minutes over 6 workers) in the scratch directory that
`GOROROBA_SCAN_TABLES` names, the system temporary directory by default. Never resubmit a directory that holds
`submission.json` (`qi_platform.py reconcile` recovers its receipt); see `docs/notes/quantum_inspire/usage.md`,
"Run on Tuna-17". The retention change that follows holds the run directories, both analyses and their replay
gates, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

# Case: Tuna-17 selector offset of the null block against an injected phase on q12

Status: written case awaiting its review and the owner's approval; nothing has been submitted. Generator and
checker: `scripts/qi_pathion_null_phase_scan_cases.py` (`--check results/quantum_inspire/cases` reproduces every
file of this directory except this one, and the QX twin `../pathion_null_phase_scan_qx/`). Ledger row: A5-186.
Predecessor: the injected-rotation scan ([case](../pathion_null_rotation_scan_tuna_17/CASE.md), verdict
`unresolved_none`) and its exploratory reading
([tuna17-null-rotation-scan-line-phase.md](../../../../docs/notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md)),
whose [draft](../../../../docs/notes/quantum_inspire/tuna17-null-phase-scan-case-draft.md) this case builds.

## What the run measures

Terms. Each shot reads five bits on the region's qubits: the coin (q2), the selector (q8) and three data bits d0
(q12), d1 (q4) and d2 (q11). The selector contrast is P(selector 0 | coin 1) - P(selector 0 | coin 0), and the d2
split is that contrast among shots with d2 = 1 less the one among d2 = 0. The visibility is the size of the
contrast inside the bins of d0 and d1, where b0's ideal law gives +-1. The fit models the device's loss as a
contraction: a retention r mixes the ideal law toward the uniform one, and the contraction share says how much of
that loss falls on the data bits alone.

The null block b0 (21 routed CZ on q2, q4, q8, q11, q12; 49 pulses: 34 on q8, 8 on q4, 5 on q12, 1 on q2, 1 on
q11) reads a raw selector contrast of +0.0145 +- 0.0010 over the eleven center circuits of the predecessor, where
exact gates give 0. The predecessor varied pulse amplitudes, and none of its preregistered worlds fits (least
chi-square 234.5 against 37.70). In the exploratory reading two elementary errors outside those worlds lead: a
rotation about z before each pulse of q12 and a conditional-phase error of the CZ gates of coupler 8-12
(chi-square 205 and 187 with one parameter per batch). Neither is adequate, and with exact pulses both give a
contrast that is even in the error, so the retained offset fixes a size near 0.18 rad for the q12 phase and leaves
its sign open.

This case injects a known phase. An `Rz(phi)` before each of q12's five pulses adds phi to the phase that precedes
that pulse. Under a phase theta on q12 the contrast against phi is the exact curve shifted by -theta: it reads zero
at phi = -theta. Under a conditional phase of coupler 8-12 the least contrast stays above zero and the d2 split of
the z12 arms departs from zero. With exact gates the curve is even in phi and reads zero at phi = 0, so a static
offset of another origin adds a constant to an even curve.

hypothesis: Tuna-17 applies `Rz` as a frame update of zero duration, so the z12 arms keep the schedule, the pulse
count and the CZ count of the center arm. The provider lists `Rz(angle)` among the native gates
(`docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md`) and publishes no pulse schedule. The
platform's compiler keeps each injected `Rz` as its own instruction before its pulse
(`docs/evidence/quantum_inspire/toolchain-token-recovery.json`, 51 circuits of this case, 0 failing; the compiled
text differs from the source by angle rounding and by `Rz(-pi)` written as `Rz(pi)`).

Predicted raw selector contrast per arm at the retention where the center reads visibility 0.42, contraction
share 0, through the mean bracket readout of the predecessor (`prediction.json`, `truths`):

| truth | center | q4 -5 | q4 +5 | q4 +10 | q4 +15 | z12 -30 | z12 -10 | z12 +10 | z12 +30 | label |
|---|---|---|---|---|---|---|---|---|---|---|
| exact gates | 0 | 0 | 0 | 0 | 0 | +0.0911 | +0.0127 | +0.0129 | +0.0954 | `offset_absent` |
| q12 phase -0.18 rad | +0.0144 | +0.0203 | +0.0082 | +0.0024 | -0.0025 | +0.1420 | +0.0512 | 0 | +0.0499 | `q12_phase` |
| q12 phase -0.15 rad | +0.0099 | +0.0148 | +0.0049 | +0.0001 | -0.0037 | +0.1331 | +0.0429 | +0.0003 | +0.0569 | `q12_phase` |
| q12 phase +0.18 rad | +0.0141 | +0.0086 | +0.0194 | +0.0237 | +0.0268 | +0.0469 | 0 | +0.0511 | +0.1465 | `q12_phase` |
| coupler 8-12 phase -0.25 rad | +0.0157 | +0.0236 | +0.0075 | -0.0001 | -0.0064 | +0.1635 | +0.0546 | +0.0036 | +0.0656 | `coupler_phase` |
| coupler 8-12 phase +0.25 rad | +0.0204 | +0.0118 | +0.0285 | +0.0353 | +0.0401 | +0.0551 | +0.0111 | +0.0503 | +0.1315 | `coupler_phase` |
| exact gates, selector flip 0.0166 when q12 reads 0 | +0.0073 | +0.0072 | +0.0072 | +0.0070 | +0.0067 | +0.0955 | +0.0196 | +0.0200 | +0.1004 | `none_adequate` |
| exact gates, selector flip 0.036 when q12 reads 0 | +0.0162 | +0.0160 | +0.0160 | +0.0155 | +0.0148 | +0.1010 | +0.0279 | +0.0286 | +0.1065 | `none_adequate` |

The last two rows are the predecessor's readout world beside exact gates, a mechanism outside this decision's
worlds: neither reads a phase label. The exact world reads 48.9 and 238.1 against its bound of 43.82, so at the
offset the device shows a readout origin reads `none_adequate`, and `exact_parabola` is reached only by an offset
near the control's threshold. The falsifier of the phase reading at the observed offset is therefore
`none_adequate` together with a parabola whose least point sits at phi = 0 (rule 5).

The standard error of one contrast at 131,072 shots is 0.0028 and of one d2 split 0.0056. The d2 split of the z12
arms stays below 0.0023 under exact gates and under a q12 phase; under the coupler phase of -0.25 rad it reads
-0.0201, -0.0042, +0.0118 and +0.0267 at -30, -10, +10 and +30 degrees, and under +0.25 rad +0.0362, +0.0192,
-0.0014 and -0.0218. The retained q4 arms of the predecessor read +0.039 at -10 degrees and -0.006 at +10 degrees:
a falling line, as in the three negative-sign rows, and steeper than any of them.

At these expected values the fit of "Preregistered decision rules" gives the other error world a chi-square of
157.0 (q12 phase -0.18 true), 106.4 (-0.15), 157.6 (+0.18), 48.8 (coupler -0.25 true) and 145.4 (+0.25) against
the separation of 25 and the adequacy bound of 37.70, and the exact world above 1,100 in each. Three choices carry
that margin. The fit includes the d2 split: on the contrasts alone, with outer arms at +-20 degrees, the coupler
truth of -0.25 rad sat 7.7 from the q12 world. The outer z12 arms sit at +-30 degrees. The split enters as each
outer arm's less its batch center's: the predecessor's centers read a d2 split of +0.0083 +- 0.0017 that no world
of this decision gives, and the coupler world's split is odd in phi and survives the subtraction.

Operating characteristics (`prediction.json`, `operating_characteristics`): 500 simulated series per truth, Gaussian
contrasts and d2 splits at the design standard errors, every batch admitted, a static d2 split of +0.0083 on every
circuit, seeded from value 4 of `docs/evidence/anu_qrng/draw-2026-11-13T172143Z.json`:

| truth | label counts |
|---|---|
| coupler 8-12 phase +0.25 rad | `coupler_phase` 498, `none_adequate` 1, `phase_mixed` 1 |
| coupler 8-12 phase -0.25 rad | `coupler_phase` 465, `none_adequate` 3, `phase_mixed` 20, `phase_unresolved` 12 |
| exact gates | `offset_absent` 499, `offset_reversed` 1 |
| exact gates, selector flip 0.0166 when q12 reads 0 | `exact_parabola` 25, `none_adequate` 471, `phase_unresolved` 4 |
| exact gates, selector flip 0.036 when q12 reads 0 | `none_adequate` 500 |
| q12 phase +0.18 rad | `phase_mixed` 2, `q12_phase` 498 |
| q12 phase -0.15 rad | `none_adequate` 1, `phase_mixed` 46, `q12_phase` 453 |
| q12 phase -0.18 rad | `none_adequate` 1, `phase_mixed` 29, `q12_phase` 470 |
| z12 +-10 from q12 phase -0.18, z12 +-30 from coupler phase -0.25 | `coupler_phase` 50, `none_adequate` 23, `phase_mixed` 328, `phase_unresolved` 99 |

No single mechanism reads the other mechanism's label. A true q12 phase of -0.15 rad reads `phase_mixed` in 46
series and a coupler phase of -0.25 rad in 20: the +-10 degree arms separate the two error worlds by about 13
per kind, so sampling noise can turn that kind toward the other world. The last row is a series of two mechanisms;
it reads a deciding label in 50 series. A looser consistency test (the other world may undercut a kind by 6.63)
lowers the false `phase_mixed` counts to 1 or 2 and raises that 50 to 257, so the rule stays strict.

### Circuits

Every circuit is the retained b0 text with each `X90` as `Rx(pi/2)`, the predecessor's center arm, rewritten on
one qubit. Angles are multiples of pi/36, the processor's angle grid.

- `b0-rx`: the center, byte for byte the predecessor's `b0-rx`, in every data batch.
- `b0-rx-q4-m5`, `-p5`, `-p10`, `-p15`: q4's 8 pulses at 85, 95, 100 and 105 degrees. `-p10` repeats a retained
  arm.
- `b0-rx-z12-m30`, `-m10`, `-p10`, `-p30`: `Rz(phi)` before each of q12's 5 pulses, phi = -30, -10, +10, +30
  degrees. The +-10 degree arms sit beside the injected phase that would cancel the fitted one (9 to 10 degrees).

### Batches

17 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch. Eight data batches at 131,072 shots per circuit:

- forward round: [q4 -5, `b0-rx`, q4 +5], [q4 +10, `b0-rx`, q4 +15], [z12 -10, `b0-rx`, z12 +10],
  [z12 -30, `b0-rx`, z12 +30];
- mirror round: the same four in reverse order with the outer arms exchanged.

Each data batch carries its own center, so a drift of the offset between batches (0.001 to 0.020 in the
predecessor) enters no within-batch comparison. The two z12 +-30 batches share the readout batch between them, so
one failed bracket on a contrast qubit there removes both and the series reads `unresolved_guard`. The QX twin holds the nine distinct
circuits in three batches of 3 at 2,048 shots.

## Why simulation cannot answer it

Whether the device carries a phase on q12, a conditional phase on coupler 8-12, or neither is a calibration fact of
Tuna-17 that the provider does not publish. The retained series cannot separate them: it varies pulse amplitudes
alone, both errors fit its contrasts almost equally, and its response is even in the error.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12 (q15 and q13 stay out). QX emulator (type 1)
  for the twin.
- Jobs and shots: 42 jobs in 17 batches, 3,735,552 shots (24 data jobs at 131,072, 18 readout jobs at 32,768),
  every job at or under 131,072 shots. The longest job takes about 80 s against the 300 s job limit.
- Expected time: 35 to 39 minutes of execution (2,089 to 2,315 s), 16 pauses budgeted at the 120 s top step of the
  pause ladder (1,920 s; the series starts at the 30 s step), plus queue time. The predecessor's 21 batches took
  66 minutes. QX twin: 9 jobs of 2,048 shots.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  (`docs/notes/quantum_inspire/usage.md`, "Queue rules: the FAQ governs").
- Quota and credits: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this
  account; the ledger snapshot after the predecessor lists its 62 jobs with no charge. Expected credits 0, read
  again from a fresh usage snapshot before the submission.

## Preregistered decision rules

`cases.json` of every batch carries these rules (`preregistered`); `decide()` applies rules 1 to 4.

1. Admission. A data batch is admitted when e01 and e10 of each qubit the contrast reads (q12, q4, q8, q2)
   change by at most 0.02 between the readout batch before it and the one after. Its d2 splits enter the fit only
   when d2's qubit (q11) passes the same bound; otherwise the batch is fitted on its three contrasts. The
   decision needs an admitted batch of each z12 kind; otherwise `unresolved_guard`. Applied to retained brackets,
   the four-qubit guard admits 10 of 10 data batches of the predecessor and 19 of 19 bracket pairs of the one-CZ
   series; q11 passes in 10 of 10 and in 15 of 19 (its e10 moved by up to 0.34 there).
2. Control. The inverse-variance mean of the center contrast over the admitted batches exceeds 3 standard errors;
   otherwise `offset_absent` (within) or `offset_reversed` (below).
3. Fit. For each of three worlds (exact gates, a rotation about z before each pulse of q12, a conditional-phase
   error of the CZ gates of coupler 8-12) one parameter per admitted z12 batch is fitted to its three contrasts and
   to the d2 split of each outer arm less its center arm's, at the retention that reproduces the batch's center
   visibility through its own bracket readout. The chi-squares are summed at the one contraction share (the
   predecessor's grid of 13) that makes the sum least. A world is adequate when its sum is at most the upper 0.001
   point (the 99.9th percentile) of chi-square with one degree of freedom per fitted value (5 per z12 batch, 3
   when its d2 splits are left out), less one per fitted parameter and one for the share: 43.82 (exact) and 37.70
   (error world) for four whole batches.
4. Labels. `exact_parabola`: the exact world is adequate, so a phase on or around q12 is falsified as the cause of
   the offset. `q12_phase` or `coupler_phase`: that world is adequate, its sum lies at least 25 below the other
   error world's, and each z12 kind, summed over its admitted replicates, reads that world at or below the upper
   0.001 point on its own degrees of freedom (26.12 for two whole batches) and no higher than the other error
   world. `phase_mixed`: the sums prefer one error world and a kind does not. `phase_unresolved`: an error world
   is adequate and the two are closer than 25. `none_adequate`: no world is adequate.
5. Reported beside the label, outside it: the fitted parameter of each admitted z12 batch; the injected phase of
   least contrast from a weighted parabola through the z12 arms and their centers; the d2 split of the +10 and +30
   degree arms pooled over the replicates whose d2 qubit passed its guard; each arm's visibility over its center's beside the exact circuit's ratio.
6. q4 line, outside the label: a weighted straight line through the contrast of each q4 arm less its batch center
   against q4's injected angle (-5, +5, +10, +15 degrees), with its chi-square on 3 degrees of freedom, its slope
   and the angle at which the pooled center plus the line reads zero.
7. Line phase, outside this analysis: the shot-order fold of
   `docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.py` is run on the retained jobs afterwards and
   decides nothing.

| label | outcome | effect on A5-186 |
|---|---|---|
| `q12_phase` | a single-qubit phase at q12's pulses is adequate and preferred in each z12 kind; its sign and size per batch are reported. A rotation about z after each pulse gives the same laws as one before each pulse, so the label leaves the placement open | changes to that statement |
| `coupler_phase` | a conditional phase of coupler 8-12 is adequate and preferred in each z12 kind | changes to that statement |
| `phase_mixed` | the series prefers one error world and a z12 kind disagrees or fits it badly: two mechanisms, a change during the series, or sampling noise on the +-10 degree kind (2 to 46 of 500 simulated series of one mechanism) | unchanged; the numbers are reported |
| `phase_unresolved` | an error world is adequate and the two are not separated | unchanged; the numbers are reported |
| `exact_parabola` | the z12 arms and their centers follow exact gates; the offset is small and not a phase on or around q12 | unchanged; the phase reading is falsified |
| `none_adequate` | no world fits; a selector readout flip beside exact gates reads this label | unchanged |
| `offset_absent`, `offset_reversed`, `unresolved_guard` | numbers reported | unchanged |

## Limits stated before the run

- The fit carries the two contractions of the predecessor at a share fitted once per series. The predecessor's
  gate-noise families are outside it: their tables exist for its worlds alone. The full-histogram fit of the
  exploratory reading shows the contraction model far from the device's law, so an adequate fit here is a
  statement about three contrasts and two relative d2 splits per batch and no more.
- The operating characteristics use Gaussian noise at contraction share 0 and the design visibility with every
  batch admitted. Gate noise, a drifting readout and a phase beside a readout offset are not simulated.
- The q4 arms sit at -5 to +15 degrees around the zero the predecessor's q4 arms bracket (+0.039 at -10 degrees,
  -0.006 at +10). Under a positive q12 phase the line's zero lies near -13 degrees, outside them, and is an
  extrapolation.
- A series whose z12 kinds follow different mechanisms reads a deciding label in 50 of 500 simulated series.
- The fitted values of one batch share shots and a center arm; the chi-square adds them as independent. On
  expected laws the correlation of a circuit's contrast and d2 split is below 0.002.
- The offset drifts on a scale of minutes, so a fitted phase is a value per batch.
- Placement. Every q12 operation between two of its pulses is diagonal, so a rotation about z after each pulse
  gives exactly the laws of one before each pulse (`--self-test`). A single-qubit phase on q12 at its CZ gates or
  a detuning during its idles puts a phase in each gap between pulses; the q12 world models equal gaps alone. The
  label `q12_phase` therefore names a single-qubit phase on q12 and no placement.
- The zero duration of `Rz` is a hypothesis. A phase on q12 moves the visibility of the z12 arms as well, so the
  reported visibility ratio bounds a finite duration and does not isolate it.
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

# QX twin: three batches, then the control analysis, which exits 1 unless the series is complete and every circuit
# reads its ideal law; the Tuna-17 lines run only after it exits 0.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_null_phase_scan_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_phase_scan_qx-batch-* \
	--out results/quantum_inspire/pathion_null_phase_scan_qx_analysis.json

# Tuna-17: seventeen batches in order, with Tuna-17 online and the account's queue empty.
SANITY_COMMAND="$PYTHON $SCAN --sanity" sh scripts/qi_pathion_one_cz_null_submit.sh 7 \
	"$CASES/pathion_null_phase_scan_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_phase_scan_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_null_phase_scan_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run
directories, both analyses and their replay gates, a refreshed `usage.json` and the
`docs/state/research_state.json` registration.

# Case: Tuna-17 selector offset of the null block against an injected X rotation

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_pathion_null_rotation_scan_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../pathion_null_rotation_scan_qx/`). Ledger row: A5-186.

## What the run measures

The null block b0 (operand e1 + e17, coset 0, 21 routed CZ on q2, q4, q8, q11, q12) reads a raw selector contrast
above zero on Tuna-17: +0.0164 +- 0.0039 in the coin series, +0.0162 +- 0.0028 and +0.0393 +- 0.0028 in the two base
batches of the [one-CZ case](../pathion_one_cz_null_tuna_17/CASE.md). The exact circuit gives 0 under every
arm-symmetric readout and under both contractions of the noise model below, and at most 0.0001 in size under its
five gate-noise families. That case's 6-CZ blocks read -0.0007 +- 0.0013
(`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, `m_six_cz`), which a coherent pulse error
and a selector flip conditioned on q12 both predict, and its replicate gate failed on b0 (chi-square 34.9 against
10.83), so row A5-186 stayed a hypothesis.

This case compares the two on b0 itself. Tuna-17 runs `X90` and `Rx` as native single-qubit operations of one 20 ns
duration and quantizes a rotation angle to a pi/36 grid (`docs/notes/quantum_inspire/cqasm.md`;
`docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md`). Replacing an `X90` by
`Rx(pi/2 + k pi/36)` adds a known rotation of 5k degrees about the pulse axis and leaves the schedule, the CZ count
and every other instruction unchanged. A pulse that already over-rotates by theta then rotates by
pi/2 + theta + k pi/36, so the selector contrast as a function of k is the pulse-error response curve shifted by
theta. A readout mechanism leaves the curve of an exact pulse in place and adds its offset. b0 holds 49 pulses: 34
on q8, 8 on q4, 5 on q12, 1 on q2, 1 on q11.

Predicted raw selector contrast per arm, each world sized to the center contrast +0.0164 at retention 0.505,
contraction share 0 and the design readout (`prediction.json`, `predicted_contrast`, which lists every world and
branch):

| world | all -20 | all -10 | center | all +10 | all +20 | q4 -10 | q4 +10 | q8 -10 | q8 +10 |
|---|---|---|---|---|---|---|---|---|---|
| exact circuit, no offset | +0.0659 | +0.0281 | 0 | +0.0636 | +0.0683 | 0 | 0 | -0.0092 | +0.0131 |
| x rotation +0.0511 rad on every pulse | +0.0612 | +0.0092 | +0.0164 | +0.0727 | +0.0622 | +0.0147 | +0.0164 | -0.0310 | +0.0191 |
| x rotation -0.1438 rad on every pulse | +0.0936 | +0.0633 | +0.0164 | +0.0088 | +0.0700 | +0.0165 | +0.0147 | +0.0671 | -0.0087 |
| x rotation +0.0924 rad on q8's pulses | +0.0441 | +0.0057 | +0.0164 | +0.0472 | +0.0304 | +0.0143 | +0.0171 | -0.0152 | -0.0112 |
| y rotation +0.0655 rad before every pulse | +0.0849 | +0.0547 | +0.0164 | +0.0808 | +0.0820 | +0.0085 | +0.0221 | +0.0127 | +0.0451 |
| y rotation -0.0692 rad before every pulse | +0.0420 | +0.0184 | +0.0164 | +0.0622 | +0.0579 | +0.0240 | +0.0066 | -0.0129 | +0.0085 |
| selector flip when q12 reads 0, x 0.0358 | +0.0678 | +0.0381 | +0.0164 | +0.0718 | +0.0682 | +0.0158 | +0.0158 | -0.0005 | +0.0216 |
| selector dropout when the coin reads 1, x 0.0360 | +0.0808 | +0.0439 | +0.0164 | +0.0781 | +0.0830 | +0.0164 | +0.0164 | +0.0073 | +0.0296 |

The standard error of one contrast at 131,072 shots is 0.0028. The readout worlds leave the two q4 arms equal, an x
over-rotation separates them by at most 0.003 (the under-rotation of q8's pulses at -0.247 rad by 0.011), and a y
or z rotation by 0.011 to 0.020 with the sign of its angle. At -10 degrees on every pulse the x over-rotation and the q12 flip sit 0.029 apart, and the two x branches
0.054 apart.

Scan set. Five sets of four scan kinds were compared at expected contrasts on all 95 sized truths of the modeled
worlds under seven noise truths (contraction shares 0 and 1, the five gate-noise families), each decided by the fit
below and again with the truth's own family removed from the fit
(`docs/notes/quantum_inspire/tuna17-null-rotation-scan-noise-simulation.md`, "Scan set"). The set of the merged
case (all +-5, q8 +-5, q8 +-10, all +-10) left 4 truths undecided, with a smallest chi-square gap of 10 between a
truth's class and the next. This set (all +-10, q4 +-10, q8 +-10, all +-20) reads all 95 in their class, and all 67
family truths again with the family removed, with a smallest gap of 50 against the separation of 25. None of the five sets read a truth in a wrong class.

hypothesis: `Rx(pi/2 + k pi/36)` is the X90 pulse at a scaled amplitude, so it carries the X90 pulse's error at
every k. The bridge batches compare `Rx(pi/2)` with `X90` inside one batch at k = 0; the provider documents both as
native and publishes no pulse shapes, and the scan cannot test the premise for k != 0. The +-20 degree arms lean on
it more than the +-10 degree arms.

### Noise model

b0's visibility on Tuna-17 is 0.44. The exact circuit gives 0.9959, and 0.88 after the design readout: the
assignment rates of the five region qubits from the stopped coset-block series (`cc.retained_readout`; q11 e10
0.1914 there). The retained b0 runs read per-bit excitations of 0.43 to 0.53 where a unital channel gives 0.48 to
0.50, so part of the loss is relaxation.

The fit explains the loss by one noise model for the series, the one that gives the world its least chi-square,
among eighteen:

- thirteen contraction shares 0 to 1 in steps of 1/12: the part of the visibility loss that depolarizes the three
  data bits alone and leaves the selector and coin law (share 1), the rest contracting the whole law toward uniform
  (share 0). Contrasts are computed at shares 0, 1/4, 1/2, 3/4, 1 and interpolated linearly to the thirteen, an
  error of at most 0.0009;
- five gate-noise families on the instruction list of each arm, each with one strength: two-qubit depolarizing
  after each CZ; phase damping after each pulse; phase damping on both qubits after each CZ; amplitude damping on
  both qubits after each CZ; amplitude with phase damping after pulses (one third of the strength) and CZ together.

Per batch, the retention (contractions) or the strength (families) is the one at which the world reproduces the
center arm's visibility through the batch's assignment matrix. hypothesis: Tuna-17's loss on b0 lies near these
eighteen models; the provider publishes no channel tomography, and the retained b0 histograms deviate from every
modeled world by a deviance of 880 to 7,900 on 31 outcomes. A loss outside the models shows as an inadequate best
world.

Row A5-186's "+0.03 rad" comes from a model that contracts nothing (visibility 0.86,
`docs/evidence/pathion-kernel-map/conjectures/c2_tuna_mech.txt`); at the observed visibility the same offset needs
+0.0511 rad at share 0, +0.0294 rad at share 1 and +0.047 rad under the two damping families, so the fitted angle
is read together with the fitted noise model.

### Evidence already retained: the d2 split

The selector contrast among outcomes with d2 = 1 less the one among d2 = 0 (`d2_split`) is positive for an x
over-rotation of the pulses, negative for an x under-rotation and for a y or z rotation, and zero for a selector
readout map (within 0.004 under the damping families). The five retained b0 circuits pool to +0.0205 +- 0.0033
(z 6.2, heterogeneity chi-square 5.3 on 4); the twelve 6-CZ circuits of the one-CZ series, which read d2, the
selector and the coin on the same q11, q8 and q2, pool to +0.0032 +- 0.0026. The comparison confounds CZ depth, and
a readout term up to 0.005 stays open. The analysis reports the statistic per circuit and pooled over the center
arms (`center_d2_split`), beside the decision and outside it.

### Circuits

Every circuit measures all 17 qubits and is the retained b0 text with its pulse lines rewritten and its comment line
naming the arm; the emitter reproduces `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte from the parsed
instruction list.

- `b0`: the retained circuit, every pulse an `X90`.
- `b0-rx`: every `X90` as `Rx(pi/2)`. This is the center arm of every scan batch.
- `b0-rx-all-m10`, `-p10`, `-m20`, `-p20`: every pulse at 80, 100, 70 and 110 degrees.
- `b0-rx-q4-m10`, `-p10`: q4's 8 pulses at 80 and 100 degrees, `Rx(pi/2)` elsewhere.
- `b0-rx-q8-m10`, `-p10`: q8's 34 pulses at 80 and 100 degrees, `Rx(pi/2)` elsewhere.

### Batches

21 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch, so each data batch sits between two brackets. The ten data batches run at 131,072 shots
per circuit:

- forward round: all +-10, q4 +-10, q8 +-10, all +-20 (each [minus arm, `b0-rx`, plus arm]), bridge [`b0`, `b0-rx`,
  `b0`];
- mirror round: bridge [`b0-rx`, `b0`, `b0-rx`], then all +-20, q8 +-10, q4 +-10, all +-10, each [plus arm, `b0-rx`,
  minus arm].

Each scan batch carries its own center, and the fit takes one parameter per batch, so a drift of the offset between
batches (0.0162 to 0.0393 in the one-CZ series) changes no within-batch comparison. The two bridge batches share
the readout batch between them, so one failed bracket there removes both. The QX twin holds the ten distinct
circuits in four batches of at most 3 at 2,048 shots.

## Why simulation cannot answer it

The simulation fixes what each mechanism predicts (the table above). Which one the device obeys is a device fact:
the X90 calibration of Tuna-17, its noise channel and the conditional misassignment of the selector are not
published, and a noise simulation of an unknown calibration reproduces any row.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12, the region of the coin and one-CZ series (q15
  and q13 stay out). QX emulator (type 1) for the twin.
- Jobs and shots: 52 jobs in 21 batches, 4,653,056 shots, every job at or under 131,072 shots. The longest job takes
  about 80 s (2.6 s plus 0.59 ms per shot, the coin series' largest rate; 92 s at the 0.7 ms planning rule of
  `docs/notes/quantum_inspire/usage.md`) against the 300 s job limit. The smallest class gap of the scan set is 50
  at 131,072 shots and scales with the shots, so half the shots would put it at the separation.
- Expected time: 43 to 48 minutes of execution (2,601 to 2,883 s), 20 pauses budgeted at the 120 s top step of the
  pause ladder (2,400 s; the series starts at the 30 s step, `usage.md`, "Pause escalation"), plus queue time. QX
  twin: 10 jobs of 2,048 shots.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  (`docs/notes/quantum_inspire/usage.md`, "Queue rules: the FAQ governs"); `qi_platform.py submit` refuses a larger
  hardware batch, a second queued batch and an early submission before any remote write.
- Quota and credits: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this
  account; expected credits 0, read again from a fresh usage snapshot before the submission.

## Preregistered decision rules

The raw counts are read; Z = 3 standard errors. Every label is a preference among the modeled worlds and noise
models.

1. Guard: a data batch is admitted when e01 and e10 of q2, q4, q8 and q12 (the coin, d1, the selector and d0)
   change by at most 0.02 between the readout batch before it and the one after. d2 is summed out of the selector
   contrast and of the visibility, so the assignment of its qubit q11 changes neither; q11's e10 moved by up to
   0.34 between consecutive brackets of the one-CZ series, and its rates are reported unguarded. The decision needs
   at least one admitted batch of each scan kind; otherwise it reads `unresolved_guard`.
2. Control: the inverse-variance mean of the center arm's contrast over the admitted scan batches exceeds 3 standard
   errors. Within 3 standard errors of zero it reads `offset_absent`, below that `offset_reversed`.
3. Fit: per admitted scan batch, world and noise model, the least chi-square of the batch's three contrasts over the
   world's one parameter, through the mean assignment matrix of the two brackets. A world's chi-square is the sum
   over the admitted scan batches at the one noise model that makes the sum least. Worlds: a rotation about x on
   the pulses of all qubits, of q8 or of q4; a rotation about y or z before or after the pulses of the same scopes;
   a selector flip when q12 reads 0; a selector dropout when the coin reads 1. The "after" worlds repeat the
   "before" worlds (about z the two give one law, about y the same law at the opposite angle). Grids: pulse angles
   -0.300 to +0.300 rad in steps of 0.001; readout probabilities 0 to 0.20 in steps of 0.0005; retention 0.05 to 1
   in 20 points; family strength in 12 points that span center visibilities 0.75 to 0.20 at the design readout,
   with linear interpolation of the contrasts between points. A center visibility outside a grid takes the grid
   end. The readout worlds act on the device's logical bits before the assignment matrix.
4. Adequacy: a world is adequate when its chi-square is at most the 0.999 quantile of the chi-square law with two
   degrees of freedom per admitted batch less one for the noise model (37.70 for eight batches).
5. Class: the x class, the y-or-z class and the readout class are compared by their best worlds. A class is
   preferred when its best world is adequate and the best world of each other class sits at least 25 above it. The
   x class is excluded when the other two classes lead, the leader is adequate, the best x world is inadequate and
   it sits at least 25 above the leader.
6. Bridge: `Rx(pi/2)` and `X90` read the same selector contrast when both bridge batches are admitted, their two
   within-batch differences of the `b0-rx` and `b0` contrasts agree within 3 standard errors of each other, and the
   pooled difference is within 3 standard errors of zero. A class label of rule 5 stands only when the bridge
   holds; otherwise the series reads `unresolved_bridge`, reports the class of the Rx circuits as `rx_label` and
   leaves A5-186 unchanged. One difference has a standard error of 0.0034 and the pooled one 0.0024, so the bridge
   resolves a difference of 0.007, 0.4 of the offset; a smaller difference between the two gates passes it. With
   equal gates each of the two tests fails by chance in 0.27 percent of series, so the bridge withholds the label in
   at most 0.54 percent (7 of 2,000 simulated series). The bridge is an equality of two observed contrasts at zero
   injected angle.
7. Reading of `pulse_x` on A5-186, which names one over-rotation of the X90 pulse: the row survives when the best x
   world rotates every pulse and every admitted batch fits a positive angle. Any other x fit (an under-rotation,
   q8's or q4's pulses alone, signs that differ between batches) amends the row.

The adequacy bound and the separation are design thresholds. The retention or strength is plugged in from the
center arm, each class enters by its least chi-square over several worlds and eighteen noise models, and each batch
takes its own parameter, so the sum is a chi-square with 15 degrees of freedom only approximately; the operating
characteristics below state the error rates the two thresholds give at the design values. The analysis reports the
fitted parameter of every batch (`best_parameters`) and the fitted noise model of every world (`noise_model`);
their agreement across batches is read from those lists, outside the decision.

| label | outcome | effect on A5-186 |
|---|---|---|
| `pulse_x`, every pulse, positive angle in every batch | the x class is preferred among the modeled worlds: the offset follows the injected rotation as an over-rotation of every pulse predicts | survives: its falsifier is unmet; the fitted angle and noise model are reported beside the row's +0.03 rad |
| `pulse_x`, any other fit | the x class is preferred with an under-rotation, on one qubit's pulses alone, or with signs that differ between batches | amended: a rotation about x is preferred, and its sign or scope differs from the row's; the scope is the best single-scope world, with its lead over the next (`x_scope_margin`) |
| `pulse_other` | the y-or-z class is preferred among the modeled worlds | not supported as stated: the scan prefers a pulse rotation about y or z or a CZ phase error, which it leaves apart |
| `readout` | the readout class is preferred among the modeled worlds | not supported: each modeled pulse rotation sits at least 25 above a selector readout map; a mechanism outside the model stays open |
| `x_excluded` | no modeled x rotation is adequate under any noise model; readout map and y-or-z rotation are closer than the separation | not supported; the surviving mechanism is undecided |
| `offset_absent`, `offset_reversed` | the center contrast reads within 3 standard errors of zero, or below it | unchanged |
| `unresolved_bridge` | the Rx circuits are classed and their equality with the retained X90 circuit is not shown | unchanged |
| `unresolved_both`, `unresolved_none`, `unresolved_guard` | numbers reported | unchanged |

### Operating characteristics

`prediction.json` (`operating_characteristics`): 10,000 simulated series per truth, Gaussian contrasts at the design
standard error, decided by rules 2 to 5 with every batch admitted; the on-demand gate
`core-pathion-null-rotation-scan-case-replay` of `ci/gates.json` replays it (about thirty minutes on the build
host). Share of runs that read the truth's own class, each truth sized to the center contrast +0.0164, under five
noise truths:

| truth | share 0 | share 1 | CZ damping | damping and dephasing | mirror round at +0.0393, share 0 |
|---|---|---|---|---|---|
| x over-rotation, all pulses | 0.9989 | 0.9983 | 0.9986 | 0.9990 | 0.9992 |
| x under-rotation, all pulses | 0.9991 | 0.9988 | 0.9994 | 0.9995 | 0.9985 |
| x over-rotation, q8 pulses (lower root) | 0.9986 | 0.9992 | 0.9992 | 0.9995 | not reached |
| x over-rotation, q8 pulses, upper root | 0.9993 | 0.9993 | 0.9990 | 0.9991 | not reached |
| x under-rotation, q8 pulses | 0.9985 | 0.9986 | 0.9986 | 0.9986 | 0.9977 |
| y rotation before, all pulses | 0.9929 | 0.9989 | 0.9992 | 0.9995 | 0.9993 |
| z rotation before, all pulses | 0.9983 | 0.9982 | 0.9981 | 0.9981 | 0.9984 |
| selector flip when q12 reads 0 | 0.9987 | 0.9984 | 0.9988 | 0.9987 | 0.9988 |
| selector dropout when the coin reads 1 | 0.9877 | 0.9989 | 0.9987 | 0.9973 | 0.9991 |
| no offset (`offset_absent`) | 0.9971 | 0.9971 | 0.9970 | 0.9971 | 0.9971 |

None of the 480,000 simulated runs reads a class other than its truth's. The remainder of each cell is
`unresolved_none` (at most 0.0023), `unresolved_both` (at most 0.0003 with an offset) or `x_excluded`, which is
compatible with the truth: 0.0116 for the dropout and 0.0065 for the y rotation at share 0, at most 0.002
elsewhere. A no-offset run reads `offset_reversed` in 0.0016 to 0.0018 and `unresolved_both` in 0.0012 to 0.0013.
"Not reached": an x rotation of q8's pulses reaches a center contrast of +0.0393 only at -0.2966 rad, so the two
positive q8 truths do not exist in the mirror round and the table reports them as `truth_unreachable`.

These tables hold the visibility and readout at their design values, admit every batch, leave the bridge out, draw
no drift inside a batch and draw each truth from a noise model the fit contains. The shot-level simulation
(`scripts/qi_pathion_null_rotation_scan_noise.py`, case note
`docs/notes/quantum_inspire/tuna17-null-rotation-scan-noise-simulation.md`) draws whole series of counts under gate noise through the guard, the bridge and the per-batch fit, including a
regime whose fit lacks the truth's noise family.

### Mechanisms outside the modeled worlds

- A conditional-phase error of the CZ gates, here `diag(1, 1, 1, -exp(i delta))` on every CZ
  (`prediction.json`, `unmodeled`, noiseless): at +0.08 rad it gives a center contrast of +0.0075 and reads
  `x_excluded`; at -0.08 rad it reads `unresolved_both`, and at +-0.12 rad (center +0.0156 and +0.0135)
  `unresolved_none`. None reads `pulse_x`. The earlier one-CZ analysis used `CZ exp(-i delta ZZ / 2)`, a different
  channel, and its small response does not bound this one.
- A scale on every pulse angle is an x over-rotation at k = 0 and reads `pulse_x`. A curvature of the pulse
  amplitude response in k, which the scaled-amplitude premise excludes, can read `pulse_x` as well: a 25 percent
  amplitude-slope nonlinearity did so in a reviewer's test of the merged case. `pulse_x` therefore states that the
  x class fits, and leaves the constant over-rotation of A5-186 unproved.
- Rotations about x whose angle differs between qubits: the worlds give one angle to one scope, so a mixture is
  fitted by its nearest single-scope world; the reported scope is the best single-scope fit.
- A selector or coin readout whose assignment during the b0 circuits differs from the one the bracket circuits read
  (the brackets prepare computational states with no gate history): the brackets and the guard cannot see it. It
  changes the contrasts the fit expects and reads as a worse fit, toward the unresolved labels.
- Leakage, residual ZZ during idles, T1 and T2 beyond the five families, and a noise model that changes between
  batches: the series fits one noise model, so such a loss shows as a worse fit, toward `unresolved_none`.

## Not built

- Pauli twirling of the CZ gates: the mechanisms under test act on the single-qubit pulses and the selector read,
  and a twirl inserts further pulses that carry the same error.
- A rerun of the 6-CZ blocks: every surviving mechanism predicts zero there, and the retained run reads zero.
- Arms at +-5 degrees: the +-5 degree arms on every pulse and on q8 left four truths undecided at expected values,
  which the +-10 degree arm on q4 and the +-20 degree arm on every pulse resolve.
- Arms on q12, q2 and q11 alone: they hold 5, 1 and 1 pulses, too few for a +-10 degree arm to resolve.
- A measurement-frame control (b0 with an X on q12 or on the coin before the read): it tests the readout worlds
  directly and adds pulses to the circuit under test; it is a candidate for a later case.

## Submission commands (not run)

The owner's approval is quoted in `--approval`. `scripts/qi_pathion_one_cz_null_submit.sh` submits one batch at a
time and collects it before the next, waits out the pause that `qi_platform.py submit` names, and stops at the first
refusal without a remainder, failed collection or failed sanity check. `QI_COLLECT_TIMEOUT` sets the seconds one
collection waits (3,600 by default); a batch still queued then stops the script and stays queued, and the same
command with the same `STAMP` resumes the series by collecting that batch without a second submit: the block
prints its stamp, and a resume exports that value as `STAMP` before the block runs again. The script refuses a
series that the runs directory already holds under another stamp. The per-batch
sanity check binds the collected batch to this case; the readout admission of a data batch needs the bracket after
it and is applied by `--analyze` on the complete series, so the series runs to its end and a batch that fails
admission leaves the fit.

```sh
set -eu
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=${STAMP:-$(date -u +%Y-%m-%dT%H%M%SZ)}
echo "STAMP=$STAMP"
SCAN=scripts/qi_pathion_null_rotation_scan_cases.py

"$PYTHON" "$SCAN" --check "$CASES"
"$PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: four batches, then the control analysis, which exits 1 unless the series is complete and every circuit
# reads its ideal law; the Tuna-17 lines run only after it exits 0.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_null_rotation_scan_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_rotation_scan_qx-batch-* \
	--out results/quantum_inspire/pathion_null_rotation_scan_qx_analysis.json

# Tuna-17: twenty-one batches in order, after the QX analysis reads a passing control and with Tuna-17 online and the
# account's queue empty.
SANITY_COMMAND="$PYTHON $SCAN --sanity" sh scripts/qi_pathion_one_cz_null_submit.sh 7 \
	"$CASES/pathion_null_rotation_scan_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_rotation_scan_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run
directories, both analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

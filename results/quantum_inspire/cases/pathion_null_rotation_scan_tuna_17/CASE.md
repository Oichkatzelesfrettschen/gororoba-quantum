# Case: Tuna-17 selector offset of the null block against an injected X rotation

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_pathion_null_rotation_scan_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../pathion_null_rotation_scan_qx/`). Ledger row: A5-186.

## What the run measures

The null block b0 (operand e1 + e17, coset 0, 21 routed CZ on q2, q4, q8, q11, q12) reads a raw selector contrast
above zero on Tuna-17 where every arm-symmetric readout and every unital or relaxation channel gives 0: +0.0164 +-
0.0039 in the coin series, +0.0162 +- 0.0028 and +0.0393 +- 0.0028 in the two base batches of the
[one-CZ case](../pathion_one_cz_null_tuna_17/CASE.md). That case's 6-CZ blocks read -0.0007 +- 0.0013
(`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, `m_six_cz`), which a coherent pulse error
and a selector flip conditioned on q12 both predict, and its replicate gate failed on b0 (chi-square 34.9 against
10.83), so row A5-186 stayed a hypothesis.

This case separates the two on b0 itself. Tuna-17 runs `X90` and `Rx` as native single-qubit operations of one 20 ns
duration and quantizes a rotation angle to a pi/36 grid (`docs/notes/quantum_inspire/cqasm.md`;
`docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md`). Replacing an `X90` by
`Rx(pi/2 + k pi/36)` adds a known rotation of 5k degrees about the pulse axis and leaves the schedule, the CZ count
and every other instruction unchanged. A pulse that already over-rotates by theta then rotates by pi/2 + theta + k pi/36, so the selector
contrast as a function of k is the pulse-error response curve shifted by theta. A readout mechanism leaves the curve
of an exact pulse in place and adds its offset. b0 holds 49 pulses: 34 on q8, 8 on q4, 5 on q12, 1 on q2, 1 on q11.

Predicted raw selector contrast per arm, each world sized to the center contrast +0.0164 at retention 0.505 and the
coin series' readout rates (`prediction.json`, `predicted_contrast`, which lists every world and branch):

| world | all -10 | all -5 | center | all +5 | all +10 | q8 -10 | q8 -5 | q8 +5 | q8 +10 |
|---|---|---|---|---|---|---|---|---|---|
| exact circuit, no offset | +0.0281 | -0.0007 | 0 | +0.0315 | +0.0636 | -0.0092 | -0.0157 | +0.0159 | +0.0131 |
| x rotation +0.0511 rad on every pulse | +0.0092 | -0.0050 | +0.0164 | +0.0523 | +0.0727 | -0.0310 | -0.0137 | +0.0313 | +0.0191 |
| x rotation -0.1438 rad on every pulse | +0.0633 | +0.0477 | +0.0164 | -0.0049 | +0.0088 | +0.0671 | +0.0415 | +0.0006 | -0.0087 |
| x rotation +0.0924 rad on q8's pulses | +0.0057 | -0.0019 | +0.0164 | +0.0398 | +0.0472 | -0.0152 | +0.0012 | +0.0123 | -0.0112 |
| y rotation +0.0655 rad before every pulse | +0.0547 | +0.0221 | +0.0164 | +0.0449 | +0.0808 | +0.0127 | +0.0027 | +0.0375 | +0.0451 |
| selector flip when q12 reads 0, x 0.0358 | +0.0381 | +0.0142 | +0.0164 | +0.0450 | +0.0718 | -0.0005 | -0.0009 | +0.0295 | +0.0216 |
| selector dropout when the coin reads 1, x 0.0360 | +0.0439 | +0.0158 | +0.0164 | +0.0469 | +0.0781 | +0.0073 | +0.0010 | +0.0321 | +0.0296 |

The standard error of one contrast at 131,072 shots is 0.0028. At -5 degrees on every pulse the x over-rotation and
the q12 flip sit 0.019 apart, and the two x branches sit 0.053 apart. At +10 degrees on q8 the y rotation sits 0.016
above the dropout and 0.024 above the q12 flip, which the +-5 degree arms leave within 0.008.

hypothesis: `Rx(pi/2 + k pi/36)` is the X90 pulse at a scaled amplitude, so it carries the X90 pulse's error. The
bridge batches test the k = 0 case, `Rx(pi/2)` against `X90`, inside one batch; the provider documents both as native
and publishes no pulse shapes.

Noise model. b0's visibility on Tuna-17 is 0.44 where the exact circuit gives 0.88. The fit contracts each law by one
retention per batch, set by the center arm's visibility, and by one contraction share for the series: the part of
the visibility loss that depolarizes the three data bits alone and leaves the selector and coin law (share 1), the
rest contracting the whole law toward uniform (share 0). The share decides how far the offset and its response to
the injected rotation shrink with the visibility, and the scan fits it. The table above is drawn at share 0. Row
A5-186's "+0.03 rad" comes from a model that contracts nothing (visibility 0.86,
`docs/evidence/pathion-kernel-map/conjectures/c2_tuna_mech.txt`); at the observed visibility the same offset needs
+0.0511 rad at share 0 and +0.0294 rad at share 1, so the fitted angle is read together with the fitted share. A
noise channel that reshapes the response curve in another way is outside the model and shows as an inadequate best
world.

### Circuits

Every circuit measures all 17 qubits and is the retained b0 text with its pulse lines rewritten and its comment line
naming the arm; the emitter reproduces `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte from the parsed instruction list.

- `b0`: the retained circuit, every pulse an `X90`.
- `b0-rx`: every `X90` as `Rx(pi/2)`. This is the center arm of every scan batch.
- `b0-rx-all-m5`, `-p5`, `-m10`, `-p10`: every pulse at 85, 95, 80 and 100 degrees.
- `b0-rx-q8-m5`, `-p5`, `-m10`, `-p10`: q8's 34 pulses at 85, 95, 80 and 100 degrees, `Rx(pi/2)` elsewhere.

### Batches

21 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch, so each data batch sits between two brackets. The ten data batches run at 131,072 shots
per circuit:

- forward round: all +-5, q8 +-5, q8 +-10, all +-10 (each [minus arm, `b0-rx`, plus arm]), bridge [`b0`, `b0-rx`,
  `b0`];
- mirror round: bridge [`b0-rx`, `b0`, `b0-rx`], then all +-10, q8 +-10, q8 +-5, all +-5, each [plus arm, `b0-rx`,
  minus arm].

Each scan batch carries its own center, and the fit takes one parameter per batch, so a drift of the offset between
batches (0.0162 to 0.0393 in the one-CZ series) changes no within-batch comparison. The QX twin holds the ten
distinct circuits in four batches of at most 3 at 2,048 shots.

## Why simulation cannot answer it

The simulation fixes what each mechanism predicts (the table above). Which one the device obeys is a device fact:
the X90 calibration of Tuna-17 and the conditional misassignment of the selector are not published, and a noise
simulation of an unknown calibration reproduces any row.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12, the region of the coin and one-CZ series (q15
  and q13 stay out). QX emulator (type 1) for the twin.
- Jobs and shots: 52 jobs in 21 batches, 4,653,056 shots, every job at or under 131,072 shots. The longest job takes
  about 80 s (2.6 s plus 0.59 ms per shot, the coin series' largest rate; 92 s at the 0.7 ms planning rule of
  `docs/notes/quantum_inspire/usage.md`) against the 300 s job limit. The x rows of the operating characteristics
  need fewer shots; 131,072 is set by the separation of the readout worlds from the y rotation.
- Expected time: 43 to 48 minutes of execution (2,601 to 2,883 s), 20 pauses of 30 s (600 s) between batches, plus
  queue time. QX twin: 10 jobs of 2,048 shots.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  (`docs/notes/quantum_inspire/usage.md`, "Queue rules: the FAQ governs"); `qi_platform.py submit` refuses a larger
  hardware batch, a second queued batch and an early submission before any remote write.
- Quota and credits: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this
  account; expected credits 0.

## Preregistered decision rules

The raw counts are read; Z = 3 standard errors.

1. Guard: a data batch is admitted when e01 and e10 of each of the five region qubits change by at most 0.02
   between the readout batch before it and the one after. The decision needs at least one admitted batch of each
   scan kind (all +-5, q8 +-5, q8 +-10, all +-10); otherwise it reads `unresolved_guard`.
2. Control: the inverse-variance mean of the center arm's contrast over the admitted scan batches exceeds 3 standard
   errors. Within 3 standard errors of zero it reads `offset_absent`, below that `offset_reversed`.
3. Fit: per admitted scan batch, world and contraction share, the least chi-square of the batch's three contrasts
   over the world's one parameter, at the retention that reproduces the center arm's visibility through the mean
   assignment matrix of the two brackets. A world's chi-square is the sum over the admitted scan batches at the one
   contraction share (0 to 1 in steps of 1/12) that makes the sum least. Worlds: a rotation about x on the pulses
   of all qubits, of q8 or of q4; a rotation about y or z before or after the pulses of the same scopes; a selector
   flip when q12 reads 0; a selector dropout when the coin reads 1. The "after" worlds repeat the "before" worlds
   (about z the two give one law, about y the same law at the opposite angle).
4. Adequacy: a world is adequate when its chi-square is at most the 0.999 quantile of the chi-square law with two
   degrees of freedom per admitted batch less one for the share (37.70 for eight batches).
5. Class: the x class, the y-or-z class and the readout class are compared by their best worlds. A class is
   preferred when its best world is adequate and the best world of each other class sits at least 25 above it. The
   x class is excluded when the other two classes lead, the leader is adequate and the best x world sits at least
   25 above it.
6. Bridge: `Rx(pi/2)` reproduces `X90` when the within-batch difference of the `b0-rx` and `b0` contrasts, pooled
   over the two bridge batches, both admitted, is within 3 standard errors of zero. A class label of rule 5 stands
   only when the bridge holds. When the two read different contrasts, or a bridge batch fails admission, the series
   reads `unresolved_bridge`, reports the class of the Rx circuits as `rx_label` and leaves A5-186 unchanged. The
   pooled difference has a standard error of 0.0024, so the bridge resolves a difference of 0.007, 0.4 of the
   offset; a smaller difference between the two gates passes it.
7. Reading of `pulse_x` on A5-186, which names one over-rotation of the X90 pulse: the row survives when the best x
   world rotates every pulse and every admitted batch fits a positive angle. Any other x fit (an under-rotation,
   q8's pulses alone, signs that differ between batches) amends the row.

The adequacy bound and the separation are design thresholds. The retention is plugged in from the center arm, each
class enters by its least chi-square over several worlds, and each batch takes its own parameter, so the sum is a
chi-square with 15 degrees of freedom only approximately; the operating characteristics below state the error rates
the two thresholds give at the design values. A per-batch parameter tests the shape of the response in each batch;
the analysis reports the fitted parameter of every batch (`best_parameters`), and their agreement across batches is
read from that list, outside the decision.

| label | outcome | effect on A5-186 |
|---|---|---|
| `pulse_x`, every pulse, positive angle in every batch | the x class is preferred: the offset follows the injected rotation as an over-rotation of every pulse predicts | survives; the fitted angle and contraction share are reported beside the row's +0.03 rad |
| `pulse_x`, any other fit | the x class is preferred with an under-rotation, on q8's pulses alone, or with signs that differ between batches | amended: a rotation about x stands, and its sign or scope differs from the row's; the scope is the best single-scope world, with its lead over the next (`x_scope_margin`) |
| `pulse_other` | the y-or-z class is preferred | amended: a coherent gate error stands, a pulse rotation about y or z or a CZ phase error |
| `readout` | the readout class is preferred | refuted as stated |
| `x_excluded` | no x rotation reproduces the scan; readout map and y-or-z rotation are closer than the separation | refuted as stated; the surviving mechanism is undecided |
| `offset_absent`, `offset_reversed` | the center contrast reads within 3 standard errors of zero, or below it | unchanged |
| `unresolved_bridge` | the Rx circuits are classed and their transfer to the retained X90 circuit is not shown | unchanged |
| `unresolved_both`, `unresolved_none`, `unresolved_guard` | numbers reported | unchanged |

### Operating characteristics

`prediction.json` (`operating_characteristics`): 10,000 simulated series per truth, Gaussian contrasts at the design
standard error, decided by rules 2 to 5 with every batch admitted; `--operating-characteristics` repeats it (about
twelve minutes on the six cores of the build host, as the on-demand gate
`core-pathion-null-rotation-scan-case-replay` of `ci/gates.json`). Share of runs per label; each cell gives the truth at contraction share 0 and, after
the slash, at share 1:

| truth (center contrast +0.0164) | `pulse_x` | `pulse_other` | `readout` | `x_excluded` | undecided |
|---|---|---|---|---|---|
| x over-rotation, all pulses | 0.9988 / 0.9983 | 0 / 0 | 0 / 0 | 0 / 0 | 0.0012 / 0.0017 |
| x under-rotation, all pulses | 0.9987 / 0.9992 | 0 / 0 | 0 / 0 | 0 / 0 | 0.0013 / 0.0008 |
| x over-rotation, q8 pulses, lower root | 0.9994 / 0.1077 | 0 / 0 | 0 / 0 | 0 / 0 | 0.0006 / 0.8923 |
| x over-rotation, q8 pulses, upper root | 0.8509 / 0.9990 | 0 / 0 | 0 / 0 | 0 / 0 | 0.1491 / 0.0010 |
| x under-rotation, q8 pulses | 0.9984 / 0.9985 | 0 / 0 | 0 / 0 | 0 / 0 | 0.0016 / 0.0015 |
| y rotation before, all pulses | 0 / 0 | 0.9879 / 0.9993 | 0 / 0 | 0.0114 / 0 | 0.0007 / 0.0007 |
| z rotation before, all pulses | 0 / 0 | 0.9921 / 0.2704 | 0 / 0 | 0 / 0 | 0.0079 / 0.7296 |
| selector flip when q12 reads 0 | 0 / 0 | 0 / 0 | 0.9972 / 0.9987 | 0.0019 / 0 | 0.0009 / 0.0013 |
| selector dropout when the coin reads 1 | 0 / 0 | 0 / 0 | 0.8752 / 0.9970 | 0.1239 / 0.0022 | 0.0009 / 0.0008 |
| no offset | 0 | 0 | 0 | 0 | 0.0013; `offset_absent` 0.9971; `offset_reversed` 0.0016 |

None of the simulated runs reads a class other than its truth's: among 10,000 runs per truth and share, no truth
outside the x class reads `pulse_x`, and no x truth reads `pulse_other`, `readout` or `x_excluded`. An over- or
under-rotation of every pulse, the mechanism A5-186 names and its mirror, reads `pulse_x` in at least 99.8 percent
of runs at either share. Three truths are left undecided (`unresolved_both`) in a large part of the runs, because
the fitted share lets a neighboring class come within the separation: the lower q8 over-rotation at share 1 (89
percent), the z rotation at share 1 (73 percent) and the upper q8 over-rotation at share 0 (15 percent). The
dropout at share 0 reads `x_excluded` in 12 percent, which gives A5-186 the same verdict as `readout`. With the
mirror round sized to +0.0393 at share 0, every truth with an offset reads its class in at least 99.7 percent.

The simulation holds the retention and readout at their design values, admits every batch, leaves the bridge out and
draws no drift inside a batch.

### Mechanisms outside the modeled worlds

- A conditional-phase error of the CZ gates (`prediction.json`, `unmodeled`, noiseless): at +0.08 rad it gives a
  center contrast of +0.0075 and reads `pulse_other`; at -0.08 rad it reads `unresolved_both`, and at +-0.12 rad
  (center +0.0156 and +0.0135) `unresolved_none`. None reads `pulse_x`. The `pulse_other` row of the table above
  therefore names a coherent gate error and leaves a CZ phase error and a y or z pulse rotation apart.
- Rotations about x whose angle differs between qubits: the worlds give one angle to one scope, so a mixture is
  fitted by its nearest single-scope world. The verdict that the error is about x stands on the response to the
  injected rotation; the reported scope is the best single-scope fit.
- A selector or coin readout whose assignment during the b0 circuits differs from the one the bracket circuits read
  (the brackets prepare computational states with no gate history): the brackets and the guard cannot see it. It
  changes the contrasts the fit expects and reads as a worse fit, toward the unresolved labels.
- Visibility loss that follows neither kind of the noise model, or a contraction share that changes between
  batches: the series fits one share, so such a loss shows as a worse fit, toward `unresolved_none`.

## Not built

- Pauli twirling of the CZ gates: the mechanisms under test act on the single-qubit pulses and the selector read,
  and a twirl inserts further pulses that carry the same error.
- A rerun of the 6-CZ blocks: every surviving mechanism predicts zero there, and the retained run reads zero.
- An arm on q4 alone: a rotation about x on q4's 8 pulses gives the center arm a contrast of exactly 0, and under
  the x and readout worlds of the table the two q4 arms at +-5 degrees differ by at most 0.0014, half a standard
  error. The y and z worlds move them further (0.007 under the y rotation of the table), and the q8 +-10 arms
  separate those worlds by more.
- Arms on q12, q2 and q11 alone: they hold 5, 1 and 1 pulses, too few for a +-5 degree arm to resolve.

## Submission commands (not run)

The owner's approval is quoted in `--approval`. `scripts/qi_pathion_one_cz_null_submit.sh` submits one batch at a
time and collects it before the next, waits out the pause that `qi_platform.py submit` names, and stops at the first
refusal without a remainder, failed collection or failed sanity check. The per-batch sanity check binds the collected
batch to this case; the readout admission of a data batch needs the bracket after it and is applied by `--analyze`
on the complete series, so the series runs to its end and a batch that fails admission leaves the fit.

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
SCAN=scripts/qi_pathion_null_rotation_scan_cases.py

"$PYTHON" "$SCAN" --check "$CASES"
"$PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: four batches, then the control analysis, which exits 1 unless the series is complete and every circuit
# reads its ideal law; the Tuna-17 lines run only after it exits 0.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_null_rotation_scan_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_rotation_scan_qx-batch-* \
	--out results/quantum_inspire/pathion_null_rotation_scan_qx_analysis.json || exit 1

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

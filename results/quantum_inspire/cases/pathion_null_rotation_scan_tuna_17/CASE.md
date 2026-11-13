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

This case separates the two on b0 itself. Tuna-17 runs `Rx` natively on a pi/36 grid and `Rz` as a frame change of
zero duration (`docs/notes/quantum_inspire/cqasm.md`). Replacing an `X90` by `Rx(pi/2 + k pi/36)` adds a known
rotation of 5k degrees about the pulse axis and leaves the schedule, the CZ count and every other instruction
unchanged. A pulse that already over-rotates by theta then rotates by pi/2 + theta + k pi/36, so the selector
contrast as a function of k is the pulse-error response curve shifted by theta. A readout mechanism leaves the curve
of an exact pulse in place and adds its offset. b0 holds 49 pulses: 34 on q8, 8 on q4, 5 on q12, 1 on q2, 1 on q11.

Predicted raw selector contrast per arm, each world sized to the center contrast +0.0164 at retention 0.505 and the
coin series' readout rates (`prediction.json`, `predicted_contrast`, which lists every world and branch):

| world | all -10 | all -5 | center | all +5 | all +10 | q8 -5 | q8 +5 | q4 -5 | q4 +5 |
|---|---|---|---|---|---|---|---|---|---|
| exact circuit, no offset | +0.0281 | -0.0007 | 0 | +0.0315 | +0.0636 | -0.0157 | +0.0159 | 0 | 0 |
| x rotation +0.0511 rad on every pulse | +0.0092 | -0.0050 | +0.0164 | +0.0523 | +0.0727 | -0.0137 | +0.0313 | +0.0158 | +0.0166 |
| x rotation -0.1438 rad on every pulse | +0.0633 | +0.0477 | +0.0164 | -0.0049 | +0.0088 | +0.0415 | +0.0006 | +0.0167 | +0.0157 |
| x rotation +0.0924 rad on q8's pulses | +0.0057 | -0.0019 | +0.0164 | +0.0398 | +0.0472 | +0.0012 | +0.0123 | +0.0155 | +0.0169 |
| y rotation +0.0655 rad before every pulse | +0.0547 | +0.0221 | +0.0164 | +0.0449 | +0.0808 | +0.0027 | +0.0375 | +0.0126 | +0.0197 |
| selector flip when q12 reads 0, x 0.0358 | +0.0381 | +0.0142 | +0.0164 | +0.0450 | +0.0718 | -0.0009 | +0.0295 | +0.0162 | +0.0162 |
| selector dropout when the coin reads 1, x 0.0360 | +0.0439 | +0.0158 | +0.0164 | +0.0469 | +0.0781 | +0.0010 | +0.0321 | +0.0164 | +0.0164 |

The standard error of one contrast at 131,072 shots is 0.0028. At -5 degrees on every pulse the x over-rotation and
the q12 flip sit 0.019 apart, and the two x branches sit 0.053 apart.

hypothesis: `Rx(pi/2 + k pi/36)` is the X90 pulse at a scaled amplitude, so it carries the X90 pulse's error. The
bridge batches test the k = 0 case, `Rx(pi/2)` against `X90`, inside one batch. The model contracts each law toward
uniform by one retention per batch and fits it to the center arm's visibility; a noise channel that reshapes the
response curve is outside the model and shows as an inadequate best world.

### Circuits

Every circuit measures all 17 qubits and is the retained b0 text with its pulse lines rewritten; the emitter
reproduces `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte from the parsed instruction list.

- `b0`: the retained circuit, every pulse an `X90`.
- `b0-rx`: every `X90` as `Rx(pi/2)`. This is the center arm of every scan batch.
- `b0-rx-all-m5`, `-p5`, `-m10`, `-p10`: every pulse at 85, 95, 80 and 100 degrees.
- `b0-rx-q8-m5`, `-p5` and `b0-rx-q4-m5`, `-p5`: the pulses of one qubit at 85 or 95 degrees, `Rx(pi/2)` elsewhere.

### Batches

21 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch, so each data batch sits between two brackets. The ten data batches run at 131,072 shots
per circuit:

- forward round: all +-5, q8 +-5, q4 +-5, all +-10 (each [minus arm, `b0-rx`, plus arm]), bridge [`b0`, `b0-rx`,
  `b0`];
- mirror round: bridge [`b0-rx`, `b0`, `b0-rx`], then all +-10, q4 +-5, q8 +-5, all +-5, each [plus arm, `b0-rx`,
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
  about 80 s (2.6 s plus 0.59 ms per shot) against the 300 s job limit.
- Expected time: 43 to 48 minutes of execution (2,601 to 2,883 s), 20 pauses of 30 s (600 s) between batches, plus
  queue time. QX twin: 10 jobs of 2,048 shots.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  (`docs/notes/quantum_inspire/usage.md`, "Queue rules: the FAQ governs"); `qi_platform.py submit` refuses a larger
  hardware batch, a second queued batch and an early submission before any remote write.
- Quota and credits: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this
  account; expected credits 0.

## Preregistered decision rules

The raw counts are read; Z = 3 standard errors.

1. Guard: a data batch is admitted when q11's e01 and e10 each change by at most 0.02 between the readout batch
   before it and the one after. The decision needs at least one admitted batch of each scan kind (all +-5, q8, q4,
   all +-10); otherwise it reads `unresolved_guard`.
2. Control: the inverse-variance mean of the center arm's contrast over the admitted scan batches exceeds 3 standard
   errors; otherwise `offset_absent`.
3. Fit: per admitted scan batch and world, the least chi-square of the batch's three contrasts over the world's one
   parameter, at the retention that reproduces the center arm's visibility through the mean assignment matrix of
   the two brackets. A world's chi-square is the sum over the admitted scan batches. Worlds: a rotation about x on
   the pulses of all qubits, of q8 or of q4; a rotation about y or z before or after the pulses of the same scopes; a
   selector flip when q12 reads 0; a selector dropout when the coin reads 1.
4. Adequacy: a world is adequate when its chi-square is at most the 0.999 quantile of the chi-square law with two
   degrees of freedom per admitted batch (39.25 for eight batches).
5. Class: the x class, the y-or-z class and the readout class are compared by their best worlds. A class is
   preferred when its best world is adequate and the best world of each other class sits at least 25 above it. The
   x class is excluded when the other two classes lead, the leader is adequate and the best x world sits at least
   25 above it.
6. Bridge: `Rx(pi/2)` reproduces `X90` when the within-batch difference of the `b0-rx` and `b0` contrasts, pooled
   over the two bridge batches, is within 3 standard errors of zero. A failed bridge leaves the decision in force
   for the Rx circuits and withholds its transfer to the retained X90 circuit.

| label | outcome | effect on A5-186 |
|---|---|---|
| `pulse_x` | the x class is preferred: the offset follows the injected rotation as an over- or under-rotation of the named scope predicts | survives, with the fitted angle and scope |
| `pulse_other` | the y-or-z class is preferred | amended: a coherent pulse error stands, about y or z |
| `readout` | the readout class is preferred | refuted as stated |
| `x_excluded` | no x rotation reproduces the scan; readout map and y-or-z rotation are closer than the separation | refuted as stated; the surviving mechanism is undecided |
| `offset_absent` | the center contrast no longer reads positive | unchanged |
| `unresolved_both`, `unresolved_none`, `unresolved_guard` | numbers reported | unchanged |

### Operating characteristics

`prediction.json` (`operating_characteristics`): 10,000 simulated series per truth, Gaussian contrasts at the design
standard error, decided by the rule above with every batch admitted; `--operating-characteristics` repeats it. Share
of runs per label, stationary truth:

| truth (center contrast +0.0164) | `pulse_x` | `pulse_other` | `readout` | `x_excluded` | undecided |
|---|---|---|---|---|---|
| x over-rotation, all pulses | 0.9994 | 0 | 0 | 0 | 0.0006 |
| x under-rotation, all pulses | 0.9994 | 0 | 0 | 0 | 0.0006 |
| x over-rotation, q8 pulses | 0.9995 | 0 | 0 | 0 | 0.0005 |
| y rotation before, all pulses | 0 | 0.8530 | 0 | 0.1467 | 0.0003 |
| z rotation before, all pulses | 0 | 0.9942 | 0 | 0 | 0.0058 |
| selector flip when q12 reads 0 | 0 | 0 | 0.8388 | 0.1607 | 0.0005 |
| selector dropout when the coin reads 1 | 0 | 0.0001 | 0.4010 | 0.5979 | 0.0010 |
| no offset | 0 | 0 | 0 | 0 | 0.0013; `offset_absent` 0.9987 |

Every truth with an offset reads the correct verdict on A5-186 (survives under an x truth, refuted or amended under
any other) in at least 99.4 percent of runs, and no truth reads `pulse_x` wrongly. The scan separates a readout map
from a y rotation weakly at this offset (the dropout truth reads `readout` in 40.1 percent and `x_excluded` in 59.8
percent of runs), and it reads a dropout truth as `pulse_other` in 0.01 percent. With the mirror round sized to
+0.0393 the dropout truth reads `readout` in 79.6 percent and the q12 flip in 99.8 percent.

The simulation holds the retention and readout at their design values and draws no drift inside a batch, no
bridge failure and no guard failure.

## Not built

- Pauli twirling of the CZ gates: the mechanisms under test act on the single-qubit pulses and the selector read,
  and a twirl inserts further pulses that carry the same error.
- A rerun of the 6-CZ blocks: every surviving mechanism predicts zero there, and the retained run reads zero.
- Arms on q12, q2 and q11 alone: they hold 5, 1 and 1 pulses, too few for a +-5 degree arm to resolve.

## Submission commands (not run)

The owner's approval is quoted in `--approval`. `scripts/qi_pathion_one_cz_null_submit.sh` submits one batch at a
time and collects it before the next, waits out the pause that `qi_platform.py submit` names, and stops at the first
refusal without a remainder, failed collection or failed sanity check.

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
SCAN=scripts/qi_pathion_null_rotation_scan_cases.py

"$PYTHON" "$SCAN" --check "$CASES"
"$PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: four batches, then the control analysis.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_null_rotation_scan_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_rotation_scan_qx-batch-* \
	--out results/quantum_inspire/pathion_null_rotation_scan_qx_analysis.json

# Tuna-17: twenty-one batches in order.
SANITY_COMMAND="$PYTHON $SCAN --sanity" sh scripts/qi_pathion_one_cz_null_submit.sh 7 \
	"$CASES/pathion_null_rotation_scan_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" "$SCAN" --analyze "$RUNS/$STAMP"-pathion_null_rotation_scan_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run
directories, both analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

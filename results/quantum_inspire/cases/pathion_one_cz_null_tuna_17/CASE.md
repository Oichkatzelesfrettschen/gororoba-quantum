# Case: Tuna-17 selector offset of the null block, coin-fixed twins and 6-CZ routing

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_pathion_one_cz_null_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this
directory except this one, and the QX twin `../pathion_one_cz_null_qx/`). Submission:
`scripts/qi_pathion_one_cz_null_submit.sh`. Ledger row: A5-186.

## What the run measures

The coin series read the null block b0 (operand e1 + e17, coset 0, 21 routed CZ) at a raw selector contrast of
+0.0164 +- 0.0039, where every arm-symmetric product readout and every unital or relaxation channel gives 0. Three
mechanisms reproduce the size when each is sized to give b0 +0.0164
(`docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt` and `c2_one_cz_twins.txt`). The prediction columns are
the raw selector contrast of the base circuit (s) and of the coin-twin pair (t, defined below):

| mechanism | b0 s / t | 6-CZ block s / t |
|---|---|---|
| over-rotation: an X-axis rotation of 0.0513 rad added to every X90 and X gate of the routed circuit, Rz exact | +0.0164 / +0.0166 | 0 / 0 |
| selector dropout when the coin reads 1 (an arm-asymmetric readout), x 0.0362 | +0.0164 / +0.0170 | +0.0164 / +0.0170 |
| selector flip when q12 reads 0 (a readout correlation), x 0.036 | +0.0164 / +0.0170 | 0 / 0 |
| hypothesis: an offset that needs the coin in superposition (no simulation) | +0.0164 / 0 | not predicted |

The over-rotation model is named exactly: `c3_mech2.simulate` multiplies each X90 and X gate by an X rotation of the
stated angle, before the gate in time, and leaves Rz exact. The robustness replay (`c2_one_cz_twins.txt`, section 4)
repeats it about X, Y and Z, before and after the gate in time, on the pulse gates X90 and X (the admitted set; hypothesis:
Rz is a frame change, not a pulse), with the angle sized to b0 wherever |angle| <= 0.15 rad reaches +0.0164: the largest
6-CZ response over the 12 admitted sized models is 0.0038 (base) and 0.0039 (twin), so "zero" below means within three
standard errors of zero and the over-rotation's bounded prediction is |6-CZ contrast| <= 0.0039. A rotation added to
every single-qubit gate including Rz is outside the admitted set; it reaches 0.0076 and 0.0103.

A 1-CZ test does not exist on this device: a coin block compiles to 3 CZ at all-to-all connectivity, and with b0's whole
role map held it routes to 12 CZ, where the over-rotation itself predicts +0.028 (0.0279 to 0.0549 over every candidate
of the search). With only the selector on q8 and the coin on q2 held (data qubits d0 q4, d1 q12, d2 q11), the blocks k4,
k8 and k12 route to 6 CZ.

### Circuits

Every circuit measures all 17 qubits. A coin-fixed twin is the routed template with the coin's first single-qubit run (the
template's Hadamard, checked to equal H up to a global phase) removed and the coin prepared in |0> (nothing) or |1>
(one X): every other instruction, the CZ count and the schedule of the other qubits are byte-identical. Twin pair
contrast t = P(s = 0) of the coin-1 twin minus that of the coin-0 twin; base contrast s = P(s = 0 | coin read 1) -
P(s = 0 | coin read 0). A twin has a classical coin, so it shows a selector response conditioned on the coin inside the
template's own gate sequence and shows no arm-label error.

- Batches 00-15 (16 template batches, mirrored order): for b0, k4, k8, k12, two base batches [readout-0, template,
  readout-1] and two twin batches (the forward round [readout-0, coin-0 twin, coin-1 twin], the mirror round
  [coin-1 twin, coin-0 twin, readout-1]). Circuits run at 32,768 shots, b0's base circuit at 65,536. The second round
  repeats the first in reverse (b0 base, b0 twin, k4 twin, k4 base, k8 base, k8 twin, k12 twin, k12 base, then the same
  list backwards), so each template's base and twin batches sit at mirrored positions and a linear drift cancels between
  replicates. b0 is `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte (the transpiler seed and role map of the
  coin series).
- Batches 16-18: the eight X-only preparations of (q2, q8, q12), every other register qubit in |0>, at 16,384 shots, as a
  secondary readout calibration (terminal-assignment context only). The two coin values of a prepared selector 1 meet
  at equal q12 inside one batch.
- The routing seeds are values 0, 64 and 128 of `docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json`; the operating
  characteristics are seeded from value 0 of `docs/evidence/anu_qrng/draw-2026-11-07T185234Z.json`.
- QX twin: every base circuit and twin (12 circuits) in three batches of 5, 5 and 2 at 2,048 shots.

### What the twins can and cannot separate

`c2_one_cz_twins.txt` (section 2) lists the predicted s and t of every template under every mechanism and the separation
at the planned shots. The 6-CZ base and twin contrasts separate the dropout from the over-rotation and from the q12 flip:
13 standard errors for their combination m, 7.4 for the base contrast and 10.7 for the twin contrast alone. b0's twin
separates no pair of modeled mechanisms, since all give it the base value; it is a control that exposes an offset
needing the coin superposition. No twin separates the over-rotation from the q12 flip: both give the 6-CZ blocks zero.
A twin with the data qubit d1 (the role q12 holds in the 6-CZ blocks) fixed leaves P(s = 0) at 1/2 under the q12 flip
(section 3), so it separates nothing and is not built; b0 has no such variant, because the first single-qubit run on the
qubit that starts d0 holds four gates (the data Hadamard mixed with later rotations), so fixing d0 changes the gate
sequence. The q12 correlation therefore rests on the X-only calibration alone, which measures a terminal-assignment
context and changes no outcome label.

## Why simulation cannot answer it

The simulation fixes what each mechanism predicts (the table above). Which one the device obeys is a device fact: the
X90 calibration of Tuna-17 and the conditional misassignment of the selector given the states of the coin and of q12 are
not published, and the retained readout circuits excite all 17 qubits, so they cannot separate a conditional effect from
the context of the others. A noise simulation of a calibration that is not known reproduces any of the three.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7, `tuna_17`), region q2, q4, q8, q11, q12 (the excluded qubits of the coin series, q15 and q13,
  stay out). QX emulator (type 1) for the twin.
- Jobs and shots: 56 jobs in 19 batches of at most 3 circuits, 1,900,544 shots in all, every job at or under 131,072
  shots and the 300 s job limit. The power rule below raised b0's base circuits from 32,768 to 65,536 shots, which added
  196,608 shots and about 110 s of execution.
- Expected time: about 19 to 21 minutes of execution (1,153 to 1,268 s: 2.6 s per job plus 0.53 ms per shot, and the
  coin series' 0.59 ms per shot), 18 pauses of 30 s between batches, plus queue time.
- Quota: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this account.

## Preregistered decision rules

Z = 3 standard errors. The raw counts are read.

1. Estimates: each batch gives a base contrast (value, binomial se) or a twin contrast; replicate batches of one template
   and kind pool by inverse variance. Pooled standard errors: b0 base 0.0028 and twin 0.0028; each 6-CZ base 0.0039 and
   twin 0.0028.
2. Heterogeneity (before any class): replicate batches of one template and kind must agree within chi-square 10.83 (1
   degree of freedom, alpha 0.001 across the eight comparisons); the three 6-CZ blocks must agree within chi-square 9.21
   (2 degrees of freedom, alpha 0.01) for the base contrasts and for the twin contrasts. Otherwise the decision is
   unresolved, so opposite or single-block responses never pool into a class.
3. Control: b0's base contrast s0 above 3 se, otherwise "offset absent" and nothing about the mechanism is decided.
4. Twin control: b0's twin contrast t0 above 3 se; if not, and s0 - t0 exceeds 3 combined se, the offset exists only with
   the coin in superposition, otherwise unresolved.
5. 6-CZ class: c and d the pooled 6-CZ base and twin contrasts, m their inverse-variance combination (se about 0.0013),
   r the combination of s0 and t0. The contexts disagree when |c - d| exceeds 3 combined se (unresolved). Zero when |m|
   is within 3 se and r - m exceeds 3 combined se; b0-like when m exceeds 3 se and |r - m| is within 3 combined se;
   otherwise unresolved.

| class | outcome | effect on A5-186 |
|---|---|---|
| zero | 6-CZ blocks read zero in both contexts: the coin-conditioned dropout is excluded; the over-rotation and the q12 correlation remain and these observables do not separate them | survives: its falsifier, a resolved nonzero 6-CZ response inconsistent with the model's bounded prediction of zero (|contrast| <= 0.0039), is unmet; the q12 correlation stays open |
| b0-like | 6-CZ blocks read the b0 value in both contexts: consistent with the coin-conditioned dropout; the over-rotation and the q12 correlation are excluded | refuted as stated: the resolved 6-CZ response is inconsistent with the bounded prediction of zero |
| superposition only | b0's classical-coin twin reads below its base contrast | refuted as modeled: the over-rotation predicts the offset in the twin as well |
| offset absent | b0's base contrast no longer reads positive | unchanged |
| any other | unresolved, numbers reported | unchanged |

The X-only calibration reports D (selector misassignment with the coin prepared 1 minus 0 at a prepared selector 1, from
the two matched pairs inside a batch) and G (with q12 prepared 0 minus 1), each as large (>= 0.036 - 3 se) or small
(|.| + 3 se < 0.012), beside the outcome; it does not change it. Labels read "consistent with" the implemented exclusive
models: a mixture of mechanisms, an effect that appears only after the template's CZ and X90 schedule, leakage or
relaxation on the coin edge, and drift between the batches are not fitted.

### Operating characteristics

`prediction.json` (`operating_characteristics`; 20,000 simulated series per world drawn at the design standard errors and
decided by the rule above, so every gate and comparison counts; `--operating-characteristics` repeats it). Share of runs
that read each row:

| world | zero | b0-like | superposition only | offset absent | unresolved (all kinds) |
|---|---|---|---|---|---|
| over-rotation (X axis) | 0.963 | 0 | 0.0002 | 0.0014 | 0.035 |
| q12 correlation | 0.967 | 0 | 0.0001 | 0.0020 | 0.031 |
| coin-conditioned dropout | 0 | 0.965 | 0.0002 | 0.0019 | 0.033 |
| superposition-only offset | 0 | 0 | 0.858 | 0.0016 | 0.140 |
| no offset | 0 | 0 | 0.0003 | 0.972 | 0.028 |
| worst admitted over-rotation (Y axis, 6-CZ 0.0038 / 0.0039) | 0.496 | 0.008 | 0.0001 | 0.0013 | 0.495 |

The chance that a run decides nothing is the sum of the unresolved and offset-absent shares: 3.7 percent
(over-rotation), 3.5 percent (dropout), 3.3 percent (q12 correlation), 14 percent (superposition only) and 50 percent
(the worst admitted over-rotation about another axis, which reads b0-like, a wrong row, in under one percent of runs).
The over-rotation world decides in 96.3 percent of runs, above the 80 percent the power rule asks, so the shots stay as
listed. With an extra independent batch drift of 0.003 (55 percent of a base batch's standard error) the over-rotation
world reads zero in 0.831 of runs, the dropout world b0-like in 0.833 and the q12 world zero in 0.833, and 0.165 to 0.168
of runs decide nothing.

## What made the coin series succeed, and its challenges

- Coin interleaving of both arms in one job: one routed CZ puts both orientation arms into every shot, so one job, one
  routing and one calibration carry the contrast (the series' resolution, pattern and cocycle-free decisions all held:
  `ba` selector 0.2350 +- 0.0038, `xor_ba` -0.7181 +- 0.0054).
- A readout-0 and readout-1 bracket in every data batch: a drift between batches is a stratum to correct, not a stop.
  The stopped predecessor halted on q11 e10 moving from 0.2762 to 0.1066 (limit 0.02).
- Region exclusions: q15 (P(0|1) 0.270) and q13 (its |1> misassignment doubles beside an excited q11) are left out, and
  the five-qubit region keeps every coupler under the residual coupling limit.
- Challenges: the null block read +0.0164 where every symmetric channel gives 0; the readout-corrected agreement with
  IBM failed on `ba` bins 1, 5 and 7 (the misses follow the logical bit d2, `c3_walsh.txt`); the retained readout
  circuits excite all 17 qubits and cannot assign a cause to the offset, which the coin-fixed twins now test inside the
  template; the offset itself may drift between 2026-11-07 00:10Z and the run, which the control reads.

## IBM reference for the same question

`results/live/pathion_parallel_coset_analysis.json` and `d1_ibm_overrotation.txt` on branch
`pathion/interpret-tuna-ascella-runs` (ibm_fez 17 and ibm_kingston 16 parallel placements): the 20-CZ k0 selector contrast
reads -0.0020 +- 0.0015 and -0.0000 +- 0.0011, and the coin-free 1-CZ blocks average -0.0008 +- 0.0007 and -0.0001 +-
0.0010. IBM shows no over-rotation (-0.0036 +- 0.0027 and -0.0000 +- 0.0019 rad; pooled with the earlier two readings
-0.0015 +- 0.0014 rad, 4.3 combined standard errors below the Tuna angle +0.0295 +- 0.0070 rad, under the 0.57 per rad
response of the written k0 compile; no ibm_kingston compile was simulated).

## Not built

- The Ry emulator: the circuits are expressible (X90 as Rx(pi/2), CZ as H-CNOT-H on `qubit[5]` with no bit register and
  no measure statement, qubit 0 leftmost), but a coarse +-0.03 check at 3 se needs 9 jobs of 1,024 shots per template
  (27 jobs of 16 s in 9 batches on the shared hardware pause, about 12 minutes) on a noise model that is undocumented,
  so it is left out with this reason.
- A data-qubit-fixed twin (see above) and a model of a physical Rz pulse error.

## Submission commands (not run)

The owner's approval is quoted in `--approval` (written case: what it measures, why simulation cannot answer it, the
backend, shots and expected seconds above; no credits). The script `scripts/qi_pathion_one_cz_null_submit.sh` submits one
batch at a time and collects it before the next, so at most one batch of the account is queued. When `qi_platform.py
submit` refuses with "wait N more seconds" it sleeps N + 1 seconds and retries, at most ten refusals per batch; it stops
at the first refusal that names no remainder, the first failed collection or sanity check, and the tenth refusal.

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)

"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --check "$CASES"
"$QI_PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: three batches, then the control analysis.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_one_cz_null_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_qx-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_qx_analysis.json

# Tuna-17: nineteen batches in order.
sh scripts/qi_pathion_one_cz_null_submit.sh 7 "$CASES/pathion_one_cz_null_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run directories,
both analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

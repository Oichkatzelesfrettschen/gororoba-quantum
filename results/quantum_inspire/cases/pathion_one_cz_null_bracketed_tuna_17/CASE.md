# Case: Tuna-17 selector offset of the null block, bracketed coin twins and rule v2

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_pathion_one_cz_null_bracketed_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../pathion_one_cz_null_bracketed_qx/`). Submission:
`scripts/qi_pathion_one_cz_null_submit.sh` with `SANITY_COMMAND` set to the successor's `--sanity`. Ledger row: A5-186.
The predecessor case `../pathion_one_cz_null_tuna_17/` (producer `scripts/qi_pathion_one_cz_null_cases.py`) keeps its
bytes; this case imports its circuit texts, twins, readouts and calibration circuits.

## What the run measures

The question and the three mechanisms are the predecessor's: the null block b0 (operand e1 + e17, 21 routed CZ) reads a
raw selector contrast of +0.0164 +- 0.0039 where every arm-symmetric product readout and every unital or relaxation
channel gives 0, and the over-rotation, the coin-conditioned selector dropout and the q12 flip each reproduce it
(`docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt`, `c2_one_cz_twins.txt`; predicted contrasts in the
predecessor's CASE.md and in `prediction.json` here, `predicted_contrast`, in ten-thousandths). The decision uses the
predecessor's thresholds, heterogeneity gates and b0-like band; it differs in two places the owner ruled on 2026-11-14
(issue 791 items 1 to 3):

- every coin twin runs between its own readout-0 and readout-1, and its contrast is read against that bracket;
- twin-control rule v2 (`scripts/qi_pathion_one_cz_null_rule_v2.py`) and the finite-count error of a deterministic arm
  (`scripts/qi_pathion_one_cz_null_analysis.py`, `arm_variance`) are preregistered from the start.

## Derived coefficients and the design they force

Each coefficient is re-derived in `tests/scripts/test_qi_pathion_one_cz_null_bracketed.py`.

1. Three circuits per batch. `docs/notes/quantum_inspire/usage.md` ("Queue rules: the FAQ governs") reads the FAQ's three
   queued jobs per hardware backend and says it does not settle whether a job is a circuit; the runner holds a batch to
   `HARDWARE_BATCH_CIRCUITS` (3, `scripts/qi_platform.py`). A twin pair plus a bracket is four circuits, so
   `[readout-0, coin-0 twin, coin-1 twin, readout-1]` is refused, and each twin runs as `[readout-0, twin, readout-1]`
   with the two twins of a pair in adjacent batches.
2. Ideal selector marginal. Every twin of the predecessor case (b0, k4, k8, k12 at coin 0 and 1) has ideal
   P(s = 0) = 1/2 exactly (the `ideal` rows of its `batch-*/cases.json`, selector at index 3 of the five logical bits,
   little-endian); the same holds for the twins here.
3. Readout model. With e01 = P(read 1 | prepared 0) from readout-0 and e10 = P(read 0 | prepared 1) from readout-1 of the
   selector (physical q8), a raw reading of P(s = 0) is P = e10 + lambda p with lambda = 1 - e01 - e10, so
   P - 1/2 = lambda (p - 1/2) + (e10 - e01) / 2. The readout-0 circuit leaves all 17 qubits in |0>; the readout-1
   circuit excites the five region qubits q2, q4, q8, q11 and q12 and leaves the other twelve in |0>.
4. Split-pair hazard, which falsifies a raw contrast of two twins from two batches. The retained one-CZ series reads the
   selector's e01 between 0.0254 and 0.0310 over its twelve readout-0 references (chi-square 84.4 about the mean on 11
   degrees of freedom) and e10 between 0.0275 and 0.0322 over twelve readout-1 references (chi-square 58.0 on 11), and
   adjacent batches step by about 0.005 (batch-02 to batch-03 and batch-07 to batch-08 of that series;
   `results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, `drift_covariate.references`, measured on
   Tuna-17, 2026-11-07). A raw contrast of twins from two batches carries [(e10 - e01)_1 - (e10 - e01)_0] / 2, about
   0.0025, roughly 0.9 pooled twin standard errors.
5. Twin estimator. The bracket offset of a batch is c = (e10 - e01) / 2, a twin reading is P - c, and the twin contrast of
   one replicate is t = (P1 - c1) - (P0 - c0) over the coin-1 and coin-0 batches.
   - Equal brackets reduce it exactly to the raw P1 - P0, the predecessor's statistic.
   - Its expectation is lambda1 (p1 - 1/2) - lambda0 (p0 - 1/2): the raw scale of the predicted contrasts and of the
     raw base contrasts, so the r and c - d comparisons mix no scales; the lambda spread residual is under 5e-5.
   - It is linear in the measured rates, so its variance is exact: var t = v(P1) + v(P0) + [v(e10_1) + v(e01_1) +
     v(e10_0) + v(e01_0)] / 4, each v the arm variance of a rate over its shots (`arm_variance`, the Agresti-Coull
     interval variance at a deterministic arm, issue 791 item 3, which QX readouts exercise since they misassign no
     shot).
   - Design standard error at 32,768 shots per circuit, P = 1/2 and the retained means e01 = 0.0281, e10 = 0.0296: per
     twin reading variance 7.629e-6 + 4.27e-7, contrast se 0.004014 (raw 0.003906, +2.8 percent), pooled over two
     replicates 0.002838 (`design`: `twin_batch_se_micro` 4014, `pooled_se_micro.twin` 2839, which rounds the unrounded
     2838.4 up).
   - A coin-conditioned selector dropout acts on the coin-1 twin's own shots; both brackets carry the same readout
     contexts (readout-0 all qubits 0, readout-1 the five region qubits excited), so c1 - c0 has expectation 0 under any
     context bias the brackets share, and the dropout's twin contrast (+0.0170 at the sized model) survives.
6. Order. The forward round is b0 base, b0 twin coin 0, b0 twin coin 1, k4 twin coin 0, k4 twin coin 1, k4 base, k8
   base, k8 twin coin 0, k8 twin coin 1, k12 twin coin 0, k12 twin coin 1, k12 base (12 batches); the mirror round is
   that list reversed, so the coin-1 twin precedes the coin-0 twin there and a linear drift g per batch enters the two
   replicates as +g and -g and cancels in the pooled twin contrast. The three X-only calibration batches of the
   predecessor follow (3, 3 and 2 circuits): 27 batches. b0 is `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte,
   as in the predecessor.
7. Shots and time. Base batches run at the predecessor's shots (b0 base batches 131,072 per circuit, other base batches
   32,768), twin batches at 32,768 per circuit, calibration at 16,384. Jobs: 80 (8 base x 3, 16 twin x 3, 8
   calibration); shots 3,080,192 (predecessor: 56 jobs, 2,293,760).

### Designs rejected

- The pair-plus-bracket batch (item 1) and the single-ended layout of the predecessor: the first exceeds the batch limit,
  the second leaves the bracket spread of item 4 uncorrected (it is a hazard the retained series measured, not a
  decided bias).
- A mid-circuit selector reference or a measured classical coin in the twin: either adds a measurement on the coin edge,
  which is a coin-conditioned readout channel, the mechanism under test, and its misassignment is unmeasured on
  Tuna-17.
- A data-qubit-fixed twin, a QX remote run as the decision, and the Ry emulator as the decision: as in the predecessor.

## Circuits and batches

Every circuit measures all 17 qubits. A coin-fixed twin is the routed template with the coin's first single-qubit run (the
Hadamard, checked up to a global phase) removed and the coin prepared in |0> or |1>; the predecessor's `twin_entry`
builds it. Twin contrast t as in item 5; base contrast s = P(s = 0 | coin read 1) - P(s = 0 | coin read 0) as in the
predecessor, read raw.

- Batches 00-23: the 24 template batches of item 6. A base batch is `[readout-0, template, readout-1]`; a twin batch is
  `[readout-0, twin, readout-1]`.
- Batches 24-26: the eight X-only preparations of (q2, q8, q12), 16,384 shots, a secondary readout calibration in a
  terminal-assignment context (D and G of the predecessor, reported beside the outcome).
- The routing seeds are those of the predecessor (values 0, 64 and 128 of
  `docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json`); the operating characteristics are seeded from value 0 of
  `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`.
- QX twin: the 12 data circuits and 8 bracket pairs, 28 circuits in 8 batches (per template one batch
  `[readout-0, coin-0 twin, readout-1, base]` and one `[readout-0, coin-1 twin, readout-1]`) at 2,048 shots. A batch
  keys its circuits by file name, so two bracket pairs cannot share one; the five-circuit service ceiling is not reached.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7), region q2, q4, q8, q11, q12 (as the predecessor); QX emulator (type 1) for the twin.
- Jobs and shots: 80 jobs in 27 batches of at most 3 circuits, 3,080,192 shots, every job at or under 131,072 shots. The
  longest job, a 131,072-shot b0 base circuit, takes 80.0 s (2.6 s plus the coin series' maximum measured 0.5906 ms per
  shot), under the 300 s job limit.
- Expected time: 1,840.5 to 2,027.1 s of execution (80 jobs at 2.6 s plus 0.53 ms to 0.5906 ms per shot), 26 pauses of 30 s
  (780 s) between batches, plus queue time. With the rounded 0.59 ms per shot the upper bound reads 2,025.3 s and the
  longest job 79.9 s.
- Quota: `docs/notes/quantum_inspire/usage.md` records no metered seconds, credits or minutes for this account.

## Preregistered decision rules

Z = 3 standard errors; the raw counts are read. The rule is the predecessor's (items 1 to 5 of its CASE.md, with the
thresholds 10.83 and 9.21 for the heterogeneity gates and `B0_LIKE_Z` 2.0) on the estimates above, with item 4 replaced by
rule v2:

> b0 twin contrast t0 above 3 se; if not, t0 within 3 se of zero (|t0| <= 3 se) and s0 - t0 above 3 combined se, the offset
> exists only with the coin in superposition; t0 below -3 se is unresolved (negative twin); otherwise unresolved.

A t0 below -3 se reads `unresolved_negative_twin`, which decides nothing and leaves A5-186 unchanged. The pooled errors
use `ana.pooled`, which refuses an error that is not positive and finite; a deterministic arm takes the finite-count
interval variance. `prediction.json` (`preregistered`, `outcomes`) holds the text of every row.

### Operating characteristics

`prediction.json` (`operating_characteristics`, shares in ten-thousandths; 20,000 simulated series per world). A base
contrast is a Gaussian draw at the design standard error; each twin batch draws binomial counts of its twin circuit and of
its two readouts at the design rates (P = 1/2 on the corrected scale, e01 = 0.0281, e10 = 0.0296) and the real estimator
reads them, so the bracket noise enters through `twin_reading`. The drift table adds an independent per-batch drift of
0.003 to every base contrast and to every twin reading, so a twin contrast carries sqrt(2) x 0.003 against its standard
error 0.004014. Worlds: the eight of the predecessor and the negative twin. Share of runs that read each row, stationary:

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.964 | 0.000 | 0.001 | 0.001 | 0.000 | 0.000 | 0.034 |
| q12 correlation | 0.966 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.032 |
| coin-conditioned dropout | 0.000 | 0.921 | 0.045 | 0.000 | 0.000 | 0.000 | 0.033 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.933 | 0.002 | 0.000 | 0.065 |
| no offset | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.970 | 0.030 |
| worst admitted over-rotation (Y axis) | 0.521 | 0.000 | 0.446 | 0.001 | 0.000 | 0.000 | 0.032 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.081 | 0.868 | 0.000 | 0.000 | 0.000 | 0.051 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.891 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 | 0.109 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.002 | 0.968 | 0.000 | 0.030 |

Under the case's drift (twin contrast drift 0.0042, base contrast drift 0.003) the shares are:

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.705 | 0.000 | 0.009 | 0.007 | 0.000 | 0.000 | 0.279 |
| q12 correlation | 0.717 | 0.000 | 0.010 | 0.006 | 0.000 | 0.000 | 0.268 |
| coin-conditioned dropout | 0.000 | 0.609 | 0.115 | 0.007 | 0.000 | 0.000 | 0.270 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.650 | 0.015 | 0.000 | 0.335 |
| no offset | 0.000 | 0.000 | 0.000 | 0.004 | 0.000 | 0.738 | 0.258 |
| worst admitted over-rotation (Y axis) | 0.382 | 0.001 | 0.342 | 0.009 | 0.000 | 0.000 | 0.267 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.001 | 0.108 | 0.586 | 0.007 | 0.000 | 0.000 | 0.298 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.603 | 0.000 | 0.001 | 0.007 | 0.000 | 0.000 | 0.389 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.022 | 0.734 | 0.000 | 0.244 |

Stationary, the four deciding worlds decide in 96.4 (over-rotation), 96.6 (q12 correlation), 92.1 (dropout) and 93.3
(superposition-only) percent, within about 0.01 of the predecessor's rule-v2 table, and a negative twin reads
`unresolved_negative_twin` in 96.8 percent of runs and superposition-only in 0.2 percent. A wrong refutation of A5-186 (a
b0-like reading of an over-rotation world) occurs in 8.1 percent of runs of the world that rotates before every
single-qubit gate, Rz included, and in under 0.1 percent of runs of any admitted world.

Under the case's drift the shares fall: the over-rotation and q12 worlds decide in 70.5 and 71.7 percent (predecessor
rule v2: 82.7 and 82.8), the dropout world in 60.9 (72.7) and the superposition-only world in 65.0 (76.8), and
`unresolved_batch` rises to about 0.12 in every world (about 0.07). The cause is the layout: a twin contrast of two batches
carries sqrt(2) x 0.003 of per-batch drift against 0.003 inside one batch, and the replicate heterogeneity gate (10.83, one
degree of freedom) reads that drift as disagreement more often. The dropout and superposition-only worlds fall below the 80
percent the predecessor's power rule asks. The 0.003 is the case's preregistered stress, taken from the retained series'
batch-to-batch spread, not a forecast of the run; stationary, every deciding world exceeds 92 percent. The mirror round
cancels a linear drift in the pooled twin contrast and is not simulated: the drift draws are independent per batch.

## QX and Ry check plan

- QX local (qxelarator 0.10.0 in the Quantum Inspire environment, `docs/notes/quantum_inspire/qx-runs.md`, "Run QX
  locally"; no account, queue or approval). The check reads the QX series through the successor's analyzer
  (`--qx-check`): every data circuit within twice the sampling floor of its ideal law, the selector's readout arms
  deterministic (zero misassigned shots), every bracket offset 0, and the bracketed twin contrast equal to the raw
  contrast. Run on 2026-11-14 at 2,048 shots per circuit over the 28 circuits: all 12 data circuits pass (largest
  total-variation distance 1.84 times its floor; three repeated runs read 1.47, 1.16 and 1.70), no readout shot is
  misassigned, and the four template contrasts agree exactly (b0 0.0078, k4 0.0044, k8 -0.0068, k12 0.0259).
- QX remote (type 1): the same series, a written case for the owner's approval (repository rule), 8 batches.
- Ry (type 5): not built for the decision (predecessor CASE.md, owner decision 2026-11-07: 1,024 shots per job and an
  undocumented noise model). The one Ry check that adds information is the bracket arithmetic on a backend with nonzero
  readout error: a single `[readout-0, twin, readout-1]` triple per coin of b0 on a 5-qubit translation
  (`docs/notes/quantum_inspire/ry-emulator.md`, "Do a Ry emulator run"), whose corrected twin P lands within 3 standard
  errors of 1/2 while the raw P carries (e10 - e01) / 2. Ry is flagged `is_hardware`, so a batch holds 3 circuits. Written
  case, owner approval, not run.

## Residual risk

- The retained b0 base replicates differ: 0.0162 then 0.0393 (se 0.0028 each, 0.0039 for the difference, chi-square
  34.86 > 10.83), so the retained series reads `unresolved_batch`. Hypothesis: a drift of the offset itself, which the
  bracket does not correct (the bracket removes the readout offset, and the offset under test is the quantity that
  drifts); the unchanged heterogeneity gate reads it as `unresolved_batch`.
- A readout-context difference between the two brackets (readout-1 excites the five region qubits only) shifts c1 and c0
  alike, but a context bias that differs between batches is outside the correction.
- The X-only calibration (batches 24 to 26) covers the assignment context; a q12 correlation that appears only after the
  template's CZ and X90 schedule stays open, and no outcome label changes.

## Submission commands (not run)

The owner's approval is quoted in `--approval`. The script submits one batch at a time and collects it before the next;
`SANITY_COMMAND` replaces its default, which belongs to the predecessor's producer.

```sh
export PYTHON="${PYTHON:-python3}"
export QI_PYTHON="${QI_PYTHON:-$HOME/.local/share/quantuminspire/venv/bin/python}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
CASES=results/quantum_inspire/cases RUNS=results/quantum_inspire/runs
STAMP=$(date -u +%Y-%m-%dT%H%M%SZ)
SANITY="$PYTHON scripts/qi_pathion_one_cz_null_bracketed_cases.py --sanity"

"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --check "$CASES"
"$QI_PYTHON" scripts/qi_toolchain_check.py --check

# QX twin: eight batches, then the control analysis.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_one_cz_null_bracketed_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_qx-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json

# Tuna-17: twenty-seven batches in order.
SANITY_COMMAND="$SANITY" sh scripts/qi_pathion_one_cz_null_submit.sh 7 "$CASES/pathion_one_cz_null_bracketed_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run directories, the
analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

# Case: Tuna-17 selector offset of the null block, in-batch bracketed coin twins and rule v2

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
predecessor's thresholds, heterogeneity gates and b0-like band; it differs in three places (owner rulings 2026-11-14,
issue 791 items 1 to 3):

- both coin twins of a template run in one batch between that batch's own readout-0 and readout-1, as
  `[readout-0, coin-0 twin, coin-1 twin, readout-1]` (the mirror round reverses the twins): four circuits per batch,
  which the `wave-v1` hardware policy admits (below);
- twin-control rule v2 (`scripts/qi_pathion_one_cz_null_rule_v2.py`) and the finite-count error of a deterministic arm
  (`scripts/qi_pathion_one_cz_null_analysis.py`, `arm_variance`) are preregistered from the start.

## Hardware policy

The case manifests select `"hardware_policy": "wave-v1"` (`scripts/qi_platform.py`, `HARDWARE_POLICIES`): a hardware batch
holds at most 5 circuits and up to 3 batches may be queued per account and backend type, a wave of 15 circuits in 3
batches, each capped by the live backend record (`max_jobs_per_batch_job`, `batchjobs_per_queue_limit`). A manifest
without the field keeps the legacy policy (3 circuits, 1 queued batch), which refuses a 4-circuit batch. The owner
ruled on 2026-11-14 that "job" in the FAQ's "not more than 3 jobs in the queue for a hardware backend" means a batch job;
the FAQ does not say it (`docs/notes/quantum_inspire/usage.md`, "Queue rules"). Evidence that the service accepts the
numbers: catalogue `max_jobs_per_batch_job` 5 and `batchjobs_per_queue_limit` 5 on every backend type; two retained
Tuna-17 batches of 5 circuits that were accepted and completed (`results/quantum_inspire/runs/2026-10-16T211635Z-tuna_17`,
`.../2026-10-16T221133Z-zero_divisor_tuna_17`); the SDK (`qi_jobs.py`) checks the batch size and nothing about the queue.

A wave is three consecutive batches of the series, listed in the series `cases.json` (`waves`): 7 waves (six of three
batches, a last of one), at most 11 circuits each. `qi_platform.py submit` takes the batches of a wave one after another;
each batch is refused while three batches of the account are in flight on the backend type, and every wave waits for all
its batches to finish and for the pause (`QI_HARDWARE_PAUSE_SECONDS`, the ladder 30, 60, 90, 120 s) before the next.
Submitting a wave's batches in series order requests that order; the service owns the execution order (its terms allow
priority without regard to the queue), so the mirrored layout's cancellation is read from the retained `queued_at` times,
not assumed. An
unfinished job on another hardware backend type refuses the batch, and the pause clock is account-wide across every
`is_hardware` type, the Ry emulator included (`docs/notes/quantum_inspire/ry-emulator.md`), so a finished Ry job delays
the next Tuna-17 batch by the rest of its pause and Ry batches do not count toward the three Tuna-17 batches. The existing
submission script submits and collects one batch at a time, which `wave-v1` admits too, and pays one pause per batch: 18
pauses of 30 s (540 s) for 19 batches. Submitting a wave concurrently (6 pauses, 180 s) is a separate procedure that this
case does not write. The admission checks read one snapshot of the account, and `SUBMIT_LOCK` excludes only sessions on
one host.

Residual risk of the policy: the FAQ sentence is ambiguous. If the provider reads "job" as a circuit, a wave of 15 circuits
queues five times the stated 3; the abuse clause removes the account. The owner accepted that reading for this case; a
provider answer would settle it.

## Derived coefficients and the design they force

Items 2, 3 and 5 are re-derived in `tests/scripts/test_qi_pathion_one_cz_null_bracketed.py`; the retained-record
statistics of item 4 come from the selector counts of the retained run directories named there and are not re-derived by
the tests.

1. Four circuits per batch. A twin pair plus its bracket is four circuits, which the legacy policy refuses and `wave-v1`
   admits (Hardware policy above).
2. Ideal selector marginal. Every twin of the predecessor case (b0, k4, k8, k12 at coin 0 and 1) has ideal
   P(s = 0) = 1/2 exactly (the `ideal` rows of its `batch-*/cases.json`, selector at index 3 of the five logical bits,
   little-endian); the same holds for the twins here.
3. Readout model. With e01 = P(read 1 | prepared 0) from readout-0 and e10 = P(read 0 | prepared 1) from readout-1 of the
   selector (physical q8), a raw reading of P(s = 0) is P = e10 + lambda p with lambda = 1 - e01 - e10, so
   P - 1/2 = lambda (p - 1/2) + (e10 - e01) / 2. The readout-0 circuit leaves all 17 qubits in |0>; the readout-1
   circuit excites the five region qubits q2, q4, q8, q11 and q12 and leaves the other twelve in |0>.
4. Why the pair stays in one batch. The retained one-CZ series reads the selector's e01 between 0.0254 and 0.0310 over
   its twelve readout-0 references (chi-square 84.4 about the mean on 11 degrees of freedom) and e10 between 0.0275 and
   0.0322 over twelve readout-1 references (chi-square 58.0 on 11), and adjacent batches step by about 0.005
   (`results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json`, `drift_covariate.references`, measured on
   Tuna-17, 2026-11-07). Over the 8 retained batches that hold both readouts (00, 03, 04, 07, 08, 11, 12, 15),
   c = (e10 - e01)/2 of the selector has chi-square 61.56 on 7 degrees of freedom about its weighted mean and ranges from
   -0.00136 to +0.00319, so a raw contrast of twins from two batches carries a c difference of up to about 0.0045 (1.6
   pooled twin standard errors). Both twins of a pair share the batch, so that difference is zero by construction.
5. Twin estimator. The bracket offset of a batch is c = (e10 - e01) / 2 and a twin reading is P - c. Both twins of a pair
   carry the one bracket of their batch, so the twin contrast t = (P1 - c) - (P0 - c) = P1 - P0 is the predecessor's raw
   contrast: the offset cancels exactly and its variance is v(P1) + v(P0), each v the arm variance of a rate over its shots
   (`arm_variance`, the Agresti-Coull interval variance at a deterministic arm, issue 791 item 3, which QX readouts
   exercise since they misassign no shot).
   - Its expectation is lambda1 (p1 - 1/2) - lambda0 (p0 - 1/2), the raw scale of the predicted contrasts and of the raw
     base contrasts, so the r and c - d comparisons mix no scales.
   - Design standard error at 32,768 shots per circuit and P = 1/2: contrast se 0.003906, pooled over two replicates
     0.002762 (`design`: `twin_batch_se_micro` 3906, `pooled_se_micro.twin` 2762). The bracket offset has se 0.000654 per
     batch at the retained means e01 = 0.0281, e10 = 0.0296 (`bracket_offset_se_micro` 654).
   - The bracket reports c and the offset-corrected reading P - c of each twin per batch (`twin_brackets` of the analysis
     record: a drift of the selector offset within the series, and a readout-0 against readout-1 context check); the
     decision does not read it. The predecessor's single readout per twin batch gives the same contrast; the second
     readout adds the per-batch c and its se at a cost of one circuit per twin batch.
   - A coin-conditioned selector dropout acts on the coin-1 twin's own shots; the batch's readout contexts are common to
     both twins, so the dropout's twin contrast (+0.0170 at the sized model) survives.
6. Order. The forward round is b0 base, b0 twin, k4 twin, k4 base, k8 base, k8 twin, k12 twin, k12 base (8 batches); the
   mirror round is that list reversed and, inside each twin batch, reverses the twin order (coin 1 then coin 0), so a
   linear drift per circuit position enters the two replicates of t as +g and -g and cancels in the pooled twin contrast
   (exactly for equal replicate weights, to first order for the analyzer's inverse-variance pool). The three X-only
   calibration batches of the predecessor follow (3, 3 and 2 circuits): 19 batches. b0 is
   `pathion_coset_coin_tuna_17/batch-02/b0.cq` byte for byte, as in the predecessor. The platform sets the execution
   order of the jobs of a batch (the retained `created_on` shows reversed twins in some batches), so the estimator uses
   batch co-membership, not the listed order.
7. Shots and time. Base batches run at the predecessor's shots (b0 base batches 131,072 per circuit, other base batches
   32,768), twin batches at 32,768 per circuit, calibration at 16,384. Jobs: 64 (8 base x 3, 8 twin x 4, 8 calibration);
   shots 2,555,904 (predecessor: 56 jobs, 2,293,760).

### Designs rejected

- Split pairs `[readout-0, twin, readout-1]` in 27 batches under the legacy 3-circuit policy: two adjacent batches sit a
  queue interval apart (23 to 207 minutes between retained batches, against 10 to 147 s inside one), which the in-batch
  pair avoids. Its simulated power under the stress below was 0.609 (dropout) and 0.650 (superposition-only).
- A mid-circuit selector reference or a measured classical coin in the twin: either adds a measurement on the coin edge,
  which is a coin-conditioned readout channel, the mechanism under test, and its misassignment is unmeasured on
  Tuna-17.
- A data-qubit-fixed twin, a QX remote run as the decision, and the Ry emulator as the decision: as in the predecessor.

## Circuits and batches

Every circuit measures all 17 qubits. A coin-fixed twin is the routed template with the coin's first single-qubit run (the
Hadamard, checked up to a global phase) removed and the coin prepared in |0> or |1>; the predecessor's `twin_entry`
builds it. Twin contrast t as in item 5; base contrast s = P(s = 0 | coin read 1) - P(s = 0 | coin read 0) as in the
predecessor, read raw.

- Batches 00-15: the 16 template batches of item 6. A base batch is `[readout-0, template, readout-1]`; a twin batch is
  `[readout-0, coin-0 twin, coin-1 twin, readout-1]` (mirror: coins reversed).
- Batches 16-18: the eight X-only preparations of (q2, q8, q12), 16,384 shots, a secondary readout calibration in a
  terminal-assignment context (D and G of the predecessor, reported beside the outcome).
- The routing seeds are those of the predecessor (values 0, 64 and 128 of
  `docs/evidence/anu_qrng/draw-2026-11-07T163258Z.json`); the operating characteristics are seeded from value 0 of
  `docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json`.
- QX twin: per template one batch `[readout-0, coin-0 twin, coin-1 twin, readout-1, base]`, 4 batches of 5 circuits (the
  service ceiling) at 2,048 shots; the QX emulator is no hardware backend and takes no policy field.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7), region q2, q4, q8, q11, q12 (as the predecessor); QX emulator (type 1) for the twin.
- Jobs and shots: 64 jobs in 19 batches of at most 4 circuits, 2,555,904 shots, every job at or under 131,072 shots. The
  longest job, a 131,072-shot b0 base circuit, takes 80.0 s (2.6 s plus the coin series' maximum measured 0.5906 ms per
  shot), under the 300 s job limit.
- Expected time: 1,521.0 to 1,675.8 s of execution (64 jobs at 2.6 s plus 0.53 ms to 0.5906 ms per shot), 6 pauses of 30 s
  (180 s) between the 7 waves under a wave procedure, 18 pauses (540 s) under the one-batch-at-a-time script, plus queue time. With the rounded 0.59 ms per shot the longest job reads 79.9 s.
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

`prediction.json` (`operating_characteristics`, shares in ten-thousandths; 20,000 simulated series per world, seeded from
value 0 of the draw above). A base contrast is a Gaussian draw at the design standard error; the two twins of a batch draw
binomial selector counts at P = 1/2 + c -/+ t / 2 and the real estimator reads them. Three tables: stationary; the
preregistered stress `batch_drift_sd_0.003`, an independent drift of 0.003 on every base contrast and every twin contrast
(the predecessor's convention); and `pair_common_drift_sd_0.003`, a drift of 0.003 on every base contrast and a drift of
each batch common to its two twins, which cancels in their difference. Worlds: the eight of the predecessor and the
negative twin. Share of runs that read each row, stationary:

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.965 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.033 |
| q12 correlation | 0.969 | 0.000 | 0.001 | 0.000 | 0.000 | 0.000 | 0.029 |
| coin-conditioned dropout | 0.000 | 0.926 | 0.043 | 0.000 | 0.000 | 0.000 | 0.031 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.940 | 0.001 | 0.000 | 0.059 |
| no offset | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.970 | 0.030 |
| worst admitted over-rotation (Y axis) | 0.497 | 0.000 | 0.468 | 0.000 | 0.000 | 0.000 | 0.035 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.078 | 0.873 | 0.001 | 0.000 | 0.000 | 0.048 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.890 | 0.000 | 0.000 | 0.001 | 0.000 | 0.000 | 0.109 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.002 | 0.973 | 0.000 | 0.025 |

Independent drift 0.003 on every contrast (`batch_drift_sd_0.003`):

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.825 | 0.000 | 0.006 | 0.002 | 0.000 | 0.000 | 0.167 |
| q12 correlation | 0.823 | 0.000 | 0.006 | 0.002 | 0.000 | 0.000 | 0.168 |
| coin-conditioned dropout | 0.000 | 0.725 | 0.113 | 0.002 | 0.000 | 0.000 | 0.160 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.771 | 0.007 | 0.000 | 0.221 |
| no offset | 0.000 | 0.000 | 0.000 | 0.003 | 0.000 | 0.833 | 0.164 |
| worst admitted over-rotation (Y axis) | 0.421 | 0.001 | 0.410 | 0.003 | 0.000 | 0.000 | 0.165 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.115 | 0.692 | 0.003 | 0.000 | 0.000 | 0.190 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.716 | 0.000 | 0.000 | 0.003 | 0.000 | 0.000 | 0.280 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.009 | 0.845 | 0.000 | 0.145 |

Drift 0.003 on the base contrasts, common to each pair (`pair_common_drift_sd_0.003`):

| world | zero | b0-like | intermediate | superposition only | negative twin | offset absent | other unresolved |
|---|---|---|---|---|---|---|---|
| over-rotation (X axis, pulse gates) | 0.914 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 | 0.084 |
| q12 correlation | 0.910 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 | 0.088 |
| coin-conditioned dropout | 0.000 | 0.821 | 0.097 | 0.000 | 0.000 | 0.000 | 0.082 |
| superposition-only offset | 0.000 | 0.000 | 0.000 | 0.869 | 0.001 | 0.000 | 0.130 |
| no offset | 0.000 | 0.000 | 0.000 | 0.003 | 0.000 | 0.901 | 0.096 |
| worst admitted over-rotation (Y axis) | 0.466 | 0.000 | 0.444 | 0.000 | 0.000 | 0.000 | 0.088 |
| X rotation before every single-qubit gate, Rz included (outside the admitted set) | 0.000 | 0.114 | 0.778 | 0.001 | 0.000 | 0.000 | 0.107 |
| X rotation after every single-qubit gate, Rz included (outside the admitted set) | 0.822 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.177 |
| negative twin (hypothesis: t0 = -s0) | 0.000 | 0.000 | 0.000 | 0.002 | 0.923 | 0.000 | 0.075 |

Stationary, the four deciding worlds decide in 96.5 (over-rotation), 96.9 (q12 correlation), 92.6 (dropout) and 94.0
(superposition-only) percent. The power rule asks 80 percent of the dropout and superposition-only worlds under a drift of
0.003. With the drift common to each pair the in-batch layout decides them in 82.1 and 86.9 percent and meets it; with an
independent drift on every contrast it decides them in 72.5 and 77.1 percent and misses it, as the predecessor's in-batch
layout does under that convention (72.7 and 76.8 percent in its rule-v2 table) and the split-pair layout did (60.9 and 65.0).
The two models bracket the truth: the in-batch pair removes every drift that shifts both twins together, and the stress
leaves a drift between the two twins of a batch, 10 to 147 s apart in the retained series, unexcluded.
Which model governs is a hypothesis; the retained twin forward-against-mirror comparison (chi-square 14.77 on 8 degrees of
freedom) shows no twin drift above the sampling noise. The residual loss under the common-drift model is the heterogeneity
gates reading base-contrast drift (`unresolved_batch` 0.04, `unresolved_block` 0.04 in every world), which no layout
change of the twins reaches. A wrong refutation of A5-186 (a b0-like reading of an over-rotation world) occurs in 7.8
percent of stationary runs of the world that rotates before every single-qubit gate, Rz included, and in under 0.1 percent
of runs of any admitted world.

## QX and Ry check plan

- QX local (qxelarator in the Quantum Inspire environment, `docs/notes/quantum_inspire/qx-runs.md`, "Run QX locally"; no
  account, queue or approval). The check reads the QX series through the successor's analyzer (`--qx-check`): every data
  circuit within twice the sampling floor of its ideal law, the selector's readout arms deterministic (zero misassigned
  shots), every bracket offset 0, and the twin contrast equal to the raw contrast. Not run for the in-batch layout of this
  version: the tests exercise the check on noiseless expected counts of the 20 circuits; a local run at 2,048 shots per
  circuit precedes the owner's approval request.
- QX remote (type 1): the same series, a written case for the owner's approval (repository rule), 4 batches.
- Ry (type 5): not built for the decision (predecessor CASE.md, owner decision 2026-11-07: 1,024 shots per job and an
  undocumented noise model). The one Ry check that adds information is the bracket arithmetic on a backend with nonzero
  readout error: a single `[readout-0, coin-0 twin, coin-1 twin, readout-1]` batch of b0 on a 5-qubit translation
  (`docs/notes/quantum_inspire/ry-emulator.md`, "Do a Ry emulator run"), whose corrected twin readings land within 3
  standard errors of 1/2 while the raw readings carry (e10 - e01) / 2. Ry is flagged `is_hardware`, so a manifest that
  selects `wave-v1` gives it 5 circuits per batch, 3 queued batches and the account's one pause clock (Hardware policy
  above). Written case, owner approval, not run.

## Residual risk

- The power rule holds under the common-drift model and misses under the independent-drift stress (Operating
  characteristics). The owner chooses the model that governs, or a wider design (a third replicate, which costs 8 more
  batches) if the stress governs.
- The FAQ's "job" is ambiguous (Hardware policy); a provider answer settles whether a wave reads as 3 or 15 jobs.
- The retained b0 base replicates differ: 0.0162 then 0.0393 (se 0.0028 each, 0.0039 for the difference, chi-square
  34.86 > 10.83), so the retained series reads `unresolved_batch`. Hypothesis: a drift of the offset itself, which the
  bracket does not correct (the bracket removes the readout offset, and the offset under test is the quantity that
  drifts); the unchanged heterogeneity gate reads it as `unresolved_batch`.
- A readout-context difference between the two brackets (readout-1 excites the five region qubits only) shifts c for both
  twins alike and cancels in t; a coin-conditioned part of the selector error is bracketed by no readout circuit, and the
  X-only calibration estimates it.
- hypothesis: the retained readout-0 selector error e01 behaves as steps rather than independent batch scatter; the
  operating characteristics draw independent drift and do not simulate steps.
- The Ry check has little statistical power: at 1,024 shots a twin's P(s = 0) carries a standard error of about 0.016,
  so it distinguishes the corrected from the raw reading only when |e10 - e01| / 2 on Ry exceeds about 0.05.
- The X-only calibration (batches 16 to 18) covers the assignment context; a q12 correlation that appears only after the
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

# QX twin: four batches, then the control analysis.
SANITY_COMMAND="true" sh scripts/qi_pathion_one_cz_null_submit.sh 1 "$CASES/pathion_one_cz_null_bracketed_qx" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_qx-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_qx_analysis.json

# Tuna-17: nineteen batches in order, under the wave-v1 policy the manifests name.
SANITY_COMMAND="$SANITY" sh scripts/qi_pathion_one_cz_null_submit.sh 7 "$CASES/pathion_one_cz_null_bracketed_tuna_17" "$RUNS" "$STAMP" "QUOTE"
"$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py --analyze "$RUNS/$STAMP"-pathion_one_cz_null_bracketed_tuna_17-batch-* \
	--out results/quantum_inspire/pathion_one_cz_null_bracketed_tuna_17_analysis.json
```

Never resubmit a directory that holds `submission.json` (`qi_platform.py reconcile` recovers its receipt); see
`docs/notes/quantum_inspire/usage.md`, "Run on Tuna-17". The retention change that follows holds the run directories, the
analyses, a refreshed `usage.json` and the `docs/state/research_state.json` registration.

# Case: Tuna-17 per-qubit readout assignment, T1 and X90 repetition ladder

Status: approved by the owner on 2026-11-16 and run; the six batches are retained under
`results/quantum_inspire/runs/2026-11-16T0401Z-characterization_tuna_17-characterization_tuna_17-batch-00` to `-batch-05`, the
analysis rows are `results/quantum_inspire/characterization_tuna_17_analysis.json`, and the record is
[tuna17-characterization-2026-11-16.md](../../../../docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md).
Every section below keeps the wording of the case as approved before the first submission, so "nothing has been
submitted", "none holds today" and "that reader does not exist yet" read as of that writing; the reader of "Record" is
`scripts/qi_retained_context.py` now. Generator and checker:
`scripts/qi_tuna17_characterization_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../characterization_qx/`). The approval asked for covers two
series in order: the QX dry run of the twin, then this Tuna-17 series.

## What the run measures

Three per-qubit quantities on all 17 qubits, on the day of the run:

- the readout assignment probabilities P(1|0) and P(1|1), from `readout-0` and `readout-1` at the start and the
  end of the series;
- the relaxation time T1, from the excited population after a wait of 0, 5, 10, 20, 40 and 80 us
  (`t1-N`, N cycles of 20 ns), corrected by the readout pair and fitted as one exponential;
- the ground population after 0, 32, 128 and 256 `X90` pulses (`x90-K`, 4K pulses, whole turns), a pass or
  fail endpoint for each qubit. It is a repetition ladder: P(0) is periodic in a coherent over-rotation, so the
  ladder bounds no error of one `X90` and gives no randomized-benchmarking figure.

Every circuit drives and reads all 17 qubits at once, so each figure is the qubit's value in that context: the
retained notes record drive crosstalk between neighbors and a neighbor-dependent readout assignment
([experiments.md](../../../../docs/notes/quantum_inspire/experiments.md),
[tuna-17.md](../../../../docs/notes/quantum_inspire/tuna-17.md)), and this series holds no single-qubit arm that
separates them.

No circuit holds a two-qubit gate, so no coupler is used. The series uses every qubit, the ones
[experiments.md](../../../../docs/notes/quantum_inspire/experiments.md) excludes from algorithm layouts included,
since the excluded qubits are among those whose present state is unknown.

## Why a simulation and the retained data cannot answer it

The provider withholds its per-qubit series: the Tuna-17 dashboard's notice of 2026-10-22 says so, and the
calibration datasource failed to answer on 2026-10-27 and 2026-11-15
([status-source observations](../../../../docs/evidence/quantum_inspire/status-sources-2026-11-15/README.md)).
The repository's own rows
([retained context](../../../../docs/evidence/qi-status-context/retained-context.json)) date from 2026-10-16 and
2026-10-17, and their implied T1 (5.1 to 52.0 us) rests on a single 2 us wait and on unchanged readout fidelity
between two runs. A noise simulation takes these quantities as inputs.

## Circuits and batches

Fourteen circuits, each `qubit[17]` with one measurement of every qubit at its end; all rotations are `X` or
`X90`, on the processor's pi/36 grid. `t1-0` has the text of `readout-1`. Six batches of at most 3 circuits, one
queued at a time, each after the account-wide pause of `scripts/qi_platform.py`:

| Batch | Circuits | Shots per circuit |
|---|---|---|
| 00 | readout-0, readout-1 | 16,384 |
| 01 | t1-0, t1-250, t1-500 | 8,192 |
| 02 | t1-1000, t1-2000, t1-4000 | 8,192 |
| 03 | x90-0, x90-8 | 8,192 |
| 04 | x90-32, x90-64 | 8,192 |
| 05 | readout-0, readout-1 | 16,384 |

Total: 14 jobs and 147,456 shots. The largest job holds 16,384 shots against the backend type's limit of 131,072
(`max_number_of_shots`, [catalogue](../../../../docs/evidence/quantum_inspire/catalogue.json)).

hypothesis: the provider accepts `x90-64`, whose 4,352 gate lines are about six times the longest circuit this
account has run on Tuna-17; the knowledge base mentions an operation cap per backend without a number. A
rejection ends the series at batch 04 with batches 00 to 03 retained, and the closing readout pair then runs
alone.

## Toolchain

`"$QI_PYTHON" scripts/qi_toolchain_check.py` (libqasm 1.2.1, OpenSquirrel 0.9.1, the Tuna-17 compiler
configuration) analyzes and compiles all 14 circuits and the 14 of the twin: every one reads `libqasm: ok`,
`compiled: ok`, with the control sequence and the gate sequence preserved
(`docs/evidence/quantum_inspire/toolchain-token-recovery.json`). `--local` runs the twin's 14 circuits on the
local qxelarator emulator and reads the noiseless outcome of each. hypothesis: the processor plays 256
consecutive `X90` pulses as written; the compile record shows no fusion, and the scheduler of the device is not
observable from the account.

## Expected seconds and credits

115.8 s of execution (`prediction.json`, `expected_execution_seconds`), by the model of
[usage.md](../../../../docs/notes/quantum_inspire/usage.md) ("Run on Tuna-17"): 2.6 s per job plus 0.53 ms per
shot, plus each circuit's wait per shot. The largest job is about 11.3 s against the 300 s limit. The series lasts
its execution, five pauses and the queue wait of each batch; the queue is read at submission. Credits: 0 expected,
since every retained job of the account shows `charged: 0`
([platform facts](../../../../docs/notes/quantum_inspire/platform-facts.md)).

## Admission

Each condition holds before the first Tuna-17 batch is submitted; none holds today, since nothing has run.

- The Tuna-17 instance reads `idle` in the compute API (`scripts/qi_status.py`, `account`), and the account's
  queue on Tuna-17 is empty.
- No other series of the account is in flight. The pause and the one-queued-batch rule are account-wide, so this
  series runs before or after the bracketed wave series, never between its batches.
- The QX dry run of the twin is collected, and its analysis reads the noiseless expectation of
  [the twin's case](../characterization_qx/CASE.md).

## Predictions and verdicts

`prediction.json` holds the thresholds; `--analyze` writes one row per qubit with each verdict.

- Readout: both closing-pair probabilities of a qubit within 0.03 of its 2026-10-17 row
  (`readout_within_tolerance`). Falsifier: a larger move, which says the readout settings changed; the T1 fit
  uses this run's own pair either way.
- Readout stability: the closing pair within 0.03 of the opening pair (`readout_stable`). Falsifier: a larger
  drift across the series, which the mean of the two pairs then misstates for the circuits between them.
- T1: one exponential fits the points above a corrected population of 0.05 (chi-square probability at least
  0.01). Falsifier: a non-monotone or two-rate decay. The point errors hold the binomial terms of the point and
  of the readout pair and leave out the covariance the shared pair adds, so the probability is approximate. A
  qubit whose T1 lies near 5 us (qubits 6, 9 and 15 on 2026-10-17) keeps three points above the floor and one
  degree of freedom; below about 3.3 us fewer than three remain and the row reads `t1_unfitted`. The T1 circuits
  span two batches, so a drift between them counts against the single exponential.
- Ladder: the corrected P(0) after 32, 128 and 256 pulses is each at least 0.5 (`ladder_clears`, written only
  when all three circuits are collected). Falsifier: a lower value at any of the three. A coherent
  over-rotation e gives cos^2(n e / 2) after n pulses. In units of pi / 512 (0.35 degrees) the three points all
  read at least 0.5 for e in [0, 1], [7, 8], [24, 25] and [31, 32], and the pattern repeats with period pi / 16
  (computed on a grid of 2,000,000 values of e); a pass therefore says e lies in one of those bands and bounds
  it only under the further assumption e < 7 pi / 512 (2.46 degrees). Decoherence alone leaves P(0) at or above 0.5 and
  shows in the decay length, not in this verdict.
- hypothesis: all 17 qubits relaxing at once read the same T1 as one qubit relaxing alone; the static ZZ shift
  moves no population, and a neighbor-dependent T1 is outside this series. The readout pair is taken with every
  neighbor in the prepared state, while late T1 points are read with neighbors near 0, so a neighbor-dependent
  assignment biases their correction.

## Pre-flight

- Hypothesis: the per-qubit readout pair and T1 of 2026-10-16 and 2026-10-17 still describe the device, and the
  qubits the retained repetition run flagged still fail under a long pulse train.
- Quantity: P(1|0), P(1|1), T1 and the ladder P(0), each as "What the run measures" defines it; the provider's
  own definitions of its withheld panels are unread.
- Falsifier: per qubit, a readout move above 0.03, a T1 outside a factor of two of its implied value, or a
  ladder verdict opposite to the prediction below.
- Predicted outcome, from the retained rows
  ([retained context](../../../../docs/evidence/qi-status-context/retained-context.json),
  [experiments.md](../../../../docs/notes/quantum_inspire/experiments.md), "Tuna-17, drivers"):
  readout within tolerance on all 17 qubits (the null; no retained rate of readout change exists); T1 between
  5.1 and 52.0 us, with six points above the floor on qubit 7 alone (52.0 us), five or four on thirteen qubits,
  three-point fits on qubits 6, 9 and 15 (implied 5.5, 5.1 and 6.3 us) and a single-exponential verdict of true
  on all 17; the ladder fails on
  qubits 6, 8 and 9 (P1 of 0.72, 0.76 and 0.88 after 40 X alone) and on qubit 2 (0.89 with its partner driven,
  as here), is open on qubit 1 (0.26 with its partner) and clears on qubits 5, 7, 13, 14 and 15; the seven
  qubits with no retained repetition figure (0, 3, 4, 10, 11, 12, 16) carry no ladder prediction. Budget:
  16,384 shots give a readout probability to 0.004 at worst, and 8,192 shots a T1 point to 0.006.
- What each result changes: a readout move replaces the qubit's retained row, and later cases build their
  mitigation from the new pair; a T1 below 10 us or unfitted keeps the qubit out of layouts that hold a wait; a
  ladder failure keeps the qubit out of circuits with long single-qubit trains, and a failure on a qubit
  predicted to clear, or on an unpredicted one, opens a single-qubit-arm case to separate crosstalk from the
  qubit's own pulse; a sanity stop ends the series and is reported before any further batch.

## Record

`--sanity RUN_DIR` after each collection: every job completed with all its shots, and `readout-0`,
`readout-1`, `t1-0` and `x90-0` read their fixed outcome on all but three qubits. Batches 02 and 04 hold no
circuit with a fixed outcome and get the job check alone, and no check detects a reversed bit order, since every
circuit treats all qubits alike. `--analyze OUT RUN_DIR...` after the series. The change that retains the runs
extends `scripts/qi_retained_context.py` to read the analysis rows, so the dashboard's table shows the new date;
that reader does not exist yet.

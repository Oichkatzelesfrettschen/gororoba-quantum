# Case: Tuna-17 per-qubit readout assignment, T1 and X90 repetition ladder

Status: written case awaiting the owner's approval; nothing has been submitted. Generator and checker:
`scripts/qi_tuna17_characterization_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of
this directory except this one, and the QX twin `../characterization_qx/`). The approval asked for covers two
series in order: the QX dry run of the twin, then this Tuna-17 series.

## What the run measures

Three per-qubit quantities on all 17 qubits, on the day of the run:

- the readout assignment probabilities P(1|0) and P(1|1), from `readout-0` and `readout-1` at the start and the
  end of the series;
- the relaxation time T1, from the excited population after a wait of 0, 5, 10, 20, 40 and 80 us
  (`t1-N`, N cycles of 20 ns), corrected by the readout pair and fitted as one exponential;
- the decay of the ground population under 0, 32, 128 and 256 `X90` pulses (`x90-K`, 4K pulses, whole turns),
  an upper bound on the error of one `X90`. It is a repetition ladder and gives no randomized-benchmarking
  figure.

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

Total: 14 jobs and 147,456 shots. Each qubit is measured once per shot, so the largest count per qubit per job is
16,384 against the provider's 500,000, and each job's shots stay under 131,072.

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

- The Tuna-17 instance reads `idle` in the compute API (`scripts/qi_status.py`, `account`), and the account's
  queue on Tuna-17 is empty.
- No other series of the account is in flight. The pause and the one-queued-batch rule are account-wide, so this
  series runs before or after the bracketed wave series, never between its batches.
- The QX dry run of the twin has been collected, and its analysis reads the noiseless expectation of
  [the twin's case](../characterization_qx/CASE.md).

## Predictions and verdicts

`prediction.json` holds the thresholds; `--analyze` writes one row per qubit with each verdict.

- Readout: both closing-pair probabilities of a qubit within 0.03 of its 2026-10-17 row. Falsifier: a larger move,
  which says the readout settings changed; the T1 fit uses this run's own pair either way.
- T1: one exponential fits the points above a corrected population of 0.05 (chi-square probability at least
  0.01). Falsifier: a non-monotone or two-rate decay.
- Ladder: the corrected P(0) after 256 pulses is at least 0.5. Falsifier: a lower value, which a coherent
  over-rotation of 0.35 degrees per pulse (cos^2(256 e / 2) = 0.5 at e = pi / 512) or stronger decoherence
  produces.
- hypothesis: all 17 qubits relaxing at once read the same T1 as one qubit relaxing alone; the static ZZ shift
  moves no population, and a neighbor-dependent T1 is outside this series.

## Record

`--sanity RUN_DIR` after each collection; `--analyze OUT RUN_DIR...` after the series; the per-qubit rows then
enter `scripts/qi_retained_context.py`'s inputs in the change that retains the runs, so the dashboard's table
shows the new date.

# Case: QX twin of the Tuna-17 interleaved T1, drive-context crosstalk and q12 phase series

Status: written case awaiting the owner's approval; nothing has been submitted. The twin rehearses the series of
[the Tuna-17 case](../characterization_interleaved_tuna_17/CASE.md) on the QX emulator (`QXsinglenodesimulator`, backend type 1)
with the same circuit texts at 10 qubits, the same batch layout and the same order, before any Tuna-17 batch is submitted. Generator and checker:
`scripts/qi_tuna17_interleaved_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this directory except this one).

## What the run measures

The emulator is noiseless, so the twin measures the series' mechanics, not a device: that every circuit parses and runs, that the
batches of at most three circuits complete with all their shots, that the status guard, the admission and status-trace records
and the analysis run end to end, and that every circuit returns its noiseless outcome. The twin holds the three arms of the Tuna-17 case
(`interleaved_t1`, `crosstalk` and `q12_phase`) and no single-qubit arm. The 10-qubit register changes the qubit map (`cases.json`): crosstalk
class A = {0, 4, 5, 6, 9} and class B' = {1, 3, 7, 8} in the place of the Tuna-17 classes, the q1/q2 pair unchanged, and the phase scan on q9 in the place of q12.
The delay of qubit i is the multiplier times its retained plateau T, as in the Tuna-17 case; the longest is 15,940 cycles (q7 at 12 T).
Shots are 1,024 per circuit in every arm, inside the emulator's 2,048. The flag rule of the crosstalk arm is the Tuna-17 case's (3.49 standard errors, per-qubit job-level sigma max(interleaved-anchor estimate, 0.0034), 0.0102 for every qubit without the interleaved arm,
verdict words "drive-and-readout context dependence"; `prediction.json` of the Tuna-17 case states it with its family rates), run by the same code.

## Why a simulation cannot replace the run

It is the run that the guard and records rehearse; a local simulation exercises the circuits (`--local` runs them on qxelarator) but not the
platform's batch, queue and collection path, which is the part the hardware series depends on.

## Circuits and batches

The same circuit texts as the Tuna-17 case at 10 qubits, in 30 provider batches of at most three circuits: 18 batches and 54 jobs for the interleaved arm
(55,296 shots), 8 and 24 for the crosstalk arm (24,576 shots) and 4 and 12 for the phase arm (12,288 shots); 90 jobs and 92,160 shots in all. The order is the Tuna-17
case's, from the same retained QRNG draw (`qrng_request.json` while it is pending).

## Expected seconds and credits

289.8 s of execution by the model of [usage.md](../../../../docs/notes/quantum_inspire/usage.md) ("Run on Tuna-17"): 176.4 s, 75.7 s and 37.7 s for the three arms.
It is an upper figure for the emulator: the circuits hold at most 256 gates on one qubit, so the gate-count growth that made the retained twin's ladders run 4 times
the model does not arise. Credits: 0 (every retained QX job charged 0).

## Admission

The Tuna-17 admission rule applies to the twin through the same `--submit` path with backend type 1: the type and its instances read `idle`
and the account's queue on it is 0. The initial admission of a batch refuses before a run directory exists; a retry after a pause refusal reads again and
refuses with the run directory and its earlier admission record in place. The owner approves the twin before the Tuna-17 series.

## Predictions and verdicts

Every job completes with 1,024 shots. The anchor circuits read their fixed outcome on all qubits; `t1-N` reads 1 on every driven qubit, the
ladder 0, and each Ramsey circuit a population of (1 + cos(angle)) / 2 on q9 with a fringe offset of 0 within its standard error (0.0176 rad at
1,024 shots, `expected_phase_se_rad`). Falsifier: an anchor off its outcome on more than three qubits, a fringe offset of 0.05 rad or more, or an analysis verdict other than
the single exponential on every qubit (the emulator has no decay, so `--analyze` reads the flat series as unfitted or single). A failure keeps the
Tuna-17 series from admission. The analysis records its unusable counts per arm (`unusable_qubits`, `unusable_normalizations`, `unusable_scans`); a dropped qubit
adds nothing to the tail statistic, so it moves that verdict toward the null. The pooled tail verdict reads `tail_confirmed` when `tail_statistic` >= 200, `inconclusive` when it is below 200 and fewer than 15 qubits (all of this 10-qubit chip) are usable, and `not_confirmed` otherwise.

`--self-test` exercises the design, order, guards, circuit timing and gate sequences, the estimator, the flag sigma floor and the three tail-verdict outcomes; the replicate gate, the tail threshold, each record field, the detuning
aggregate and the staggered comparison are exercised by the test file only.

## Pre-flight

- Hypothesis: the twin returns the noiseless outcome of all 90 jobs and the pipeline records admission and status for each.
- Quantity: per circuit the count of ones per qubit; per Ramsey scan the fringe offset; per run directory its admission and trace records.
- Falsifier: any circuit off its noiseless law (five binomial deviations for a fringe point), a fringe offset of 0.05 rad or more, or a run directory without both records.
- Predicted outcome: all circuits on their law, offset 0.00 within 0.018 rad, 30 run directories with both records.
- Budget: 30 batches, 90 jobs, 92,160 shots, 289.8 s, 0 credits, against the twin of the retained series (14 jobs, 178 s measured).

# Case: QX twin of the Tuna-17 interleaved T1, single-qubit and q12 phase series

Status: written case awaiting the owner's approval; nothing has been submitted. The twin rehearses the series of
[the Tuna-17 case](../characterization_interleaved_tuna_17/CASE.md) on the QX emulator (`QXsinglenodesimulator`, backend type 1)
with the same texts, the same batches and the same order, before any Tuna-17 batch is submitted. Generator and checker:
`scripts/qi_tuna17_interleaved_cases.py` (`--check results/quantum_inspire/cases` reproduces every file of this directory except this one).

## What the run measures

The emulator is noiseless, so the twin measures the series' mechanics, not a device: that every circuit parses and runs, that the
batches of at most three circuits complete with all their shots, that the status guard, the admission and status-trace records
and the analysis run end to end, and that every circuit returns its noiseless outcome. The qubit map differs because the
emulator holds 10 qubits: the single-qubit arm drives qubits 5, 7, 9, 0, 4, 6, 3 and 1 in the place of 5, 7, 14, 0, 4, 10, 11 and 16, and the phase
scan uses q9, q8 and q4 in the place of q12, q8 and q4. Shots are 1,024 per circuit, inside the emulator's 2,048.

## Why a simulation cannot replace the run

It is the run that the guard and records rehearse; a local simulation exercises the circuits (`--local` runs them on qxelarator) but not the
platform's batch, queue and collection path, which is the part the hardware series depends on.

## Circuits and batches

The same 101 circuit files as the Tuna-17 case at 10 qubits, in 65 provider batches of at most three circuits (66 jobs in 22 batches for the interleaved
arm, 96 in 32 for the single-qubit arm, 32 in 11 for the phase arm); 194 jobs and 198,656 shots. The order is the Tuna-17 case's, from the same retained QRNG draw (`qrng_request.json`
while it is pending).

## Expected seconds and credits

612.0 s of execution by the model of [usage.md](../../../../docs/notes/quantum_inspire/usage.md) ("Run on Tuna-17"), an upper figure for the emulator: the circuits
hold at most 256 gates on one qubit, so the gate-count growth that made the retained twin's ladders run 4 times the model does not arise. Credits: 0
(every retained QX job charged 0).

## Admission

The Tuna-17 admission rule applies to the twin through the same `--submit` path with backend type 1: the type and its instances read `idle`
and the account's queue on it is 0. The owner approves the twin before the Tuna-17 series.

## Predictions and verdicts

Every job completes with 1,024 shots. The anchor circuits read their fixed outcome on all qubits; `t1-N` reads 1 on every driven qubit, the
ladder 0, and each Ramsey circuit a population of (1 + cos(angle)) / 2 on its qubit with a fringe offset of 0 within its standard error (about 0.016 rad at
1,024 shots). Falsifier: an anchor off its outcome on more than three qubits, a fringe offset of 0.05 rad or more, or an analysis verdict other than
the single exponential on every qubit (the emulator has no decay, so `--analyze` reads the flat series as unfitted or single). A failure keeps the
Tuna-17 series from admission.

## Pre-flight

- Hypothesis: the twin returns the noiseless outcome of all 194 jobs and the pipeline records admission and status for each.
- Quantity: per circuit the count of ones per qubit; per Ramsey scan the fringe offset; per run directory its admission and trace records.
- Falsifier: any circuit off its noiseless law (five binomial deviations for a fringe point), a fringe offset of 0.05 rad or more, or a run directory without both records.
- Predicted outcome: all circuits on their law, offset 0.00 within 0.016 rad, 65 run directories with both records.
- Budget: 65 batches, 194 jobs, 198,656 shots, 612 s, 0 credits, against the twin of the retained series (14 jobs, 178 s measured).

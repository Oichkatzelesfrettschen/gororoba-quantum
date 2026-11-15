# Case: QX dry run of the Tuna-17 characterization series

Status: written case awaiting the owner's approval with [the Tuna-17 case](../characterization_tuna_17/CASE.md);
nothing has been submitted. Generator and checker: `scripts/qi_tuna17_characterization_cases.py`.

## What the dry run checks

The 14 circuit texts of the Tuna-17 series on `qubit[10]`, end to end on the QX emulator: the syntax as the
platform parses it, submission and collection, the result width (10 characters per shot, qubit 0 rightmost) and
the analysis on noiseless data.

## Batches and shots

The six batches of the Tuna-17 series, every circuit at 1,024 shots (the emulator admits 10 qubits and 2,048
shots). Expected execution: 44.2 s by the Tuna model of `prediction.json`, an upper figure for the emulator: the daily median execution of its
retained jobs lies between 0.05 and 11.3 s (`docs/evidence/qi-status-context/retained-context.json`).

## Noiseless expectation

- `readout-0` and every `x90-K`: all shots `0000000000`.
- `readout-1` and every `t1-N`: all shots `1111111111`; the emulator applies no relaxation during `wait`.
- Analysis: P(1|0) = 0 and P(1|1) = 1 on every qubit; every T1 point has corrected population 1, so the fit
  returns no finite T1 and the row carries no `t1_single_exponential: true`; the ladder reads P(0) = 1 at 256
  pulses and clears.

A T1 verdict of true on QX, or any shot outside the two strings, is a defect of the case, the analysis or the
platform and blocks the hardware series. The local qxelarator run (`--local`) already reads the two strings.

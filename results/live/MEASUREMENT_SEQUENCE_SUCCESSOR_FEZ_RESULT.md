# Result: the measurement-sequence successor on ibm_fez, width 24 at 5600 shots

The [successor case](MEASUREMENT_SEQUENCE_SUCCESSOR_CASE.md) was written for ibm_kingston at width 32. Its Kingston
job `dbhkprlep8hs73amc680` was cancelled while queued (0 s billed), and the owner approved the amended case on
ibm_fez: width 24, 5600 shots, the 20 us repetition delay, F = 1.5 pool coverage, a 100 s cap on the backup
instance, preceded by a scatter-floor diagnostic. Width 24 follows from the layout rule: 30 Fez qubits pass it, and
the diagnostic needs 38 qubits in total.

## Records

| Step | Record | Job | Billed |
|---|---|---|---|
| Kingston binding dry runs and submitted record | `2026-10-29T131159.515371Z`, `2026-10-29T132851.529467Z`, `2026-10-29T133453.165309Z` | `dbhkprlep8hs73amc680` (cancelled) | 0 s |
| Fez scatter-floor diagnostic | `2026-10-29T231157.338216Z` (dry run), `2026-10-29T231232.725730Z` | `dbht5v42d77s739ddn30` | 15 s |
| Fez rehearsal and sparse-gap scale | `2026-10-29T231459.174185Z`, [9693dec5b38146f1-w24-s5600.json](../../docs/evidence/measurement_sequence/successor-sparse-scale/9693dec5b38146f1-w24-s5600.json) | none | 0 s |
| Fez null | [successor-null-fez-w24-s5600.json](../../docs/evidence/measurement_sequence/successor-null-fez-w24-s5600.json) | Actions run 40973485511 | 0 s |
| Fez binding dry run and run | `2026-10-30T010259.410185Z`, `2026-10-30T010826.175789Z` | `dbhutsene4hc73bdm7j0` | 31 s |

The Fez floor is 0.0390 (main-qubit RMS; statistical part 0.0028) against Kingston's 0.0188
([scatter-floor-ibm_fez.json](../../docs/evidence/measurement_sequence/scatter-floor-ibm_fez.json)). The null at
width 24 gives 0 false fires on every arm and meets every target; 1020 shard rows recomputed on the build host match
byte for byte. Its plateau-retained arm issues a verdict in 4.8 % of replicates, the cost of the doubled floor.

## Run

The binding dry run planned on the 17:57 PDT calibration of 2026-10-29, two hours after the rehearsal's, and
`msq_successor_coverage.py` passed at F = 1.5 before and after the send. The job ran 101 PUBs on 24 qubits and
charged 31 s against the planner's 27.2 s.

## Result

Every analyzable qubit fails the carryover screen, so the analysis selects no qubit and withholds the device verdict
and every qubit's departure verdict. The screen measured the residue of a single reset, not the carryover the next
shot inherits, so the failure is a property of the screen's construction and says nothing adverse about ibm_fez.

| Quantity | ibm_fez (this run) | ibm_kingston | Margin |
|---|---|---|---|
| Reader carryover D (in-circuit: predecessor, terminal reset, 20 us idle, reader) | median 0.019, 0.012 to 0.030, z at least 12, on all 20 qubits that reach the screen | not measured | 0.0047 |
| Reset control rc1 - rc0 (one in-shot reset) | median 0.017, 0.012 to 0.032, all 24 qubits | median 0.0123, 0.0049 to 0.0366, all 32 qubits ([2026-10-27](MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)) | 0.0094 (reported only) |
| Cross-shot carryover from consecutive pattern rows (`pattern_crosscheck`) | median 0.00065 (SE 0.0004); 0 of 20 exceed the reader bound | +0.00020 +- 0.00006 ([raw diagnostics](../../docs/evidence/measurement_sequence/envelope-run-raw-diagnostics.json)) | |
| Calibrated `prob_meas0_prep1` of the layout | median 0.0073 | median 0.0071 | |

The reader D tracks the single-reset control (median ratio 1.14, r = 0.50 across qubits) and runs 2.6 times the
calibrated P(0|1): a measure-and-flip reset leaves a qubit in |1> whenever its own measurement misreads 1 as 0, and
the reader sees that residue. The next shot starts after a further `init_qubits` reset, which suppresses the residue
again, and the cross-shot carryover the executor's real order delivers is 0.00065, the size Kingston showed. The
design's bound (`|r1 - r0| <= 1` for everything after the terminal reset) is valid but discards that second reset, so
it overstates the inherited carryover about thirtyfold, and its 0.0047 margin lies below the single-reset residue on
every Heron r2 qubit measured so far. The defect was checkable before the run: the 2026-10-27 Kingston reset control
had measured the same residue at 0.0123, and the null planted carryover only near the margin, never at the size a
single reset leaves. A repetition delay of 50 us would not change it, because the residue is the reset measurement's
error rather than decay. The four qubits whose cross-shot carryover is largest (q151 0.0073, q95 0.0044, q121 0.0041,
q56 0.0024) are the four the pattern screen withheld, so that screen works as designed.

The departure test would also have been weak on ibm_fez: at its floor the N = 16 departure's systematic standard
error is about 0.032 (q2: +0.003 +- 0.032). Free-evolution T2 is a median 0.13 of the calibrated echo T2
(descriptive).

The pinching question stays open. A successor bounds the inherited carryover from what the next shot inherits: the
pattern rows' cross-shot estimate, which this run measured at SE 0.0004 against the 0.0047 margin, or readers that
repeat the reset `init_qubits` applies before reading. Either is a design change with its own null and written
case.

## Record repair

The submit reused the approved dry run's predictions, and `reuse_approved_predictions` copied the approved groups,
whose member ideals reference shared laws by digest, without the approved record's `ideal_laws`; `--collect` then
refused the record. The raw results were preserved first. The record's `ideal_laws` holds the three laws taken from
the approved record (sha256 `5a9931be...`, bound in `prediction_reuse.record_sha256`), each checked against its
content digest, and `ideal_laws_restored` names the source and the as-submitted record sha256 (`a105b99b...`).
`live_run.py` now copies the laws on reuse (test `test_reused_predictions_carry_their_shared_laws`).

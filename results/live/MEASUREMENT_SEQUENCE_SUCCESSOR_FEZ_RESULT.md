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
shot inherits, and its margin lies below that residue on both Heron r2 devices measured, so the screen could not
pass on either.

| Quantity | ibm_fez (this run) | ibm_kingston | Margin |
|---|---|---|---|
| Reader carryover D (in-circuit: predecessor, terminal reset, 20 us idle, reader) | median 0.019, 0.012 to 0.030, z at least 12, on all 20 qubits that reach the screen | not measured | 0.0047 |
| Reset control rc1 - rc0 (one in-shot reset) | median 0.017, 0.012 to 0.032, all 24 qubits | median 0.0123, 0.0049 to 0.0366, all 32 qubits ([2026-10-27](MEASUREMENT_SEQUENCE_ENVELOPE_FINDINGS.md)) | 0.0094 (reported only) |
| Cross-shot carryover from consecutive pattern rows (`pattern_crosscheck`) | inverse-variance mean 0.00061 +- 0.00008 on the 20 pattern-passing qubits; 0 of 20 exceed the reader bound | +0.00020 +- 0.00006 ([raw diagnostics](../../docs/evidence/measurement_sequence/envelope-run-raw-diagnostics.json)) | |
| Calibrated `prob_meas0_prep1` of the layout | median 0.0073 | median 0.0071 | |

The reader D tracks the single-reset control (median ratio 1.14, r = 0.50 across qubits). The raw bits locate that
residue: pooled over qubits, rc1's final read is 1 on 2.17 % of shots whose first read was 1, against a ground
baseline of 0.28 %, so the residue is the measure-and-flip reset failing on a qubit left in |1>. Decay during the
reset's measurement and feed-forward accounts for a third to a half of it (0.52 us / T1 with the run's fitted T1,
1.5 us / T1 with the calibrated T1; R2 at most 0.34). The next shot starts after the service's `init_qubits` reset,
which suppresses an ordinary |1> again: on the pattern-passing qubits the cross-shot carryover is 0.00061 +- 0.00008,
three times Kingston's 0.00020 +- 0.00006 (z about 4) and still an eighth of the 0.0047 margin. The design's bound
(`|r1 - r0| <= 1` for everything after the terminal reset) is valid but discards that second reset, so it overstates
the inherited carryover about thirtyfold, and its margin lies below the single-reset residue on every Heron r2 qubit
measured so far. The defect was checkable before the run: the 2026-10-27 Kingston reset control had measured the same
residue at 0.0123, and the null planted carryover only near the margin, never at the size a single reset leaves. The
repetition delay does not enter the reader D: the reader idle is the constant `MSQR_READER_IDLE_SECONDS`
(`qpu_planning.py`), so a 50 us run leaves D, and the screen's verdict, unchanged by construction.

The departure test would also have been weak on ibm_fez: at its floor the N = 16 departure's systematic standard
error is about 0.032 (q2: +0.003 +- 0.032). Free-evolution T2 is a median 0.13 of the calibrated echo T2
(descriptive).

The pinching question stays open. A successor bounds the inherited carryover from what the next shot inherits: the
pattern rows' cross-shot estimate, which this run measured at SE 0.0004 against the 0.0047 margin, or readers that
repeat the reset `init_qubits` applies before reading. Either is a design change with its own null and written
case.

## Conjectures tested against the raw bits

Each row states a conjecture, the test run on the retained shot-ordered bits (ibm_fez run `2026-10-30T010826.175789Z`;
ibm_kingston run `2026-10-27T014422.881898Z`, job `dbg08t9j4t8s73abaghg`) and the verdict. Pooled counts sum over
qubits; rc1 is `x; measure pre; reset; idle; measure final; reset` and rc0 omits the x.

| Conjecture | Test | Verdict |
|---|---|---|
| The reader D is the residue of one measure-and-flip reset | rc1 P(final 1 given pre 1) 0.0217 (2897/133220), given pre 0 0.0237 (28/1180, at the reset-failure rate), ground baseline 0.0028; D/rc 1.14 | holds |
| That residue is the calibrated assignment error P(0|1) | corr(D, calibrated P(0|1)) 0.24, D/P(0|1) 2.8 | refuted |
| The residue is decay during the reset's measure and feed-forward | residue = 0.52 us / T1-fitted + 0.0136 (R2 0.28), or 1.5 us / T1-calibrated + 0.0082 (R2 0.26; 0.34 without q56) | partial: a third to a half |
| A 50 us repetition delay rescues the screen | the reader idle is the constant `MSQR_READER_IDLE_SECONDS`, independent of the repetition delay | refuted by construction |
| The next shot inherits D times the next reset's residue | mean D x rc 0.00033 against observed 0.00061 +- 0.00008 | right magnitude, refuted in detail (z 3.4) |
| In-run ground readout is 20 times the calibration | raw ground P1 median 0.0039; the analysis's readout `offset` is 1 - P1(ro0) - P1(t1-0), not P(1|0) | refuted |
| A failed reset leaves a state that survives the next reset | rc1 final 1 to next shot's rc0 first read P1 0.081 (237/2925) against 0.0024 after final 0, z 66; an ordinary |1> survives at 0.022 | holds: a reset-immune subpopulation |
| Ground-start shots that read 1 are misreads of |0> | rc0 shots with pre 1 read final 1 in 231/548 (0.42); a misread |0> would give 0.0028, a true |1> 0.022 | refuted: reset-immune states, about 0.17 % of ground-start shots |
| Cross-shot carryover = residue x the qubit's measured persistence (no fitted parameter) | corr 0.90 over 24 qubits, best scale 0.84, chi2 223 (zero) to 67 on 23 dof | rejected as complete (p about 1e-5); it orders the qubits, and q95 and q132 carry the excess |
| The pattern-screen failures are the reset-immune carriers | persistence q151 0.30, q121 0.29, q95 0.15, then q23 0.14 and q147 0.12; q56 falls below 0.03 but has the shortest fitted T1 (33 us); the four failures are the four largest cross-shot values | holds for three of four |
| The memory is a slow fluctuator (milliseconds or longer) | event at shot j, target at shot j + k of the next PUB: carriers P1 0.228 at k = 0, at baseline (z at most 1.6) for k = 1, 2, 10, 100; ibm_kingston 0.310, then baseline | refuted: the memory outlasts one shot step and is gone 101 PUB steps later |
| The events are bursts that strike many qubits at once | shots holding two or more rc0 immune events: 2 against 3.9 for independent qubits (ibm_kingston 5 against 5.8); failed resets 561 against 533 (989 against 965) | refuted |
| The pinching endpoint carries the persistence | corr(N = 16 departure, persistence) 0.13 over 24 qubits | not detected |
| The reset-immune carriers are an ibm_fez property | ibm_kingston: reset failure 0.0185, persistence 0.065 (313/4848, z 64), immune survival 0.28 (330/1161); carriers q62 (0.30) and q154 (0.32), both withheld by its 2026-10-27 crosstalk screen | refuted: Heron r2 on both devices |
| The measure arm's N = 16 transition excess is readout misassignment alone | excess median 0.0043 per step (z 23); partial corr with persistence given assignment error and 1/T1 0.75, leave-one-out at least 0.64, but 0.13 without q151, q121 and q95 | refuted on three carriers; no relation across the other 21 |

The reset-immune events read as 1, survive a measure-and-flip reset that fixes an ordinary |1> 98 % of the time, carry
into the next shot through `init_qubits`, and are gone 101 PUB steps later; they strike qubits independently. Two
readings fit those counts: a population outside the computational subspace (a leaked |2>, read as 1 and left alone
by the conditional x, decaying within tens of microseconds) and a readout fault on the same qubit with a similar
lifetime. The carriers' rc1 shots that read 0 first and 1 at the end (6.8 % on ibm_fez carriers against 1.0 % on the
other qubits; ibm_kingston 7.4 % against 1.5 %) need a true |1> misread twice in a row, which a repeating readout
fault produces directly and leakage only through a |2> read as 0 that decays to |1> before the final read, so the
counts favor the readout fault without excluding leakage. A |1>-|2> pi pulse before the reset, or a
leakage-resolving readout on a carrier, separates the two; that is a hardware case of its own. The carriers raise the
measure arm's transition excess but leave the N = 16 departure uncorrelated with persistence, so per-qubit
persistence belongs among the successor's screens as a measured covariate rather than an assumed zero.

## Record repair

The submit reused the approved dry run's predictions, and `reuse_approved_predictions` copied the approved groups,
whose member ideals reference shared laws by digest, without the approved record's `ideal_laws`; `--collect` then
refused the record. The raw results were preserved first. The record's `ideal_laws` holds the three laws taken from
the approved record (sha256 `5a9931be...`, bound in `prediction_reuse.record_sha256`), each checked against its
content digest, and `ideal_laws_restored` names the source and the as-submitted record sha256 (`a105b99b...`).
`live_run.py` now copies the laws on reuse (test `test_reused_predictions_carry_their_shared_laws`).

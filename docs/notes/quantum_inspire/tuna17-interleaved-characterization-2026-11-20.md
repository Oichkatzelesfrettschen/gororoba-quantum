# Tuna-17 interleaved characterization of 2026-11-20

Case: [characterization_interleaved_tuna_17](../../../results/quantum_inspire/cases/characterization_interleaved_tuna_17/CASE.md)
(approved by the owner 2026-11-19; submit gate amended in [tuna17-interleaved-submit-gate.md](tuna17-interleaved-submit-gate.md)).
Runs: the 30 directories `results/quantum_inspire/runs/2026-11-19T1735Z-t17-characterization_interleaved_tuna_17-*`
(18 `interleaved_t1`, 8 `crosstalk`, 4 `q12_phase`), each passing `--sanity`. Analysis:
[characterization_interleaved_tuna_17_analysis.json](../../../results/quantum_inspire/characterization_interleaved_tuna_17_analysis.json)
from `scripts/qi_tuna17_interleaved_cases.py --analyze OUT RUNS... --prediction .../prediction.json` (compute host,
Python 3.14.7; a second run reproduced the first byte for byte).

The interleaved arm ran 2026-11-20 22:34 to 22:55 UTC and the crosstalk arm 22:55 to 23:04. The q12 arm ran batch 00 at
23:05 that evening, batch 01 on 2026-11-21 at 17:36 (submitted while the device read `executing`) and batches 02 and 03
at 19:38 to 19:40, after the submit gate changed: 20.6 hours between the two `w0` batches. 90 jobs, 688,128 shots and
643.2 s of execution (the sum of the 90 jobs' `execution_time_in_seconds` in their `results.json` result rows),
against the case's 660.2 s, 0 credits; the series spanned about 21 hours of wall clock.

## Preregistered verdicts

- Interleaved T1, pooled: `not_confirmed` (tail statistic 0 against the threshold 200, 17 of 17 qubits usable). The
  rule counts a qubit's tail gain only where both the replicate check and the tail fit's own lack-of-fit test reach
  0.01. On 16 of 17 qubits both fail: the three rounds of one multiplier disagree beyond their variance, and every
  plateau and two-rate fit is rejected (largest probability 0.0006, q8). On q15 both pass, and the single exponential
  has the lower AICc. `not_confirmed` therefore records that the rule found no admissible tail; the test had no power
  against a tail on the sixteen qubits whose fits the data reject, and the verdict is not evidence against a tail. Per-qubit labels (descriptive): 16 `unresolved`, q15
  `level_shift`.
- Crosstalk: 29 of 98 contrasts flagged at |z| > 3.49, on 15 distinct qubits. The 3.49 threshold holds a familywise level
  of 0.05 for independent contrasts; the contrasts of one condition batch share one all-17 job (CASE.md), so the rate is
  not exact and flags within a batch are correlated. The flag sigma is the floor 0.0034 on 14 qubits and the
  interleaved anchors' estimate on q6 (0.0055), q7 (0.0037) and q13 (0.0042). The largest
  are at the 256-pulse X90 ladder (q15 with class B' driven, z 44.1, reading 0.41 lower than with all 17 driven; q4 with
  class A driven, z 23.5), the 128-pulse ladder (q4, z 15.9) and the 250-cycle T1 wait (q14, z -14.0). The arm's
  reading is drive-and-readout context dependence.
- The q1/q2 pair (128-pulse X90 ladder): q1 alone against all 17 driven, z -1.8, not flagged; q2 alone 0.675 against
  0.614 with all 17 driven, z 6.9, flagged. With only q1 driven, q2 reads 0.008. The retained record
  ([experiments](experiments.md)) read q2 at 0.046 alone and 0.893 with q1 driven in a different circuit (40 X pulses),
  so the two series do not compare like for like; in this circuit, driving q1 alone leaves q2 near 0, and q2's own
  ladder reading is the one that moves.
- q12 phase: the fringe offset reads +0.027 +- 0.008 rad at a wait of 0 cycles and +0.025 +- 0.010 rad at 25 cycles,
  both `null` under the registered band (inside 0.05 rad of zero); the difference, -0.002 +- 0.013 rad, is zero within
  0.05 rad. The prediction of about -0.15 rad from the null-rotation scan refit
  ([refit](tuna17-null-rotation-scan-phase-refit.md)) is falsified on q12. `null` is the band's verdict, not zero
  rotation: the wait-0 offset lies 3.2 binomial standard errors from zero. Its error carries binomial variance only,
  and its two batches (00 and 02, complementary triads of angles) ran 20.6 hours apart. Each triad alone fixes a phase
  with its binomial error and no degree of freedom for a fit test, and the post-hoc split
  `docs/evidence/qi-tuna17-interleaved-rounds/q12_batches.py` compares them: batch 00 reads +0.018 +- 0.012 rad and
  batch 02 +0.037 +- 0.012, a difference of -0.019 +- 0.017 (z -1.1); at 25 cycles batches 01 and 03 differ by
  -0.002 +- 0.020. The pooled offsets do not hide a shift between the days at that resolution.
- Simultaneous against staggered excitation, descriptive: over 48 rows the all-driven crosstalk reading minus the
  interleaved fit at the same wait has a mean of 0.002, and the mean of the rows' own standardized differences is 0.36.
  That mean of z-scores is not a standard error of the mean difference, and the rows share anchors and fits, so the
  record does not resolve a schedule effect. Single rows reach |z| of 10.2 (q1 at 5 us), 9.3 (q13 at 5 us) and 4.7 (q15
  at 80 us); all sixteen 5 us rows lie outside the interleaved fit's delay range, and 14 of 16 rows at 80 us are
  positive.

## Round split, descriptive

`docs/evidence/qi-tuna17-interleaved-rounds/round_fits.py` (post hoc, deciding nothing) fits one exponential to each
round's six points per qubit, through the analysis's own anchored points and fit, with output
`round_fits.json` beside it.

- One exponential is accepted (lack-of-fit probability at least 0.01) in 13 of the 51 round fits, so each round alone
  departs from one exponential on most qubits, and a T1 that moves between rounds does not restore the single
  exponential.
- The fitted parameter T of those mostly rejected fits differs between rounds on 15 of 17 qubits with errors from the
  fit's curvature, and on 3 (q0 13.5, 18.2 and 18.2 us; q4 22.4, 26.0 and 22.7 us; q14 30.3, 27.9 and 32.5 us) with
  errors scaled by sqrt(chi-square / dof). The scaling estimates each round's scale from 5 degrees of freedom, the
  threshold 0.01 is unadjusted for 17 qubits, and the scaling hides large swings on badly fitted qubits (q2 20.4 to
  25.8 us). Neither count measures T1 drift: T is the parameter of a model the data reject.
- q1 fits a T of 2.7 to 3.0 us in every round, far below the other sixteen qubits (13.1 to 32.5 us), and fails every
  fit.

## Open hypotheses, each with its test

- hypothesis: T1 itself moves between jobs (two-level-system switching), rather than an additive level that shifts
  each job. The two predict different replicate scatter: a moving T1 changes the excited population most near
  t ~ T1, where its sensitivity (t/T1) exp(-t/T1) peaks, while a level shift scatters every multiplier alike. Test:
  the replicate variance by multiplier (0.5 to 12 T) in the retained record, against the two profiles.
- hypothesis: a disturbance common to all qubits of a batch drives much of the replicate failure. Test: the 17 by 18
  matrix of anchored residuals, its leading component against batch and execution order.
- hypothesis: the large ladder contrasts on q4 and q15 are coherent over-rotations that depend on which neighbors are
  driven. Test: a fit of the retained 32, 128 and 256 pulse readings per context to an over-rotation, then the
  single-qubit arm of [issue 941](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/941) on those two
  qubits.

## Open

- No claim cites the 30 acquisitions yet; the claim that interprets them is a later change.
- The case sizes the single-drive follow-up for six of eight flagged qubits persisting; 15 distinct qubits flag here,
  so the follow-up of issue 941 needs its budget recomputed before it is proposed.
- `scripts/qi_retained_context.py` still reads the 2026-11-16 characterization for each qubit's readout and implied
  T1; this change regenerates its retained-context file for the new jobs. CASE.md asks the retaining change to read the
  new analysis rows there; the interleaved fits are rejected on 16 of 17 qubits, so their T values would mislead the
  dashboard, and that extension waits for a fit that passes.
- The account ledger snapshot of this change declares 84 jobs unretained, among them the null phase scan series of
  2026-11-21 and its QX twin, whose retention is a separate change.

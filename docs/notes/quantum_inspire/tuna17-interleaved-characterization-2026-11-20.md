# Tuna-17 interleaved characterization of 2026-11-20

Case: [characterization_interleaved_tuna_17](../../../results/quantum_inspire/cases/characterization_interleaved_tuna_17/CASE.md)
(approved by the owner 2026-11-19; submit gate amended in [tuna17-interleaved-submit-gate.md](tuna17-interleaved-submit-gate.md)).
Runs: the 30 directories `results/quantum_inspire/runs/2026-11-19T1735Z-t17-characterization_interleaved_tuna_17-*`
(18 `interleaved_t1`, 8 `crosstalk`, 4 `q12_phase`), each passing `--sanity`. Analysis:
[characterization_interleaved_tuna_17_analysis.json](../../../results/quantum_inspire/characterization_interleaved_tuna_17_analysis.json)
from `scripts/qi_tuna17_interleaved_cases.py --analyze OUT RUNS... --prediction .../prediction.json` (compute host,
Python 3.14.7; a second run reproduced the first byte for byte).

The interleaved arm ran 2026-11-20 22:34 to 22:55 UTC and the crosstalk arm 22:55 to 23:04; the q12 arm ran its first
batches that evening and its last on 2026-11-21 at 19:40, after the submit gate changed. 90 jobs, 688,128 shots,
643.2 s of execution against the case's 660.2 s, 0 credits.

## Preregistered verdicts

- Interleaved T1, pooled: `not_confirmed` (tail statistic 0 against the threshold 200, 17 of 17 qubits usable). The
  statistic is 0 because the rule counts a qubit's tail gain only where the replicate check passes (probability at
  least 0.01), and the three rounds of one multiplier disagree beyond their variance on 16 of 17 qubits; the one qubit
  that passes it, q15, accepts the single exponential. `not_confirmed` therefore records that the rule found no
  admissible tail. It is not evidence against a tail. Per-qubit labels (descriptive): 16 `unresolved`, q15
  `level_shift`.
- Crosstalk: 29 of 98 contrasts flagged at |z| > 3.49. The flag sigma is the floor 0.0034 on 14 qubits and the
  interleaved anchors' estimate on q6 (0.0055), q7 (0.0037) and q13 (0.0042). The largest
  are at the 256-pulse X90 ladder (q15 with class B' driven, z 44.1, reading 0.41 lower than with all 17 driven; q4 with
  class A driven, z 23.5), the 128-pulse ladder (q4, z 15.9) and the 250-cycle T1 wait (q14, z -14.0). The arm's
  reading is drive-and-readout context dependence.
- The q1/q2 pair (128-pulse ladder): q1 alone against all 17 driven, z -1.8, not flagged; q2 alone 0.675 against 0.614
  with all 17 driven, z 6.9, flagged. With only q1 driven, q2 reads 0.008, against the 0.893 of the retained record
  ([experiments](experiments.md)); the retained reading did not repeat in this series.
- q12 phase: the fringe offset reads +0.027 +- 0.008 rad at a wait of 0 cycles and +0.025 +- 0.010 rad at 25 cycles,
  both `null` (inside 0.05 rad of zero); the difference, -0.002 +- 0.013 rad, is zero within 0.05 rad. The
  prediction of about -0.15 rad from the null-rotation scan refit
  ([refit](tuna17-null-rotation-scan-phase-refit.md)) is falsified on q12.
- Simultaneous against staggered excitation, descriptive: over 48 rows the all-driven crosstalk reading minus the
  interleaved fit at the same wait averages 0.002 (0.36 standard errors); the staggered schedule moves the mean decay
  by less than the arm resolves.

## Round split, descriptive

`docs/evidence/qi-tuna17-interleaved-rounds/round_fits.py` (post hoc, deciding nothing) fits one exponential to each
round's six points per qubit, through the analysis's own anchored points and fit, with output
`round_fits.json` beside it.

- One exponential is accepted (lack-of-fit probability at least 0.01) in 13 of the 51 round fits. Each round alone
  departs from one exponential on most qubits, so T1 moving between rounds does not restore the single exponential.
- With each round's T error from the fit's curvature, the three round values of T disagree on 15 of 17 qubits. Scaled
  by sqrt(chi-square / dof), since most round fits fail, they disagree on 3: q0 (13.5, 18.2 and 18.2 us), q4 (22.4,
  26.0 and 22.7 us) and q14 (30.3, 27.9 and 32.5 us). T1 changes on a scale of minutes on those three qubits; on the
  other fourteen the round differences sit inside the scatter of the points about each round's fit.
- q1 fits a T of 2.7 to 3.0 us in every round, far below the other sixteen qubits (13 to 32 us), and fails every fit.

## Open hypotheses, each with its test

- hypothesis: the excess scatter of the delay points about one exponential comes from job-to-job level changes larger
  than the anchors' estimate of the job-level variance. Test: refit with the job-level variance estimated from the
  delay points' own replicate scatter, and read whether the replicate check then passes.
- hypothesis: q0, q4 and q14 carry two-level-system defects whose coupling changes over minutes. Test: repeated
  single-delay circuits on those qubits over an hour, read as a time series of the excited population.
- hypothesis: the large ladder contrasts on q4 and q15 are coherent over-rotations that depend on which neighbors are
  driven. Test: the single-qubit arm of [issue 941](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/issues/941)
  on those two qubits.

## Open

- No claim cites the 30 acquisitions yet; the claim that interprets them is a later change.
- The account ledger snapshot of this change declares 84 jobs unretained, among them the null phase scan series of
  2026-11-21 and its QX twin, whose retention is a separate change.

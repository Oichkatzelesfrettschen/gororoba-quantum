# IQM Emerald idle schedule with delay-measured T1: result of 2026-11-21

Case: [idle-schedule-t1-emerald](../../../results/iqm/proposals/idle-schedule-t1-emerald/CASE.md) (cases.json sha256
37326cf0793dd2a3fdd41ddca07c234206ec7baaf2c3c67e6d21386b9da87df9, approval "owner AskUserQuestion 2026-11-21T20:53Z").
Run: `results/iqm/runs/2026-11-21T205643Z-emerald-idle-schedule-t1-emerald-probe`, job `01a1ffe5-b55a-74f5-a116-d45746738d44`, calibration set ecec1d0a. Analysis:
`results/iqm/idle_schedule_t1_emerald_analysis.json` (`scripts/iqm_idle_schedule_probe.py analyze`, compute host).

## Preregistered verdicts

- H1, schedule: `asap` on every pulsed arm.
- H2, common gap: `unidentifiable`. QB44's delay fit fails its gate (chi-square 33.9 on 2 degrees of freedom, survival
  about 4e-8 against `T1_FIT_P_MIN` 0.001), and the preregistered test covers all twelve pulsed qubits. QB44 also carried
  the widest calibrated T1 uncertainty of the cohort in the predecessor's case (21.7 percent); its delay decay departs
  from one exponential.
- Stationarity: not computed by the preregistered path, which returns at the exclusion.

## Descriptive readings of the eleven gated qubits

These come from the same analysis record and decide nothing; each rests on a unit delay scale (CASE.md, "Circuits").

- Mean per-pulse gap at 1000 pulses 27.21 +- 0.47 ns, at 500 pulses 33.06 +- 0.58 ns. A common gap is rejected at
  both lengths (chi-square 44.3 and 114.5 on 10 degrees of freedom). The two means differ by 5.85 ns, about 7.9
  combined standard errors, which falsifies the stationary gap model the estimator assumes. A model g(N) = a + b / N
  reads the difference as a fixed extra wait of about b = 5.9 us per train and a = 21.4 ns per pulse beyond the nominal
  24 ns (two points, so the model is fitted, not tested).
- Per layout: the eight qubits pulsed beside both train qubits read the same gap beside QB20 and beside QB26 (16
  comparisons, mean z 0.37, standard deviation 0.64; `docs/evidence/iqm-emerald-idle-schedule-t1/layout_split.py` on the
  analysis record). Relaxation driven by the particular train qubit would differ between layouts; this reading does not
  show it.
- T1 measured by the delay circuits over the calibration copy's T1: median 1.15, range 0.79 to 1.87 across the twelve
  qubits (`over_calibrated`).
- Cost: 0.233 s of compilation and 2.408 s of execution (wall clock equal to the billed execution), 3 billed seconds,
  2.25 credits; the balance read 26.75 afterwards. The case's projection of at least 7 billed seconds, scaled from the
  cancelled predecessor (`01a1f811`), did not hold: that job's slow execution did not repeat.

## Open hypotheses, each with its discriminating test

- hypothesis: the excess decay is a timing overhead of the control stack (per pulse and per train), not a T1
  calibration error. Support: the gap is common to both layouts and T1 reads near or above the calibration copy.
  Falsifier: a train of a third length (250 or 2000 pulses) off the line a + b / N, or a gap that tracks the train qubit.
- hypothesis: the fixed per-train wait of about 5.9 us is measurement alignment: iqm-pulla's multiplexed-probe merge
  pass "delays all measurements until the last possible moment" (docs/notes/iqm/docs/iqm-pulla). Test: a train circuit
  whose pulsed qubits are measured alone against one measured jointly with the train qubit.
- hypothesis: the delay instruction realizes its duration at unit scale. A scale a != 1 rescales every T1 and gap above;
  no reading of this job tests it.
- QB44: a two-level-system defect or a non-exponential decay channel; a frequency-resolved T1 or repeated delay
  circuits over time separate the two.

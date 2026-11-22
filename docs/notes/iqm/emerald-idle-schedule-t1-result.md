# IQM Emerald idle schedule with delay-measured T1: result of 2026-11-21

Case: [idle-schedule-t1-emerald](../../../results/iqm/proposals/idle-schedule-t1-emerald/CASE.md) (cases.json sha256
37326cf0793dd2a3fdd41ddca07c234206ec7baaf2c3c67e6d21386b9da87df9, approval "owner AskUserQuestion 2026-11-21T20:53Z").
Run: `results/iqm/runs/2026-11-21T205643Z-emerald-idle-schedule-t1-emerald-probe`, job `01a1ffe5-b55a-74f5-a116-d45746738d44`, calibration set ecec1d0a. Analysis:
`results/iqm/idle_schedule_t1_emerald_analysis.json` (`scripts/iqm_idle_schedule_probe.py analyze`, compute host).

## Preregistered verdicts

- H1, schedule: `asap` on every pulsed arm.
- H2, common gap: `unidentifiable`. QB44's delay fit fails its gate (chi-square 33.9 on 2 degrees of freedom, survival
  about 4e-8 against `T1_FIT_P_MIN` 0.001), and the preregistered test covers all twelve pulsed qubits, so the test
  returns before it reads any gap. The verdict records non-identification: it neither supports nor refutes a common gap,
  and the question stays open for a later case. The exclusion rests on the delay fit alone; QB44's calibrated T1
  uncertainty (21.7 percent in the predecessor's case, the widest of the cohort) is context, not the gate.
- Stationarity: not computed by the preregistered path, which returns at the exclusion.

## Descriptive readings

These come from the same analysis record and decide nothing; each rests on a unit delay scale (CASE.md, "Circuits").
The gap readings cover the eleven qubits that pass the delay-fit gate; the layout split and the T1 ratio cover the
qubits named in each item.

- Per-pulse gap of the eleven: mean 27.21 +- 0.47 ns at 1000 pulses and 33.06 +- 0.58 ns at 500. Each +- is the
  standard error of an inverse-variance mean under a common gap, which the record rejects at both lengths (chi-square
  44.3 and 114.5 on 10 degrees of freedom), so it understates the spread of the gap across qubits: the per-qubit gaps
  run from 23.5 to 36.8 ns at 1000 pulses and from 26.1 to 58.6 ns at 500, QB30 the largest at both (36.8 +- 2.2 and
  58.6 +- 3.1 ns). The two means differ by 5.84 ns, 7.8 standard errors of the difference; that comparison is
  descriptive, not the preregistered stationarity test, and it is inconsistent with one gap shared by both train
  lengths. A model g(N) = a + b / N through the two means gives a = 21.4 ns per pulse beyond the nominal 24 ns and
  b = 5.84 us per train; two points determine it exactly, so a and b are fitted values, not measured constants.
- Per layout: the eight qubits pulsed beside both train qubits, QB44 among them, read the same gap beside QB20 and
  beside QB26 (16 comparisons, mean z 0.52, standard deviation 0.89, with the shared T1 error counted once;
  `docs/evidence/iqm-emerald-idle-schedule-t1/layout_split.py` on the analysis record keeps every qubit with a positive
  delay rate). Relaxation driven by the particular train qubit
  would differ between layouts; this reading does not show it.
- T1 measured by the delay circuits over the calibration copy's T1 (`over_calibrated`), all twelve qubits: median
  1.15, range 0.79 to 1.87; QB42 (0.79) and QB34 (0.87) read below the calibration copy.
- Cost: compilation 0.233 s and execution 2.408 s (`raw/job.json` timeline), 2.641 s of runtime billed as 3 whole
  seconds at 0.75 credits per second, 2.25 credits; the balance read 26.75 afterwards. The case's projection of at
  least 7 billed seconds, scaled from the cancelled predecessor (`01a1f811`), did not hold: that job's slow execution
  did not repeat.

## Open hypotheses, each with its discriminating test

- hypothesis: the excess decay is a timing overhead of the control stack (per pulse and per train), not a T1
  calibration error. Support: the gap is common to both layouts and the median delay T1 reads above the calibration
  copy. Falsifier: a train of a third length (250 or 2000 pulses) off the line 21.4 ns + 5.84 us / N by more than three
  combined standard errors, or a gap that tracks the train qubit. Cheapest test: both lengths on one tightly fitted
  qubit (QB24), same estimator. Written case:
  [idle-schedule-third-length-emerald](../../../results/iqm/proposals/idle-schedule-third-length-emerald/CASE.md).
- hypothesis: the fixed per-train wait of about 5.8 us belongs to the terminal measurement. These circuits end in one
  joint `measure` over all twelve qubits, so iqm-pulla's multiplexed-probe merge pass, which postpones sequential
  measurements (docs/notes/iqm/docs/iqm-pulla), has nothing to merge here and does not explain the term. Test: a train
  circuit whose pulsed qubits are measured alone against one measured jointly with the train qubit falsifies a
  joint-measure overhead.
- hypothesis: the delay instruction realizes its duration at unit scale. A scale common to every delay cancels in the
  shape of one exponential but rescales every T1 and gap above, and no reading of this job tests it. A pulse train
  cannot serve as the clock, since its true duration is the unknown this run measures; a test needs an independent
  clock, such as the period of a Ramsey fringe at a known detuning, read across delay durations.
- hypothesis: QB30 carries an extra term beyond the cohort's gap (about 4 and 8 standard errors above the eleven-qubit
  means, with the highest delay-T1 ratio, 1.87). Falsifier: a repeat of the 500-pulse arms in which QB30 falls inside
  the other ten.
- QB44: a time-varying defect such as a two-level system, or a static non-exponential decay channel. A repeat of the
  same delay circuits whose fit passes its gate shows the decay changed over time, which supports the time-varying
  defect and falsifies a static channel; a repeat that still fails leaves a stable defect and a static channel
  unseparated, since this case's instructions (prx, delay, measure) give no frequency-resolved T1.

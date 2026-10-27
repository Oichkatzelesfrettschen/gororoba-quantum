# Idle-penalty probe on ibm_kingston: findings

The run is Kingston job `dbfrg3fpc3tc739o4kag`, retained as `results/live/2026-10-26T202817.431767Z`. It was approved
under [IDLE_PENALTY_PROBE_CASE.md](IDLE_PENALTY_PROBE_CASE.md).

| Field | Value |
|---|---|
| Shots | 4096 per PUB |
| PUBs | 44, in one dynamic job |
| Pairs | 31 coupled pairs, 62 qubits |
| Repetition delay | 20 us |
| Billed | 16 s, against the case's 25 s ceiling |
| Execution | 2026-10-26 21:54:17 to 21:54:32 UTC, inside one calibration window (2026-10-26T14:25:32-07:00) |

The planning calibration was 12:25:31-07:00. Every multiplier normalizes against the 14:25 calibration in force at
execution. The collector withheld no comparison.

Two files carry the analysis:

- `idle-penalty-report.json`: the preregistered analysis, written by `scripts/idle_penalty_report.py`. Its decisions
  are in that script's docstring.
- `idle-penalty-exploratory.json`: quantities chosen after the data, written by `scripts/idle_penalty_exploratory.py`.

The analysis digest is in each file's `identity`. The analyzer changed in one way after collection: the exposure
gate the case listed as the step before any readout verdict. Every estimator, threshold and decision rule is
unchanged.

`idle-penalty-report-vectorized-encoding.json` and `idle-penalty-exploratory-vectorized-encoding.json` replay both
analyses after `law_encoding.py`, one of the analyzer sources the digest covers, gained a vectorized encoder that
writes byte-identical laws; they differ from the two files above only in `identity.analysis_digest`, and gate
`core-idle-penalty-report-replay` checks them. The two files above keep their bytes.

## Exposure

The analyzer reads the service schedule of every PUB (`metadata.compilation.scheduler_timing` in `raw/`) before any
estimate, and it refuses a run on any of these departures:

- On every replica, the compiled ISA instructions on each qubit, in order, must consume the scheduled instances one
  for one. `scheduled_idle_replay.padded_replica` does this check, so a dropped or added read or pulse on either role
  fails it.
- All 31 replicas of each member must share one idle sequence.
- Every probe idle must have its planned length: 2500, 10000 and 25000 dt, with echo halves of 1250, 5000 and 12500
  dt.
- Each readout arm must repeat the probe sequence of its Ramsey reference: 10000 dt for the during and after arms,
  2500 dt for the short arm.
- The reader must play exactly 12 intermediate reads (3 in the short arm). They must sit inside the probe idle in the
  during and short arms, and after the probe's final read in the after arm.

The retained run passes every check. A mutation test refuses each departure separately.

The ALAP schedule places the during-arm train late in the idle. On the qubit channel, the first of the 12 reads
starts 2692 dt into the 10000 dt idle, and the last pulse of the twelfth ends 309 dt before the idle ends, a span of
6999 dt (28.0 us). Counted with each read's full 545 dt Target duration, the train lasts 7244 dt (29.0 us).

## Preregistered results

| Quantity | Median | 95% interval | n | Analyzer verdict |
|---|---|---|---|---|
| kappa_1 = Gamma_1 T1_reported | 1.057 | [0.978, 1.183] | 62 | optimistic_t1 "absent or unresolved" |
| kappa_2* = T2_reported / T2* | 1.451 | [1.276, 1.905] | 62 | |
| kappa_2e = T2_reported / T2echo | 1.140 | [1.036, 1.227] | 62 | |
| kappa_2* / kappa_2e | 1.269 | [1.170, 1.330] | 62 | echo_gain "present" |

The intervals are order-statistic intervals of the median over this cohort of 62 qubits. For kappa_1 the interval
lies wholly below the 1.5 threshold.

Readout of the 31 partners during a probe's 40 us idle (pair means, 31 units):

| Endpoint | During vs after | During vs quiet Ramsey | Quiet null (after vs Ramsey) | Decision |
|---|---|---|---|---|
| Ramsey phase rate | -2.72 kHz, se 0.53, t -5.13 | -2.73 kHz, se 0.54, t -5.10 | -0.010 kHz, se 0.020 | present |
| Visibility change | -0.026, se 0.011, t -2.34, chi2 tail 3e-87 | -0.019, se 0.011, t -1.63, chi2 tail 9e-87 | +0.007, se 0.003 | present |

Both decisions stand as the preregistered rule produced them. Two limits apply:

- All pairs share each wide PUB's shots, window and readout environment. The pair-mean tests treat pairs as
  independent.
- The visibility "present" rests on the chi-square alone, because neither t statistic passes its alpha 1e-3
  quantile. That chi-square uses conditional per-pair shot-noise errors, which are lower bounds. The visibility result
  therefore establishes pairwise departures that differ from pair to pair. It does not establish a mean visibility
  loss across the device.

A repeat states a repaired visibility rule in its own case, before its data.

## Observations

- **Relaxation.** The reported T1 holds at the cohort median, while individual qubits spread widely around it.
  - kappa_1 ranges from 0.36 to 5.5 (qubit 144).
  - 43 of 62 qubits depart from 1 by more than 3.29 conditional standard errors, and the median error is 0.026.
  - Those errors hold the assignment references fixed, and the qubits share PUBs. The count describes this cohort
    and carries no calibrated p-value.
- **Dephasing.** Free-induction decay runs 1.27 times faster than echoed decay. Echoed T2 is about 12% shorter than
  reported (T2_reported / 1.14). The noise model charges every undecoupled idle the reported echo T2, so on most
  qubits it charges less dephasing than this run measures.
- **Ramsey phase rate.** The sign follows the analyzer convention (`atan2(Y, X)`, during minus reference); no signed
  detuning was injected to calibrate it against laboratory frequency.
  - The short arm unwraps every probe. On each probe the chosen branch lies within 1.2 kHz of the short-arm value,
    and branches are 25 kHz apart.
  - 30 of 31 pair means and 56 of 62 probes read negative. The pair median is -1.6 kHz, and the most negative pair is
    33/32 at -11.0 kHz.
  - The probe-level extreme is qubit 33 at -21.5 kHz, beside qubit 89 at -11.2 kHz.
  - The quiet null stays within plus or minus 0.3 kHz on every pair.
- **Visibility.** It is local.
  - The pair median is -0.006.
  - Probe 74 loses 0.57 of its visibility, and probes 140, 150, 70 and 154 lose 0.12 to 0.27.

## Exploratory reanalysis

These results come from `scripts/idle_penalty_exploratory.py` and `idle-penalty-exploratory.json`. They were not
preregistered.

- **Pure-dephasing multipliers.** The multiplier is (1/T2_measured - kappa_1 / 2 T1_reported) / (1/T2_reported -
  1/2 T1_reported).
  - Free evolution: cohort median 1.88, order-statistic band [1.39, 2.40].
  - Echo: median 1.20, band [1.04, 1.29].
  - The bands are order statistics over point estimates and do not propagate uncertainty. The per-qubit values run
    from -0.67 to 17.9 (free) and from -0.24 to 6.5 (echo), which shows how unstable the subtraction becomes where the
    pure-dephasing rate is small.
- **Reader excitation.** The reader's final population after its train exceeds its ground reference by a median of
  -0.0005 and a maximum of 0.038.
  - Static ZZ times that excitation predicts at most 0.16 kHz of shift, and it correlates with the measured shift at
    r = -0.13.
  - This bounds only the final population. Transient excitation or leakage during the train, chip-wide readout drive,
    and a phase present only in this schedule remain possible.
  - The phase-rate contrast is consistent with a frequency pull associated with readout, and this design does not
    identify its mechanism.
  - Every replica's partner reads at once, so the design cannot separate a probe's own partner from readout elsewhere
    on the chip.
- **Visibility against shift.** Pair visibility change and pair shift correlate at r = -0.07 across 31 heavy-tailed
  pairs. Probe 74 carries both effects. Whether they share a cause stays open, with low confidence either way.
- **Qubit 47.** It reads kappa_2* 5.43, but its three-point exponential fit has chi-square 27.5 on one degree of
  freedom. That makes it an outlier with a poor fit in one run, nothing more specific.

## Bearing on the retained kappa of about 3

The retained kappa came from two runs:
- `2026-10-12T055624.091217Z`, on qubits 73, 79, 92, 93, 94 and 95, with property stamp 10-11 22:36 -07:00;
- `2026-10-13T020454.599853Z`, on qubits 73, 79, 92, 93 and 94, with property stamp 10-12 18:47 -07:00.

Both stamps fall under one T1/T2 refresh, 10-11 20:36 -07:00; the next refresh came at 10-12 22:30. This run placed
73, 94 and 95, under the 10-26 14:25 calibration:

| Qubit | kappa_1 | kappa_2* | kappa_2e | Free pure dephasing | Phase rate (kHz) | dV |
|---|---|---|---|---|---|---|
| 73 | 1.03 +- 0.03 | 0.93 +- 0.07 | 0.90 +- 0.07 | 0.88 | +0.10 +- 0.12 | -0.003 |
| 94 | 0.88 +- 0.02 | 0.95 +- 0.07 | 0.83 +- 0.06 | 0.99 | -0.07 +- 0.11 | -0.018 |
| 95 | 1.05 +- 0.03 | 1.65 +- 0.15 | 1.12 +- 0.13 | 2.54 | +0.03 +- 0.10 | +0.005 |

Qubits 73 and 94 read nominal on every endpoint. Qubit 95, which only the first run used, shows excess free dephasing
with no excess relaxation and no readout effect.

Under today's calibration, this probe's single-qubit idle physics does not account for a threefold charge on 73 and
94. Three accounts remain:
- the excess changed over two weeks;
- it sits on the unplaced qubits 79, 92 and 93;
- it belongs to those runs' own gates and measurements on their layout.

This comparison cannot separate drift over time, calibration normalization and a changed circuit context.

The N=21 runs with kappa near 1.6 (`2026-10-18T090603.530638Z`, `2026-10-25T193443.839527Z`) used qubits 104-107,
117 and 124-126. This run placed 105, 107 and 117:

| Qubit | kappa_1 | kappa_2* | kappa_2e | Free pure dephasing | Phase rate (kHz) | dV |
|---|---|---|---|---|---|---|
| 105 | 0.95 +- 0.02 | 1.28 +- 0.08 | 1.33 +- 0.08 | 1.64 | -2.40 +- 0.11 | +0.005 |
| 107 | 0.91 +- 0.02 | 1.02 +- 0.09 | 0.88 +- 0.08 | 1.14 | -5.52 +- 0.11 | +0.028 |
| 117 | 1.09 +- 0.02 | 1.28 +- 0.08 | 1.11 +- 0.08 | 1.43 | -0.74 +- 0.12 | +0.018 |

N=21 idles through mid-circuit measurement. A readout-time phase that a fit charges as incoherent decay inflates the
fitted kappa above 1. That account of kappa near 1.6 has low-to-medium confidence. A replay of the retained N=21 runs
with this run's phase rates and free dephasing added to the noise model tests it, and refutes it if the fitted
multiplier stays near 1.6.

## Open

- **Stability across calibrations (question d).** It needs a repeat on the same ordered 31 pairs under a refreshed
  T1/T2, compared with `--compare`; [IDLE_PENALTY_REPEAT_CASE.md](IDLE_PENALTY_REPEAT_CASE.md) preregisters it.
- **Readout attribution, and whether phase rate and visibility loss share a cause.** This needs a campaign whose
  replica classes differ: focal partner only, background readers only, all readers, and none.
- **The unplaced historical qubits 79, 92 and 93.** One guarded job cannot hold all three, because 93 neighbors both
  79 and 92 (`targets.json`); [IDLE_PENALTY_FOCAL_CASE.md](IDLE_PENALTY_FOCAL_CASE.md) places them in two jobs.

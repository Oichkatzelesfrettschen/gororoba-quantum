# Tuna-17 null block: q4 angle and q12 phase scan (draft case)

Status: draft. It is no written case in the sense of root AGENTS.md ("Hardware services"): no generator, circuit
file, prediction record or operating characteristic exists, nothing is approved and nothing is submitted. "Not
built" lists what precedes the owner's approval. Ledger row: A5-186. Predecessor: the injected-rotation scan
([case](../../../results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md), verdict
`unresolved_none`) and its exploratory reading
([tuna17-null-rotation-scan-line-phase.md](tuna17-null-rotation-scan-line-phase.md)).

## Question

The null block b0 reads a selector offset with a static part near 0.014 that drifts between jobs and a part of
amplitude 0.025 that follows the phase of the shot-order line on q4's read bit. Three questions, each a device
fact:

1. Does an injected `Rz` on q12 null the static part, at which angle and with which sign?
2. Is the static part a single-qubit phase on q12 or a conditional phase of coupler 8-12?
3. Is the quantity the line modulates the q12 phase itself, and are the static and oscillating parts linear in
   q4's pulse angle with one common zero?

## Why the retained data cannot answer it

The retained series varies pulse amplitudes only. In the forward model a q12 phase and a conditional phase on
coupler 8-12 fit its 24 contrasts almost equally (chi-square 205 and 187 with one parameter per batch), exact
pulses give an even response to a q12 phase, so the offset fixes its size (0.18 rad) and leaves its sign open, and
the q4 arms hold two angles (+-10 degrees) around a zero that lies between 0 and +15 degrees.

## Circuits

Every circuit is the retained b0 text with each `X90` as `Rx(pi/2)` (the center arm `b0-rx` of the predecessor),
rewritten on one qubit. Angles are multiples of pi/36, the processor's angle grid.

- `b0-rx`: the center, in every data batch.
- `b0-rx-q4-m5`, `-p5`, `-p10`, `-p15`: q4's 8 pulses at 85, 95, 100 and 105 degrees. `-p10` repeats a retained arm.
- `b0-rx-z12-m20`, `-m10`, `-p10`, `-p20`: an `Rz(phi)` on q12 before each of its 5 pulses, phi = -20, -10, +10,
  +20 degrees. `Rz` is virtual and takes no time, so the schedule, the pulse count and the CZ count equal the
  center's.

## Batches

17 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch. Eight data batches at 131,072 shots per circuit:

- forward round: [q4-m5, b0-rx, q4-p5], [q4-p10, b0-rx, q4-p15], [z12-m10, b0-rx, z12-p10],
  [z12-m20, b0-rx, z12-p20];
- mirror round: the same four in reverse order with the outer arms exchanged.

Each data batch carries its own center, so the drift of the static part between batches enters no within-batch
comparison.

## Predictions

Mean selector contrast and `d2_split` in the forward model at the retained mean bracket and visibility 0.42
(`docs/evidence/qi-null-rotation-scan-line-phase/followup_predictions.py`). The standard error of one contrast at
131,072 shots is 0.0028 and of one `d2_split` 0.0056; each arm has two replicates.

| Arm | Exact pulses | q12 phase -0.18 rad | Coupler 8-12 phase -0.25 rad |
|---|---|---|---|
| q4 -5 degrees | 0.000 | 0.019 | 0.022 |
| center | 0.000 | 0.014 | 0.014 |
| q4 +5 degrees | 0.000 | 0.008 | 0.007 |
| q4 +10 degrees | 0.000 | 0.002 | 0.000 |
| q4 +15 degrees | 0.000 | -0.002 | -0.006 |
| z12 -20 degrees | 0.047 | 0.093 | 0.100 (`d2_split` -0.011) |
| z12 -10 degrees | 0.013 | 0.048 | 0.050 (-0.004) |
| z12 +10 degrees | 0.013 | 0.000 | 0.003 (+0.011) |
| z12 +20 degrees | 0.048 | 0.012 | 0.020 (+0.018) |

`d2_split` stays below 0.002 in every z12 arm under exact pulses and under the q12 phase. A q12 phase of +0.18 rad
gives the z12 column mirrored in the sign of phi. The retained q4 arms read 0.039 at -10 degrees and -0.006 at +10
degrees, a steeper line than either world gives (0.024 and 0.002; 0.028 and 0.000).

Line phase. With the contrast near 0.42 (phi0 + phi + A cos(theta))^2 in the total q12 phase, a line that
modulates that phase by A gives a first harmonic 0.84 A (phi0 + phi): the retained 0.025 at phi = 0 fixes A near
0.165 rad, and the z12 arms then read 0.073, 0.049, 0.001 and 0.024 with reversed phase at -20, -10, +10 and +20
degrees. A line that modulates another quantity leaves the first harmonic of the z12 arms near the center's 0.025.
The same model gives a second harmonic of 0.0057 at the center, where the retained series reads 0.0017 +- 0.0012,
so the retained data already disfavor the first reading at about 3 standard errors.

## Decision rules (draft, fixed before any submission)

1. Admission: the readout guard of the predecessor on each data batch (e01 and e10 of the guard qubits steady
   across its two brackets), and a control that the center arms pooled over the admitted batches exceed 3
   standard errors.
2. Static part against phi. For each of three worlds (exact pulses, q12 phase, coupler 8-12 phase) fit one
   parameter per admitted z12 batch to its three contrasts at the noise strength that reproduces the center
   visibility, over the predecessor's noise models. Four batches give 8 degrees of freedom; the adequacy bound is
   the 0.001 point, 26.12. Labels: `exact_parabola` (the exact world is adequate: the hypothesis of a phase on or
   around q12 is falsified), `q12_phase` or `coupler_phase` (that world is adequate and its chi-square lies at
   least 25 below the other's), `phase_unresolved` (both adequate, closer than 25), `none_adequate`.
3. Sign and size: the fitted q12 phase per batch with its interval, and the injected angle of least contrast.
4. `d2_split` of the z12 +10 and +20 degree arms, pooled over replicates, against 0 and against the coupler
   world's +0.011 and +0.018: reported beside rule 2 and outside its label.
5. Line phase. The line's frequency and phase come from q4's bit on the odd-indexed shots of each job and the
   contrast is folded on the even-indexed shots (`line_phase_split.py`). Per arm, the first harmonic projected on
   the center's phase. Labels: `line_on_q12_phase` (the four z12 values follow 0.84 A (phi0 + phi) with the A and
   phi0 of rule 3 within 3 standard errors each, the +20 degree arm reversed), `line_elsewhere` (all four within
   3 standard errors of the center's value), `line_unresolved`.
6. q4 line. Weighted straight-line fits against q4's angle over -5, 0, +5, +10, +15 degrees of (a) the mean
   contrast less its batch center and (b) the projected first harmonic. Reported: both chi-squares on 3 degrees of
   freedom, both zero crossings with intervals, and their difference in standard errors.

A5-186 changes only on `q12_phase` or `coupler_phase` with rule 1 passed, and then to the statement of that label;
every other outcome reports the numbers.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7), region q2, q4, q8, q11, q12. QX emulator (type 1) for the twin of the nine distinct
  circuits at 2,048 shots.
- Jobs and shots: 42 jobs in 17 batches, 3,735,552 shots (24 data jobs at 131,072, 18 readout jobs at 32,768),
  every job at or under 131,072 shots and about 80 s against the 300 s limit.
- Expected time: about 35 minutes of execution and 16 pauses, under one hour at the 30 s pause step; the
  predecessor's 21 batches took 66 minutes.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  ([usage.md](usage.md), "Queue rules: the FAQ governs").
- Credits: expected 0, read from a fresh usage snapshot before the submission.

## Limits stated before the run

- The predictions use a contraction at one visibility; the gate-noise families and the measured brackets enter
  through the fit of rule 2, and the operating characteristics of the labels are not computed.
- The static part drifts on a scale of minutes (0.001 to 0.020 in the predecessor), so a fitted phase is a value
  per batch.
- An `Rz` before each pulse of q12 is one placement. A phase that accumulates during idles or inside the CZ of
  coupler 8-12 commutes differently with the pulses, which the two fitted worlds of rule 2 bracket and no third
  world covers.
- The source of the line is unmeasured; rule 5 reads only whether its effect scales with the injected phase.

## Not built

- The generator (a successor of `scripts/qi_pathion_null_rotation_scan_cases.py` with the `z12` arms and the q4
  steps), its tests, `cases.json`, the batch directories and their `--check`.
- `prediction.json` with the operating characteristics of rules 2 and 5 under the three worlds and under gate
  noise, and a shot-level simulation of the line-phase statistic.
- The QX twin and its control analysis.
- The written case under `results/quantum_inspire/cases/`, its local review and the owner's approval.

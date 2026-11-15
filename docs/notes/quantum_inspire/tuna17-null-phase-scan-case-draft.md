# Tuna-17 null block: q4 angle and q12 phase scan (draft case)

Status: superseded by the written case
[pathion_null_phase_scan_tuna_17/CASE.md](../../../results/quantum_inspire/cases/pathion_null_phase_scan_tuna_17/CASE.md),
which the generator `scripts/qi_pathion_null_phase_scan_cases.py` builds. The case keeps this draft's z12, z8c and
q4 questions and changes the design: every circuit but a bridge arm carries the same nine `Rz` (zero where an arm
injects none), so the arms share one schedule; the z12 arms sit at +-10 and +-30 degrees, the z8c arms at +-10
degrees in four batches, the q4 arms at -10, -5, +5 and +10 degrees, and two bridge batches compare the padded
center with the unpadded one; the fit carries relative d2 splits and CZ damping beside the contractions, and a
deciding label needs every deciding kind to agree. The text below is the draft as reviewed; where the two differ
the case governs. Nothing is approved and nothing is submitted. Ledger row: A5-186. Predecessor: the injected-rotation scan
([case](../../../results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md), verdict
`unresolved_none`) and its exploratory reading
([tuna17-null-rotation-scan-line-phase.md](tuna17-null-rotation-scan-line-phase.md)).

## Question

The null block b0 reads a selector offset with a static part near 0.014 that drifts between jobs and a part of
amplitude 0.025 that follows the phase of the shot-order line on q4's read bit. Three questions, each a device
fact:

1. Does an injected `Rz` on q12 move the static part as a phase on or around q12 predicts, and with which sign?
2. Is the static part a single-qubit phase on q12 or a conditional phase of coupler 8-12?
3. Is the quantity the line modulates the q12 phase itself, and does the oscillating part reverse beyond the q4
   angle where a straight line through the retained arms puts its zero?

## Why the retained data cannot answer it

The retained series varies pulse amplitudes only. In the forward model a q12 phase and a conditional phase on
coupler 8-12 fit its 24 contrasts almost equally (chi-square 205 and 187 with one parameter per batch), exact
pulses give an even response to a q12 phase, so the offset fixes its size (0.18 rad) and leaves its sign open, and
the q4 arms hold two angles (+-10 degrees) around a zero that lies between 0 and +20 degrees. No retained arm
acts on q8's side of coupler 8-12, where the two worlds differ most.

## Circuits

Every circuit is the retained b0 text with each `X90` as `Rx(pi/2)` (the center arm `b0-rx` of the predecessor),
rewritten on one qubit. Angles are multiples of pi/36, the processor's angle grid. The pulse count and the CZ count
of the `z12` and `z8c` arms equal the center's. Their schedule is unverified: the provider lists `Rz` as a native
operation and gives native single-qubit gates 20 ns under as-late-as-possible scheduling
([operational specifics](site/kbase_tuna-operational-specifics.md)), so the five `Rz` of a `z12` arm may add
100 ns on q12 and the four of a `z8c` arm 80 ns on q8, and no compile of these circuits has run. The minus and
plus arm of a pair hold the same `Rz` count; an arm and its center do not. Seven
distinct circuits:

- `b0-rx`: the center, in every data batch.
- `b0-rx-z12-m20`, `-p20`: an `Rz(phi)` on q12 before each of its 5 pulses, phi = -20 and +20 degrees. In the
  forward model the same `Rz` after each pulse gives the same laws, so one placement stands for both.
- `b0-rx-z8c-m10`, `-p10`: an `Rz(phi)` on q8 after each of the 4 CZ gates of coupler 8-12, phi = -10 and +10
  degrees.
- `b0-rx-q4-p5`, `-p20`: q4's 8 pulses at 95 and 110 degrees. The predecessor holds +-10 degrees.

## Batches

17 batches of at most 3 circuits. A readout batch [readout-0, readout-1] at 32,768 shots opens the series and
follows every data batch. Eight data batches at 131,072 shots per circuit, each [minus arm, `b0-rx`, plus arm] in
the forward round and reversed in the mirror round:

- `z12`: four batches (two forward, two mirror), so each of the two arms that carry the line test has four jobs;
- `z8c`: two batches;
- `q4`: two batches, [q4-p5, b0-rx, q4-p20].

Each data batch carries its own center, so the drift of the static part between batches enters no within-batch
comparison.

## Predictions

Mean selector contrast, with `d2_split` in parentheses for the center, `z12` and `z8c` rows, in the forward model at the retained mean bracket and
visibility 0.42 (`docs/evidence/qi-null-rotation-scan-line-phase/followup_predictions.py`). The standard error of
one contrast at 131,072 shots is 0.0028 and of one `d2_split` 0.0056.

| Arm | Exact pulses | q12 phase -0.18 rad | Coupler 8-12 phase -0.25 rad |
|---|---|---|---|
| center | 0.000 (0.000) | 0.014 (0.000) | 0.014 (+0.004) |
| z12 -20 degrees | 0.047 (+0.001) | 0.093 (+0.001) | 0.100 (-0.011) |
| z12 +20 degrees | 0.048 (+0.001) | 0.012 (0.000) | 0.020 (+0.018) |
| z8c -10 degrees | 0.003 (+0.006) | 0.032 (+0.006) | 0.038 (+0.037) |
| z8c +10 degrees | 0.010 (+0.018) | 0.007 (+0.017) | -0.001 (-0.006) |
| q4 +5 degrees | 0.000 | 0.008 | 0.007 |
| q4 +20 degrees | 0.000 | -0.006 | -0.010 |

A q12 phase of +0.18 rad gives the z12 rows exchanged. Evidence already retained: the `d2_split` of the 24
scan arms of the predecessor reads chi-square 427 under the q12 phase and 211 under the coupler phase at the
parameters of the contrast fits (`d2_split_worlds.py`), so the retained data lean to the coupler and fit neither. The z8c arms carry the separation of the two worlds: their
`d2_split` differs by 0.031 at -10 degrees and by 0.023 at +10 degrees, 7.8 and 5.8 standard errors of a two-job
mean, and the contrast at +10 degrees by 0.008. The retained q4 arms read 0.039 at -10 degrees and -0.006 at +10
degrees, a steeper line than either world gives (0.024 and 0.002; 0.028 and 0.000).

Line phase. With the contrast near 0.42 (phi0 + phi + A cos(theta))^2 in the total q12 phase, a line that
modulates that phase by A gives a first harmonic 0.84 A (phi0 + phi): the retained 0.025 at phi = 0 fixes A near
0.165 rad, and the z12 arms then read 0.073 at -20 degrees and 0.024 with reversed phase at +20 degrees. A line
that modulates another quantity leaves the first harmonic of the z12 arms near the center's 0.025. The same model
gives a second harmonic of 0.0057 at the center, where the retained series reads 0.0017 with a shot-noise error
of 0.0012, so the retained data already disfavor the first reading. In the retained q4 arms the first harmonic
reads 0.036 at -10 degrees and 0.006 at +10 degrees; a straight line through them and the center's 0.025 crosses
zero near +14 degrees. The +10 degree value rests on a fold without a detected reference, so rule 6 reads the
q4 arms by a reference-free amplitude.

## Decision rules (draft, fixed before any submission)

1. Admission: the readout guard of the predecessor on each data batch (e01 and e10 of the guard qubits steady
   across its two brackets), and a control that the center arms pooled over the admitted batches exceed 3
   standard errors.
2. Static part against phi. For each of three worlds (exact pulses, q12 phase, coupler 8-12 phase) fit one
   parameter per admitted `z12` and `z8c` batch to its three contrasts at the noise strength that reproduces the
   center visibility, over the predecessor's noise models. Six batches give 12 degrees of freedom; the adequacy
   bound is the 0.001 point, 32.91. Labels: `exact_parabola` (the exact world is adequate: the hypothesis of a
   phase on or around q12 is falsified), `q12_phase` or `coupler_phase` (that world is adequate and its chi-square
   lies at least 25 below the other's), `phase_unresolved` (both adequate, closer than 25), `none_adequate`.
3. Sign and size: the fitted q12 phase per batch with its interval.
4. `d2_split` of the `z8c` and `z12` arms, pooled over replicates, against each world's value: reported beside
   rule 2 and outside its label.
5. Line phase. The line's frequency and phase come from q4's bit on the odd-indexed shots of each job and the
   contrast is folded on the even-indexed shots (`line_phase_split.py`). Per arm, the first harmonic projected on
   the center's phase, with its error taken over jobs (the spread of the per-job projections) and an exact
   sign-flip p-value over the arm's jobs beside the shot-noise error; over four jobs that p-value is at least
   2/16 = 0.125, so it supports no label by itself. Labels: `line_on_q12_phase` (the two `z12`
   values follow 0.84 A (phi0 + phi) with the A and phi0 of rule 3 within 3 job-level standard errors each, the +20
   degree arm reversed), `line_elsewhere` (both within 3 of the center's value), `line_unresolved`.
6. q4. The mean contrast less its batch center at +5 and +20 degrees with the retained values at -10, 0 and +10
   degrees in one weighted straight-line fit (chi-square, zero crossing with its interval). For the oscillation,
   the reference-free amplitude of the selector-coin parity bit over the line band against its off-line maximum
   (`line_parity_amplitude.py`), since q4's bit reads at its off-line level at +10 degrees in the retained series and a signed
   fold has no reference there: the retained amplitudes are 0.0186, 0.0142 and 0.0067 at -10, 0 and +10 degrees
   against an off-line level near 0.005. Reported: the amplitudes at +5 and +20 degrees; an amplitude at +20
   degrees above the off-line maxima of its jobs reads as a return of the oscillation beyond its zero.

A5-186 changes only on `q12_phase` or `coupler_phase` with rule 1 passed, and then to the statement of that label;
every other outcome reports the numbers.

## Backend, shots, seconds, quota

- Backend: Tuna-17 (type 7), region q2, q4, q8, q11, q12. QX emulator (type 1) for the twin.
- Tuna-17 jobs and shots: 42 jobs in 17 batches, 3,735,552 shots (24 data jobs at 131,072, 18 readout jobs at
  32,768), every job at or under 131,072 shots and 72 to 92 s (2.6 s plus 0.53 ms per shot; 0.7 ms per shot
  planning rule, [usage.md](usage.md)) against the 300 s limit.
- QX twin: the seven distinct circuits at 2,048 shots in 3 batches, 7 jobs, 14,336 shots. Both together: 20
  batches, 49 jobs, 3,749,888 shots.
- Expected time: 35 to 45 minutes of execution at those two rates and 16 pauses. The wall-time ceiling
  takes the top pause step, 120 s ([usage.md](usage.md), "Pause escalation"): 32 minutes of pauses, 67 to 77
  minutes in all; at the 30 s step 43 to 53 minutes. The predecessor's 21 batches took 66 minutes. The execution
  seconds of the QX twin are not estimated.
- Queue rule: one batch of at most 3 circuits queued at a time, each collected before the next
  ([usage.md](usage.md), "Queue rules: the FAQ governs").
- Credits: expected 0, read from a fresh usage snapshot before the submission.

## Limits stated before the run

- The predictions use a contraction at one visibility; the gate-noise families and the measured brackets enter
  through the fit of rule 2, and the operating characteristics of the labels are not computed.
- The static part drifts on a scale of minutes (0.001 to 0.020 in the predecessor), so a fitted phase is a value
  per batch.
- The `Rz` placements are two: before each q12 pulse (equal in the model to after each pulse) and on q8 after
  each CZ of coupler 8-12. A phase that accumulates during idles commutes differently with the pulses and has no
  arm; a physical echo changes the pulse history and the schedule and belongs to a successor.
- The two-job arms (`z8c`, `q4`) have no job-level error of their own; rule 5's job-level calibration holds for
  the centers and the four-job `z12` arms.
- Rule 5 takes q4's bit as the phase reference in the `z12` arms and assumes that an `Rz` on q12 leaves q4's
  response to the line in place; an arm whose q4 bit carries no line (checked per job against the off-line band)
  has no signed harmonic, and its parity amplitude is reported in its place.
- The source of the line is unmeasured; rule 5 reads only whether its effect scales with the injected phase.

## Open defects of the rules

- An added `Rz` may change the timing of its qubit (see "Circuits"), so an arm-against-center difference mixes
  the injected phase with up to 100 ns of instruction time. The successor compiles every circuit, records the
  schedule, and either matches it across arms or states the difference.
- Rule 2 is no function of its inputs. With the bound 32.91, chi-squares (exact, q12, coupler) = (10, 5, 20)
  meet both `exact_parabola` and `phase_unresolved`, and (40, 20, 35) meet no label. The bound is uncalibrated
  for the minimum over noise models; the predecessor's rule removes one more degree of freedom
  (`adequacy_limit`, 11 here).
- Rule 2 fits one parameter per batch and holds no test that one world persists across batches, so batches of
  different worlds can sum to a label.
- The retained contrasts and `d2_split` reject both phase worlds by wide margins (187 and 205; 211 and 427), so
  `none_adequate` is the likely label unless the model widens, and its rate is not computed.
- Rule 5 names "the A and phi0 of rule 3", which rule 3 does not define, and gives no label for a `z12` job whose
  q4 bit carries no line.
- Rule 6 holds no label and no threshold: a band maximum above the off-line maxima is an observed maximum with
  no stated coverage.
- A q12 phase before every pulse, after every pulse, or before all but the first pulse gives the same laws, so a
  `q12_phase` label names that class and no single placement.

## Not built

- The generator (a successor of `scripts/qi_pathion_null_rotation_scan_cases.py` with the `z12` and `z8c` arms and the q4
  steps), its tests, `cases.json`, the batch directories and their `--check`.
- `prediction.json` with the operating characteristics of rules 2 and 5 under the three worlds and under gate
  noise, and a shot-level simulation of the line-phase statistic.
- A toolchain compile of every circuit (`scripts/qi_toolchain_check.py`) with the schedule read from it.
- The `--sanity` and `--analyze` paths and the replay gate of the retained analysis.
- The written case under `results/quantum_inspire/cases/`, its local review and the owner's approval, which
  precedes every provider job, the emulator included.
- After that approval: the QX twin and its control analysis, then the Tuna-17 series.

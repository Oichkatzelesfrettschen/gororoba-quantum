# Tuna-17 null rotation scan: exploratory reading of the retained series

Status: exploratory reanalysis of retained shots. It changes no retained record and no preregistered verdict: the
series reads `unresolved_none`
([analysis](../../../results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json)), and ledger row
A5-186 stays unchanged. Every statement below is measured on the 21 retained batches of 2026-11-15
(`results/quantum_inspire/runs/2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-*`), computed in the
forward model of `scripts/qi_pathion_null_rotation_scan_cases.py`, or marked `hypothesis:`. Scripts and their
outputs: [docs/evidence/qi-null-rotation-scan-line-phase](../../evidence/qi-null-rotation-scan-line-phase/). Subject:
the written case
[pathion_null_rotation_scan_tuna_17](../../../results/quantum_inspire/cases/pathion_null_rotation_scan_tuna_17/CASE.md).
Follow-up: [draft case](tuna17-null-phase-scan-case-draft.md).

## Result

The selector offset of the null block b0 has two parts. A constant component of about 0.014 drifts between jobs. A
second component follows the phase of the shot-order line of
[tuna-17.md](tuna-17.md) ("50 Hz"), which q4's read bit carries in every data job: the selector contrast of
`b0` and `b0-rx` reads about 0.014 + 0.025 cos(theta) over the line's phase theta. The pulse angle of q4 sets the
size of both components. No model fitted so far is adequate. The line is a periodic component of the retained
shot order; this series establishes neither that the order is execution time nor the line's source.

## What the scan arms read against exact pulses

`exact_pulse_residuals.py` computes the exact-pulse forward law of every arm at the gate-noise strength that
reproduces the batch's center visibility. Most of the wing response is the injected angle itself: exact pulses give
0.02 to 0.06 for the `all` arms at +-10 degrees, 0.06 to 0.08 at +-20 degrees and about -0.011 and +0.014 for the q8
arms (ranges over the five gate-noise families). Two readings lie outside it:

- the center arm, 0.001 to 0.020 over eleven jobs where exact pulses give 0;
- the q4 arms, 0.037 and 0.041 at -10 degrees and -0.004 and -0.007 at +10 degrees, where exact pulses give 0 at
  every q4 angle.

The eleven `b0-rx` readings are heterogeneous (chi-square 44.0 on 10 degrees of freedom, `time_bins.py`); inside
a job the eight consecutive shot bins stay below the 0.05 point of chi-square with 7 degrees of freedom in 21 of 24 jobs.

## Widened one- and two-parameter worlds

`widened_worlds.py`, `widened_worlds_round2.py` and `widened_worlds_round3.py` fit elementary errors to the 24 raw
selector contrasts under a contraction matched to each batch's center visibility. Candidates and falsifiers stand
in each script's docstring and were written before the fit.

| World | One parameter per batch (limit 39.25) | One shared parameter |
|---|---|---|
| exact pulses | 934 | 934 |
| conditional phase on coupler 8-12 | 187 | 307 at -0.25 rad |
| phase before each q12 pulse | 205 | 275 at -0.18 rad |
| conditional phase on every CZ | 248 | 633 |
| x rotation of every pulse | (preregistered: 515) | 870 |
| best preregistered world, y on q8 | 234.5 | |

A phase on q12 after each of its CZ gates equals the per-pulse phase to every digit, since q12 couples to q8 alone
in b0. Phase errors on q4, q8, q2, q11 and the other couplers leave the chi-square near the exact value. Pairs of
the two leading worlds with a second elementary error fit the forward round (54 on 10 degrees of freedom at best)
and fail the mirror round at the forward parameters (131 at best against 32.9). The per-batch q12 phase reads -0.16 to
-0.20 rad in six batches and -0.09 and +0.14 rad in batches 13 and 15.

A reviewer's computation during the review of the retaining change, not retained, ranks the same coupler first
(-0.28 rad, chi-square 249 with one contraction) and reports that it reproduces the signs of `d2_split` in every
arm outside the fit.

`full_histogram_fit.py` fits all 96 outcome counts per batch: every candidate reads 124,000 to 153,000 on 720
degrees of freedom, so the contraction is far from the device's law and that ranking carries no reading.

## Readout

`bracket_drift.py`: the selector's read value depends on q12's by 0.0047 (z = 2.4) with every register qubit
prepared 1 and by 0.0015 (z = 0.4) prepared 0, over 360,448 shots each. The best readout world needs a flip
probability of 0.036 to 0.042 at assignment, which would appear as a split of that size; a readout effect that
arises only after the gate schedule lies outside this test. q4's assignment moves during the series: e10 reads
0.050 to 0.060 in the first four brackets and 0.038 to 0.041 from minute 24 on (chi-square 439 on 10), e01 rises
from 0.009 to 0.015. The center offset follows another schedule (0.019 to minute 22, 0.001 at minute 45, 0.014 to
0.019 from minute 56).

The provider's batch identifier 958295 lies between batch-15 (958294) and batch-16 (958296) and is absent from
the account ledger; batch-16 waits about six minutes. hypothesis: another account's batch ran between them.

## The shot-order line

`line_scan.py` runs the repository's scanner (`scripts/qi_shot_record_line.py`) on all 62 jobs. None of the ten QX
jobs is detected. On Tuna-17 a line at 0.02011 to 0.02013 cycles per shot sits on q4's bit in nearly every data job
(first-harmonic amplitude 0.010 to 0.028 at a standard error of 0.002) and on q12's and q8's bits in rotated arms
(up to 0.029; band-corrected p down to 1e-36 at +-20 degrees). The reported execution time per shot (0.51 to
0.53 ms, which includes overhead) puts it at 38 to 40 Hz; this series measures no source. The `readout-1` jobs
carry a separate line at 0.02144 cycles per shot on qubit 6, outside the register.

`line_phase_bins.py` takes the line's frequency and phase of each job from q4's bit (phase 0 at the maximum of
P(q4 reads 1)) and reads the selector contrast in eight phase bins:

| Arm | Jobs | Mean contrast | First harmonic | Second harmonic |
|---|---|---|---|---|
| `b0-rx` | 11 | 0.0138 | 0.0252 (21.4 standard errors, phase +0.04) | 0.0017 (1.4) |
| `b0` | 3 | 0.0153 | 0.0278 (12.3) | 0.0028 (1.3) |
| q4 -10 degrees | 2 | 0.0388 | 0.0360 (13.0) | 0.0026 |
| q4 +10 degrees | 2 | -0.0059 | 0.0057 (2.0) | 0.0031 |
| q8 -10 / +10 degrees | 2 / 2 | -0.0059 / 0.0292 | 0.0023 / 0.0021 (0.8) | |
| all -10 / +10 degrees | 2 / 2 | 0.0493 / 0.0549 | 0.0104 (3.7) / 0.0087 (3.2, phase -2.65) | |
| all -20 / +20 degrees | 2 / 2 | 0.0722 / 0.0539 | 0.0177 (6.0, phase -3.10) / 0.0136 (4.8) | |

The quoted multiples are shot-noise ratios at the fitted phase. Each of the fourteen `b0` and `b0-rx` jobs shows
the first harmonic at 0.022 to 0.035. The fold of the same shots at 0.0237 cycles per shot gives 0.7 shot-noise
errors pooled.

`line_phase_split.py` removes the shared-shot path and calibrates at the job level. The frequency and phase come
from the odd-indexed shots and the fold uses the even-indexed ones: the coherent mean over the fourteen jobs is
0.0239 with a shot-noise error of 0.0015 (ratio 16.2) and an error over jobs of 0.0023 (10.6), which takes the
fitted phases, the frequency drift and the scatter between jobs as random. The exact sign-flip null over the
jobs gives p = 2/16384, its smallest value. The same maximize-then-fold procedure in an off-line band gives
0.0016 (shot-noise ratio 1.1, sign-flip p = 0.67).

`line_phase_conditionals.py` reads which probabilities carry it (first harmonics on the even shots, errors over
jobs):

| Statistic | First harmonic | Phase |
|---|---|---|
| P(selector reads 0 given coin reads 1) | 0.0086 +- 0.0009 | -0.25 |
| P(selector reads 0 given coin reads 0) | 0.0153 +- 0.0018 | +3.07 |
| selector contrast | 0.0239 +- 0.0023 | -0.14 |
| P(selector reads 0) | 0.0043 +- 0.0010 | -3.02 |
| P(coin reads 1) | 0.0004 +- 0.0009 | |
| contrast where q4 reads 0 / reads 1 | 0.0235 +- 0.0032 / 0.0241 +- 0.0024 | -0.07 / -0.21 |

The two conditional probabilities move in
opposite phase, so the contrast carries their sum while the marginals nearly cancel, and the dependence is the
same in both strata of q4's read value: an assignment effect of q4's read bit on the selector is excluded as its
path.

Readings:

- The constant component and the first harmonic vary independently in this series: batch-15's center reads a
  mean of 0.001 with a first harmonic of 0.025. A symmetric swing about zero that rectifies into the mean would
  carry a second harmonic near the mean; the second harmonic is 0.0017 against a mean of 0.0138, so that model is
  disfavored. How many device variables stand behind the two components is not identified.
- q4's injected angle scales both: -10 degrees raises the mean and the oscillation, +10 degrees removes the mean
  and lowers the oscillation to the null level of the reference-free statistic below.

The fold needs q4's bit as its phase reference, and the scanner detects no line on any bit in the q4 +10 and q8
+10 degree jobs, so a small folded harmonic there can be a lost reference. `line_parity_amplitude.py` needs none:
the selector-coin parity bit has mean near 1/2 + contrast/2, and its largest amplitude over the line band is
compared with the same maximum over an off-line band of equal width (0.004 to 0.006 in every arm):

| Arm | Parity bit, line band | q4 bit, line band |
|---|---|---|
| `b0-rx` / `b0` | 0.0142 / 0.0150 | 0.0116 / 0.0146 |
| q4 -10 / +10 degrees | 0.0186 / 0.0067 | 0.0156 / 0.0048 |
| q8 -10 / +10 degrees | 0.0047 / 0.0053 | 0.0231 / 0.0058 |
| all -10 / +10 degrees | 0.0078 / 0.0050 | 0.0205 / 0.0122 |
| all -20 / +20 degrees | 0.0096 / 0.0116 | 0.0110 / 0.0254 |

The centers read half their folded harmonic, as the parity relation gives. Both q8 arms read at the off-line
level, at -10 degrees with a strong reference on q4's bit, and the q4 +10 degree arm reads within 0.002 of it;
q4's own bit reads at its off-line level at q4 +10 and at q8 +10 degrees. These are observed band maxima: a
maximum over frequencies is biased upward and noise can add to or cancel a harmonic, so the table is descriptive
and sets no upper limit on an oscillation in those arms. A limit with stated coverage needs a calibration that
this analysis lacks.

## Phase-resolved fits

`phase_resolved_fit.py` lets one error parameter follow the line, u = u0 + A cos(theta), and fits the 72 pooled
phase-bin contrasts and the nine q4 line amplitudes of the nine `Rx` arm types. No candidate is adequate (limit
112.3 on the contrasts, 70 degrees of freedom): a conditional phase on coupler 8-12 reads 315 and a phase on q12
376 (before its pulses and after its CZ gates alike), and both predict no line on q4's bit, so the alignment of
each arm to the line is unidentified in them and each arm takes the better of the two; a conditional phase on
every CZ reproduces q4's amplitudes and reads 806. `phase_resolved_two_source.py` drives two parameters with one phase: the best pair, a
conditional phase on coupler 4-8 (static -0.025 rad, oscillating 0.125 rad) with a phase on q12 (static -0.15 rad,
oscillating 0.10 rad), reads 304 against 109.8 (68 degrees of freedom).

## Model facts that bear on the next case

Computed in the forward model at the retained mean bracket and visibility 0.42 (`followup_predictions.py`):

- Exact pulses read 0 at every q4 angle. With a q12 phase of -0.18 rad the q4 response is linear, 0.024 at -10
  degrees to -0.006 at +20 degrees; with a conditional phase of -0.25 rad on coupler 8-12 it runs from 0.028 to
  -0.010.
- Under exact pulses the contrast is even in a phase on q12: 0.0128 at +-10 degrees, 0.047 at +-20 degrees, about
  0.42 phi^2. The static offset of 0.014 therefore corresponds to a q12 phase of 0.18 rad of either sign, and an
  injected `Rz` on q12 reads the sign: with -0.18 rad present, +10 degrees gives 0.000 and -10 degrees gives 0.048.
- A conditional phase on coupler 8-12 leaves 0.020 at +20 degrees on q12 with `d2_split` +0.018, where the q12
  phase gives 0.012 with `d2_split` below 0.001.
- An `Rz` on q8 after each CZ of coupler 8-12 separates the two most: at -10 and +10 degrees `d2_split` reads
  +0.006 and +0.017 under the q12 phase and +0.037 and -0.006 under the coupler phase.
- `d2_split_worlds.py` scores the retained `d2_split` of the 24 scan arms, which no fit used, at the shared
  parameters of the contrast fits: chi-square 1125 under exact pulses, 427 under the q12 phase and 211 under the
  coupler phase. The retained data favor the coupler phase and fit neither.
- All 45 `Rz` angles of b0 are multiples of the processor's pi/36 angle grid, so the grid rounds none of them.

## Open

- hypothesis: one slowly drifting phase on q12 or on coupler 8-12 carries the constant component. Falsifier: the
  draft case's `Rz` arms on q12 read the exact-pulse parabola centered at zero.
- hypothesis (from the review of this note): q4's drive reaches the joint response of the coin and the selector,
  which the opposite phases of the two conditional probabilities admit. Falsifier: the first harmonic stays under a
  q4 angle that the retained trend puts beyond its zero (the draft's +20 degree arm).
- A record order that the provider's serialization imposes is not excluded as the line's origin; the fourteen
  fitted phases do not lock to the record start (circular resultant 0.42 in the review's computation).
- The source and the path of the line (flux pickup against another path, [tuna-17.md](tuna-17.md)) are unseparated.
- The gate-noise families are untried in the phase-resolved and full-histogram fits.
- The public calibration dashboard returned no series for the run date (its data source timed out on every
  query); the series ages out about 30 days after the run.
- The forward-against-mirror consistency of the preregistered fit and a successor record for the case text's
  status line belong to the change that registers the claim.

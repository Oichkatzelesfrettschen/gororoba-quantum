# Measurement sequence: pinching on a Heron r2 qubit

The `measurement-sequence` family asks whether a mid-circuit measurement on an IBM Heron r2 qubit acts
as an ideal pinching, a nonselective projective measurement in Z. The source candidate is item 1 of
"Experiment candidates" in
[the proposal audit](../archive/reviews/quantum-recovery-proposal-audit.md); this note fixes the angle,
the arms and the endpoints. The code is `measurement_sequence_groups` and `measurement_sequence_contracts`
in `gororoba_quantum/diagnostic_experiments.py`, planned by `measurement_sequence_candidates` in
`gororoba_quantum/qpu_planning.py` and selected with `live_run.py --family measurement-sequence
--layout Q1,Q2,...`.

## Circuit

A named physical qubit starts in |0> and receives N steps of `RX(sign * THETA / N)`, with the total
rotation THETA = 8 pi / 9 (160 degrees), N in (1, 2, 4, 8, 16) and sign + or -.

- **Measure arm (N = 2, 4, 8, 16).** Each rotation is followed by a measurement into the next bit of a mid-circuit register
  `mcm` (N bits). The program never reads or conditions on those bits, and the raw shots keep them. After
  the N steps a final measurement writes the 1-bit register `final`, the only register an endpoint reads.
  The circuit holds no reset, no feed-forward and no settling delay.
- **Delay arm, the elapsed-time control.** The circuit is identical except that each mid-circuit measurement
  is replaced by a `delay` of the qubit's measure duration in dt, taken from the fresh Target
  (`qpu_planning.measurement_delay`, the rule `folded_group` uses). The only measurement is the final one.
  The delay keeps the elapsed time and drops the projection, but idle dephasing pinches the qubit as well, so
  the delay arm's P0 rises above its ideal. Its gap to the unitary arm is the share of the Zeno rise that idle
  dephasing explains; the kingston dry run models the delay arm at N = 16 as 0.09 to 0.17 against the ideal
  0.030, and Garnet near 0.46.
- **Unitary arm, the mutation null (N = 16 only).** Sixteen `RX(sign * THETA / 16)` rotations run back to
  back with a `barrier` on the qubit between consecutive rotations, then the final measurement. The barriers
  stop the transpiler from merging the rotations into one gate (without them the run compiles to two `sx`
  in all; with them 32 `sx` and 15 barriers survive), so the circuit applies the full rotation count in the
  shortest time and holds neither a measurement nor an idle. Its ideal P0 is cos(THETA / 2)^2.
- **Settle arm, the gap-lengthening control (N = 16 only).** The measure arm with a `delay` of 2.0 us after each
  mid-circuit measurement, before the next rotation, rounded up to the Target's timing granularity
  (`qpu_planning.settle_delay`). It is dynamic, like the measure arm, and its ideal law is the measure arm's
  joint law (final P0 0.8914). The 2 us gap is an experimental hypothesis: the repository's Heron r2 sources
  ([readout resonator note](../notes/ibm_quantum/heron-r2-readout-resonator.md)) state no device-matched
  ring-down or residual-photon decay time, so the gap is not a validated bound. The arm tests whether
  lengthening the gap after each measurement from zero (the measure arm) to 2 us changes the deficit.
- **T1 arm (static, per qubit).** `x`, a `delay` of t, the pre-readout delay, then the final measurement, for t
  in (0, 20, 50, 100, 200) us converted to dt like the other idles (a zero t omits the idle). One member per t,
  `msq_t1_d{k}_q{Q}`, k = 0..4. Each is a single circuit, not a signed quartet. The ideal law is the noise-free
  P1 = 1; the noise model prices the decay from the Target's T1 when the planner simulates it.
- **ro0 (static, per qubit).** A `delay` of the pre-readout idle, then the final measurement of a qubit that
  starts in |0>: `msq_ro0_q{Q}`, ideal law P1 = 0, no endpoint. With the t1 member at idle 0 (`x`, the same wait,
  the same read; the analysis calls it ro1) it brackets the final read's offset and scale, which corrects every
  arm. The family runs with no twirling and no dynamical decoupling (`live_run.py` refuses `--twirl` and `--dd`
  with `--family`), so the static job that holds ro0 and ro1 and the dynamic job that holds the measure and
  settle arms read through the same unsymmetrized `measure` after the same 2 us idle.
- **Pre-readout delay (every member).** A `delay` of 2.0 us, rounded up to the Target's timing granularity
  (`qpu_planning.prereadout_delay`), precedes the final measurement of every member of every arm and is
  recorded per qubit as `prereadout_delay_dt`. Residual readout photons of the last mid-circuit measurement
  may bias the final assignment of the measure and settle arms, and the unitary and delay arms carry no
  such history to cancel it. The 2 us pre-readout delay in every member is a hypothesized allowance for that
  history, subject to the same missing decay-time figure as the settle gap; it equalizes the wait across
  members and removes no bias that a measurement has shown.

The four arms carry four roles: the measure arm is the object of the test, the unitary arm is the mutation
null that removes the property under test, the delay arm is the elapsed-time control, and the settle arm is
the gap-lengthening control. The t1 arm measures the qubit's relaxation in the job. The case analysis ([Decision rule](#decision-rule))
fits T1 from the t1 members and uses that fit, not the Target's T1, for the measure-arm and settle predictions,
because the T1 lift at N = 16 is decision-sized.

Register order is `final` (clbit 0), then `mcm`. A measure member's ideal law and score weights span all
N + 1 clbits, the convention of the N=21 segmented family (`qpe_diagnostics.n21_segmented_law`), and the
weights select final = 0. The delay and unitary arms have one clbit.

## Ideal law

After each measurement the qubit state is diagonal in Z, so the next rotation by phi = THETA / N repeats the
last outcome with probability cos(phi / 2)^2. The Z expectation shrinks by cos(phi) per step, so the
measure arm's final P0 is

    P0_measure(N) = (1 + cos(THETA / N)^N) / 2

and the delay and unitary arms compose their rotations coherently into `RX(sign * THETA)`, so in the ideal

    P0_delay = P0_unitary = cos(THETA / 2)^2 = 0.0302.

| N | P0 measure | P0 delay and unitary | measure - unitary |
|---|------------|----------------------|-------------------|
| 1 | 0.0302 | 0.0302 | 0.0000 |
| 2 | 0.5151 | 0.0302 | 0.4849 |
| 4 | 0.6722 | 0.0302 | 0.6420 |
| 8 | 0.8040 | 0.0302 | 0.7738 |
| 16 | 0.8914 | 0.0302 | 0.8612 |

The measure arm runs at N = 2, 4, 8, 16 (the N = 1 row is the reference value shared with the delay arm); the
unitary arm runs at N = 16 only; the delay arm runs at every N.

The values come from `msq_pinched_p0` and `msq_delay_p0`; `diagnostic_experiments.py --self-test` checks
them against exact density-matrix evolution (rotate, keep the diagonal, N times) and unitary evolution to
1e-12.

## Arms and order

Each (arm, N) holds four signed members named `msq_{arm}_n{N}_{s}{r}_q{qubit}`, where `s` is `p` for
`RX(+THETA / N)` or `m` for `RX(-THETA / N)` and `r` is the repeat letter. They run in the order
`pa`, `ma`, `mb`, `pb`, that is +, -, -, +, so a linear drift cancels in the pooled mean. The two signs
share one ideal law because cosine is even, so the signed difference carries no contrast.

`local_compute.is_dynamic` classifies a circuit with a gate after a measurement as dynamic. The measure arm
and the settle arm are dynamic; the delay, unitary, ro0 and t1 arms are static. The measure arm does not run at N = 1: its ideal 0.0302
equals the delay arm's, so it carries no pinching information, and its measure, pre-readout delay, measure sequence would fuse
into a dynamic PUB among static components. One group holds one job kind, so
each qubit owns a static group `msq_static_q{qubit}` (30 members: the delay arm
at each N, the unitary arm, ro0, then the five t1 members) and a dynamic group `msq_dynamic_q{qubit}` (20 members: the measure arm at N = 2, 4, 8, 16, then the settle arm).
Row r of each kind fuses across the named qubits into one PUB, so every qubit runs the same member in the
same shots, 30 static and 20 dynamic PUBs in all. The dynamic job runs with twirling and dynamical
decoupling off.

## What the family isolates

The state after each measurement is diagonal in Z, so a readout-induced frequency shift delta that
persists into the next rotation acts only during the pulse of duration tau, at second order in delta * tau.
For tau <= 100 ns and delta <= 2 pi * 100 kHz the flip probability at N = 16 moves by about -2.5e-6 per step.
Interpreting a departure still needs a control: the settle arm inserts a 2 us gap after each measurement. A
deficit that stays unchanged when the gap grows from zero to 2 us bounds only the tail component that decays
within 2 us; a tail slower than 2 us stays unexcluded. A deficit that shrinks with the gap attributes that part
to a tail. A measured P0 below the ideal (a
positive deficit, `q{Q}_msq_deficit_n{N}` in the summaries) measures transitions that the
measurement induces once the unitary and delay controls separate it from rotation error and idle
dephasing, and the settle arm bounds a readout tail that decays within 2 us. The calibration noise model treats a mid-circuit measurement as projective, so it prices
the measure arm at readout error and decoherence alone, and only the device answers this. The unitary
arm removes the projection and the idle: its P0 stays at cos(THETA / 2)^2 up to gate and readout error,
and the N = 16 contrast of the measure and unitary arms is the mutation-test endpoint. The delay arm holds
the elapsed time fixed and removes the projection, so measure minus delay at N = 16 isolates what the
measurement adds beyond the idle dephasing of the same duration. The family fits no
per-measurement transition parameter; that is post hoc analysis of the retained shots.

## Endpoints

Per qubit, seventeen two-sided precision endpoints split the family-wise alpha evenly:

- `msq_p0_measure_n{N}_q{Q}` for N in (2, 4, 8, 16): the final P0 pooled over the four signed members of
  the measure arm, half-width 0.03.
- `msq_p0_delay_n{N}_q{Q}`: the same for the delay arm, half-width 0.03.
- `msq_p0_unitary_n16_q{Q}`: the same for the unitary arm, half-width 0.03.
- `msq_p0_settle_n16_q{Q}`: the same for the settle arm, half-width 0.03.
- `msq_p1_t1_d{k}_q{Q}` for k = 0..4: the t1 member's P1, half-width 0.03. T1 is a contract because the
  predictions depend on its fitted value.
- `msq_zeno_contrast_n16_q{Q}`: measure minus unitary at N = 16, ideal 0.8612, half-width 0.055.

A pooled member carries score values at weight 1/4. The optimizer treats each PUB as a stream of span 0.25
with the tail alpha_endpoint divided by the stream count, so a pooled P0 over 4 PUBs has the radius
sqrt(ln(8 / alpha_endpoint) / (2 shots)) and the contrast over 8 PUBs has 2 * sqrt(ln(16 / alpha_endpoint) /
(2 shots)). At alpha 0.05 and 14 qubits (alpha_endpoint 2.10e-4) a pooled P0 reaches 0.0254 at 8192 shots and
0.0359 at 4096, a t1 P1 (one PUB, radius sqrt(ln(2 / alpha_endpoint) / (2 shots))) 0.0237 and 0.0334, and the
contrast 0.0524 and 0.0741. The 0.05 starting half-width for the contrast fails at
8192 shots with 14 qubits, so the contrast half-width is 0.055. The smallest admitted power-of-two tier is
8192 shots from 1 to 14 qubits (`diagnostic_experiments.py --self-test` checks 1, 4 and 14).

In the FakeFez planning fixture with one qubit, 8192 shots plan 30 static PUBs at about 69.3 s of charge and 20
dynamic PUBs at about 47.3 s, 116.6 s in all, against 60.6 s at 4096 (the 4096 tier fails the declared half-widths and
the 16384 tier the per-job ceiling).

The 2 us pre-readout delay in every member is a hypothesized allowance for readout history and carries no
in-job validation. An in-job N = 1 measure-versus-delay diagnostic cannot run in this family, because the measure arm's N = 1 member
would fuse as a dynamic PUB among static components; the IQM Garnet case keeps that N = 1 diagnostic because its
circuits do not fuse.

The measure arm at N = 16 carries 17 clbits, so each ideal law, prediction and score vector holds 131072
entries, and the exact-oracle comparison of every compiled replica (`qpe_diagnostics.ideal_compiled_probabilities`)
enumerates 2^17 branches in about 10 s per N = 16 member.

## Decision rule

This section fixes the analysis before any data of this family exists. The rule, the tables below and the
constants are bound to the run by the experiment digest: `measurement_sequence_analysis.py` sits in
`live_run.EXPERIMENT_SOURCE_MANIFEST`, so `--collect` refuses a record whose digest differs.

### Where the analysis runs

`live_run.py --collect` writes the analysis to `collect.json` as `family_analysis.pinching`, beside the generic
precision endpoints. `qpu_planning.measured_family` dispatches to `measurement_sequence_analysis.collected`, the
route `et-row` and `folded-correction` take. `adjudicate.py` holds a second analysis of the raw
registers, named by its own digest (`adjudicate.py` plus `live_run.py` plus package versions) and a replay seed,
so a decision written there would not be bound to the circuits' experiment digest and would arrive after the data.
`adjudicate.py` stays free for post hoc work on the retained shots, such as a per-measurement transition fit.

The analysis runs only when every member of both jobs executed under one calibration
(`runtime._comparisons_withheld`); otherwise `pinching` reports the reason. Counts are the member's distribution
times its executed shots, and flips between consecutive mid-circuit bits come from the joint law over the N + 1
clbits, so no raw register is read. `live_run.py` adds `placed_gate_calibration` (the sx error and duration and the
measure duration from `BackendProperties` at the PUB's execution start) to the execution evidence of this family.

### Readout correction across the two jobs

The static job holds ro0, the t1 series and the delay and unitary arms; the dynamic job holds the measure and
settle arms. The family runs with `--twirl` and `--dd` refused, so neither job symmetrizes readout or inserts
dynamical decoupling into the pre-readout idle, and both read through the same `measure` after the same 2 us
idle. The correction (Zobs - o) / s, with the offset o and scale s from ro0 and ro1, therefore transfers to the
dynamic job's final read. The transfer fails if the final read after a mid-circuit measurement carries a readout
history that ro0 and ro1 lack; the family has no N = 1 measure member, so no in-job diagnostic separates that bias
from a pinching departure (see Limits).

### Model

The Bloch iteration (`measurement_sequence_analysis.chain_matrix`) plays each RX step in its compiled form
`rz(pi/2) sx rz(THETA/N + pi) sx rz(pi/2)`. T1 and T2 act during each sx, and a depolarizing shrink 1 - lambda
follows it, with lambda = 2 (e_sx - r) for the Target's sx error e_sx and the first-order relaxation error
r = t / (3 T2) + t / (6 T1) of the gate (never below zero). The sx pair carries the state through the equator,
so T2 decays the information a pinched qubit holds in z. The arm then pinches (zeroes the transverse part) or
stays coherent, and relaxes with T1 and T2 over its idle: a fraction f of the measure duration, plus the settle
idle for the settle arm, or the delay arm's idle. The state is diagonal after every measurement, so T2 acts on
the measure arm only through the gates.

- The sx pair needs the Target's sx error, not a prx error. It is read from `BackendProperties` at execution
  start, with a systematic of 100 % of its value entered as an absolute shift of the depolarizing remainder
  (`SX_SYSTEMATIC = 1`). The shift stays active when r exceeds e_sx (a short Ramsey T2), where the remainder is zero.
- The Target's measure duration spans the readout pulse and the integration, and the projection falls somewhere
  inside it. The post-measurement state relaxes for a fraction f of it. f has no calibrated value, so the analysis
  takes f = 0.5 with the variance 1/12 of a uniform distribution on [0, 1] (`WINDOW_RELAX_FRACTION`). The Aer noise
  model of a backend charges no relaxation during a measure instruction (f = 0), which the planning row of the
  validation table exercises.
- The initial excitation p enters only through q = z_eq / (1 - 2 p), which the t1 series fits. The planning tables
  use p = 0.015745, the largest initialization bound over 149 qubits at the 250 us repetition delay
  (`results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md`); the same findings measure a shot-history effect of
  +0.00003 at 250 us, so the model carries one p per qubit and no dependence on the previous circuit.
- T1 and q come from the t1 series (x, idle of 0, 20, 50, 100, 200 us) after the ro0/ro1 correction. The
  predictions are recomputed at the fitted values; the calibrated T1 enters only the planning tables.

The statistics are the Garnet analysis's: every group's binomial variance (Agresti-Coull-shifted proportion), the sx
shift and f propagate through the joint fit, correction and model by the delta method, and each pooled group sums
the four signed members' counts. The sx shift and f are shared by every qubit of a device, so the delta method
reports them apart from the statistical part.

### Per-qubit tests

Z_DECIDE = 3 standard errors throughout, from the full standard error (statistics, T1 and q fit, sx shift, f and the
gate-model systematic below).

1. Readout floor. A qubit whose fitted readout scale lies below 0.5 is unusable and makes no decision.
2. Mutation test. It passes when the N = 16 contrast (measure minus unitary P0) exceeds 0.5 by 3 standard errors.
3. Departure test. z = (measured - predicted) / SE for the measure arm's N = 16 P0 against the ideal-projective
   prediction at the fitted T1 and q: `departs_below` (z <= -3), `consistent`, `exceeds_prediction` (z >= 3).
4. Gap test. The settle arm's N = 16 P0 against the prediction at the per-step z loss the measure arm implies. The
   2 us gap is an experimental hypothesis (the repository's Heron r2 sources give no ring-down time), so the test
   asks only whether lengthening the gap after each measurement from zero to 2 us changes the deficit:
   `reduced_by_gap` (z >= 3), `unchanged_by_gap`, `deepened_by_gap` (z <= -3). `unchanged_by_gap` bounds only a
   tail component that decays within 2 us; a slower tail stays unexcluded.
5. Informative qubit. A qubit is informative when it is usable, its mutation test passes and its widened departure
   standard error is at most twice its planning value (`PLANNING_SE_FACTOR = 2`). The planning value is the departure
   standard error of the analysis run on the expected counts of the planning model, widened by the scatter floor when
   one is set (`planning_departure_se`). Any other qubit is `uninformative` and leaves the count and pooled rules.

### Gate-model systematic

The unitary arm (thirty-two sx, no measurement, no idle) tests the gate model in the job, but its residual does not
veto a run. Its measured-minus-modeled N = 16 P0 bounds what a gate-model error can do to the measure arm, and
that shift adds in quadrature to the departure standard error.

Four error classes perturb the sx model (`GATE_CLASSES`): depolarizing error (an absolute shift of the
depolarizing error per sx), a factor on the transverse decay rate during the drive, a tilt of the second sx's
rotation axis from the first's, and an over-rotation of the pi / 2 pulse. A tilt common to every sx is a frame
change about Z that leaves every z population unchanged, so only the relative tilt acts. The sx pair crosses the
equator, so these errors reach the measure arm; a mid-circuit measurement erases a phase error only for a single
small-angle pulse, not for a composite step. For each class, `gate_propagation` finds the smallest magnitude, on
each side of nominal and within the stretch where the unitary shift moves one way, that reproduces the observed
residual, and takes the measure-arm shift that magnitude produces. The ratios (measure-arm shift over unitary-arm
shift) at the fixture calibration, over the eight fixture qubits, for a residual of +0.01 and -0.01:

| Class | Ratio, residual +0.01 | Ratio, residual -0.01 |
|---|---|---|
| depolarizing error | -0.82 to -0.80 | -0.82 to -0.80 |
| dephasing during the drive | -0.52 to -0.51 | -0.52 to -0.51 |
| relative axis tilt | +0.29 to +0.30 | +0.57 to +0.58 |
| pi / 2 over-rotation | +0.12 to +0.13 | a negative residual lies outside the class (its shift is second order and positive) |

The largest shift over the classes is the qubit's propagated systematic. Classes of opposite unitary sign cancel in
the unitary arm and add on the measure arm, so a qubit's own residual can sit at zero while its measure arm moves.
The systematic therefore also takes the shifts that a residual equal to the device scatter, plus and minus, would
carry (`widen_for_device_scatter`); the device scatter is the root-mean-square of the usable qubits' residuals,
floored at the model scatter when one is set.

### Source of the model-scatter floor

No value is registered. A floor must come from retained Kingston unitary data with a known ideal outcome: the
model scatter of observed-minus-modeled P0 across qubits, with the model built as `chain_matrix` builds it. The
search covered the 233 `record.json` files under `results/live/` (262 run directories) and the research registry
(`docs/state/research_state.json`, 276 acquisitions, 32 on IBM backends). The Kingston runs hold
`qubit_baseline` (ground, one x, Ramsey), the state-prep controls, the rank-sector, ripple, correction and N=21
families (multi-qubit circuits with cz) and the 2026-10-25 measurement-sequence dry run (Aer outcomes, no hardware
shots). None holds a single-qubit sx sequence of useful length with a known ideal outcome, so no defensible scatter
exists, and the constant `MODEL_SCATTER_FLOOR` is `None`.

With the floor unset, a fired `departs_below` or `exceeds_prediction` verdict reads `gate_model_unbounded` and
attributes nothing to the measurement; the gap verdicts compare arms of equal gate count and need no floor. A
measured floor needs a Heron diagnostic that spends quantum time and the owner's approval: the unitary arm (four
signed members at N = 16) on many qubits in one static PUB set, whose per-qubit residuals give the scatter; its run
and computation then go in this section and the value replaces `None`. The sweeps and the Aer validation below use
`DEMONSTRATION_SCATTER_FLOOR = 0.015`, an illustrative value that exercises the mechanism and measures no device.
The largest floor that keeps a fixture qubit informative is about 0.0175, so a measured scatter beyond that makes
the family uninformative on that device.

### Device verdicts

`device_verdict` combines the informative qubits. A verdict (`departs_below`, `exceeds_prediction`,
`settle_reduced_by_gap`, `settle_deepened_by_gap`) fires when at least two informative qubits return it or the pooled
z over them reaches 3 in its direction. With fewer than two informative qubits every verdict reads `uninformative`,
so `none` always means a clean null. The mutation test must pass on every usable qubit for the device to read a
passing mutation test; a failing qubit is uninformative.

The pooled z weights qubits by inverse total variance. Statistical errors are independent across qubits and add in
quadrature; the sx shift, f and the gate-model systematic are shared by the device and add linearly, so pooling
eight qubits does not shrink them (`pooled_z`).

False-flag arithmetic for eight informative qubits, with a correct model: a per-qubit two-sided 3-standard-error
test fires with probability 0.0027, so the sixteen per-qubit departure and gap tests raise at least one descriptive
per-qubit outcome in about 4 % of null runs, and the per-qubit outcomes stay descriptive. A device verdict fires
through the pooled z with probability at most 0.00135 and through the count rule (two or more of eight) with
probability 5e-5, about 0.14 % per direction and 0.55 % over the four verdicts; the shared systematics lie in the
pooled denominator but not in a null run's noise, so these are upper bounds.

Minimum detectable departure, a per-step z loss eps injected in both pinched arms (`minimum_detectable`, retained in
`docs/evidence/measurement_sequence/minimum-detectable.json`, demonstration floor):

| Row | Pooled eps at pooled z = -3 | Mean N = 16 P0 shift there | Per-qubit eps at z = -3 | Mean departure SE |
|---|---|---|---|---|
| planning | 0.0039 | -0.044 | 0.0042 to 0.0054 (median 0.0044) | 0.0155 |
| model error, residual about +-0.01 | 0.0038 | -0.044 | 0.0041 to 0.0052 (median 0.0043) | 0.0155 |

### Tables

The model sweep (`measurement_sequence_analysis.py sweep`; rows retained in
`docs/evidence/measurement_sequence/model-sweep.json`) runs the real `evaluate` and `device_verdict` over expected
counts of model devices, rounded to whole shots, for eight qubits scaled from the fixture calibration, with the
demonstration floor. It tests the estimator, not the model: it draws no random number and holds no seed. The pass
rule is fixed in `sweep_failures`, by the `expect` of each row: `clean` (every qubit at |departure z| < 1, gap
verdict `unchanged_by_gap`, every device status `none`), `none` (every status `none`, never `uninformative`),
`not_attributed` (no departure attributed; `uninformative` satisfies it), `departure` (`departs_below` attributed,
gap verdict unchanged), `tail` (`settle_reduced_by_gap` attributed), `uninformative` and `either`. The model-error
rows inject a gate-model error per qubit: dephasing during the drive x0.5 and x1.5 (residual about +-0.002), a
moderate set (dephasing x5, tilt +-0.0035 rad; residual about +-0.01) and a large set (dephasing x12, tilt
+-0.0085 rad; residual about +-0.03). The tilt rows pair a negative tilt with an sx error whose unitary sign is
opposite, the cancellation case.

| Row | Informative qubits | Departure z, per qubit | Pooled departure z | Unitary residual | Propagated SE | Device status |
|---|---|---|---|---|---|---|
| planning | 8 of 8 | -0.01 to 0.01 | -0.00 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| p=0 | 8 of 8 | -0.01 to 0.00 | -0.00 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| p=0.04 | 8 of 8 | -0.01 to 0.00 | -0.00 | -0.000 to +0.000 | 0.0121 to 0.0123 | none |
| thermal 0.01 | 8 of 8 | -0.00 to 0.01 | 0.00 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| T1 x0.8 | 8 of 8 | -0.01 to 0.01 | -0.00 | -0.000 to +0.000 | 0.0119 to 0.0122 | none |
| T1 x1.2 | 8 of 8 | -0.00 to 0.01 | 0.00 | -0.000 to +0.000 | 0.0121 to 0.0123 | none |
| window x1.05 | 8 of 8 | 0.01 to 0.02 | 0.02 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| no relaxation in the window | 8 of 8 | -0.40 to -0.24 | -0.32 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| full relaxation in the window | 8 of 8 | 0.24 to 0.38 | 0.30 | -0.000 to +0.000 | 0.0120 to 0.0122 | none |
| sx x2 | 8 of 8 | -0.67 to -0.35 | -0.50 | +0.006 to +0.015 | 0.0120 to 0.0123 | none |
| sx x3 | 8 of 8 | -0.87 to -0.53 | -0.71 | +0.013 to +0.030 | 0.0173 to 0.0242 | none |
| sx x4 | 7 of 8 | -0.93 to -0.61 | -0.80 | +0.019 to +0.044 | 0.0232 to 0.0357 | none |
| measure eps 0.01 | 8 of 8 | -7.21 to -5.58 | -7.04 | -0.000 to +0.000 | 0.0120 to 0.0122 | attributed, none |
| tail eps 0.01 (measure arm only) | 8 of 8 | -7.21 to -5.58 | -7.04 | -0.000 to +0.000 | 0.0120 to 0.0122 | attributed, none |
| model error, drive dephasing x0.5 and x1.5 | 8 of 8 | -0.07 to 0.07 | 0.00 | -0.002 to +0.002 | 0.0120 to 0.0122 | none |
| model error x0.5 and x1.5 + measure eps 0.02 | 8 of 8 | -12.47 to -9.72 | -12.24 | -0.002 to +0.002 | 0.0120 to 0.0122 | attributed, none |
| model error, residual about +-0.01 | 8 of 8 | -0.45 to 0.25 | -0.12 | -0.008 to +0.012 | 0.0120 to 0.0122 | none |
| model error +-0.01 + sx x3 | 8 of 8 | -1.10 to -0.34 | -0.68 | +0.004 to +0.033 | 0.0212 to 0.0263 | none |
| model error +-0.01 + measure eps 0.02 | 8 of 8 | -12.63 to -9.79 | -12.30 | -0.008 to +0.012 | 0.0120 to 0.0122 | attributed, none |
| model error, residual about +-0.03 | 8 of 8 | -0.62 to 0.36 | -0.19 | -0.017 to +0.033 | 0.0216 to 0.0271 | none |
| model error +-0.03 + sx x3 | 1 of 8 | -0.92 to -0.08 | n/a | -0.004 to +0.050 | 0.0324 to 0.0402 | uninformative |
| model error +-0.03 + measure eps 0.02 | 8 of 8 | -8.01 to -6.68 | -7.36 | -0.017 to +0.033 | 0.0216 to 0.0271 | attributed, none |
| axis tilt -0.016 + sx x3 | 8 of 8 | -2.21 to -1.88 | -2.12 | -0.008 to +0.010 | 0.0120 to 0.0122 | none |
| axis tilt -0.022 + sx x4 | 8 of 8 | -2.97 to -2.14 | -2.88 | +0.002 to +0.028 | 0.0121 to 0.0228 | none |
| corner | 8 of 8 | -0.64 to -0.34 | -0.47 | +0.006 to +0.015 | 0.0119 to 0.0122 | none |

The Aer validation (`scripts/measurement_sequence_validation.py`; summaries in
`docs/evidence/measurement_sequence/aer-validation.json`) compiles the 50 members per qubit onto the FakeFez Target
for eight qubits, simulates every entry with `live_run.noise_simulator` at 8192 shots and runs `collected` with the
demonstration floor. Shot-sampled rows use the 3-standard-error rule. The four seeds are values 0 to 3 of
`docs/evidence/anu_qrng/draw-2026-10-25T225550Z.json`, one per row in order.

| Row | Informative qubits | Departure z, per qubit | Pooled departure z | Unitary residual | Propagated SE | Device status |
|---|---|---|---|---|---|---|
| planning (Target as reported) | 8 of 8 | -0.68 to -0.07 | -0.36 | -0.003 to +0.002 | 0.0119 to 0.0122 | none |
| sx errors x4 | 8 of 8 | -1.37 to -1.01 | -1.19 | +0.012 to +0.029 | 0.0156 to 0.0226 | none |
| flip 0.01 after each measure-arm measurement | 8 of 8 | -8.56 to -7.63 | -8.32 | -0.002 to +0.001 | 0.0119 to 0.0121 | attributed |
| flip 0.01 after each measure- and settle-arm measurement | 8 of 8 | -8.38 to -7.57 | -8.30 | -0.006 to +0.002 | 0.0119 to 0.0122 | attributed |

The planning row passes with every qubit inside |z| < 1 and no verdict; the sx row widens each departure standard
error through the unitary residual and attributes nothing; the flip rows show the gap verdict moving only when the
flip is absent from the settle arm.

### Limits

- The scatter floor is unmeasured (see its section). Until it is, no departure is attributed to the measurement.
  Combinations of a relative tilt and an sx error that cancel in the unitary arm were scanned (tilt -0.006 to -0.03 rad
  against sx errors x2 to x6, demonstration floor): the largest pooled z was -2.88, at a tilt of -0.022 rad with sx x4.
  A larger cancelling error than the floor covers would attribute a departure that is a gate error.
- The post-measurement relaxation fraction f and the compiled duration of a mid-circuit measure are not verified
  against the backend scheduler tables of a run; the analysis takes the Target's duration and carries f as a
  systematic.
- The final read that follows a mid-circuit measurement can carry a readout history that ro0 and ro1 lack. Heron
  has no N = 1 measure member in this family (the Garnet case keeps that diagnostic), so a bias of that kind reads as
  a pinching departure and, because the settle arm has the same final read, as an unchanged gap. The agreement of the
  last mid-circuit bit with the final bit at N = 16 (`repeat_read_n16`, from the joint law) is a descriptive stand-in.
- ro1 puts every qubit in |1> at once, while the measure arm's neighbors vary from shot to shot, so
  state-dependent simultaneous-readout crosstalk is uncalibrated.
- The Aer validation runs on the FakeFez calibration, not a retained ibm_kingston Target, and an Aer noise model
  holds no mid-circuit measurement physics beyond readout error and decoherence.

## Tuna-17 port

THETA / N = 8 pi / (9 N) is a multiple of pi / 36 for every N in the set (32, 16, 8, 4 and 2 units of
pi / 36), so each rotation lies on Tuna-17's angle grid
([backends](../notes/quantum_inspire/backends.md)). Repeated mid-circuit readouts of one qubit beyond the
retained `readout_ringdown_tuna_17` runs are unverified there, so a Tuna-17 port starts with a dry run of the
N = 16 measure arm.

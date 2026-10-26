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
change about Z that leaves every z population unchanged, so only the relative tilt acts. The relative tilt is odd
under the rotation sign: the reflection x -> -x maps the sign -1 chain at tilt d onto the sign +1 chain at -d, while
depolarizing error, drive dephasing and the angle error are reflection-invariant. The experiment pools the four signed
members (+, -, -, +) with equal weight, so the model compares the mean of the two signs (`chain_matrix(sign=...)`,
`corrected_z`), and a tilt moves the pooled unitary and measure arms only at second order. A model that evaluated the
sign +1 chain alone showed a first-order tilt effect (unitary P0 -0.011 and +0.016 at d = +-0.005 against +0.002 pooled)
that the data cannot carry; `device_counts` likewise generates each signed member from its own sign. The sx pair crosses the
equator, so these errors reach the measure arm; a mid-circuit measurement erases a phase error only for a single
small-angle pulse, not for a composite step. For each class, `gate_propagation` finds the smallest magnitude, on
each side of nominal and within the stretch where the unitary shift moves one way, that reproduces the observed
residual, and takes the measure-arm shift that magnitude produces. The ratios (measure-arm shift over unitary-arm
shift) at the fixture calibration, over the eight fixture qubits, for a residual of +0.01 and -0.01:

| Class | Ratio, residual +0.01 | Ratio, residual -0.01 |
|---|---|---|
| depolarizing error | -0.82 to -0.80 | -0.82 to -0.80 |
| dephasing during the drive | -0.52 to -0.51 | -0.52 to -0.51 |
| relative axis tilt | -0.02 | a negative residual lies outside the class (its pooled shift is second order and positive) |
| pi / 2 over-rotation | +0.12 to +0.13 | a negative residual lies outside the class (its shift is second order and positive) |

The largest shift over the classes is the qubit's propagated systematic. Depolarizing error and drive dephasing
shift the unitary arm one way on each side of nominal and the measure arm the other, so a model that overpredicts one
and underpredicts the other can leave a qubit's own residual at zero while its measure arm moves by the difference of
their ratios (-0.8 and -0.5).
The systematic therefore also takes the shifts that a residual equal to the device scatter, plus and minus, would
carry (`widen_for_device_scatter`); the device scatter is the root-mean-square of the usable qubits' residuals,
floored at the model scatter when one is set.

### Source of the model-scatter floor

No value is registered. A floor must come from Kingston single-qubit sx-sequence data with a known ideal outcome: the
model scatter of observed-minus-modeled P0 across qubits, with the model built as `chain_matrix` builds it. The
search covered the 233 `record.json` files under `results/live/` (262 run directories) and the research registry
(`docs/state/research_state.json`, 276 acquisitions, 32 on IBM backends). The Kingston runs hold
`qubit_baseline` (ground, one x, Ramsey), the state-prep controls, the rank-sector, ripple, correction and N=21
families (multi-qubit circuits with cz) and the 2026-10-25 measurement-sequence dry run (Aer outcomes, no hardware
shots). None holds a single-qubit sx sequence of useful length with a known ideal outcome, so no defensible scatter
exists, and the constant `MODEL_SCATTER_FLOOR` is `None`.

`collected` takes the floor from `MODEL_SCATTER_FLOOR` when that is set and otherwise from the diagnostic file
`MODEL_SCATTER_FLOOR_FILE` (`docs/evidence/measurement_sequence/scatter-floor.json`) when
`MODEL_SCATTER_DIAGNOSTIC_SHA256` names its SHA-256 digest, the file carries schema
`measurement-sequence-scatter-floor-v1` and a floor in (0, 1), and its `backend` is the backend of the run. With
neither it withholds the whole pinching analysis (`family_analysis.pinching.withheld`), because a main run without a
floor can only report `gate_model_unbounded` on a fired departure verdict and attributes nothing. The digest constant
sits in `measurement_sequence_analysis.py`, which is in `live_run.EXPERIMENT_SOURCE_MANIFEST`, so the experiment
digest of every later main run binds the floor file by content. The sweeps and the Aer validation below use
`DEMONSTRATION_SCATTER_FLOOR = 0.015`, an illustrative value that exercises the mechanism and measures no device.

#### The diagnostic family

`live_run.py --family measurement-sequence-diagnostic --layout Q1,Q2,...` plans the members of the main family that need
no measurement history, built by the main family's own functions under the main family's names, so the circuits are
identical (`diagnostic_experiments.py --self-test` compares each one): the four signed unitary members at N = 16 in the
order +, -, -, +, ro0, and the t1 member at idle 0 (ro1). Every member is static, so each row fuses across all named
qubits into one PUB and the run holds six static PUBs in one job, with no mid-circuit measurement, twirling or
dynamical decoupling. A PUB lasts about one repetition cycle per shot whatever the qubit count, which puts 38 qubits at
the cost of one. Two endpoints per qubit admit the design at the main family's half-width 0.03: the pooled unitary P0
(`msq_p0_unitary_n16_qQ`) and ro1's P1 (`msq_p1_t1_d0_qQ`); 8192 shots admit up to 60 qubits.

The qubits are the main family's eight (91, 118, 95, 61, 147, 151, 59, 89, `MSQD_MAIN_QUBITS`) and thirty further qubits
chosen from the live Target alone by `measurement_sequence_scatter.select_extra_qubits`, which the command
`measurement_sequence_scatter.py select` runs against a backend (a calibration read, no job):

- A further qubit is eligible when the live Target does not exclude it, reports a readout error of at most 0.01 and an
  sx error of at most 1e-3 (both bounds cover the eight main qubits), and reports T1 and T2 of at least 20 us.
  On the Kingston Target of 2026-10-25 18:19 PDT the readout bound sits near the median (0.0093) and the sx bound above
  the 95th percentile (8.7e-4); no bound selects on T1 or T2 beyond the 20 us minimum, so the T2 pattern test below
  keeps its spread.
- It must couple to no main qubit and to no kept qubit, so the 38 qubits are pairwise uncoupled and share no coupler
  (the eight main qubits are pairwise uncoupled on ibm_kingston).
- The eligible qubits are scanned in ascending readout error (ties by qubit index), each kept when no coupler joins it
  to a main or kept qubit, until thirty are kept. The ascending order draws the extra qubits from the same quality
  class as the main eight, whose readout errors (0.0037 to 0.0056) lie in the best quarter of the Target, so the floor describes the
  qubits the main verdict uses.

The layout is pinned on the command line. The planner refuses a layout with a repeated qubit, a qubit the live Target
excludes or a pair joined by a coupler (`layout_violations`), records the roles in `main_qubits` and `extra_qubits`
and records each qubit's readout error, sx error, T1 and T2 at planning in `plan_calibration`. `floor_document`
refuses a run whose `main_qubits` differ from `MSQD_MAIN_QUBITS`.

#### Model path of the residual

The diagnostic has no t1 series, so the unitary model cannot fit T1 and q in the job. It evaluates
`model_tables(t1_cal_s, q_planning, ctx)["unitary"]["16"]`, the function the main analysis calls for the unitary arm,
at the Target's T1 at execution and the planning excitation `PLANNING_P_INIT` (q = 1 / (1 - 2 p)). The 32 sx last about
1 us and the arm has no idle, so the modeled P0 depends on T1 and q only through the relaxation during the gates:
T1 x 0.5 to x 2 and p from 0 to 0.1 move it by at most 0.0009 on the eight main qubits (about a tenth of the smallest
floor of interest). The readout correction is the analysis's: offset and scale from ro0 and ro1, `(Zobs - o) / s`.
The residual is the corrected P0 minus the model; its statistical standard error propagates the binomial variances
(Agresti-Coull-shifted, `msa.var`) of ro0, ro1 and the pooled unitary members through `propagate_many`, and the sx
systematic of 100 % of the reported sx error is reported apart as `se_sx_systematic`.

#### Floor rule (preregistered before any diagnostic data)

An informative diagnostic qubit has a fitted readout scale of at least 0.5 (`READOUT_CONTRAST_FLOOR`). The scale test is
the only rejection: no outlier removal follows, because a qubit whose gate model fails is the scatter the floor must
carry. The floor is the larger of the root-mean-square, over the informative qubits, of the readout-corrected unitary
N = 16 residual taken over all informative qubits and over the informative main qubits alone, and statistical noise stays
in.

- Statistical noise stays in, as it did for the Garnet floor. The residual's statistical standard error is about 0.002
  per qubit at 8192 shots (the Aer planning row, 0.0021), so keeping it raises a floor of 0.02 by 0.5 % and errs
  towards a wider departure standard error. The summary reports the all-qubit root-mean-square, the root-mean-square
  statistical standard error and the root-mean-square less the latter in quadrature
  (`rms_all_less_statistical_in_quadrature`), so a reader sees how much of the floor counting noise explains.
- Both populations enter. The extra qubits give the estimate its statistical weight: its relative sampling error is
  1 / sqrt(2 n), 0.11 for the 38 qubits and 0.35 for the eight alone. The main qubits are the ones the main verdict
  applies to, so a floor below their own root-mean-square would understate; the rule takes the larger, and the summary
  reports `rms_all`, `rms_main` and `rms_extra`.
- At least 20 informative qubits (`MIN_INFORMATIVE`) are needed; fewer give no floor and the file is not written.

The summary also reports the mean residual (a common-mode offset enters the root-mean-square in full), the per-qubit
residuals with their standard errors, and the descriptive T2 pattern: the Spearman rank correlation of the residual with
T2 (and with the sx error), its two-sided p value from the t approximation on n - 2 degrees of freedom, and the sign
counts in the lowest and highest T2 terciles. The drive-dephasing lead seen on Garnet predicts residuals above 0 on long
T2 qubits and below 0 on short ones, a positive rank correlation. The pattern enters no decision.

`measurement_sequence_scatter.py floor RUN_DIR --out FILE` writes `scatter-floor.json` from a collected diagnostic run
directory (`record.json` and `collect.json`, `family_analysis.scatter`): the floor, backend, both rule texts, the qubit
lists, the summary, the T2 pattern, every qubit's row and the digests of the record, collect.json, the experiment and
both modules. Registering it sets `MODEL_SCATTER_DIAGNOSTIC_SHA256` to the file's digest in the same change; the main
case is then planned again, because the analysis digest changes.

#### Aer validation of the estimator

`scripts/measurement_sequence_scatter_validation.py` (summaries in
`docs/evidence/measurement_sequence/scatter-validation.json`) plans the diagnostic on FakeFez (the fixture excludes
q91, so it runs 7 main qubits and 31 further qubits chosen by the same rule), simulates every entry with
`live_run.noise_simulator` at 8192 shots and runs `measurement_sequence_scatter.collected`. An RZ gate after every sx of the
compiled unitary members moves a qubit's ideal P0 by a chosen amount (the relative-tilt class); a tilt of one sign
moves the +THETA and -THETA members in opposite directions, so the error is solved per member from the compiled
step. The seeds are values 0 to 3 of `docs/evidence/anu_qrng/draw-2026-10-26T013550Z.json`, one per
row in order.

| Row | Statistical rms | rms, all 38 | rms, main 7 | rms, extra 31 | Floor | T2 rank correlation (p) |
|---|---|---|---|---|---|---|
| planning (Target as reported) | 0.0021 | 0.0019 | 0.0007 | 0.0021 | 0.0019 | -0.05 (0.8) |
| tilt +-0.02, alternating by qubit index | 0.0022 | 0.0199 | 0.0210 | 0.0197 | 0.0210 | +0.10 (0.6) |
| tilt +0.03 on the 7 main qubits only | 0.0022 | 0.0123 | 0.0282 | 0.0024 | 0.0282 | +0.03 (0.8) |
| tilt +0.02 above and -0.02 below the median T2 | 0.0022 | 0.0194 | 0.0210 | 0.0190 | 0.0210 | +0.71 (6e-07) |

The pass rules are fixed in `violations`: the planning floor stays within `(1 + 3 / sqrt(2 n))` times
`sqrt(statistical_rms ** 2 + 0.003 ** 2)` (0.003 allows the Aer-versus-model mismatch of the existing validation, about
0.002); the injected rows recover `sqrt(mean(injected ** 2) + planning_floor ** 2)` within 10 %, every residual
carries the injected sign, and the main-only row's floor equals the main-qubit root-mean-square (0.0282 for an injected
0.03) because the all-qubit value (0.0123) lies below it. The planning row shows the estimator returns about the
statistical scatter (0.0020 against 0.0021) when the model is right, and the injected rows show that a per-qubit model
error of 0.02 comes back as a floor of 0.0210, with the sign pattern against T2 recovered (rank correlation +0.71)
when the error is ordered by T2. The pattern test finds nothing in the alternating row (p 0.56), where no order exists.

The diagnostic's model has no tilt, and each injected error is solved per signed member, so the floors above are the
same to four digits before and after the analysis pooled the two rotation signs. A tilt common to all four members
would show the sign dependence instead: the +THETA and -THETA members move in opposite directions and the pooled unitary
P0 moves at second order only (`test_axis_tilt_is_odd_under_the_sign_and_the_pool_is_even`), so the floor measures the
sign-even model error, which is the part the measure arm's pooled observable carries.

#### What a floor value means for the main case

The floor widens each qubit's departure standard error by about 0.8 of its value (the depolarizing class,
`propagated_se`), so the smallest per-step transition rate the device rule detects at pooled z = -3 on the eight fixture
qubits grows with it (`minimum_detectable`, 8192 shots): 0.0030 at a floor of 0.01, 0.0049 at 0.02 and 0.0097 at 0.04.
The planning standard error includes the floor, so the informative-qubit rule does not remove qubits as the floor
grows; the cost appears as detection power. The Garnet diagnostic measured about 0.04 on its pi / 2-pair arm. A
Kingston floor near 0.04 would leave the main run able to attribute only a transition rate near 0.01 per step, and the
owner decides at that value whether the main run is worth its quantum time.

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
| model error, residual -0.016 to +0.014 | 0.0039 | -0.043 | 0.0040 to 0.0060 (median 0.0044) | 0.0155 |

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
moderate set (dephasing x5 and a device with no drive dephasing and no sx error; residuals +0.014 and -0.016) and a
large set (dephasing x12, a tilt of 0.02 rad and the same -0.016 device; residuals up to +0.033). The unitary arm
pools the four signed members, so a tilt moves it upward at second order only; the two tilt rows (0.02 and 0.03 rad)
pair that second-order shift with an sx error of three and four times the Target's and read uninformative, with no
departure attributed. An earlier version evaluated the sign +1 chain alone, which showed a first-order tilt shift that
cancels in the pool and gave a pooled z of -2.12 and -2.88 on the cancelling tilt rows; that cancellation does not
exist in the pooled observable.

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
| sx x3 | 8 of 8 | -0.87 to -0.58 | -0.77 | +0.013 to +0.030 | 0.0156 to 0.0242 | none |
| sx x4 | 7 of 8 | -0.93 to -0.61 | -0.80 | +0.019 to +0.044 | 0.0232 to 0.0357 | none |
| measure eps 0.01 | 8 of 8 | -7.21 to -5.58 | -7.04 | -0.000 to +0.000 | 0.0120 to 0.0122 | attributed, none |
| tail eps 0.01 (measure arm only) | 8 of 8 | -7.21 to -5.58 | -7.04 | -0.000 to +0.000 | 0.0120 to 0.0122 | attributed, none |
| model error, drive dephasing x0.5 and x1.5 | 8 of 8 | -0.07 to 0.07 | 0.00 | -0.002 to +0.002 | 0.0120 to 0.0122 | none |
| model error x0.5 and x1.5 + measure eps 0.02 | 8 of 8 | -12.47 to -9.72 | -12.24 | -0.002 to +0.002 | 0.0120 to 0.0122 | attributed, none |
| model error, residual -0.016 to +0.014 | 8 of 8 | -0.49 to 0.61 | 0.02 | -0.016 to +0.014 | 0.0120 to 0.0127 | none |
| model error -0.016..+0.014 + sx x3 | 8 of 8 | -0.80 to 0.54 | -0.14 | -0.016 to +0.028 | 0.0161 to 0.0223 | none |
| model error -0.016..+0.014 + measure eps 0.02 | 8 of 8 | -12.69 to -9.16 | -12.21 | -0.016 to +0.014 | 0.0120 to 0.0127 | attributed, none |
| model error, residual -0.016 to +0.033 | 8 of 8 | -0.62 to 0.43 | -0.16 | -0.016 to +0.033 | 0.0224 to 0.0271 | none |
| model error -0.016..+0.033 + sx x3 | 0 of 8 | -0.76 to 0.31 | n/a | -0.016 to +0.054 | 0.0338 to 0.0429 | uninformative |
| model error -0.016..+0.033 + measure eps 0.02 | 8 of 8 | -7.76 to -6.32 | -6.98 | -0.016 to +0.033 | 0.0224 to 0.0271 | attributed, none |
| axis tilt 0.02 + sx x3 | 0 of 8 | -0.49 to -0.26 | n/a | +0.044 to +0.060 | 0.0405 to 0.0484 | uninformative |
| axis tilt 0.03 + sx x4 | 0 of 8 | -0.42 to -0.21 | n/a | +0.088 to +0.108 | 0.0773 to 0.0876 | uninformative |
| corner | 8 of 8 | -0.64 to -0.34 | -0.47 | +0.006 to +0.015 | 0.0119 to 0.0122 | none |

The Aer validation (`scripts/measurement_sequence_validation.py`; summaries in
`docs/evidence/measurement_sequence/aer-validation.json`) compiles the 50 members per qubit onto the FakeFez Target
for eight qubits, simulates every entry with `live_run.noise_simulator` at 8192 shots and runs `collected` with the
demonstration floor. Shot-sampled rows use the 3-standard-error rule. The four seeds are values 0 to 3 of
`docs/evidence/anu_qrng/draw-2026-10-25T225550Z.json`, one per row in order.

| Row | Informative qubits | Departure z, per qubit | Pooled departure z | Unitary residual | Propagated SE | Device status |
|---|---|---|---|---|---|---|
| planning (Target as reported) | 8 of 8 | -0.68 to -0.07 | -0.36 | -0.003 to +0.002 | 0.0119 to 0.0122 | none |
| sx errors x4 | 8 of 8 | -1.44 to -1.01 | -1.22 | +0.012 to +0.029 | 0.0153 to 0.0226 | none |
| flip 0.01 after each measure-arm measurement | 8 of 8 | -8.56 to -7.63 | -8.32 | -0.002 to +0.001 | 0.0119 to 0.0121 | attributed |
| flip 0.01 after each measure- and settle-arm measurement | 8 of 8 | -8.38 to -7.57 | -8.30 | -0.006 to +0.002 | 0.0119 to 0.0122 | attributed |

The planning row passes with every qubit inside |z| < 1 and no verdict; the sx row widens each departure standard
error through the unitary residual and attributes nothing; the flip rows show the gap verdict moving only when the
flip is absent from the settle arm.

### Limits

- The scatter floor is unmeasured (see its section). Until its file is registered, the pinching analysis withholds.
  Depolarizing error and drive dephasing are the classes that shift the unitary arm in one direction and the measure arm
  in the other (ratios -0.8 and -0.5); a model that overpredicts one and underpredicts the other can hide a measure-arm
  shift of the difference of the two ratios times the unitary shift, which the device-scatter widening covers up to
  the floor. A larger offsetting error than the floor covers would attribute a departure that is a gate error.
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

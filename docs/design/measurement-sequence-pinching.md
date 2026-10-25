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
- **Pre-readout delay (every member).** A `delay` of 2.0 us, rounded up to the Target's timing granularity
  (`qpu_planning.prereadout_delay`), precedes the final measurement of every member of every arm and is
  recorded per qubit as `prereadout_delay_dt`. Residual readout photons of the last mid-circuit measurement
  may bias the final assignment of the measure and settle arms, and the unitary and delay arms carry no
  such history to cancel it. The 2 us pre-readout delay in every member is a hypothesized allowance for that
  history, subject to the same missing decay-time figure as the settle gap; it equalizes the wait across
  members and removes no bias that a measurement has shown.

The four arms carry four roles: the measure arm is the object of the test, the unitary arm is the mutation
null that removes the property under test, the delay arm is the elapsed-time control, and the settle arm is
the gap-lengthening control. The t1 arm measures the qubit's relaxation in the job. The case analysis fits T1
from the t1 members and uses that fit, not the Target's T1, for the measure-arm and settle predictions, because
the T1 lift at N = 16 is decision-sized.

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
and the settle arm are dynamic; the delay, unitary and t1 arms are static. The measure arm does not run at N = 1: its ideal 0.0302
equals the delay arm's, so it carries no pinching information, and its measure, pre-readout delay, measure sequence would fuse
into a dynamic PUB among static components. One group holds one job kind, so
each qubit owns a static group `msq_static_q{qubit}` (29 members: the delay arm
at each N, the unitary arm, then the five t1 members) and a dynamic group `msq_dynamic_q{qubit}` (20 members: the measure arm at N = 2, 4, 8, 16, then the settle arm).
Row r of each kind fuses across the named qubits into one PUB, so every qubit runs the same member in the
same shots, 29 static and 20 dynamic PUBs in all. The dynamic job runs with twirling and dynamical
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
measurement induces once the unitary, delay and settle controls separate it from rotation error, idle
dephasing and a readout tail. The calibration noise model treats a mid-circuit measurement as projective, so it prices
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

In the FakeFez planning fixture with one qubit, 8192 shots plan 29 static PUBs at about 67.2 s of charge (64.9 s
of execution plus 2.3 s overhead) and 20 dynamic PUBs at about 47.3 s, 114.5 s in all, against 59.6 s at 4096.

The 2 us pre-readout delay in every member is a hypothesized allowance for readout history and carries no
in-job validation. An in-job N = 1 measure-versus-delay diagnostic cannot run in this family, because the measure arm's N = 1 member
would fuse as a dynamic PUB among static components; the IQM Garnet case keeps that N = 1 diagnostic because its
circuits do not fuse.

The measure arm at N = 16 carries 17 clbits, so each ideal law, prediction and score vector holds 131072
entries, and the exact-oracle comparison of every compiled replica (`qpe_diagnostics.ideal_compiled_probabilities`)
enumerates 2^17 branches in about 10 s per N = 16 member.

## Tuna-17 port

THETA / N = 8 pi / (9 N) is a multiple of pi / 36 for every N in the set (32, 16, 8, 4 and 2 units of
pi / 36), so each rotation lies on Tuna-17's angle grid
([backends](../notes/quantum_inspire/backends.md)). Repeated mid-circuit readouts of one qubit beyond the
retained `readout_ringdown_tuna_17` runs are unverified there, so a Tuna-17 port starts with a dry run of the
N = 16 measure arm.

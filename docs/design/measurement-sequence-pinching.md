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

- **Measure arm.** Each rotation is followed by a measurement into the next bit of a mid-circuit register
  `mcm` (N bits). The program never reads or conditions on those bits, and the raw shots keep them. After
  the N steps a final measurement writes the 1-bit register `final`, the only register an endpoint reads.
  The circuit holds no reset, no feed-forward and no settling delay.
- **Delay arm, the mutation null.** The circuit is identical except that each mid-circuit measurement is
  replaced by a `delay` of the qubit's measure duration in dt, taken from the fresh Target
  (`qpu_planning.measurement_delay`, the rule `folded_group` uses). The only measurement is the final one.

Register order is `final` (clbit 0), then `mcm`. A measure member's ideal law and score weights span all
N + 1 clbits, the convention of the N=21 segmented family (`qpe_diagnostics.n21_segmented_law`), and the
weights select final = 0. The delay arm has one clbit.

## Ideal law

After each measurement the qubit state is diagonal in Z, so the next rotation by phi = THETA / N repeats the
last outcome with probability cos(phi / 2)^2. The Z expectation shrinks by cos(phi) per step, so the
measure arm's final P0 is

    P0_measure(N) = (1 + cos(THETA / N)^N) / 2

and the delay arm composes its rotations coherently into `RX(sign * THETA)`, so at every N

    P0_delay = cos(THETA / 2)^2 = 0.0302.

| N | P0 measure | P0 delay | measure - delay |
|---|------------|----------|-----------------|
| 1 | 0.0302 | 0.0302 | 0.0000 |
| 2 | 0.5151 | 0.0302 | 0.4849 |
| 4 | 0.6722 | 0.0302 | 0.6420 |
| 8 | 0.8040 | 0.0302 | 0.7738 |
| 16 | 0.8914 | 0.0302 | 0.8612 |

The values come from `msq_pinched_p0` and `msq_delay_p0`; `diagnostic_experiments.py --self-test` checks
them against exact density-matrix evolution (rotate, keep the diagonal, N times) and unitary evolution to
1e-12.

## Arms and order

Each (arm, N) holds four signed members named `msq_{arm}_n{N}_{s}{r}_q{qubit}`, where `s` is `p` for
`RX(+THETA / N)` or `m` for `RX(-THETA / N)` and `r` is the repeat letter. They run in the order
`pa`, `ma`, `mb`, `pb`, that is +, -, -, +, so a linear drift cancels in the pooled mean. The two signs
share one ideal law because cosine is even, so the signed difference carries no contrast.

`local_compute.is_dynamic` classifies a circuit with a gate after a measurement as dynamic. The measure arm
at N >= 2 is dynamic; the N = 1 measure arm and the delay arm are static. One group holds one job kind, so
each qubit owns a static group `msq_static_q{qubit}` (24 members: the N = 1 measure arm, then the delay arm
at each N) and a dynamic group `msq_dynamic_q{qubit}` (16 members: the measure arm at N = 2, 4, 8, 16).
Row r of each kind fuses across the named qubits into one PUB, so every qubit runs the same member in the
same shots, 24 static and 16 dynamic PUBs in all. The dynamic job runs with twirling and dynamical
decoupling off.

## What the family isolates

The state after each measurement is diagonal in Z, so a frequency shift of the qubit after readout rotates a
diagonal state into itself and leaves the measure arm's P0 unchanged. A measured P0 below the ideal (a
positive deficit, `q{Q}_msq_deficit_n{N}` in the summaries) therefore measures transitions that the
measurement induces. The calibration noise model treats a mid-circuit measurement as projective, so it prices
the measure arm at readout error and decoherence alone, and only the device answers this. The delay arm
holds the elapsed time fixed and removes the projection: its P0 stays at cos(THETA / 2)^2 up to
decoherence, and the N = 16 contrast of the two arms is the mutation-test endpoint. The family fits no
per-measurement transition parameter; that is post hoc analysis of the retained shots.

## Endpoints

Per qubit, eleven two-sided precision endpoints split the family-wise alpha evenly:

- `msq_p0_measure_n{N}_q{Q}` for N in (1, 2, 4, 8, 16): the final P0 pooled over the four signed members of
  the measure arm, half-width 0.03.
- `msq_p0_delay_n{N}_q{Q}`: the same for the delay arm, half-width 0.03.
- `msq_zeno_contrast_n16_q{Q}`: measure minus delay at N = 16, ideal 0.8612, half-width 0.055.

A pooled member carries score values at weight 1/4. The optimizer treats each PUB as a stream of span 0.25
with the tail alpha_endpoint divided by the stream count, so a pooled P0 over 4 PUBs has the radius
sqrt(ln(8 / alpha_endpoint) / (2 shots)) and the contrast over 8 PUBs has 2 * sqrt(ln(16 / alpha_endpoint) /
(2 shots)). At alpha 0.05 and 14 qubits (alpha_endpoint 3.25e-4) a P0 reaches 0.0248 at 8192 shots and
0.0351 at 4096, and the contrast 0.0514 and 0.0727. The 0.05 starting half-width for the contrast fails at
8192 shots with 14 qubits, so the contrast half-width is 0.055. The smallest admitted power-of-two tier is
8192 shots from 1 to 14 qubits (`diagnostic_experiments.py --self-test` checks 1, 4 and 14).

The measure arm at N = 16 carries 17 clbits, so each ideal law, prediction and score vector holds 131072
entries, and the exact-oracle comparison of every compiled replica (`qpe_diagnostics.ideal_compiled_probabilities`)
enumerates 2^17 branches in about 10 s per N = 16 member.

## Tuna-17 port

THETA / N = 8 pi / (9 N) is a multiple of pi / 36 for every N in the set (32, 16, 8, 4 and 2 units of
pi / 36), so each rotation lies on Tuna-17's angle grid
([backends](../notes/quantum_inspire/backends.md)). Repeated mid-circuit readouts of one qubit beyond the
retained `readout_ringdown_tuna_17` runs are unverified there, so a Tuna-17 port starts with a dry run of the
N = 16 measure arm.

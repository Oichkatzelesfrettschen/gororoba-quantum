# Latency-recovery findings on ibm_kingston

## Run

- Record: [2026-10-25T193443.839527Z](2026-10-25T193443.839527Z/collect.json), job
  `dbf5kdom94ac738ssug0`, on the backup account.
- Approved dry run: [2026-10-25T192932.145570Z](2026-10-25T192932.145570Z/CASE_ADDENDUM.md);
  the submission reused its predictions under unchanged calibration values.
- Calibration: 2026-10-25T12:18:10-07:00, with medians T1 258 us and
  T2 163 us.
- Executed layout: physical qubits [106, 105, 104, 117, 107, 125] for r, d0,
  d1, d2, a0, a1 (`groups[0].replicas[0].initial_layout` of record.json; the
  scheduler tables touch only these qubits). The console's
  [150, 151, 138, 152, 149, 153] is the routing template the replica was
  placed from, and no measurement ran there.
- Execution: 34 dynamic PUBs at 16384 shots, 50 us repetition delay; 40 s
  charged against 40.44 s predicted.
- L = 215 dt (0.86 us). W = 2500 dt (10 us).

The design is [heron-latency-logical-recovery.md](../../docs/design/heron-latency-logical-recovery.md).

## Preregistered contracts

All intervals are Hoeffding intervals at alpha 0.05/7 per endpoint, from
`family_analysis` in collect.json.

| Contract | Estimate | Interval | Reading |
|---|---:|---|---|
| recovery, F(`ff_0`) - null | 0.745 | [0.699, 0.790] | holds: above 0.5 |
| code_property, F(`ff_0`) - F(`ff_0_unencoded`) | 0.553 | [0.507, 0.598] | holds: above 0.25 |
| latency_cost, F(`frame_0`) - F(`ff_0`) | 0.010 | [-0.035, 0.055] | unresolved |
| latency_is_idle, F(`frame_l`) - F(`ff_0`) | -0.004 | [-0.049, 0.041] | inside +-0.049, not inside +-0.01 |
| window_cost_ff, F(`ff_0`) - F(`ff_w`) | 0.217 | [0.172, 0.262] | resolved |
| window_cost_frame, F(`frame_l`) - F(`frame_lw`) | 0.223 | [0.178, 0.268] | resolved |
| window_slope, their difference | -0.006 | [-0.101, 0.088] | inside +-0.101, not inside +-0.01 |

The feed-forward correction recovers the injected error. F(`ff_0`) is 0.780
against the no-correction null of 0.035, and the unencoded arm reads 0.227,
near its ideal 1/4.

## Executed exposures

The controller overlaps a requested delay with the feed-forward broadcast, so
each arm's exposure comes from the returned schedule.
`scripts/latency_recovery_exposure.py --run results/live/2026-10-25T193443.839527Z`
reads it as the cycles (4 ns) from the end of the syndrome captures to the
first decode CZ:

| Arm | Exposure (cycles) | Exposure (us) |
|---|---:|---:|
| `frame_0` | 107 | 0.428 |
| `ff_0` | 317 | 1.268 |
| `frame_l` | 322 | 1.288 |
| `ff_w` | 2754 | 11.016 |
| `frame_lw` | 2822 | 11.288 |

Every basis of an arm shares its exposure.

Feed-forward exposes the block for 210 cycles (840 ns) more than `frame_0`.
`frame_l` matches `ff_0` to within 5 cycles, so `latency_is_idle` compares
equal exposures. Its interval, -0.049..0.041, includes 0. The controller
latency and the conditional therefore cost no resolved fidelity beyond the
idle they impose; the T1/T2 model puts that idle at 0.006.

The requested 2500-cycle window adds 2437 cycles (9.748 us) on the
feed-forward path, because the broadcast overlaps the start of the delay, and
2500 cycles (10.000 us) on the frame path. `window_slope` therefore compares
increments 63 cycles apart. At the measured slope, that difference accounts
for about 0.006 of fidelity, inside its +-0.094 interval.

## Window rates

Both paths lose fidelity at the same rate over their executed increments:

| Quantity over the executed increment | Feed-forward (9.748 us) | Frame (10.000 us) |
|---|---:|---:|
| fidelity loss (preregistered contract) | 0.217 | 0.223 |
| finite-window slope (F(0) - F(W))/dt | 0.0222 per us | 0.0223 per us |
| -ln(F(W)/F(0))/dt | 0.0334 per us | 0.0339 per us |
| coherence rate -ln(C(W)/C(0))/dt | 0.0248 per us | 0.0263 per us |
| coherence time constant | 40.3 us | 38.1 us |
| phase frequency | -13.3 kHz | -12.9 kHz |
| slope of the phase-removed fidelity | 0.0101 per us | 0.0105 per us |

The Aer prediction under the same calibration put the window loss at 0.082
and 0.079 and the coherence time constant at 65 to 67 us. The device loses
2.7 times the predicted fidelity.

## Composition of the window cost (descriptive)

Coherence C and phase phi come from the XX, YY, XY and YX expectations in the
collect.json summary. `F_phase_removed = (1 + 2C + ZZ)/4` is the fidelity a
virtual Z by -phi would give.

| Arm | F | C | phi (rad) | ZZ | F_phase_removed |
|---|---:|---:|---:|---:|---:|
| `ff_0` | 0.780 | 0.719 | -0.154 | 0.697 | 0.784 |
| `ff_w` | 0.563 | 0.565 | -0.969 | 0.612 | 0.685 |
| `frame_l` | 0.776 | 0.715 | -0.175 | 0.695 | 0.781 |
| `frame_lw` | 0.553 | 0.550 | -0.988 | 0.604 | 0.676 |

Over the window the phase of the four-qubit block turns by -0.81 rad on both
paths, a summed detuning near -13 kHz. That coherent rotation accounts for
about 0.12 of the 0.22 fidelity loss, and a frame correction removes it.

The remainder is decay at 1.6 to 1.75 times the calibrated T1/T2 rate. ZZ
survives 0.88 and 0.87 of the window against 0.92 predicted. The block is the
parity coherence of r, d0, d1 and d2, so its coherence decays at four
single-qubit rates combined.

## Reading for the latency-constrained recovery model

- On this device the cost of waiting comes from idle coherence, not from the
  controller. The controller's 840 ns adds no resolved cost beyond the idle it
  imposes.
- The coded Bell pair's fidelity falls at a finite-window slope of 0.022 per
  us over 10 us without a frame correction, and 0.010 per us with one. The
  proposal's `exp(-delta T)` reward needs a rate, and -ln(F(W)/F(0))/dt gives
  0.033 to 0.034 per us.
- That number is the reward's delta only if the fidelity decays exponentially.
  Two exposures cannot test that, and the 13 kHz rotation is not exponential.
  A multi-point delay ladder decides the law.
- The coherence decays at 0.025 to 0.026 per us, 1.6 to 1.75 times the
  calibrated T1/T2 rate.

## Relation to the proposal audit

The [proposal audit](../../docs/archive/reviews/quantum-recovery-proposal-audit.md)
listed two items as unrecorded:
- Whether Heron r2 feed-forward time scales with the measured outcomes.
  [feedforward-latency.json](../../docs/evidence/heron_platform/feedforward-latency.json)
  records it: 201 cycles from capture end for one capture, rising to 305 for
  28 captures in one broadcast.
- A fidelity-versus-delay law on an encoded state. This run measures one: a
  decay with a 38 to 40 us coherence time constant plus a -13 kHz frame
  rotation of the four-qubit block, with no resolved controller term. The
  qubit-143 beat the audit cites remains a property of that qubit.

## Boundary

- One layout, one calibration, one job. The Hoeffding intervals hold under
  arbitrary dependence within a shot and are conservative; normal-theory
  errors near 0.005 per difference are description only.
- The phase and the decay rates are descriptive: no contract preregistered
  them beyond `decay_not_phase`, which compares only `ff_0` and `frame_0`
  (C loss 0.011, phase shift -0.09 rad).
- The detuning's source (ZZ to the measured ancillas, a static frame offset
  of each qubit, or residual photons after readout) is undecided.
- A bit-flip code protects no phase, so the run says nothing about a code
  that corrects phase.
- Layout search and model sampling used the runner's fixed seeds
  (transpiler 20261013, simulator 20261011) rather than a QRNG draw, because
  `live_run.py` takes no seed at run time (issue #514).
- The run's `experiment_digest` covers the runner's source manifest, which
  did not yet list `latency_recovery.py`. The record pins source commit
  `2f5c673` with `sources_modified` false, and that commit fixes the module's
  bytes.

# Latency-recovery findings on ibm_kingston

## Run

- Record: [2026-10-25T193443.839527Z](2026-10-25T193443.839527Z/collect.json), job
  `dbf5kdom94ac738ssug0`, on the backup account.
- Approved dry run: [2026-10-25T192932.145570Z](2026-10-25T192932.145570Z/CASE_ADDENDUM.md);
  the submission reused its predictions under unchanged calibration values.
- Calibration: 2026-10-25T12:18:10-07:00, with medians T1 258 us and
  T2 163 us.
- Layout: [150, 151, 138, 152, 149, 153] for r, d0, d1, d2, a0, a1.
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
near its ideal 1/4. Neither the controller latency nor the conditional costs
a resolved amount of fidelity beyond its idle. The difference is bounded to
-0.035..0.055 against no latency at all, and to -0.049..0.041 against an
equal idle; the T1/T2 model puts the idle cost at 0.006.

Both paths lose the same fidelity over the 10 us window: 0.217 with
feed-forward and 0.223 with the frame. The Aer prediction under the same
calibration was 0.082 and 0.079, so the device loses 2.7 times what its
calibrated T1 and T2 predict.

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

Over W the phase of the four-qubit block turns by -0.81 rad on both paths:
a summed detuning near -13 kHz. That coherent rotation accounts for about
0.12 of the 0.22 fidelity loss, and a frame correction removes it.

The remainder is decay:

| Path | Coherence ratio over W | Time constant | ZZ ratio |
|---|---:|---:|---:|
| feed-forward | 0.785 | 41 us | 0.88 |
| frame | 0.769 | 38 us | 0.87 |
| Aer (both paths) | 0.86 | 65 to 67 us | 0.92 |

The block decays 1.6 to 1.75 times faster than its calibrated T1 and T2
predict. The block is the parity coherence of r, d0, d1 and d2, and its
coherence decays at four single-qubit rates combined.

## Reading for the latency-constrained recovery model

- On this device the reward's decay parameter is set by idle coherence, not by
  the controller. Over 10 us the coded Bell pair loses F at 0.022 per us with
  no frame correction, and 0.010 per us after one.
- Its coherence decays at 0.024 to 0.026 per us.
- The 832 ns controller latency adds no resolved cost beyond that idle.
- A queue model's service-time penalty therefore needs the measured idle
  decay of the encoded block, which here exceeds the T1/T2 prediction by 1.6
  to 1.75 times plus a 13 kHz frame rotation, rather than a controller term.

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

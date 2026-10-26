# Case addendum: latency-recovery on ibm_kingston

This addendum records the analysis of the dry run beside it and the approval
it rests on. `UNAPPROVED_CASE.md` keeps its generated text.

## What the dry run establishes

- Admission: `candidate-000-shots-16384`, one dynamic job of 34 PUBs at
  16384 shots and a 50 us repetition delay. The planned charge is 40.4 s
  under a 90 s per-job and combined ceiling.
- Layout: [150, 151, 138, 152, 149, 153] for r, d0, d1, d2, a0, a1, with 24 CZ
  per encoded member and 14 per unencoded member.
- Calibration: 2026-10-25T12:18:10-07:00, with medians T1 258 us and
  T2 163 us.
- Contracts: all seven are feasible. The Hoeffding half-width is 0.0452 on
  each two-arm difference and 0.0944 on `window_slope`, against targets of
  0.05 and 0.1.

| Prediction (Aer, calibration noise) | Value |
|---|---|
| F(`ff_0`), error arm | 0.915 |
| F(`frame_0`), error arm | 0.916 |
| no-correction null | 0.017 |
| F(`ff_0_unencoded`) | 0.252 |
| `latency_is_idle` difference (T1/T2 cost of L = 215 dt) | -0.006 |
| `window_cost_ff`, `window_cost_frame` (W = 2500 dt, 10 us) | 0.082, 0.079 |

## Reading of the plan

- `recovery` and `code_property` sit far beyond their thresholds.
- Both window costs exceed the half-width by a factor near 1.8, so the run
  resolves the decay rate delta of the coded block per unit idle on both the
  feed-forward and the frame path.
- The T1/T2 cost of the latency itself (0.006) lies below the half-width.
  `latency_cost` and `latency_is_idle` therefore bound a feed-forward cost
  beyond the idle to about +-0.045 and resolve one only if the device adds
  that much. Readout-induced dephasing or controller behavior that Aer does not
  model would be such a cost.

## Account

- The primary account held 117 s of 600 s at 2026-10-25T18:4x UTC. Less the
  60 s reserve, that falls below the 90 s ceiling.
- The backup account (`backup-ibm-quantum-platform`, 600 s free) runs the
  dry run, the submission and the collection.

## Approval

The user approved the case on 2026-10-25, provided the dry run supplies what
the design needs. The admission, the resolvable window cost and the stated
bound on the latency cost above meet that condition. The submission binds this
record by its SHA-256 and uses the 90 s ceiling.

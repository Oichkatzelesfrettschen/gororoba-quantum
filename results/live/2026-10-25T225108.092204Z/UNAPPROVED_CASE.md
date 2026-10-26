# QPU case: qet-frame-diagnostic on ibm_kingston

The owner approved this case on 2026-10-25, asking first whether more shots, qubits or PUBs would add information. The
answer added six PUBs under the same account and ceiling: an idle-wait sweep that turns the phase into a detuning, and
the deferred-frame `<X_A X_B>` reads.

## Binding

- [record.json](record.json) SHA-256 `44f1e36fa58b81c7776945c4ae7381cd1afd28ffe030895d344862b7bd4c80be`;
  [isa.qpy](isa.qpy) SHA-256 `0373850a2df61c679a97198899a4a57f40a9106f0e864b9bac42a784720c629e`.
- Experiment digest `75d5507eec69ea15e47a87f8bdb368d9cc395059656a494c368ecfb384962df8`; source commit `307cbbd`,
  sources unmodified; Kingston calibration 2026-10-25T15:17:22-07:00.
- Account `backup-ibm-quantum-platform`, with 517 of 600 s remaining; the 60 s reserve is held.
- Pairs: the same 14 as the ladder run [2026-10-25T203822.040562Z](../2026-10-25T203822.040562Z/FINDINGS.md), placed
  under the same exclusion of the 79 qubits above 1 percent readout error.

## Question

In the ladder run, the scheduler put the preparation CX's closing sx on B after Alice's readout window. B therefore
waited 722 cycles mid-CX, and an equatorial rotation of B by phi fits every pair's `<Z_B>`, `<Y_B>` and parity. The
fit gives phi = 0.94 and 0.92 rad on [149, 150] and [80, 81], and 0.02 to 0.34 rad on the other pairs. The job
answers three questions, each on the same pairs under one calibration:

1. Does Alice's readout during that wait cause the phase, or does B carry a static detuning or ZZ? The `idle`
   variant waits the same 722 dt mid-CX with no readout of A.
2. Does completing the CX before the window move the phase from the parity onto `<X_A X_B>`? This is the `completed`
   variant.
3. Does an X echo on B across the window refocus the phase and restore the energy margin? This is the `echo` variant.
4. Is the phase linear in the wait? `idle_short` and `idle_long` wait 361 and 1444 dt mid-CX. The slope through the
   origin gives B's static detuning, 2 pi delta dt, and a nonzero intercept would mean an offset independent of the
   wait.

## Preregistered decisions (per pair, then pooled over the 14 pairs with t-intervals)

- **Static or readout-induced.** `readout_induced_parity_loss = idle_parity - asrun_parity`. A pooled interval
  containing zero, with both variants below 0.95 on [149, 150] and [80, 81], means a static phase. A positive lower
  bound means a readout-induced phase.
- **Frame.** A parity above 0.95 in `completed` on every pair, with `completed_coherence_phase` tracking the as-run
  window phase pair by pair (a positive correlation over the 14 pairs), confirms the frame mechanism.
- **Echo.** If the phase is static, `echo_coherence_phase` falls below `completed_coherence_phase` on the two
  large-phase pairs, and `echo_channel_floor_margin` exceeds `completed_channel_floor_margin` pooled. If the echo
  fails to refocus, the phase is time-varying within the window.
- **Energy.** The `completed` and `echo` channel floor margins (raw and readout-corrected) are reported against the
  same rule as the ladder: a one-sided 95 percent lower bound above zero.

## Predictions

The calibration-noise model in the record charges relaxation only on explicit delays and carries no coherent
detuning; on the ladder run it missed the parity loss entirely. The decisive predictions therefore come from the
ladder's hardware fit, assuming a static phase:

| Quantity | as-run | idle | completed | echo |
|---|---|---|---|---|
| parity, pooled | 0.88 | 0.88 | about 0.98 | about 0.98 |
| parity on [149, 150] and [80, 81] | 0.61, 0.56 | 0.61, 0.56 | about 0.98 | about 0.98 |
| `<X_A X_B>`, pooled | about -0.64 | about -0.64 | about -0.60 | about -0.64 |
| `<X_A X_B>` on the two pairs | -0.67, -0.57 | | about -0.39, -0.34 | about -0.67, -0.57 |

The record's noise model predicts `completed` and `echo` margins of 0.074 and 0.021. The echo costs two x gates and
explicit idle relaxation that the as-run frame never charged.

## Cost

There are 24 PUBs at 8192 shots, 196,608 shots in all, at the 250 us repetition delay plus a schedule of about 5 to
11 us. That comes to about 50.5 s, plus 2.3 s of job overhead: roughly 53 s, with a 60 s ceiling.

## Why simulation cannot answer it

The model has no term for the phase. Whether that phase is a static detuning, a ZZ coupling or a shift driven by A's
readout tone is a property of these qubits and this readout chain, so only the device can say which.

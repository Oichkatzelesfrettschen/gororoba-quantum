# Unapproved QPU case: qet-compensated-ladder at a 50 us repetition delay

Status: UNAPPROVED. This record is a submit-free dry run. Writing the case authorizes nothing and submits no job.

## Binding

- [record.json](record.json) SHA-256 `2c27cd151a1b68576d2d58324deececdc7f1dea58069f6719a00b237fb2d7335`;
  [isa.qpy](isa.qpy) SHA-256 `56bee2738732f6beb0f72f642e68a14f11bc1c276a33dc1522a83aad208f0188`.
- Source commit `4d09c8a`, sources unmodified; the account is `backup-ibm-quantum-platform`, with 462 s remaining and
  the 60 s reserve held. The pairs are the same 14 as
  [the frame diagnostic](../2026-10-25T225332.266272Z/FINDINGS.md), under the same readout-cap exclusion.
- The run uses `--rep-delay 0.00005`, inside the backend's [0, 2 ms] range; every shot opens with the service's
  measure-and-conditional-x reset (`INIT_q` in the scheduled timing).

## Questions

1. **Compensation.** The frame diagnostic shows the ladder's energy shortfall is B's coherent phase over the
   measure-to-branch idle, measured at -1.06 to +0.21 rad. Does a record-independent `rz(alpha)` on B, chosen per pair
   as the grid point nearest the phase that pair's own reference arms read in this job, restore a positive channel
   floor margin? Passivity permits that rotation, and the Kabsch floor already includes it, so the information excess
   stays the test that information was used.
2. **Repetition delay.** Does a 50 us repetition delay cost preparation or readout fidelity relative to the 250 us
   runs on the same pairs? The comparison reads the |00> and |11> calibration assignments and the completed-frame
   reference observables against the frame diagnostic's values (same pairs, about 25 minutes apart).

## Preregistered endpoints

- **Primary.** The mean over the 14 pairs of `selected_margin`, the channel floor margin at each pair's selected
  alpha. Rule: the one-sided 95 percent lower bound exceeds zero.
- **Secondary.** `selected_excess`; `selected_margin - uncompensated_margin` (positive lower bound = compensation
  helps); the margin at every alpha per pair as a device map.
- **Repetition delay.** The per-pair change of each assignment error and of `<Z_A Z_B>` against the frame
  diagnostic. Any change above 0.01 in assignment, or a parity drop above 0.02 pooled, is a fidelity cost of the
  shorter delay.

## Predictions

The idle-free Aer model reads 0.063 for the margin at alpha = 0. The hardware-informed expectation follows from the
frame diagnostic's completed-frame values: compensating the coherent phase removes about 1 - cos(phi) of the
coherence loss. That is most of it on [149, 150], [80, 81] and [91, 98], and little on pairs with phi below 0.2.
The incoherent part, B's dephasing over the idle and readout, stays. A pooled selected margin near zero to +0.05 is
the expectation; the readout-corrected value would sit about 0.09 higher.

## Cost

147,456 shots at a 50 us repetition delay plus a 14.5 us shot schedule (both resets included) come to about 9.5 s,
plus about 2.3 s of job overhead: roughly 12 s, with a 30 s ceiling. The same job at 250 us would take about 41 s.

## Submit command

```sh
cd gororoba_quantum
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
"$PYTHON" live_run.py --groups qet_compensated_ladder --backends ibm_kingston --exclude-qubits "$(cat EXCLUDE)" \
  --shots 8192 --rep-delay 0.00005 --no-isolated-reference --max-execution-seconds 30 \
  --max-total-execution-seconds 30 --reserve-seconds 60 --min-remaining-seconds 60 --out ../results/live \
  --approved-record ../results/live/2026-10-25T230238.648709Z \
  --approved-record-sha256 2c27cd151a1b68576d2d58324deececdc7f1dea58069f6719a00b237fb2d7335 --submit
```

`EXCLUDE` is the readout-cap list of the frame-diagnostic case.

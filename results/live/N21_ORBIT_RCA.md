# N=21 orbit feed-forward: coherent kickback phase RCA

Runs on ibm_fez, physical qubits 142 (control), 136 (work 1), 143 (work 4),
144 (work 16), 4096 shots per PUB.

Status: the phases below are model-dependent fit parameters from these runs'
calibrations, not measured rotations. PATCH_WINDOW_FINDINGS.md adds a
same-calibration characterization: product-state Ramsey probes show no
resolved window phase, and that run's orbit distributions change with the
window context while a no-phase arm-dependent loss model fits them as well as
the phase model. The window attribution below is one candidate, not an
established mechanism, and the echo-contrast comparison (0.17 rad fitted,
contrast nearly unchanged) shows why contrast alone cannot settle orbit
phase.

| Run | Job | Charge | Record |
|---|---|---|---|
| Orbit feed-forward | db6ub8svf2bc73d1rc50 | 4 s | 2026-10-13T080216.451663Z |
| Window arms | db6uqdkvf2bc73d1sc80 | 11 s | 2026-10-13T083417.634585Z |

## Calibration

The first run read the 06:27 UTC calibration three times, the last 2 s before
submission. A snapshot stamped 08:01:23 UTC existed when the job ran at
08:02:44 but published after 08:10; its T1, T2 and assignment values for all
four qubits equal the earlier snapshot's. Backend properties report no qubit
frequency, so no calibration age gives the noise model a coherent-phase term.

## Mechanism fit

`scripts/n21_orbit_rca.py` evolves the logical circuit as an exact five-qubit
density matrix and fits each mechanism plus two depolarizing nuisances to the
eight cells of a pair (6 dof). On the first run a work-superposition phase
lowers the deviance from 65.4 to 2.5; mid-circuit assignment (63.8), reset
failure, window T1 and window dephasing (65.4) leave it unchanged, and
terminal assignment needs 14 and 24 percent error rates.

| Arm | Phase (rad) | 95% profile interval | Signed contrast fb / no-fb (model) | Contrast difference |
|---|---|---|---|---|
| first run, nominal | +0.59 | [0.52, 0.68] | +0.090 / -0.107 (0.000 / -0.207) | 0.197 |
| nominal repeat | +0.70 | [0.58, 0.79] | +0.093 / -0.090 (0.000 / -0.198) | 0.183 |
| window_delay (+415 dt idle) | +0.41 | [0.21, 0.58] | +0.040 / -0.071 | 0.111 |
| extra_readout | +0.63 | [0.47, 0.73] | +0.056 / -0.041 | 0.098 |
| window_echo | +0.17 | [0.05, 0.26] | +0.029 / -0.142 (0.007 / -0.195) | 0.170 |

## Hardware-schedule exposure

Idle time of the work qubits from their last round-1 pulse to their first
round-2 pulse, signed by each echo X, read from each PUB's scheduler timing
(dt = 4 ns):

| Arm | Qubit 136 (work 1) | Qubit 144 (work 16) |
|---|---|---|
| nominal fb / no-fb | 962 / 838 | 1412 / 1288 |
| window_delay | 1377 / 1253 | 1827 / 1703 |
| extra_readout | 1378 / 1254 | 1828 / 1704 |
| window_echo | 13 / 6 | 532 / 525 |

The delay and the extra readout lengthen the window by the same 415 dt. The
echo refocuses 136 completely; 144 keeps 532 dt unrefocused because its
round-1 pulses end 248 dt before the window opens.

## Findings

- The phase reproduces on the same qubits across a recalibration (0.59, then 0.70).
- The echo arm's phase is 0.17 [0.05, 0.26], disjoint from nominal: most of
  the phase accrues while the work pair idles during the control's
  measurement and reset. The echo removes the per-arm bias (feed-forward
  signed contrast +0.093 to +0.029, model +0.007) and leaves the contrast
  difference unchanged (0.170 against 0.183).
- Adding 415 dt to the window, by idling or by a second readout, cuts the
  contrast difference to 0.111 and 0.098 against model values near 0.21.
  Reported T2 of 89 to 235 us predicts a loss of a few percent.
- One quasi-static Gaussian detuning per work qubit, fitted jointly to all
  32 cells with the exposures above, gives G2 = 49.9 on 18 dof against 22.7
  for free per-arm phases and 83.6 for static detuning alone. No single
  idle-proportional mechanism reproduces all four arms.
- The extra-readout arm misfits the single-phase model (G2 9.3 on 3 dof),
  so its fitted phase does not support a conclusion; the delay arm is
  borderline (5.6). The preregistered ordering assumed the window preserves
  coherence, which the contrast loss contradicts.
- Mid-circuit assignment explains none of the first run's stratum shift. The
  extra readout overwrote its bit, so readout agreement was not measured.
- A coherent phase does not cancel in the contrast difference; the first
  run's agreement with the model's 0.207 combines a phase with extra loss.

## Open candidates and discriminators

1. Fast, window-length-dependent decoherence of the work pair beyond the
   reported T2, for instance a coherent exchange with spectator 143 (which
   holds the orbit bit for 4) or with the other neighbors 123 and 145.
2. Two opposing phase contributions: a readout-associated shift and a static
   detuning.
3. Decisive characterization: window Ramsey on 136 and 144 separately, as
   static circuits on the same patch, sweeping the idle in steps of about
   one readout, with and without a concurrent control readout, recording
   both phase and coherence. It also measures T2* directly; IBM documents
   its reported T2 as a Hahn-echo value, which an unechoed window does not
   follow.

## Mitigation

The explicit delay-X-delay-X echo survives transpilation (planning contract)
and removes the per-arm bias. IBM rejects dynamical decoupling on dynamic
circuits, so a placement-aware echo, timed so each work qubit's halves are
balanced from its own last pulse, is the engineering follow-up; 144's
unbalanced 532 dt shows the halves must start at each qubit's own idle start.

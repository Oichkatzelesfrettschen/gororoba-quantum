# N=21 orbit feed-forward: coherent kickback phase RCA

Runs on ibm_fez, physical qubits 142 (control), 136 (work 1), 143 (work 4),
144 (work 16), 4096 shots per PUB.

Status: the phases below are model-dependent fit parameters from these runs'
calibrations, not measured rotations. The orbit law depends on the phases
only through theta = phi1 + phi2, so per-round phases are not separately
identifiable from these distributions. PATCH_WINDOW_FINDINGS.md adds a
same-calibration characterization: product-state Ramsey probes show no
resolved window phase, and that run's orbit distributions change with the
window context, with the one-phase model within one residual dimension of the
causal saturated model. The window attribution below is one candidate, not
an established mechanism, and the echo-contrast comparison (0.17 rad fitted,
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

## Exact-ISA window exposure

The `piecewise` block of each rca-mechanism-fit.json fits one static
detuning per placed window qubit through the archived ISA itself
(`CompiledLaw`): an exact density matrix on the active wires, with a Z
rotation of rate times length on every idle interval the qubit plays inside
the control's measurement-to-feed-forward window, the two depolarizing rounds
at the first measurement and at the terminal one, and the mid-circuit
assignment flip on every write of the recorded bit before the if_else,
the extra readout's second write included. Each qubit's coupling to the work register
in each recorded branch follows from the circuit, so no single-gap sign is
needed. dt is 4 ns from docs/evidence/heron_platform/targets.json.

Work-only gates inside the window split it: in nominal_feedback (window 1426
to 2394 dt) qubit 136 idles over [1373, 2335] and [2381, 2416], qubit 143
over [1419, 2335] and [2393, 2400], and qubit 144 over [1194, 2606]. The
single gap keeps the first interval of each.

| Exposure (083417, 8 members, 24 cells) | G2 | dof | goodness-of-fit p |
|---|---|---|---|
| no detuning | 180.96 | 22 | < 1e-3 |
| single gap, rates on 136, 143, 144 | 27.29 | 19 | 0.10 |
| piecewise, rates on 136, 143, 144 | 26.75 | 19 | 0.11 |

Per pair (piecewise / single gap): nominal 3.5 / 3.1, window_delay 5.4 /
6.5, extra_readout 12.3 / 12.1, window_echo 5.5 / 5.5; without detuning
71.7, 26.9, 45.6 and 36.8. On 080216 both exposures reach G2 1.80 on 1 dof
against 65.42 on 4 without detuning, with five parameters on six cells.

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
- Superseded: an earlier analysis revision fitted one quasi-static Gaussian
  detuning per work qubit jointly to all 32 cells (G2 = 49.9 on 18 dof
  against 22.7 for free per-arm phases and 83.6 for static detuning alone).
  The retained [rca-mechanism-fit.json](2026-10-13T083417.634585Z/rca-mechanism-fit.json)
  records that fit as skipped, because the window state is not a branch
  phase on the work bit for residue 1 and joint probes leave the relative
  sign of qubits 136 and 144 unresolved. The three deviances carry no
  current evidence; the fit of Exact-ISA window exposure replaces them.
- Static detuning on the window qubits, evaluated through the archived
  ISA, explains the 083417 orbit family: G2 falls from 181.0 to 26.8 on 19
  dof with three rates (goodness of fit p = 0.11). The likelihood-ratio
  statistic of 154.2 on 3 added parameters is nominal only, because the
  rates are periodic and their likelihood has several basins.
- Splitting the window at work-only pulses does not change the fit: the
  splits are 35 dt on qubit 136 and 7 dt on 143, the piecewise exposure
  lowers G2 by 0.54 at equal parameter count, and the single gap already
  fits the no_feedback members. The unresolved joint probe came from the
  five-qubit logical model, not from the window's segmentation.
  The single gap also has a basin at G2 27.26, with qubit 143 near -0.75
  rad/us, that the seeded search does not start in, so the piecewise gain
  lies between 0.51 and 0.54.
- The fitted rates are not identified: the two exposures' optima, 0.54
  apart in G2, place qubit 136 at -0.160 and +0.163 rad/us and qubit 143 at
  -3.26 and +0.87 rad/us, so no rate is a measured detuning; the deviances
  and segment tables are the result.
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

# Quantum Inspire experiments: spectator-drive crosstalk and transported-pair teleportation

Claim kind: exploratory reanalysis, hardware. The circuits, shot counts and
qubit roles were fixed in `cases.json` before submission; the phase-domain
residual, the driver crosstalk and conditioning fields, and every threshold
below were chosen after the Tuna-17 data arrived.

## Sources the cases translate

- Wu, Camenzind et al., "Simultaneous high-fidelity single-qubit gates in a
  spin qubit array", Nature Physics (2026), doi:10.1038/s41567-026-03466-2.
  A five-qubit Si/SiGe array driven through one shared microwave line loses
  fidelity under parallel operation; the paper attributes it to off-resonant
  a.c.-Stark shifts (crosstalk phase quadratic in drive amplitude, fitted
  exponent 1.91(5)) and compensates with pairwise phase calibrations whose
  sum predicts the simultaneous-drive phase (its Fig. 4d).
- Matsumoto et al., "Two-qubit logic and teleportation with mobile spin
  qubits in silicon", Nature 653, 392 (2026), doi:10.1038/s41586-026-10423-9.
  Two electron spins carried towards each other in conveyor potentials form a
  CZ (98.86 +- 0.29 %); a Bell pair created that way and separated supports a
  conditional, post-selected teleportation with 86.7 +- 0.9 % average gate
  fidelity after state-preparation and measurement correction.

No spin-qubit backend is reachable from this account (Spin-2+ offline, no
backend type; [backends.md](backends.md)), so both cases run on transmons:
Tuna-17 for the device answer, QX for the ideal reference.

## Cases

`scripts/qi_crosstalk_teleport_cases.py --write results/quantum_inspire/cases`
generates every backend's cQASM 3.0 from the catalogue topology; gate
core-327 regenerates them byte for byte.

- **Spectator-drive additivity.** Target T: X90, `wait(40)` (800 ns), Y90,
  so P1 = (1 + sin phi)/2 reads the Rz(phi) accumulated in the idle with
  standard error 1/sqrt(shots) on phi. Drivers A and B (both coupled to T):
  40 X gates then `wait(1)`, an identity that sits inside T's idle under ALAP
  scheduling. Four circuits (none, A, B, AB) in one batch job; every disjoint
  star of the coupling map runs in parallel (Tuna-17: T=0 (1,2), 3 (5,6),
  4 (7,8), 11 (13,14), 12 (9,15)). Pairwise falsifier:
  phi(AB) - phi(A) - phi(B) + phi(none) = 0.
- **Transported-pair teleportation.** Path I - P1 - P2 - D: H and CNOT make a
  Bell pair on P1, P2; SWAP carries P2's half to D (the gate-level analog of
  conveyor shuttling); CNOT(I, P1) and H(I) form the Bell measurement; D is
  rotated into the input's eigenbasis and measured. Without feed-forward the
  correction X^m(P1) Z^m(I) is applied to D's recorded bit, which is exact for
  Pauli-eigenstate inputs; the m(I) = m(P1) = 0 subset is the paper's
  post-selected protocol. Tuna-17 paths: |0> on 1-0-2-4, |1> on 5-3-6-9,
  |+> on 10-7-11-8, |+i> on 14-12-15-16.

## Runs

| Run | Backend | Shots per circuit | Outcome |
|---|---|---|---|
| runs/2026-10-16T211635Z-QXsinglenodesimulator | QX (batch 869574) | 2048 | 5 jobs completed |
| runs/2026-10-16T211635Z-tuna_17 | Tuna-17 (batch 869577) | 16384 | 5 jobs completed |
| runs/2026-10-16T211635Z-Rydberg | Ry emulator (batch 869576) | 1024 | teleport job failed, empty log |
| runs/2026-10-16T213823Z-Rydberg-diagnostic | Ry emulator (batch 869597) | 1024 | X on q[0] read `10` in every shot |

Each run directory keeps the circuits, cases.json with their sha256,
submission.json (approval text, queue at submit), raw/ (every shot),
results.json (job records, result metadata, charged transactions: none) and
analysis.json, which gate core-328 recomputes from raw/ byte for byte.

## Results

**QX (ideal reference).** Every target read P1 within sampling of 0.5;
pairwise residuals 0.012, 0.077 and 0.018 rad against sigma 0.044 rad;
drivers read 0; teleportation fidelity 1.0 on both paths after the
Pauli-frame correction, with a post-selected fraction near 1/4. The analysis
reproduces the ideal law.

**Tuna-17, target phases** (rad; sigma of each phi 0.0078, of the residual 0.0156):

| Star T (A, B) | phi none | shift A | shift B | shift AB | residual | z |
|---|---|---|---|---|---|---|
| 0 (1, 2) | -0.028 | -0.122 | +0.139 | +0.035 | +0.018 | +1.15 |
| 3 (5, 6) | -0.121 | +0.074 | +0.060 | +0.081 | -0.053 | -3.38 |
| 4 (7, 8) | -0.034 | +0.633 | +0.030 | +0.695 | +0.032 | +2.04 |
| 11 (13, 14) | -0.076 | +0.014 | +0.153 | +0.113 | -0.054 | -3.43 |
| 12 (9, 15) | -0.042 | -0.043 | -0.037 | -0.059 | +0.021 | +1.35 |

- Driving a neighbor moves the target's phase by up to 0.633 rad in 800 ns
  (Q7 on Q4), against an idle phase of -0.03 to -0.12 rad. The repository's
  IBM noise model, with independent per-qubit channels, predicts a shift of
  exactly zero.
- The pairwise sum captures most of each simultaneous shift (Q4: 0.663
  predicted, 0.695 measured) and fails at |z| > 3.29 on targets 3 and 11.
- Conditioning the target on each driver's final outcome leaves its phase
  within a few hundredths of a radian (Q4 under Q7: 0.602 vs 0.591), so the
  shift does not follow the driver's final state. A ZZ phase from the driver's
  time-averaged excitation during its X train is not excluded by this split.

**Tuna-17, drivers** (P1 after 40 X gates, ideal 0):

| Driver | Driven alone | Driven with its partner | change z |
|---|---|---|---|
| Q1 | 0.062 | 0.259 | +48.5 |
| Q2 | 0.046 | 0.893 | +153.6 |
| Q5 | 0.155 | 0.131 | -6.3 |
| Q6 | 0.717 | 0.702 | -3.1 |
| Q7 | 0.271 | 0.274 | +0.6 |
| Q8 | 0.764 | 0.765 | +0.1 |
| Q9 | 0.883 | 0.864 | -5.2 |
| Q13 | 0.187 | 0.178 | -2.1 |
| Q14 | 0.059 | 0.060 | +0.2 |
| Q15 | 0.092 | 0.097 | +1.5 |

- Simultaneous drive degrades single-qubit gates on a pair that shares no
  coupler: Q2 goes from 0.046 to 0.893 when Q1 is driven at the same time.
  This is the parallel-operation degradation the Nature Physics paper
  reports, on transmons with dedicated drive lines rather than one shared
  line.
- Coherent error: Q6, Q8 and Q9 exceed P1 = 0.5 when driven alone, which
  depolarizing, relaxation and readout error cannot produce; a pure per-gate
  over-rotation needs at least 0.050, 0.053 and 0.061 rad per X. Q5, Q13 and
  Q15 are consistent with coherent error without bounding it.
- The four configurations ran as sequential jobs about 11 s apart, so drift
  between jobs enters every cross-configuration difference; the 0.85 jump on
  Q2 exceeds any drift the other drivers show.

**Tuna-17, teleportation** (raw, no state-preparation or readout correction):

| Input | Path I-P1-P2-D | Corrected fidelity (95% CI) | Post-selected fidelity (95% CI) | Post-selected fraction |
|---|---|---|---|---|
| \|0> | 1-0-2-4 | 0.746 (0.739-0.752) | 0.768 (0.756-0.781) | 0.268 |
| \|1> | 5-3-6-9 | 0.827 (0.821-0.832) | 0.782 (0.769-0.795) | 0.230 |
| \|+> | 10-7-11-8 | 0.844 (0.839-0.850) | 0.846 (0.835-0.857) | 0.253 |
| \|+i> | 14-12-15-16 | 0.862 (0.857-0.867) | 0.864 (0.853-0.875) | 0.236 |

- Each input ran on its own path, so no single channel has a Bloch-sphere
  average; the cross-axis mean 0.831 assumes a path-independent channel.
- A Z-basis fidelity alone is reachable by measure-and-prepare, so the |0>
  and |1> rows carry no quantum claim by themselves; the |+> and |+i> rows
  test phase transport through the SWAP.
- The raw numbers are not comparable to the paper's SPAM-corrected 86.7 %
  process fidelity.

## Relation to the repository's IBM noise

The repository simulates IBM Heron with live_run's noise model (gate
depolarizing, thermal relaxation, asymmetric readout per qubit;
gororoba_quantum/calibration_snapshot.py), whose recorded boundary excludes
coherent error, crosstalk and leakage. That model class predicts, for these
cases, a zero neighbor-dependent target shift, an additivity residual of
zero, driver P1 below 1/2 after an even X count, and no change of a driver's
P1 when its partner is driven. Every Tuna-17 signal above is therefore
outside the model class: the drive-induced target shifts, the Q1/Q2
simultaneous-drive degradation and the Q6/Q8/Q9 over-rotation. The idle
phases (-0.03 to -0.12 rad over 840 ns, a frequency offset of 5 to 23 kHz)
sit at the tens-of-kHz scale of the Heron idle detunings in
hw-idle-detuning-scale (40.9 kHz between two Kingston work qubits).

## Next cases

- Static-|1> control: hold each driver in |1> (X before and after the
  window, no drive inside it) to measure the ZZ phase alone and separate it
  from the drive-induced shift.
- Interleave the four configurations inside one job (disjoint stars per
  configuration) so drift cancels between them.
- Drive amplitude series (1, 2, 4 X-pair densities) to test the quadratic
  amplitude law of the a.c.-Stark mechanism.
- Teleportation with all six axial inputs on one path to give a channel's
  sphere average, and a direct-SWAP control without the Bell measurement.
- Ry emulator: rebuild the teleport case in the Rydberg-native form (no bit
  register, RYD blockade gates) and read results leftmost-first.
- Tuna-5 and Tuna-9 cases are generated and wait for those backends to come
  online.

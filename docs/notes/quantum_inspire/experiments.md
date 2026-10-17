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
  qubits in silicon", Nature 653, 391-397 (2026), doi:10.1038/s41586-026-10423-9.
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
core-327 regenerates them byte for byte. Each backend is a series of
`batch-NN/` cases of at most three circuits, each submittable on its own:
batch-00 holds none, A and B, and batch-01 holds none, AB and teleport, so
every phase shift subtracts the undriven reference measured in its own batch
(a batch boundary is a calibration boundary).
`--analyze RUN_DIR... --out FILE` merges the run directories of one series,
refuses a series that lacks a batch, and `--replay-series FILE RUN_DIR...`
recomputes FILE from them.
The retained 211635Z runs predate the split and ran all five circuits as one
batch.

- **Spectator-drive additivity.** Target T: X90, `wait(40)` (800 ns), Y90,
  so P1 = (1 + sin phi)/2 reads the Rz(phi) accumulated in the idle with
  standard error 1/sqrt(shots) on phi. Drivers A and B (both coupled to T):
  40 X gates then `wait(1)`, an identity that sits inside T's idle under ALAP
  scheduling. Four configurations (none, A, B, AB); every disjoint
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
| runs/2026-10-16T211635Z-Rydberg | Ry emulator (batch 869576) | 1024 | teleport job failed: "error interpreting cQASM script" |
| runs/2026-10-16T213823Z-Rydberg-diagnostic | Ry emulator (batch 869597) | 1024 | X on q[0] read `10` in every shot |

Each run directory keeps the circuits, cases.json with their sha256,
submission.json (approval text, queue at submit), raw/ (every shot),
results.json (job records, result metadata, charged transactions: none) and
analysis.json, which gate core-331 recomputes from raw/ byte for byte.

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
P1 when its partner is driven.

`scripts/qi_ibm_noise_replay.py` checks that prediction numerically: it
rebuilds every star and path from the retained cQASM as a Qiskit circuit on
the lowest-error disjoint Kingston embeddings (stars on qubits 10/9/11,
47/46/48, 136/123/143, 147/137/148, 22/21/23; paths 48-47-46-45,
109-118-129-128, 42-41-36-21, 149-148-147-137), transpiles at level 0 against
docs/evidence/calibration/ibm_kingston.json, inserts ALAP delays and saves
exact Aer probabilities beside 16384-shot samples. It ran on a Kaggle CPU
kernel (results/kaggle/2026-10-16T214611Z-qi-ibm-noise-replay) and is retained
as results/quantum_inspire/ibm_noise_replay/tuna_17-ibm_kingston.json; gate
core-340 replays every star and path.

| Quantity | Kingston model (exact) | Tuna-17 measured |
|---|---|---|
| largest target phase shift from a driven neighbor | 1.2e-14 rad | 0.695 rad |
| largest pairwise residual | 1.3e-15 rad | 0.054 rad |
| largest driver P1 after 40 X | 0.012 | 0.893 |
| teleport corrected fidelity, inputs 0 / 1 / + / +i | 0.986 / 0.981 / 0.982 / 0.971 | 0.746 / 0.827 / 0.844 / 0.862 |
| teleport post-selected fidelity | 0.988 / 0.974 / 0.983 / 0.969 | 0.768 / 0.782 / 0.846 / 0.864 |
| post-selected fraction | 0.252-0.253 | 0.230-0.268 |

Kingston's X lasts 32 ns, so the replay's driver train spans 1.3 us against
the target's 0.93 us window; under independent channels that changes no
target outcome. Every Tuna-17 signal above is therefore outside the model
class: the drive-induced target shifts, the Q1/Q2
simultaneous-drive degradation and the Q6/Q8/Q9 over-rotation. The idle
phases (-0.03 to -0.12 rad over 840 ns, a frequency offset of 5 to 23 kHz)
sit at the tens-of-kHz scale of the Heron idle detunings in
hw-idle-detuning-scale (40.9 kHz between two Kingston work qubits).

## Zero-divisor witness on Tuna-17 (preregistered)

`scripts/qi_zero_divisor_cases.py` builds Design B's fixed-operand LCU for
a = e1 + e10 (root AGENTS.md, "Zero-product witnesses"): the dark witness
(e1 + e10)(e4 - e15) = 0 (ideal P(s = 0) = 0), the bright control
(e1 + e10)(e4 + e15) (ideal 1) and the negative fixture (e1 + e10)(e2 - e13)
(ideal 1/2). Before writing a circuit, `certify()` computes every product with
cd_core.cd_multiply and with the retained D = 16 tables of hypercomplex,
hypercomplex-engine, Cayley-Calculator and cayley-dickson
(docs/evidence/algebra_packages/tables.json), finds the dark pair in
cd_core.sedenion_zero_divisor_corpus, and requires SELECT to equal
cd_sign(16, m, q)|m XOR q> on all 32 inputs.

The SELECT sign function has algebraic degree 4, which needs pi/8 phases that
Tuna would round to the pi/36 grid. Its ANF factors as
q0 + Maj(q1, q2, q3) + q1 q2 q3 + a(q0 + q2 + q3) + a(1 + q2) Maj(q0, q1, q3),
so an in-place majority (Cuccaro MAJ) gives an exact SELECT of two Toffolis
and two CCZ on five qubits, with every gate in H, S, T, Tdag and CZ. Routed
onto Tuna-17 a replica takes 75-91 CZ and 26 T. The generator places two
disjoint regions, {1,2,4,8,12} and {10,11,13,14,16}, and excludes qubits 0,
5, 6, 7 and 9 (EXCLUDED_QUBITS) with every coupler on them. READOUT_EXCLUDED
holds q9, which read P1 0.27-0.28 in a gate-free circuit, and q0 and q6,
which read P1 0.39 and 0.14 prepared in |1> after the platform
recalibration. The Ramsey visibility of the coupler-ZZ map
(results/quantum_inspire/coupler_zz_tuna_17_analysis.json, `min_visibility`,
minimum over neighbor sectors and the 0.5 us and 2 us delays) splits the 17
qubits into 14 at 0.755 and above and q5, q6, q7 at 0.043, 0.270 and 0.084;
no value lies between 0.30 and 0.755, so VISIBILITY_FLOOR = 0.5 excludes
exactly {5, 6, 7}, which `visibility_excluded()` derives from the retained
file and `--self-test` requires. The 12 remaining qubits
fit two connected 5-qubit regions at most; of the 4 disjoint pairs,
`--select-regions` ranks this one first by routed CZ over the three cases
(494: 75, 75 and 79 for dark, bright and fixture on {1,2,4,8,12}; 87, 87 and
91 on {10,11,13,14,16}), then by the 2 couplers joining the regions (the
pair {1,2,4,8,12} with {11,13,14,15,16} also costs 494 and joins 3), then
lexicographically. The cases rotate through the regions (latin-1..3): dark and bright, bright
and fixture, fixture and dark, so every case runs once in each region and
every pair of cases shares a circuit. readout-0 and readout-1 prepare every
qubit in |0> and |1>. A batch boundary is a calibration boundary, so the
generator emits three batches of three circuits, batch-00..02, each holding
one witness circuit followed by readout-0 and readout-1. A witness circuit
carries two cases in its two regions, so its contrast shares one calibration,
and its readout correction uses the assignment measured in the same batch:
`load_series` keys shots by (batch, file), and `secondary()` resamples each
batch's readout pair and then its witness circuit, correcting every circuit
with its own batch's assignment. A readout change between batches therefore
moves only that batch's corrected estimates and bootstrap intervals, while
the raw estimators stay fixed (`--self-test`, gate core-348). Pooled means
average circuits from three calibrations. The retained 221133Z runs predate
batching and ran all five circuits as one batch, which forms the single
calibration group of their replay; they executed three regions,
{0,1,2,4,5}, {7,8,10,11,13} and {9,12,14,15,16}, in a 3x3 Latin square, and
their analyses read the regions recorded with them, so the tables below
describe that placement. The estimators and the comparison were fixed in cases.json before
submission (claim class: preregistered hardware inference). The QX twin packs
the same six replicas two per 10-qubit circuit (the retained 221133Z twin
ran the earlier nine).

| Region | dark P(s=0) | bright | fixture | endpoint contrast B - D (95%) |
|---|---|---|---|---|
| {0,1,2,4,5} | 0.491 | 0.493 | 0.518 | 0.002 (-0.009 to 0.013) |
| {7,8,10,11,13} | 0.467 | 0.518 | 0.497 | 0.051 (0.040 to 0.062) |
| {9,12,14,15,16} | 0.455 | 0.527 | 0.481 | 0.072 (0.061 to 0.083) |
| pooled (95% CI) | 0.471 (0.466-0.475) | 0.512 (0.508-0.517) | 0.499 (0.495-0.504) | 0.0415 +- 0.0032 |
| readout-corrected mean | 0.457 | 0.501 | 0.484 | 0.0435 (0.037 to 0.050) |
| QX twin (ideal platform) | 0.000 | 1.000 | 0.490 | 1.000 |
| Kingston, hw-zero-divisor-floor | 0.182 (0.146-0.217) | 0.828 | -- | 0.646 |

Kingston's 0.646 is the endpoint contrast; its fitted fringe visibility is
0.678 with offset 0.502 and phase 0.197 rad
(results/live/2026-10-15T070853.550532Z/collect.json), and the two need not
coincide. Every comparison below uses the endpoint contrast B - D.

**Preregistered results** (raw counts, replicas treated as independent):

- The platform executes the certified circuits as specified: the QX twin
  reads dark 0, bright 1 and fixture 0.490. The exact SELECT identity itself
  rests on the full-operator certificate (signed output amplitude on all 32
  inputs, no global phase allowed), not on finite QX samples.
- Tuna-17 keeps an endpoint contrast of 0.042, 4.2 % of the ideal and 6.5 %
  of Kingston's 0.646. Dark lies below bright by about 13 standard errors;
  statistical resolution and retained contrast answer different questions.
- Dark and bright straddle 1/2: their midpoint is 0.4915 and the sum
  residual dark + bright - 1 is -0.017 (z = -5.3). That rejects the
  preregistered shared symmetric-contraction model,
  p_obs = 1/2 + lambda (p_ideal - 1/2) with one lambda for every
  preparation. It does not exclude depolarizing noise in general: separate
  contractions lambda_D = 0.058 and lambda_B = 0.024 reproduce both endpoints.
- The fixture agrees with its ideal: 0.499, z = -0.42.
- The region on qubits 0, 1, 2, 4, 5 shows no resolved endpoint contrast at
  this precision (0.002, 95 % interval -0.009 to 0.013). The teleport path
  1-0-2-4 and the Q1/Q2 simultaneous-drive failure sit in the same region,
  a repeated spatial association whose shared cause these acquisitions do
  not identify.
- The routed depths differ (66-70 CZ and 26 T here, about 45 CZ with
  continuous rotations on Kingston), so the contrast ratio compares two
  implementations of one witness, not two devices alone.

**Secondary analysis** (fixed after the data; `secondary` in analysis.json):
the three replicas of a Latin circuit share every shot, so the raw
uncertainties use the delta-method covariance of the per-circuit joint
selector outcomes; the readout-corrected values come from a seeded
multinomial bootstrap (4000 draws) of each circuit's joint selector outcomes
and of the joint selector readout in both calibration circuits, which carries
the calibration's own sampling error. The same-shot covariances between
regions measure about 1 % of the variances, so the preregistered z-scores
stand.

| Test | Null | raw | readout-corrected (95%) |
|---|---|---|---|
| endpoint contrast B - D | 0 | 0.0415 +- 0.0032 | 0.0435 (0.037 to 0.050) |
| shared symmetric contraction D + B - 1 | 0 | -0.0169 +- 0.0032 | -0.042 (-0.049 to -0.036) |
| common affine response H = F - (D + B)/2 | 0 | +0.0075 +- 0.0028 (z 2.7) | +0.0047 (-0.001 to 0.011) |
| fixture against its ideal F - 1/2 | 0 | -0.001 +- 0.002 | -0.016 (-0.021 to -0.012) |

- Readout asymmetry runs the other way. Every selector misreads |1> as 0
  (2.7-5.2 %) more often than |0> as 1 (0.5-1.8 %), which alone would raise
  the raw sum residual by e10 - e01; correcting for it deepens the residual
  from -0.017 to -0.042. Under the all-|0>/all-|1> calibration model readout
  hides part of the asymmetry rather than producing it.
- After correction H is consistent with zero while the fixture sits 0.016
  below 1/2: all three preparations follow one affine response
  p = u + v p_ideal with u + v/2 = 0.479, an additive shift toward
  selector 1 common to the circuits. Circuit-dependent symmetric contractions
  would hold an ideal-1/2 fixture at 1/2 and are disfavored by that
  corrected fixture. The calibration model omits readout crosstalk under the
  witness's state, which bounds this conclusion.
- By region the common affine response holds on {7,8,10,11,13}
  (H = 0.005 +- 0.005) and {9,12,14,15,16} (H = -0.010 +- 0.005) and fails on
  {0,1,2,4,5} (H = 0.027 +- 0.005, z 5.6), the region without resolved
  contrast. A common response with a shifted midpoint is a probability-level
  description; it identifies no unique channel acting on the five-qubit
  circuit.

**Per-batch series, QX dry run.** The batched series' QX twin, generated
before the placement above (three regions, nine replicas), ran as
batch-00 (twin-1..3, batch job 870037, jobs 1527264, 1527266, 1527267) and
batch-01 (twin-4..5, batch job 870040, jobs 1527269, 1527270), 2048 shots
each, retained as results/quantum_inspire/runs/2026-10-17T034409Z-zero_divisor_qx-batch-00
and -batch-01. `--analyze` over both batches writes
results/quantum_inspire/zero_divisor_qx_analysis.json, and gate core-330
replays it with `--replay-series`.

| Case | replicas (count of 2048 at s = 0) | P(s=0) (95%) | ideal |
|---|---|---|---|
| dark | 0, 0, 0 | 0.000 (0.000-0.001) | 0 |
| bright | 2048, 2048, 2048 | 1.000 (0.999-1.000) | 1 |
| fixture | 1007, 998, 1053 | 0.498 (0.485-0.510) | 1/2 |

The fixture sits 0.002 below 1/2 (z = -0.36), so the emulator executes the
batched circuits as certified and the series analysis keys every replica to
its batch.

**Two-region placement, QX dry run.** The twin of the two-region placement
(six replicas, two per 10-qubit circuit) ran as one batch (twin-1..3, batch
job 870091, jobs 1527349, 1527350, 1527352), 2048 shots each, retained as
results/quantum_inspire/runs/2026-10-17T042652Z-zero_divisor_qx-batch-00.
`--analyze` writes results/quantum_inspire/zero_divisor_qx_two_region_analysis.json,
which gate core-330 replays with `--replay-series`; gate core-374 reruns
`--select-regions` and requires REGIONS to rank first.

| Case | replicas {1,2,4,7,8}, {11,12,14,15,16} (count of 2048 at s = 0) | P(s=0) (95%) | ideal |
|---|---|---|---|
| dark | 0, 0 | 0.000 (0.000-0.001) | 0 |
| bright | 2048, 2048 | 1.000 (0.999-1.000) | 1 |
| fixture | 1004, 986 | 0.486 (0.471-0.501) | 1/2 |

The fixture sits 0.014 below 1/2 (z = -1.81), inside the two-sided 95%
sampling band, so the regenerated circuits execute as certified on the
emulator.

## Residual ZZ of every Tuna-17 coupler

Each coupling-map edge carries a flux-tunable coupler that the control
system parks between gates; the park leaves a residual diagonal coupling J,
half the shift of a qubit's frequency when its neighbor flips. Pulse and
flux control are not exposed, so the map reads the couplers through gates.
`scripts/qi_coupler_zz_map.py` builds it from one property of Tuna-17's
coupling graph: it is bipartite (P = {0,4,5,6,10,11,12,16},
Q = {1,2,3,7,8,9,13,14,15}), and a diagonal Hamiltonian conserves every Z.
One configuration therefore runs Ramsey on every qubit of one part (X90,
idle, X90 or Y90) while the other part sits in |+> and is read in Z;
grouping each target's shots by its neighbors' outcomes gives every
conditional sector at once, and a weighted fit
nu(z) = omega + sum_k J_k s_k returns every incident coupler with a residual
that tests the pairwise, additive form. The rate comes from two delays,
0.5 and 2 us, so each sector's fixed phase cancels and a rate is known
modulo 666.7 kHz. Every sector of a target takes the alias branch nearest
the circular mean of its sectors, so J reads differences on one branch and
omega carries any common alias; a target detuned near 333 kHz would otherwise
split its sectors across branches and fail the additivity test spuriously.
The role swap measures every coupler again from its other end. The case is
10 circuits (2 roles x 2 quadratures x 2 delays, plus two readout circuits),
run as five batches: both readout references together, then one batch per
delay's x and y pair. A frame change between the two delays' batches adds
the same rate to every sector of a target and lands in omega, never in J;
`--conformance`
evolves all 17 qubits under injected frequencies, one of them at 320 kHz
across the alias edge, and all 24 couplings through the ALAP-scheduled
circuits and recovers them to 1e-10 Hz.

**Submission under the conditions of use.** The FAQ allows three queued
jobs per hardware backend, so the series ran as four batches of at most three
circuits, each submitted only after the previous one was collected, its
sanity gate passed (completed shots, readout error below 0.2, spectators near
P1 = 1/2) and a 120 s pause elapsed, with the account's own queue confirmed
empty; `qi_platform.py submit` refuses any batch that would lift the queued
jobs above three. A QX dry run on the 10-qubit subgraph {0..9} (12 couplers)
preceded any hardware submission: all ten jobs completed and every J and
frequency read consistent with zero (largest |z| 1.73 and 2.0) at
visibility 1.000. On Tuna-17 the four batches ran from 22:52 to 23:07 UTC,
10.2 to 14.3 s per 16384-shot job.

**Map** (results/quantum_inspire/coupler_zz_tuna_17_analysis.json; claim
kind exploratory reanalysis). Qubits 5, 6 and 7 fail as Ramsey targets on
visibility alone: it falls to 0.04, 0.27 and 0.08 by 2 us, while every other
qubit keeps at least 0.75. Qubits 5 and 6 idle 322 and 324 kHz from their
frames (modulo 666.7 kHz) and qubit 7 at -116 kHz; on one alias branch the
additive fit holds on all three (chi2 16.4/11, 0.26/1, 0.13/4) and on every
other target (smallest p 0.034, qubit 2). An end-quality rule fixed after the
data (visibility at least 0.3, additivity p at least 1e-3) excludes those
ends, so their couplers take J from the other end; every coupler keeps one
usable end. The retained run predates the paired batching: its P-role 0.5 us
and Q-role 2 us x/y pairs ran in adjacent batches, so a calibration change
between those batches enters their phases (`quadrature_pairs_across_batches`
in the analysis).

| Coupler | J (kHz) | ends | | Coupler | J (kHz) | ends |
|---|---|---|---|---|---|---|
| (11,14) | -31.4 +- 0.9 | 2 (-31.40, -31.47) | | (2,4) | +4.1 +- 0.9 | 2 |
| (1,4) | -19.3 +- 0.9 | 2 (-19.6, -19.0) | | (9,12) | +3.7 +- 0.9 | 2 |
| (3,5) | +11.7 +- 1.3 | 1 (Q3) | | (7,10) | +3.1 +- 1.2 | 1 (Q10) |
| (12,14) | +10.4 +- 0.9 | 2 | | (14,16) | -3.1 +- 1.0 | 2 |
| (0,2) | -7.9 +- 1.0 | 2 | | (4,7) | -3.0 +- 1.3 | 1 (Q4) |
| (3,6) | -7.8 +- 1.3 | 1 (Q3) | | (12,15) | +3.0 +- 0.9 | 2 |
| (11,13) | +7.5 +- 0.9 | 2 | | (0,1) | -2.2 +- 0.9 | 2 |
| (8,11) | +6.6 +- 0.9 | 2 (z -3.2) | | (8,12) | -0.7 +- 0.9 | 2 |
| (15,16) | +5.3 +- 1.0 | 2 | | (6,9) | +0.5 +- 1.5 | 1 (Q9) |
| (2,5) | +5.3 +- 1.3 | 1 (Q2) | | (5,8) | -0.4 +- 1.3 | 1 (Q8) |
| (4,8) | -5.0 +- 1.0 | 2 | | (10,13) | -0.4 +- 0.9 | 2 |
| | | | | (7,11) | -0.2 +- 1.3 | 1 (Q11) |
| | | | | (5,9) | +0.0 +- 1.4 | 1 (Q9) |

The 15 couplers with two usable ends agree within |z| 1.7 except (8,11)
(z -3.2, with Q11's additive fit at chi2 19.1/11). Two parks leave a
frequency shift above 35 kHz on flip (2J): (11,14) at -63 kHz and (1,4) at
-39 kHz. Two caveats bound every value: a spectator's Z outcome labels its
state through the 2 us idle only up to its decay, and neighbor readout error
mixes sectors; both shrink J toward zero, the second by about the neighbor's
1 - e01 - e10 (0.87 to 0.96 here).

**What the map explains.** `--explain-spectators` splits each neighbor-drive
shift of the earlier crosstalk run into the part the map predicts (a driver
toggled through 40 X gates is excited about half of the 800 ns window, so the
target's phase moves by -2 (2 pi J) (1/2) t) and a residual
(results/quantum_inspire/spectator_zz_split.json):

| Target, driver | measured (rad) | coupler ZZ predicted | residual (drive crosstalk) |
|---|---|---|---|
| Q11, Q14 | +0.153 | +0.158 +- 0.005 | -0.005 |
| Q4, Q8 | +0.030 | +0.025 | +0.005 |
| Q3, Q6 | +0.060 | +0.039 | +0.021 |
| Q12, Q9 | -0.043 | -0.019 | -0.024 |
| Q12, Q15 | -0.037 | -0.015 | -0.022 |
| Q11, Q13 | +0.014 | -0.038 | +0.051 |
| Q0, Q2 | +0.139 | +0.040 | +0.099 |
| Q0, Q1 | -0.122 | +0.011 | -0.133 |
| Q3, Q5 | +0.074 | -0.059 | +0.133 |
| Q4, Q7 | +0.633 | +0.015 | +0.618 |

Coupler ZZ accounts for the whole shift Q14 imposes on Q11 and Q8 on Q4; the
large shifts elsewhere, above all Q7 on Q4, are drive crosstalk the parked
coupler does not carry. The corner on qubits 0, 1, 2, 4, 5 where the
zero-divisor witness kept no resolved contrast combines the second-strongest
park, (1,4) at -19.3 kHz, (0,2) at -7.9 kHz, the short-coherence Q5, and the
Q1/Q2 drive crosstalk: a repeated spatial association, not a demonstrated
cause.

## Next cases

- Interleave the four configurations inside one job (disjoint stars per
  configuration) so drift cancels between them.
- Drive amplitude series (1, 2, 4 X-pair densities) to test the quadratic
  amplitude law of the a.c.-Stark mechanism.
- Teleportation with all six axial inputs on one path to give a channel's
  sphere average, and a direct-SWAP control without the Bell measurement.
- Ry emulator: rebuild the teleport case in the Rydberg-native form (no bit
  register, RYD blockade gates) and read results leftmost-first; until then
  the generator emits no Ry case.
- Zero-divisor depth series: the bright and dark witnesses with the SELECT
  repeated as SELECT, SELECT^dagger, SELECT pairs (identity padding) to fit
  the per-layer contraction directly, and a selector-only control to locate
  the bias toward 1.
- Tuna-5 and Tuna-9 cases are generated and wait for those backends to come
  online.

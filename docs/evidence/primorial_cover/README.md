# Primorial cover defects: certificates and the Kingston noise prediction

Six records live here.

- `certificates.json` is the output of `gororoba_quantum/primorial_cover.py
  --out`, recomputed byte for byte by gate `core-688` (about 5 s). It holds the
  four defect-one instances (k, gap) = (6, 20), (8, 32), (14, 86) and
  (14, 88) with their witnesses, CRT starts, wheel gaps, exhaustive branch
  counts (4, 15, 1485 and 150, none coverable), the 20 branches at each k = 14
  instance whose whole residual set gives a nonpositive capacity bound, the
  repair primes, the k = 14 linear relaxations (optimum 0, rational fractional
  cover verified exactly), the two Hall subsets, six positive controls, the
  slice tables with their exact Walsh coefficients and QAOA laws, the gap-20
  quotient and the parity network. The mathematics is in
  [primorial-cover-defects.md](../../notes/topics/primorial-cover-defects.md).
- `noise.json` is the output of `scripts/primorial_cover_noise.py`, run as
  Kaggle CPU kernel version 5 of `gororoba-primorial-cover-noise` under
  `push --ci-env` (Python 3.14.7, qiskit 2.6.0, qiskit-aer 0.17.2, numpy 2.5.4,
  four workers; `kaggle_environment.json`). The run is retained under
  `results/kaggle/2026-10-25T075839Z-gororoba-primorial-cover-noise/`, whose
  `collect.json` binds the file's bytes. The kernel built the hypercomplex
  stack and regenerated the retained tables before its entry ran
  (`kaggle_hypercomplex.json`). Gate `core-689` (about 90 s) requires
  `noise.json` to equal the collected output, recompiles every arm and
  requires layouts and CZ counts to match exactly and every law to 1e-8.
  A build-host CPU run of the same commit gives identical laws.
- `ziller_table.json` is the output of `gororoba_quantum/primorial_table.py
  --out`, recomputed byte for byte by gate `core-primorial-ziller-table-replay`
  (full tier, every worker; 176 s wall and 348 CPU-s on four workers, 218 s
  and 441 CPU-s on twelve under a load average near 20, the second round's
  single cell at k = 20, L = 73 taking about 90 s alone). It
  decides every even difference from 2 to h(k) for k = 1..20, 637 cells,
  where h(k) is the largest difference Ziller's Table 1 (arXiv:2007.01808v1,
  p. 12) prints. Each search walks the allowed residues of 3, 5, 7 and 11 in
  lexicographic order and runs the pruned depth-first search of
  `primorial_cover` over the remaining primes; a cover found at level k is
  carried to later levels with the smallest allowed residue of each new prime
  and rechecked there, so L is searched again only where it is excluded. The
  record keeps 84 witnesses (one per half-length, at the level first
  covered), the branch count of each of the 9 exclusions, and per row the
  missing set, N_min(k) and the membership of h(k) in D(k).
- `null_residuals.json` is the output of `scripts/primorial_null_residuals.py`,
  run as Kaggle CPU kernel version 3 of `gororoba-primorial-null-residuals`
  under `push --ci-env` and retained under
  `results/kaggle/2026-10-25T185707Z-gororoba-primorial-null-residuals/`,
  whose `collect.json` binds the file's bytes. It reads `noise.json` for the
  paths and shot budgets and records that file's sha256. Gate
  `core-primorial-null-residuals-replay` requires the file to equal the
  collected output, recomputes it, and requires the pulse identity, budgets
  and verdicts to match exactly and every bias to 1e-8.
- `bound_residuals.json` is the output of
  `scripts/primorial_bound_residuals.py`, run as Kaggle CPU kernel version 4
  of `gororoba-primorial-bound-residuals` under `push --ci-env` and retained
  under `results/kaggle/2026-10-25T221805Z-gororoba-primorial-bound-residuals/`,
  whose `collect.json` binds the file's bytes. It reads `noise.json`,
  `null_residuals.json` and the snapshot and records their sha256s. Gate
  `core-primorial-bound-residuals-replay` requires the file to equal the
  collected output, recomputes it, and requires every boolean, count and
  string to match exactly and every float to 1e-8 (376 s wall and 3,326
  CPU-s on the build host). The Kaggle record and a build-host run of the same commit agree
  with no departure at that tolerance.
- `probe_case.json` is the output of `scripts/primorial_probe_case.py`, run as Kaggle CPU kernel version 3
  of `gororoba-primorial-probe-case` under `push --ci-env` with the private dataset
  `gororoba-primorial-evidence` (noise.json, bound_residuals.json and the ibm_kingston snapshot,
  results/kaggle/datasets/gororoba-primorial-evidence.json) attached, and retained under
  `results/kaggle/2026-10-26T012733Z-gororoba-primorial-probe-case/`, whose `collect.json` binds the file's
  bytes. Gate `core-primorial-probe-case-replay` requires the file to equal the collected output, recomputes
  it, and requires every count, boolean and string to match and every float to 1e-8 (720 s wall and
  2,244 CPU-s on the build host under load).

## Ziller Table 1 through k = 20

The search agrees with Table 1 in every row k = 1..20: the missing
differences are 20 (k = 6), 32 (k = 8), 86 and 88 (k = 14), 98 (k = 15), 146
(k = 19) and 166, 170 and 172 (k = 20), no other k up to 20 misses one, every
N_min(k) matches, and h(k) lies in D(k) in every row. Each missing difference
first enters range at the level where it is excluded, and each one below
k = 20 is covered one level later: 20 at k = 7, 32 at k = 9, 86 and 88 at
k = 15, 98 at k = 16 and 146 at k = 20. The h(k)
column enters as the range bound only: D(k) is not downward closed, so the
search reproduces h(k) in D(k) and leaves its maximality to Ziller and to the
Jacobsthal values of his reference [10]. The exclusion counts (135 to 180
branches) are exhaustive over the branch primes; their correctness rests on
the pruning bound shared with `primorial_cover._coverable`; at k = 6, 8 and 14
they agree with `certificates.json`, which branches over different primes.

## Question and falsifiers

The design question of
[primorial-cover-defect-probes.md](../../design/primorial-cover-defect-probes.md):
under the noise model live_run uses (gate depolarizing and thermal relaxation,
asymmetric assignment) of `docs/evidence/calibration/ibm_kingston.json`
(calibration 2026-10-15T19:42:21-07:00), do the primorial circuits keep their
ideal readings, and what does a hardware run add? Stated before the run:

- **(a)** The quotient fails if a marked label reads below 0.9 or a
  complement-marked arm above 0.05.
- **(b)** Phase-gradient tomography fails if an assignment-corrected
  coefficient lies 1/16 or more from its exact value, the radius that
  identifies its integer numerator over 8.
- **(c)** The gap-88 repair contrast fails if the noisy QAOA total variation
  drops below half its ideal 0.132128.
- **(d)** The gap-86 repair fails the mutation test unless its compiled laws
  differ from the unrepaired ones.

## Method

Every arm compiles at optimization level 0 with the layout given and is ALAP
scheduled against the snapshot Target, keeping the delays on its path, on the
three-qubit path minimizing summed CZ error plus mean assignment error
(45-46-47; two-qubit edge 147-148) and on the path at the median of that cost
(117-125-126; edge 24-25). The compiled CZ count must equal the logical
entangler count (8 for every three-qubit arm), and each arm's noiseless law
must equal its statevector law to 1e-9. `snapshot_laws.outcome_law` gives
each exact law. The arms are the quotient's four marked, four
complement-marked, one no-oracle and four basis arms; twelve edges in X and Y
for the zero-angle null block, gap86, gap86 repaired, gap88 and gap88
repaired; the gap88 QAOA pair; and eight three-qubit basis arms, which give
the per-qubit assignment matrix. Shot budgets use the delta method for each
edge phase, with each mean's binomial variance scaled by `1/(1 - a - b)^2`
through the assignment inversion and, after null subtraction, the null arm's
phase variance added. Noise-free scenarios on the best path follow every CZ by
a conditional phase of 0.02, 0.05 or 0.1 rad, replace every sx by
RX(pi/2 (1 + eta)) at eta = 0.002, 0.004 or 0.01, or detune one path qubit by
10 or 30 kHz, its frame drifting by RZ(2 pi delta t) after every scheduled
gate or delay of duration t.

## Result

| | best | median |
| --- | ---: | ---: |
| (a) marked label read | 0.979 to 0.984 | 0.963 to 0.973 |
| (a) complement-marked arm | 0.0023 to 0.0029 | 0.0013 to 0.0015 |
| quotient mean cost at the problem label (ideal 1, uniform 1.75) | 1.017 | 1.031 |
| (b) gap88 largest bias, raw / corrected / null-subtracted | 0.0173 / 0.0020 / 0.0025 | 0.0133 / 0.0028 / 0.0032 |
| (b) shots per setting, all seven at family-wise 0.01, corrected / null-subtracted | 1,242 / 2,803 | 1,405 / 3,169 |
| gap88 repair `c_Z1` shift (exact -0.5), corrected | -0.4987 | -0.4992 |
| (c) QAOA total variation (ideal 0.132128) | 0.126 | 0.120 |

1. Falsifiers (a), (b) and (c) pass on both paths. Readout asymmetry is the
   largest bias source: uncorrected, it moves `c_Z2` by about 0.085/8 on the
   best path in every cost; the assignment correction removes it.
2. (d) holds as predicted: the gap-86 repaired arms compile to the same
   circuits and laws, so that repair is not measurable.
3. The CZ conditional-phase scenario gives largest biases 0.057, 0.143 and
   0.287 uncorrected and 0.0005, 0.0032 and 0.0128 after null subtraction, with
   cycle residuals 0.0004, 0.0025 and 0.0103: the error reads as a
   self-consistent Hamiltonian on `c_Z0`, `c_Z0Z1` and `c_Z1`, and the null
   arm removes it to first order. The sx amplitude error enters at second
   order: largest biases 0.00003, 0.0001 and 0.0007 uncorrected and at most
   0.0004 after null subtraction, against a per-coefficient standard
   deviation of at most 0.019 at 2,803 shots per setting.
4. A 10 kHz detuning of q0, q1 or q2 gives largest biases 0.078, 0.024 and
   0.015 uncorrected (0.233, 0.072 and 0.046 at 30 kHz). Wire 0 is never a
   CNOT target, so its drift lands on `c_Z0` alone; a q1 detuning also moves
   `c_Z0Z1`, and a q2 detuning `c_Z0Z2`, `c_Z1Z2` and `c_Z0Z1Z2`, because those
   wires carry parities during the block. Null subtraction leaves at most
   0.0022 at 30 kHz.

The incoherent model holds no coherent error, crosstalk or leakage, so its
pass on (a) to (c) is a design check, not a hardware prediction of those
terms; static ZZ and axis tilt are not simulated.

## Static ZZ and axis tilt

`noise.json` leaves two coherent families out. `null_residuals.json` adds
them on the gap-88 and zero-angle gradient arms of both paths, compiled as in
the noise record, with noise-free laws and every error at its pulse start in
the ALAP schedule, in the forms of `scripts/atlas_coherent_families.py`:
static ZZ on both couplers in the partner-in-0 frame (`zz`,
CPhase(-2 pi zeta t)) and the symmetric frame (`zz_symmetric`,
RZZ(pi zeta t)), and drive-axis tilt RY(-beta) R RY(beta) of every sx and x
pulse R, at fixed values and at each path qubit's gate-error bound: the
largest coherent tilt its snapshot sx error r allows,
acos(2 sqrt(1 - 1.5 r) - 1) (`atlas_coherent_families.gate_bounds`), on all
three qubits in each of the eight sign patterns. The criterion: a scenario
leaves a device question when its null-subtracted bias reaches one standard
deviation of the noisy null-subtracted estimate at the budget `noise.json`
retains for its path. An exploratory build-host run of the fixed-value
scenarios preceded the criterion; the gate-bound scenarios and the retained
run followed it.

| | best (45-46-47) | median (117-125-126) |
| --- | ---: | ---: |
| signal and null pulse streams identical | yes | yes |
| budget, shots per setting / coefficient SD | 2,803 / 0.0188 | 3,169 / 0.0186 |
| `zz` 2 / 5 / 20 kHz, raw bias | 0.0078 / 0.019 / 0.078 | same |
| `zz` 20 kHz, null-subtracted | 0.00038 | 0.00038 |
| `zz_symmetric` 20 kHz, raw / null-subtracted | 0.024 / 0.00013 | same |
| tilt 0.02 rad on q0 / q1 / q2, null-subtracted | 0.00022 / 0.0030 / 0.0045 | same |
| tilt 0.02 rad on all three, raw / null-subtracted | 0.174 / 0.0055 | same |
| shots per setting to resolve that residual at 3 SD | 290,836 | 320,842 |
| tilt gate-error bounds, q0 / q1 / q2 (rad) | 0.029 / 0.028 / 0.034 | 0.021 / 0.036 / 0.033 |
| tilt at the bounds, worst sign pattern, raw / null-subtracted | 0.233 / 0.0147 | 0.302 / 0.0159 |
| shots per setting to resolve that residual at 3 SD | 41,323 | 39,194 |

No scenario reaches its threshold, but tilt at the gate-error bound comes
closest: 0.78 and 0.85 of the budget's standard deviation. The bound charges
the whole reported sx error to coherent tilt, so it is an upper limit, and the
residual stays far inside the identification radius 1/16. The fixed-value
scenarios give the same biases on both paths because every path qubit and
coupler of both has the same sx, x and cz durations in the snapshot (32, 32
and 68 ns), so the schedules coincide; only the budgets and the tilt bounds
differ. ZZ enters the null-subtracted fit at second order (the residual
grows about sixteenfold from 5 to 20 kHz), and so does tilt. The record
covers the gap-88 cost on Heron r2 timing; crosstalk and leakage remain
outside it.
That verdict holds one family at a time; tilt and CZ phase jointly at their
bounds exceed it, as [Joint coherent bounds](#joint-coherent-bounds) records.

## Joint coherent bounds

`bound_residuals.json` tests the gap-88 null-subtracted fit against coherent
errors jointly and per coefficient, on the arms and paths above; the design
reading is
[primorial-cover-joint-coherent-bounds.md](../../design/primorial-cover-joint-coherent-bounds.md).
A numpy statevector of the three path qubits replays the timed compiled arms
and must reproduce every scenario of `null_residuals.json` and every
coherent sensitivity of `noise.json` to 1e-9 before any new scenario is read
(departure at most 1.6e-15). Each scenario reports:

- `max_z`, the largest null-subtracted coefficient bias divided by that
  coefficient's own standard deviation at the retained budget (0.0103 to
  0.0188);
- `shots_identify_all`, the budget rule of `primorial_cover_noise.phase_fit`
  with the scenario's bias in place of the incoherent one, None when the bias
  reaches 1/16.

Families at the gate-error bounds: drive-axis tilt and sx/x amplitude
error under the sx budget and under the tighter sx-and-x budget (the x
pulse's tilt infidelity is (2/3) sin^2(beta)), the CZ conditional phase at
acos(1 - 10 r / 3), all 8^3 qubit directions jointly with the 4 coupler
signs, a 5^5 interior grid over tilt and CZ phase with a coordinate-ascent
refinement, and the CZ phase replaced by its Pauli twirl with ideal frames.
Static detuning on all three qubits (5 and 30 kHz) and static ZZ in both
frames (2 and 20 kHz), which no gate error bounds, enter alone and in pairs
with the bounded families, every sign pattern.
The record adds the signal-arm-only mismatch at which max_z crosses 1, a
coherent-fraction scan (worst of 32 sign patterns per cell), and every
three-qubit path of the snapshot at its own bounds.

| | best (45-46-47) | median (117-125-126) |
| --- | ---: | ---: |
| tilt alone, sx bound, max_z | 0.79 | 0.89 |
| CZ phase alone at its bound, max_z | 0.72 | 0.77 |
| tilt and CZ phase jointly, max_z / bias | 2.61 / 0.049 | 2.84 / 0.050 |
| refined interior maximum, max_z | 2.62 | 2.85 |
| shots to identify at that bias (retained) | 53,363 (2,803) | 76,596 (3,169) |
| joint under the sx-and-x budget, max_z | 1.90 | 2.06 |
| twirled CZ phase alone / with tilt, max_z | 0.27 / 1.07 | 0.29 / 1.20 |
| fraction scan, tilt 0.1 of bound and CZ phase at bound, max_z | 0.84 | 0.90 |
| fraction scan, tilt 0.2 of bound and CZ phase at bound, max_z | 0.98 | 1.04 |
| detuning 30 kHz alone / with CZ phase 0.04 rad, max_z | 0.13 / 0.43 | 0.14 / 0.45 |
| detuning 30 kHz with the CZ-phase / tilt bound, max_z | 1.32 / 1.59 | 1.40 / 1.75 |
| partner-in-0 ZZ 20 kHz with the tilt / CZ-phase bound, max_z | 1.03 / 0.98 | 1.15 / 1.04 |
| q0 detuning mismatch reaching max_z 1 (kHz) | 2.4 | 2.2 |

All 226 working paths reach max_z 1 at their own bounds and 82 exceed the
identification radius; eight paths through qubits 113, 121 and 146 (sx and x
error 1.0) are dropped. The path sweep compiles every path, finds 9 distinct
gate streams, and reads every path against the best path's standard
deviations. The twirled rows idealize the twirl as ideal Pauli frames around
the CZ, leaving the sx and x stream unchanged. An exploratory build-host run
preceded the per-coefficient reading and every row after the joint
families, and the detuning and ZZ pairs followed a review of the first
retained run; the record's docstring lists the order.

## Probe case

`probe_case.json` designs the hardware case
[PRIMORIAL_COHERENCE_CASE.md](../../../results/live/PRIMORIAL_COHERENCE_CASE.md) on the best and median
paths of `noise.json`:

- **Detuning mapping.** A constant-amplitude pulse under a detuning Delta equals the record's tilt
  Delta / Omega to an infidelity of 3.6e-10 over 0 to 60 kHz, so predictions put tilt on pulses and
  detuning on idles and CZs only.
- **Probes.** The circuits of `gororoba_quantum/coherence_probes.py` recover injected tilt, CZ phase,
  detuning and ZZ, every family at once, within 5.2e-5 rad of x tilt, 4.1e-5 rad of sx tilt, 4e-6 rad of
  CZ phase, 2.6 Hz of detuning and 1.3 Hz of ZZ. Under the snapshot's noise every estimate's bias stays
  below its standard error; the shots that resolve each decision threshold at three standard deviations
  are 2 (CZ phase at 0.7 of its bound), at most 18 (tilt at 0.2 of its sx and x bounds), at most 60
  (detuning of 5 kHz) and 757 (ZZ of 2 kHz, which sets the 98-circuit job at 757 shots per circuit).
- **Twirl instances.** The client-side Sampler's boxing and samplomatic 0.21.0's `build`, sampled at 32
  randomizations (QRNG seed 2441) and 512 (seed 50280), reproduce the ideal law to 3e-7. Independent
  randomizations of the signal and null arms leave their coherent errors unshared: at the gate-error
  bounds the 32-instance joint max_z is 5.4 and 6.5 against 2.6 and 2.8 untwirled, and 512 instances
  bring it to 1.03 and 1.11. The case runs untwirled.
- **Noise model.** The decisive scenarios under the snapshot's noise give a null-subtracted bias of 0.051
  and 0.053 at the joint bound against 0.049 and 0.050 noise-free, the difference the incoherent floor
  (0.0026 and 0.0033).
- **Schedule.** The probe job runs a 25.0 ms column of 98 circuits, about 20.9 s of QPU time at 757 shots;
  the untwirled gap-88 job of 104 circuits (gap-88, null, null, gap-88 per setting and 8 basis
  preparations) a 26.3 ms column, 75.8 and 85.4 s at the paths' budgets.
- **Decision rule.** The untwirled predicted max_z over 128 Sobol points of the estimates' uncertainty
  has a 95th percentile of 0.0004 and 0.0005 at zero error (proceed), 0.069 and 0.072 at the repository's
  measured scales (proceed) and 1.07 and 1.14 at the decision thresholds (stop).

An exploratory build-host run came before the retained one and changed the design: it found the sx tilt
cells biased by ZZ between neighbors flipping together (now run on the outer pair and the middle qubit
separately), the twirled mode's harm, and the need for the balanced gap-88 order and the noise-model
check, all added before the retained run.

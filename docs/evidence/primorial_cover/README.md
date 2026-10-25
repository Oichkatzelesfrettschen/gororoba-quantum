# Primorial cover defects: certificates and the Kingston noise prediction

Three records live here.

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

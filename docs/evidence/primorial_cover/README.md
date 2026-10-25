# Primorial cover defects: certificates and the Kingston noise prediction

Two records live here.

- `certificates.json` is the output of `gororoba_quantum/primorial_cover.py
  --out`, recomputed byte for byte by gate `core-682` (about 5 s). It holds the
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
  Kaggle CPU kernel version 2 of `gororoba-primorial-cover-noise` under
  `push --ci-env` (Python 3.14.7, qiskit 2.6.0, qiskit-aer 0.17.2, numpy 2.5.4,
  four workers; `kaggle_environment.json`). The run is retained under
  `results/kaggle/2026-10-25T002903Z-gororoba-primorial-cover-noise/`, whose
  `collect.json` binds the file's bytes. The kernel built the hypercomplex
  stack and regenerated the retained tables before its entry ran
  (`kaggle_hypercomplex.json`). Gate `core-683` (about 90 s) requires
  `noise.json` to equal the collected output, recompiles every arm and
  requires layouts and CZ counts to match exactly and every law to 1e-8.
  A build-host CPU run of the same commit agrees with it to 1.1e-16.

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

Every arm compiles at optimization level 0 with the layout given, on the
three-qubit path minimizing summed CZ error plus mean assignment error
(45-46-47; two-qubit edge 147-148) and on the path at the median of that cost
(117-125-126; edge 24-25). The compiled CZ count must equal the logical
entangler count (8 for every three-qubit arm), and each arm's noiseless law
must equal its statevector law to 1e-9. `snapshot_laws.outcome_law` gives
each exact law. The arms are the quotient's four marked, four
complement-marked, one no-oracle and four basis arms; twelve edges in X and Y
for the zero-angle null block, gap86, gap86 repaired, gap88 and gap88
repaired; the gap88 QAOA pair; and eight three-qubit basis arms, which give
the per-qubit assignment matrix. A noise-free scenario follows every CZ by a
conditional phase of 0.02, 0.05 or 0.1 rad on the best path.

## Result

| | best | median |
| --- | ---: | ---: |
| (a) marked label read | 0.979 to 0.984 | 0.963 to 0.973 |
| (a) complement-marked arm | 0.0023 to 0.0029 | 0.0013 to 0.0015 |
| quotient mean cost at the problem label (ideal 1, uniform 1.75) | 1.017 | 1.031 |
| (b) gap88 largest bias, raw / corrected / null-subtracted | 0.0174 / 0.0019 / 0.0024 | 0.0134 / 0.0027 / 0.0031 |
| (b) shots per setting, all seven at family-wise 0.01, null-subtracted | 1,236 | 1,269 |
| gap88 repair `c_Z1` shift (exact -0.5), corrected | -0.4991 | -0.4996 |
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
   arm removes it to first order.
4. The cost block lasts 0.832 us, so a static detuning shifts its qubit's
   single-body coefficient by 0.0075 per kHz; the null arm carries the same
   shift.

The model holds no coherent error, crosstalk or leakage, so its pass on (a) to
(c) is a design check, not a hardware prediction of those terms.

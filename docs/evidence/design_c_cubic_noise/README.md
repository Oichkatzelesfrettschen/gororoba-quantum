# Dim-32 Design C spectral classes under the Kingston calibration

`result.json` is the output of `scripts/design_c_cubic_noise.py --pairs all`,
run as Kaggle kernel version 3 of `gororoba-design-c-cubic-noise` from commit
ef9a761 (Tesla T4, qiskit 2.5.2, qiskit-aer-gpu-cu11 0.17.2;
`kaggle_environment.json`). The kernel built the hypercomplex package stack
from the pinned archives and regenerated the retained tables byte for byte
before its entry ran (`kaggle_hypercomplex.json`). Noise comes from
`docs/evidence/calibration/ibm_kingston.json` (calibration
2026-10-15T19:42:21-07:00). For each of the 360 degree-3 dim-32 pairs it
compiles three implementations of W_ij to that Target (optimization level 3,
seed 11) and samples 20,000 noisy shots of the Walsh distribution.

## Result

| Ideal class K | Pairs | Factorized: noisy K (range) | Reed-Muller: noisy K | CCZ normal form: noisy K | Factorized TV | Mean CZ (fact., RM, NF) |
| --- | ---: | --- | --- | --- | ---: | --- |
| 11/32 = 0.344 | 234 | 0.211 (0.181 to 0.253) | 0.307 | 0.298 | 0.181 | 122.9, 19.6, 29.2 |
| 5/32 = 0.156 | 126 | 0.102 (0.093 to 0.113) | 0.141 | 0.140 | 0.169 | 127.6, 29.2, 31.4 |

- The factorized circuit, the one whose hardware run tests composition of
  the three multiplication blocks, keeps the two classes apart under this
  noise model: every high-class pair estimates above 0.181 and every
  low-class pair below 0.113. The mean class gap falls from 0.188 to
  0.109.
- The diagonal references keep about 86 percent of the gap at a sixth to a
  quarter of the factorized mean CZ count; they encode the predicted phase
  and serve as calibration references, not as tests of composition.
- The model carries gate depolarizing and thermal-relaxation errors from
  the Target and asymmetric readout from the properties, as
  `live_run.noise_simulator` does; coherent errors, crosstalk and leakage
  are outside it, so the margin is a model prediction a hardware case would
  test, not a hardware result.
- Version 1 of this kernel ran before the stack proof existed and is retained
  under results/kaggle/ as history only; this result replaces it.

## Replay

Gate core-282 reruns pairs (1, 16) and (9, 18), one per class, on the CPU
and requires each TV distance and collision estimate to agree with the
retained GPU values within five standard errors of a difference of two
independent estimates, and the CZ counts to agree exactly.

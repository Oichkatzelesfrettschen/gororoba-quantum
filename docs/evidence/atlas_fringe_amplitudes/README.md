# Fringe amplitude ratios on the Fez and Kingston atlas runs

`result.json` is the output of `scripts/atlas_fringe_amplitudes.py --runs
ibm_fez,ibm_kingston --lanes 4`. The script docstring defines the observable,
the noise propagation, the predictors, the scores and the falsifiers.

- **Observable.** For each edge, the observable is y = log(b_hw / b_replay).
  b is the least-squares contrast of a + b cos(phi - phi0) fitted to the 8
  phase points. The replay is the calibration-bound execution replay, and
  sigma_y propagates the binomial noise of both fringes.
- **Structure.** The `structure` block covers all 14 lanes and needs no
  simulation.
- **Fits.** The `lanes` block fits lane 4 of each run. Fez fits 12 edges on
  qubits 50, 51, 52, 58 and 71. Kingston fits 10 edges on qubits 138 and
  150-153; 2 of its edges span a calibration change and are excluded.

## Inputs

`inputs` names the 301 files the computation read, each with its sha256:

- both runs' `record.json`, `isa.qpy` and raw PUB files;
- the Fez `measured-ripple.json` and the Kingston `collect.json`;
- the retained `docs/evidence/atlas_detuning_map/result.json`;
- the two calibration snapshots of lane 4.

`--check` verifies every digest before it recomputes anything. It also
stops when the rerun reads a file the result does not name.

## Structure against shot noise (all 14 lanes)

Columns, by group:

- **Replay normalization:** n edges, weighted mean of y, standard deviation
  of y, RMS of sigma_y, and chi-square against a lane constant with its
  p-value. tau is the DerSimonian-Laird excess scatter.
- **Ideal normalization:** log(2 b_hw), its chi-square per degree of freedom
  and its tau.
- **Bootstrap:** the largest departure of the bootstrap standard deviation
  from the propagated sigma (2000 draws).

| Backend | Lane | n | mean y | sd y | noise | chi2 / dof | p | tau | ideal chi2/dof | ideal tau | bootstrap dev |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fez | 0 | 12 | -0.375 | 0.225 | 0.038 | 320.1/11 | < 1e-9 | 0.175 | 49.77 | 0.197 | 0.03 |
| fez | 1 | 12 | -0.054 | 0.046 | 0.025 | 36.7/11 | 1.3e-04 | 0.037 | 12.44 | 0.060 | 0.02 |
| fez | 2 | 12 | -0.151 | 0.046 | 0.021 | 47.2/11 | 2.0e-06 | 0.038 | 7.51 | 0.042 | 0.02 |
| fez | 3 | 12 | -0.267 | 0.105 | 0.030 | 188.5/11 | < 1e-9 | 0.115 | 24.21 | 0.113 | 0.04 |
| fez | 4 | 12 | -0.218 | 0.055 | 0.024 | 54.6/11 | 9.3e-08 | 0.046 | 8.05 | 0.051 | 0.03 |
| fez | 5 | 12 | -0.291 | 0.048 | 0.031 | 27.9/11 | 3.4e-03 | 0.037 | 10.80 | 0.077 | 0.03 |
| fez | 6 | 12 | -0.139 | 0.045 | 0.024 | 37.5/11 | 9.5e-05 | 0.036 | 10.31 | 0.055 | 0.02 |
| kingston | 0 | 10 | -0.167 | 0.057 | 0.024 | 53.8/9 | 2.0e-08 | 0.053 | 6.94 | 0.046 | 0.03 |
| kingston | 1 | 10 | -0.155 | 0.038 | 0.020 | 32.3/9 | 1.8e-04 | 0.032 | 8.46 | 0.043 | 0.02 |
| kingston | 2 | 10 | -0.116 | 0.029 | 0.021 | 17.1/9 | 4.7e-02 | 0.020 | 3.53 | 0.026 | 0.04 |
| kingston | 3 | 10 | -0.077 | 0.020 | 0.022 | 7.4/9 | 0.59 | 0.000 | 10.49 | 0.051 | 0.02 |
| kingston | 4 | 10 | -0.138 | 0.053 | 0.020 | 61.8/9 | 1.0e-09 | 0.049 | 10.96 | 0.050 | 0.04 |
| kingston | 5 | 10 | -0.149 | 0.021 | 0.023 | 7.6/9 | 0.57 | 0.000 | 2.96 | 0.025 | 0.03 |
| kingston | 6 | 10 | -0.123 | 0.025 | 0.020 | 13.6/9 | 0.14 | 0.014 | 2.57 | 0.019 | 0.03 |

- **The shot-noise floor holds on every lane.** The bootstrap departs from
  the propagated sigma by at most 4 percent, inside the 10 percent
  falsifier.
- **Ten lanes carry amplitude structure beyond shot noise (p < 0.01):** all
  seven Fez lanes and Kingston lanes 0, 1 and 4. Their excess scatter is
  0.03 to 0.18 in log contrast.
- **Four lanes are consistent with a lane constant:** Kingston lanes 2, 3,
  5 and 6. On those lanes the model step reduces to the constant.
- **Fez lane 0 has a broad spread, not a single outlier.** Four of its 12
  edges sit below y = -0.55.
- **Normalizing by the replay lowers the excess scatter tau on 12 of 14
  lanes against the ideal normalization; it rises on Fez lane 3 and
  Kingston lane 0.** tau is in units of y under both normalizations, so it
  compares them. The calibrated channels therefore carry part of the edge
  structure. The two chi-square columns do not compare: the replay one
  divides by sigma_y, which includes sigma_replay, and the ideal one by
  sigma_hw alone.

## The replay omits idle relaxation

`replay_channel_check` tests what the replay charges. It compares the
replay's own loss, log(2 b_replay), with the loss of the calibrated channels
alone: the cz and sx depolarizing columns plus the readout factor
log(1 - E).

| Lane 4 | mean difference | chi2, replay omits idle | chi2, replay charges idle | mean idle Lambda |
| --- | ---: | ---: | ---: | ---: |
| Fez | -0.0013 | 9.4 / 12 (p 0.67) | 503.5 / 12 | -0.085 |
| Kingston | 0.0020 | 8.5 / 10 (p 0.58) | 205.5 / 10 | -0.051 |

The calibrated channels reproduce the replay contrast within its shot
noise. The idle-relaxation column Lambda is absent from it. The replay
simulates the ISA circuit, which carries no delay, so qubits waiting
between their pulses stay ideal there.

## Model scores on lane 4

Each entry gives the leave-one-out RMS of y, then its noise floor in
parentheses, then the fitted parameters. Models whose fitted parameter
leaves the physical domain are marked as collinear.

| Model | Fez | Kingston |
| --- | --- | --- |
| lane constant | 0.057 (0.025), -0.221 | 0.055 (0.021), -0.142 |
| measured qubit | 0.067 (0.027) | unidentified (one edge on qubit 152) |
| idle relaxation | 0.036 (0.025), kappa 2.61 | 0.054 (0.021), kappa 2.74 |
| idle relaxation + constant | 0.040 (0.026), kappa 3.23 | 0.059 (0.023), kappa 1.67 |
| idle prediction, kappa = 1 | 0.143 (0.024) | 0.103 (0.020) |
| idle prediction + constant | 0.047 (0.025) | 0.054 (0.021) |
| CZ depolarizing | 0.058 (0.025), kappa 1.65 | 0.060 (0.021), kappa 1.20 |
| CZ depolarizing + constant | 0.058 (0.026) | 0.065 (0.023) |
| sx depolarizing | 0.067 (0.025) | 0.062 (0.021) |
| readout | 0.112 (0.025) | 0.056 (0.021) |
| replay loss (all channels scaled) | 0.073 (0.035), beta 1.01 | 0.062 (0.030), beta 0.91 |
| idle damping and dephasing (exploratory) | 0.043 (0.026), 2.32 / 2.97 | 0.067 (0.023), 0.99 / 3.72 |
| idle + CZ (exploratory) | 0.029 (0.026), kappa_cz -1.44, collinear | 0.058 (0.023) |
| cz_phase curvature + constant | 0.049 (0.035), refuted by phase | 0.052 (0.025), refuted by phase, beyond bound |
| sx_amplitude curvature + constant | 0.056 (0.028), beyond bound, refuted by phase | 0.065 (0.025), beyond bound, refuted by phase |
| axis_tilt curvature + constant | 0.048 (0.029), beyond bound, refuted by phase | 0.048 (0.023), beyond bound, refuted by phase |
| detuning curvature + constant | 0.057 (0.037), 20 to 99 kHz, refuted by phase | 0.038 (0.032), 29 to 222 kHz, refuted by phase |
| zz / zz_symmetric curvature + constant | 0.053 / 0.047, 39 to 265 kHz, refuted by phase | 0.061 / 0.064, refuted |

### Fez lane 4

- Idle relaxation is the only single physical column that beats the lane
  constant.
- Without a constant it accounts for the structure at 1.44 times its floor.
  With a constant it scores 0.040 against the constant's 0.057, at 1.52
  times its floor, just past the 1.5 criterion.
- The parameter-free prediction at kappa = 1 is refuted: its chi-square is
  437 over 12 edges. y - Lambda still carries structure, with chi-square
  per degree of freedom 3.4.
- The hardware therefore loses about 2.6 to 3.2 times the idle relaxation
  that T1 and T2 predict.

### Kingston lane 4

- Idle relaxation without a constant ties the lane constant (0.054 against
  0.055).
- With a constant it is refuted (0.059).
- No physical column predicts the edge structure on this lane.

### Coefficient readings

- **Without a constant, kappa is essentially mean y over mean Lambda.**
  This gives 2.6 on Fez and 2.7 on Kingston. The agreement between the runs
  concerns the mean loss, not the structure.
- **The direction is expected.** The reported T2 comes from a Hahn echo
  (`docs/notes/ibm_quantum/qpu-information.md`). These runs execute with
  dynamical decoupling and twirling off. A free idle gap therefore dephases
  at the Ramsey rate, which is at least the echo rate.
- **The mechanism is not established.** The split gives a damping
  coefficient of 2.3 on Fez. The echo-to-Ramsey difference cannot raise T1
  losses, and the split is poorly conditioned (fold condition 9 to 21). The
  Ramsey-dephasing mechanism is rated low to moderate.

### Other incoherent scales

- CZ depolarizing scale, sx depolarizing scale, readout and the scaled
  replay loss are each refuted on both lanes.
- The two-column idle + CZ fits need a negative CZ excess (kappa_cz from
  -0.36 to -1.69; below -1 the CZ factor c is negative). That reflects
  collinearity between the two columns, not a model.

### Coherent families

- Each fits magnitudes to the contrast through the second-order curvature.
- Every fit is refuted by the phase on both lanes. At the best sign
  pattern, the resimulated phase shifts leave a residual at or above the
  RMS of the measured offsets about their lane mean.
- The bounded families (sx_amplitude, axis_tilt and cz_phase on Kingston)
  also need magnitudes beyond the calibration bound.
- Column normalization makes the detuning and ZZ curvature designs
  identified, and their fits need tens to hundreds of kHz.
- The coherent families carry the phase offsets of the companion fit and
  not the amplitude structure.

## Confirmation criterion for the 14-lane run

The hypotheses were selected on lane 4, so the confirming set is the eight
other structured lanes: Fez 0, 1, 2, 3, 5 and 6, and Kingston 0 and 1.

- **Confirmed** if `idle_relaxation_plus_constant` scores below
  `lane_constant` on at least 6 of the 8. **Refuted** otherwise.
- **The kappa = 1 prediction is refuted** on every lane where the
  chi-square of y - Lambda exceeds its 99th percentile. It is already
  refuted on lane 4 of both runs.

## Gates

- **core-340** (pr tier, 83 s for both modes at one worker): `--self-test`.
  It checks:
  - the thermal and depolarizing channels against qiskit_aer;
  - qubit order;
  - the density matrix against the statevector on Fez lane 4;
  - the bootstrap against the propagated sigma;
  - planted structure: a lane constant passes, a planted 3 x idle
    relaxation is flagged and its coefficient recovered within 3 standard
    errors, and a planted sx amplitude of -0.02 on qubit 58 is recovered in
    magnitude, sign and constant.
- **core-341** (full tier, 395 s for both modes at one worker: 227 s normal, 168 s optimized):
  `--check result.json --runs ibm_fez,ibm_kingston --lanes 4`. It recomputes
  both lanes and the 14-lane structure block, and compares every number
  within 1.5e-6 absolute or 1e-9 relative.

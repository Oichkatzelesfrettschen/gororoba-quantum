# Perceval-native integration for Belenos

Three tools put Perceval 1.3.1 and exqalibur 1.4.2 beside our own Belenos code. Our code stays
authoritative for approval binding, digests and records; each native feature enters as an opt-in
whose result a record captures. No tool submits, creates or cancels a provider job, and none draws
from an unseeded generator. Tests: `tests/scripts/test_qd_live_noise_sim.py`,
`test_qd_perceval_crosscheck.py` and `test_qd_offline_mitigation.py`.

## Live-figure noisy simulation

`scripts/qd_live_noise_sim.py` rebuilds each retained entry on Perceval's SLOS backend: the served
`computed_circuit` and `computed_input`, threshold detectors, and a `NoiseModel` whose
indistinguishability, g2 and transmittance come from the run's `perfs_at_plan` (or any catalogue
through `--perfs`, or the newest `platform-before/catalogue.json` through `--newest-catalogue`).
The tool reads the exact output distribution, so no seed enters, and passes the expected counts to
`qd_belenos_cone.cell`, which reports `in_block_cone` and `tvd_cone_from_ideal` as the retained
reading does. Arms: `ideal`, `noise`, `noise_eff` (per-mode detector efficiency t_out / max t_out, a
relative-weight reading), `noise_dark` (receipt dark counts as independent clicks per pulse) and
`noise_eff_dark`. Each arm runs with the served input and with the block's source mode, which removes
a per-iteration `input_mode` switch. The record of job-16 is
`docs/evidence/quandela/belenos_live_noise_sim.json`; `--check` replays it.

Question: can a noise model with the live figures produce the routing collapse? Prediction, recorded
before the run: no, because a figure-driven simulation is a function of (mesh, input, figures), so
entries that share a mesh and an input receive one prediction. Measured (evidence class: local
simulation against retained provider counts; tvd threshold 0.3 marks a collapsed entry):

| Run | Entries (collapsed) | Observed tvd range | Predicted tvd, every arm | Observed in_block_cone min | Predicted in_block_cone min |
|---|---|---|---|---|---|
| job-16 | 24 (2) | 0.078 to 0.819 | 0 to 0.157 | 0.450 | 1.000 |
| job16 replay a3eb02eb | 10 (1) | 0.106 to 0.618 | 0 to 0.062 | 0.712 | 0.999 |
| off-cone jobs 7b918f1c, 74edcf2e, 21baf895 | 30 each (15 each) | 0.189 to 0.898 | 0 to 0.062 | 0.135 | 0.992 |

Every arm reads `does_not_reproduce` on every run. On mesh 29dc6ef8 with source mode 20, the
observed tvd spread is 0.742 in job-16 and 0.512 in the replay against a predicted spread of 0 (ideal,
noise, noise_eff) or at most 0.001 (dark arms); the three off-cone jobs spread 0.255, 0.021 and 0.027
against at most 0.008. The dark counts explain at most 69 of 1243 off-cone clicks in job-16. The
collapse is therefore a property of the entry (the iteration within its job), outside the reach of
a static source, detector and dark-count model; the `noise_eff` arm moves the in-cone shape (tvd up
to 0.157) and leaves every click inside the cone. The simulated `global_perf` differs from the served
`physical_perf` by a factor 0.31 to 0.95 within job-16, 0.13 to 0.39 in the replay and 0.017 to 1.24
in the off-cone jobs, so detection efficiency varies from entry to entry beyond the published figures.
The replay and off-cone runs live on branch `qd-belenos-offcone-mechanisms-case`; their readings
come from `--write` against that branch's case directories and sit in the pull request body, not in a
retained record.

## Native cross-checks

`scripts/qd_perceval_crosscheck.py` records four comparisons in
`docs/evidence/quandela/belenos_perceval_crosscheck.json`:

- `unitary`: `qd_belenos_mesh.unitary` equals `Circuit.compute_unitary()` of the served circuit
  on all 24 job-16 entries (largest difference below 5e-10 after rounding; 5.3e-16 on entry 0), over
  552 couplers, 574 phase shifters and 276 Mach-Zehnder cells.
- `optimizer`: `CircuitOptimizer(ntrials=1).optimize` over the served architecture with symbolic
  phases, started from the served phases, returns fidelity 1.0, which fixes the parameter order of
  `mesh_phases` against Perceval's. No random start runs.
- `decomposition`: `Circuit.decomposition` (triangle, `BS(theta, phi_tr)`) returns a 300-component
  circuit with error below 1e-6 for the 24-mode Fourier matrix and returns `None` for the served
  unitary; with `allow_error=True` it returns a 294-component circuit with error below 1e-2. The
  retry draws from an unseeded generator, so the record keeps only the error class. The mesh fit of
  `qd_belenos_mesh.BlockFit` reaches the served unitary exactly, which the native triangle does not.
- `cz`: the success probability of Catalog `postprocessed cz` with
  `NoiseModel(indistinguishability=M)` equals 1/9 for inputs 00, 01 and 11 and (5 - 4M)/9 for
  input 10 at M in 1, 0.8, 0.5 and 0 (difference 0), so the rate ratio D equals 5 - 4M, the law of
  `ascella_cz_tomography_reference_case.rail_rate_ratio`. Catalog `heralded cz` succeeds with
  2/27 at M = 1 for every input.

## Offline mitigations

`scripts/qd_offline_mitigation.py` separates the three mitigations of the quantum cloud by
Perceval's `extend_computation` and `parse_results` split:

| Mitigation | Offline on retained counts | Reason |
|---|---|---|
| DetectorBalancing | yes, for a run with `mitigations: []` | one `probs` computation; the detector model is the catalogue's `specs.detector` at unit efficiency |
| PhotonRecycling | only for 3 or more ideal photons with n - 1 and n - 2 photon states | a function of the count distribution |
| DistinguishablePhotonMitigation | no | the sub-computations with fewer input photons are provider jobs; `dpm_overhead` prices them offline |

A run without the `mitigations` field carries the server's default mitigation, and
`read_run` refuses it unless `allow_server_default` is set (the CLI flag
`--allow-server-default` records a warning). The record
`docs/evidence/quandela/belenos_offline_mitigation.json` reads the 12 entries of
`bdsc_qualification` `tc-none-e1`: single-photon inputs on threshold detectors give a perf factor of
1.0 and a one-click change of 0, so balancing leaves them unchanged, PhotonRecycling is not applicable
and DistinguishablePhotonMitigation order 1 needs 2 sub-computations.

## Unseeded generators in Perceval 1.3.1

`probs_to_sample_count` draws from numpy's global generator; `seeded_counts` calls
`perceval.random_seed(seed)` first, so a caller that writes counts passes a value of a retained QRNG
draw through `qrng_seeds.add_seed_argument`. `Matrix.random_unitary`, `CircuitOptimizer.optimize`
without `first_guess` (its `seed` argument defaults to None) and the `allow_error` retries of
`Circuit.decomposition` are unseeded as well, and no tool here calls them.

## Open items

- The off-cone readings of branch `qd-belenos-offcone-mechanisms-case` enter a retained record when
  that branch lands.
- A seeded Perceval `CircuitOptimizer` fit of the 4-mode block against `BlockFit` needs a QRNG draw
  and a ledger row; the tools here run only the first-guess form.
- The `program-quandela-belenos` skill does not yet name these tools.

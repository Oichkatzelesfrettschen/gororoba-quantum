# Ghost runs: every retained IBM job replayed under every retained calibration

`scripts/ghost_run.py` rebuilds each retained run's executed replicas from its
`isa.qpy` and `record.json` exactly as `live_run.collect` does. It simulates
them under calibration snapshots from `docs/evidence/calibration/history/`
(`scripts/ghost_calibrations.py`). It then compares each replica's simulated
distribution with the hardware distribution in `collect.json` by total
variation distance. Each member is sampled at the shot count its job ran
with, which is the pub_shots tier collect.json records per executed member.

[result.json](result.json) is the output of the Kaggle T4 kernel
`gororoba-ghost-runs` version 3 (run directory
results/kaggle/2026-10-16T090343Z-gororoba-ghost-runs, qiskit 2.5.2,
qiskit-aer 0.17.2), which ran the script at its committed revision. The
runs' raw files reached the kernel as the private dataset
`gororoba-retained-runs`, and all 659 files matched their recorded sha256
([kaggle_datasets.json](kaggle_datasets.json)). The stack proof
([kaggle_hypercomplex.json](kaggle_hypercomplex.json)) reads
`identical: true`. [report.json](report.json) is
`ghost_run.py --report result.json`.

Every retained snapshot of a run's backend covers every member of the run.
The report reads three of them:

- **execution**: per member, the snapshot in force at its PUB start. Every
  one of the 2335 executed members maps to a snapshot carrying exactly the
  calibration identity its collection recorded (gate core-286).
- **current**: the backend's calibration when the snapshots were exported.
- **all states**: every retained snapshot, grouped by noise content. The
  14 calibration identities hold 12 distinct noise models, because two
  Kingston updates changed no gate, readout or coherence value.

## Result

The table gives, for each run:

- the mean TV distance under the execution calibration;
- the paired per-replica difference of today's calibration from it on the
  same members, with its standard error in parentheses;
- the mean distance over all members under each distinct state;
- the replay self-check: the number of replicas whose collection recorded
  its own replay distance, the mean |ghost - recorded|, and the mean
  |ghost - ghost'| between two independent ghost draws.

| Run | Backend | Members (shots) | Execution TVD | Current minus execution | States, range | Self-check: pairs, recorded / resampled |
| --- | --- | --- | ---: | --- | --- | --- |
| 2026-10-11T152922 | Kingston | 9 (9x4096) | 0.102 | -0.0017 (0.0017) | 6, 0.094-0.103 | 29: 0.0027 / 0.0038 |
| 2026-10-12T055624 | Kingston | 16 (16x8192) | 0.138 | -0.0181 (0.0015) | 6, 0.120-0.142 | 16: 0.0052 / 0.0036 |
| 2026-10-13T020454 | Kingston | 4 (4x8192) | 0.186 | -0.0316 (0.0013) | 6, 0.154-0.186 | 0 |
| 2026-10-13T022433 | Kingston | 4 (4x8192) | 0.210 | -0.0316 (0.0013) | 6, 0.178-0.210 | 0 |
| 2026-10-13T025444 | Fez | 929 (856x1024, 73x4096) | 0.069 | -0.0034 (0.0005) | 5, 0.066-0.069 | 0 |
| 2026-10-13T032011 | Fez | 176 (120x1024, 56x4096) | 0.041 | +0.0023 (0.0007) | 5, 0.039-0.048 | 0 |
| 2026-10-13T080216 | Fez | 2 (2x4096) | 0.070 | -0.0136 (0.0060) | 5, 0.056-0.071 | 2: 0.0101 / 0.0068 |
| 2026-10-13T083417 | Fez | 8 (8x4096) | 0.072 | -0.0120 (0.0025) | 5, 0.060-0.074 | 8: 0.0081 / 0.0079 |
| 2026-10-13T201757 | Fez | 46 (40x1024, 6x4096) | 0.027 | -0.0009 (0.0009) | 5, 0.026-0.027 | 24: 0.0096 / 0.0081 |
| 2026-10-15T030748 | Kingston | 15 (15x2048) | 0.203 | -0.0091 (0.0024) | 6, 0.194-0.205 | 15: 0.0063 / 0.0112 |
| 2026-10-15T030903 | Kingston | 176 (120x1024, 56x4096) | 0.072 | -0.0015 (0.0005) | 6, 0.070-0.076 | 0 |
| 2026-10-15T031229 | Kingston | 929 (856x1024, 73x4096) | 0.083, 0.093 | -0.0018 (0.0005) | 6, 0.082-0.086 | 0 |
| 2026-10-15T070847 | Kingston | 7 (7x1024) | 0.435 | -0.0042 (0.0024) | 6, 0.424-0.445 | 7: 0.0186 / 0.0091 |
| 2026-10-15T070853 | Kingston | 14 (14x2048) | 0.098 | -0.0029 (0.0013) | 6, 0.093-0.098 | 105: 0.0084 / 0.0091 |

The recovered Kingston wide-control acquisition keeps its submitted circuits
and raw counts but no planning record, so its members cannot be rebuilt and
it is skipped with that reason. The Kingston 2026-10-15T031229 run executed
under two calibrations, hence two execution means.

## Readings

- **The ghost reproduces the recorded replay to sampling precision.** Eight
  runs' collections recorded their own replay distances, 206 replicas in
  all.
  - Pooled, the mean |ghost - recorded| is 0.0077 TV, against 0.0079 TV
    between two independent ghost draws of the same replicas.
  - Per run it ranges from 0.0027 to 0.0186, and the largest single
    difference is 0.044.
  - The signed mean stays within 0.003 on every run.
  - Only 2026-10-15T070847 sits clearly above its resample scatter (0.0186
    against 0.0091, over 7 replicas at 1024 shots).

  The six family collections (ripple, rank-sector, folded correction) record
  no replay distance, and for those the identity check above is the binding.
- **Calibration identity explains little of the hardware mismatch.** Across
  every retained calibration of a backend the predicted distance moves by
  0.001 to 0.032 TV, while the distance itself is 0.026 to 0.435 TV. The
  corner baseline's 0.435 is the Kingston q0/q1 readout fault, which no
  calibration carries (`hw-corner-readout-fault`).
- **The execution calibration is rarely the best predictor.** Today's
  calibration fits the old hardware data better by more than two standard
  errors on 10 of 14 runs, within two standard errors on 3, and worse on
  one (2026-10-13T032011, +0.0023, 3.3 standard errors).
- **Whether a noisier model fits better is not settled.** On the qubits
  each run used, today's mean CZ error is higher on 10 of 14 runs, and its
  change correlates with the distance change at -0.31. The readout change
  correlates at +0.32, the opposite sign. Fourteen runs cannot separate
  these. A sweep that scales the model's gate and readout errors by a
  factor per run, and finds the minimizing factor, would. The walk
  scaffold's hardware loss of 1.8 to 4.4 times the calibrated per-CZ loss
  predicts factors above one for CZ.

## Gates

- core-286: `scripts/ghost_calibrations.py --check`, the snapshot hashes,
  round trips and the execution identity of every executed member.
- core-287: `scripts/ghost_run.py --check result.json --runs
  results/live/2026-10-13T080216.451663Z` reruns that run's execution-state
  ghost on the CPU (about 7 s) and requires each execution mean within five
  standard errors. `--report result.json` must also reproduce
  [report.json](report.json) byte for byte.

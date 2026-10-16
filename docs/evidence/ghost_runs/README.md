# Ghost runs: every retained IBM job replayed under every retained calibration

`scripts/ghost_run.py` rebuilds each retained run's executed replicas from its
`isa.qpy` and `record.json` exactly as `live_run.collect` does, simulates them
under calibration snapshots from `docs/evidence/calibration/history/`
(`scripts/ghost_calibrations.py`), and compares each replica's simulated
distribution with the hardware distribution in `collect.json` by total
variation distance. [result.json](result.json) is the output of the Kaggle T4
kernel `gororoba-ghost-runs` version 2 (run directory
results/kaggle/2026-10-16T052709Z-gororoba-ghost-runs, qiskit 2.5.2,
qiskit-aer 0.17.2). The runs' raw files reached the kernel as the private
dataset `gororoba-retained-runs`, whose 659 files all matched their recorded
sha256 ([kaggle_datasets.json](kaggle_datasets.json)); the stack proof
([kaggle_hypercomplex.json](kaggle_hypercomplex.json)) reads `identical: true`.
[report.json](report.json) is `ghost_run.py --report result.json`.

Each run is simulated under three kinds of calibration state, all from the
same backend:

- **execution**: the snapshot in force at each member's PUB start. Every one
  of the 2335 executed members maps to a snapshot carrying exactly the
  calibration identity its collection recorded (gate core-286).
- **current**: the backend's calibration when the snapshots were exported.
- **other**: every remaining snapshot of the backend. The 14 calibration
  identities hold 12 distinct noise models, because two Kingston updates
  changed no gate, readout or coherence value; the report groups them.

## Result

Mean TV distance per run under the execution calibration, and the paired
per-replica difference of today's calibration from it on the same members
(standard error in parentheses):

| Run | Backend | Members | Execution TVD | Current minus execution | Other states (distinct, range) | Self-check pairs |
| --- | --- | ---: | ---: | --- | --- | ---: |
| 2026-10-11T152922 | Kingston | 9 | 0.102 | -0.0017 (0.0017) | 4, 0.094-0.103 | 29 |
| 2026-10-12T055624 | Kingston | 16 | 0.138 | -0.0181 (0.0015) | 4, 0.121-0.142 | 16 |
| 2026-10-13T020454 | Kingston | 4 | 0.186 | -0.0316 (0.0013) | 5, 0.165-0.186 | 0 |
| 2026-10-13T022433 | Kingston | 4 | 0.210 | -0.0316 (0.0013) | 5, 0.190-0.210 | 0 |
| 2026-10-13T025444 | Fez | 929 | 0.069 | -0.0032 (0.0005) | 3, 0.066-0.068 | 0 |
| 2026-10-13T032011 | Fez | 176 | 0.040 | +0.0020 (0.0007) | 3, 0.038-0.047 | 0 |
| 2026-10-13T080216 | Fez | 2 | 0.070 | -0.0136 (0.0060) | 3, 0.068-0.071 | 2 |
| 2026-10-13T083417 | Fez | 8 | 0.072 | -0.0120 (0.0025) | 3, 0.072-0.074 | 8 |
| 2026-10-13T201757 | Fez | 46 | 0.026 | -0.0015 (0.0008) | 3, 0.026-0.026 | 24 |
| 2026-10-15T030748 | Kingston | 15 | 0.203 | -0.0091 (0.0024) | 5, 0.203-0.205 | 15 |
| 2026-10-15T030903 | Kingston | 176 | 0.070 | -0.0011 (0.0005) | 5, 0.070-0.075 | 0 |
| 2026-10-15T031229 | Kingston | 929 | 0.082, 0.094 | -0.0016 (0.0005) | 4, 0.083-0.085 | 0 |
| 2026-10-15T070847 | Kingston | 7 | 0.435 | -0.0042 (0.0024) | 4, 0.424-0.445 | 7 |
| 2026-10-15T070853 | Kingston | 14 | 0.098 | -0.0029 (0.0013) | 4, 0.093-0.097 | 105 |

The recovered Kingston wide-control acquisition keeps its submitted circuits
and raw counts but no planning record, so its members cannot be rebuilt and
it is skipped with that reason. The Kingston 2026-10-15T031229 run executed
under two calibrations, hence two execution means.

## Readings

- **The ghost reproduces the recorded replay.** Where a run's collection
  recorded its own replay distances (eight runs, 206 replicas), the ghost's
  execution-state distance differs from them by at most 0.0015 TV on average
  (sd 0.004 to 0.022). The six family collections (ripple, rank-sector,
  folded correction) record no replay distance; for those the identity
  check above is the binding.
- **Calibration identity explains little of the hardware mismatch.** Across
  every retained calibration of a backend the predicted distance moves by
  0.001 to 0.032 TV, while the distance itself is 0.026 to 0.435 TV. The
  corner baseline's 0.435 is the Kingston q0/q1 readout fault no calibration
  carries (`hw-corner-readout-fault`).
- **The execution calibration is rarely the best predictor.** Today's
  calibration fits the old hardware data better by more than two standard
  errors on 10 of 14 runs, within two standard errors on 3, and worse on
  one (2026-10-13T032011, +0.0020, 2.9 standard errors).
  Whether a noisier model fits better is not settled: on the qubits each run
  used, today's mean CZ error is higher on 10 of 14 runs and its change
  correlates with the distance change at -0.31, while the readout change
  correlates at +0.31, the opposite sign. Fourteen runs cannot separate these.
  A sweep that scales the model's gate and readout errors by a factor per
  run and finds the minimizing factor would; the walk scaffold's hardware
  loss of 1.8 to 4.4 times the calibrated per-CZ loss predicts factors above
  one for CZ.

## Gates

- core-286: `scripts/ghost_calibrations.py --check`, the snapshot hashes,
  round trips and the execution identity of every executed member.
- core-287: `scripts/ghost_run.py --check result.json --runs
  results/live/2026-10-13T080216.451663Z` reruns that run's execution-state
  ghost on the CPU (about 7 s) and requires its mean distance within five
  standard errors, and `--report result.json` must reproduce
  [report.json](report.json) byte for byte.

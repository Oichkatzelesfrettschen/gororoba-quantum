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
  one of the 3275 executed members maps to a snapshot carrying exactly the
  calibration identity its collection recorded (gate core-286).
- **current**: the backend's calibration when the snapshots were exported.
- **all states**: every retained snapshot, grouped by noise content. The
  20 calibration identities the ghost covers (11 Kingston, 9 Fez) hold 16
  distinct noise models, 8 per backend, because some updates changed no
  gate, readout or coherence value.

## Result

The table gives, for each run:

- the mean TV distance under the execution calibration;
- the paired per-replica difference of today's calibration from it on the
  same members, with its standard error and the number of executed PUBs in
  parentheses. Members of one PUB share its shots, so the error is clustered
  by PUB; a run with few PUBs has few degrees of freedom;
- the mean distance over all members under each distinct state;
- the replay self-check: the number of replicas whose collection recorded
  its own replay distance, the mean |ghost - recorded|, and the mean
  |ghost - ghost'| between two independent ghost draws.

| Run | Backend | Members (shots) | Execution TVD | Current minus execution | States, range | Self-check: pairs, recorded / resampled |
| --- | --- | --- | ---: | --- | --- | --- |
| 2026-10-11T152922 | Kingston | 9 (9x4096) | 0.102 | -0.0017 (0.0013, 6 PUBs) | 8, 0.094-0.103 | 29: 0.0027 / 0.0038 |
| 2026-10-12T055624 | Kingston | 16 (16x8192) | 0.138 | -0.0181 (0.0015, 16 PUBs) | 8, 0.088-0.142 | 16: 0.0052 / 0.0036 |
| 2026-10-13T020454 | Kingston | 4 (4x8192) | 0.186 | -0.0316 (0.0013, 4 PUBs) | 8, 0.140-0.186 | 0 |
| 2026-10-13T022433 | Kingston | 4 (4x8192) | 0.210 | -0.0316 (0.0013, 4 PUBs) | 8, 0.165-0.210 | 0 |
| 2026-10-13T025444 | Fez | 929 (856x1024, 73x4096) | 0.069 | -0.0034 (0.0004, 146 PUBs) | 8, 0.063-0.069 | 0 |
| 2026-10-13T032011 | Fez | 176 (120x1024, 56x4096) | 0.041 | +0.0023 (0.0006, 36 PUBs) | 8, 0.038-0.048 | 0 |
| 2026-10-13T080216 | Fez | 2 (2x4096) | 0.070 | -0.0136 (0.0060, 2 PUBs) | 8, 0.056-0.071 | 2: 0.0101 / 0.0068 |
| 2026-10-13T083417 | Fez | 8 (8x4096) | 0.072 | -0.0120 (0.0025, 8 PUBs) | 8, 0.060-0.074 | 8: 0.0081 / 0.0079 |
| 2026-10-13T201757 | Fez | 46 (40x1024, 6x4096) | 0.027 | -0.0009 (0.0009, 46 PUBs) | 8, 0.026-0.031 | 24: 0.0096 / 0.0081 |
| 2026-10-15T030748 | Kingston | 15 (15x2048) | 0.203 | -0.0091 (0.0024, 15 PUBs) | 8, 0.194-0.205 | 15: 0.0063 / 0.0112 |
| 2026-10-15T030903 | Kingston | 176 (120x1024, 56x4096) | 0.072 | -0.0015 (0.0003, 36 PUBs) | 8, 0.070-0.085 | 0 |
| 2026-10-15T031229 | Kingston | 929 (856x1024, 73x4096) | 0.083, 0.093 | -0.0018 (0.0004, 146 PUBs) | 8, 0.082-0.086 | 0 |
| 2026-10-15T070847 | Kingston | 7 (7x1024) | 0.435 | -0.0042 (0.0024, 7 PUBs) | 8, 0.424-0.445 | 7: 0.0186 / 0.0091 |
| 2026-10-15T070853 | Kingston | 14 (14x2048) | 0.098 | -0.0029 (0.0012, 14 PUBs) | 8, 0.093-0.098 | 105: 0.0084 / 0.0091 |
| 2026-10-18T083402 | Kingston | 149 (149x32768) | 0.003 | +0.0018 (none, 1 PUB) | 8, 0.003-0.008 | 149: 0.0005 / 0.0004 |
| 2026-10-18T083403 | Kingston | 149 (149x16384) | 0.002 | +0.0022 (none, 1 PUB) | 8, 0.002-0.008 | 149: 0.0007 / 0.0006 |
| 2026-10-18T083404.226285 | Kingston | 149 (149x32768) | 0.003 | +0.0028 (none, 1 PUB) | 8, 0.003-0.009 | 149: 0.0005 / 0.0005 |
| 2026-10-18T083404.414317 | Kingston | 149 (149x16384) | 0.002 | +0.0024 (none, 1 PUB) | 8, 0.002-0.008 | 149: 0.0007 / 0.0006 |
| 2026-10-18T090603 | Kingston | 2 (2x100000) | 0.025 | -0.0025 (0.0008, 2 PUBs) | 8, 0.018-0.026 | 2: 0.0027 / 0.0020 |
| 2026-10-18T214519 | Kingston | 148 (148x32768) | 0.006 | -0.0002 (none, 1 PUB) | 8, 0.006-0.009 | 148: 0.0005 / 0.0005 |
| 2026-10-18T220218 | Kingston | 148 (148x32768) | 0.006 | -0.0001 (none, 1 PUB) | 8, 0.006-0.009 | 148: 0.0005 / 0.0005 |
| 2026-10-19T151959 | Fez | 14 (14x16384) | 0.133 | -0.0057 (0.0020, 14 PUBs) | 8, 0.128-0.133 | 14: 0.0034 / 0.0043 |
| 2026-10-19T170620 | Fez | 12 (12x8192) | 0.148 | -0.0011 (0.0023, 12 PUBs) | 8, 0.147-0.154 | 12: 0.0056 / 0.0085 |
| 2026-10-19T231043 | Fez | 6 (6x8192) | 0.084 | +0.0032 (0.0004, 6 PUBs) | 8, 0.082-0.087 | 6: 0.0035 / 0.0026 |
| 2026-10-20T031212 | Fez | 14 (14x12288) | 0.323 | +0.0027 (0.0004, 14 PUBs) | 8, 0.323-0.326 | 14: 0.0039 / 0.0044 |

The five 2026-10-18 Kingston runs and the Kingston snapshot of
2026-10-18T01:38:20-07:00 entered through `ghost_calibrations.py --add` and
`ghost_run.py --merge`, which ghosted only the 54 (run, snapshot) pairs the
coverage rule lacked on the build host's CPU (the `merged` header record):
the new runs under all nine Kingston snapshots and the nine retained
Kingston runs under the new one. Every entry the kernel wrote keeps its
bytes (core-293). The two n21 members draw from their exact
branch-resolved law (`member_law` `exact_multinomial`), since a 100000-shot
dynamic PUB costs about an hour per snapshot under Aer. The Kingston
states column counts the new snapshot, and with those 19 runs the
report's correlations read -0.52 for CZ and +0.28 for readout, CZ error
higher now on 11 of 19 (the second merge below updates them). The readings below describe the 14 kernel runs under the
2026-10-16 snapshot set; the new Kingston snapshot widens their state
ranges to as much as 0.054 TV (2026-10-12T055624, 0.088 to 0.142), beyond
the 0.001 to 0.032 the first reading states.

A second merge added the ten runs of 2026-10-18 to 2026-10-20 with two
Kingston snapshots (2026-10-18T12:19:44 and 14:27:34-07:00) and four Fez
snapshots (2026-10-19T07:44:14, 09:47:37, 15:07:33 and 19:30:42-07:00). The
four Kingston init-control runs that requested a 0 us repetition delay, or
100000 shots at 20 us, ended with every job in ERROR, so `prepare()` skips
each with `no job of the run returned shots`. The six that returned shots reproduce
their recorded replays within 0.0056 TV (mean |ghost - recorded|, 0.0005 on
the two 148-member 20 us control runs), and every retained calibration of
their backend moves their predicted distance by at most 0.008 TV. With 25
ghosted runs the report's correlations read -0.26 for CZ and +0.29 for
readout, CZ error higher now on 15 of 25.

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
  one (2026-10-13T032011, +0.0023, 3.8 standard errors). The
  2 standard error mark is a normal approximation; 2026-10-13T080216 rests
  on 2 PUBs, so its -2.3 is the weakest of the ten.
- **Whether a noisier model fits better is not settled.** On the qubits
  each run used, today's mean CZ error is higher on 10 of 14 runs, and its
  change correlates with the distance change at -0.31. The readout change
  correlates at +0.32, the opposite sign (report.json `correlations` and
  each run's `calibration_change`, taken on the qubits of the ghosted
  members, against the snapshot most of them ran under). Fourteen runs cannot separate
  these. A sweep that scales the model's gate and readout errors by a
  factor per run, and finds the minimizing factor, would. The walk
  scaffold's hardware loss of 1.8 to 4.4 times the calibrated per-CZ loss
  predicts factors above one for CZ.

## Gates

- core-293: `ghost_run.py --provenance result.json KERNEL_OUTPUT`: `result.json`
  without the runs and pairs its `merged` records name equals the kernel's
  retained output byte for byte.
- core-286: `scripts/ghost_calibrations.py --check`, the snapshot hashes,
  round trips and the execution identity of every executed member.
- core-287: `scripts/ghost_run.py --check result.json --runs
  results/live/2026-10-13T080216.451663Z,merged` reruns that run's
  execution-state ghost on the CPU and requires each execution mean within
  five standard errors, and replays the execution-snapshot ghost of every
  run a merge added, bit for bit. Before that it rebuilds every run's skip reason, members, width
  exclusions, shots and execution snapshots from the archived inputs, and
  recomputes every summary and recorded-replay agreement from the retained
  distances. `--report result.json` must reproduce
  [report.json](report.json), correlations included, byte for byte.

# Calibration drift from the retained record medians

`result.json` is `scripts/calibration_median_drift.py --out` over the 157
run records under `results/live/` (each named with its sha256). Every record
stores, for each backend it read, the calibration identity (properties
`last_update_date`) and the medians of T1, T2, readout error and CZ error over
the qubits and couplers it admitted (`live_run.BackendSnapshot.medians`). It
replaces the kernels `calibration-drift-cpu` and `calibration-drift-ghost`,
which crashed before any analysis and plotted one point per record
(`docs/evidence/simulation-notebook-audit/README.md`).

## How the medians are read

- **One row per identity.** Several records read the same calibration, so a
  record-indexed series repeats points. The series keeps one row per
  (backend, identity), ordered by the identity's timestamp; every record of
  one identity without an operator exclusion carries the same medians (the
  script stops otherwise).
- **Operator exclusions change the population.** A record made with
  `--exclude-qubits` takes its medians over the qubits it kept, as few as 1
  of 156. Within one Kingston identity (2026-10-15T15:29:07-07:00) five such
  records give median T2 from 76 to 290 us. These records are listed per
  identity and kept out of the series.
- **A new identity need not remeasure.** Of the 41 Fez steps between
  consecutive identities, 13 change the T1 median and 4 the CZ median; the
  rest repeat the previous values.
- **The snapshot reproduces the record.** For the 8 identities with both a
  retained snapshot (`docs/evidence/calibration/history/`) and a device-wide
  record, the snapshot's T1, T2 and CZ errors over that record's admitted
  qubits and couplers give its medians to 1e-12. The snapshot stores
  assignment flips rather than the service's `readout_error`; their medians
  differ by at most 3.7e-4.

## Result

Device-wide medians, 2026-10-10 to 2026-10-14 (`series_summary`):

| Backend | Identities | T1 (us) | T2 (us) | Readout error | CZ error |
| --- | ---: | --- | --- | --- | --- |
| ibm_fez | 42 | 124.5-141.0 | 89.6-101.7 | 0.0090-0.0111 | 0.00264-0.00274 |
| ibm_kingston | 40 | 242.0-248.5 | 135.9-142.3 | 0.0081-0.0110 | 0.00190-0.00221 |
| ibm_marrakesh | 38 | 151.3-180.1 | 74.0-92.8 | 0.0119-0.0175 | 0.00269-0.00286 |

The device-wide median also moves when the quality exclusions change, so
`paired_snapshot_drift` holds the population fixed. Between consecutive
retained snapshots it takes the median relative change over the qubits
(couplers) the policy admits in both, 110 to 152 qubits and 87 to 160
couplers:

- T1 by at most 7.8 percent (Fez, over 55 hours) and T2 by at most 3.1 percent;
- assignment error by at most 8.5 percent (Marrakesh, 11 hours);
- CZ error by at most 6.1 percent (Kingston, 13 hours).

Pairs less than an hour apart (Kingston 18:47 to 19:15 and 19:47 to 20:25)
changed none of the four.

The medians and snapshots carry no qubit frequency, so this drift neither
supports nor excludes a frame detuning; the frame detunings fitted to the
atlas fringes (`docs/evidence/atlas_detuning_map/`) are a separate
observable.

Gate core-326 runs `--check result.json` in normal and optimized Python: it
recomputes from the 157 named records, requires each sha256, and requires
the result byte for byte.

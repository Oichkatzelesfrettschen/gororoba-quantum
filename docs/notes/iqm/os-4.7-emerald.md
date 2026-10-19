# What IQM OS 4.7 changed on Emerald

Emerald's upgrade window closed 2026-10-19T15:00Z. This note compares the
snapshot of 2026-10-19T15:58Z ([docs/evidence/iqm/](../../evidence/iqm/))
with the pre-upgrade baseline of 06:08Z (commit 2009f0f,
[hardware-pre-4.7.md](hardware-pre-4.7.md)). Artifacts are compared up to
element order: the service returns loci, instruction lists and settings
subtrees in a different order on every read, so a byte difference alone
carries no change.

## Versions

| | baseline (06:08Z) | 15:58Z |
|---|---|---|
| IQM Server (`/about`) | 3.0.0 | 3.0.1.20261019072700 |
| Emerald, emerald:mock station control | 49.0.3 | 50.0.0 |
| Garnet, Sirius and their mocks | 49.0.3 | 49.0.3 |
| REST API | v1 (2025-09-01) | v1 (2025-09-01), no path or schema change in the server OpenAPI |

Garnet and Sirius records differ only in queue length, health timestamps
and availability windows; their upgrade follows on 2026-10-21.

## Emerald and emerald:mock

- **`measure_012`.** The dynamic quantum architecture gains the gate
  `measure_012` with implementation `constant`: a three-state readout that
  iqm-pulse 15.0.0 adds ("Add new readout operation for three state
  readout, `measure_012`", `docs/iqm-pulse/changelog.md`). Emerald
  calibrates it on QB43 alone; emerald:mock on all 54 qubits. Every other
  gate keeps its implementations, defaults, overrides and loci:
  CZ `slepian_crf` on 83 couplings and `crf_acstarkcrf` on QB44-QB50 and
  QB50-QB51, `prx` `drag_crf_sx`, `measure_fidelity` default
  `shelved_constant`.
- **Job route.** The per-QC OpenAPI adds
  `GET /api/v1/jobs/{job_id}/artifacts/sweep_results_streaming`, which the
  captured 4.7 documentation does not name.
- **Pulse schema.** The protobuf schema
  `iqm.data_definitions.common.v1.Slepian` gains `flat_width`, iqm-pulse
  15's flat middle segment of a Slepian pulse: the rise and fall together
  last `full_width - flat_width`, and the default 0.0 is the standard
  Slepian.
- **Settings.** The settings tree grows from 3133 to 3531 parameters with
  none removed and no existing value changed: `max_iir_stages` and
  `max_fir_taps` under each of 115 AWG precompensation blocks,
  `voltage_range` on 144 flux channels, and `calibration_pll_frequency`,
  `mixer_in_iq_gain_error` and `mixer_in_iq_phase_error` on each of the 8
  probe lines. emerald:mock gains the same 398.
- **Unchanged.** Channel properties, chip design records, DUTs, static
  architecture, qubit and coupler counts, job limits
  (20000 shots, 100 circuits, 30000 instructions), 0.75 credits/s and
  2400.00 credits per hour timeslot.

## Calibration

The upgrade arrived with calibration set
`51194779-d109-4536-ba98-b9346dac2b35` (metrics 13:44Z) in place of
`b306d0dc-0374-4594-9fa1-4dc45a6c4333`. Medians moved within the range one
recalibration moves them: CZ IRB 0.99632 to 0.99728, PRX RB 0.99967 to
0.99968, readout 0.98848 to 0.98845, T1 50 to 49 us, T2 15 us, T2 echo
38 us; gate and readout durations are unchanged (24, 40, 360 ns). One
calibration on each side supports no claim that the upgrade changed
quality.

## Client

iqm-client 36.0.0 from the `iqm-resonance-stack` package reads all three
QPUs through `IQMProvider(..., token=...)` across both station-control
versions; every Target holds `cz`, `r`, `measure`, `reset`, `delay`, `id`
and `if_else`, and a Bell circuit transpiles to 3 `r`, 1 `cz` and 2
`measure` (Sirius adds 2 `move`). The Qiskit Target omits `measure_012`.

The unversioned https://docs.iqm.tech/PACKAGE/ pages still served IQM OS
4.6 at 16:00Z (iqm-client 35.0.3, iqm-pulse 14.0.3 inventories), so the
`/4.7/` capture remains the current documentation.

# What IQM OS 4.7 changed on Emerald, Garnet and Sirius

Emerald's upgrade window closed 2026-10-19T15:00Z and Garnet's and Sirius's
2026-10-21T16:00Z. The Emerald sections compare the snapshot of
2026-10-19T15:58Z (commit 5ec5e8c) with the pre-upgrade baseline of 06:08Z
(commit 2009f0f, [hardware-pre-4.7.md](hardware-pre-4.7.md)); the Garnet and
Sirius section compares the snapshot of 2026-10-22T20:48Z
([docs/evidence/iqm/](../../evidence/iqm/)) with the 2026-10-19T15:58Z one. Artifacts are compared up to
element order: the service returns loci, instruction lists and settings
subtrees in a different order on every read, so a byte difference alone
carries no change.

## Versions

| | baseline (2026-10-19T06:08Z) | 2026-10-19T15:58Z | 2026-10-22T20:48Z |
|---|---|---|---|
| IQM Server (`/about`) | 3.0.0 | 3.0.1.20261019072700 | 3.0.1.20261019072700 |
| Emerald, emerald:mock station control | 49.0.3 | 50.0.0 | 50.0.0 |
| Garnet, Sirius and their mocks | 49.0.3 | 49.0.3 | 50.0.0 |
| REST API | v1 (2025-09-01) | v1 (2025-09-01), no path or schema change in the server OpenAPI | unchanged |

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

## Garnet, Sirius and their mocks

Station control moved from 49.0.3 to 50.0.0 on all four records, and each
gained the changes Emerald gained, with Emerald's native ISA, limits and
prices unchanged:

- **`measure_012`.** Implementation `constant`, calibrated on Garnet QB1,
  QB3, QB7, QB9 and QB14 and on Sirius QB2, QB4, QB8, QB17, QB20, QB21 and
  QB23; garnet:mock carries it on all 20 qubits and sirius:mock on all 24.
  Every other gate keeps its implementations, defaults and loci.
- **Job route.** Each per-QC OpenAPI adds
  `GET /api/v1/jobs/{job_id}/artifacts/sweep_results_streaming`; the route
  sets of the three QPUs now differ only in the QC name in their paths.
- **Pulse schema.** Both per-QC OpenAPIs gain the Slepian `flat_width`
  field. Garnet's calibration set carries it on all 30 `slepian_crf` CZ
  couplers at 0.0, the standard Slepian, as Emerald's does on its 83;
  Sirius's CZ and MOVE use `crf_crf`, which has no such field.
- **Settings.** Garnet's settings tree grows from 1117 to 1254 parameters
  (`voltage_range` 50, `max_fir_taps` and `max_iir_stages` 39 each,
  `calibration_pll_frequency`, `mixer_in_iq_gain_error` and
  `mixer_in_iq_phase_error` 3 each) and Sirius's from 1071 to 1215
  (`voltage_range`, `max_fir_taps` and `max_iir_stages` 48 each), with none
  removed. Sirius changes no existing value; Garnet moves every drive AWG
  and probe-line readout `trigger_delay` by +25 ns (for example
  `QB1__drive.awg.trigger_delay` 485 ns to 510 ns and
  `PL-1__readout.trigger_delay` 480 ns to 505 ns), a timing offset inside
  the control stack that leaves gate and readout durations unchanged.
- **Calibration.** Garnet's default set `9069c4ef` (metrics
  2026-10-22T16:38Z) replaces `04b7af66`: CZ IRB median 0.99425 to 0.99407,
  PRX 0.99934 to 0.99930, readout 0.97945 to 0.98040, T1 42 to 39 us. Sirius's
  set `10fb5570` (metrics 2026-10-22T05:48Z) replaces `53d7843b`: CZ IRB
  0.97400 to 0.97090, PRX 0.99902 to 0.99880, readout 0.98335 to 0.98200, T1
  26 to 28 us. As on Emerald, one calibration on each side supports no
  claim that the upgrade changed quality.
- **Unchanged.** Qubit and coupler counts, job limits (Garnet 20000 shots,
  100 circuits, 10000 instructions; Sirius 20000, 100, 75000), 0.50 and
  0.30 credits/s and the 1800.00 and 1080.00 credit timeslots.

The read-only MCP tools (`iqm_quantum_computer`, `iqm_architecture`,
`iqm_metrics`, `iqm_queue_availability`, `iqm_timeslots`, `iqm_artifact`,
`iqm_tokens`) answer for both QPUs on 50.0.0 with unchanged response shapes,
and `iqm_architecture` returns `measure_012` among their gates.

## Calibration

The upgrade arrived with calibration set
`51194779-d109-4536-ba98-b9346dac2b35` (metrics 13:44Z) in place of
`b306d0dc-0374-4594-9fa1-4dc45a6c4333`. Medians moved within the range one
recalibration moves them: CZ IRB 0.99632 to 0.99728, PRX RB 0.99967 to
0.99968, readout 0.98848 to 0.98845, T1 50 to 49 us, T2 15 us, T2 echo
38 us; gate and readout durations are unchanged (24, 40, 360 ns). One
calibration on each side supports no claim that the upgrade changed
quality.

## Client (Emerald, 2026-10-19)

iqm-client 36.0.0 from the `iqm-resonance-stack` package reads all three
QPUs through `IQMProvider(..., token=...)` across both station-control
versions; every Target holds `cz`, `r`, `measure`, `reset`, `delay`, `id`
and `if_else`, and a Bell circuit transpiles to 3 `r`, 1 `cz` and 2
`measure` (Sirius adds 2 `move`). The Qiskit Target omits `measure_012`.

The unversioned https://docs.iqm.tech/PACKAGE/ pages still served IQM OS
4.6 at 16:00Z (iqm-client 35.0.3, iqm-pulse 14.0.3 inventories), so the
`/4.7/` capture remains the current documentation.

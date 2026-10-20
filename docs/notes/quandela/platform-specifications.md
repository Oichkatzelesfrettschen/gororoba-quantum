# Quandela Cloud platform specifications

This page records the specification of each Quandela quantum processor (QPU) and of the simulators on the same API. Two sources feed it, and each figure names its source:

- **Snapshot**: [`catalogue.json`](../../evidence/quandela/catalogue.json), retrieved 2026-10-20T08:51:26+00:00, with the Belenos chip architecture carried from 2026-10-17T17:53:31+00:00 because the live record had none. The 2026-10-17 snapshot that the earlier figures come from is in commit `bfcfda2`. Gate core-502 checks the facts table in [README.md](README.md) and [AGENTS.md](../../../AGENTS.md) against this file.
- **Live processor reads**: the processor records of `qpu:belenos` and `qpu:ascella`, read on 2026-10-19 21:09 PDT (2026-10-20 04:09 UTC), retained as [Belenos](../../evidence/quandela/live-processor-qpu-belenos-2026-10-20T04-09-24Z.json) and [Ascella](../../evidence/quandela/live-processor-qpu-ascella-2026-10-20T04-09-25Z.json). Only these two records are retained from the live session. Availability counters, usage totals and the daily availability series read in the same session are not retained here; the snapshot's `statistic` and `token_usage` fields hold the 2026-10-17 values.

Calibration state, including the Belenos history, is in [calibration.md](calibration.md). Installed software and configuration are in [setup-verification.md](setup-verification.md).

## Quantum processors

### Specification

| Specification | Ascella (`qpu:ascella`) | Belenos (`qpu:belenos`) |
| --- | --- | --- |
| Modes | 12 (1 to 12) | 24 (1 to 24) |
| Maximum photons per job | 6 | 12 |
| Photon-source input modes | 0, 2, 4, 6, 8, 10 (6 inputs) | 0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22 (12 inputs) |
| Vendor description | universal: any unitary on 12 modes | universal: any unitary on 24 modes |
| Native commands | `probs`, `samples`, `sample_count`, `entropy` (see the contradictions below) | `probs`, `samples`, `sample_count`, `entropy` |
| Detector | `threshold` (spec field) | `threshold` (spec field) |
| Job time limit | 300 s | 300 s |
| Price | 1e-06 credits per shot | 1e-06 credits per shot |
| Known mitigations (snapshot) | PhotonRecycling, CompilationAveraging, DistinguishablePhoton, DetectorBalancing | the same four |
| Software (snapshot) | exqalibur 1.4.1, hardware-core 3.9.3, mosaiq-arcturus 2.1.1 | exqalibur 1.4.2, hardware-core-quandela 3.9.10, mosaiq-belenos 2.9.5 |
| Bookable time slots (snapshot) | yes | yes |

### Performance

| Figure | Ascella, snapshot 2026-10-17 (`bfcfda2`) | Ascella, live 2026-10-20 04:09 UTC | Belenos, snapshot 2026-10-17 (`bfcfda2`) | Belenos, live 2026-10-20 04:09 UTC |
| --- | --- | --- | --- | --- |
| Clock | 13.33 MHz | 13.33 MHz | 4.94 MHz | 4.94 MHz |
| Transmittance | 5.14 % | 5.25 % | 2.89 % | 6.06 % |
| HOM visibility | 87.74 % | 87.48 % | 94.2 % | 88.5 % |
| g2 | 1.8 % | 1.9 % | 1.0 % | 0.9 % |
| Maximum dark count | 1428 /s (mode 10) | 1885 /s (mode 10) | 38.2 /s (mode 5) | 412.7 /s (mode 5) |
| Transmission per input mode (t_in) | 24.99 to 36.04 % | 25.03 to 37.83 % | 1.09 to 3.05 % | 3.80 to 6.91 % |
| Transmission per output mode (t_out) | 77.32 to 111.05 % | 77.86 to 110.28 % | 4.29 to 398.55 % | 58.05 to 124.05 % |
| Status | available | available | available | running |

The Belenos snapshot column is the 2026-10-17 record in commit `bfcfda2`. The catalogue commit `af0e57c` (retrieved 2026-10-17T17:31:00+00:00) carries the same Belenos figures but reads `running`. The t_out figures are relative units, as [strategy.md](strategy.md) records them, so values above 100 % are not transmission fractions. t_in is nonzero only on the photon-source input modes.

Derived rates:

- **Ascella.** The vendor formula is Clock x Transmittance^n. From the live values, one photon gives about 700 kHz (13.33 MHz x 0.0525) and six photons give about 0.28 /s (13.33 MHz x 0.0525^6). These follow from the formula; they are not vendor-published rates.
- **Belenos.** The vendor formula is Clock x (Transmittance x Brightness)^n. No record carries a Brightness value, so no Belenos rate is computed.

### Chip architecture

Decoded from the `specs.architecture` blob of the snapshot with `decode()` in [`scripts/qd_belenos_mesh.py`](../../../scripts/qd_belenos_mesh.py).

- **Ascella.** 132 Rx couplers and 126 symbolic phase shifters. The coupler angles run from 1.4204 to 1.4739 rad, all below pi/2 (1.5708) by 0.0969 to 0.1504 rad. The MZI grouping is not established: `mzis()` raises "coupler on mode 0 closes no MZI", so this page gives no MZI count for Ascella. The live Ascella architecture of 2026-10-20 04:09 UTC is identical to the snapshot blob (same length, 3670 characters, same SHA-256 prefix).
- **Belenos.** 552 Rx couplers at calibrated angles, from 1.5573 to 1.6619 rad (-0.0135 to +0.0911 rad from pi/2), and 574 symbolic phases `phi0` to `phi573`. `mzis()` groups them as 276 MZIs of two phases each; the other 22 phases are not in an MZI. The live Belenos record of 2026-10-20 04:09 UTC has no architecture field, so the Belenos architecture is verified only through the retained catalogue and the QPU runs ([calibration.md](calibration.md)).

## Simulators

| Platform | Description | Modes | Photons | Native commands | Status (snapshot) | Bookable (snapshot) |
| --- | --- | --- | --- | --- | --- | --- |
| `sim:ascella` | Arcturus simulator | 12 | 1 to 6 | `probs`, `samples`, `sample_count` | available | no |
| `sim:belenos` | Belenos simulator | 24 | 1 to 12 | `probs`, `samples`, `sample_count`, `entropy` | available | no |
| `sim:gpu:small` | Clifford on GPU | - | 2 to 24 | `probs`, `samples`, `sample_count` | available | no |
| `sim:gpu:medium` | Clifford on GPU | - | 2 to 24 | `samples`, `sample_count` | decommissioned | no |
| `sim:sampling` | Boson sampler, Clifford and Clifford 2017 backend | - | 2 to 12 | `probs`, `samples`, `sample_count` | available | yes |
| `sim:slos` | SLOS backend | - | 2 to 12 | `probs`, `samples`, `sample_count` | available | no |

A dash means the record gives no mode count. Every simulator runs 300 s per job at 0 credits per shot. The accepted state kinds are FS, NFS and SVD for `sim:gpu:small` and `sim:sampling`, and FS, NFS, SVD, AFS and SV for `sim:slos`.

## Contradictions in the record

Each is reported as the record states it. None is resolved here.

1. **Detector.** The spec field is `threshold` for both QPUs. The Belenos documentation says some detectors are quasi number-resolving. The Ascella documentation says its detectors are not number-resolving.
2. **Ascella commands.** The Ascella documentation says the QPU "supports sampling commands: samples and sample_count." Its `available_commands` field also lists `probs` and `entropy`. The Belenos documentation names no commands.
3. **`support_multi_photon`.** It is `false` on both QPUs and on `sim:ascella` and `sim:belenos`, and `true` on `sim:gpu:small`, `sim:gpu:medium` (decommissioned), `sim:sampling` and `sim:slos`. The field is recorded as-is and not interpreted here.

## Limits and availability

- **Job limits** (snapshot `account.availability`): 1 running job, 1 queued job, 10 Quantum Toolbox jobs. The counters at the snapshot were 0, 0 and 0.
- **Account usage** (snapshot `token_usage`): no jobs at the snapshot. Later usage is not retained here; `qd_usage` reads it live.
- **Explorer availability**: each Explorer row's `statistic` field carries the daily series in the snapshot. Days after 2026-10-17 are not retained here.
- **Weekly maintenance** (snapshot Explorer row): `qpu:belenos` 2026-10-22 07:30 to 11:00 UTC (00:30 to 04:00 PDT). `qpu:ascella` lists none.

## What moved since the snapshot

Belenos moved most. Transmittance rose from 2.89 % to 6.06 % in the 04:09 UTC live read of 2026-10-20, and HOM fell from 94.2 % to 88.5 %. The 08:51 UTC catalogue of the same day reads `calibration`, with transmittance 5.97 %, HOM 82.5 %, g2 0.9 % and a maximum dark count of 298.5 /s on mode 5. Its architecture is absent from the live record, so the carried 2026-10-17 copy stands. The QPU run records hold the states between those reads, and [calibration.md](calibration.md) gives them.

Ascella moved little: transmittance 5.14 % to 5.25 % by the 04:09 UTC read, HOM 87.74 % to 87.48 %, g2 1.8 % to 1.9 %. Its maximum dark count rose from 1428 to 1885 /s on mode 10. At 08:51 UTC on 2026-10-20 the catalogue reads transmittance 5.23 %, HOM 87.28 %, g2 2.0 % and a maximum dark count of 2169 /s on mode 10.

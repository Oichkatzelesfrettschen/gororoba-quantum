# Quandela QPU calibration

This page gives the calibration state of each QPU, the history the repository retains, and what the code gates on. The specifications are in [platform-specifications.md](platform-specifications.md).

## What the records call calibration

The records carry four things under that name or its effects:

- **Platform status.** A string on each Explorer row and each processor record. `available`, `running` and `calibration` have been observed. The OpenAPI description types `status` as a free string, so the value set is observed, not specified. `calibration` is reported by the catalogue retrieved 2026-10-20 08:51 UTC for `qpu:belenos`, and [strategy.md](strategy.md) records it around 2026-10-17 22:15 UTC ("Calibration windows"); no other retained file carries it. `plan` refuses unless the Explorer row and the processor record both read `available` ([`scripts/qd_platform.py`](../../../scripts/qd_platform.py), `plan`).
- **Performance figures.** Clock, transmittance, HOM visibility, g2, dark counts per detector and transmission per mode. They change between reads. Each QPU run's `submission.json` keeps the figures as read at plan time, under `perfs_at_plan`.
- **Coupler angles.** The Rx couplers in `specs.architecture`. A recalibration changes them, and the transpiler's output for a compilation seed depends on them ([strategy.md](strategy.md): "Coupler angles change with recalibration").
- **Maintenance.** The weekly window on the Explorer row.

## Current state

The newest retained catalogue is the after-job read of the Ascella signed-coherence permuted repeat, 2026-10-24 08:35 PDT (2026-10-24 15:35:30 UTC), retained as [platform-after/catalogue.json](../../../results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/platform-after/catalogue.json) and read through the Perceval 1.3.1 and exqalibur 1.4.2 clients; both QPU workers report perceval-quandela 1.3.0 in `specs.software_versions`. Both QPU records carry `specs.architecture`, `commands`, `default_mitigations`, `known_mitigations` and `specs.type`, and `architecture_carried` is empty, so no coupler set in it is carried from an earlier read.

| | Ascella | Belenos |
| --- | --- | --- |
| Status | available | available |
| HOM visibility | 87.46 % | 88.8 % |
| g2 | 2.0 % | 1.1 % |
| Transmittance | field absent | 5.5 % |
| Maximum dark count | 5679 /s, mode 10 | 10365.3 /s, mode 5 |
| Clock | 13.33 MHz | 4.94 MHz |
| Source-connected input modes | 0, 2, 4, 6, 8, 10 | 0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22 |
| `t_out` per mode | field absent | 67.15 % to 133.81 % |
| Next maintenance (Explorer row) | none listed | 2026-10-29 08:30 to 12:00 UTC |

`t_out` above 100 % shows a relative normalization, not an absolute detector efficiency. Ascella's record has carried no transmittance field since the plan read of 2026-10-23 17:11 UTC (`ascella-mosaiq-update-order-retry`), after 5.12 % at 06:56 UTC that day (`ascella-approved-order-pilot-retry`); the earlier Ascella values below keep their dates. The before-job read of the same run (15:30:55 UTC) and both reads of job-00 (09:17:08 and 09:21:58 UTC) sit beside it in their run directories.

### Belenos read of 2026-10-25 19:04 UTC

The plan read of the single-chip teleportation rehearsal, retained as
[platform-read/catalogue.json](../../../results/quandela/cases/teleportation_rehearsal/job-00/platform-read/catalogue.json),
reports `qpu:belenos` `available` with HOM 83.8 %, g2 16.7 %, Transmittance 0.05 % and 21187.1 /s dark counts on
mode 5, at the 2026-10-24 schema and clock. Every source-connected mode's `t_in` reads 0.01 % to 0.02 %, against
2.43 % to 6.31 % at 2026-10-24 15:35:30 UTC, so the source-side transmission fell about 250-fold while `t_out`
stays between 15.88 % (mode 5) and 164.32 %. Perceval's `estimate_required_shots` answers None for the rehearsal
under these figures. Cause not identified; `qpu:ascella` in the same read reports HOM 86.8 % and g2 1.9 %.

The record holds still. The read of 2026-10-26 01:16:38 UTC,
[live-processor-qpu-belenos-2026-10-26T01-16-38Z.json](../../evidence/quandela/live-processor-qpu-belenos-2026-10-26T01-16-38Z.json),
carries a `perfs` object byte-identical to the 19:04:53 UTC read, every per-mode dark count and transmission included,
and the first read of this state is the 18:47:04 UTC catalogue of
[ascella_signed_coherence job-02](../../../results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02/platform-before/catalogue.json).
On 2026-10-24 the same object changed at each of the six two-hourly reads of the dark drift series (07:04 to 19:04 UTC,
[results/quandela/bdsc_drift_series_dark/](../../../results/quandela/bdsc_drift_series_dark/)) and held between them,
with the mode-5 dark count moving between 7326.8 /s and 18616.3 /s. Six and a half hours without a change therefore
span at least three refresh intervals, and the figures most likely describe the last calibration the service
published rather than the chip at the time of the read (inference; a changed record or a provider statement settles
it). The explorer row of the same read reports 97.89 % availability for 2026-10-26 and schedules the weekly
maintenance for 2026-10-29 08:30 to 12:00 UTC, not yet started. A plan admits the rehearsal only on a record that
models at or above F* = 0.86, so a frozen record holds the case.

### Live reads of 2026-10-20 (historical)

The table below is the state as of the live processor reads of 2026-10-19 21:09 PDT (2026-10-20 04:09 UTC), retained as [Belenos](../../evidence/quandela/live-processor-qpu-belenos-2026-10-20T04-09-24Z.json) and [Ascella](../../evidence/quandela/live-processor-qpu-ascella-2026-10-20T04-09-25Z.json). The maintenance window is the snapshot's Explorer row, which read it on 2026-10-17.

| | Ascella | Belenos |
| --- | --- | --- |
| Status | available | running |
| HOM visibility | 87.48 % | 88.5 % |
| g2 | 1.9 % | 0.9 % |
| Transmittance | 5.25 % | 6.06 % |
| Maximum dark count | 1885 /s, mode 10 | 412.7 /s, mode 5 |
| Architecture in the live record | yes, identical to the snapshot | no |
| Next maintenance (snapshot) | none listed | 2026-10-22 07:30 to 11:00 UTC |

## Belenos calibration history

The timeline combines the catalogue reads with `perfs_at_plan` from the 17 QPU runs under `results/quandela/runs/`. Times are UTC.

| Time (UTC) | Source | Status | HOM | Transmittance | g2 | Maximum dark count |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-17 17:31 | catalogue, commit `af0e57c` | running | 94.2 % | 2.89 % | 1.0 % | 38.2 /s, mode 5 |
| 2026-10-17 17:53 | catalogue, retained | available | 94.2 % | 2.89 % | 1.0 % | 38.2 /s, mode 5 |
| 2026-10-17 21:37 | QPU run, box-kite job-04 | available | 92.6 % | 2.89 % | 1.0 % | 49.2 /s, mode 5 |
| about 22:15 | strategy.md: status `calibration` observed | calibration | - | - | - | - |
| 2026-10-18 02:55 to 03:37 | 7 QPU runs | available | 57.6 % | 2.87 % | 1.1 % | 21.8 /s, mode 0 |
| 2026-10-18 04:24 to 04:26 | 2 QPU runs | available | 57.7 % | 2.80 % | 1.1 % | 31.1 /s, mode 5 |
| 2026-10-18 07:45 | 1 QPU run | available | 57.0 % | 2.87 % | 0.9 % | 42.4 /s, mode 5 |
| 2026-10-18 09:03 to 09:05 | 3 QPU runs | available | 57.9 % | 2.88 % | 1.0 % | 41.1 /s, mode 5 |
| 2026-10-18 15:53 | 1 QPU run | available | 57.6 % | 2.95 % | 1.0 % | 78.4 /s, mode 5 |
| 2026-10-18 19:05 to 19:36 | 2 QPU runs | available | 58.3 % | 2.69 % | 1.1 % | 255.4 /s, mode 5 |
| 2026-10-20 04:09 | live read, retained | running | 88.5 % | 6.06 % | 0.9 % | 412.7 /s, mode 5 |
| 2026-10-20 08:51 | catalogue, retained | calibration | 82.5 % | 5.97 % | 0.9 % | 298.5 /s, mode 5 |

In one line: HOM read 94.2 % on 2026-10-17, then 92.6 % at the first QPU run. A calibration was observed around 22:15 UTC. From the next run at 02:55 UTC on 2026-10-18 to the last run at 19:36 UTC, HOM stayed between 57.0 % and 58.3 %. The live read on 2026-10-19 is 88.5 %.

- **Couplers.** Every circuit returned by the 17 QPU runs (2026-10-17 21:37 UTC to 2026-10-18 19:36 UTC) passes `same_mesh` against the snapshot architecture: same topology and same coupler angles. The couplers did not change across those runs. After 19:36 UTC on 2026-10-18 the coupler state is unknown, because the live record returns no architecture.
- **Dark counts.** The maximum detector dark count sat on mode 0 (21.8 /s) from 02:55 to 03:37 UTC on 2026-10-18. It moved to mode 5 at 04:24 UTC, rose to 255.4 /s by 19:36 UTC, and reads 412.7 /s on the live read. The cause is not identified.
- **Transmittance.** It stayed between 2.69 % and 2.95 % in every run, then reads 6.06 % on the live read. Nothing in the retained records explains the change.

## Ascella calibration

- **Snapshot**, 2026-10-17 17:53 UTC: available; HOM 87.74 %; transmittance 5.14 %; g2 1.8 %; maximum dark count 1428 /s on mode 10.
- **Live read**, 2026-10-20 04:09 UTC: available; HOM 87.48 %; transmittance 5.25 %; g2 1.9 %; maximum dark count 1885 /s on mode 10.
- **Architecture.** Identical between the two reads (same length and SHA-256 prefix). The coupler angles run from 1.4204 to 1.4739 rad, all below pi/2.
- **History.** Nine Ascella QPU jobs, from 2026-10-21 to 2026-10-24, are retained under `results/quandela/runs/`, and [research_state.json](../../state/research_state.json) registers each. The two signed-coherence jobs completed: job-00 with 524,288 samples, job-01 with 1,048,576 ([job-00](../../../results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/README.md), [job-01](../../../results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/README.md)). Each run's `submission.json` carries `perfs_at_plan`, and its `platform-before/` and `platform-after/` catalogues extend this two-point record.
- **Correction.** The README said `qpu:ascella` "read `calibration`" at the snapshot. The retained snapshot does not support that. The same commit that added the sentence (`af0e57c`) retains an Ascella record with status `available`. The README now states the retained value.

## Gating rules: documented and enforced

| Rule | Where documented | Enforced in code |
| --- | --- | --- |
| Refuse a job unless the Explorer row and the processor record both read `available` | strategy.md, "Calibration windows" | yes: `plan` checks both |
| Refuse a mesh case whose live couplers or symbols differ from the case, and a case seeded from a retained run on `qpu:belenos` whose live couplers differ from the retained catalogue | [README.md](README.md), section "Mesh control" | yes: `live_mesh` for mesh cases, `live_architecture` for seeded cases on `qpu:belenos`; other QPU cases get no coupler check |
| Two-photon cases wait until HOM is above 90 % | strategy.md, "Design rules taken from it", item 1 | warns, does not hold: `plan` reads HOM and prints a stderr warning when it is absent or at or below 90 % |

Consequences for Belenos on 2026-10-19:

- While the Belenos Explorer row or processor record reads other than `available`, `plan` refuses, so no Belenos job can be planned. The catalogue retrieved 2026-10-20 08:51 UTC reads `calibration` on both.
- Once the status reads `available` again, every mesh or seeded case reaches `live_mesh` or `live_architecture`. With `specs.architecture` absent, both raise `PlatformError` naming the platform. The change is written and not yet run against a live record.
- Under the documented HOM rule, the live 88.5 % is below 90, so `plan` warns on a two-photon case. The warning is the only check: `plan` does not hold the case.

## Record fields Perceval reads

Perceval 1.3.1 builds `PlatformSpecs` from the processor record's `specs`
(`RPCBasedCommunicationLayer.fetch_data`), takes `type` from the record's
top level and `perfs` beside it, and reads the fields below. The live
columns are the reads of 2026-10-21 near 03:50 UTC through the MCP server
(qpu:belenos with `include_bulk`).

| Field | Consumer in Perceval 1.3.1 | Behavior when absent | qpu:belenos | sim:belenos | qpu:ascella |
|---|---|---|---|---|---|
| `commands` | `RemoteComputer.__init__` freezes the command signatures; `RPCBasedCommunicationLayer.send` builds a v2 body only when present | `CommandFactory` signatures without `compilation_seed`, and a version-1 body | absent | present | present |
| `available_commands` | `PlatformSpecs.commands` fallback, `PayloadUpdater._downgrade_to_v1` | no command resolves | present | present | present |
| `default_mitigations` | `RemoteComputer.estimate_required_shots` | read as `[]` | absent | DetectorBalancing | `[]` |
| `known_mitigations` | `RemoteComputer._use_mitigations_remotely` | read as `[]`: every requested mitigation runs locally | absent | 4 names | 4 names |
| `architecture` | `RemoteComputer._get_imperfections`, `estimate_required_shots` | the experiment's own detectors stand in | absent | present | present |
| `type` (in specs) | overwritten from the record's top-level `type` | none | absent (top level `qpu`) | present | present |
| `constraints` | `RemoteComputer` constraint check | no check | present | present | present |
| `parameters` | `RemoteComputer.parameters` | none | present | present | present |
| `pcvl_version`, `software_versions` | `qd_platform.payload_version_basis` matches them against a frozen record | commands stay absent | 1.3.0 | 1.3.0 | 1.3.0 |
| `detector`, `connected_input_modes` | `PlatformSpecs._make_architecture` from `specific_circuit` | no architecture is built | present | present | present |

A version-1 body keeps a `mitigations` key, and `PayloadUpdater._update_to_v2`
rebuilds the version-2 payload through `PayloadGenerator.from_computation`
without it, so an explicit empty list returns as "server default"; the
`qd_platform.py --self-test` round trip shows the key lost. Whether the
service's worker upgrades through that path is inferred from
perceval-quandela 1.3.0 carrying it; a sim:belenos job sent as version 1
with `mitigations = []`, whose result metadata names the processing applied,
would decide it. The missing field also breaks the request before any body
exists: `RemoteComputer` builds its command signatures once, at
construction, and the `CommandFactory` fallback's `sample_count` takes no
`compilation_seed`, so `validate_single` rejects every seeded iteration.
The frozen 2026-10-17 qpu:belenos record (`docs/evidence/bdsc/inputs/receipt.json`)
carries the server's serialized command set at the same `pcvl_version` and
`software_versions` as every live record since, byte-identical to the
sim:belenos one, and all 17 retained qpu:belenos job bodies of 2026-10-17
and 2026-10-18 are version 2. `qd_platform.payload_version_basis` therefore
installs that command set before `RemoteComputer` is built, and again just
before `send`, only when both version fields match; `plan` records the
basis, a validation failure reads as a `PlatformError`, and a policy case
refuses any body that comes out version 1. On the live record of
2026-10-20 the empty-mitigation template case then builds a version-2 body
with `mitigations = []`, and the provider-default case one without the
key.

## Open items

1. **Missing Belenos fields (historical; present again on 2026-10-24).** The 2026-10-24 catalogues of the Ascella signed-coherence runs carry all five fields for `qpu:belenos`, read through the Perceval 1.3.1 client (see [Current state](#current-state)). The `processor_record_completeness` row of `docs/evidence/bdsc/provider_contract.json` keeps its 2026-10-20 wording, because `scripts/bdsc_certificate.py` writes that file and retained replay records bind the script's digest; this item is its dated successor. The account below describes 2026-10-20 to 2026-10-21. The live records of 2026-10-20 04:09 UTC and 08:51 UTC lack `specs.architecture`, `commands`, `default_mitigations`, `known_mitigations` and `specs.type`; `available_commands` is present. The 17:31 UTC record of 2026-10-17 was `running` and carried all five, so the status does not explain the omission. An `include_bulk` read through the MCP server on 2026-10-21 near 03:50 UTC (`running`, then `calibration`) still lacks all five while `documentation` arrives, so the default read's bulk filter does not cause it; the qpu:belenos software versions equal the 2026-10-17 ones, and qpu:ascella and sim:belenos carry all five in the same hour. The omission is on the provider side and has persisted across three days and both observed statuses; its cause is a question for Quandela (`docs/evidence/bdsc/provider_contract.json`, `processor_record_completeness`). Perceval 1.3.1 tolerates each absence and changes behavior on two: `PlatformSpecs.known_mitigations` reads `[]`, so `RemoteComputer._use_mitigations_remotely` treats any explicitly requested mitigation as unknown and corrects it locally; `default_mitigations` reads `[]`, so `estimate_required_shots` assumes no server default. `commands` falls back to `CommandFactory` built from `available_commands`, whose signatures lack `compilation_seed`, and `type` comes from the record's top level. A request with `mitigations = None` therefore runs under a server default the record no longer declares (DetectorBalancing on 2026-10-17 and on sim:belenos, none on qpu:ascella), and only an explicit empty list fixes the processing from the request. A non-mesh `unitary` case needs no architecture; a mesh or seeded case stays refused until the field returns.
2. **Snapshot refreshed, Belenos chip carried.** The catalogue was refreshed on 2026-10-20 at 08:51 UTC, and `qpu:belenos` reads `calibration` in it. Its live record had no architecture, so `snapshot()` in [`scripts/qd_platform.py`](../../../scripts/qd_platform.py) carries the 2026-10-17 copy: `architecture_carried` names `qpu:belenos`, and `architecture_observed_utc` stamps it 2026-10-17T17:53:31+00:00, so the carried couplers are not presented as a read of today's chip. The refresh ran from the primary checkout, whose code predates the carry. The branch's snapshot logic, given the same responses, wrote the committed file. The facts table is unchanged, so core-502 passes.
3. **HOM rule is a warning.** `plan` warns on a two-photon case whose HOM is absent or at or below 90 %; it does not hold the case. Whether it should hold one is a decision for the user.
4. **Failure mode in `plan`.** `architecture_blob` raises `PlatformError` on a missing `specs.architecture`, in place of the earlier `KeyError`. The self-test covers the helper; no live record has exercised the path.
5. **Coupler state from 2026-10-18 19:36 UTC to 2026-10-24.** Unknown for that interval; the 2026-10-24 catalogues carry the Belenos architecture again, and a comparison of their couplers with the 2026-10-17 snapshot is not recorded here.
6. **Dark count on mode 5.** Rose from 31.1 /s at 2026-10-18 04:24 UTC to 412.7 /s at the 2026-10-20 live read, and reads 7326.8 /s at 09:21:58 UTC and 10365.3 /s at 15:35:30 UTC on 2026-10-24. Cause not identified.

## Sources

- The 2026-10-24 catalogues under `results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00/` and `results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/` (`platform-before/`, `platform-after/`).
- [`catalogue.json`](../../evidence/quandela/catalogue.json), retrieved 2026-10-20T08:51:26+00:00. The 2026-10-17 copy is in commit `bfcfda2`.
- Commit `af0e57c`: its catalogue was retrieved 2026-10-17T17:31:00+00:00, and it introduced the README sentence corrected above.
- `results/quandela/runs/*/submission.json`: `perfs_at_plan` and `platform_at_plan` for the 17 QPU runs, and the computed circuits checked with `same_mesh`.
- [strategy.md](strategy.md): "Calibration windows" and "Design rules taken from it".
- The live processor reads, retained under [`docs/evidence/quandela/`](../../evidence/quandela/) as `live-processor-qpu-belenos-2026-10-20T04-09-24Z.json` and `live-processor-qpu-ascella-2026-10-20T04-09-25Z.json`.

# Quandela QPU calibration

This page gives the calibration state of each QPU, the history the repository retains, and what the code gates on. The specifications are in [platform-specifications.md](platform-specifications.md).

## What the records call calibration

The records carry four things under that name or its effects:

- **Platform status.** A string on each Explorer row and each processor record. `available`, `running` and `calibration` have been observed. The OpenAPI description types `status` as a free string, so the value set is observed, not specified. `calibration` is reported by the catalogue retrieved 2026-10-20 08:51 UTC for `qpu:belenos`, and [strategy.md](strategy.md) records it around 2026-10-17 22:15 UTC ("Calibration windows"); no other retained file carries it. `plan` refuses unless the Explorer row and the processor record both read `available` ([`scripts/qd_platform.py`](../../../scripts/qd_platform.py), `plan`).
- **Performance figures.** Clock, transmittance, HOM visibility, g2, dark counts per detector and transmission per mode. They change between reads. Each QPU run's `submission.json` keeps the figures as read at plan time, under `perfs_at_plan`.
- **Coupler angles.** The Rx couplers in `specs.architecture`. A recalibration changes them, and the transpiler's output for a compilation seed depends on them ([strategy.md](strategy.md): "Coupler angles change with recalibration").
- **Maintenance.** The weekly window on the Explorer row.

## Current state

Live processor reads of 2026-10-19 21:09 PDT (2026-10-20 04:09 UTC), retained as [Belenos](../../evidence/quandela/live-processor-qpu-belenos-2026-10-20T04-09-24Z.json) and [Ascella](../../evidence/quandela/live-processor-qpu-ascella-2026-10-20T04-09-25Z.json). The maintenance window is the snapshot's Explorer row, which read it on 2026-10-17.

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
- **History.** No Ascella QPU run is retained, so the Ascella record has two points, not a timeline.
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

1. **Missing Belenos fields.** The live records of 2026-10-20 04:09 UTC and 08:51 UTC lack `specs.architecture`, `commands`, `default_mitigations`, `known_mitigations` and `specs.type`; `available_commands` is present. The 17:31 UTC record of 2026-10-17 was `running` and carried all five, so the status does not explain the omission. An `include_bulk` read through the MCP server on 2026-10-21 near 03:50 UTC (`running`, then `calibration`) still lacks all five while `documentation` arrives, so the default read's bulk filter does not cause it; the qpu:belenos software versions equal the 2026-10-17 ones, and qpu:ascella and sim:belenos carry all five in the same hour. The omission is on the provider side and has persisted across three days and both observed statuses; its cause is a question for Quandela (`docs/evidence/bdsc/provider_contract.json`, `processor_record_completeness`). Perceval 1.3.1 tolerates each absence and changes behavior on two: `PlatformSpecs.known_mitigations` reads `[]`, so `RemoteComputer._use_mitigations_remotely` treats any explicitly requested mitigation as unknown and corrects it locally; `default_mitigations` reads `[]`, so `estimate_required_shots` assumes no server default. `commands` falls back to `CommandFactory` built from `available_commands`, whose signatures lack `compilation_seed`, and `type` comes from the record's top level. A request with `mitigations = None` therefore runs under a server default the record no longer declares (DetectorBalancing on 2026-10-17 and on sim:belenos, none on qpu:ascella), and only an explicit empty list fixes the processing from the request. A non-mesh `unitary` case needs no architecture; a mesh or seeded case stays refused until the field returns.
2. **Snapshot refreshed, Belenos chip carried.** The catalogue was refreshed on 2026-10-20 at 08:51 UTC, and `qpu:belenos` reads `calibration` in it. Its live record had no architecture, so `snapshot()` in [`scripts/qd_platform.py`](../../../scripts/qd_platform.py) carries the 2026-10-17 copy: `architecture_carried` names `qpu:belenos`, and `architecture_observed_utc` stamps it 2026-10-17T17:53:31+00:00, so the carried couplers are not presented as a read of today's chip. The refresh ran from the primary checkout, whose code predates the carry. The branch's snapshot logic, given the same responses, wrote the committed file. The facts table is unchanged, so core-502 passes.
3. **HOM rule is a warning.** `plan` warns on a two-photon case whose HOM is absent or at or below 90 %; it does not hold the case. Whether it should hold one is a decision for the user.
4. **Failure mode in `plan`.** `architecture_blob` raises `PlatformError` on a missing `specs.architecture`, in place of the earlier `KeyError`. The self-test covers the helper; no live record has exercised the path.
5. **Coupler state after 2026-10-18 19:36 UTC.** Unknown until the architecture returns.
6. **Dark count on mode 5.** Rose from 31.1 /s to 412.7 /s between 2026-10-18 04:24 UTC and the live read. Cause not identified.

## Sources

- [`catalogue.json`](../../evidence/quandela/catalogue.json), retrieved 2026-10-20T08:51:26+00:00. The 2026-10-17 copy is in commit `bfcfda2`.
- Commit `af0e57c`: its catalogue was retrieved 2026-10-17T17:31:00+00:00, and it introduced the README sentence corrected above.
- `results/quandela/runs/*/submission.json`: `perfs_at_plan` and `platform_at_plan` for the 17 QPU runs, and the computed circuits checked with `same_mesh`.
- [strategy.md](strategy.md): "Calibration windows" and "Design rules taken from it".
- The live processor reads, retained under [`docs/evidence/quandela/`](../../evidence/quandela/) as `live-processor-qpu-belenos-2026-10-20T04-09-24Z.json` and `live-processor-qpu-ascella-2026-10-20T04-09-25Z.json`.

# Quandela platform surface, 2026-11-27

This note maps the fields the Quandela server presents today for each
Explorer platform, marks the fields that are absent or changed against the
retained catalogue, and states what each absence does to the runner. `qpu:belenos`
was unreachable from at least the retained read of 2026-11-06 18:59 UTC; its
daily availability reads 0 from 2026-11-20 to 2026-11-25, 1888.68 on
2026-11-26 and 17744.02 on 2026-11-27, so this note is the first full re-read
after the outage. The watch is one
command ([Watch](#watch)).

Evidence classes: every field and figure below is a measured read of the live
server (REST route `/api/platforms/{name}/processor`) taken on 2026-11-27 at
about 23:42 to 23:50 UTC, through the `quandela` MCP tools
(`qd_platforms`, `qd_platform` with `include_bulk`, `qd_availability`,
`qd_usage`) and, independently of the MCP server, through
`scripts/qd_surface.py read` on the compute workstation (23:49:41 UTC). The
two reads present the same field set for all six platforms the MCP read
covered. The retained side is the committed catalogue copies named in each
row. A cause stated for an absence is a hypothesis unless a row says measured.
No job was submitted, cancelled or created.

## Result

- The five worker-derived fields `specs.architecture`, `specs.commands`,
  `specs.default_mitigations`, `specs.known_mitigations` and `specs.type`
  are absent from both QPU records today. The brief's finding that
  `qpu:belenos` lacks `specs.architecture` holds, and it is a recurrence,
  not a post-outage change: the same five fields were absent from
  `qpu:belenos` on 2026-10-20 and on every retained read from 2026-10-30 to
  2026-11-07, and present on every retained read from 2026-10-23 to
  2026-10-27 ([history](#presence-history-of-the-five-fields)).
- `qpu:ascella` lost the same five fields since its last retained read
  (2026-11-07 04:28 UTC, all five present). It lost them before, on every
  retained read from 2026-10-30 to 2026-10-31. Its status reads
  `maintenance`.
- The simulators `sim:belenos` and `sim:ascella` carry all five today;
  `sim:slos` and `sim:sampling` never carried `architecture` or
  `default_mitigations`, and carry the other three.
- The performance figures moved: `qpu:belenos` HOM 88.8 % (88.2 % on
  2026-11-07), transmittance 5.37 % (5.23 %), g2 0.7 % (1.3 %), clock 4.94 MHz
  (unchanged). HOM stays below the 90 % floor of `hom_warning`, so a plan of
  a two-photon block on `qpu:belenos` prints its warning.
- Software versions on `qpu:belenos`: Perceval `pcvl_version` 1.3.0,
  `perceval-quandela` 1.3.0, `pcvl-worker` 2.1.1, `exqalibur` 1.4.2,
  `hardware-core-quandela` 3.9.10, `mosaiq-belenos` 2.9.5,
  `universalchipworker` 2.1.1; each equals the 2026-10-31 and 2026-11-07
  retained values.
- `sim:gpu:small` reads `unreachable` (availability 0 since 2026-11-05) and
  `sim:gpu:medium` reads `decommissioned` and locked; both predate the
  outage in the retained record (`sim:gpu:small` read `unreachable` on
  2026-11-07).
- The token job limits are unchanged: 1 running, 1 queued, 10 running Quantum
  Toolbox jobs, with 0 held now. The usage report reads 178 jobs (166 on
  2026-11-07).

## Explorer rows

| platform | kind | status | max s per job | credits per shot | bookable | locked | next maintenance |
|---|---|---|---|---|---|---|---|
| `qpu:belenos` | qpu | available | 300 | 1e-06 | yes | no | 2026-12-03 08:30 to 12:00 as listed in UTC under the label "Weekly maintenance", zone label Europe/Paris |
| `qpu:ascella` | qpu | maintenance | 300 | 1e-06 | yes | no | none listed |
| `sim:belenos` | simulator | available | 300 | 0 | no | no | none |
| `sim:ascella` | simulator | available | 300 | 0 | no | no | none |
| `sim:slos` | simulator | available | 300 | 0 | no | no | none |
| `sim:sampling` | simulator | available | 300 | 0 | yes | no | none |
| `sim:gpu:small` | simulator | unreachable | 300 | 0 | no | no | none |
| `sim:gpu:medium` | simulator | decommissioned | 300 | 0 | no | yes | none |

The public list (`/api/platforms/public`) names `qpu:belenos` (available)
and `qpu:ascella` (maintenance) only.

## Field surface per platform

Each cell is the value class of the field in the live record of 2026-11-27:
s string, i integer, f float, b boolean, l non-empty list, o non-empty
object, e empty value, n null, - absent. The machine-readable copy is
[platform-surface-2026-11-27.json](../../evidence/quandela/platform-surface-2026-11-27.json)
(classes and scalar figures; no architecture or documentation text).

| field | qpu:belenos | qpu:ascella | sim:belenos | sim:ascella | sim:slos | sim:sampling | sim:gpu:small | sim:gpu:medium |
|---|---|---|---|---|---|---|---|---|
| `perfs` | - | - | e | e | e | e | - | - |
| `perfs.Clock (MHz)` | f | f | - | - | - | - | - | - |
| `perfs.Dark counts (detection/s)` | l | l | - | - | - | - | - | - |
| `perfs.HOM (%)` | f | f | - | - | - | - | - | - |
| `perfs.Transmission per mode (%).t_in` | l | - | - | - | - | - | - | - |
| `perfs.Transmission per mode (%).t_out` | l | - | - | - | - | - | - | - |
| `perfs.Transmittance (%)` | f | f | - | - | - | - | - | - |
| `perfs.current_noise` | - | - | - | - | - | - | i | i |
| `perfs.g2 (%)` | f | i | - | - | - | - | - | - |
| `perfs.message` | - | - | - | - | - | - | s | s |
| `specs.architecture` | - | - | s | s | - | - | - | - |
| `specs.available_commands` | l | l | l | l | l | l | l | l |
| `specs.commands` | - | - | s | s | s | s | s | - |
| `specs.connected_input_modes` | l | l | l | l | - | - | - | - |
| `specs.constraints.accepted_state_kinds` | - | - | - | - | l | l | l | - |
| `specs.constraints.max_mode_count` | i | i | i | i | - | - | - | - |
| `specs.constraints.max_photon_count` | i | i | i | i | i | i | i | i |
| `specs.constraints.max_sample_count` | n | n | n | n | - | - | - | - |
| `specs.constraints.min_mode_count` | i | i | i | i | - | - | - | - |
| `specs.constraints.min_photon_count` | i | i | i | i | i | i | i | i |
| `specs.constraints.support_multi_photon` | b | b | b | b | b | b | b | b |
| `specs.default_mitigations` | - | - | s | s | - | - | - | - |
| `specs.description` | s | s | s | s | - | - | - | - |
| `specs.detector` | s | s | s | s | - | - | - | - |
| `specs.documentation` | s | s | s | s | s | s | e | e |
| `specs.known_mitigations` | - | - | l | l | l | l | l | - |
| `specs.min_client_version` | s | s | s | s | s | s | s | s |
| `specs.parameters.compute_physical_logical_perf` | - | - | - | - | s | s | s | - |
| `specs.parameters.final_mode_number` | s | s | s | s | - | - | - | - |
| `specs.parameters.use_photon_recycling` | s | s | s | s | - | - | - | - |
| `specs.pcvl_version` | s | s | s | s | s | s | s | s |
| `specs.pre_shots_compatibility` | b | b | b | b | - | - | - | - |
| `specs.processor_name` | s | s | s | s | - | - | - | - |
| `specs.software_versions` | - | - | - | e | - | - | - | - |
| `specs.software_versions.clifford-gpu-worker` | - | - | - | - | - | - | s | - |
| `specs.software_versions.default-simulator-worker` | - | - | - | - | s | s | - | - |
| `specs.software_versions.exqalibur` | s | s | s | - | s | s | s | - |
| `specs.software_versions.hardware-core` | - | - | s | - | - | - | - | - |
| `specs.software_versions.hardware-core-quandela` | s | s | - | - | - | - | - | - |
| `specs.software_versions.mosaiq-arcturus` | - | s | - | - | - | - | - | - |
| `specs.software_versions.mosaiq-belenos` | s | - | s | - | - | - | - | - |
| `specs.software_versions.pcvl-worker` | s | s | s | - | s | s | s | - |
| `specs.software_versions.perceval-quandela` | s | s | s | - | s | s | s | - |
| `specs.software_versions.universalchipworker` | s | s | s | - | - | - | - | - |
| `specs.type` | - | - | s | s | s | s | s | - |
| `status` | s | s | s | s | s | s | s | s |
| `type` | s | s | s | s | s | s | s | s |

`specs.architecture` is a serialized chip, `specs.commands` a serialized
Perceval command set, `specs.documentation` an HTML page. The two GPU
simulator records are the sparsest: `sim:gpu:medium` carries `perfs`,
`available_commands`, `constraints`, `documentation`,
`min_client_version` and `pcvl_version` only.

## Fields absent, empty or changed against the retained catalogue

The retained baselines are the newest committed reads: 2026-11-07 04:28 UTC
for `qpu:ascella`, `sim:belenos` and `sim:ascella`; 2026-10-31 04:26 and
2026-11-07 04:28 UTC for `qpu:belenos` (the same field set);
2026-10-20 08:51 UTC for `sim:slos` and `sim:sampling`. The `State`
column reads present, absent or changed; "first seen absent" is the earliest
retained read in the current run of absence.

| platform | field | state | last present | first seen absent | repository code that depends on it | watch |
|---|---|---|---|---|---|---|
| `qpu:belenos` | `specs.architecture` | absent | 2026-10-27 00:55 UTC (retained read); carried copy observed 2026-10-17 17:53 UTC | 2026-10-30 01:18 UTC (first ever 2026-10-20 04:09 UTC) | `architecture_blob`, `live_mesh`, `live_architecture`, `snapshot` carry, `check` | re-read and note if it returns |
| `qpu:belenos` | `specs.commands` | absent | 2026-10-27 00:55 UTC | 2026-10-30 01:18 UTC | `payload_version_basis`, `retained_commands` | re-read and note if it returns |
| `qpu:belenos` | `specs.default_mitigations`, `specs.known_mitigations` | absent | 2026-10-27 00:55 UTC | 2026-10-30 01:18 UTC | `facts_table` mitigation list; Perceval client defaults | re-read and note if they return |
| `qpu:belenos` | `specs.type` | absent | 2026-10-27 00:55 UTC | 2026-10-30 01:18 UTC | Perceval takes the type from the record's top level, which is present | re-read and note if it returns |
| `qpu:ascella` | the same five fields | absent | 2026-11-07 04:28 UTC | 2026-11-27 (this audit; earlier run of absence 2026-10-30 to 2026-10-31) | `payload_version_basis`, `retained_commands`; no mesh check reads Ascella's architecture | re-read and note if they return |
| `qpu:belenos` | `perfs.HOM (%)` | changed | 88.2 on 2026-11-07 | 88.8 today | `hom_warning` (floor 90) | track the figure |
| `qpu:belenos` | `perfs.Transmittance (%)`, `perfs.g2 (%)` | changed | 5.23 and 1.3 on 2026-11-07 | 5.37 and 0.7 today | `plan` records the perfs | track the figures |
| `qpu:belenos` | `status` | changed | `unreachable` on 2026-11-07 | `available` today | `plan` admits `available` and the statuses the case lists | none |
| `qpu:ascella` | `status` | changed | `available` on 2026-11-07 | `maintenance` today | `plan --admit-status` | re-read when the status returns to `available` |
| `qpu:ascella` | `perfs.Transmittance (%)` | present | absent on every retained read 2026-10-23 to 2026-10-27 | back by 2026-10-30 01:18 UTC; 5.56 today | [calibration.md](calibration.md) says the field has been absent since 2026-10-23 | none; that sentence is superseded here |
| `sim:gpu:small` | whole record | unchanged | `unreachable` since at least 2026-11-07 | not applicable | none | note if the status returns to `available` |
| `sim:gpu:medium` | whole record | unchanged | `decommissioned` | not applicable | none | none |

Fields that did not change: every field of `sim:belenos`, `sim:ascella`,
`sim:slos` and `sim:sampling`; `perfs.Clock (MHz)` (4.94 on
`qpu:belenos`, 13.33 on `qpu:ascella`); the `constraints` of every
platform; the documentation text of every platform. `sim:ascella` presents
`pcvl_version` 1.3.1 and an empty `specs.software_versions` object; both
equal the 2026-11-07 retained read.

## Presence history of the five fields

Retained QPU reads that carry a processor record (46 files: the catalogue,
the live-processor evidence files, the platform-before and platform-after
catalogues of the retained runs). The five fields move together in every
retained read.

- `qpu:belenos`: present 2026-10-17 17:53 UTC; absent 2026-10-20 04:09 to
  08:51 UTC; present 2026-10-23 19:54 to 2026-10-27 00:55 UTC; absent
  2026-10-30 01:18 UTC to 2026-11-07 04:28 UTC and in the live read of
  2026-11-27.
- `qpu:ascella`: present 2026-10-20 04:09 to 2026-10-27 00:55 UTC; absent
  2026-10-30 01:18 to 2026-10-31 04:26 UTC; present 2026-11-06 18:59 to
  2026-11-07 04:28 UTC; absent in the live read of 2026-11-27.

The status of `qpu:belenos` on the absent reads is `running` (eight
reads), `unreachable` (two), `calibration` (one, the 2026-10-20 08:51
catalogue) and `available` (today). Hypothesis: the server omits the worker
derived fields when it cannot read them from the QPU worker, and `available`
does not guarantee that read. Evidence against it: `qpu:belenos` reads
`available` today and `qpu:ascella` read `available` on 2026-10-30. The
provider's statement recorded in [calibration.md](calibration.md) (open item 1)
is that the fields are intended to be present and that the omission was a
cloud bug; today's read shows the omission again. The next discriminating
read is the status and field set across one weekly maintenance window
(2026-12-03).

## Consequences for the runner

No code changes in this record. Each path below fails closed on the missing
field, or recovers from a retained copy and says so.

| missing field | code path | behavior today |
|---|---|---|
| `specs.architecture` on `qpu:belenos` | `architecture_blob` in `scripts/qd_platform.py` | raises `PlatformError` ("the live record has no specs.architecture, so its couplers cannot be checked") |
| the same | `live_mesh`, called by `plan` (and by `submit`, which repeats `plan`) for a case with `gate_form` `mesh` or an `architecture` in its circuit | the plan stops; a mesh case does not submit |
| the same | `live_architecture`, called by `plan` for a case with `seeded_from`, active for `qpu:belenos` only | the plan stops; a seeded case does not submit |
| the same | `snapshot` through `architecture_provenance` | carries the retained copy into `catalogue.json`, stamps it in `architecture_observed_utc` and names `qpu:belenos` in `architecture_carried`; with no retained catalogue in the output directory it prints "no chip architecture live or retained" |
| the same | `check` | requires `qpu:belenos` to carry an architecture; it passes on a catalogue that carries the retained copy and exits otherwise, and it requires the architecture markers to name exactly the platforms that carry an architecture |
| `specs.architecture` on `qpu:ascella` | none | no mesh check decodes Ascella's chip; `snapshot` carries a retained Ascella copy too when one exists, and a stale copy then enters the catalogue under its observation stamp |
| `specs.commands` | `payload_version_basis` and `retained_commands` | restore the command set from the newest frozen record with equal `pcvl_version`, `pcvl-worker` and `perceval-quandela`; today `qpu:belenos` restores from `docs/evidence/bdsc/inputs/receipt.json` (2026-10-17) and `qpu:ascella` from `docs/evidence/quandela/catalogue.json` (2026-10-20), measured by calling `retained_commands` on today's specs. A software-version change on a worker returns `absent`, and `payload` then refuses a case that carries `mitigations` ("Perceval built a version-1 body because the platform record lacks specs.commands") |
| `specs.default_mitigations`, `specs.known_mitigations` | the Perceval client | reads both as empty lists; an explicit mitigation request is corrected locally, and a request without `mitigations` runs under a server default the record no longer declares ([calibration.md](calibration.md), open item 1) |
| `perfs.HOM (%)` | `hom_warning` | warns for two photons in one block below 90 %; today's 88.8 % warns and holds nothing |
| `status` other than the case's admitted ones | `plan` | refuses; `qpu:ascella` reads `maintenance` today |

The facts table of `scripts/qd_platform.py facts` reads `constraints`,
`connected_input_modes`, `available_commands`, `detector` and the
Explorer price columns, all present and equal to the retained catalogue, and
this record changes none of them; its mitigation line reads
`known_mitigations` of every record that carries one.

## Other consumers of the server

- The dashboard collector in gororoba-infrastructure
  (`read_quandela` in `dashboard/provider_credit_readers.py`, run by the
  `infra-collector` service) calls `qd_platform.get` on
  `/api/tokens/usage/report` only and reads `total_jobs`,
  `usage[].free_credits` and `usage[].credits`. It reads no processor
  record, so the absent fields do not reach it. Today's report sums to
  197.19 free credits over 178 jobs against its 200-credit monthly allotment
  constant; the collector's own note states that the figure is cumulative over
  the token's jobs, not the month's draw.
- The MCP `qd_availability` read answers its job limits and reports the
  platform queue as `requires-dashboard-session`: the job token cannot read
  the dashboard's queue count, so the queue depth and position of a job stay
  outside every token read.
- The MCP `qd_platform` read already states presence per field
  (`bulk_fields`, `record_fields`); the five absent fields read `absent`
  there, so an agent need not infer absence from a missing key.

## Watch

```sh
QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token" \
  "$PYTHON" scripts/qd_surface.py diff
```

The command reads the Explorer list and every processor record (read-only,
no job), compares the value class of every field against
`docs/evidence/quandela/platform-surface-2026-11-27.json` and prints the
fields that are absent, new or changed in class, then the figures that
changed. The exit status is 1 when a field differs and 0 otherwise; a figure
change alone leaves it 0. Run it after each weekly maintenance window
(Thursday 08:30 to 12:00 Europe/Paris) and before each case that needs a
mesh check. When the five QPU fields return the output lists them as `new`;
record the date here and in [calibration.md](calibration.md), then write a new
baseline with `scripts/qd_surface.py read --out FILE` under a dated name.
`scripts/qd_surface.py` has no write path other than `read --out`. A surface of schema `qd-surface-v2` adds the sha256 of every long string (`specs.architecture`, `specs.commands`), the short policy lists, the Explorer price, limit, lock and status fields and summary statistics of numeric lists; `diff` exits 1 on any field, policy, price, version or architecture change, and a baseline of the first schema reports each of those items as new until `read --out` records a v2 baseline.

## Open items

1. Cause of the intermittent omission of the five QPU fields: not settled. The
   discriminating evidence is a read taken during a maintenance window and one
   during a running job, each with the status and the field set.
2. Whether the fields return on `qpu:ascella` after its maintenance status
   ends: unread.
3. [calibration.md](calibration.md) still states that Ascella's
   transmittance has been absent since 2026-10-23; the retained reads show it
   back by 2026-10-30 and present today.

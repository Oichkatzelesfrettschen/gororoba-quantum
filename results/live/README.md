# Live-run audit records

Each directory records one `gororoba_quantum/live_run.py` invocation under its
UTC start time. `record.json` carries the schema-specific plan and lifecycle
evidence; `isa.qpy` carries the exact circuits produced by that revision.

- **Schema 5 records.** The `live-target-cross-group-fused-pubs-v1` contract
  jointly allocates same-backend, same-kind replica pools and archives the
  exact fused Runtime PUBs. Ordered manifests map each PUB to namespaced
  logical components and bind that map into recovery tags. The full experiment
  has 29 logical static entries in 14 PUBs and 9 logical dynamic entries in 6
  PUBs when each kind uses one backend. The shared reference PUB changes the
  old isolated crosstalk statistic into a global packed-workload versus global
  replica-0 comparison. Collection reconstructs each logical entry from QPY
  and fans the PUB's execution window and calibration out to every component.
- **Schema 4 records.** The `live-target-packed-replicas-v1` contract combines
  live system inventory, circuit-derived capability admission,
  degraded-hardware-filtered routing, recursive Target validation, packed
  disjoint replicas, isolated crosstalk references, per-replica variance and
  admission views, approval-gated pre-submission reselection, whole-group
  job-batch partitioning, archive integrity, immediate batch revalidation, and
  recovery identities. A changed approved plan enters `approval_required`,
  records its revised QPY digest, and sends zero Runtime jobs. `--collect`
  accepts a submitted schema-4 record only when its
  source digest and contract identifier match the checkout. The top-level
  `policy.replica_floor` records an explicit all-group override or `null`;
  `groups[].replica_floor` records the effective floor applied to each group.
- **Schema 3 packed-replica records.** Records from source commits `9384f01`,
  `b447626`, `da50fd5`, `cdb37c4`, `78a3bb7`, and `02a5b4b` carry `replicas`,
  per-replica predictions, intervals, variance, crosstalk, and admission views.
  The last two records exercise the explicit global floor and the per-group
  floor respectively. All packed schema-3 records predate system inventory,
  filtered-Target routing, approval-gated reselection, and the planned-job
  ledger.
- **Schema 3 capability-admission record.** The retained
  `2026-10-10T220438.712726Z` record from source `0205a61` carries
  `system_inventory`, `circuit_requirements`, capability decisions, and
  filtered-Target routing for 31 unreplicated base and mirror circuits. The
  record lacks replica placement, isolated references, variance views, and
  submission evidence.
- **Schema 2 records.** These records carry the earlier lifecycle, source
  digest, and commit contract. They predate system inventory and the
  planned-job ledger.
- **Legacy records.** Records without `schema_version` are historical dry-run
  plans. `--collect` rejects them.

`2026-10-11T062204.877756Z` is the first retained schema-5 fused-PUB
qualification. It comes from clean source commit `4b5dd78` with experiment
digest `7d756845d39509883131ed3453f61be6b6ce4b35fba25677a070128cf3063374`.
The explicit `--max-pending 300` dry-run bound admits Fez at 270 pending jobs
and Kingston at 183; Marrakesh reports maintenance. Kingston wins all seven
groups. The archive holds 20 uniquely named circuits and its manifests map 38
unique logical components to 14 static and six dynamic PUBs. Independent QPY
validation confirms exact manifest/register order, component ownership,
disjoint cross-group footprints, and the required joint-placement rounds. The
record stays `planned`, has no `submission` field, and sends zero QPU jobs, so
the explicit queue bound leaves default-policy submission readiness
unestablished. Record SHA-256 is
`813be4a7e9e654c5a0043c596f900d4f3537c010d5bc9a863037f77163f4ae50`; QPY
SHA-256 is
`999c9efdf2aa68113eacd0160774e9178a4d3dc46be6939991a9b1003821b7bb`.

`2026-10-10T223619.798923Z` is the first combined schema-4 qualification. The
default queue gate first rejects Fez at 194 pending jobs and Kingston at 81;
Marrakesh reports maintenance. The retained rerun sets `--max-pending 250` for
submit-free compilation and local simulation, selects Kingston for all seven
groups, and archives 38 circuits. Its QPY circuit names equal the group-member
and execution-requirement names. The record stays `planned` with `submission`
absent, so it records zero QPU jobs and does not establish default-policy
submission readiness. Record SHA-256 is
`6c347e70e0ea22de682fc935d810612287bbb984d1a3ac551b367f550d5f0f7c`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

`2026-10-10T230646.694665Z` requalifies schema 4 after the first review fixes at
source `2563b3a`, with `code_commit.sources_modified=false` and an experiment
digest that matches that source tree. The default gate records Fez at 141
pending jobs, Kingston at 92, and Marrakesh in maintenance. The retained
`--max-pending 250` rerun again selects Kingston for all seven groups, archives
the same 38 uniquely named circuits, applies the hybrid group's 0.8 floor to
nine replicas, and admits the hybrid factor and order-recovery yields in the
local noise model. Its state remains `planned`, `submission` remains absent,
and the explicit bound leaves default-policy submission readiness
unestablished. Record SHA-256 is
`8452d0751b1aa505c2abf02f19c3d17184b6f8585c39cec5c27f6c58a4a2b09b`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

`2026-10-10T232219.919322Z` requalifies the final direct-pinned-discovery source
at `584a78d`, again with clean source provenance and the matching experiment
digest. The default gate records Fez at 147 pending jobs, Kingston at 95, and
Marrakesh in maintenance. The retained 250-job-bound run has the same Kingston
selection, 38-circuit archive, nine hybrid replicas, and locally admitted
hybrid intervals. Its state remains `planned`, `submission` remains absent, and
the run records zero QPU jobs. Record SHA-256 is
`0c5b57a2db2d4e246908c5a05ccf1eadc0aa87629e2ac3950586f38ef7c55744`; QPY
SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

A dynamic member marks `duration_bound: lower_without_classical_latency`.
Schema-5 and schema-4 top-level inventory fields describe initial planning;
`revalidation[].system_inventory` describes each full pre-submission refresh;
`submission.planned_jobs[].pre_submit_revalidation` describes each immediate
batch refresh. Record, QPY, and collection writes use atomic replacement with
file and containing-directory fsync.

The two historical schema-3 contracts require shape-aware classification:

```sh
for record_path in results/live/*/record.json; do
    jq -r --arg path "$record_path" '
      if .schema_version == 5 then "schema5-fused-pubs"
      elif .schema_version == 4 then "schema4-combined"
      elif .schema_version == 3 and has("system_inventory")
        then "schema3-capability"
      elif .schema_version == 3 then "schema3-replicas"
      elif .schema_version == 2 then "schema2"
      else "legacy"
      end + " " + (.state // "planned") + " " +
      (.code_commit.head[0:7] // "-") + "  " + $path
    ' "$record_path"
done
```

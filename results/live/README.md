# Live-run audit records

Each directory records one `gororoba_quantum/live_run.py` invocation under its
UTC start time. `record.json` carries the schema-specific plan and lifecycle
evidence; `isa.qpy` carries the exact circuits produced by that revision.

- **Schema 4 records.** The `live-target-packed-replicas-v1` contract combines
  live system inventory, circuit-derived capability admission,
  degraded-hardware-filtered routing, recursive Target validation, packed
  disjoint replicas, isolated crosstalk references, per-replica variance and
  admission views, stable-pass pre-submission reselection, whole-group job-batch
  partitioning, archive integrity, immediate batch revalidation, and recovery
  identities. `--collect` accepts a submitted schema-4 record only when its
  source digest and contract identifier match the checkout. The top-level
  `policy.replica_floor` records an explicit all-group override or `null`;
  `groups[].replica_floor` records the effective floor applied to each group.
- **Schema 3 packed-replica records.** Records from source commits `9384f01`,
  `b447626`, `da50fd5`, `cdb37c4`, `78a3bb7`, and `02a5b4b` carry `replicas`,
  per-replica predictions, intervals, variance, crosstalk, and admission views.
  The last two records exercise the explicit global floor and the per-group
  floor respectively. All packed schema-3 records predate system inventory,
  filtered-Target routing, stable-pass reselection, and the planned-job ledger.
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

A dynamic member marks `duration_bound: lower_without_classical_latency`.
Schema-4 top-level inventory fields describe initial planning;
`revalidation[].system_inventory` describes each full pre-submission refresh;
`submission.planned_jobs[].pre_submit_revalidation` describes each immediate
batch refresh. Record, QPY, and collection writes use atomic replacement with
file and containing-directory fsync.

The two historical schema-3 contracts require shape-aware classification:

```sh
for record_path in results/live/*/record.json; do
    jq -r --arg path "$record_path" '
      if .schema_version == 4 then "schema4-combined"
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

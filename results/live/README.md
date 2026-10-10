# Live-run audit records

Each directory is one run of `gororoba_quantum/live_run.py`, named by its UTC
start time. `record.json` holds the schema-specific plan and lifecycle evidence;
`isa.qpy` holds the compiled circuits. Schema 3 planning records carry system
inventory, capability, circuit-requirement, exclusion, selection, and
noise-model evidence. Schema 3 submission records add revalidation, recovery,
and job-batch evidence.

- **Schema 3 records.** A record carries `schema_version: 3`, an explicit
  lifecycle `state`, `experiment_digest`, and `code_commit`. Initial planning
  stores `system_inventory`, eligible `backends` snapshots with capability
  summaries, `circuit_requirements`, capability and routing decisions in
  `selection_trace`, selected group results, and named ISA circuits. Submission
  adds one `revalidation` entry per fresh admission pass and writes the complete
  `planned_jobs` ledger before any job starts. Every batch keeps each result
  group intact and records ordered members, the exact QPY archive SHA-256,
  calibration stamps, batch indexes, effective options, and unique recovery
  tags. An immediate batch refresh records its admission evidence and budget
  before the attempt. Collection reconciles an attempted job without an id
  through one exact recovery-tag match, validates accepted jobs against the
  plan, and reports every batch and member without a recorded job id.
- **Schema 2 records.** The retained schema 2 record carries the lifecycle,
  source digest, and commit contract. The record predates `system_inventory`,
  `circuit_requirements`, `revalidation`, and the planned-job ledger.
- **Legacy records.** A record without `schema_version` was written by an
  earlier revision of live_run.py. Every such record here is a dry-run plan
  with no submitted jobs. It shows what that revision selected and simulated,
  which the design notes cite, and `--collect` rejects it.

A dynamic member marks `duration_bound: lower_without_classical_latency`.
`--collect` accepts only a submitted record whose digest matches the checkout
and otherwise names the commit to collect from. Record, QPY, and collection
writes use atomic replacement with file and directory fsync. Top-level inventory
fields describe initial planning; `revalidation[].system_inventory` describes
each full pre-submission refresh, and
`planned_jobs[].pre_submit_revalidation` describes each immediate batch refresh.

The schema field decides which kind a record is:

```sh
for r in results/live/*/record.json; do
    jq -r --arg r "$r" 'if .schema_version == 3 then "schema3 " + .state + " " + .code_commit.head[0:7] elif .schema_version == 2 then "schema2 " + .state + " " + .code_commit.head[0:7] else "legacy" end + "  " + $r' "$r"
done
```

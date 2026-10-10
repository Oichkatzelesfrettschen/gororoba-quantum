# Live-run audit records

Each directory is one run of `gororoba_quantum/live_run.py`, named by its UTC
start time. `record.json` holds the backend states, exclusions, selection
trace, noise-model predictions, and, after `--submit`, the job ids; `isa.qpy`
holds the compiled circuits.

- **Schema 3 records.** Schema 2 with every group run as packed disjoint
  replicas. Each group lists its `replicas` (placement, register prefix,
  layout score), each member its `replica_prefixes`, `replica_qubits`, and
  per-replica predictions, and the group carries pooled, per-replica,
  interval, variance, crosstalk, and admission views. `isa.qpy` holds the
  packed circuits that run. `--collect` accepts only schema 3.
- **Schema 2 records.** A record carries `schema_version: 2`, an explicit
  lifecycle `state`, `experiment_digest`, and `code_commit`. A dynamic member
  marks `duration_bound: lower_without_classical_latency`. Job-id and
  collection writes use atomic replacement. `--collect` names the commit to
  collect it from, whose digest and schema match.
- **Legacy records.** A record without `schema_version` was written by an
  earlier revision of live_run.py. Every such record here is a dry-run plan
  with no submitted jobs. It shows what that revision selected and simulated,
  which the design notes cite, and `--collect` rejects it.

The schema field decides which kind a record is:

```sh
for r in results/live/*/record.json; do
    jq -r --arg r "$r" 'if .schema_version >= 2 then "schema\(.schema_version) " + .state + " " + .code_commit.head[0:7] else "legacy" end + "  " + $r' "$r"
done
```

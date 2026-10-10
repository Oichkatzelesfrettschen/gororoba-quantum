# Live-run audit records

Each directory is one run of `gororoba_quantum/live_run.py`, named by its UTC
start time. `record.json` holds the backend states, exclusions, selection
trace, noise-model predictions, and, after `--submit`, the job ids; `isa.qpy`
holds the compiled circuits.

- **Schema 2 records.** A record carries `schema_version: 2`, an explicit
  lifecycle `state`, `experiment_digest`, and `code_commit`. A dynamic member
  marks `duration_bound: lower_without_classical_latency`. `--collect` accepts
  only a submitted record whose digest matches the checkout and otherwise
  names the commit to collect from. Job-id and collection writes use atomic
  replacement.
- **Legacy records.** A record without `schema_version: 2` was written by an
  earlier revision of live_run.py. Every such record here is a dry-run plan
  with no submitted jobs. It shows what that revision selected and simulated,
  which the design notes cite, and `--collect` rejects it.

The schema field decides which kind a record is:

```sh
for r in results/live/*/record.json; do
    jq -r --arg r "$r" 'if .schema_version == 2 then "schema2 " + .state + " " + .code_commit.head[0:7] else "legacy" end + "  " + $r' "$r"
done
```

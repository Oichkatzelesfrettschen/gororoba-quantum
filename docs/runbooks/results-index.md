# Results index

`scripts/results_index.py` answers which run, acquisition and claim a job id
or file belongs to, by joining the research registry
(`docs/state/research_state.json`), the provider run sets that
`scripts/research_state.py` validates (IBM retained-run audit, Quantum
Inspire, Quandela and IQM run directories) and the Kaggle receipt chains of
`scripts/kaggle_run.py`. It computes every answer from the retained files at
call time and writes nothing under the repository, so no index file can fall
out of date and no pull request regenerates one.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/results_index.py summary            # counts and coverage gaps
"$PYTHON" scripts/results_index.py runs --provider ibm
"$PYTHON" scripts/results_index.py job 1528724        # provider job id -> run, acquisition, claims
"$PYTHON" scripts/results_index.py claim a5-stiefel-pfaffian-reduction
"$PYTHON" scripts/results_index.py path results/live/<run>/raw/<job>/pub_00.json
"$PYTHON" scripts/results_index.py --json summary     # any subcommand as JSON
"$PYTHON" scripts/results_index.py --json ledger --summary
"$PYTHON" scripts/results_index.py ledger --markdown > /tmp/quantum-ledger.md
"$PYTHON" scripts/results_index.py --json ledger > /tmp/quantum-ledger.json
```

`summary` lists coverage gaps: provider runs no acquisition registers,
acquisitions whose run the provider adapter does not hold, acquisitions without
claim citations, and Kaggle submissions without a collection receipt. Kaggle
runs are compute sessions and enter no acquisition. Their kernels can perform
simulation or classical analysis. A job id is the provider's own identifier as text (IBM job
id, Quantum Inspire job number, Quandela and IQM job UUID); a Kaggle run's
job is its `owner/slug/version` kernel reference.

`sqlite [OUT]` writes the same relations (`runs`, `jobs`, `acquisitions`,
`claims`, `claim_qualifications`, `claim_acquisitions`, `claim_evidence`, `claim_gates`,
`claim_dependencies`) to a new SQLite file for ad hoc SQL. OUT defaults to
`${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/results-index.sqlite` and must
lie outside the repository and not exist; the file is a cache that the
command rebuilds, never a reviewed artifact, because SQLite file bytes vary
with the library version.

```sh
"$PYTHON" scripts/results_index.py sqlite /tmp/results-index.sqlite
sqlite3 /tmp/results-index.sqlite "SELECT a.provider, COUNT(*) FROM claim_acquisitions ca
  JOIN acquisitions a ON a.id = ca.acquisition GROUP BY a.provider"
```

The command reads only what the registry and adapters already validate, so
`scripts/research_state.py --check` failing makes the index refuse to build.
`tests/scripts/test_results_index.py` checks the joins on a synthetic tree
in the pull-request suite, and its `audit` test, which gate core-615 of
`ci/gates.json` runs on demand, requires on the retained tree that every acquisition owns its run, every job
resolves to its run, every claim resolves to the runs of its acquisitions,
and a build leaves `git status` unchanged. The design choice against a committed catalog
is argued in
[the catalog opposition review](../archive/reviews/2026-10-25-results-catalog-opposition.md).

## Quantum evidence ledger

`ledger` joins every registered evidence class with the tracked files under
`results/` and `docs/evidence/`. Claim evidence and documents outside
those roots also enter the census. The JSON view carries full claim records,
acquisitions, provider-qualified jobs, source-file digests and source-native
library/provenance metadata. The A5 findings retain their own statements,
statuses, field restrictions, evidence, falsifiers and supersession. The
[ledger architecture](../design/quantum-evidence-ledger.md) defines the joins
and the limits of each observation.

`ledger --markdown` renders the claim table; `--summary` reports its denominator
and gap counts. Both outputs are disposable views. The detailed JSON includes
every unclaimed acquisition, claim without a replay gate or pinned evidence,
artifact without a direct claim citation or indexed run owner, and execution
record outside indexed runs. Tracked-file presence and untracked claim-artifact
lists expose packaging gaps separately. These sets are work queues, not counts of failed
experiments: case definitions, proposals, source code and algebraic evidence
also occur in the artifact census. A run owner identifies a directory; a claim
binding identifies scientific evidence. The ledger keeps those relations apart.

Quandela discovery includes submitted directories under `cases/`, with the
same raw-reader validation as `runs/`. The ledger classifies IBM execution
candidates through the existing evidence-closure reader and reconciles known
unexecuted cancellations against the validated retention audit. Account-only
jobs remain separate from acquisitions.

`observation` resolves an RFC 6901 JSON Pointer against the exact retained file
and returns its SHA256, selected value, citing claims and containing runs:

```sh
"$PYTHON" scripts/results_index.py --json observation \
  docs/evidence/ibm-fez-actor-pilot/analysis.json --pointer /conditions/0
"$PYTHON" scripts/results_index.py job 1528724 --provider quantum_inspire
```

An empty pointer selects the whole document; `/conditions/0/n` selects one
denominator. Escape `/` inside a key as `~1` and `~` as `~0`. A missing field
fails, while a recorded zero or null retains its value. A file citation locates
potentially relevant claims; the citation alone does not establish that the
claim uses the selected field. Record-selector bindings remain in
`evidence_bindings`, with their original digest semantics.

Every query validates the registry before returning a scientific view. That
validation checks the retained evidence bindings and provider-adapter contracts;
it does not run the registered numerical replay commands. The ledger labels
replay execution `not-run-by-ledger` even when a claim has status `established`.
The SQLite `jobs.provider` column qualifies job identity, and
`claim_qualifications` preserves boundaries, assumptions and supersession for SQL
consumers. Library versions describe the retained producer environment; they
make no assertion about the environment running the query.

## Run layout and registry adapters

- results/ holds audit records: hw_estimate/ for the fixed ibm_fez compile and
  live/ for live runs.
- A collected run keeps its lossless result under `raw/<job_id>/` (every
  classical register as shot-ordered bit strings, each PUB's metadata with
  the backend scheduler table, the result metadata, the job metrics, and an
  index of sha256s), written by `--collect` before any analysis and
  recoverable with `--preserve-raw DIR` for a record collected under an
  earlier revision. collect.json is the preregistered analysis at the run's
  experiment digest; `adjudicate.py DIR` writes
  adjudication-<digest>-seed<seed>.json, a second analysis of the same raw
  files named by its own analysis digest, beside any earlier one. Raw files
  are never rewritten by a later collection or analysis.
- docs/state/research_state.json registers every acquisition under its
  provider, and scripts/research_state.py holds one adapter per provider
  whose run set the registry matches exactly: `ibm` runs come from the
  retained-run audit, `quantum_inspire` runs from the directories under
  results/quantum_inspire/runs/ (circuits matching cases.json, one raw shot
  list per completed job, failed jobs included) bound to the ledger in
  docs/evidence/quantum_inspire/usage.json. A retained run therefore enters
  the registry, with a claim citing it and a refreshed ledger or inventory,
  in the change that retains it. The ledger is account-wide, so sessions
  that share the account land runs from separate branches: `qi_platform.py
  snapshot` writes `unretained`, the sorted ids of the ledger jobs that no
  run directory of the tree holds, and research_state.py requires every
  retained job to match its ledger row, every ledger job to be retained or
  declared, and every declared job to appear in the ledger. A job both
  retained and declared passes (its run landed after the snapshot), and the
  transaction rows of declared-only jobs belong to the other branch and stay
  uncompared. A branch merging main re-snapshots only when its own retained
  jobs are missing from the snapshot it carries; a `qi-usage-v1` ledger
  declares no unretained job.
- Every run record carries the identity of the system that ran or would
  run it as data: live_run.py records each backend's `backend_version` and
  `processor_type` from its configuration in `backends`, `system_inventory`
  and each group, and the properties' `backend_version` at each execution
  start in collect.json. Calibration and Heron r2 Target snapshots carry the
  same fields; a simulation record that copies a snapshot's calibration
  stamp copies them too (`calibration_snapshot.backend_identity`) beside the
  Aer version and device, and one that names its snapshot by path reaches
  them through that file. A Kaggle submission.json records the entry's Aer
  device and every bundled snapshot's identity. The approved-record
  comparison reads none of these fields, and every checker accepts a
  record without them.

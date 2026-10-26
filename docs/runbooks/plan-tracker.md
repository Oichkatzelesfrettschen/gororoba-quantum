# Plan tracker

Planning records preserve next actions and evidence across interruptions. The
[entrance](../state/plans.md) and [complete catalogue](../state/plan-catalogue.md) are generated.
JSON under `docs/state/plans/` owns work status. Design prose explains mechanisms; the research registry
owns scientific claims; provider approval records own execution authority.

## Capture and query

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" scripts/plan_tracker.py capture target-mechanism \
  --summary 'Investigate a bounded mechanism question.' --source docs/README.md
"$PYTHON" scripts/plan_tracker.py list --limit 12
"$PYTHON" scripts/plan_tracker.py search calibration --json
"$PYTHON" scripts/plan_tracker.py show target-mechanism
```

Capture creates an inbox item. `update ID --input FILE` applies a JSON object patch; `--input -` reads stdin.
Flags `--summary`, `--scope`, `--owner`, `--next-action`, `--state` override corresponding patch fields.
`step ID STEP --input FILE` adds or patches a step. Its flags are `--action`, `--acceptance`, `--state`
and `--reason`. Identity fields stay stable. Complex changes can be edited directly in JSON.

Before moving to planned or active, provide scope, owner, next action and steps with action and acceptance.
A step is todo, doing, done or cancelled; one step per plan can be doing. Research steps describe bounded
investigations with stop conditions, rather than promising a theorem on a schedule.

`pause ID --last-result TEXT --next-action TEXT --resume-when TEXT` records a resumption capsule.
`resume ID` restores active status and its next action. A pause condition is an explicit external hold.
`list` and `search` filter by `--state`, `--kind`, `--owner`, `--blocked`; output identifies revision and
truncation count. `--json` supplies structured output. Provider operations remain outside the tracker.

## Record contract

A record needs `schema: work-plan-v1`, descriptive `id`, `kind`, `summary` (up to 300 characters),
`sources`, `state` and `reconciliation` with `status` and `note`. Reconciliation is verified, historical
or unresolved. Sources are existing repository-relative files or HTTPS references. Ignored local files
need a retained successor. Kinds are investigation, implementation, experiment and coordination.

Lifecycle is inbox, planned, active, paused or closed. Optional `related` names plans; `claims` and
`acquisitions` name existing research-registry IDs. Plan `depends_on` references plan IDs or
`plan-id/step-id`; step dependencies use local step IDs or `plan-id/step-id`. Blocking edges are acyclic;
related links may cycle. Cancelled prerequisites do not satisfy dependencies. A runnable prerequisite
later in the list remains eligible.

`step ID STEP --state done --receipt FILE` attaches a receipt with `result`, timezone-aware `observed_at`,
full Git `revision`, and a nonempty `evidence` list of objects containing `ref` and `sha256`.
The command fills `scope_sha256`, binding parent ID/scope/dependencies and the step obligation.
Hashes and revisions must come from actual observations. HTTPS references retain an observed digest but
receive no implicit freshness check; retain sanitized response files for reproducible remote observations.

An evidence `ref` names a whole file or one record of a shared JSON registry:
`FILE.json#COLLECTION/FIELD=VALUE` selects the single object of the top-level array `COLLECTION` whose string
`FIELD` equals `VALUE`, for example `docs/state/research_state.json#claims/id=a5-stiefel-universal`,
`ci/gates.json#gates/name=core-690` or `docs/SOURCES.json#pdfs/path=docs/pdf/2103.12805v1.pdf`. Its digest is
`plan_records.digest` of that object (sorted-key JSON), so edits to other records of the registry leave the
receipt fresh, while a changed, removed or duplicated record requests revalidation. Code, proofs and evidence
bundles keep whole-file references. `digest REF...` prints the digest each reference binds:

```sh
"$PYTHON" scripts/plan_tracker.py digest scripts/plan_records.py \
  'docs/state/research_state.json#claims/id=a5-stiefel-universal'
```

A revalidation moves a whole-registry reference to a record selector when it observes that record; the
receipts already recorded keep the references they observed.

A closed plan needs `disposition` (completed, cancelled, superseded) and `resolution`. Supersession also
needs `superseded_by`. All children must be terminal. Completed plans require all steps done and a plan
receipt whose digest binds the ordered step obligations. `plan_records.obligation(plan)` calculates that
digest for a closure patch. A completed falsification can record a rejected hypothesis. Artifact identity
checks and substantive scientific validation have different evidentiary roles.

Changed evidence requests revalidation while preserving historical completion. Freshness reads only the
newest receipt (latest `observed_at`) of the plan and of each step, so a revalidation reruns the acceptance
and appends a receipt over the current bytes with `step ID STEP --receipt FILE` or `update ID --receipt
FILE`; the superseded receipt stays in the record. Changed obligations
invalidate their receipts: reopen and reassess, preserving prior receipts through Git history or a
successor record. Update commands require the existing records to validate; repair malformed manual edits
before running them.

## Verification and concurrent work

```sh
"$PYTHON" scripts/plan_tracker.py render --write
"$PYTHON" scripts/plan_tracker.py check
"$PYTHON" scripts/plan_tracker.py check --base origin/main
"$PYTHON" scripts/plan_tracker.py review-merge BASE LEFT RIGHT
```

`render` alone prints the entrance. `check` validates records, the retained inventory and generated views
offline. `check --base REF` also holds each plan that the change since the merge base of REF and HEAD closes
or gives a receipt: the newest receipt of the plan and of each step must be fresh at HEAD, and each added
receipt must name a revision HEAD descends from. A receipt names the commit it observed, so the evidence file
of an observation can land in the commit after it. Plans the change leaves alone keep the warning-only
revalidation flag. Gate `core-plan-tracker` runs `check --base origin/main` and names the record directory
and both views as operands, so a pull request that edits only plan records still selects it. CLI mutations serialize through a worktree-local Git metadata lock and replace each record
atomically. Manual editing and CLI mutation of the same record require coordination; manual editors do
not acquire the CLI lock. Owners record responsibility, not a global task lock.

`review-merge` exits 1 when both branches changed the same record differently, even in disjoint fields.
Reconcile JSON by hand, regenerate Markdown, then check the combined tree. Cross-plan dependencies also
receive combined validation. Generated Markdown is a disposable projection. Follow the repository's
Codex review and merge procedure; tracker commands perform neither hosted writes nor provider operations.

## Discovery and migration

```sh
"$PYTHON" scripts/plan_tracker.py scan --all-worktrees > /tmp/planning-inventory.json
```

Discovery includes explicit plan directories, first-party designs, runbook cases and planning headings
or filenames, plus ignored local Markdown/JSON plans. Captured vendor sources, paper notes, evidence and
generated state are excluded. Candidates need human classification; arbitrary prose is not a complete
machine-readable commitment language.

Snapshots record branch, revision, dirty flag and index digest without absolute paths. Source hashes are
rechecked; changing HEAD, status, index or worktree registration rejects the scan. The
[migration inventory](../evidence/plan-reconciliation/README.md) predates the index-digest enhancement and
retains HEAD, dirty flag and exact source-file hashes. It is historical; subsequent scans are reconciled
explicitly. Unresolved findings identify missing evidence rather than silently becoming completed work.

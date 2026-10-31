# Repository layout reconciliation

This document measures the shape of the checkout at commit `a1d1743` (main, 2026-10-30), measures the
operating cost of the rules that produced that shape, and keeps only the changes that survive a
falsification pass. The first draft set a sixteen-item layout program; two external reviews refuted three
of its recommendations, and a third review together with the operating data refuted most of the rest
([Falsification](#falsification)). The work record is
[repository-layout-reconciliation](../state/plans/repository-layout-reconciliation.json); the raw numbers
are in [operating-data.md](../archive/reviews/layout-reconciliation/operating-data.md).

The repository's goal is a short path from a scientific question to interpretable evidence that is never
lost, never spends an unapproved resource, and never promotes a guess into a claim. Each rule and each CI
lane below is judged against that goal with one question: what does it catch, measured, against what it
costs, measured.

## Measured state

| Quantity | Value |
|---|---|
| Tracked files and bytes | 28,759 files, 7.03 GB (results/ 4.41 GB, docs/ 2.61 GB, code and tests 17 MB) |
| Packed history after `git gc` | 915 MB (before: 81,076 loose objects, 2.32 GiB) |
| Byte-identical duplicate content | 463 MB; 277 MB of it copies of `isa.qpy` (one archive in 15 directories) |
| Largest single bundle | `docs/evidence/a5-exceptional-fibers/working/`, 2.20 GB, bound by no ledger |
| `results/live/` run directories | 354: 61 collected runs, 144 with `UNAPPROVED_CASE.md`, 102 holding only `record.json` and `isa.qpy` |
| Gates | 633 in `ci/gates.json`: 464 `pr` tier (48 measured minutes), 169 `full` (456 minutes); 51 `pr` gates exceed the 15 s pull-request cutoff |
| Python modules in `gororoba_quantum/` | 155 flat files, 90,796 lines; `live_run.py` 8,486 lines, imports 27 modules, imported by 26 |
| Commits touching `live_run.py` or `experiments.py`, 2026-10-10 to 10-30 | 262 (13 per day) |
| Markdown under `docs/notes/` | 2,906 files, 2,413 of them vendor documentation captures |
| Instruction text per agent session | `AGENTS.md` 534 lines, `ci/AGENTS.md` 490 lines, user guide 411 lines: 92 KB before a task starts |
| Codex review loop, last 60 merged PRs | 312 review requests, 142 threads, 110 fixes; 91 requests on the 29 PRs that produced no thread; median open-to-merge 0.45 h |
| `pr.yml`, last 100 PR runs | lint 0 failures, types 0, tests 13, gates 9; whole workflow about 5 minutes |
| Nightly audit, last 9 scheduled runs | 8 failed; 16 gates red on 2026-10-30, 12 of them cited by no claim; issue #554 open since 2026-10-26 |
| Work records | 141 plans, 74 in `inbox` |

## Storage classes

Every tracked byte belongs to one of six classes, and the classes differ in the properties that decide a
home. Location decides none of them: lifecycle state decides retention, content identity decides
deduplication, access frequency decides materialization, and dependency direction decides package
boundaries.

| Class | Examples | Mutability | Binding | Growth driver |
|---|---|---|---|---|
| Code | `gororoba_quantum/`, `scripts/`, `ci/` | edited | tests, gates | authored |
| Authored prose | notes, designs, runbooks | edited | link checker | authored |
| Bound evidence | replay inputs, ledgers, collected runs | immutable | sha256 in a gate or ledger | one record per hardware run |
| Unbound producer output | dry-run records, `isa.qpy` copies, rejected candidates, working logs | immutable by rule, bound by nothing | a case document's citation at most | one record per plan; proportional to iteration |
| Third-party captures | vendor docs, PyPI metadata, PDFs | immutable, pruned by inventory | `MANIFEST.json` sha256 | vendor release cadence |
| Caches | mypy, pycache, local scratch | disposable | none | every run |

Git stores identical blobs once in history and once per checkout, so the 463 MB of duplicates cost eight
times 463 MB on the build host and zero bytes of clone. No move at the tip shrinks the 915 MB pack,
because force-push is denied; the pack is accepted as it is.

## Findings that survive

### The dry-run rule is the producer of the bulk

The merge rule in `AGENTS.md` requires a live dry run for every change to `live_run.py` or
`experiments.py`, and the dry run writes `record.json` and `isa.qpy` into a new `results/live/`
directory. Over twenty days those two files changed in 262 commits and `results/live/` gained 351
directories; per day, the count of bare dry-run directories and the count of commits touching the two
files have Pearson r = 0.87. The 277 MB of identical `isa.qpy` copies are the same compiled circuit
written once per commit of an 8,486-line module that changes thirteen times a day. The layout problem and
the governance problem have one cause: a rule that reads the live Target to test a refactor, and keeps
the bytes forever because the Target cannot be read again.

A dry run becomes bound evidence at a definite event: the approval hashes its record and archive
(`live_run.py` computes `qpy_archive_sha256` after the atomic write), collection verifies the archive
digest, and a gate or ledger cites the directory. A run none of these events reached is unbound producer
output. Its bytes stay (the existing `unretained-dry-run-logs/` precedent shows a discarded record cannot
be regenerated), and the producer stops writing them twice.

### The import graph refutes a prefix-based package cut

The names in `gororoba_quantum/` cluster by prefix (`correction_*` 14, `rank_*` 6, `msq_*` 5), and the
first draft proposed five subpackages along those prefixes. The import graph has 517 edges and two
strongly connected components of 14 modules each: the experiment family around `experiments`, and the
planning family around `live_run` (`qpu_planning`, `qpu_cases`, `runtime_contracts`,
`correction_planning`, `diagnostic_experiments`, `et_planning`, `ibm_account`,
`measurement_sequence_scatter`, `msq_envelope`, `msq_envelope_analysis`, `msq_successor_analysis`,
`readout_actor_family`, `ripple_contracts`). The five-way cut has 334 cross edges against 183 intra and
leaves 67 modules unassigned; `live_run` imports `correction_collection` while four `correction_*`
modules import `live_run`, so the proposed `hardware` and `analysis` packages would hold a cycle behind
re-export shims. Ten private names of `live_run` are imported elsewhere (`_compile` at 22 sites, `_ops`
10, `_instance_hash` 8, `_archived_entries` 8). The hub, not the directory tree, is the obstacle.

Python caches a module by its import name, so `import live_run` and `import gororoba_quantum.live_run`
over one file produce two module objects with distinct classes and registries; a package root that
admits both names breaks monkeypatching and class identity. One canonical import name is a precondition
of any package root.

### One working bundle holds a third of the tree

`docs/evidence/a5-exceptional-fibers/working/` retains 2.20 GB of Singular logs and relation files, bound
by no ledger; `docs/local/a5-failed-runs/` holds 2.1 GB of ignored siblings. Moving the bundle saves no
clone bytes and hides publicly cited diagnostic data. Its checkout cost is a per-worktree sparse
exclusion for whoever wants it; its history cost is sunk. New bulk of this class goes outside git
([Program](#program)).

## Falsification

Each claim below is a recommendation of the first draft or of one of the three reviews. The test names
the measurement; the verdict says what the data did to the claim.

| Claim | Test | Verdict |
|---|---|---|
| Moving the a5 bundle or any retained blob reduces repository cost | pack size is history; force-push denied | Refuted (Codex, Grok). History accepted. |
| Age-out of unreferenced dry runs controls growth | 16 unreferenced directories hold 54 MB of 2.2 GB | Refuted. Producer writes are the lever. |
| Five prefix-based subpackages give the code a hierarchy | import-graph scan: 334 cross edges, cycle `live_run` to `correction_*` | Refuted. Interface extraction from the hub first. |
| A package root with both import names is a safe first step | module cache keyed by name | Refuted (third review). One canonical name. |
| Vendor captures, paper notes, design prose and results-tree code need to move now | each move rebinds gates and ledgers; no measured reader cost beyond search noise | Deferred. Filtering search beats relocating 2,400 files. |
| Every authored document needs one parent entry in one map | a result is reached from its question, its experiment and its proof | Refuted (third review). Canonical content, many routes. |
| Sparse profiles are a prerequisite | 8 worktrees on one disk; link checker and `ci/gate_inputs.py` under-approximate on absent files | Deferred. Optional per worktree after the two readers test the skip-worktree bit. |
| The Codex loop's second round after operator review earns its cost | 29 of 60 PRs produced no thread and consumed 91 requests; 2.2 requests per thread | Partly refuted. First round catches (110 fixes); the repeat round on an unchanged diff is ceremony. |
| `lint` and `types` as blocking jobs catch defects | 0 failures in 100 runs | Refuted as gates; kept as 1 to 3 minute parallel jobs because they cost nothing on the critical path. |
| `tests` and `gates` as blocking jobs catch defects | 13 and 9 failures in 100 runs | Confirmed. |
| The nightly audit guards the claims | red 8 of 9 nights; 12 of 16 failing gates cited by no claim; merges continue | Refuted as a signal. A light that is always red is ignored. |
| The 15 s cutoff selects the gates that matter | 51 `pr` gates above it defer a reached regression to the red nightly | Refuted (third review, measured). Select by reach, bound by budget, report pending. |
| A live dry run proves a `live_run.py` change | r = 0.87 with bare directories; reads an uncontrolled live Target | Refuted. A retained Target snapshot tests a refactor; a live read tests a submission. |
| A retained run needs a citing claim in the retaining change | `AGENTS.md` line 503 | Refuted (third review). Capture first, interpret later. |
| 92 KB of instruction text per session is the price of safety | user guide sets 200 lines; the two repository guides hold 148 "every/never/must" sentences | Refuted. Rules derivable from the tree leave the guide. |
| 141 plan records with 74 in `inbox` track work | `core-plan-tracker` among the nightly failures; inbox never triaged | Refuted as a tracker; kept as a capture queue with a triage rule. |
| The PR lane reuses ledger passes | `ci/pr_checks.sh` line 105 passes `--affected-ledger` (selection only) | Confirmed claim, immaterial: the gates job takes 2.8 minutes. |

What survives: the producer fixes, the hub extraction, a CI whose red means something, a review loop of
one round, retention decoupled from interpretation, and an instruction file a session can afford.

## Rules the program obeys

- A retained file keeps its path and bytes while any ledger, record or digest binds it; a correction is a
  new file linked from the old one's map row.
- A producer changes before its readers depend on the new shape, and every reader accepts both shapes.
- A check blocks a merge only where the operating data shows it catching defects; a check that never
  fails runs unblocking or leaves.
- A fresh provider read is reserved for a question about the provider; a refactor is tested against a
  retained snapshot.
- Capture precedes interpretation: a run is retained the moment it exists; a claim is a later change.
- New bulk above 50 MB per file or 100 MB per bundle lives outside git history, pinned here by commit and
  sha256 manifest.

## Program

Each item names its mechanism and the check that proves it. The first three change code; the next four
change the operating rules and need the owner's word ([Decisions](#decisions-for-the-owner)).

### New runs write each circuit archive once

`live_run.py` writes the compiled archive to `results/live/archives/<sha256>.qpy` when that digest is
absent and records the digest (already in `submission.qpy_archive_sha256`) plus a relative locator. One
archive API in the run-record module returns the archive for a run directory: a historical
`run_dir / "isa.qpy"` when present, otherwise the content store by digest, with the bytes verified against
the recorded sha256 for every run. The 48 files that open the path call the API; retained directories
keep their `isa.qpy`. The allocation planner writes `shot_allocation.allocation_search.candidates` to
`allocation-search.json` beside the record and leaves each candidate's name, feasibility and estimated
seconds in the record. The same shape serves the IQM `metrics.json`, Quandela, Kaggle and `circuit.json`
duplicate groups whose records already carry a digest. Check: a dry run of an existing case produces no
`isa.qpy` in its directory and a record under 2 MB; adjudication of a retained run reads its original
bytes; the gates binding retained runs pass unchanged.

### `live_run.py` yields its record and archive I/O first

The extraction follows the private-symbol consumers: record and archive I/O (`_write_once_atomically`,
`_archived_entries`, the archive API) leaves first because the item above needs it; compilation and
placement (`_compile`, `_ops`, `_physical`, `_bind`) next, then planning and approval (`_instance_hash`),
each when an active task touches it. `live_run.py` stays the CLI and the compatibility facade under one
import name, so approval comparisons, QPY bytes, schemas and monkeypatch surfaces keep their behavior. An
import-boundary test rejects an edge from an extracted module back into `live_run` or into either
strongly connected component. Subpackages wait until a cluster has no edge into a cycle. Check per
extraction: `mypy` over the five code roots, the `tests` check, every gate the diff reaches, and a
snapshot dry run (below) byte-identical to the retained case.

### Caches and object store leave the checkout

`ci/pinned_tool.py` resolves the mypy cache root under `${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/`,
the canonical checkout registers `git maintenance start`, and the stale "18 MiB" comment in `pr.yml`
names the measured pack. Check: no `.mypy_cache` in a checkout after a gate run; loose objects under
`gc.auto` after a day of commits.

### A refactor is tested against a retained Target, a submission against the live one

The merge rule's live dry run for every change to `live_run.py` or `experiments.py` is replaced by a
snapshot dry run. `live_run.py` gains a snapshot mode that plans the retained cases against the retained
Heron r2 Targets in `docs/evidence/heron_platform/targets.json` and writes under a scratch directory,
where the `tests` check compares the record to the retained case's record field by field; today the
module has no such flag, and every dry run reads the live Target. A live read remains the rule for a
change that touches calibration admission, the approval comparison, the submission path or execution
readiness, and for every `--submit`. Check: the snapshot dry run of a retained case reproduces its
record; `results/live/` gains no directory from a refactoring PR.

### CI that reports a verdict a researcher reads

The pull-request `gates` job selects by reach and runs every reached gate inside the job budget, longest
first, reporting a reached gate it could not finish as `pending` with its name rather than deferring it
silently at 15 s; `lint` and `types` keep running in parallel but leave the branch-protection set, since
100 runs produced no failure. The nightly audit splits in two: the gates some claim cites run every night
and a red night names the claim in #554; the 12 red gates no claim cites get
a claim or leave `ci/gates.json` in one PR; the 72 gates above 60 s (456 of the 504 measured minutes)
run weekly and on a change to their inputs, through the ledger that already keys them. Check: the
scheduled audit is green or names a claim; the summary reads RUN, REUSE and PENDING per gate.

### One review round, and a second only for a changed diff

A PR gets one Codex review of its head. Threads are fixed, refuted or bounded as today; a PR whose round
produced no thread merges on green checks after the operator reads the diff; a second round is requested
only when the operator review changed code. Twenty-nine of sixty PRs would have merged one round earlier.
Check: requests per merged PR fall from 5.2 toward 2.

### Capture precedes interpretation

A retained run enters `docs/state/research_state.json` in the change that retains it, with its ledger
row, and the claim citing it is a later change; `scripts/research_state.py` requires the registry match
and no longer requires a citing claim. Check: `retain_run.sh` followed by the registry check passes on a
run with no claim.

### The instruction files and the plan inbox fit a session

The root guide keeps the rules a session cannot derive from the tree (approval before every submission,
seeds from a QRNG draw, retained bytes immutable, one review round, the snapshot dry run) in about 200
lines, with the gate machinery and the Codex mechanics in runbooks; that cut is in progress on its own
branch. The 74 `inbox` plan records are triaged to `active` or `closed` in one pass and the
`core-plan-tracker` gate leaves the nightly blocking set. Check: a new session's instruction load under
30 KB; no `inbox` record older than 14 days.

### Deferred

Vendor captures to `docs/captures/`, paper notes to `docs/notes/papers/`, design prose out of
`gororoba_quantum/`, code out of `results/live/`, a map ownership check, subpackages, scripts by provider,
sparse profiles and a public data repository for the a5 bundle are recorded here and in the first
reviews' archive, and none stands before the next experiment. Search noise from the 2,413 captures is
answered by excluding `docs/notes/*/docs/` from the default search paths of the agents' tools.

## Decisions for the owner

The four rule changes above alter the operating contract in `AGENTS.md`, so they take the owner's word
before the edit lands. Recommended: all four.

1. Snapshot dry run replaces the live dry run for refactors (the live read stays for admission,
   approval, submission and readiness changes).
2. One Codex round, with a second only when the operator review changed code.
3. Nightly audit of cited gates only; the 12 uncited red gates get a claim or leave; gates above 60 s run
   weekly and on input change.
4. Retention decoupled from a citing claim.

## Peer review

The first draft and a brief carrying every measurement went to the Codex CLI (`gpt-daybreak-blue-latest`,
medium reasoning, read-only sandbox) and the Grok Build CLI on 2026-10-30; a local Ollama model gave a
third, shallow sample. Both substantive reviews refuted the private-repository move, the timestamp-search
age-out and the prefix-based package cut, and each source claim they made was checked line by line before
adoption. The owner then supplied a third review ([review-iteration-first.md](../archive/reviews/layout-reconciliation/review-iteration-first.md))
arguing that the program made ordinary development behave like an archival release; its four source
claims (the `--affected-ledger` selection, the `--ledger-audit` nightly, the 15 s cutoff, the claim
coupling at `AGENTS.md` line 503) hold, and its unmeasured claim of procedural burden was measured in
[operating-data.md](../archive/reviews/layout-reconciliation/operating-data.md) and confirmed. The
archive holds the brief, the three reviews and the import-graph scan.

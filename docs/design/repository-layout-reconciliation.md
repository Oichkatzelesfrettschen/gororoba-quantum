# Repository layout reconciliation

This document measures the shape of the checkout at commit `a1d1743` (main, 2026-10-30), names the
mechanism behind each structural defect, and sets the program that corrects them under the repository's
own constraints: retained bytes are immutable, a move carries every reference, ledger and gate in the same
change, and a new producer changes before any reader. Every number below comes from `git ls-files`,
`git count-objects`, `ci/gates.json`, an import-graph scan of `gororoba_quantum/` and the run directories
at that commit; a later measurement replaces the number, not the mechanism. The work record is
[repository-layout-reconciliation](../state/plans/repository-layout-reconciliation.json). A peer review
of the first draft ([Peer review](#peer-review)) changed three of its recommendations; the measurements
that decided each change are in the text.

## Measured state

| Quantity | Value |
|---|---|
| Tracked files | 28,759 |
| Tracked bytes in the checkout | 7.03 GB (results/ 4.41 GB, docs/ 2.61 GB, code and tests 17 MB) |
| Packed history after `git gc` | 915 MB in 2 packs (before: 81,076 loose objects, 2.32 GiB, 13 packs of 30 MB) |
| Byte-identical duplicate content | 2,541 blob ids at more than one path, 463 MB of redundant checkout bytes |
| Largest single bundle | `docs/evidence/a5-exceptional-fibers/working/`, 956 files, 2.20 GB (31 % of tracked bytes) |
| `results/live/` run directories | 354: 61 collected runs, 144 with `UNAPPROVED_CASE.md`, 149 bare dry runs (`record.json` + `isa.qpy`) |
| `results/live/` directories nothing outside them names | 16, 54 MB, none collected |
| Gates | 633 in `ci/gates.json` (464 `pr` tier, 169 `full`), 30,206 measured seconds, 137 distinct bound paths, 32 gates reading `results/live` |
| Python modules in `gororoba_quantum/` | 155 flat files, 90,796 lines, `live_run.py` 8,486 lines and 280 definitions, no `__init__.py` |
| Import graph | 517 edges; two strongly connected components of 14 modules each; `live_run` imports 27 modules and is imported by 26 |
| Scripts in `scripts/` | 373 Python files, 259 of them inserting `gororoba_quantum/` on `sys.path` |
| Markdown files under `docs/notes/` | 2,906, of which 2,413 are vendor documentation captures (IQM 1,925, Quantum Inspire 178, qBraid 165, Open Quantum 78, Quandela 67) |
| Loose notes at `docs/notes/*.md` | 68, 28 of them the `note` of a `docs/SOURCES.json` record |
| Documentation maps | `docs/README.md` 353 links, `docs/INDEX.md` 321 links, 107 targets in both |
| Ignored bytes inside the checkout | 3.2 GB: `docs/local/` 2.34 GB (`a5-failed-runs` 2.1 GB), `docs/local_source_cache/` 318 MB, `.mypy_cache` trees 330 MB |

## Storage classes

Every tracked byte belongs to one of six classes, and the classes differ in the properties that decide a
home. Location decides none of them: lifecycle state decides retention, content identity decides
deduplication, access frequency decides materialization, and dependency direction decides package
boundaries.

| Class | Examples | Mutability | Binding | Reader | Growth driver |
|---|---|---|---|---|---|
| Code | `gororoba_quantum/`, `scripts/`, `ci/` | edited | tests, gates | humans, CI | authored |
| Authored prose | notes, designs, runbooks | edited | link checker | humans | authored |
| Bound evidence | replay inputs, ledgers, collected runs | immutable | sha256 in a gate or ledger | gates, nightly | one record per hardware run |
| Unbound producer output | dry-run records, `isa.qpy` copies, rejected candidates, working logs | immutable by rule, bound by nothing | a case document's citation at most | rarely | one record per plan; proportional to iteration |
| Third-party captures | vendor docs, PyPI metadata, PDFs | immutable, pruned by inventory | `MANIFEST.json` sha256 | capture `--check`, humans occasionally | vendor release cadence |
| Caches | mypy, pycache, local scratch | disposable | none | tools | every run |

Git stores identical blobs once in history and once per checkout in the working tree, so the 463 MB of
duplicates cost eight times 463 MB on a build host with eight worktrees and zero bytes of clone. The pack is
915 MB for a 7 GB tree because the text compresses about 8:1. The repository therefore has two sizes with
two levers: clone size (history, which no move at the tip reduces because force-push is denied) and
checkout size (working tree times worktrees, which sparse materialization reduces without moving bytes).

## Findings

### Dry runs have lifecycle states, not a storage class

The submission rule writes a record for every plan, and 293 of the 354 live directories are dry runs or
unapproved cases. A dry run becomes bound evidence at a definite event: the approval hashes its record and
archive (`live_run.py` computes `qpy_archive_sha256` after the atomic write and the approved-record
comparison reads the record digest), collection verifies the archive digest before interpreting circuits,
and a gate or ledger cites the directory. A run none of these events reached is unbound producer output,
and declaring it immutable adds no integrity. The first draft counted "referenced" directories by searching
every file for the run timestamp (338 of 354) and proposed aging the rest out; the search is the wrong root
set, because a name in a Markdown file is neither a digest nor a promise of future use, and the existing
log-only directory already records the loss: a record discarded this way cannot be regenerated, since the
dry run read the live Target at the moment it ran (`results/live/unretained-dry-run-logs/README.md`).

The producer, not deletion, is the lever on growth:

- `isa.qpy` is written into every run directory, and the same compiled archive recurs across a day's
  dry runs: 277 MB of the 463 MB redundant bytes are identical copies (one archive appears in 15
  directories). The record already binds the archive by content in `submission.qpy_archive_sha256`, and
  48 files name `run_dir / "isa.qpy"`.
- `record.json` totals 932 MB over 351 files. In the eleven records above 1 MB the key
  `shot_allocation.allocation_search.candidates` carries every rejected allocation candidate with its full
  job and observable tables: 20.3 MB of a 24 MB record, 81 MB across the tree.

### One working bundle holds a third of the tree

`docs/evidence/a5-exceptional-fibers/working/` retains the Singular logs, relation files and split
`.part` files of the exceptional-fiber computations: 2.20 GB, with 107 MB duplicated between `runs/` and
`distribute/out/`. No ledger binds a file under `working/`; the only gate text naming it excludes it from
Ruff and mypy; no Markdown outside the bundle links into it. Its README states the role: diagnostic working
data that enters the claim record only through the kernel-attachments ledger, and the findings note rests
on it. `docs/local/a5-failed-runs/` holds a further 2.1 GB of ignored siblings. Moving the bundle to the
private documents repository, the first draft's recommendation, saves no clone bytes (the blobs stay in
history) and makes publicly cited diagnostic data less reviewable; the sound destinations are a sparse
exclusion in ordinary worktrees now and a public data repository for artifacts of this class in future.

### The import graph refutes a prefix-based package cut

`gororoba_quantum/` is a directory of 155 modules imported by bare name: 136 gates run with
`cwd: gororoba_quantum`, tests import `live_run` and `diagnostic_experiments` unqualified, and 259 scripts
insert the directory on `sys.path`. The names cluster by prefix (`correction_*` 14, `rank_*` 6, `msq_*` 5,
`kernel_*` 5, `et_*` 5), and the first draft proposed five subpackages along those prefixes. The import
graph says otherwise:

| Measurement | Value |
|---|---|
| Strongly connected component A (14 modules) | `experiments`, `coherence_probes`, `conditional_ramsey`, `crossed_tile_template`, `diagnostic_controls`, `idle_penalty`, `idle_readout`, `maximal_experiments`, `primorial_campaigns`, `qet_ladder`, `qubit_baseline`, `rank_sector_experiments`, `ripple_experiments`, `star_ramsey` |
| Strongly connected component B (14 modules) | `live_run`, `qpu_planning`, `qpu_cases`, `runtime_contracts`, `correction_planning`, `diagnostic_experiments`, `et_planning`, `ibm_account`, `measurement_sequence_scatter`, `msq_envelope`, `msq_envelope_analysis`, `msq_successor_analysis`, `readout_actor_family`, `ripple_contracts` |
| Edges inside the proposed five packages | 183 |
| Edges across them | 334, with mutual pairs hardware-analysis (22 and 27), hardware-algebra, hardware-providers |
| Modules the prefix rule leaves unassigned | 67 |
| Private names of `live_run` imported elsewhere | `_compile` (22 sites), `_ops` (10), `_instance_hash` (8), `_archived_entries` (8), `_recovery_tags`, `_distribution`, `_write_once_atomically`, `_physical`, `_bind`, `_gate_time_view` |

`live_run.py` imports `correction_collection` and four `correction_*` modules import `live_run`, so the
proposed `hardware` and `analysis` packages would hold a cycle behind re-export shims. Directories drawn
along prefixes would tidy the monolith without changing its dependency direction. Thirteen Markdown design
documents (`DESIGN_NOTES.md`, `QPU_EXECUTION_ROADMAP.md`, `CLAIM_BOUNDARIES.md` and ten more) also live in
the code directory and are mapped from `docs/README.md`.

### Code and prose live in the results tree

`results/live/` holds, beside the run directories, three Python files (`folded_raw_analysis.py`,
`test_folded_raw_analysis.py`, `verify_source_closure.py`), 26 case and findings documents in capitals
(`PRIMORIAL_COHERENCE_CASE_3.md`, `N21_ORBIT_RCA.md`), registries (`qpu-job-inventory.json`,
`qpu-coordination.json`) and a `local-audit-provenance/` tree. Gates bind several of these paths, so each
move rebinds its gate in the same change.

### Documentation navigation has two maps and three catalogs

`docs/README.md` and `docs/INDEX.md` share 107 link targets; `docs/state/plans.md`,
`docs/state/plan-catalogue.md`, `docs/state/RESEARCH_STATE.md` and `docs/state/QPU_RUN_CENSUS.md` each
catalog a different cut of the same work; the root `README.md` is 639 lines. Under `docs/notes/`, 22 of the
68 loose files are paper notes named by arXiv or old-style identifiers (`2102.01682.md`, `math-0511691.md`)
beside `docs/notes/papers/`, which holds 237 notes of the same kind; the source verifier accepts a `note`
path at `docs/notes/`, `docs/notes/papers/` or `docs/notes/quantum-tools/`, so the move is a registry edit.
The remaining 46 are research notes of the kind `docs/notes/topics/` owns. The link checker proves that
every link resolves; nothing checks that a document has one parent entry.

### Vendor captures sit beside authored notes

The provider capture scripts (`scripts/capture_iqm_docs.py` and five siblings) retain every page of a
vendor's documentation as Markdown under `docs/notes/<provider>/docs/`, bound by a `MANIFEST.json` of
sha256 digests and pruned when the inventory changes. These 2,413 files are retained source bytes with a
checker, which is the `docs/evidence/` contract, placed where the map and the readers expect authored
guides. The 83 % of `docs/notes/` Markdown that is capture output is the overload a reader meets.

### Stray top-level entries

| Entry | State | Disposition |
|---|---|---|
| `error.log` | untracked Codex CLI log carrying an account identifier | moved to the trash on 2026-10-30 |
| `cd/` | empty untracked directory | moved to the trash on 2026-10-30 |
| `plans/` | 4 tracked files, superseded by `docs/state/plans/`; cited by plan-reconciliation evidence | archive under `docs/archive/` when its citing ledgers are rebound |
| `literature -> docs` | tracked symbolic link, 51 files cite `literature/` paths including `docs/SOURCES.json` | keep until every citation reads `docs/` |
| `formalization.yaml` | tracked index of `proofs/` in the mathlib-initiative schema | keep |

### Object store, caches and a stale assumption in CI

81,076 loose objects (2.32 GiB) sat beside 13 small packs; `git gc` on 2026-10-30 took 5.5 minutes and
left 2 packs of 915 MB. Each worktree checkout carries the full 7 GB tree, and `ci/pinned_tool.py` keys a
mypy cache directory under the working directory, so eight checkouts on the build host hold eight copies
of the tree and their own caches. The user-level rule places build trees and caches under
`${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/`. The `gates` job of `pr.yml` fetches the whole history
under a comment that reads "about 18 MiB packed"; the pack is 915 MB, and the fetch sits inside an
8-minute job budget.

## Rules the program obeys

- A retained file keeps its path and bytes while any ledger, record or digest binds it; a correction is a
  new file that the old one's map row links.
- A move is `git mv` plus every reference, ledger entry and gate command in one commit, proven by
  `scripts/check_markdown_links.py`, `ci/run_gates.py --affected-by` on the branch diff and the `sources`
  suite.
- A producer changes before its readers depend on the new shape, and every reader accepts both shapes: a
  run collected under an earlier revision replays unchanged.
- Retention follows lifecycle state, recorded in a digest-bound ledger, never a file's location or a
  text search for its name.
- Materialization follows access: a worktree holds what its task reads; the nightly audit holds
  everything.
- A package boundary follows dependency direction, proven by an import-graph check that rejects a reverse
  edge; a directory move that preserves a cycle is refused.
- One home per fact, one parent entry per document. A second area that needs the fact gets a link.
- Deletion of tracked bytes and relocation of bytes to another repository are owner decisions.

## Program

Each item names its mechanism and the check that proves it. Items that need no owner decision proceed in
their own pull requests in the order listed; the items under the owner's decisions wait for the answer.

### Caches and object store leave the checkout

`ci/pinned_tool.py` resolves the mypy cache root to `${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/mypy/`
keyed by the checkout path, and keeps the per-invocation hash directory that protects concurrent gates.
`git maintenance start` registers the canonical checkout (maintenance is per repository, so the linked
worktrees share it) for the incremental schedule: commit-graph and prefetch hourly, loose-objects and
incremental-repack daily, pack-refs weekly. The stale "18 MiB" comment in `pr.yml` is replaced by the
measured pack size and the fetch is timed. Check: `du -s .mypy_cache` reads zero after a gate run, and
`git count-objects -v` reports a loose count under `gc.auto` after a day of commits.

### Sparse materialization profiles for worktrees

`git sparse-checkout` stores its rules per worktree once `set` has enabled `extensions.worktreeConfig`
(already on in this repository), so each of the eight worktrees can hold a different directory set over one
shared object database. Cone mode lists directories to include and cannot exclude one nested directory
without naming its 163 sibling bundles, so the profiles use non-cone patterns with negations, the shape the
link checker's excluded prefixes already have: a code profile is `/*` with `!/results/` and
`!/docs/evidence/a5-exceptional-fibers/working/`; a documentation profile adds `!/docs/captures/`; an
evidence-review profile keeps `results/` and drops the working bundle; the full-audit profile is the whole
tree. `pr.yml` checks out the 7 GB tree inside its 8-minute jobs; `actions/checkout` accepts `filter:
blob:none` and `sparse-checkout`, so the lint, types and tests jobs materialize the code profile and the
gates job hydrates what the reached gates declare. `ci/fetch_open_gororoba.sh` already implements the
cone-mode, blobless, exact-commit pattern for an external checkout. Three readers need a change first,
because an excluded tracked file is listed by `git ls-files` but absent on disk: the link checker drops
absent Markdown from its checked set and fails on a fragment link into an absent target
(`scripts/check_markdown_links.py`), and the gate selector drops tracked files absent from disk and stops
its import traversal at a missing source (`ci/gate_inputs.py`), which under-approximates reach. Each
gains a skip-worktree test (`git ls-files -t` marks the entry `S`) and either hydrates the path or fails
naming it; a gate whose inputs are excluded is reported, never silently unselected. The nightly audit
keeps the full profile. Beside the sparse rules, `git config feature.manyFiles true` (index version 4,
untracked cache, fsmonitor hook) is the per-worktree setting for a 28,759-file index. Check: a code-profile
worktree is under 1 GB on disk; `ci/run_gates.py --affected-by` on a diff touching an excluded bundle
reports the gate as unmaterialized; the link checker on a sparse worktree passes with the same count as on
a full one; the `lint` job of `pr.yml` reports its checkout time before and after.

### Lifecycle ledger for runs

A run has states planned, cased, approved, collected and cited, and the promotion events already exist:
the unapproved case document, `approval-consumed.json`, `collect.json`, a gate or claim citation. The
retention audit (`results/live/qpu-job-retention-audit.json`, written by `scripts/retain_run.sh` and
checked by `scripts/research_state.py`) becomes the digest-bound ledger of every promoted run, and a
run's state is read from that ledger, never from a text search. An age-out job exists only if the owner sets a
grace window; it removes terminal unpromoted runs alone and writes a tombstone per run: run time, source
commit, record digest, archive digest, disposition, and the statement that the plan cannot be regenerated
because it read the live Target. The 16 unpromoted directories hold 54 MB, so age-out is hygiene; the
producer items below are the growth lever, and the lossy precedent in `unretained-dry-run-logs/` argues
for keeping every record once the producer writes it once. Check: the ledger lists every collected and
cited run at `a1d1743`; the age-out job in dry-run mode names the 16 unpromoted directories and no other.

### New runs write each circuit archive once

`live_run.py` writes the compiled archive to `results/live/archives/<sha256>.qpy` when that digest is
absent and records the digest, which `submission.qpy_archive_sha256` already carries, plus a relative
locator. One archive API in the run-record module returns the archive for a run directory: it prefers a
historical `run_dir / "isa.qpy"` when present, otherwise resolves the content store from the digest,
confines any recorded path to the archive root, verifies the bytes against the recorded sha256 for every
run (dry runs included) and returns bytes or decoded circuits. The 48 files that open the path call the
API. Retained directories keep their `isa.qpy`. The same shape serves the other duplicate groups whose
records already carry a digest: the IQM calibration `metrics.json` copied into each run (24.6 MB), the
Quandela (22.5 MB) and Kaggle (11.8 MB) groups, and the 3.6 MB `circuit.json` retained at 342 paths. Check: a dry run of an existing case produces no `isa.qpy`
in its directory and the adjudication of a retained run reads its original bytes; the gates that bind
retained runs pass unchanged.

### Allocation search candidates become a sidecar

The planner writes `shot_allocation.allocation_search.candidates` to `allocation-search.json` beside the
record and leaves each candidate's `name`, `feasible` and `estimated_charge_seconds` in the record. Readers
of the candidates (the planning contracts) open the sidecar when the record names it. Check: a dry run of
the ripple atlas case writes a record under 2 MB, and the approved-record comparison of a retained case
reads the same values from the record and the sidecar.

### A storage-class rule for large artifacts

Existing history stays as it is: no move at the tip, no LFS pointer and no deletion removes a blob from
the 915 MB pack, and blobless clones avoid downloading what a worktree excludes. For artifacts that arrive
from now on, the rule is by size and access: a replay input under a documented threshold stays in this
repository because self-contained replay has value; a bundle above it goes to a public data repository
under the same owner, pinned by commit and by a sha256 manifest retained here, fetched by the gates that
reach it (the reached-gate calculation already exists; each gate declares the object digests it needs and
CI hydrates those objects, cached by digest, as `scripts/fetch_source_cache.py` already does for reading
copies); a frozen milestone bundle receives a Zenodo deposit with a DOI, described by a BagIt payload
manifest (`manifest-sha256.txt`, with `fetch.txt` for remote payload members) or an RO-Crate so the deposit
carries its own checksums. The `gororoba-retained-runs` Kaggle dataset is the existing checksum-matched
external mirror and keeps its provider-specific rules. Git LFS, git-annex with a special remote and DVC
rank below these for a two-person team on GitHub: LFS adds metered storage and bandwidth (10 GiB each on
the free plan) and cannot repair history, git-annex adds a remote to operate and back up (its RIA store
layout is the precedent for a flat content-addressed store), and DVC adds a cache and pipeline model beside
the gate machinery the repository already has. Software Heritage already archives this public repository's history, so a
separate deposit of git-tracked bytes adds nothing until bytes leave git. The one lever that would shrink the
existing pack, a successor repository whose default branch never held the blobs with this URL kept as the
historical object store, is a new canonical remote rather than a rewrite; it is listed so the ranking is
complete, and it is unwarranted while sparse materialization and the storage-class rule run. The
exceptional-fiber working bundle is the first candidate for the public data repository
([Decisions](#decisions-for-the-owner)). Check: the manifest verifier
rejects a bundle whose bytes differ from the manifest; a gate reaching an external bundle hydrates and
passes on a hosted runner inside its time budget.

### Paper notes join the paper library

The 22 identifier-named notes under `docs/notes/` move to `docs/notes/papers/` with `git mv`;
`docs/SOURCES.json` `note` fields, `docs/INDEX.md` and every inbound link update in the same commit.
Check: `docs/verify_sources.py` and the `sources` suite pass, and the link checker resolves 889 files.

### Vendor captures get an evidence home

`docs/notes/<provider>/docs/`, `api/`, `pypi/`, `site/`, `releases/` and the other manifest-bound capture
trees move to `docs/captures/<provider>/`; the capture scripts, their `--check` gates and each provider
README's table name the new path. Authored guides stay in `docs/notes/<provider>/`. Check: each capture
`--check` passes without network access and `docs/notes/` holds about 500 Markdown files.

### Design prose leaves the code directory

The thirteen Markdown documents in `gororoba_quantum/` move to `docs/design/` (designs, roadmaps, claim
boundaries) or `docs/notes/topics/` (synthesis notes), and `docs/README.md` rows follow. Check: the link
checker passes and `gororoba_quantum/` holds Python, its agent guide and requirements.

### Results hold bytes the programs write

The three Python files under `results/live/` move to `scripts/` (and `tests/` for the test), the 26 case
and findings documents to `docs/evidence/ibm-live-cases/` with lowercase hyphenated names, and the
registries stay where `live_run.py` and the retention audit write them. Gates naming the moved paths are
rewritten in the same commit, and the retention audit's inventory digest is rebound. Check: `ci/run_gates.py
--affected-by` on the diff reaches every rewritten gate and each passes.

### One documentation map with an ownership check

Four entries carry every path a newcomer takes: `AGENTS.md` (rules), `docs/README.md` (areas and task
entries), `docs/INDEX.md` (sources) and `docs/state/plans.md` (work records). The root `README.md` keeps
purpose, installation, first run, high-level layout and one link to the map; `docs/README.md` is the single
human map, partitioned by reader question; `docs/INDEX.md` is the source library index alone; `plan-catalogue.md`, `RESEARCH_STATE.md` and `QPU_RUN_CENSUS.md` stay generated views,
each linked once from the map, and run-level discovery stays in `scripts/results_index.py` rather than a
new catalog. A map check beside the link checker enforces ownership: every authored document has one
parent entry, the two global maps share only an allowlisted set of hubs (`SOURCES.json`,
`sources/README.md`), and generated views carry derived state only. Check: the map check reports zero
duplicate non-hub targets and zero orphaned authored documents.

### The package gains a hierarchy where the graph allows one

The sequence follows dependency direction rather than prefixes:

1. `gororoba_quantum/__init__.py` makes the directory a package while it stays on `sys.path`, so
   `import live_run` and `from gororoba_quantum import live_run` both resolve; imports gain the prefix
   without a file moving.
2. The import-graph scan (modules, edges, strongly connected components, private-symbol consumers) becomes
   a checked artifact under `docs/evidence/`, regenerated by a gate.
3. `live_run.py` yields its concerns to modules behind stable interfaces, in the order the private-symbol
   consumers point to: record and archive I/O (`_write_once_atomically`, `_archived_entries`, the archive
   API above), Target snapshots and calibration instants, compilation and placement (`_compile`, `_ops`,
   `_physical`, `_bind`), planning and approval (`_instance_hash`, `_candidates`), submission and
   collection (`_recovery_tags`, `_distribution`). `live_run.py` remains the CLI and the compatibility
   facade, so approval comparisons, exact QPY bytes, schemas, monkeypatch surfaces and historical
   collection keep their behavior; each extraction is proven by a byte-identical dry run of a retained
   case and by the gates with `cwd: gororoba_quantum` the diff reaches.
4. An import-boundary test rejects an edge from an extracted interface module back into `live_run` or
   into either strongly connected component.
5. Only when a cluster has no edge into a cycle does it move into a subpackage, one per pull request,
   with the 136 gate commands and the scripts naming it rewritten in the same change. The experiment
   family component (component A above) and the planning component (component B) are the last to move,
   after their cycles are cut.

Check per step: `mypy` over the five code roots, the `tests` check, every gate the diff reaches, a
`live_run.py` dry run writing its audit record, and the import-boundary test.

### Scripts group by provider

`scripts/` gains `scripts/<provider>/` directories for the `qi_`, `ascella_`/`qd_`, `iqm_` and `n21_`
clusters, with the `sys.path` insertion replaced by the package import, one cluster per pull request, after
the package root exists. Check: `ci/seed_provenance.py` scans the new paths and the gates naming each
script pass.

## Decisions for the owner

1. Home of artifacts above the size threshold, starting with the 2.2 GB working bundle and its 2.1 GB
   ignored siblings. Options: a public data repository under the same owner, pinned by commit and sha256
   manifest, with the bundle's README, split list and manifest retained here (recommended: the data stays
   reviewable where the findings cite it, and history here is untouched either way); keep in this
   repository and rely on sparse profiles alone (checkout cost solved, clone cost grows with every future
   bundle); the private documents repository (saves no clone bytes and hides publicly cited data). The
   threshold itself is part of the decision; 50 MB per file, the split boundary the bundle already uses,
   or 100 MB per bundle are the candidates.
2. Grace window and tombstone policy for the age-out of terminal unpromoted dry runs. Options: a 28-day
   window matching the quota period (recommended: a plan older than one quota cycle was never
   submitted under the calibration it read); 90 days; or no age-out, every dry run kept (growth continues
   at the slimmed producer's rate). The tombstone fields above are fixed in every option.
3. Order of the package work. Options: interface extraction from `live_run.py` before any directory move
   (recommended, because the import graph shows the cycles a prefix cut would preserve); package root only;
   or no package change.

## Peer review

The first draft of this document and a brief carrying every measurement went to external reviewers on
2026-10-30. The Codex CLI run (`gpt-daybreak-blue-latest`, medium reasoning, read-only sandbox) read the
brief and the repository and returned seven verdicts; its source claims were checked line by line before
adoption: the `live_run` to `correction_*` import cycle, the private-symbol consumers, the link checker's
absent-file filter, the gate selector's traversal stop, the stale `pr.yml` comment, the sparse blobless
pattern in `ci/fetch_open_gororoba.sh`, and the unretained-logs README all hold. Its falsifier for the
package cut, an import-graph scan, was run and refuted the cut (the table above). The Grok Build CLI (`grok` 1.0.70, single-turn, tools limited to reading) read the brief and
the tree and returned a second review whose checks of the gate count, the pack size and the link checker
agree with the measurements here; it supplied the non-cone sparse pattern, the `actions/checkout` filter,
the successor-repository option, the `feature.manyFiles` setting and the extension of the archive resolver
to the other duplicate groups, each verified before adoption. A local Ollama model (`glm-4.7-flash-64k`
through `opencode run`) answered the seven questions in general terms and named a record field
(`job_type`) that no record carries; its output is retained as a third sample and changed nothing. Both
reviews, the Codex review and the brief are retained under `docs/archive/reviews/layout-reconciliation/`.
Amazon Bedrock returned no review:
every Anthropic, xAI and OpenAI model id is unavailable to the account and every on-demand open-weight
model answered with the daily token throttle ([free-plan-usage.md](../notes/aws/free-plan-usage.md)).

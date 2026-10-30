# Repository layout reconciliation

This document measures the shape of the checkout at commit `a1d1743` (main, 2026-10-30), names the
mechanism behind each structural defect, and sets the program that corrects them under the repository's
own constraints: retained bytes are immutable, a move carries every reference, ledger and gate in the same
change, and a new producer changes before any reader. Every number below comes from `git ls-files`,
`git count-objects`, `ci/gates.json` and the run directories at that commit; a later measurement replaces
the number, not the mechanism. The work record is
[repository-layout-reconciliation](../state/plans/repository-layout-reconciliation.json).

## Measured state

| Quantity | Value |
|---|---|
| Tracked files | 28,759 |
| Tracked bytes in the checkout | 7.03 GB (results/ 4.41 GB, docs/ 2.61 GB, code and tests 17 MB) |
| Packed history after `git gc` | 915 MB in 2 packs (before: 81,076 loose objects, 2.32 GiB, 13 packs of 30 MB) |
| Byte-identical duplicate content | 2,541 blob ids at more than one path, 463 MB of redundant checkout bytes |
| Largest single bundle | `docs/evidence/a5-exceptional-fibers/working/`, 956 files, 2.20 GB (31 % of tracked bytes) |
| `results/live/` run directories | 354: 61 collected runs, 144 with `UNAPPROVED_CASE.md`, 149 bare dry runs (`record.json` + `isa.qpy`) |
| `results/live/` directories nothing outside them references | 16, 54 MB, none collected |
| Gates | 633 in `ci/gates.json` (464 `pr` tier, 169 `full`), 30,206 measured seconds, 137 distinct bound paths |
| Python modules in `gororoba_quantum/` | 155 flat files, 90,796 lines, `live_run.py` 8,486 lines, no `__init__.py` |
| Scripts in `scripts/` | 373 Python files, 259 of them inserting `gororoba_quantum/` on `sys.path` |
| Markdown files under `docs/notes/` | 2,906, of which 2,413 are vendor documentation captures (IQM 1,925, Quantum Inspire 178, qBraid 165, Open Quantum 78, Quandela 67) |
| Loose notes at `docs/notes/*.md` | 68, 28 of them the `note` of a `docs/SOURCES.json` record |
| Documentation maps | `docs/README.md` 353 links, `docs/INDEX.md` 321 links, 107 targets in both |
| Ignored bytes inside the checkout | 3.2 GB: `docs/local/` 2.34 GB (`a5-failed-runs` 2.1 GB), `docs/local_source_cache/` 318 MB, `.mypy_cache` trees 330 MB |

## Findings

### Dry-run records are the doctrine, not debris

The submission rule writes a record for every plan, and 293 of the 354 live directories are dry runs or
unapproved cases. 338 of the 354 directories are named by their timestamp somewhere outside themselves
(a case document, a findings note, a gate, a ledger), so the directories are evidence, and the 16
unreferenced ones hold 54 MB. The lever on `results/live/` is therefore the producer, not deletion: what
`live_run.py` writes per run decides the growth rate.

Two producer mechanisms account for most of the 2.2 GB:

- `isa.qpy` is written into every run directory, and the same compiled archive recurs across a day's
  dry runs: 277 MB of the 463 MB redundant bytes are identical `isa.qpy` copies (one archive appears in 15
  directories). The record already binds the archive by content in `submission.qpy_archive_sha256`, and
  48 files name the archive path, among them `adjudicate.py`, `qpu_planning_contracts.py`, `patch_window_analysis.py`,
  `scheduled_idle_scaling.py`, `inventory_retained_runs.py` and the retention audit, which open
  `run_dir / "isa.qpy"` directly.
- `record.json` totals 932 MB over 351 files. In the eleven records above 1 MB the key
  `shot_allocation.allocation_search.candidates` carries every rejected allocation candidate with its full
  job and observable tables: 20.3 MB of a 24 MB record, 81 MB across the tree.

Git stores identical blobs once, so the duplicates cost checkout bytes and file counts, not clone size;
the 915 MB pack is the clone cost of the whole 7 GB tree.

### One working bundle holds a third of the tree

`docs/evidence/a5-exceptional-fibers/working/` retains the Singular logs, relation files and split
`.part` files of the exceptional-fiber computations: 2.20 GB, with 107 MB duplicated between `runs/` and
`distribute/out/`. No ledger binds a file under `working/`: the kernel-attachments results reference none of
its paths, and the only gate text naming it excludes it from Ruff and mypy. Its README states the role:
diagnostic working data over F_32009 that enters the claim record only through the kernel-attachments
ledger. `docs/local/a5-failed-runs/` holds a further 2.1 GB of ignored siblings. Whether this material lives
in this repository, in the private documents repository beside it, or in a data repository with a
sha256 manifest here is the owner's decision ([Decisions](#decisions-for-the-owner)).

### The scientific code has a latent hierarchy and no package

`gororoba_quantum/` is a directory of 155 modules imported by bare name: 136 gates run with
`cwd: gororoba_quantum`, tests import `live_run` and `diagnostic_experiments` unqualified, and 259 scripts
insert the directory on `sys.path`. The names already cluster: `correction_*` (14), `rank_*` (6),
`msq_*` (5), `kernel_*` (5), `et_*` (5), `qpu_*` (4), `pub_*` (4), `primorial_*` (4), `four_*` (4),
`aer_*`, `idle_*`, `ripple_*`, `hypercomplex_*` (3 each); `scripts/` clusters as `qi_*` (69),
`ascella_*` (45), `qd_*`, `n21_*`, `iqm_*` (14 each), `bdsc_*` (11). The import graph has five hubs:
`parallel` (57 importers), `cd_core` (33), `experiments` (30), `live_run` (26), `experiment_optimizer` (19).
Thirteen Markdown design documents (`DESIGN_NOTES.md`, `QPU_EXECUTION_ROADMAP.md`, `CLAIM_BOUNDARIES.md`
and ten more) live in the code directory and are mapped from `docs/README.md`.

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
The remaining 46 are research notes of the kind `docs/notes/topics/` owns.

### Vendor captures sit beside authored notes

The provider capture scripts (`scripts/capture_iqm_docs.py` and its siblings) retain every page of a
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

### Object store and caches

81,076 loose objects (2.32 GiB) sat beside 13 small packs; `git gc` on 2026-10-30 took 5.5 minutes and
left 2 packs of 915 MB. Each worktree checkout carries the full 7 GB tree, and `ci/pinned_tool.py` keys a
mypy cache directory under the working directory, so eight checkouts on the build host hold eight copies
of the tree and their own caches. The user-level rule places build trees and caches under
`${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/`.

## Rules the program obeys

- A retained file keeps its path and bytes while any ledger, record or digest binds it; a correction is a
  new file that the old one's map row links.
- A move is `git mv` plus every reference, ledger entry and gate command in one commit, proven by
  `scripts/check_markdown_links.py`, `ci/run_gates.py --affected-by` on the branch diff and the `sources`
  suite.
- A producer changes before its readers depend on the new shape, and every reader accepts both shapes: a
  run collected under an earlier revision replays unchanged.
- One home per fact. A second area that needs the fact gets a link.
- Deletion of tracked bytes and relocation of bytes to another repository are owner decisions.

## Program

Each item names its mechanism and the check that proves it. Items that need no owner decision proceed in
their own pull requests in the order listed; the items under the owner's decisions wait for the answer.

### Caches and object store leave the checkout

`ci/pinned_tool.py` resolves the mypy cache root to `${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/mypy/`
keyed by the checkout path, and keeps the per-invocation hash directory that protects concurrent gates.
`git maintenance start` registers the canonical checkout for hourly incremental repacks so loose objects
stop accumulating. Check: `du -s .mypy_cache` reads zero after a gate run, and `git count-objects -v`
reports a loose count under `gc.auto` after a day of commits.

### New runs write each circuit archive once

`live_run.py` writes the compiled archive to `results/live/archives/<sha256>.qpy` when that digest is
absent and records the digest, which `submission.qpy_archive_sha256` already carries. A resolver in the
run-record module returns `run_dir / "isa.qpy"` when it exists and the archive path otherwise; the
48 files that name the path call the resolver. Retained directories keep their `isa.qpy`. Check: a dry run of an existing case
produces no `isa.qpy` in its directory and the adjudication of a retained run reads its original bytes;
the gates that bind retained runs pass unchanged.

### Allocation search candidates become a sidecar

The planner writes `shot_allocation.allocation_search.candidates` to `allocation-search.json` beside the
record and leaves each candidate's `name`, `feasible` and `estimated_charge_seconds` in the record. Readers
of the candidates (the planning contracts) open the sidecar when the record names it. Check: a dry run of
the ripple atlas case writes a record under 2 MB, and the approved-record comparison of a retained case
reads the same values from the record and the sidecar.

### Paper notes join the paper library

The 22 identifier-named notes under `docs/notes/` move to `docs/notes/papers/` with `git mv`;
`docs/SOURCES.json` `note` fields, `docs/INDEX.md` and every inbound link update in the same commit.
Check: `docs/verify_sources.py` and the `sources` suite pass, and the link checker resolves 888 files.

### Vendor captures get an evidence home

`docs/notes/<provider>/docs/`, `api/`, `pypi/`, `site/`, `releases/` and the other manifest-bound capture
trees move to `docs/captures/<provider>/`; the capture scripts, their `--check` gates and each provider
README's table name the new path. Authored guides stay in `docs/notes/<provider>/`. Check: each capture
`--check` passes without network access and `docs/notes/` holds about 500 Markdown files.

### Design prose leaves the code directory

The thirteen Markdown documents in `gororoba_quantum/` move to `docs/design/` (designs, roadmaps, claim
boundaries) or `docs/notes/topics/` (synthesis notes), and `docs/README.md` rows follow. Check: the link
checker passes and `gororoba_quantum/` holds Python, its agent guide and `requirements`.

### Results hold bytes the programs write

The three Python files under `results/live/` move to `scripts/` (and `tests/` for the test), the 26 case
and findings documents to `docs/evidence/ibm-live-cases/` with lowercase hyphenated names, and the
registries stay where `live_run.py` and the retention audit write them. Gates naming the moved paths are
rewritten in the same commit, and the retention audit's inventory digest is rebound. Check: `ci/run_gates.py
--affected-by` on the diff reaches every rewritten gate and each passes.

### One documentation map

`docs/INDEX.md` becomes the source index alone (its stated role) and drops the rows that duplicate the
map; `docs/README.md` keeps areas and task entry points; `docs/state/plan-catalogue.md`,
`RESEARCH_STATE.md` and `QPU_RUN_CENSUS.md` stay generated views, each linked once from the map. The root
`README.md` keeps installation, layout and the first run, and links the map for everything else. Check:
the two files share no link target that is not a hub (`SOURCES.json`, `sources/README.md`).

### The package gains a hierarchy in waves

`gororoba_quantum/__init__.py` makes the directory a package while the directory stays on `sys.path`, so
`import live_run` and `from gororoba_quantum import live_run` both resolve during the transition. Each wave
moves one cluster into a subpackage and leaves a one-line re-export module at the old name, then rewrites
the gates, scripts and tests that name the cluster, and removes the re-export when nothing imports it. The
clusters and their order:

| Wave | Subpackage | Modules |
|---|---|---|
| infrastructure | `gororoba_quantum/infra/` | `parallel`, `packing`, `qrng_seeds`, `aer_identity`, `aer_*` |
| algebra | `gororoba_quantum/algebra/` | `cd_core`, `rank_*`, `kernel_*`, `four_*`, `hypercomplex_*`, `primorial_*`, `principal_skew_atlas`, `skew_schur_charts`, `boolean_anf`, `modular_arithmetic`, `demarrais_structures` |
| hardware | `gororoba_quantum/hardware/` | `live_run`, `qpu_*`, `runtime_contracts`, `heron_multiprogramming`, `experiments`, `experiment_optimizer`, `pub_*`, `idle_*` |
| analysis | `gororoba_quantum/analysis/` | `adjudicate`, `msq_*`, `measurement_sequence_*`, `correction_*`, `diagnostic_experiments`, `qpe_diagnostics`, `empirical_bernstein_contracts`, `star_ramsey`, `readout_actor_family` |
| providers | `gororoba_quantum/providers/` | `qi_stack`, `et_*`, `bdsc`, `provider_counters`, `ripple_*` |

`live_run.py` at 8,486 lines splits along its existing section boundaries (calibration, planning,
compilation, submission, collection) inside `hardware/` in the same wave. Check per wave: `mypy` over the
five code roots, the `tests` check, and every gate with `cwd: gororoba_quantum` the diff reaches; a
`live_run.py` dry run writes its audit record.

### Scripts group by provider

`scripts/` gains `scripts/<provider>/` directories for the `qi_`, `ascella_`/`qd_`, `iqm_` and `n21_`
clusters, with the `sys.path` insertion replaced by the package import, one cluster per pull request.
Check: `ci/seed_provenance.py` scans the new paths and the gates naming each script pass.

## Decisions for the owner

1. Home of the 2.2 GB working bundle and its 2.1 GB ignored siblings. Options: keep in this repository
   (clone stays near 1 GB, every checkout carries 2.2 GB); move the `working/` tree to the private
   documents repository with `README.md`, `split.txt` and a sha256 manifest retained here (checkout drops
   31 %, the bundle leaves public history only at the move commit); or a public data repository under the
   same owner, cited by URL and digest. The recommendation is the documents repository: the bundle's own
   README names it diagnostic working data outside the claim record, and that repository already holds
   material this one cites by digest.
2. Retention of the 16 unreferenced dry-run directories (54 MB) and future unreferenced dry runs. Options:
   keep every dry run (the current rule); move unreferenced dry runs older than a window into
   `results/live/unretained-dry-run-logs/` as logs only; or record only the plan digest for a dry run that
   no case cites. The recommendation is the second: the directory already exists for that purpose.
3. Depth of the package hierarchy. Options: the five subpackages above with the flat re-exports removed
   after the waves; a package with `__init__.py` and no moves (imports gain a prefix, files stay flat);
   or no package change. The recommendation is the five subpackages, because the 136 gates and 259 scripts
   are rewritten once per cluster and the clusters are already what the names say.

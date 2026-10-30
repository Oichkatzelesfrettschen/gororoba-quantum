# Peer-review brief: layout of a research repository with retained evidence

You are reviewing a storage and layout design for a public research repository (quantum hardware
experiments, exact algebra computations, formal proofs). Read every fact below as measured; read every
option as a proposal to attack. Answer the numbered questions at the end with a verdict, the mechanism
behind it and the falsifier that would change your mind. Prefer first principles over convention, and
name any mechanism the author missed. The author's own recommendation is marked; disagree where the facts
warrant.

## The repository's contract

- Retained bytes are immutable. A file a ledger, record or digest binds keeps its path and bytes; a
  correction is a new file that the old one's map row links.
- 633 gates (`ci/gates.json`) replay retained records; 137 distinct paths are bound by gate commands, 99
  gates name replay files whose digests are compared. A pull request runs only the gates its diff reaches
  (reach is computed from import closure plus explicit input globs); the full audit runs nightly.
- Every hardware submission is preceded by a dry run that writes a record; a submission is approved
  against that record's digest. Dry runs are therefore evidence of what was planned, not scratch.
- Force-push is denied by the permission harness, so history is never rewritten.
- A private sibling repository (`gororoba-quantum-documents`, cloned beside this one) already holds
  reading copies of sources that cannot be redistributed; this repository cites them by sha256.
- Build host: 8 worktree checkouts of this repository on one ext4 disk at 90 % capacity; CI runs on
  hosted GitHub runners with an 8-minute job budget for lint, types and tests and 30 minutes for gates.

## Measured state at commit a1d1743 (2026-10-30)

| Quantity | Value |
|---|---|
| Tracked files | 28,759 |
| Tracked bytes in the checkout | 7.03 GB: results/ 4.41 GB, docs/ 2.61 GB, code and tests 17 MB |
| Packed history after `git gc` | 915 MB in 2 packs (before gc: 81,076 loose objects, 2.32 GiB; the previous 13 packs held 30 MB) |
| Byte-identical duplicate content | 2,541 blob ids at more than one path; 463 MB of redundant checkout bytes |
| Largest bundle | `docs/evidence/a5-exceptional-fibers/working/`: 956 files, 2.20 GB, Singular logs and relation files over F_32009, files over 50 MB split into 45 MB parts; 107 MB duplicated inside it between `runs/` and `distribute/out/`; bound by no ledger; its README calls it diagnostic working data that enters claims only through a separate ledger |
| Ignored siblings of that bundle | `docs/local/a5-failed-runs/` 2.1 GB (git-ignored, on disk in one checkout) |
| `results/live/` | 354 run directories, 2.20 GB: 61 collected hardware runs; 144 with an unapproved case document; 149 bare dry runs holding only `record.json` and `isa.qpy` |
| Referenced run directories | 338 of 354 are named by timestamp in some file outside themselves (case documents, findings, gates, ledgers); 16 unreferenced, 54 MB, none collected |
| `isa.qpy` (compiled circuit archive) | 349 files, 517 MB; 277 MB are byte-identical copies (one archive appears in 15 directories); the record already stores `submission.qpy_archive_sha256`; 48 files in the code name `run_dir / "isa.qpy"` |
| `record.json` | 351 files, 932 MB; in the 11 records above 1 MB the key `shot_allocation.allocation_search.candidates` holds every rejected allocation candidate with full job and observable tables (20.3 MB of a 24 MB record; 81 MB in total) |
| Other duplicate groups | IQM calibration `metrics.json` copied into each run (24.6 MB), Quandela 22.5 MB, Kaggle 11.8 MB, a 3.6 MB `circuit.json` at 342 paths |
| Code | `gororoba_quantum/`: 155 flat modules, 90,796 lines, no `__init__.py`; `live_run.py` 8,486 lines; modules import each other by bare name; 136 gates run with `cwd: gororoba_quantum`; `scripts/`: 373 files, 259 insert `gororoba_quantum/` on `sys.path`; tests import bare names |
| Name clusters in the code | `correction_*` 14, `rank_*` 6, `msq_*` 5, `kernel_*` 5, `et_*` 5, `qpu_*` 4, `pub_*` 4, `primorial_*` 4, `four_*` 4; scripts `qi_*` 69, `ascella_*` 45, `qd_*` 14, `n21_*` 14, `iqm_*` 14, `bdsc_*` 11 |
| Import hubs | `parallel` imported by 57 modules, `cd_core` 33, `experiments` 30, `live_run` 26, `experiment_optimizer` 19 |
| Docs | `docs/notes/`: 2,906 Markdown files, 2,413 of them vendor documentation captures (IQM 1,925 pages, Quantum Inspire 178, qBraid 165, Open Quantum 78, Quandela 67), each tree bound by a `MANIFEST.json` of sha256 and a `--check` gate; 68 loose notes at `docs/notes/*.md`, 22 of them paper notes by arXiv id beside `docs/notes/papers/` (237 notes); 13 design Markdown files inside the code directory; two maps (`docs/README.md` 353 links, `docs/INDEX.md` 321 links, 107 shared targets) and three generated catalogs |
| Results tree contents other than runs | 3 Python files, 26 case and findings documents, registries (`qpu-job-inventory.json`), an audit-provenance tree |
| Caches inside checkouts | `.mypy_cache` trees 330 MB (keyed per invocation under the working directory), `docs/local/` 2.34 GB |

## First-principles decomposition

Every byte in the tree belongs to one of six storage classes, and the classes differ in the properties
that decide a home:

| Class | Examples | Mutability | Binding | Reader | Growth driver |
|---|---|---|---|---|---|
| Code | `gororoba_quantum/`, `scripts/`, `ci/` | edited | tests and gates | humans, CI | authored |
| Authored prose | notes, designs, runbooks | edited | link checker | humans | authored |
| Bound evidence | replay inputs, ledgers, collected runs | immutable | sha256 in gates or ledgers | gates nightly | one record per hardware run |
| Unbound producer output | dry-run records, `isa.qpy`, rejected candidates, working logs | immutable by rule, bound by nothing | none or a case document | rarely | one record per plan; proportional to iteration count |
| Third-party captures | vendor docs, PyPI metadata, PDFs | immutable, pruned by inventory | `MANIFEST.json` sha256 | capture `--check`, humans occasionally | vendor release cadence |
| Caches | mypy, pycache, local scratch | disposable | none | tools | every run |

Observations that follow from the table:

1. Git deduplicates identical blobs in history, not in checkouts. The 463 MB of duplicates cost 8 x 463 MB
   of disk on the build host and zero bytes of clone. The pack is 915 MB for a 7 GB tree because text
   compresses about 8:1. So "repo size" is two numbers with different levers: clone size (history) and
   checkout size (working tree times worktrees).
2. Unbound producer output is the only class whose growth is proportional to how often the team iterates,
   and its bytes are read almost never. Every other class grows with external events.
3. The immutability rule exists for bound evidence; applying it to unbound output is a policy choice, not
   a mechanism requirement. Where a record is bound only by a case document's citation of its timestamp,
   the binding is a name, not a digest.
4. The checkout cost of immutable bytes can be removed without moving them: `git sparse-checkout` (cone
   mode) excludes directories from a worktree while history keeps them; a blobless partial clone
   (`--filter=blob:none`) fetches contents on demand. Neither changes a path, a digest or a gate.
5. Content-addressed storage (one file per sha256, pointers from records) is already half-implemented: the
   record carries the archive digest. The producer writes the copy anyway.
6. A package hierarchy is a naming change for the import mechanism; the clusters already exist in the
   prefixes. The cost is the number of sites that name a module (136 gate commands, 259 path insertions,
   tests), paid once per cluster.

## Options under review

### Home of the 2.2 GB working bundle (and 2.1 GB ignored siblings)

- Keep in this repository as is.
- Keep in this repository, exclude from worktrees by sparse-checkout, keep in history. Clone cost
  unchanged (its share of the 915 MB pack), checkout cost removed per worktree.
- Move to the private documents repository with README, split list and sha256 manifest retained here.
  Public history keeps the bytes reachable at the move commit (no rewrite), so the clone cost stays until
  history is rewritten, which the harness forbids.
- A public data repository (or git-annex / DVC / LFS remote) cited by URL and digest.
- Zenodo or Software Heritage deposit for the diagnostic data with a DOI, manifest here.

Author's recommendation before review: private documents repository. Author's doubt: the clone cost does
not drop without a rewrite, and the owner notes that the same decision applies to many other artifacts,
so a per-bundle move does not scale; a storage-class rule is needed instead.

### Retention of unreferenced dry runs

- Keep every dry run (current rule).
- Age-out: an unreferenced dry run older than a window keeps only its log in `results/live/unretained-dry-run-logs/`.
- Record only the plan digest for a dry run no case cites.
- Keep every dry run but stop writing the bytes that duplicate: content-addressed `isa.qpy`
  (`results/live/archives/<sha256>.qpy`, resolver for the 48 readers), rejected candidates in a sidecar.

Author's recommendation before review: age-out plus the producer changes. Author's doubt: the 16
unreferenced directories are 54 MB, so age-out saves little today; the producer changes address the
growth; the real question is whether a dry run is evidence (immutable, bound) or scratch (disposable), and
the current practice treats it as both.

### Depth of the package hierarchy

- Five subpackages (`infra`, `algebra`, `hardware`, `analysis`, `providers`) in waves with re-export shims.
- `__init__.py` only; files stay flat; imports gain a prefix.
- No change.

Author's recommendation before review: five subpackages. Author's doubt: `live_run.py` at 8,486 lines is
the hub 26 modules import; splitting it is the real work and the subpackage move is cosmetic beside it.

## Questions

1. Which storage class should own dry-run records, and what mechanism makes the answer enforceable
   (a digest-bound ledger, an age-out job, a producer that writes less)?
2. Is sparse-checkout plus a blobless clone sufficient for the checkout problem, so that no bytes move?
   What breaks: gates that read the excluded paths, the nightly audit, the link checker?
3. For the clone-size problem (915 MB and growing), rank: do nothing, LFS, git-annex with a special
   remote, DVC, a separate data repository, a Zenodo deposit. Account for: no force push, GitHub hosting,
   a two-person team, replays that must read the bytes locally and in CI.
4. Content-addressed `isa.qpy`: is a resolver over 48 call sites the right shape, or should the record
   carry a relative path to the archive so readers need no resolver?
5. Package hierarchy: is the five-subpackage split justified by the import graph given, or does the
   graph argue for a different cut (for example by the five hubs)? What does splitting an 8,486-line hub
   module cost relative to the gain?
6. Documentation: two maps sharing 107 targets and three generated catalogs. What is the minimal set of
   entry documents for a repository with this many evidence bundles, and what rule keeps it minimal?
7. Name any mechanism or precedent from other research or data-heavy repositories that this brief
   missed.

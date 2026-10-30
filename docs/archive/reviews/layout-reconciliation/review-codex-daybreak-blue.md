# Peer review

The brief concerns repository architecture, evidence retention, reproducible replay, and Git storage mechanics. I read the brief in full and checked the gate selector, link checker, CI workflows, live-run archive handling, evidence documentation, and existing archive/fetch precedents.

The central correction is simple: artifact location cannot decide retention, materialization, or package boundaries. Lifecycle state decides retention; content identity decides deduplication; access frequency decides materialization; dependency direction decides package boundaries.

## 1. Which storage class owns dry-run records?

**Verdict: SERIOUS correction required. Dry runs require lifecycle states, not one storage class.**

**Mechanism**

A dry run becomes bound evidence when a case, approval, collection, finding, gate, or ledger binds its bytes. The submission path already hashes the approved record and QPY archive (`gororoba_quantum/live_run.py:3414`), while collection verifies the archive digest before interpreting circuits (`gororoba_quantum/live_run.py:6763`). Those records belong to bound evidence.

A bare run that remains absent from every authoritative registry is unbound producer output. The repository gains no integrity by declaring unreferenced bytes immutable.

The enforceable design should be:

1. The producer writes a compact run manifest, a content-addressed QPY object, and optional verbose sidecars.
2. Case creation, approval, collection, gate admission, or claim citation promotes the run into a digest-bound retention ledger.
3. An age-out job removes only terminal, unpromoted runs after a grace period.
4. The age-out job writes a tombstone containing the run time, source commit, record digest, artifact digests, disposition, and an explicit statement that the removed plan cannot be reconstructed.

A timestamp-reference scan is unsuitable as the root set. The scan can miss generated registries, indirect references, future approval use, and readers outside Markdown.

The author correctly prioritizes producer slimming, but the proposed age-out rule is premature. The existing log-only precedent demonstrates the information loss: the repository says the removed records cannot be regenerated because every run read a live Target and properties (`results/live/unretained-dry-run-logs/README.md:26`). A digest without retrievable bytes is a tombstone, not evidence.

**Falsifier**

A binding audit or scientific policy requiring every planning attempt to remain replayable would place every dry run in bound evidence and prohibit age-out. Conversely, measured evidence that uncited runs receive no use after a defined interval would support the proposed retention window.

## 2. Are sparse checkout and blobless clone sufficient?

**Verdict: SOUND for ordinary worktrees; insufficient for the audit without explicit materialization profiles.**

**Mechanism**

Sparse checkout removes excluded files from each worktree. A fresh `--filter=blob:none` clone also avoids downloading excluded blobs. Applying sparse checkout to an existing full clone only removes working-tree copies; the shared object database retains already downloaded blobs.

The repository already implements the desired external-fetch mechanism: exact commit pinning, cone-mode sparse checkout, blobless fetch, detached checkout, and head verification (`ci/fetch_open_gororoba.sh:39`).

The 2.2 GB exceptional-fiber working tree is safe to exclude from ordinary worktrees because the current gates explicitly exclude it from Ruff and mypy, and its README says claim admission occurs through a separate ledger (`docs/evidence/a5-exceptional-fibers/README.md:3`).

Three failure modes remain:

- A gate that opens an excluded input fails.
- Gate selection can under-approximate dependencies in a sparse checkout because the selector discards tracked files absent from disk and stops dependency traversal at missing sources (`ci/gate_inputs.py:54`, `ci/gate_inputs.py:127`).
- The link checker silently excludes absent Markdown source files from its checked set, while a fragment link to an absent Markdown target can fail when anchor extraction attempts to read it (`scripts/check_markdown_links.py:241`, `scripts/check_markdown_links.py:299`).

The repository should define named profiles:

- developer/code;
- documentation;
- evidence review;
- full audit.

Each gate should either require a full-audit profile or hydrate and verify its declared inputs before selection and execution. The current nightly workflow requests full history explicitly (`.github/workflows/ci.yml:59`), so local sparse profiles do not impair hosted nightly execution.

The pull-request workflow also contains a stale “about 18 MiB packed” comment while the measured pack is 915 MB (`.github/workflows/pr.yml:83`). The stale assumption belongs in the reconciliation scope because checkout cost influences the eight-minute jobs.

**Falsifier**

A tested hydration wrapper that materializes command operands, import closure, checksum members, glob inputs, and traced reads before gate selection would permit sparse checkout in every job. The link checker would also need to inspect the committed tree rather than silently omitting absent files.

## 3. Rank the clone-size options

**Verdict: No listed relocation can shrink the existing 915 MB history under the no-rewrite rule. Rank current history separately from future growth.**

For the existing pack, the correct action is **do nothing to history**. Moving bytes, adding LFS pointers, or deleting paths at the tip leaves the historical blobs reachable. Blobless clones can avoid downloading them, but ordinary full clones cannot.

For future large artifacts, the ranking is:

1. **Separate public data repository, pinned by commit and SHA-256 manifest.**  
   A public repository preserves reviewability, gives replay tools ordinary local files, supports sparse/blobless fetches, and keeps code-only CI independent of the data repository.

2. **Zenodo for frozen publication or milestone bundles.**  
   Zenodo supplies immutable custody and a DOI. Whole-deposit retrieval and release-oriented versioning make Zenodo a poor working store for frequently changing replay inputs.

3. **Keep small, frequently replayed evidence in the main repository.**  
   Self-contained replay has real value. A size-and-access threshold should drive export instead of an indiscriminate “all evidence elsewhere” rule.

4. **Git LFS for future large blobs.**  
   GitHub integration is convenient, but storage and bandwidth quotas, CI hydration, public-fork behavior, and another remote failure surface need measured acceptance. LFS cannot repair existing history without migration and rewrite.

5. **git-annex with a special remote.**  
   git-annex has the right content-addressed semantics, but the two-person team must operate, authenticate, monitor, and back up the special remote.

6. **DVC.**  
   DVC adds cache, remote, metadata, and pipeline semantics without matching the repository’s immutable-evidence workflow. The repository already possesses its own gate and provenance machinery.

The recommendation to move the exceptional-fiber data into the private documents repository is weak. The move saves zero historical clone bytes and makes publicly cited diagnostic data less reviewable. The working record says the findings rest on those data even though a separate ledger controls claim admission (`docs/evidence/a5-exceptional-fibers/README.md:3`). A public data repository or frozen Zenodo deposit is the defensible destination unless redistribution restrictions exist.

External replay data should be fetched only for reached gates, cached by immutable digest, and verified against the in-repository manifest.

**Falsifier**

Measured GitHub LFS storage, bandwidth, fork, and CI behavior within a permanent budget would move LFS upward. An already operated, durable annex remote would similarly improve git-annex’s rank.

## 4. Should `isa.qpy` use a resolver or a recorded path?

**Verdict: Use a central resolver. A recorded relative path is a locator, not a replacement for the resolver.**

**Mechanism**

The digest identifies the archive. A path only describes one storage layout. Historical records lack the proposed path field and existing retained archives must remain at `run_dir / "isa.qpy"`, so backward-compatible resolution remains necessary.

One archive API should:

1. Prefer a historical local `isa.qpy` when present.
2. Otherwise resolve the content-store object from its digest or validated locator.
3. Confine any recorded path to the allowed archive root.
4. Verify the exact bytes against the recorded SHA-256.
5. Return bytes or decoded circuits through one interface.

New records may carry both digest and relative path, but readers should treat the digest as authority. Replacing 48 direct `isa.qpy` opens with 48 record-path opens merely distributes a different convention. The current producer already computes the digest immediately after its atomic write (`gororoba_quantum/live_run.py:8435`).

The proposed design’s legacy-first resolver is therefore directionally correct. The resolver must verify every selected archive, including unsubmitted dry-run archives, rather than restricting integrity checks to submitted runs.

**Falsifier**

A schema library that migrates every historical and future record to a validated, root-confined artifact reference could eliminate digest-derived fallback. Readers would still need that shared schema library, which is functionally the resolver.

## 5. Does the import graph justify five subpackages?

**Verdict: SERIOUS architectural defect in the recommendation. The reported graph does not justify the five-way cut.**

**Mechanism**

Importer counts identify pressure points, not package boundaries. The proposed packages also contain a concrete cycle:

- `live_run.py`, assigned to `hardware`, imports `correction_collection`, assigned to `analysis` (`gororoba_quantum/live_run.py:69`).
- Correction modules import `live_run` in the reverse direction.

The proposed `hardware` and `analysis` packages would therefore preserve a cross-package cycle behind re-export shims. The new directories would make the monolith tidier without making its dependency direction clearer.

The five hubs also play different architectural roles:

- `parallel` is infrastructure.
- `cd_core` is an algebra specification.
- `experiments` contains domain definitions.
- `experiment_optimizer` contains planning logic.
- `live_run` is an application orchestrator and compatibility surface.

A defensible sequence is:

1. Add a package root and convert imports without moving modules.
2. Generate the complete import graph, strongly connected components, and private-symbol consumer inventory.
3. Extract record/archive I/O, target snapshots, compilation and placement, planning and approval, submission, and collection behind stable interfaces.
4. Keep `live_run.py` as the CLI and compatibility facade.
5. Add import-boundary tests that reject reverse dependencies.
6. Group cohesive experiment families only after the runtime interfaces stabilize.

`live_run.py` contains about 249 class and function definitions, and repository consumers import private helpers such as `_compile`, `_bind`, and `_gate_time_view`. Splitting the hub costs more than moving 8,486 lines: the change must preserve approval comparisons, exact QPY bytes, schemas, CLI behavior, monkeypatch surfaces, historical collection, and dry-run output. The gain is still worth pursuing because explicit interfaces reduce the blast radius of later changes. Moving the intact hub into `hardware/` earns almost none of that gain.

**Falsifier**

A generated import graph showing low inter-package edge density, an acyclic dependency order, and no large cross-package strongly connected component would support the proposed five packages. Byte-stable dry runs and historical replay tests would then need to establish compatibility.

## 6. What is the minimal documentation entry set?

**Verdict: Keep two global human entry documents and one specialized source index. Generated catalogs remain subordinate views.**

**Mechanism**

The minimal structure is:

1. Root `README.md`: purpose, installation, first run, high-level layout, and one link to the documentation map.
2. `docs/README.md`: the single human map organized by reader task and subject. The file already declares itself the single documentation entry (`docs/README.md:1`).
3. `docs/INDEX.md`: source-library, licensing, and bibliography index only.

`RESEARCH_STATE.md`, `QPU_RUN_CENSUS.md`, plan catalogs, and similar files are generated query views. Each generated view should receive exactly one link from the appropriate map row. Evidence bundles keep local `README.md` files, while machine-derived discovery belongs in the existing results-index command rather than another manually maintained catalog.

The enforceable rule should exceed “one home per fact”:

- Every authored document has one canonical parent entry.
- Global maps partition by reader question.
- Duplicate targets between global maps require a small hub allowlist.
- Generated catalogs contain derived state, never authored facts.
- A map lint reports duplicate non-hub targets and orphaned authored documents.

The current link checker proves validity, not minimality. A second check must enforce the navigation ownership rule.

**Falsifier**

Navigation evidence showing that readers cannot reach a major artifact class within two links from the global entries would justify another entry surface. Raw link counts do not establish such a need.

## 7. Missed mechanisms and precedents

**Verdict: The brief omits several relevant mechanisms, including precedents already implemented in the repository.**

- **DataLad with git-annex/RIA storage:** a mature research-data precedent for Git metadata plus on-demand content-addressed retrieval.
- **BagIt and RO-Crate at publication boundaries:** BagIt supplies portable payload manifests; RO-Crate supplies provenance and relationships. Neither needs to become the live internal storage model.
- **Gate-directed hydration:** the existing reached-gate calculation can drive an external-object fetch plan. Each gate declares object digests; CI fetches only the objects needed by that shard.
- **Named sparse profiles per linked worktree:** all eight worktrees share the Git object database but may materialize different directory sets.
- **Digest-admitted local caches:** the existing source-cache fetcher already restores ignored content from external locations under checksum control.
- **Pinned sparse external checkout:** the repository already implements exact-commit, blobless retrieval in `ci/fetch_open_gororoba.sh`.
- **Software Heritage plus verified Git bundles:** the repository already archives source history through these mechanisms (`docs/runbooks/repository-archive.md:1`). Software Heritage preserves Git history; it does not substitute for external data payload custody.
- **Generated-at-read indexes:** `scripts/results_index.py` joins runs, jobs, acquisitions, claims, and paths without committing another stale catalog (`docs/runbooks/results-index.md:1`).
- **Existing public dataset mirror:** the `gororoba-retained-runs` Kaggle dataset is already a checksum-matched external-data precedent. Provider publication and lifecycle rules prevent treating Kaggle as an automatic default.
- **Import-boundary enforcement:** package architecture requires a checked dependency policy. Re-export shims alone can hide permanent cycles.

## Overall verdict

The brief measures the repository well but draws three weak recommendations from those measurements. The private relocation does not solve historical clone size; age-out lacks an authoritative promotion and reachability model; and the five-package taxonomy preserves known dependency cycles. The sound program is lifecycle-based retention, producer-side content addressing, named sparse materialization profiles, public external custody for large reviewable data, and interface extraction before directory movement.
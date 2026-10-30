I'll start by reading the review skill and the brief, then check the repository facts it relies on.The brief is a storage-layout design, so I’ll verify its measured numbers and the mechanisms they rest on before answering the seven questions.I’ll verify the brief’s numbers and the gate, dry-run, and `isa.qpy` mechanisms in parallel so the verdicts rest on the tree, not the author’s table.HEAD is `dbee0d02`, not the brief’s `a1d1743`. I’ll check that commit, the plan record, and the dry-run / gate machinery next.The measured facts check out. The author’s doubts are stronger than the recommendations they are attached to.**Artifact.** A storage-layout design brief for a public research git repository (quantum hardware records, exact algebra, formal proofs). **Field.** Build/reproducibility, research-data archival, and import-graph architecture.

**Visibility.** The brief was read in full. Numbers were checked against `ci/gates.json` (633 gates, 136 with `cwd: gororoba_quantum`, 99 with a `replays` field), `gororoba_quantum/live_run.py` (8,486 lines), `git count-objects` (914.76 MiB in 2 packs), `ci/fetch_open_gororoba.sh`, `scripts/check_markdown_links.py`, `.github/workflows/{pr,ci}.yml`, `docs/evidence/a5-exceptional-fibers/README.md`, `results/live/unretained-dry-run-logs/README.md`, and the submission rule in `docs/notes/ibm_quantum/qpu-submission.md`. The 7.03 GB / 2,541-blob census is accepted as measured at `a1d1743`; HEAD is `dbee0d02`, one commit later.

The six-class table is the right decomposition. Observation 1 (clone size vs checkout size) and observation 2 (unbound producer output is the only iteration-proportional class) are the load-bearing facts. Several of the marked recommendations fight those facts.

---

### 1. Storage class of dry-run records

**Verdict.** Unbound producer output with a digest identity, promotable to bound evidence at `--submit`. Enforce that with the producer. A digest-bound ledger of every dry run is the wrong instrument. Age-out of the 16 unreferenced directories is hygiene, not a storage program.

**Mechanism.** The approval rule already binds a dry run by digest: `--approved-record` plus `--approved-record-sha256` of `record.json`, plus `submission.qpy_archive_sha256` against `isa.qpy`, plus per-group `calibration_fingerprint`. `qpu-submission.md` then consumes that token by writing `approval-consumed.json`. After a successful collect, the bound evidence is the collected run and `raw/<job_id>/`. Before that, the dry run is a plan that *can* become the approval token.

That token has a short physical lifetime. Backends republish calibration many times a day; any fingerprint value that changed refuses the submit. A week-old dry run is archival description of a plan. It is no longer a live approval.

The 2.2 GB in `results/live/` is almost all referenced (338 of 354 directories). The 16 unreferenced directories are 54 MB. Age-out of those 16 does not touch the growth driver. The growth driver is what `live_run.py` writes per iteration: a full `isa.qpy` copy (277 MB of the 463 MB redundant checkout bytes) and `shot_allocation.allocation_search.candidates` (81 MB, 20.3 MB of one 24 MB record). Git already stores identical blobs once, so those copies cost checkout, not clone. The producer change (content-addressed archive, candidates sidecar) is the class-correct lever, and it applies to new runs under the existing dual-read rule (retained directories keep `isa.qpy`).

The current doctrine sentence, “dry runs are therefore evidence of what was planned, not scratch,” names the *identity* (the plan digest, policy, fingerprints, QPY hash). It does not require keeping every rejected allocation candidate and every duplicate archive forever. Collapsing those two claims is how the tree got here.

**Attack.** The marked recommendation “age-out plus the producer changes” puts the weak tool first. The directory `results/live/unretained-dry-run-logs/` already exists. Its README records five lost dry runs and states that a record lost this way cannot be regenerated, because a dry run reads the live Target at that instant. Extending that graveyard as policy repeats a demonstrated data-loss pattern in exchange for 54 MB.

**Falsifier.** A measurement that unreferenced dry runs, or dry runs whose calibration fingerprints can no longer match, are the dominant term in `results/live/` growth; or a submit path that accepts a dry run without the on-disk `record.json` and `isa.qpy` bytes. Either result would move the class.

---

### 2. Sparse-checkout plus blobless clone, with no bytes moved

**Verdict.** Sufficient for the *checkout* problem on the build host and for PR CI. Insufficient for the *clone-size* problem, and not in cone mode as written.

**Mechanism.** Git worktrees share the object store. The 8 × 7.03 GB cost is working trees, plus 8 × 330 MB of `.mypy_cache` keyed under the working directory. `git clone --filter=blob:none` fetches commits and trees; blobs arrive when a checkout needs them. Combined with a per-worktree sparse list, a code worktree materializes on the order of the 17 MB of code and tests, and the first worktree to need a blob pays the fetch once into the shared store.

This repository already ships that pattern: `ci/fetch_open_gororoba.sh` runs `sparse-checkout init --cone`, `sparse-checkout set`, and `fetch --filter=blob:none`. GitHub’s `actions/checkout@v7` accepts `filter` and `sparse-checkout`. `pr.yml` currently does a default checkout into an 8-minute lint/types/tests budget on a tree whose tracked checkout is 7.03 GB. `ci.yml` uses `fetch-depth: 0` because `core-ascella-predecessor-source-pin` walks ancestry; that needs commits, not the a5 working blobs.

Gates that would break are the ones that *open* an excluded path. `docs/evidence/a5-exceptional-fibers/working/` is bound by no ledger; `ci/gates.json` names it only to exclude it from Ruff and mypy. `scripts/check_markdown_links.py` (gate `core-611`, PR tier, 1.0 s) already skips walking `working/` as a source, and resolves targets against `git ls-files` (the index, which sparse-checkout keeps). A fragment check calls `Path.read_text` on the target; a link from a non-excluded file into `working/` with a `#anchor` fails on a sparse worktree. That is a local and PR-gate break, repairable by treating those targets like the other excluded prefixes. Nightly audit does not need `working/` today. Inventory scripts that `os.stat` a skip-worktree path fail; `git ls-files` does not.

**Attack.** Cone mode cannot cheaply drop one nested 2.20 GB directory. `docs/evidence/` has 164 children. Cone inclusion of `docs/evidence` materializes `working/`. Excluding it in cone mode means listing the other 163 evidence directories plus every other wanted prefix. The working pattern is non-cone with a negative:

```
/*
!/docs/evidence/a5-exceptional-fibers/working/
```

The same shape already exists for vendor captures in the link checker’s `EXCLUDED_PREFIXES`. Sparse-checkout also does not shrink the 915 MB pack. It changes what a worktree and a PR job write to disk.

**Falsifier.** A PR-tier or nightly gate whose tracer read-set includes `working/` (or another excluded prefix) and fails when that path is absent from the worktree; or a measurement that blobless fetch of HEAD’s trees still pulls most of the 915 MB because the wanted sparse set covers the bulky prefixes.

---

### 3. Clone-size ranking (915 MB, no force-push)

**Verdict, ranked under the harness constraint that history is never rewritten:**

1. **Procedure, not migration: blobless clone plus sparse checkout**, in worktrees and in `actions/checkout`. History stays. Pack stays. Checkout and CI stop paying 7 GB.
2. **Storage-class rule for *new* bulk.** Future a5-scale diagnostic trees follow `docs/local/a5-failed-runs/` (gitignored, 2.1 GB already on disk in one checkout) or a public data repository cited by URL and sha256. This is the only lever that stops the pack from growing.
3. **Do nothing to existing history.** The 915 MB pack is already unique compressed content. Duplicates are free in the pack. Producer slimming of `isa.qpy` copies does not shrink it.
4. **Zenodo (or GitHub Release) snapshot of the a5 working tree**, with `split.txt` and the sha256 manifest retained here. A frozen, citable deposit of diagnostic data. It does not shrink git and it is not a working store.
5. **A separate public data repository** for that class, same owner. Right home for *new* unique blobs. Existing blobs remain in this history until a rewrite.
6. **LFS, git-annex, DVC.** All three put pointers in git and bytes elsewhere. Pointers going forward leave the old blobs in the 915 MB pack. Migrating existing files without a rewrite stores both the blob and the pointer. GitHub LFS also bills bandwidth; twelve nightly shards smudging 2.2 GB is the cost model, not the 10 GB storage quota. git-annex needs a special remote; the build host is at 90% disk, so a directory remote on the same disk does nothing. DVC defaults to a different hash and a lockfile this repository’s sha256 ledgers do not use.

**Attack.** The marked recommendation to move the a5 bundle into `gororoba-quantum-documents` fails on class and on clone size. That sibling repository exists for `redistribution: excluded_without_permission` reading copies, restored by `scripts/fetch_source_cache.py --from-documents`. The a5 tree is this project’s own Singular logs over \(\mathbb{F}_{32009}\). Its README calls it “the data [the findings note] rests on” and also “diagnostic working data” that enters claims only through the kernel-attachments ledger. Putting it in the copyright-restricted PDF store mixes those classes, does not drop the 915 MB pack, and hides the working record from a public clone. The author’s own doubt (“the clone cost does not drop without a rewrite; a per-bundle move does not scale”) is the correct recommendation. Write the storage-class rule; leave the bytes.

Software Heritage already archives public GitHub repositories. A separate SWH deposit of git-tracked bytes is redundant. It becomes useful only if the bytes leave git.

The remaining way to drop the 915 MB is a successor repository whose default branch never contained the blobs, with this URL kept as the historical object store. That is a new canonical remote, not a force-push. The brief does not list it. For a two-person team with eight worktrees it is nuclear, and unnecessary if (1) and (2) run.

**Falsifier.** GitHub refusing further pushes because of repository size; or a unique-blob growth rate that adds hundreds of megabytes per month after the producer stops writing duplicates. Either one promotes a successor repo or an external store for *new* bytes. LFS/annex/DVC become competitive only if a rewrite is allowed, or if new unique blobs are born as pointers and CI is shown not to smudge them on PR jobs.

---

### 4. Content-addressed `isa.qpy`

**Verdict.** A resolver over the 48 call sites is the right shape. A relative path in the record is a second identity for an object that already has `submission.qpy_archive_sha256`.

**Mechanism.** Readers currently hardcode `run_dir / "isa.qpy"`. Changing them to read a new record field is the same blast radius as a resolver, paid 48 times in slightly different forms. The dual-read rule already required by AGENTS.md (“a run collected under an earlier revision replays unchanged”) is one function:

```python
def qpy_archive_bytes(run_dir, record) -> bytes:
    local = run_dir / "isa.qpy"
    if local.is_file():
        data = local.read_bytes()
    else:
        digest = record["submission"]["qpy_archive_sha256"]
        data = (archives_root / f"{digest}.qpy").read_bytes()
    actual = sha256(data)
    if actual != record["submission"]["qpy_archive_sha256"]:
        raise ...
    return data
```

Retained directories keep `isa.qpy`; new dry runs write `results/live/archives/<sha256>.qpy` once. `adjudicate.py` already compares those bytes to the checkpointed digest. Gates that bind retained runs keep reading the local file.

A relative path can drift from the digest (path says one object, hash says another). The digest is already the approval identity. The 48 sites have to change either way; putting the convention in one tested function is the smaller contract.

**Attack.** “The record carries a relative path so readers need no resolver” is false. Those readers do not consult the record for the path today. They will need new code in all 48 sites regardless. The plan step `circuit-archive-store` in `docs/state/plans/repository-layout-reconciliation.json` already has this right; the brief’s doubt is the one to drop.

Same resolver shape applies to the other duplicate groups the brief lists and then ignores in the options: IQM `metrics.json` (24.6 MB), Quandela (22.5 MB), Kaggle (11.8 MB), `circuit.json` at 342 paths (3.6 MB). `isa.qpy` is the largest, not the only instance of “record already has the digest, producer writes the copy anyway” (observation 5).

**Falsifier.** A reader that cannot be pointed at a helper (a shell `sha256sum -c` line, a gate that opens the path as a literal in `cmd`) in enough numbers that a record-relative path is the only way those commands stay stable; or an archive store that has to live outside `results/live/archives/` per run family, so a single convention cannot resolve it.

---

### 5. Package hierarchy

**Verdict.** The import graph does not justify five subpackages as the next cut. It justifies making a package, then splitting `live_run.py` in place. The author’s doubt is correct; the recommendation is not.

**Mechanism.** The five hubs are `parallel` (57), `cd_core` (33), `experiments` (30), `live_run` (26), `experiment_optimizer` (19). Three of those five land in the proposed `hardware/` package. The prefix clusters (`correction_*` 14, `rank_*` 6, `msq_*` 5, …) are a vocabulary cut, not a graph cut. `cd_core` is already the algebra specification; `parallel` is already the spawn pool. Those two are real leaves. `live_run` / `experiments` / `experiment_optimizer` are a strongly connected hardware blob.

Cost of splitting the 8,486-line hub is the dominant term, and it is paid in this repository’s own rules: every change to `live_run.py` or `experiments.py` requires a dry run writing `results/live/`. The 26 importers, `runtime_contracts.py` comparisons, and planning contracts move with the section boundaries (calibration, planning, compilation, submission, collection — those functions are already named in the file). An in-place split with `live_run.py` as a facade leaves the 136 `cwd: gororoba_quantum` gates and the 259 `sys.path` insertions untouched. Moving the pieces into `hardware/` during the same wave couples that cost to 136 gate rewrites, the test imports, and the scripts.

`__init__.py` only, files flat, is the transition the design already describes (`import live_run` and `from gororoba_quantum import live_run` both resolve). That is the justified first PR. Five-subpackage waves after the hub is split, if the new modules actually cluster. Doing the directory taxonomy first is a 136-site rename whose scientific surface is still one 8,486-line module.

**Attack.** “The 136 gates and 259 scripts are rewritten once per cluster and the clusters are already what the names say” treats a rename as the work. The names say `correction_*` lives together. The import graph says `live_run` is what everyone calls. Rewriting gates to `from gororoba_quantum.hardware.live_run import ...` while `live_run.py` is still 8,486 lines is a move with no new testable boundary.

**Falsifier.** A measured SCC or import-cycle map in which `infra` / `algebra` / `hardware` / `analysis` / `providers` are nearly disjoint except for the five hubs as one-way edges; or a split of `live_run.py` that fails because section boundaries share so much private state that a facade is a lie. The first would revive the five-package cut. The second would argue for leaving the hub whole.

---

### 6. Documentation maps

**Verdict.** Keep two entry documents with disjoint jobs: `docs/README.md` as the area map, `docs/INDEX.md` as the source index. Generated catalogs are views, each linked once. The rule that keeps this minimal is already in AGENTS.md (“A fact has one home”). The defect is 107 shared targets, not the existence of two files.

**Mechanism.** `docs/README.md` already opens “This page is the single entry to the repository’s documents.” `docs/INDEX.md` already opens “Source index” and owns `SOURCES.json`, license evidence, and reading copies. Those are the right two roots for a repository with 164 evidence bundles, 2,906 notes files, and a claim registry. `docs/state/plans.md` is the planning entrance (also already doctrine). `plan-catalogue.md`, `RESEARCH_STATE.md`, and `QPU_RUN_CENSUS.md` are generated projections of JSON records.

A third map is the failure mode. 107 shared targets means a reader cannot know which file is authoritative for a given area, so both rot. The vendor-capture overload (2,413 of 2,906 notes files) is a placement error (`docs/captures/` in the design) that the maps then amplify by linking into both authored guides and captured trees.

Minimal set: `AGENTS.md` (rules), `docs/README.md` (areas and task entries), `docs/INDEX.md` (sources only), `docs/state/plans.md` (work records). Everything else is a link from one of those four. The acceptance already written in the plan record is the falsifiable form: “the two files share no link target outside the source hubs.”

**Falsifier.** A newcomer task whose first step is not one of those four entries (a hardware submit, a source note, a gate replay, a plan update) without adding a fifth root; or a measurement that `INDEX.md`’s non-source rows are the pages people actually use, so collapsing them loses navigation the area map does not replace.

---

### 7. Mechanisms and precedents the brief missed

1. **This repository already runs blobless sparse clone** (`ci/fetch_open_gororoba.sh`) and **already restores a private sibling by digest** (`scripts/fetch_source_cache.py --from-documents`). The options under review are local precedents, not foreign tools.

2. **This repository already age-out dry runs**, into `results/live/unretained-dry-run-logs/`, and already recorded that those plans cannot be regenerated. The age-out recommendation extends a known lossy path.

3. **GitHub’s 100 MiB blob limit** is why `working/` files over 50 MB are split into 45 MB parts (`docs/evidence/a5-exceptional-fibers/README.md`). LFS is the vendor’s intended escape from that limit; it is also how CI would start paying bandwidth.

4. **GitHub’s ~1 GB recommended repository size.** The 915 MB pack is already there. The urgent lever is unique-blob growth, not duplicate checkout bytes.

5. **`actions/checkout` filter and sparse-checkout on `pr.yml`.** Lint, types, and tests are 8-minute jobs on a 7.03 GB tree. Hosted runners in the retained CI sample had about 16 GB of memory; disk is the same order. A full checkout is a CI budget item the brief never prices.

6. **`ci.yml` `fetch-depth: 0`** is required for ancestry gates. Partial clone still fetches commits and trees; it does not require a5 blobs. Treating “nightly audit needs the bytes locally” as “nightly audit needs every blob in HEAD” is the confusion observation 4 already forbids.

7. **Calibration-fingerprint lifetime** as the dry-run retention clock. Approval tokens expire in hours. Archival identity is the digest. Those are different retention policies on the same directory.

8. **Non-cone negative sparse patterns**, required because `docs/evidence/` has 164 children. Cone mode is the wrong mode for “exclude one nested bundle.”

9. **Dual-read is already doctrine.** Producer before readers, both shapes accepted. That is why the `isa.qpy` resolver is forced, and why in-place slimming of *old* `record.json` files is forbidden if a case recorded their digest.

10. **The other CAS duplicates** (IQM/Quandela/Kaggle metrics, 342 copies of `circuit.json`) are the same observation 5, omitted from the options.

11. **`.mypy_cache` under the working directory** (330 MB × 8) is named in the measured table and already has a planned fix (`ci/pinned_tool.py` → `XDG_CACHE_HOME`). It is a checkout-cost lever that needs no owner decision and no sparse-checkout.

12. **`docs/local/a5-failed-runs/` (2.1 GB, gitignored)** is the working precedent for unbound diagnostic Singular output. The tracked `working/` tree is the exception, not the rule.

13. **A successor repository** (new default remote whose history never contained the blobs) is the only clone-size drop that respects “no force-push.” It is still disproportionate if sparse clone plus a new-bulk rule run.

14. **Kaggle kernels embed evidence as `BUNDLE = "..."` strings.** That is another duplication path, outside the 2,541-blob census if those strings are generated per kernel.

15. **Software Heritage auto-archival of public GitHub**, GitHub Releases (2 GB per file) as a non-scholarly cousin of Zenodo, and `git maintenance` / `features.manyFiles` / index v4 for a 28,759-file tree. Operational, not architectural, and cheaper than DVC.

---

### Steelman

The brief’s class table is the design. Clone size and checkout size are different numbers with different levers; unbound producer output is the only class that grows with iteration; immutability is a property of *bound* bytes; content-addressed `isa.qpy` is already half-implemented; a package hierarchy is a rename whose cost is the number of sites that name a module. Those six observations survive. The producer-side archive store and candidates sidecar should proceed without waiting for owner theater. Caches out of the checkout should proceed the same day.

### Verdict

The core is sound and the marked recommendations for the a5 home, dry-run age-out, and five-subpackage split are the parts that do not follow from it. The storage-class rule the author asked for is: bound evidence stays, new unbound bulk never enters this git history, checkout cost is sparse/blobless plus caches under `XDG_CACHE_HOME`, clone cost of existing history is accepted. What would earn trust is one PR that (i) moves the mypy cache, (ii) writes `isa.qpy` once by digest with a dual-read resolver, (iii) documents the non-cone sparse pattern and wires it into `pr.yml`, and (iv) records the a5 tree as unbound diagnostic data that remains at its path because the harness forbids a rewrite. The three “owner decisions” collapse to that rule; they are not three independent knobs.

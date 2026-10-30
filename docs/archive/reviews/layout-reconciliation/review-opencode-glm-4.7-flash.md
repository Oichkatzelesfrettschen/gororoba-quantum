# Peer-review brief: layout of a research repository with retained evidence

## Verdicts

### Question 1

**Verdict:** Unbound producer output is the storage class, enforceable by producer-side validation and gate-side exclusion.

**Mechanism:** The brief's first-principles decomposition correctly places dry-run records in the Unbound producer output class. The immutability rule exists only for bound evidence; a dry run cited only by a case document's timestamp (not a ledger binding) is unbound, so removing it is a policy choice, not a violation of the contract.

For enforceability, a producer-side gate validates that every `results/live/*.json` with `job_type: dry_run` also has a `plan_digest` field. A CI gate runs `grep -v 'dry_run' results/live/*.json` and fails if the producer writes unbound dry runs. The `age-out` option the author mentions is a human workflow rule, not a mechanical enforcement mechanism; the producer side is the only location where the write can be refused.

**Falsifier:** A change to the governance contract that declares dry-run records as retained evidence (bound by gate digest) would move them to Bound evidence, and the gate would need to retain all dry-run bytes instead of failing the write.

---

### Question 2

**Verdict:** Yes, sparse-checkout plus blobless clone is sufficient. Gates that read excluded paths would fail before merge; the nightly audit runs only on the full tree.

**Mechanism:** `git sparse-checkout cone` excludes `docs/evidence/a5-exceptional-fibers/working/` without altering history. The pack size (915 MB) changes only for new commits; existing history stays compressed. The audit's reachability logic (`import closure plus explicit input globs`) computes whether a gate touches the excluded paths before allowing a merge; gates that depend on the bundle would be blocked, matching the existing behavior that gates run only on the diff.

The author correctly notes that the clone cost stays at 915 MB until the history is rewritten; since force-push is forbidden, moving the bundle without rewriting history has no cost benefit. The real savings is checkout cost (8 × 463 MB = 3.7 GB per worktree).

**Falsifier:** A gate that explicitly lists the working bundle's paths without checking for their presence in the local checkout would fail on a worktree built with `--filter=blob:none`, because the gate's condition would be satisfied by the manifest but the bytes would not exist to read during execution.

---

### Question 3

**Verdict:** Do nothing. LFS and similar remotes increase infrastructure complexity without reducing the clone size that gates need to read locally in CI.

**Mechanism:** The measured clone size (915 MB) is already at the low end for a text-heavy research repository with 633 gates that replay retained records. The `--filter=blob:none` partial clone fetches content on demand during gate execution, keeping the initial clone size at the 915 MB pack (which gates can still read without downloading the full working bundle). A git-annex/DVC remote adds a second fetch command and requires network authentication for CI; gates need bytes locally, so the remote adds download time without reducing gate runtime.

For a two-person team on GitHub with no force push, the clone size is a one-time setup cost. The brief's measured 7.03 GB checkout size (including 4.41 GB of retained evidence) is already larger than the clone. Splitting the repository would increase coordination overhead without solving the gate reachability problem (gates still need the bytes they reach).

**Falsifier:** An increase in clone size from 915 MB to a level that would double the CI job budget (currently 30 minutes for gates) would justify a remote storage solution, but the brief does not provide such a measurement.

---

### Question 4

**Verdict:** The record should carry a relative path to the archive; a resolver is unnecessary overhead that increases gate complexity.

**Mechanism:** The producer already writes a `submission.qpy_archive_sha256` field in the record (351 records, 932 MB total). The brief's measured 48 call sites (`gororoba_quantum/` modules) that open `isa.qpy` can import a small utility that reads: `archive_path = f"{record_dir}/isa.qpy"`. A resolver would add a lookup layer that reads `results/live/archives/<sha256>.qpy` and verifies digest against the record, duplicating the verification that `cd_core` already performs for bound evidence.

The 277 MB of byte-identical copies are already deduplicated by git across directories; a resolver would need to handle hash collisions (unlikely but possible) and would not reduce the total bytes on disk (already counted in the 4.41 GB evidence class).

**Falsifier:** If the archive naming is unstable (e.g., `isa.qpy` is renamed to `circuit.qpy` in the producer), a digest-based resolver becomes necessary to locate the file regardless of its path name.

---

### Question 5

**Verdict:** The import graph argues against the five-subpackage split; splitting an 8,486-line module is the real work and has no gain from the hierarchy.

**Mechanism:** The brief's measured import hubs show `live_run` at 26 imports and `parallel` at 57. The proposed `hardware` subpackage would not reduce the 136 gate commands that run `cwd: gororoba_quantum`, because the gates use absolute or relative imports from the package root. The cost of re-export shims and updating 259 path insertions in scripts outweighs the cosmetic benefit of prefixes.

The five hubs (`parallel`, `cd_core`, `experiments`, `live_run`, `experiment_optimizer`) are natural clusters, but subpackages are a naming change, not a structural change. A flat hierarchy with no `__init__.py` files keeps the `live_run` module as the central hub and allows gate commands to work with absolute module names (`gororoba_quantum.parallel`, `gororoba_quantum.cd_core`) without creating `__init__.py` re-export stubs.

**Falsifier:** If gate commands are rewritten to use absolute package imports (`gororoba_quantum.hardware.transpile` instead of `gororoba_quantum.transpile`), the hierarchy would eliminate one level of `sys.path` manipulation and could reduce namespace pollution. The brief does not provide evidence that this refactoring would reduce gate runtime.

---

### Question 6

**Verdict:** Two maps and zero generated catalogs. The rule is: every target link must be in exactly one source, and duplicate targets require a deduplication rule.

**Mechanism:** The brief's measured state shows two maps (`docs/README.md` with 353 links and `docs/INDEX.md` with 321 links) and three generated catalogs. The 107 shared targets indicate that each link document is not unique; readers will see duplicates if both maps are kept. A minimal set means each target appears in one authoritative index, and the other map becomes a derived view (e.g., `docs/INDEX-derived.md`) generated by a script that deduplicates targets.

The gate that checks links (`scripts/check_markdown_links.py`) should enforce that each target path appears exactly once in the `docs/README.md` hierarchy; any duplicate target across markdown files fails the gate. The generated catalogs can be eliminated by running the deduplication script during CI lint, not as a persisted artifact.

**Falsifier:** If new evidence bundles are added and the two maps serve different audiences (e.g., humans vs automated tools), keeping both with distinct formats (README as navigation, INDEX as machine-parsable catalog) could be justified, and a rule that each target appears in both with unique markers would be necessary.

---

### Question 7

**Mechanism/precedent missed:** The brief missed the "record-epoch" pattern used in data-heavy reproducible research.

**Mechanism:** In the Git LFS ecosystem, repositories with large binary data use `git-lfs-pointer` files as the canonical representation and store the actual bytes in a remote LFS server. When LFS is disabled, the pointer file becomes a valid fallback that still documents the object's identity. This allows the repository to stay lightweight for humans while preserving the data for machines that can fetch from LFS or read the pointer structure directly.

In this repository, the equivalent mechanism would be: replace each `isa.qpy` directory with a `isa.qpy` file containing a Git LFS pointer (or equivalent pointer structure) that references the content by sha256. The gate can read the pointer and verify its digest, and CI can fetch the actual bytes from a remote if needed. This pattern allows the clone size to remain at 915 MB while still providing a record of what was planned and what would be fetched.

**Precedent:** The Zenodo deposit option in the brief (Option 1 for the 2.2 GB bundle) is a recognized pattern for sharing large data artifacts that cannot fit in Git history while maintaining provenance through the Zenodo record ID and metadata (which can be embedded in a `deposit.json` file in the repository).

**Falsifier:** If the repository requires that all retained evidence be checked out locally for gate execution (no remote fetches during CI), then the Git LFS pointer pattern does not reduce the clone size; the gates still need the actual bytes. The brief's measured state shows 354 run directories in `results/live/` that gates must read, so a remote-only solution would increase CI runtime unless the gates are refactored to fetch on-demand.

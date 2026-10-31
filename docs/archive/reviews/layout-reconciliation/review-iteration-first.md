# Third review: iteration first (owner-supplied, 2026-10-30)

The owner supplied this review of PR #688 at `0df906f6` from an external model session. It is retained
verbatim below. Its source claims were checked against the tree before the design document adopted or
refuted them ([design document](../../../design/repository-layout-reconciliation.md), section
"Falsification"): `ci/pr_checks.sh` line 105 passes `--affected-ledger` and line 106 the 15 s cutoff;
`.github/workflows/ci.yml` line 152 selects `--ledger-audit` on schedule and dispatch; `AGENTS.md`
line 503 couples retention to a citing claim; the module-identity claim about `__init__.py` follows from
the import system's cache keyed by module name.

---

**The storage and dependency corrections are sound, but they do not yet solve the working-experience problem.** The proposed program still makes too much ordinary development behave like preparation for an archival release.

For the team you describe, the governing objective should be:

> Minimize the time from a scientific question to trustworthy, interpretable evidence—without losing data, corrupting shared work, spending unapproved resources, or promoting speculation into an established result.

That calls for a small research workflow with automated safeguards, not more arbitration. The directory-first approach should be superseded by an **iteration-first approach**: improve the development loop, fix the producers that create unnecessary work, and restructure modules only where doing so removes a demonstrated obstacle.

The findings below refer to PR #688 at `0df906f6` and its base, `a1d1743`, rather than an assumed later state.

## 1. The procedural burden is real—and it has identifiable causes

The current rules require the Codex review loop to continue until the current head receives a clean signal, followed by an operator review and another final Codex review. They also require a live dry run whenever `live_run.py` or `experiments.py` changes. Those requirements apply broadly, rather than according to what behavior the change affects.

That is the first place to simplify. An archive-resolver extraction, a numerical-method change, an approval-bypass fix, and a documentation correction should not all encounter the same review ceremony.

There is another consequential coupling: the records section requires a retained acquisition to enter the research registry **with a claim citing it** in the change that retains it. That makes data preservation depend on interpretation. An acquisition should be retainable before anyone has worked out what it means.

The replacement should be straightforward:

**Capture the evidence immediately. Interpret it when warranted. Review the interpretation before treating it as established.**

Likewise, replace the blanket live-dry-run requirement with tests against a retained calibration snapshot for changes that should be behavior-preserving. Reserve a fresh provider read for changes involving current provider behavior, calibration admission, or actual execution readiness. A fresh snapshot is useful for those questions; it is an uncontrolled extra variable in an ordinary refactoring test.

The proposed documentation ownership check also goes too far. PR #688 would require one parent entry per authored document and prevent most overlap between the two maps. One canonical document per maintained fact is sensible; one navigational parent per document is not necessary. A geometry result can legitimately be reachable from its mathematical question, hardware experiment, and proof obligation. Navigation should support those relationships rather than force them into a single-parent hierarchy.

**Keep canonical content. Allow multiple useful routes to it.**

## 2. Make exploration cheap; make evidence capture automatic

The everyday working loop should be:

**Question → smallest discriminating computation or experiment → inspect the result → challenge the interpretation → choose the next experiment.**

It should not require a new design document, work-plan entry, review archive, claim record, and full replay cycle every time around.

### Ordinary development

An agent begins with a bounded task: the question, relevant files, known constraints, and what observation would count as progress. That context can live in an existing research note or PR description. It does not need a new schema.

The agent edits code, runs focused checks, explores alternatives, and records the useful conclusion. Exploratory code can be integrated when it is appropriately tested and clearly identified; merging a useful experimental tool must not imply that its scientific hypothesis is established.

Most failed attempts need a concise explanation, not an archived conversation. Preserve the inputs and outputs of failures that constrain the science, reveal an important numerical failure, consume external resources, or cannot be reconstructed. Do not make every abandoned prompt a permanent research artifact.

### Evidence capture

The runner—not the human or LLM—should record the source revision, any uncommitted source changes needed to reconstruct the run, parameters, seeds, input identities, environment, execution status, and output hashes.

A Git commit alone is insufficient when the experiment ran from a modified worktree. Capture the patch or an equivalent source snapshot automatically.

There should be no "fill in the provenance paperwork" step after a promising result. The information should already exist.

Also distinguish **retained data from disposable cache contents**. Downloaded copies of durably stored artifacts can be cached. The only copy of an acquisition or costly computation cannot.

### Scientific promotion

A result becomes a supported claim only when its assumptions, evidence, relevant checks, and limits have been examined. Use the existing research-state registry for that transition; do not introduce a parallel certification system.

An experiment can therefore be:

- Preserved but not yet interpreted.
- Interpreted but still exploratory.
- Used to support a bounded, reviewed claim.

These are distinctions in meaning, not three mandatory meetings or three new documents.

This makes uncertainty usable. "This finite-field calculation excludes the proposed model at these inputs" is a valuable outcome. "The global topology remains unresolved" is not a failed CI job.

## 3. Give CI three explicit jobs—and stop conflating them

The existing CI is not purposeless. Its purposes are obscured by how the work is scheduled and presented.

The PR workflow runs linting, typing, the non-audit pytest suite, and affected gates subject to a default **15-second per-gate measured-duration cutoff**. The restored ledger helps determine which gates are affected. However, the ordinary PR command passes `--affected-ledger`, not `--ledger`: it uses previous read sets for selection without enabling the runner's unchanged-result reuse mechanism.

The nightly workflow deliberately does something different: it runs every gate through `--ledger-audit`, including checks that a normal ledger-enabled run would reuse. Its purpose includes detecting cases where the reuse mechanism would incorrectly skip a failing check. That is a legitimate audit—not an independent new scientific measurement.

The replacement should expose three clearly separated answers:

| Check family | Question it answers | When to run it |
|---|---|---|
| **Integration checks** | Does this change preserve the affected software contracts and safety boundaries? | On the proposed integration, with focused local equivalents during development. |
| **Evidence checks** | Are the affected retained artifacts intact, and do the claimed results still follow under their declared reproduction contract? | When relevant inputs, producers, checkers, environments, or claims change; otherwise reuse a valid receipt. |
| **Independent audit** | Did dependency selection, caching, environment assumptions, or portability checks miss something? | A bounded rotating sample, plus full cold runs for releases, major environment changes, and changes to the verification machinery. |

These are scheduling modes of the existing system, not a proposal for three new platforms.

### Select by relevance first, cost second

The present duration cutoff is an understandable scheduling shortcut, but **duration does not determine whether a check matters**.

An affected approval-integrity check cannot become optional because it takes sixteen seconds. Conversely, an unrelated historical replay should not block a documentation correction merely because it is cheap.

Choose the required checks from the changed contract. Then decide whether to execute them, reuse valid results, or place them in a longer-running verification job. A required check that has not completed remains pending; it must not silently become "passed."

This also separates software integration from scientific endorsement. A new exploratory analysis can land without declaring its scientific output established. A change to the submission guard, artifact decoder, or a contract relied upon by existing users still needs its relevant correctness checks before integration.

### Reuse the machinery that already exists

`ci/gate_ledger.py` already keys recorded passes using the gate command and configuration, traced file contents and directory observations, worker allocation, tracer identity, and host identity. It refuses to retain reusable entries when a run fails or its trace is incomplete. That is a substantial foundation. Another cache framework is unnecessary.

The useful work is to expose and improve its operation:

Show why a check was selected, which dependency invalidated its previous result, whether reuse was permitted, and why reuse was refused. Measure actual hit rates before promising savings.

Do not remove environment or worker-count distinctions merely to increase cache hits. Where numerical behavior depends on them, they are part of the result's meaning. Where a check is demonstrably independent of a distinction, narrow its key deliberately.

A CI summary should read approximately like this—an illustrative format, not an actual run:

```text
RUN       archive-integrity: resolver implementation changed
RUN       collection-regression: affected caller changed
REUSE     a5-finite-certificate: inputs, checker and environment unchanged
PENDING   historical-replay: required artifact unavailable
```

That communicates substantially more than "617 gates green."

### Separate preservation, replay, and scientific agreement

A checksum proves that retained bytes have not changed. A replay checks that a computation can be reproduced. A numerical comparison checks agreement under a declared mathematical or statistical criterion.

They should not be interchangeable.

Preserve exact equality for integer and finite-field certificates, immutable artifacts, and interfaces that explicitly promise bitwise determinism. For floating-point algorithms whose contract is numerical rather than bitwise, use a justified error criterion and test scientifically relevant decisions near their boundaries. Do not loosen an existing contract merely to make a failing run green.

Likewise, preserve an old result's original producer identity. A harmless edit to today's implementation should not require rewriting historical provenance. Check the historical reproduction and the current implementation's compatibility as separate questions.

### Make heavyweight CI earn its computation

Keep full cold audits available. Do not simply disable them while the selector and reuse mechanism remain insufficiently validated.

But replace the unconditional daily all-history workload gradually with targeted invalidation and a bounded cold-audit sample. Expand that sample when it finds missed dependencies or nondeterminism. Run broader audits after changes to the selector, tracer, runtime, or reproduction policy.

**CI should usually verify the output of scientific computation, not repeat the entire search that discovered it.** Where a compact certificate or a discriminating regression case suffices, retain the expensive discovery run and verify the smaller object. Where full recomputation is genuinely necessary, name that reason.

## 4. Coordinate agents with isolation and a single integration point

For one human and several concurrent agent instances, the default arrangement should be simple.

**Give each independent task its own branch and worktree, with one active writer.** A resumed agent continues that task; it does not automatically create another branch or another layer of plans. Other agents can inspect and review the same work read-only. Git worktrees provide separate working directories and indexes while sharing repository data, but they are not a substitute for coordinating shared external resources.

Record the task's intended scope in the existing PR or task note. When two tasks both need substantial edits to `live_run.py`, split out a prerequisite or sequence those edits. Do not have two agents independently perform overlapping architectural surgery and defer the disagreement to merge time.

Use one integration session to bring completed changes together. That session may be an authorized agent, not necessarily a human doing clerical work. It validates the combined result against the current base, updates generated views, and merges within the existing permission constraints.

Three details matter:

**Generate shared summaries centrally.** Agents should not independently rewrite the root README, global research-state view, and plan catalog for every local discovery. Keep their source records task-local where possible; regenerate aggregate views during integration.

**Separate shared immutable artifacts from mutable scratch.** Share verified, content-addressed objects. Give each task its own temporary outputs. Publish objects atomically so another process cannot mistake a partial write for a completed artifact.

**Coordinate actual scarce resources.** Worktree isolation does not stop two agents from oversubscribing the GPU, consuming the same QPU allowance, or mutating a shared environment. Use the existing budget and execution controls for those resources. Preserve approval-bound, single-use submission safeguards. Ordinary offline edits should not require renewed permission.

### Replace ritual review with targeted review

Routine changes should receive the checks appropriate to their scope. Substantive changes should receive one focused independent review of the relevant risk. A later edit requires additional review when it materially changes the reviewed behavior—not automatically because the commit identifier changed.

Changes to billing, authorization, destructive operations, artifact integrity, or scientific conclusions deserve stronger scrutiny. A second reviewer is useful when examining a different failure mode: for example, mathematical validity versus implementation correctness.

Two LLMs agreeing is not a proof. A counterexample, an executable regression, an independently derived calculation, or a checked certificate is more useful than another general "review everything" round.

This changes the current review policy; it does not authorize bypassing it before that policy change is adopted.

## 5. Keep the useful parts of PR #688, but remove the migration campaign

The public-data direction, producer-side deduplication, sparse materialization, and interface-first refactoring remain useful. They should become a few practical improvements, not prerequisites for continuing research.

### Accept the existing history; stop adding unnecessary bulk

Accept the reported 915 MB packed history. Do not spend research time rearranging already-retained blobs in pursuit of clone-size savings.

For new bulk, use a public artifact location with commit-pinned metadata and SHA-256 identities. A public data repository can provide that catalog, but putting every new payload into its ordinary Git history would merely relocate the growth problem. Keep the code repository's manifests and small replay fixtures convenient; retrieve larger payloads when needed.

Use **50 MB per file and 100 MB per bundle as initial admission guardrails**, not as a declaration that everything smaller belongs in Git. Repeated small outputs can still dominate growth.

Choose **no automatic age-out of research records** for now. Fix the producer and deduplicate first. Disposable caches can expire; unique observations and unreconstructable dry-run snapshots should not disappear because a calendar threshold passed.

### Reduce materialization without hiding missing dependencies

Use sparse worktrees and blobless fetching together where appropriate. They address different costs. The checkout action's implementation distinguishes fetch filtering from sparse working-tree configuration; filtering alone is not a promise of a small materialized checkout.

Roll this out first to jobs with clear input sets. Do not exclude evidence from all test jobs and then interpret missing files as irrelevant. PR #688 correctly identifies that the existing link checker and dependency traversal can treat absent tracked files differently from present ones. Fix that before relying on sparse selection for correctness: required inputs must be fetched or reported unavailable, never silently omitted.

The everyday command should hide these details from the researcher.

### Extract interfaces when they unblock work

Start with record/archive I/O because it directly supports deduplication and reduces the number of callers depending on `live_run.py` internals. Then extract another boundary when an active task benefits from it.

Do not require a repository-wide package redesign first.

There is also a concrete defect to correct in the proposed migration: adding `__init__.py` while permitting both `import live_run` and `import gororoba_quantum.live_run` does **not** guarantee one module identity. Python caches modules by import name. In a minimal reproduction run here under Python 3.13.5, the same source file loaded through those names produced distinct module objects, classes, and registries. That can break monkeypatching, singleton state, and class-identity checks. Use one canonical implementation identity and deliberate compatibility entry points.

Keep the dependency-boundary test. Drop the idea that all cycles must be eliminated before useful package work can proceed. Prevent new reverse dependencies across the boundary being extracted; leave unrelated restructuring for later.

### Improve navigation by filtering, not relocating everything

Default human and agent searches to authored source, tests, and current research notes. Make vendor captures, generated evidence, and historical reviews explicitly searchable without allowing them to dominate ordinary discovery.

The documented measurement that 2,413 of 2,906 Markdown files under `docs/notes/` are vendor captures explains much of the apparent documentation overload. Moving all those files is less urgent than ensuring an agent looking for your reasoning does not receive pages of captured SDK documentation instead.

## 6. Replace the long program with three deliverables

**First: make the existing CI explain and minimize its work.** Report selection and invalidation reasons, expose receipt reuse, distinguish integration status from evidence status, and replace blanket repeat-review/live-dry-run requirements with change-specific checks. Preserve the current safety baseline while validating the narrower selection.

**Second: stop expensive iteration from producing expensive repository growth.** Extract the archive resolver, write identical circuit archives once, move bulky allocation diagnostics out of the central record, and capture provenance automatically. Preserve historical readers and records unchanged.

**Third: make concurrent work and resumption ordinary.** Provide task worktrees with sensible materialization and external scratch/cache locations; centralize integration and generated summaries; keep one short task context that tells the next agent what question remains and which command produces the next useful observation.

Defer the large document moves, parent-ownership checks, wholesale package hierarchy, and archival-format expansion. None should stand between a researcher and the next experiment.

The success test is practical: a fresh agent should be able to identify the active question, reproduce the relevant baseline, run one discriminating variation, and return an interpretable result without reading the entire repository's institutional history.

**Preserve evidence automatically, verify changes proportionately, and reserve expensive computation for an explicit scientific or reliability question.** That provides the control a small research team needs without making process the repository's principal output.

*Review scope: repository documents and CI implementation were inspected; the full repository test suite was not executed, and no repository files were changed.*

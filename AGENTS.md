# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.


## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only. [ci/AGENTS.md](ci/AGENTS.md) holds the
gate machinery: runner and shards, the gate ledger and premerge cache, the
Python and Qiskit pins, replay runtimes, the Rocq replays and gate cost.

**Pull requests and the audit.** The workflow `pr.yml` runs
`sh ci/pr_checks.sh lint|types|tests` on every pull request push: Ruff and
mypy over ci/, tests/, gororoba_quantum/, scripts/ and kaggle_kernel/, and
pytest over tests/ with `-m "not audit"`. Branch protection on main requires
the three checks `lint`, `types` and `tests` green on the head; with the Codex
review loop they admit a merge ([Merging](#reviews-and-merges)), and no local
gate run or premerge replay is required. Locally, `sh ci/pr_checks.sh tests
PATH` runs the touched tests under the hosted environment; pushing needs no
exhaustive run. `ci.yml` is the audit: every gate, the retained-evidence
replays, the Rocq replays and the ledger, nightly on main and on manual
dispatch ([ci/AGENTS.md](ci/AGENTS.md)). A failing scheduled run updates the
issue "Nightly audit failing" with each failing gate and the claims citing it;
it blocks no unrelated pull request.

**Code style.** Every Python file a change touches passes, before each push,
through `"$PYTHON" ci/pinned_tool.py TOOL ARGS` (the versions of
ci/requirements-ci.txt):
- `ruff format --target-version py313` (120-column lines from pyproject.toml;
  the Python 3.13 target is the Quantum Inspire interpreter's);
- `ruff check` (pycodestyle, pyflakes, import order, bugbear, pyupgrade, S101);
- `mypy` on the touched files, and over gororoba_quantum/, scripts/, ci/,
  tests/ and kaggle_kernel/ (from gororoba_quantum/: `mypy . ../scripts ../ci
  ../tests ../kaggle_kernel`) when a change alters a signature another module
  imports.

A gate command run outside ci/run_gates.py needs `PYTHON` exported
(`export PYTHON="${PYTHON:-python3}"`); an unexported assignment expands empty
and every gate exits 127 in 0.0 s. A check raises explicitly and never uses
`assert`, which `python -O` strips. Every CPU-bound loop over independent items
runs through parallel.py, an order-preserving spawn pool, and a serial loop
over such items is a defect review rejects; items that share a seeded generator
draw every item's inputs first, in the generator's order, and then map, so
pooled and serial runs write the same bytes. A classical estimator over many
synthetic replicates (a null calibration, a bootstrap) is batched across
replicates with numpy before it is pooled, and a gate proves the batched path
returns the scalar reference's bits: it keeps the scalar arithmetic order,
repeats `sum()`'s Neumaier compensation and sends every replicate-dependent
`exp` and `** 2` through `math.exp` and `math.pow`
([vectorized-fits.md](docs/runbooks/vectorized-fits.md)). Mock outcomes
(`--native-dry-run` timing) never enter scientific analysis or measured
visualizations. Local shells, CI and Kaggle start Python with
`GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`, which the combined Qiskit
Rust and Aer OpenMP extensions require. A change to live_run.py or
experiments.py also gets a dry run, `"$PYTHON" live_run.py --out
../results/live`, whose audit record lands under results/live/. A change to
`proofs/`, a replay bundle or its receipts follows the Rocq replay of
[ci/AGENTS.md](ci/AGENTS.md#layout-and-gates).

## Work planning

[docs/state/plans.md](docs/state/plans.md) is the planning entry point. JSON records own work status;
Markdown views are generated. Capture ideas cheaply, then record scope, owner, next action and checkable
steps before committing work. Update records when scope changes, work pauses or an obligation closes.
Completion requires scope-bound receipts; scientific claims and provider approvals keep their existing
authorities. Reconcile JSON conflicts by hand, regenerate views and run `scripts/plan_tracker.py check`.
The [operator procedure](docs/runbooks/plan-tracker.md) documents commands and shared-checkout locking.

## Source library and research replay

`docs/` owns source notes, retained PDFs, retrieval identities and research
replays, and [docs/README.md](docs/README.md) is the map of every document.
`literature -> docs` preserves recorded paths; new Markdown links use `docs/`. Immutable source ledgers retain their recorded bytes. The
`sources` suite in ci/gates.json covers the source registry, the evidence
replays and their checksum ledgers.


Changes to proof replay inputs also follow the pinned Rocq replay in
`docs/evidence/folding_proofs/README.md`. Imported paper parser diagnostics
remain source limitations in the registry; checksum admission preserves the
original bytes and differs from a fresh mathematical proof check.

## Documents

[docs/README.md](docs/README.md) is the map and decides where a document
lives; read it before writing one.

- Extend before adding. A fact has one home; a second area that needs it gets
  a link, and a deduplication merges the fact up to the nearest home every
  reader reaches, never into sibling copies.
- Place by kind: a source note in `docs/notes/papers/` with its
  `docs/SOURCES.json` record; a research note in `docs/notes/topics/`; a
  provider guide in `docs/notes/<provider>/`; a design or plan in
  `docs/design/`; operator commands in `docs/runbooks/`; a replay and its
  retained output in `docs/evidence/<name>/`; generated registries in
  `docs/state/`; handoffs, session logs and review reports in
  `docs/archive/`. Session-local scratch stays in the ignored `docs/local/`.
- A new document gets its map row or an inbound link in the same change;
  `scripts/check_markdown_links.py` fails on a broken link or anchor.
- Names state target and mechanism in lowercase with hyphens; a date or
  phase label appears only under `docs/archive/`.
- Retained bytes are immutable: a file a ledger, record or digest binds keeps
  its path and bytes, and a correction lands in a new document that the old
  one's map row links.
- A move runs through `git mv` and updates every reference, ledger and gate
  in the same change.
- An AGENTS.md holds rules a session cannot derive from the tree, kept short;
  reference tables, procedures and measurements live in the docs they
  describe, with a pointer.

## Mandatory source and hardware grounding

All architectural design, code synthesis, circuit optimization, and review decisions
must be strictly grounded in verified repository sources rather than inferred or
approximated from external generalizations. Never guess or estimate hardware
specifications, timing budgets, algebraic conventions, or mathematical invariants.

Grounding binds all operations through two authoritative pillars:

1. **Heron r2 Hardware Documentation and Live Snapshots.**
   The repository maintains authoritative hardware definitions and execution constraints:
   - `docs/notes/ibm_quantum/`: Transcribed reference documentation covering processor
     families (`processor-types.md`), backend details and basis instruction sets
     (`qpu-information.md`), transpilation to ISA circuits (`transpile.md`), pass
     managers (`transpile-with-pass-managers.md`), transpiler stages (`transpiler-stages.md`),
     dynamic circuits and mid-circuit measurement (`execute-dynamic-circuits.md`),
     native fractional gate limits (`fractional-gates.md`), stretch delays (`stretch.md`),
     circuit timing (`qiskit-runtime-circuit-timing.md`), repetition rates and shot loops
     (`repetition-rate-execution.md`), calibration cadence (`calibration-jobs.md`),
     and execution time estimation (`estimate-job-run-time.md`).
   - `docs/notes/ibm_heron_platform.md`: Measured platform targets, timing alignments,
     instruction variants (`measure_2`, `reset_2`, `xslow`), and fractional-gate error
     evaluations across `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`.
   - `docs/evidence/heron_platform/targets.json`: Complete, machine-readable Target
     snapshots across all 156 qubits and 352 coupling pairs.

2. **Mathematical Papers, Notes, and Formal Proofs.**
   The repository contains exact algebraic specifications, proof certificates, and
   literature records:
   - Primary research notes in `docs/notes/` and hosted/local papers in `docs/pdf/`
     and `docs/local_source_cache/` (indexed in `docs/INDEX.md` and `docs/SOURCES.json`).
     When mathematical derivations require broader context, follow the linked arXiv
     version of record directly.
   - Proof certificates in `proofs/` and verification evidence in `docs/evidence/`
     (including Rocq formal certificates for `TargetFlipN21`, `FoldAverageDescent`,
     `TerminalChannelSeparation`, and `C881`).
   - Sedenion, octonion, and Cayley-Dickson multiplication conventions codified in
     `gororoba_quantum/cd_core.py` and the Algebra Circuit Design Rules of
     docs/notes/algebra_circuit_rules.md.

Every module, test contract, and hardware execution plan reflects these recorded sources.
When an algebraic sign, gate duration, layout connectivity, or error rate is needed, code
directly imports or validates against the registered repository artifact.


## Algebra rules and Heron r2 facts

Binding rules for circuit and hardware work, before the notes open:

- `a -> L_a` is a linear encoding, never an algebra homomorphism.
- `|0>` is `e_0 = 1`, the identity, never the zero vector. A zero product is a
  heralded branch of zero probability while the full state keeps norm 1.
- Algebra index bit `b` sits on register qubit `b` (little-endian, as in
  Qiskit outcome strings).
- A sign register needs `|->` for phase kickback; `|0>` records a which-path
  label.
- Certify every zero-divisor pair with `cd_core` before circuit work.
  `gororoba_quantum/cd_core.py` is the specification, and a package result
  enters evidence only through a declared map onto it, checked on every basis
  pair.
- A hardware probe of an algebraic property passes the mutation test (the
  ideal observable changes when the property is removed), lists its +-
  arms +, -, -, + and decides against a null arm
  ([Hardware probes](docs/notes/algebra_circuit_rules.md#hardware-probes)).
- The account reaches ibm_fez, ibm_kingston and ibm_marrakesh, all Heron r2:
  156 qubits, heavy-hex, basis cz, id, rz, sx, x and xslow. The live Target is
  the timing authority (dt 4 ns), and `service.backends()` precedes naming a
  backend.
- IBM removed pulse-level control on 3 February 2025; designs use the gate
  set, fractional gates and dynamic circuits.

The full rules, witnesses, observables and the Cayley-Dickson package table are
in [docs/notes/algebra_circuit_rules.md](docs/notes/algebra_circuit_rules.md).
The Heron r2 execution facts are in
[docs/notes/ibm_heron_platform.md](docs/notes/ibm_heron_platform.md), and the
build-host Python stack in
[docs/notes/build_host/python-stack.md](docs/notes/build_host/python-stack.md).

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- The default saved account is primary. A second saved account named
  `backup-ibm-quantum-platform` holds a different IBM Cloud instance with its
  own 600 s rolling quota, and quotas never pool. `GOROROBA_IBM_ACCOUNT`
  selects the account for every script (unset or empty selects the default) and
  stays the same for a case's dry run, `--submit` and `--collect`. The backup
  serves when the primary's remaining seconds minus the reserve fall below the
  case's summed ceilings.
- Routing. A simulation of 14 qubits or fewer runs on Kaggle kernels through
  `scripts/kaggle_run.py` ([docs/notes/kaggle/README.md](docs/notes/kaggle/README.md)).
  A 15-qubit run is decision-gated: it waits for the user's approval of a
  written case naming its substrate (an optimized Aer run on the build host or a
  Kaggle T4 x2, or Tuna-17 through Quantum Inspire) and why that one answers
  the question. IBM hardware serves 16 or more qubits, or a smaller run whose
  question concerns the device itself (a named qubit's readout, detuning or
  drift); its case states why Aer cannot answer it.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The sequence is a submit-free dry run, its analysis, the written
  case, the approval, and then `--submit` with `--approved-record` (the dry
  run's record), `--approved-record-sha256` (its record.json digest) and
  `--max-execution-seconds` (the case's seconds). The fresh plan must match the
  record or the run writes an `approval_required` record and sends nothing; the
  first batch consumes the approval by writing `approval-consumed.json`.
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates and submits, and no calibration value is cached or read back from
  a file to drive a submission. Calibration reads, transpilation, noise
  simulation, result retrieval and `--preserve-raw` need no approval.
- The binding mechanics (calibration fingerprints, prediction reuse,
  `approved_backend_scope`, `--exclude-qubits`, per-instance inventories and the
  Kaggle noise snapshot rule) live in
  [docs/notes/ibm_quantum/qpu-submission.md](docs/notes/ibm_quantum/qpu-submission.md).

## Hardware services

Future acquisition decision statements and job-specific cancellation authority
follow [the evidence-closure procedure](docs/runbooks/evidence-closure.md).
An account-wide queue grants no authority to cancel another worker's job.
The derived closure snapshot is a view; it never replaces the research registry.

Each provider guide holds the environment, credential handling, MCP
registration, backend table, limits, gates and run procedure; the live provider
pages stay the authority because they change. Tokens and keys live outside every
checkout and never enter a commit, log or memory.

- Quantum Inspire: [docs/notes/quantum_inspire/README.md](docs/notes/quantum_inspire/README.md);
  interpreter `QI_PYTHON` (Python 3.13 venv `QI_ENV`); MCP `quantum-inspire`;
  tokens in `~/.quantuminspire/config.json` through `qi login`.
- Open Quantum: [docs/notes/open_quantum/README.md](docs/notes/open_quantum/README.md);
  interpreter `OQ_PYTHON` (venv `OQ_ENV`); MCP `openquantum`; key file named by
  `OPENQUANTUM_SDK_KEY` (`~/.config/openquantum/sdk-key.json`).
- Quandela Cloud: [docs/notes/quandela/README.md](docs/notes/quandela/README.md);
  Perceval on the system Python, `QD_PYTHON` for the MCP server; MCP `quandela`;
  token file named by `QUANDELA_TOKEN_FILE`.
- IQM Resonance: [docs/notes/iqm/README.md](docs/notes/iqm/README.md);
  interpreter `iqm-python` of the iqm-resonance-stack package; MCP `iqm`; token
  pair file named by `IQM_TOKENS_FILE`.

Every job (QPU, emulator, simulator or mock), upload, QRNG read, timeslot
booking and notebook session on any provider waits for the user's approval of a
written case: what it measures, why a simulation cannot answer it, the backend,
shots, expected seconds and expected credits. A Quantum Inspire hardware batch
also keeps its pause and queue limits, and Open Quantum Public Compute makes
every uploaded circuit and result public and non-confidential (the upload in
`prepare_job` is itself the publication), so unpublished methods stay off it.

## Qiskit skills

The Qiskit agent skills come from https://github.com/Qiskit/skills, installed
by copy into `~/.claude/skills/`:

| skill | installed path | upstream commit |
|---|---|---|
| migrate-qiskit-ibm-runtime | `~/.claude/skills/migrate-qiskit-ibm-runtime/` | a5499c7c24f51633cbd0a5e7ea5902841e5b983e |

Upstream also publishes them as a Claude Code plugin:
`/plugin marketplace add Qiskit/skills`, then
`/plugin install qiskit-ai-skills@qiskit`.

**Monthly check.**
1. Compare `git ls-remote https://github.com/Qiskit/skills HEAD` with the
   pinned commit above.
2. On a difference, clone the new commit into a scratch directory and read
   every changed or added file in full before installing: skills are
   instructions an agent executes, so they get the review any code gets.
3. Copy the skill directories into `~/.claude/skills/`, update the table above
   in a PR, and rerun the audit below. A new skill on the upstream roadmap
   (mitigation evaluation, layout selection, circuit optimization) also gets a
   written decision on whether it replaces anything in live_run.py.

**When to invoke.** Run `/migrate-qiskit-ibm-runtime` with scope
gororoba_quantum/ in these cases, and follow its phases, grounding, and report
format:
- any change that touches qiskit-ibm-runtime: primitives, options, jobs,
  service, backends, sessions, or batches;
- any change to the qiskit-ibm-runtime pin in requirements.txt;
- after every monthly skill update.

The skill sets the destination as the client-side
`qiskit_ibm_runtime.executor_sampler.Sampler` from runtime 0.50.0. It forbids
inventing an API path that its guides and the API reference do not enumerate,
so such a path is validated at run time and named in the error when absent.

**Rules the audit established.** The skill's local verification ran circuits
through the client-side Sampler and established the job split live_run.py
uses. In runtime 0.50, gate twirling sends circuits through samplomatic
boxing, which rejects `if_else`, and IBM's Sampler rejects dynamical
decoupling on dynamic circuits. So live_run.py sends circuits with
mid-circuit measurement, reset, or feed-forward in their own job, with
twirling and dynamical decoupling off.

## Reviews and merges

Codex, the chatgpt-codex-connector app, supplies the default pull-request
review. It reviews only on request: an issue comment `@codex review` asks for
a review of the current head, so the operator posts one right after opening
a PR and after every push that needs review.

Codex is the only hosted reviewer. Copilot reviews are billed to the owner,
so no pull request requests one; when the Codex app reports exhausted
code-review quota, the owner decides how the PR proceeds.

- *Progress.* The bot keeps one summary comment per PR, marked
  `codex-pull-request-review-summary`, which reads Running while a review is in
  progress.
- *Outcome.* A review with findings publishes inline review comments with P1 or
  P2 badges. A clean review either posts an issue comment whose text, after
  an optional `<!-- codex-review-receipt:v1 -->` marker, begins "Codex
  Review: Didn't find any major issues" with a reviewed commit matching the PR
  head, or adds an app-owned `+1` reaction after the completed summary update
  for the current head. A prior reaction cannot qualify a later review round.
- *Status tool.* `scripts/codex_review_status.sh PR...` prints each PR's head,
  summary head, review state, and head-bound clean signal, then every unresolved
  thread with its root comment id and full body. It accepts comments and
  reactions only from the stable app and bot identities, requires the clean
  comment to follow the current review request and the reaction to occur
  strictly after the completed summary update. It paginates every issue,
  reaction, thread, and thread-comment connection, then re-reads the head and
  PR update marker, and summary to reject a changing snapshot.

**One round, per PR:**
1. Wait until the Codex review completes: its summary stops reading
   Running. Then read every unresolved thread
   in full from `codex_review_status.sh` or the GraphQL thread connection.
   Threads can arrive between rounds and attach to the newest commit, so the
   open-thread list,
   not memory of the last round, is the work queue.
2. Triage each thread against reachability.
   - A defect a user reaches through a documented interface (the CLI, the
     record files the program writes, the default flow) gets a fix.
   - A claim the source refutes gets the refuting line in the reply.
   - Malformed or adversarial input outside the documented domain gets a reply
     naming the boundary and a follow-up issue.
3. Fix every reachable thread on the PR's own branch in one commit. A change to live_run.py or experiments.py also gets a live dry run,
   and a change to qiskit-ibm-runtime usage also gets `/migrate-qiskit-ibm-runtime`.
   Then push.
4. Reply to each thread's root comment with
   `gh api repos/OWNER/REPO/pulls/PR/comments/ID/replies -f body=...`. The reply
   begins with one of three markers, then says what changed or why:
   - `Fixed in <commit>`
   - `Refuted:` followed by the refuting source line
   - `Boundary:` followed by the documented limit and the follow-up issue
5. Run `scripts/resolve_answered_threads.sh PR`. It resolves only threads
   carrying a reply from the authenticated operator that begins with one of
   those markers, and lists every other open thread as unanswered. A comment
   such as "will fix" or a question resolves nothing. Never resolve a thread
   whose finding has not been read and answered.
6. Request Codex again and start at step 1. A PR leaves the loop when the
   current-head Codex status reports `verdict=clean-comment...` or
   `verdict=clean-reaction...` and every review thread is resolved.

**Stacked PRs.**
- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top, and run a dry run on every
  branch the merge touched.

**Merging.** A PR merges after this sequence:
1. Codex reviews; every thread is fixed, refuted or bounded and resolved
   (One round above), and the touched files pass the code-style tools.
2. The operator reviews the whole PR diff against origin/main, every commit
   regardless of author, not only the commits written in this loop, and fixes
   what that review finds.
3. Codex reviews the head once more; that round's threads are answered and
   resolved the same way.
4. The `pr.yml` jobs `lint`, `types` and `tests` pass on the head. A push
   that changes the head reruns them; a red job gets its fix commit on the
   branch.
5. GitHub reports mergeable_state clean.

Then, bottom-up, for each PR:
1. Merge it with a merge commit:
   `gh api -X PUT repos/OWNER/REPO/pulls/PR/merge -f merge_method=merge`.
2. Retarget the next PR to main: `gh api -X PATCH repos/OWNER/REPO/pulls/NEXT -f base=main`.
   Deleting a base branch closes every PR that targets it, so the retarget
   comes first.
3. Delete the merged remote branch:
   `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
4. Pull main in the primary checkout, then `git worktree remove` and
   `git branch -d` the merged branch.

**API use.** Everything goes through REST with `gh api`, except review
threads, which only GraphQL exposes: both scripts list them through the
reviewThreads connection, and resolution uses resolveReviewThread and
unresolveReviewThread.

## Records

- results/ holds audit records: hw_estimate/ for the fixed ibm_fez compile and
  live/ for live runs.
- A collected run keeps its lossless result under `raw/<job_id>/` (every
  classical register as shot-ordered bit strings, each PUB's metadata with
  the backend scheduler table, the result metadata, the job metrics, and an
  index of sha256s), written by `--collect` before any analysis and
  recoverable with `--preserve-raw DIR` for a record collected under an
  earlier revision. collect.json is the preregistered analysis at the run's
  experiment digest; `adjudicate.py DIR` writes adjudication-<digest>-seed<seed>.json, a second
  analysis of the same raw files named by its own analysis digest, beside
  any earlier one. Raw files
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
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`. Account identifiers are credentials, account
  and instance ids, CRNs and email addresses. A public platform handle --
  the GitHub owner in every repository URL, the Kaggle username in a
  kernel or dataset slug (`owner/slug`) -- names published work, and
  records keep it so `collect` and `status` resolve the kernel.

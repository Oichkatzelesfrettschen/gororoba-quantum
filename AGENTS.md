# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only.

GitHub Actions runs every gate ([.github/workflows/ci.yml](.github/workflows/ci.yml)).
[ci/gates.json](ci/gates.json) lists each gate as one command with its
working directory; [ci/run_gates.py](ci/run_gates.py) runs a shard of them on
a thread pool sized to the runner's CPUs and keeps going past failures, so a
red shard lists every failing gate. Each gate records its measured seconds;
shards are assigned longest-first. Pull requests run the `pr` tier, every
gate that measured under two minutes, on six shards; pushes to main, the
nightly schedule and manual runs add the `full` tier's long simulation
contracts on twelve shards. Runners are 2-vCPU, 8 GB machines on Python 3.14
with the pins in requirements.txt and ci/requirements-ci.txt (mypy, ruff and
the plotting-only `matplotlib==3.11.2`). A pull request merges when every
shard is green and its review threads are resolved; a red main or nightly
run is fixed in the next change. A new module, evidence
replay or contract joins the gate list in ci/gates.json in the same change.


CPU-bound loops over independent items (embedding scores in replica
placement, operator checks, registry parsing) run through parallel.py, an
order-preserving process pool started with spawn on every platform, so a
parallel run returns exactly what the serial loop returns.
`GOROROBA_WORKERS=N` caps the worker count and `GOROROBA_WORKERS=1` runs
serially; the default is every CPU available to the process
(`parallel.default_threads()`), which also sets `--simulation-threads`. Aer runs batch
every replica of a choice in one call and parallelize experiments itself.

A change to live_run.py or experiments.py also gets a dry run,
`"$PYTHON" live_run.py --out ../results/live`, whose audit record lands under
results/live/.

The matched diagnostic families and statistical design contracts are documented
in [QPU_OPTIMIZATION.md](gororoba_quantum/QPU_OPTIMIZATION.md). Their local
gates exercise exact labeled laws, bounded inference, fake-backend layouts,
aggregate budgets, and negative dry-run records; hardware claims require
separately approved results.

The independently admitted packed ripple and rank-sector families are described
in [PACKED_ALGEBRA.md](gororoba_quantum/PACKED_ALGEBRA.md). `--native-dry-run`
calls Runtime with `dry_run=True` and retains mock timing in a separate sidecar.
Mock outcomes never enter scientific analysis or measured visualizations.

The measured folded-job figure uses `results/ripple/folded-job-review.json`.
After changing its renderer, run `"$PYTHON" scripts/render_folded_job_review.py
--png results/ripple/folded-job-review.png --check` from the root. Independent
raw replay uses `"$PYTHON" scripts/review_folded_jobs.py --run-dir "$FOLDED_RUN"
--check`, with `FOLDED_RUN` pointing to the retained archive in hardware
[evidence PR #37](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/37).
The raw archive remains owned by that evidence change.

The N=21 target-flip certificate gets a fresh Rocq compile and kernel check
when its generator, witnesses, or evaluator changes. Run the checks on a copy
under temporary storage so the checkout retains source files only:

```sh
(
  set -eu
  proof_tmp="$(mktemp -d)"
  cp proofs/TargetFlipN21.v "$proof_tmp/"
  (cd "$proof_tmp"
    rocq compile -q -w +all TargetFlipN21.v >compile.log 2>&1
    if rg -n "Warning:" compile.log; then exit 1; fi
    rocq check -silent -o TargetFlipN21)
)
```

The certificate proves finite Boolean permutation action. Operator checks in
modular_arithmetic.py establish Qiskit phase and clean-workspace behavior.

Changes to `proofs/FoldAverageDescent.v`, `proofs/TerminalChannelSeparation.v`,
`proofs/TerminalChannelSeparationReal.v`, or their receipts also run
`ROCQ="${ROCQ:-rocq}" sh docs/evidence/formal_certificates/replay_rocq.sh` with the
pinned Rocq 9.1.1 toolchain. The replay compiles in temporary storage,
treats warnings as errors, kernel-checks, and compares raw assumptions.
The [bundle](docs/evidence/formal_certificates/README.md) distinguishes
real foundations, deterministic interval premises and unproved coverage.

The recovered wide-control acquisition uses
`scripts/review_wide_control_job.py --check` and `--self-test`, each in
normal and optimized Python. `scripts/reconcile_qpu_inventory.py --check`
binds the complete recorded service inventory to every raw job archive;
its synthetic contract rejects missing/duplicate jobs, altered denominators
and raw corruption. These replays and measured extraction/render checks
join `ci/gates.json`.

Changes to the C881 proof sources or receipts also run the pinned Rocq
procedure in `docs/evidence/c881_exhaustive/README.md`. The CI receipt
check verifies retained hashes; a fresh kernel replay remains the proof-change
procedure because hosted CI supplies no pinned Rocq toolchain.

## Source library and research replay

`docs/` owns source notes, retained PDFs, retrieval identities and research
replays. `literature -> docs` preserves recorded paths; new Markdown links use
`docs/`. Immutable source ledgers retain their recorded bytes. The
`sources` suite in ci/gates.json covers the source registry, the evidence
replays (normal and optimized modes) and their checksum ledgers.


Changes to proof replay inputs also follow the pinned Rocq replay in
`docs/evidence/folding_proofs/README.md`. Imported paper parser diagnostics
remain source limitations in the registry; checksum admission preserves the
original bytes and differs from a fresh mathematical proof check.

<!-- algebra-circuit-rules:begin -->
## Algebra circuit design rules

These rules bind every circuit, case, analysis and note that encodes
Cayley-Dickson arithmetic on a qubit register. The root AGENTS.md,
gororoba_quantum/AGENTS.md and scripts/AGENTS.md carry this section with
identical bytes; `ci/check_agents_sections.py` fails on any difference.
`docs/evidence/reviewer_associator_audit/` replays the numeric claims below
(gates sources-240 and sources-241), and `scripts/algebra_circuit_fixtures.py`
(gates core-251 and core-252) runs the zero-product, Hadamard-basis and
workspace fixtures on the circuit builders of `designs.py`.

**Encoding and representation.**
- The map `a -> L_a` is a linear encoding, not an algebra homomorphism.
  Associative matrix composition represents a non-associative product through
  `(L_a L_b - L_ab) c = -(a, b, c)` with `(a, b, c) = (ab)c - a(bc)`: two
  wirings compared by an observable, never a claim that matrix products
  fail to associate. A faithful associative representation of a
  non-associative product does not exist.
- A sedenion-coefficient encoding states its coefficient domain (real or
  complex), normalization, basis convention (`cd_core.cd_sign`, doubling
  `(a, b)(c, d) = (ac - conj(d) b, da + b conj(c))`) and scale. The basis
  state `|0>` is `e_0 = 1`, the multiplicative identity, never the zero
  vector. A unitary cannot output the zero vector: an algebraic zero product
  is a heralded branch of zero probability while the full state keeps norm 1.
- Norm multiplicativity `|ab| = |a||b|` holds for real coefficients in
  dimensions 1, 2, 4 and 8 only (Hurwitz). The real sedenions already have
  zero divisors, `(e1 + e10)(e4 - e15) = 0`, and the complex-linear extension
  has them even on associative subalgebras: `(e_0 + i e_1)(e_0 - i e_1) = 0`.

**Zero-product witnesses.**
- Certify every claimed zero-divisor pair with `cd_core` before circuit work.
  Four product terms that land on four distinct XOR labels cannot cancel:
  `(e1 + e10)(e2 - e13) = e3 + e7 + e8 - e12`, which is the repository's
  negative regression fixture (fixed-operand LCU `P(s = 0) = 1/2`). The
  corpus pair `(e1 + e10)(e4 - e15) = 0` is the dark witness, and
  `(e1 + e10)(e4 + e15)` is its bright control (`P(s = 0) = 1`).
- Read the selector's success outcome, not "output label unequal to zero".
  The fixed-operand LCU of Design B gives `P(s = 0) = ||x y||^2 / 2` for
  normalized `x = (e_i + t e_j)/sqrt2`, `t = +-1`, and normalized `y`. The
  universal coefficient contraction of the D-dimensional algebra (D = 16 for
  the sedenions), `M|i, j> = sigma(i, j)|i xor j>`, has `M M^dagger = D I`,
  so its success Kraus operator is `M / sqrt(D)` and `P = ||x y||^2 / D`. Reports
  give success counts, attempts, the bright reference, the uncertainty and
  the implemented normalization; the dark floor carries preparation, coherent
  control, incoherent, readout and sampling contributions together.

**Signs, workspace and measurement basis.**
- A sign register prepared in `|0>` records the sign as a which-path label;
  phase kickback needs the register in `|->`, where `X|-> = -|->`. Every
  retained input or workspace register that differs between branches
  suppresses their interference and enters the overlap.
- Before two computation branches recombine, return every temporary register
  to a common state (undo branch-specific XORs), and include all registers in
  the overlap calculation.
- In a Hadamard test, `<X_c>` before the final H, or `<Z_c>` after it, equals
  `Re<psi_L|psi_R>`; `X_c` measured after the final H reads the pre-H `Z_c`,
  which is 0 for balanced branches.
- A uniform superposition over all `16^3` sedenion basis triples gives
  witness expectation `1 - 2(1848/4096) = 25/256` and `P(c = 1) = 231/512`;
  the deterministic `-1` belongs to a single non-associating triple or to
  input supported inside that sign sector.

**Observables and claims.**
- Associator-sign measurement, zero-product success and state-coherence
  reconstruction are three observables. The fixed-pair witness
  `W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j)` is diagonal, so its expectation
  `sum_k rho_kk omega(i, j, k)` reconstructs no coherence of the data
  register; coherences need their own basis settings (for a two-qubit pair,
  XX, XY, YX, YY with the register order fixed).
- Logical register counts: fixed-pair associator test, 4 data qubits plus 1
  control; fixed sparse operand zero-product LCU, 4 data qubits plus 1
  selector; two-input signed lookup, 8 input qubits plus 1 sign qubit; three
  independent input registers with coherent branch control, 12 input qubits
  plus 1 control plus workspace. Routed gate costs are measured separately.
- Name the interferometer an associator-sign interference witness; a
  holonomy claim needs a parameter space, transport rule and closed-loop
  observable. Non-Abelian braiding is noncommutative and associative and
  supports no non-associativity claim. A circuit construction establishes
  ideal implementability, hardware data establish performance under a stated
  implementation, and a priority claim needs a separate literature
  comparison.
- IBM removed pulse-level control on 3 February 2025; designs use the gate
  set, fractional gates and dynamic circuits.
<!-- algebra-circuit-rules:end -->

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. The case is written against a submit-free dry run, and the
  `--submit` command names that run with `--approved-record`, its record.json
  digest with `--approved-record-sha256`, and the case's seconds with
  `--max-execution-seconds` (the Sampler's max_execution_time, which the
  service enforces; the dry run is made with the same value, since the
  policy carries it). `--max-total-execution-seconds` caps the sum of all
  job ceilings, and `--reserve-seconds` names the retained quota. The fresh
  plan must match the record in experiment
  digest, shots, policy (twirling, DD, budget floor, execution ceiling),
  dependency versions, IBM Cloud instance, groups, backends, seeds, layouts,
  replica qubits, fused PUB manifests, calibration at the refresh and again
  at each batch, and QPY bytes, or the run writes an `approval_required`
  record and sends nothing. The first batch consumes the approval by writing
  `approval-consumed.json` into the approved record's directory, so a second
  invocation on the same record sends nothing. Calibration reads,
  transpilation, noise simulation, result retrieval, and `--preserve-raw`
  need no approval.
- Calibration is a property of the run. live_run.py fetches each backend's
  Target and properties afresh in the process that decides, compiles,
  simulates, and submits; no calibration value is cached or read back from a
  file to drive a submission.

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
review. It reviews on open, and an issue comment `@codex review` requests a
review of the current head.

When the hosted Codex app reports exhausted code-review quota, request Copilot
instead. The user authorizes that substitution. Submit a REST review request
to `pulls/PR/requested_reviewers` with
`{"reviewers":["copilot-pull-request-reviewer[bot]"]}` and verify that the
`copilot-pull-request-reviewer` check starts. An empty `requested_reviewers`
response can accompany an accepted request; the check confirms execution.
Read the completed Copilot review and every review thread. Admission requires
a review by that app on the current commit, zero open findings, a successful
current-commit Copilot check, and resolved review threads. General expert-review
cautions retain their scientific scope; concrete findings require the same
triage and fixes below. The Codex status script reports Codex clean signals;
Copilot admission uses its REST reviews/checks and GraphQL review threads.
Return to the default reviewer when hosted Codex review becomes available.

- *Progress.* The bot keeps one summary comment per PR, marked
  `codex-pull-request-review-summary`, which reads Running while a review is in
  progress.
- *Outcome.* A review with findings publishes inline review comments with P1 or
  P2 badges. A clean review either posts an issue comment beginning "Codex
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
1. Wait until the selected review completes: the Codex summary stops reading
   Running, or the Copilot check completes. Then read every unresolved thread
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
3. Fix every reachable thread on the PR's own branch in one commit; CI runs the
   gates on the push. A change to live_run.py or experiments.py also gets a live dry run,
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
6. Request the selected reviewer again and start at step 1. A PR leaves the
   loop when the current-head Codex status reports `verdict=clean-comment...`
   or `verdict=clean-reaction...`, or the authorized Copilot admission above
   passes, and every review thread is resolved.

**Stacked PRs.**
- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top. CI reruns every gate; run a dry
  run on every branch the merge touched.

**Merging.** A PR merges when its latest review is clean, every thread is
resolved, and GitHub reports mergeable_state clean. Bottom-up, for each PR:
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
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`.

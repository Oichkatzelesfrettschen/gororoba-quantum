# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only. Before any push, these exit 0:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  ruff check gororoba_quantum scripts/python_call_graph.py scripts/left_mult_sign_rank.py \
    scripts/mod15_signed_multiplier_census.py scripts/associator_walsh_classes.py
  ruff format --check gororoba_quantum scripts/python_call_graph.py scripts/left_mult_sign_rank.py \
    scripts/mod15_signed_multiplier_census.py scripts/associator_walsh_classes.py
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" scripts/python_call_graph.py >/dev/null
  cd gororoba_quantum
  mypy boolean_anf.py cd_core.py verify.py designs.py factoring.py \
    hybrid_shor.py modular_arithmetic.py compile_evidence.py packing.py \
    parallel.py predict.py select_lcu.py experiments.py live_run.py order_finding.py \
    runtime_contracts.py variance.py target_flip.py target_flip_certificate.py \
    affine_residual.py affine_residual_challenger.py adjudicate.py \
    ../scripts/python_call_graph.py ../scripts/left_mult_sign_rank.py \
    ../scripts/mod15_signed_multiplier_census.py ../scripts/associator_walsh_classes.py
  "$PYTHON" verify.py       # needs the open_gororoba checkout at GOROROBA_ROOT
  "$PYTHON" designs.py
  "$PYTHON" factoring.py
  "$PYTHON" target_flip.py
  "$PYTHON" target_flip_certificate.py --check
  "$PYTHON" affine_residual.py
  "$PYTHON" modular_arithmetic.py
  "$PYTHON" order_finding.py
  "$PYTHON" compile_evidence.py --seeds 20261010 \
    --candidate one_clean_cycle >/dev/null
  "$PYTHON" ../scripts/mod15_signed_multiplier_census.py
  "$PYTHON" ../scripts/associator_walsh_classes.py --max-dim 64 >/dev/null
  "$PYTHON" runtime_contracts.py
  "$PYTHON" variance.py
  "$PYTHON" adjudicate.py --check
  "$PYTHON" cd_core.py >/dev/null
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 8
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 5 --mutate high-low-unconditional
  "$PYTHON" ../scripts/left_mult_sign_rank.py --max-n 5 --mutate high-high-no-early-return
  "$PYTHON" hybrid_shor.py simulate 15 --shots 256 --seed 7
)
```

CPU-bound loops over independent items (embedding scores in replica
placement, operator checks, registry parsing) run through parallel.py, an
order-preserving process pool started with spawn on every platform, so a
parallel run returns exactly what the serial loop returns.
`GOROROBA_WORKERS=N` caps the worker count and `GOROROBA_WORKERS=1` runs
serially; the default is the CPUs available to the process. Aer runs batch
every replica of a choice in one call and parallelize experiments itself.

A change to live_run.py or experiments.py also gets a dry run,
`"$PYTHON" live_run.py --out ../results/live`, whose audit record lands under
results/live/.

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
  policy carries it); the fresh plan must match the record in experiment
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

Codex, the chatgpt-codex-connector app, reviews every pull request. It reviews
on open, and an issue comment `@codex review` requests a review of the current
head.
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
1. Wait until the summary comment stops reading Running. Then read every
   unresolved thread in full from `codex_review_status.sh`. Threads can arrive
   between rounds and attach to the newest commit, so the open-thread list,
   not memory of the last round, is the work queue.
2. Triage each thread against reachability.
   - A defect a user reaches through a documented interface (the CLI, the
     record files the program writes, the default flow) gets a fix.
   - A claim the source refutes gets the refuting line in the reply.
   - Malformed or adversarial input outside the documented domain gets a reply
     naming the boundary and a follow-up issue.
3. Fix every reachable thread on the PR's own branch in one commit, and run the
   gates. A change to live_run.py or experiments.py also gets a live dry run,
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
6. Comment `@codex review` and start again at step 1. A PR leaves the loop when
   the current-head status reports `verdict=clean-comment...` or
   `verdict=clean-reaction...` and no thread is open.

**Stacked PRs.**
- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top. Then rerun the gates and a dry
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

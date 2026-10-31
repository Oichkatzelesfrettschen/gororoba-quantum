# Operating rules decomposed to first principles

This document takes every rule in the repository's agent guide as a hypothesis about a failure it
prevents, measures whether that failure has occurred, asks whether a mechanism can enforce it instead of
prose, and keeps as text only what no mechanism and no file in the tree carries. The owner's objective
sets the standard: the shortest path from a scientific question to interpretable evidence, with no lost
data, no unapproved spend, no secret in history, no collision between concurrent agents, and no guess
promoted to a claim. The team is one human and one to four agent sessions.

The measurements come from [operating-data.md](../archive/reviews/layout-reconciliation/operating-data.md)
(60 merged pull requests, 100 `pr.yml` runs, 9 scheduled audits, the gate ledger at `a1d1743`). Two
external reviews read the same brief ([brief.md](../archive/reviews/operating-rules/brief.md)) and the
checkout: the Grok Build CLI ([review-grok.md](../archive/reviews/operating-rules/review-grok.md)) and the
Codex CLI ([review-codex.md](../archive/reviews/operating-rules/review-codex.md)). Every `file:line` claim
adopted below was re-read in the tree. The work record is
[operating-rules-contract](../state/plans/operating-rules-contract.json); the layout program that led
here is [repository-layout-reconciliation](repository-layout-reconciliation.md).

## The failures the rules exist for

Six failures account for every sentence in the guide. Each has a measured history and a mechanism that
either exists or is one check away.

| Failure | Observed here | Mechanism today | What is missing |
|---|---|---|---|
| A secret, account identifier or home path in history | none in the window; the rule is a hard boundary | prose in three paragraphs; no scanner in `ci/gates.json` | a `tests`-job scanner for tokens, CRNs, emails and home paths with an allowlist for the published GitHub owner and Kaggle slug |
| Unapproved or misdirected spend of provider time | none; two sessions on one IBM instance blocked each other's audit | `scripts/approved_run.sh` refuses a drifted plan and sends nothing; a harness deny on force-push and recursive delete | a deny on every other submit entry point; launcher refusals for the 14/15/16-qubit routing; an Open Quantum client that refuses the public plan without a case flag |
| Another worker's job cancelled | a Codex session once cancelled a shared-token Quandela job | `scripts/acquisition_decisions.py` validates a cancellation-authority record (`docs/runbooks/evidence-closure.md`) | the validator in front of every cancel tool, which is where the incident got through |
| Retained data edited or lost | the nightly found three drifted evidence bindings after merges | replay and `sha256sum -c` gates, after the merge, when the gate is under 15 s or the tracer connected the edit | gates selected by reach regardless of duration (below) |
| A guess promoted to a claim | none in the window | `scripts/research_state.py --check`; the record schema | a claim check that rejects a measured figure built on a `--native-dry-run` sidecar; a schema that requires the probe arms and a null arm |
| An irreproducible result | none in the window | `ci/seed_provenance.py` in the `tests` job; shrink-only `ci/reproduction_seeds.json`; `check_markdown_links.py`; `core-plan-tracker` | nothing; the checks are the rule |

Every other sentence in the guide repeats a check that already runs, a fact a file already holds, or a
procedure a runbook already describes.

## What the operating data says about the rules

| Rule | What it costs | What it caught | Verdict |
|---|---|---|---|
| Run ruff, mypy before every push | 4 lines per session; a local tool run per push | `lint` and `types` failed 0 times in 100 runs; ruff also runs again as gates `core-000`, `core-001`, `core-002` when a diff reaches them | The CI jobs are the rule. The sentence and the duplicate gates leave. |
| A dry run for every change to `live_run.py` or `experiments.py` | 351 run directories in 20 days, 102 bare, 277 MB of identical `isa.qpy`; bare directories track those commits per day at r = 0.87 | nothing a test did not; no gate or workflow requires the dry run | The sentence is the producer of the bulk. It leaves; a snapshot dry run under the `tests` job takes its place. |
| Request a Codex review after every push; a second round after the operator review | 312 requests for 60 merges; 91 on 29 PRs that produced no thread | 142 threads, 110 fixes, 7 refutations in the first rounds | One round earns its cost. The repeat round on an unchanged diff is ceremony. |
| The nightly audit of every gate | 12 shards, about 25 minutes wall, 504 measured gate minutes per night | red 8 of 9 nights; 12 of 16 red gates cited by no claim; three drifted bindings found once | The audit polices a ledger skip no workflow takes ([CI purpose](#what-the-ci-is-for)). It runs cited gates nightly and the rest weekly. |
| 15 s gate cutoff on pull requests | 51 `pr`-tier gates above the cutoff defer to the red nightly; `core-615`, the behavioral suite, is 15.1 s | a merge can be green and wrong until 09:17 UTC the next day | Selection by reach, bounded by the job budget, with `pending` for an unfinished reached gate. |
| A retained run needs a citing claim in the same change | capture waits on interpretation | `scripts/research_state.py --add-acquisition` already admits a run without a claim; `--check` then requires the claim | `--check` admits an acquisition whose claim is pending; the claim is a later change. |
| Algebra conventions, Heron census, pulse-control date in the guide | 12 lines in every session | nothing; `cd_core.py`, `docs/notes/algebra_circuit_rules.md` and `docs/evidence/heron_platform/targets.json` are the sources | One pointer line. Inlining the facts contradicts the guide's own "never guess" rule, because the prompt becomes the source. |
| Compute-flags review before every option-bearing command | a runbook read before ordinary commands | one measured incident, Singular local orderings past an hour at tens of GiB | The runbook keeps the table and the incident; the guide keeps one line naming Singular and msolve. |
| Plan record before committing work | 141 records, 74 in `inbox`; `core-plan-tracker` among the nightly failures | nothing the PR description did not | `core-plan-tracker` stays as the check; the capture sentence leaves. |
| Qiskit skill run on any runtime touch | a skill run per session that touches the runtime | one real constraint: dynamic circuits ship with twirling and dynamical decoupling off | A test on `live_run.py` for the job split; the monthly skill check stays in its runbook. |
| Guide size | 534 lines, 33 KB per session; `ci/AGENTS.md` 490 lines; the user guide sets 200 | the guide's own sentence "an AGENTS.md holds rules a session cannot derive" has not been applied to itself | About 40 lines of boundaries and overrides remain as text. |

## What the CI is for

The owner could not deduce the purpose because the comments describe a three-speed ledger and the
triggers run one speed. `ci/AGENTS.md` describes pull requests running reached gates, pushes to main
running with `--ledger` and skipping gates whose key is unchanged, and a nightly `--ledger-audit` that
runs everything to catch a read the tracer cannot see. `.github/workflows/ci.yml` lines 7 to 10 trigger
on `schedule` and `workflow_dispatch` only; both select `--ledger-audit` at line 152, and no push trigger
exists, so the `--ledger` skip is unreachable. The nightly therefore spends the full 504 measured minutes
every night to police a skip that no job performs. `ci/pr_checks.sh` line 105 passes `--affected-ledger`,
which widens selection and skips nothing, and line 106 drops every reached gate above 15 s
(`ci/run_gates.py` line 256 filters by `seconds`), so the 51 `pr`-tier gates between 15 s and the 30 s
tier boundary run only on the nightly. `ci/audit_report.py` lists each red gate beside the claims that
cite it and qualifies only those claims, so a red gate with no claim changes no scientific status and
still keeps issue #554 open.

The purpose, stated so a researcher can read it, is three questions:

| Question | Who answers it | When |
|---|---|---|
| Does this change keep the contracts it reaches? | `pr.yml`: `tests`, `gates` selected by reach and bounded by the job budget, with `pending` named for a reached gate that did not finish; `lint` and `types` run beside them without blocking | every pull request |
| Do the retained artifacts behind each claim still replay? | the gates some claim cites | nightly, with the claim named on a failure |
| Did the selector, the tracer or the environment miss something? | every other gate, through the ledger that already keys them | weekly, and on a change to the selector, the tracer, the runtime pins or a gate's inputs |

A red gate no claim cites gets a claim or leaves `ci/gates.json`; the 12 red ones on 2026-10-30 are the
first batch. Ruff leaves the gate list because the `lint` job runs it. The `--ledger` branch gains the
push trigger the comment promises, or the branch leaves.

The Codex review adds the classification that makes the schedule stateable gate by gate: every gate
declares what it protects, one of `claim` (a current claim id), `immutable-binding` (a bound path),
`supported-runtime` (an advertised environment), `ledger-sentinel` (a read the tracer cannot see) or
`exploratory`. Claim, binding and runtime gates run when their inputs change and nightly; sentinels run
as a rotating stratified sample nightly; the exhaustive `--ledger-audit` runs weekly and on dispatch; an
exploratory gate with no owner and no review date is archived. The review also names the control-plane
load the loop adds: `scripts/codex_review_wait.sh` polls status, mergeability and check runs every 90 s
although branch protection already decides admission, so the waiter needs only the review signal.

## The minimal operating contract

Ordered by what it protects. Each boundary is text because no mechanism carries it yet; the mechanism
column names the check that would let the sentence leave.

| Boundary | Text that stays | Mechanism that would replace it |
|---|---|---|
| Secrets | No token, key, account identifier, CRN, email address or home path in a commit, log or memory; an IBM instance is a 12-hex sha256 of its CRN; the GitHub owner and the Kaggle slug stay because `collect` and `status` resolve them | a scanner in the `tests` job |
| Spend and publication | Every provider job, paid upload, notebook session, timeslot and provider QRNG read waits for the owner's written case naming the question, why simulation cannot answer it, backend, shots, seconds and credits; IBM `--submit` goes through `scripts/approved_run.sh`; `GOROROBA_IBM_ACCOUNT` is fixed across a case's dry run, submit and collect; Open Quantum's public plan publishes the upload; free QRNG draws, calibration reads, transpilation, local simulation, retrieval and `--preserve-raw` need no case | harness denies on every submit entry point; launcher refusals for the routing split |
| Other workers | No cancellation of a job this session did not submit without the cancellation-authority record | the validator in front of each cancel tool |
| Retained data | A ledger- or digest-bound file keeps its path and bytes; a correction is a new file; `raw/<job_id>/` is never rewritten; external-only sources live in the private documents repository | the replay gates, selected by reach |
| Shared history | Merge commits; retarget a stacked PR before deleting its base; Codex is the only hosted reviewer and reviews once per head, a second time only after the operator review changed code; the four `pr.yml` checks admit a merge and no local gate run precedes a push | repository merge setting; the review scripts |
| Claims | A mock timing never enters a claim or a figure; a new seed literal comes from a registered draw and a seed that reproduces a retained record keeps its value; hardware numbers and algebraic conventions come from the registered artifacts, never from recall | the claim checker; `ci/seed_provenance.py`, which already runs |
| Routing | 14 qubits or fewer on Kaggle; 16 or more, or a device question, on IBM with a case saying why Aer cannot; 15 waits for a case naming the substrate | launcher refusals |

Forty lines carry these seven boundaries. Everything else in the 203-line guide proposed in PR #692 is a
check that already runs, a runbook that already exists, or a fact a file already holds, and the
[appendix](#appendix-the-guide-as-forty-lines) shows the text.

### Checks that replace text and already run

`lint`, `types`, `tests` (`pr.yml`); `tests/ci/test_seed_provenance.py`; `core-611` for links and
anchors; `core-plan-tracker`; `scripts/approved_run.sh`; ruff `S101` for stripped asserts; the
vectorized-fits equivalence gate; the `rocq-replay` job, which moves onto the pull request when
`ci/rocq_changed.sh` matches so the local-replay sentence leaves.

### What the two reviews agree on

Both reviews, written without sight of each other, reach the same shape: a contract of boundaries
ordered by what they protect (secrets, spend and publication, other workers' jobs, retained bytes,
shared history, claims), checks that replace prose, and a nightly that audits the selector by sample
rather than by exhaustion. Both name the dry-run sentence as the writer of the measured bulk, both move
the algebra and Heron facts to their files, both keep one Codex round per merge candidate, and both
remove the universal plan-record rule (Codex: a plan record only for provider operations, retained
campaigns, stacked branches or multi-session work; a single-session change uses its PR). Codex adds a
typed case field for seeds (`reproduction`, `independent`, `deterministic-identifier`) so the question a
seed answers is data the checker reads, and a provenance class on result records (`mock`, `simulated`,
`provider`) that a claim or figure manifest cannot consume as measured evidence.

### Checks that do not exist yet

Each one releases the paragraph beside it: the secret scanner; a `live_run.py` test that a calibration
loaded from a file cannot be the submission source and that `--native-dry-run` never reaches the submit
API; launcher refusals for the routing split; an Open Quantum client that refuses the public plan without
a case flag; cancel tools that refuse without an authority record; a claim check that rejects a figure
whose inputs carry a mock sidecar; a snapshot dry run under the `tests` job against
`docs/evidence/heron_platform/targets.json`; a `flock` around `research_state.json` writes so two
sessions on one instance stop blocking each other's audit; a test that dynamic-circuit jobs ship with
twirling and dynamical decoupling off.

### Sentences that leave

The algebra bullets, the arm order and the Heron census (their homes are `cd_core.py`, the algebra note
and the Target snapshot); the global-monomial sentence and the compute-flags preface (the runbooks keep
the incident and the table); the vectorized-fits recipe, the parallel-pool essay and the pre-push lint
mandate (CI is the authority); the dry-run sentence; the seed essay beyond one line; the Qiskit skill
ritual; the document taxonomy and the plan-capture sentence; the review-loop procedure beyond the three
reply prefixes; and `ci/AGENTS.md` as session context, which stays on disk for the jobs it describes and
loads into no session that is editing a circuit.

## Falsifiers

| Removal | Observation that would bring the sentence back |
|---|---|
| Pre-push lint and types | more than about five `lint` or `types` failures per 100 pull requests |
| The dry-run sentence | a `live_run.py` defect that unit tests and the snapshot dry run missed and only a live dry run caught, twice; one catch is a test to write |
| Algebra and Heron bullets | a merged circuit or claim whose sign, endianness or backend fact contradicts `cd_core.py` or the Target snapshot and whose author had not opened them |
| The second Codex round | a defect in a merged PR that the first round reviewed and the operator review did not change |
| Nightly of cited gates, weekly of the rest | a drifted binding whose gate the weekly cadence missed for longer than a claim's reader tolerates; the fix is a shorter cadence for that gate, not a nightly for all |
| Claim coupling of retention | a retained acquisition that no claim ever cited and that a reader mistook for a result; the fix is a report of unclaimed acquisitions, not a block on retention |
| Seed essay reduced to one line | a merged seed the literal scan cannot see that produced a result the owner cannot replay; that falsifies the checker's coverage |
| Secret paragraphs replaced by a scanner | a credential that matches no scanner rule and reaches a commit; add the pattern, keep the one-line ban |
| Cancel sentence replaced by a tool deny | a cancel that reached a provider without an authority record; the deny sits on the wrong tool |

## Decisions for the owner

1. Adopt the forty-line guide in the appendix as the replacement for the 203-line text of PR #692, with
   the runbooks it points at (recommended; the appendix is the diff).
2. CI: nightly for cited gates, weekly for the rest, `pending` instead of the 15 s drop, ruff out of
   the gate list, the 12 uncited red gates claimed or removed (recommended).
3. One Codex round per head; a second only after the operator review changed code (recommended).
4. The snapshot dry run in the `tests` job replaces the live dry run for refactors (recommended; the
   live read stays for admission, approval, submission and readiness changes).

## Appendix: the guide as forty lines

The text below is the proposed `AGENTS.md` body after the loader line and the pointers to
`docs/README.md`, `docs/PYTHON.md` and the runbooks. Each line names a boundary or an override; each
procedure it omits lives in the runbook the line names.

```text
Secrets. No token, key, account identifier, CRN, email address or local absolute path enters a commit,
a log or memory. An IBM Cloud instance appears only as a 12-hex sha256 of its CRN. The GitHub owner and
the Kaggle owner/slug stay in records so collect and status resolve them. Credentials live in the
provider stores named in docs/notes/providers.md.

Spend and publication. Every provider job (QPU, emulator, simulator or mock), paid upload, notebook
session, timeslot booking and provider QRNG read waits for the owner's approval of a written case: what
it measures, why a simulation cannot answer it, the backend, shots, expected seconds and expected
credits. IBM --submit runs as sh scripts/approved_run.sh --check CMD -- FLAGS; a plan that differs
from the approved record writes approval_required and sends nothing. GOROROBA_IBM_ACCOUNT stays the
same for a case's dry run, submit and collect; the two IBM quotas never pool. Open Quantum's public
plan publishes the upload in prepare_job, so unpublished methods stay off it. Free ANU and Outshift
QRNG draws, calibration reads, transpilation, local simulation, result retrieval and --preserve-raw
need no case. Routing: 14 qubits or fewer run on Kaggle; 16 or more, or a question about the device,
run on IBM with a case saying why Aer cannot; a 15-qubit run waits for a case naming its substrate.

Other workers. A session cancels no job it did not submit without the cancellation-authority record of
docs/runbooks/evidence-closure.md.

Retained data. A file a ledger, record or digest binds keeps its path and bytes; a correction is a new
file the old one's map row links. raw/<job_id>/ is never rewritten. External-only sources live only in
the private gororoba-quantum-documents repository.

Shared history. Branch, pull request, merge commit (merge_method=merge). Retarget a stacked PR to main
before deleting its base. Codex is the only hosted reviewer: one @codex review per head, a second only
when the operator review changed code; reply Fixed in <commit>, Refuted: <source line> or Boundary:
<limit, issue>, then scripts/resolve_answered_threads.sh. The four pr.yml checks admit a merge; no
local gate run precedes a push. Procedure: docs/runbooks/codex-review-loop.md.

Claims. A mock or --native-dry-run timing never enters a claim or a measured figure. Every new seed
comes from a registered QRNG draw through qrng_seeds.add_seed_argument or a ledger row; a seed that
reproduces a retained record keeps its value (ci/seed_provenance.py enforces both). Hardware numbers,
timing budgets and algebraic conventions come from docs/evidence/heron_platform/targets.json, the live
Target, gororoba_quantum/cd_core.py and docs/notes/algebra_circuit_rules.md, never from recall.
Singular and msolve use the orderings and flag rows of docs/runbooks/computer-algebra.md and
docs/runbooks/compute-flags.md.

Code. Python starts with GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096. A CPU-bound loop over
independent items runs through parallel.py. A change to live_run.py gets the snapshot dry run of the
tests job; a change to admission, approval, submission or readiness also gets a live dry run.
Checked-in text is emoji-free American English.
```

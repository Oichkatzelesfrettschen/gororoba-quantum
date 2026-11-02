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

The measurements describe the CI as it stood when they were taken: a nightly and weekly audit, selection of
gates by reach under a 900 s budget, and a gate ledger. That machinery is gone. `pr.yml` runs lint, types and
the unit tests on each pull request and each push to main, every gate of `ci/gates.json` runs on demand,
and `proofs.yml` compiles the Rocq bundles when a proof path changes ([ci/AGENTS.md](../../ci/AGENTS.md)). The
verdict column and the sections "What the CI is for" and "Falsifiers" below state the present rule.

## The failures the rules exist for

Six failures account for every sentence in the guide. Each has a measured history and a mechanism that
either exists or is one check away.

| Failure | Observed here | Mechanism today | What is missing |
|---|---|---|---|
| A secret, account identifier or home path in history | none in the window; the rule is a hard boundary | prose in three paragraphs; no scanner in `ci/gates.json` | a `tests`-job scanner for tokens, CRNs, emails and home paths with an allowlist for the published GitHub owner and Kaggle slug |
| Unapproved or misdirected spend of provider time | none; two sessions on one IBM instance blocked each other's audit | `scripts/approved_run.sh` refuses a drifted plan and sends nothing; a harness deny on force-push and recursive delete | a deny on every other submit entry point; launcher refusals for the 14/15/16-qubit routing; an Open Quantum client that refuses the public plan without a case flag |
| Another worker's job cancelled | a Codex session once cancelled a shared-token Quandela job | `scripts/acquisition_decisions.py` validates a cancellation-authority record (`docs/runbooks/evidence-closure.md`) | the validator in front of every cancel tool, which is where the incident got through |
| Retained data edited or lost | the nightly found three drifted evidence bindings after merges | `sha256sum -c` gates and replays of `ci/gates.json` on demand | a replay run whenever a producer, an input or a pin changes |
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
| The nightly audit of every gate | 12 shards, about 25 minutes wall, 504 measured gate minutes per night | red 8 of 9 nights; 12 of 16 red gates cited by no claim; three drifted bindings found once | The audit policed a ledger skip no workflow took ([CI purpose](#what-the-ci-is-for)). It is removed; replays run on demand. |
| 15 s gate cutoff on pull requests | 51 `pr`-tier gates above the cutoff defer to the red nightly; `core-615`, the behavioral suite, is 15.1 s | a merge can be green and wrong until 09:17 UTC the next day | No cutoff and no selection: `ci/gates.json` holds only checks of at most 30 s hosted wall, and every one runs on every pull request. |
| A retained run needs a citing claim in the same change | capture waits on interpretation | `scripts/research_state.py --add-acquisition` already admits a run without a claim; `--check` then requires the claim | `--check` admits an acquisition whose claim is pending; the claim is a later change. |
| Algebra conventions, Heron census, pulse-control date in the guide | 12 lines in every session | nothing; `cd_core.py`, `docs/notes/algebra_circuit_rules.md` and `docs/evidence/heron_platform/targets.json` are the sources | One pointer line. Inlining the facts contradicts the guide's own "never guess" rule, because the prompt becomes the source. |
| Compute-flags review before every option-bearing command | a runbook read before ordinary commands | one measured incident, Singular local orderings past an hour at tens of GiB | The runbook keeps the table and the incident; the guide keeps one line naming Singular and msolve. |
| Plan record before committing work | 141 records, 74 in `inbox`; `core-plan-tracker` among the nightly failures | nothing the PR description did not | `core-plan-tracker` stays as the check; the capture sentence leaves. |
| Qiskit skill run on any runtime touch | a skill run per session that touches the runtime | one real constraint: dynamic circuits ship with twirling and dynamical decoupling off | A test on `live_run.py` for the job split; the monthly skill check stays in its runbook. |
| Guide size | 534 lines, 33 KB per session; `ci/AGENTS.md` 490 lines; the user guide sets 200 | the guide's own sentence "an AGENTS.md holds rules a session cannot derive" has not been applied to itself | About 40 lines of boundaries and overrides remain as text. |

## What the CI is for

The CI answers one question on every pull request and every push to main: did this change break code that
worked? It runs fast, pinned checks that compare exact values exactly and floating-point values within stated
tolerances. Reproducing a retained historical record is a separate act, run by hand when an input changes (an
interpreter, numpy, qiskit or Singular pin) from `ci/gates.json`, as is every check of data rather than code: a
digest ledger, the source registry, the reading copies held in the gororoba-documents repositories, a research
script run end to end. Each of those fails on state the pull request did not change. The audit that preceded this rule spent the
full 504 measured minutes every night to police a ledger skip that no job performed, and every red night of its
last week came from environment drift (a Singular banner date, last-bit float drift on AMD EPYC AVX-512
runners, a timeout, one SIGSEGV), never from a code defect.

The purpose, stated so a researcher can read it, is three questions:

| Question | Who answers it | When |
|---|---|---|
| Does this change keep the contracts of the tree? | `pr.yml`: `tests` (unit tests on synthetic inputs, providers mocked); `lint` and `types` run beside it | every pull request and every push to main |
| Does a proof still compile? | `proofs.yml`, path-filtered, not a required check | a pull request or push touching a proof path |
| Do the retained artifacts behind each claim still replay? | `sh ci/pr_checks.sh gates`, by hand | after a pin or producer change |

A gate no claim cites stays a contract check or leaves `ci/gates.json`; a claim cites a gate of either manifest.
Ruff left the gate list because the `lint` job runs it.

The Codex review proposed a classification of each gate by what it protects, one of `claim` (a current claim id),
`immutable-binding` (a bound path), `supported-runtime` (an advertised environment), `ledger-sentinel` (a read the
tracer cannot see) or `exploratory`, with a schedule per class. The tracer and the schedule are gone, and moving
every gate out of the pull-request run to the on-demand `ci/gates.json` replaces the classification. The review also names the control-plane
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
| Retained data | Raw provider data, approval-hashed records and published replay bundles keep their path and bytes and a correction is a new file; a derived analysis that a ledger binds is corrected in place with its ledger; `raw/<job_id>/` is never rewritten; external-only sources live in the private documents repository | the replay gates, selected by reach |
| Shared history | Merge commits; retarget a stacked PR before deleting its base; Codex is the only hosted reviewer and reviews once per head, a second time only after the operator review changed code; the four `pr.yml` checks admit a merge and no local gate run precedes a push | repository merge setting; the review scripts |
| Claims | A mock timing never enters a claim or a figure; a new seed literal comes from a registered draw and a seed that reproduces a retained record keeps its value; hardware numbers and algebraic conventions come from the registered artifacts, never from recall | the claim checker; `ci/seed_provenance.py`, which already runs |
| Routing | 14 qubits or fewer on Kaggle; 16 or more, or a device question, on IBM with a case saying why Aer cannot; 15 waits for a case naming the substrate | launcher refusals |

Forty lines carry these seven boundaries. Everything else in the 203-line guide proposed in PR #692 is a
check that already runs, a runbook that already exists, or a fact a file already holds, and the
[appendix](#appendix-the-guide-as-forty-lines) shows the text.

### Checks that replace text and already run

`lint`, `types`, `tests` (`pr.yml`); `tests/ci/test_seed_provenance.py`; `core-611` for links and
anchors; `core-plan-tracker`; `scripts/approved_run.sh`; ruff `S101` for stripped asserts; the
vectorized-fits equivalence gate; the `rocq` job of `proofs.yml`, which compiles a pull request that touches a
proof path so the local-replay sentence leaves.

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
| No scheduled run; replays on demand | a drifted binding that a pull-request gate missed and a replay run after the next pin change found late; the fix is a pull-request gate for that binding, not a schedule |
| Claim coupling of retention | a retained acquisition that no claim ever cited and that a reader mistook for a result; the fix is a report of unclaimed acquisitions, not a block on retention |
| Seed essay reduced to one line | a merged seed the literal scan cannot see that produced a result the owner cannot replay; that falsifies the checker's coverage |
| Secret paragraphs replaced by a scanner | a credential that matches no scanner rule and reaches a commit; add the pattern, keep the one-line ban |
| Cancel sentence replaced by a tool deny | a cancel that reached a provider without an authority record; the deny sits on the wrong tool |

## Decisions for the owner

1. Adopt the forty-line guide in the appendix as the replacement for the 203-line text of PR #692, with
   the runbooks it points at (recommended; the appendix is the diff).
2. CI: lint, types and unit tests on each pull request and push to main; every gate of `ci/gates.json` on
   demand; no schedule; ruff out of the gate list (adopted).
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

Retained data. Raw provider data, a record an approval hashes and a published replay bundle keep their
path and bytes; a correction is a new file the old one's map row links. A derived analysis that a ledger
or digest binds is corrected in place in the change that refreshes its ledger or digest. raw/<job_id>/ is never rewritten. External-only sources live only in
the private gororoba-documents-private repository.

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

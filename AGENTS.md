# gororoba-quantum agent guide

This file carries the repository's own rules; the user-level agent guide
supplies what it leaves unstated. CLAUDE.md loads it.

## Layout and gates

The modules run as scripts from gororoba_quantum/ and form no installable
package; requirements.txt pins the tested runtime and pyproject.toml carries
lint and type-check configuration only. Before any push, these exit 0:

```sh
PYTHON=${PYTHON:-python3}
ruff check gororoba_quantum && ruff format --check gororoba_quantum
cd gororoba_quantum
mypy cd_core.py verify.py designs.py predict.py select_lcu.py experiments.py live_run.py order_finding.py
$PYTHON verify.py         # needs the open_gororoba checkout at GOROROBA_ROOT
$PYTHON designs.py
$PYTHON order_finding.py
```

A change to live_run.py or experiments.py also gets a dry run,
`$PYTHON live_run.py --out ../results/live`, whose audit record lands under
results/live/.

## QPU time and calibration

- The plan allows 600 s of quantum time on a rolling 28-day window: usage()
  reports a usage_period that ends at the moment of the call, so each second
  spent returns 28 days later and no reset date exists.
- Every `--submit` waits for the user's approval of a written case: what the
  run measures, why noise simulation cannot answer it, and its expected
  seconds. Calibration reads, transpilation, and noise simulation need no
  approval.
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

- Every PR gets a Codex review: the bot reviews on open, and the comment
  `@codex review` requests another.
- Each reachable thread is fixed in one push per PR, answered with the fixing
  commit, and resolved; then a re-review is requested, and the cycle repeats
  until a review comes back clean.
- Stacked PRs merge bottom-up. Retarget the next PR's base to main before
  deleting a merged branch, so GitHub does not close it.
- GitHub is polled over REST (`gh api`); GraphQL is reserved for resolving
  review threads.

## Records

- results/ holds audit records: hw_estimate/ for the fixed ibm_fez compile and
  live/ for live runs.
- A record names an IBM Cloud instance only by a 12-hex sha256 of its CRN.
- Tokens, account identifiers, and local absolute paths stay out of every
  commit. The IBM credential lives in the qiskit account store,
  `~/.qiskit/qiskit-ibm.json`.

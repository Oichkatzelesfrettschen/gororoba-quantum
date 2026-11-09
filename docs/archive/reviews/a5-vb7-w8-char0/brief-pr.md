# Brief: adversarial review of the pull request on branch a5/vb-degree7-export-and-w8-char0

Read first: docs/local/briefs/workspace-AGENTS.md (a copy of the workspace guide), then AGENTS.md at the root of this
checkout. Spawn no subagents. Never commit, push, stash, submit to a provider, start a Kaggle session or create a
cloud resource. Change no repository file except your report. Never signal a process you did not start: the
session's jobs run on this host and on the Windows workstation laptop.

You may run git, Python as `python3` (set `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`), Singular as
`Singular -q --no-rc < script`, shellcheck and `python3 ci/pinned_tool.py ruff check|mypy FILE`. Run at most one
computation at a time, under 8 GiB, in a scratch directory under /tmp.

Material: `git diff d970b76f3...HEAD` (this branch stacks on PR 803, whose head is d970b76f3), the files it touches,
and the records they cite. The reconciled earlier reviews are in docs/archive/reviews/a5-vb7-w8-char0/README.md. Read
the code and records as the authority, not the summaries.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. Engine v13 (docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v13.py) differs from v12 only in producing
   the export basis by `slimgb` under option(redSB), and keeps v11's export identity because the reduced basis is
   unique. Status: proved in part, measured in part (ledger A5-280). Falsifier: a code path in v13 that depends on the
   algorithm, or an N with a different basis.
2. The refuted levers and the refuted cofactor certificate are correctly refuted (A5-281, A5-282). Status: measured
   and argued. Falsifier: a load-matched win, or a valid certificate route the rows overlook.
3. Every launcher now propagates a failed child as a nonzero exit, and `run-cells-v13.sh` refuses more than four
   cells. Status: computed. Falsifier: an input that makes a launcher exit 0 after a failed child.
4. The Kaggle kernel generator (vb-export-levers/kaggle/make_kernels.py) builds jobs whose outputs can be compared
   byte for byte with the workstation exports. Status: argued. Falsifier: any difference in ring, ideal, options or
   write format between the kernel script and the v13 STD_SCRIPT.
5. AGENTS.md states the owner's ruling of 2026-11-09 (Kaggle under 12 h and scoped long runs approved; paid cloud and
   QPU keep a written case) without loosening any other provider rule. Status: argued. Falsifier: a sentence that
   now admits a provider job, upload or paid machine without a case.
6. The scope document (docs/design/a5-open-tasks-and-compute-scope.md) and plan
   (docs/design/a5-vb-degree7-and-w8-char0-plan.md) state no number that the cited records do not hold. Status:
   argued. Falsifier: a number without a source, or one that differs from its record.
7. The ledger rows A5-279 to A5-283 match their evidence and statuses. Falsifier: a status that the evidence does not
   support.

Also report, ranked by consequence: defects with file:line, missing tests, stale text, and anything a hosted reviewer
would flag. Mark every finding proved, computed, measured or hypothesis, with the file:line or command output behind
it. Write the report to the path named on your command line, under 300 lines.

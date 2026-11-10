# Brief: adversarial review of gororoba-quantum pull request 808 (branch least-squares-precision/portable-sweep, head 5ba6b3791)

Read first: <workspace>/AGENTS.md, then <worktree>/AGENTS.md.

Rules:
- Work read-only: change no file except your report (named at the end).
- Never commit, push, stash, or contact a remote host.
- Spawn no subagents.
- You may run git and `/usr/bin/python` with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`. Run no sweep; keep each computation under 10 minutes, scratch under /tmp.

## Material

Worktree <worktree>. Review the whole pull request: `git diff origin/main...HEAD` and the PR body `docs/local/pr-body.md`.
Your earlier review is `docs/local/reviews/codex-sweep.md`; its reconciliation, with nemotron's review and the
Advisor's verdicts, is `docs/local/reviews/reconcile-sweep.md`. The owner ruled on 2026-11-09 to keep `cap.bytes`.

## Claims under review

1. The fixes 068f1b71d, 549328395 and 5ba6b3791 resolve each of your seven findings as the reconciliation states.
2. The host rows carry only the public substrate profile: no kernel release, distribution, memory size, hostname, user name or local path.
3. Every README statement is supported by the rows at the strength it states, and each unrun check is marked not run.
4. `fp_host.quadblas_status` and the `quadblas` need skip exactly the configurations that call `numpy_quaddtype.set_num_threads`.

## Questions

Defects with file:line; overstatements; anything a hosted reviewer would flag (lint, types, tests, CI budget,
privacy). Report ranked by consequence; mark each claim proved, computed, measured or hypothesis. Write it to
<worktree>/docs/local/reviews/codex-pr808.md, under 100 lines.

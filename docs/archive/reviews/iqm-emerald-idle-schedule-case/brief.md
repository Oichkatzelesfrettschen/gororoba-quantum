# Brief: gororoba-quantum PR 959: written case for one IQM Emerald idle-schedule job

Read first: the workspace AGENTS.md, then the sections of the workspace reference (workspace/reference.md in gororoba-infrastructure) on comments, commits, pull requests and reviews, then the repository's AGENTS.md. Work read-only: change no file except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git and read files; keep any computation under 10 minutes in a scratch directory outside every repository.

Material: the worktree the branch worktree (repository gororoba-quantum); the change under review is `git diff origin/main...HEAD` there, and `git log origin/main..HEAD`.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The chosen qubits exist in the retained Emerald architecture (docs/evidence/iqm/qc/emerald/) and are mutually suitable as the case says.
2. Seconds and credits follow from the retained credit model (details.json rate, ceiling_credits in scripts/iqm_jobs.py) as computed.
3. The five-line pre-flight has a real falsifier and a decision per outcome; the Garnet comparison cites retained records correctly.
4. The credit expiry date: docs/evidence/iqm/account/credit.json says 2026-11-01; check what the case says.

## Questions to answer

- Defects in the change: code, claims and records, with file:line.
- Anything the change states that its sources do not support.

Report ranked by consequence, every claim tied to a file:line or a command with its output, each marked proved, computed, measured or hypothesis. Print it as your answer, under 120 lines.

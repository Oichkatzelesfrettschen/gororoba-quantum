# Brief: gororoba-quantum PR 957: retained draw, batch order and QX-twin results for the Tuna-17 interleaved case

Read first: the workspace AGENTS.md, then the sections of the workspace reference (workspace/reference.md in gororoba-infrastructure) on comments, commits, pull requests and reviews, then the repository's AGENTS.md. Work read-only: change no file except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git and read files; keep any computation under 10 minutes in a scratch directory outside every repository.

Material: the worktree the branch worktree (repository gororoba-quantum); the change under review is `git diff origin/main...HEAD` there, and `git log origin/main..HEAD`.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The batch order consumes the draw in index order with the rejection rule of qrng_request.json, and --check reproduces every generated file (read scripts/qi_tuna17_interleaved_cases.py; you may run its --check and --self-test offline if the interpreter is present, under 10 minutes).
2. The two test edits that pin DRAW to None keep the pending-state tests meaningful (they would fail if the pending branch broke).
3. The QX-twin analysis (tail 0/10, crosstalk 0/56, q9 offset 0.0125±0.0156 rad) follows from the committed results by the case analysis code; recompute one arm.
4. CASE.md status and draw lines are accurate; the 25.5 min wall time versus the predicted 289.8 s is recorded as a deviation.

## Questions to answer

- Defects in the change: code, claims and records, with file:line.
- Anything the change states that its sources do not support.

Report ranked by consequence, every claim tied to a file:line or a command with its output, each marked proved, computed, measured or hypothesis. Print it as your answer, under 120 lines.

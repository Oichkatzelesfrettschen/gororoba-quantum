# Brief: gororoba-quantum PR 960: written case for a controlled sim:belenos b1 repeat

Read first: the workspace AGENTS.md, then the sections of the workspace reference (workspace/reference.md in gororoba-infrastructure) on comments, commits, pull requests and reviews, then the repository's AGENTS.md. Work read-only: change no file except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git and read files; keep any computation under 10 minutes in a scratch directory outside every repository.

Material: the worktree the branch worktree (repository gororoba-quantum); the change under review is `git diff origin/main...HEAD` there, and `git log origin/main..HEAD`.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. The retained b1 job timings (544e010f at most 300 s; fa2da727 canceled at 305 s, 23 of 24 iterations) are read correctly from the retained records.
2. The ABAB design discriminates request cost from service variation; NOTE the owner chose three runs per request (6 jobs) on 2026-11-19, so review the design at three runs and say what the case text must change.
3. Credits and seconds follow from the retained usage reports and the 300 s platform limit.

## Questions to answer

- Defects in the change: code, claims and records, with file:line.
- Anything the change states that its sources do not support.

Report ranked by consequence, every claim tied to a file:line or a command with its output, each marked proved, computed, measured or hypothesis. Print it as your answer, under 120 lines.

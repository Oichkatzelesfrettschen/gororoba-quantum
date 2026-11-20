# Brief: gororoba-quantum PR 956: retained ANU draw record for an external benchmark seed set

Read first: the workspace AGENTS.md, then the sections of the workspace reference (workspace/reference.md in gororoba-infrastructure) on comments, commits, pull requests and reviews, then the repository's AGENTS.md. Work read-only: change no file except your report; never commit, push, stash, submit to a provider or start a cloud resource; spawn no subagents. You may run git and read files; keep any computation under 10 minutes in a scratch directory outside every repository.

Material: the worktree the branch worktree (repository gororoba-quantum); the change under review is `git diff origin/main...HEAD` there, and `git log origin/main..HEAD`.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. docs/evidence/anu_qrng/draw-2026-11-19T164733Z.json is a well-formed draw record: raw_sha256 equals sha256 of its raw bytes and values equal the raw JSON data (scripts/anu_qrng.py check logic; read it, do not run network).
2. The record names no secret (no key, header value or account id).
3. Whether gororoba-quantum keeps an index of draws and their consumers (search docs/notes/qrng/ and docs/evidence/anu_qrng/) that this PR must update.

## Questions to answer

- Defects in the change: code, claims and records, with file:line.
- Anything the change states that its sources do not support.

Report ranked by consequence, every claim tied to a file:line or a command with its output, each marked proved, computed, measured or hypothesis. Print it as your answer, under 120 lines.

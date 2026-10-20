# Quantum Inspire branch pair map

Read-only mapping. Merge base of both branches is 942319f (main after PR #144). No worktree was written.

## 1. Unique commits

docs/quantum-inspire-kbase only (6, oldest first):
- 9cf5991 crawl the full Quantum Inspire site, cQASM spec, SDK docs and releases into docs/notes/quantum_inspire.
- 9ce967d knowledge-base digest, cQASM reference, citations and releases.
- f83e014 drop pictographs from rendered captures; link live sources.
- ca8e104 guide index, durable platform facts, Ry failure message.
- 1c5b67b hardware queue rule in the backend, platform-fact and reconciliation pages.
- 34e157a capture gate core-346; no retained account identifiers.

quantum-inspire/tuna17-coupler-zz-map only (about 30 non-merge commits, oldest first, plus merges from docs/quantum-inspire-platform and main):
- 3e97230 bipartite conditional-Ramsey map of every Tuna-17 coupler's residual ZZ.
- 5575370 QX dry-run profile for the coupler ZZ map.
- 3897214 QX dry run of the coupler ZZ map.
- 99fb069 per-batch sanity gate for the coupler ZZ series.
- fbe021c Tuna-17 coupler residual-ZZ map and its spectator split.
- 7365672 refresh evidence digests after the merged branch-aware analysis.
- f2b96a1 BLAS-independent analysis bytes; typed rate vector.
- eee3ddf joint alias branch, paired quadrature batches, complete-batch checks.
- 488c3cf shared readout batch, readout-sensitivity bound, single-series analyses.
- 4d24e79 send the eight conformance evolutions to the process pool.
- Earlier on this branch (from the PR #144 review line): submission receipts, queue preflight, idempotent collection, token file permissions, strict hardware queue rule, MCP input guards, three-circuit case series, backend width preflight, emulator claim kind, digest-only pseudonyms, and the fixes that enforce source widths and catalogue admission before submission.

## 2. Files changed by both branches (relative to main)

Both branches change these two files:
- AGENTS.md
- docs/notes/quantum_inspire/experiments.md

`git merge-tree --write-tree docs/quantum-inspire-kbase quantum-inspire/tuna17-coupler-zz-map` reports no CONFLICT lines and exits 0. Both shared files auto-merge.

## 3. PR #146 against main

`git merge-tree --write-tree main quantum-inspire/tuna17-coupler-zz-map` reports no CONFLICT lines and exits 0. PR #146 has no conflicting files against main.

Side-by-side for the three named files:
- AGENTS.md: the kbase branch rewrites the Ry emulator sentence to say the failure message is "error interpreting cQASM script" with an empty log. The coupler branch changes the 2026-10-16 job count from twenty-two to forty-two and adds core-332 and core-333 to the gate list in the Quantum Inspire gates paragraph.
- ci/gates.json: the coupler branch adds gate entries core-332 (coupler map --check and --conformance, 1 s, pr tier) and core-333 (analyze replays of the Tuna-17 and QX series and the spectator split, 2 s, pr tier), and appends scripts/qi_coupler_zz_map.py to the ruff check, ruff format and mypy command lists. The kbase branch does not touch this file.
- docs/state/research_state.json: the coupler branch adds 167 lines of registry entries (QX dry-run batches 0 to 3 and Tuna-17 coupler batches) with no deletions. The kbase branch does not touch this file.

## 4. Older worktrees contained in docs/quantum-inspire-kbase

`git merge-base --is-ancestor` returns true for all three, and `git rev-list --count docs/quantum-inspire-kbase..BRANCH` is 0 for each:
- docs/spin-qubit-paper-sources (b91e753): ancestor, 0 unique commits.
- sim/quantum-inspire-ibm-noise (b37ed24): ancestor, 0 unique commits.
- state/multi-provider-acquisitions (a521418): ancestor, 0 unique commits.

`git -C` status in each of the three worktrees printed nothing, so none has uncommitted changes. Deleting them after docs/quantum-inspire-kbase merges loses no commits. Their worktrees and branches still need removal through the normal flow.

## Notes

- The quantum-inspire MCP server failed to connect (CONNECTION_CLOSED) during the session. It was not needed for this read-only task.
- Confidence: high for the commit, merge-tree and ancestry results (direct git output). The one-line summaries of the coupler branch's earlier commits come from subject lines only; their bodies were not read.

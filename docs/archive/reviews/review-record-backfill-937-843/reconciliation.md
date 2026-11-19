# Reconciliation: local review of PR 958 (docs/archive/reviews: records for merged pull requests)

Head read: the head before the fixing commit (inferred from the branch log, a7dff50d525146fe80f2bc8fbace6b353ac56093). Reviewer: the local codex round (gpt-daybreak-blue, read-only, exit 0), chosen by the owner on 2026-11-19; the Advisor last. Every finding below carries its disposition; a fixing commit is named by its full hash after its diff was read.

| # | Finding | Source | Check | Verdict |
|---|---|---|---|---|
| F1 | SERIOUS: the records say no finding was raised, then list Advisor findings | codex | README.md and reconciliation.md of the two records at the lines the report cites | Fixed in ee2aa8622e00dd1cec03de3508b4c54d57a1f249: hosted Codex raised none; the Advisor and worker findings are stated |
| F2 | SERIOUS: the record shape differs from the reference (no brief; table lacks Source and Check) | codex | find over the reference directory against the two records | Fixed in part by ee2aa8622e00dd1cec03de3508b4c54d57a1f249 (Source and Check columns); open as a boundary: both PRs are merged, no brief exists, and the records say so |
| F3 | SERIOUS: the orchestration source of the Advisor and worker receipts has no locator | codex | git grep on origin/main finds no such record | Open as a boundary: ee2aa8622e00dd1cec03de3508b4c54d57a1f249 states the source is a private session record this repository does not retain |
| F4 | SLOPPY: no index row or inbound link | codex | rg over docs/archive/reviews/README.md | Fixed in ee2aa8622e00dd1cec03de3508b4c54d57a1f249: the index links both records |
| C1-2 | Claims 1 and 2: merge-ancestry of the named commits; no leak | codex | git merge-base --is-ancestor for five commits; changed-text scan | Pass |
| A1 | Advisor (parent) | Advisor |  | Needs the abbreviated hashes expanded to 40 hex |
| A1f | The expansion | this record | git rev-parse for each hash; git merge-base --is-ancestor against refs/pull/937/head and refs/pull/843/head; the merge commits against origin/main | Fixed in b8893a86e2ea02a6f70c9d4a3157ec0c94067be4 (full hashes; each reachable as the READMEs state) |

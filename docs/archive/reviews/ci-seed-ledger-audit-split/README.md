# Review of the seed-ledger audit split (pull request 1013)

Pull request 1013 keeps the seed-ledger checks that need no retained tree in every pull request and moves the checks
that read the 5.27 GB tree under results/ behind `audit`, as the owner chose after the hosted Codex P1 on pull
request 1012 ([its review record](../ci-macos-pytest-step/README.md)).

## Reviewers

The owner chose no local reviewers. The Advisor reviewed the first head, and the hosted Codex round ran on head
a9c381b75.

## Advisor findings

| Finding | Disposition |
|---|---|
| Marking the owned/reserved and runtime-ledger tests `audit` removed more from pull requests than the body named | Fixed in d2a6c2dfe and a9c381b75: `check_tree_once(retained=False)` keeps the owned and reserved rows in every pull request, since they reach the tree only through the manifest claims; the runtime ledger needs the tree, and AGENTS.md, ci/AGENTS.md and the body now name it as a cost |
| `check_tree(None, retained=False)` still read the tree through `check_tree_once` | Fixed in the same commits: the flag passes through |
| The gate the guide names had not run by name | Run: `sh ci/pr_checks.sh gates --gates core-behavior-01` passed in 54.3 s; its `seconds` entry only selects gates for `--max-seconds` |
| The validation timings mixed runs | Fixed in the body: the seed file alone, cold, took 16 s here and 43 s on main after #1012 |
| The hosted effect was unmeasured | Measured in run 45693986275: seed-provenance tests 20.3 s on macos-26 core, 27.4 s on the x64 core shard, 12.7 s on ubuntu-26.04-arm, and no tree test in any pull-request selection |

## Hosted Codex round (head a9c381b75)

Codex completed the round with no findings.

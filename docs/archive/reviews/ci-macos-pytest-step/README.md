# Review of the macOS pytest-step change (pull request 1012)

Pull request 1012 splits the macOS arm64 pytest leg of `pr.yml` into two shards, reads the retained tree once per
xdist worker in `ci/seed_provenance.py`, and removes the reverse lookup from the redirect test's servers (issue 1009).

## Reviewers

The owner chose no local reviewers for this pull request. The Advisor reviewed it, and the hosted Codex round ran on
head da350c607.

## Advisor findings

| Finding | Disposition |
|---|---|
| The `xdist_group` mark that was to pin the tree checks to one worker has no effect | Measured: pytest 9.2.0 reads `Node._id` and pytest-xdist 3.8.0 writes `_nodeid`; the mark left the pull request, the read is once per worker, and issue 1011 records the inert marks |
| The precompile comment attributed the 45 s macOS start-up to compilation | Fixed in da350c607: run 45681335219 measured 38 s and 25 s start-up per shard, and ubuntu-26.04-arm moved from 14 s to 12 s with the same step |
| The `pr.yml` comment cited the 35.6 s call as slow repository reads | Fixed in da350c607: that call was the getfqdn lookup; the comment cites the measured 1.97 times per-test ratio |
| The `tree_scan` docstring stated the page-cache cause as fact | Fixed in da350c607: the cause is marked as a hypothesis beside the measured pass times |
| `--check` now runs the reference parse | Recorded in the pull-request body: a malformed retained file with a `qrng:` reference now fails `--check` as well as `--runtime`; the suite verdict is unchanged |

## Hosted Codex round (head da350c607)

| Finding | Reply |
|---|---|
| P1: keep the retained-tree scan behind the `audit` marker, since the module fixture moves the read out of the call budget | Boundary: ci/AGENTS.md ("Behavioral suite") puts a large retained read behind `audit`, while AGENTS.md has `ci/seed_provenance.py` enforce the seed ledger in the `tests` check. The choice belongs to the owner; the read sits outside the call budget and inside the 10-minute step timeout |

## Measured outcome

Runs 45681335219 and 45683699892 passed every job. The macOS core shard's pytest step took 231 s and 194 s, the
scripts shard's 167 s and 271 s, each inside 75 percent of its 600 s limit. The redirect test took 0.508 s and
0.512 s on macOS, against 35.6 s in each of the five runs before.

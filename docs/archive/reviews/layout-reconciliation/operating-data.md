# Operating data behind the falsification pass (2026-10-30)

Every row below was read from the GitHub REST API, `ci/gates.json`, `docs/state/plans/` and the git log of
main at `a1d1743` on 2026-10-30, by scripts kept in the session scratch directory. A later measurement
replaces a number, not the mechanism it exposes.

## Codex review loop over the last 60 merged pull requests

| Quantity | Value |
|---|---|
| `@codex review` requests | 312 (median 4 per PR, mean 5.2) |
| Root review threads | 142 (31 PRs had at least one; 29 had none) |
| Replies beginning `Fixed` / `Refuted` / `Boundary` | 110 / 7 / 1 |
| Requests spent on the 29 PRs that produced no thread | 91 |
| Requests per thread | 2.2 |
| Open-to-merge time | median 0.45 h, mean 2.2 h; five PRs above 8 h (#661 15.7 h with 49 commits, #639 15.3 h with 73 commits) |
| Commits per PR | median 4, mean 8.6 |

## `pr.yml` jobs over the last 100 pull-request runs

| Job | Failures | Median minutes | Maximum minutes |
|---|---|---|---|
| lint | 0 | 1.2 | 4.0 |
| types | 0 | 2.7 | 8.8 |
| tests | 13 | 5.1 | 7.9 |
| gates | 9 | 2.8 | 8.8 |

## `ci.yml` audit over the last 60 runs

| Trigger | Success | Failure | Cancelled |
|---|---|---|---|
| schedule (nightly) | 1 | 8 | 0 |
| workflow_dispatch | 13 | 7 | 8 |
| pull_request | 9 | 5 | 3 |
| push | 2 | 2 | 2 |

Wall time median 25 min, maximum 80 min, over 12 gate shards. The run of 2026-10-30 09:24 UTC failed 16
gates; 12 of them are cited by no claim (`core-074--experiment_source_manifest`,
`core-074--fused_collection`, `core-289`, `core-339`, `core-409`, `core-582`, `core-583`,
`core-597--slice0..3`, `core-614`, `core-plan-tracker`). The tracking issue "Nightly audit failing" (#554)
has been open since 2026-10-26; the repair pull requests #678, #680 and #681 landed on 2026-10-30 and the
next scheduled run still failed.

## Gate cost from `ci/gates.json`

| Quantity | Value |
|---|---|
| Gates | 633: 464 `pr` tier (48 measured minutes in total), 169 `full` tier (456 minutes) |
| Measured seconds | median 5.3 s; 438 gates at or under 15 s, 123 between 15 and 60 s, 72 above 60 s |
| `pr`-tier gates above the 15 s pull-request cutoff | 51 (a reached gate above the cutoff defers to the nightly audit) |
| Costliest gates | `core-769` 9,000 s; six Ascella signed-coherence replays 505 to 885 s; `core-661` 834 s; `core-primorial-probe-case-replay` 720 s |

## Dry-run directories against the commits that require them

The merge rule requires a live dry run for every change to `live_run.py` or `experiments.py`. Over
2026-10-10 to 2026-10-30, 262 commits touched those two files (13 per day) and `results/live/` gained 351
directories, 102 of them holding only `record.json` and `isa.qpy`. Per day, the count of bare dry-run
directories and the count of commits touching the two files have Pearson r = 0.87 (19 days; the two
heaviest days, 2026-10-10 and 2026-10-11, hold 86 commits and 50 bare directories).

## Instruction text loaded into every agent session

| File | Lines | Bytes |
|---|---|---|
| `AGENTS.md` (repository) | 534 | 32,822 |
| `ci/AGENTS.md` | 490 | 32,134 |
| user-level agent guide | 411 | 27,206 |
| `docs/runbooks/` (23 files) | 3,549 | |

The repository guide and the CI guide together hold 148 sentences carrying "every", "never", "waits",
"requires", "must" or "only". The user-level guide sets a 200-line budget for a root instruction file.

## Work records

141 plan records: 74 `inbox`, 50 `closed`, 13 `active`, 2 `paused`, 2 `planned`; 488 steps, 292 done.
The `core-plan-tracker` gate is among the nightly failures above.

# Review of PR 935 (the macOS arm leg on macos-26)

The owner chose no local reviewer beyond the Advisor for this pull request. The Advisor read the pull request head
`47d8f58a9` (the merge of main `91bdb304f` into the branch commit `5c3604b10`). The hosted Codex round is requested
on the head that carries this record, in the order of `AGENTS.md` ("Reviews and merges"); its threads hold its
findings. No reviewer brief file exists for the Advisor, which read the pull request from the session. Where a source
is silent the entry reads "not recorded".

## Reviewers and heads

| Reviewer | Head read | Requested | Posted | Findings |
|---|---|---|---|---|
| Advisor | `47d8f58a9` | not recorded | not recorded | evidence sound; four items below, none blocking |

## Findings and dispositions

| # | Reviewer | Finding | Check against the source | Verdict | Action |
|---|---|---|---|---|---|
| 1 | Advisor | The diff changes four files and nothing else names the label | `.github/workflows/pr.yml` (matrix entry and one comment), `.github/actions/pins-venv/action.yml` (cache key image), `ci/AGENTS.md` (the job list and the branch-protection sentence) and `tests/platform_expectations.py` (the platform note); the `darwin-arm64` strict-expected-failure entries are untouched | confirmed | none needed |
| 2 | Advisor | `docs/runbooks/ci-runtime.md` still names `macos-15` | line 99 records a past failed run by its run number, job number and image (`macos-15-arm64/20261104.0514`); the image name is the evidence of that incident, so the line keeps its text | confirmed as a dated record | the body's Validation states why the line stays |
| 3 | Advisor | The record that the new runner leaves the expectations unchanged | the macos-15 job of the push run for main `91bdb304f` (run 43987669520) and the macos-26 job of run 43987918872 on the branch head read the same main commit plus the four-file diff; both report 7052 passed, 60 skipped, 14 xfailed (355.17 s and 324.15 s) and 83 passed for the contract suites; no strict expected failure flipped and no new failure appeared | confirmed | none needed |
| 4 | Advisor | Hygiene of the body and the branch commit bodies | the commit body of `5c3604b10` and the merge commit body carry no host, session or local path; the body's Validation line named the machine class that ran no jobs | holds | the body now says the checks ran on hosted runners and names no machine of the author's |
| 5 | Advisor | Merge sequencing against branch protection | the read-only protection response lists the required contexts `tests`, `lint`, `types`, `contracts`, `arm (ubuntu-26.04-arm)` and `arm (macos-15)`; this branch no longer produces the last one, and `ci/AGENTS.md` states that protection does not require the branch to be current with main | holds | the body's Residual risk carries the swap before the merge, the `main` merge every other open pull request then needs, the capacity notice on the runner class and the rollback (restore the saved contexts, revert this change) |

## Validation at the reviewed head

The six `pr.yml` checks (`lint`, `types`, `tests`, `contracts`, `arm (ubuntu-26.04-arm)`, `arm (macos-26)`) passed on
`47d8f58a9` in run 43987918872. The branch-protection read changed nothing.

## Not recorded

- The time of the Advisor request and its posting.
- Any hosted review before the one this record precedes.

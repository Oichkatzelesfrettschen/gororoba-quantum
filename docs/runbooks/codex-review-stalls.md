# Codex review stalls

A Codex review round sometimes never completes. The bot reacts with eyes to the
`@codex review` comment, its summary comment reads Running for the current
head, and no review, clean comment or reaction follows. The round stays
Running for hours and never completes. A fresh `@codex review` on the same head
starts a new round, which usually completes.
`scripts/codex_review_wait.sh` applies that remedy: it waits for the round and
the head's check runs, sends one repeated request when a round shows no result
600 seconds after it started, and stops with exit 5 when the repeated request
also stalls, which leaves the next step to the owner.

```sh
sh scripts/codex_review_wait.sh PR 3600 LOG
```

The script exits 0 when the review of the head and every check run on it have
completed, 2 at the deadline, 3 after five consecutive poll failures, 4 when
the pull request conflicts with its base and 5 on a second stall. A conflicting
pull request gets no merge commit and no check runs from GitHub, so it waits
on a merge of the base, which the operator pushes, rather than on a review.

## Measurement

Every `@codex review` request on pull requests 590 to 673 (223 requests, 2026-10-27
to 2026-10-30) was classified by whether a Codex review or clean comment
followed before the next request on the same pull request. For each request,
`git merge-tree` also checked whether the pull request head as of that moment
merged cleanly into the first-parent main as of that moment. 31 requests
(14 %) received no result. The 31 include requests that a later push
superseded within minutes, so the rate of true stalls is at most 14 %.

| candidate cause | observation | verdict |
| --- | --- | --- |
| the head conflicts with main, so GitHub builds no merge ref | 27 of the 31 unanswered requests had a clean merge; 20 of the 24 requests on a conflicting head were answered | refuted |
| several pull requests requested within ten minutes | unanswered share 0.17, 0.14, 0.13 and 0.12 with 0, 1, 2 and 3 or more other requests in the window | refuted |
| diff size | stalls hit pull requests of 3 files (#623) and of 787 files (#661) alike | refuted |
| a draft-to-ready toggle restarts a dropped round | no new round on a stalled pull request (2026-10-28 trial) | refuted |
| the round is dropped by the service | a stall follows a stall on the same pull request 6 times in 25, against 15 times in 123 after an answered request; a repeated request on the same head was answered 7 times in 8 | consistent |

No property of the repository or the pull request that these checks read predicts a stall. The
remedy is therefore a timed repeat rather than a change to the pull request.
Answered requests took a median of 2.7 minutes, with the 95th percentile at
6.4 minutes and the slowest at 10.2 minutes (115 requests on #590 to #634),
which sets the 600-second stall threshold.

A falsifier for the service-drop reading is a property that separates stalled
from answered requests at a rate well above the 14 % base, for example the
bot's eyes reaction arriving late or a summary update that never names the
head. A record of those fields per request would test it.

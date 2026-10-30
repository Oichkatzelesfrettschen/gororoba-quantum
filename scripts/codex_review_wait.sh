#!/bin/sh
# Wait until the Codex review of a pull request's head completes and every
# check run on that head has completed, then print the review status line and
# the check conclusions. A round with no result STALL seconds after its
# request gets one fresh `@codex review` on the same head, because a dropped
# round never completes on its own and a same-head request starts a new one
# (docs/runbooks/codex-review-stalls.md). A pull request that conflicts with its
# base gets no merge commit and no check runs, so the wait stops and names it.
# Usage: scripts/codex_review_wait.sh PR DEADLINE_SECONDS LOG [STALL_SECONDS]
# Exit: 0 review and checks done, 2 deadline, 3 consecutive poll failures,
# 4 the pull request conflicts with its base, 5 the repeated request also stalled.
set -eu

[ "$#" -ge 3 ] || { echo "usage: $0 PR DEADLINE_SECONDS LOG [STALL_SECONDS]" >&2; exit 2; }
pr=$1
deadline=$2
log=$3
stall=${4:-600}
here=$(cd "$(dirname "$0")" && pwd)
slug=$(git -C "$here" remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')

child=
cleanup() { if [ -n "$child" ]; then kill "$child" 2>/dev/null || true; fi; }
trap cleanup EXIT
trap 'exit 130' INT TERM HUP

end=$(( $(date +%s) + deadline ))
failures=0
retried_round=
status=
pending=
while :; do
    if status=$(timeout -k 10 120 sh "$here/codex_review_status.sh" "$pr" 2>>"$log" | head -n 1) &&
        pull=$(timeout -k 10 60 gh api "repos/$slug/pulls/$pr" --jq '"\(.head.sha) \(.mergeable_state)"' 2>>"$log") &&
        head=${pull% *} && mergeable=${pull#* } &&
        pending=$(timeout -k 10 60 gh api "repos/$slug/commits/$head/check-runs?per_page=100" \
            --jq '[.check_runs[] | select(.status != "completed")] | length' 2>>"$log"); then
        failures=0
        echo "$(date -u +%FT%TZ) mergeable=$mergeable pending=$pending $status" >>"$log"
        if [ "$mergeable" = dirty ]; then
            echo "PR $pr conflicts with its base: no merge commit, no check runs; merge the base and push"
            exit 4
        fi
        short=$(printf '%.7s' "$head")
        # A completed round reads a stable snapshot and a verdict for the latest request:
        # clean, or findings to read; pending means a newer request postdates the summary.
        case "$status" in
            *review=done*"summary-head=$short"*snapshot=stable*verdict=clean-* | \
                *review=done*"summary-head=$short"*snapshot=stable*verdict=open-threads* | \
                *review=done*"summary-head=$short"*snapshot=stable*verdict=later-finding*)
                if [ "$pending" = 0 ]; then
                    echo "$status"
                    gh api "repos/$slug/commits/$head/check-runs?per_page=100" \
                        --jq '.check_runs[] | "\(.name) \(.conclusion)"'
                    exit 0
                fi
                ;;
            *)
                round=$(printf '%s\n' "$status" | sed -n 's/.* round-start=\([^ ]*\) .*/\1/p')
                if [ -n "$round" ] && [ "$round" != - ] && [ "$round" != "$retried_round" ] &&
                    [ $(( $(date +%s) - $(date -d "$round" +%s) )) -ge "$stall" ]; then
                    if [ -n "$retried_round" ]; then
                        echo "PR $pr: the repeated request of round $retried_round also stalled; last: $status"
                        exit 5
                    fi
                    timeout -k 10 60 gh api "repos/$slug/issues/$pr/comments" -f body='@codex review' >/dev/null
                    echo "$(date -u +%FT%TZ) round $round showed no result after ${stall}s; requested again" >>"$log"
                    retried_round=$round
                fi
                ;;
        esac
    else
        failures=$((failures + 1))
        if [ "$failures" -ge 5 ]; then echo "PR $pr: 5 consecutive poll failures; see $log"; exit 3; fi
    fi
    if [ "$(date +%s)" -ge "$end" ]; then echo "PR $pr: deadline; last: $status pending=$pending"; exit 2; fi
    sleep 90 &
    child=$!
    wait "$child"
    child=
done

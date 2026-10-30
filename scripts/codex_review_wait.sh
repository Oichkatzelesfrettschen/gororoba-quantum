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
retried_at=
status=
pending=
while :; do
    # The status command's own exit status counts as a poll failure, so it is captured before its first line.
    if report=$(timeout -k 10 120 sh "$here/codex_review_status.sh" "$pr" 2>>"$log") &&
        status=$(printf '%s\n' "$report" | head -n 1) && [ -n "$status" ] &&
        pull=$(timeout -k 10 60 gh api "repos/$slug/pulls/$pr" --jq '"\(.head.sha) \(.mergeable_state)"' 2>>"$log") &&
        head=${pull% *} && mergeable=${pull#* } &&
        pending=$(timeout -k 10 60 gh api "repos/$slug/commits/$head/check-runs?per_page=100" \
            --jq '[.check_runs[] | select(.status != "completed")] | length' 2>>"$log"); then
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
                # The repeated request is timed from when this script sent it: the summary can keep an older
                # round-start until the bot picks the new request up.
                now=$(date +%s)
                if [ -n "$retried_at" ]; then
                    if [ $((now - retried_at)) -ge "$stall" ]; then
                        echo "PR $pr: the repeated request also showed no result after ${stall}s; last: $status"
                        exit 5
                    fi
                else
                    # The round starts at the later of the summary's round-start and the newest request, since the
                    # summary keeps an older round-start until the bot picks a new request up.
                    round=$(printf '%s\n' "$status" | sed -n 's/.* round-start=\([^ ]*\) .*/\1/p')
                    # A failed fetch counts as a failed poll: the stale round-start alone would spend the retry early.
                    if ! requests=$(timeout -k 10 60 gh api --paginate "repos/$slug/issues/$pr/comments" \
                        --jq '.[] | select(.body | startswith("@codex review")) | .created_at' 2>>"$log"); then
                        failures=$((failures + 1))
                        if [ "$failures" -ge 5 ]; then echo "PR $pr: 5 consecutive poll failures; see $log"; exit 3; fi
                        sleep 90 &
                        child=$!
                        wait "$child"
                        child=
                        continue
                    fi
                    requested=$(printf '%s\n' "$requests" | sort | tail -n 1)
                    start=0
                    if [ -n "$round" ] && [ "$round" != - ]; then start=$(date -d "$round" +%s); fi
                    if [ -n "$requested" ] && [ "$(date -d "$requested" +%s)" -gt "$start" ]; then
                        start=$(date -d "$requested" +%s)
                    fi
                    if [ "$start" -gt 0 ] && [ $((now - start)) -ge "$stall" ]; then
                        timeout -k 10 60 gh api "repos/$slug/issues/$pr/comments" -f body='@codex review' >/dev/null
                        echo "$(date -u +%FT%TZ) round $round showed no result after ${stall}s; requested again" >>"$log"
                        retried_at=$now
                    fi
                fi
                ;;
        esac
        failures=0
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

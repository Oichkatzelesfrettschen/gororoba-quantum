#!/bin/sh
# Post `@codex review` on a pull request only when the rules of AGENTS.md
# "Reviews and merges" admit a new round:
# - the pull request's own diff changed since the head of the last completed
#   round, so a merge of main or a conflict-free regeneration earns no request;
#   the diff is compared by `git patch-id --stable` of merge-base..head against
#   the current origin/main, which leaves out every commit main contributed;
# - fewer than MAX_ROUNDS rounds were requested, where a round is a request
#   separated from the previous counted request by at least one pushed commit
#   (a same-head repeat after a stalled round counts once).
# A refusal names its reason and exits 3; the owner decides a third round.
# Usage: scripts/codex_review_request.sh PR [MAX_ROUNDS]
# Exit: 0 requested, 2 usage or lookup failure, 3 refused.
set -eu

[ "$#" -ge 1 ] || { echo "usage: $0 PR [MAX_ROUNDS]" >&2; exit 2; }
pr=$1
max=${2:-2}
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
slug=$(git -C "$repo" remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')

# Rounds requested so far: walk the timeline in order; a request opens a round
# when it is the first one or a commit arrived after the last counted request.
rounds=$(gh api --paginate "repos/$slug/issues/$pr/timeline?per_page=100" \
    --jq '.[] | if .event == "committed" or .event == "head_ref_force_pushed" then "c"
              elif .event == "commented" and ((.body // "") | startswith("@codex review")) then "r"
              else empty end' |
    awk 'BEGIN { n = 0; fresh = 1 } $0 == "c" { fresh = 1 } $0 == "r" && fresh { n++; fresh = 0 } END { print n }')
if [ "$rounds" -ge "$max" ]; then
    echo "PR $pr: $rounds automated review rounds already requested (cap $max); ask the owner" >&2
    exit 3
fi

status=$(sh "$here/codex_review_status.sh" "$pr" | head -n 1)
summary=$(printf '%s\n' "$status" | sed -n 's/.* summary-head=\([0-9a-f]\{7,\}\).*/\1/p')
if [ -n "$summary" ]; then
    head=$(gh api "repos/$slug/pulls/$pr" --jq .head.sha)
    git -C "$repo" fetch -q origin "+refs/heads/main:refs/remotes/origin/main" "pull/$pr/head"
    reviewed=$(git -C "$repo" rev-parse --verify -q "$summary^{commit}") || {
        echo "PR $pr: reviewed head $summary is not reachable locally" >&2
        exit 2
    }
    diff_id() {
        base=$(git -C "$repo" merge-base origin/main "$1")
        git -C "$repo" diff "$base" "$1" | git -C "$repo" patch-id --stable | cut -d ' ' -f 1
    }
    if [ "$(diff_id "$reviewed")" = "$(diff_id "$head")" ]; then
        echo "PR $pr: the diff of head $(printf '%.7s' "$head") equals the reviewed head $summary; no request" >&2
        echo "  wait with: sh scripts/codex_review_wait.sh $pr DEADLINE LOG 600 $summary" >&2
        exit 3
    fi
fi

gh api "repos/$slug/issues/$pr/comments" -f body='@codex review' >/dev/null
echo "PR $pr: requested automated review round $((rounds + 1)) of $max"

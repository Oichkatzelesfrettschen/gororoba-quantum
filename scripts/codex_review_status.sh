#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $endCursor) belong to the query text,
# so the single quotes are deliberate.
# shellcheck disable=SC2016
# Report, per pull request, the head commit, the state of the Codex review, the
# latest Codex verdict, and every unresolved review thread: its root comment
# id, path, and full body, which is what triage reads.
# Usage: scripts/codex_review_status.sh PR [PR...]
set -eu

[ "$#" -gt 0 ] || { echo "usage: $0 PR [PR...]" >&2; exit 2; }

slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}

for pr in "$@"; do
    head=$(gh api "repos/$slug/pulls/$pr" --jq '.head.sha[0:7]')
    # --paginate walks every page of issue comments, so the newest summary and
    # verdict are found however many comments the PR carries. The bot keeps
    # one summary comment per PR and edits it; it reads Running while a review
    # is in progress.
    state=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login | test("codex"; "i"))
            | select(.body | test("codex-pull-request-review-summary"))
            | if (.body | test("Running")) then "running" else "done" end' | tail -n 1)
    verdict=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login | test("codex"; "i"))
            | select(.body | test("codex-pull-request-review-summary") | not)
            | (.created_at + " " + (.body | split("\n")[0]))' | tail -n 1)
    echo "PR $pr head=$head review=${state:-none} latest-verdict: ${verdict:-no clean-review comment}"
    # GraphQL pagination: gh api --paginate follows pageInfo.endCursor.
    gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
        query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes { isResolved comments(first: 1) { nodes { databaseId path line body } } }
              }
            }
          }
        }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
                 | select(.isResolved | not) | .comments.nodes[0]
                 | "--- open \(.databaseId) \(.path):\(.line // "?")\n\(.body
                     | gsub("<sub><sub>!\\[(?<b>P[0-9]) Badge\\]\\([^)]*\\)</sub></sub>"; "[\(.b)]")
                     | gsub("\n\nUseful\\? React with[^\n]*"; ""))\n"'
done

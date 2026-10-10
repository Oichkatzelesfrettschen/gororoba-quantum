#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $id) belong to the query text, so
# the single quotes are deliberate.
# shellcheck disable=SC2016
# Report, per pull request, the head commit, the state of the Codex review, the
# latest Codex verdict, and every unresolved review thread with its root
# comment id. Usage: scripts/codex_review_status.sh PR [PR...]
set -eu

[ "$#" -gt 0 ] || { echo "usage: $0 PR [PR...]" >&2; exit 2; }

slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}

for pr in "$@"; do
    head=$(gh api "repos/$slug/pulls/$pr" --jq '.head.sha[0:7]')
    # The bot keeps one summary comment per PR and edits it; it reads Running
    # while a review is in progress.
    state=$(gh api "repos/$slug/issues/$pr/comments" --jq '
        [.[] | select(.user.login | test("codex"; "i"))
             | select(.body | test("codex-pull-request-review-summary"))
             | if (.body | test("Running")) then "running" else "done" end] | last // "none"')
    verdict=$(gh api "repos/$slug/issues/$pr/comments" --jq '
        [.[] | select(.user.login | test("codex"; "i"))
             | select(.body | test("codex-pull-request-review-summary") | not)
             | (.created_at + " " + (.body | split("\n")[0]))] | last // "no clean-review comment"')
    echo "PR $pr head=$head review=$state latest-verdict: $verdict"
    gh api graphql -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
        query($owner: String!, $repo: String!, $pr: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(first: 100) {
                nodes { isResolved comments(first: 1) { nodes { databaseId path body } } }
              }
            }
          }
        }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
                 | select(.isResolved | not) | .comments.nodes[0]
                 | "  open \(.databaseId) \(.path): \(.body | split("\n")[0]
                     | gsub("<sub><sub>!\\[(?<b>P[0-9]) Badge\\]\\([^)]*\\)</sub></sub>"; "[\(.b)]")
                     | .[0:110])"'
done

#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $endCursor) belong to the query text,
# so the single quotes are deliberate.
# shellcheck disable=SC2016
# Report, per pull request, the head commit, the state of the Codex review, the
# latest Codex verdict, and every unresolved review thread: its root comment
# id, path, and every comment in it with its author, so a rejection posted after
# an answer is read with the finding.
# Usage: scripts/codex_review_status.sh PR [PR...]
set -eu

[ "$#" -gt 0 ] || { echo "usage: $0 PR [PR...]" >&2; exit 2; }

slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}

for pr in "$@"; do
    head=$(gh api "repos/$slug/pulls/$pr" --jq '.head.sha[0:7]')
    # Comments count as the reviewer's only under the app's exact login, so a
    # user whose name merely contains codex cannot forge a state or verdict.
    # --paginate walks every page of issue comments, so the newest summary and
    # verdict are found however many comments the PR carries. The bot keeps
    # one summary comment per PR and edits it; it reads Running while a review
    # is in progress.
    # Each request's output lands in a variable before the last match is taken,
    # so a failed request stops the script under set -e instead of being masked
    # by a pipeline that ends in tail.
    states=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login == "chatgpt-codex-connector[bot]")
            | select(.body | test("codex-pull-request-review-summary"))
            | if (.body | test("Running")) then "running" else "done" end')
    verdicts=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login == "chatgpt-codex-connector[bot]")
            | select(.body | test("codex-pull-request-review-summary") | not)
            | (.created_at + " " + (.body | split("\n")[0]))')
    state=$(printf '%s\n' "$states" | tail -n 1)
    verdict=$(printf '%s\n' "$verdicts" | tail -n 1)
    echo "PR $pr head=$head review=${state:-none} latest-verdict: ${verdict:-no clean-review comment}"
    # GraphQL pagination: gh api --paginate follows pageInfo.endCursor.
    gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
        query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  isResolved
                  root: comments(first: 1) { nodes { databaseId path line } }
                  comments(last: 100) { nodes { author { login } body } }
                }
              }
            }
          }
        }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
                 | select(.isResolved | not)
                 | .root.nodes[0] as $root
                 | "--- open \($root.databaseId) \($root.path):\($root.line // "?")\n"
                   + ([.comments.nodes[]
                       | "[\(.author.login)] " + (.body
                         | gsub("<sub><sub>!\\[(?<b>P[0-9]) Badge\\]\\([^)]*\\)</sub></sub>"; "[\(.b)]")
                         | gsub("\n\nUseful\\? React with[^\n]*"; ""))]
                      | join("\n\n")) + "\n"'
done

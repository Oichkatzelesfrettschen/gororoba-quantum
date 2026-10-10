#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $id, $endCursor) belong to the query
# text, so the single quotes are deliberate.
# shellcheck disable=SC2016
# Resolve the unresolved review threads of one pull request that carry an
# answer from the authenticated operator, and list every other open thread as
# unanswered. An answer is a reply whose text begins with one of the markers
# AGENTS.md defines: "Fixed in <commit>", "Refuted:", or "Boundary:". Any
# other reply, from anyone, leaves the thread open.
# Usage: scripts/resolve_answered_threads.sh PR
set -eu

[ "$#" -eq 1 ] || { echo "usage: $0 PR" >&2; exit 2; }
pr=$1
slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}
operator=$(gh api user --jq .login)

# Every page of threads (gh api --paginate follows pageInfo.endCursor); one
# line per open thread: thread id, root comment id, count of marked answers.
threads=$(gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
    query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100, after: $endCursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id isResolved
              comments(first: 100) { nodes { databaseId author { login } body } }
            }
          }
        }
      }
    }' --jq ".data.repository.pullRequest.reviewThreads.nodes[]
             | select(.isResolved | not)
             | [.id, (.comments.nodes[0].databaseId | tostring),
                ([.comments.nodes[1:][]
                  | select(.author.login == \"$operator\")
                  | select(.body | test(\"^(Fixed in [0-9a-f]{7,40}|Refuted:|Boundary:)\"))]
                 | length | tostring)]
             | join(\" \")")

# Thread ids, comment ids, and counts contain no spaces, so word splitting on
# each line is exact.
echo "$threads" | while read -r thread root answers; do
    [ -n "$thread" ] || continue
    if [ "$answers" -gt 0 ]; then
        gh api graphql -F id="$thread" -f query='
            mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }' \
            --jq '.data.resolveReviewThread.thread.isResolved' >/dev/null
        echo "resolved thread of comment $root"
    else
        echo "unanswered: comment $root (left open)"
    fi
done

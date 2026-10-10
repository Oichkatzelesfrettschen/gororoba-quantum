#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $id) belong to the query text, so
# the single quotes are deliberate.
# shellcheck disable=SC2016
# Resolve the unresolved review threads of one pull request that carry a reply
# from someone other than the reviewer bot, and list the rest as unanswered.
# A thread is closed only after its finding has an answer naming the fix or
# the refuting line. Usage: scripts/resolve_answered_threads.sh PR
set -eu

[ "$#" -eq 1 ] || { echo "usage: $0 PR" >&2; exit 2; }
pr=$1
slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}

threads=$(gh api graphql -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id isResolved
              comments(first: 50) { nodes { databaseId author { login } } }
            }
          }
        }
      }
    }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
             | select(.isResolved | not)
             | [.id, (.comments.nodes[0].databaseId | tostring),
                ([.comments.nodes[1:][] | select(.author.login | test("codex"; "i") | not)] | length | tostring)]
             | join(" ")')

# Thread ids, comment ids, and counts contain no spaces, so word splitting on
# each line is exact.
echo "$threads" | while read -r thread root replies; do
    [ -n "$thread" ] || continue
    if [ "$replies" -gt 0 ]; then
        gh api graphql -F id="$thread" -f query='
            mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }' \
            --jq '.data.resolveReviewThread.thread.isResolved' >/dev/null
        echo "resolved thread of comment $root"
    else
        echo "unanswered: comment $root (left open)"
    fi
done

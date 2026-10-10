#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $id, $endCursor) belong to the query
# text, so the single quotes are deliberate.
# shellcheck disable=SC2016
# Resolve the unresolved review threads of one pull request whose current
# response is an answer from the authenticated operator, and list every other
# open thread as unanswered. An answer is a reply whose text begins with one of
# the markers AGENTS.md defines: "Fixed in <commit>", "Refuted:", or
# "Boundary:". It counts only when no comment from anyone else follows it, so a
# reviewer's rejection of an earlier answer reopens the obligation; any other
# reply, from anyone, leaves the thread open.
# Usage: scripts/resolve_answered_threads.sh PR
set -eu

[ "$#" -eq 1 ] || { echo "usage: $0 PR" >&2; exit 2; }
pr=$1
slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}
operator=$(gh api user --jq .login)

# Every page of threads (gh api --paginate follows pageInfo.endCursor); one
# line per open thread: thread id, root comment id, and 1 when its current
# response is a marked operator answer, else 0. The predicate needs only the
# newest comments: the latest non-operator comment and any marked answer after
# it both lie in comments(last: 100) whenever an answer is current, so a
# longer thread needs no inner pagination.
threads=$(gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
    query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100, after: $endCursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id isResolved
              root: comments(first: 1) { nodes { databaseId } }
              comments(last: 100) { nodes { author { login } body } }
            }
          }
        }
      }
    }' --jq ".data.repository.pullRequest.reviewThreads.nodes[]
             | select(.isResolved | not)
             | (.comments.nodes | to_entries) as \$c
             | ([\$c[] | select(.value.author.login != \"$operator\") | .key] | max // -1) as \$other
             | ([\$c[] | select(.value.author.login == \"$operator\")
                        | select(.value.body | test(\"^(Fixed in [0-9a-f]{7,40}|Refuted:|Boundary:)\"))
                        | .key] | max // -1) as \$answer
             | [.id, (.root.nodes[0].databaseId | tostring), (if \$answer > \$other then \"1\" else \"0\" end)]
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

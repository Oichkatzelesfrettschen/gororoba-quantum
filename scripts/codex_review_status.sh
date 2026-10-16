#!/bin/sh
# GraphQL variables ($owner, $repo, $pr, $endCursor) belong to the query text,
# so the single quotes are deliberate.
# shellcheck disable=SC2016
# Report, per pull request, the head commit, the state and commit of the latest
# Codex review, its head-bound clean signal, and every unresolved review thread:
# its root comment id, path, and every comment in it with its author, so a
# rejection posted after an answer is read with the finding.
# Usage: scripts/codex_review_status.sh PR [PR...]
set -eu

[ "$#" -gt 0 ] || { echo "usage: $0 PR [PR...]" >&2; exit 2; }

slug=$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')
owner=${slug%%/*}
repo=${slug#*/}

timestamp_at_or_after() {
    comparison_candidate=$1
    comparison_boundary=$2
    [ "$comparison_candidate" != - ] && [ "$comparison_boundary" != - ] &&
        awk -v candidate="$comparison_candidate" -v boundary="$comparison_boundary" \
            'BEGIN { exit !((candidate "") >= (boundary "")) }'
}

timestamp_after() {
    comparison_candidate=$1
    comparison_boundary=$2
    [ "$comparison_candidate" != - ] && [ "$comparison_boundary" != - ] &&
        awk -v candidate="$comparison_candidate" -v boundary="$comparison_boundary" \
            'BEGIN { exit !((candidate "") > (boundary "")) }'
}

fetch_summary_rows() {
    summary_pr=$1
    gh api --paginate "repos/$slug/issues/$summary_pr/comments" --jq '
        .[] | select(.user.login == "chatgpt-codex-connector[bot]")
            | select(.user.id == 199175422)
            | select(.user.node_id == "BOT_kgDOC98s_g")
            | select(.performed_via_github_app.id == 1144995)
            | select(.performed_via_github_app.node_id == "A_kwHOAOQ6Gs4AEXij")
            | select(.body | test("codex-pull-request-review-summary"))
            | [.updated_at,
               (if (.body | test("\\*\\*Running\\*\\*")) then "running"
                elif (.body | test("\\*\\*Completed\\*\\*")) then "done"
                else "unknown" end),
               (try (.body
                     | capture("\\| `(?<commit>[0-9a-f]{7,40})` \\|").commit)
                catch "-")]
            | @tsv'
}

for pr in "$@"; do
    pull_row=$(gh api "repos/$slug/pulls/$pr" --jq \
        '[.head.sha, .created_at, .updated_at] | @tsv')
    IFS='	' read -r head_full pull_created pull_updated <<EOF
$pull_row
EOF
    head=$(printf '%s\n' "$head_full" | cut -c 1-7)
    # GitHub identifies the OpenAI app as 1144995 and its bot account as
    # 199175422. Issue comments expose both identities; issue reactions expose
    # the bot identity but omit performed_via_github_app. A display name or a
    # login that merely contains codex cannot forge a state or verdict.
    # --paginate walks every page of issue comments, so the latest summary and
    # clean comment are found however many comments the PR carries. The bot
    # keeps one summary comment per PR and edits it for each review round.
    # Each request's output lands in a variable before the last match is taken,
    # so a failed request stops the script under set -e instead of being masked
    # by a pipeline that ends in tail.
    summary_rows=$(fetch_summary_rows "$pr")
    summary_row=$(printf '%s\n' "$summary_rows" | tail -n 1)
    summary_updated=-
    state=none
    summary_head=-
    if [ -n "$summary_row" ]; then
        IFS='	' read -r summary_updated state summary_head <<EOF
$summary_row
EOF
    fi

    clean_rows=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login == "chatgpt-codex-connector[bot]")
            | select(.user.id == 199175422)
            | select(.user.node_id == "BOT_kgDOC98s_g")
            | select(.performed_via_github_app.id == 1144995)
            | select(.performed_via_github_app.node_id == "A_kwHOAOQ6Gs4AEXij")
            | select(.body | test("codex-pull-request-review-summary") | not)
            | select(.body
                     | sub("^<!-- codex-review-receipt:v1 -->[[:space:]]*"; "")
                     | startswith("Codex Review: Didn'"'"'t find any major issues"))
            | [.created_at,
               (try (.body
                     | capture("\\*\\*Reviewed commit:\\*\\* `(?<commit>[0-9a-f]{7,40})`").commit)
                catch "-")]
            | @tsv')
    clean_row=$(printf '%s\n' "$clean_rows" | tail -n 1)
    clean_created=-
    clean_head=-
    if [ -n "$clean_row" ]; then
        IFS='	' read -r clean_created clean_head <<EOF
$clean_row
EOF
    fi

    trigger_times=$(gh api --paginate "repos/$slug/issues/$pr/comments" --jq '
        .[] | select(.user.login != "chatgpt-codex-connector[bot]")
            | select(.body
                     | test("(^|\\n)[[:space:]]*@codex (security )?review[[:space:]]*($|\\n)"))
            | .created_at')
    trigger_created=$(printf '%s\n' "$trigger_times" | tail -n 1)

    reaction_times=$(gh api --paginate "repos/$slug/issues/$pr/reactions" --jq '
        .[] | select(.user.login == "chatgpt-codex-connector[bot]")
            | select(.user.id == 199175422)
            | select(.user.node_id == "BOT_kgDOC98s_g")
            | select(.content == "+1")
            | .created_at')
    reaction_created=$(printf '%s\n' "$reaction_times" | tail -n 1)

    summary_matches_head=false
    clean_comment_matches_head=false
    clean_comment_is_fresh=false
    reaction_is_fresh=false
    pending_request=false
    round_started=$pull_created
    case "$head_full" in
        "$summary_head"*) summary_matches_head=true ;;
    esac
    case "$head_full" in
        "$clean_head"*) clean_comment_matches_head=true ;;
    esac
    if [ -n "$trigger_created" ]; then
        if timestamp_at_or_after "$trigger_created" "$summary_updated"; then
            pending_request=true
        else
            round_started=$trigger_created
        fi
    fi
    if timestamp_at_or_after "$clean_created" "$round_started"; then
        clean_comment_is_fresh=true
    fi
    if [ -n "$reaction_created" ] &&
        timestamp_after "$reaction_created" "$summary_updated"; then
        reaction_is_fresh=true
    fi

    verdict=missing-clean-signal
    if [ "$state" = running ] || [ "$pending_request" = true ]; then
        verdict=pending
    elif [ "$state" = "done" ] && [ "$summary_matches_head" = true ]; then
        if [ "$clean_comment_matches_head" = true ] &&
            [ "$clean_comment_is_fresh" = true ]; then
            verdict="clean-comment@$clean_created"
        elif [ "$reaction_is_fresh" = true ]; then
            verdict="clean-reaction@$reaction_created"
        fi
    elif [ "$state" = "done" ]; then
        verdict=stale-summary
    fi
    # The outer query finds every open thread. Each node query paginates that
    # thread's complete comment connection, so a long discussion retains its
    # root finding instead of truncating to the latest 100 comments.
    open_thread_rows=$(gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
        query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  id isResolved
                  root: comments(first: 1) { nodes { databaseId path line } }
                }
              }
            }
          }
        }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
                 | select(.isResolved | not)
                 | .root.nodes[0] as $root
                 | [.id, ($root.databaseId | tostring), $root.path,
                    (($root.line // "?") | tostring)]
                 | @tsv')
    open_threads=$(
        while IFS='	' read -r thread_id root_id path line; do
            [ -n "$thread_id" ] || continue
            printf '%s\n' "--- open $root_id $path:$line"
            gh api graphql --paginate -F id="$thread_id" -f query='
                query($id: ID!, $endCursor: String) {
                  node(id: $id) {
                    ... on PullRequestReviewThread {
                      comments(first: 100, after: $endCursor) {
                        pageInfo { hasNextPage endCursor }
                        nodes { author { login } body }
                      }
                    }
                  }
                }' --jq '.data.node.comments.nodes[]
                         | "[\(.author.login)] " + (.body
                           | gsub("<sub><sub>!\\[(?<b>P[0-9]) Badge\\]\\([^)]*\\)</sub></sub>"; "[\(.b)]")
                           | gsub("\n\nUseful\\? React with[^\n]*"; ""))'
            printf '\n'
        done <<EOF
$open_thread_rows
EOF
    )

    thread_times=$(gh api graphql --paginate -F owner="$owner" -F repo="$repo" -F pr="$pr" -f query='
        query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes { root: comments(first: 1) { nodes { createdAt } } }
              }
            }
          }
        }' --jq '.data.repository.pullRequest.reviewThreads.nodes[]
                 | .root.nodes[0].createdAt')
    latest_thread_created=$(printf '%s\n' "$thread_times" | tail -n 1)

    # The second PR and summary reads reject a push, timeline event, or review
    # state update that races the comments, reactions, and thread snapshot.
    final_pull_row=$(gh api "repos/$slug/pulls/$pr" --jq \
        '[.head.sha, .updated_at] | @tsv')
    IFS='	' read -r final_head_full final_pull_updated <<EOF
$final_pull_row
EOF
    final_summary_rows=$(fetch_summary_rows "$pr")
    final_summary_row=$(printf '%s\n' "$final_summary_rows" | tail -n 1)
    snapshot=stable
    if [ "$head_full" != "$final_head_full" ] ||
        [ "$pull_updated" != "$final_pull_updated" ] ||
        [ "$summary_row" != "$final_summary_row" ]; then
        snapshot=changed
        verdict=unstable-snapshot
    elif [ -n "$open_threads" ]; then
        verdict=open-threads
    elif [ -n "$latest_thread_created" ] &&
        timestamp_at_or_after "$latest_thread_created" "$summary_updated"; then
        verdict=later-finding
    fi

    echo "PR $pr head=$head review=$state summary-head=$summary_head round-start=$round_started snapshot=$snapshot verdict=$verdict"
    if [ -n "$open_threads" ]; then
        printf '%s\n' "$open_threads"
    fi
done

# Codex review loop, stacked PRs and merging

Codex, the chatgpt-codex-connector app, supplies the default pull-request
review. It reviews only on request: an issue comment `@codex review` asks for
a review of the current head, so the operator posts one right after opening a
PR and after every push that needs review. Codex is the only hosted reviewer.
Copilot reviews are billed to the owner, so no pull request requests one; when
the Codex app reports exhausted code-review quota, the owner decides how the
PR proceeds. A round that never completes follows
[codex-review-stalls.md](codex-review-stalls.md).

- *Progress.* The bot keeps one summary comment per PR, marked
  `codex-pull-request-review-summary`, which reads Running while a review is in
  progress.
- *Outcome.* A review with findings publishes inline review comments with P1 or
  P2 badges. A clean review either posts an issue comment whose text, after
  an optional `<!-- codex-review-receipt:v1 -->` marker, begins "Codex
  Review: Didn't find any major issues" with a reviewed commit matching the PR
  head, or adds an app-owned `+1` reaction after the completed summary update
  for the current head. A prior reaction cannot qualify a later review round.
- *Status tool.* `scripts/codex_review_status.sh PR...` prints each PR's head,
  summary head, review state, and head-bound clean signal, then every unresolved
  thread with its root comment id and full body. It accepts comments and
  reactions only from the stable app and bot identities, requires the clean
  comment to follow the current review request and the reaction to occur
  strictly after the completed summary update. It paginates every issue,
  reaction, thread, and thread-comment connection, then re-reads the head and
  PR update marker, and summary to reject a changing snapshot.

## One round, per PR

1. Wait until the Codex review completes: its summary stops reading
   Running. `scripts/codex_review_wait.sh PR DEADLINE LOG` waits on the
   review and the checks and repeats a request once when a round shows no
   result after 600 s, since up to one request in seven gets no result from the
   service ([codex-review-stalls.md](codex-review-stalls.md)).
   Then read every unresolved thread
   in full from `codex_review_status.sh` or the GraphQL thread connection.
   Threads can arrive between rounds and attach to the newest commit, so the
   open-thread list,
   not memory of the last round, is the work queue.
2. Triage each thread against reachability.
   - A defect a user reaches through a documented interface (the CLI, the
     record files the program writes, the default flow) gets a fix.
   - A claim the source refutes gets the refuting line in the reply.
   - Malformed or adversarial input outside the documented domain gets a reply
     naming the boundary and a follow-up issue.
3. Fix every reachable thread on the PR's own branch in one commit. A change to
   live_run.py or experiments.py also gets a live dry run, and a change to
   qiskit-ibm-runtime usage also gets `/migrate-qiskit-ibm-runtime`
   ([qiskit-skills.md](qiskit-skills.md)). Then push.
4. Reply to each thread's root comment with
   `gh api repos/OWNER/REPO/pulls/PR/comments/ID/replies -f body=...`. The reply
   begins with one of three markers, then says what changed or why:
   - `Fixed in <commit>`
   - `Refuted:` followed by the refuting source line
   - `Boundary:` followed by the documented limit and the follow-up issue
5. Run `scripts/resolve_answered_threads.sh PR`. It resolves only threads
   carrying a reply from the authenticated operator that begins with one of
   those markers, and lists every other open thread as unanswered. A comment
   such as "will fix" or a question resolves nothing. Never resolve a thread
   whose finding has not been read and answered.
6. Request Codex again and start at step 1. A PR leaves the loop when the
   current-head Codex status reports `verdict=clean-comment...` or
   `verdict=clean-reaction...` and every review thread is resolved.

## Stacked PRs

- Each branch builds on the one below it, so a fix lands on the lowest branch
  that holds the code and then merges upward, branch by branch, with
  `git merge --no-ff`.
- Rebasing is out because the permission harness denies force-push.
- When one file conflicts heavily, take the lower branch's reviewed version and
  re-apply the upper branch's own changes on top, and run a dry run on every
  branch the merge touched.

## Merging

A PR merges after this sequence:
1. Codex reviews; every thread is fixed, refuted or bounded and resolved
   (One round above), and the touched files pass the code-style tools
   ([ci/AGENTS.md](../../ci/AGENTS.md#code-style-tools)).
2. The operator reviews the whole PR diff against origin/main, every commit
   regardless of author, not only the commits written in this loop, and fixes
   what that review finds.
3. Codex reviews the head once more; that round's threads are answered and
   resolved the same way.
4. The `pr.yml` jobs `lint`, `types`, `tests` and `gates` pass on the head. A push
   that changes the head reruns them; a red job gets its fix commit on the
   branch.
5. GitHub reports mergeable_state clean.

Then, bottom-up, for each PR:
1. Merge it with a merge commit:
   `gh api -X PUT repos/OWNER/REPO/pulls/PR/merge -f merge_method=merge`.
2. Retarget the next PR to main: `gh api -X PATCH repos/OWNER/REPO/pulls/NEXT -f base=main`.
   Deleting a base branch closes every PR that targets it, so the retarget
   comes first.
3. Delete the merged remote branch:
   `gh api -X DELETE repos/OWNER/REPO/git/refs/heads/BRANCH`.
4. Pull main in the primary checkout, then `git worktree remove` and
   `git branch -d` the merged branch.

## API use

Everything goes through REST with `gh api`, except review threads, which only
GraphQL exposes: both scripts list them through the reviewThreads connection,
and resolution uses resolveReviewThread and unresolveReviewThread.

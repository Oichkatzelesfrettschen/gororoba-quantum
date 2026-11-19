# Review record: qd_teleportation_rehearsal: compare circuit_params by realized unitary

Commit references: every commit named in this record is a full 40-hex hash. Each branch commit is reachable from refs/pull/937/head and each squash or merge commit from the default branch (git merge-base --is-ancestor, 2026-11-19).

Pull request: gororoba-quantum #937, branch photonic-circuit-params-gauge-comparator, merged 2026-11-16T12:19:21Z (GitHub mergedAt), merge commit 97a2cc72fae23eb3f0605699d2bb37499f496cae.

This record was written after the merge from the pull request itself (title, body, commits, reviews, issue comments and inline review comments as GitHub returns them). This record is a post-merge backfill, so no brief exists. Its scope is the pull request's own threads and the private orchestration record of the session that ran the Advisor and worker rounds below, which this repository does not retain; a step with no source in either reads "not recorded". Reviewer verdicts below are the threads' own; no later judgment is added.

Reviewers that ran:
- Hosted Codex (requested by an "@Codex review" comment, 2026-11-16T09:28Z): review of 9fce104c5a1cb1a1086ef6bca2242f520aded837 completed; no findings, receipt "Didn't find any major issues".
- Further rounds recovered from the orchestration record (what ran, on which head, disposition): see "Rounds beyond the pull request" below.
- Local codex, grok and red-team rounds: not recorded.

Findings: hosted Codex raised none; the Advisor and worker findings are listed under "Rounds beyond the pull request" and in reconciliation.md.

## Rounds beyond the pull request
- Implementing worker report at e4275dc0ab4b51b265b40981545ece1647336840 (before the review): close_request compares circuit_params through the realized unitary at tolerance 1e-12 (rebuild against retained within 6e-16; one parameter moves an entry about 0.31 per radian), every other cases.json field exact; two arm64 expected-failure entries removed; tests passed on three CPU families (Zen 4 63 passed plus a full suite of 7034, Neoverse N1 63, Xeon 68); job-00 replay gate passes on Zen 4 and N1; six hosted checks pass.
- Advisor (2026-11-16, Advisor only under the owner's ruling of 08:06Z): comparator confirmed (NaN fails closed; the fixture moves match the 16 mismatches seen; a 1e-11 mutation clears the threshold by about 3x). Blocking items closed: no digest pin on any touched file; --submit sends the run's frozen cases.json and circuit.json, and close_request runs only on replay and tests. Pending item: a theta = pi gauge fixture.
- Follow-up worker, head 9fce104c5a1cb1a1086ef6bca2242f520aded837: the theta = pi gauge fixture (a common shift of alpha and beta accepted with residual 5e-16 on Zen 4 and 2.3e-16 on N1; alpha alone, opposite shifts and a common shift at cos(theta/2) != 0 refused); 64 tests and 5 audit tests pass on two compute hosts.
- Hosted Codex on 9fce104c5a1cb1a1086ef6bca2242f520aded837: no findings; merged on the owner's word "Merge" (merge commit as above).

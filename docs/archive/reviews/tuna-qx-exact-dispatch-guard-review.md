The proposed dispatch guard does not yet qualify as an exact implementable transaction. I found no FATAL defect because the guard and approval path remain unimplemented and therefore unreachable, but six SERIOUS design gaps and two SLOPPY ambiguities must close before approval review.

## SERIOUS findings

1. **The stated lock sequence deadlocks against the actual helper.**

The design acquires `SUBMIT_LOCK` and then invokes the deadline helper while retaining that lock ([design:40](../../../docs/design/tuna-qx-exact-dispatch-guard.md), [design:63](../../../docs/design/tuna-qx-exact-dispatch-guard.md)). The public helper unconditionally acquires the same lock again ([qi_platform_submission_deadline.py:58](../../../scripts/qi_platform_submission_deadline.py)). `token_lock` uses a new `open` followed by blocking `flock(LOCK_EX)` and has no reentrant ownership mechanism ([qi_platform.py:183](../../../scripts/qi_platform.py)).

Read-only reproduction using two descriptors for an unrelated existing file:

```text
flock -x fd1
flock -xn fd2
SECOND_OPEN_BLOCKED status=1
```

Calling public `submit()` under the already-held lock therefore blocks itself. The design must either:

- delegate lock ownership to public `submit()` and add an under-lock consumption-marker callback; or
- define and test a supported locked submission API that accepts explicit lock ownership.

Calling private `_submit()` directly would avoid the second lock but would create an undocumented coupling that the design presently does not name.

2. **Approval authenticity and account-scoped consumption have no enforceable construction.**

The design correctly states that a local JSON file or digest cannot authenticate approval ([design:23](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), but it does not specify:

- the authoritative approval channel or signature;
- the canonical approval identifier;
- how renewed approval differs from a copied approval;
- the account identifier and marker namespace;
- marker schema, permissions, ownership and durable location.

The connected submitter only tests `approval.strip()` and stores that string verbatim ([qi_platform_submission_deadline.py:101](../../../scripts/qi_platform_submission_deadline.py), [qi_platform_submission_deadline.py:166](../../../scripts/qi_platform_submission_deadline.py)). The generic CLI accepts any nonempty text ([qi_platform.py:1201](../../../scripts/qi_platform.py)).

Concrete false-acceptance shape: copy a locally valid approval record, replace its claimed unique identifier, and run it from another case directory. A validator limited to local hashes cannot distinguish that copy from renewed owner approval. Different home directories also produce different `submit.lock` paths for the same provider account.

The approval record needs an authenticated, replay-resistant authority plus one canonical consumption key derived from that authority—not a caller-selected identifier. The helper should retain only a sanitized approval identifier/digest, not potentially private approval prose.

3. **“Zero allowed credits” is incompatible with the admitted billing uncertainty.**

The packet specifies zero allowed credits ([design:17](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), while the design acknowledges that local checks cannot guarantee a future zero charge ([design:53](../../../docs/design/tuna-qx-exact-dispatch-guard.md)).

Historical zero-valued transactions and public policy text cannot establish that a newly created job will consume zero credits. If zero is a hard authorization ceiling, dispatch requires either:

- an authoritative provider quote/reservation guaranteeing zero charge for these exact requests; or
- an approval envelope that explicitly authorizes a bounded charge risk.

A test double can verify refusal logic, but it cannot prove live provider pricing. A late-charge test must also prove that a later nonzero transaction invalidates the case without being misrepresented as an authorized zero-credit execution.

4. **Path, filesystem and executable-source identity rules remain non-executable prose.**

The design requires rejection of symbolic links, hard links and changed bytes ([design:34](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), but supplies no path-resolution or file-descriptor algorithm.

The existing helper follows `case_dir / row["file"]`, reads the pathname and validates content hashes ([qi_platform_submission_deadline.py:103](../../../scripts/qi_platform_submission_deadline.py)). It does successfully hold validated source content in memory afterward, closing a later source-content pathname race. It does not establish:

- trusted-root containment;
- absence of symbolic components;
- regular-file type and ownership;
- hard-link count;
- stable inode/device across validation;
- trusted ownership of the marker and lock parents;
- that loaded Python code corresponds to the packet-bound producer bytes.

The implementation needs trusted-root resolution and descriptor-based validation such as `openat`/`O_NOFOLLOW` plus `fstat`, followed by exclusive publication of approved copies into a trusted run directory. Shared/NFS filesystems also require an explicit statement that their locking, link-exclusivity and directory-fsync semantics are sufficient. Otherwise the guarantee must be limited to a trusted local filesystem and non-hostile same-user processes.

5. **The persistent clock and deadline algorithm is unspecified, and lock waiting is unbounded.**

The design recognizes that a persisted monotonic value cannot survive restart without boot/process identity ([design:40](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), but does not define the identity or clock. Linux `CLOCK_MONOTONIC` may also exclude suspend time, allowing wall-clock freshness to expire while the monotonic interval remains short.

The actual lock acquisition blocks indefinitely and cannot be interrupted by the deadline. The helper checks the deadline only after the lock returns. The existing regression merely replaces the lock with a fake context manager that advances a fake clock ([test_qi_platform_submission_deadline.py:267](../../../tests/scripts/test_qi_platform_submission_deadline.py)); it does not exercise a held kernel lock.

Required design details include:

- boot identity, UTC initiation horizon and monotonic/boottime duration;
- nonblocking or timed lock acquisition;
- the deadline used after the callback, language pagination and durable state publication;
- refusal after suspend, restart or clock-domain disagreement.

6. **Account-wide and paginated observations do not form an atomic snapshot.**

`Client.pages()` performs ordinary page-number requests without snapshot or cursor identity ([qi_platform.py:405](../../../scripts/qi_platform.py)). Concurrent account activity can reorder transactions between pages, concealing or duplicating a row. Another host can enqueue immediately after the locked callback. The design acknowledges that the local lock cannot stop independent clients ([design:79](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), so “current account transaction information” and “current-user queue” are observations, not atomic preconditions.

The final contract must either use a provider-supported stable cursor/snapshot or explicitly bound these claims. Tests must mutate pagination and queue state between pages, between callback return and the first POST, and during collection.

## SLOPPY findings

1. **“Receipt recovery” overstates lost-response recovery.**

The helper checkpoints an identity only after receiving its response. A lost response from project, batch, algorithm, commit, file or job creation leaves that identity unknown. Read-only reconciliation can recover a fully checkpointed batch after a lost enqueue response, but it cannot discover all earlier accepted creations ([qi_platform.py:1047](../../../scripts/qi_platform.py)).

The design should say: earlier lost creation responses consume approval and remain blocked/ambiguous; only the fully checkpointed enqueue outcome is recoverable unless the provider supplies idempotency or exact read-only discovery.

2. **“Checked bytes” is literally stronger than current dispatch behavior.**

The helper validates source bytes, decodes them as UTF-8, and submits a JSON string ([qi_platform_submission_deadline.py:114](../../../scripts/qi_platform_submission_deadline.py), [qi_platform_submission_deadline.py:230](../../../scripts/qi_platform_submission_deadline.py)). For the present ASCII sources, the semantic text is stable. Byte-for-byte provider identity still requires canonical UTF-8 rules and source readback; the HTTP request does not transmit the original byte blob directly.

## Required regression set

At minimum, the implementation and dedicated gate must cover:

- real kernel-lock non-reentrancy, contention, expiry and process death;
- copied approval across run roots, processes, home directories and renewed approvals;
- each packet/source/producer mutation at validation, lock acquisition, callback and pre-POST boundaries;
- parent/leaf symlink, hard link, traversal, absolute path and insecure/shared parent;
- crash before/after marker fsync and before/after every remote request;
- accepted-but-lost response for every POST and enqueue PATCH, proving zero automatic retry;
- pagination insertion/deletion/reordering and concurrent independent-client activity;
- every backend, gate, compiler, raw-data, capacity, heartbeat, queue and transaction predicate independently;
- policy redirect, unexpected host, oversized/partial body, changed text and deadline expiry;
- suspend/restart/boot-identity and admission-age expiry;
- late nonzero transaction and incomplete publication.

## Binding and review limits

All six paths in `local hash binding list` match their expected SHA-256 in both the index and working tree, with `0/0` unstaged line differences. Both staged and unstaged `git diff --check` completed successfully; Git emitted only the existing fsmonitor IPC warning.

I performed static inspection and the read-only flock probe. I did not run pytest because these tests create temporary files, contrary to the requested read-only boundary. I accessed no provider, credentials or tokens and performed no submission, upload, message, seed draw or file write.

The case, dispatch guard and approval remain unimplemented and unapproved. Local receipts cannot authenticate the owner or provider, live availability and billing remain unknown, and the separate fresh admission, QX approval guard, and QX-to-Tuna policy gap remain open.

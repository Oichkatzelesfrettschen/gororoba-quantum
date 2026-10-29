The staged Python primitive is a local-filesystem concurrency/security mechanism; it claims to create one fail-closed marker for supplied account and approval digests. I read both complete staged blobs, the archived review, and both staged/current design text. I performed no test execution, network access, credential reads, provider operations, or writes.

## Findings

1. **SERIOUS boundary — durable failure quarantine remains unimplemented.**

   After exclusive creation, every write or `fsync` error propagates while leaving the directory entry in the live namespace ([qi_tuna_consumption_marker.py:49](../../../scripts/qi_tuna_consumption_marker.py)). The tests demonstrate only that an immediate retry sees `FileExistsError` ([test_qi_tuna_consumption_marker.py:47](../../../tests/scripts/test_qi_tuna_consumption_marker.py)).

   A failed file or directory `fsync`, followed by a crash that loses the entry, permits the same supplied approval to create a new marker after restart. The design correctly assigns cross-restart quarantine to the caller ([tuna-qx-exact-dispatch-guard.md:156](../../../docs/design/tuna-qx-exact-dispatch-guard.md)), but the indexed call graph contains only test callers. No staged dispatch adapter or durable attempt ledger implements that obligation.

2. **SERIOUS boundary — trusted namespace and authenticated identity remain caller assertions.**

   `consume()` accepts a descriptor and three caller-selected byte strings. It verifies descriptor type, digest length, and directory type, but it establishes neither directory provenance nor account/approval authenticity ([qi_tuna_consumption_marker.py:18](../../../scripts/qi_tuna_consumption_marker.py)).

   Reachable reuse paths include:

   - Supply another account or approval digest: the function derives another filename.
   - Supply the same digests in another directory or host: each namespace admits its own marker.
   - Unlink the marker from a writable or hostile same-user namespace: the name becomes reusable.
   - Replace the borrowed descriptor before `os.dup()` completes: the duplicate can identify another directory.

   The working-tree design’s unstaged candidate account-binding paragraph explicitly leaves derivation, secret custody, aliases, shared namespace, and cross-host behavior unimplemented ([tuna-qx-exact-dispatch-guard.md:49](../../../docs/design/tuna-qx-exact-dispatch-guard.md)). Local `O_EXCL` cannot coordinate an independent host or noncompliant client.

3. **SERIOUS evidence gap — the archived review does not bind the current staged blobs.**

   The archived review reports the former descriptor race and missing identity/mode tests ([tuna-consumption-marker-review.md:9](../../../docs/archive/reviews/tuna-consumption-marker-review.md)). Those defects have since been addressed, but its recorded hashes at lines 66–67 describe earlier blobs.

   The document therefore remains useful historical evidence, not a current-head review receipt. Any staged claim of independent review needs a follow-up record bound to the hashes below.

4. **SLOPPY test coverage — central repairs are covered, but several failure contracts remain textual.**

   The staged tests now cover descriptor substitution after duplication, a known marker-name vector, exact payload bytes, private group/other mode, regular-file type, and an existing symlink.

   They still lack:

   - partial and zero-progress write injection;
   - exact file-then-directory `fsync` ordering;
   - close-error behavior;
   - borrowed-descriptor substitution before duplication, documenting the caller boundary;
   - subprocess contention;
   - crash/restart durability;
   - distinct approval-digest key separation.

   The mode assertion checks privacy, not exact `0600`: a restrictive process umask may reduce owner permissions while the test still passes ([test_qi_tuna_consumption_marker.py:134](../../../tests/scripts/test_qi_tuna_consumption_marker.py)). The implementation requests `0600`, which prevents group/other access under normal creation semantics, but the complete guard still must define directory owner, mode, ACL, and filesystem requirements.

5. **SOUND — the former post-validation descriptor-reuse race is repaired.**

   `consume()` duplicates the borrowed descriptor first, validates the duplicate, passes only that duplicate to `openat` and directory `fsync`, and closes it in `finally` ([qi_tuna_consumption_marker.py:24](../../../scripts/qi_tuna_consumption_marker.py)). Replacing the original descriptor afterward does not redirect the marker.

   The deterministic substitution test exercises exactly that sequence ([test_qi_tuna_consumption_marker.py:86](../../../tests/scripts/test_qi_tuna_consumption_marker.py)). The remaining pre-duplication interval is expressly assigned to the caller, rather than silently claimed safe.

6. **SOUND — local key stability and fail-closed creation are correctly designed.**

   The name hashes a domain separator plus two fixed-width values, account and approval, while the payload records account, approval, and packet digests ([qi_tuna_consumption_marker.py:35](../../../scripts/qi_tuna_consumption_marker.py)). Changing only the packet therefore collides with the existing marker, as required.

   `O_CREAT|O_EXCL|O_NOFOLLOW` blocks every existing final-component entry. Complete writes precede file `fsync`, which precedes directory `fsync`. These guarantees remain conditional on a trusted local filesystem with the required semantics.

## Boundary summary

| Surface | Current status |
|---|---|
| Duplicate descriptor lifetime | Implemented after `os.dup`; caller owns stability before duplication |
| Local key stability | Implemented and pinned by a known vector |
| File privacy | Requests `0600`; test proves group/other bits absent |
| Trusted canonical namespace | Unimplemented |
| Authenticated account and approval | Unimplemented |
| Cross-host coordination | Unimplemented |
| Cross-restart failure quarantine | Unimplemented caller obligation |
| Provider billing, queue, retry, idempotency, and lost responses | Entirely outside this primitive |
| Actual dispatch integration | No indexed non-test caller |

## Exact staged SHA-256 hashes

Computed twice directly from the Git index blobs:

- `scripts/qi_tuna_consumption_marker.py`: `dbaf93d5db016d483a22066ec0224e81ea6de9aff066f54655b747fc71534a61`
- `tests/scripts/test_qi_tuna_consumption_marker.py`: `cb8a431c7f89f3d2c062e50f7f2a3a777ca3d027d16c244286d654630ce5c6cc`

The scoped final observations record both Python files as staged additions with zero unstaged diff. The design remains `AM`; its account-binding paragraph exists only in the working-tree version.

The core primitive is sound as a trusted-local tombstone. It is not an approval guard. The decisive remaining work is a production adapter that authenticates canonical identities, fixes one trusted namespace, persists quarantine across failed synchronization and restart, coordinates every authorized host, and handles provider ambiguity without retrying the approval.

The review tracker recorded 3 minutes 21 seconds elapsed.

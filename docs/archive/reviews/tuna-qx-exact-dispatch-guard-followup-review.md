The revision is materially more accurate as a requirements document, but it is not yet an executable authorization protocol. It corrects the wording of most prior findings while deliberately leaving authority, provider evidence, implementation, and tests open.

## Binding result

All six entries in `the review binding list` match their expected SHA-256 in both the index and working tree. Every bound path has `0/0` unstaged line changes. Staged and unstaged `git diff --check` passed; Git emitted only the existing fsmonitor IPC warning.

## Prior-finding adjudication

| Prior finding | Design status | Remaining status |
|---|---|---|
| Nested submission lock | Corrected as a requirement at [design:95](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Blocked until one supported lock protocol is chosen, implemented and tested |
| Copy-resistant approval and account consumption | Requirements strengthened at [design:37](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | SERIOUS authority and namespace blocker |
| Zero-credit authorization | Scientific contradiction correctly exposed at [design:17](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Dispatch remains prohibited without provider guarantee or new bounded-risk approval |
| Filesystem/path/code identity | Concrete implementation requirements added at [design:53](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Blocked until protocol, code and mutation tests exist |
| Bounded wait and persistent clocks | Requirements added at [design:66](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Blocked because the helper still uses blocking `flock` and `time.monotonic()` |
| Pagination and independent clients | Limitation accurately documented at [design:80](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Provider snapshot or explicit residual-risk approval remains absent |
| Lost-response recovery | Actual recovery boundary correctly documented at [design:118](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Required endpoint-by-endpoint fault tests remain absent |
| UTF-8 checked bytes | Claim corrected at [design:104](../../../docs/design/tuna-qx-exact-dispatch-guard.md) | Canonicalization, provider readback and mutation tests remain absent |

## Unresolved SERIOUS blockers

1. **The approval authority remains undefined.**

“Verifiable receipt” and “trusted operator” are alternatives, not a protocol. The trusted-operator branch does not explain what prevents the operator’s local record from being copied or fabricated. A locally written approval string remains merely a claim about approval.

Realistic counterexample: copy the packet and approval record into two run roots, change a caller-selected local identifier, and invoke each under different home directories. The unchanged client derives `SUBMIT_LOCK` from the home-relative credential path ([qi_platform.py:116](../../../scripts/qi_platform.py)); the two processes obtain unrelated locks. Without an authoritative account key and shared consumption namespace, each can consider the approval unused.

Required evidence:

- one canonical approval authority and receipt schema;
- a derivation of the consumption key that callers cannot choose;
- an account-binding mechanism that works across home directories and participating hosts;
- concurrent copy/replay tests across directories, processes and home paths;
- fail-closed behavior when the authority or shared namespace is unavailable.

2. **The zero-credit case remains unauthorized.**

The revision correctly states that historical transactions and policy text cannot guarantee a future zero charge. The retained terms say normal noncommercial simulation up to 26 qubits is free under conditions, but also permit charges for advanced use ([terms:59](../../../docs/notes/quantum_inspire/site/terms-and-conditions.md), [terms:81](../../../docs/notes/quantum_inspire/site/terms-and-conditions.md)). The retained OpenAPI exposes transaction and ordinary reservation endpoints, but no identified billing quote, credit reservation or idempotency header.

Therefore:

- the historical terms are relevant evidence, not an exact-request price guarantee;
- a zero-credit hard ceiling still forbids dispatch;
- a bounded-charge alternative requires a separately written case and a new explicit user approval.

There is also one misleading sentence: “The existing zero-credit approval” at [design:23](../../../docs/design/tuna-qx-exact-dispatch-guard.md) conflicts with the declaration that no current approval exists at line 49. It should say “a future approval limited to zero credits” or “the proposed zero-credit envelope.”

3. **The supported lock path has not been selected.**

The revision correctly rejects calling public `submit()` while already holding its lock. Actual public submission still takes a blocking lock unconditionally ([qi_platform_submission_deadline.py:58](../../../scripts/qi_platform_submission_deadline.py)).

The document offers two unresolved paths:

- a digest-bound wrapper around private `_submit()`; or
- a new supported lock-aware API.

An exact design must select one. Until then, implementers can choose incompatible lock ownership and marker ordering. The safer supported API must establish who owns acquisition, marker creation, callback execution and release.

4. **Clock and retry requirements exceed actual helper behavior.**

The helper uses a finite `time.monotonic()` deadline ([qi_platform_submission_deadline.py:27](../../../scripts/qi_platform_submission_deadline.py)). The underlying lock uses an indefinitely blocking `flock` ([qi_platform.py:183](../../../scripts/qi_platform.py)).

The ordinary authenticated retry is already checked against the monotonic deadline. The missing guarantee is suspend-aware time: a long system suspend can leave `CLOCK_MONOTONIC` short while UTC freshness has expired. Authentication refresh can then finish after the wall-clock horizon, and the monotonic check may still admit the retry.

Required tests must inject:

- held kernel lock through and beyond the horizon;
- changed Linux boot identity;
- backward wall-clock movement;
- `CLOCK_BOOTTIME` advancing while monotonic time does not;
- suspend during initial authentication and during 401 refresh;
- expiry between callback, language pagination, state fsync and first POST.

The existing lock-wait regression only monkeypatches the lock and advances a fake clock ([test_qi_platform_submission_deadline.py:267](../../../tests/scripts/test_qi_platform_submission_deadline.py)); it does not test kernel-lock contention.

5. **Filesystem and executable-code trust remain requirements without a mechanism.**

The new descriptor-relative, no-follow, inode/device and link-count requirements are appropriate. They are not implemented by the current helper, which reads ordinary paths and follows their components ([qi_platform_submission_deadline.py:103](../../../scripts/qi_platform_submission_deadline.py)).

“Bind the loaded code” also needs an exact mechanism. Hashing `__file__` is insufficient if Python imported one module object and the on-disk file was later replaced with approved bytes. A clean isolated process launched only after validation, or equivalent loaded-code attestation, must be specified.

Required mutations include parent and leaf symlinks, hard links, absolute/traversal paths, inode replacement between checks, insecure parent ownership, stale imported modules, modified bytecode and unsupported shared-filesystem semantics.

6. **Non-atomic provider observations cannot enforce exact zero or exclusivity.**

The revision correctly admits this limitation. `Client.pages()` uses page numbers and the page count returned by each request without a snapshot token ([qi_platform.py:405](../../../scripts/qi_platform.py)). The retained transaction API has page, size and sort parameters but no captured snapshot/cursor mechanism.

Realistic counterexamples:

- a transaction is created immediately after the final page;
- another host fills or alters the queue after the callback;
- independent account activity creates a delayed charge while the local lock remains held.

A user can approve a clearly described residual observation risk, but that approval cannot simultaneously be represented as proof of a hard zero-credit guarantee. Provider-side atomic evidence remains absent.

## Lost responses and UTF-8

The lost-response wording now matches the helper. An accepted `/projects` response lost in transit leaves no project ID; reconciliation reports an unknown outcome. An accepted `/files` response lost in transit leaves earlier identities but no file ID. Only an already checkpointed batch with an ambiguous enqueue can be recovered read-only.

The current tests cover expiry after returned resource identities and one lost enqueue response ([test_qi_platform_submission_deadline.py:132](../../../tests/scripts/test_qi_platform_submission_deadline.py), [test_qi_platform_submission_deadline.py:185](../../../tests/scripts/test_qi_platform_submission_deadline.py)). They do not simulate server acceptance followed by a lost response for every POST. The generic phrase “receipt recovery” at [design:142](../../../docs/design/tuna-qx-exact-dispatch-guard.md) should be narrowed to enqueue recovery or durable blocked ambiguity.

The UTF-8 description is now accurate: the helper hashes bytes, decodes text, and places the string in JSON ([qi_platform_submission_deadline.py:114](../../../scripts/qi_platform_submission_deadline.py), [qi_platform_submission_deadline.py:230](../../../scripts/qi_platform_submission_deadline.py)). Collection currently retrieves jobs, results, logs and transactions, but does not read stored file content back ([qi_platform_submission_deadline.py:291](../../../scripts/qi_platform_submission_deadline.py)). Required tests must cover CRLF, BOM, non-ASCII normalization and provider-side textual normalization, then compare canonical or exact stored bytes according to the approved contract.

## Gate and evidence limits

The dedicated QX gates presently cover local replay and manifest verification only ([ci/gates.json:5135](../../../ci/gates.json)). No exact-dispatch implementation or fault-test gate exists.

I ran read-only hash, diff, source, test and retained-API inspections. I ran no tests because the existing pytest fixtures write temporary files. I accessed no provider, credential or token and performed no submission, upload, message, draw or filesystem write.

The revision closes the earlier claim-versus-reality defects as documentation requirements. It does not close the authorization, zero-credit, multi-home consumption, lock, timing, filesystem, provider-atomicity, source-readback or fault-test blockers. The QX case, guard and approval remain unimplemented and unapproved.

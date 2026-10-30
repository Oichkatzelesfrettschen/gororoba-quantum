The staged transport is a useful synthetic attempt-event presenter, but it is not admissible collection infrastructure. I found no intrinsic FATAL defect under its explicit non-admission contract. Treating any returned or replayed data as scientific evidence would be FATAL.

## Final staged identities

The design changed concurrently during review. The final verdict uses the later staged bytes.

| Staged input | SHA-256 |
|---|---|
| `scripts/qi_tuna_attempt_transport.py` | `7c949bed13e19673b1cb5607a20a87bc5b69feeae4efa3092397a2564438e211` |
| `tests/scripts/test_qi_tuna_attempt_transport.py` | `800fe04ee94572adb7c1948e97eb173954ddc66b8832f2740dad2e78f80c8d1e` |
| `docs/design/tuna-destination-sequential-evidence-case.md` | `20a6c7c0decd3fe740e8906f5bc27077c2e4c90c6c4f4ced14c42fa44e1ae825` |
| `docs/archive/reviews/tuna-readback-expiry-review.md` | `f451300348edd2d2321edc930bc9caebe66c44b205847eaced6e5185447c7093` |

The design began the review at `4df9975e6ae4b1738bfc3ad43f55ac3e21b585868fc836c93fd04ab1298d1263`. The only observed delta added the private-journal paragraph now at [tuna-destination-sequential-evidence-case.md:277](../../../docs/design/tuna-destination-sequential-evidence-case.md). The added paragraph explicitly preserves the missing-dispatcher and missing-quarantine verdict.

## Findings

1. **FATAL if used for scientific admission; SOUND only as a non-admission helper. High confidence.**

   The successful path returns the ordinary legacy `Readback` type at [qi_tuna_attempt_transport.py:128](../../../scripts/qi_tuna_attempt_transport.py). The value contains requested path/query, status, media type, body, and digest, but carries no authenticated account, effective URL, trusted timing decision, quarantine decision, or admission state.

   Existing decoder and storage interfaces already accept that type. A future caller could discard the attempt outcomes and pass the returned value into score-producing code. The archival review identifies the same score-shape hazard at [tuna-readback-expiry-review.md:28](../../../docs/archive/reviews/tuna-readback-expiry-review.md).

   The module docstring explicitly withholds admission at lines 3–7, so the current helper contract remains honest. The API type does not enforce that boundary.

2. **SERIOUS: the actual dispatcher and collector integration are missing. High confidence.**

   The staged index contains no production caller of `read_journaled_qi_json`; only synthetic journal tests invoke it. The existing collector continues to call the older transport at [qi_tuna_readback_collection.py:51](../../../scripts/qi_tuna_readback_collection.py).

   The final staged design states that the collector does not use the transport and that the journal/transport pair connects only in synthetic tests at [tuna-destination-sequential-evidence-case.md:267](../../../docs/design/tuna-destination-sequential-evidence-case.md). The older executor remains frozen to another case at line 479.

   A staged private persistence primitive now exists, but **no actual dispatcher or collector integration exists**.

3. **SERIOUS: durable cross-restart quarantine integration is missing. High confidence.**

   The transport merely invokes caller callbacks at [qi_tuna_attempt_transport.py:63](../../../scripts/qi_tuna_attempt_transport.py) and lines 112–123. Callback return proves neither filesystem durability nor crash survival.

   The final design requires persistence failure to prohibit further requests and create a separately durable quarantine surviving restart at [tuna-destination-sequential-evidence-case.md:255](../../../docs/design/tuna-destination-sequential-evidence-case.md). The newly staged journal remains synthetic-only and explicitly leaves cross-restart quarantine and authenticated context external at lines 277–287.

4. **SERIOUS: the records omit required identity, timing, and effective-request bindings. High confidence.**

   `AttemptIntent` contains only attempt ordinal, path, and query; `AttemptOutcome` contains envelope fields, bounded bytes, completion, and exception class names at [qi_tuna_attempt_transport.py:19](../../../scripts/qi_tuna_attempt_transport.py).

   The design requires slot and request ordinals, account namespace, method, authority, case/clock digests, prepared/effective request, response URL, trusted clock observations, body length/digest, and explicit failure classification at [tuna-destination-sequential-evidence-case.md:245](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   `allow_redirects=False` is merely passed to an `Any` session. The transport never verifies that the session honored the option, inspects `response.url`, or checks the authenticated subject after refresh.

5. **SERIOUS: timeout and request-start coverage remain partial. High confidence.**

   The code validates a finite positive scalar and passes it to `session.request`, but the scalar does not bound refresh, clock callbacks, response close, retention callbacks, or a custom session that ignores it. A clock check cannot interrupt a blocked operation.

   The final transport-owned clock check occurs at line 95. Close and outcome retention can cross the observation boundary afterward and still lead to a successful `Readback` return.

   The code sets `request_called=True` immediately before invoking the session at lines 74–78. The flag means only that Python reached the call site:

   - a local failure can occur before any network send;
   - a request exception can occur after the provider received the request;
   - preemption can move the actual invocation past the deadline.

   The design explicitly leaves that request-start gap unresolved at [tuna-destination-sequential-evidence-case.md:355](../../../docs/design/tuna-destination-sequential-evidence-case.md).

6. **SERIOUS: simultaneous transport and persistence failures can lose the primary diagnostic and have no quarantine outcome. High confidence.**

   Stream and close failures are correctly separated: the stream exception remains `error_type`, the close exception becomes `close_error_type`, and the stream exception is re-raised.

   If `retain_outcome` then raises, its exception supersedes the explicit primary re-raise. Python exception context may retain the earlier failure in-process, but no durable record or quarantine is guaranteed. The tests cover stream-plus-close and a standalone retention failure, but omit stream-plus-close-plus-retention failure and other transport-plus-retention combinations.

7. **SERIOUS: the tests leave important hostile-response and ordering branches open. High confidence.**

   The staged tests do not establish:

   - exact method, URL, query, timeout, streaming, and redirect arguments;
   - refresh and clock ordering around the 401 retry;
   - refresh failures before either intent;
   - non-integer status, raising status/header access, invalid media type, non-byte chunks, empty bodies, unexpected non-200 status, or a second 401;
   - complete `AttemptIntent` and `AttemptOutcome` field integrity;
   - timeout validation boundaries;
   - outcome-retention failure combined with request, stream, timeout, oversize, validation, or close failure;
   - restart refusal and score refusal after persistence failure;
   - direct rejection of unadjudicated `Readback` values by scientific scoring.

   The combined stream/close fixture at [test_qi_tuna_attempt_transport.py:309](../../../tests/scripts/test_qi_tuna_attempt_transport.py) checks only exception labels, not prefix, completion, status, content type, or `request_called`.

8. **SLOPPY: failure classification collapses to exception class names. High confidence.**

   Deadline expiry, invalid chunks, oversized bodies, invalid status, empty bodies, and bad media types can collapse to `TimeoutError` or `ValueError`. Those names are diagnostic details, not the closed failure taxonomy required for immutable adjudication. The terminal authorization error at line 132 also appears unreachable because a second 401 becomes and re-raises a `ValueError`.

## Exception and ordering assessment

The implemented order is:

`clock -> refresh -> clock -> intent callback -> clock -> request -> envelope -> clock -> chunks/checks -> complete -> clock -> validation -> close -> outcome callback -> raise/retry/return`

| Path | Static result |
|---|---|
| Invalid target, timeout, or callback shape | Fails before intent and request |
| Clock/refresh failure before intent | Produces no attempt outcome |
| Intent callback failure | Prevents the request; partial persistence remains externally ambiguous |
| Clock failure after intent | Retains `request_called=False` outcome |
| Request exception | Retains `request_called=True`, empty body, incomplete outcome |
| Partial stream failure | Retains exact bounded prefix with `complete=False` |
| Oversized chunk | Retains exactly `MAX_BODY` bytes with `complete=False` |
| Expiry after a chunk | Retains observed prefix with `TimeoutError` |
| Expiry after full stream | Retains full body with `complete=True` and `TimeoutError`; recovery-only |
| Expiry during close/retention | Undetected by the transport’s clock checks |
| Stream plus close failure | Retains both exception types; stream remains primary |
| Outcome callback failure | Prevents retry/return but can supersede the earlier exception |
| First 401 | Closes and presents the outcome before forced-refresh retry |
| Second 401 or other non-200 | Retains outcome and raises; no further retry |
| Nonempty `application/json` containing malformed JSON | Returned as untrusted bytes; strict parsing remains downstream |

The prefix truncation, close-before-outcome order, retry-after-outcome order, and `request_called` ambiguity are correctly represented under the narrow synthetic contract.

## Verdict

The transport materially improves failed-attempt visibility: partial, oversized, late-at-check, request-failure, close-failure, and first-401 paths reach an outcome callback before retry or propagation. The code still lacks the mechanisms that convert callback presentation into admissible evidence: an actual dispatcher, authenticated effective-request binding, enforceable operation bounds, trusted timing adjudication, restart-surviving quarantine, and a type boundary preventing ordinary `Readback` values from entering scoring.

The review was static. I ran no tests, imports, linters, network operations, credential reads, provider operations, jobs, uploads, draws, or messages. One `git write-tree` probe was mistakenly attempted; the read-only filesystem rejected it before creating an index lock or Git object. Final observations recorded the same `HEAD` (`55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`), an absent index lock, unchanged script/test/archive-review hashes, and the concurrently updated design hash reported above. The four named working-tree files matched their final staged bytes.

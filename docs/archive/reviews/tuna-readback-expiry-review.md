The staged change is a sound, narrow retention-order repair, but it does not make the collection path admissible for the proposed sequential inference. The review found no intrinsic FATAL defect under the module’s explicit “collection only, no admission” contract, five SERIOUS boundaries, and one SLOPPY test-coverage finding.

The reviewed artifacts cover Python network collection, expiry ordering, durable retention, provenance, and statistical-evidence admission.

## Exact identities

The staged hashes came directly from the index.

| Artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_readback_collection.py` | `45a5b6e074f8fd314537b51ff7334dfcbc6432f9ca12ab58c83b09832b15f3af` |
| `tests/scripts/test_qi_tuna_readback_collection_boundaries.py` | `05b2e481ee8bbc8b7de2780925d123674cf681d0118d598814b00a6d4d73e7f8` |
| Working-tree acquisition design | `1f907a5d68e3ffb352a1de5cad7a44a41524765d14ff3cdb791ac7f613e7e6fc` |
| Earlier review | `8307a7908c12d3b2a88dd70fefccc0382fddad56990159c2c4c57c787f48e622` |

The target working-tree files matched their staged blobs. `HEAD` remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

The acquisition design changed repeatedly during the review. The verdict applies to the final observed `1f907a…` working-tree bytes; its staged version remains `bea0efbe93d7ce86346a638c1e68358f2e0c956cb5128527d8eaa5023fbeb081`.

## FATAL

No FATAL defect exists inside the collector’s stated non-admission contract.

Treating a capture or reloaded capture as admitted sequential evidence would be fatally invalid. The module and design disclaim that use, so the defect belongs to the still-missing integration/adjudication layer rather than the narrow collector.

## SERIOUS findings

1. **Retained late data can still become score-shaped and indistinguishable from admitted data. High confidence.**

   The collector retains a receipt and only then checks expiry at [qi_tuna_readback_collection.py:51](../../../scripts/qi_tuna_readback_collection.py). If the final receipt completes the private store, the clock check raises without returning a capture, but [load_private_readbacks](../../../scripts/qi_tuna_private_readbacks.py) can reconstruct the complete capture without timing or quarantine state.

   The surrounding fixture explicitly constructs that condition at [test_qi_tuna_private_recovery_boundaries.py:90](../../../tests/scripts/test_qi_tuna_private_recovery_boundaries.py). The existing integration path then demonstrates `reload -> decode -> score` at [test_qi_tuna_readback_collection.py:193](../../../tests/scripts/test_qi_tuna_readback_collection.py).

   Neither `ReadbackCapture` nor `decode_captured_complete` carries the observation boundary, clock decision, quarantine decision, or immutable neutral score. The acquisition design requires exactly those distinctions at [tuna-destination-sequential-evidence-case.md:314](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   Remedy: require an immutable adjudication record before decoding for inference. The record must bind the capture, deadline observations, terminal attempt status, quarantine state, charge evidence, and the single immutable complete-or-neutral score decision.

2. **The staged repair preserves only receipts that the transport successfully returns; full and partial late bodies still disappear. High confidence.**

   The transport checks the clock while streaming and after the body loop at [qi_tuna_readback_transport.py:93](../../../scripts/qi_tuna_readback_transport.py). An expiry detected there raises before a `Readback` reaches the collector, so the collector cannot retain either the prefix or a complete late body.

   The new expiry fixture triggers expiry in `Response.close()` at [test_qi_tuna_readback_collection_boundaries.py:101](../../../tests/scripts/test_qi_tuna_readback_collection_boundaries.py), after the transport’s final clock check. The fixture therefore proves the newly repaired close-to-retention boundary, not expiry during streaming or immediately after full-body completion.

   The earlier review’s failed/partial-attempt finding therefore remains substantially open at [tuna-receipt-aware-collection-review.md:21](../../../docs/archive/reviews/tuna-receipt-aware-collection-review.md). The current design requires retained prefixes and recovery-only complete late bodies at [tuna-destination-sequential-evidence-case.md:234](../../../docs/design/tuna-destination-sequential-evidence-case.md).

3. **Clock checks do not establish atomic request-start or capture-return boundaries. High confidence.**

   The transport performs a clock check and then calls `session.request` at [qi_tuna_readback_transport.py:74](../../../scripts/qi_tuna_readback_transport.py). Preemption can move the actual request start past the deadline. The design acknowledges that gap at [tuna-destination-sequential-evidence-case.md:140](../../../docs/design/tuna-destination-sequential-evidence-case.md), while the case contract requires requests to start before the boundary at [line 300](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   A smaller sampling window also exists between the collector’s final post-retention check and its return at [qi_tuna_readback_collection.py:53](../../../scripts/qi_tuna_readback_collection.py). `ReadbackCapture` retains no clock sample that an adjudicator could evaluate.

4. **Retry and failure chronology remains unretained. High confidence.**

   The first HTTP 401 causes an automatic retry at [qi_tuna_readback_transport.py:73](../../../scripts/qi_tuna_readback_transport.py), but the rejected attempt produces no retained intent or terminal observation. Non-200 responses, invalid media types, oversized or empty bodies, clock exceptions, request exceptions, and close failures likewise produce no attempt receipt.

   The acquisition design requires a durable intent before each request and a terminal observation before any retry at [tuna-destination-sequential-evidence-case.md:224](../../../docs/design/tuna-destination-sequential-evidence-case.md). The collector cannot implement neutral failure semantics or prove one score per assignment from the current success-only receipts.

5. **Authentication, effective-request provenance, charge evidence, and score binding remain external. High confidence.**

   `Readback` records the caller-supplied path and query rather than the prepared/effective URL, authenticated subject, account namespace, response URL, or observation times. A custom session can therefore return internally consistent bytes from another route while the receipt repeats the requested locator.

   The association decoder then reduces the validated capture to counts, and the scorer accepts those counts without provider receipts, producer hashes, deadline evidence, or zero-charge evidence. The earlier review’s first, second, and fourth SERIOUS findings remain open. The design accurately states the missing adjudication requirements at [tuna-destination-sequential-evidence-case.md:176](../../../docs/design/tuna-destination-sequential-evidence-case.md).

## Lesser finding

**SLOPPY — the new tests cover positions thoroughly but cover only one expiry phase.**

The staged tests provide useful exhaustive matrices:

- all four receipt positions across path, query, status, media type, body, and digest mutations;
- retention callback failure at all four positions;
- expiry after the transport returns a receipt at all four positions.

The tests omit checkpoint-retention expiry, expiry during refresh, the check-to-request window, request-return expiry, each streaming phase, full-body expiry before `Readback` construction, expiry during retention, the final check-to-return window, 401 attempt retention, failure journaling, and rejection of a late reloaded capture by an admission layer. The test title “expiry after response” therefore describes a broader boundary than the fixture actually exercises.

## Sound mechanisms

- The collector now calls the retention callback before its post-response clock check and before any subsequent request.
- A retention exception at every response position stops the next request.
- The receipt mutation matrix closes the earlier review’s later-position coverage gap.
- Exact path, query, status, JSON media type, body type, and SHA-256 checks remain strict.
- The module and working design explicitly withhold authenticity, durability, timing admission, charge admission, and physical-schedule claims.

## Verdict and trust limitations

The staged change correctly repairs one ordering boundary: a successfully returned receipt reaches retention before expiry stops the collector. The change does not implement the attempt journal, immutable deadline adjudication, neutral failure decision, authenticated request record, charge check, or provenance-bound score required by the working acquisition design.

The review was static and read-only. It ran no tests, imports, linters, network requests, credential reads, provider operations, jobs, uploads, draws, messages, or repository writes. Fake sessions cannot establish live HTTP, OAuth, provider timing, filesystem-crash, pricing, or physical acquisition behavior. SHA-256 values identify reviewed bytes; they do not authenticate their provenance or prove correctness.

The native review goal completed in 4 minutes 7 seconds with 72,524 tracked tokens.

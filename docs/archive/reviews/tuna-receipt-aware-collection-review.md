No FATAL defect appears in the staged local mechanisms. The new collection layer closes the archived review’s locator/query/body-binding finding, but the resulting score remains inadmissible as campaign evidence because authentication, durable provenance, expiry adjudication, pricing, and provider timing semantics remain external.

## Findings

1. **SERIOUS — receipt locators record requested intent, not authenticated observation.**

   [qi_tuna_readback_transport.py:54](../../../scripts/qi_tuna_readback_transport.py) accepts an arbitrary `session`, while lines 77–102 construct the receipt from the caller’s original path and query. The receipt does not bind the prepared/effective URL, authenticated account namespace, response URL, or session identity.

   A custom or misconfigured session can return internally valid bodies from another route while the receipt still claims the expected locator. The collection checks that assertion at [qi_tuna_readback_collection.py:76](../../../scripts/qi_tuna_readback_collection.py), but cannot authenticate it.

   Remedy: require a reviewed authenticated-session adapter and retain a canonical request receipt binding effective method, authority, path, query, account context, response envelope, and body digest.

2. **SERIOUS — source-to-score provenance disappears after validation.**

   The collection passes all five exact bodies into the association decoder at [qi_tuna_readback_collection.py:104](../../../scripts/qi_tuna_readback_collection.py), but the decoder returns only `slot`, `arm`, `kind`, and two counts at [qi_tuna_source_association.py:355](../../../scripts/qi_tuna_source_association.py). The test passes that bare row directly into the statistical scorer at [test_qi_tuna_readback_collection.py:187](../../../tests/scripts/test_qi_tuna_readback_collection.py).

   A hand-written row substituted after validation is indistinguishable to the scorer. The score retains no checkpoint, job/result identity, source/catalogue/manifest digest, ordered receipt digest, or producer hash.

   Remedy: emit an immutable adjudication record binding the score decision to all evidence and producer digests. Keep the provenance-agnostic statistical core behind that adjudicator.

3. **SERIOUS — failures, refresh attempts, and partial responses are not retained.**

   At [qi_tuna_readback_transport.py:80](../../../scripts/qi_tuna_readback_transport.py), the first `401`, non-200 responses, invalid media types, oversized/partial bodies, empty bodies, and clock expiry all exit without a `Readback`. A successful retry erases the first attempt’s envelope and ordering. Clock expiry after the full body has been read at line 98 also discards those bytes.

   A failed retention callback similarly leaves no returned capture even though the provider read occurred; the test demonstrates that state at [test_qi_tuna_readback_collection.py:86](../../../tests/scripts/test_qi_tuna_readback_collection.py).

   Remedy: produce an immutable attempt receipt before every retry or failure, including attempt number, locator, envelope, retained prefix or complete-body digest, completion status, and clock decision.

4. **SERIOUS integration boundary — late or charged results can still become score-shaped rows.**

   `ReadbackCapture` retains no boot identity, observation boundary, availability time, charge evidence, or immutable expiry decision. The association predicate accepts any locally consistent completed result, including one received after the 3600-second slot boundary or accompanied by a charge. The integration test uses a no-op clock and immediately scores the response.

   Queue state, heartbeat, terms, pricing, pause enforcement, zero-charge confirmation, neutral failure scoring, late recovery, atomic provider snapshots, live language identity, served schedule, calibration, and acquisition-order semantics remain unimplemented. Returned list order is established; physical acquisition order and per-shot timestamps are not.

   This is consistent with the files’ disclaimers, but treating their output as inferentially admitted would be a false admission.

5. **SLOPPY — the response envelope and mutation coverage remain narrow.**

   `Readback` retains only status and content type beyond the decoded body. It omits attempt number, observation times, effective response URL, and content/transfer-encoding metadata. Consequently, the digest identifies the HTTP library’s decoded bytes but cannot reconstruct the envelope that produced them.

   The collection mutations at [test_qi_tuna_readback_collection.py:192](../../../tests/scripts/test_qi_tuna_readback_collection.py) primarily alter receipt zero; the fake session also ignores the supplied query parameters. Later-position callback failures, clock failures around every callback, exact request parameters, and partial response handling remain uncovered.

## Sound mechanisms

- The archived review’s principal local defect is closed: [qi_tuna_readback_collection.py:76](../../../scripts/qi_tuna_readback_collection.py) enforces exact receipt order, paths, queries, status, JSON media type, and body SHA-256 before decoding.
- The checkpoint and every successful response reach the retention callback before the next read begins. Callback return still does not prove durable storage.
- The transport has a closed GET/path/query surface, disables redirects, limits decoded bodies to 2 MiB, preserves successful body bytes in order, and hashes those exact decoded bytes.
- The association parser strictly handles UTF-8 JSON, rejects duplicate keys and non-finite values, and strongly binds catalogue, manifest, source, checkpoint identities, provider content, measurement mapping, ordered returned shots, and histogram.
- No intrinsic false admission appears inside the association predicate when all documented caller obligations are honored.

## Exact staged SHA-256

| Artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_readback_collection.py` | `42b825488bc60aee3745f9597b1b85b04c271e8e286efb21d32e40b67dc089df` |
| `tests/scripts/test_qi_tuna_readback_collection.py` | `16411ec2ca498b13608303e3192c96bd4329e5851a5ee9d6b40dbc3aedfe0c91` |
| `scripts/qi_tuna_readback_transport.py` | `246672e6346a555ec67bb54f23e6be47157b357f36c451a6d8649766d2c65a00` |
| `scripts/qi_tuna_source_association.py` | `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be` |
| Review basis | `b2b7cbc4437ab6832feb678a64bea6b896209b041bf20f786327af9c8cd8ec78` |
| Design basis | `bea0efbe93d7ce86346a638c1e68358f2e0c956cb5128527d8eaa5023fbeb081` |

Verdict: the staged code now forms a defensible strict local readback-and-decoding predicate. The most important missing mechanism is an authenticated, durable adjudication record that retains every attempt and binds exact provider receipts through the final score decision. Until that layer also enforces observation deadlines, neutral failure semantics, zero-charge evidence, and live provider admission, the pipeline cannot support the proposed sequential inference.

The review was static and read-only. I ran no tests, network requests, credential reads, provider operations, jobs, uploads, draws, messages, or repository edits. Final observations retained HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346` and the staged hashes shown above.

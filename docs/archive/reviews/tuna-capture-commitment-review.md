Reviewed artifacts are Python cryptographic-binding, parser, filesystem-provenance, and acquisition-evidence code. The staged commitment primitive is sound within its declared boundary. The staged integration does not establish an admissible acquisition path.

No FATAL implementation defect found.

## Findings

1. **SERIOUS — the integration performs a self-comparison, then proceeds directly to scoring.**

   [test_qi_tuna_readback_collection.py:199](../../../tests/scripts/test_qi_tuna_readback_collection.py) derives the expected commitment from the resident capture:

   ```python
   verify_capture_commitment(reloaded, capture_commitment(capture))
   ```

   Lines 202–205 then decode and score the reloaded capture. The comparison establishes same-process round-trip equality. It does not authenticate restart provenance, successful durable persistence, observation time, account/request identity, charge state, or scientific admission. A caller can compute `capture_commitment(reloaded)` and obtain a match for any internally valid coherent replacement.

   The module itself states the boundary correctly at [qi_tuna_capture_commitment.py:1](../../../scripts/qi_tuna_capture_commitment.py), and the design repeats it at [tuna-destination-sequential-evidence-case.md:180](../../../docs/design/tuna-destination-sequential-evidence-case.md).

   Remedy: place an adjudication API between reload and scoring. Its immutable record must bind an independently authenticated expected commitment, attempt journal, deadline decision, durability/quarantine result, account and effective-request identity, charge evidence, producer hashes, and the single complete-or-neutral score decision.

2. **SERIOUS, inherited boundary — the commitment cannot close the receipt-aware or private-store findings.**

   The commitment covers the caller-declared path/query, status, content type, body length, and body digest. It does not bind the prepared/effective URL, authenticated account namespace, response URL, failed attempts, clock observations, successful synchronization, or quarantine state.

   This remains consistent with:

   - [tuna-receipt-aware-collection-review.md:5](../../../docs/archive/reviews/tuna-receipt-aware-collection-review.md), which distinguishes requested locators from authenticated observations.
   - [tuna-private-readbacks-review.md:7](../../../docs/archive/reviews/tuna-private-readbacks-review.md), which shows that a late sync failure can leave a reloadable complete-looking capture.
   - [the acquisition design’s journal contract](../../../docs/design/tuna-destination-sequential-evidence-case.md), which correctly leaves the attempt journal and durable quarantine unimplemented.

   The commitment is therefore a byte-match primitive, not an admission primitive. The current API does not technically prevent callers from confusing those meanings; only documentation currently preserves the distinction.

3. **SLOPPY — the tests avoid the strongest coherent-substitution falsifier.**

   The focused mutations at [test_qi_tuna_capture_commitment.py:43](../../../tests/scripts/test_qi_tuna_capture_commitment.py) mostly use stale or malformed metadata. The integration mutations at [test_qi_tuna_readback_collection.py:207](../../../tests/scripts/test_qi_tuna_readback_collection.py) alter only receipt zero.

   Missing cases include:

   - same-length body substitution with its recomputed valid body digest;
   - valid status substitution such as 200 to 201;
   - coherent checkpoint plus all-four-receipt replacement;
   - later-position receipt substitutions;
   - verification of those replacements against a fixed, pre-existing external commitment.

   These omissions do not reveal an algorithmic collision. They leave the evidence-critical trust boundary uncalibrated.

4. **SLOPPY — canonicality has one implementation vector, not an independent encoding specification.**

   The focused test reconstructs the schema but uses the same `json.dumps` implementation and options as production at lines 22–39. It should add a literal canonical-byte or precomputed-digest vector containing non-ASCII text, escapes, control characters, and non-empty ordered queries.

   The public shape validator also bounds bodies but leaves path length, content-type length, query length, query-key length, and integer magnitude unbounded. Intended transport-generated captures have a closed locator surface, so this is a direct-construction robustness issue rather than an acquisition-path defect.

## Sound mechanisms

- The encoding at [qi_tuna_capture_commitment.py:59](../../../scripts/qi_tuna_capture_commitment.py) is deterministic and unambiguous for admitted values: fixed schema, sorted keys, compact separators, ASCII escaping, ordered arrays, and a NUL-terminated domain prefix.
- Ordered query multiplicity remains visible; JSON serialization does not collapse it into an object.
- Boolean-as-integer confusion is rejected through exact-type checks.
- The module recomputes every body digest before using the supplied digest. It does not blindly trust external body metadata.
- A coordinated body-plus-digest or metadata substitution changes the outer commitment. Binding is computational and depends on SHA-256 collision and second-preimage resistance; it is not a mathematical injectivity proof.
- `ReadbackCapture` and `Readback` are frozen dataclasses whose admitted leaves are bytes, strings, integers, and tuples. Ordinary mutable-alias and check-to-hash races are absent.
- The malformed expected commitment checks enforce exact lowercase 64-hex syntax and constant-time comparison.
- The acquisition design accurately withholds authentication, timeliness, durability, provider truth, and admission. The two prior reviews and current design are substantively consistent.

The archived reviews describe older integration bytes: the receipt-aware review recorded `16411e…`, and the private-store review later observed `defce5…`. The current staged integration is `1ede90…`. Their findings remain applicable, but their hash tables and old line locators are historical receipts rather than current-head review evidence.

## Exact identities

Final read-only observation: `2026-10-28T06:49:43Z`; HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

| Artifact | Staged SHA-256 | Git blob |
|---|---|---|
| `scripts/qi_tuna_capture_commitment.py` | `7e5eac896f14dfa3757f27e7d4a35ead98e857f06ab5b13eb91a140fc146b97e` | `a66e3a16b7260c92a12993388c6072a0ea17482f` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `cda6b4a0bee51d5db6a968730c23b4fef6f945e41f4859808df4731722a237cb` | `dd8dc89d68c44682b37bfcc1c1ae5d25f0640a5d` |
| `tests/scripts/test_qi_tuna_readback_collection.py` | `1ede90ffe8fc1adc90020c2c01cd3e1a29ddf4c4786e2475a76fb293e061c0e8` | `212b673dfa5300fb0100bcd2b7b7ba45b9edd72a` |
| Receipt-aware review | `8307a7908c12d3b2a88dd70fefccc0382fddad56990159c2c4c57c787f48e622` | `c9077374c2fcd020be9676dda342ed672abd2008` |
| Private-store review | `ba14de7563dddbf6e7888725f5107f31f42af022ae09df10d0900878a22b5005` | `1db8bf9101aa2577c9dc60a715ff3ffd9813e2e0` |

Working-tree acquisition-design SHA-256:

`d2701c11645a8826be4fa1b8ba80e52f11a5090d519736c6f44a9bcb3326ae93`

At the final observation, the design’s staged blob matched those working-tree bytes; Git blob `6bff20b3a3e7585cfae30311025340e6c84027d8`.

The design index entry changed during the review from the older staged `bea0ef…` revision to the final `d2701c…` revision. My process performed only reads.

## Scope limits

Static inspection only. I ran no tests, linters, imports, network requests, credential reads, provider operations, jobs, uploads, random draws, external messages, or repository writes. The review establishes local encoding and comparison properties only; it provides no filesystem-crash evidence, provider authentication, timing evidence, physical acquisition order, or scientific admission.

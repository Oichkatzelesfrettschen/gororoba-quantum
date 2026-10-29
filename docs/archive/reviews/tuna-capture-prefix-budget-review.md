The staged validator core is sound, but the staged collector still fails the follow-up review’s explicit retention-order requirement. The change prevents returning an incompatible capture while preserving the incompatible bytes on disk.

All locators below are index-line locators from `git show :path`; the capture script and its test contain later unstaged changes, so worktree links would identify different bytes.

## Findings

1. **SERIOUS — validation still occurs after retention.**

   The follow-up requires rejecting an over-budget response before `retain_readback` (`INDEX docs/archive/reviews/tuna-journaled-collection-followup-review.md:7-15`). The collector instead performs:

   - retention at `INDEX scripts/qi_tuna_journaled_collection.py:95`
   - prefix validation at line 96
   - expiry checking at line 97

   The staged test demonstrates the defect at `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:358-403`: four large `Content-Type` values reach private retention; the fourth response produces a complete reloadable capture; `capture_commitment` then rejects it.

   A stronger counterexample uses `application/json;` followed by non-Basic Multilingual Plane characters. The transport accepts the media-type prefix, private retention JSON-escapes the metadata to roughly twelve times its character count, and only afterward does prefix validation reject it. The loader subsequently refuses metadata exceeding `MAX_BODY`.

   The attempt journal already retains the provider outcome. Moving prefix validation before private readback retention would preserve attempt evidence without retaining bytes outside the commitment domain.

2. **SERIOUS — fourth-response callback or expiry failures remain indistinguishable after restart.**

   A fourth `retain_readback` callback can make every file visible and then raise during its final synchronization. The collector propagates the exception at line 95, but the private store can reload as a complete capture. The supporting staged boundary test proves this filesystem state at `INDEX tests/scripts/test_qi_tuna_private_recovery_boundaries.py:23-58`.

   Likewise, a fourth response can be retained and validated before the clock raises at collector line 97. The direct collection test covers the exception and endpoint stopping at `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:143-193`, but it never reloads or classifies the resulting complete-looking store.

   The retained files carry no durable state distinguishing:

   - successfully collected;
   - retained but expired;
   - visible despite callback failure;
   - quarantined;
   - admitted.

3. **SERIOUS evidence gap — callback and expiry coverage remains incomplete.**

   The staged tests establish partial-stream stopping, checkpoint-callback refusal, all four readback-retention and post-retention-clock positions, 401 retention before refresh, forced-refresh failure, and large-metadata endpoint stopping.

   They do not establish the follow-up matrix for initial-clock failure, post-checkpoint-clock failure, initial refresh, intent or outcome callback failure, clocks surrounding refresh and intent, request/stream clock expiry, or callbacks that write partially before raising. The retention fixture at `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:161-166` raises before invoking the real store, so it cannot falsify after-write ambiguity.

4. **SLOPPY evidence gap — canonical bytes remain absent from the fixed vector.**

   Canonical construction is deterministic: sorted keys, compact separators, ASCII escaping, bounded integers, and no floating-point values appear at `INDEX scripts/qi_tuna_capture_commitment.py:100-112`.

   However, `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:94-110` retains only the expected digest while claiming a literal canonical-byte vector. The other expected-value calculation at lines 22-39 uses the same Python JSON implementation as the production code. The tests should retain the canonical bytes or an independently replayable encoding receipt.

## Sound portions

- **Shared prefix/complete validation:** `validate_capture_prefix` and `capture_commitment` both call `_validated_envelopes`; complete validation adds only the four-receipt cardinality requirement (`INDEX scripts/qi_tuna_capture_commitment.py:37-46,95-102`).
- **Escaped-size accounting:** staged tests cover control characters, DEL, Basic Multilingual Plane characters, lone surrogates, and non-Basic Multilingual Plane characters, and prove oversized aggregates fail before serialization (`INDEX tests/scripts/test_qi_tuna_capture_commitment.py:153-176`).
- **Fixed-overhead reserve:** the maximum omitted canonical overhead is `167 + 4×163 + 3 = 822` bytes. The 2,048-byte reserve therefore leaves at least 1,226 bytes of margin. The implementation is sound; the staged tests do not preserve this proof.
- **Endpoint stopping:** sequential exception propagation stops later endpoints, and the large-metadata test proves stopping at positions three and four.
- **Identifier bounds:** all four checkpoint identifiers are parsed and bounded before the first callback (`INDEX scripts/qi_tuna_journaled_collection.py:65-80`); staged tests cover independent 257-bit rejection and inclusive 256-bit acceptance.
- **Admission boundary:** the module accurately declares authentication, trusted timing, durability, admission, and cross-restart quarantine unresolved (`INDEX scripts/qi_tuna_journaled_collection.py:3-6`). Treating `UnadmittedCapture` as enforcement would be FATAL: callers can access `.capture` directly. The wrapper is a warning label, not an admission mechanism.

## Exact staged SHA-256

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_capture_commitment.py` | `b65404a694d9f135b28b15cefe383060d718962e1fddde3d174b20e204c7b9a1` |
| `scripts/qi_tuna_journaled_collection.py` | `fa4dae8b3ba3baec20dab8e1feeb72cdf732687e172857e6d6e27c832abcfe42` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `536de40440f3b3434027bb971296139b2d0d890ebbf7e2e23153dff337b2c7ad` |
| `tests/scripts/test_qi_tuna_journaled_collection.py` | `225646bae941e1d6e7ebc648efc757355477025c62ea6259d5afccb56a3c5b5c` |
| Supporting `tests/scripts/test_qi_tuna_private_recovery_boundaries.py` | `0b2c5b70ff950a086688d4bcdb9a4fe0365d31992e9326a9397a85f2398a6429` |
| Review contract | `94ee70fcc2213eff90715f5505dc9bd305c34487d7de6c607206909e76f4ad3c` |

Verdict: the staged change does not close the follow-up review. Prefix/complete equivalence, digest construction, reserve bounds, identifier validation, and local endpoint stopping are sound. The collector must validate each candidate prefix before private retention, and a durable external quarantine/adjudication record must classify complete-looking fourth-response artifacts before they can support timing or scientific claims.

The review ran zero tests and performed zero repository edits, credential reads, network calls, provider operations, jobs, uploads, draws, or messages. Before-and-after observations retained HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, porcelain-status digest `22212c04…4bc5`, target index-entry digest `e4664ced…31d`, and local-ref digest `8a796a33…74a`.

Reviewed the complete staged blobs as systems/evidence-retention code. All locators below refer to `INDEX path:line`; both test files have unstaged worktree changes, so worktree line links could identify different bytes.

## Severity-ranked findings

1. **FATAL — the staged review document describes the inverse of the staged implementation.**

   `INDEX docs/archive/reviews/tuna-capture-prefix-budget-review.md:7-19,67` says retention precedes validation. The current staged collector instead performs:

   - prefix validation at `INDEX scripts/qi_tuna_journaled_collection.py:95`;
   - capture retention at line 96;
   - the post-retention clock check at line 97.

   The regression at `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:358-399` likewise requires the rejected receipt to remain absent from the private store and prevents every later request.

   The document’s central verdict therefore cannot serve as a review receipt for the current index.

2. **SERIOUS — the review document’s staged provenance is stale.**

   The four primary SHA-256 values at `INDEX docs/archive/reviews/tuna-capture-prefix-budget-review.md:60-63` differ from the current staged bytes. Line 51 also says the tests lack a fixed-reserve proof, but `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:179-207` now contains that proof.

3. **SERIOUS residual limitation — a valid fourth receipt can leave a complete-looking store after failure.**

   After successful prefix validation, the collector calls `retain_readback` and then `check_clock` at `INDEX scripts/qi_tuna_journaled_collection.py:96-97`. Either operation can raise after all four receipt files become visible.

   `INDEX scripts/qi_tuna_private_readbacks.py:130-157` exposes files before the callback finishes. `INDEX tests/scripts/test_qi_tuna_private_recovery_boundaries.py:23-58` demonstrates that a final synchronization failure can leave a reloadable four-receipt store.

   The collector accurately excludes durability and cross-restart quarantine at lines 3-6. Consequently, reloadability proves neither successful collection nor timeliness, quarantine, or admission.

4. **SLOPPY — the collector’s limitation statement omits source association explicitly.**

   Lines 65-79 parse checkpoint identifiers and derive allowed locators, but the collector authenticates neither the checkpoint nor its case, catalogue, manifest, backend, or result-page source. `UnadmittedCapture` prevents an admission claim, but the module docstring should name checkpoint/source association among the caller-owned controls.

5. **SLOPPY evidence gap — the claimed canonical-byte vector retains only its digest.**

   `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:94-110` claims a literal canonical-byte vector hashed with OpenSSL, but the staged test retains only the resulting digest. Lines 22-39 derive another expectation through the same Python JSON implementation used by production. Retaining the canonical ASCII bytes or an independent replay receipt would establish the claimed provenance.

## Static verification

| Requirement | Result |
|---|---|
| Attempt outcome before prefix validation | **SOUND.** `retain_outcome` executes in the transport’s `finally` block at `INDEX scripts/qi_tuna_attempt_transport.py:119-139`; the readback returns at line 147; prefix validation follows at collector line 95. Callback completion is established, while durable persistence remains caller-owned. |
| Invalid prefix before capture retention | **SOUND.** Validation at line 95 precedes retention at line 96. An exception exits the loop before retention or another request. |
| ASCII and escaped Unicode regressions | **SOUND.** `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:358-399` covers large ASCII metadata failing at positions three and four and non-Basic-Multilingual-Plane Unicode failing at position four. The failed attempt becomes terminal; the invalid receipt stays out of the private store. |
| Escaped-size accounting | **SOUND.** Commitment lines 20-35 match `ensure_ascii=True`: short control escapes use two bytes, other control and Basic Multilingual Plane values use six, and non-Basic-Multilingual-Plane values use twelve. Tests at lines 153-176 include DEL, lone surrogates, and non-Basic-Multilingual-Plane characters. |
| Fixed metadata reserve | **SOUND and conservative.** Maximum omitted canonical overhead is 822 bytes. The 2,048-byte reserve leaves 1,226 bytes of margin. The test at lines 179-207 uses maximal receipt cardinality, query cardinality, integer width, status, checkpoint length, and body length. |
| Clock and failure effects | Initial clock failure precedes all retention; post-checkpoint clock failure can leave only the checkpoint; request, stream, close, and clock failures after intent reach the outcome callback; prefix failure retains attempt evidence only; readback-retention and post-retention-clock failures stop later endpoints but can leave visible files. |
| Source, identity, timing, quarantine | Explicitly unresolved. The commitment binds checkpoint bytes and ordered receipt envelopes, but authenticates neither account/token subject, source/case identity, effective URL, provider observation time, callback durability, nor quarantine/admission state. Local request order also establishes no provider execution-order guarantee. |

## Exact staged SHA-256

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_journaled_collection.py` | `b69fc636fb9c7fd8e75f2f4f6f7cfbe125c636ef818e1b594e7d428ae2550b00` |
| `scripts/qi_tuna_capture_commitment.py` | `45519a76f10e3ca7b33c29b1fe5e0168965d5671feb6b515354e54a49ea6f70d` |
| `tests/scripts/test_qi_tuna_journaled_collection.py` | `6b9cbf6b464fb5acf0e5c03676d407690ff5a9954bae16a331c16e6fa09038b0` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `68e757351acfc5856625e20af039f9cd94ef9af2c259eec264f247f9d2960bab` |
| `docs/archive/reviews/tuna-capture-prefix-budget-review.md` | `99006b95737f18d44701a531e1ba7ddaaeec881f3d1087b52553c4d1e92a9e2f` |
| Supporting `tests/scripts/test_qi_tuna_private_recovery_boundaries.py` | `0b2c5b70ff950a086688d4bcdb9a4fe0365d31992e9326a9397a85f2398a6429` |

Verdict: the staged code repairs the requested outcome-validation-retention ordering, and the ASCII, escaped-Unicode, and fixed-reserve accounting are statically sound. The staged review document is fatally stale. Durable classification of complete-looking stores after callback or clock failure remains an explicit external quarantine/adjudication obligation.

The review used only read-only Git and text inspection. It ran zero tests, imports, credential reads, network calls, provider operations, jobs, uploads, draws, repository edits, or external messages.

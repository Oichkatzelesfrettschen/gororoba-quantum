The identifier-bound repair is sound, but the staged composition still has one SERIOUS compatibility defect: response-dependent `Content-Type` metadata can be fully retained yet rejected by the commitment.

I reviewed the complete staged Python blobs as systems/security evidence code. The unstaged working-tree changes to `tests/scripts/test_qi_tuna_journaled_collection.py` were excluded.

## Findings

1. **SERIOUS — successfully retained response metadata can exceed the commitment budget.**

   `INDEX scripts/qi_tuna_journaled_collection.py:84-98` retains each successful receipt and returns the four-receipt capture without enforcing the commitment’s cumulative escaped-metadata limit. The transport accepts any content type whose prefix before `;` is `application/json`, while `INDEX scripts/qi_tuna_capture_commitment.py:78-81` limits the aggregate metadata of all four receipts to `MAX_BODY`.

   Counterexample: four HTTP 200 responses with `Content-Type: application/json;` followed by 600,000 ASCII characters. Each attempt journal and private readback metadata file remains individually below 2 MiB, so all four callbacks can succeed. The commitment accumulates more than 2.4 MiB and rejects the resulting capture.

   `INDEX tests/scripts/test_qi_tuna_journaled_collection.py:337-355` proves only identifier compatibility with short synthetic headers. The commitment test at lines 147-150 proves aggregate rejection but never composes that rejection with successful collection and retention.

   Remedy: use a shared commitment-envelope budget while processing receipts, and reject an over-budget response before `retain_readback` and endpoint progression.

2. **SERIOUS evidence gap — the expanded tests still cover only part of the archived failure matrix.**

   The new tests genuinely establish:

   - First 401 retention before forced refresh and retry: lines 220-265.
   - Forced-refresh failure leaving one `retry_pending` journal and stopping later endpoints: lines 268-309.
   - Readback-retention and post-retention-clock failures at each of the four endpoint positions: lines 143-193.

   They do not establish composition behavior for the initial clock, post-checkpoint clock, initial refresh, intent/outcome callback failures, clocks surrounding refresh and intent, or request/stream clock failures. The four-position test verifies endpoint stopping and terminal attempt journals, but it neither inspects the retained capture prefix nor exercises a callback that writes partially before failing.

3. **SLOPPY evidence gap — escaped-size coverage improved, but the fixed reserve remains unproved.**

   `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:153-160` now compares `_escaped_size` with canonical JSON across control characters, DEL, Basic Multilingual Plane characters, lone surrogates, and a non-Basic Multilingual Plane character. Lines 163-176 prove that an oversized escaped aggregate fails before `json.dumps`. These additions repair the main pre-serialization defect identified by the archived review.

   The implementation still begins with an unexplained `metadata_size = 2048` reserve at `INDEX scripts/qi_tuna_capture_commitment.py:47-49`. The staged tests contain no explicit bound for the omitted schema keys, punctuation, digests, status values, lengths, and array structure. The reserve appears conservative, so this is a maintenance-proof gap rather than a demonstrated undercount. The fixed vector at test lines 94-110 also retains only the digest, not the canonical bytes or an independently replayable encoding receipt.

## Identifier repair

**SOUND.** `INDEX scripts/qi_tuna_journaled_collection.py:65-79` parses and bounds `job`, `file`, `batch`, and `result`, then validates every constructed target. The first caller-controlled callback occurs at line 80.

`INDEX tests/scripts/test_qi_tuna_journaled_collection.py:312-334` supplies a 257-bit value independently in all four positions and verifies that clocks, refresh, retention callbacks, journals, and requests remain untouched. Lines 337-355 exercise the inclusive 256-bit maximum through `capture_commitment`.

## Authenticated admission and quarantine

**FATAL if these artifacts are treated as an admission layer; accurately unresolved by the code.**

Neither the wrapper nor the commitment binds the authenticated account or token subject, effective URL, trusted clock evidence, source/case identity, durability, or a cross-restart quarantine decision. The 401 refresh test establishes local ordering only. The wrapper’s accessible `capture` field and the decoder-rejection test provide an accidental-use guard, not authentication or quarantine.

The module docstrings correctly assign those controls to a later adjudicator. The coherent-replacement test at `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:85-91` also correctly demonstrates that a self-derived expected commitment authenticates nothing.

## Exact staged SHA-256

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_journaled_collection.py` | `43ce816b8788b126d9e2098680eceb60d783e2c38dfd61dcc83e07c00613cc6e` |
| `tests/scripts/test_qi_tuna_journaled_collection.py` | `73325a3c690eccce84cdaf2ad85c135eec42a78fd97da98f9b402202daec03b9` |
| `scripts/qi_tuna_capture_commitment.py` | `ac48334497da49dbe7261fbb8a6c56024ab91e6aacf36da5442dbc3c8acfc15d` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `536de40440f3b3434027bb971296139b2d0d890ebbf7e2e23153dff337b2c7ad` |

The archived review’s hashes are obsolete for the collector and both test files; only the commitment implementation retains its archived hash.

Review basis HEAD: `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

The before-and-after observations record identical HEAD, porcelain-status digest, target index-entry digest, and local-ref digest. `git diff --cached --check` reported clean output for the four files. I ran no tests, credentials reads, network calls, provider operations, jobs, uploads, draws, external messages, or repository edits.

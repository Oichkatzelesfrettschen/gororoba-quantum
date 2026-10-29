The revised staged code is sound as a synthetic, locally consistent attempt recorder. It remains inadmissible as authenticated acquisition or scientific evidence. I found no intrinsic FATAL defect within that narrow contract.

The archived reviews describe earlier blobs: all four script/test hashes have since changed.

## Residual findings

1. **FATAL if scientifically admitted; SOUND as explicitly unadmitted data. High confidence.**

   The new [`UnadmittedReadback`](../../../scripts/qi_tuna_attempt_transport.py) closes the accidental return-type hole, and the decoder test verifies rejection of the wrapper at [test_qi_tuna_attempt_transport.py:373](../../../tests/scripts/test_qi_tuna_attempt_transport.py).

   Admission remains unenforced. The public `readback` field exposes the legacy `Readback`, while the records still omit account identity, method, authority, case and clock digests, effective request, response URL, trusted timing, quarantine, and adjudication. Repository search found production use only of the older transport; the new transport and journal connect solely in synthetic tests.

2. **SERIOUS — crash-surviving quarantine remains external. High confidence.**

   [`PrivateAttemptJournal`](../../../scripts/qi_tuna_attempt_journal.py) stores persistence failure only in `_failed`. A sync or close can report failure after complete bytes become readable. Process exit erases the latch, and [`load_attempt_journal`](../../../scripts/qi_tuna_attempt_journal.py) consults no durable failure marker.

   The journal test injects only the first intent-sync failure at [test_qi_tuna_attempt_journal.py:39](../../../tests/scripts/test_qi_tuna_attempt_journal.py). It does not exercise outcome/body/directory-sync failures, close failures, or a restart that loads complete-looking files after a reported persistence failure.

3. **SERIOUS — exact provider request, authentication, and timing semantics remain unbound. High confidence.**

   The transport visibly passes `GET`, the canonical requested URL, query, timeout, streaming, and disabled redirects at [qi_tuna_attempt_transport.py:83](../../../scripts/qi_tuna_attempt_transport.py). It does not inspect the effective prepared request, `response.url`, redirect history, authenticated subject, or refresh identity. A caller-supplied `Any` session can ignore the arguments.

   `request_called=True` still means only that execution reached the call site. Refresh, request, streaming, close, and retention lack an enforceable end-to-end deadline; the final clock check precedes close and retention. The tests never assert the exact method, URL, options, refresh force flag, or clock/refresh ordering.

4. **SERIOUS when integrated without external serialization — concurrent consistency is assumed, not implemented. High confidence.**

   The journal correctly documents caller-owned serialization. The loader snapshots directory names once at [qi_tuna_attempt_journal.py:200](../../../scripts/qi_tuna_attempt_journal.py), then reads files individually. A same-user process can add an entry after that snapshot or replace separate files between reads. Per-file mutation checks cannot establish a directory-wide snapshot. The tests contain no concurrent mutation case.

5. **SLOPPY — negative coverage remains narrower than the validator’s claims. High confidence.**

   The validator now statically rejects the archived contradictory states at [qi_tuna_attempt_journal.py:44](../../../scripts/qi_tuna_attempt_journal.py), including exact-type checks that reject Python boolean/integer aliases. Tests cover four contradictions and boolean aliases only for attempt ordinals. They omit aliases in status, body length, query values, `request_called`, and `complete`, plus error-free empty/non-JSON HTTP 200 and second-attempt error-free HTTP 401 mutations.

## Confirmed repairs

- The success result is now explicitly unadmitted.
- Retention failure preserves a prior transport error and groups distinct transport-plus-close errors at [qi_tuna_attempt_transport.py:132](../../../scripts/qi_tuna_attempt_transport.py). The triple-failure test genuinely inspects that group.
- The outcome validator rejects the archived impossible state combinations on both write and reload.
- A lone retryable HTTP 401 now returns `lifecycle="retry_pending"` at [qi_tuna_attempt_journal.py:267](../../../scripts/qi_tuna_attempt_journal.py), and tests distinguish it from terminal replay.
- Metadata fields and final encoded metadata are bounded before the body write at [qi_tuna_attempt_journal.py:101](../../../scripts/qi_tuna_attempt_journal.py) and [qi_tuna_attempt_journal.py:175](../../../scripts/qi_tuna_attempt_journal.py).

## Exact staged SHA-256 inputs

| Staged input | SHA-256 |
|---|---|
| `scripts/qi_tuna_attempt_transport.py` | `d4f128f7b6eb43d918895dad18f5b8aa7378a0f9535eb64398c7fef567885068` |
| `scripts/qi_tuna_attempt_journal.py` | `b497a26c7cf8e66315898665b4a8422e1281caeb63ff0f928f7d56d05efb7635` |
| `tests/scripts/test_qi_tuna_attempt_transport.py` | `29e62f2d191ccc4e8c1945dd8028f0e7da946502e0ac0a9a6449285e23d8e052` |
| `tests/scripts/test_qi_tuna_attempt_journal.py` | `b20c7336d2137dda9f86047fbb5f9b84a6467ac21a78663ff2b6dd35cb26c788` |
| `docs/archive/reviews/tuna-attempt-transport-review.md` | `9826e7cebf3a90303bf51551659be8a2a025850166401bdb48cff97beb03830e` |
| `docs/archive/reviews/tuna-private-attempt-journal-review.md` | `1bca745e934c8c414a15180927cdcd683cfb3b121cb130d9a2ff119195db4221` |

Supporting staged inputs included the design (`47794818…29cf`), private persistence helper (`4fb6db32…a66`), readback transport (`246672e6…a00`), collection (`45a5b6e0…3af`), and JSON validator (`4abd49b1…5be`).

This was static inspection only. I ran no tests, imports, credentials, network, provider operations, jobs, uploads, draws, messages, or edits. Initial and final observations recorded identical `HEAD` `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, identical six staged hashes and index entries, matching working-tree copies, and an empty `git diff --cached --check` result. Other repository surfaces were not measured.

Prior memory was used only to keep live Quantum Inspire credential validity outside this static verdict; that remembered authentication state was not refreshed and may be stale.

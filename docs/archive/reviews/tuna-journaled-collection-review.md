The staged code contains one SERIOUS cross-component defect and two substantial evidence gaps. The local 401 and callback sequencing is otherwise sound on static inspection. The artifacts remain categorically unfit for scientific admission without the external controls their docstrings identify.

I reviewed the complete staged versions of the four requested files, plus the staged attempt transport, attempt journal, private readback store, dispatch clock, readback collection, source-association helpers, and relevant design sections. The two test files have unstaged changes (`AM`); this review excluded those working-tree versions.

## Findings

1. **SERIOUS — the collector accepts captures that the commitment layer refuses.**

`INDEX scripts/qi_tuna_journaled_collection.py:64-73` accepts every positive batch identifier and passes the value directly into the `/batch_jobs` query. The transport and attempt journal impose no 256-bit limit. `INDEX scripts/qi_tuna_capture_commitment.py:58-65`, however, rejects every query integer above 256 bits.

Counterexample:

```json
{"job":11,"file":12,"batch":2^256,"result":21}
```

The actual JSON would contain the decimal representation of `2^256`. The collector can:

- retain the checkpoint;
- issue and retain `/jobs/11`;
- issue `/batch_jobs?id=<257-bit value>`;
- return a locally complete `UnadmittedCapture` if the synthetic or provider session returns valid responses.

`capture_commitment(result.capture)` then rejects the second receipt. The rejection occurs after provider-facing reads and durable callbacks rather than before the first state transition.

Remedy: define one shared identifier/query bound, validate all four locators before `check_clock()`, `retain_checkpoint()`, or any request, and add a 256/257-bit collector-to-commitment round-trip test.

2. **SERIOUS evidence gap — the composition tests do not establish the advertised failure matrix.**

The collector’s control flow propagates exceptions and stops later loop iterations, but the staged tests cover only a narrow subset:

| Failure surface | Result visible from inspection | Staged composition coverage |
|---|---|---|
| Initial clock, collector line 75 | No checkpoint or request | Missing |
| Checkpoint callback, line 76 | A partial checkpoint write is possible; no request | Simple immediate exception only |
| Post-checkpoint clock, line 77 | Checkpoint may exist; no attempt begins | Missing |
| Initial refresh or surrounding clocks, transport lines 67–69 | No intent exists | Missing |
| Intent callback | A partial journal write is possible; no request | Component test only |
| Clock after intent | A not-called outcome should be retained | Component test only |
| Request/status/stream/close failures | An ambiguous attempt or bounded prefix should be retained | Partial second stream only at composition level |
| Outcome callback | A provider attempt may exist; retry must stop | Component test only |
| First HTTP 401 and forced refresh | First outcome must precede forced refresh and second intent | Entire composition path missing |
| Failure after first 401 | Journal should reload as `retry_pending`; later endpoints must remain untouched | Missing |
| Readback callback | Terminal attempt exists; capture persistence may be ambiguous | First endpoint only |
| Post-readback clock | Complete-looking retained bytes may exist but cannot be on-time evidence | First endpoint only |
| Failures at endpoints three and four | Earlier receipts remain retained; later requests stop | Missing |
| Callback or response-close operation that blocks indefinitely | Synchronous collection cannot fail-stop | Missing; bounded callbacks remain a caller obligation |

The attempt-transport tests cover many component cases, including 401 ordering, request ambiguity, partial bodies, close errors, and outcome-retention failure. They do not prove that four separate journals, the capture store, forced refresh, and endpoint progression compose correctly.

Remedy: parameterize request position across all four endpoints and inject each callback/clock failure. Add integrated 401→200, 401→forced-refresh failure, 401→post-outcome clock failure, second-attempt failure, and late-sync/restart-quarantine cases.

3. **SLOPPY — the canonical-size tests can pass without proving pre-allocation enforcement.**

The `_escaped_size` implementation at `INDEX scripts/qi_tuna_capture_commitment.py:19-34` appears correct for ASCII, short escapes, `\uXXXX`, lone surrogates, and non-Basic Multilingual Plane surrogate pairs. The 256-bit signed-integer bounds also appear correct.

The tests establish less:

- `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:147-150` accepts any `"metadata is oversized"` failure. A broken preflight could allocate the oversized canonical JSON and fail only at producer lines 98–100; the test would still pass.
- The fixed digest at test lines 94–110 does not retain the exact canonical byte string or an independently reproducible encoding receipt. OpenSSL hashes supplied bytes; OpenSSL does not independently establish the JSON encoding.
- The fixed vector omits a non-Basic Multilingual Plane character, a lone surrogate, DEL or another six-byte escape, negative boundary integers, and reversed query order.
- The fixed `metadata_size = 2048` reserve has no direct proof or regression assertion that the fixed schema overhead remains below the reserve.

Remedy: make the test fail if `json.dumps` is reached for an aggregate rejected by preflight, retain literal canonical bytes beside their digest, add escape-category vectors, and assert the fixed-overhead calculation explicitly.

## Scientific and security admission boundary

**FATAL if these primitives are treated as an admission layer; correctly disclaimed by the staged code.**

The journal does not bind the authenticated account, token subject, method and authority, effective prepared request, response URL, trusted clock evidence, charge state, source/case digest, or durable quarantine decision. Refresh operations occur outside the attempt stream. A forced refresh can fail or change effective identity while the journal records only a first 401 and, if execution continues, another requested locator.

Likewise, `UnadmittedCapture.capture` is deliberately accessible. The wrapper prevents accidental direct decoder use; it is not a security boundary. A caller can unwrap the capture. A self-derived expected commitment also authenticates nothing, as the coherent-replacement test explicitly demonstrates at `INDEX tests/scripts/test_qi_tuna_capture_commitment.py:85-91`.

The older memory-derived Tuna evidence context likewise distinguishes ordered returned bit strings from per-shot timestamps; that note may be stale, while the current staged design independently preserves the same timing limitation.

## Sound portions

- The transport retains an intent before `session.request`.
- A response closes and its complete, error-free 401 outcome reaches retention before forced refresh and the second intent.
- Intent or outcome callback exceptions prevent the next request.
- Partial and oversized streams retain only the bounded observed prefix.
- Close failures prevent retry and enter the outcome classification.
- Readback retention precedes the collector’s final clock check.
- The commitment binds checkpoint bytes by length and digest, ordered receipt envelopes, body lengths, and verified body digests.
- The JSON encoding uses sorted keys, compact separators, ASCII escaping, ordered arrays, and a domain-separated SHA-256 input.
- The module and design text accurately reserve authentication, timing, durability, quarantine, and scientific admission for a later adjudicator.

## Exact staged SHA-256

The hashes were computed twice from `git show :PATH` and remained identical during review:

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_journaled_collection.py` | `dfde1bcfe2bc14ef703074fdbc8b20017a14ea02ebbfcfd8824530e444b5d27b` |
| `tests/scripts/test_qi_tuna_journaled_collection.py` | `38d60c71bc26a247a632bc989f898fac818815eea5f49ad380add39ed78f4bf0` |
| `scripts/qi_tuna_capture_commitment.py` | `ac48334497da49dbe7261fbb8a6c56024ab91e6aacf36da5442dbc3c8acfc15d` |
| `tests/scripts/test_qi_tuna_capture_commitment.py` | `c07482f57fdbd0268de4bbf9af7c3d84ed9e971b9a26bc10de546d82a489f4e5` |

Review basis HEAD: `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`.

I ran zero tests, credentials reads, network calls, provider operations, jobs, uploads, random draws, messages, or repository edits.

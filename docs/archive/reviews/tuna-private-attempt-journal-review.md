Verdict: the staged journal is a useful local consistency recorder, but it is unsafe as acquisition or scientific-admission evidence. I found three serious defects plus several coverage gaps. The repository accurately documents most provenance limitations.

All line references below identify the staged blobs whose hashes appear later. Four working-tree copies changed during review; those unstaged changes were excluded.

## Findings

1. **FATAL for scientific admission — the journal lacks the acquisition identity and evidence required by its own design.**

   `AttemptIntent` records only attempt number, path, and query (`scripts/qi_tuna_attempt_transport.py:19-35`). The design requires slot, request ordinal, account namespace, method, canonical authority, case digest, clock-evidence digest, effective request, effective response URL, and observation evidence (`docs/design/tuna-destination-sequential-evidence-case.md:245-265`).

   The transport also returns the ordinary `Readback` type at line 131, which `PrivateReadbackStore.retain_readback` accepts directly. The API therefore supplies no type-level barrier between an unadjudicated local receipt and downstream capture data.

   The repository search found journal/transport use only in synthetic tests; the staged design explicitly says the existing collector remains unwired (`design:267-287`). This is therefore an admission blocker rather than a presently reachable provider defect.

   Remedy: return an explicitly unadmitted type, bind the full authenticated request and clock context, and require an adjudicator before conversion into any scoring-compatible capture.

2. **SERIOUS — the outcome validator accepts states the transport cannot produce.**

   `_outcome_object` at `scripts/qi_tuna_attempt_journal.py:37-64` validates types but omits state-machine consistency. It accepts, among other impossible records:

   - `request_called=False`, `status=200`, `complete=True`, with no error;
   - an error-free HTTP 200 with an empty body or non-JSON media type;
   - an error-free HTTP 401 on attempt two;
   - an incomplete outcome without an error classification.

   The transport rejects these combinations at `scripts/qi_tuna_attempt_transport.py:96-125`, but both the writer and loader accept them. A coherently edited metadata file can therefore replay an event the supposed producer would never emit.

   Remedy: validate outcome semantics against attempt number, request state, completion, status, media type, body, and error fields during both retention and reload. Add one negative mutation per invariant.

3. **SERIOUS — a successfully loaded journal may be only a retry-pending prefix.**

   `load_attempt_journal` breaks when the second intent is absent and accepts any nonempty exact name set (`journal:152-156,214-216`). The staged test deliberately accepts a lone complete HTTP 401 pair (`test_qi_tuna_attempt_journal.py:201-217`), while the transport necessarily continues after that first 401 (`transport:126-127`).

   A crash, refresh failure, or clock failure between the first terminal outcome and the second intent therefore produces the same loaded value as an intentionally stopped caller. The tuple contains enough information for a careful caller to recognize the 401, but the API provides no explicit `retry_pending`, `aborted`, or terminal lifecycle state.

   Remedy: retain or derive an explicit lifecycle verdict and prevent successful load from being interpreted as operation completeness.

4. **SERIOUS — persistence failure quarantine exists only in process memory.**

   `_write_exclusive` writes, file-syncs, directory-syncs, and then closes. Any sync or close failure can occur after complete bytes have become readable or durable. `PrivateAttemptJournal` records the failure only in `_failed`; process exit erases that latch. A later `load_attempt_journal` can consequently accept a complete-looking directory.

   The staged journal test injects only the first intent-sync failure (`test:56-71`) and never attempts restart recovery. The shared private-readback recovery test already demonstrates the same helper leaving a reloadable capture after final metadata sync failure.

   The module and design correctly require an independent cross-restart quarantine, but the repository contains no production caller providing one. A successful reload proves neither successful persistence nor clearance after a failed write.

   Remedy: bind every case to a separately durable quarantine/adjudication authority and require that authority’s clean decision before interpreting reloaded files.

5. **SLOPPY — “local byte consistency” overstates what reload verifies.**

   Bodies receive SHA-256 verification, but intent and outcome metadata are parsed and compared semantically. Reordering JSON keys or changing whitespace alters the retained bytes without causing rejection. A same-user actor can coherently replace a body and update its metadata digest, and reload will accept the new pair.

   The filesystem checks defend against symlinks, hardlinks, FIFOs, public modes, unilateral body replacement, and mutation during an open read. They do not authenticate historical bytes or exclude another process with the same user identity. The documentation acknowledges the latter boundary, but “semantic field consistency plus current-body digest” is the accurate claim.

6. **SLOPPY — bounded body handling does not imply bounded metadata.**

   `_outcome_object` bounds only `body`. It accepts unbounded `content_type`, error-class strings, and integer status values; `_json_bytes` then serializes without a size limit. `_write_exclusive` can successfully retain metadata larger than `MAX_BODY`, after which `_read_private` rejects that same file as oversized.

   Remedy: bound every serialized field and the final encoded metadata before creating a file.

7. **SLOPPY — the staged tests omit most requested adversarial cases.**

   The journal tests cover ordering, one intent-sync failure, one body mutation, two attempt-number boolean aliases, one missing outcome, and locator-changing retry. They omit:

   - malformed, duplicate-key, truncated, and non-object JSON;
   - boolean/integer aliases in status, body length, query values, and completion fields;
   - extra entries and several missing-file permutations;
   - journal-specific symlink, hardlink, FIFO, mode, and replacement races;
   - short or zero-progress writes;
   - body/outcome file-sync and directory-sync failures;
   - file-close and journal-directory-close failures;
   - complete-looking restart recovery after persistence failure;
   - semantically impossible but type-correct outcomes.

## What holds

Within the stated one-owner filesystem boundary, the staged implementation gets several mechanisms right:

- intent precedes the request, and outcome retention precedes retry;
- retry requires a complete, error-free HTTP 401 for the same canonical locator;
- body prefixes are bounded and retained with completion/error classification;
- exclusive creation prevents overwriting;
- short writes loop until completion, while zero-progress writes fail;
- body files precede outcome metadata, with file and directory synchronization;
- missing and extra filenames are rejected;
- exact type checks prevent Python’s ordinary `bool`/`int` aliasing;
- duplicate JSON keys, non-finite constants, symlinks, hardlinks, public files, and ordinary in-read mutation are rejected.

These properties establish constrained local consistency only. They establish neither authenticated provider provenance, trusted observation time, persistence after a reported failure, durable quarantine, nor scientific admission. A prior retained-evidence note also reported ordered returned strings without per-shot timestamps; the present repository design independently preserves that clock-evidence boundary.

## Exact staged SHA-256 inputs

Computed from index bytes using `git show :PATH | sha256sum`.

| Staged input | SHA-256 |
|---|---|
| `scripts/qi_tuna_attempt_journal.py` | `bbe2b420c3ef4ef7bb092902f5c2624afbcfe7ae72354e200dccf01d8316c415` |
| `tests/scripts/test_qi_tuna_attempt_journal.py` | `c154b4bf1de3566e90a3f2114badd55a4eb9a96aca516fcfb6f2d4bf9c5d6a32` |
| `scripts/qi_tuna_attempt_transport.py` | `7c949bed13e19673b1cb5607a20a87bc5b69feeae4efa3092397a2564438e211` |
| `scripts/qi_tuna_private_readbacks.py` | `4fb6db329b26db801ef871ab4bd083888296503e6c34e76e6ebea35d6ed69a66` |
| `docs/design/tuna-destination-sequential-evidence-case.md` | `20a6c7c0decd3fe740e8906f5bc27077c2e4c90c6c4f4ced14c42fa44e1ae825` |

Static read-only inspection only. I ran zero tests, provider operations, network calls, credential reads, uploads, draws, messages, or edits.

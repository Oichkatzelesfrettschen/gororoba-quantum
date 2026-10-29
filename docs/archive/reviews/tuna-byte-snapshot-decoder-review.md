Artifact: staged Python offline evidence predicate and tests. Fields: JSON parsing, provider-resource identity, provenance, and statistical-input admission.

## Findings

1. **SERIOUS — exponent overflow bypasses non-finite rejection.**

   [_json_object](../../../scripts/qi_tuna_source_association.py) rejects literal `NaN` and `Infinity` through `parse_constant`, but leaves `parse_float=float`. A valid JSON number such as `1e400` decodes to positive infinity. An ignored extra field containing that value can survive parsing and let [decode_associated_complete_bytes](../../../scripts/qi_tuna_source_association.py) return a score.

   This contradicts the blanket non-finite rejection contract in the [design](../../../docs/design/tuna-destination-sequential-evidence-case.md). The [tests](../../../tests/scripts/test_qi_tuna_source_association.py) exercise duplicate keys but contain no literal or exponent-overflow non-finite mutation.

   Remedy: use a finite-checking `parse_float` callback or a non-overflowing representation followed by a recursive finiteness check. Test `NaN`, `Infinity`, `-Infinity`, `1e400`, and `-1e400`.

2. **SLOPPY — the decoder checks only part of the manifest’s orientation metadata.**

   The [metadata checks](../../../scripts/qi_tuna_source_association.py) bind width, early-qubit order, arm-specific classical bits, and terminal bits. They ignore `bit_order`, `index_convention`, and `canonical_early_string_offsets`.

   A digest-bound future manifest could therefore contain contradictory orientation metadata and still pass. The staged manifests are internally consistent, and the design independently fixes classical bit zero as the rightmost character, so this does not invalidate the current retained sources. It does mean the predicate cannot claim full metadata consistency.

3. **SLOPPY — byte-entry regression coverage is incomplete.**

   Language, compile settings, raw shots, histograms, and decoder mutations are tested primarily through the lower-level decoded-mapping entry point. The byte path receives positive records and duplicate-key mutations, but the provider-file snapshot itself lacks a duplicate-key mutation.

   Shared delegation makes the current behavior sound. The test suite should nevertheless drive those failures through `decode_associated_complete_bytes`, especially duplicate `language_id`, `compile_stage`, `compile_properties`, and `content` fields.

## Sound behavior

- `object_pairs_hook` recursively rejects duplicate keys at every object nesting level.
- The byte entry point creates privately owned dictionary/list trees from immutable bytes.
- The resource chain binds catalogue digest, slot, arm, manifest, source, job, file, commit, batch, Tuna-17 backend type 7, 4096 shots, and result identity.
- The batch page requires one batch containing exactly one checkpointed job. The result page requires one checkpointed result associated with that job.
- The checkpoint and provider file must carry the same positive language identifier. The file must report compile stage `none` and empty compile properties.
- Complete decoding requires 4096 ordered width-20 binary strings. The histogram requires valid width-20 keys, nonnegative integer counts, and exact multiplicity agreement with the raw shots. Valid zero-count bins remain intentionally admissible.
- The independent calculation catches drift in the two scored qubit-6 destinations.

## Remaining trust and provider requirements

The final collector must:

- Use the byte entry point exclusively for provider JSON. The lower-level mapping APIs cannot recover duplicate keys discarded by ordinary JSON decoding.
- Retain and authenticate exact response bytes, request locators, response envelopes and metadata. The current platform client’s `response.json()` path loses duplicate-key evidence.
- Bind the authenticated catalogue digest, assignment release and opening, allocation custody, fairness assumptions, approved case, and approval consumption.
- Establish the live admitted cQASM language identifier. The synthetic test value `8` supplies only local equality evidence.
- Establish authenticated file, job, batch, and result readback behavior, plus stable pagination or an explicitly approved non-atomic page boundary.
- Bind both reviewed decoder producers and their exact bytes.
- Persist slot number, arm, intent, boot identity, UTC boundary, and suspend-aware `CLOCK_BOOTTIME` boundary. Enforce the deadline on every request and retry.
- Establish result availability and zero-charge evidence by the observation boundary. Later collection cannot replace a boundary-time neutral score.
- Establish that provider raw-data order represents acquisition order. Ordered bit strings do not supply per-shot timestamps.
- Complete fresh backend, queue, heartbeat, pricing, terms, compiler, transaction, account-lock, one-batch, pause, no-retry, and late-charge admission.
- Obtain separate explicit approval for the required Quantum Inspire QX emulator run and later Tuna-17 hardware execution.
- Treat stored-source association as distinct from proof of the served analog schedule, acquisition-index mapping, calibration, discrimination, thresholds, or in-phase/quadrature data.

## Exact staged SHA-256

| Staged blob | SHA-256 |
|---|---|
| `scripts/qi_tuna_source_association.py` | `6f8e807ba7dc8c45cda763f670b883e5dd1f73f058f1b5e908afbd592a407a47` |
| `tests/scripts/test_qi_tuna_source_association.py` | `717921d5318ca7179a55bb60b255bdec4d26605a43d8c8b1d9ad5b400126d3a8` |

I ran only read-only text, Git-index, status, and SHA-256 inspections. I ran no tests, executable probes, network operations, credential access, provider operations, jobs, uploads, draws, messages, or repository edits. The two staged hashes matched before and after review. An unstaged design-document edit appeared during review; it adds the byte-preserving transport requirement and does not change this verdict.

Verdict: the staged code has a coherent source-to-result association chain for already authenticated, immutable inputs, but it is not an admission gate. One reachable false acceptance exists in histogram validation. Catalogue release provenance, atomic page capture, timing, charge, and served-hardware semantics remain external and unimplemented.

## Findings

1. **SERIOUS — malformed zero-count histogram keys pass validation.**

   `INDEX scripts/qi_tuna_source_association.py:258-263` validates only key/value types, then compares `Counter(raw)` with `Counter(histogram)`. Python treats absent `Counter` keys as zero, so valid raw shots plus:

   ```python
   {valid_shot: 4096, "not-a-width-20-shot": 0}
   ```

   pass. The staged tests at `INDEX tests/scripts/test_qi_tuna_source_association.py:231-253` cover wrong positive counts and Boolean counts, but omit zero-count junk.

   Require every histogram key to be exactly 20 binary characters and compare against `dict(Counter(raw))`, or define and enforce a canonical zero-bin policy.

2. **SERIOUS — page completeness is asserted by supplied metadata, not established.**

   `validate_result_page` accepts a caller-provided mapping claiming `total=page=pages=1` (`INDEX script:110-135`). It does not bind the endpoint request, filters, cursor, retained response bytes, observation time, or a stable second read. A later result remains possible.

   The staged batch input is weaker: `validate_slot_association` receives a bare batch mapping, with no batch response envelope or cardinality at all (`INDEX script:188-215`). The staged design explicitly identifies both omissions at lines 117-125.

3. **SERIOUS — provider/checkpoint JSON can become lossy before validation.**

   Catalogue and manifest bytes use a duplicate-key-rejecting parser (`INDEX script:18-40`). Checkpoint, job, batch, provider-file, result-page, and histogram objects arrive already decoded. Ordinary JSON decoding can collapse duplicate `id`, `job_id`, `file_id`, or histogram keys before this verifier sees them, contrary to the design’s duplicate-identity rejection requirement at staged lines 95-100.

   Retain and authenticate raw response-envelope bytes, then decode every provider record with the same duplicate-key and non-finite-value rejection policy.

4. **SERIOUS — immutability is only a caller promise.**

   The module delegates concurrent-mutation prevention at `INDEX script:3-6`. The decoder reads mutable dictionaries and lists multiple times, including two result-page validations and separate raw-shot validation, counting, and histogram comparison. The test at staged lines 442-450 rejects a `dict` subclass, but ordinary dictionaries and lists can still mutate between reads.

   The collector must snapshot authenticated bytes under the account/collection lock and validate only the resulting immutable parse.

5. **SERIOUS — decoder semantics are correct now but lack durable provenance linkage.**

   Every staged manifest binds the arm-specific readout mapping. The association decoder ignores that digest-bound metadata and calls separately versioned `decode_counts` (`INDEX script:15,255-256`). The current hard-coded offsets in `INDEX scripts/qi_tuna_sequential_score.py:18-31` match all 48 manifests, but later decoder drift would leave source association valid while producing incorrect score counts.

   Derive offsets from validated manifest metadata or bind and verify an explicit decoder schema/hash.

6. **SERIOUS if composed as campaign admission — required provenance and hardware semantics remain absent.**

   The tests derive `expected_catalogue_sha256` from the same supplied catalogue bytes. A coordinated replacement of catalogue, manifests, sources, and checkpoint hashes remains internally valid. The helper correctly declares that the caller must authenticate the catalogue digest and assignment release, but the reviewed surface supplies no such caller.

   `decode_associated_complete` also returns the exact `kind="complete"` row accepted by `score_sequence` without verifying:

   - authenticated assignment opening and current-slot release;
   - boot identity, observation boundary, or immutable decision time;
   - zero-charge evidence;
   - queue, pause, heartbeat, pricing, terms, or account-lock admission;
   - compiler/backend receipt admission;
   - whether provider readback corresponds to the served analog schedule.

   The design requires these at staged lines 167-259. Exact provider source text proves file association, not physical execution semantics. Earlier retained Tuna evidence likewise distinguishes ordered bit strings from per-shot timestamps; I used that only as a caution, not as current provider proof.

7. **SLOPPY — staged integration coverage uses an all-zero vector.**

   The positive complete-result test at staged lines 206-230 cannot detect swapped early destinations or a wrong terminal bit. An asymmetric raw record should pass through source association, decoding, and `score_sequence` as one end-to-end contract.

8. **SLOPPY — the staged design underclaims the staged implementation.**

   The staged design says raw shots are not validated at lines 122-125, while staged code validates status, shot counts, ordered binary shots, and histogram consistency. The current unstaged design corrects this wording. The index therefore contains stale design prose.

## Sound portions

- Slot and arm bind transitively through catalogue digest, catalogue row, manifest digest, manifest identity, source digest, checkpoint, and decoder arm.
- Job, file, commit, batch, backend type, shot count, result identity, raw-data flag, one-job membership, UTF-8 source content, and provider source text are checked exactly.
- All 48 alternatives are present and unique: slots 1–24, each with baseline and rotated arms.
- Every catalogue manifest digest matches its staged `cases.json`; every manifest source and backend digest matches staged bytes.
- All manifests consistently bind Tuna-17 backend type 7, 4,096 shots, one circuit, unapproved status, and `provider_execution_authorized=false`.
- Baseline source SHA-256: `3ab15a468b5eaa4811a2a06f297754269976f6901dde12370cf3d5fad593f267`
- Rotated source SHA-256: `3084eef16a0d32a23d7b3fa41c92f27fa3ce4f3d84791d128a10246728ad6d5d`
- Shared backend snapshot SHA-256: `e92dab9819a2c20da16d057373e5025e89f6e22abc34253178cb801ac32e1223`

## Exact reviewed hashes

- Staged script: `fa8198bab55fd1882d600cd40faafdbc4ebdb74213929893631999560f2818be`
- Staged test: `1f9efb4cd2c11445a3a80b0859669b0a69e9dcb8577a633a4f266eebab6bb893`
- Staged design: `ad235494bc752f215a00a879755b4af64c79a834884d245f65fc22ab75c3737e`
- Staged catalogue: `353c28a3342835478f1713f61fe590ceb8a0bd0f5f7cdea59a03a6c7a126cde4`
- Staged decoder: `d344f69db36dcc79a6ce605686aa1dfcc488fa034ad09fdfab5c7d7f9d16611b`
- Current unstaged design: `b1b22bc5ec923b7184047321901b8170df4f8fcaee8f0ad730a32d14d258e303`

All 48 staged manifest hashes were independently matched to the catalogue. I performed no test or script execution, network access, provider operation, or repository edit. The static review completed in about six minutes.

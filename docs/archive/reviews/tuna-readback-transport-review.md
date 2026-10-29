The staged local mechanisms are largely sound. No FATAL implementation defect appeared. One SERIOUS integration blocker remains: the pipeline discards the transport receipt’s locator and response envelope before association checking.

Artifact: staged Python transport, strict evidence decoder, and fake-only tests. Fields: HTTP/security boundaries, strict JSON parsing, provider-resource identity, and measurement interpretation.

## Findings

1. **SERIOUS — decoded bytes remain unbound to their request locator and response envelope.**

   The transport returns `path`, `query`, `status`, `content_type`, `body`, and `body_sha256` in [`Readback`](../../../scripts/qi_tuna_readback_transport.py). The integration test passes only `receipt.body` into the association decoder at [test line 298](../../../tests/scripts/test_qi_tuna_source_association.py).

   Consequently, the association predicate cannot detect a valid internally matching body paired with the wrong locator or response envelope. Only the result page traverses the transport; checkpoint, job, batch, and file snapshots enter the byte decoder directly. The staged design requires locator, envelope, and result identity retention before scoring at staged lines 146–156.

   Remedy: add a receipt-aware collection predicate covering all provider snapshots, with negative path/query/status/content-type/body swaps. Bind the reviewed transport and decoder producer hashes in the final packet.

2. **SERIOUS evidence boundary — fake sessions establish zero live authentication or provider state.**

   [`read_qi_json`](../../../scripts/qi_tuna_readback_transport.py) accepts an already-authenticated session and a refresh callback. The fake session has no authentication behavior, while the refresh test records only callback order at [test line 90](../../../tests/scripts/test_qi_tuna_readback_transport.py).

   Static inspection cannot establish:

   - actual provider authentication or token forwarding;
   - whether refresh updates the same live session;
   - current account access, queue, pricing, credits, heartbeat, terms, or pause state;
   - real request or result-availability timing;
   - atomic pagination or acquisition order;
   - the served analog schedule, calibration, discrimination thresholds, or in-phase/quadrature data.

   The staged design expressly assigns authentication and the trusted clock to the caller and says fake sessions establish neither provider behavior nor a live authentication boundary. A prior local note records OAuth expiry and stale long-lived clients, but that historical state was not reverified and may be stale.

3. **SLOPPY coverage — byte and clock limits are locally implemented but narrowly exercised.**

   The transport rejects accumulated decoded bodies above 2 MiB and checks its supplied clock around refresh, requests, and yielded body chunks at [transport lines 73–100](../../../scripts/qi_tuna_readback_transport.py). The tests use one already-allocated oversized chunk and fake clocks.

   The staged tests therefore do not exercise exact-limit acceptance, a limit crossed across several chunks, real transfer/content decoding, blocking inside the HTTP stack, suspend/reboot continuity, or preemption between the last clock check and request start. The design acknowledges that preemption gap and states that this helper is not an admission or dispatch guard.

4. **SOUND — the GET surface fails closed.**

   [`_validate_target`](../../../scripts/qi_tuna_readback_transport.py) uses a fixed HTTPS authority and closed path/query shapes with positive, non-Boolean identifiers. Requests use `GET`, disable redirects, stream the body, close responses, permit one deadline-checked 401 refresh attempt, and reject other statuses and non-JSON content types.

5. **SOUND — strict JSON and measurement-map findings are closed.**

   The association parser requires exact `bytes`, bounds each snapshot, rejects recursive duplicate keys, rejects `NaN`, infinities, and finite overflow, and uses exact integer-type checks that exclude Booleans at [association lines 19–53](../../../scripts/qi_tuna_source_association.py).

   The decoder now checks `decoder_rule`, the arm-specific early destinations, terminal destinations, and the complete ordered `measurement_to_bit_map` at [lines 303–346](../../../scripts/qi_tuna_source_association.py). Tests mutate missing, duplicated, reordered, Boolean, and conflicting map entries at [test line 339](../../../tests/scripts/test_qi_tuna_source_association.py). The archived false acceptance is repaired.

6. **SOUND — basic production linkage exists.**

   The association test feeds the fake transport’s exact returned body into `decode_associated_complete_bytes` at [lines 260–301](../../../tests/scripts/test_qi_tuna_source_association.py). It also replaces the association module’s imported production `decode_counts` binding with a wrong decoder and requires rejection at [lines 409–427](../../../tests/scripts/test_qi_tuna_source_association.py). This is genuine production-path linkage, although it does not cure the discarded receipt metadata.

## Exact staged SHA-256

| Staged artifact | SHA-256 |
|---|---|
| `scripts/qi_tuna_readback_transport.py` | `246672e6346a555ec67bb54f23e6be47157b357f36c451a6d8649766d2c65a00` |
| `tests/scripts/test_qi_tuna_readback_transport.py` | `8c129177316b555866ea3e1f290b75b6f3dca09adf4ee060c6a5705c5be8434c` |
| `scripts/qi_tuna_source_association.py` | `4abd49b146891fcb3ab374e20bd2dc978025046f7381b191923e315e35ab75be` |
| `tests/scripts/test_qi_tuna_source_association.py` | `09e4d62258703029c7d488148a0b8937d13a04fadad7f2ee3ac71679bc3e485b` |
| Design basis | `420a2f024a077ba40f7ea0d6d2b702b2137fd58de8527a5a55e0080dadea1578` |
| Archived review basis | `d8968e95524d9ab9b09d21db042e8cc996d2ac4725edff05868600dbfa1a2de5` |

The design file has an unstaged privacy sentence; its working-tree hash is `7e121ca55d8b565843961e72e12927843d03502edabb4b17146eac765b4f29a5`. This review used the staged design blob.

The static review ran no tests, network requests, credential reads, provider operations, jobs, uploads, draws, messages, or repository writes. Before-and-after observations recorded the same HEAD, `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, and the same six staged hashes above.

Verdict: the local decoder and fake transport are defensible, and the archived measurement-map defect is fixed. The evidence pipeline remains inadmissible until a receipt-aware layer binds authenticated locators and response envelopes to every decoded provider snapshot and separately establishes the live authentication, clock, account, and provider-response boundaries.

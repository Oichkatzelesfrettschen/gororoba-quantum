# Final review

Launch metadata reports `gpt-daybreak-blue-latest`, high reasoning effort, default tier.

## Findings

- FATAL: none.
- SERIOUS: none.
- SLOPPY: none affecting execution readiness.

## Prior SERIOUS findings

1. **Request-deadline propagation: repaired and remains closed.** The successor client imposes the intrinsic finite deadline on inherited GET, pagination, POST, PATCH, and authenticated retry paths (`scripts/qi_platform_submission_deadline.py:27-55`). Submission retains the account lock through admission and enqueue (`scripts/qi_platform_submission_deadline.py:58-81,155-180,270-287`). The historical `scripts/qi_platform.py` tracked diff remains empty.

2. **Locked-admission evidence consumption: repaired.** The shared validator now requires the dedicated schema, successful admission, empty failures, exact manifest and producer identities, full frozen backend/compiler/topology/gates, enabled status, empty queue, pause clearance, zero-ledger evidence, heartbeat freshness, limits, and strict chronology (`scripts/qi_tuna_destination_one_analysis.py:163-250`).

   The runner consumes that validator before accepting completion (`scripts/qi_tuna_destination_one_run.py:196-268`), while the final analyzer independently consumes it before classification (`scripts/qi_tuna_destination_one_analysis.py:460-504`). The locked receipt digest enters the completion input set and per-job/final provenance (`scripts/qi_tuna_destination_one_analysis.py:481-525`; `scripts/qi_tuna_destination_one_run.py:269-288`). Semantic mutation tests recompute dependent hashes, preventing byte-binding checks from concealing invalid receipt content (`tests/scripts/test_qi_tuna_destination_one_analysis.py:614-722`; `tests/scripts/test_qi_tuna_destination_one_run.py:154-220`).

## Timestamp and collection repair

The successor route consistently uses precise `utc_now().isoformat()` timestamps for admission, locked observation, execution window, submission state, enqueue confirmation, collection, and terminal state. No current successor path calls the whole-second `qi_platform.now()`.

The collector:

- Inherits the finite request deadline for status, results, logs, and paginated transaction reads.
- Records `collected_utc` after those reads with fractional precision.
- Validates manifest, job identity, shots, raw results, histogram, and transactions before publication.
- Compares every retained raw ordered list before writing anything, so a histogram-preserving permutation refuses recollection.
- Preserves existing raw and result bytes when only the new observation timestamp differs.

See `scripts/qi_platform_submission_deadline.py:291-374`. The same-second finish/collection, exact recollection, permutation refusal, and expiry regressions are at `tests/scripts/test_qi_platform_submission_deadline.py:294-349`. The coherent provider/local clock assumption remains explicit and fail-closed (`docs/design/tuna-readout-destination-one-admission.md:59-62`).

## Packet and integration checks

My read-only digest audit found:

- All 14 campaign producer-input hashes match current files.
- All three manifests, circuit sources, and backend snapshots are byte-identical to the predecessor nominal-one cases.
- Each manifest retains one 4096-shot circuit.
- Campaign, decision, written-case, and terms hashes match the supplied values.
- Analyzer/note contract and compiler receipt digests match the campaign.

Exact packet:

- Campaign: `b0bb0ef6497a2a57b9478a9174d786e5b0945dbc3ce4a66042ce4123d3eafd25`
- Decision: `69aa7bbf3408853effa93f0930968cdac7caa7b0d61dd5cd4770c81da24e75f5`
- Written case: `7cb1a4d533eedb07a7a1bcad375f88f59aa828e5e81039c2d7cf5d62228aa059`
- Terms: `625a8a553b4379cc4d7130d1f452dd99b0e2f2d671429a1836a14c68fd36b206`

The execution path performs fresh observation, supplies the locked callback to guarded submission, collects with the successor collector, validates completion, and only then advances (`scripts/qi_tuna_destination_one_run.py:397-473`). Ambiguity, invalidity, or deadline expiry stops without automatic retry.

Eight write-free test functions passed directly. `git diff --check` passed. The pinned Quantum Inspire interpreter lacks pytest, and ambient pytest could not start because the read-only sandbox provides no writable temporary directory. I therefore did not independently rerun the 279-test suite, pinned Ruff/mypy, or full compiler replay.

The existing `destination-one-deadline-repair-verification.json` binds an earlier packet (`docs/evidence/tuna-projector-geometry/destination-one-deadline-repair-verification.json:166-177`). The planned successor final-verification receipt and exact owner-approval receipt are expected pending artifacts, rather than code defects; neither older receipt should qualify the current packet.

## Scientific boundary

The analysis remains a descriptive three-job predictable-response comparison: 12 response contrasts and 12 endpoint contrasts with the accepted `log(48/0.01)` martingale bound. The targets permit adapted shot dependence but do not estimate stationary populations or causal treatment effects (`docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md:3-30`).

Analog scheduling, integration, discrimination, calibration, apparatus memory, and causal destination attribution remain unresolved. Three jobs provide only three intervention units, and the nominal-zero prefix remains retrospective evidence (`docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md:47-53`). Analog schedules or IQ data are therefore interpretation obligations, not prerequisites for this explicitly descriptive acquisition.

## Verdict

**PASS for the exact authorized three-job nominal-one case**, after:

1. recording the existing owner authorization against the exact packet hashes above;
2. retaining the successor final-verification receipt for the current packet; and
3. passing fresh admission at each dispatch.

This verdict covers exactly three serial 4096-shot jobs, a 900-second aggregate execution ceiling, zero expected/allowed credits, 30-second pauses, 60-second admission freshness, and the 7200-second request-initiation horizon. It grants no causal attribution and no additional hardware scope. Additional hardware still requires a new queue-aware case.

Unrun by this review: provider access, credential access, fresh policy/queue/pause/heartbeat/ledger observations, submission, collection, recovery, authentication refresh against the live service, emulator execution, full pytest, pinned Ruff/mypy, and full compiler replay.

DONE
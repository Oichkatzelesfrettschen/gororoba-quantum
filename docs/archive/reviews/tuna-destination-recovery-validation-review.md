The repair concerns provenance validation and reproducibility, not scientific inference. I reviewed the full delta from capture commit `1ba7ba8`, the successor artifact, tests, gate, registry, and documentation.

## Finding

### SERIOUS — Recovery chronology still accepts collection before recovery began

The validator checks two independent chains at [qi_tuna_destination_prefix.py:53](../../../scripts/qi_tuna_destination_prefix.py):

- `stop <= recovery-start <= receipt-complete`
- `job-finish <= collection <= receipt-complete`

It never requires `recovery-start <= collection`.

Consequently, the predicate accepts, for example:

- stop `20:47:55`
- job finish `20:48:00`
- collection `20:49:00`
- recovery start `20:50:00`
- receipt completion `20:51:00`

Collection preceding the recovery intent contradicts the claimed recovery provenance. The existing `chronology` mutation only moves recovery start before the stop at [test_qi_tuna_destination_prefix.py:73](../../../tests/scripts/test_qi_tuna_destination_prefix.py), so it misses this cross-order defect.

Required repair: enforce:

```text
stop <= recovery-start
max(recovery-start, job-finish) <= collection <= receipt-complete
```

Add a regression that places recovery start after `results.json.collected_utc` but before a later receipt-completion timestamp.

The retained run itself has valid chronology:

```text
stop 20:47:55
< recovery start 20:49:19
< job finish 20:51:29.770929
< collection/receipt completion 20:51:40
```

Thus the defect affects validator completeness, not the truth of the current retained receipt.

## Sound repairs

The remaining requested repairs are correctly implemented:

- Recovery intent and receipt schemas, job types, job/case identity, exact-false creation/resume flags, stopped-state digest, completion digest, collected status, and intent/receipt agreement are checked at [qi_tuna_destination_prefix.py:29](../../../scripts/qi_tuna_destination_prefix.py). Positive identity follows transitively because the receipt must equal the third job already admitted by `validate_batch`.
- The execution state must contain exactly the first two completion receipts and identify the third batch as active at [qi_tuna_destination_prefix.py:60](../../../scripts/qi_tuna_destination_prefix.py).
- Every source-readback receipt must have the correct schema, one job object, matching job/file, exact local and stored source digests, exact-true match flag, expected field shapes, content availability, and an observation timestamp after job creation at [qi_tuna_destination_prefix.py:66](../../../scripts/qi_tuna_destination_prefix.py).
- The successor includes the recovery intent, recovery receipt, and all three source-readback hashes at [qi_tuna_destination_prefix.py:157](../../../scripts/qi_tuna_destination_prefix.py).
- The successor’s jobs, counts, contrasts, shot total, execution seconds, primary outcome, scope, and causal status are byte-equivalent as JSON values to the capture artifact.
- The initial artifact remains unchanged from `1ba7ba8`, and its recorded producer digest matches the script bytes at that commit. The frozen analyzer, campaign, mathematical note, and raw acquisition remain unchanged.
- The gate now replays the validation successor at [gates.json:5040](../../../ci/gates.json). The registry binds its `acbd07d9…` digest and all three readback receipts at [research_state.json:2290](../../../docs/state/research_state.json).
- The documentation correctly distinguishes the preserved capture artifact from the validation successor and states that provenance additions do not revise the scientific result at [ordered-response-acquisition.md:56](../../../docs/evidence/tuna-projector-geometry/ordered-response-acquisition.md).

Normal and optimized ambient replays matched the successor. The submit-free retained replay test passed. I did not independently run the 17 temporary-directory cases, pinned tools, combined 97 tests, registry/link/plan checks, or provider operations.

## Verdict

The source-readback portion of the original finding is repaired. The recovery portion is substantially repaired, and the exact retained recovery is coherent, but the missing `recovery-start <= collection` edge prevents full closure of the semantic-validator finding.

The complete campaign outcome remains **implementation route unavailable**. The successor remains post hoc and descriptive, admits no statistical acceptance, leaves causality unresolved, and establishes neither populations nor a physical mechanism. This review grants no acquisition approval.

DONE
The preceding SERIOUS pagination finding closes. The replay-provenance SLOPPY finding closes within its local-only boundary. The historical-snapshot finding remains partially open as one SLOPPY defect. I found zero new FATAL or SERIOUS findings.

## SLOPPY — Historical snapshot validation omits batch reachability and gate capability

[qi_tuna_qx_destination.py](../../../scripts/qi_tuna_qx_destination.py) now validates backend identity, width, shot limit, execution limit, raw-data support, and simulator status. However, the validator ignores:

- `max_jobs_per_batch_job`
- `batchjobs_per_queue_limit`
- the required `X`, `init`, `measure`, and `barrier` gates in `gateset`

The proposal explicitly requires one batch containing three jobs in [tuna-destination-qx-conformance.md](../../../docs/design/tuna-destination-qx-conformance.md). The normal submission path checks the batch limit in [qi_platform.py](../../../scripts/qi_platform.py) and queue limit at [qi_platform.py](../../../scripts/qi_platform.py).

A read-only in-memory mutation produced these false passes:

```text
CONTRADICTORY_SNAPSHOT_ACCEPTED max_jobs_per_batch_job=1 circuits=3
CONTRADICTORY_SNAPSHOT_ACCEPTED batchjobs_per_queue_limit=0 circuits=3
CONTRADICTORY_SNAPSHOT_ACCEPTED gateset=['init', 'measure', 'barrier'] circuits=3
```

The current bound snapshot is internally consistent: it records ten qubits, five jobs per batch, five queued batches, and includes `X`. Therefore the staged manifest remains correct, but the verifier still fails to earn that correctness against relevant snapshot mutations.

The regression at [test_qi_tuna_qx_destination.py](../../../tests/scripts/test_qi_tuna_qx_destination.py) changes `id` and `nqubits` together, allowing the `id` failure to mask missing width validation. It exercises none of the three omitted fields. Separate one-field mutations should cover every static constraint.

## Earlier finding adjudication

- **SERIOUS batch pagination: CLOSED.**
  [capture_readback](../../../scripts/qi_tuna_qx_destination.py) now uses `Client.get()` directly and requires one item, `page=1`, `pages=1`, `total=1`, and a positive page size. `Client.get()` passes those query parameters directly at [qi_platform.py](../../../scripts/qi_platform.py). An in-memory response containing one item but `total=2` was rejected:

  ```text
  INCONSISTENT_BATCH_PAGE_REJECTED backend readback must resolve exactly one batch
  ```

  The regression checks the exact request and contradictory total at [test_qi_tuna_qx_destination.py](../../../tests/scripts/test_qi_tuna_qx_destination.py). It does not independently mutate `page`, `pages`, or `size`, although the implementation rejects those malformed envelopes.

- **SLOPPY historical snapshot validation: PARTIALLY CLOSED.**
  Core identity and resource fields are now checked, but the counterexamples above remain reachable.

- **SLOPPY replay provenance: CLOSED, locally bounded.**
  [build_manifest](../../../scripts/qi_tuna_qx_destination.py) validates timezone-aware ordered timestamps, future timestamps, numeric Python 3.13 versions, exact package versions, boundary text, producer hash, command, and rows. The targeted negative regression passed.
  [qi_tuna_qx_local_replay.py](../../../scripts/qi_tuna_qx_local_replay.py) recomputes parser and one-shot simulator results, ignoring only the necessarily dynamic timestamps during comparison. The QI-required gate at [ci/gates.json](../../../ci/gates.json) reaches the destination, replay producer, QI stack, and platform client through dependency closure. The audit job sets `GOROROBA_QI_REQUIRED=1`, so an unavailable QI stack fails instead of taking the fallback.

## Verification and limits

- All seven `local hash binding list` digests match both staged and working bytes.
- All seven bound paths have zero unstaged differences.
- Exact manifest replay passed.
- Ruff check, Ruff formatting, and mypy passed for both producers and the tests.
- The targeted metadata regression passed.
- `QI_PYTHON` was unset, so the local command took its documented fallback. This review did not execute libqasm or qxelarator and does not claim observed simulator replay.
- Tests requiring temporary-file writes were inspected but not executed under the read-only constraint.
- Local records remain unauthenticated observations. They establish neither provider execution nor provider identity.

The separate QX approval guard, fresh backend/queue/policy admission, and QX-to-Tuna end-to-end policy gap remain open blockers.

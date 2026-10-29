The capacity and gate-capability implementation closes the earlier false acceptances. One SLOPPY regression-coverage gap remains; I found zero current false acceptances.

## SLOPPY — Type and per-gate predicates lack independent regression mutations

[qi_tuna_qx_destination.py](../../../scripts/qi_tuna_qx_destination.py) correctly validates:

- Backend type ID and identifier.
- Minimum three-qubit capacity.
- Exactly 2048 maximum shots and 3600 execution seconds.
- Raw-data support and simulator identity.
- At least three jobs per batch and one batch queue slot.
- A list containing `X`, `init`, `measure`, and `barrier`.

[test_qi_tuna_qx_destination.py](../../../tests/scripts/test_qi_tuna_qx_destination.py) now mutates every field separately. However:

- The sole gate mutation removes `X`. A regression deleting `init`, `measure`, or `barrier` from the required set would escape this test.
- The tests exercise wrong values but not explicit type predicates. For example, removing the type guards could admit `id=true`, `nqubits=3.0`, `max_number_of_shots=2048.0`, `job_execution_time_limit=3600.0`, `max_jobs_per_batch_job=3.0`, or `batchjobs_per_queue_limit=true`.
- A `gateset` object whose keys are the required gates could pass `issubset()` if the list-type guard regressed; the existing missing-`X` list would still reject.

The current implementation rejected all those malformed values in read-only in-memory probes. The gap concerns future regression detection, not present behavior. Separate mutations for each required gate and each essential type guard would close it.

## Sound reachability checks

The frozen sources use only `X`, `init`, `measure`, and `barrier`. They require three qubits, three batch jobs, and 2048 shots per job. The historical snapshot records:

- Backend type ID `1`, identifier `QXsinglenodesimulator`.
- Ten qubits.
- Five jobs per batch and five queued batches.
- 2048 maximum shots and 3600 seconds.
- Raw-data support, simulator status, and all four required gates.

Minimum valid mutations—three qubits, three jobs per batch, one queue slot, and exactly the four required gates—were accepted. Every independently removed resource or gate was rejected.

## Verification limits

- All three `local hash binding list` hashes match both staged and working bytes.
- The bound paths have zero unstaged differences and pass targeted `diff --check`.
- Exact manifest replay, Ruff check/format, mypy, and the checked-in snapshot mutation test passed.
- Read-only probes covered 20 malformed and four minimum-valid snapshots.
- The checks establish historical configuration sufficiency only. They do not authenticate the snapshot or establish current backend status, queue occupancy, fresh admission, approval, or provider reachability.
- No provider, credential, submission, upload, simulator, or filesystem-write path was exercised.

Verdict: the earlier capacity and capability false passes are closed in the implementation. Full test-level closure still needs independent type and per-required-gate mutations.
# Submitted circuit comparison

The [pooled-validation comparison](comparison-pooled-validation.json) covers all 40 jobs in the
[retained-job audit](../../../results/live/qpu-job-retention-audit.json). The collector revalidated and reused the
28 rows of the immutable [original comparison](comparison.json), then retrieved the twelve missing jobs' submitted
inputs through the IBM Runtime read-only job interface. The missing set includes four failed jobs and eight
completed jobs, with 148 circuit items. Every retrieved item equals its expected retained circuit in order.
These observations establish submitted-circuit agreement rather than successful execution of a failed job.

The [service-retrieval comparison](comparison-retained-audit.json) records the actual retrieval time and twelve
retrieved job IDs. The pooled-validation successor preserves those fields and all 40 rows, and records a distinct
offline validation time. The [historical collector text](collector-retained-audit.py.txt) retains the exact source
that produced the service-retrieval comparison; the snapshot is data rather than an active Python module.

The active successor binds the audit, original seed, current collector, predecessor comparison and archived
collector text, plus the direct repository dependencies `ibm_account.py`, `parallel.py` and `live_run.py`. These
named files and the pinned Qiskit/runtime versions bound the replay; the provenance does not claim a complete
transitive import closure. Both earlier comparisons retain their recorded bytes. Gate `core-281` checks the
complete successor and its predecessor chain on the historical `qiskit-2.5` replay runtime.

Replay from the repository root with the interpreter qualified against `ci/requirements-replay.txt`:

```sh
export PYTHON="${REPLAY_PYTHON:?Set REPLAY_PYTHON to the qualified qiskit-2.5 interpreter}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" -B -W error scripts/compare_submitted_circuits.py --check \
  --out docs/evidence/submitted_circuits/comparison-pooled-validation.json
```

QPY reserialization depends on the Qiskit version: Qiskit 2.5.2 reproduces all 28 original rows, while Qiskit 2.6.0
produces different serialized digests. The checker requires the successor's recorded runtime versions; changing
serialization versions requires a separately justified successor rather than replacing the original hashes.

An authorized future read-only extension uses `--write --out NEW_PATH --seed
docs/evidence/submitted_circuits/comparison.json`. The collector validates seed rows before opening the service,
fetches only missing jobs, validates every complete row before publication, and refuses an occupied output path.
The collector creates neither quantum jobs nor circuit uploads. Independent per-job QPY validation runs through
the order-preserving process pool; sequential service retrieval preserves the read-only request order. Tests
compare serial and two-worker results and first-failure ordering.

A source-binding successor uses `--rebind PREVIOUS_V4 --collector-snapshot ARCHIVED_TEXT --out NEW_PATH`. Offline
rebinding validates every retained row, the original seed, the predecessor's source snapshot and runtime, then
preserves retrieval identities while recording the offline operation separately. The writer refuses an occupied
destination. Retained source changes require a new comparison because the successor binds its collector's bytes.

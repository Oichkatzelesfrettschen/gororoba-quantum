# Quantum task artifact retention

The artifact inventory retains the task-owned API investigations, failed routes,
reproducers, gate logs, operator reviews, and analysis scratch that accompanied
the Quandela MCP repair and local photonic/compiler cross-checks. The inventory
uses logical source names so source identities remain separate from host paths.

The [snapshot inventory](snapshot/inventory.json) records original SHA-256 and
size separately from retained sanitized text. Sanitization removes credential
fields, account identifiers, email addresses, and local home/temporary paths.
Sanitized captures are research snapshots, rather than lossless hardware receipts.
The canonical provider acquisition directories retain hardware receipts.

The capture covers the task's operator scratch tree, both embedded scratch tar
archives, Ascella API-capture diagnostics, and the explicitly selected Quandela,
photonic, hypercomplex-library, and simulation qualification files. Active log
captures describe a bounded observation, rather than completed qualification.
Completed qualification outputs require a new immutable capture.

The [historical worktree scratch inventory](historical-worktree-scratch/inventory.json)
covers ignored research in six task-owned, already-merged worktrees: library
import coverage, numerical-model pytest regressions, campaign submission
deadlines, rejected-request recovery, proposal source bindings, and quaternion
dephasing. The inventory retains 25 source identities and 19 unique captures.
Regenerable pytest fixture repositories receive a metadata disposition rather
than publication of their generated Git objects and sockets.

Byte-identical tracked artifacts link to their repository path and original Git
identity. The verifier checks the checkout bytes, so a shallow offline checkout
needs no historical Git object. A future source change must retain the prior
bytes or deliberately replace the reference with a retained capture.

Build environments and caches retain relative-path/size inventory digests,
file counts, and sizes rather than installed binaries. Those digests describe
inventory metadata, rather than content. Third-party reading copies and the
downloaded dashboard vendor bundle retain hashes rather than republished bytes.
Synchronization locks receive transient dispositions. Archive members are read
without extraction and retain individual identities.

The original snapshot's tracked-byte deduplication overwrote some external-copy
and lock classifications. The [disposition correction map](snapshot/disposition-corrections.json)
supersedes exactly those classifications while preserving the checksum-bound
original inventory bytes. The verifier derives the required correction domain
from every historical row and rejects missing, additional, or incorrect entries.
New captures preserve non-content classifications before tracked deduplication.
The expanded plaintext sanitizer covers every declared private field; all
retained text also passes the expanded sanitizer's idempotence check.

PR #352 owns MCP/API repairs. PR #368 owns the approved Ascella plan and waiting
evidence. PR #369 owns local simulator outputs and the full-precision cQASM
exporter. Other agents' hardware jobs, credentials, unrelated ignored research,
and shared test-fixture trees remain outside the capture boundary. The capture
operation reads sources and writes a new destination; cleanup follows merger and
separate process-use checks.

Replay from the repository root:

```sh
export PYTHON="${PYTHON:-python3}"
export PYTHONPATH=gororoba_quantum:scripts
"$PYTHON" scripts/quantum_artifact_retention.py \
  docs/evidence/quantum-task-artifact-retention/snapshot --check
"$PYTHON" -m pytest -q tests/scripts/test_quantum_artifact_retention.py
```

The capture CLI accepts repeated `--source logical-name=PATH` arguments and a
fresh destination. `--tracked-root .` enables repository-byte deduplication.
The capture refuses existing destinations, unclassified binary inputs, unsafe
archive members, and oversized inputs.

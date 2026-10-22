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

The [broad validation and orchestration inventory](broad-validation-and-orchestration/inventory.json)
adds 32 source identities and 25 captures. The completed frozen-source run at
`46b50f4625641ca8dd9df0baf492e48ee7256508` records 535 passing gates and one
failure across 536 gates in 7362.42 seconds. The failing lint/type gate
`core-000` exposed an unused type-ignore suppression, repaired in `fd65f74`.
That historical receipt is distinct from the integrated-head qualification at
`278d415`, which remained running when the capture was made. Orchestration
snapshots describe bounded observations of active waiting processes. The capture
also retains the bytecode before/after digest observation and checkout-line-ending
probe inputs.

The [verifier regression and provenance checks](verifier-regression-and-provenance-checks/inventory.json)
retain two failing regression reproductions, the subsequent 53-test passing
result, the passing retention-gate timing receipt, and local simulator
provenance-fix gate timings. These completed focused checks differ from full
integrated qualification receipts.

The [integrated MCP qualification inventory](integrated-mcp-qualification/inventory.json)
retains the completed exact-head run at
`278d41587c4e78a6406023536b5b4b5d77bca0aa`: 391 passing gates, zero failures,
and 145 unchanged-ledger skips across 536 gates. The inventory includes the
validation log, ledger, timing receipt, and launcher/orchestration evidence.
Sanitized launcher snapshots describe the recorded execution environment;
their process-specific environment sources are historical rather than portable
replay entry points.

The [qualification summary parser recovery](qualification-summary-parser-recovery/inventory.json)
retains the corrected follow-on launchers and their recovery receipt. The
original parsers accepted summaries without skips and rejected or ignored the
successful summary containing 145 skips. The correction accepts the optional
skip count. Python 3.14's `sys.remote_exec` launched replacement helpers from
the original helper's loaded environment. Linux's same-user tracing restriction
required scoped existing sudo authority; the operation left the tracing policy
unchanged and wrote a receipt containing process IDs and script/log paths,
rather than environment contents. The recovered launch observations show the
simulation qualification starting and retention qualification waiting for an
explicit clean-head request; those observations are bounded active-process
snapshots rather than completed qualification receipts.

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
The plaintext sanitizer normalizes casing and separators for every declared
private field and consumes escaped quotes inside quoted values. All retained
text also passes the sanitizer's idempotence check. Verification rejects
capture-only options rather than silently ignoring their requested behavior.

PR #352 owns MCP/API repairs. PR #368 owns the approved Ascella plan and waiting
evidence. PR #369 owns local simulator outputs and the full-precision cQASM
exporter. Other agents' hardware jobs, credentials, unrelated ignored research,
and shared test-fixture trees remain outside the capture boundary. The capture
operation reads sources and writes a new destination; cleanup follows merger and
separate process-use checks.

Replay from the repository root:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B scripts/quantum_artifact_retention.py \
  docs/evidence/quantum-task-artifact-retention --check-tree
"$PYTHON" -B -m pytest -q tests/scripts/test_quantum_artifact_retention.py
```

The capture CLI accepts repeated `--source logical-name=PATH` arguments and a
fresh destination. `--tracked-root .` enables repository-byte deduplication.
The capture refuses existing destinations, unclassified binary inputs, unsafe
archive members, and oversized inputs.
Tree verification discovers every inventory, rejects orphan checksums or capture
directories, and applies the verifier to each discovered snapshot. A later
immutable capture therefore enters the same gate without a directory-list edit.

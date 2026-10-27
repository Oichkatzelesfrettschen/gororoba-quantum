# Sequential-projector QX conformance

The approved three-circuit QX batch completed on 27 October 2026 with 2048 shots per circuit.
All 18 discrepancy checks frozen in the [acquisition design](../../design/tuna-projector-geometry.md)
pass. The remote emulator reproduces the expected geometry contrast, cancelling-rotation mutation,
and signed moment within those tolerances. Tuna behavior and early classical-bit retention remain
unmeasured.

## Admission and retained execution

The [live terms and account preflight](approved-qx-preflight.json) records free noncommercial use,
an empty transaction ledger, and an empty QX account queue. The [backend observation](approved-qx-backend.json)
records idle QX, a ten-qubit capacity, 2048 maximum shots per job, five circuits per batch,
five queued batches, and a 3600-second per-job execution limit. The submitted batch used nine qubits,
three circuits and 2048 shots per circuit. The FAQ's three-job hardware queue restriction does not
classify QX as hardware; the batch also contains only three jobs.

The [submission receipt](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/submission.json)
binds the user's verbatim approval and manifest digest to batch 895296 and jobs 1615796, 1615797 and
1615798. The guarded submit path observed an idle backend and zero account-queued batches before
enqueueing once. The [collection](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/results.json)
reports completed status and all requested shots for each job. The raw directory retains the shot order.
The run also preserves the design text that supplied the pre-acquisition screen.

| Circuit | Job | Shots | Provider execution seconds |
|---|---:|---:|---:|
| Normal Z endpoint | 1615796 | 2048 | 0.418324 |
| Cancelling-rotation Z mutation | 1615797 | 2048 | 0.096957 |
| Normal X endpoint | 1615798 | 2048 | 0.739070 |
| Total | | 6144 | 1.254351 |

The total lies within the written historical estimate of 0.09 to 31.2 seconds. Execution time excludes
queue and API overhead. The collection contains zero transaction rows; the refreshed account
[usage ledger](../quantum_inspire/usage.json) also records zero transaction change.

## Frozen screen and observed moments

The nine herald frequencies lie between 0.489746 and 0.517090, within 0.05 of 1/2.
The following six joint frequencies use tolerance 0.05; the three signed means use tolerance 0.10.
Each numerator is evaluated against 2048 shots without conditioning on herald success.

| Endpoint | Angle | Observed numerator / 2048 | Ideal mean |
|---|---:|---:|---:|
| Normal joint Z | 0 degrees | 1009 / 2048 = 0.492676 | 0.5 |
| Normal joint Z | 45 degrees | 757 / 2048 = 0.369629 | 0.375 |
| Normal joint Z | 90 degrees | 524 / 2048 = 0.255859 | 0.25 |
| Mutation joint Z | 0 degrees | 1039 / 2048 = 0.507324 | 0.5 |
| Mutation joint Z | 45 degrees | 1009 / 2048 = 0.492676 | 0.5 |
| Mutation joint Z | 90 degrees | 1024 / 2048 = 0.5 | 0.5 |
| Normal signed X | 0 degrees | 57 / 2048 = 0.027832 | 0 |
| Normal signed X | 45 degrees | 513 / 2048 = 0.250488 | 0.25 |
| Normal signed X | 90 degrees | 14 / 2048 = 0.006836 | 0 |

The [integer-count replay](../../../scripts/qi_projector_conformance.py) compares probability-count
differences times 20, and signed-sum differences times 10, against 2048. Its
[retained verdict](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/conformance.json)
binds raw data, collection, submission, manifest and analyzer identities. Gate
`core-qi-projector-conformance` re-derives that float-free JSON exactly:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/qi_projector_conformance.py --check \
  results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/conformance.json
```

These samples support remote circuit and register conformance, not an exact mathematical proof.
QX returns terminal qubit outcomes and cannot validate Tuna's separate early-history bit register.
The calibration datasource outage remains a hardware limitation. The Tuna qualification batch has recorded
user authorization and requires completed review and fresh hardware admission checks.

The supplemental [joint outcome audit](../../../results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/joint-law-audit.json)
reconstructs all 512 terminal outcomes from independent analytic local laws. All observed
outcomes have positive ideal support. Full-histogram total variation distances are
0.081351602058 (geometry Z), 0.016601562500 (mutation Z), and 0.098872232426
(geometry X). Adjacent repeats and contiguous block counts remain descriptive diagnostics;
they establish neither shot independence nor hardware behavior. Replay with
`"$PYTHON" scripts/qi_projector_distribution_audit.py --check
results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/joint-law-audit.json`.
The 18 preregistered conformance checks retain their original decision rule and bytes.

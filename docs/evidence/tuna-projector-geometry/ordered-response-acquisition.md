# Tuna destination response: deadline and acquired nominal-zero prefix

The owner approved the [ordered response case](../../design/tuna-readout-ordered-response-admission.md)
for six serial jobs of 4096 shots, with a 3600-second request-initiation window.
The executor stopped at **20:47:55 UTC on 27 October 2026** after three submissions.
All three nominal-one jobs remained undispatched. The
[frozen analysis](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/analysis.json)
returns **implementation route unavailable** because required acquisition artifacts
are absent. The complete six-job comparison establishes neither equivalence nor departure.

The [owner approval](ordered-response-owner-approval.json),
[run approval packet](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/approval.json),
and [sequence plan](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/sequence-plan.json)
bind campaign `53eb49080573b876545b5301b195ee06127625653266fbb64b98a60823e07a76`.
The approved analyzer, mathematical note and circuit sources retain their bytes.

## Acquisitions and recovery

| Nominal-zero job | Provider job / batch | Shots | Reported execution seconds | Creation to `queued_at` |
|---|---|---:|---:|---:|
| Baseline before | 1618109 / 895781 | 4096 | 5.176820 | 17 min 5.678760 s |
| Rotated early destinations | 1618345 / 895833 | 4096 | 4.710931 | 16 min 27.075253 s |
| Baseline after | 1618590 / 895884 | 4096 | 4.469031 | 27 min 57.501464 s |

The three acquisitions retain **12,288 ordered width-20 shots**,
**14.356782 reported execution seconds**, and zero recorded transaction charges.
The intervals use provider timestamp fields and do not measure pulse starts or
analog settling times. Each successor's creation followed its predecessor's
completion plus the required 30 seconds. The measured gaps were 48.625765 and
45.583803 seconds.

The [automatic execution state](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/execution-state.json)
preserves the timeout and its two automatic collections. The third submitted job
completed at 20:51:29.770929 UTC. A separate
[read-only recovery receipt](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/read-only-recovery-receipt.json)
records collection at 20:51:40 UTC and binds the third completion receipt.
Recovery retrieved the existing job and left the executor stopped. The three
nominal-one job slots have neither submission receipts nor execution intents.

Every submitted job has a completion receipt checking its source, manifest,
submission, raw shots, histogram, timing, identities and zero charges. Each also
has a `stored-source-observation.json`: authenticated file reads match the
submitted cQASM bytes. The file API reports `compile_stage=none` and empty compile
properties; those fields do not expose the served pulse or integration program.

The [initial queue observation](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/provider-queue-observation.json)
reported 48 queued entries, 505 seconds average wait and 956 seconds maximum wait
at 19:55 UTC. The
[later observation](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/baseline-after-queue-observation.json)
reported 53 entries, 944 seconds average and 1680 seconds maximum at 20:45 UTC,
while Tuna remained enabled/executing with a fresh heartbeat. These are aggregate
provider statistics rather than a forecast for an individual job. The measured
waits exhausted the approved local window; the reported quantum execution times
remained within their ceilings.

## Descriptive prefix, excluded from the complete-case decision

The [validated prefix description](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/nominal-zero-prefix-receipt-validation.json)
uses the frozen decoder and per-job operational validators. The separate
[replay](../../../scripts/qi_tuna_destination_prefix.py) preserves the primary
refusal and emits counts and exact empirical contrast numerators. It supplies
neither an acceptance decision nor new confidence intervals for the truncated case.
All counts below have denominator 4096, and the columns follow actual execution order.

The [initial description](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/nominal-zero-prefix-descriptive.json)
retains its bytes and its producer version in capture commit `1ba7ba8`.
The validation successor adds semantic checks of recovery schema, job identity,
stopped-state and completion digests, read-only flags, chronology and all three
stored-source observations. Its counts, job tables and primary refusal are identical
to the initial description; the added provenance does not revise the scientific result.

| Physical qubit | Early-one counts before / rotated / after | Terminal-one counts before / rotated / after | Maximum absolute empirical joint-cell contrast |
|---|---|---|---:|
| 4 | 1687 / 1699 / 1664 | 43 / 44 / 66 | 0.0052490234375 |
| 11 | 4031 / 4018 / 4019 | 99 / 93 / 91 | 0.001708984375 |
| 6 | 1442 / 3419 / 1449 | 938 / 2525 / 969 | 0.43896484375 |

The empirical contrast is the rotated frequency minus the arithmetic mean of the
two baseline frequencies. For qubit 6, the four early/final cells, ordered
`00,01,10,11` with the early label first, have counts:

- Before: `2029,625,1129,313`.
- Rotated: `238,439,1333,2086`.
- After: `2043,604,1084,365`.

The maximum absolute before/after cell difference is 0.0126953125. The rotated
table differs strongly from those empirical endpoints. The early and terminal
one-frequency contrasts are 0.4818115234375 and 0.3836669921875, respectively.
The terminal destination remains bit 6 in all three programs.

A transformation confined to the already stored early labels leaves a fixed
dataset's terminal marginal unchanged. Such a relabeling cannot remove the
observed terminal-count difference. The observation does not isolate why the
different jobs produced different responses: broader reconstruction changes,
served scheduling/settings, physical context, calibration changes, apparatus
memory and a transient coinciding with the rotated job remain alternatives.
The changed destinations cover all three ancillas, so the case also leaves
cross-channel effects unidentified. Binary labels are not independently measured
excited-state populations.

The prefix is posthoc descriptive evidence. Its apparent bracketing pattern does
not override the absent nominal-one acquisitions, the frozen stopping rule or the
whole-case refusal. The original failed projector qualification remains refused.

## Resolution requirements

The [unsent upstream report](../../notes/quantum_inspire/upstream-readout-report.md)
provides the official contact routes. A provider investigation can use jobs
1618109, 1618345 and 1618590 to request served compiler/configuration identities,
acquisition-index-to-bit maps, per-qubit thresholds/integration windows, schedule
fingerprints and calibration/history records spanning 20:05–20:51 UTC. Retained
IQ and reconstruction replay would discriminate more directly than another
unqualified interpretation of binary labels.

A future acquisition needs its own written case and approval. Its request window
must account for measured provider waits as well as shot execution and pauses.
A longer bounded window or independently preregistered preparation-specific cases
can address that operational constraint. Randomized or counterbalanced job-level
assignments still need qualified uncertainty and carryover controls to address
causal attribution. The incomplete case cannot be silently continued or relabeled
as a completed six-job test.

The [ledger revalidation](qualification-ledger-revalidation.json) compares the
refreshed account snapshot against the preceding committed snapshot: all 426
previous job rows remain identical and the three added rows belong to this case.
Historical qualification completion receipts cite that immutable scoped comparison
instead of binding their old result to every subsequent account-total change.

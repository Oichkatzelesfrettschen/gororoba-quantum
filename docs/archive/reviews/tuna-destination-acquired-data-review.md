The artifact is an incomplete six-job acquisition with three retained nominal-zero jobs, plus a post hoc descriptive replay. The relevant fields are statistical inference, evidence provenance, and guarded hardware operations. I reviewed every retained acquisition artifact and both new Python files.

## Finding

### SLOPPY — The prefix replay does not fully validate the recovery and source-readback evidence it cites

The replay requires `read-only-recovery-receipt.json`, but it merely records that file’s digest at [qi_tuna_destination_prefix.py:81](../../../scripts/qi_tuna_destination_prefix.py). It never validates:

- recovery schema, job and case identity;
- the stopped execution-state digest;
- the third completion-receipt digest;
- `provider_resource_creation_authorized=false`;
- `automatic_executor_resumed=false`;
- recovery chronology.

The replay also ignores all three `stored-source-observation.json` receipts. The tests cover an exact replay, missing completion receipt, and reordered shots, but neither malformed recovery semantics nor source-readback tampering at [test_qi_tuna_destination_prefix.py:13](../../../tests/scripts/test_qi_tuna_destination_prefix.py).

This defect does not invalidate the retained data: my independent audit confirmed every current recovery field and source-readback digest. The defect limits what the replay proves automatically. A durable repair should validate those receipts semantically, include their hashes in the output provenance, and add mutation tests.

I found no serious or fatal defect in the acquired evidence.

## Primary result

The authoritative campaign outcome remains **implementation route unavailable**. The frozen analyzer records the absent required artifacts, prohibits physical continuation, and refuses retry at [analysis.json:12](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/analysis.json).

The post hoc prefix replay does not change that decision. It explicitly records:

- `primary_case_outcome = implementation route unavailable`;
- `statistical_acceptance_admitted = false`;
- causal attribution unresolved;
- scope limited to a descriptive nominal-zero prefix.

Those limits appear in [nominal-zero-prefix-descriptive.json:1259](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/nominal-zero-prefix-descriptive.json). The acquisition note preserves the same boundary at [ordered-response-acquisition.md:56](../../../docs/evidence/tuna-projector-geometry/ordered-response-acquisition.md).

The incomplete campaign establishes neither the frozen equivalence endpoint nor the frozen departure alternative.

## Evidence-chain audit

All checked file, identity, chronology, and count validations passed:

- The approval, written case, decision, terms, sequence plan, analyzer, mathematical note, six manifests, and submitted source digests match their frozen bindings.
- Exactly three submission receipts exist, all for the nominal-zero prefix. The nominal-one directories contain prepared assets but lack admission, intent, submission, collection, and completion receipts.
- The three jobs contain 4,096 ordered width-20 raw strings each. Every raw histogram exactly matches its retained result histogram.
- Jobs `1618109`, `1618345`, and `1618590` have distinct batch identities, complete status, raw-data enablement, exact shot counts, and zero recorded transactions.
- The reported execution times sum exactly to `14.356782` seconds.
- Every admission preceded job creation by less than 11 seconds. The inter-job creation gaps after predecessor completion were `48.625765` and `45.583803` seconds, both exceeding the required 30 seconds.
- The stopped execution state contains exactly the first two automatic completions and names the third batch as active at the deadline at [execution-state.json:3](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/execution-state.json).
- The recovery receipt’s stopped-state digest matches the unchanged `execution-state.json`; its job identity is `1618590`; its completion digest matches the third completion receipt; and both resource-creation and executor-resumption flags are false at [read-only-recovery-receipt.json:2](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/read-only-recovery-receipt.json).
- Job `1618590` was created before the deadline, completed at `20:51:29.770929Z`, and was collected at `20:51:40Z`. Recovery therefore retrieved an existing approved identity rather than extending the acquisition.
- All three source-readback receipts report matching local and stored source digests. They appropriately disclaim any knowledge of served pulses, integration, or reconstruction at [stored-source-observation.json:2](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/prepared-zero-baseline-after/stored-source-observation.json).

“Zero charges” means zero transaction rows in the retained collections. It does not prove that a delayed provider charge can never appear.

## Independent numerical replay

Direct decoding of all 12,288 raw strings reproduced the retained counts:

| Qubit | Early-one before / rotated / after | Terminal-one before / rotated / after | Maximum absolute joint-cell contrast |
|---|---:|---:|---:|
| 4 | 1687 / 1699 / 1664 | 43 / 44 / 66 | 0.0052490234375 |
| 11 | 4031 / 4018 / 4019 | 99 / 93 / 91 | 0.001708984375 |
| 6 | 1442 / 3419 / 1449 | 938 / 2525 / 969 | 0.43896484375 |

For qubit 6, the independently recovered joint counts were:

- Before: `2029,625,1129,313`
- Rotated: `238,439,1333,2086`
- After: `2043,604,1084,365`

The largest endpoint difference is `52/4096 = 0.0126953125`. The maximum rotated-minus-pooled-baseline joint-cell contrast is `3596/8192 = 0.43896484375`. The terminal-one contrast is `0.3836669921875`.

The source comparison confirms that only early destinations cycle from `17,18,19` to `19,17,18`; every program retains `b[0:16] = measure q` for terminal readout at [baseline-before.cq:9](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/prepared-zero-baseline-before/baseline-before.cq) and [rotated-destinations.cq:9](../../../results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response/prepared-zero-rotated-destinations/rotated-destinations.cq).

## Physical interpretation

The qubit-6 difference is a real feature of the retained decoded strings. Relabeling only the already stored early bits cannot change the terminal bit-6 marginal in those same strings. That observation rejects a correction consisting solely of permuting the three stored early labels.

The observation does not identify a destination effect. The three arms are also three different jobs at three different times, with long and unequal queue delays. The design has one rotated job rather than randomized or replicated job-level assignments. Consequently:

- a synchronized transient remains viable;
- broader full-string reconstruction or bit-assignment changes remain viable;
- served scheduling, pulse, integration, threshold, or context changes remain unmeasured;
- calibration drift and apparatus memory remain viable;
- simultaneous rotation of all three early destinations leaves cross-channel effects confounded;
- binary labels remain readout classifications rather than independently measured physical populations.

The close bracketing endpoints make the qubit-6 pattern diagnostically interesting, but two endpoints do not observe the intervening trajectory. Treating 4,096 shots as 4,096 independently assigned hardware interventions would be statistical theatre: the intervention unit was the job.

## Useful next discriminators

The retained data can support additional explicitly post hoc falsification of simple decoder hypotheses, including testing candidate whole-string permutations against every terminal marginal and cross-qubit joint table. Such analysis still cannot establish mechanism.

The most useful provider-side retrospective evidence for these exact job IDs would be:

- served compiler/configuration and schedule fingerprints;
- acquisition-index-to-classical-bit maps;
- retained IQ or integration outputs;
- thresholds, integration windows, and assignment configuration;
- calibration and apparatus-history records spanning the three executions.

A future acquisition could use one-destination-at-a-time mutations, counterbalanced or randomized job-level ordering, repeated blocks, and bracketing readout calibration. Every such acquisition requires a new written case and separate approval; this review grants neither.

## Tested and unrun scope

I performed:

- strict JSON parsing of all 48 run JSON files;
- independent hash, approval, admission, identity, timing, raw/histogram, completion, recovery, and source-receipt checks;
- independent raw-string decoding and arithmetic;
- exact frozen-analyzer replay, which matched and returned its expected nonzero unavailable status;
- exact prefix replay;
- the submit-free retained-prefix test, which passed under ambient Python 3.14.8.

I did not run:

- provider or network observations;
- submission, collection, reconciliation, cancellation, uploads, or messages;
- the two tests requiring writable temporary directories;
- pinned Python 3.14.7, pinned Ruff, pinned mypy 2.4.0, or compiler-runtime gates;
- stochastic simulation, resampling, or new statistical inference;
- any new acquisition.

Verdict: the three acquired nominal-zero jobs form a coherent and useful descriptive anomaly record. The frozen six-job campaign remains incomplete and statistically undecided. Causal destination attribution and physical-mechanism identification remain unresolved.

DONE
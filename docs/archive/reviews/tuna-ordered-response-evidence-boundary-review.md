Review scope: the ordered destination-response successor spans statistical inference, reproducible evidence validation, and guarded hardware operations. I reviewed the complete new generator, runner, analyzer, tests, proposal bundle, decision/admission records, and their direct `qi_platform.py` dependencies. I made no provider calls or repository changes.

## Findings

### SERIOUS — The analyzer can certify a substantive outcome from an operationally incomplete, schema-less run

The frozen analyzer validates selected contents of `submission.json` and `results.json`, but it does not validate their schemas and never requires the run-level approval record or the per-job admission, execution-intent, and completion-admission receipts. See [qi_tuna_readout_destination_analysis.py:138](../../../scripts/qi_tuna_readout_destination_analysis.py) and [qi_tuna_readout_destination_analysis.py:290](../../../scripts/qi_tuna_readout_destination_analysis.py).

The focused test fixture demonstrates the gap rather than merely leaving it hypothetical:

- It writes schema-less submission and collection objects at [test_qi_tuna_readout_destination_analysis.py:40](../../../tests/scripts/test_qi_tuna_readout_destination_analysis.py).
- It creates neither `approval.json` nor any `admission.json`, `execution-intent.json`, or `completion-admission.json`.
- The analyzer nevertheless returns `objective established within scope` at [test_qi_tuna_readout_destination_analysis.py:106](../../../tests/scripts/test_qi_tuna_readout_destination_analysis.py).

That contradicts the claimed fail-closed boundary for absent or malformed required acquisition artifacts in [tuna-readout-ordered-response-admission.md:77](../../../docs/design/tuna-readout-ordered-response-admission.md) and the decision record’s `protocol inadmissible` contract at [readout-ordered-response-decision.json:41](../../../docs/evidence/tuna-projector-geometry/readout-ordered-response-decision.json).

The live executor itself does create and validate these artifacts, so this defect does not let its normal execution loop submit a seventh job or bypass fresh admission. It does mean the bound final analyzer is not an end-to-end campaign-conformance checker and can launder an incomplete run into a favorable descriptive verdict.

Required fix: either:

- make the analyzer validate exact submission and collection schemas plus the bound approval, fresh admission, execution-intent, and completion-admission chain for every batch; or
- split the scientific classifier from a mandatory operational-conformance wrapper, with the published terminal outcome available only after both pass.

The regression suite should explicitly show missing or malformed operational receipts producing `implementation route unavailable` or `protocol inadmissible`.

### SERIOUS — Malformed numeric fields receive inconsistent acceptance

The live completion validator requires transaction changes to be exact integers at [qi_tuna_destination_sequential_run.py:226](../../../scripts/qi_tuna_destination_sequential_run.py), while the final analyzer converts arbitrary JSON values using `Decimal(str(...))` at [qi_tuna_readout_destination_analysis.py:174](../../../scripts/qi_tuna_readout_destination_analysis.py) and [qi_tuna_readout_destination_analysis.py:177](../../../scripts/qi_tuna_readout_destination_analysis.py). Consequently, strings such as `"0"` or `"5"` can satisfy analyzer checks despite violating the documented API field types.

This is another route by which “malformed artifact” does not reliably mean inadmissible. Apply one shared validator: finite JSON number excluding Boolean for execution time, and exact integer zero for transaction changes.

### SLOPPY — The 3600-second deadline can terminate automatic collection, not merely further dispatch

The design describes the deadline as stopping further dispatch while an already dispatched identity still requires collection or explicit cancellation authority at [tuna-readout-ordered-response-admission.md:54](../../../docs/design/tuna-readout-ordered-response-admission.md). The runner passes that same campaign deadline into collection at [qi_tuna_destination_sequential_run.py:346](../../../scripts/qi_tuna_destination_sequential_run.py), and `qi_platform.collect` uses it to stop polling and result retrieval at [qi_platform.py:1113](../../../scripts/qi_platform.py).

The dispatched job remains preserved and read-only recovery remains available, so this does not duplicate work. The documentation should state plainly that the automatic runner can stop before collection and require manual reconciliation/collection after the campaign deadline.

## Sound portions

- The martingale derivation is correct for bounded adapted indicators with fixed weights. Independent recomputation gave:

  - \(r_D=0.0409754677912993\ldots\), conservatively stored as `0.040975467792`.
  - \(r_R=0.0473143947189549\ldots\), conservatively stored as `0.047314394719`.
  - The 48 two-sided contrasts yield the stated familywise bound of 0.01.
  - The three reported separation values, `0.018049064416`, `0.181950935584`, and `0.005371210562`, are arithmetically correct.

- The maximally dependent example is correct: after the first common Bernoulli outcome becomes known, the predictable average is \((p+(n-1)Z)/n\). The note honestly explains why a narrow predictable-response interval does not create 4096 independent interventions.

- The baseline screen is appropriately limited. It checks the two endpoint predictable averages and explicitly leaves a transient during the rotated job unidentified.

- The five outcomes have coherent boundaries: baseline and equivalence admission are closed; departure is strict; overlap remains inconclusive; missing evidence and malformed evidence have distinct labels in the intended contract.

- Source and decoder bindings are strong. All six source/compiled pairs had identical normalized instruction streams, and the rotated circuits change only early destinations `17,18,19` to `19,17,18`. The inverse bit decoding in [qi_tuna_readout_destination_analysis.py:120](../../../scripts/qi_tuna_readout_destination_analysis.py) matches the frozen maps.

- Campaign hashes currently agree across the written case, decision, admission, analyzer, mathematical note, compiler receipt, runner, six manifests, and six source files. The campaign contains exactly six jobs and 24,576 requested shots.

- The execution path enforces the important operational order:

  1. collect and validate the preceding job;
  2. wait for the account-wide pause;
  3. replay the fixed proposal;
  4. obtain fresh terms, structure, heartbeat, queue, ledger, and pause observations;
  5. enforce the 60-second admission age;
  6. submit under the account lock with the exact `expected_cases_sha256`;
  7. stop on ambiguity, failure, charge, partial collection, or identity conflict.

- The retained live observation matches its claims: Tuna-17 was enabled/executing, the heartbeat age was 9.32 seconds, the account queue and pause were zero, the limit was `300.0` seconds per job, and the ledger had zero transaction rows. The observation is timestamped evidence, not current state; the runner correctly repeats admission before every dispatch.

- The zero-credit case has substantial historical support: the retained account snapshot covers 426 jobs, 7,788,544 completed shots, 4963.250562 reported execution seconds, and zero transaction rows. Nevertheless, zero cost remains a terms-based expectation plus a post-collection check, not a provider-side spending cap. A delayed or unexpected first charge can only stop later jobs.

## Verification performed

- Six deterministic tests not requiring writable temporary storage passed.
- The other 26 focused tests were read in full. The complete suite could not start because the read-only environment provided no writable temporary directory.
- Both staged and unstaged `git diff --check` passed.
- Markdown-link validation passed for 699 files.
- The plan tracker passed for 110 records.
- Ambient Ruff checks passed, but the installed Ruff version was 0.14.11 rather than the pinned 0.17.1.
- Ambient mypy 1.19.1 reported a `str-bytes-safe` warning in the predecessor generator at [qi_tuna_readout_mapping_cases.py:59](../../../scripts/qi_tuna_readout_mapping_cases.py). The repository pins mypy 2.4.0, so this is not a pinned-gate result.
- Exact generator/compiler replay was attempted but remained unrun because the system interpreter lacks `opensquirrel`. The retained compiler receipt was inspected, and all six retained source/compiled normalized streams compared equal locally.
- Provider execution, live refresh, submission, collection, full pinned static gates, and tests requiring `tmp_path` were unrun.

## Verdicts

1. **Offline correctness: HOLD.** The martingale mathematics, arithmetic, decoder, classification logic, and exact source bindings are sound. The frozen analyzer’s evidence boundary is not: it accepts schema-less and operationally incomplete campaigns. Fix that before treating its output as campaign conformance.

2. **Exact-case approval readiness: HOLD.** The six-job runner is correctly bounded to one 4096-shot circuit per batch, six batches total, zero expected credits, and digest-guarded serial submission. The packet is close, but the bound analyzer must enforce—or be wrapped by—its claimed operational evidence chain, followed by regeneration of affected hashes and a complete pinned verification run. The existing records explicitly state `execution_authorized=false`; this review grants no approval.

3. **Causal-inference limits: NOT ADMITTED, by design.** Even after the validator fix, the campaign can establish only selected per-qubit early/final marginal predictable-response equivalence or departure along one fixed A–B–A history. It cannot attribute a difference to classical destinations, exclude a synchronized transient, establish stationary detector behavior, test the full cross-ancilla joint law, or identify pulse scheduling, IQ reconstruction, assignment, carryover, or a physical mechanism. Randomized or counterbalanced job-level assignments and provider-side schedule/acquisition provenance remain necessary for causal attribution.

DONE
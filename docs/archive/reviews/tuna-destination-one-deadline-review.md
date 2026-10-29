# Adversarial review: nominal-one Tuna destination case

Model/effort: launch and current session metadata report `gpt-daybreak-blue-latest`, reasoning effort `high`.

## Findings

### FATAL

None found.

### SERIOUS — HOLD: submission deadline is not propagated across the resource-creation chain

The runner calculates the minimum of the 60-second admission deadline and the 7200-second campaign horizon, then passes that deadline into `qi_platform.submit` at `scripts/qi_tuna_destination_one_run.py:362-379`.

The platform helper enforces that deadline for the initial project request at `scripts/qi_platform.py:948-965`, but the remaining provider writes omit it:

- Batch creation: `scripts/qi_platform.py:985`
- Algorithm creation: `scripts/qi_platform.py:989-992`
- Commit creation: `scripts/qi_platform.py:993`
- File upload: `scripts/qi_platform.py:994-1004`
- Job creation: `scripts/qi_platform.py:1005-1013`
- Batch enqueue: `scripts/qi_platform.py:1036-1039`

`Client.post` supports `execution_deadline`, but those calls do not supply it (`scripts/qi_platform.py:415-416`). `Client.patch` does not accept a deadline at all (`scripts/qi_platform.py:418-419`).

Concrete reachable execution:

1. Admission begins at time A.
2. The guarded project POST starts at A+59 seconds and therefore passes.
3. The project response arrives at A+61.
4. Batch, file, job, and enqueue requests then start without a deadline.
5. The provider job is created after the documented 60-second admission boundary.

The same defect permits later submission requests to begin after the 7200-second campaign horizon when project creation began just before that horizon. The eventual completion checks detect stale creation at `scripts/qi_tuna_destination_one_run.py:238-254` and `scripts/qi_tuna_destination_one_analysis.py:177-193`, but post-acquisition invalidation cannot undo provider writes made outside the admission contract.

The existing regression exercises only expiry while waiting for the account lock (`tests/scripts/test_qi_tuna_destination_one_run.py:292-309`). It does not advance the clock between project, batch, job, and enqueue calls.

Required repair:

- Propagate `execution_deadline` through every backend, queue, language, POST, and enqueue request in `_submit`.
- Add an optional deadline to `Client.patch`.
- Add deterministic regressions that cross the deadline after project creation, after batch creation, and before enqueue, proving that no subsequent request is dispatched.
- Regenerate the campaign and decision bindings affected by the `qi_platform.py` digest.
- Record the already-given three-job authorization against the repaired exact-case hashes.

That repair leaves the authorized circuits, shots, order, credits, and acquisition scope unchanged. It does not require authorization for additional jobs. Relaxing the 60-second or 7200-second boundaries instead would change the reviewed contract.

### SLOPPY

None found.

## Sound portions

- The new primary endpoint is honestly separated from the incomplete six-job campaign. The old nominal-zero prefix is retrospective evidence only (`docs/design/tuna-readout-destination-one-admission.md:3-8`; `docs/evidence/tuna-projector-geometry/destination-one-decision.json:18-26`).
- All three proposal manifests, backend snapshots, and cQASM sources are byte-identical to the old nominal-one cases. The baseline sources are identical; only early destinations cycle from bits 17,18,19 to 19,17,18. Terminal destinations remain 0–16 (`results/quantum_inspire/proposals/tuna-readout-destination-one/prepared-one-*/`: circuit lines 26-30).
- The decoder reverses the provider string convention and restores physical q4, q11, q6 consistently (`scripts/qi_tuna_destination_one_analysis.py:296-306`, `319-366`).
- The martingale calculation is correct: 12 response plus 12 endpoint contrasts, two-sided familywise alpha 0.01, `log(48/.01)=log(4800)`, with upward-rounded radii 0.039396318627 and 0.045490950328 (`docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md:9-27`).
- The 0.10 practical-margin separations recompute exactly as 0.021207362746, 0.178792637254, and 0.009018099344. Closed equivalence, strict departure, and endpoint veto logic match the written contract (`scripts/qi_tuna_destination_one_analysis.py:485-556`).
- The fixed scope is three serial single-job batches, 4096 shots each, 12,288 total, 300 seconds per job, 900 aggregate, expected 14.688660 reported seconds, and zero credits (`results/quantum_inspire/proposals/tuna-readout-destination-one/campaign.json:12-46,67-81`).
- The 7200-second arithmetic is correct: `3×1680 + 900 + 2×30 + 1200 = 7200`. The documentation correctly states that future queue service remains unbounded.
- The analyzer preserves all five outcomes, requires a complete fixed acquisition, rejects failed/partial/charged/misbound evidence, enforces distinct job and batch identities, and prevents statistical early stopping.
- Existing run roots are rejected before mutation (`scripts/qi_tuna_destination_one_run.py:317-320`). Ambiguous submission checkpoints block retry (`scripts/qi_platform.py:872-878,1033-1044`). Recovery is read-only and does not authorize replacement jobs.
- Fresh admission requires an empty account-specific queue, zero pause, current structure, heartbeat at most 120 seconds old, and exact-zero account ledger changes (`scripts/qi_projector_live_admission.py:97-183`).

## Scientific limits

The case can classify only realized predictable binary-response contrasts. Its bound assumes trusted shot ordering and fixed complete jobs. Three jobs remain only three intervention units. The design does not establish excited-state populations, destination causality, analog schedule equality, acquisition-index mapping, discrimination thresholds, calibration stability, IQ interpretation, absence of synchronized transients, or absence of apparatus memory. The nominal-zero prefix cannot repair those limitations or the old unavailable primary endpoint.

## Checked surface and local results

I reviewed the requested scripts, tests, design, mathematical note, decision, terms receipt, proposal, compiler receipt, imported admission helper, and submission/collection paths.

Submit-free checks completed:

- Exact compiler/source proposal replay passed under `/usr/bin/qi-stack-python`.
- Exact campaign, written-case, decision, analyzer, compiler, and terms binding preflight passed.
- Candidate campaign, decision, and written-case SHA-256 values matched the supplied values.
- All old/new nominal-one manifest and source bytes matched.
- Thirteen write-free focused tests passed under Python 3.14.7 with bytecode and pytest caches disabled.

Unrun by this review:

- The full 99-test successor suite and 197-test combined suite.
- Tests requiring writable pytest temporary directories.
- Pinned Ruff and mypy.
- Optimized-mode replay.
- Provider policy reads, credential access, fresh queue/pause/heartbeat/ledger admission.
- Submission, collection, recovery, IQ, schedule, or hardware execution.
- Any emulator or stochastic check.

The owner-approval receipt is presently absent, as expected. `docs/design/tuna-readout-destination-one-admission.md:90-93` requires that receipt before execution.

## Verdict

- Offline scientific and evidence contract: **PASS**.
- Exact three-job execution readiness: **HOLD** pending deadline propagation, regenerated exact bindings, and recording of the existing owner authorization.
- Causal or physical-mechanism inference: **NOT ADMITTED**.

No provider operation or fresh live admission was performed.
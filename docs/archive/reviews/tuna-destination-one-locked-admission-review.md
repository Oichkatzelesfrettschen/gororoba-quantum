# Repair review: three-job nominal-one Tuna case

Model configuration: `gpt-daybreak-blue-latest`, high reasoning effort, default tier.

Artifact fields: deadline-bounded distributed API orchestration, durable checkpointing, reproducible evidence, and statistical acquisition governance. I reviewed the successor helper, runner integration, focused tests, regenerated packet, retained verification receipt, and inherited `qi_platform.py` behavior.

## Findings

### FATAL

None.

### SERIOUS — HOLD: the final analyzer ignores the locked-admission receipt

The execution path now writes the decisive under-lock observation to `locked-admission.json` and refuses dispatch when that observation fails (`scripts/qi_tuna_destination_one_run.py:316-358`). The tests verify that the producer records actual acceptance or refusal and exact producer identities (`tests/scripts/test_qi_tuna_destination_one_run.py:489-531`).

The evidence consumer never reads that receipt:

- `validate_completion` validates only the earlier `admission.json` and omits `locked-admission.json` from its input hashes (`scripts/qi_tuna_destination_one_run.py:249-278`).
- `validate_batch` calls only `validate_admission`, then expects a completion receipt whose input set excludes the locked receipt (`scripts/qi_tuna_destination_one_analysis.py:421-455`).
- The final analysis provenance likewise omits it (`scripts/qi_tuna_destination_one_analysis.py:456-480`).
- The analysis fixture creates no locked-admission receipt at all (`tests/scripts/test_qi_tuna_destination_one_analysis.py:174-221`), yet `test_complete_fixed_case` still requires `objective established within scope` (`tests/scripts/test_qi_tuna_destination_one_analysis.py:225-230`).

Concrete reproduction: remove `locked-admission.json`, change its `admitted` field to false, alter its queue/heartbeat/ledger result, or replace its producer hashes. The frozen analyzer returns exactly the same scientific classification because no code path opens the file.

That breaks the claimed evidence chain. The under-lock recheck is the mechanism that closes the admission-to-dispatch window; an analysis that accepts its absence cannot independently establish that the repaired route was used. Binding the runner and helper source digests proves what those programs would do, but not that the required per-job receipt exists or matches the acquired job.

Required repair:

- Make each successful completion require a valid `locked-admission.json`.
- Validate its schema, `admitted=true`, empty failures, manifest hash, runner/helper hashes, full frozen structure, enabled state, queue, pause, zero-ledger result, heartbeat, limits, and chronology before provider job creation.
- Include its digest in `completion-admission.json` and final analysis provenance.
- Add missing, malformed, false-admission, hash-mutation, structure-mutation, and chronology regressions to the analyzer tests.

This repair does not alter the authorized circuits, shots, order, margins, horizon, credits, or scientific scope. Regenerate the packet bindings before recording the existing approval receipt.

### SLOPPY

None found beyond the blocking evidence omission.

## Prior deadline finding disposition

The original deadline-propagation defect is repaired.

- The successor client stores one intrinsic finite deadline and takes the minimum with any explicit deadline (`scripts/qi_platform_submission_deadline.py:25-50`).
- Inherited `get`, paginated `pages`, and `post` dynamically dispatch through the overridden `request`; successor `patch` does likewise (`scripts/qi_platform_submission_deadline.py:32-53`).
- The base request checks immediately before transport and again after rejected-request authentication handling (`scripts/qi_platform.py:382-400`).
- Every resource operation therefore inherits the deadline even where individual calls omit an explicit argument (`scripts/qi_platform_submission_deadline.py:120-163,188-276`).
- Expiry after project, batch, algorithm, commit, file, or job creation leaves known identities checkpointed and blocks the next request (`scripts/qi_platform_submission_deadline.py:164-285`; `tests/scripts/test_qi_platform_submission_deadline.py:102-130`).
- Pre-dispatch enqueue expiry records `enqueue-refused-before-dispatch`; a lost enqueue response retains `enqueue_outcome_unknown` and remains non-retriable (`scripts/qi_platform_submission_deadline.py:270-285`; tests at lines 145-169).
- Authentication refresh may cross the deadline, but the rejected compute request is not retried afterward (`tests/scripts/test_qi_platform_submission_deadline.py:172-186`).
- Queue, pause, backend enablement, complete structure, heartbeat, and ledger are rechecked while holding the inherited account submission lock (`scripts/qi_platform_submission_deadline.py:56-79,120-163`; `scripts/qi_tuna_destination_one_run.py:316-358`).
- The historical `scripts/qi_platform.py` tracked diff is empty.

The prior SERIOUS timing defect is therefore closed.

## Sound boundaries

- Campaign, decision, written-case, and terms hashes match the supplied repaired values.
- Full local compiler/source replay and exact binding preflight passed.
- All three nominal-one manifests, backend snapshots, and circuit sources remain byte-identical to the predecessor proposal.
- The 60-second freshness limit and 7200-second request-initiation horizon remain unchanged.
- Policy reads, pause inspection, initial admission, locked admission, resource creation, job creation, and enqueue are deadline-bounded.
- In-flight requests may finish after their initiation deadline; subsequent compute requests remain blocked.
- Checkpoint semantics preserve every resource identity returned before failure and prevent automatic retry or resume.
- The unchanged statistical contract remains 12 response cells plus 12 endpoint contrasts using `log(48/.01)`, five outcomes, and unresolved attribution.
- The old nominal-zero prefix remains retrospective only. The old six-job primary endpoint remains unavailable.

## Verification performed

Reviewer-run, write-free checks:

- Full local proposal/compiler replay: passed.
- Exact packet binding preflight: passed.
- Predecessor manifest/source byte comparison: passed.
- Six selected write-free tests: passed.
- In-memory class-dispatch probe for inherited `get/pages/post` and successor `patch`: passed.
- `git diff --check`: clean.
- Historical `scripts/qi_platform.py` diff: empty.

The retained verification receipt reports 221 focused tests, 55 deadline/runner cases, pinned Ruff and mypy success, and byte-identical normal/optimized synthetic analysis (`docs/evidence/tuna-projector-geometry/destination-one-deadline-repair-verification.json:1-11`). I did not independently rerun tests requiring writable temporary directories.

Unrun by this review: provider access, credential reads, policy/network observations, fresh queue/pause/heartbeat/ledger admission, submission, collection, recovery, emulator execution, full 221-test suite, pinned Ruff/mypy, and owner-receipt creation.

## Verdict

- Deadline repair: **PASS**.
- Scientific and causal scope: **unchanged and appropriately bounded**.
- Exact three-job execution readiness: **HOLD** until the locked-admission receipt becomes a mandatory, hash-bound input to completion and final analysis.
- After that repair, regenerated exact bindings, recording of the existing owner approval, and fresh per-dispatch admission, the authorized three jobs require no additional approval.
- Any hardware beyond those three jobs still requires a new queue-aware case.
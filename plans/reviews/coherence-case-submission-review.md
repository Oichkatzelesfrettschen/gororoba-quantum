# Coherence-window case: submission-path review

Review-only. No live_run.py submit, collect, approved-record, or preserve-raw invocation was made, no IBM service was contacted, nothing under results/live/2026-10-14T060826.976518Z/ was written, and no tracked file was edited or committed. The only new file in the worktree is this report.

Environment: Python 3.14.7; qiskit 2.5.2; qiskit-ibm-runtime 0.50.0 (installed under /usr/lib/python3.14/site-packages); qiskit-aer 0.17.2. All seven versions in the approved record match the installed packages. Worktree HEAD is 10bb9ee; the only untracked path is the approved case directory.

## What the artifact is and claims

A submit-gated QPU case: a saved submit-free dry run (record.json, isa.qpy) that the owner would approve, plus a command that re-plans, compares the fresh plan with the record, and sends two client-side Sampler jobs (10 static PUBs, 5 dynamic PUBs, 2048 shots each, 9 s ceilings, 18 s combined). Field: quantum-hardware job submission, with approval gating, cost accounting, and Qiskit runtime client semantics. Visibility: the submit-relevant regions of gororoba_quantum/live_run.py were read, not all 5168 lines; the cited supporting modules were read in full where cited. This is a committed tree, not a diff.

## Checks and results

Demonstrated in this revision:

1. Fresh-side policy, raw comparison. `main` was run with the case's flags, the service class and the plan entry point stubbed, and `policy` rebuilt exactly as `plan()` builds it (live_run.py:2564-2581). `fresh == record["policy"]` is True with no JSON round-trip on the fresh side. `local_compute.settings` (including `aer_native`) is also raw-equal. A recursive walk finds no tuples, no non-string keys, and no non-JSON types.
2. Fresh-side family_configuration. `take_snapshot` ran against the fake backend FakeFez (refresh stubbed) and `qpu_planning.patch_candidates` built the coherence-window configuration in memory. Keys match the record exactly, every value is JSON-native (str, list, dict of str to int, int, float), and `readout_qubits` and `patch_qubits` match the record. The raw comparison fails only on calibration-derived values (window_dt 786 vs 836, control_measure_dt 390 vs 415, control_reset_dt 396 vs 421), because the fake calibration is dated 2025-02-26 and the record's is 2026-10-13. That is expected and says nothing about the gate's type handling.
3. Archived circuits through the client-side Sampler. isa.qpy was loaded in memory (no write). The 10 static PUB circuits went through one `configure_sampler(FakeFez(), "static", False, None, [], 2048, 9).run(batch)` call and the 5 dynamic PUB circuits through one dynamic call. Both returned all PUBs with 2048 shots, in 34.7 s and 13.9 s, with no raised exception and no warning recorded. The circuits are 156-wire ISA circuits with 4 active qubits, 4 clbits, no parameters, and no control flow, so a raw run was feasible and no Clifford conversion was needed.
4. Migrate-skill grounding. Detailed in section 5.

Correction to the earlier draft: the earlier comparator probe built its "fresh" view from the JSON-loaded record and therefore compared JSON against JSON. It could not detect a type difference on the fresh side, so it does not bear on F1. Check 1 is the raw comparison and supersedes that probe. Whether F1 is blocking is answered by check 1 and check 2: the current fresh values trigger no type mismatch, so F1 is a latent hazard, not an observed defect.

Other checks, carried from the earlier pass and re-confirmed:

- Option paths in `configure_sampler` exist in the installed 0.50.0 option models, and assignments are validated (options_models/base.py:31, `validate_assignment=True`, `extra="forbid"`). Static and dynamic jobs were constructed locally with no warnings; `max_execution_time` is 9 on both.
- The ceiling reaches the runtime request: executor_sampler/sampler.py:226, prepare.py:99, options_models/converters.py:58, executor/executor.py:171-177.
- The family path rejects `--twirl` and `--dd` (live_run.py:4825-4826).
- Both contract scripts exit 0 with no warning lines. `experiment_digest()` reproduces e62dc0e6... and `_code_commit()` reports head 10bb9ee, sources_modified false.
- Every file `from_run` reads is written by collect or by the submit path (section 4). The collect ledger carries `raw` (live_run.py:4316), which `_bound_counts` reads.

## Findings, worst first

Each finding carries a label (demonstrated, assumed, or unsupported) and the governing principle it bears on.

F1. Type-sensitive comparator. SLOPPY, latent.
- Barb: the gate compares an in-memory plan against a file it has already flattened to JSON, so a tuple where the record holds a list would turn an identical plan into a "differs".
- Grounding: demonstrated. `approved_record_mismatches` (live_run.py:2777-2822) uses `!=` on the raw fresh view. Injecting a tuple into `patch_qubits` makes the comparator report `family_configuration differs`. Principle: a comparison must use the representation that was persisted, or normalize both sides to it. Failure mode is fail-closed: `approval_required`, no job, and no approval marker written (the mismatch raises at 3422, before the batch loop at 3502).
- Current status: no tuple exists in the current fresh values. Demonstrated for policy (check 1), family_configuration types (check 2), and `execution_pubs` manifests (manifest() returns lists, strings, bools, and ints; live_run.py:774-788, 801-817). `observable_contracts` and `selected_job_costs` are normalized by a JSON round-trip (qpu_planning.py:514-515, 719).
- Remedy: apply `json.loads(json.dumps(view))` inside `refreshed_plan_view` (live_run.py:2713-2733) before the comparison. Not required for this case.
- Falsifier: a future change that puts a tuple into `patch_candidates` or `qpu_planning.settings` output.

F2. The approval marker is spent before the remote call and is never removed. SERIOUS, operational, by design.
- Barb: the one-attempt authorization is spent on a checkpoint, not on acceptance, so a transient failure after the first batch starts costs the owner a new written case with zero jobs sent.
- Grounding: demonstrated by code order. `consume_approval` runs at live_run.py:3506 and writes approval-consumed.json with O_EXCL and fsync (2742-2775). The batch then sets state "attempted", calls checkpoint, and calls `sampler.run` (around 3519-3524). The only unlink in live_run.py removes collect.partial.json (4267). Nothing removes the marker on a later failure. Principle: an authorization that must not be replayed also must not be spent without a send. The code chooses no-replay over no-loss, which prevents a double submit.
- Assumed: that a client-side rejection in the prepare or boxing path could occur on the real service path. The local batch run (check 3) did not reproduce one, so that specific failure is unsupported as an observed risk. Frequency of transient failures is unsupported.
- Remedy: none required for this case. State in the approval that a failure after the first batch starts requires a renewed approval, or split pre-send from accepted-send in the marker.

F3. Charge margin on the static job. Disclosure, not a defect.
- Barb: the static ceiling leaves 3.8 s of room over the modeled circuit time, and the 2.3 s overhead beneath it is a planning number.
- Grounding: demonstrated arithmetic from the record. Static: modeled PUB time 5.2349 s, overhead 2.3 s, estimated charge 7.5349 s, ceiling 9 s, margin 3.7651 s. Dynamic: 2.6346 s, 2.3 s, 4.9346 s, 9 s, margin 6.3654 s. The record calls the overhead "a declared overhead ... not a backend guarantee" and the case says native timing is unqualified (UNAPPROVED_CASE.md).
- Assumed: that the service counts the overhead inside `max_execution_time`. The SDK docstring says a job exceeding the limit "is forcibly cancelled" (options_models/sampler.py:40-46); the charge accounting relationship is not verified.
- Unsupported: that a cancelled job returns partial counts, and that the static job's real overhead is at or below 3.77 s.
- Falsifier: a completed static job with system execution time above 9 s, or with non-circuit time above 3.77 s in its scheduler timing.

F4. The approved case directory is the only copy of the compared plan in this worktree. Note.
- Grounding: demonstrated (git status shows the directory untracked; it holds record.json and isa.qpy, which the `--approved-record-sha256` and `--approved-record` checks read).
- Remedy: keep the directory intact until the run is collected and analyzed; commit it in an evidence change after the run, not before.

## Steelman

The design is careful in the places where a QPU spend is irreversible. The gate compares the fields the owner reads, fails closed, writes the approval marker before the remote call so a crash cannot double-send, sets every option explicitly and checks the option paths against the installed package, and forwards the ceiling to the runtime request. The dry run and the approval command use the same code path. The case states its own uncertainty (overhead as a planning assumption, native timing unqualified, the 390 s quota reading as a moment-in-time value) and does not present the estimate as a service fact.

## Section 5. Migration-skill audit (report-only, scope gororoba_quantum/ and scripts/)

- Phase 1: registry read. Target: installed 0.50.0 is at or above `min_runtime_version` 0.50.0, so hop B is available. The code already targets the client-side destination.
- Phase 2: detection sweep over gororoba_quantum/ and scripts/. Zero hits for `SamplerV2`, `EstimatorV2`, `qiskit_ibm_runtime.sampler`, `qiskit_ibm_runtime.estimator`. Primitive imports are `qiskit_ibm_runtime.executor_sampler` (live_run.py:61, runtime_contracts.py:34, pub_shot_runtime_contracts.py:25). So server-to-client was early-exited through `already_migrated`, and no change was assigned to it. Zero hits for `quasi_dists`, `IBMSampler`, `IBMEstimator`, `IBMRuntimeService`, `circuit_indices`, `observable_indices`, `NoiseLearner`, `backend.run(`, `auth=`, `channel="ibm_quantum"`, `RuntimeJob`, `program_id`, `check_pending_jobs`, `get_backend(`, `service.open(`, `open_session`, `Session.from_id`. The remaining matches are Qiskit transpile keyword arguments, Aer simulator `set_options` (local_compute.py:164, 249), dataclass `asdict`, compiler-pass callbacks, dict keys, and `browser.close()` (scripts/validate_measured_explorer.py:105).
- Phase 3 grounding did not run: no change was assigned after the early exit. The published migrate-to-client-side guide (the server-to-client `url`) was not fetched, because the no-IBM-contact rule covers this review. The local guide files were not read, because no trigger matched them.
- Phase 4 and Phase 5: no edits were made, so no imports were rewritten and no checklist items applied.
- Phase 6: no migrated code exists to verify. The client-side import resolves (live_run.py imports it at module load). No `DeprecationWarning` and no "no effect in local testing mode" warning was recorded in the construction and batch runs (check 3). The service-object methods on the live path exist in 0.50.0: `QiskitRuntimeService` usage, job, jobs, backends, backend, instances, active_instance (qiskit_runtime_service.py:1316, 1170, 1203, 548, 957, 1471, 1484); `IBMBackend` configuration, properties, status, refresh, target_history (ibm_backend.py:404, 325, 380, 312, 301); job usage and metrics (base_runtime_job.py:124, 152). The `jobs()` keywords the code uses exist (qiskit_runtime_service.py:1203-1212).

## Section 4. What from_run reads

Reads (scripts/coherence_window_analysis.py:202-257 and helpers):

- record.json: family_configuration (readout_qubits, dt_seconds), submission.jobs (job_id, kind, members), observable_contracts, execution_pubs.
- isa.qpy, checked against submission.qpy_archive_sha256 (scripts/patch_window_analysis.py:57-58).
- collect.json, first element's jobs ledger (patch_window_analysis.py:59). The writer (live_run.py:4266-4276) emits a one-element list with a jobs key, and each job carries its raw digests (4316).
- raw/<job_id>/index.json: files and job_id (patch_window_analysis.py:72-75); metrics, metrics_sha256, metrics_latest (adjudicate.py:292-301).
- raw/<job_id>/pub_NN.json: registers, pub_index, pub_name, metadata.compilation.scheduler_timing.timing (patch_window_analysis.py:76-91).
- raw/<job_id>/job_metrics*.json, through latest_metrics.

Writers: the raw writer (live_run.py:4993-5041) writes pub_NN.json, result_metadata.json, and index.json with per-file digests. `_merged_index` (5046-5052) and `snapshot_metrics` (5055-5082) write the metrics snapshots and their index fields. The submission block is written at 3437, 3525, and 3535.

Conclusion: every file from_run reads is written by collect or by the submit path (demonstrated). Timing is available only if `execution.scheduler_timing` is set, which configure_sampler sets for both jobs (3581); without it, executed_idle_us returns None and the exposure is unresolved (patch_window_analysis.py:93-104). Demonstrated by reading.

Not run: from_run on a collected run, since none exists. The approved dry-run record has no submission key, so from_run cannot run on it, which is expected.

## Not run or not established

- Fresh plan against the live service, and the approval-only comparison on live calibration: needs IBM contact, out of scope. Check 1 and 2 cover the in-memory comparison with stubbed service and fake snapshot.
- Service-side enforcement of max_execution_time and charge accounting: needs a submitted job.
- Local batch runs are FakeFez local-testing runs (noise model from the fake device; its calibration is dated 2025-02-26). They exercise the client-side prepare and run path, not the service's job-size, shot, or queue admission.
- from_run on a collected run: none exists, so the read set is established by code reading.
- Repository gates in ci/gates.json: not requested for this review.
- Probe scripts were kept in the session scratchpad, outside the repository.

No code change blocks the case. Checks 1 through 3 (raw comparator equality on policy and family types, archived batches running clean under the case's settings, and the from_run read set) found no defect. The owner's written approval of this case and its ceilings, and the approval-only re-plan that must pass the comparison before any job is sent, remain the gates. Accept F2 and F3 explicitly in that approval.

Verdict: SAFE TO SUBMIT

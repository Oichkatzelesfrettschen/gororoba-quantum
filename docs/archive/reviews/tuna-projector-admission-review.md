# Submission-path disposition

The execution runner invokes `qi_platform.submit` with the exact frozen
`expected_cases_sha256`, after requiring a fresh live receipt with `admitted=true`.
The runner uses the guarded Python API, satisfying the conditional blocker below.
The regression test `test_changed_manifest_refused_before_client` verifies rejection
before provider client creation. The ordinary CLI is outside this acquisition path.
Actual local compiler replay passed; live admission is repeated immediately before submission.
The documentation replay command and stale approval wording were corrected.

# Admission review

Launch and session metadata record `gpt-daybreak-blue-latest` with high reasoning effort. I reviewed the current filesystem bytes for every requested admission script, test, receipt, document, manifest, circuit, and relevant `qi_platform.py` path. Provider operations remained unrun.

## Remaining blocker

### SERIOUS — The standard submit CLI drops the frozen-manifest digest guard

The live admission correctly binds manifest SHA-256 `d9a41a…cfb2` and every source/compiled circuit at [qi_projector_live_admission.py:49](../../../scripts/qi_projector_live_admission.py).

The internal submission API supports `expected_cases_sha256` at [qi_platform.py:831](../../../scripts/qi_platform.py) and refuses a changed manifest before creating a provider client at [qi_platform.py:881](../../../scripts/qi_platform.py).

The command-line interface exposes only `--backend-type-id` and `--approval` at [qi_platform.py:1201](../../../scripts/qi_platform.py), then calls `submit()` without `expected_cases_sha256` at [qi_platform.py:1225](../../../scripts/qi_platform.py). The deterministic reproduction was:

```text
usage: qi_platform.py submit [-h] --backend-type-id BACKEND_TYPE_ID
                             --approval APPROVAL
                             case_dir
```

Consequently, a consistent manifest-and-circuit alteration after live admission could pass the ordinary CLI’s internal hashes while crossing the exact default-angle acquisition boundary authorized by the user. The shared working tree makes that a reachable failure mode rather than a theoretical objection.

Required resolution:

- Expose `--expected-cases-sha256` through the CLI and pass it into `submit()`, or use a reviewed submission wrapper that supplies the exact frozen digest.
- Test that a changed manifest fails before any remote request.
- Preferably validate the fresh live-admission receipt’s `admitted=true`, empty failures, and matching input digest in the same wrapper.

If the parent’s “guarded submit” already means calling the Python API with `expected_cases_sha256="d9a41a…cfb2"`, this blocker is satisfied without another approval or a manifest change.

## Nonblocking defects

### SLOPPY — The documented QX replay command does not replay anything

[qx-conformance.md:76](../../../docs/evidence/tuna-projector-geometry/qx-conformance.md) instructs the reader to use `--help` and a run path. The audit script accepts `--check RECEIPT` and embeds the run path internally.

The reproducible command is:

```sh
"$PYTHON" scripts/qi_projector_distribution_audit.py \
  --check results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx/joint-law-audit.json
```

### SLOPPY — Two durable records still request approval that has already been granted

[qx-conformance.md:68](../../../docs/evidence/tuna-projector-geometry/qx-conformance.md) and [tuna-projector-geometry.json:162](../../../docs/state/plans/tuna-projector-geometry.json) still describe separate approval as pending. The admission contract correctly records the existing authorization at [tuna-projector-qualification-admission.md:5](../../../docs/design/tuna-projector-qualification-admission.md).

The parent should update those records to “authorization recorded; compiler and live admission pending.” The stale wording does not require the user to approve the unchanged batch again.

## Sound findings

- **Custom-angle disposition: sound.** The fixed manifest, historical producer, three source circuits, and three compiled circuits are byte-bound. The qualification analyzer independently validates the fixed `(0°,45°,90°)` metadata and physical bit map at [qi_tuna_qualification.py:30](../../../scripts/qi_tuna_qualification.py). The successor prohibition at [tuna-projector-qualification-admission.md:72](../../../docs/design/tuna-projector-qualification-admission.md) correctly prevents permutations until generator metadata is repaired and all six assignments are tested.

- **Compiler admission: sound for its declared scope.** The replay recompiles all six sources, compares exact compiled bytes, and compares complete normalized instruction order, targets, measurement destinations, and eight-significant-digit rotations at [qi_projector_compiler_admission.py:94](../../../scripts/qi_projector_compiler_admission.py). The receipt binds the compiler driver, package sources, versions, backend observations, manifests, and compiler configurations. Hardware scheduling remains expressly outside scope.

- **Live structural admission: sound.** The check compares backend identity, capacity, raw support, protocol, limits, compiler configuration, complete topology, required edges, and gate set at [qi_projector_live_admission.py:96](../../../scripts/qi_projector_live_admission.py). It also requires an empty account queue, expired hardware pause, available backend instances, zero ledger changes, and heartbeat age within the caller’s policy. The 120-second heartbeat threshold is correctly treated as an admission policy rather than a device specification.

- **Collection compatibility: sound.** The qualification analyzer consumes the exact `qi_platform.collect()` structure: three `jobs`, one result per completed job, raw lists under `raw/<file>.json`, and batch-job transactions. It verifies job identities, 4096 completed raw shots, width 20, histogram equality, source hashes, batch identity, and per-job execution time in `[0,300]` seconds at [qi_tuna_qualification.py:93](../../../scripts/qi_tuna_qualification.py).

- **Bit order: sound.** Classical bit `b` maps to string offset `19-b`. Early bits 17, 18, and 19 map to offsets 2, 1, and 0; final ancilla bits 4, 11, and 6 map to offsets 15, 8, and 13. The disagreement calculation uses precisely those pairs.

- **Threshold logic: sound.** Twelve contrasts gate qualification: nine active terminal qubits plus three early ancilla bits. A difference count of 2048/4096 passes. For early/final disagreement, 409/4096 passes and 410/4096 fails. Every comparison uses integer arithmetic at [qi_tuna_qualification.py:63](../../../scripts/qi_tuna_qualification.py).

- **Timing contract: sound.** The 14.31264-second value remains an estimate. The analyzer reports actual duration and enforces the explicit 300-second limit independently for each job. A modest estimate overrun therefore remains descriptive rather than becoming an invented stopping rule.

- **Charge handling: sound.** Every retained transaction must belong to one of the submitted jobs; every change must equal zero for qualification to pass. An empty transaction list represents zero recorded charge, matching the completed QX collection format.

- **Historical qubit disposition: sound.** Earlier records observed poor q6 prepared-one and q9 prepared-zero behavior. Later records observed q6 at 0.957 and q9 prepared-zero at 0.018 after recovery at [tuna-17.md:57](../../../docs/notes/quantum_inspire/tuna-17.md). The admission contract correctly treats those as observations from different times and requires fresh qualification of `(3,6,9)` at [tuna-projector-qualification-admission.md:61](../../../docs/design/tuna-projector-qualification-admission.md). Historical exclusion does not establish current failure; historical recovery does not establish current performance.

- **QX supplemental audit: sound.** The retained full-law replay matches current raw bytes and reports zero impossible outcomes in all three executed QX circuits. The audit remains explicitly descriptive and makes neither an IID nor hardware claim.

## Deterministic verification

Completed locally:

- Ruff format and lint: clean for all eight new Python files.
- Mypy: clean for all eight new Python files.
- Retained compiler-input and complete-stream check: passed.
- QX full-distribution receipt replay: passed.
- Focused tests that require no writable temporary directory: **67 passed**.
- Twelve temporary-directory cases were inspected but not executed in the read-only environment.
- Plan tracker: 110 records consistent.
- Markdown links: all 692 checked files resolve.
- Staged and unstaged `git diff --check`: clean.

Still intentionally unrun:

- Actual Quantum Inspire interpreter compiler replay with `--check`.
- Fresh authenticated live admission.
- Provider submission and collection.
- The twelve writable-temporary-directory tests.
- Full repository test and gate suites.
- Every successor causal-campaign acquisition.

## Verdicts

- **Fixed-manifest disposition:** **PASS.** Exact manifest admission safely bounds the historical custom-angle defect out of this acquisition. Successor angle permutations remain prohibited.

- **Bounded three-circuit Tuna qualification:** **HOLD on the ordinary CLI path.** Close the expected-manifest-digest handoff described above. After that handoff, a successful actual compiler replay and fresh `admitted=true` live receipt are sufficient to execute the unchanged batch under the user’s existing authorization. Redundant approval is neither required nor appropriate.

- **Full causal campaign:** **HOLD / prospective.** Four-state joint calibration, angle-placement counterbalancing, early/deferred/deferred-sequential timing controls, signed and mutation arms, gap response, spectator contexts, leakage diagnostics, executed-order/dependence analysis, and a frozen uncertainty model remain outstanding. A passing qualification cannot support a causal projector or backaction claim.

REVIEW_COMPLETE

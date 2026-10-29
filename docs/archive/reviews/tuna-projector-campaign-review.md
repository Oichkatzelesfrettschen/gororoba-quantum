## Verified correction and disposition

The requested Codex CLI model was `gpt-daybreak-blue-latest`, with reasoning effort `high`.
The launch header and session turn contexts agree. The reviewer subsequently retracted its
unsupported model-unavailability assertion. Three compact circuits executed on QX; six circuits
in the proposal comprise those three and three unsubmitted Tuna circuits. The original report
below contains the superseded assertions so its review history remains visible.

The custom-angle metadata defect affects prospective counterbalanced cases. The bounded acquisition
admits only the exact default-angle manifest and circuit digests. Successor angle permutations
remain blocked until source-derived metadata and all six permutation checks exist.

# Independent adversarial review — HEAD `f6e4ef6`

I verified the checkout HEAD as `f6e4ef6c570f68dabf68b7b7c0a234d89b25ba74` and reviewed tracked HEAD content only. Parent-owned modified plan views and post-HEAD untracked audit code/results were excluded from the evidence base.

The requested `gpt-daybreak-blue-latest` model was unavailable in this runtime. I performed the review with the session model at high reasoning effort, without delegation.

## Blocking findings

### HIGH — Custom angle placement silently receives incorrect metadata

The circuit generator accepts caller-supplied angles and emits rotations from those angles at [qi_projector_geometry.py:53](../../../scripts/qi_projector_geometry.py) and [qi_projector_geometry.py:73](../../../scripts/qi_projector_geometry.py). The metadata generator instead reads the module-level default `ANGLES` at [qi_projector_geometry.py:100](../../../scripts/qi_projector_geometry.py), and the batch builder passes neither the selected angles nor a circuit-derived angle at [qi_projector_geometry.py:145](../../../scripts/qi_projector_geometry.py).

A future call using a permutation such as `(90°, 0°, 45°)` therefore generates the requested gates while labeling the replicas as `(0°, 45°, 90°)`. The proposed successor campaign explicitly requires rotating each angle across placements at [tuna-projector-geometry.md:185](../../../docs/design/tuna-projector-geometry.md). The defect would convert placement effects into apparent angle effects.

Required fix:

- Pass the exact angle tuple into `shot_metadata`.
- Derive or independently validate each metadata angle against the emitted `Ry` gates.
- Add permutation tests covering all six angle-to-placement permutations.
- Reject any source circuit whose rotations and manifest metadata disagree.

The default QX run and present three-circuit Tuna qualification use the default tuple, so this defect does not invalidate their recorded metadata.

### HIGH — The Tuna compiler receipt is static evidence rather than a replayable admission check

The compiler receipt records package versions and source/compiled hashes at [local-compiler-receipt.json:1](../../../results/quantum_inspire/proposals/tuna-projector-geometry/local-compiler-receipt.json), but it lacks:

- The exact compiler command.
- A digest of the backend compiler configuration.
- The compiler/exporter producer revision.
- A complete normalized source-to-compiled instruction comparison.
- A gate-ledger entry that regenerates and verifies the six outputs.

The existing toolchain checker scans retained cases rather than proposal directories at [qi_toolchain_check.py:67](../../../scripts/qi_toolchain_check.py). The gate ledger replays the QX conformance result at [gates.json:4994](../../../ci/gates.json), but it does not replay the Tuna compilation.

Manual inspection found matching recorded hashes and plausible instruction preservation in all six compiled circuits. That observation establishes the current bytes, not the reproducibility of the compilation process.

Required fix before hardware execution:

- Add a deterministic proposal compiler replay.
- Bind the exact backend `default_compiler_config` and its digest.
- Bind the exporter/compiler source revision and versions.
- Compare the complete normalized gate/control sequence, not only control differences.
- Admit the replay through a test or gate.
- Revalidate the live Tuna backend’s topology, gates, and compiler configuration. A mismatch must stop submission and require renewed circuit review.

### HIGH — The documented qualification thresholds lack an executable post-collection decision check

The provider procedure calls for generator checking before submission and a sanity check after collection at [usage.md:109](../../../docs/notes/quantum_inspire/usage.md). The geometry script exposes circuit generation and descriptive case analysis at [qi_projector_geometry.py:243](../../../scripts/qi_projector_geometry.py) and [qi_projector_geometry.py:279](../../../scripts/qi_projector_geometry.py), but it does not implement the stated assignment-contrast and early/final-disagreement decisions from [tuna-projector-geometry.md:169](../../../docs/design/tuna-projector-geometry.md).

Required fix:

- Freeze a read-only qualification analyzer before acquisition.
- Verify three completed jobs, 4096 shots per job, width-20 raw strings, ordered-shot preservation, manifest/circuit digests, job state, charges, and timing.
- Compute the all-zero/all-one assignment contrasts and early/final ancilla disagreement.
- Define inclusive/exclusive behavior exactly at each threshold.
- Add malformed width, missing job, partial collection, threshold-boundary, and incorrect bit-map tests.
- Make failure refuse a qualification claim while preserving the raw record.

Adding an analyzer without changing circuit or manifest bytes does not enlarge the written acquisition case. Any circuit or manifest change would invalidate the existing case binding.

### HIGH — The submission guard does not constitute complete live structural admission

The live submission checks at [qi_platform.py:901](../../../scripts/qi_platform.py) cover backend identity, availability, qubit count, job/circuit/shot limits, queue depth, and pause state. The guard does not compare the live topology, gate set, or default compiler configuration with the proposal’s frozen backend description.

The design itself requires live edge and compiler validation at [tuna-projector-geometry.md:103](../../../docs/design/tuna-projector-geometry.md). Therefore, passing the present submission guard alone is insufficient.

Live admission must verify:

- All six physical edges used by the three replicas.
- Gate availability and compiler configuration.
- Enabled/status/heartbeat observations.
- Maximum shots, circuits, jobs, queue, and pause limits.
- Current free-use terms and ledger/account scope.
- Exact source, compiled-circuit, manifest, and written-case digests.

Every observation must be timestamped. A structural mismatch must stop the batch.

### HIGH — The full causal successor campaign remains a research outline

The successor sequence at [tuna-projector-geometry.md:183](../../../docs/design/tuna-projector-geometry.md) names valuable comparisons, but HEAD implements only QX terminal conformance and the three-circuit Tuna qualification at [qi_projector_geometry.py:127](../../../scripts/qi_projector_geometry.py).

A defensible mechanism campaign still requires:

- A precise causal estimand separating measurement pulse, elapsed time, detector context, assignment error, leakage, drive/CZ error, and drift.
- Four-state joint A/C calibration for every relevant readout placement and context.
- Angle-by-placement counterbalancing.
- Early, deferred-simultaneous, and deferred-sequential circuits with timing-matched null arms.
- Signed `+45°/-45°`, `θ=0`, and canceling-rotation mutation controls in every relevant context.
- Compiler evidence that the mutation survives optimization and has matched exposure.
- Multiple gap durations with a frozen response model. A decay-shaped result alone does not identify resonator backaction.
- Isolated versus parallel execution and spectator-state controls.
- Leakage-sensitive diagnostics; binary readout alone cannot identify leakage.
- Calibration bracketing, executed-order records, and a block/dependence model that addresses the recorded approximately 50 Hz structure.
- Power, multiplicity, uncertainty propagation, stopping, missingness, and failed-job rules.
- Separate written cases, cost estimates, and user approvals for each acquisition stage.

The current documents appropriately describe these items as prospective. The implementation cannot yet support a causal mechanism claim.

## Nonblocking but material findings

### MEDIUM — Frozen QX conformance checks selected statistics rather than the full outcome law

The checker evaluates nine herald counts, six joint counts, and three signed sums at [qi_projector_conformance.py:19](../../../scripts/qi_projector_conformance.py). It does not check B-bit outcomes, complete local-pattern support, or a wrong-endian negative control.

Independent raw reconstruction supplied the missing diagnostic confidence:

- Every raw file contained exactly 2048 width-9 strings.
- Raw histograms matched `results.json`.
- Recorded SHA-256 digests matched.
- Correct right-to-left decoding produced zero impossible local outcomes.
- Deliberately reversed decoding produced 1523, 3072, and 2048 impossible outcomes across the three circuits.
- The maximum absolute standardized residual across supported local patterns was approximately 1.99.
- Every one of the 18 frozen conformance checks passed.

A separate diagnostic replay should preserve those complete-distribution and endianness checks. The frozen preregistered decision rule should remain immutable.

### MEDIUM — QX data cannot establish shot independence or hardware behavior

The QX shot records lack per-shot timestamps and a provider RNG independence certificate. Lag scans through 64 shots produced maximum absolute autocorrelations of roughly 0.047–0.065, with no decisive anomaly, but those scans cannot prove independence. The design correctly conditions its concentration statement on independence at [tuna-projector-geometry.md:152](../../../docs/design/tuna-projector-geometry.md).

QX also omits Tuna’s early-measurement register behavior. QX validates logical terminal distributions and register interpretation; it does not qualify early-bit retention, measurement backaction, device timing, or Tuna calibration.

### MEDIUM — The bounded hardware controls cannot identify a physical mechanism

The all-zero and all-one circuits can expose gross state-retention and readout failures. They do not determine the four-state correlated A/C assignment matrix. The all-one arm also combines state preparation, simultaneous drive, spectator context, and readout response—precisely the interactions already recorded around Tuna qubit 13.

The geometry circuit fixes angle to physical placement, uses parallel replicas, and lacks fresh T1/T2 or readout-duration measurements. The recorded 300 ns versus older 800 ns readout-duration discrepancy remains a timestamped limitation. The batch can qualify a bounded instrument/register path; it cannot identify projector geometry or measurement-induced backaction.

## Sound portions

- The first-principles projector calculation is correct.
  \(P=(I+Z_A)/2\),
  \(Q_\theta=[I+(\cos\theta Z_A+\sin\theta X_A)Z_B]/2\),
  and the two nonzero eigenvalues of \(P Q_\theta P\) are \((1\pm\cos\theta)/2\).

- The predicted moments are correct: \(m_1=1/2\), \(m_2=(1+\cos^2\theta)/4\), and variance \(\cos^2\theta/4\).

- The `Ry(-θ)`–parity–`Ry(+θ)` construction implements the stated ancilla-zero matrix element. The signed X-basis prediction \(\sin\theta\cos\theta/2\), including the `±45°` sign reversal, is correct.

- The canceling-rotation mutation correctly reduces the measured projector to the `θ=0` form.

- The pure-versus-mixed-input discussion is appropriately bounded. Equal B-basis populations reproduce the relevant A/C statistics without certifying mixedness or inter-sector coherence.

- The early/deferred equivalence statement is valid under its explicit commutation and data-only-evolution assumptions. The document appropriately treats physical timing and detector context as nuisance variables outside that algebraic identity.

- The three physical triples use edges present in the recorded Tuna topology. The proposal avoids the documented absent `10–11` edge.

- QX circuit compaction avoids relying on an emulator early-measurement bit that QX cannot preserve.

- The QX approval, submission, circuits, manifest, raw strings, results, and conformance digests form a coherent chain. The QX authorization expressly excludes Tuna hardware.

- The three QX jobs completed with 2048 shots each. Total recorded execution time was 1.254351 seconds; transaction records were empty. Actual execution order was mutation, geometry-Z, then geometry-X. The conformance claims are order-insensitive.

- The source notes consistently distinguish:
  - Exact projector identities.
  - Numerical Grassmannian/SVD checks.
  - Algebraic source proofs under explicit premises.
  - QX finite-shot emulator conformance.
  - Prospective physical claims.

  The Grassmannian code does not prove a Tuna mechanism. `BranchSignedCoherence.v` proves algebraic signed identities under stated premises rather than Born sampling or device behavior. The design respects both boundaries.

## Local verification and unrun checks

Completed deterministic checks:

- Focused Ruff formatting and lint checks passed.
- Focused mypy checking passed.
- Twenty-five focused pytest cases passed; three temporary-directory cases were deselected because the read-only filesystem offered no writable pytest temporary root.
- The recorded QX conformance replay matched all 18 checks.
- Proposal and run circuit/manifest comparisons matched byte-for-byte.
- Source and compiled hashes matched the compiler receipt.
- `git diff --check` for the reviewed commit passed.
- Independent raw-string statistics, support checks, bit-order falsification, block summaries, and lag scans completed without writing artifacts.

Unrun checks:

- `test_batches_and_fresh_output`
- `test_manifest_bit_order_and_provenance`
- `test_collection_requires_manifest_shot_count`
- Full repository lint, type, test, and gate suites
- A fresh local Quantum Inspire compiler replay
- A replay of the Rocq certificates
- Builds/tests of the external Grassmannian source tree
- Reading the unavailable local copy of the exact-factoring manuscript
- Provider status, topology, compiler configuration, limits, queue, pause, account, ledger, and free-use queries
- Remote compilation, submission, collection, or cancellation
- Credential access
- QRNG acquisition
- Stochastic simulation
- Tuna joint-readout calibration
- Tuna early-bit retention qualification
- Angle-by-placement rotations
- Early/deferred/deferred-sequential comparisons
- Hardware signed and mutation controls
- Gap-response experiments
- Spectator and isolated-versus-parallel experiments
- Leakage diagnostics
- Fresh device timing, T1, T2, assignment, or readout-duration measurements
- Shot-timestamp/IID validation

## Verdicts

| Scope | Verdict | Permitted conclusion |
|---|---|---|
| QX conformance | **PASS, narrowly scoped** | The six compact logical circuits, recorded bit order, selected joint laws, and signed observable conform on QX within the frozen finite-shot checks. The result establishes neither Tuna behavior nor a physical mechanism. |
| Three-circuit Tuna qualification | **HOLD at HEAD; conditionally suitable after fixes and complete live admission** | After replayable compiler admission, a frozen qualification analyzer, the expanded live structural checks, and explicit user approval, the exact all-zero/all-one/geometry batch is suitable only for bounded state-retention and register-path qualification. Its written estimate of 12,288 shots and approximately 14.31264 seconds is arithmetically correct. Zero credits remain a live-term condition rather than a guarantee. |
| Full causal campaign | **NOT READY** | The causal estimand, controls, timing matches, joint calibration, counterbalancing, dependence model, leakage diagnostics, and acquisition plans remain incomplete. A qualification result cannot be promoted into a projector-law or measurement-backaction claim. |

This review grants neither provider approval nor authority to enlarge the acquisition. Any change to circuit or manifest bytes requires renewed case binding and user approval. Tool-tracked review time was approximately 7 minutes.

REVIEW_COMPLETE

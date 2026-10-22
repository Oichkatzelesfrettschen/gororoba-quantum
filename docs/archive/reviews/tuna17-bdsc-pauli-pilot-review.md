# Review: Tuna-17 BDSC Pauli pilot (adversarial, stability, literature)

Read-only review by Codex CLI (gpt-daybreak-blue-latest, medium effort) of
main f2ebcbe, 2026-10-22: the written case, `scripts/qi_bdsc_pauli_cases.py`,
the design, the runbook and the retained case series. Its findings were fixed
on branch `qi/bdsc-pauli-pilot-review` (PR #349) in commits 14235db and
b3a2507. One fix departs from the review: F8 proposed the pooled kernel +
bright - 1 mean as a primary endpoint, but a coherent error moves the four
pair residuals by +0.15, +0.15, -0.15 and -0.15, which the mean cancels; the
primary test is the per-patch chi-square of the pair residuals instead. The
review's live-page checks did not run (its sandbox had no network); the
provider pages were read live afterwards and are quoted in
[usage.md](../../notes/quantum_inspire/usage.md#what-the-provider-requires).
File references below are repository paths at f2ebcbe.

The ideal algebra and circuit construction are sound. The acquisition is not ready for approval. One P1 defect allows hardware work to continue after a preregistered stop; several P2 defects make the corrected-score and phase interpretations stronger than the implemented statistics support.

## Findings

### F1 - P1: Stop conditions do not gate subsequent submissions

Claim attacked: batch 00 assignment error, bracket drift, a failed job, a short shot list, or a failed QX control stops the series before more hardware is used.

Authority: runbook:65 (`docs/runbooks/bdsc-tuna17-pauli-pilot.md:65`), case:51 (`docs/local/CASE-tuna17-bdsc-pauli-pilot.md:51`), reference CLI:1970 (`scripts/qi_bdsc_pauli_cases.py:1970`), submission guard:625 (`scripts/qi_platform.py:625`).

Failure scenario: `--references` can report batch-00 `P(0|1) = 0.20` and still exit zero. It does not require full shot counts. The submission command checks backend status, capacity, queue, circuit count, shots, and pause, but consumes neither batch order nor a stop-clear receipt. Batch 01 can therefore be submitted after batch 00 has already invalidated the case. The final analysis then withholds its top-level contraction and phase results, turning the later hardware jobs into guaranteed waste. The QX "any cell off ideal stops" condition is likewise an operator instruction rather than an enforced verdict.

Fix: implement a series state machine. Every post-00 submission must consume a digest-bound receipt proving that the preceding batch was collected, had full shots, and cleared every applicable stop. `--references` should return nonzero when a stop fires. The QX analysis needs an explicit pass/fail verdict tied to its intended interval criterion.

### F2 - P2: The product-channel correction is used after the experiment detects that its model is false

Claim attacked: `score_readout_corrected` is a readout-corrected physical score with a 95 percent interval.

Authority: design:176 (`docs/design/bdsc-tuna17-pauli-pilot.md:176`), correction:1223 (`scripts/qi_bdsc_pauli_cases.py:1223`), context diagnostic:1343 (`scripts/qi_bdsc_pauli_cases.py:1343`), stack analysis:177 (`docs/local/tuna17-stack-decomposition.md:177`).

Failure scenario: retained evidence gives q13 `e10` near 0.046 with q11 idle and 0.091 with q11 excited. A witness leaves q11 outcome-dependent, while readout-1 prepares it excited. The repository's own model produces corrected kernel and bright biases near -0.0078 and +0.0078, about four stated standard errors. Nevertheless, neighbor-context flags neither stop nor invalidate the independent four-qubit tensor correction. Its bootstrap also draws each qubit's reference rate independently, discarding joint calibration-shot covariance.

Fix: make the raw score the primary estimand. Rename the inverted value a tensor-product-model mitigation estimate and state that its interval is conditional on that model. Withhold affected patch estimates when context diagnostics reject independence, or fit and jointly bootstrap a declared conditional assignment channel with enough calibration patterns to identify it.

Nation et al. explicitly distinguishes the tensored assignment model from correlated mitigation. The retained primary source inspected was `https://arxiv.org/pdf/2108.12518v1`: (retained in the repository as `docs/pdf/2108.12518v1.pdf`)

### F3 - P2: The phase estimator combines sine and cosine channels with different physical visibility

Claim attacked: `atan2(S,C)` separates a single branch phase from damping.

Authority: design:161 (`docs/design/bdsc-tuna17-pauli-pilot.md:161`), especially the admitted neighbor-context difference at design:168 (`docs/design/bdsc-tuna17-pauli-pilot.md:168`), and implementation:1458 (`scripts/qi_bdsc_pauli_cases.py:1458`).

Failure scenario: the quadrature batch supplies `S`, while different witness circuits supply `C`. If the true phase is 0.1 rad, quadrature visibility is 0.70, and witness visibility is 0.85, the implementation returns 0.0825 rad. The 0.0175 rad bias is roughly three times the design's stated 0.006 rad error. Neighbor activity, drift, basis-pulse error, and readout context can all produce unequal visibility.

Fix: acquire sine and cosine quadratures with matched preparation, neighbor activity, calibration bracket, and temporal block. Alternatively, use a preregistered analysis-phase scan and sinusoidal fit. A two-point estimator needs an explicit equal-visibility falsifier and a joint covariance model.

### F4 - P2: Phase remains "significant" when visibility is unresolved

Claim attacked: the scalar delta-method `phi_se` supports a phase test throughout the estimator's input domain.

Authority: implementation:1481 (`scripts/qi_bdsc_pauli_cases.py:1481`).

Failure scenario: the verified probe `S = 0`, `C = -0.005`, unit parity variance, and 32768 shots per cell yields `V = 0.005`, `phi = pi`, `phi_se = 0.78125`, and `z = 4.021`. Visibility is only about 1.28 standard errors from zero. Phase is unidentified at zero amplitude, but noise on the negative cosine axis becomes a phase violation.

Fix: test the two-dimensional amplitude `(S,C)` against zero first and withhold phase when visibility lacks support. For admitted amplitudes, use a joint bootstrap or circular confidence region.

### F5 - P2: The bootstrap has zero-width boundary intervals

Claim attacked: the parametric bootstrap propagates finite-shot witness and assignment uncertainty.

Authority: bootstrap:1096 (`scripts/qi_bdsc_pauli_cases.py:1096`).

Failure scenario: 1000 observations concentrated in one score-zero outcome, with empirically perfect references, produced `[0.0, 0.0]` on repeated deterministic probes. Plug-in multinomial and binomial draws cannot leave an empirical probability of exactly zero or one. The resulting "95 percent" interval asserts zero uncertainty from finite data.

Fix: use a boundary-aware law, such as Dirichlet/Jeffreys draws for outcomes and beta draws for assignment rates, or a frequentist construction with established boundary coverage. Add all-zero and all-one witness and reference cases to the self-test.

### F6 - P2: A fired stop still emits inferential cell results

Claim attacked: a fired stop yields "no inference."

Authority: analysis order:1204 (`scripts/qi_bdsc_pauli_cases.py:1204`), stop classification:1262 (`scripts/qi_bdsc_pauli_cases.py:1262`).

Failure scenario: the program computes raw means, empirical-Bernstein and Wilson intervals, corrected scores, and bootstrap intervals for all 45 cells before it evaluates reference stops. A 0.20 batch-00 breach therefore returns `claim_kind = stopped` but still publishes inferential cell fields. A sufficiently poor assignment matrix can instead make inversion fail before any stopped record is constructed.

Fix: calculate the reference report immediately after validating shot counts. A stopped result should contain the stop and bounded operational diagnostics only. If raw summaries are retained, omit corrected estimates and inferential intervals and label them explicitly non-inferential.

### F7 - P2: Submission does not bind the live topology, gate set, or compiler contract

Claim attacked: the selected CZ paths and native `X90`/`mY90` readout survive to execution.

Authority: design:23 (`docs/design/bdsc-tuna17-pauli-pilot.md:23`), builder:833 (`scripts/qi_bdsc_pauli_cases.py:833`), live submission checks:629 (`scripts/qi_platform.py:629`).

Failure scenario: generation validates a retained catalogue. Submission compares the live backend for identity, status, width, limits, queue, and pause, but not topology, gate set, or `default_compiler_config`. A service-side compiler or topology change can rewrite, reject, or relocate the intended circuit without invalidating the approval record.

Fix: put expected topology, gate-set, and compiler-configuration digests in each case manifest. Compare them with the freshly fetched backend before the first remote write and require regenerated toolchain evidence after any mismatch.

### F8 - P2: The violation language ignores multiplicity and alternative causes

Claim attacked: any `|z| >= 3` violation names a multi-qubit error outside contraction.

Authority: preregistered claim:151 (`scripts/qi_bdsc_pauli_cases.py:151`), contraction tests:1406 (`scripts/qi_bdsc_pauli_cases.py:1406`), quadrature tests:1491 (`scripts/qi_bdsc_pauli_cases.py:1491`).

Failure scenario: the analysis exposes up to 40 unadjusted three-sigma flags across contraction pairs, pooled values, middle/sector cells, phases, and nulls. Under independence, the probability of at least one false flag is about 10.25 percent; the actual correlated family error is unquantified. Drift, context-dependent SPAM, and model mismatch can also violate the simple contraction without identifying coherent multi-qubit error or leakage.

Fix: preregister a small primary endpoint family with simultaneous error control, label other tests exploratory, and phrase a violation as falsifying the stationary contraction-plus-readout model rather than identifying a mechanism.

### F9 - P2: The stack decomposition reviews the superseded design as though it were current

Claim attacked: the stack note describes the retained 24-job case.

Authority: scope:3 (`docs/local/tuna17-stack-decomposition.md:3`), stale budget:186 (`docs/local/tuna17-stack-decomposition.md:186`), stale proposals:247 (`docs/local/tuna17-stack-decomposition.md:247`).

Failure scenario: the note still reports the old Latin layout, absent quadrature, incomplete batch-00 calibration, decomposed readout rotations, 18 toolchain rows, and six batches. It then proposes changes already present in the retained eight-batch, 24-job case. A reviewer can reject current circuits for defects already repaired or use the wrong resource budget.

Fix: archive and label the note as a pre-`c26a991` analysis, or reconcile every gate census, timeline, batch count, and risk statement to the retained case.

### F10 - P2: The runbook requests a fresh calibration surface the provider does not expose

Claim attacked: the operator obtains fresh placement, readout rates, and calibration before batch 00.

Authority: runbook:64 (`docs/runbooks/bdsc-tuna17-pauli-pilot.md:64`), provider note:25 (`docs/notes/quantum_inspire/tuna-17.md:25`).

Failure scenario: Quantum Inspire publishes no Tuna calibration dataset. A fresh catalogue/status read cannot provide current assignment rates, so the instruction is either impossible or invites stale rates to masquerade as current calibration.

Fix: enumerate the available fresh surfaces: identity, status, topology, gates, compiler configuration, and queue. State that batch-00 readout-0/readout-1 is the first fresh assignment measurement and must clear before any witness submission.

### F11 - P3: The QX manifest incorrectly includes hardware pauses

Authority: cost function:740 (`scripts/qi_bdsc_pauli_cases.py:740`), QX manifest:1065 (`results/quantum_inspire/cases/bdsc_pauli_qx/batch-00/cases.json:1065`).

The manifest records eleven 120-second pauses and `wall_seconds = 1452.7`, while the runbook correctly says the hardware pause does not apply to QX. Parameterize the cost by backend class and record zero QX pause.

### F12 - P3: Raw-shot parsing accepts non-binary characters

Authority: shot parser:1033 (`scripts/qi_bdsc_pauli_cases.py:1033`).

`shot_bits(["xxxx"], 4)` produces integer value 72 in every column rather than an immediate format error. Reject every character outside ASCII `0` and `1`, and include the batch/file identity in the error.

### F13 - P3: The M3 literature summary conflates solver scalability with correlated calibration

Authority: literature note:200 (`docs/notes/quantum_inspire/shot-record-literature.md:200`).

Nation et al.'s linear calibration statement concerns the tensored single-qubit model. Its reduced-subspace solver can consume correlated assignment elements, but those elements still require a separately specified correlated channel and calibration. Split those claims.

### F14 - P3: The phase method lacks an exact literature comparator

Authority: design:145 (`docs/design/bdsc-tuna17-pauli-pilot.md:145`).

The ideal derivation is original and valid, but the prose can be mistaken for standard GHZ parity-oscillation or multiple-quantum-coherence practice. Call it a repository-derived fixed-quadrature estimator, cite the chosen comparator, and state explicitly that it uses two fixed bases from unmatched acquisitions instead of an analysis-phase scan.

## Sound results

- `E0 = I/2 - YIXY/4 + YZXY/4`, the little-endian encoding, and the score signs replay exactly against `cd_core`, `bdsc.ideal_effect()`, and `bdsc.projector()`.
- `X90` maps Y readout to Z and `mY90` maps X readout to Z with the implemented sign convention.
- All 12 state preparations and the quadrature closed forms pass statevector checks; the maximum discrepancy is `1.0e-15`.
- The YZXY local-basis grouping is correct because the two nonidentity Pauli words are qubit-wise commuting.
- The 13-basis lower bound is valid for local product-basis readout and is correctly limited to that measurement class.
- The pooled contraction variance includes within-circuit cross-patch covariance without requiring covariance inversion. Constant-score singular covariance is handled.
- Bootstrap streams are deterministic from `SeedSequence([20261022, index])` and ordered mapping.
- The Tuna series has eight batches of three circuits, 24 jobs, and 32768 shots per job. All six GHZ-path CZ edges occur in the retained coupling map.
- The retained timing arithmetic is internally correct: 479.2 seconds execution plus seven 120-second pauses equals 1319.2 seconds. That estimate remains a budget model, not an executed-duration guarantee.

## Literature and online visibility

Actually read:

- Nation et al., `https://arxiv.org/pdf/2108.12518v1`.
- Retained IBM qubit-wise-commuting grouping guide: `https://quantum.cloud.ibm.com/docs/en/guides/execute-dynamic-circuits`.
- Retained IQM GHZ multiple-quantum-coherence example: `https://docs.iqm.tech/4.7/iqm-benchmarks/examples/example_ghz.html`.
- Retained cQASM `R_n` specification: `https://qutech-delft.github.io/cQASM-spec/latest/standard_gate_set/single_qubit/sq_Rn.html`.

Not read:

- Bravyi et al. primary PDF and DOI `10.1103/PhysRevA.103.042605`; the local PDF is absent. Only the repository note's bounded title/abstract/introduction extraction was available.
- Mooney et al., DOI `10.1088/2399-6528/ac1df7`; the IQM documentation cites it, but the primary paper is absent.
- A primary qubit-wise-commuting grouping paper; none was retained.
- Current live Quantum Inspire, cQASM, IBM, IQM, arXiv, and publisher pages. The in-app browser was unavailable, Playwright lacked its browser binary, and direct HTTP failed DNS resolution.

## Verification and boundary

Passed:

- Pauli replay: 84 blade effects, 21 probes, 28 words, 13 bases.
- Case regeneration: all 82 retained files matched byte for byte.
- Full synthetic self-test: ideal, depolarized, readout-biased, coherent, branch-phase, drift, breach, context, and twin cases passed.
- Retained toolchain check: 1175 circuit records matched their bytes, backends, and compiler configurations.
- Mypy passed for all three reviewed Python files.
- Installed Ruff 0.14.11 format and lint passed with cache disabled.
- `git diff --check` passed.
- Final `git status` remained clean on `qi/bdsc-pauli-pilot-review`.

Not run:

- Pinned Ruff 0.17.1: uv could not create its cache lock in the read-only filesystem.
- Live toolchain recompilation: `QI_PYTHON` was unset; the retained record was checked without recompiling.
- Local qxelarator series: its interface necessarily writes run directories.
- Any provider query, job, upload, comment, or submission: prohibited by the review boundary.

No file changed and nothing was submitted. Tracker status is complete; metered usage was 681,494 tokens over about 7 minutes 26 seconds.

## Verdict

The algebraic target, emitted Clifford preparations, native basis rotations, placement connectivity, and deterministic case generation deserve trust. The proposed hardware acquisition does not yet deserve approval. The first required repair is a machine-enforced, digest-bound stop-clear chain between collected batches and later submissions. After that, the corrected-score and phase claims must be narrowed or redesigned around their actual model assumptions: correlated readout context, matched quadrature visibility, identifiable phase, and family-wise inference.

| Finding | Severity | File:line | One-line fix |
|---|---|---|---|
| F1 | P1 | `scripts/qi_bdsc_pauli_cases.py:1970` | Bind every later submission to a collected, full-shot, stop-clear predecessor receipt. |
| F2 | P2 | `scripts/qi_bdsc_pauli_cases.py:1223` | Withhold or context-condition tensor mitigation when neighbor diagnostics reject independence. |
| F3 | P2 | `docs/design/bdsc-tuna17-pauli-pilot.md:161` | Measure sine and cosine in matched contexts or use a phase scan. |
| F4 | P2 | `scripts/qi_bdsc_pauli_cases.py:1481` | Gate phase inference on statistically supported visibility. |
| F5 | P2 | `scripts/qi_bdsc_pauli_cases.py:1096` | Use boundary-aware multinomial and assignment-rate uncertainty. |
| F6 | P2 | `scripts/qi_bdsc_pauli_cases.py:1204` | Classify stops before computing or emitting inferential cells. |
| F7 | P2 | `scripts/qi_platform.py:629` | Bind submission to live topology, gate-set, and compiler digests. |
| F8 | P2 | `scripts/qi_bdsc_pauli_cases.py:151` | Control multiplicity and stop attributing model rejection to one mechanism. |
| F9 | P2 | `docs/local/tuna17-stack-decomposition.md:3` | Archive the note as historical or reconcile it to the 24-job design. |
| F10 | P2 | `docs/runbooks/bdsc-tuna17-pauli-pilot.md:64` | Name available live surfaces and make batch 00 the first fresh assignment calibration. |
| F11 | P3 | `scripts/qi_bdsc_pauli_cases.py:740` | Record zero pause for the QX emulator. |
| F12 | P3 | `scripts/qi_bdsc_pauli_cases.py:1033` | Reject non-binary shot characters with source identity. |
| F13 | P3 | `docs/notes/quantum_inspire/shot-record-literature.md:200` | Separate M3 solver scaling from correlated-channel calibration cost. |
| F14 | P3 | `docs/design/bdsc-tuna17-pauli-pilot.md:145` | Label and cite the fixed-quadrature method as distinct from standard GHZ scans. |


# Peer-review report

Launch metadata reports `gpt-daybreak-blue-latest`, high reasoning effort, default tier.

Artifact fields: retained quantum-hardware acquisition, conditional-martingale statistics, immutable evidence serialization, reproducible analysis, and timestamped provider-API observations.

## Findings

### FATAL

None.

### SERIOUS

None.

### SLOPPY — ancillary API-equivalence evidence is attestational, not locally replayable

The primary acquisition is independently replayable. The post-acquisition `/final_results/job/{id}` equivalence claim is weaker.

`destination-job-artifact-observations.json` retains response-object hashes and response shapes, while `destination-final-result-equivalence.json` retains Boolean equivalence assertions and hashes of the repository raw files (`docs/evidence/tuna-projector-geometry/destination-job-artifact-observations.json:575-579`; `docs/evidence/tuna-projector-geometry/destination-final-result-equivalence.json:2-126`). The equivalence rows do not bind the corresponding provider-response object hashes, retain a sanitized response projection, or identify a locally available producer. Repository search found only prose consumers of these records.

Consequently, local evidence confirms that the retained summary *records* six matching endpoint responses, but another reviewer cannot independently derive those Boolean checks from retained provider payloads. This does not affect the frozen three-job result, whose raw strings and result records are retained and replayed independently.

Future read-only investigations should retain either:

- sanitized response objects sufficient to recompute every equality; or
- a deterministic checked producer binding each response-object hash to the retained raw/result hashes and field projection.

Confidence: high. Severity remains SLOPPY because this concerns an ancillary API-availability investigation, not the primary acquisition or decision.

## SOUND — completed acquisition and frozen decision

Independent raw-string recomputation confirms:

- Jobs `1620359`, `1620485`, and `1620614`, each with 4096 width-20 shots.
- Total reported execution time `16.783859` seconds.
- Empty transaction lists in all three collected results.
- Queue intervals `496.451396`, `503.073686`, and `1936.258985` seconds.
- Successor creation followed predecessor finish by `46.329855` and `45.412798` seconds and followed raw collection in both cases.
- Every raw histogram equals the retained ordered strings.
- All nine inverse-decoded four-cell tables equal the canonical analysis.

The recomputed summary is exactly:

- `max |D| = 0.019287109375`
- maximum absolute response-interval endpoint `0.058683428002`
- `max |R| = 0.021728515625`
- maximum absolute baseline-interval endpoint `0.067219465953`

All 12 response and 12 endpoint intervals therefore lie inside the preregistered ±0.10 boundary. The frozen result, **objective established within scope**, is correct.

Qubit 11 early/terminal disagreement independently recomputes to `2788 / 2687 / 2762` shots. Its early-one counts are `1320 / 1404 / 1361`, while terminal-one counts are `3794 / 3763 / 3745`. The evidence report records these values and properly refuses to translate binary labels into populations or QND behavior (`docs/evidence/tuna-projector-geometry/nominal-one-destination-response.md:40-78`).

The statistical wording is appropriately narrow. The simultaneous bound concerns fixed, selected realized predictable contrasts under adapted shot dependence. It does not establish stationary repeated-run means, physical populations, or causal effects. Three jobs remain three intervention units (`docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md:9-30,47-53`).

## SOUND — serialization defect reconciliation

The encoding defect is genuinely reconciled, not ignored:

- The original runtime `analysis.json` remains byte-preserved.
- Direct frozen-analyzer `--check` against runtime bytes fails, as expected.
- Direct `--check` against `analysis-canonical.json` passes.
- The new consumer freshly executes the complete frozen analyzer, validates the exact completed executor state, and permits only valid complete-case outcomes (`scripts/qi_tuna_destination_analysis_receipt.py:58-96`).
- It requires runtime bytes to equal the historical indent-one insertion-order writer and canonical bytes to equal the analyzer’s sorted indent-two contract (`scripts/qi_tuna_destination_analysis_receipt.py:97-105`).
- It checks 16 frozen producer/analyzer/note hashes, 40 acquisition inputs, both parsed objects, JSON number representations, unresolved attribution, refusal of retry, and refusal of physical continuation (`scripts/qi_tuna_destination_analysis_receipt.py:31-55,106-141`).

Normal and optimized (`-O`) checks both passed locally for the canonical analysis and serialization receipt. The current receipt producer hash, 16 frozen source hashes, and all 40 input hashes match actual files. The new gate invokes this consumer and declares runtime, canonical, and receipt replays (`ci/gates.json:5052-5059`).

The endpoint has not changed. The consumer reconciles two producer-specific encodings of the same fresh report. Future runners should use the canonical writer, while the acquired historical producer remains immutable.

## SOUND — registration and ledger

The read-only registry check passed with 285 claims and 319 acquisitions. The two older nominal-zero claim objects are byte-equivalent as parsed objects to commit `f7e85775b96cfbffd8b8982b0fb3e3317c54edc2`.

The new claim accurately states the bounded endpoint and exclusions (`docs/state/research_state.json:2240-2270`). Its replay gate and evidence hashes match the current canonical analysis and serialization receipt.

Independent ledger checking confirms:

- 432 retained jobs, up from 429.
- Exact rows for the three new job identities.
- Zero transaction rows.
- Empty `unretained`.
- The usage snapshot digest equals `destination-one-ledger-revalidation.json`.

Zero charge is therefore a retained snapshot observation, not a perpetual account guarantee.

## API and calibration interpretation

The retained records support only timestamped observations:

- Six stored-source digests reportedly matched their manifests; generated-sibling queries returned empty.
- The six final-result responses reportedly contained only execution time, requested/completed shots, histogram, and binary raw data.
- `/metadata/backend/7` returned HTTP 404.
- The observed OpenAPI contained 53 paths and zero metadata routes.
- One bounded quantum-job log request timed out after ten seconds.
- Grafana and a local direct probe both failed before HTTP while connecting to `131.180.205.138:443`.
- The remote Prometheus version remains unmeasured.

The prose handles those boundaries correctly (`docs/notes/quantum_inspire/destination-response-upstream-request.md:12-50`). A single timeout establishes failure of that request, not permanent route absence. A 404 and route inventory establish the served surface at the recorded time, not provider-side retention policy. Benchmarking status between the rotated and final jobs establishes context only; it does not prove recalibration or configuration change (`docs/evidence/tuna-projector-geometry/nominal-one-destination-response.md:31-38`).

## Scientific interpretation and future requirements

The evidence supports one statement: the selected nominal-one early/final response marginals meet the frozen descriptive ±0.10 comparison under its simultaneous 99% contract.

The evidence does not identify:

- physical state populations;
- QND behavior;
- projector geometry;
- destination causality;
- stationarity;
- served measurement schedules;
- integration windows or thresholds;
- acquisition-index reconstruction;
- calibration identity;
- apparatus memory.

The old six-job endpoint remains implementation route unavailable. The nominal-zero/nominal-one comparison remains retrospective.

Useful non-hardware evidence would be a per-event association trace, pre-packing labels, integrated IQ with discriminator configuration, served acquisition schedules, and job-specific calibration/configuration identities (`docs/notes/quantum_inspire/destination-response-upstream-request.md:52-84`). The support request remains unsent and this review grants no messaging authority.

The three completed jobs need no new approval. Any further hardware requires a new written case and approval accounting for the measured `1936.258985`-second wait, benchmarking context, fresh queue conditions, job-level assignment, and carryover controls (`docs/notes/quantum_inspire/destination-response-upstream-request.md:133-137`).

## Checked and unrun surfaces

Checked locally:

- Relevant root, `scripts/`, and `ci/` AGENTS instructions.
- Entire new consumer and its test module.
- Frozen analyzer/runner writer integration.
- All three raw files, manifests, results, completion receipts, state, approval, and analyses.
- Normal and `-O` canonical and serialization-receipt replays.
- Expected runtime-byte failure.
- All 40 receipt-input and 16 frozen-source hashes.
- Independent decoder, counts, contrasts, timing, ordering, histogram, and ledger recomputation.
- Research-state validation.
- Frozen source/proposal diff against commit `f7e85775b96cfbffd8b8982b0fb3e3317c54edc2`.
- `git diff --check`.

Unrun or unavailable to this review:

- Provider/network/API access and fresh live observations.
- Credential access, submissions, uploads, emulators, cancellation, or messages.
- Independent replay of the 21 pytest cases requiring writable temporary directories.
- Full 300-test suite and pinned Ruff/mypy.
- Compiler replay.
- Reconstruction of the post-acquisition endpoint-equivalence booleans from unretained provider response bodies.
- Pending final retention-verification and plan-step receipts.

## Verdict

**Bounded PASS for primary acquisition retention, frozen statistical interpretation, serialization reconciliation, ledger registration, and the stated scientific limits.**

The serialization defect is repaired without rewriting history or changing the endpoint. No physical cause has been identified. The ancillary API-equivalence summary has the provenance limitation described above and should remain an observation record rather than an independently replayed result. Further hardware requires a new approved, queue-aware and temporally controlled case.
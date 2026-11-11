# Ascella–Belenos offline network records

Inspect a proposed case and a normalized terminal joint histogram with
[`scripts/qd_network_analysis.py`](../../scripts/qd_network_analysis.py).
The reusable reader and scorer live in
[`gororoba_quantum/qd_network_records.py`](../../gororoba_quantum/qd_network_records.py).
Both schemas are local scientific interchange formats. They do not describe
an available Quandela joint-device endpoint.

The [design](../design/ascella-belenos-entanglement-teleportation.md) owns
the physical claim levels, apparatus gates and protocol. The
[dated provider assessment](../evidence/quandela/remote-result-contract/provider-assessment.json)
records the later response about calibration and result semantics. Its
`body_sha256` identifies the provider's comment body as read at the
assessment's `observed_at`; the body bytes are not retained in the
repository, and the six `provider_statements` are the assessor's paraphrases
recorded on that date. Neither the digest nor a paraphrase can be checked
offline. A reader who fetches the comment compares its UTF-8 bytes with the
digest, and a mismatch means the provider edited the comment after the
assessment (the comment was already updated once, on 2026-11-03). The
[plan record](../state/plans/ascella-belenos-entanglement-teleportation.json)
owns implementation status. None establishes a qualified Ascella–Belenos
physical route.

## Scope and admission

Version 1 handles a terminal, single-hop C3 proposal with a Phi+ resource,
the existing partial Bell analyzer, six equiprobable Pauli input states,
and X/Y/Z receiver measurements. It supports either declared transfer
direction. Each declared acquisition block contains 18 distinct
input/analyzer cells when complete. The receiver is measured; this format
does not assert that its quantum state survives the acquisition.

Every report keeps `execution_admitted` and `physical_claim_admitted`
false. A case's `review_ready` means that the supported declarations are
complete. It does not check the truth of an evidence declaration, inspect
the referenced evidence bytes, validate an approval, or authorize a job.
A joint record remains `descriptive_only` with `review_ready: false`:
there is no supported provider adapter proving its raw-to-normalized
derivation and no physical or inferential certification in this reader.

Use the [pending case](../evidence/quandela/network-records/pending-case.json)
as a typed inventory. Its revision pins the evidence baseline from which
this implementation was developed. Its unknown physical, budget,
approval and payload fields remain null. Change those fields only when
the corresponding evidence exists. Do not substitute the provider's
partial calibration reply for a route, attempt-denominator, or complete
observation contract.

## Run the offline inspection

Run these commands from the repository root with its pinned runtime and
dependencies. Set `PYTHON` to that interpreter's absolute path. Apply the
[compute environment](compute-flags.md) for the host; the small
inspection below uses two workers and one BLAS/OpenMP thread per process.

```sh
env GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
  GOROROBA_WORKERS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  "$PYTHON" scripts/qd_network_analysis.py \
  docs/evidence/quandela/network-records/pending-case.json \
  --out /tmp/ascella-belenos-pending-assessment.json \
  --require-review-ready
```

The pending case produces a report and exits 1 because its declarations
are unresolved. Omit `--out` to write the report to standard output. Exit
0 without `--require-review-ready` means that a valid descriptive report
was produced.

Inspect a future normalized joint record and bind supplied source bytes:

```sh
env GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
  GOROROBA_WORKERS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  "$PYTHON" scripts/qd_network_analysis.py /path/to/joint-record.json \
  --case /path/to/case.json \
  --raw-result /path/to/provider-result.json \
  --payload /path/to/submitted-payload.json \
  --out /tmp/ascella-belenos-joint-analysis.json
```

Supply `--payload` only when the record declares its digest. Omitted
binding inputs appear as `unverified`. The CLI reads each supplied input
as one bounded byte snapshot, hashes the parsed snapshot, and refuses
inputs larger than 64 MiB. It rejects a report destination that resolves
to any input or bound-source path. It writes the complete report through
a temporary sibling and atomic replacement only after validation and
binding succeed. An invalid binding leaves any existing report intact.

| Exit | Meaning |
|---|---|
| 0 | Produced a structurally valid report; no execution or physical claim is admitted. |
| 1 | Produced a report, but `--require-review-ready` found unresolved review requirements. Joint records always retain this hold in version 1. |
| 2 | Refused malformed input, an inconsistent binding, an oversized source, or an invalid/unwritable path. |

The command performs no provider operation. It does not construct or
submit a live payload, join independent jobs, spend credits, or change
the source artifacts.

## Case contract

Use `schema: qd-network-case-v1`, `status: draft` or `review_candidate`,
and `admission: blocked`. `case_template(full_git_revision)` returns the
complete field set with unresolved values null. Unknown or missing keys
are errors; copy the actual template instead of assembling a partial
case object.

| Field group | Required representation |
|---|---|
| Identity | Nonempty `source_repository`; lowercase 40-character `source_revision`; `teleportation_A_to_B` or `teleportation_B_to_A`; both local platform IDs. |
| Supported claim | `claim_level: C3`, `output_capability: O0`, `logical_frame_convention: receiver_byproduct_Xx_Zz`. Other declared C0–C6/O0–O3 values are retained as unsupported scope and cannot be review-ready. |
| Ensemble | `uniform_pauli_six`, six exact `"1/6"` probability strings, physical-preparation evidence and an accepted-multiphoton bound in [0,1] or null. |
| Analysis | `output_measurements: ["X", "Y", "Z"]`, `base_setting_cells: 18`. |
| Physical contracts | Joint platform ID; route, resource factory, Bell instrument, joint result, attempt-denominator, effective-processing and calibration evidence. |
| Statistical contract | Benchmark-certificate evidence; a `uniform_six_success_weighted_fidelity` estimand, alpha strictly between zero and one, systematic allowance in [0,1], `fixed_attempts` stopping rule, positive integer `attempts_per_cell`, and unique planned `block_ids`. |
| Limits and authority | Positive `max_jobs` and `max_seconds`, nonnegative `max_credits`, approval-record evidence, and a lowercase SHA-256 payload digest; unresolved entries stay null. |

Every evidence field is either null or an object with exactly four keys:

```json
{
  "status": "unknown",
  "reference": null,
  "sha256": null,
  "reason": "Acquisition-bound evidence is not available."
}
```

The allowed statuses are `unknown`, `documented`, `unavailable` and
`conflicting`. Supply reference and digest together. `documented`
requires both; every other status requires a reason. A syntactically
valid digest is a declaration until the referenced bytes are actually
verified. Case inspection lists `byte_verified_evidence: []` explicitly.

## Normalized joint-record contract

Use `schema: qd-network-joint-v1` and
`representation: joint_histogram`. Retain a true joint observation over
the Bell and receiver detectors. Independent Ascella and Belenos
marginals, common timestamps, API job ordering, and matching row counts
do not supply that observation.

| Field group | Required representation |
|---|---|
| Provenance | `data_origin: synthetic` or `measured`; full `protocol_revision`; case and raw-result SHA-256 digests; nullable payload digest. |
| Apparatus | `joint_job_id`, nullable `joint_platform_id`, both `apparatus_ids`, nullable `route_id`, and the case's transfer direction/frame convention. These are declarations. |
| Processing | `processing_status: raw_detector_counts`, `processed_counts`, or `unknown`; a string array `processing_chain` preserving the declared transformations. |
| Assumptions | Exactly `fixed_channel`, `basis_independent_selection`, `setting_identity`, `input_label_isolation`, `single_copy_input`, `calibration_validity`, `raw_event_provenance`, `physical_route`, `resource_factory`, and `bell_instrument`; each uses the evidence representation above. |
| Coverage | Nonempty unique `block_ids`; a `cells` array. Declare an intended block even if it has no returned cells. Standalone inspection sees only these declarations; a bound case with a statistical contract also checks the planned block identities. |

Each cell has exactly these fields:

| Field | Meaning |
|---|---|
| `setting_id`, `block_id` | Unique setting identity and one declared acquisition block. |
| `calibration_id` | Nullable calibration identity. Different non-null identities inside one block are reported. |
| `input_label`, `analyzer_basis` | One of `+X,-X,+Y,-Y,+Z,-Z` and one of `X,Y,Z`. A block cannot contain duplicate input/basis cells. |
| `expected_configuration_id`, `applied_configuration_id` | Frozen setting identity and nullable acquired identity. Unknown or unequal applied settings remain explicit issues. |
| `attempts` | A typed source-trigger counter, as described below. |
| `reported_count` | Sum of every outcome row, including rejected rows. |
| `anomalies` | Exactly nonnegative integer `duplicates`, `unmatched`, and `missing` counts. Nonzero entries remain integrity issues. |
| `outcomes` | Joint rows with `bell_pattern`, `receiver_pattern`, `resource_herald`, and `count`. |

The Bell pattern has four threshold bits in `c0,c1,d0,d1` order. Receiver
occupations are two nonnegative integers. Preserve no-click, multiple
occupation, rejected Bell, and failed-resource rows. Duplicate joint
outcome keys are errors; sum identical raw outcomes during a separately
audited normalization. Integers range from zero to 2^63−1; booleans,
negative/fractional counts, non-finite numbers and duplicate JSON keys
are errors. Reported joint events cannot exceed a supplied source-trigger
count. The difference between triggers and reported events does not by
itself identify why an event was unreported.

An attempt counter contains exactly `value`, `population`, `status`,
`source`, and `reason`. Its population is always `source_trigger`.
Observed and modeled values are nonnegative integers. A modeled counter
requires its assumptions in `reason`. An unavailable counter has null
value and a reason. A requested shot cap, detected-shot/billing count,
photon-filtered sample count, or accepted-output count is not an optical
source-trigger count. Measured records with modeled attempts receive no
measured per-attempt or ensemble success-weighted score.

The complete key sets and parser are the executable contract. The
[reader tests](../../tests/gororoba_quantum/test_qd_network_records.py)
provide small, explicitly synthetic record examples. They do not use
retained hardware jobs as substitute joint acquisitions.

## Scoring and incomplete observations

The scorer reuses the frozen protocol's derived Phi+ frame table.
Patterns `1100` and `0011` carry `(x,z)=(1,0)`; `1001` and `0110` carry
`(1,1)`. An output is eligible only when the resource herald succeeds,
the Bell pattern is accepted and the receiver occupation sums to one.
For raw receiver bit `d`, decode X as `d XOR z`, Y as `d XOR x XOR z`,
and Z as `d XOR x`. The report retains every original normalized outcome
and the counts per Bell branch. Rejection categories are exclusive in
resource, Bell, then receiver order.

For each input i, use only its matching analyzer cell for fidelity.
Let a_i be accepted outputs, c_i correct outputs, and n_i source
attempts, summed over the supplied blocks for that input. The report
separates:

| Estimand | Definition | Availability |
|---|---|---|
| Per-input conditional fidelity | c_i / a_i | Null when a_i = 0. |
| Mean conditional fidelity | (1/6) sum_i c_i / a_i | Null if any input has no accepted matching output. |
| Pooled conditional fidelity | sum_i c_i / sum_i a_i | Describes the accepted mixture actually supplied; its input weights need not equal the declared prior. |
| Equal-prior success-weighted fidelity | sum_i (c_i / n_i) / sum_i (a_i / n_i) | Requires every declared block's matching cells and usable positive attempt denominators; null if total success is zero. |
| Equal-prior success probability | (1/6) sum_i a_i / n_i | Uses the same denominator requirements; equals zero for a completely observed zero-success ensemble. |

Do not discard a zero-success input to manufacture a six-input mean.
Do not replace the equal-prior ratio with pooled accepted counts when
the attempt allocations differ. The other twelve analyzer cells remain
in the report and in the 18-cell completeness check; they are not extra
observations of the matching-basis fidelity.

Inspect per-block reports before the pooled report. Different underlying
channels, input allocations or calibration states can make the pooled
descriptive ratio scientifically inappropriate. The reader does not
certify block exchangeability, basis-independent selection, independent
input preparation, or the single-copy assumption. It supplies no
confidence interval or quantum certificate. Apply an appropriate sampling
model and the existing certified classical benchmark only after their
prerequisites are established; a generic binomial or Hoeffding interval
does not automatically cover this estimated ratio.

## Byte binding and derivation

`--case`, `--raw-result`, and `--payload` compare the exact supplied
bytes with the declared digests. A mismatch is an error. A bound case
must also agree on the source revision, transfer direction, frame,
joint-platform ID, apparatus partition, payload digest, C3 claim, and
O0 output scope. When the case supplies a statistical contract, its
planned block identities must match the record's declared blocks.
Preserve unreturned planned blocks with no cells so the incomplete
coverage remains visible. Binding also reports cells below, above, or
without an observed fixed-attempt target; it does not reject descriptive
partial acquisitions merely for falling short. Unknown physical fields
remain unknown after hashing.

A matching raw-result digest establishes which raw bytes were supplied.
It does not prove that the normalized cells were produced from them.
`raw_to_normalized_derivation_verified` therefore remains false. Add a
provider-specific adapter only after an acquisition-bound observation
contract specifies joint event identity, selections, controls and
denominators. Test that adapter against actual retained raw records;
do not infer coincidences by pairing independent marginal records.

## Regression checks and remaining work

Run the reader, CLI, protocol-boundary and existing protocol/benchmark
tests with the pinned runtime:

```sh
env GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 \
  GOROROBA_WORKERS=2 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  "$PYTHON" -m pytest -q \
  tests/gororoba_quantum/test_qd_network_records.py \
  tests/scripts/test_qd_network_analysis.py \
  tests/scripts/test_qd_network_protocol_boundaries.py \
  tests/scripts/test_qd_network_protocol.py \
  tests/scripts/test_qd_classical_benchmark.py
```

The boundary suite checks product and incoherent resources, factorized
joint distributions, a missing frame correction, zero-success inputs,
label-informed classical fabrication, and basis-dependent witness
fabrication. These controls demonstrate why a high arithmetic score
does not establish its physical prerequisites.

The existing offline protocol, certified benchmark, local rehearsal and
secondary-analysis implementations remain the owners of their math.
This change adds record validation and the missing consequential
controls; it leaves their pinned historical producer bytes intact.
Provider raw normalization, optical link qualification, new QPU jobs,
live surviving output and sequential transfer remain blocked by the
physical gates in the design. Historical rehearsal outcomes remain
descriptive and retain their homogeneity vetoes and label-isolation
limitations.

## Repository ownership

The 2026-11-11 cross-repository review places this implementation in
`gororoba-quantum`. Its new schemas do not replace any historical
observable, associator, platform-balance, or reading-copy interface.

| Repository | Relevant boundary and disposition |
|---|---|
| `gororoba-quantum` | Own the protocol, provider assessment, normalized records, CLI, tests, design and work-plan status here. |
| `gororoba-open` | Preserve the historical quantum-input pins in [observable reconciliation](https://github.com/Oichkatzelesfrettschen/gororoba-open/blob/b73ca1050ace1c5c6f8a25564879f70bacdbf80b/docs/engineering/quantum_observable_reconciliation.txt) and the associated formal/provenance consumers; they do not consume these new schemas. |
| `gororoba-infrastructure` | The inspected dashboard consumes the existing platform/balance interface; this implementation changes neither that interface nor its consumer. |
| `gororoba-documents-private` and `gororoba-documents-public` | Preserve reading-copy ownership and hashes in [reading-copy-locations.tsv](../sources/reading-copy-locations.tsv). This change introduces no replacement paper bytes. |
| `gororoba-documents-technical` | No inspected network-record consumer or scoped document relocation requires a patch. |

Keep the existing source restoration and index-maintenance tools as the
owners of paper retrieval and location mapping. Do not duplicate this
reader across repositories or rewrite a historical consumer's receipt
to point at an unrelated new record format.

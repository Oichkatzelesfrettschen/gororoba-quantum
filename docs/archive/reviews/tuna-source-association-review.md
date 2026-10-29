Review verdict: the source/job/batch/file chain is mostly sound, but the staged checker does not establish a unique source-to-result association. One serious false-acceptance class remains.

### Findings

1. SERIOUS — Result identity and uniqueness are absent.

[qi_tuna_source_association.py:50](../../../scripts/qi_tuna_source_association.py) checks only `Result.job_id`. The checker accepts a result with a missing, Boolean, malformed, stale, or conflicting `Result.id`.

The retained OpenAPI schema requires `Result.id`, while `/results/job/{job_id}` returns a paginated `Page_Result`, permitting multiple candidate records ([openapi.json:1](../../../docs/notes/quantum_inspire/api/openapi.json), JSON pointers `#/components/schemas/Result` and `/results/job/{job_id}`). The design requires rejection of missing and duplicate identities ([design:90](../../../docs/design/tuna-destination-sequential-evidence-case.md)).

The success fixtures explicitly certify the incomplete mapping `{"job_id": 11}` ([test:25](../../../tests/scripts/test_qi_tuna_source_association.py), [test:46](../../../tests/scripts/test_qi_tuna_source_association.py)).

Remedy: require an exact positive `Result.id`, retain that identity in an immutable collection checkpoint, and validate the complete paginated job-result response has exactly one admissible result. Add missing, Boolean, conflicting, duplicate, and omitted-page cases.

2. SERIOUS — Preselecting mappings discards duplicate/readback evidence.

`validate_association` receives one already-selected batch and result mapping. The retained API exposes batch readback through a filtered page and result readback through a paginated page. After the caller extracts one item, the checker cannot distinguish:

- one record from two records sharing the requested association;
- a complete response from the first page of several;
- an authenticated readback from a constructed dictionary;
- a missing provider resource from a caller that simply never invokes the checker.

The design assigns authentication and record retention to the caller, but duplicate rejection belongs to the stated association requirement. The collection boundary must retain the full response envelope, pagination completion, request locator, and cardinality before invoking a projection-level validator.

3. SLOPPY — Test names claim broader coverage than the fixtures provide.

`test_each_association_edge_refuses_conflict` ([test:49](../../../tests/scripts/test_qi_tuna_source_association.py)) omits the result identity edge and every response-cardinality case. The file-level claim that substituted provider resources are rejected ([test:1](../../../tests/scripts/test_qi_tuna_source_association.py)) is false for a substituted result having the same `job_id`.

The fixtures are field projections, not OpenAPI-conformant provider records. The accepted result lacks every required `Result` field except `job_id`. Either rename the tests as projection checks or supply schema-complete fixtures and test the full collection envelope.

### Static guarantees that do hold

The checker correctly establishes, relative to trusted supplied mappings:

- exact built-in positive integers, rejecting Booleans and integer subclasses;
- exact source SHA-256 and strict UTF-8 decoding;
- exact provider source text;
- job-to-file and job-to-batch links;
- requested-shot equality with the checkpoint;
- exact `raw_data_enabled is True`;
- batch identity, backend type, and one-element job membership;
- file identity and commit link;
- selected result-to-job equality.

The forged string-subclass test correctly confirms that a custom comparison method cannot bypass the digest check.

### Boundaries outside the checker

- Raw data: `raw_data_enabled=True` proves only the supplied job flag. OpenAPI permits `Result.raw_data=null`; the checker ignores `raw_data`, `shots_requested`, `shots_done`, counts, ordering, and width.
- Compiler surface: exact `File.content` does not validate `language_id`, `compile_stage`, `compile_properties`, `generated`, compilation output, destination mapping, or the served analog schedule. The design correctly keeps fresh compilation and structural checks separate ([design:26](../../../docs/design/tuna-destination-sequential-evidence-case.md)).
- Caller trust: the caller must authenticate observations, bind the checkpoint to the approved assignment and fixed Tuna-17 case, retain full provider responses, and reject duplicate JSON keys before converting responses to mappings.
- Provider trust: the static checker assumes the provider truthfully implements the retained schema and that `Job.file_id` denotes the source actually used. Static equality cannot prove live readback availability, compilation semantics, physical execution, or schedule.
- Full schema validity: ignored job, batch, file, and result fields may be missing or malformed without affecting acceptance.

### Exact staged SHA-256

- `scripts/qi_tuna_source_association.py`: `d169e935202bf489b900cc5ba1a29707f42d1171c26ca84cd10d49301129c86c`
- `tests/scripts/test_qi_tuna_source_association.py`: `f7a3c72a1e3742ef24f90deba2304bfc81790c0134e1fd43ccab1d1613bbd526`

The worktree copies matched those staged bytes.

The review ran no tests, Python code, network operations, credential reads, provider operations, jobs, uploads, draws, or messages. Final measurements retained HEAD `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, the two original index entries, both named-file hashes, local-ref targets, and the pre-existing 237-entry worktree-status inventory. The review wrote no repository files.

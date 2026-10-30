The staged proposal’s circuit logic and manifest are sound, but the readback verifier is not ready for provider use. One FATAL reachability defect and one SERIOUS malformed-result false pass block approval.

## Findings

### FATAL — readback calls an API endpoint absent from the retained contract

[capture_readback()](../../../scripts/qi_tuna_qx_destination.py) calls:

```text
GET /batch_jobs/{batch_id}
```

The retained [OpenAPI contract](../../../docs/notes/quantum_inspire/api/openapi.json) exposes `GET /batch_jobs` with an `id` query parameter, but exposes no `GET /batch_jobs/{id}`. The repository’s established reconciliation implementation explicitly documents and uses the supported route at [qi_platform.py:1077](../../../scripts/qi_platform.py).

Exact local reproduction:

```sh
jq -r '.paths | keys[] | select(contains("batch_jobs"))' \
  docs/notes/quantum_inspire/api/openapi.json
```

The output contains `/batch_jobs` and action endpoints, but lacks `/batch_jobs/{id}`.

The unit double incorrectly blesses the nonexistent route at [test_qi_tuna_qx_destination.py:360](../../../tests/scripts/test_qi_tuna_qx_destination.py).

Remedy: use `client.pages("/batch_jobs", id=batch_id)`, require exactly one row with the expected ID, and update the test double to reject undocumented paths.

### SERIOUS — a partial provider Result passes capture and terminal analysis

The retained OpenAPI schema requires `Result.created_on`. Neither the capture validation at [qi_tuna_qx_destination.py:260](../../../scripts/qi_tuna_qx_destination.py) nor collection analysis at [qi_tuna_qx_destination.py:411](../../../scripts/qi_tuna_qx_destination.py) validates that field.

The test fixture itself demonstrates the false pass:

- Its result object omits `created_on` at [test_qi_tuna_qx_destination.py:121](../../../tests/scripts/test_qi_tuna_qx_destination.py).
- `analyze_collection()` accepts the fixture and reports a passed screen at [line 197](../../../tests/scripts/test_qi_tuna_qx_destination.py).
- The readback double returns the same incomplete result and capture succeeds at [line 399](../../../tests/scripts/test_qi_tuna_qx_destination.py).

An independent in-memory replay produced:

```text
MISSING_REQUIRED_RESULT_CREATED_ON_ACCEPTED True False
```

The `False` provider-admission value correctly limits the scientific conclusion, but the receipt validator still accepts a malformed provider object.

Remedy: require every OpenAPI-mandatory Result field, parse `created_on` as timezone-aware, and add missing-field mutations for capture and analysis.

### SLOPPY — local observation provenance accepts impossible metadata

[build_manifest()](../../../scripts/qi_tuna_qx_destination.py) checks versions, source hashes, counts, and selected flags, but ignores observation timestamp syntax and ordering, Python-version type, command identity, and qxelarator producer identity.

An in-memory mutation changed:

- `observed_utc` and `started_utc` to `not-a-time`;
- `finished_utc` to 1900;
- `python_version` to an integer or null.

`build_manifest()` still returned:

```text
MALFORMED_LOCAL_OBSERVATIONS_ACCEPTED qi-qx-destination-conformance-case-v1 3
```

The current observation bytes are hash-bound and internally plausible, but the dedicated gate cannot reproduce the claimed libqasm or qxelarator executions. It verifies a stored assertion, not those executions.

The illustrative `0.09–31.2 s` range at [tuna-destination-qx-conformance.md:91](../../../docs/design/tuna-destination-qx-conformance.md) also lacks exact retained run paths and hashes in the manifest evidence map.

Remedy: retain executable observation producers or exact commands, validate timestamp/type fields, and bind the historical timing inputs or remove the numeric range.

## Bounded passes

- The four current worktree and staged hashes exactly match `local hash binding list`.
- The source hashes match the constants and manifest:
  - baseline: `004667f9…dc91af`
  - rotated: `39454ac0…5e584`
  - asymmetric: `dc9de025…f0ecd`
- Every manifest evidence digest matches its current file.
- Exact manifest replay passes.
- The QX predictions are correct under the documented last-measurement-per-qubit contract: baseline and rotated yield `000`; `X q[0]` leaves q0 measured as one, and q0 is rightmost, yielding `001`.
- Raw-shot width, completeness, histogram equality, ordered-result hashing, execution limits, transaction emptiness, batch/job/file binding, unique analyzed result IDs, and separate local/provider clock domains are otherwise handled coherently.
- Exclusive readback-output reservation and the durable incomplete marker behave as documented.
- A synthetic local receipt can set `terminal_screen_passed=true`, but `provider_conformance_admitted` remains false. That scientific boundary is sound.
- Ruff lint and format pass; mypy reports success for both Python files. The dedicated manifest gate passes. Pytest could not start because the read-only sandbox exposes no writable temporary directory.
- The reviewed artifact introduces no random seed.

## Verdict

The reduced circuit proposal is a defensible terminal-output plumbing check, not Tuna validation. The staged verifier should remain working-unapproved until the unsupported batch endpoint and incomplete Result acceptance are fixed. The acknowledged QX-to-Tuna end-to-end gap and missing manifest-bound approval guard remain absolute policy blockers: the staged files authorize neither upload nor submission, and a passing terminal screen establishes neither provider conformance nor Tuna behavior.
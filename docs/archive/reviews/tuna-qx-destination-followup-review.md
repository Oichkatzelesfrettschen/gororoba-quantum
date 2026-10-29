The repair closes the prior FATAL endpoint defect and SERIOUS Result-field defect. The current artifacts are internally consistent, but one SERIOUS pagination false pass and two SLOPPY provenance gaps remain.

The reviewed artifacts span API pagination, parser/simulator replay, reproducibility, and scientific evidence boundaries. I read the complete verifier, replay producer, tests, case, manifest, replay record, and connected QI client paths.

## Findings

### SERIOUS — contradictory batch pagination metadata becomes invisible

[capture_readback()](../../../scripts/qi_tuna_qx_destination.py) correctly calls the documented `/batch_jobs?id=...` route, but [Client.pages()](../../../scripts/qi_platform.py) discards `page`, `pages`, `size`, and `total`. Capture then treats `len(batches) == 1` as proof that the provider resolved exactly one batch.

Concrete counterexample supplied to the actual `Client.pages()` implementation:

```json
{
  "items": [{"id": 100, "backend_type_id": 1, "job_ids": [1000, 1001, 1002]}],
  "page": 1,
  "pages": 1,
  "size": 100,
  "total": 2
}
```

Observed result:

```text
INCONSISTENT_BATCH_PAGE_ACCEPTED 1 100
```

The response says two matching objects exist while exposing one; capture cannot see the contradiction. The test double at [test_qi_tuna_qx_destination.py:426](../../../tests/scripts/test_qi_tuna_qx_destination.py) bypasses actual pagination and therefore cannot catch the false pass.

Remedy: fetch the filtered first page directly and require `page=1`, `pages=1`, `total=1`, one item, and a valid size, or make `Client.pages()` validate and expose pagination metadata.

### SLOPPY — the authoritative backend snapshot is hash-bound but semantically ignored

[build_manifest()](../../../scripts/qi_tuna_qx_destination.py) includes `approved-qx-backend.json` only in the evidence-digest map. It never validates the snapshot’s backend ID, identifier, qubit capacity, shot limit, raw-data support, or execution limit against the manifest constants.

An in-memory snapshot mutation set:

```text
id=7
identifier=different_backend
nqubits=2
max_number_of_shots=1
job_execution_time_limit=1
supports_raw_data=false
```

`build_manifest()` still returned:

```text
CONTRADICTORY_BACKEND_SOURCE_ACCEPTED 1 3 2048 3600
```

The current snapshot does contain the expected values, so the present manifest is correct. The replay gate would nevertheless accept a contradictory snapshot after regenerating `cases.json`.

Remedy: parse and validate the registered snapshot before constructing the manifest. Fresh admission remains separately required.

### SLOPPY — replay provenance exists, but malformed replay metadata and false boundaries remain admissible

The new [local replay producer](../../../scripts/qi_tuna_qx_local_replay.py) genuinely binds source hashes, parser errors, simulator counts, versions, producer digest, and timestamps. The current [local-replay.json](../../../results/quantum_inspire/proposals/tuna-destination-qx-conformance/local-replay.json) matches those expectations.

The verifier still accepts:

```text
started_utc = 9999-01-01T00:00:00+00:00
finished_utc = 9999-01-01T00:00:01+00:00
python_version = 3.13.fabricated
boundary = provider authenticated
```

Observed result:

```text
MALFORMED_REPLAY_METADATA_ACCEPTED qi-qx-destination-conformance-case-v1 3
```

The permissiveness comes from `startswith("3.13.")`, lack of a future-time check, and lack of boundary validation at [qi_tuna_qx_destination.py:158](../../../scripts/qi_tuna_qx_destination.py).

The dedicated gate at [ci/gates.json:5111](../../../ci/gates.json) only replays the manifest under ordinary `$PYTHON`. It neither runs the QI-stack producer nor declares `requires: ["qi"]`. The producer also lacks a semantic `--check` mode. Thus the staged record is reproducible in principle but untested by the dedicated gate.

Remedy: validate an exact Python version form and exact boundary, reject implausibly future local timestamps, and add a QI-stack semantic replay gate that ignores only dynamic timestamps.

## Prior finding disposition

| Prior finding | Status |
|---|---|
| FATAL undocumented `/batch_jobs/{id}` route | Closed. Capture now uses `client.pages("/batch_jobs", id=batch_id)`. |
| SERIOUS missing `Result.created_on` accepted | Closed. Capture and analysis require a timezone-aware creation timestamp; negative tests cover both paths. |
| SLOPPY malformed historical observation metadata | Closed for the prior counterexamples. Invalid timestamps, reversed times, and non-string interpreter identities now fail. |
| SLOPPY parser/simulator provenance lacked a producer | Substantially closed by the new producer and record; automated execution and strict metadata validation remain open as described above. |
| SLOPPY unbound execution-time forecast | Closed. The case now states no forecast and retains only hard ceilings. |

## Bounded passes

- All six supplied hashes match `local hash binding list`, the working files, and staged index bytes.
- All ten manifest evidence hashes match current files.
- The three source hashes remain:
  - baseline: `004667f94872f372eab01eb75dfbc6e5fb25e0b16534d3c20da6b1c7f5dc91af`
  - rotated: `39454ac0e32f0bebfd687d5def41666ee7e35b3af5d61430c2f0b084d355e584`
  - asymmetric: `dc9de0253a6d544bf76ba215a3fca2cf253dda549364f899064f927c1d7f0ecd`
- The normalized streams confirm baseline/rotated equality and the sole added `X q[0]`. Under QX’s last-measurement register with q0 rightmost, `000`, `000`, and `001` are correct deterministic predictions.
- Result IDs are positive and unique across capture and analysis.
- Ordered raw shots are width-three binary strings; the retained provider-result hash binds their order. Histogram counts reject booleans, floats, zero, and negatives.
- Execution durations reject booleans, strings, missing values, NaN, infinity, negatives, and values above 3600 seconds.
- Provider job chronology stays within the provider clock domain. Submission, collection, and readback chronology stays within the local clock domain.
- Source bytes, job/file associations, batch membership, shot counts, compile settings, transaction emptiness, and retained-result hashes are coherently checked.
- Readback output is exclusively reserved and fsynced with an incomplete marker before client construction. The documented final-publication interruption boundary remains honest.
- `provider_conformance_admitted` remains false even for fully fabricated locally consistent receipts.
- No reviewed artifact introduces a random seed.

Verification results:

- Exact manifest replay: passed.
- Ruff lint and format: passed.
- Mypy: passed for all three reviewed Python files.
- Direct pure malformed-shot negative test: passed.
- Numeric and timestamp falsifiers: passed.
- Full pytest module: untested because the read-only sandbox exposes no writable temporary directory; pytest failed before collecting tests.
- Local libqasm/qxelarator producer execution: untested. I did not run a simulator job, write an output record, access the QI environment, or load credentials.

## Verdict

The reduced QX case remains scientifically bounded and substantially improved. The current sources, predictions, replay record, manifest, result validation, clock separation, and non-admission boundary are sound. Batch pagination still permits a concrete malformed-response false pass, so the verifier has not yet earned a clean pass. The missing approval guard, fresh admission, and QX-to-Tuna end-to-end gap remain explicit blockers and are not waived by any local or future QX terminal screen.
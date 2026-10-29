The staged validator is sound for ordinary, stable `dict` inputs, but one SERIOUS false-acceptance class remains under its advertised `Mapping` interface. No FATAL issue appeared.

Locators below refer to index blobs, not working-tree copies.

### Findings

- **SERIOUS, high confidence — type checking and comparison observe different mapping values.**

  - At staged `scripts/qi_tuna_source_association.py:27`, each of `total`, `page`, and `pages` is fetched twice. A stateful `Mapping` can return exact integer `2` for the type check and exact integer `1` for the comparison, causing contradictory pagination evidence to pass.
  - At staged `scripts/qi_tuna_source_association.py:83`, `provider_file.get("content")` receives the exact-string check, while `provider_file["content"]` supplies the compared value. A custom mapping can return mismatched source text first and expected source text second.
  - The public annotations at staged lines 12, 20, and 42–47 explicitly admit `Mapping` implementations. The tests use only ordinary dictionaries and one adversarial value subclass; they never exercise a stateful mapping.
  - Concurrent mutation creates similar double-read windows for `items[0]` at staged lines 33/35 and `job_ids[0]` at line 81.
  - Remedy: read every field and list element once into a local, validate and use that same object, and require the collection boundary to supply an owned, duplicate-aware plain-dictionary snapshot. Single-read locals close the direct bypasses; collection ownership is still needed for cross-field snapshot coherence.

- **SLOPPY — test names claim more provider evidence than the fixtures contain.**

  Staged `tests/scripts/test_qi_tuna_source_association.py:31` names `test_matching_provider_readback_accepts_the_source_association`, but lines 34–48 construct dictionaries locally. Staged line 150 names `test_association_requires_the_complete_result_page`, but that test is another positive synthetic-page acceptance case; rejection coverage lives elsewhere.

  The implementation header correctly says the check runs without provider access and relies on caller-authenticated observations. The tests should use “supplied projection” or similarly bounded language.

- **SLOPPY — negative coverage misses the advertised input surface.**

  Staged test lines 126–140 cover duplicate records, partial-page metadata, and missing, Boolean, or conflicting result IDs. They do not cover stateful `Mapping` inputs, malformed result `job_id`, malformed page counters, empty items, or invalid `size`. Static inspection shows the ordinary-dictionary cases are rejected, so this is a coverage deficit rather than another implementation defect.

### What the projection does establish

For stable plain dictionaries, the staged implementation correctly establishes:

- Exact built-in positive checkpoint, job, and result IDs; Boolean and subclass identities fail.
- `total == page == pages == 1`, `1 <= size <= 100`, and exactly one plain-dictionary result item.
- Duplicate items and honestly reported multi-page or partial-page responses fail.
- Result-to-job equality.
- Strict UTF-8 decoding, exact SHA-256, and exact provider source text.
- Exact job/file/batch linkage, requested shots, backend identity, file commit identity, `raw_data_enabled is True`, and singleton batch membership.

The `size` field represents page capacity rather than returned-item count, so `size > 1` with one total result is consistent with the retained request schema.

These checks satisfy the static edges identified in the [archived review](../../../docs/archive/reviews/tuna-source-association-review.md), apart from the arbitrary-`Mapping` bypass above.

### What successful validation does not establish

The [design’s source-to-result section](../../../docs/design/tuna-destination-sequential-evidence-case.md) correctly assigns these obligations to collection rather than projection:

- A caller can coordinate a substituted checkpoint, source, resources, and result ID into a self-consistent accepted mapping. The verifier cannot authenticate checkpoint provenance or bind it to the approved Tuna-17 assignment.
- Mapping conversion can already have discarded duplicate JSON keys, request locators, pages, or envelope provenance.
- A one-result response cannot exclude a result created after the read. Page completeness applies only at a named observation boundary.
- The batch input is caller-selected; only the collection layer can prove complete batch-response cardinality.
- The result projection checks `id` and `job_id`, not full result-schema completeness, ordered shots, timestamps, execution duration, or scoring admissibility.
- Exact source/resource equality cannot prove that Quantum Inspire compiled or executed those bytes, served a particular physical schedule, or returned an atomic provider snapshot.
- `validate_association` returns `None`; downstream code must retain and score the exact validated response rather than another or subsequently mutated response.

Therefore, the validator earns a static association predicate over trusted inputs. It does not earn full collection validity or provider semantics.

### Exact staged identities

| Staged path | SHA-256 | Git index blob |
|---|---|---|
| `scripts/qi_tuna_source_association.py` | `2993c9962f9ca47a3a8f0c9f9f4d18b416c5ded5c6d02fe5ddb427fe4d9d27b9` | `9a5788f3662d5486d3f442fb5e80277d575ae767` |
| `tests/scripts/test_qi_tuna_source_association.py` | `f3cba1a941b55d40e049864078f0f3a8935dffecbc1c98f711250da3767c4a2c` | `e7bd2b7fdd3eade7958f9453ddad2c635fe253ef` |

HEAD remained `55b6dcb8861be4fe8ec8f8f38a3fa1844755d346`, and both index blobs and staged SHA-256 values remained identical across the review.

The script initially reported `A` and later reported `AM`; the test reported `AM` throughout. Thus an unstaged script modification appeared during the review. The review ignored both unstaged copies and remained bound to the unchanged index blobs.

No tests or Python programs ran. The review used no network, credentials, provider access, jobs, uploads, draws, messages, or repository writes.

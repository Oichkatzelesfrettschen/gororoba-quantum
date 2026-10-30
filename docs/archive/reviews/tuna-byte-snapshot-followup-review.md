Artifact: staged Python offline evidence predicate and tests. Fields: strict JSON parsing, provider-resource identity, immutable evidence snapshots, and raw-result admission.

## Findings

1. **SERIOUS — contradictory executable measurement metadata is still accepted.**

   [qi_tuna_source_association.py](../../../scripts/qi_tuna_source_association.py) validates six `analysis_metadata` fields, then derives counts from hard-coded destinations at lines 320–324. It never validates the manifest’s `measurement_to_bit_map`, which independently declares those destinations in [cases.json](../../../results/quantum_inspire/proposals/tuna-destination-slot-alternatives/slot-01/baseline/cases.json). It also ignores `analysis_metadata.decoder_rule`.

   A digest-bound manifest can therefore carry the expected checked fields alongside a contradictory measurement map and still produce a score. That violates the design’s claim that the independent calculation uses the selected manifest’s destination metadata ([design](../../../docs/design/tuna-destination-sequential-evidence-case.md)).

   The retained manifests inspected here are internally consistent, so this false acceptance does not invalidate them. Require the exact arm-specific three early mappings plus all 17 terminal mappings, rejecting missing, duplicate, reordered, Boolean, or conflicting entries. Add map mutations to the tests.

2. **SLOPPY — tests do not cover the remaining false acceptance.**

   The orientation mutations at [test_qi_tuna_source_association.py](../../../tests/scripts/test_qi_tuna_source_association.py) now cover the three fields identified by the archived review, but nothing mutates `measurement_to_bit_map` or `decoder_rule`.

   Duplicate-key tests cover every supplied snapshot class and at least one nested result object, but do not explicitly cover every nested shape, including catalogue alternatives, manifest circuits, `analysis_metadata`, batch items, and histogram objects. The recursive hook makes this a coverage gap rather than another implementation false acceptance.

## Closed archived findings and sound behavior

- `_finite_float` now rejects overflowed JSON numbers such as `1e400`; `parse_constant` rejects `NaN`, `Infinity`, and `-Infinity`. Tests cover all five positive and negative mutations at [lines 288–294](../../../tests/scripts/test_qi_tuna_source_association.py).
- `object_pairs_hook=_unique_object` applies recursively, rejecting duplicate keys at every JSON object level. Provider-file duplicates now cover language ID, compile stage, compile properties, and content.
- `bit_order`, `index_convention`, and `canonical_early_string_offsets` are now checked exactly. The archived review’s corresponding finding is resolved.
- The byte entry point accepts exact `bytes`, creates privately owned dictionary/list trees, and delegates only those trees. Lower-level mapping APIs still cannot recover duplicate keys discarded before invocation.
- The association chain binds catalogue digest, slot, arm, manifest, source digest and UTF-8 text, job, file, commit, batch, result, language ID, Tuna-17 backend type 7, 4096 shots, raw-data enablement, compile stage, and compile properties.
- Complete results require 4096 width-20 binary shot strings and an exact histogram multiplicity match. Nonnegative zero-count bins remain intentionally valid.

The archived review is historical rather than a current staged-blob receipt: its recorded script and test hashes differ from the present index because the cited defects were subsequently repaired.

## Unimplemented live evidence, not decoder false acceptances

The static predicate does not establish:

- authentication or retention of HTTP bytes, request locators, response envelopes, assignment release, approval, or account context;
- the live cQASM language identifier, authenticated readback behavior, or atomic pagination;
- observation-boundary timing, suspend/reboot continuity, result availability, acquisition order, or per-shot timestamps;
- pricing, zero-charge evidence, queue, heartbeat, terms, pause, retry, or late-charge rules;
- served analog schedules, calibration, discrimination, thresholds, or in-phase/quadrature data.

The caller must use the byte entry point exclusively for provider JSON and retain the original authenticated bytes separately.

## Exact staged SHA-256

| Staged blob | SHA-256 |
|---|---|
| `scripts/qi_tuna_source_association.py` | `93b5b01b3ec646ec47f49b822567af1bc3d9018f70f110cdd5a2708ffff177a6` |
| `tests/scripts/test_qi_tuna_source_association.py` | `02cf641a2a4ec885a7aab6fb12711a0607a52259a4ea4a8258846c32d00163a4` |
| Review basis document | `e1db26961b559216f6cf08c9d7e80cdaad31bd53330c736e25e74afd6fd7a401` |
| Design basis document | `54d109064b397789f88bd800bcd9c353655a049f9dd7a74dd358a3e5bb544164` |

The staged and working-tree bytes matched for all four files. I performed static read-only inspection only: no tests, network access, credentials, provider operations, jobs, uploads, draws, external messages, or repository edits.

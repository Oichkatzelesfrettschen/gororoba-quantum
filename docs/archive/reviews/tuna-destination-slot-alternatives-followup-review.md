The targeted repairs earn a bounded PASS. I found no FATAL, SERIOUS, or SLOPPY defect in the repair itself.

## Verified closure

- All 150 follow-up bindings match both staged and working bytes.
- The changed artifacts are exactly the producer, regression test, private-assignment design, and catalogue.
- All 144 arm files retain their prior hashes.
- The rebuilt catalogue is explained solely by its updated `producer_sha256`:

  - Current catalogue: `353c28a3…cde4`
  - Substituting the prior producer hash reconstructs the prior catalogue digest exactly: `f5f09ed…a7ec`
  - The catalogue’s producer hash equals the current producer’s `c5e82b34…7513`.

- The builder’s normal `--check` passes, and Ruff format/check passes with the locally installed version.

## Hard-link repair

[`check_proposal()`](../../../scripts/qi_tuna_destination_slot_cases.py) now rejects every regular file whose `st_nlink` differs from one. The check covers sources, manifests, backend snapshots, and the catalogue.

The regression at [test line 91](../../../tests/scripts/test_qi_tuna_destination_slot_cases.py) creates a second filesystem name for a valid source and requires rejection. The regression has the correct causal shape: unchanged bytes, additional hard link, expected failure.

Because the user prohibited filesystem writes, I did not execute the `tmp_path` test. An in-memory `st_nlink=2` mutation produced the precise `hard-linked files are inadmissible` rejection. The actual proposal contains 145 singly linked files and zero multiply linked files.

The repair makes no check-to-use claim. Ordinary mutation or replacement after checking remains possible and belongs to the deliberately absent dispatch guard.

## Private-assignment requirements

The expanded section at [lines 46–68](../../../docs/design/tuna-destination-private-assignment.md) now explicitly requires:

- authenticated or independently witnessed acquisition provenance, or an explicit trust assumption covering fabrication and selection;
- a prespecified first eligible request;
- a no-discard rule;
- retention of every attempt, failure, and retry decision;
- a witnessed commitment time;
- request time and response deadline fixed before arm disclosure;
- rejection of missing, late, or selectively timed releases;
- a threat model covering future-value visibility, timing control, and log modification;
- confidentiality for selected directories, source hashes, manifest hashes, and related access logs.

The document correctly labels these as requirements, not implemented mechanisms. It also continues to state that the commitment encoding, salt custody, allocation release, verification, and testing require implementation and independent review.

## Remaining blockers

The following remain open by design rather than as repair regressions:

- The generic submission route still lacks the exact dispatch guard.
- QRNG acquisition, custody, commitment, one-slot release, and opening verification remain unimplemented.
- The proposal check does not remove check-to-use races.
- Consequently, the artefacts authorize neither a provider request nor randomized inference.

Final measurements found all 150 bound working and staged bytes unchanged after the review, with clean staged and working `git diff --check` results.

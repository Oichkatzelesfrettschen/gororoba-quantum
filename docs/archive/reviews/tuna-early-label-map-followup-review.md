## Focused review result

No FATAL, SERIOUS, or SLOPPY findings.

The preceding SLOPPY regression-coverage finding is closed.

- Producer SHA-256 remains `271486a916177ad96d5f5203c2c5c4233e14312542b8954abd7abd3050f789af`.
- Record SHA-256 remains `5093dcda0011f164a3a22427ec7c287d0b7b6bc2f5d15c20782f311020d21008`.
- The test changed as intended, now SHA-256 `4459b45f4bd859c2a73460c272c9d934da09169b13ae06a608f3679ab258667b`.

The repaired validator at `tests/scripts/test_qi_tuna_early_label_maps.py:123` independently establishes:

- Exactly all \(3!\times2^3=48\) signed permutations occur once (`:125-130`).
- Every map is a bijection of all 64 labels and preserves terminal bits 3–5 (`:131-140`).
- The 48 maps induce 48 distinct transformations (`:141-142`).
- Every transformation’s inverse belongs to the family (`:143-146`).
- The prior duplicate-identity counterexample is explicitly constructed and rejected (`:157-159`).

A coherent defective producer-and-record regeneration with six copies of the identity permutation and all eight polarity masks fails the independent expected-family comparison. The existing scalar reconstruction at `tests/scripts/test_qi_tuna_early_label_maps.py:101-120` separately prevents correct map labels from concealing incorrectly computed scores.

Independent execution confirmed, for both retained cases:

- 48 specifications and 48 distinct transformations.
- 48 bijections and 48 terminal-preserving maps.
- All 48 inverses present.
- The duplicate-identity family raises the expected `ValueError`.
- Retained numerators remain:
  - nominal one: minimum `600`, terminal lower bound `232`;
  - stopped nominal-zero prefix: minimum `6310`, terminal lower bound `6286`.

Normal and optimized exact record checks both passed:

```text
Early-label maps preserve terminal projections in both retained preparation cases.
```

Pytest was not run because the focused tests require writable `tmp_path` storage, which the read-only review boundary prohibits. The relevant pure validation logic and both CLI replay modes were exercised directly without writes.

Bounded PASS. The repair changes only regression coverage; unchanged producer and record bytes preserve the prior descriptive conclusions. The result remains post-acquisition, the nominal-zero endpoint remains incomplete, and the analysis establishes neither physical causality nor immunity to drift or timing confounds.
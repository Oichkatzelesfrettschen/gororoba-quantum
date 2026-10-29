The scoring-test masking repairs and governing-design binding earn a bounded PASS. No FATAL, SERIOUS, or SLOPPY finding remains within this follow-up scope.

## Binding closure

All four entries in [tuna-sequential-score-followup-bindings.txt](tuna-sequential-score-review.json) match both staged and working bytes:

| Artifact | SHA-256 |
|---|---|
| Scoring core | `d344f69db36dcc79a6ce605686aa1dfcc488fa034ad09fdfab5c7d7f9d16611b` |
| Repaired tests | `df4f6edfc4c627927176c16b017c68c23e38384da37e929afb93d03d4d8840bc` |
| Sequential evidence case | `749cd8633bf7db9c8ed96b8d425c97821294d2250bb0dfea48537a57ca6e72f5` |
| Sequential uncertainty design | `a94cbad3c6d0a007296ec5d5b36d52b73e5e31e710d4276c26c76d4c008e75b3` |

The follow-up binding now includes both governing design documents. Final `sha256sum -c`, unstaged-diff, and `git diff --check` checks were clean.

## Mutation closure

The unmodified [test suite](../../../tests/scripts/test_qi_tuna_sequential_score.py) passed all 14 collected cases.

Each mutation ran in a fresh interpreter against the real checked-in pytest suite:

| Mutation | Rejecting test | Result |
|---|---|---|
| Terminal offset 13 changed to 0 | [decoder isolation test](../../../tests/scripts/test_qi_tuna_sequential_score.py) | 1 failed, 13 passed |
| Baseline treated as rotated | [baseline four-process test](../../../tests/scripts/test_qi_tuna_sequential_score.py) | 1 failed, 13 passed |
| Shared stop checked only terminal | `test_single_observable_crossing_does_not_stop[terminal]` at [line 185](../../../tests/scripts/test_qi_tuna_sequential_score.py) | 1 failed, 13 passed |
| Terminal-negative process forced neutral | [baseline four-process test](../../../tests/scripts/test_qi_tuna_sequential_score.py) | 1 failed, 13 passed |
| `confirmed_failure` removed | Parameterized neutral-class test at [line 175](../../../tests/scripts/test_qi_tuna_sequential_score.py) | 1 failed, 13 passed |
| `partial` removed | Same parameterized test | 1 failed, 13 passed |

The repaired tests avoid the earlier masking:

- Terminal bit 6 is isolated from both early destinations.
- Baseline scoring checks all four response/direction values.
- Early-only and terminal-only crossings are separate parameter cases.
- All three neutral classifications are enumerated.
- Expected values are hard-coded independently of implementation helpers.

Ruff lint, Ruff formatting, and mypy also passed.

## Review limits

This follow-up reviewed only the named masking repairs and binding completeness. It did not repeat the full scoring derivation, review an eventual runner, or establish source/job identity, randomization, concealment, timing, cost, admission, or inference eligibility. The mutations remained in memory; no files, credentials, providers, messages, uploads, submissions, or random seeds were used.

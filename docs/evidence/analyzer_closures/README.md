# Retained analyzer closures

Each directory holds the scripts/ bytes a record's approval bound, named by
the first twelve hex digits of that closure's sha256
(`qpu_planning.analyzer_closure`: the sha256 of the canonical JSON map from
`scripts/NAME` to each file's sha256). An analyzer that refuses a record
whose bound closure differs from its own replays that record only through
these bytes, so the live scripts keep changing while the record stays
replayable. [ci/frozen_replay.py](../../../ci/frozen_replay.py) points
`qpu_planning.SCRIPTS_DIR` at a directory here and runs its analyzer, which
then hashes the retained copy and checks it against the record itself.

| Closure | Files | Record | Gate |
|---|---|---|---|
| `46d2411ed6a7` | `n21_orbit_rca.py` d04ce0fddd35..., `n21_spectator_ramsey.py` 05440fac02b2... | [2026-10-20T031212.175942Z](../../../results/live/2026-10-20T031212.175942Z) ramsey.json | core-603 |

The copies are the bytes of origin/main at merge ae44a4c. Ruff excludes this
tree (pyproject.toml), since a retained file keeps the lint state it was
approved with.

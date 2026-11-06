# Generated views

Four Markdown views project records that stay tracked. Each view is git-ignored and rendered on demand, so a
pull request that edits a record changes no view and two pull requests never conflict on one.

| View | Record it renders | Render command |
|---|---|---|
| `docs/state/plans.md`, `docs/state/plan-catalogue.md` | `docs/state/plans/*.json` | `"$PYTHON" scripts/plan_tracker.py render --write` (`render` alone prints the entrance) |
| `docs/state/RESEARCH_STATE.md` | `docs/state/research_state.json` and the retained run directories | `"$PYTHON" scripts/research_state.py --write` |
| `docs/sources/reading-copies.md` | `docs/SOURCES.json` and `docs/sources/reading-copy-locations.tsv` | `"$PYTHON" scripts/source_reading_copies.py` |

The checks keep validating the records: `scripts/plan_tracker.py check` (gate core-plan-tracker),
`scripts/research_state.py --check` (core-270) and `scripts/source_reading_copies.py --check`
(sources-reading-copies-index) fail on a malformed record, a dangling reference or an unrenderable registry, and
compare no rendered file. `scripts/results_index.py` ([results index](results-index.md)) computes its answers at
call time and writes nothing under the repository. Prose links to a record, never to a view, because a fresh
checkout holds no view.

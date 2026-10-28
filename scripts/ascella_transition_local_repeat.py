"""Run the matched-mesh repeat with the source-compatible successor case."""

from pathlib import Path

import ascella_transition_day_repeat as repeat

repeat.BUNDLE = Path("docs/evidence/ascella-transition-day-repeat-ci")

if __name__ == "__main__":
    raise SystemExit(repeat.main())

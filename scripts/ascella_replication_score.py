"""The preregistered score of Ascella's replication meshes against the frozen element offsets.

docs/state/plans/ascella-replication-meshes-case.json fixes this contract before its seeds are drawn, and the offsets
come from docs/evidence/ascella-order-coefficients/replication-offsets.json (scripts/ascella_replication_offsets.py).
The contract is that of scripts/ascella_new_mesh_score.py, under the replication's design:

- Predictors: R-B, all-meshes, the predictor that carried on the new-seed meshes, unchanged; R-C, all-served, the
  same family refitted on every perturbed mesh the retained runs hold. Bonferroni ALPHA_EACH each.
- References: jobs 00, 02, 03, 04 and 05-i88. A mesh any of them served is excluded; job-05-i88's anchors, the last
  acquisition before the replication, set the anchor baseline.
- Acquisition: job-06 runs 96 iterations. Job-07 runs 96 iterations when job-06 completed with every iteration
  counted, and 88, the count job-05-i88 completed in 265 s, otherwise. The rule reads completion alone, never an X
  count. A partial job of either stays descriptive and the primary reads the other alone.
- Outcome, in the order of ascella_new_mesh_score.outcome: "not read", "both carried", "R-B carried only", "R-C carried
  only", "inconclusive: anticorrelated", "inconclusive: anchors moved", "bounded" when both upper shares lie below
  REFERENCE_LABEL's share in new-seed-score.json, and "inconclusive". R-B carried replicates the new-seed reading on
  independent meshes; R-C carried with R-B not carried places the gain in the meshes jobs 04 and 05 added.

Usage:
  "$PYTHON" scripts/ascella_replication_score.py OFFSETS CONFIRMATION REFERENCE_RUNS... -- NEW_RUNS... OUT [--check]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_new_mesh_score as base  # noqa: E402

FIRST = "job-06"
FULL_ITERATIONS = 96
# job-05-i88 completed 88 iterations of 32,768 samples in 265 s, the longest count the service has returned.
FALLBACK_ITERATIONS = 88


def replication_runs(first: dict[str, Any]) -> list[str]:
    """The replication acquisition job-06's summary admits: job-07 at 96 iterations after a complete job-06."""
    count = FULL_ITERATIONS if first["complete"] else FALLBACK_ITERATIONS
    return [FIRST, f"job-07-i{count}"]


REPLICATION = base.Design(
    "ascella-replication-score-v1",
    "docs/state/plans/ascella-replication-meshes-case.json",
    ("all-meshes", "all-served"),
    ("R-B", "R-C"),
    ("job-00", "job-02", "job-03", "job-04", "job-05-i88"),
    "job-05-i88",
    "job-0[67]*/cases.json",
    replication_runs,
    False,
    False,
    "docs/evidence/ascella-order-coefficients/new-seed-score.json",
    "P-B",
)


def main(argv: list[str]) -> int:
    return base.run(argv, REPLICATION)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

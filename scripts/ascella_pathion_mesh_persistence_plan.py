"""Plan printer of the Ascella mesh-persistence case, the versioned successor of the builder's `--plan` mode.

The builder (scripts/ascella_pathion_mesh_persistence.py) keeps its bytes because both submitted `cases.json` files bind
its sha256 in `analysis_sources`. Its `plan()` reads `record['r_quantiles']['0.5']`, but the frozen
`persistence_plan.json` nests `r_quantiles` under the drift scenarios `none`, `measured` and `random`, so the pinned
mode raises `KeyError: '0.5'`. This module prints the same plan with the median read from the `random` scenario, the
one whose first percentile sets `persistence_cutoff` (`persistence_plan` in the analysis module). The printer refuses a
plan record whose `random` first percentile, rounded to four places, differs from that cutoff.

Usage:
  "$PYTHON" scripts/ascella_pathion_mesh_persistence_plan.py --plan
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import ascella_pathion_mesh_persistence as case  # noqa: E402

CUTOFF_SCENARIO = "random"


def cutoff_scenario_median(record: dict[str, Any]) -> float:
    """Fixed-mesh median of r under the drift scenario that sets the persistence cutoff."""
    quantiles = record["r_quantiles"][CUTOFF_SCENARIO]
    if round(quantiles["0.01"], 4) != record["persistence_cutoff"]:
        raise ValueError(f"persistence_cutoff is not the first percentile of the {CUTOFF_SCENARIO!r} scenario")
    return float(quantiles["0.5"])


def plan() -> dict[str, Any]:
    """Sizes, counting errors, the frozen persistence plan and the predicted readings under each mechanism."""
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    if record["persistence_cutoff"] != case.PERSISTENCE_CUTOFF:
        raise ValueError("PERSISTENCE_CUTOFF differs from the frozen persistence plan")
    th = case.PREREGISTERED
    slot_sd = math.sqrt(2) * case.level_se(1.0)
    design = th["original_failing_raw_mean"]
    median = cutoff_scenario_median(record)
    return {
        "iterations": case.ITERATIONS,
        "expected_seconds": case.check_duration(),
        "samples_per_iteration": case.SAMPLES,
        "level_standard_error": {f"L={lv}": case.level_se(lv) for lv in (0.25, 0.5, 0.75, 1.0)},
        "persistence_plan": record,
        "predictions": {
            "per_mesh_fixed": {
                "persistence_r": f">= {case.PERSISTENCE_CUTOFF} (fixed-mesh median {median:.4f})",
                "replay_ba": f"{case.ORIGINAL_BA} +- {th['anchor_replay_band']}",
                "fresh_ba": f"median {case.MODE_FIT_BA} +- {th['fresh_band']}, sd about 0.025",
                "fresh_failing_aligned_mean": f"below {th['aligned_mesh']} (near 0)",
            },
            "slot_efficiency": {
                "fresh_ba": f"every seed {case.ORIGINAL_BA} +- {th['fresh_band']}, sd about {slot_sd:.4f}",
                "fresh_failing_aligned_mean": f"at or above {th['aligned_block']} (near {design:.4f})",
            },
            "static_shifter_map": {
                "frozen_map": "carries at seed-block p < 0.005, with its share",
                "prior_art": "signed-coherence new-seed score r 0.157 and 0.319 (share 2.5 and 10.5 percent)",
            },
            "redraw_or_drift_between_jobs": {"persistence_r": f"below {case.PERSISTENCE_CUTOFF}"},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--plan", action="store_true", required=True, help="print sizes and predictions, no files")
    parser.parse_args()
    print(json.dumps(plan(), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

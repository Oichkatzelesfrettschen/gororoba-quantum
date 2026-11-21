"""Per-batch q12 Ramsey phases of the interleaved Tuna-17 series, a descriptive split written after the analysis.

The registered analysis pools the two batches of each wait (00 and 02 at 0 cycles, 01 and 03 at 25 cycles), which ran
up to 20.6 hours apart and hold complementary triads of angles. Three angles 120 degrees apart fix the offset, the
amplitude and the phase of P = c + a cos(angle + phase) exactly, so each batch alone gives a phase with its binomial
error (no degree of freedom is left for a goodness-of-fit test). This split fits each batch through the analysis's own
fringe_fit and compares the two batches of each wait. It decides nothing.

Usage: python3 docs/evidence/qi-tuna17-interleaved-rounds/q12_batches.py OUT.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import qi_tuna17_interleaved_cases as case  # noqa: E402

RUNS = "results/quantum_inspire/runs"
PATTERN = "2026-11-19T1735Z-t17-characterization_interleaved_tuna_17-q12_phase-batch-*"


def batch_fit(batch: dict[str, Any]) -> dict[str, Any]:
    points = [
        (row["angle"], batch["p1"][name][row["qubit"]], batch["shots"])
        for name, row in batch["rows"].items()
        if row["kind"] == "ramsey"
    ]
    waits = {row["wait_cycles"] for row in batch["rows"].values() if row["kind"] == "ramsey"}
    if len(waits) != 1:
        raise SystemExit(f"{batch['run']}: a batch holds more than one wait")
    fit = case.fringe_fit(sorted(points))
    if fit is None:
        raise SystemExit(f"{batch['run']}: the triad gives no fringe")
    return {"run": batch["run"], "wait_cycles": waits.pop(), "angles": sorted(p[0] for p in points), **fit}


def main(out: Path) -> None:
    runs = sorted((ROOT / RUNS).glob(PATTERN))
    if len(runs) != 4:
        raise SystemExit(f"want 4 q12_phase runs, found {len(runs)}")
    fits = [batch_fit(b) for b in case.read_batches(runs)]
    comparisons = []
    for wait in sorted({f["wait_cycles"] for f in fits}):
        a, b = (f for f in fits if f["wait_cycles"] == wait)
        difference = math.remainder(a["phase"] - b["phase"], 2 * math.pi)
        se = math.hypot(a["phase_se"], b["phase_se"])
        comparisons.append(
            {"wait_cycles": wait, "runs": [a["run"], b["run"]], "difference": difference, "se": se, "z": difference / se}
        )
    record = {"schema": "qi-tuna17-q12-batch-phases-v1", "batches": fits, "comparisons": comparisons}
    out.write_text(json.dumps(record, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))

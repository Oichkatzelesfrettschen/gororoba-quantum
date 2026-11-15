"""Calibration of the phase scan's scaled separation on value 9 of the operating-characteristic draw.

Label counts of 500 simulated series per scenario of operating_characteristics() at separations 30, 35 and 40,
every other rule as the generator holds it. The case keeps the least separation under which no scenario reads a
deciding label of another world; value 10 then records the characteristics of that rule. Writes
separation_calibration.json beside this file."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

CALIBRATION_INDEX = 9
CANDIDATES = (30.0, 35.0, 40.0)


def wrong_labels(counts: dict[str, dict[str, int]]) -> dict[str, int]:
    out = {}
    for name, tally in counts.items():
        world = ps.TRUTHS[name][0] if name in ps.TRUTHS else None
        wrong = sum(n for label, n in tally.items() if label in ps.ERROR_WORLDS and label != world)
        if wrong:
            out[name] = wrong
    return out


def main() -> None:
    record: dict[str, object] = {"seed_index": CALIBRATION_INDEX, "candidates": {}}
    for separation in CANDIDATES:
        oc = ps.operating_characteristics(index=CALIBRATION_INDEX, separation=separation)
        counts = oc["label_counts"]
        record["candidates"][f"{separation:g}"] = {"wrong_labels": wrong_labels(counts), "label_counts": counts}
        print(separation, wrong_labels(counts), flush=True)
    chosen = next(
        (s for s in CANDIDATES if not record["candidates"][f"{s:g}"]["wrong_labels"]),
        None,
    )
    record["chosen"] = chosen
    print("chosen", chosen)
    (HERE / "separation_calibration.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

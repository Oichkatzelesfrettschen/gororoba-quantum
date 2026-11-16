"""Calibration of the phase scan's scaled separation on value 9 of the operating-characteristic draw.

Label counts of simulated series per scenario at separations 30, 35 and 40. The case kept the least separation under
which no scenario read a deciding label of another world; value 10 then recorded the characteristics of that rule.

  calibrate_separation.py r5 [--out DIR]
      Rule R5, the readout flip fixed at 0, as the retained separation_calibration.json holds it: 500 series per
      scenario, the 25 scenarios that existed at value 9 in their historical order (a scenario's position seeds its
      draw), the generator's consistency margin. Writes separation_calibration.json, which is byte for byte the
      retained record.
  calibrate_separation.py r6 --index N [--out DIR]
      Rule R6, the readout flip fitted over FLIP_GRID, through operating_characteristics() with every default of the
      generator, seeded from value N of its draw. Writes separation_calibration_r6.json.

DIR defaults to this file's directory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

R5_INDEX = 9
CANDIDATES = (30.0, 35.0, 40.0)
R5_FLIPS = (0.0,)
R5_SERIES = 500
R5_CHUNK = 250
# Scenarios of TRUTHS added after value 11 of the draw recorded rule R5.
R5_ADDED = (
    "q12 phase -0.18 rad, selector flip 0.036",
    "coupler 8-12 phase -0.25 rad, selector flip 0.036",
    "q8 phase at coupler 8-12 -0.25 rad, selector flip 0.042",
)
OUTPUT = {"r5": "separation_calibration.json", "r6": "separation_calibration_r6.json"}


def wrong_labels(counts: dict[str, dict[str, int]]) -> dict[str, int]:
    out = {}
    for name, tally in counts.items():
        world = ps.TRUTHS[name][0] if name in ps.TRUTHS else None
        wrong = sum(n for label, n in tally.items() if label in ps.ERROR_WORLDS and label != world)
        if wrong:
            out[name] = wrong
    return out


def r5_counts(index: int, separation: float) -> dict[str, dict[str, int]]:
    """Label counts of R5_SERIES series per scenario with the readout flip fixed at 0: the flip-outer worker of
    operating_characteristics() on the scenario list and positions of value 9. Each series is fixed by (seed,
    position), so a draw of NULL_SERIES series begins with the R5_SERIES series."""
    names = [n for n in ps.TRUTHS if n not in R5_ADDED] + list(ps.MIXED)
    seed = ps.oc_seed(index)
    items = [
        (seed, name, position, start, start + R5_CHUNK, ps.KIND_MARGIN, separation, R5_FLIPS)
        for position, name in enumerate(names)
        for start in range(0, R5_SERIES, R5_CHUNK)
    ]
    counts: dict[str, dict[str, int]] = {name: {} for name in names}
    for item, tally in zip(items, ordered_map(ps.oc_worker, items, min_items=2), strict=True):
        for label, n in tally.items():
            counts[item[1]][label] = counts[item[1]].get(label, 0) + n
    return {name: dict(sorted(tally.items())) for name, tally in counts.items()}


def label_counts(rule: str, index: int, separation: float) -> dict[str, dict[str, int]]:
    ps.build_tables()
    if rule == "r5":
        return r5_counts(index, separation)
    counts: dict[str, dict[str, int]] = ps.operating_characteristics(index=index, separation=separation)["label_counts"]
    return counts


def calibrate(rule: str, index: int) -> dict[str, object]:
    candidates: dict[str, object] = {}
    for separation in CANDIDATES:
        counts = label_counts(rule, index, separation)
        wrong = wrong_labels(counts)
        candidates[f"{separation:g}"] = {"wrong_labels": wrong, "label_counts": counts}
        print(rule, separation, wrong, flush=True)
    chosen = next((s for s in CANDIDATES if not candidates[f"{s:g}"]["wrong_labels"]), None)  # type: ignore[index]
    print("chosen", chosen)
    return {"seed_index": index, "candidates": candidates, "chosen": chosen}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("rule", choices=sorted(OUTPUT))
    parser.add_argument("--index", type=int, help="draw index; required for r6, 9 for r5")
    parser.add_argument("--out", type=Path, default=HERE, help="directory of the record")
    args = parser.parse_args(argv)
    if args.rule == "r5":
        if args.index not in (None, R5_INDEX):
            parser.error(f"rule r5 reproduces the record of value {R5_INDEX}")
        index = R5_INDEX
    elif args.index is None:
        parser.error("rule r6 needs --index, the value of the draw that seeds the recalibration")
    else:
        index = args.index
    record = calibrate(args.rule, index)
    (args.out / OUTPUT[args.rule]).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
